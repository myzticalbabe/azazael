# Forked from src/CORE/WORMS/NATURE_CLUSTERS.py on 2026-05-29 for azazael-core standalone package.
# Sync changes from canonical source when updating.
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

import os
import sys
import json
import time
import hashlib
import threading
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Worm Registry ──────────────────────────────────────────────────
try:
    from azazael_core.worm_registry import (
        register_worm, WORM_REGISTRY, get_worms_by_category,
        get_all_categories, discover_worms, mark_spawned,
        SpawnDiversityEngine,
    )
    _REGISTRY_OK = True
except ImportError:
    _REGISTRY_OK = False
    WORM_REGISTRY = {}
    def get_worms_by_category(c): return {}
    def get_all_categories(): return set()
    def discover_worms(): return 0
    def mark_spawned(t): pass
    SpawnDiversityEngine = None
    def register_worm(**kw): return lambda cls: cls

# ── PAMS Memory Recording ──────────────────────────────────────────
try:
    from CORE.PamsRecorder import PamsRecorder
    _pams = PamsRecorder()
    _PAMS_OK = True
except ImportError:
    _PAMS_OK = False
    _pams = None

# ── Free-Threading ─────────────────────────────────────────────────
try:
    from azazael_core.freethreading import is_free_threaded, FreeThreadPool
    _FREETHREAD_OK = True
