---
name: azazael-sync-kali
description: >-
  Kali WSL2 sync integration — cross-distro sync via the E: drive bridge,
  run_wsl_kali(), batch copy patterns, get_env_status() probing
auto_load: false
---

# azazael-sync-kali — Kali WSL2 Sync Integration

> **Created:** July 8, 2026 (Session 8)
> **Purpose:** Document Kali Linux WSL2 integration in `sync_all.py` — the 6th environment in the hub-and-spoke topology.
> **Cross-reference:** `azazael-sync-wsl`, `scripts/sync_all.py`, `DISCLOSURE_WHITEPAPER_TODO.md` §A6B

## Architecture

Kali Linux on WSL2 has its filesystem inside `ext4.vhdx` — not directly browsable from WSL Ubuntu via `/mnt/e/`. Only `ext4.vhdx` and `shortcut.ico` exist at `E:/Kali/`. All file operations must go through `wsl.exe -d kali-linux`.

### Environment Entry

```python
ENVIRONMENTS = {
    "kali": {
        "root": "E:/Kali/azazael",
        "type": "wsl",
        "wsl_distro": "kali-linux",
    },
}
```

## Key Functions

### `run_wsl_kali(command: str) -> subprocess.CompletedProcess`
Execute commands inside Kali via `wsl -d kali-linux`. All commands are shell-escaped.

```python
def run_wsl_kali(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["wsl", "-d", "kali-linux", "bash", "-c", command],
        capture_output=True, text=True, timeout=30
    )
```

### `sync_wsl_to_kali() -> int`
Batched 3-stage sync from WSL Ubuntu to Kali:

1. **Stage 1 — Collect all files**: `find` all .py/.md files in `/root/azazael/`
2. **Stage 2 — Copy to E: bridge**: Copy all files to `/mnt/e/kali_sync_temp/` (Windows bridge directory)
3. **Stage 3 — Batch import into Kali**: Single `wsl -d kali-linux` command copies all files from `/mnt/e/kali_sync_temp/` into Kali's `/root/azazael/`
4. **Cleanup**: Remove `/mnt/e/kali_sync_temp/` after successful sync

**Why batched?** Each `wsl.exe` subprocess call has ~200ms overhead. For 350+ files, individual copies would take minutes. Batching into a single command reduces this to seconds.

### `get_env_status()` — Kali Probing
Kali's filesystem requires special handling — `Path.exists()` doesn't work. Instead, probe via `wsl.exe`:

```python
result = run_wsl_kali("test -d /root/azazael && echo 'EXISTS' || echo 'MISSING'")
```

### `wsl_path()` — E: Drive Handler
Added E: drive handler alongside existing C: and G: handlers:

```python
if win_path.startswith("E:"):
    return "/mnt/e" + win_path[2:].replace("\\", "/")
```

## CLI Integration

```bash
# Check Kali status (probes ext4.vhdx filesystem)
python3 scripts/sync_all.py --status

# Sync WSL → Kali only
python3 scripts/sync_all.py --sync-to kali

# Full sync including Kali
python3 scripts/sync_all.py --sync-all
```

## Cross-Distro Patterns

| Pattern | Detail |
|---------|--------|
| **Bridge directory** | `/mnt/e/kali_sync_temp/` — Windows E: drive accessible from both WSL distros |
| **wsl.exe dispatch** | `wsl -d kali-linux bash -c "<cmd>"` — cross-distro command execution |
| **Batched copy** | Single `cp -r /mnt/e/kali_sync_temp/* /root/azazael/` in Kali |
| **Cleanup** | `rm -rf /mnt/e/kali_sync_temp/` after successful sync |

## Known Limitations

1. **Kali must be initialized**: No azazael repo exists in Kali by default. First sync requires `--sync-to kali` to create the directory structure.
2. **wsl.exe unavailable from Windows**: Sync from Windows→Kali not yet implemented. Only WSL Ubuntu→Kali path currently wired.
3. **No verify_integrity() for Kali**: File comparison requires cross-distro hash computation — not yet implemented.
4. **E: drive bridge speed**: E: is an SD card — file I/O may be slow for large syncs.

## Related Skills

- `azazael-sync-wsl` — WSL-aware sync_all.py bidirectional sync patterns
- `azazael-paths` — Dynamic path resolution
- `azazael-deploy` — Docker, CLI packaging, G: archive
