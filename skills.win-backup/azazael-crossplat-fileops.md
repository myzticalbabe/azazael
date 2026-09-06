---
name: azazael-crossplat-fileops
description: Safe Windows file operations from Git Bash/bash environment — avoid path escaping, data loss, and timeout issues.
metadata:
  category: quality
  project: azazael
---

# Azazael Cross-Platform File Operations

## Problems Solved

1. **Backslash path mangling** — `C:\Users` becomes `C:Users` in bash
2. **Copytree+rmtree data loss** — Timeout kills process mid-move, source deleted but destination incomplete
3. **G: drive slow transfers** — 7.5 GB takes 10+ minutes, timeouts cause partial copies
4. **PowerShell escaping** — `$`, `{}`, `%` get interpreted by bash before reaching PowerShell

## Path Handling

### ❌ NEVER
```bash
# Bash escape sequences destroy backslash paths
python C:\Users\clint\script.py     # FAILS: \U -> U, \D -> D
dir C:\Users\clint\Desktop          # FAILS
```

### ✅ ALWAYS — Three safe patterns

**Pattern 1: Forward slashes (works in Git Bash)**
```bash
python C:/Users/clint/script.py
dir C:/Users/clint/Desktop/CAIN_panels/
```

**Pattern 2: Python pathlib (most portable)**
```python
from pathlib import Path
desktop = Path.home() / "Desktop"
panels_dir = desktop / "CAIN_panels"
for f in sorted(panels_dir.glob("*.png")):
    print(f.name)
```

**Pattern 3: cmd.exe //c prefix (bypasses MSYS2)**
```bash
cmd.exe //c "dir C:\Users\clint\Desktop"
```

## Safe File Moves

### ❌ NEVER — Copy+Delete Pattern (Risk: Data Loss)
```python
# DANGEROUS: If copytree times out but rmtree completes, source is lost
shutil.copytree(src, dst)
shutil.rmtree(src)  # ← Source deleted even if destination incomplete!
```

### ✅ ALWAYS — Verify-Then-Delete Pattern
```python
import shutil
from pathlib import Path

def safe_move(src: Path, dst: Path):
    """Copy, verify, then delete — never delete without verification."""
    if dst.exists():
        shutil.rmtree(dst)
    
    shutil.copytree(src, dst)
    
    # Verify completeness
    src_files = list(src.rglob("*"))
    dst_files = list(dst.rglob("*"))
    src_size = sum(f.stat().st_size for f in src_files if f.is_file())
    dst_size = sum(f.stat().st_size for f in dst_files if f.is_file())
    
    if len(src_files) == len(dst_files) and src_size == dst_size:
        shutil.rmtree(src)
        print(f"Moved {src_size / (1024*1024):.0f} MB - verified OK")
    else:
        print(f"VERIFY FAILED: {len(src_files)} src vs {len(dst_files)} dst files")
        print(f"             {src_size} src vs {dst_size} dst bytes")
        print("Source NOT deleted - data preserved")
```

### For G: Drive (Slow SD Card) — Background Robocopy
```python
import subprocess
from pathlib import Path

def background_robocopy(src: Path, dst: Path):
    """Launch robocopy in background, no timeout issues."""
    cmd = [
        "cmd.exe", "/c", "start", "/b",
        "robocopy", str(src), str(dst), "/E", "/NP",
        ">", str(dst.parent / "robocopy.log"), "2>&1"
    ]
    subprocess.Popen(cmd, shell=True)
    print(f"Background robocopy launched: {src} -> {dst}")
    print("Check progress: findstr /i \"Files\\|Copied\" robocopy.log")
```

## Timeout Guidelines

| Operation | Min Timeout | Notes |
|-----------|-------------|-------|
| `shutil.copytree` (local, <1GB) | 120s | Same drive |
| `shutil.copytree` (G: drive, <5GB) | 600s | SD card, slow |
| `shutil.copytree` (G: drive, >5GB) | 1200s+ | Or use background robocopy |
| `robocopy` via basher | 600s | Use background instead |
| `dir /s` on G: | 60s | Slow directory enumeration |

## Related Skills
- `azazael-powershell-escape` — Safe PowerShell commands from basher
- `azazael-error-prevention` — Anti-pattern #1 (nested quotes)
- `azazael-paths` — Path resolution (get_project_root, get_g_drive)
- `azazael-startup` — Loads this skill at session start
