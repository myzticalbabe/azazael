---
name: azazael-paths
description: Azazael path resolution — centralized dynamic paths via CORE/paths.py, get_project_root, get_g_drive, caching, environment variable awareness.
metadata:
  category: architecture
  project: azazael
---
# Azazael Paths — Centralized Resolution

## Core File: `CORE/paths.py`

### Path Functions
```python
from CORE.paths import (
    get_project_root,   # Path to azazael/ directory
    get_src_dir,        # Path to azazael/src/
    get_output_dir,     # G:\AZAZAEL\ or project output/
    get_desktop_dir,    # User's desktop
    get_g_drive,        # Optional[Path] — G:\ drive
    clear_cache,        # Clear cached paths (for testing)
)
```

### Usage Patterns
```python
root = get_project_root()
config_path = root / "config" / "settings.yaml"
data_path = root / "data" / "output.json"

# Handle Optional[Path] returns
g_drive = get_g_drive()
if g_drive:
    archive = g_drive / "AZAZAEL" / "CODEX_VIDEOS"
    archive.mkdir(parents=True, exist_ok=True)
```

## Resolution Order

### get_project_root()
1. Check `AZAZAEL_ROOT` environment variable
2. Walk up from `__file__` to find `azazael/src/CORE/`
3. Return parent of `src/` directory

### get_g_drive()
1. Check `AZAZAEL_G_DRIVE` environment variable
2. Check if `G:\` exists on this system
3. Return `None` if not available (callers must handle)

### get_output_dir()
1. Check `AZAZAEL_OUTPUT_DIR` environment variable
2. Use `G:\AZAZAEL\` if G drive available
3. Fall back to project `output/` directory

## Caching

All path functions cache results after first call:
```python
# First call — resolves and caches
root = get_project_root()

# Subsequent calls — returns cached
root = get_project_root()  # Instant

# Force re-resolution (rarely needed)
clear_cache()
root = get_project_root()
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZAZAEL_ROOT` | Override project root | `C:\dev\azazael` |
| `AZAZAEL_G_DRIVE` | Override G drive path | `D:\archive` |
| `AZAZAEL_OUTPUT_DIR` | Override output directory | `C:\output` |
| `PYTHONIOENCODING` | Force UTF-8 on Windows | `utf-8` |

## Integration with Other Modules

### TRIMZ.py and ERRORZ.py
Both have `_LOCAL_TARGETS` and `_DESKTOP_TARGETS` lists. These duplicate path logic that should be centralized in `paths.py`. Migration target:
```python
# Current (in TRIMZ.py):
_LOCAL_TARGETS = [_PROJECT_ROOT]

# Target (consolidate into paths.py):
from CORE.paths import get_local_targets
local_targets = get_local_targets()
```

### Path Safety Rules
- Always use `pathlib.Path`, never string paths
- Always handle `Optional[Path]` with `if path:` checks
- Never hardcode `C:\Users\clint` — use `get_project_root()`
- Never hardcode `G:\` — use `get_g_drive()`

## Related Skills
- `azazael-architecture` — Parent: project layout, key numbers, component overview
- `azazael-files` — Complete file index with import resolution
- `azazael-environment` — Environment variable setup, PYTHONIOENCODING
