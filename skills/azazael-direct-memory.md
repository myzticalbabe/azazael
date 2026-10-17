---
name: azazael-direct-memory
description: DirectMemory — Canonical session recording system. Stdlib-only, <0.1s init, WAL mode, signal-safe, atexit-safe. UUID7 event IDs, CD1 schema compliance.
metadata:
  category: system
  project: azazael
  priority: high
  auto_load: true
---

# Azazael DirectMemory — Canonical Session Recording

> **Canonical source:** `SYSTEM_INSTRUCTIONS.md` (RULE 5), `azazael/DIRECT_MEMORY_INSTRUCTIONS.md`
> **Implementation:** `src/CORE/direct_memory.py`
> **Status:** CANONICAL — replaces deprecated CodebuffTracker + SessionRecorder (hard-blocked)

---

## Overview

DirectMemory is the **CANONICAL** session recording system:
- **Stdlib-only** — zero external dependencies
- **<0.1s init** — no cold start delay
- **WAL mode** — concurrent read/write safe
- **Signal-safe** — survives hard kills
- **atexit-safe** — auto-records session_end on clean exit

---

## Quick Start

```python
import sys; sys.path.insert(0, 'src')
from CORE.direct_memory import DirectMemory

dm = DirectMemory()  # Auto-starts session, auto-records session_start
```

## Recording Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `dm.record(event_type, data)` | Generic event recording | `dm.record("task_start", {"name": "fix bug"})` |
| `dm.file_edit(path, desc, lines_changed)` | File modifications | `dm.file_edit("foo.py", "Fix typo", 1)` |
| `dm.file_create(path, desc, file_size)` | New files | `dm.file_create("new.py", "New module", 500)` |
| `dm.code_review(desc, issues_found, issues_fixed)` | Code reviews | `dm.code_review("Review PR", 2, 1)` |
| `dm.test_run(name, passed, failed)` | Test results | `dm.test_run("unit tests", 10, 0)` |
| `dm.milestone(name, details)` | Phase completion | `dm.milestone("Phase 1", {"files": 5})` |
| `dm.error_occurrence(err_id, title, file)` | Error recording | `dm.error_occurrence(50, "Bug", "app.py")` |
| `dm.end(summary)` | Session end | `dm.end({"tasks": 5})` |

## CD1 Schema Compliance (Error #186)

All records MUST include:
- **`correlation_id`**: UUID7 linking events across memory backends
- **`audit_hash`**: BLAKE2b-256 hash of record content for integrity
- **`schema_version`**: Integer for schema evolution tracking

## UUID7 Usage (RFC 9562)

```python
from CORE.uuid7 import uuid7

event_id = uuid7()  # Time-ordered, sortable, unique
# NOT uuid.uuid4() — that creates un-ordered IDs
```

## Minimum Required Events Per Session

| Event | When | Recorded By |
|-------|------|-------------|
| `session_start` | Session init | Auto-recorded by `DirectMemory()` |
| `tooling_verify` | Each session startup | Auto-recorded by `check_tooling.py` |
| `session_end` | Session completion | `dm.end(summary)` |

## Migration Status

| System | Status | Action |
|--------|:------:|--------|
| **DirectMemory** | ✅ **CANONICAL** | Use for ALL session recording |
| CodebuffTracker | ❌ Hard-blocked | Raises ImportError (F03 fix) |
| SessionRecorder | ❌ Hard-blocked | Raises ImportError (F03 fix) |

## Related Skills

- `azazael-pams-memory` — PAMS/LocalMemoryStore (cross-session queries + FTS5 search)
- `azazael-verifiable-truth` — Audit trail recording (complements DirectMemory)
- `azazael-system-startup` — Step 4 initializes DirectMemory at session start
- `azazael-session-recording` — Session lifecycle management
