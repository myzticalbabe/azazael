# coding: utf-8
"""
METACLUSTER — MetaCluster Orchestrator (Cluster-of-Clusters)

Meta-level orchestrator that manages registry categories as a unified fleet.
U3/D1: the nature taxonomy is gone. A MetaCluster coordinates CATEGORIES —
flat registry dispatch, no cross-nature routing, no feeds_into topology.

Architecture:
    MetaCluster (top-level orchestrator)
    ├── Category("monitor")     → monitor worms (from registry)
    ├── Category("diagnostic")  → diagnostic worms
    └── ... (all registry categories, flat)

    MetaClusterState (shared state across all categories)
    ├── Results aggregation
    ├── Insight generation
    └── PAMS recording of every action

Public surface is unchanged (orchestrate/discover_all/get_status/mermaid/
hooks/history); the `natures` parameters now take category names. Result and
state field names keep their keys so chain/state readers do not break.

Usage:
    >>> from CORE.WORMS.METACLUSTER import MetaCluster
    >>> mc = MetaCluster()
    >>> mc.discover_all()              # Auto-discover all categories
    >>> results = mc.orchestrate()     # Run priority categories end-to-end
    >>> print(mc.to_mermaid())         # Visualize the meta-cluster
"""

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field

# ── Flat registry dispatch (U3/D1) ─────────────────────────────────
# No NatureClusterManager, no CrossNatureRoutingEngine: both were deleted
# with the taxonomy. Categories come straight from the worm registry.
try:
    from CORE.worm_registry import (
        register_worm, WORM_REGISTRY, discover_worms,
        get_all_categories, get_worms_by_category, mark_spawned,
    )
    _REGISTRY_OK = True
except ImportError:
    _REGISTRY_OK = False
    WORM_REGISTRY = {}
    def discover_worms(worms_dir: Optional[str] = None, progress_callback: Optional[Callable] = None) -> int: return 0
    def get_all_categories() -> Set[str]: return set()
    def get_worms_by_category(category: str) -> Dict[str, Dict]: return {}
    def mark_spawned(name: str) -> Any: pass
    def register_worm(category: str = "", priority: int = 0, cooldown_seconds: float = 0, description: str = "", tags: Optional[set[str]] = None, **kwargs: Any) -> Callable[..., Any]: return lambda f: f
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
                    _pams = False
    return _pams if _pams else None


# ── MemoryBus (lazy, thread-safe) ────────────────────────────────────
_mem_bus: Any = None
_mem_bus_lock = threading.Lock()
def _get_mem_bus():
    """Lazy MemoryBus — double-checked locking for Python 3.14t free-threading."""
    global _mem_bus
    if _mem_bus is None:
        with _mem_bus_lock:
            if _mem_bus is None:
                try:
                    from CORE.MemoryBus import MemoryBus
                    _mem_bus = MemoryBus()
                except ImportError:
                    _mem_bus = False
    return _mem_bus if _mem_bus else None

# ── Free-Threading ─────────────────────────────────────────────────
try:
    from CORE.freethreading import is_free_threaded
    _FREETHREAD_OK = True
except ImportError:
    _FREETHREAD_OK = False
    def is_free_threaded() -> bool:
        try:
            return not sys._is_gil_enabled()
        except Exception:
            return False

# ── Config (lazy, thread-safe) ─────────────────────────────────
_cfg: Any = None
_cfg_lock = threading.Lock()
def _get_config():
    """Lazy config — double-checked locking for Python 3.14t free-threading."""
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


# ── Circuit Breaker (lazy, thread-safe) ────────────────────────────
_breaker_registry: Any = None
_breaker_lock = threading.Lock()
def _get_breakers():
    """Lazy BreakerRegistry — double-checked locking for Python 3.14t free-threading."""
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
    """Lazy structured logger — double-checked locking for Python 3.14t free-threading."""
    global _logger
    if _logger is None:
        with _logger_lock:
            if _logger is None:
                try:
                    from CORE.azazael_logging import get_logger
                    _logger = get_logger("MetaCluster")
                except ImportError:
                    _logger = False
    return _logger if _logger else None


