---
name: azazael-pams-memory
description: Persistent AI memory system — LocalMemoryStore (SQLite), PamsRecorder with local fallback, MemoryBus pub/sub, session audit trails, recall/query/search APIs. Load when working with memory storage or investigating memory recall issues.
metadata:
  category: memory
  project: azazael
  priority: high
---

# Azazael PAMS Memory — Persistent AI Memory System

## Overview

The memory system has three layers:

1. **LocalMemoryStore** (`CORE/local_memory.py`) — SQLite-backed persistent store, works OFFLINE
2. **PamsRecorder** (`CORE/PamsRecorder.py`) — Event recorder with LocalMemoryStore fallback
3. **MemoryBus** (`CORE/MemoryBus.py`) — Pub/sub messaging with local queue fallback

The key finding: **PAMS server is not required** for memory to work. LocalMemoryStore provides full CRUD + FTS5 search + recall/query with zero dependencies beyond Python's built-in sqlite3.

## LocalMemoryStore API

```python
from CORE.local_memory import LocalMemoryStore, get_memory_store

store = LocalMemoryStore()  # or get_memory_store() for singleton

# Record events
store.record_event("EveUnleashed", "inference", {"prompt": "...", "tps": 45.2},
                   severity="info", tags=["inference", "test"])

# Query with filters
results = store.query_memories(source="EveUnleashed", event_type="inference", limit=20)

# Full-text search
found = store.search_memories("GPU", source="EveUnleashed")

# Recall recent
recent = store.recall_recent(10)

# List sessions
sessions = store.list_sessions()

# Get full session with all memories
session_data = store.get_session("session_20260529_120000")

# Get statistics
stats = store.get_stats()
# => {total_memories, total_sessions, db_size_mb, sources, event_types, severities}

# Export to JSON
store.export_json("memory_dump.json")

# Maintenance
store.vacuum()
store.purge_old(days=90)
```

## Storage Location

Default: `~/.azazael/memory_store.db`
Override: Set `AZAZAEL_MEMORY_DIR` environment variable

## PamsRecorder v2.0 API

```python
from CORE.PamsRecorder import PamsRecorder, get_recorder

rec = PamsRecorder()  # Singleton

# Record (automatically falls back to LocalMemoryStore if PAMS is down)
rec.record_event("inference", {"prompt": "hello"}, source="EveUnleashed",
                 severity="info", tags=["inference"])

# Query/Recall (new in v2.0!)
results = rec.query_memories(source="EveUnleashed", limit=20)
found = rec.search_memories("error")
recent = rec.recall_recent(5)

# Stats
stats = rec.get_stats()
# => {version, session_id, total_events, local_store_available, local_store: {...}}
```

## Fallback Chain

1. PAMS HTTP API (`http://127.0.0.1:21434/api/memory`) — if server running
2. LocalMemoryStore (SQLite at `~/.azazael/memory_store.db`) — PRIMARY fallback
3. Direct SQLite write to conversations.db — if path exists
4. JSON file buffer (`azazael/data/pams_fallback_records.json`) — last resort

## Why Memory Wasn't Working

Root causes discovered:
1. PAMS server not running (port 8420/21434 not in use)
2. PamsRecorder v1.0 had NO query/recall API — it was write-only!
3. The conversations.db path pointed to a Python site-packages directory that didn't exist
4. JSON fallback worked but had no way to query/search

All fixed in PamsRecorder v2.0 + LocalMemoryStore.

## How to Verify Memory Is Working

```python
from CORE.local_memory import LocalMemoryStore
store = LocalMemoryStore()
store.record_event("test", "verify", {"msg": "hello"})
results = store.query_memories(source="test", limit=1)
assert len(results) > 0, "Memory not working!"
print("Memory OK:", results[0])
```

## Related Files

- `azazael/src/CORE/local_memory.py` — SQLite memory store (primary)
- `azazael/src/CORE/PamsRecorder.py` — Event recorder with local fallback
- `azazael/src/CORE/MemoryBus.py` — Pub/sub messaging bus
- `Desktop/EveUnleashed_Selector/eve_unleashed_app.py` — Eve Unleashed app (consumer)

## Related Skills

- `azazael-codex` — CODEX video + PAMS/MemoryBus patterns
- `azazael-system-startup` — Auto-load startup instructions
- `azazael-eve-unleashed` — Eve Unleashed standalone app
