# Forked from src/CORE/WORMS/CLUSTERWORMS.py on 2026-05-29 for azazael-core standalone package.
# Sync changes from canonical source when updating.
# coding: utf-8
"""
CLUSTERWORMS - Coordinated Worm Collectives

Tier 2: Coordinated groups of worms working in unison.

Features:
- Worm coordination with shared state
- Inter-worm messaging
- Cluster lifecycle management
- Result aggregation
- Cluster persistence
- Dynamic worm resolution from WORM_REGISTRY (replaces hardcoded if/elif)
- PAMS memory recording of every cluster action
- MemoryBus publishing for inter-agent communication
- Mermaid graph generation for cluster visualization
- Nature-based cluster auto-building from registry categories

Usage:
    >>> from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
    >>> cluster = ClusterWORMZ("system")
    >>> cluster.add_worm("SYSTEMZ", config={})
    >>> cluster.add_worm("PROCESSZ", config={})
    >>> results = cluster.execute_all()
    >>> aggregated = cluster.aggregate_results()
    
    # Dynamic Nature-based clusters:
    >>> cluster = ClusterWORMZ.build_from_nature("security")
    >>> print(cluster.to_mermaid())
"""

import os
import sys
import json
import time
import hashlib
import threading
import traceback
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from collections import defaultdict

# ── Worm Registry ─────────────────────────────────────────────────
try:
    from azazael_core.worm_registry import (
        register_worm, WORM_REGISTRY, get_worms_by_category,
        get_all_categories, discover_worms, mark_spawned,
    )
    _REGISTRY_OK = True
except ImportError:
    _REGISTRY_OK = False
    WORM_REGISTRY = {}
    def get_worms_by_category(c): return {}
    def get_all_categories(): return set()
    def discover_worms(): return 0
    def mark_spawned(t): pass
    def register_worm(**kw): return lambda cls: cls

# ── PAMS Memory Recording ─────────────────────────────────────────
try:
    from CORE.PamsRecorder import PamsRecorder
    _pams = PamsRecorder()
    _PAMS_OK = True
except ImportError:
    _PAMS_OK = False
    _pams = None

# ── MemoryBus ─────────────────────────────────────────────────────
try:
    from CORE.MemoryBus import MemoryBus
    _mem_bus = MemoryBus()
    _BUS_OK = True
except ImportError:
    _BUS_OK = False
    _mem_bus = None

# ── Free-Threading ────────────────────────────────────────────────
try:
    from azazael_core.freethreading import is_free_threaded
    _FREETHREAD_OK = True
except ImportError:
    _FREETHREAD_OK = False
    def is_free_threaded():
        try:
            return not sys._is_gil_enabled()
        except Exception:
            return False

# ── Optional GUI ──────────────────────────────────────────────────
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    _GUI_OK = True
except ImportError:
    _GUI_OK = False


# ═══════════════════════════════════════════════════════════════════════
# DATA TYPES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ClusterResult:
    """Result from cluster execution."""

    cluster_id: str
    worm_results: Dict[str, Any]
    aggregated_metrics: Dict[str, float]
    duration_ms: float
    success_count: int
    failure_count: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WormConfig:
    """Configuration for a worm in cluster."""

    name: str
    module: str
    enabled: bool = True
    priority: int = 0
    timeout: int = 30
    retry: int = 1
    params: Dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════
# CLUSTER REGISTRY + DYNAMIC RESOLUTION
# ═══════════════════════════════════════════════════════════════════════

CLUSTER_REGISTRY = {
    "bibl": {
        "description": "BIBL crawling and trimming",
        "worms": ["WORMZ", "TRIMZ"],
    },
    "system": {
        "description": "Full system monitoring",
        "worms": ["SYSTEMZ", "PROCESSZ", "DISKZ"],
    },
    "network": {
        "description": "Network and time management",
        "worms": ["NETWORXZ", "CLOCKZ", "DISKZ"],
    },
    "security": {
        "description": "Security auditing",
        "worms": ["PROCESSZ", "NETWORXZ", "SYSTEMZ"],
    },
    "analysis": {
        "description": "Code analysis and metrics",
        "worms": ["METAZ", "METRICZ", "DEPENDZ"],
    },
    "validation": {
        "description": "Code validation and error checking",
        "worms": ["VALIDZ", "DEADZ", "ERRORZ"],
    },
    "health": {
        "description": "System health monitoring",
        "worms": ["HEALTHZ", "OPTIMIZ", "SYSTEMZ"],
    },
    "full": {
        "description": "Complete ecosystem scan",
        "worms": ["SYSTEMZ", "PROCESSZ", "DISKZ", "NETWORXZ", "WORMZ"],
    },
}

