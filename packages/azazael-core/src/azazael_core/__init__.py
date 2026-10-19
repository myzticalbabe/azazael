# coding: utf-8
"""
AZAZAEL Core — Standalone Package
=================================

Re-exports all core functionality from the CORE/ directory for 
standalone installation and usage as `azazael-core`.

Key modules:
  - paths       — Dynamic path resolution (get_project_root, get_desktop_dir, etc.)
  - worm_registry — @register_worm, WORM_REGISTRY, discover_worms()
  - freethreading — Python 3.15t free-threading awareness
  - config      — Config class for centralized configuration

The 50 expansion worms (from CORE/WORMS/expansion/) are bundled at
`azazael_core.worms` and auto-register on import.
The 3 cluster modules (CLUSTERWORMS, METACLUSTER; NATURE_CLUSTERS removed per D1/U3)
are bundled at `azazael_core.worms.clusters` with graceful fallbacks.
"""

# ── Re-export core path utilities ────────────────────────────────────
from .paths import (
    get_project_root,
    get_desktop_dir,
    get_g_drive,
    resolve_path,
    get_src_dir,
    get_output_dir,
    get_core_dir,
    get_worms_dir,
    VERSION as PATHS_VERSION,
)

# ── Re-export worm registry ─────────────────────────────────────────
from .worm_registry import (
    register_worm,
    WORM_REGISTRY,
    SpawnDiversityEngine,
    discover_worms,
    mark_spawned,
    get_unspawned_worms,
    get_all_categories,
    get_worms_by_category,
)

# ── Re-export configuration (Config class with env-aware defaults) ───
from .config import Config

# ── Re-export free-threading utilities ───────────────────────────────
try:
    from .freethreading import (
        is_free_threaded,
        FreeThreadPool,
        ThreadSafeDict,
        ThreadSafeList,
        get_thread_info,
        benchmark_parallel,
    )
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    FreeThreadPool = None
    ThreadSafeDict = dict
    ThreadSafeList = list

    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False

    def get_thread_info() -> dict:
        return {'free_threaded': is_free_threaded()}

    def benchmark_parallel(*args, **kwargs):
        return []

# ── Auto-register bundled expansion worms ───────────────────────────
try:
    from .worms import expansion
except ImportError:
    pass

# ── Import cluster modules (graceful fallback) ────────────────────
try:
    from .worms import clusters
except ImportError:
    pass

__all__ = [
    # paths
    "get_project_root", "get_desktop_dir", "get_g_drive", "resolve_path",
    "get_src_dir", "get_output_dir", "get_core_dir", "get_worms_dir",
    "PATHS_VERSION",
    # worm_registry
    "register_worm", "WORM_REGISTRY", "SpawnDiversityEngine",
    "discover_worms", "mark_spawned", "get_unspawned_worms",
    "get_all_categories", "get_worms_by_category",
    # config
    "Config",
    # freethreading
    "is_free_threaded", "FreeThreadPool", "ThreadSafeDict", "ThreadSafeList",
    "get_thread_info", "benchmark_parallel",
]
