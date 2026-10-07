# Forked from src/CORE/worm_registry.py on 2026-05-29 for azazael-core standalone package.
# Sync changes from canonical source when updating.
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
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import threading

# ─── Global Registry ───────────────────────────────────────────────

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


# ─── Decorator ──────────────────────────────────────────────────────

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

    Example:
        @register_worm(category="diagnostic", priority=8, cooldown_seconds=60)
        class NetworkDiag:
            VERSION = "1.0.0"
    """
    def decorator(cls):
        name = cls.__name__
        module = cls.__module__
        source_file = inspect.getfile(cls) if hasattr(inspect, 'getfile') else ""

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

        # Register in sys.modules so __import__ can find it
        return cls

    return decorator


# ─── Auto-Discovery ─────────────────────────────────────────────────

def discover_worms(
    worms_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> int:
    """
    Auto-discover and import all worm modules from CORE/WORMS directory.

    progress_callback: Optional callback(processed, total, module_name),
    mirroring the canonical src/CORE/worm_registry.py API.

    Returns number of newly discovered worm classes.
    """
    global _discovery_done

    if worms_dir is None:
        worms_dir = str(Path(__file__).resolve().parent / "worms")
        if not Path(worms_dir).exists():
            return 0  # Standalone: worms/ not found

    if not os.path.isdir(worms_dir):
        return 0

    before_count = len(WORM_REGISTRY)

    # Add WORMS dir to sys.path temporarily
    if worms_dir not in sys.path:
        sys.path.insert(0, worms_dir)

    _candidates = sorted(
        fn for fn in os.listdir(worms_dir)
        if not fn.startswith(("_", ".")) and fn.endswith(".py")
    )
    for _idx, filename in enumerate(_candidates):
        module_name = filename[:-3]  # strip .py
        # Skip already-registered modules by checking if we have classes from this module
        already_registered = any(
            info.get("source_file", "").endswith(filename)
            for info in WORM_REGISTRY.values()
        )
        if not already_registered:
            try:
                module = importlib.import_module(module_name)
                # Find all classes in the module that look like worms (have VERSION attr)
                for attr_name in dir(module):
                    obj = getattr(module, attr_name)
                    if not inspect.isclass(obj):
                        continue
                    if attr_name.startswith("_"):
                        continue
                    if not hasattr(obj, "VERSION"):
                        continue
                    # Skip config classes
                    if attr_name.endswith("Config"):
                        continue

                    # Auto-categorize based on name
                    category = _guess_category(attr_name, module_name)
                    priority = _guess_priority(attr_name, module_name)
                    cooldown = _guess_cooldown(category)

                    # Register if not already
                    if attr_name not in WORM_REGISTRY:
                        register_fn = register_worm(
                            category=category,
                            priority=priority,
                            cooldown_seconds=cooldown,
                            description=obj.__doc__ or "",
                        )
                        register_fn(obj)
            except Exception as e:
                # Module might have import issues or psutil segfaults
                pass

        if progress_callback:
            progress_callback(_idx + 1, len(_candidates), module_name)

    _discovery_done = True
    return len(WORM_REGISTRY) - before_count


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


# ─── Spawn Diversity Engine ─────────────────────────────────────────

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
    """

    def __init__(self):
        self.spawn_history: List[SpawnRecord] = []
        self._last_category: Optional[str] = None
        self._lock = threading.Lock()

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
            # ── Cooldown check ──
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

            # ── Category rotation ──
            if category == self._last_category:
                continue  # Skip same category as last spawn

            priority = info.get("priority", 5)

            # ── Staleness bonus ──
            spawn_count = info.get("spawn_count", 0)
            staleness_bonus = 0
            if spawn_count == 0:
                staleness_bonus = 5.0  # Never spawned — big bonus
            elif last_spawned:
                try:
                    last_time = datetime.fromisoformat(last_spawned).timestamp()
                    hours_since = (now - last_time) / 3600
                    staleness_bonus = min(3.0, hours_since * 0.5)  # Up to 3.0 bonus
                except (ValueError, TypeError):
                    pass

            # ── Time-based pattern bonus ──
            hour = datetime.now().hour
            time_bonus = self._get_time_bonus(category, hour)

            # ── Fleet status bonus ──
            fleet_bonus = 0
            if fleet_status:
                fleet_bonus = self._get_fleet_bonus(category, fleet_status)

            # ── Compute weighted score ──
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

        return {
            "type": best["type"],
            "priority": best["priority"],
            "reason": best["reason"],
            "category": best["category"],
        }

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

            # High CPU → prefer monitors
            if cpu > 70 and category == "monitor":
                bonus += 2.0

            # High error rate → prefer defense
            if error_rate > 0.1 and category == "defense":
                bonus += 3.0

            # Many failed worms → prefer repair/diagnostic
            if getattr(fleet_status, "failed", 0) > 3 and category in ("repair", "diagnostic"):
                bonus += 2.0

            # Low activity → prefer exploratory analysis
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


# ─── Convenience Functions ──────────────────────────────────────────

def get_worms_by_category(category: str) -> Dict[str, Dict]:
    """Get all registered worms in a category."""
    return {
        name: info for name, info in WORM_REGISTRY.items()
        if info.get("category") == category
    }


def get_all_categories() -> Set[str]:
    """Get all unique categories in the registry."""
    return set(info.get("category", "utility") for info in WORM_REGISTRY.values())


def get_unspawned_worms() -> List[str]:
    """Get list of worm types that have never been spawned."""
    return [
        name for name, info in WORM_REGISTRY.items()
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
