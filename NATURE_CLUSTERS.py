from CORE.worm_registry import BaseWormMixin
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
from typing import Dict, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError

# Module-level worm result cache — avoids redundant worm executions
# within a short window (e.g., monitor nature re-executing SYSTEMZ).
# Maps worm name → (timestamp, result_dict). TTL: 5 seconds.
_worm_result_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_worm_cache_lock = threading.Lock()
_WORM_CACHE_TTL = 5.0  # seconds

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
    def get_worms_by_category(category: str) -> dict[str, dict[Any, Any]]: return {}
    def get_all_categories() -> set[str]: return set()

    def discover_worms(
        worms_dir: (str | None) = None,
        progress_callback: (Callable | None) = None) -> int: return 0
    def mark_spawned(name: str) -> Any: pass
    SpawnDiversityEngine = None

    def register_worm(category: str = "",
        priority: int = 0,
        cooldown_seconds: float = 0,
        description: str = "",
        tags: (set[str] | None) = None,
        **kwargs: Any) -> Callable[..., Any]: return lambda f: f


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


# ── DirectMemory (lazy, thread-safe) ────────────────────────────
_dm: Any = None
_dm_lock = threading.Lock()
def _get_dm():
    """Lazy DirectMemory — double-checked locking for Python 3.14t free-threading."""
    global _dm
    if _dm is None:
        with _dm_lock:
            if _dm is None:
                try:
                    from CORE.direct_memory import DirectMemory
                    _dm = DirectMemory(session_id="nature_cluster_execution")
                except ImportError:
                    _dm = False  # Sentinel: don't retry
    return _dm if _dm else None


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
    worm_results: dict[str, Any] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0
    duration_ms: float = 0.0
    started_at: str = ""
    completed_at: str = ""
    cluster_id: str = ""
    errors: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    all_cached: bool = False  # True if all results came from cache (T34 pre-cache check)


@dataclass
class CrossNatureRoute:
    """A route connecting two Natures for data flow."""
    from_nature: str
    to_nature: str
    data_mapping: dict[str, str] = field(default_factory=dict)  # {from_worm_result_key: to_worm_input_key}
    description: str = ""


# ═══════════════════════════════════════════════════════════════════════
# NATURE DEFINITIONS — Maps Natures to their purpose and routing
# ═══════════════════════════════════════════════════════════════════════

