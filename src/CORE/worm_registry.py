# coding: utf-8
"""
worm_registry — Centralized Worm Registry with Auto-Discovery & Spawn Diversity

Provides:
- @register_worm decorator for automatic class registration
- Global WORM_REGISTRY dict with full metadata
- Auto-discovery from CORE/WORMS directory
- SpawnDiversityEngine: category rotation, cooldown, weighted selection,
  time-based spawning patterns, and all-registered-worm coverage

Usage:
    >>> from CORE.worm_registry import register_worm, WORM_REGISTRY, SpawnDiversityEngine
    >>> @register_worm(category="diagnostic", priority=7, cooldown_seconds=30)
    ... class NetworkDiag:
    ...     VERSION = "1.0.0"
    ...
    >>> sde = SpawnDiversityEngine()
    >>> next_spawn = sde.pick_next_spawn(fleet_status, history)
"""

import os
import sys
import time
import importlib
import inspect

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass
import threading

# --- Global Registry -----------------------------------------------

# Structured logger with correlation IDs (per ALL 5 inference models' finding)
import logging
_log = logging.getLogger("worm_registry")

# Simple thread-local correlation ID for traceability across operations
_thread_local = threading.local()
_thread_local.correlation_id: Optional[str] = None


def _get_correlation_id() -> str:
    """Get the current thread's correlation ID, generating one if needed."""
    if not hasattr(_thread_local, "correlation_id") or _thread_local.correlation_id is None:
        from CORE.uuid7 import uuid7
        _thread_local.correlation_id = uuid7().hex[:12]
    return _thread_local.correlation_id


def _log_event(event: str, **context: Any):
    """Log a structured event with correlation ID and context."""
    extra = {"cid": _get_correlation_id(), **context}
    _log.info(f"[registry] {event}", extra=extra)


WORM_REGISTRY: Dict[str, Dict[str, Any]] = {}
"""Global worm type registry.
Key: worm class name (e.g. "NetworkDiag")
Value: {
    "class": the actual class,
    "module": module name,
    "category": str,
    "priority": int (1-10),
    "cooldown_seconds": float,
    "description": str,
    "registered_at": iso timestamp,
    "spawn_count": int,
    "last_spawned": iso timestamp or None,
    "tags": set of tags,
    "source_file": str,
}
"""

_registry_lock = threading.RLock()
_discovery_done = False


# --- Decorator ------------------------------------------------------

# -- Valid categories for input validation ---------------------------
_VALID_CATEGORIES = frozenset({
    "monitor", "diagnostic", "analysis", "defense",
    "optimization", "orchestration", "sync", "repair", "utility",
    "learning", "ml", "data", "visualization",
    "container", "communication", "migration",
    "security", "config", "backup",
    "profiling", "telemetry",
    "expansion", "network", "system",
})


def _validate_registry_params(category: str, priority: int, cooldown_seconds: float, tags: Optional[Set[str]]):
    """Validate register_worm() parameters. Raises ValueError on invalid input.

    Added per ALL 5 inference models' production audit finding on input validation.
    """
    if category not in _VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. Must be one of: {sorted(_VALID_CATEGORIES)}"
        )
    if not isinstance(priority, int) or priority < 1 or priority > 10:
        raise ValueError(f"Priority must be int 1-10, got {priority}")
    if not isinstance(cooldown_seconds, (int, float)) or cooldown_seconds <= 0:
        raise ValueError(f"cooldown_seconds must be positive, got {cooldown_seconds}")
    if tags is not None:
        if not isinstance(tags, set):
            raise ValueError(f"tags must be a set, got {type(tags).__name__}")
        for tag in tags:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError(f"Each tag must be a non-empty string, got {tag!r}")
            if any(c in tag for c in "<>\"'&;`|"):
                raise ValueError(f"Tag '{tag}' contains dangerous characters")


