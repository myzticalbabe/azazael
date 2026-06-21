# DIRECT_MEMORY_INSTRUCTIONS — Mandatory Session Recording System

> *Created: June 7, 2026*
> *Applies to: All Codebuff / Azazael development sessions*
> *Canonical module: `CORE/direct_memory.py`*

---

## 🔴 MANDATE: DirectMemory Required for ALL Sessions

**Every Codebuff session operating on the Azazael codebase MUST:**

1. **Initialize DirectMemory at session start** (Step 4 of system-startup)
2. **Record ALL session actions** (file reads/edits/creates, skill loads, code reviews, test runs, milestones, errors)
3. **Call `dm.end()` at session completion** with summary data

**Failure to use DirectMemory is a PROCESS VIOLATION.**

---

## Quick Start

```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.direct_memory import DirectMemory

dm = DirectMemory()  # Auto-records session_start + atexit handler

# Record everything
dm.file_read(["MEMORIES.md", "ERROR_LOG.md"], "canonical files")
dm.skill_loaded("azazael-startup")
dm.file_edit("file.py", "Fix bug", lines_changed=3)
dm.code_review("Subject", issues_found=2)
dm.test_run("suite", passed=10, failed=0)
dm.milestone("Phase done", {"count": 5})

# MANDATORY at session end:
dm.end({"tasks_complete": 5, "summary": "What was done"})
```

---

## API Reference

| Method | Purpose | Key Args |
|--------|---------|----------|
| `record(event_type, data, severity, tags)` | Generic event | event_type, data dict |
| `file_read(filepaths, description)` | File reads | List of paths |
| `file_edit(filepath, description, lines_changed)` | File edits | Path, desc, line count |
| `file_create(filepath, description, file_size_bytes)` | File creations | Path, desc, size |
| `file_delete(filepath, description)` | File deletions | Path, reason |
| `skill_loaded(skill_name)` | Skill loads | Skill name |
| `code_review(subject, issues_found, issues_fixed)` | Code reviews | Subject, counts |
| `test_run(test_suite, passed, failed, skipped)` | Test results | Suite name, counts |
| `milestone(title, details)` | Milestones | Title, details dict |
| `tooling_verify(tools_found, tools_missing, details)` | Tooling checks | Found/missing counts |
| `error_occurrence(error_id, title, file_path)` | Error occurrences | Error #NN from ERROR_LOG |
| `end(summary)` | **Session end (MANDATORY)** | Summary dict |

---

## Why DirectMemory Replaces Everything Else

| Old System | Why Deprecated |
|------------|---------------|
| `SessionRecorder` (`record_session.py`) | Same API but no atexit safety, no singleton pattern |
| `CodebuffTracker` (`codebuff_tracker.py`) | 660-line wrapper with quality validation overhead that's never used |
| Direct SQLite injection | Manual, error-prone, no convenience methods |

**DirectMemory** is:
- **Stdlib-only** — zero CORE imports, works immediately
- **<0.1s initialization** — no worm registry discovery
- **Atexit-safe** — auto-records session_end on unexpected exit
- **Same SQLite DB** — cross-session queryable with `LocalMemoryStore`

---

## Memory Store Location

- **Database**: `~/.azazael/memory_store.db` (SQLite)
- **Override**: Set `AZAZAEL_MEMORY_DIR` environment variable
- **Query**: Use `LocalMemoryStore` (`CORE/local_memory.py`) for cross-session queries

---

## Session Lifecycle

```
Session Start
    │
    ├── DirectMemory()        ← Auto-records session_start
    │
    ├── dm.file_read(...)     ← Record file reads
    ├── dm.skill_loaded(...)  ← Record skill loads
    ├── dm.file_edit(...)     ← Record file changes
    ├── dm.code_review(...)   ← Record code reviews
    ├── dm.test_run(...)      ← Record test results
    ├── dm.milestone(...)     ← Record milestones
    │
    └── dm.end(...)           ← MANDATORY: records session_end + marks ended_at
                                  (also auto-called by atexit on unexpected exit)
```

---

## Enforcement Checklist

Before ending ANY Codebuff session on Azazael:

- [ ] `DirectMemory()` initialized at session start
- [ ] All file reads recorded via `dm.file_read()`
- [ ] All file edits/creates/deletes recorded
- [ ] All skill loads recorded via `dm.skill_loaded()`
- [ ] All code reviews recorded via `dm.code_review()`
- [ ] All test runs recorded via `dm.test_run()`
- [ ] All milestones recorded via `dm.milestone()`
- [ ] `dm.end()` called with summary data

---

## Related Files

| File | Purpose |
|------|---------|
| `azazael/src/CORE/direct_memory.py` | Canonical DirectMemory module |
| `azazael/src/CORE/local_memory.py` | Cross-session querying (LocalMemoryStore v2.0) |
| `azazael/src/CORE/record_session.py` | Legacy SessionRecorder (deprecated) |
| `azazael/src/CORE/codebuff_tracker.py` | Legacy CodebuffTracker (deprecated) |
| `azazael/.agents/skills/azazael-system-startup/SKILL.md` | Startup skill with DirectMemory init |
| `azazael/SYSTEM_INSTRUCTIONS.md` | General system instructions |
| `azazael/MEMORIES.md` | Anti-patterns, session history |
