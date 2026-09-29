# coding: utf-8
"""
NATURE_CLUSTERS — Nature-Based Worm Clustering System

Groups worms by their Nature (category) for coordinated execution.
Replaces the hardcoded if/elif dispatch in CLUSTERWORMS.py with
dynamic, registry-based worm resolution.

Architecture:
    NatureCluster ("security")
    ├── VulnScanner
    ├── PortAuditor
    ├── CertMonitor
    ├── FirewallAudit
    └── PermissionScanner

    NatureCluster ("profiling")
    ├── CodeProfiler
    ├── MemoryLeakDetector
    ├── IOBottleneckFinder
    ├── GILContentionProbe
    └── CPUFlameProfiler

Features:
- Dynamic worm discovery from WORM_REGISTRY
- Nature-based grouping with auto-categorization
- Parallel/sequential cluster execution
- PAMS memory recording of every cluster action
- Mermaid graph generation for cluster relationships
- Cross-Nature dependency mapping
- Thread-safe execution with progress tracking
- Nature scoring: which Nature to activate based on system state

Usage:
    >>> from CORE.WORMS.NATURE_CLUSTERS import NatureCluster, NatureClusterManager
    >>> ncm = NatureClusterManager()
    >>> ncm.discover_all_natures()  # Auto-discover from registry
    >>> cluster = ncm.get_cluster("security")
    >>> results = cluster.execute()
    >>> mermaid = ncm.to_mermaid()
"""

import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed, wait

# ── Worm Registry ──────────────────────────────────────────────────
try:
    from CORE.worm_registry import (
        register_worm, WORM_REGISTRY, get_worms_by_category,
        get_all_categories, discover_worms, mark_spawned,
        SpawnDiversityEngine,
    )
    _REGISTRY_OK = True
except ImportError:
    _REGISTRY_OK = False
    WORM_REGISTRY = {}
    def get_worms_by_category(category: str) -> Dict[str, Dict[Any, Any]]: return {}
    def get_all_categories() -> Set[str]: return set()

    def discover_worms(
        worms_dir: Optional[str] = None,
        progress_callback: Optional[Callable] = None) -> int: return 0
    def mark_spawned(name: str) -> Any: pass
    SpawnDiversityEngine = None

    def register_worm(category: str = "",
        priority: int = 0,
        cooldown_seconds: float = 0,
        description: str = "",
        tags: Optional[set[str]] = None,
        **kwargs: Any) -> Callable[..., Any]: return lambda f: f


# ── OpenTelemetry tracing (lazy, fail-open) ────────────────────
# Every cluster run and every worm inside it becomes a span written to
# memory_store.db via the existing CD3 SQLiteSpanExporter, so a worm's
# execution can be correlated with the DirectMemory events that surround
# it (the exporter already indexes on correlation_id for exactly this).
# Tracing is strictly observational: if OTel or the exporter is missing,
# the cluster runs exactly as before.
_cluster_tracer: Any = None
_tracer_lock = threading.Lock()
_tracer_ready = False


def _get_cluster_tracer():
    """Lazy tracer singleton. Returns None when tracing is unavailable."""
    global _cluster_tracer, _tracer_ready
    if _tracer_ready:
        return _cluster_tracer
    with _tracer_lock:
        if _tracer_ready:
            return _cluster_tracer
        try:
            from CORE.cd3_exporter import configure_otel_tracing
            _cluster_tracer = configure_otel_tracing(
                service_name="azazael-nature-clusters")
        except Exception:
            _cluster_tracer = None
        _tracer_ready = True
    return _cluster_tracer


# ── PAMS Memory Recording (lazy, thread-safe) ─────────────────
_pams: Any = None
_pams_lock = threading.Lock()


def _get_pams():
    """Lazy PAMS recorder — double-checked locking for Python 3.14t free-threading."""
    global _pams
    if _pams is None:
        with _pams_lock:
            if _pams is None:
                try:
                    from CORE.PamsRecorder import PamsRecorder
                    _pams = PamsRecorder()
                except ImportError:
                    _pams = False  # Sentinel: don't retry
    return _pams if _pams else None


# ── Free-Threading ─────────────────────────────────────────────────
try:
    from CORE.freethreading import is_free_threaded, FreeThreadPool
    _FREETHREAD_OK = True
except ImportError:
    _FREETHREAD_OK = False
    FreeThreadPool = None

    def is_free_threaded() -> bool:
        try:
            return not sys._is_gil_enabled()
        except Exception:
            return False

# ── Config (lazy, thread-safe) ─────────────────────────────────
_cfg: Any = None
_cfg_lock = threading.Lock()
def _get_config():
    """Lazy config — double-checked locking for Python 3.14t free-threading.

    Called from _execute_single_worm() which runs in worker threads under
    parallel execution, so this must be thread-safe.
    """
    global _cfg
    if _cfg is None:
        with _cfg_lock:
            if _cfg is None:
                try:
                    from CORE.config import get_config
                    _cfg = get_config()
                except ImportError:
                    _cfg = False
    return _cfg if _cfg else None

# ── Circuit Breaker (lazy) ────────────────────────────────────────
_breaker_registry: Any = None
_breaker_lock = threading.Lock()
def _get_breakers():
    """Lazy BreakerRegistry — double-checked locking for Python 3.14t free-threading.

    Called from _execute_single_worm() which runs in worker threads under
    parallel execution, so this must be thread-safe.
    """
    global _breaker_registry
    if _breaker_registry is None:
        with _breaker_lock:
            if _breaker_registry is None:
                try:
                    from CORE.circuit_breaker import BreakerRegistry
                    _breaker_registry = BreakerRegistry()
                except ImportError:
                    _breaker_registry = False
    return _breaker_registry if _breaker_registry else None

# ── Structured Logger (lazy, thread-safe) ────────────────────────
_logger: Any = None
_logger_lock = threading.Lock()
def _get_log():
    """Lazy structured logger — double-checked locking for Python 3.14t free-threading.

    Called from _execute_single_worm() which runs in worker threads under
    parallel execution, so this must be thread-safe.
    """
    global _logger
    if _logger is None:
        with _logger_lock:
            if _logger is None:
                try:
                    from CORE.azazael_logging import get_logger
                    _logger = get_logger("NatureCluster")
                except ImportError:
                    _logger = False
    return _logger if _logger else None


# ═══════════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class NatureResult:
    """Result from a NatureCluster execution."""
    nature: str
    worm_results: Dict[str, Any] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0
    duration_ms: float = 0.0
    started_at: str = ""
    completed_at: str = ""
    cluster_id: str = ""
    errors: List[str] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    #: Worms the spine quarantine store held out of this run. Reported so a
    #: gated worm is visible as "skipped", never silently as "ran" -- a run
    #: that quietly dropped work would look identical to a clean one.
    quarantined_skipped: List[str] = field(default_factory=list)
    #: Worms held out because the Black Queen retired them. A retirement that
    #: is only written to the registry is a claim; enforcing it here is what
    #: makes it true, so the two must be reported separately -- a quarantine
    #: is a temporary hold, a retirement is permanent.
    retired_skipped: List[str] = field(default_factory=list)


@dataclass
class CrossNatureRoute:
    """A route connecting two Natures for data flow."""
    from_nature: str
    to_nature: str
    data_mapping: Dict[str, str] = field(default_factory=dict)  # {from_worm_result_key: to_worm_input_key}
    description: str = ""


# ═══════════════════════════════════════════════════════════════════════
# NATURE DEFINITIONS — Maps Natures to their purpose and routing
# ═══════════════════════════════════════════════════════════════════════

