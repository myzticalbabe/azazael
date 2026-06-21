---
name: azazael-exe-build
description: Nuitka .exe building procedures — Python 3.14t required, patched Nuitka, common gotchas, build.bat patterns, standalone deployment.
metadata:
  category: packaging
  project: azazael
---

# Azazael .exe Build Skill

## Overview

This skill documents the procedures for building standalone `.exe` files using Nuitka.
All AZAZAEL standalone executables are built with **Python 3.14t** (free-threading).
Nuitka 4.1.2 requires 9 C-level patches for 3.14t support, applied via `patch_nuitka_314t.py`.

---

## Critical: Python Version Requirement

| Python | Nuitka | PyInstaller |
|--------|--------|-------------|
| 3.14t (free-threading) | ✅ Works (patched) | ❌ Incompatible |
| 3.13.x | ❌ Not used | ❌ Not used |

**Always build with Python 3.14t.** Before building, apply the patches:
```bash
python azazael/docs/scripts/patch_nuitka_314t.py --apply
```

The resulting `.exe` runs fine on any Windows system — no Python required at runtime.

---

## Standard Build Command

```bash
python -m nuitka \
  --standalone \
  --onefile \
  --assume-yes-for-downloads \
  --output-filename=NAME.exe \
  SOURCE_FILE.py
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `--standalone` | Bundle all Python dependencies into the .exe |
| `--onefile` | Single .exe output (not a folder) |
| `--assume-yes-for-downloads` | Non-interactive (required for CI/scripts) |
| `--nofollow-import-to=X` | Exclude optional heavy deps (torch, optree, openvino) |
| `--remove-output` | Clean up build directory after |

---

## azazael-core Build Procedure

### Prerequisites
```bash
# Apply Nuitka 3.14t patches first
python azazael/docs/scripts/patch_nuitka_314t.py --apply

# Install package in dev mode
pip install -e packages/azazael-core/
```

### Build Command
```bash
cd packages/azazael-core
python -m nuitka \
  --standalone \
  --onefile \
  src/azazael_core/cli.py \
  -o azazael-core.exe \
  --nofollow-import-to=torch \
  --nofollow-import-to=optree \
  --nofollow-import-to=openvino
```

### One-Click Build
```cmd
build.bat
```
This script:
1. Applies Nuitka 3.14t patches
2. Installs the package in dev mode
3. Runs Nuitka with the correct flags
4. Reports success/failure

---

## Desktop Standalone Suite Build

The Desktop standalone suite (`Desktop/AZAZAEL_Standalone/`) is built via `build_all.py`:

```bash
cd Desktop/AZAZAEL_Standalone
python build_all.py          # Build all modules
python build_all.py MODULE   # Build single module
```

### Module Inventory (51 modules, 9 tiers)

| Tier | Count | Examples |
|------|-------|----------|
| Core Apps | 3 | CODEX_Studio, AZAZAEL_CLI, AZAZAEL_Toolkit |
| CODEX CORE | 8 | ASCII_Flowchart, Auto_Downloader, Emoji_Maker |
| Analysis + TOOLKIT | 6 | Complete_Systems, Changelog_Gen, QL_Analysis |
| VIDEO Scripts | 4 | Create_Video, Matrix_Video, Compress_Video |
| POPUPS GUI | 4 | POPUP_Simple, POPUP_Clickable, POPUP_Immersive, POPUP_Bugfree |
| WORMS Diagnostics | 13 | CLUSTERWORMS, DISKZ, NETWORXZ, PROCESSZ, etc. |

---

## Typical .exe Sizes

| Dependency Level | Size Range | Examples |
|-----------------|------------|----------|
| Pure Python (stdio) | 4-8 MB | POPUP_Simple, ASCII_Flowchart, CLOCKZ |
| Light deps (pyyaml) | 8-12 MB | azazael-core, Environment_Manager |
| Medium deps (PIL, tkinter) | 12-18 MB | BINARY_Analysis, NETWORK_Diag |
| Heavy deps (numpy, PIL) | 18-25 MB | QL_Optimizer, Math_Certainty |
| GUI + multimedia | 30-35 MB | CODEX_Studio |

---

## Common Gotchas

### 1. Nuitka 3.14t Patches Not Applied
**Symptom:** C compilation errors about `_PyStackRef`, `Py_GIL_DISABLED`, etc.
**Fix:** Run `python azazael/docs/scripts/patch_nuitka_314t.py --apply` before building.

### 2. Heavy Optional Deps Get Bundled
**Symptom:** .exe is 50+ MB because torch/numpy were pulled in
**Fix:** Use `--nofollow-import-to=torch --nofollow-import-to=numpy` for modules that try/except these imports.

### 3. Unicode/Emoji in Terminal Output
**Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode character`
**Fix:** Use `.encode('cp1252', 'replace').decode('cp1252')` to strip non-cp1252 chars before printing.

### 4. __file__ Behaves Differently in Nuitka
**Symptom:** `Path(__file__).parent` resolves to a temp directory
**Fix:** Use `sys.argv[0]` or `Path(sys.executable).parent` for .exe location.

### 5. Nuitka Crash Report
**Symptom:** Build fails with `nuitka-crash-report.xml`
**Fix:** Read the crash report for the specific error. Common causes: missing deps, syntax errors in source.

---

## .bat Launcher Pattern

Each standalone .exe has a companion `.bat` launcher. The correct pattern:

```batch
@echo off
echo AZAZAEL MODULE_NAME
echo.
"%~dp0MODULE_NAME_314t.exe" %*
```

### BROKEN Pattern (52 files affected)
```batch
"C:\Users\clint\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\clint\azazael\src$path" %*
```
The literal `$path` was a template variable that was never substituted. These .bat files are non-functional.

### FIX
All `_314t.bat` files should be regenerated to invoke the `.exe` directly:
```batch
@echo off
echo AZAZAEL MODULE_NAME v3.1.0
echo.
"%~dp0MODULE_NAME_314t.exe" %*
```

---

## CI/CD Build Pattern (GitHub Actions)

```yaml
- name: Apply 3.14t patches
  run: python azazael/docs/scripts/patch_nuitka_314t.py --apply
- name: Build .exe
  run: |
    python -m nuitka \
      --standalone \
      --onefile \
      --assume-yes-for-downloads \
      src/azazael_core/cli.py \
      -o azazael-core.exe \
      --nofollow-import-to=torch \
      --nofollow-import-to=optree \
      --nofollow-import-to=openvino
```

---

## Related Skills
- `azazael-packaging` — Python packaging for free-threading environments
- `azazael-standalone` — Standalone Suite inventory
- `azazael-deploy` — Deployment procedures
