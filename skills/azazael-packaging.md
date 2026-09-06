---
name: azazael-packaging
description: Python packaging insight — Nuitka builds on Python 3.14t free-threading. Strategy for standalone .exe builds with the patched Nuitka.
---

# Python Packaging for Free-Threading Environments

## Overview
All builds use **Python 3.14.6t** (free-threading) exclusively. Python 3.13 is not used.

### Current Status
| Tool | Python 3.14t |
|------|--------------|
| Nuitka 4.1.2 (patched) | ✅ Works (with 9 C-level patches applied via `patch_nuitka_314t.py`) |
| PyInstaller 6.20 | ❌ Incompatible |

### Nuitka Patches
Before building, apply the 3.14t patches:
```bash
python docs/scripts/patch_nuitka_314t.py --apply
```
This patches allocator.h, SconsPythonBuild.py, and code_generation templates.

## Nuitka Command Template
```bash
python -m nuitka \
  --standalone \
  --onefile \
  --assume-yes-for-downloads \
  --output-dir=OUTPUT_DIR \
  --output-filename=NAME.exe \
  SOURCE_FILE.py
```

## Key Flags
- `--standalone` — Bundles all dependencies
- `--onefile` — Single .exe output
- `--assume-yes-for-downloads` — Non-interactive (required for CI/scripts)
- `--remove-output` — Clean build directory after

## Typical .exe Sizes
- Simple scripts (stdio only): ~4 MB
- GUI scripts (tkinter): ~5-6 MB
- Heavy deps (numpy, PIL): ~14-15 MB
