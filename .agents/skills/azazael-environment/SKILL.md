---
name: azazael-environment
description: Azazael environment setup — Python 3.10+/3.14t requirements, dependency installation, project path configuration, Windows-specific configuration.
metadata:
  category: workflow
  project: azazael
---
# Azazael Environment

## Python Versions

### REQUIRED: Python 3.14t (Free-Threaded) ONLY

**Python 3.13 is NOT used.** Python 3.14t is the exclusive Python version for ALL workloads:
- Development: all coding, testing, and debugging
- Nuitka builds: all .exe compilation with patched Nuitka 4.1.2
- ML/AI: numpy, torch (CPU), gymnasium, langchain
- Infrastructure: worm registry, cluster execution, database

### Why 3.14t Only
Python 3.14t (free-threading, no-GIL) is the target runtime:
- `ThreadPoolExecutor` for managed thread pools
- `threading.Lock()` for targeted synchronization
- Lock-free data structures for hot paths
- True parallelism for worm cluster execution

The cluster system is designed for free-threading from the ground up.

### Check Version
```python
import sys
ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
ft = hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled()
print(f"Python {ver}")
print(f"Free-threaded: {ft}")
assert ft, "Must run on Python 3.14t free-threading build"
```

## Dependencies

| Package / Tool | Version | Purpose | Install | Package Manager |
|----------------|---------|---------|---------|-----------------|
| Pillow | >=10.0 | CODEX video frame generation | `pip install Pillow` | pip (PyPI) |
| psutil | >=5.9 | System monitoring (PROCESSZ, SYSTEMZ, DISKZ) | `pip install psutil` | pip (PyPI) |
| ffmpeg | any | CODEX .mp4 video encoding | `winget install ffmpeg` | winget |
| **FreeBuff** | 0.0.100 | AI coding agent (CLI) | `npm install -g freebuff` | **npm (NOT pip)** |

### Install All Python Deps
```bash
pip install Pillow psutil
```

### Verify Installations
```python
from PIL import Image; print("Pillow: OK")
import psutil; print(f"psutil: {psutil.__version__}")
```

### 🚨 FreeBuff is npm-only
FreeBuff is **NOT** on PyPI. `pip install freebuff` will always fail with "could not find package."
```bash
# Correct install:
npm install -g freebuff
# Verify:
freebuff --version
```

For full tooling verification at session start, run:
```bash
python scripts/check_tooling.py
```

## Project Path Setup

### Required Before Any Imports
```python
import sys
sys.path.insert(0, 'azazael/src')
```

### Using the Paths Module
```python
from CORE.paths import get_project_root, get_src_dir, get_g_drive, get_output_dir

root = get_project_root()      # Always returns project root
src = get_src_dir()            # azazael/src/
g_drive = get_g_drive()        # Optional[Path] — G:\ drive
output = get_output_dir()      # G:\AZAZAEL\ or project output/
```

## Windows-Specific Configuration

### Encoding
Always set `PYTHONIOENCODING=utf-8` before running:
```bash
set PYTHONIOENCODING=utf-8 && python ...
```

### Fonts for CODEX Video
- Primary: `C:/Windows/Fonts/consola.ttf` (Consolas)
- Fallback: `C:/Windows/Fonts/arial.ttf` (Arial)

### Shell Commands
- Use `rm`/`mkdir`/`mv` in bash (Git Bash, WSL)
- Use `del`/`mkdir`/`move` in cmd.exe
- Prefer Python's `os`/`shutil`/`pathlib` for cross-platform safety

## Related Skills
- `azazael-startup` — Parent: complete 24-skill loading sequence, mandatory first skill
- `azazael-paths` — Centralized path resolution (get_project_root, get_g_drive)
- `azazael-threading` — 3.14t free-threading patterns for parallel execution