# ═══════════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class MetaClusterResult:
    """Aggregate result from a MetaCluster orchestration run."""
    orchestration_id: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    natures_executed: int = 0
    total_worms_ok: int = 0
    total_worms_fail: int = 0
    nature_results: Dict[str, Any] = field(default_factory=dict)
    routed_data: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    cross_nature_paths_used: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class MetaClusterState:
    """Shared state across all clusters in a MetaCluster run."""
    run_id: str = ""
    started_at: str = ""
    phase: str = "idle"  # idle, discovering, executing, routing, analyzing, complete
    active_natures: Set[str] = field(default_factory=set)
    completed_natures: Set[str] = field(default_factory=set)
    failed_natures: Set[str] = field(default_factory=set)
    worm_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # {nature: {worm: result}}
    routed_messages: List[Dict] = field(default_factory=list)
    events: List[Dict] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock)


# NOTE: CrossNatureRoutingEngine lived in CORE.WORMS.CROSS_NATURE_ROUTER,
# deleted with the taxonomy (U3/D7). Nothing routes between categories.


# ═══════════════════════════════════════════════════════════════════════
# META CLUSTER — The Top-Level Orchestrator
# ═══════════════════════════════════════════════════════════════════════

@register_worm(category="orchestration", priority=10, cooldown_seconds=5.0,
    description="MetaCluster — cluster-of-clusters orchestrator coordinating all registry categories with flat dispatch and PAMS recording")