# Known worm-to-module mapping for backward-compatible dynamic resolution
_WORM_MODULE_MAP = {
    "SYSTEMZ": ("SYSTEMZ", "SYSTEMZ"),
    "PROCESSZ": ("PROCESSZ", "PROCESSZ"),
    "DISKZ": ("DISKZ", "DISKZ"),
    "NETWORXZ": ("NETWORXZ", "NETWORXZ"),
    "CLOCKZ": ("CLOCKZ", "CLOCKZ"),
    "WORMZ": ("WORMZ", "WORMZ"),
    "METAZ": ("METAZ", "METAZ"),
    "METRICZ": ("METRICZ", "METRICZ"),
    "DEPENDZ": ("DEPENDZ", "DEPENDZ"),
    "VALIDZ": ("VALIDZ", "VALIDZ"),
    "DEADZ": ("DEADZ", "DEADZ"),
    "ERRORZ": ("ERRORZ", "ERRORZ"),
    "TRIMZ": ("TRIMZ", "TRIMZ"),
    "OPTIMIZ": ("OPTIMIZ", "OPTIMIZ"),
    "HEALTHZ": ("HEALTHZ", "HEALTHZ"),
    "LOGZ": ("LOGZ", "LOGZ"),
    "CHANGEZ": ("CHANGEZ", "CHANGEZ"),
    "DOCKERZ": ("DOCKERZ", "DOCKERZ"),
    "TELEMETRYZ": ("TELEMETRYZ", "TELEMETRYZ"),
}

# Standard method names to try on worm instances, in priority order
_STANDARD_METHODS = [
    "get_summary", "get_status", "run", "execute", "scan",
    "check", "analyze", "audit", "collect", "probe", "profile",
    "inspect", "query", "fetch", "start", "monitor",
]

# Legacy hardcoded dispatch — used as fallback when dynamic resolution fails
_LEGACY_DISPATCH = {
    "SYSTEMZ": lambda: __import__("SYSTEMZ").SYSTEMZ().get_status().__dict__,
    "PROCESSZ": lambda: __import__("PROCESSZ").PROCESSZ().get_summary(),
    "DISKZ": lambda: __import__("DISKZ").DISKZ().get_summary(),
    "NETWORXZ": lambda: __import__("NETWORXZ").NETWORXZ().get_summary(),
    "CLOCKZ": lambda: __import__("CLOCKZ").CLOCKZ().get_uptime(),
    "WORMZ": lambda: __import__("WORMZ").WORMZ().run().__dict__,
    "TRIMZ": lambda: (lambda w: (w.scan_all(show_progress=False), {"files_scanned": len(w.results)})[1])(__import__("TRIMZ").TRIMZ()),
    "HEALTHZ": lambda: __import__("HEALTHZ").HEALTHZ().check().__dict__,
    "OPTIMIZ": lambda: __import__("OPTIMIZ").OPTIMIZ().analyze().__dict__,
    "ERRORZ": lambda: __import__("ERRORZ").ERRORZ().run().__dict__,
    "METRICZ": lambda: __import__("METRICZ").METRICZ().run().__dict__,
    "METAZ": lambda: __import__("METAZ").METAZ().run().__dict__,
    "DEPENDZ": lambda: __import__("DEPENDZ").DEPENDZ().run().__dict__,
    "VALIDZ": lambda: __import__("VALIDZ").VALIDZ().run().__dict__,
    "DEADZ": lambda: __import__("DEADZ").DEADZ().run().__dict__,
    "DOCKERZ": lambda: __import__("DOCKERZ").DOCKERZ().get_status().__dict__,
    "LOGZ": lambda: __import__("LOGZ").LOGZ().run().__dict__,
    "CHANGEZ": lambda: __import__("CHANGEZ").CHANGEZ().run().__dict__,
    "TELEMETRYZ": lambda: __import__("TELEMETRYZ").TELEMETRYZ().get_status().__dict__,
}


def _resolve_worm_dynamic(module_name: str) -> Optional[Dict[str, Any]]:
    """
    Resolve and execute a worm dynamically using the WORM_REGISTRY.
    
    Strategy (in priority order):
    1. Look up the class from WORM_REGISTRY and instantiate it
    2. Try to find and call a standard method
    3. Fall back to legacy hardcoded dispatch
    
    Args:
        module_name: The worm class name (e.g., "SYSTEMZ", "PortAuditor")
    
    Returns:
        Dict with result data, or None if resolution failed
    """
    # Strategy 1: Registry-based resolution
    if _REGISTRY_OK:
        discover_worms()
        
        # Direct lookup in registry
        reg_info = WORM_REGISTRY.get(module_name)
        if reg_info:
            cls = reg_info.get("class")
            if cls and callable(cls):
                return _execute_worm_class(module_name, cls)
        
        # Search all categories for the class name
        for category in get_all_categories():
            cat_worms = get_worms_by_category(category)
            cat_info = cat_worms.get(module_name)
            if cat_info:
                cls = cat_info.get("class")
                if cls and callable(cls):
                    return _execute_worm_class(module_name, cls)
    
    # Strategy 2: Legacy hardcoded dispatch (backward compatibility)
    if module_name in _LEGACY_DISPATCH:
        try:
            result = _LEGACY_DISPATCH[module_name]()
            return {"success": True, "method": "legacy_dispatch", "result": result}
        except Exception as e:
            return {"success": False, "error": str(e), "method": "legacy_dispatch"}
    
    # Strategy 3: Try to import and find the class by convention
    if module_name in _WORM_MODULE_MAP:
        mod_name, cls_name = _WORM_MODULE_MAP[module_name]
        try:
            mod = __import__(mod_name)
            cls = getattr(mod, cls_name)
            return _execute_worm_class(module_name, cls)
        except Exception:
            pass
    
    return None