NATURE_DEFINITIONS = {
    "monitor": {
        "purpose": "System resource monitoring and health tracking",
        "triggers": "high CPU, memory pressure, disk alerts",
        "feeds_into": ["defense", "orchestration", "telemetry"],
        "icon": "MON",
        "data_contracts": {
            "emits": {"cpu_pct": "float", "mem_pct": "float", "disk_io": "float", "timestamp": "iso"},
            "requires": {},
        },
    },
    "diagnostic": {
        "purpose": "Deep system analysis and problem diagnosis",
        "triggers": "anomalies detected, health degradation",
        "feeds_into": ["repair", "defense", "orchestration"],
        "icon": "DIAG",
        "data_contracts": {
            "emits": {"diagnosis": "str", "severity": "str", "affected": "list[str]"},
            "requires": {"metrics": "dict"},
        },
    },
    "analysis": {
        "purpose": "Code and data pattern analysis",
        "triggers": "new code, scheduled scans, exploration",
        "feeds_into": ["optimization", "defense", "visualization"],
        "icon": "ANLY",
        "data_contracts": {
            "emits": {"patterns": "list[dict]", "score": "float"},
            "requires": {"source": "str"},
        },
    },
    "defense": {
        "purpose": "Error detection, health checks, security auditing",
        "triggers": "errors above threshold, security alerts",
        "feeds_into": ["repair", "orchestration", "telemetry"],
        "icon": "DEF",
        "data_contracts": {
            "emits": {"findings": "list[dict]", "verdict": "str"},
            "requires": {"target": "str"},
        },
    },
    "optimization": {
        "purpose": "Performance tuning and resource optimization",
        "triggers": "profiling results, bottlenecks found",
        "feeds_into": ["monitor", "orchestration", "telemetry"],
        "icon": "⚡",
    },
    "orchestration": {
        "purpose": "Worm coordination, spawn management, cluster control",
        "triggers": "fleet status changes, mode transitions",
        "feeds_into": ["monitor", "defense", "telemetry"],
        "icon": "ORCH",
    },
    "sync": {
        "purpose": "Time synchronization, clock management, scheduling",
        "triggers": "time drift, scheduled intervals",
        "feeds_into": ["monitor", "orchestration"],
        "icon": "SYNC",
    },
    "repair": {
        "purpose": "Automated code repair and auto-fix application",
        "triggers": "errors detected, defense alerts",
        "feeds_into": ["defense", "orchestration"],
        "icon": "REPR",
    },
    "security": {
        "purpose": "Vulnerability scanning, port auditing, cert monitoring",
        "triggers": "new deployments, scheduled security audits",
        "feeds_into": ["defense", "orchestration", "telemetry"],
        "icon": "SEC",
    },
    "profiling": {
        "purpose": "Code profiling, memory leak detection, bottleneck analysis",
        "triggers": "performance degradation, scheduled profiling",
        "feeds_into": ["optimization", "visualization", "telemetry"],
        "icon": "PROF",
    },
    "telemetry": {
        "purpose": "Span tracing, metric aggregation, event routing, alerting",
        "triggers": "always active — continuous telemetry pipeline",
        "feeds_into": ["visualization", "orchestration", "defense"],
        "icon": "TELE",
    },
    "container": {
        "purpose": "Container lifecycle, compose validation, image auditing",
        "triggers": "container deployments, registry updates",
        "feeds_into": ["monitor", "security", "orchestration"],
        "icon": "CONT",
    },
    "config": {
        "purpose": "Config linting, env validation, secret rotation, feature flags",
        "triggers": "config changes, scheduled audits",
        "feeds_into": ["security", "orchestration"],
        "icon": "⚙️",
    },
    "backup": {
        "purpose": "State snapshots, incremental backups, recovery testing",
        "triggers": "scheduled intervals, pre-deployment",
        "feeds_into": ["orchestration", "defense"],
        "icon": "BAK",
    },
    "migration": {
        "purpose": "Code migration, dependency upgrades, schema versioning",
        "triggers": "version bumps, scheduled upgrades",
        "feeds_into": ["analysis", "orchestration"],
        "icon": "MIGR",
    },
    "communication": {
        "purpose": "Message brokering, RPC, webhooks, IPC, protocol negotiation",
        "triggers": "inter-worm communication, external integrations",
        "feeds_into": ["orchestration", "telemetry"],
        "icon": "COMM",
    },
    "learning": {
        "purpose": "RL training, model versioning, data pipelines, A/B testing",
        "triggers": "scheduled training, data availability",
        "feeds_into": ["optimization", "visualization", "orchestration"],
        "icon": "LEARN",
    },
    "visualization": {
        "purpose": "Dashboard generation, graph rendering, report compilation",
        "triggers": "data availability, scheduled reporting",
        "feeds_into": ["orchestration"],
        "icon": "VIS",
    },
    "mesh": {
        "purpose": "Cross-env fabric transport Win<->WSL2<->Bare<->Kali<->G:",
        "triggers": "cross-env send, partition detected, beacon interval",
        "feeds_into": ["orchestration", "consensus", "telemetry"],
        "icon": "MESH",
    },
    "synapse": {
        "purpose": "Neural edge weights, MoE dispatch, gating, long-context sequencing",
        "triggers": "inference request, route scoring, log flood",
        "feeds_into": ["orchestration", "learning", "servemesh"],
        "icon": "SYNA",
    },
    "consensus": {
        "purpose": "Quorum votes, leader election, fork resolution across envs",
        "triggers": "multi-env finding, partition heal, model fork",
        "feeds_into": ["mesh", "orchestration", "immune"],
        "icon": "CONS",
    },
    "engram": {
        "purpose": "Distributed memory shards, recall routing, dream consolidation",
        "triggers": "memory write/recall, nightly consolidation",
        "feeds_into": ["learning", "mesh", "telemetry"],
        "icon": "ENGR",
    },
    "federated": {
        "purpose": "FedAvg aggregation, mesh NAS, multi-provider reward shaping",
        "triggers": "training round complete, arch proposal",
        "feeds_into": ["learning", "synapse", "mesh"],
        "icon": "FEDR",
    },
    "servemesh": {
        "purpose": "Inference endpoint LB, provider failover, model shard catalogue",
        "triggers": "inference request, provider down, model publish",
        "feeds_into": ["synapse", "telemetry", "mesh"],
        "icon": "SRVM",
    },
    "immune": {
        "purpose": "Anomaly sentinel, quarantine, attestation, self-heal",
        "triggers": "metric anomaly, integrity failure, poisoned shard",
        "feeds_into": ["defense", "orchestration", "mesh"],
        "icon": "IMMU",
    },
    "xenomorph": {
        "purpose": "Hostile-adaptive red team lifecycle; Queen prefers bare, interim degraded elsewhere",
        "triggers": "red-team round, quorum-approved injection, leader term expiry",
        "feeds_into": ["immune", "consensus", "mesh"],
        "icon": "XENO",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# INDIVIDUAL NATURE CLUSTER
# ═══════════════════════════════════════════════════════════════════════

class NatureCluster:
    """
    A cluster of worms sharing the same Nature (category).
    
    Dynamically discovers and groups all worms of a given Nature,
    supports parallel/sequential execution with PAMS recording.
    
    Usage:
        cluster = NatureCluster("security")
        cluster.discover_worms()  # Auto-discover from registry
        result = cluster.execute()  # Run all worms in this Nature
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, nature: str):
        self.nature = nature
        self.cluster_id = f"nature_{nature}_{time.time_ns()}"
        self.worms: Dict[str, type] = {}  # {class_name: class}
        self.instances: Dict[str, Any] = {}  # {class_name: instance}
        self.results: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._parallel = False
        self._timeout = 60
        self.definition = NATURE_DEFINITIONS.get(nature, {})
        self._failed_executions: List[Dict] = []  # dead letter queue (no-breaker mode)

    def _record_outcome(self, name: str, result: Dict[str, Any],
                          did: str | None = None) -> bool:
        """Route one worm outcome to the canonical telemetry tap.

        Fourth producer of the single-schema outcome stream (see
        CORE/WORMS/worm_telemetry.py): ClusterWORMZ, CONCURRENCY,
        NatureCluster, and the registry-reported path all land the same
        keys. `did` carries the spawn decision so choice->outcome joins
        stay causal. Fail-soft: telemetry must never break execution.
        """
        try:
            from CORE.WORMS.worm_telemetry import emit_worm_outcome
            return bool(emit_worm_outcome(name, result, nature=self.nature,
                                          decision_id=did,
                                          source="NatureCluster"))
        except Exception:
            return False

    # ── Dead Letter Queue Management ────────────────────────────────

    def _record_failure(self, name: str, worm_result: Dict[str, Any],
                        breaker_state: Optional[str] = None):
        """Record a failed worm execution to the dead letter queue.

        Thread-safe helper used by _execute_single_worm to avoid
        duplicating DLQ recording logic across 3 code paths.
        """
        with self._lock:
            self._failed_executions.append({
                "worm": name,
                "nature": self.nature,
                "error": worm_result.get('error', 'unknown'),
                "method": worm_result.get('method', '?'),
                "breaker_state": breaker_state,
                "timestamp": time.time(),
            })
    def get_failed_executions(self, since: float = 0) -> List[Dict]:
        """Get failed executions from the internal dead letter queue.

        Args:
            since: Unix timestamp — only return failures after this time
                   (default 0 = all failures)

        Returns:
            List of failed execution records, most recent first.
        """
        with self._lock:
            results = [f for f in self._failed_executions if f["timestamp"] >= since]
            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results
    def retry_failed_worms(self, max_retries: int = 2) -> Dict[str, Any]:
        """Retry all failed worms from the dead letter queue.

        Iterates over _failed_executions, re-executes each worm,
        and removes successful retries from the queue.

        Args:
            max_retries: How many times to retry each failed worm
                         (0=clear without retrying)

        Returns:
            Dict with retry_count, success_count, still_failed, and errors.
        """
        results = {
            "retried": 0,
            "succeeded": 0,
            "still_failed": 0,
            "errors": [],
        }

        # Snapshot the current failures
        with self._lock:
            failures = list(self._failed_executions)

        if not failures:
            return results

        # Group failures by worm name (deduplicate multiple entries for same worm)
        seen_worms: Dict[str, Dict] = {}
        for f in failures:
            name = f["worm"]
            if name not in seen_worms:
                seen_worms[name] = f

        for worm_name, failure in seen_worms.items():
            cls = self.worms.get(worm_name)
            if not cls:
                results["errors"].append(f"{worm_name}: worm class no longer registered")
                results["still_failed"] += 1
                continue

            success = False
            last_error = ""
            for attempt in range(max_retries + 1):
                worm_result = self._execute_single_worm(worm_name, cls)
                if worm_result.get("success"):
                    success = True
                    break
                last_error = worm_result.get("error", "unknown")

            results["retried"] += 1
            if success:
                results["succeeded"] += 1
                # Remove this worm's failures from the queue
                with self._lock:
                    self._failed_executions = [
                        f for f in self._failed_executions
                        if f["worm"] != worm_name
                    ]
            else:
                results["still_failed"] += 1
                results["errors"].append(
                    f"{worm_name}: {last_error} (after {max_retries + 1} attempts)"
                )

        return results
    def clear_failed_executions(self):
        """Clear the dead letter queue (remove all failed execution records)."""
        with self._lock:
            self._failed_executions = []

    # ── Discovery ──────────────────────────────────────────────────
    
    def discover_worms(self) -> int:
        """
        Auto-discover worms of this Nature from WORM_REGISTRY.
        Returns count of worms found.
        
        Only records to PAMS if new worms were discovered (deduplicates
        repeated discovery calls). Previous behavior recorded a memory
        event EVERY call, creating thousands of duplicate events.
        """
        if not _REGISTRY_OK:
            return 0
        
        # Trigger discovery first
        discover_worms()
        
        category_worms = get_worms_by_category(self.nature)
        
        with self._lock:
            count = 0
            new_worms = []
            for name, info in category_worms.items():
                cls = info.get("class")
                if cls and inspect.isclass(cls) and name not in self.worms:
                    self.worms[name] = cls
                    count += 1
                    new_worms.append(name)
        
        # Only record if new worms were actually discovered (prevents
        # duplicate event flooding — see DB dedup lesson)
        if count > 0:
            self._record("nature_cluster_discovery", {
                "nature": self.nature, "worms_found": count,
                "new_worms": new_worms,
                "total_worms": len(self.worms),
            })
        return len(self.worms)
    def add_worm_manual(self, name: str, cls: type):
        """Manually add a worm class to this cluster."""
        with self._lock:
            self.worms[name] = cls
    
    # ── Execution ──────────────────────────────────────────────────
    
    def set_parallel(self, enabled: bool):
        self._parallel = enabled
    def set_timeout(self, seconds: int):
        self._timeout = seconds
    def execute(self, worm_names: Optional[List[str]] = None, *,
                order: Optional[List[str]] = None,
                decision_id: Optional[str] = None) -> NatureResult:
        """
        Execute all worms (or a subset) in this Nature.

        Args:
            worm_names: Specific worm names to execute (None = all)
            order: Decided execution order (from SpawnDiversityEngine).
                Overrides Q-sorting: the executed order must be the order
                that was DECIDED, or the choice log describes a plan nobody
                followed. Unknown names are kept out (run, nothing invented,
                nothing lost).
            decision_id: Spawn decision this run executes. Stamped on every
                outcome row so choice->outcome joins stay causal.

        Returns:
            NatureResult with per-worm results and aggregate stats.
        """
        if not self.worms:
            self.discover_worms()

        targets = list(self.worms.items())
        if order is not None:
            by_name = dict(targets)
            targets = [(n, by_name[n]) for n in order if n in by_name]
        elif worm_names:
            targets = [(n, c) for n, c in targets if n in worm_names]

        # ── Execution gates (the boundary that makes them real) ───────
        # Two independent stores say "this worm must not run":
        #   * the spine quarantine store -- temporary, evidence-driven
        #   * registry lifecycle_state == "retired" -- permanent, Black Queen
        # Enforcing both HERE, at the point of execution and after targets are
        # chosen, means neither can be bypassed by a caller that skipped the
        # scheduler. Both imports are local and tolerant so a missing or broken
        # store degrades to "no gate" instead of blocking every nature run.
        quarantined_skipped: List[str] = []
        retired_skipped: List[str] = []
        gated: List[Any] = []
        try:
            from CORE import spine_registry as _spine
        except Exception:  # noqa: BLE001 -- absent spine means no quarantine gate
            _spine = None
        try:
            from CORE.worm_registry import WORM_REGISTRY as _registry
        except Exception:  # noqa: BLE001 -- absent registry means no retire gate
            _registry = {}
        for _name, _cfg in targets:
            if _spine is not None and _spine.is_quarantined(_name):
                quarantined_skipped.append(_name)
                continue
            _entry = _registry.get(_name) or {}
            if _entry.get("lifecycle_state") == "retired":
                retired_skipped.append(_name)
                continue
            gated.append((_name, _cfg))
        targets = gated

        result = NatureResult(
            nature=self.nature,
            cluster_id=self.cluster_id,
            started_at=datetime.now().isoformat(),
            quarantined_skipped=quarantined_skipped,
            retired_skipped=retired_skipped,
        )
        
        start = time.perf_counter()
        
        # ── Spine feedback ledger ────────────────────────────────────
        # Every outcome recorded to CORE.spine_registry so HomeostatWorm
        # can Q-reinforce and propose cooldown/priority shifts. Best-effort:
        # if the ledger is missing/unavailable, execution proceeds as before.
        _spine_ledger = None
        try:
            from CORE import spine_registry as _spine_ledger
        except ImportError:
            _spine_ledger = None

        # ── Q-weighted execution ordering (LEAP A) ─────────────────
        # Primary key: spine Q-weight (EMA of execution outcomes) so
        # healthy worms run first and failing ones are demoted — the
        # mesh adapts execution order from its own history. Secondary:
        # registry priority. Python's stable sort keeps cold worms
        # (q=0.0) in priority order. Fails open to priority-only if the
        # ledger is unavailable or errors.
        _priority_key = lambda x: WORM_REGISTRY.get(x[0], {}).get("priority", 5)  # noqa: E731
        if order is None:
            if _spine_ledger is not None:
                try:
                    _qmap = _spine_ledger.get_q_weights()
                    targets.sort(key=lambda x: (
                        -_qmap.get(f"{self.nature}:{x[0]}", 0.0),
                        -_priority_key(x),
                    ))
                except Exception:
                    targets.sort(key=_priority_key, reverse=True)
            else:
                targets.sort(key=_priority_key, reverse=True)
        # else: decided order stands untouched (see docstring).
        
        if self._parallel and len(targets) > 1:
            self._execute_parallel(targets, result)
        else:
            self._execute_sequential(targets, result)
        
        result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        result.completed_at = datetime.now().isoformat()
        
        # ── Feed the homeostat ledger (per-worm outcomes) ─────────────
        if _spine_ledger is not None:
            for name, _ in targets:
                wr = result.worm_results.get(name)
                if wr is None:
                    continue
                _spine_ledger.record_outcome(
                    self.nature, name,
                    bool(wr.get("success", False)),
                    float(wr.get("duration_ms", 0.0) or 0.0),
                    (wr.get("error") or None),
                )

        # ── Outcome tap (one row per worm, in execution order) ─────────
        # The spawn decision names worms; the tap proves they ran, stamped
        # with the decision id so choice->outcome joins stay causal.
        for name, _ in targets:
            wr = result.worm_results.get(name) or {}
            self._record_outcome(name, wr, did=decision_id)

        # Mark all as spawned
        for name, _ in targets:
            mark_spawned(name)

        # ── OTel spans (observational, never fatal) ──────────────────
        self._emit_traces(targets, result)
        
        self._record("nature_cluster_executed", {
            "nature": self.nature, "worms": len(targets),
            "success": result.success_count, "failures": result.failure_count,
            "duration_ms": result.duration_ms,
        })
        
        return result

    def _emit_traces(self, targets: List[Tuple[str, type]], result: NatureResult) -> None:
        """Emit one cluster span plus a child span per worm to the CD3 exporter.

        Attributes mirror the fields the ledger and PAMS already record
        (nature, worm, success, duration_ms, error) so a trace can be joined
        against the memory events for the same run. Best-effort by
        construction: any failure here is swallowed, because observability
        must never be able to break execution.
        """
        tracer = _get_cluster_tracer()
        if tracer is None:
            return
        try:
            with tracer.start_as_current_span("nature_cluster.execute") as span:
                span.set_attribute("nature", self.nature)
                span.set_attribute("cluster_id", self.cluster_id)
                span.set_attribute("worms", len(targets))
                span.set_attribute("success_count", result.success_count)
                span.set_attribute("failure_count", result.failure_count)
                span.set_attribute("duration_ms", float(result.duration_ms or 0.0))
                for name, _ in targets:
                    wr = result.worm_results.get(name) or {}
                    with tracer.start_as_current_span("worm.execute") as wspan:
                        wspan.set_attribute("nature", self.nature)
                        wspan.set_attribute("worm", name)
                        wspan.set_attribute("success", bool(wr.get("success", False)))
                        wspan.set_attribute(
                            "duration_ms", float(wr.get("duration_ms", 0.0) or 0.0))
                        err = wr.get("error")
                        if err:
                            wspan.set_attribute("error", True)
                            wspan.set_attribute("error.message", str(err)[:200])
        except Exception:
            pass  # tracing is observational; execution already succeeded
    def _execute_sequential(self, targets: List[Tuple[str, type]], result: NatureResult):
        """Execute worms one at a time, with circuit breaker protection."""
        for name, cls in targets:
            worm_result = self._execute_single_worm(name, cls)
            result.worm_results[name] = worm_result
            if worm_result.get("success", False):
                result.success_count += 1
            else:
                result.failure_count += 1
                result.errors.append(f"{name}: {worm_result.get('error', 'unknown')}")
    def _record_parallel_result(self, result: NatureResult, name: str,
                                worm_result: Dict[str, Any]) -> None:
        """Fold one parallel worm outcome into the cluster result."""
        result.worm_results[name] = worm_result
        if worm_result.get("success", False):
            result.success_count += 1
        else:
            result.failure_count += 1
            result.errors.append(
                f"{name}: {worm_result.get('error', 'unknown')}")

    def _execute_parallel(self, targets: List[Tuple[str, type]], result: NatureResult):
        """Execute worms in parallel, enforcing `_timeout` for real.

        Deep dive 2026-09-15: the per-worm timeout was DEAD CODE, the same
        class of defect as the audit's findings #3/#6 — a safety rail that
        could not fire. The old body iterated `as_completed(futures)`, and
        `as_completed` only ever yields futures that have ALREADY completed,
        so the following `fut.result(timeout=self._timeout)` never blocked and
        `_timeout` was never consulted. A single hung worm therefore stalled
        the entire nature — and, via `SpineCycleWorm`, the autonomic cycle
        driving it — for as long as the worm chose.

        Two things are required for a timeout that actually bounds wall time:

        1. Bound the **wait**, not just the result read. `wait(timeout=...)`
           returns as soon as the batch is done or the budget expires.
        2. Do **not** use the executor as a context manager. `__exit__` calls
           `shutdown(wait=True)`, which joins the running task anyway, so the
           method would still block for the full hung duration despite having
           "timed out". Shutdown is explicit and non-joining instead.

        `_timeout = None` keeps the historical unbounded behaviour.
        """
        if not targets:
            return
        timeout = getattr(self, "_timeout", None)
        executor = ThreadPoolExecutor(max_workers=min(len(targets), 8))
        futures: Dict[Any, str] = {}
        try:
            for name, cls in targets:
                futures[executor.submit(self._execute_single_worm, name, cls)] = name

            done, pending = wait(list(futures), timeout=timeout)
            for fut in done:
                name = futures[fut]
                try:
                    # Already complete, so this cannot block. A non-zero
                    # timeout here would have been masking the bug.
                    worm_result = fut.result(timeout=0)
                except Exception as e:
                    worm_result = {"success": False, "error": str(e)}
                self._record_parallel_result(result, name, worm_result)

            for fut in pending:
                name = futures[fut]
                # Best effort: a task already running cannot be interrupted,
                # but an unstarted one is genuinely dropped.
                try:
                    fut.cancel()
                except Exception:
                    pass
                self._record_parallel_result(result, name, {
                    "success": False,
                    "error": f"timeout after {timeout}s",
                    "timed_out": True,
                })
        finally:
            # Never join a hung worm.
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except TypeError:  # pragma: no cover - Python < 3.9 signature
                executor.shutdown(wait=False)

    def _execute_single_worm(self, name: str, cls: type) -> Dict[str, Any]:
        """Execute a single worm (used by parallel executor).
        
        When circuit breaker is enabled, wraps execution in breaker
        protection with exponential backoff retry.
        Uses lazy config/breaker imports.
        
        Failed executions are ALWAYS recorded to the internal dead letter
        queue (_failed_executions) regardless of circuit breaker availability.
        """
        breakers = _get_breakers()
        cfg = _get_config()
        log = _get_log()
        
        if breakers:
            breaker = breakers.get(name)
            max_retries = cfg.clusters.max_retries if cfg else 3
            def _do_execute():
                instance = self._get_or_create_instance(name, cls)
                return self._run_worm_method(name, instance)
            
            try:
                result = breaker.retry_with_backoff(_do_execute, max_retries=max_retries)
                # Record failure to DLQ if breaker retries were exhausted
                if not result.get("success"):
                    self._record_failure(name, result, result.get('breaker_state'))
                    if log:
                        log.warning("worm_failed", {
                            "worm": name, "error": result.get('error')
                        })
                return result
            except RuntimeError as e:
                if log:
                    log.warning("breaker_open", {"worm": name, "state": breaker.state.value, "error": str(e)})
                result = {"success": False, "error": str(e), "breaker_state": breaker.state.value}
                self._record_failure(name, result, breaker.state.value)
                return result
            except Exception as e:
                if log:
                    log.warning("worm_failed", {"worm": name, "error": str(e)})
                return {"success": False, "error": str(e)}
        
        if log:
            log.info("worm_executing", {"worm": name})
        # Direct execution without circuit breaker —
        # record failures to internal dead letter queue for observability
        instance = self._get_or_create_instance(name, cls)
        worm_result = self._run_worm_method(name, instance)
        
        # Record failed executions to local dead letter queue
        # (always-on — runs regardless of breaker availability)
        if not worm_result.get("success"):
            self._record_failure(name, worm_result)
            if log:
                log.warning("worm_failed_no_breaker", {
                    "worm": name, "error": worm_result.get('error')
                })
        return worm_result
    def _get_or_create_instance(self, name: str, cls: type) -> Any:
        """Get cached instance or create new one."""
        with self._lock:
            if name not in self.instances:
                try:
                    self.instances[name] = cls()
                except Exception:
                    self.instances[name] = None
        return self.instances[name]
    
    # Read-only zero-arg entry points for healthy worms whose API does not
    # match the standard names (none inherit BaseWormMixin). Calling an
    # arbitrary method here would risk side effects (train/rotate/rollback),
    # so every entry below was hand-verified read-only. Worms with no safe
    # zero-arg method get an honest "standby" report instead of an error.
    _SAFE_METHODS = {
        "CainWorm": "run_complete_analysis",
        "RPCEndpoint": "list_methods",
        "SecretRotator": "generate_password",
        "EnvValidator": "scan_env_files",
        "DotfileSync": "get_checksums",
        "DiagnosticWorm": "scan_all_modules",
        "GILContentionProbe": "measure_contention",
        "MemoryLeakDetector": "take_snapshot",
        "IOBottleneckFinder": "measure_io",
        "PortAuditor": "scan_local_ports",
        "VulnScanner": "scan_requirements",
        "CLOCKZ": "get_utc",
        "MetricAggregator": "get_snapshot",
        "SpanTracer": "get_trace_tree",
        "RLTrainLoop": "get_training_stats",
        "ReportCompiler": "compile_html",
        "HeatmapBuilder": "get_busiest_hours",
        "GraphRenderer": "to_dot",
        "TimelineViz": "to_timeline_html",
    }

    # Orchestrator/manager worms must NEVER execute inside a cycle: they fan
    # out into sub-executions of the whole architecture (MetaCluster and
    # NatureClusterManager re-run all natures recursively — 300s+ and
    # self-amplifying). The cycle IS the orchestration; report standby.
    # `SpineCycleWorm` joined this set on 2026-09-15 (audit finding #2). It
    # is registered `orchestration` and exposes execute() -> run_cycle(), so a
    # generic nature sweep would instantiate a SECOND cycle besides the
    # autonomic heart's and run it concurrently against process-global state.
    # Its own module-level gate makes that safe; this makes it not happen.
    _NO_EXECUTE = frozenset({
        "ClusterWORMZ", "MetaCluster", "NatureClusterManager", "WormFleet",
        "ConcurrencyManager", "ErrorRecoveryOrchestrator", "SpineCycleWorm",
    })

    def _run_worm_method(self, name: str, instance: Any) -> Dict[str, Any]:
        """Run the appropriate method on a worm instance."""
        if instance is None:
            return {"success": False, "error": "Failed to instantiate"}

        # Mid-flight clarification channel: a worm asking for owner input is a
        # normalised outcome, not a crash. Bound as locals so the `except`
        # clauses below resolve by closure, and so a missing delegation module
        # degrades to "no channel" instead of an import error on every run.
        try:
            from CORE.WORMS.expansion.delegation import (
                NeedsClarification, ClarificationTimeout)
        except Exception:  # noqa: BLE001 -- optional channel
            NeedsClarification = type("NeedsClarification", (Exception,), {})
            ClarificationTimeout = type("ClarificationTimeout", (Exception,), {})

        if name in self._NO_EXECUTE:
            return {"success": True, "method": "standby-orchestrator",
                    "result": {"mode": "standby",
                               "reason": "orchestrator fans out; cycle is the orchestration"}}
        def _call(method_name: str) -> Dict[str, Any]:
            try:
                method = getattr(instance, method_name)
                _t0 = time.perf_counter()
                result = method()
                _ms = round((time.perf_counter() - _t0) * 1000, 2)
                # Convert to dict if dataclass
                if hasattr(result, "__dict__"):
                    result = result.__dict__
                return {"success": True, "method": method_name, "result": result,
                        "duration_ms": _ms}
            except NeedsClarification as _nc:
                return {"success": False,
                        "error": "needs owner input: %s" % _nc,
                        "method": method_name, "duration_ms": 0.0,
                        "result": {"needs_input": _nc.question},
                        "decision_id": _nc.decision_id,
                        "outcome": "needs_input"}
            except ClarificationTimeout as _ct:
                return {"success": False, "error": str(_ct),
                        "method": method_name, "duration_ms": 0.0,
                        "result": {"timed_out": True},
                        "timed_out": True,
                        "decision_id": _ct.decision_id,
                        "outcome": "clarification_timeout"}
            except Exception as e:
                return {"success": False, "error": str(e), "method": method_name,
                        "duration_ms": 0.0}

        # 1. Declared schema first (BaseWormMixin present + future worms)
        declared = getattr(instance, "__summary_method__", "")
        if declared and callable(getattr(instance, declared, None)):
            return _call(declared)

        # 2. Common method names in priority order
        for method_name in ["get_summary", "get_status", "run", "execute",
                            "scan", "check", "analyze"]:
            if hasattr(instance, method_name):
                return _call(method_name)

        # 3. Hand-verified read-only entry point for known non-standard worms
        safe = self._SAFE_METHODS.get(name)
        if safe and callable(getattr(instance, safe, None)):
            return _call(safe)

        # 4. Healthy instance, no safe zero-arg behavior: standby, not error
        try:
            methods = sorted(m for m in dir(instance)
                             if not m.startswith("_")
                             and callable(getattr(instance, m, None)))
        except Exception:
            methods = []
        return {"success": True, "method": "standby",
                "result": {"mode": "standby", "methods": methods[:12]}}

    # ── Status ─────────────────────────────────────────────────────
    
    def get_status(self) -> Dict[str, Any]:
        """Get cluster status."""
        breakers = _get_breakers()
        breaker_stats = {}
        if breakers:
            try:
                breaker_stats = {
                    "breaker_ok": True,
                    "breaker_stats": breakers.all_stats(),
                }
            except Exception:
                pass
        
        with self._lock:
            return {
                "nature": self.nature,
                "cluster_id": self.cluster_id,
                "worm_count": len(self.worms),
                "worm_names": sorted(self.worms.keys()),
                "parallel": self._parallel,
                "timeout": self._timeout,
                "definition": self.definition,
                "feeds_into": self.definition.get("feeds_into", []),
                "version": self.VERSION,
                "free_threaded": is_free_threaded(),
                "breaker_ok": breakers is not None,
                "failed_executions": len(self._failed_executions),
                **breaker_stats,
            }
    
    def get_worm_info(self) -> List[Dict[str, Any]]:
        """Get detailed info about each worm in this cluster."""
        info_list = []
        for name in sorted(self.worms.keys()):
            reg_info = WORM_REGISTRY.get(name, {})
            info_list.append({
                "name": name,
                "priority": reg_info.get("priority", "?"),
                "cooldown_seconds": reg_info.get("cooldown_seconds", "?"),
                "description": reg_info.get("description", ""),
                "version": reg_info.get("version", "?"),
                "spawn_count": reg_info.get("spawn_count", 0),
                "last_spawned": reg_info.get("last_spawned"),
                "source_file": reg_info.get("source_file", ""),
            })
        return info_list
    
    # ── Memory Recording ───────────────────────────────────────────
    
    def _record(self, event_type: str, data: Dict[str, Any]):
        """Record event to PAMS memory."""
        pams = _get_pams()
        if pams:
            try:
                pams.record_event(
                    event_type, data,
                    source=f"NatureCluster.{self.nature}",
                    severity="info",
                )
            except Exception:
                pass
    
    # ── Mermaid Graph ──────────────────────────────────────────────
    
    def to_mermaid(self) -> str:
        """Generate Mermaid graph for this Nature's worms."""
        lines = [f"subgraph {self.nature}[{self.definition.get('icon', '')} {self.nature.upper()}]"]
        for name in sorted(self.worms.keys()):
            reg = WORM_REGISTRY.get(name, {})
            desc = reg.get("description", "")
            if desc:
                desc = desc[:60] + "..." if len(desc) > 60 else desc
                lines.append(f'    {name}["{name}<br/><small>{desc}</small>"]')
            else:
                lines.append(f'    {name}["{name}"]')
        lines.append("end")
        return "\n".join(lines)
    def __repr__(self):
        return f"NatureCluster({self.nature}, {len(self.worms)} worms)"


import inspect  # needed for isclass check in discover_worms


# ═══════════════════════════════════════════════════════════════════════
# NATURE CLUSTER MANAGER — Orchestrates All Natures
# ═══════════════════════════════════════════════════════════════════════

@register_worm(category="orchestration", priority=9, cooldown_seconds=10.0,
    description="Nature-based cluster manager — dynamically groups worms by Nature, executes by need, records to PAMS")
class NatureClusterManager:
    """
    Manages all NatureClusters across the ecosystem.
    
    Discovers all worm categories, creates NatureCluster per category,
    scores which Natures need attention based on system state,
    and orchestrates cross-Nature execution.
    
    Usage:
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        results = ncm.execute_nature("security")
        all_results = ncm.execute_priority_natures(max_natures=3)
        print(ncm.to_mermaid())
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.clusters: Dict[str, NatureCluster] = {}
        self._lock = threading.RLock()
        self._execution_history: List[Dict] = []
        self._diversity: Optional[SpawnDiversityEngine] = (
            SpawnDiversityEngine() if SpawnDiversityEngine else None        )
    
    # ── Discovery ──────────────────────────────────────────────────
    
    def discover_all_natures(self) -> Dict[str, int]:
        """
        Discover all worms from registry, group by Nature.
        Returns {nature: worm_count}.
        """
        if not _REGISTRY_OK:
            return {}
        
        discover_worms()
        categories = get_all_categories()
        
        nature_counts = {}
        with self._lock:
            for cat in sorted(categories):
                # Reuse an existing cluster so its populated `worms` dict
                # persists, making the `name not in self.worms` dedup effective
                # across manager runs. Fresh instances would re-see every worm
                # as "new" each time, flooding nature_cluster_discovery events.
                cluster = self.clusters.get(cat)
                if cluster is None:
                    cluster = NatureCluster(cat)
                count = cluster.discover_worms()
                if count > 0:
                    self.clusters[cat] = cluster
                    nature_counts[cat] = count
        
        self._record("nature_manager_discovery", {
            "natures_found": len(nature_counts),
            "total_worms": sum(nature_counts.values()),
            "per_nature": nature_counts,
        })
        return nature_counts
    def _credit_snapshot(self) -> dict:
        """Per-worm grounded credit for the diversity engine. Best-effort."""
        try:
            from CORE.WORMS.expansion.spawn_credit import build_spawn_credit
            credit = build_spawn_credit()
            return {w: float(o.get("rate", 0.0))
                    for w, o in (getattr(credit, "outcomes", {}) or {}).items()}
        except Exception:
            return {}

    def _q_weight_snapshot(self) -> dict:
        """Spine Q-weights keyed nature:worm for the diversity engine."""
        try:
            from CORE import spine_registry as _spine
            return dict(_spine.get_q_weights())
        except Exception:
            return {}

    def get_cluster(self, nature: str) -> Optional[NatureCluster]:
        """Get or create a cluster for a given Nature."""
        with self._lock:
            if nature not in self.clusters:
                cluster = NatureCluster(nature)
                cluster.discover_worms()
                if cluster.worms:
                    self.clusters[nature] = cluster
            return self.clusters.get(nature)
    
    # ── Dead Letter Queue Management (Aggregated) ─────────────────

    def get_dead_letter_summary(self, lookback_seconds: float = 3600) -> Dict[str, Any]:
        """Get an aggregated summary of failed executions across ALL natures.

        Combines individual NatureCluster DLQs into a single view with
        per-worm deduplication and per-nature breakdown.

        Args:
            lookback_seconds: How far back to include (default 1 hour)

        Returns:
            Dict with total_failed, per_nature, per_worm, and recent_errors.
        """
        since = time.time() - lookback_seconds
        summary: Dict[str, Any] = {
            "total_failed": 0,
            "affected_natures": 0,
            "per_nature": {},
            "per_worm": {},
            "recent_errors": [],
        }

        with self._lock:
            for nature, cluster in self.clusters.items():
                failures = cluster.get_failed_executions(since=since)
                if not failures:
                    continue

                summary["affected_natures"] += 1
                summary["per_nature"][nature] = len(failures)
                summary["total_failed"] += len(failures)

                # Per-worm counts
                worm_counts: Dict[str, int] = {}
                for f in failures:
                    w = f["worm"]
                    worm_counts[w] = worm_counts.get(w, 0) + 1
                summary["per_worm"].update(worm_counts)

                # Recent errors (most recent first, up to 5 per nature)
                for f in failures[:5]:
                    summary["recent_errors"].append({
                        "nature": nature,
                        "worm": f["worm"],
                        "error": f["error"][:120],
                        "method": f.get("method", "?"),
                        "breaker_state": f.get("breaker_state"),
                        "timestamp": f["timestamp"],
                    })

        summary["recent_errors"].sort(key=lambda x: x["timestamp"], reverse=True)
        summary["recent_errors"] = summary["recent_errors"][:20]

        return summary
    def retry_all_failed_worms(self, max_retries: int = 2) -> Dict[str, Any]:
        """Retry all failed worms across every NatureCluster.

        Delegates to each cluster's retry_failed_worms() and aggregates
        results.

        Args:
            max_retries: How many times to retry each failed worm

        Returns:
            Dict with total_retried, total_succeeded, still_failed, per_nature.
        """
        results = {
            "total_retried": 0,
            "total_succeeded": 0,
            "still_failed": 0,
            "per_nature": {},
            "errors": [],
        }

        with self._lock:
            for nature, cluster in self.clusters.items():
                cluster_result = cluster.retry_failed_worms(max_retries=max_retries)
                if cluster_result["retried"] > 0:
                    results["per_nature"][nature] = cluster_result
                    results["total_retried"] += cluster_result["retried"]
                    results["total_succeeded"] += cluster_result["succeeded"]
                    results["still_failed"] += cluster_result["still_failed"]
                    results["errors"].extend(cluster_result["errors"])

        return results

    # ── Execution ──────────────────────────────────────────────────
    
    def execute_nature(self, nature: str, parallel: bool = False) -> Optional[NatureResult]:
        """Execute all worms in a given Nature.

        The SpawnDiversityEngine is INVOKED here, not merely instantiated:
        its decision (order + decision_id) reaches the executor so choice
        rows and outcome rows describe one decision (2026-09-28; the engine
        wrote 608 orphan choice rows before this call existed). Fail-open:
        a broken engine degrades to unordered, unjoined execution.
        """
        cluster = self.get_cluster(nature)
        if not cluster:
            return None

        cluster.set_parallel(parallel)
        order: Optional[list] = None
        did: Optional[str] = None
        if self._diversity is not None:
            try:
                candidates = list(cluster.worms)
                order, did = self._diversity.decide_execution_order(
                    nature, candidates,
                    q_weights=self._q_weight_snapshot(),
                    credit=self._credit_snapshot())
            except Exception:
                order, did = None, None
        result = cluster.execute(order=order, decision_id=did)
        
        with self._lock:
            self._execution_history.append({
                "nature": nature, "success": result.success_count,
                "failures": result.failure_count,
                "duration_ms": result.duration_ms,
                "timestamp": datetime.now().isoformat(),
            })
        
        return result
    def execute_all_natures(self, parallel_natures: bool = False, 
                            parallel_worms: bool = False) -> Dict[str, NatureResult]:
        """Execute all discovered Natures."""
        results = {}
        
        if parallel_natures:
            with ThreadPoolExecutor(max_workers=min(len(self.clusters), 8)) as executor:
                futures = {}
                for nature in self.clusters:
                    fut = executor.submit(self.execute_nature, nature, parallel_worms)
                    futures[fut] = nature
                for fut in as_completed(futures):
                    nature = futures[fut]
                    try:
                        result = fut.result(timeout=300)
                        if result:
                            results[nature] = result
                    except Exception as e:
                        results[nature] = NatureResult(
                            nature=nature, errors=[str(e)]
                        )
        else:
            for nature in sorted(self.clusters.keys()):
                result = self.execute_nature(nature, parallel_worms)
                if result:
                    results[nature] = result
        
        self._record("nature_manager_executed_all", {
            "natures": len(results), "total_ok": sum(r.success_count for r in results.values()),
            "total_fail": sum(r.failure_count for r in results.values()),
        })
        return results
    def execute_priority_natures(self, max_natures: int = 3) -> Dict[str, NatureResult]:
        """
        Execute Natures scored by priority: what needs attention most.
        Uses system state + nature definitions + diversity engine.
        """
        scores = self._score_natures()
        top_natures = sorted(scores, key=scores.get, reverse=True)[:max_natures]
        
        results = {}
        for nature in top_natures:
            result = self.execute_nature(nature)
            if result:
                results[nature] = result
        
        return results
    def _score_natures(self) -> Dict[str, float]:
        """Score each Nature based on system state and urgency."""
        scores = {}
        
        # System metrics
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
        except ImportError:
            cpu, mem = 50.0, 50.0
        
        for nature in self.clusters:
            score = 5.0  # Base score
            
            NATURE_DEFINITIONS.get(nature, {})
            
            # System state boosts
            if cpu > 80 and nature in ("monitor", "profiling"):
                score += 15.0
            if cpu > 60 and nature == "optimization":
                score += 8.0
            if mem > 85 and nature in ("monitor", "optimization"):
                score += 10.0
            
            # Error-driven boosts
            recent_errors = sum(
                1 for h in self._execution_history[-10:]
                if h.get("nature") == nature and h.get("failures", 0) > 0
            )
            if recent_errors > 2:
                score += 12.0  # Boost if recent errors
                if nature == "defense":
                    score += 5.0
            
            # Recency penalty
            last_exec = next(
                (h for h in reversed(self._execution_history) if h.get("nature") == nature),
                None,
            )
            if last_exec:
                seconds_ago = (datetime.now() - datetime.fromisoformat(
                    last_exec["timestamp"])).total_seconds()
                if seconds_ago < 60:
                    score -= 5.0  # Recently executed
                elif seconds_ago > 600:
                    score += 5.0  # Stale — boost
            
            # Worm count bonus
            worm_count = len(self.clusters[nature].worms)
            score += min(worm_count * 0.5, 3.0)
            
            scores[nature] = score
        
        return scores
    
    # ── Cross-Nature Routing ───────────────────────────────────────
    
    def get_cross_nature_routes(self) -> List[CrossNatureRoute]:
        """Get all cross-Nature routing paths based on NATURE_DEFINITIONS."""
        routes = []
        for nature, definition in NATURE_DEFINITIONS.items():
            for target in definition.get("feeds_into", []):
                routes.append(CrossNatureRoute(
                    from_nature=nature,
                    to_nature=target,
                    description=f"{definition.get('icon', '')} {nature} → {target}",
                ))
        return routes
    def route_results(self, from_results: Dict[str, NatureResult],
                      route: CrossNatureRoute) -> Dict[str, Any]:
        """Route data from one Nature's results to another's inputs."""
        routed = {"from": route.from_nature, "to": route.to_nature, "data": {}}
        
        source = from_results.get(route.from_nature)
        if not source:
            return routed
        
        # Collect all worm results as routing data
        for worm_name, worm_result in source.worm_results.items():
            if isinstance(worm_result, dict):
                routed["data"][worm_name] = worm_result.get("result", worm_result)
        
        return routed
    
    # ── Status ─────────────────────────────────────────────────────
    
    def get_status(self) -> Dict[str, Any]:
        """Get full manager status."""
        with self._lock:
            return {
                "version": self.VERSION,
                "natures": len(self.clusters),
                "total_worms": sum(len(c.worms) for c in self.clusters.values()),
                "natures_list": sorted(self.clusters.keys()),
                "execution_history_count": len(self._execution_history),
                "recent_executions": self._execution_history[-5:],
                "cross_nature_routes": len(self.get_cross_nature_routes()),
                "free_threaded": is_free_threaded(),
            }
    
    def list_all_worms(self) -> Dict[str, List[str]]:
        """List all worms grouped by Nature."""
        return {
            nature: sorted(cluster.worms.keys())
            for nature, cluster in sorted(self.clusters.items())
        }
    
    # ── Mermaid Graph ──────────────────────────────────────────────
    
    def to_mermaid(self, include_routes: bool = True) -> str:
        """
        Generate a complete Mermaid graph of all Nature clusters,
        their worms, and cross-Nature routing.
        """
        lines = ["graph TB"]
        lines.append("    title[\"AZAZAEL NATURE CLUSTERS\"]")
        lines.append("    style title fill:#1a1a2e,stroke:#00d9ff,color:#00d9ff")
        lines.append("")
        
        # Add each Nature subgraph
        for nature, cluster in sorted(self.clusters.items()):
            definition = NATURE_DEFINITIONS.get(nature, {})
            icon = definition.get("icon", "")
            purpose = definition.get("purpose", "")
            
            lines.append(f"    subgraph {nature}[{icon} {nature.upper()}]")
            lines.append(f"        {nature}_desc[\"{purpose}\"]")
            lines.append(f"        style {nature}_desc fill:#16213e,stroke:#333,color:#888")
            
            # List worms compactly
            worm_list = sorted(cluster.worms.keys())
            if len(worm_list) <= 6:
                for i, name in enumerate(worm_list):
                    lines.append(f"        {nature}_{i}[\"{name}\"]")
            else:
                lines.append(f"        {nature}_worms[\"{len(worm_list)} worms: {', '.join(worm_list[:5])}...\"]")
            
            lines.append("    end")
            lines.append("")
        
        # Add cross-Nature routes
        if include_routes:
            routes = self.get_cross_nature_routes()
            if routes:
                lines.append("    %% Cross-Nature Routes")
                for route in routes:
                    lines.append(f"    {route.from_nature} -->|{route.description.split(chr(10))[0] if chr(10) in route.description else route.description}| {route.to_nature}")
        
        return "\n".join(lines)
    def to_mermaid_functions(self) -> str:
        """
        Generate a detailed Mermaid class diagram showing all worm
        classes and their key methods per Nature.
        """
        lines = ["classDiagram"]
        
        for nature, cluster in sorted(self.clusters.items()):
            definition = NATURE_DEFINITIONS.get(nature, {})
            icon = definition.get("icon", "")
            
            lines.append(f"    %% {icon} {nature.upper()}")
            for name in sorted(cluster.worms.keys()):
                cls = cluster.worms[name]
                methods = [m for m in dir(cls) if not m.startswith("_") and callable(getattr(cls, m, None))]
                method_str = "+" + "()\\n+".join(sorted(methods)[:6])
                lines.append(f"    class {name} {{")
                lines.append(f"        +VERSION")
                lines.append(f"        {method_str}()")
                lines.append(f"    }}")
        
        return "\n".join(lines)
    
    # ── Memory Recording ───────────────────────────────────────────
    
    def _record(self, event_type: str, data: Dict[str, Any]):
        """Record event to PAMS memory."""
        pams = _get_pams()
        if pams:
            try:
                pams.record_event(
                    event_type, data,
                    source="NatureClusterManager",
                    severity="info",
                )
            except Exception:
                pass
    def __repr__(self):
        return f"NatureClusterManager({len(self.clusters)} natures, {sum(len(c.worms) for c in self.clusters.values())} worms)"


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    """CLI entry point for NatureClusterManager."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NATURE_CLUSTERS — Nature-Based Worm Clustering"
    )
    parser.add_argument("--discover", action="store_true", help="Discover all Natures and worms")
    parser.add_argument("--list", action="store_true", help="List all Natures and their worms")
    parser.add_argument("--execute", type=str, help="Execute a specific Nature (e.g., 'security')")
    parser.add_argument("--execute-all", action="store_true", help="Execute all Natures")
    parser.add_argument("--execute-priority", type=int, default=0, help="Execute top-N priority Natures")
    parser.add_argument("--parallel", action="store_true", help="Use parallel execution")
    parser.add_argument("--mermaid", action="store_true", help="Generate Mermaid graph")
    parser.add_argument("--mermaid-functions", action="store_true", help="Generate Mermaid class diagram")
    parser.add_argument("--status", action="store_true", help="Show manager status")
    parser.add_argument("--routes", action="store_true", help="Show cross-Nature routes")
    
    args = parser.parse_args()
    ncm = NatureClusterManager()
    ncm.discover_all_natures()
    
    if args.discover:
        status = ncm.get_status()
        print(f"Discovered {status['natures']} Natures with {status['total_worms']} worms")
    
    elif args.list:
        for nature, worms in sorted(ncm.list_all_worms().items()):
            print(f"\n[{nature}] ({len(worms)} worms):")
            cluster = ncm.get_cluster(nature)
            if cluster is not None:
                for info in cluster.get_worm_info():
                    print(f"  {info['name']:30} pri={info['priority']} — {info['description'][:60]}")
    
    elif args.execute:
        result = ncm.execute_nature(args.execute, parallel=args.parallel)
        if result:
            print(f"\nNatureCluster [{args.execute}]: {result.success_count} ok, {result.failure_count} fail, {result.duration_ms:.0f}ms")
            for name, wr in result.worm_results.items():
                status = "OK" if wr.get("success") else "FAIL"
                print(f"  [{status}] {name}")
        else:
            print(f"Nature '{args.execute}' not found")
    
    elif args.execute_all:
        results = ncm.execute_all_natures(parallel_worms=args.parallel)
        for nature, r in results.items():
            print(f"[{nature}] {r.success_count}/{r.success_count + r.failure_count} ok ({r.duration_ms:.0f}ms)")
        total_ok = sum(r.success_count for r in results.values())
        total_worms = sum(r.success_count + r.failure_count for r in results.values())
        print(f"\nTotal: {total_ok}/{total_worms} worms succeeded")
    
    elif args.execute_priority:
        results = ncm.execute_priority_natures(max_natures=args.execute_priority)
        for nature, r in results.items():
            print(f"[{nature}] {r.success_count} ok, {r.failure_count} fail")
    
    elif args.mermaid:
        print(ncm.to_mermaid())
    
    elif args.mermaid_functions:
        print(ncm.to_mermaid_functions())
    
    elif args.status:
        import json
        print(json.dumps(ncm.get_status(), indent=2, default=str))
    
    elif args.routes:
        for route in ncm.get_cross_nature_routes():
            print(f"  {route.from_nature} → {route.to_nature}: {route.description}")
    
    else:
        print("NATURE_CLUSTERS v" + NatureClusterManager.VERSION)
        print()
        print("Usage:")
        print("  --discover                 Discover all Natures and worms")
        print("  --list                     List all Natures and their worms")
        print("  --execute NATURE           Execute a specific Nature")
        print("  --execute-all              Execute all Natures")
        print("  --execute-priority N       Execute top-N priority Natures")
        print("  --parallel                 Use parallel execution")
        print("  --mermaid                  Generate Mermaid graph")
        print("  --mermaid-functions        Generate Mermaid class diagram")
        print("  --status                   Show manager status")
        print("  --routes                   Show cross-Nature routes")


if __name__ == "__main__":
    main()
