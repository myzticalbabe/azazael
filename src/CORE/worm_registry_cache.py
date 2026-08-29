# coding: utf-8
"""


__all__ = [
    "CACHE_DIR",
    "CACHE_FILE",
    "cache_status",
    "invalidate_cache",
    "load_registry",
    "save_cache",
]

worm_registry_cache.py — Pickle-backed worm registry cache.

Eliminates the 38-45s discover_worms() cold start by caching the registry
to disk via pickle. First call builds cache (~38s); subsequent calls load
from pickle in <0.1s. Invalidates when source files change.

Usage:
    from CORE.worm_registry_cache import load_registry
    load_registry()  # <0.1s when cache is fresh

OR in worm_registry.py:
    from CORE.worm_registry_cache import load_registry
    if not WORM_REGISTRY:
        load_registry()
"""
import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
from typing import Any

__version__ = "1.1.0"

CACHE_DIR = Path.home() / ".azazael"
CACHE_FILE = CACHE_DIR / "worm_registry_cache.pkl"


def _ensure_import_paths():
    """Put all worm import roots on sys.path before unpickling.

    The registry pickle stores live class objects. Worms are imported
    either as bare module names (WORMS dir prepended to sys.path) or as
    ``worms.*`` package-style modules (Vermillion LightFury). Unpickling
    therefore needs both the CORE/WORMS dir and the VF package parent
    importable. Mirrors the resolution in worm_registry.py so the cache
    loads in fresh processes.
    """
    # CORE/WORMS — bare module refs (e.g. BENCHMARK_WORM) go on as-is;
    # src root covers CORE.WORMS.* style refs.
    core_dir = Path(__file__).resolve().parent
    for root in (str(core_dir / "WORMS"), str(core_dir.parent)):
        if root not in sys.path:
            sys.path.insert(0, root)
    # Vermillion LightFury — ``worms.*`` package refs: the worms/ dir is a
    # package, so its PARENT goes on path to make `import worms.x` resolve.
    vf_candidates = []
    env_vf = os.environ.get("VERMILLION_LIGHTFURY_DIR", "")
    if env_vf:
        vf_candidates.append(os.path.join(env_vf, "worms"))
    azazael_root = Path(__file__).resolve().parent.parent.parent
    vf_candidates.append(str(azazael_root / "vermillion_lightfury" / "worms"))
    if os.name == "nt":
        vf_candidates.append(str(Path.home() / "vermillion_lightfury" / "worms"))
    else:
        vf_candidates.append("/root/vermillion_lightfury/worms")

    for cand in vf_candidates:
        worms_dir = Path(cand)
        if worms_dir.is_dir():
            insert = str(worms_dir.parent)
            if insert not in sys.path:
                sys.path.insert(0, insert)


def _get_module_mtimes(worms_dir: str) -> dict:
    """Get modification times of all worm .py files (recursive)."""
    mtimes = {}
    worms_path = Path(worms_dir)
    if not worms_path.is_dir():
        return mtimes
    try:
        for f in sorted(worms_path.rglob("*.py")):
            if not f.name.startswith("_") and not f.name.startswith("."):
                rel = str(f.relative_to(worms_path))
                mtimes[rel] = f.stat().st_mtime
    except OSError:
        pass
    return mtimes


def _is_cache_fresh(worms_dir: str) -> bool:
    """Check if the pickle cache is up to date with source files."""
    if not CACHE_FILE.exists():
        return False
    try:
        _ensure_import_paths()
        with open(CACHE_FILE, "rb") as fh:
            cache = pickle.load(fh)
        cached_mtimes = cache.get("_mtimes", {})
        current_mtimes = _get_module_mtimes(worms_dir)
        if set(cached_mtimes.keys()) != set(current_mtimes.keys()):
            return False
        for name, mtime in current_mtimes.items():
            if abs(cached_mtimes.get(name, 0) - mtime) > 0.01:
                return False
        return True
    except (pickle.PickleError, KeyError, OSError, EOFError, ModuleNotFoundError, ImportError, AttributeError):
        return False