except ImportError:
    _FREETHREAD_OK = False
    FreeThreadPool = None
    def is_free_threaded():
        try:
            return not sys._is_gil_enabled()
        except Exception:
            return False


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
        "icon": "📊",
    },
    "diagnostic": {
        "purpose": "Deep system analysis and problem diagnosis",
        "triggers": "anomalies detected, health degradation",
        "feeds_into": ["repair", "defense", "orchestration"],
        "icon": "🔍",
    },
    "analysis": {
        "purpose": "Code and data pattern analysis",
        "triggers": "new code, scheduled scans, exploration",
        "feeds_into": ["optimization", "defense", "visualization"],
        "icon": "🧠",
    },
    "defense": {
        "purpose": "Error detection, health checks, security auditing",
        "triggers": "errors above threshold, security alerts",
        "feeds_into": ["repair", "orchestration", "telemetry"],
        "icon": "🛡️",
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
        "icon": "🎯",
    },
    "sync": {
        "purpose": "Time synchronization, clock management, scheduling",
        "triggers": "time drift, scheduled intervals",
        "feeds_into": ["monitor", "orchestration"],
        "icon": "🕐",
    },
    "repair": {
        "purpose": "Automated code repair and auto-fix application",
        "triggers": "errors detected, defense alerts",
        "feeds_into": ["defense", "orchestration"],
        "icon": "🔧",
    },
    "security": {
        "purpose": "Vulnerability scanning, port auditing, cert monitoring",
        "triggers": "new deployments, scheduled security audits",
        "feeds_into": ["defense", "orchestration", "telemetry"],
        "icon": "🔒",
    },
    "profiling": {
        "purpose": "Code profiling, memory leak detection, bottleneck analysis",
        "triggers": "performance degradation, scheduled profiling",
        "feeds_into": ["optimization", "visualization", "telemetry"],
        "icon": "📈",
    },
    "telemetry": {
        "purpose": "Span tracing, metric aggregation, event routing, alerting",
        "triggers": "always active — continuous telemetry pipeline",
        "feeds_into": ["visualization", "orchestration", "defense"],
        "icon": "📡",
    },
    "container": {
        "purpose": "Container lifecycle, compose validation, image auditing",
        "triggers": "container deployments, registry updates",
        "feeds_into": ["monitor", "security", "orchestration"],
        "icon": "📦",
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
        "icon": "💾",
    },
    "migration": {
        "purpose": "Code migration, dependency upgrades, schema versioning",
        "triggers": "version bumps, scheduled upgrades",
        "feeds_into": ["analysis", "orchestration"],
        "icon": "🚚",
    },
    "communication": {
        "purpose": "Message brokering, RPC, webhooks, IPC, protocol negotiation",
        "triggers": "inter-worm communication, external integrations",
        "feeds_into": ["orchestration", "telemetry"],
        "icon": "📨",
    },
    "learning": {
        "purpose": "RL training, model versioning, data pipelines, A/B testing",
        "triggers": "scheduled training, data availability",
        "feeds_into": ["optimization", "visualization", "orchestration"],
        "icon": "🤖",
    },
    "visualization": {
        "purpose": "Dashboard generation, graph rendering, report compilation",
        "triggers": "data availability, scheduled reporting",
        "feeds_into": ["orchestration"],
        "icon": "🎨",
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
    
    # ── Discovery ──────────────────────────────────────────────────
    
    def discover_worms(self) -> int:
        """
        Auto-discover worms of this Nature from WORM_REGISTRY.
        Returns count of worms found.
        """
        if not _REGISTRY_OK:
            return 0
        
        # Trigger discovery first
        discover_worms()
        
        category_worms = get_worms_by_category(self.nature)
        
        with self._lock:
            count = 0
            for name, info in category_worms.items():
                cls = info.get("class")
                if cls and inspect.isclass(cls):
                    self.worms[name] = cls
                    count += 1
        
        self._record("nature_cluster_discovery", {
            "nature": self.nature, "worms_found": count,
            "worm_names": list(self.worms.keys()),
        })
        return count
    
    def add_worm_manual(self, name: str, cls: type):
        """Manually add a worm class to this cluster."""
        with self._lock:
            self.worms[name] = cls
    
    # ── Execution ──────────────────────────────────────────────────
    
    def set_parallel(self, enabled: bool):
        self._parallel = enabled
    
    def set_timeout(self, seconds: int):
        self._timeout = seconds
    
    def execute(self, worm_names: Optional[List[str]] = None) -> NatureResult:
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
        
        return result
    
    def _execute_sequential(self, targets: List[Tuple[str, type]], result: NatureResult):
        """Execute worms one at a time."""
        for name, cls in targets:
            try:
                instance = self._get_or_create_instance(name, cls)
                worm_result = self._run_worm_method(name, instance)
                result.worm_results[name] = worm_result
                if worm_result.get("success", False):
                    result.success_count += 1
                else:
                    result.failure_count += 1
                    result.errors.append(f"{name}: {worm_result.get('error', 'unknown')}")
            except Exception as e:
                result.worm_results[name] = {"success": False, "error": str(e)}
                result.failure_count += 1
                result.errors.append(f"{name}: {str(e)}")
    
    def _execute_parallel(self, targets: List[Tuple[str, type]], result: NatureResult):
        """Execute worms in parallel using thread pool."""
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
                if worm_result.get("success", False):
                    result.success_count += 1
                else:
                    result.failure_count += 1
                    result.errors.append(f"{name}: {worm_result.get('error', 'unknown')}")
    
    def _execute_single_worm(self, name: str, cls: type) -> Dict[str, Any]:
        """Execute a single worm (used by parallel executor)."""
        instance = self._get_or_create_instance(name, cls)
        return self._run_worm_method(name, instance)
    
    def _get_or_create_instance(self, name: str, cls: type) -> Any:
        """Get cached instance or create new one."""
        with self._lock:
            if name not in self.instances:
                try:
                    self.instances[name] = cls()
                except Exception:
                    self.instances[name] = None
            return self.instances[name]
    
    def _run_worm_method(self, name: str, instance: Any) -> Dict[str, Any]:
        """Run the appropriate method on a worm instance."""
        if instance is None:
            return {"success": False, "error": "Failed to instantiate"}
        
        # Try common method names in priority order
        methods = ["get_summary", "get_status", "run", "execute", "scan", "check", "analyze"]
        
        for method_name in methods:
            if hasattr(instance, method_name):
                try:
                    method = getattr(instance, method_name)
                    result = method()
                    # Convert to dict if dataclass
                    if hasattr(result, "__dict__"):
                        result = result.__dict__
                    return {"success": True, "method": method_name, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e), "method": method_name}
        
        return {"success": False, "error": f"No standard method found on {name}"}
    
    # ── Status ─────────────────────────────────────────────────────
    
    def get_status(self) -> Dict[str, Any]:
        """Get cluster status."""
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
        if _PAMS_OK and _pams:
            try:
                _pams.record_event(
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
            SpawnDiversityEngine() if SpawnDiversityEngine else None
        )
    
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
    
    def get_cluster(self, nature: str) -> Optional[NatureCluster]:
        """Get or create a cluster for a given Nature."""
        with self._lock:
            if nature not in self.clusters:
                cluster = NatureCluster(nature)
                cluster.discover_worms()
                if cluster.worms:
                    self.clusters[nature] = cluster
            return self.clusters.get(nature)
    
    # ── Execution ──────────────────────────────────────────────────
    
    def execute_nature(self, nature: str, parallel: bool = False) -> Optional[NatureResult]:
        """Execute all worms in a given Nature."""
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
            
            definition = NATURE_DEFINITIONS.get(nature, {})
            
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
        lines.append("    title[\"🌐 AZAZAEL NATURE CLUSTERS\"]")
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
        if _PAMS_OK and _pams:
            try:
                _pams.record_event(
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
