# Azazael Architecture — Two-Ledger System

## Overview

Azazael uses a **dual-ledger recording system** for full session observability,
tamper detection, and cross-referencing between DirectMemory (DM) and
AuditTrail (AJ).

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│      DirectMemory (DM)      │     │      AuditTrail (AJ)        │
│  SQLite (memory_store.db)   │◄───►│  JSONL (.audit/ files)      │
│  Structured queryable store │     │  Hash-chained append log    │
│  WAL mode, thread-safe      │     │  Ed25519 signed entries     │
│  Zero CORE imports          │     │  Merkle tree roots          │
│  < 0.1ms per write          │     │  Tamper-evident             │
└───────────┬─────────────────┘     └───────────┬─────────────────┘
            │                                    │
            └───────────── session_mappings ─────┘
                          (SQLite table)
```

## Session Mappings (CD2 — June 15 2026)

The `session_mappings` table in `memory_store.db` provides the cross-reference
bridge between DM and AJ sessions.

### Schema
```sql
session_mappings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    dm_session_id    TEXT NOT NULL,       -- DirectMemory session ID
    audit_filepath   TEXT,                 -- .audit/session_X.jsonl path
    audit_session_id TEXT,                -- AJ session UUID
    correlation_id   TEXT,                -- CD1 cross-domain correlation ID
    linked_at        TEXT DEFAULT (datetime('now')),
    mapping_type     TEXT DEFAULT 'auto',  -- 'auto', 'manual', 'backfill'
    confidence       REAL DEFAULT 1.0,    -- 0.0–1.0 link reliability
    notes            TEXT DEFAULT '',
    UNIQUE(dm_session_id, audit_filepath)
)
```

### Linking Strategies
1. **correlation_id match** (highest priority) — CD1 UUID7 per-instance ID
2. **timestamp proximity** (5s window) — DM session_start ~= AJ session_start
3. **time range overlap** (parallel sessions)

## Event Vocabulary (CD2)

Both ledgers share a common event type vocabulary defined in `EVENT_VOCAB`
(`audit_trail.py`) and `DirectMemory._V` (`direct_memory.py`).

| Key | Canonical Type | DM Method | AJ Function |
|-----|---------------|-----------|-------------|
| SESSION_START | session_start | (auto) | _init_session() |
| SESSION_END | session_end | end() | close_session() |
| FILE_READ | file_read | file_read() | audit_file_read() |
| FILE_EDIT | file_edit | file_edit() | audit_file_edit() |
| FILE_CREATE | file_create | file_create() | audit_file_create() |
| FILE_DELETE | file_delete | file_delete() | audit_file_delete() |
| SKILL_LOADED | skill_loaded | skill_loaded() | audit_skill_loaded() |
| INFERENCE_SPAWN | inference_spawn | inference_spawn() | audit_inference_spawn() |
| TEST_RUN | test_run | test_run() | audit_test_run() |
| CODE_REVIEW | code_review | code_review() | audit_code_review() |
| GATE_PASSED | gate_passed | gate_passed() | audit_gate_passed() |
| SENTINEL_RUN | sentinel_run | sentinel_run() | audit_sentinel_run() |
| SCAN_ANTI_PATTERN | scan_anti_pattern | scan_anti_pattern() | audit_scan_run() |
| SYNC_SKILLS | sync_skills | sync_skills() | audit_sync_run() |
| MILESTONE_REACHED | milestone_reached | milestone() | — |
| TOOLING_VERIFY | tooling_verify | tooling_verify() | audit_tooling_verify() |
| ERROR_OCCURRENCE | error_occurrence | error_occurrence() | audit_error_occurrence() |
| EXPECT_ACTION | expect_action | expect_action() | audit_expect_action() |
| CHAIN_CHECKPOINT | chain_checkpoint | — | (internal) |

## CLI Tools

```
azazael-ctl                    # Unified CLI
├── crossref                   # Cross-reference commands (cli_crossref.py)
│   ├── summary                #   Mapping summary
│   ├── backfill               #   Auto-link sessions
│   ├── list                   #   List all mappings
│   ├── unlinked               #   Show unlinked sessions
│   ├── query <session>        #   Query by session ID
│   ├── corr <id>              #   Query by correlation ID
│   ├── export <csv|json>      #   Export mappings
│   ├── watch                  #   Watch for new sessions
│   ├── diff                   #   Show recent session changes
│   ├── search <type>          #   Search by event type
│   └── interactive            #   Interactive browser
├── audit                      # Audit trail commands (cli_audit.py)
│   ├── status                 #   Health summary
│   ├── verify <file>          #   Chain integrity check
│   ├── search <type>          #   Find entries by type
│   ├── diff <a> <b>           #   Compare two files
│   ├── repair <file>          #   Forensic recovery
│   └── archive <file>         #   Lock file as read-only
├── memory                     # DirectMemory commands (cli_memory.py)
│   ├── status                 #   Health summary
│   ├── recent <n>             #   Recent events
│   ├── stats                  #   Event type distribution
│   ├── search <type>          #   Search by event type
│   ├── timeline <session>     #   Session timeline
│   └── gc                     #   Close stale sessions
├── inference                  # InferencePool commands (planned)
│   ├── benchmark              #   Run benchmark
│   ├── models                 #   List available models
│   └── classify <text>        #   Classify text
├── status                     # Full system health report
└── help                       # Show usage
```

## Key Files

| File | Purpose |
|------|---------|
| `src/CORE/direct_memory.py` | DirectMemory session recorder |
| `src/CORE/audit_trail.py` | Hash-chained audit trail |
| `src/CORE/inference_pool.py` | Parallel LLM dispatcher |
| `src/CORE/freethreading.py` | Free-threading utilities |
| `src/CORE/__init__.py` | Package exports |
| `src/CORE/cli_crossref.py` | Cross-reference CLI |
| `src/CORE/cli_audit.py` | Audit trail CLI |
| `src/CORE/cli_memory.py` | DirectMemory CLI |
| `src/CORE/azazael_ctl.py` | Unified CLI wrapper |
| `src/CORE/vocab_migration.py` | Event type migration tools |
| `src/CORE/audit_repair.py` | Audit trail repair tools |
| `tests/test_session_mappings.py` | Mapping table tests |
| `tests/test_inference_pool.py` | InferencePool tests |

## Testing

```bash
# Run all tests (3.15t production venv)
cd azazael && C:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest tests/ -v

# Run specific test file
C:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest tests/test_session_mappings.py -v
C:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest tests/test_inference_pool.py -v

# Run with live Ollama (requires running server)
C:/Azazael/.venvs/py315t/Scripts/python.exe -m CORE.inference_pool
```
