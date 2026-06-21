---
name: azazael-session-recording
description: Session recording — stdlib-only utilities, CodebuffTracker v2.2, timeout avoidance patterns.
metadata:
  category: quality
  project: azazael
---

# Azazael Session Recording — Reliable Patterns

## Quick Start (Always Works)

```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.record_session import SessionRecorder

rec = SessionRecorder()
rec.skill_loaded("azazael-startup")
rec.file_read(["MEMORIES.md", "ERROR_LOG.md"], "canonical files")
rec.milestone("startup complete")
rec.end({"tasks": 5})
```

Completes in **<0.1s**. Zero CORE imports. Zero worm registry discovery.

## Three Recording Methods (Pick One)

### 1. `CORE.record_session.SessionRecorder` (preferred)
- **Location:** `azazael/src/CORE/record_session.py`
- **Import:** `from CORE.record_session import SessionRecorder`
- **Speed:** <0.1s (stdlib only — sqlite3, json, pathlib)
- **API:** Convenience methods: `file_edit()`, `file_create()`, `code_review()`, `test_run()`, `milestone()`, `skill_loaded()`, `tooling_verify()`, etc.
- **Use when:** You need structured recording with clean method names.

### 2. `CORE.codebuff_tracker.CodebuffTracker` (v2.2+)
- **Location:** `azazael/src/CORE/codebuff_tracker.py`
- **Import:** `from CORE.codebuff_tracker import CodebuffTracker, get_tracker`
- **Speed:** <0.1s (uses `_DirectStore` — stdlib-only SQLite backend, no CORE imports)
- **API:** Same as before: `record_file_edit()`, `record_code_review()`, `record_test_run()`, `record_session_start()`, `record_session_end()`, quality validation, atexit handler.
- **Use when:** You want the full CodebuffTracker API with quality validation and atexit safety.
- **Note:** v2.2 defaults to `_DirectStore`. Pass `store=LocalMemoryStore()` only if CORE is already loaded.

### 3. Direct SQLite injection (raw)
- **Speed:** <1s (stdlib only)
- **Use when:** You need bare-metal control or can't import anything.
- **Example:**
```python
import sqlite3, json
from pathlib import Path

db = Path.home() / ".azazael" / "memory_store.db"
conn = sqlite3.connect(str(db))
conn.execute(
    "INSERT INTO memories(session_id,source,event_type,data,severity,tags,timestamp) "
    "VALUES(?,?,?,?,?,?,?)",
    ("sess_001", "Codebuff", "milestone",
     json.dumps({"action": "done"}),
     "info", json.dumps(["session-recording"]),
     "2026-06-06T12:00:00")
)
conn.commit(); conn.close()
```

## Why CodebuffTracker Used to Time Out (and How v2.2 Fixed It)

**v2.1 (broken):** Module-level `from CORE.local_memory import LocalMemoryStore`
triggered worm registry discovery — 300+ files scanned, 91 modules imported —
cold start: 38-45s. Basher timeouts (30s default) killed it every time.
6/6 recording attempts failed.

**v2.2 (fixed):** `_DirectStore` class — stdlib-only SQLite backend,
zero CORE imports. Import + init = **0.06s**. All convenience methods,
quality validation, and atexit handling preserved.

```
CodebuffTracker v2.2 import chain:
  codebuff_tracker.py → _DirectStore (sqlite3, json, pathlib) → DONE (<0.1s)

CodebuffTracker v2.1 import chain (OLD):
  codebuff_tracker.py → CORE.local_memory → discover_worms() → 38-45s → TIMEOUT
```

## Timing Comparison

| Method | Time | Reliability |
|--------|------|-------------|
| `CORE.record_session.SessionRecorder` | **<0.1s** | ✅ Always works |
| `CORE.codebuff_tracker.CodebuffTracker` (v2.2) | **0.06s** | ✅ Always works |
| Direct SQLite injection | <2s | ✅ Always works |
| `CodebuffTracker` (v2.1, old) | 120-300s | ❌ Always times out |
| `LocalMemoryStore` import | 120-300s | ❌ Always times out |

## Related Skills
- `azazael-sop` — Rule 5: mandatory session recording
- `azazael-system-startup` — Startup procedure integration
- `azazael-startup` — Mandatory first skill, loading sequence