def register_worm(
    category: str = "utility",
    priority: int = 5,
    cooldown_seconds: float = 30.0,
    description: str = "",
    tags: Optional[Set[str]] = None,
):
    """
    Decorator to register a worm class in the global WORM_REGISTRY.

    Args:
        category: One of "monitor", "diagnostic", "analysis", "defense",
                  "optimization", "orchestration", "sync", "repair", "utility"
        priority: Spawn priority 1-10 (10 = highest)
        cooldown_seconds: Minimum seconds between spawns of this type
        description: Human-readable description
        tags: Optional set of tags for filtered selection

    Raises:
        ValueError: If any parameter is invalid (per security hardening).

    Example:
        @register_worm(category="diagnostic", priority=8, cooldown_seconds=60)
        class NetworkDiag:
            VERSION = "1.0.0"
    """
    # -- Input validation (per ALL 5 inference models' finding) --
    _validate_registry_params(category, priority, cooldown_seconds, tags)

    def decorator(cls):
        if not isinstance(cls, type):
            raise TypeError(f"@register_worm requires a class, got {type(cls).__name__}")

        name = cls.__name__
        module = cls.__module__
        try:
            source_file = inspect.getfile(cls)
        except (OSError, TypeError, Exception):
            source_file = ""  # exec()-defined classes or REPL classes have no source file

        with _registry_lock:
            WORM_REGISTRY[name] = {
                "class": cls,
                "module": module,
                "category": category,
                "priority": priority,
                "cooldown_seconds": cooldown_seconds,
                "description": description or (cls.__doc__ or "").split("\n")[0].strip(),
                "registered_at": datetime.now().isoformat(),
                "spawn_count": 0,
                "last_spawned": None,
                "tags": tags or set(),
                "source_file": source_file,
                "version": getattr(cls, "VERSION", "0.0.0"),
            }

        _log_event("worm_registered", name=name, category=category, priority=priority)
        return cls

    return decorator


# --- Auto-Discovery -------------------------------------------------