def _load_cache_readonly(worms_dir: str) -> (dict[str, Any] | None):
    """Read registry from pickle cache if fresh. Never rebuilds.

    Safe to call from within discover_worms() — no circular import risk.

    Returns None if cache is stale or missing (caller should fall through
    to normal discovery and call save_cache() afterwards).
    """
    if not _is_cache_fresh(worms_dir):
        return None
    try:
        _ensure_import_paths()
        with open(CACHE_FILE, "rb") as fh:
            cache = pickle.load(fh)
        return {k: v for k, v in cache.items() if not k.startswith("_")}
    except (pickle.PickleError, KeyError, OSError, EOFError, ModuleNotFoundError, ImportError, AttributeError):
        return None


def save_cache(registry: dict[str, Any], worms_dir: str) -> None:
    """Save registry to pickle cache. Called after successful discover_worms().

    Safe to call from within discover_worms() — no circular import risk.
    """
    try:
        from CORE.worm_registry import get_all_categories
    except ImportError:
        get_all_categories = lambda: set(
            info.get("category", "utility") for info in registry.values()
        )

    cache: dict[str, Any] = dict(registry)
    cache["_mtimes"] = _get_module_mtimes(worms_dir)
    cache["_built_at"] = datetime.now().isoformat()
    cache["_total_registered"] = len(registry)
    cache["_categories"] = sorted(get_all_categories())

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "wb") as fh:
        pickle.dump(cache, fh, protocol=pickle.HIGHEST_PROTOCOL)


def load_registry(worms_dir: (str | None) = None, force_rebuild: bool = False) -> dict[str, Any]:
    """Load worm registry from pickle cache, or rebuild if stale.

    Returns the registry dict and populates WORM_REGISTRY as a side effect.
    Subsequent calls return cached data in <0.1s.

    NOTE: Do NOT call this from within discover_worms() — that creates a
    circular import (load_registry -> discover_worms -> load_registry). Use
    _load_cache_readonly() + save_cache() inside discover_worms() instead.

    Args:
        worms_dir: Path to CORE/WORMS directory.
        force_rebuild: If True, skip cache and run full discovery.

    Returns:
        dict with worm registry entries.
    """
    if worms_dir is None:
        worms_dir = str(Path(__file__).resolve().parent / "WORMS")

    # Try cache first (read-only, no rebuild)
    if not force_rebuild:
        registry = _load_cache_readonly(worms_dir)
        if registry is not None:
            # Populate the in-memory WORM_REGISTRY. Unpickling re-imports
            # worm modules, whose @register_worm decorators partially
            # repopulate WORM_REGISTRY as a side effect — so merge only
            # missing keys rather than skipping on non-empty.
            try:
                from CORE.worm_registry import WORM_REGISTRY
                for name, info in registry.items():
                    if name not in WORM_REGISTRY:
                        WORM_REGISTRY[name] = info
            except ImportError:
                pass
            return registry

    # Rebuild: run full discover_worms()
    # Guard: only add to sys.path once
    src_dir = str(Path(worms_dir).parent.parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    if worms_dir not in sys.path:
        sys.path.insert(0, worms_dir)

    from CORE.worm_registry import discover_worms, WORM_REGISTRY

    discover_worms(worms_dir=worms_dir)
    # discover_worms() already calls save_cache() on success, no need to double-save

    return dict(WORM_REGISTRY)


def invalidate_cache():
    """Delete the cache file. Next load_registry() will rebuild."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


def cache_status() -> dict:
    """Return cache status information."""
    if not CACHE_FILE.exists():
        return {"exists": False, "reason": "No cache file"}
    try:
        _ensure_import_paths()
        with open(CACHE_FILE, "rb") as fh:
            data = pickle.load(fh)
        built_at = data.get("_built_at", "unknown")
        return {
            "exists": True,
            "built_at": built_at,
            "worm_count": data.get("_total_registered", 0),
            "total_registered": data.get("_total_registered", 0),
            "categories": data.get("_categories", []),
            "cache_size_kb": round(CACHE_FILE.stat().st_size / 1024, 1),
        }
    except Exception as e:
        return {"exists": False, "reason": str(e)}


# [!]️ No module-level auto-build — would trigger circular import with worm_registry.py
# Cache is built lazily: discover_worms() -> save_cache(), or load_registry() -> save_cache()