NATURE_DEFINITIONS = {
    "monitor": {
        "purpose": "System resource monitoring and health tracking",
        "triggers": "high CPU, memory pressure, disk alerts",
        "feeds_into": ["defense", "orchestration", "telemetry"],
        "icon": "[chart]",
    },
    "diagnostic": {
        "purpose": "Deep system analysis and problem diagnosis",
        "triggers": "anomalies detected, health degradation",
        "feeds_into": ["defense", "orchestration"],
        "icon": "[search]",
    },
    "analysis": {
        "purpose": "Code and data pattern analysis",
        "triggers": "new code, scheduled scans, exploration",
        "feeds_into": ["defense", "visualization"],
        "icon": "[brain]",
    },
    "defense": {
        "purpose": "Error detection, health checks, security auditing",
        "triggers": "errors above threshold, security alerts",
        "feeds_into": ["orchestration", "telemetry"],
        "icon": "[shield]",
    },
    "orchestration": {
        "purpose": "Worm coordination, spawn management, cluster control",
        "triggers": "fleet status changes, mode transitions",
        "feeds_into": ["monitor", "defense", "telemetry"],
        "icon": "[target]",
    },
    "sync": {
        "purpose": "Time synchronization, clock management, scheduling",
        "triggers": "time drift, scheduled intervals",
        "feeds_into": ["monitor", "orchestration"],
        "icon": "[clock]",
    },
    "security": {
        "purpose": "Vulnerability scanning, port auditing, cert monitoring",
        "triggers": "new deployments, scheduled security audits",
        "feeds_into": ["defense", "orchestration", "telemetry"],
        "icon": "[lock]",
    },
    "profiling": {
        "purpose": "Code profiling, memory leak detection, bottleneck analysis",
        "triggers": "performance degradation, scheduled profiling",
        "feeds_into": ["visualization", "telemetry"],
        "icon": "[chart-up]",
    },
    "telemetry": {
        "purpose": "Span tracing, metric aggregation, event routing, alerting",
        "triggers": "always active — continuous telemetry pipeline",
        "feeds_into": ["visualization", "orchestration", "defense"],
        "icon": "[antenna]",
    },
    "container": {
        "purpose": "Container lifecycle, compose validation, image auditing",
        "triggers": "container deployments, registry updates",
        "feeds_into": ["monitor", "security", "orchestration"],
        "icon": "[package]",
    },
    "config": {
        "purpose": "Config linting, env validation, secret rotation, feature flags",
        "triggers": "config changes, scheduled audits",
        "feeds_into": ["security", "orchestration"],
        "icon": "[gear]",
    },
    "backup": {
        "purpose": "State snapshots, incremental backups, recovery testing",
        "triggers": "scheduled intervals, pre-deployment",
        "feeds_into": ["orchestration", "defense"],
        "icon": "[disk]",
    },
    "migration": {
        "purpose": "Code migration, dependency upgrades, schema versioning",
        "triggers": "version bumps, scheduled upgrades",
        "feeds_into": ["analysis", "orchestration"],
        "icon": "[truck]",
    },
    "communication": {
        "purpose": "Message brokering, RPC, webhooks, IPC, protocol negotiation",
        "triggers": "inter-worm communication, external integrations",
        "feeds_into": ["orchestration", "telemetry"],
        "icon": "[envelope]",
    },
    "learning": {
        "purpose": "RL training, model versioning, data pipelines, A/B testing",
        "triggers": "scheduled training, data availability",
        "feeds_into": ["visualization", "orchestration"],
        "icon": "[robot]",
    },
    "visualization": {
        "purpose": "Dashboard generation, graph rendering, report compilation",
        "triggers": "data availability, scheduled reporting",
        "feeds_into": ["orchestration"],
        "icon": "[palette]",
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
        self.worms: dict[str, type] = {}  # {class_name: class}
        self.instances: dict[str, Any] = {}  # {class_name: instance}
        self.results: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._parallel = False
        self._timeout = 60
        self._max_retries = 3  # overridden by per-nature config in execute()
        self.definition = NATURE_DEFINITIONS.get(nature, {})
        self._failed_executions: list[dict] = []  # dead letter queue (no-breaker mode)
    
    # ── Dead Letter Queue Management ────────────────────────────────

    def _record_failure(self, name: str, worm_result: dict[str, Any],
                        breaker_state: (str | None) = None):
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
    def get_failed_executions(self, since: float = 0) -> list[dict]:
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
    def retry_failed_worms(self, max_retries: int = 2) -> dict[str, Any]:  # type: ignore[return-value]
        """Retry all failed worms from the dead letter queue.

        Iterates over _failed_executions, re-executes each worm,
        and removes successful retries from the queue.

        Args:
            max_retries: How many times to retry each failed worm
                         (0=clear without retrying)

        Returns:
            Dict with retry_count, success_count, still_failed, and errors.
        """
        results: dict[str, Any] = {
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
        seen_worms: dict[str, dict] = {}
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
    def execute(self, worm_names: (list[str] | None) = None) -> NatureResult:
        """
        Execute all worms (or a subset) in this Nature.
        
        Args:
            worm_names: Specific worm names to execute (None = all)
        
        Returns:
            NatureResult with per-worm results and aggregate stats.
        """
        if not self.worms:
            self.discover_worms()
        
        targets = list(self.worms.items())
        if worm_names:
            targets = [(n, c) for n, c in targets if n in worm_names]
        
        result = NatureResult(
            nature=self.nature,
            cluster_id=self.cluster_id,
            started_at=datetime.now().isoformat(),
        )
        
        start = time.perf_counter()
        
        # Sort by priority from registry
        targets.sort(key=lambda x: WORM_REGISTRY.get(x[0], {}).get("priority", 5), reverse=True)
        
        # Fast path: if ALL worms are cached, skip thread pool AND DM writes entirely.
        # Each ThreadPoolExecutor creation costs ~25ms; 17 natures × 25ms = ~425ms.
        # Each DM SQLite write costs 5-17ms; 17 × 2 writes = ~200ms.
        # Checking the cache synchronously before dispatch saves both overheads.
        if self._all_worms_cached(targets):
            with _worm_cache_lock:
                for name, _ in targets:
                    cache_entry = _worm_result_cache.get(name)
                    if cache_entry is not None:
                        _, cached_result = cache_entry  # unpack (timestamp, result_dict)
                    else:
                        cached_result = {"success": False, "error": "cache miss (TOCTOU)"}
                    result.worm_results[name] = cached_result
                    if cached_result.get("success", False):
                        result.success_count += 1
                    else:
                        result.failure_count += 1
            result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
            result.completed_at = datetime.now().isoformat()
            result.all_cached = True  # Signal to MetaCluster: skip routing + DM
            # Structured JSON log — cache-hit (observability for warm-path runs)
            log = _get_log()
            if log:
                log.debug("nature_execute_cached", {
                    "nature": self.nature, "worms": len(targets),
                    "duration_ms": result.duration_ms,
                })
            for name, _ in targets:
                mark_spawned(name)
            # Skip DM writes entirely for cache-hit natures — nothing executed.
            # MetaCluster still records orchestrate_start/complete for observability.
            return result
        
        # Apply per-nature config overrides from azazael.yaml.
        # Placed AFTER the cache-hit fast-path to avoid unnecessary YAML
        # lookups on warm runs (saves ~1ms per nature on the 6-15ms floor).
        # CLUSTERWORMS.build_from_nature() already does this, but the primary
        # orchestration path (MetaCluster → NatureClusterManager → execute())
        # bypasses CLUSTERWORMS, so we must also apply overrides here.
        cfg = _get_config()
        if cfg:
            try:
                nature_cfg = cfg.get_nature_config(self.nature)
                merged = nature_cfg.merge_with_cluster(cfg.clusters)
                self._parallel = merged["parallel"]
                self._timeout = merged["timeout"]
                self._max_retries = merged["max_retries"]
            except Exception:
                import warnings
                warnings.warn(f"Per-nature config for '{self.nature}' failed — using defaults")
        
        # Record nature execution start to DirectMemory (only when actually executing)
        dm = _get_dm()
        if dm:
            try:
                dm.record("nature_execute_start", {
                    "nature": self.nature,
                    "worm_count": len(self.worms),
                    "parallel": self._parallel,
                }, tags=["nature", self.nature, "start"])
            except Exception:
                pass
        
        if self._parallel and len(targets) > 1:
            self._execute_parallel(targets, result)
        else:
            self._execute_sequential(targets, result)
        
        result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        result.completed_at = datetime.now().isoformat()
        
        # Mark all as spawned
        for name, _ in targets:
            mark_spawned(name)
        
        self._record("nature_cluster_executed", {
            "nature": self.nature, "worms": len(targets),
            "success": result.success_count, "failures": result.failure_count,
            "duration_ms": result.duration_ms,
        })
        
        # Record nature execution complete to DirectMemory
        if dm:
            try:
                dm.record("nature_execute_complete", {
                    "nature": self.nature,
                    "worms": len(targets),
                    "ok": result.success_count,
                    "fail": result.failure_count,
                    "duration_ms": result.duration_ms,
                    "errors": result.errors,
                }, severity="error" if result.failure_count > 0 else "info",
                   tags=["nature", self.nature, "complete"])
            except Exception:
                pass
        
        return result
    def _all_worms_cached(self, targets: list[tuple[str, type]]) -> bool:
        """Check if all target worms have valid cached results.

        Returns True only if every worm is in _worm_result_cache with a
        non-expired TTL (using the worm's declared cooldown). Thread-safe.
        """
        if not targets:
            return False
        with _worm_cache_lock:
            for name, _ in targets:
                cache_entry = _worm_result_cache.get(name)
                if cache_entry is None:
                    return False
                cached_time, _ = cache_entry
                cooldown = WORM_REGISTRY.get(name, {}).get("cooldown_seconds", _WORM_CACHE_TTL)
                if time.time() - cached_time >= cooldown:
                    return False
        return True

    def _execute_sequential(self, targets: list[tuple[str, type]], result: NatureResult):
        """Execute worms one at a time, with circuit breaker protection."""
        # Import once (not per-worm) to avoid loop overhead
        try:
            from CORE.metrics import record_worm_execution
            _track_metrics = True
        except ImportError:
            _track_metrics = False
        for name, cls in targets:
            worm_result = self._execute_single_worm(name, cls)
            result.worm_results[name] = worm_result
            # Per-worm metrics tracking — skip cached results to avoid double-counting
            if _track_metrics and not worm_result.get("cached"):
                record_worm_execution(
                    name,
                    success=worm_result.get("success", False),
                    duration_ms=worm_result.get("duration_ms", 0),
                    error=worm_result.get("error"),
                )
            if worm_result.get("success", False):
                result.success_count += 1
            else:
                result.failure_count += 1
                result.errors.append(f"{name}: {worm_result.get('error', 'unknown')}")
    def _execute_parallel(self, targets: list[tuple[str, type]], result: NatureResult):
        """Execute worms in parallel using thread pool."""
        # Import once (not per-worm) to avoid loop overhead
        try:
            from CORE.metrics import record_worm_execution
            _track_metrics = True
        except ImportError:
            _track_metrics = False
        futures = {}
        with ThreadPoolExecutor(max_workers=min(len(targets), 8)) as executor:
            for name, cls in targets:
                fut = executor.submit(self._execute_single_worm, name, cls)
                futures[fut] = name
            
            for fut in as_completed(futures.keys()):
                name = futures[fut]
                try:
                    worm_result = fut.result(timeout=self._timeout)
                except Exception as e:
                    worm_result = {"success": False, "error": str(e)}
                
                result.worm_results[name] = worm_result
                # Per-worm metrics tracking — skip cached results to avoid double-counting
                if _track_metrics and not worm_result.get("cached"):
                    record_worm_execution(
                        name,
                        success=worm_result.get("success", False),
                        duration_ms=worm_result.get("duration_ms", 0),
                        error=worm_result.get("error"),
                    )
                if worm_result.get("success", False):
                    result.success_count += 1
                else:
                    result.failure_count += 1
                    result.errors.append(f"{name}: {worm_result.get('error', 'unknown')}")
    def _execute_single_worm(self, name: str, cls: type) -> dict[str, Any]:
        """Execute a single worm (used by parallel executor).
        
        Uses a module-level result cache with per-worm TTL matching the
        worm's declared cooldown_seconds (from @register_worm), falling
        back to 5.0s. Monitor nature worms (SystemZ=15s, DBMonitor=60s,
        etc.) stay cached for their natural refresh intervals, eliminating
        redundant system calls on warm orchestration runs.
        
        When circuit breaker is enabled, wraps execution in breaker
        protection with exponential backoff retry.
        Uses lazy config/breaker imports.
        
        Failed executions are ALWAYS recorded to the internal dead letter
        queue (_failed_executions) regardless of circuit breaker availability.
        """
        # Check result cache (lock-guarded for 3.14t free-threading).
        # Uses worm's declared cooldown as TTL: SystemZ gets 15s,
        # DatabaseMonitorWorm gets 60s, etc. Falls back to 5.0s.
        with _worm_cache_lock:
            cache_entry = _worm_result_cache.get(name)
            if cache_entry is not None:
                cached_time, cached_result = cache_entry
                cooldown = WORM_REGISTRY.get(name, {}).get("cooldown_seconds", _WORM_CACHE_TTL)
                if time.time() - cached_time < cooldown:
                    # Mark as cached so callers skip metrics double-counting
                    result = dict(cached_result)
                    result["cached"] = True
                    return result
        
        breakers = _get_breakers()
        cfg = _get_config()
        log = _get_log()
        
        if breakers:
            breaker = breakers.get(name)
            max_retries = self._max_retries
            def _do_execute():
                instance = self._get_or_create_instance(name, cls)
                return self._run_worm_method(name, instance, timeout=self._timeout)
            
            try:
                result = breaker.retry_with_backoff(_do_execute, max_retries=max_retries)
                # Cache successful results (TTL = worm's cooldown_seconds)
                if result.get("success"):
                    with _worm_cache_lock:
                        _worm_result_cache[name] = (time.time(), result)
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
        worm_result = self._run_worm_method(name, instance, timeout=self._timeout)
        
        # Cache successful results (TTL = worm's cooldown_seconds) (lock-guarded for 3.14t)
        if worm_result.get("success"):
            with _worm_cache_lock:
                _worm_result_cache[name] = (time.time(), worm_result)
        
        # Record failed executions to local dead letter queue
        if not worm_result.get("success"):
            self._record_failure(name, worm_result)
            if log:
                log.warning("worm_failed_no_breaker", {
                    "worm": name, "error": worm_result.get('error')
                })
        
        # Record per-worm result to DirectMemory
        dm = _get_dm()
        if dm:
            try:
                dm.record("worm_executed", {
                    "worm": name,
                    "nature": self.nature,
                    "success": worm_result.get("success", False),
                    "method": worm_result.get("method", "?"),
                    "error": worm_result.get("error"),
                }, severity="error" if not worm_result.get("success") else "info",
                   tags=["worm", name, self.nature])
            except Exception:
                pass
        
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
    
    def _run_worm_method(self, name: str, instance: Any, timeout: int = 30) -> dict[str, Any]:
        """Run the appropriate method on a worm instance.

        Wraps execution in a single-worker ThreadPoolExecutor with a
        timeout to prevent any single worm from hanging the entire
        nature execution. On timeout, the pool is shut down non-blocking
        (wait=False) to avoid teardown itself hanging on a stuck thread.
        Pattern: same as CLUSTERWORMS.py WormExecutor._execute_direct().
        """
        if instance is None:
            return {"success": False, "error": "Failed to instantiate"}
        
        # Try common method names in priority order
        methods = ["get_summary", "get_status", "run", "execute", "scan", "check", "analyze"]
        
        for method_name in methods:
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)

                def _call():
                    result = method()
                    if hasattr(result, "__dict__"):
                        result = result.__dict__
                    return {"success": True, "method": method_name, "result": result}

                pool = ThreadPoolExecutor(max_workers=1)
                try:
                    future = pool.submit(_call)
                    return future.result(timeout=timeout)
                except FutureTimeoutError:
                    pool.shutdown(wait=False)
                    return {"success": False, "error": f"Worm {name}.{method_name}() timed out after {timeout}s", "method": method_name}
                except Exception as e:
                    pool.shutdown(wait=False)
                    return {"success": False, "error": str(e), "method": method_name}
                finally:
                    try:
                        pool.shutdown(wait=False)
                    except Exception:
                        pass
        
        return {"success": False, "error": f"No standard method found on {name}"}
    
    # ── Status ─────────────────────────────────────────────────────
    
    def get_status(self) -> dict[str, Any]:
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
    
    def get_worm_info(self) -> list[dict[str, Any]]:
        """Get detailed info about each worm in this cluster."""
        info_list: list[dict[str, Any]] = []
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
    
    def _record(self, event_type: str, data: dict[str, Any]):
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


__all__ = ['CrossNatureRoute', 'NATURE_DEFINITIONS', 'NatureCluster', 'NatureClusterManager', 'NatureResult', 'main']

# ═══════════════════════════════════════════════════════════════════════
# NATURE CLUSTER MANAGER — Orchestrates All Natures
# ═══════════════════════════════════════════════════════════════════════

@register_worm(category="orchestration", priority=9, cooldown_seconds=10.0,
    description="Nature-based cluster manager — dynamically groups worms by Nature, executes by need, records to PAMS")
class NatureClusterManager(BaseWormMixin):
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
        self.clusters: dict[str, NatureCluster] = {}
        self._lock = threading.RLock()
        self._execution_history: list[dict] = []
        self._diversity: (SpawnDiversityEngine | None) = (
            SpawnDiversityEngine() if SpawnDiversityEngine else None        )
    
    # ── Discovery ──────────────────────────────────────────────────
    
    def discover_all_natures(self) -> dict[str, int]:
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
    def get_cluster(self, nature: str) -> (NatureCluster | None):
        """Get or create a cluster for a given Nature."""
        with self._lock:
            if nature not in self.clusters:
                cluster = NatureCluster(nature)
                cluster.discover_worms()
                if cluster.worms:
                    self.clusters[nature] = cluster
            return self.clusters.get(nature)
    
    # ── Dead Letter Queue Management (Aggregated) ─────────────────

    def get_dead_letter_summary(self, lookback_seconds: float = 3600) -> dict[str, Any]:
        """Get an aggregated summary of failed executions across ALL natures.

        Combines individual NatureCluster DLQs into a single view with
        per-worm deduplication and per-nature breakdown.

        Args:
            lookback_seconds: How far back to include (default 1 hour)

        Returns:
            Dict with total_failed, per_nature, per_worm, and recent_errors.
        """
        since = time.time() - lookback_seconds
        summary: dict[str, Any] = {
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
                worm_counts: dict[str, int] = {}
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
    def retry_all_failed_worms(self, max_retries: int = 2) -> dict[str, Any]:
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
                    results["per_nature"][nature] = cluster_result  # type: ignore[index]
                    results["total_retried"] += cluster_result["retried"]
                    results["total_succeeded"] += cluster_result["succeeded"]
                    results["still_failed"] += cluster_result["still_failed"]
                    results["errors"].extend(cluster_result["errors"])

        return results

    # ── Execution ──────────────────────────────────────────────────
    
    def execute_nature(self, nature: str, parallel: bool = False) -> (NatureResult | None):
        """Execute all worms in a given Nature.

        Creates or retrieves the NatureCluster for the given nature
        and runs all worms. Per-nature config overrides (timeout,
        parallel, max_retries from azazael.yaml) are applied by the
        underlying NatureCluster.execute() call.

        Args:
            nature: Nature name (e.g., 'monitor', 'security').
            parallel: If True, execute worms in parallel. Note: if
                      azazael.yaml has a per-nature parallel override,
                      the YAML value in NatureCluster.execute() takes
                      precedence.

        Returns:
            NatureResult with per-worm results and aggregate counts,
            or None if the nature has no registered worms.
        """
        cluster = self.get_cluster(nature)
        if not cluster:
            return None
        
        cluster.set_parallel(parallel)
        result = cluster.execute()
        
        with self._lock:
            self._execution_history.append({
                "nature": nature, "success": result.success_count,
                "failures": result.failure_count,
                "duration_ms": result.duration_ms,
                "timestamp": datetime.now().isoformat(),
            })
        
        return result
    def execute_all_natures(self, parallel_natures: bool = False, 
                            parallel_worms: bool = False) -> dict[str, NatureResult]:
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
    def execute_priority_natures(self, max_natures: int = 3) -> dict[str, NatureResult]:
        """
        Execute Natures scored by priority: what needs attention most.
        Uses system state + nature definitions + diversity engine.
        """
        scores = self._score_natures()
        top_natures: list[str] = sorted(scores, key=scores.get, reverse=True)[:max_natures]  # type: ignore[arg-type]
        
        results = {}
        for nature in top_natures:
            result = self.execute_nature(nature)
            if result:
                results[nature] = result
        
        return results
    def _score_natures(self) -> dict[str, float]:
        """Score each Nature based on system state and urgency."""
        scores: dict[str, float] = {}
        
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
            if cpu > 60 and nature == "profiling":
                score += 8.0
            if mem > 85 and nature in ("monitor", "profiling"):
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
    
    def get_cross_nature_routes(self) -> list[CrossNatureRoute]:
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
    def route_results(self, from_results: dict[str, NatureResult],
                      route: CrossNatureRoute) -> dict[str, Any]:
        """Route data from one Nature's results to another's inputs."""
        routed = {"from": route.from_nature, "to": route.to_nature, "data": {}}
        
        source = from_results.get(route.from_nature)
        if not source:
            return routed
        
        # Collect all worm results as routing data
        for worm_name, worm_result in source.worm_results.items():
            if isinstance(worm_result, dict):
                routed["data"][worm_name] = worm_result.get("result", worm_result)  # type: ignore[index]
        
        return routed
    
    # ── Status ─────────────────────────────────────────────────────
    
    def get_status(self) -> dict[str, Any]:
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
    
    def list_all_worms(self) -> dict[str, list[str]]:
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
        lines.append("    title[\"[globe] AZAZAEL NATURE CLUSTERS\"]")
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
    
    def _record(self, event_type: str, data: dict[str, Any]):
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
                status = "OK" if wr.get("success") else "FAIL"  # type: ignore[assignment]
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
