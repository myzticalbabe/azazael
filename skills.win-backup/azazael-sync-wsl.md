---
name: azazael-sync-wsl
description: WSL-aware sync_all.py — bidirectional sync (WSL→Windows, WSL→G:), get_env_status + verify_integrity from WSL. Load when syncing from WSL or troubleshooting environment status.
metadata:
  category: infrastructure
  project: azazael
  version: 1.0.0
  created: July 8, 2026 (Session 6)
---

# azazael-sync-wsl — WSL-Aware sync_all.py

## Overview

`sync_all.py` is the 5-environment bidirectional sync engine. As of Session 6, it is fully WSL-aware — all status, verification, and sync commands work from both Windows and WSL.

**5 environments:**
1. Windows 11: `C:/Users/clint/azazael/` (hub)
2. WSL2 Ubuntu: `/root/azazael/`
3. Desktop: `C:/Users/clint/Desktop/AZAZAEL_Standalone/`
4. G: source-of-truth: `G:/source-of-truth/azazael/`
5. G: AZAZAEL_ROOT: `G:/AZAZAEL/AZAZAEL_ROOT/`

## WSL Detection

```python
IS_WSL = Path("/root/azazael").exists()
```

When `IS_WSL` is True:
- WSL paths (`/root/azazael/`) are accessed directly via `Path.exists()/.glob()`
- Windows paths (`C:/...`, `G:/...`) are converted to `/mnt/c/...`, `/mnt/g/...` via `_resolve_path()`
- `run_wsl()` (which calls `wsl.exe`) is skipped — it doesn't exist on WSL

## Key Functions (WSL-Aware)

### `_resolve_path(p: Path, env_type: str) -> Path`
Converts `C:/G:/` paths → `/mnt/c/`/`mnt/g/` on WSL for non-WSL env types. No-op for WSL envs.

### `get_env_status(env_name, env_info)`
Uses `_resolve_path()` + direct `Path.exists()/.glob()/.rglob()`. No `run_wsl()` calls. Works from both platforms.

### `verify_integrity()`
Uses `_resolve_path()` for win_root and g_source paths. Uses `wsl_files()` helper — `Path.glob()` directly when on WSL, `run_wsl()` fallback on Windows.

### `sync_wsl_to_windows()`
Syncs WSL→Windows via `/mnt/c/Users/clint/azazael/`. Uses `shutil.copy2()` directly.

### `sync_wsl_to_g()`
Syncs WSL→both G: archives via `/mnt/g/` paths.

## CLI Commands

### From WSL
```bash
python3 scripts/sync_all.py --status       # All 5 env status (4/5 reachable from WSL)
python3 scripts/sync_all.py --verify       # Integrity check (tests/scripts subset)
python3 scripts/sync_all.py --sync-all     # WSL→Windows + WSL→G: (skips Windows→WSL)
python3 scripts/sync_all.py --sync-to windows  # WSL→Windows only
python3 scripts/sync_all.py --sync-to g    # WSL→G: archives only
```

### From Windows
```bash
python scripts/sync_all.py --status        # All 5 env status
python scripts/sync_all.py --sync-all      # Windows→WSL + Windows→G: + Windows→Desktop
python scripts/sync_all.py --sync-to wsl2  # Windows→WSL only
python scripts/sync_all.py --sync-to desktop  # Windows→Desktop only
```

## Sync Patterns

```python
SYNC_CODE_PATTERNS   = ["src/CORE/WORMS/expansion/*.py", "src/CORE/WORMS/CLUSTERWORMS.py", ...]
SYNC_DOC_PATTERNS    = ["docs/*.md", "LESSONS_*.md", "MEMORIES*.md", "MASTER_TASKS.md"]
SYNC_SCRIPT_PATTERNS = ["scripts/*.py"]
SYNC_SKILL_PATTERNS  = ["skills/*.md"]
```

## Cross-References

- `azazael-startup` — Session startup procedure
- `azazael-files` — File index and import resolution
- `azazael-deploy` — Docker, CLI packaging, deployment