class MetaCluster:
    """
    MetaCluster — the top-level orchestrator that manages clusters of clusters.
    
    Coordinates registry categories with flat dispatch, generates insights,
    and records every action to PAMS memory.
    
    Usage:
        mc = MetaCluster()
        mc.discover_all()
        
        # Run a single category end-to-end
        result = mc.orchestrate_nature("security")
        
        # Run multiple categories
        result = mc.orchestrate(natures=["security", "defense", "monitor"])
        
        # Run with auto-prioritization
        result = mc.orchestrate_adaptive(max_natures=5)
        
        # Visualize
        print(mc.to_mermaid())
        print(mc.to_mermaid_execution_flow())
    """
    
    VERSION = "2.0.0"
    
    def __init__(self):
        self.categories: Dict[str, List[str]] = {}
        self.state: Optional[MetaClusterState] = None
        self._history: List[MetaClusterResult] = []
        self._lock = threading.RLock()
        self._hooks: Dict[str, List[Callable]] = {
            "pre_nature": [],
            "post_nature": [],
            "on_insight": [],
            "on_error": [],
        }
    
    # ── Discovery ──────────────────────────────────────────────────
    
    def discover_all(self) -> Dict[str, int]:
        """Discover all registry categories from the worm registry."""
        try:
            discover_worms()
        except Exception:
            pass
        counts = {c: len(get_worms_by_category(c))
                  for c in sorted(get_all_categories())}
        self.categories = {c: sorted(get_worms_by_category(c))
                           for c in counts}
        _record_event("metacluster_discovery", {
            "natures": len(counts),
            "total_worms": sum(counts.values()),
            "per_nature": counts,
        })
        return counts
    
    # ── Hooks ──────────────────────────────────────────────────────
    
    def on(self, hook_name: str, callback: Callable):
        """Register a hook callback. Supports: pre_nature, post_nature, on_insight, on_error."""
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)

    def _run_hooks(self, hook_name: str, **kwargs):
        """Run all registered hooks for a given hook point."""
        for cb in self._hooks.get(hook_name, []):
            try:
                cb(**kwargs)
            except Exception:
                pass
    
    # ── Orientation ────────────────────────────────────────────────
    
    def orchestrate(self, natures: Optional[List[str]] = None,
                    parallel: bool = False, max_natures: int = 0) -> MetaClusterResult:
        """
        Orchestrate a set of registry categories end-to-end (U3: `natures`
        takes category names; kept for caller compatibility).
        
        Args:
            natures: Specific categories to execute (None = auto-discover all)
            parallel: Execute categories in parallel where possible
            max_natures: Limit to top-N categories by priority weight
        
        Returns:
            MetaClusterResult with full execution details and insights.
        """
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
        # Initialize state
        orchestration_id = f"meta_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:6]}"
        self.state = MetaClusterState(
            run_id=orchestration_id,
            started_at=datetime.now().isoformat(),
            phase="discovering",
        )
        
        start = time.perf_counter()
        
        # Phase 1: Discover
        if not self.categories:
            self.discover_all()
        
        # Determine categories to execute
        if natures is None:
            natures = sorted(self.categories.keys())
        
        if max_natures > 0:
            ranked = self._rank_categories(natures)
            # `max_natures` must cap what can actually RUN. A circular
            # category (the orchestration infrastructure itself) is dropped by
            # the filter below, so letting it consume the budget made a
            # request for one category execute ZERO -- and the run still
            # reported `complete`. Same guarantee as the old nature filter.
            eligible = [n for n in ranked if not self._is_circular_category(n)]
            # If EVERY requested category is circular, keep the old selection
            # so the filter below still reports and marks them: an empty
            # request must stay visible as a no-op, never silently replaced.
            natures = (eligible or ranked)[:max_natures]
        
        # Requested order is execution order (no routing topology to sort by).
        execution_order = [n for n in natures if n in self.categories]
        
        # ── Drop circular categories ──────────────────────────────
        # A category holding the orchestration infrastructure would re-enter
        # this method or deadlock. Mark its worms spawned to keep
        # "never spawned" alerts honest.
        circular_natures = [n for n in execution_order if self._is_circular_category(n)]
        if circular_natures:
            execution_order = [n for n in execution_order if n not in circular_natures]
            for nature in circular_natures:
                for worm_name in (self.categories.get(nature) or []):
                    try:
                        mark_spawned(worm_name)
                    except Exception:  # noqa: BLE001 — bookkeeping is best-effort
                        pass

        self.state.phase = "executing"
        self.state.active_natures = set(execution_order)
        
        # Phase 2: Execute categories in order
        cfg = _get_config()
        cfg.clusters.default_timeout if cfg else 60
        cfg.clusters.max_parallel_worms if cfg else 8
        cfg.clusters.max_retries if cfg else 3
        
        nature_results: Dict[str, Any] = {}
        routed_data: Dict[str, Any] = {}
        total_ok = 0
        total_fail = 0
        errors = []

        # A run that executes nothing must SAY so. Everything below is a loop
        # over `execution_order`, so an empty order produced a result object with
        # phase "complete", zero errors and zero categories -- indistinguishable
        # from a clean full pass. `active_natures` is already empty here; this
        # makes it countable by a caller that only reads `errors`.
        if not execution_order:
            errors.append(
                "no category was eligible to execute: the requested set collapsed "
                "to nothing after the orchestration-infrastructure filter "
                "(circular=%s)" % (sorted(circular_natures) or "none"))
        cross_nature_paths = []
        
        log = _get_log()
        _get_breakers()
        
        for nature in execution_order:
            self.state.phase = f"executing_{nature}"
            
            # Pre-hook
            self._run_hooks("pre_nature", nature=nature, state=self.state)
            
            # Execute the category cluster with config-driven timeout
            try:
                cluster = ClusterWORMZ.build_from_registry(
                    sorted(self.categories.get(nature, [])))
                cluster.set_parallel(parallel)
                cluster.execute_all()
                agg = cluster.aggregate_results()
                results = agg.worm_results or {}
                errs = [str((v or {}).get("error", ""))[:100]
                        for v in results.values()
                        if isinstance(v, dict) and not v.get("success", True)
                        and (v or {}).get("error")]
                nature_results[nature] = {
                    "success_count": agg.success_count,
                    "failure_count": agg.failure_count,
                    "duration_ms": agg.duration_ms,
                    "worm_results": results,
                    "errors": errs,
                }
                total_ok += agg.success_count
                total_fail += agg.failure_count
                if errs:
                    errors.extend(errs)
                
                with self.state.lock:
                    self.state.completed_natures.add(nature)
                    self.state.worm_results[nature] = results
                
                if log:
                    log.info("nature_executed", {
                        "nature": nature,
                        "ok": agg.success_count,
                        "fail": agg.failure_count,
                        "duration_ms": agg.duration_ms,
                    })
            except Exception as e:
                with self.state.lock:
                    self.state.failed_natures.add(nature)
                err_msg = f"Nature '{nature}' failed: {str(e)}"
                errors.append(err_msg)
                self._run_hooks("on_error", nature=nature, error=str(e), state=self.state)
                if log:
                    log.error("nature_failed", {"nature": nature, "error": str(e)})
            
            # Post-hook
            self._run_hooks("post_nature", nature=nature, result=nature_results.get(nature), state=self.state)
        
        # Phase 4: Generate insights
        self.state.phase = "analyzing"
        insights = self._generate_insights(nature_results, self.state)
        recommendations = self._generate_recommendations(nature_results, self.state)
        
        for insight in insights:
            self._run_hooks("on_insight", insight=insight, state=self.state)
        
        self.state.phase = "complete"
        
        # Compute duration before any try blocks
        result_duration_ms = round((time.perf_counter() - start) * 1000, 2)
        
        # Record metrics
        try:
            from CORE.metrics import metrics_collector
            metrics_collector.record("metacluster.orchestrate.duration_ms", result_duration_ms)
            metrics_collector.record("metacluster.orchestrate.worms_ok", total_ok)
            metrics_collector.record("metacluster.orchestrate.worms_fail", total_fail)
            metrics_collector.record("metacluster.orchestrate.natures", len(nature_results))
        except Exception:
            pass
        
        # Build result
        result = MetaClusterResult(
            orchestration_id=orchestration_id,
            started_at=self.state.started_at,
            completed_at=datetime.now().isoformat(),
            duration_ms=result_duration_ms,
            natures_executed=len(nature_results),
            total_worms_ok=total_ok,
            total_worms_fail=total_fail,
            nature_results=nature_results,
            routed_data=routed_data,
            insights=insights,
            recommendations=recommendations,
            cross_nature_paths_used=cross_nature_paths,
            errors=errors,
        )
        
        with self._lock:
            self._history.append(result)
            if len(self._history) > 100:
                self._history = self._history[-50:]
        
        _record_event("metacluster_orchestrated", {
            "orchestration_id": orchestration_id,
            "natures": len(nature_results),
            "ok": total_ok, "fail": total_fail,
            "duration_ms": result.duration_ms,
            "insights": len(insights),
        })
        
        return result

    def _rank_categories(self, categories: List[str]) -> List[str]:
        """Priority-weight ranking over registry categories (was _score_natures)."""
        weights: Dict[str, float] = {}
        for category in categories:
            try:
                worms = get_worms_by_category(category)
            except Exception:
                worms = {}
            weights[category] = sum(
                float((info or {}).get("priority", 0)) for info in worms.values())
        return sorted(categories, key=lambda c: weights.get(c, 0.0), reverse=True)

    def _is_circular_nature(self, nature: str, feeds: Optional[Dict[str, List[str]]] = None) -> bool:
        """Report whether executing ``nature`` would be circular.

        Two senses (kept — tests pin both): with `feeds`, reachability over
        that graph (DFS cycle detection); without, the orchestration-safety
        check against the flat registry. U3 kept the name so callers work.
        """
        if feeds is not None:
            return self._reaches_cycle(nature, feeds)
        return self._is_circular_category(nature)

    @staticmethod
    def _reaches_cycle(nature: str, feeds: Dict[str, List[str]]) -> bool:
        """Iterative DFS: does any path out of ``nature`` revisit a node on it?"""
        on_path: Set[str] = set()
        # (node, is_exit) — children are pushed ahead of the exit marker, so a
        # node only leaves the path once its whole subtree has been walked.
        stack: List[tuple] = [(nature, False)]
        while stack:
            node, leaving = stack.pop()
            if leaving:
                on_path.discard(node)
                continue
            if node in on_path:
                return True
            on_path.add(node)
            stack.append((node, True))
            for downstream in feeds.get(node) or []:
                stack.append((downstream, False))
        return False

    def _is_circular_category(self, category: str) -> bool:
        """True when the category holds the orchestration classes themselves.

        Executing those recurses or deadlocks. Matched by module path rather
        than identity so METACLUSTER does not import the orchestrators back,
        which would close an import cycle. (Was _contains_orchestration_
        infrastructure over NCM clusters; now over the flat registry.)
        """
        try:
            worms = get_worms_by_category(category)
        except Exception:
            return False
        orchestrators = {
            "MetaCluster": "METACLUSTER",
            "ClusterWORMZ": "CLUSTERWORMS",
            "ErrorRecoveryOrchestrator": "ERROR_RECOVERY",
        }
        for name, info in worms.items():
            module = str((info or {}).get("module", ""))
            for cls_name, owner in orchestrators.items():
                if name == cls_name or cls_name in module:
                    if owner in module.upper():
                        return True
        return "orchestration" in str(category).lower() and any(
            n in str(worms) for n in ("MetaCluster", "ClusterWORMZ"))

    def orchestrate_nature(self, nature: str, parallel: bool = False) -> Optional[MetaClusterResult]:
        """Orchestrate a single Nature (convenience method)."""
        return self.orchestrate(natures=[nature], parallel=parallel)

    def orchestrate_adaptive(self, max_natures: int = 5,
                             parallel: bool = False) -> MetaClusterResult:
        """
        Adaptive orchestration: automatically select and prioritize Natures
        based on system state, recent execution history, and diversity engine.
        """
        return self.orchestrate(max_natures=max_natures, parallel=parallel)

    def orchestrate_full_pipeline(self, start_nature: str,
                                  parallel: bool = False) -> MetaClusterResult:
        """
        Execute one category end-to-end (U3: was follow-the-routing-graph
        from a start Nature; no graph remains, so this runs the single
        requested category like orchestrate_nature).
        """
        return self.orchestrate(natures=[start_nature], parallel=parallel)
    
    # ── Insights & Recommendations ─────────────────────────────────
    
    def _generate_insights(self, nature_results: Dict[str, Any],
                           state: MetaClusterState) -> List[str]:
        """Generate human-readable insights from execution results."""
        insights = []
        
        total_ok = sum(r.get("success_count", 0) for r in nature_results.values())
        total_fail = sum(r.get("failure_count", 0) for r in nature_results.values())
        total_worms = total_ok + total_fail
        success_rate = (total_ok / max(total_worms, 1)) * 100
        
        if total_worms > 0:
            insights.append(f"Overall success rate: {success_rate:.0f}% ({total_ok}/{total_worms} worms)")
        
        # Per-category insights
        for nature, result in sorted(nature_results.items()):
            n_ok = result.get("success_count", 0)
            n_fail = result.get("failure_count", 0)
            n_total = n_ok + n_fail
            
            if n_fail > 0:
                insights.append(f"⚠️ {nature}: {n_fail}/{n_total} worms failed")
            elif n_total > 0:
                insights.append(f"OK {nature}: all {n_total} worms succeeded")
        
        return insights

    def _generate_recommendations(self, nature_results: Dict[str, Any],
                                  state: MetaClusterState) -> List[str]:
        """Generate actionable recommendations from results."""
        recommendations = []
        
        # Failed categories
        for nature, result in nature_results.items():
            if result.get("failure_count", 0) > 0:
                recommendations.append(f"Investigate failures in '{nature}' category cluster")
        
        # Unused categories
        try:
            all_natures = set(get_all_categories())
        except Exception:
            all_natures = set()
        executed = set(nature_results.keys())
        unused = all_natures - executed
        if unused:
            recommendations.append(f"Consider running unused categories: {', '.join(sorted(unused)[:5])}")
        
        return recommendations
    
    # ── Status ─────────────────────────────────────────────────────
    
    def get_status(self) -> Dict[str, Any]:
        """Get full MetaCluster status."""
        try:
            categories = sorted(get_all_categories())
        except Exception:
            categories = []
        return {
            "version": self.VERSION,
            "categories": len(categories),
            "ncm": {"categories": len(categories)},
            "routing_paths": 0,
            "cross_nature_routes": 0,
            "orchestration_history": len(self._history),
            "last_orchestration": self._history[-1].orchestration_id if self._history else None,
            "free_threaded": is_free_threaded(),
            "hooks_registered": {k: len(v) for k, v in self._hooks.items()},
            "state_phase": self.state.phase if self.state else "idle",
        }
    
    def get_last_result(self) -> Optional[MetaClusterResult]:
        """Get the most recent orchestration result."""
        return self._history[-1] if self._history else None
    
    # ── Mermaid Graphs ─────────────────────────────────────────────
    
    def to_mermaid(self) -> str:
        """
        Generate complete Mermaid graph of the MetaCluster:
        all registry categories and their worms (U3: no routing overlay).
        """
        try:
            categories = sorted(get_all_categories())
        except Exception:
            return "graph TB\n    error[\"registry unavailable\"]"
        lines = ["graph TB"]
        for category in categories:
            try:
                worms = sorted(get_worms_by_category(category))
            except Exception:
                worms = []
            lines.append(f'    {category}["{category}<br/>{len(worms)} worms"]')
            for worm in worms[:20]:
                lines.append(f'    {category} --> {worm}')
        return "\n".join(lines)

    def to_mermaid_execution_flow(self, result: Optional[MetaClusterResult] = None) -> str:
        """
        Generate Mermaid flowchart showing execution order and results
        from the most recent (or specified) orchestration.
        """
        result = result or self.get_last_result()
        if not result:
            return "graph LR\n    empty[\"No orchestration results yet\"]"
        
        lines = ["graph LR"]
        lines.append(f'    title["* MetaCluster Orchestration<br/>{result.orchestration_id}<br/>{result.duration_ms:.0f}ms, {result.total_worms_ok}OK/{result.total_worms_fail}FAIL"]')
        lines.append("    style title fill:#1a1a2e,stroke:#00d9ff,color:#00d9ff")
        lines.append("")
        
        # Nodes for each category
        for nature, n_result in result.nature_results.items():
            ok = n_result.get("success_count", 0)
            fail = n_result.get("failure_count", 0)
            status = "ok" if fail == 0 else "fail"
            color = "#00ff88" if status == "ok" else "#ff4444"
            
            duration = n_result.get('duration_ms', 0)
            lines.append(f'    {nature}["{nature}<br/>{ok}OK {fail}FAIL ({duration:.0f}ms)"]')
            lines.append(f"    style {nature} fill:#16213e,stroke:{color},color:{color}")
        
        return "\n".join(lines)

    def to_mermaid_routing_topology(self) -> str:
        """
        Routing topology (U3: flat dispatch declares no routes).
        Kept so dashboard callers keep working; reports the fact.
        """
        return ("graph TB\n"
                '    title["Flat dispatch — no routing topology"]\n'
                "    style title fill:#1a1a2e,stroke:#00d9ff,color:#00d9ff")

    def to_mermaid_all_functions(self) -> str:
        """
        Generate Mermaid class diagram showing all worm classes and
        their registry categories (U3: flat, ex taxonomy).
        """
        try:
            categories = sorted(get_all_categories())
        except Exception:
            return "classDiagram\n    %% No data"
        lines = ["classDiagram"]
        for category in categories:
            try:
                worms = sorted(get_worms_by_category(category))
            except Exception:
                worms = []
            for worm in worms[:30]:
                lines.append(f"    {category} --> {worm}")
        return "\n".join(lines)
    
    # ── Persistence ────────────────────────────────────────────────
    
    def export_state(self, filepath: str = "") -> str:
        """Export full MetaCluster state to JSON."""
        if not filepath:
            filepath = str(Path.home() / "azazael" / "data" / "metacluster_state.json")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        export = {
            "version": self.VERSION,
            "exported_at": datetime.now().isoformat(),
            "free_threaded": is_free_threaded(),
            "categories": sorted(get_all_categories()) if _REGISTRY_OK else [],
            "routes": [],
            "orchestration_history": [
                {
                    "id": r.orchestration_id,
                    "natures": r.natures_executed,
                    "ok": r.total_worms_ok,
                    "fail": r.total_worms_fail,
                    "duration_ms": r.duration_ms,
                    "insights": r.insights,
                    "recommendations": r.recommendations,
                }
                for r in self._history[-20:]
            ],
        }
        
        with open(filepath, "w") as f:
            json.dump(export, f, indent=2, default=str)
        
        _record_event("metacluster_exported", {"filepath": filepath})
        return filepath

    def __repr__(self):
        natures = len(self.categories)
        history = len(self._history)
        return f"MetaCluster(v{self.VERSION}, {natures} categories, flat, {history} runs)"


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _record_event(event_type: str, data: Dict[str, Any]):
    """Record event to PAMS memory."""
    pams = _get_pams()
    if pams:
        try:
            pams.record_event(
                event_type, data,
                source="MetaCluster",
                severity="info",
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="METACLUSTER — MetaCluster Orchestrator"
    )
    parser.add_argument("--discover", action="store_true", help="Discover all Natures")
    parser.add_argument("--orchestrate", type=str, nargs="*", help="Orchestrate specific Natures")
    parser.add_argument("--adaptive", type=int, default=0, help="Adaptive orchestration with max N Natures")
    parser.add_argument("--pipeline", type=str, help="Run full pipeline from a start Nature")
    parser.add_argument("--parallel", action="store_true", help="Parallel execution")
    parser.add_argument("--mermaid", action="store_true", help="Full Mermaid graph")
    parser.add_argument("--mermaid-flow", action="store_true", help="Execution flow Mermaid graph")
    parser.add_argument("--mermaid-routing", action="store_true", help="Routing topology Mermaid graph")
    parser.add_argument("--mermaid-functions", action="store_true", help="Class diagram Mermaid graph")
    parser.add_argument("--export", type=str, help="Export state to JSON file")
    parser.add_argument("--status", action="store_true", help="Show MetaCluster status")
    
    args = parser.parse_args()
    mc = MetaCluster()
    
    if args.discover:
        counts = mc.discover_all()
        print(f"Discovered {len(counts)} Natures, {sum(counts.values())} worms")
    
    elif args.orchestrate is not None:
        natures = args.orchestrate if args.orchestrate else None
        result = mc.orchestrate(natures=natures, parallel=args.parallel)
        print(f"Orchestrated {result.natures_executed} Natures: {result.total_worms_ok}OK/{result.total_worms_fail}FAIL ({result.duration_ms:.0f}ms)")
        for insight in result.insights:
            print(f"  {insight}")
        for rec in result.recommendations:
            print(f"  {rec}")
    
    elif args.adaptive > 0:
        result = mc.orchestrate_adaptive(max_natures=args.adaptive, parallel=args.parallel)
        print(f"Adaptive: {result.natures_executed} Natures, {result.total_worms_ok}OK/{result.total_worms_fail}FAIL ({result.duration_ms:.0f}ms)")
    
    elif args.pipeline:
        result = mc.orchestrate_full_pipeline(args.pipeline, parallel=args.parallel)
        print(f"Pipeline [{args.pipeline}]: {result.natures_executed} Natures, {result.total_worms_ok}OK/{result.total_worms_fail}FAIL")
        for path in result.cross_nature_paths_used:
            print(f"  {path}")
    
    elif args.mermaid:
        print(mc.to_mermaid())
    
    elif args.mermaid_flow:
        print(mc.to_mermaid_execution_flow())
    
    elif args.mermaid_routing:
        print(mc.to_mermaid_routing_topology())
    
    elif args.mermaid_functions:
        print(mc.to_mermaid_all_functions())
    
    elif args.export:
        path = mc.export_state(args.export)
        print(f"Exported to: {path}")
    
    elif args.status:
        import json
        print(json.dumps(mc.get_status(), indent=2, default=str))
    
    else:
        print("METACLUSTER v" + MetaCluster.VERSION)
        print()
        print("Usage:")
        print("  --discover                   Discover all Natures")
        print("  --orchestrate [NATURES...]   Orchestrate specific Natures")
        print("  --adaptive N                 Adaptive orchestration (max N Natures)")
        print("  --pipeline NATURE            Execute full routing pipeline")
        print("  --parallel                   Use parallel execution")
        print("  --mermaid                    Full Mermaid graph")
        print("  --mermaid-flow               Execution flow graph")
        print("  --mermaid-routing            Routing topology")
        print("  --mermaid-functions          Class diagram")
        print("  --export PATH                Export state to JSON")
        print("  --status                     Show status")


if __name__ == "__main__":
    main()
