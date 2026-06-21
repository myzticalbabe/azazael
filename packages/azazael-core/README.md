# AZAZAEL Core

Standalone core package extracted from the AZAZAEL monorepo.

## What is azazael-core?

`azazael-core` is the foundational layer of the AZAZAEL Native Intelligence 
Artifacts platform. It provides:

- **Dynamic Path Resolution** — `paths.py` resolves project roots, desktop directories,
  G: drive mounts, and environment-specific paths without hardcoding.
- **Worm Registry** — `@register_worm` decorator, `WORM_REGISTRY` dict, `discover_worms()`,
  and category management for 77+ diagnostic worm classes.
- **Free-Threading Awareness** — Python 3.14t GIL-disabled support with 
  `FreeThreadPool`, `ThreadSafeDict`, and `ThreadSafeList`.
- **Configuration** — Centralized config loading with YAML/JSON support.
- **Circuit Breaker** — Failure isolation pattern for worm execution.

## Installation

```bash
pip install -e packages/azazael-core
```

Requirements: Python >= 3.14 (free-threading build, 3.14t)

## Quick Start

```python
from azazael_core import get_project_root, discover_worms, get_all_categories

# Resolve project paths dynamically
root = get_project_root()
print(f"Project root: {root}")

# Discover and inspect worms
discover_worms()
for cat in get_all_categories():
    print(f"  {cat}")
```

## CLI Usage

```bash
# After pip install:
azazael-core paths     # Show dynamic project paths
azazael-core registry  # List worm registry contents
azazael-core config    # Show current configuration
azazael-core version   # Print version info
```

## Building Standalone .exe

**Important:** Build with Python 3.14t (free-threading). Python 3.13 is not used.
Nuitka 4.1.2 requires patches for 3.14t support — run
`azazael/docs/scripts/patch_nuitka_314t.py --apply` before building.
Optional imports (torch, optree, openvino) must be excluded since they are
not available in the build environment.

```bash
pip install nuitka

# Apply 3.14t patches first:
python azazael/docs/scripts/patch_nuitka_314t.py --apply

# Build on 3.14t (default python):
python -m nuitka --standalone --onefile src/azazael_core/cli.py \
    -o azazael-core.exe \
    --nofollow-import-to=torch \
    --nofollow-import-to=optree \
    --nofollow-import-to=openvino
```

Result: ~6.8 MB compressed .exe (from ~21.8 MB uncompressed build tree).

## License

MIT — See LICENSE file in parent project.
