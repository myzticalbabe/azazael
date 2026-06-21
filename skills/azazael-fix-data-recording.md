---
name: azazael-fix-data-recording
description: Quick-reference fixes for database and session recording errors — SQLite WAL mode, PAMS fallback, and memory system issues.
metadata:
  category: fixes
  project: azazael
---

# 🛠️ Skill: Fixes for Database & Session Recording

*Quick-reference solutions extracted from ERROR_LOG.md for known errors in Database & Session Recording.*

## Error #57 — CodebuffTracker/LocalMemoryStore Session Recording Times Out
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
Pre-warm the registry in a separate process BEFORE session recording:
```
# Step 1: Pre-warm registry (takes ~40s but discards process)
python -c "import sys; sys.path.insert(0,'azazael/src'); from CORE.worm_registry import discover_worms; n=discover_worms(); print(f'Warmed: {n}')"

# Step 2: Session recording now works (<2s)
python -c "import sys; sys.path.insert(0,'azazael/src'); from CORE.codebuff_tracker import get_tracker; t=get_tracker(); t.record_session_end({'summary':'ok'})"
```
**Prevention:**
1. Always pre-warm registry before CodebuffTracker or LocalMemoryStore calls
2. Account for minimum 90s timeout on first registry operation
3. Consider running registry warm-up at session start (as part of startup sequence)
4. Cache the Python process to avoid cold-start penalty

---
## Error #64 — PAMS Server DOWN Blocks All Memory Recording
**Symptom:** Local PAMS server (port 21434) is offline/crashed.
**Fix Solution:**
MemoryBus now has SQLite-backed persistent fallback queue (`memorybus_queue` table in memory_store.db). When PAMS is unreachable, messages are persisted to SQLite instead of ephemeral in-memory list. `close()` persists remaining messages. `flush_local_queue()` flushes both in-memory and persistent queues. Version bumped to 1.1.0.
**Prevention:**
Always verify PAMS server is running (`curl http://127.0.0.1:21434/health`). MemoryBus persistent queue survives process restarts.

---
## Error #65 — Session Lifecycle: ended_at=NULL on Hard Kills
**Symptom:** `atexit` handlers do not fire on SIGTERM, SIGINT, or SIGBREAK (hard process kills).
**Fix Solution:**
Added `signal.signal()` handlers for SIGTERM, SIGINT, and SIGBREAK in `DirectMemory.__init__()`. Handler writes `ended_at` + `session_end` directly to SQLite (no lock acquisition to avoid deadlock), then calls `os._exit(128+signum)`. Uses `_signal_ending` flag to prevent re-entry.
**Prevention:**
Signal handlers provide last-resort session closure. Explicit `dm.end()` is still preferred.

---
## Error #66 — Deprecated CodebuffTracker + SessionRecorder Still Importable
**Symptom:** Both deprecated trackers emitted `FutureWarning` on import but were still fully functional.
**Fix Solution:**
Changed `warnings.warn(FutureWarning)` to `raise ImportError(...)` in both files. Removed unused `import warnings`. Unreachable code preserved for reference. All recording now forces use of DirectMemory (stdlib-only, <0.1s).
**Prevention:**
DirectMemory is the sole canonical recording system. Any import of codebuff_tracker or record_session now raises ImportError.

---
## Error #67 — Recording Path Fragmentation: 3 Different session_id Formats
**Symptom:** LocalMemoryStore used `session_%Y%m%d_%H%M%S` format while DirectMemory/CodebuffTracker/SessionRecorder used `codebuff_%Y%m%d_%H%M%S`.
**Fix Solution:**
Changed LocalMemoryStore session_id format to `codebuff_%Y%m%d_%H%M%S`, matching DirectMemory. All 4 recording systems now use the same format.
**Prevention:**
All new recording systems must use `codebuff_%Y%m%d_%H%M%S` format.

---
## Error #69 — DELETE Journal Mode Causes "database is locked" on Concurrent Writes
**Symptom:** All three SQLite connection points used `PRAGMA journal_mode=DELETE`.
**Fix Solution:**
Changed all three to `PRAGMA journal_mode=WAL` with timeout 2→5s, busy_timeout 2000→5000ms, and `wal_autocheckpoint=1000`. DirectMemory.end() and MemoryBus.close() run `PRAGMA wal_checkpoint(TRUNCATE)` before close. Version bumped to 1.1.0.
**Prevention:**
All SQLite connections in Azazael must use WAL mode. Check with `PRAGMA journal_mode`.

---
## Error #70 — MemoryBus Ephemeral Data Loss: In-Memory List on PAMS Downtime
**Symptom:** When PAMS is unreachable, MemoryBus stores messages in an in-memory Python list (`self.
**Fix Solution:**
Added `memorybus_queue` SQLite table to `memory_store.db`. `publish()` now calls `_persist_to_queue()` when falling back. `close()` persists remaining in-memory messages to SQLite before clearing. `flush_local_queue()` flushes both in-memory and persistent queues with batched UPDATE.
**Prevention:**
Any fallback queue must have persistent storage. In-memory-only queues = data loss.

---
## Error #71 — 38s Worm Registry Discovery Blocks CodebuffTracker Initialization
**Symptom:** Importing any `CORE.
**Fix Solution:**
codebuff_tracker.py now raises ImportError on import (see F03). DirectMemory is stdlib-only (<0.1s) and is the canonical path. Nobody can accidentally import codebuff_tracker and trigger worm discovery.
**Prevention:**
DirectMemory (`CORE/direct_memory.py`) is the sole recording system. It has zero CORE imports and always completes in <0.1s.

---
## Error #72 — 6/6 Session Recording Failures Due to 38s Timeout
**Symptom:** Identical root cause to F08 — the 38s worm discovery exhausts the 30s session timeout before any memory system can initialize.
**Fix Solution:**
DirectMemory replaces CodebuffTracker entirely (see F03, F08). It is stdlib-only, has zero CORE imports, completes in <0.1s, and never triggers worm discovery. All 6 recording attempts now succeed.
**Prevention:**
Use DirectMemory for ALL session recording. It is the canonical and only supported system.

---
## Error #73 — PamsRecorder Fallback Layers 3 and 4 Broken
**Symptom:** Fallback layer 3 (`conversations.
**Fix Solution:**
Removed fallback layer 3 entirely. Added `with self._lock` protection around layer 4 `_fallback_buffer.append()`. Layer 2 (LocalMemoryStore, now module-level import) is the primary fallback.
**Prevention:**
Fallback layers must have valid, verified paths and thread-safe writes. Never hardcode paths to external services' internal databases.

---