def discover_worms(
    worms_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> int:
    """
    Auto-discover and import all worm modules from CORE/WORMS directory.

    Uses pickle cache (~/.azazael/worm_registry_cache.pkl) to avoid the
    38-45s cold start. If cache is fresh, loads registry in <0.2s.
    If cache is stale or missing, runs full discovery and rebuilds cache.

    Args:
        worms_dir: Optional path to WORMS directory (default: CORE/WORMS).
        progress_callback: Optional callback(processed, total, module_name).

    Returns number of newly discovered worm classes.
    """
    global _discovery_done
    
    # Short-circuit: if discovery already completed, skip redundant work.
    # Thread-safe: _discovery_done is only set True after WORM_REGISTRY
    # is fully populated. Workers see True → registry is valid.
    if _discovery_done:
        return 0

    if worms_dir is None:
        worms_dir = str(Path(__file__).resolve().parent / "WORMS")

    if not os.path.isdir(worms_dir):
        return 0

    # -- Try pickle cache first (avoids 38-45s cold start) --
    # Uses _load_cache_readonly() — NEVER rebuilds from within discover_worms().
    # Calling load_registry() here would create an infinite loop:
    #   discover_worms -> load_registry -> discover_worms -> ...
    if not WORM_REGISTRY:
        try:
            from CORE.worm_registry_cache import _load_cache_readonly
            registry = _load_cache_readonly(worms_dir)
            if registry:
                with _registry_lock:
                    WORM_REGISTRY.update(registry)
                _discovery_done = True
                _log_event("discovery_cache_hit", count=len(WORM_REGISTRY), worms_dir=worms_dir)
                return len(WORM_REGISTRY)
        except Exception as exc:
            _log_event("discovery_cache_miss", error=str(exc)[:80])
            pass  # Cache unavailable — fall through to full discovery

    before_count = len(WORM_REGISTRY)

    # Add WORMS dir to sys.path temporarily
    if worms_dir not in sys.path:
        sys.path.insert(0, worms_dir)

    # Pre-compute already-registered filenames for faster lookup.
    # Use os.path.basename() for robust cross-platform path handling.
    registered_files = {
        os.path.basename(info.get("source_file", ""))
        for info in WORM_REGISTRY.values()
        if info.get("source_file")
    }

    # Build sorted file list once (avoids double-iterating listdir)
    py_files = sorted(
        f for f in os.listdir(worms_dir)
        if f.endswith(".py") and not f.startswith("_") and not f.startswith(".")
    )
    total = len(py_files)

    for processed, filename in enumerate(py_files, 1):
        # Skip already-registered modules (fast set lookup)
        if filename in registered_files:
            continue

        module_name = filename[:-3]  # strip .py

        if progress_callback:
            progress_callback(processed, total, module_name)

        try:
            module = importlib.import_module(module_name)

            # After import, skip dir() loop if @register_worm already registered this module
            src_file = getattr(module, "__file__", "")
            if src_file:
                src_name = os.path.basename(src_file)
                already_has_classes = any(
                    info.get("source_file", "").endswith(src_name)
                    for info in WORM_REGISTRY.values()
                )
                if already_has_classes:
                    continue

            # Find classes with VERSION attribute (fast isinstance check)
            for attr_name in dir(module):
                if attr_name.startswith("_"):
                    continue
                if attr_name.endswith("Config"):
                    continue
                obj = getattr(module, attr_name, None)
                if not isinstance(obj, type):
                    continue
                if not hasattr(obj, "VERSION"):
                    continue

                # Skip if already registered (fast dict lookup)
                if attr_name in WORM_REGISTRY:
                    continue

                # Auto-categorize and register
                auto_category = _guess_category(attr_name, module_name)
                register_fn = register_worm(
                    category=auto_category,
                    priority=_guess_priority(attr_name, module_name),
                    cooldown_seconds=_guess_cooldown(auto_category),
                    description=obj.__doc__ or "",
                )
                register_fn(obj)

        except Exception:
            # Module might have import issues or psutil segfaults
            pass

    _discovery_done = True

    # -- Save to pickle cache for next session --
    new_count = len(WORM_REGISTRY) - before_count
    if new_count > 0:
        try:
            from CORE.worm_registry_cache import save_cache
            save_cache(WORM_REGISTRY, worms_dir)
        except Exception:
            pass  # Non-fatal — cache save failed, but discovery succeeded

    return new_count


def _guess_category(class_name: str, module_name: str) -> str:
    """Heuristic category guessing for auto-discovered worms."""
    name_upper = class_name.upper()
    module_upper = module_name.upper()

    if any(kw in name_upper for kw in ["DIAG", "SCAN", "INSPECT"]):
        return "diagnostic"
    if any(kw in name_upper for kw in ["ANALYSIS", "ANALYZE", "REVERSE"]):
        return "analysis"
    if any(kw in name_upper for kw in ["ERROR", "HEALTH", "HEAL", "REPAIR", "DEFENSE"]):
        return "defense"
    if any(kw in name_upper for kw in ["OPTIMIZE", "OPTIMIZ", "TRIM", "PRUNE"]):
        return "optimization"
    if any(kw in name_upper for kw in ["ORCHESTRATE", "ORCHESTRA", "META", "HYDRA"]):
        return "orchestration"
    if any(kw in name_upper for kw in ["SYNC", "CLOCK", "TIME"]):
        return "sync"
    if any(kw in name_upper for kw in ["SYSTEM", "PROCESS", "DISK", "NETWORK", "NET", "MONITOR"]):
        return "monitor"
    if any(kw in name_upper for kw in ["CLUSTER", "FLEET", "POOL", "SPAWN"]):
        return "orchestration"

    return "utility"


def _guess_priority(class_name: str, module_name: str) -> int:
    """Heuristic priority guessing for auto-discovered worms."""
    name_upper = class_name.upper()
    if any(kw in name_upper for kw in ["SYSTEM", "HEALTH", "ERROR"]):
        return 8
    if any(kw in name_upper for kw in ["PROCESS", "NETWORK", "DIAG"]):
        return 7
    if any(kw in name_upper for kw in ["ANALYSIS", "BINARY", "REVERSE"]):
        return 6
    if any(kw in name_upper for kw in ["DISK", "CLOCK", "SYNC"]):
        return 5
    if any(kw in name_upper for kw in ["OPTIMIZ", "TRIM"]):
        return 4
    return 3


def _guess_cooldown(category: str) -> float:
    """Heuristic cooldown guessing based on category."""
    cooldowns = {
        "monitor": 15.0,
        "diagnostic": 30.0,
        "analysis": 60.0,
        "defense": 30.0,
        "optimization": 45.0,
        "orchestration": 20.0,
        "sync": 30.0,
        "repair": 60.0,
        "utility": 30.0,
    }
    return cooldowns.get(category, 30.0)


# --- Lazy PAMS Recorder (thread-safe, defer import) ----------------
_pams_instance: Any = None
_pams_instance_lock = threading.Lock()


def _get_pams_recorder():
    """Lazy PAMS recorder — double-checked locking for Python 3.14t free-threading."""
    global _pams_instance
    if _pams_instance is None:
        with _pams_instance_lock:
            if _pams_instance is None:
                try:
                    from CORE.PamsRecorder import PamsRecorder
                    _pams_instance = PamsRecorder()
                except ImportError:
                    _pams_instance = False
    return _pams_instance if _pams_instance else None


# --- BaseWormMixin — explicit schema registration (thread-safe for 3.14t) ----

class BaseWormMixin:
    """
    Mixin that provides default `get_summary()` for worm classes.

    Uses **explicit schema registration** instead of introspection,
    making it thread-safe under Python 3.14t free-threading.

    Worm classes declare their summary method and fields upfront:
        class MyWorm(BaseWormMixin):
            __summary_method__ = "scan_all"       # method to call for get_summary()
            __summary_fields__ = ["results"]      # instance attrs to include in summary

            def scan_all(self):
                return {"found": 42}

        w = MyWorm()
        print(w.get_summary())
        # {"success": True, "method": "scan_all", "result": {"found": 42}, ...}

    If no explicit schema is set, returns basic class info (name, module, version)
    instead of using introspection.
    """

    # -- Schema (override in subclass) --------------------------------
    __summary_method__: str = ""       # Method name to call for summary
    __summary_fields__: list[str] = []  # Instance attribute names to include

    # -- Standard method names to auto-discover if __summary_method__ is not set ---
    _DISCOVERY_CANDIDATES = ["execute", "run", "scan", "check", "analyze",
                             "audit", "collect", "probe", "profile", "inspect",
                             "monitor", "report", "validate", "detect", "measure",
                             "track", "fix", "heal", "start", "test", "verify",
                             "publish", "subscribe", "deliver", "negotiate",
                             "orchestrate", "handle_request", "register_model",
                             "register_schema", "register_peer", "register_method",
                             "check_latest", "check_usage", "check_outdated",
                             "check_package", "compare_versions", "compile_html",
                             "crawl_all", "predictive_crawl", "train_model",
                             "train_episode", "train_from_memory",
                             "discover_all", "discover_all_natures",
                             "execute_nature", "execute_all_natures",
                             "export_state", "import_state", "get_snapshot",
                             "inc_counter", "set_gauge", "observe",
                             "scan_all", "scan_all_modules", "scan_env_files",
                             "scan_requirements", "scan_local_ports",
                             "run_scheduler", "run_scan", "run_all",
                             "run_comprehensive_scan", "run_complete_analysis",
                             "audit_exposure", "audit_image",
                             "detect_bottleneck", "detect_anomalies",
                             "detect_breaking_changes",
                             "measure_contention", "measure_io",
                             "create_snapshot", "list_versions",
                             "rollback", "rotate_secret", "generate_password",
                             "generate_shim", "test_restore", "verify_archive",
                             "archive", "backup_data", "restore_data",
                             "render_svg", "to_dot", "to_timeline_html",
                             "build_hourly_heatmap",
                             "compare_snapshots", "take_snapshot",
                             "watch_file", "read_new_lines",
                             "register_webhook", "replay",
                             "find_overly_permissive", "get_firewall_rules",
                             "fix_file", "fix_bom", "fix_bad_syspath",
                             "heal_module", "apply_healing",
                             "serialize", "deserialize",
                             "check_bom", "check_syntax", "check_imports",
                             "is_enabled", "set_flag",
                             "crawl_file", "crawl_folder", "crawl_delta",
                             "find_python_files", "remove_bom",
                             "compute_manifest", "find_changes",
                             "start_service", "stop_service",
                             "predict_failure", "record_history",
                             "add_edge", "add_node", "add_section",
                             "add_span", "add_mapping",
                             "get_checksums", "format_report",
                             "parse_requirements",
                             "normalize", "impute_missing", "one_hot_encode",
                             "extract_worm_features",
                             "update_learned_patterns", "sample", "capture_sample"]

    def __init_subclass__(cls, **kwargs):
        """Auto-discover __summary_method__ if not explicitly set.

        Checks for common standard methods (execute, run, scan, etc.)
        and sets __summary_method__ to the first one found.
        This ensures 40 previously-skipped worms get auto-discovered.
        """
        super().__init_subclass__(**kwargs)
        # Only auto-discover if __summary_method__ is the default empty string
        if cls.__summary_method__:
            return
        for candidate in cls._DISCOVERY_CANDIDATES:
            if hasattr(cls, candidate) and callable(getattr(cls, candidate, None)):
                cls.__summary_method__ = candidate
                break

    def get_summary(self) -> Dict[str, Any]:
        """
        Return a summary dict using the declared schema.

        If `__summary_method__` is set, calls that method and returns its result.
        If `__summary_fields__` is set, includes those instance attributes.
        Falls back to basic class info if no schema is declared.

        Thread-safe: uses only class-level constants and instance __dict__ reads
        via explicit field names — no dir(), no getattr() for method discovery.

        Returns:
            Dict with "success", "method", "result" matching what executors expect.
        """
        # -- Explicit method call --
        method_name = self.__summary_method__
        if method_name:
            # Direct attribute lookup by explicit name (thread-safe, no dir())
            try:
                method = object.__getattribute__(self, method_name)
                if callable(method):
                    result = method()
                    if hasattr(result, "__dict__"):
                        result = result.__dict__
                    return {"success": True, "method": method_name, "result": result}
            except AttributeError:
                pass
            except Exception:
                pass

        # -- Explicit field summary --
        fields = self.__summary_fields__
        if fields:
            result = {}
            for field_name in fields:
                try:
                    result[field_name] = object.__getattribute__(self, field_name)
                except AttributeError:
                    pass
            return {"success": True, "method": "get_summary", "result": result}

        # -- Fallback: basic class info (no introspection) --
        return {
            "success": True,
            "method": "get_summary",
            "result": {
                "class": type(self).__name__,
                "module": type(self).__module__,
                "version": getattr(self, "VERSION", "?"),
            },
        }

    def get_status(self) -> Dict[str, Any]:
        """Default status — returns basic class info without introspection."""
        return {
            "class": type(self).__name__,
            "module": type(self).__module__,
            "version": getattr(self, "VERSION", "?"),
            "summary_method": self.__summary_method__ or "(default)",
            "summary_fields": self.__summary_fields__,
        }


# --- Spawn Diversity Engine -----------------------------------------

@dataclass
class SpawnRecord:
    """Record of a single spawn event."""
    worm_type: str
    category: str
    timestamp: float
    priority: int
    reason: str


class SpawnDiversityEngine:
    """
    Spawn diversity engine that prevents spawning the same worm types
    repeatedly and ensures broad ecosystem coverage.

    Features:
    - Category rotation: never spawn same category in consecutive picks
    - Cooldown enforcement: each type has minimum time between spawns
    - Weighted selection: priority × recency × diversity bonus
    - Time-based patterns: spawn different profiles based on hour of day
    - Staleness penalty: worms never spawned get increasing priority bonus
    - All-registered-worm coverage: ensures every worm type eventually gets spawned
    - PAMS memory recording: every spawn recommendation is logged to PAMS
    """

    def __init__(self):
        self.spawn_history: List[SpawnRecord] = []
        self._last_category: Optional[str] = None
        self._lock = threading.Lock()

    def _record_pams(self, event_type: str, data: Dict[str, Any]):
        """Record event to PAMS memory (non-blocking on failure)."""
        pams = _get_pams_recorder()
        if pams:
            try:
                pams.record_event(
                    event_type, data,
                    source="SpawnDiversityEngine",
                    severity="info",
                )
            except Exception:
                pass

    def record_spawn(self, worm_type: str, category: str, priority: int, reason: str = ""):
        """Record a spawn event for diversity tracking."""
        with self._lock:
            self.spawn_history.append(SpawnRecord(
                worm_type=worm_type,
                category=category,
                timestamp=time.time(),
                priority=priority,
                reason=reason,
            ))
            self._last_category = category

            # Prune history (keep last 1000)
            if len(self.spawn_history) > 1000:
                self.spawn_history = self.spawn_history[-1000:]

    def pick_next_spawn(
        self,
        fleet_status: Any = None,
        worm_types_override: Optional[Dict[str, Dict]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Pick the best next worm type to spawn, considering diversity,
        cooldowns, category rotation, time-based patterns, and staleness.

        Also records the selection to PAMS for audit trail.

        Args:
            fleet_status: Optional FleetStatus-like object with cpu_percent, etc.
            worm_types_override: Override WORM_REGISTRY entries (for MetaWormSpawner compat)

        Returns:
            Dict with "type", "priority", "reason", "category" — or None if nothing to spawn
        """
        registry = worm_types_override or WORM_REGISTRY
        if not registry:
            return None

        now = time.time()
        candidates = []

        for worm_type, info in registry.items():
            # -- Cooldown check --
            cooldown = info.get("cooldown_seconds", 30)
            last_spawned = info.get("last_spawned")
            if last_spawned:
                try:
                    last_time = datetime.fromisoformat(last_spawned).timestamp()
                    if now - last_time < cooldown:
                        continue  # Still on cooldown
                except (ValueError, TypeError):
                    pass

            category = info.get("category", "utility")

            # -- Category rotation --
            if category == self._last_category:
                continue  # Skip same category as last spawn

            priority = info.get("priority", 5)

            # -- Staleness bonus --
            spawn_count = info.get("spawn_count", 0)
            staleness_bonus: float = 0.0
            if spawn_count == 0:
                staleness_bonus = 5.0  # Never spawned — big bonus
            elif last_spawned:
                try:
                    last_time = datetime.fromisoformat(last_spawned).timestamp()
                    hours_since = (now - last_time) / 3600
                    staleness_bonus = min(3.0, hours_since * 0.5)  # Up to 3.0 bonus
                except (ValueError, TypeError):
                    pass

            # -- Time-based pattern bonus --
            hour = datetime.now().hour
            time_bonus = self._get_time_bonus(category, hour)

            # -- Fleet status bonus --
            fleet_bonus: float = 0.0
            if fleet_status:
                fleet_bonus = self._get_fleet_bonus(category, fleet_status)

            # -- Compute weighted score --
            # Higher = more likely to be picked
            score = (
                priority * 2.0           # Base priority (2x weight)
                + staleness_bonus * 3.0  # Staleness matters most (3x)
                + time_bonus * 1.5       # Time patterns (1.5x)
                + fleet_bonus * 2.0      # Fleet context (2x)
            )

            candidates.append({
                "type": worm_type,
                "priority": priority,
                "category": category,
                "score": score,
                "spawn_count": spawn_count,
                "staleness_bonus": staleness_bonus,
                "time_bonus": time_bonus,
                "reason": self._build_reason(worm_type, category, staleness_bonus, time_bonus, fleet_bonus),
            })

        if not candidates:
            return None

        # Sort by score descending, pick top
        candidates.sort(key=lambda x: -x["score"])
        best = candidates[0]

        pick = {
            "type": best["type"],
            "priority": best["priority"],
            "reason": best["reason"],
            "category": best["category"],
        }

        # Record selection to PAMS for audit trail
        self._record_pams("spawn_selected", {
            "worm_type": pick["type"],
            "category": pick["category"],
            "priority": pick["priority"],
            "reason": pick["reason"],
            "total_candidates": len(candidates),
        })

        return pick

    def pick_diverse_batch(self, count: int, fleet_status: Any = None) -> List[Dict[str, Any]]:
        """
        Pick a diverse batch of 'count' worm types, each from different categories.

        Returns list of spawn recommendations, each from unique categories.
        """
        picks = []
        used_categories: Set[str] = set()
        used_types: Set[str] = set()

        for _ in range(count):
            next_pick = self.pick_next_spawn(fleet_status=fleet_status)
            if next_pick is None:
                break

            cat = next_pick.get("category", "")
            wtype = next_pick.get("type", "")

            if cat in used_categories or wtype in used_types:
                # Temporarily mark as spawned and try again
                self._last_category = cat
                continue

            picks.append(next_pick)
            used_categories.add(cat)
            used_types.add(wtype)
            self._last_category = cat

        return picks

    def get_staleness_report(self, worm_types_override: Optional[Dict] = None) -> List[Dict]:
        """Get report of which worm types haven't been spawned recently."""
        registry = worm_types_override or WORM_REGISTRY
        now = time.time()
        report = []

        for wtype, info in registry.items():
            spawn_count = info.get("spawn_count", 0)
            last_spawned = info.get("last_spawned")

            hours_since = None
            if last_spawned:
                try:
                    last_time = datetime.fromisoformat(last_spawned).timestamp()
                    hours_since = (now - last_time) / 3600
                except (ValueError, TypeError):
                    pass

            staleness = float("inf") if spawn_count == 0 else (hours_since or float("inf"))

            report.append({
                "type": wtype,
                "category": info.get("category", "utility"),
                "spawn_count": spawn_count,
                "hours_since_last": round(hours_since, 1) if hours_since else None,
                "staleness": staleness,
            })

        # Sort: never-spawned first, then longest since last spawn
        report.sort(key=lambda x: (-x["spawn_count"] if x["spawn_count"] == 0 else 0,
                                    -(x["staleness"] if x["staleness"] != float("inf") else 0)))
        return report

    def get_category_rotation_order(self) -> List[str]:
        """Get the recommended rotation order for categories, accounting for recent spawns."""
        # All known categories
        all_categories = list(set(
            info.get("category", "utility") for info in WORM_REGISTRY.values()
        ))

        # Reorder: last-spawned category goes to the end
        if self._last_category and self._last_category in all_categories:
            all_categories.remove(self._last_category)
            all_categories.append(self._last_category)

        return all_categories

    def _get_time_bonus(self, category: str, hour: int) -> float:
        """Get time-of-day based bonus for a category."""
        # Morning (6-12): monitoring is more useful
        if 6 <= hour < 12:
            if category == "monitor":
                return 2.0
            if category == "sync":
                return 1.0

        # Afternoon (12-18): analysis and optimization
        elif 12 <= hour < 18:
            if category in ("analysis", "optimization"):
                return 2.0
            if category == "diagnostic":
                return 1.5

        # Evening (18-22): defense and diagnostic
        elif 18 <= hour < 22:
            if category in ("defense", "diagnostic"):
                return 2.0

        # Night (22-6): repair and sync
        else:
            if category in ("repair", "sync", "orchestration"):
                return 2.0
            if category == "optimization":
                return 1.5

        return 0.0

    def _get_fleet_bonus(self, category: str, fleet_status: Any) -> float:
        """Get fleet-status based bonus for a category."""
        bonus = 0.0
        try:
            cpu = getattr(fleet_status, "cpu_percent", 0)
            error_count = getattr(fleet_status, "total_failures", 0)
            exec_count = max(getattr(fleet_status, "total_executions", 1), 1)
            error_rate = error_count / exec_count

            # High CPU -> prefer monitors
            if cpu > 70 and category == "monitor":
                bonus += 2.0

            # High error rate -> prefer defense
            if error_rate > 0.1 and category == "defense":
                bonus += 3.0

            # Many failed worms -> prefer repair/diagnostic
            if getattr(fleet_status, "failed", 0) > 3 and category in ("repair", "diagnostic"):
                bonus += 2.0

            # Low activity -> prefer exploratory analysis
            if exec_count < 10 and category in ("analysis", "diagnostic"):
                bonus += 1.5

        except Exception:
            pass

        return bonus

    def _build_reason(self, worm_type: str, category: str,
                      staleness: float, time_bonus: float, fleet_bonus: float) -> str:
        """Build a human-readable reason string for a spawn recommendation."""
        parts = []
        if staleness > 2:
            parts.append("stale")
        if time_bonus > 1:
            parts.append("time_preferred")
        if fleet_bonus > 1:
            parts.append("fleet_needed")
        if not parts:
            parts.append("diversity_rotation")
        return f"{worm_type.lower()}_{'_'.join(parts)}"


# --- Convenience Functions ------------------------------------------

def get_worms_by_category(category: str) -> Dict[str, Dict]:
    """Get all registered worms in a category. Thread-safe: uses _registry_lock."""
    with _registry_lock:
        return {
            name: info for name, info in list(WORM_REGISTRY.items())
            if info.get("category") == category
        }


def get_all_categories() -> Set[str]:
    """Get all unique categories in the registry. Thread-safe: uses _registry_lock."""
    with _registry_lock:
        return set(info.get("category", "utility") for info in list(WORM_REGISTRY.values()))


def get_unspawned_worms() -> List[str]:
    """Get list of worm types that have never been spawned. Thread-safe: uses _registry_lock."""
    with _registry_lock:
        return [
            name for name, info in list(WORM_REGISTRY.items())
            if info.get("spawn_count", 0) == 0
        ]


def mark_spawned(worm_type: str):
    """Mark a worm type as having been spawned (increment counter, set timestamp)."""
    with _registry_lock:
        if worm_type in WORM_REGISTRY:
            WORM_REGISTRY[worm_type]["spawn_count"] += 1
            WORM_REGISTRY[worm_type]["last_spawned"] = datetime.now().isoformat()


def reset_registry():
    """Reset the registry (for testing)."""
    global _discovery_done
    with _registry_lock:
        WORM_REGISTRY.clear()
        _discovery_done = False


# Auto-discover on import
def _auto_discover():
    try:
        discover_worms()
    except Exception:
        pass


# Don't auto-discover at import time (let caller decide when)
