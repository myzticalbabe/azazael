# LESSONS — Task J: LocalMemoryStore Tiered C: + G: Storage

**Task:** Fix LocalMemoryStore timeouts caused by C: resource constraints by routing storage to G:
**Date:** June 4, 2026
**Reference:** local_memory.py, LESSONS_MASTER.md #55 (WSL2 path duality), #56 (G: graceful degradation)

---

## Problem

The CodebuffTracker (which uses LocalMemoryStore internally) timed out at 30s when trying to record session actions. Investigation revealed:

| Drive | Total | Free | Usage | Status |
|-------|-------|------|-------|--------|
| **C:** | 756 GB | **51 GB** | **94%** | Critically constrained |
| **G:** | 477 GB | **364 GB** | 24% | Optimal |

**Root cause:** The default storage path was `~/.azazael/memory_store.db` on C:. C: at 94% usage means:
- SQLite WAL/journal files have no room to grow
- VACUUM operations need double the database size in free space
- I/O contention from Windows system processes competing for the same disk
- The tracker's `record_session_start()` → SQLite connection → timeout at 30s

**G: was available with 364GB free but never used** — the storage path had no G: fallback.

---

## Fix: Tiered Storage Resolution

### New resolution order in `_get_store_path()`:

| Priority | Path | When |
|----------|------|------|
| 1 | `AZAZAEL_MEMORY_DIR` env var | Explicit override |
| 2 | `G:/AZAZAEL/memory/memory_store.db` | `G:/AZAZAEL` directory exists (auto-detected) |
| 3 | `~/.azazael/memory_store.db` | Legacy fallback (G: unavailable) |

### Key changes to `src/CORE/local_memory.py`:

```python
def _get_store_path() -> Path:
    env_dir = os.environ.get("AZAZAEL_MEMORY_DIR", "")
    if env_dir:
        base = Path(env_dir)
    else:
        g_memory_base = Path("G:/AZAZAEL/memory")
        if Path("G:/AZAZAEL").exists():  # Check G: is mounted
            base = g_memory_base
        else:
            base = Path.home() / ".azazael"
    base.mkdir(parents=True, exist_ok=True)
    target_db = base / "memory_store.db"
    _migrate_to_g_drive(target_db, base)  # One-time C:→G: migration
    return target_db
```

### One-time migration from C: to G:

`_migrate_to_g_drive()` copies existing `~/.azazael/memory_store.db` (plus WAL/SHM files) to G: on first access. Uses an atomic lock file (`.migration_lock`) to ensure only one process migrates. Logs migration via `logging.getLogger("azazael.memory")`.

---

## Lesson J1: Always Check Disk Space Before Diagnosing Database Timeouts

**Symptom:** LocalMemoryStore operations timeout at 30s with no error message.
**Checklist:**
1. `df -h` or `wmic logicaldisk` — check free space on all drives
2. `ls -la <db_path>` — does the database file exist? How large?
3. `ls -la <db_path>-wal` — check WAL file size (grows unbounded without checkpoint)
4. Is C: above 90% usage? Above 95%? → SQLite needs free space

**Prevention:** Always check disk space before diagnosing database issues. The fastest SQLite in the world won't help if the disk is full.

---

## Lesson J2: Tiered Storage Is Always Better Than Single-Path Default

**Pattern:** External/archive drives (G:) often have vastly more free space than system drives (C:). Always check both and prefer the one with more space.

**Implementation:** Use a resolution chain (env var → external drive → home directory) rather than a single hardcoded default. The `Path.exists()` check makes this automatic — no configuration needed.

**The backup path automatically follows:** `start_auto_backup()` defaults to `Path(self.db_path).parent / "backups"`. When the db moves to G:, backups automatically go to `G:/AZAZAEL/memory/backups/`.

---

## Lesson J3: One-Time Data Migration Must Be Atomic

**Pattern:** `_migrate_to_g_drive()` uses:
1. **Lock file** (`O_CREAT | O_EXCL`) — atomically claims migration responsibility
2. **Copy** existing db + WAL + SHM from C: to G:
3. **Log** the migration for auditability
4. **Clean up** lock file on failure so migration can retry

**Prevention:** Any one-time data migration MUST be:
- Atomic (only one process runs it)
- Complete (copy WAL and SHM, not just the main .db)
- Logged (so CI pipelines can verify)
- Retryable (clean up lock on failure)

---

## Session Actions

| Action | File | Change |
|--------|------|--------|
| Updated `_get_store_path()` | `src/CORE/local_memory.py` | Added G: tier with `Path("G:/AZAZAEL").exists()` check |
| Added `_migrate_to_g_drive()` | `src/CORE/local_memory.py` | One-time atomic C:→G: migration with lock file |
| Created G: directory | `G:/AZAZAEL/memory/` | Storage target with 364GB free |
| Renamed `g_drive` → `g_memory_base` | `src/CORE/local_memory.py` | Clear variable naming |

**Cross-reference:** LESSONS_MASTER.md #55 (WSL2 path duality — same source/dest distinction), #56 (G: graceful degradation — same `Path.exists()` guard pattern)