def _execute_worm_class(name: str, cls: type) -> Dict[str, Any]:
    """
    Instantiate a worm class and call its primary method.
    
    Tries standard methods in priority order, converts dataclass
    results to dicts automatically.
    """
    try:
        instance = cls()
    except Exception as e:
        return {"success": False, "error": f"Instantiation failed: {str(e)}"}
    
    for method_name in _STANDARD_METHODS:
        if hasattr(instance, method_name) and callable(getattr(instance, method_name)):
            try:
                method = getattr(instance, method_name)
                result = method()
                
                # Convert dataclass to dict
                if hasattr(result, "__dict__") and not isinstance(result, dict):
                    result = result.__dict__
                
                return {"success": True, "method": method_name, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e), "method": method_name}
    
    return {"success": False, "error": f"No standard method found on {name}"}


# ═══════════════════════════════════════════════════════════════════════
# CLUSTER STATE
# ═══════════════════════════════════════════════════════════════════════

class ClusterState:
    """Shared state for cluster execution."""

    def __init__(self, cluster_id: str):
        self.cluster_id = cluster_id
        self.results: Dict[str, Any] = {}
        self.metrics = defaultdict(list)
        self.messages: List[Dict] = []
        self.last_sync = datetime.now()
        self.lock = threading.Lock()

    def add_result(self, worm_name: str, result: Any):
        """Add result from worm."""
        with self.lock:
            self.results[worm_name] = result
            self.last_sync = datetime.now()

    def send_message(self, from_worm: str, to_worm: str, data: Any):
        """Send message between worms."""
        with self.lock:
            self.messages.append(
                {
                    "from": from_worm,
                    "to": to_worm,
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def broadcast(self, data: Any, exclude: List[str] = None):
        """Broadcast message to all worms."""
        with self.lock:
            for worm in self.results.keys():
                if exclude and worm in exclude:
                    continue
                self.messages.append(
                    {
                        "from": "BROADCAST",
                        "to": worm,
                        "data": data,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def get_messages(self, worm_name: str) -> List[Dict]:
        """Get messages for worm."""
        with self.lock:
            return [
                m
                for m in self.messages
                if m["to"] == worm_name or m["to"] == "BROADCAST"
            ]

    def clear_messages(self, worm_name: str = None):
        """Clear processed messages."""
        with self.lock:
            if worm_name:
                self.messages = [m for m in self.messages if m["to"] != worm_name]
            else:
                self.messages = []


# ═══════════════════════════════════════════════════════════════════════
# WORM EXECUTOR — Dynamic Resolution
# ═══════════════════════════════════════════════════════════════════════

class WormExecutor:
    """
    Executes a single worm in cluster context.
    
    Uses dynamic registry-based resolution instead of hardcoded if/elif.
    Falls back to legacy dispatch for backward compatibility.
    """

    def __init__(self, name: str, config: WormConfig, state: ClusterState):
        self.name = name
        self.config = config
        self.state = state

    def execute(self, timeout: int = None) -> Dict[str, Any]:
        """Execute worm with configuration using dynamic resolution."""
        start = time.time()
        success = False
        result = None
        error = None

        try:
            timeout = timeout or self.config.timeout
            
            # Primary: dynamic registry-based resolution
            resolved = _resolve_worm_dynamic(self.config.module)
            
            if resolved:
                success = resolved.get("success", False)
                if success:
                    result = resolved.get("result")
                else:
                    error = resolved.get("error", "Unknown error")
                    result = {"error": error}
            else:
                error = f"Unknown module: {self.config.module}"
                result = {"error": error}

        except Exception as e:
            error = str(e)
            result = {"error": error}
            success = False

        duration = (time.time() - start) * 1000

        output = {
            "name": self.name,
            "success": success,
            "duration_ms": duration,
            "result": result,
            "error": error,
        }

        self.state.add_result(self.name, output)
        return output


# ═══════════════════════════════════════════════════════════════════════
# CLUSTERWORMS — Main Cluster Orchestrator with PAMS + Mermaid
# ═══════════════════════════════════════════════════════════════════════

@register_worm(
    category="orchestration", priority=8, cooldown_seconds=20.0,
    description="Coordinated worm collectives with shared state, dynamic resolution, PAMS recording, and Mermaid visualization"
)
class ClusterWORMZ:
    """
    Coordinated worm collectives with shared state and inter-worm messaging.
    
    Now with:
    - Dynamic worm resolution from WORM_REGISTRY (replaces hardcoded if/elif)
    - PAMS memory recording of every cluster action
    - MemoryBus publishing for inter-agent communication
    - Mermaid graph generation for cluster visualization
    - Nature-based cluster auto-building from registry categories
    """

    VERSION = "2.0.0"

    def __init__(self, cluster_type: str = "system"):
        self.cluster_type = cluster_type
        self.cluster_id = f"cluster_{time.time_ns()}"
        self.configs: List[WormConfig] = []
        self.state = ClusterState(self.cluster_id)
        self.parallel = False
        self.timeout = 60
        self._execution_count: int = 0

        self._load_cluster_config(cluster_type)
        self._record("cluster_created", {
            "cluster_type": cluster_type,
            "cluster_id": self.cluster_id,
        })

    def _load_cluster_config(self, cluster_type: str):
        """Load predefined cluster configuration."""
        if cluster_type in CLUSTER_REGISTRY:
            for worm_name in CLUSTER_REGISTRY[cluster_type]["worms"]:
                self.add_worm(worm_name, worm_name)

    # ── Dynamic Cluster Building ──────────────────────────────────

    @classmethod
    def build_from_nature(cls, nature: str) -> Optional["ClusterWORMZ"]:
        """
        Build a cluster dynamically from a Nature (category) in the worm registry.
        """
        if not _REGISTRY_OK:
            return None
        
        discover_worms()
        cat_worms = get_worms_by_category(nature)
        
        if not cat_worms:
            warnings.warn(f"No worms found in Nature category '{nature}'. Available: {sorted(get_all_categories())}")
            return None
        
        cluster = cls(f"nature_{nature}")
        # Clear auto-loaded configs and rebuild from registry
        cluster.configs = []
        for worm_name in sorted(cat_worms.keys()):
            cluster.add_worm(worm_name, worm_name)
        
        cluster._record("cluster_built_from_nature", {
            "nature": nature, "worm_count": len(cat_worms),
            "worms": sorted(cat_worms.keys()),
        })
        
        if _BUS_OK and _mem_bus:
            try:
                _mem_bus.publish(
                    "cluster.nature.built",
                    {"nature": nature, "worm_count": len(cat_worms)},
                    source="ClusterWORMZ",
                )
            except Exception:
                pass
        
        return cluster

    @classmethod
    def build_from_registry(cls, worms: List[str]) -> "ClusterWORMZ":
        """
        Build a cluster from a list of worm names, resolving them
        dynamically from the registry.
        """
        cluster = cls("custom")
        cluster.cluster_id = f"cluster_custom_{time.time_ns()}"
        cluster.configs = []
        
        for worm_name in worms:
            cluster.add_worm(worm_name, worm_name)
        
        return cluster

    @classmethod
    def build_full_ecosystem(cls) -> "ClusterWORMZ":
        """Build a cluster containing ALL registered worms across ALL categories."""
        if not _REGISTRY_OK:
            return cls("full")
        
        discover_worms()
        all_worms: Set[str] = set()
        for category in get_all_categories():
            cat_worms = get_worms_by_category(category)
            all_worms.update(cat_worms.keys())
        
        return cls.build_from_registry(sorted(all_worms))

    # ── Worm Management ───────────────────────────────────────────

    def add_worm(self, name: str, module: str, config: Dict = None):
        """Add worm to cluster."""
        worm_config = WormConfig(
            name=name,
            module=module,
            enabled=config.get("enabled", True) if config else True,
            priority=config.get("priority", 0) if config else 0,
            timeout=config.get("timeout", 30) if config else 30,
            retry=config.get("retry", 1) if config else 1,
            params=config.get("params", {}) if config else {},
        )
        self.configs.append(worm_config)

    def remove_worm(self, name: str):
        """Remove worm from cluster."""
        self.configs = [c for c in self.configs if c.name != name]

    def set_parallel(self, parallel: bool):
        """Set parallel or sequential execution."""
        self.parallel = parallel

    def set_timeout(self, timeout: int):
        """Set execution timeout."""
        self.timeout = timeout

    # ── Execution ─────────────────────────────────────────────────

    def execute_all(self) -> List[Dict[str, Any]]:
        """Execute all worms in cluster.
        
        Recording strategy:
        - _record() -> PamsRecorder: persistent audit trail (all events)
        - _mem_bus.publish() -> MemoryBus: real-time pub/sub for inter-agent coordination
        These are complementary, not redundant — PAMS is for post-mortem,
        MemoryBus is for live coordination between agents.
        """
        self._record("cluster_execution_started", {
            "cluster_type": self.cluster_type,
            "worm_count": len([c for c in self.configs if c.enabled]),
            "parallel": self.parallel,
        })
        
        # Publish to MemoryBus
        if _BUS_OK and _mem_bus:
            try:
                _mem_bus.publish(
                    "cluster.execute.start",
                    {"cluster_id": self.cluster_id, "worm_count": len(self.configs)},
                    source="ClusterWORMZ",
                )
            except Exception:
                pass
        
        results = []
        enabled_configs = [c for c in self.configs if c.enabled]
        enabled_configs.sort(key=lambda x: x.priority, reverse=True)

        if self.parallel:
            threads = []
            results_lock = threading.Lock()
            cancel_event = threading.Event()
            for config in enabled_configs:
                executor = WormExecutor(config.name, config, self.state)
                def execute_and_collect(ex, cfg_name, retries_left):
                    # Check for cancellation before starting
                    if cancel_event.is_set():
                        return
                    out = ex.execute()
                    # Retry logic for parallel path
                    while retries_left > 0 and not out.get("success"):
                        if cancel_event.is_set():
                            return
                        time.sleep(0.1)
                        out = ex.execute()
                        retries_left -= 1
                    if not cancel_event.is_set():
                        with results_lock:
                            results.append(out)
                        mark_spawned(cfg_name)
                t = threading.Thread(
                    target=execute_and_collect,
                    args=(executor, config.name, max(0, config.retry - 1)),
                    daemon=True,
                )
                threads.append((t, config.name))
                t.start()
            for t, name in threads:
                t.join(timeout=self.timeout)
                if t.is_alive():
                    # Thread exceeded timeout — signal cancellation
                    cancel_event.set()
        else:
            for config in enabled_configs:
                executor = WormExecutor(config.name, config, self.state)
                result = executor.execute(timeout=self.timeout)
                # Retry logic
                for attempt in range(max(0, config.retry - 1)):
                    if result.get("success"):
                        break
                    time.sleep(0.1)
                    result = executor.execute(timeout=self.timeout)
                results.append(result)
                mark_spawned(config.name)

        self._execution_count += 1
        
        self._record("cluster_execution_completed", {
            "cluster_type": self.cluster_type,
            "results": len(results),
            "success": len([r for r in results if r.get("success")]),
        })
        
        return results

    def execute_worm(self, name: str) -> Optional[Dict]:
        """Execute single worm by name."""
        for config in self.configs:
            if config.name == name:
                executor = WormExecutor(config.name, config, self.state)
                result = executor.execute()
                mark_spawned(name)
                return result
        return None

    # ── Result Aggregation ────────────────────────────────────────

    def aggregate_results(self) -> ClusterResult:
        """Aggregate results from all worms."""
        results = self.state.results

        metrics = {
            "total_duration_ms": 0,
            "success_rate": 0,
            "avg_duration_ms": 0,
        }

        success_count = 0
        total_duration = 0

        for worm_name, result in results.items():
            if isinstance(result, dict) and "duration_ms" in result:
                total_duration += result["duration_ms"]
                if result.get("success", False):
                    success_count += 1

        metrics["total_duration_ms"] = total_duration
        metrics["success_rate"] = success_count / len(results) if results else 0
        metrics["avg_duration_ms"] = total_duration / len(results) if results else 0

        return ClusterResult(
            cluster_id=self.cluster_id,
            worm_results=results,
            aggregated_metrics=metrics,
            duration_ms=total_duration,
            success_count=success_count,
            failure_count=len(results) - success_count,
        )

    # ── Status ────────────────────────────────────────────────────

    def get_status(self) -> Dict:
        """Get cluster status."""
        return {
            "cluster_id": self.cluster_id,
            "cluster_type": self.cluster_type,
            "version": self.VERSION,
            "worm_count": len(self.configs),
            "enabled_count": len([c for c in self.configs if c.enabled]),
            "parallel": self.parallel,
            "timeout": self.timeout,
            "execution_count": self._execution_count,
            "last_sync": self.state.last_sync.isoformat(),
            "free_threaded": is_free_threaded(),
            "worm_names": sorted([c.name for c in self.configs]),
            "registry_ok": _REGISTRY_OK,
            "pams_ok": _PAMS_OK,
            "bus_ok": _BUS_OK,
        }

    # ── Mermaid Graphs ────────────────────────────────────────────

    def to_mermaid(self, title: str = "") -> str:
        """
        Generate Mermaid graph of this cluster's worms.
        
        Shows worm names, priorities, and the cluster structure.
        """
        label = title or f"{self.cluster_type.upper()} Cluster"
        lines = ["graph TB"]
        lines.append(f'    title["CLUSTER: {label}<br/>{len(self.configs)} worms | {self.cluster_id}"]')
        lines.append("    style title fill:#1a1a2e,stroke:#00d9ff,color:#00d9ff")
        lines.append("")
        
        lines.append(f"    subgraph {self.cluster_type}[{self.cluster_type.upper()}]")
        
        for config in sorted(self.configs, key=lambda c: c.priority, reverse=True):
            status = "enabled" if config.enabled else "disabled"
            color = "#00ff88" if config.enabled else "#666"
            lines.append(f'        {config.name}["{config.name}<br/>pri={config.priority} | {status}"]')
            lines.append(f"        style {config.name} fill:#16213e,stroke:{color},color:{color}")
        
        lines.append("    end")
        return "\n".join(lines)

    def to_mermaid_execution_flow(self) -> str:
        """
        Generate Mermaid flowchart of the execution order with results.
        """
        results = self.state.results
        lines = ["graph LR"]
        lines.append(f'    title["⚡ Execution Flow: {self.cluster_type}<br/>{len(results)} results"]')
        lines.append("    style title fill:#1a1a2e,stroke:#00d9ff,color:#00d9ff")
        lines.append("")
        
        sorted_names = sorted(self.configs, key=lambda c: c.priority, reverse=True)
        prev = None
        
        for config in sorted_names:
            name = config.name
            result = results.get(name, {})
            status = "OK" if result.get("success") else "FAIL"
            color = "#00ff88" if result.get("success") else "#ff4444"
            duration = result.get("duration_ms", 0)
            
            lines.append(f'    {name}["{status} {name}<br/>{duration:.0f}ms"]')
            lines.append(f"    style {name} fill:#16213e,stroke:{color},color:{color}")
            
            if prev:
                lines.append(f"    {prev} --> {name}")
            prev = name
        
        return "\n".join(lines)

    def to_mermaid_interactions(self) -> str:
        """
        Generate Mermaid sequence diagram of inter-worm messaging.
        """
        lines = ["sequenceDiagram"]
        lines.append(f"    title Inter-Worm Messaging: {self.cluster_type}")
        
        # Participants
        for config in self.configs:
            lines.append(f"    participant {config.name}")
        
        # Messages
        for msg in self.state.messages[:20]:
            from_w = msg.get("from", "???")
            to_w = msg.get("to", "???")
            data_str = str(msg.get("data", ""))[:40]
            lines.append(f"    {from_w}->>+{to_w}: {data_str}")
        
        return "\n".join(lines)

    # ── PAMS Memory Recording ─────────────────────────────────────

    def _record(self, event_type: str, data: Dict[str, Any]):
        """Record event to PAMS memory."""
        if _PAMS_OK and _pams:
            try:
                _pams.record_event(
                    event_type, data,
                    source=f"ClusterWORMZ.{self.cluster_type}",
                    severity="info",
                )
            except Exception:
                pass

    def __repr__(self):
        return f"ClusterWORMZ({self.cluster_type}, {len(self.configs)} worms, v{self.VERSION})"


# ═══════════════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════════════

def run_popup():
    """Run cluster worms with popup window."""
    if not _GUI_OK:
        print("tkinter not available — GUI disabled")
        return
    
    root = tk.Tk()
    root.title("CLUSTERWORMS — Coordinated Worm Collectives")
    root.geometry("1000x750")
    root.configure(bg="#1a1a2e")

    def log(msg, level="INFO"):
        colors = {
            "OK": "#00ff88",
            "FAIL": "#ff4444",
            "INFO": "#00aaff",
            "CLUSTER": "#ff00ff",
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        text_area.insert("end", f"[{timestamp}] [{level}] {msg}\n")
        text_area.see("end")
        root.update_idletasks()

    header = tk.Frame(root, bg="#16213e", pady=15)
    header.pack(fill="x")

    tk.Label(
        header,
        text="CLUSTERWORMS v2.0",
        font=("Consolas", 28, "bold"),
        bg="#16213e",
        fg="#00d4ff",
    ).pack()

    tk.Label(
        header,
        text="Tier 2: Coordinated Worm Collectives + Dynamic Resolution",
        font=("Consolas", 12),
        bg="#16213e",
        fg="#7c3aed",
    ).pack()

    status_label = tk.Label(
        root,
        text="Ready",
        font=("Consolas", 14),
        bg="#1a1a2e",
        fg="#00ff88",
    )
    status_label.pack(pady=5)

    control_frame = tk.Frame(root, bg="#1a1a2e", pady=10)
    control_frame.pack(fill="x", padx=20)

    tk.Label(
        control_frame,
        text="Cluster:",
        bg="#1a1a2e",
        fg="#00d4ff",
        font=("Consolas", 11),
    ).pack(side="left")

    cluster_var = tk.StringVar(value="system")
    cluster_combo = ttk.Combobox(
        control_frame,
        textvariable=cluster_var,
        values=list(CLUSTER_REGISTRY.keys()),
        width=15,
        font=("Consolas", 10),
    )
    cluster_combo.pack(side="left", padx=10)

    parallel_var = tk.BooleanVar(value=False)
    parallel_check = tk.Checkbutton(
        control_frame,
        text="Parallel Execution",
        variable=parallel_var,
        font=("Consolas", 11),
        bg="#1a1a2e",
        fg="#00ff88",
        selectcolor="#16213e",
    )
    parallel_check.pack(side="left", padx=20)

    progress_frame = tk.Frame(root, bg="#1a1a2e", pady=10)
    progress_frame.pack(fill="x", padx=20)

    progress = ttk.Progressbar(progress_frame, mode="determinate", length=950)
    progress.pack(fill="x")

    progress_label = tk.Label(
        progress_frame,
        text="0 / 0 worms",
        font=("Consolas", 12),
        bg="#1a1a2e",
        fg="#00ff88",
    )
    progress_label.pack()

    stats_frame = tk.Frame(root, bg="#1a1a2e", pady=5)
    stats_frame.pack(fill="x", padx=20)

    stats_label = tk.Label(
        stats_frame,
        text="Worms: 0 | Success: 0 | Duration: 0ms",
        font=("Consolas", 12),
        bg="#1a1a2e",
        fg="#00d4ff",
    )
    stats_label.pack()

    text_area = scrolledtext.ScrolledText(
        root, wrap="word", font=("Consolas", 10), bg="#0f0f1a", fg="#00ff88", height=35
    )
    text_area.pack(fill="both", expand=True, padx=20, pady=10)

    button_frame = tk.Frame(root, bg="#1a1a2e", pady=15)
    button_frame.pack(fill="x", padx=20)

    def run_cluster():
        status_label.config(text="Executing...")
        progress["value"] = 0
        text_area.delete("1.0", "end")

        cluster_type = cluster_var.get()
        parallel = parallel_var.get()

        log("=" * 60, "CLUSTER")
        log(f"CLUSTERWORMS v2 — {cluster_type.upper()} Cluster", "CLUSTER")
        log("=" * 60, "CLUSTER")

        cluster = ClusterWORMZ(cluster_type)
        cluster.set_parallel(parallel)

        status = cluster.get_status()
        log(f"Cluster: {status['cluster_id']}", "INFO")
        log(f"Worms: {status['worm_count']} | Parallel: {parallel}", "INFO")
        log(f"Dynamic Resolution: {'ON' if _REGISTRY_OK else 'OFF (legacy)'}", "INFO")
        log("-" * 60, "INFO")

        progress["value"] = 20
        progress_label.config(text="Executing worms...")
        root.update()

        results = cluster.execute_all()

        progress["value"] = 80
        log(f"\nExecution Results:", "INFO")
        for r in results:
            status_icon = "OK" if r.get("success") else "FAIL"
            method = r.get("result", {})
            if isinstance(method, dict):
                method_name = method.get("method", "?")
            else:
                method_name = "?"
            log(
                f"  [{status_icon}] {r['name']}: {r.get('duration_ms', 0):.0f}ms [{method_name}]",
                status_icon if r.get("success") else "FAIL",
            )

        agg = cluster.aggregate_results()

        log(f"\nAggregation:", "INFO")
        log(
            f"  Success Rate: {agg.success_count}/{len(results)} ({agg.success_count / max(len(results), 1) * 100:.0f}%)",
            "INFO",
        )
        log(f"  Total Duration: {agg.duration_ms:.0f}ms", "INFO")
        
        log(f"\nMermaid Graph:", "INFO")
        log(cluster.to_mermaid(), "INFO")

        progress["value"] = 100
        stats_label.config(
            text=f"Worms: {len(results)} | Success: {agg.success_count} | Duration: {agg.duration_ms:.0f}ms"
        )
        status_label.config(text="Complete!")

    def show_clusters():
        text_area.delete("1.0", "end")
        log("=" * 60, "CLUSTER")
        log("Available Clusters + Dynamic Natures", "CLUSTER")
        log("=" * 60, "CLUSTER")
        for name, info in CLUSTER_REGISTRY.items():
            log(f"\n{name.upper()}:", "INFO")
            log(f"  Description: {info['description']}", "INFO")
            log(f"  Worms: {', '.join(info['worms'])}", "INFO")
        
        if _REGISTRY_OK:
            log(f"\n── Dynamic Nature Clusters ──", "CLUSTER")
            discover_worms()
            for cat in sorted(get_all_categories()):
                cat_worms = get_worms_by_category(cat)
                log(f"\n[{cat}]: {len(cat_worms)} worms", "INFO")
                log(f"  {', '.join(sorted(list(cat_worms.keys())[:8]))}", "INFO")

    btn_run = tk.Button(
        button_frame,
        text="EXECUTE",
        command=run_cluster,
        font=("Consolas", 13, "bold"),
        bg="#16213e",
        fg="#00ff88",
        width=12,
    )
    btn_run.pack(side="left", padx=10)

    btn_show = tk.Button(
        button_frame,
        text="CLUSTERS",
        command=show_clusters,
        font=("Consolas", 13, "bold"),
        bg="#16213e",
        fg="#ff00ff",
        width=10,
    )
    btn_show.pack(side="left", padx=10)

    close_btn = tk.Button(
        button_frame,
        text="CLOSE",
        command=root.destroy,
        font=("Consolas", 13, "bold"),
        bg="#ff4444",
        fg="#ffffff",
        width=10,
    )
    close_btn.pack(side="right", padx=10)

    log("CLUSTERWORMS v2 Ready — Dynamic Resolution ON", "INFO")
    log(f"Registry OK: {_REGISTRY_OK} | PAMS OK: {_PAMS_OK} | Bus OK: {_BUS_OK}", "INFO")
    log("Select cluster type and click EXECUTE", "INFO")

    root.mainloop()


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CLUSTERWORMS v2 — Coordinated Worm Collectives"
    )
    parser.add_argument(
        "--type", type=str, help="Cluster type (system, network, bibl, etc.)"
    )
    parser.add_argument("--list", action="store_true", help="List available clusters")
    parser.add_argument("--execute", action="store_true", help="Execute cluster")
    parser.add_argument("--parallel", action="store_true", help="Parallel execution")
    parser.add_argument("--popup", action="store_true", help="Show popup window")
    parser.add_argument("--mermaid", action="store_true", help="Generate Mermaid graph")
    parser.add_argument("--mermaid-flow", action="store_true", help="Execution flow Mermaid")
    parser.add_argument("--build-nature", type=str, help="Build cluster from Nature category")
    parser.add_argument("--discover", action="store_true", help="Discover and list all Nature categories")

    args = parser.parse_args()

    if args.popup:
        run_popup()
    
    elif args.discover:
        if _REGISTRY_OK:
            discover_worms()
            print("Nature Categories Available for Cluster Building:")
            print()
            for cat in sorted(get_all_categories()):
                cat_worms = get_worms_by_category(cat)
                print(f"  [{cat}] {len(cat_worms)} worms")
                for name in sorted(list(cat_worms.keys())[:8]):
                    print(f"    - {name}")
                if len(cat_worms) > 8:
                    print(f"    ... and {len(cat_worms) - 8} more")
            print(f"\nTotal: {len(get_all_categories())} categories")
        else:
            print("Worm registry not available")
    
    elif args.build_nature:
        cluster = ClusterWORMZ.build_from_nature(args.build_nature)
        if cluster:
            print(f"Built cluster from [{args.build_nature}] Nature: {len(cluster.configs)} worms")
            for c in cluster.configs:
                print(f"  - {c.name}")
            cluster.set_parallel(args.parallel)
            results = cluster.execute_all()
            agg = cluster.aggregate_results()
            print(f"Success: {agg.success_count}/{len(results)}")
            print(f"Duration: {agg.duration_ms:.0f}ms")
            
            if args.mermaid:
                print("\n" + cluster.to_mermaid())
        else:
            print(f"No worms found for Nature '{args.build_nature}'")
    
    elif args.mermaid:
        cluster = ClusterWORMZ(args.type or "system")
        print(cluster.to_mermaid())
    
    elif args.list:
        print("Available Clusters:")
        for name, info in CLUSTER_REGISTRY.items():
            print(f"  {name}: {info['description']}")
            print(f"    Worms: {', '.join(info['worms'])}")
        
        if _REGISTRY_OK:
            discover_worms()
            print(f"\nDynamic Nature Categories: {len(get_all_categories())}")
            for cat in sorted(get_all_categories()):
                cat_worms = get_worms_by_category(cat)
                print(f"  [{cat}]: {len(cat_worms)} worms")
    
    elif args.execute:
        cluster_type = args.type or "system"
        cluster = ClusterWORMZ(cluster_type)
        cluster.set_parallel(args.parallel)
        results = cluster.execute_all()
        agg = cluster.aggregate_results()
        print(f"Cluster: {cluster_type}")
        print(f"Success: {agg.success_count}/{len(results)}")
        print(f"Duration: {agg.duration_ms:.0f}ms")
        
        if args.mermaid_flow:
            print("\n" + cluster.to_mermaid_execution_flow())

    else:
        print("CLUSTERWORMS v2 — Dynamic Worm Resolution")
        print()
        print("Usage:")
        print("  python CLUSTERWORMS.py --type system --execute")
        print("  python CLUSTERWORMS.py --list")
        print("  python CLUSTERWORMS.py --type bibl --parallel --execute")
        print("  python CLUSTERWORMS.py --build-nature security --execute")
        print("  python CLUSTERWORMS.py --discover")
        print("  python CLUSTERWORMS.py --mermaid")
        print("  python CLUSTERWORMS.py --popup")


if __name__ == "__main__":
    main()
