# coding: utf-8
"""
CORE/paths.py — Centralized Dynamic Path Resolution for Azazael Ecosystem.

Replaces hardcoded absolute paths (C:/Users/clint/Desktop/...) with
portable, environment-aware resolution that works across machines.

Usage:
    from CORE.paths import get_project_root, get_azazael_root, get_output_dir
    root = get_project_root()  # azazael/
    src_dir = get_src_dir()    # azazael/src/
    desktop = get_desktop_dir()
    g_drive = get_g_drive()

Environment Variables:
    AZAZAEL_ROOT       — override project root
    AZAZAEL_OUTPUT      — override output directory
    AZAZAEL_ARCHIVE     — override archive directory (default: G:/AZAZAEL/)

Version: 1.0.0
"""

import os
from pathlib import Path


VERSION = "1.0.0"

# ── Cache for computed paths ────────────────────────────────────────────────
_cache: dict = {}


def _resolve_project_root() -> Path:
    """Determine the project root (azazael/) from this file's location."""
    # This file is at: azazael/src/CORE/paths.py
    # Project root is two levels up
    return Path(__file__).resolve().parent.parent.parent


def get_project_root() -> Path:
    """Get the Azazael project root directory.

    Resolution order:
    1. AZAZAEL_ROOT environment variable
    2. Computed from this file's location

    Returns: Path to azazael/
    """
    if "project_root" not in _cache:
        env_root = os.environ.get("AZAZAEL_ROOT")
        _cache["project_root"] = Path(env_root) if env_root else _resolve_project_root()
    return _cache["project_root"]


def get_src_dir() -> Path:
    """Get the azazael/src/ directory."""
    if "src_dir" not in _cache:
        _cache["src_dir"] = get_project_root() / "src"
    return _cache["src_dir"]


def get_output_dir() -> Path:
    """Get the output directory for generated files.

    Resolution order:
    1. AZAZAEL_OUTPUT environment variable
    2. azazael/output/
    """
    if "output_dir" not in _cache:
        env_out = os.environ.get("AZAZAEL_OUTPUT")
        out = Path(env_out) if env_out else get_project_root() / "output"
        out.mkdir(parents=True, exist_ok=True)
        _cache["output_dir"] = out
    return _cache["output_dir"]


def get_desktop_dir() -> Path:
    """Get the user's Desktop directory."""
    if "desktop_dir" not in _cache:
        _cache["desktop_dir"] = Path.home() / "Desktop"
    return _cache["desktop_dir"]


def get_g_drive() -> Path | None:
    """Get the G: drive path if available.

    Resolution order:
    1. AZAZAEL_ARCHIVE environment variable
    2. G:/AZAZAEL/ if G: exists
    3. None if G: is not accessible
    """
    if "g_drive" not in _cache:
        env_arch = os.environ.get("AZAZAEL_ARCHIVE")
        if env_arch:
            _cache["g_drive"] = Path(env_arch)
        else:
            g = Path("G:/")
            _cache["g_drive"] = g / "AZAZAEL" if g.exists() else None
    return _cache["g_drive"]


def get_core_dir() -> Path:
    """Get the azazael/src/CORE/ directory."""
    if "core_dir" not in _cache:
        _cache["core_dir"] = get_src_dir() / "CORE"
    return _cache["core_dir"]


def get_worms_dir() -> Path:
    """Get the azazael/src/CORE/WORMS/ directory."""
    if "worms_dir" not in _cache:
        _cache["worms_dir"] = get_core_dir() / "WORMS"
    return _cache["worms_dir"]


def get_meta_dir() -> Path:
    """Get the azazael/src/META/ directory."""
    if "meta_dir" not in _cache:
        _cache["meta_dir"] = get_src_dir() / "META"
    return _cache["meta_dir"]


def get_codex_dir() -> Path:
    """Get the azazael/src/CODEX/ directory."""
    if "codex_dir" not in _cache:
        _cache["codex_dir"] = get_src_dir() / "CODEX"
    return _cache["codex_dir"]


def get_codex_videos_dir() -> Path:
    """Get the azazael/src/CODEX/VIDEOS/ directory."""
    if "codex_videos_dir" not in _cache:
        _cache["codex_videos_dir"] = get_codex_dir() / "VIDEOS"
    return _cache["codex_videos_dir"]


def resolve_path(path: str) -> Path:
    """Resolve a possibly-relative path against the project root.

    If the path is absolute, return it as-is.
    If it starts with ~, expand it.
    Otherwise, resolve relative to the project root.
    """
    p = Path(path)
    if p.is_absolute():
        return p
    if str(path).startswith("~"):
        return p.expanduser()
    if str(path).startswith("G:"):
        return p
    return get_project_root() / p


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if needed. Returns the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


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


def clear_cache():
    """Clear the path resolution cache (useful for testing)."""
    _cache.clear()


if __name__ == "__main__":
    print(f"CORE/paths.py v{VERSION}")
    print(f"  Project root:  {get_project_root()}")
    print(f"  Src dir:       {get_src_dir()}")
    print(f"  Output dir:    {get_output_dir()}")
    print(f"  Desktop dir:   {get_desktop_dir()}")
    print(f"  G: drive:      {get_g_drive()}")
    print(f"  CORE dir:      {get_core_dir()}")
    print(f"  WORMS dir:     {get_worms_dir()}")
    print(f"  META dir:      {get_meta_dir()}")
    print(f"  CODEX dir:     {get_codex_dir()}")
    print(f"  CODEX/VIDEOS:  {get_codex_videos_dir()}")
