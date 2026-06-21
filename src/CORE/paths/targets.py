# coding: utf-8
"""
CORE/paths/targets.py — Target list functions for TRIMZ, ERRORZ, etc.

Provides pre-computed lists of target directories used by filesystem
scanning worms. Imports from sibling domain modules at top level
(state → internal → external → targets forms a clean DAG with no cycles).
"""

from pathlib import Path

from .state import _cache
from .external import get_desktop_dir
from .internal import get_src_dir, get_worms_dir, get_meta_dir


def get_desktop_targets() -> list:
    """Get standard Desktop target folders used by TRIMZ, ERRORZ, etc."""
    if "desktop_targets" not in _cache:
        _cache["desktop_targets"] = [
            str(get_desktop_dir() / d) for d in [
                "Azazael", "HYDRA.py", "HORUS.py", "TARBABY.py",
                "POINDEXTER", "PERSEPHONE", "WORMZ", "METAWORMS",
            ]
        ]
    return list(_cache["desktop_targets"])


def get_local_targets() -> list:
    """Get standard local project target folders (matches _PROJECT_ROOT from TRIMZ/ERRORZ)."""
    if "local_targets" not in _cache:
        _cache["local_targets"] = [
            str(get_src_dir()),        # azazael/src/ (matches _PROJECT_ROOT in TRIMZ.py, ERRORZ.py)
            str(get_worms_dir()),      # azazael/src/CORE/WORMS/
            str(get_meta_dir()),       # azazael/src/META/
        ]
    return list(_cache["local_targets"])


def get_trim_targets() -> list:
    """Get TRIMZ-specific target folders (desktop + local, filtered for existence)."""
    if "trim_targets" not in _cache:
        desktop = [p for p in get_desktop_targets() if Path(p).exists()]
        _cache["trim_targets"] = desktop + get_local_targets()[:1]
    return list(_cache["trim_targets"])


def get_error_targets() -> list:
    """Get ERRORZ-specific target folders (desktop + local, filtered for existence)."""
    if "error_targets" not in _cache:
        desktop = [p for p in get_desktop_targets() if Path(p).exists()]
        _cache["error_targets"] = desktop + get_local_targets()
    return list(_cache["error_targets"])
