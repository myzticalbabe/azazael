# ⛔ MANDATORY — THE MEMORY CONTEXT BELOW IS PRE-LOADED. READ IT BEFORE RESPONDING. ⛔

> **This file is read by Codebuff at the start of EVERY session.**
> The memory context below comes directly from `workspace/session_memory.db`.
> It was last updated at session end. No commands needed to load it.

---

## 🧠 CURRENT MEMORY STATE (from session_memory.db)

### Stats
| Table | Count |
|-------|-------|
| Sessions | 28 |
| Decisions | 18 (18 closed ✅) |
| File changes | 19 |
| Lessons | 61 (59 active, 2 deprecated) |
| High-confidence | 58 |
| Goals | 7/7 completed |
| Pending goals | 0 |
| Unlinked lessons | 0 |
| Untagged lessons | 0 |
| Open decisions | 0 |
| Stale lessons | 16 |
| DB integrity | ok (0.14 MB) |

### 46 Active Lessons — Project Landscape

#### 🔴 Bug Fixes — DO NOT reintroduce (10 lessons)
- File-picker hallucinations → verify with `ls`/`find` before acting (conf=0.95)
- Schema drift between dataclass and DB → use numbered migration list (conf=0.95)
- SQLite legacy mode rolls back on `close()` → always `conn.commit()` (conf=0.90)
- `generate_report()` never called → verify print statements match actual I/O (conf=0.85)
- Complex shell commands corrupt JSON → write_file first, then execute (conf=0.85)
- AGENTS.md stats go stale quickly → update at every session end (conf=0.90)
- Decision closure is essential → review open decisions at session end (conf=0.90)
- Session lifecycle must be complete → always end_session() or auto-close runs (conf=0.90)
- Lesson metadata is essential → always set related_files + tags (conf=0.95)
- DB health requires regular audit → run full awareness report at session end (conf=0.90)

#### 🟡 Architecture — System-wide knowledge (34 lessons)

| Project | Readme | Key Details |
|---------|--------|-------------|
| **AZAZAEL Core** | [📄](workspace/projects/azazael/README.md) | Full production wiring — auto-regenerating docs, WAL mode, integrity checks, CLI /review and /dashboard commands. Chain-of-information metadata, worm/hydra orchestration, Python 3.14.5t free-threaded build, auto-close sessions, session lifecycle management |
| **CODEX** | [📄](workspace/projects/codex/README.md) | Documentation/animation subsystem, 54 animation protocols in 12 categories |
| **Eve Unleashed** | [📄](workspace/projects/eve-unleashed/README.md) | Inference engine with 14+ test cases |
| **OpenMono** | [📄](workspace/projects/openmono/README.md) | Multi-agent coding with 20 built-in tools, .NET 9, Docker |
| **OpenMono Go Bridge** | [📄](workspace/projects/openmono-go-bridge/README.md) | 14 tools, goroutine-parallel dispatch, JSON-RPC |
| **OpenMono Rust** | [📄](workspace/projects/openmono-rust/README.md) | Native interop, axum HTTP, OpenVINO + ONNX Runtime |
| **OpenMono iGPU** | [📄](workspace/projects/openmono-igpu/README.md) | Gemma 3 4B on Intel OpenCL, 10.98 tok/s, Qwen 3 at 38 tok/s |
| **PerformanceMonitor** | [📄](workspace/projects/performance-monitor/README.md) | Cross-project system monitoring, hydra integration |
| **Llama Server** | [📄](workspace/projects/llama-server/README.md) | iGPU/CPU inference, OpenVINO SYCL backend |
| **ONNX Runtime 1.18.0** | [📄](workspace/projects/onnx-runtime/README.md) | Cross-platform ML inference, Intel OpenVINO EP |
| **TensorFlow Build** | [📄](workspace/projects/tensorflow/README.md) | CUDA/cuDNN/WSL2 build guide |
| **Open Interpreter** | [📄](workspace/projects/open-interpreter/README.md) | Local LLM code execution agent |
| **PAMS** | [📄](workspace/projects/pams/README.md) | Project awareness — search when drives mounted (conf=0.50) |
| **Python 3.14.5t** | [📄](workspace/projects/python-3145t/README.md) | Free-threaded CPython, cp314 wheels |
| **Production Wiring** | — | WAL mode + PRAGMA tuning, integrity checks, auto-regenerating docs on end_session(), /review CLI command, periodic optimize() |
| **Codebase Organization** | — | Flat ecosystem structure, generated documentation, lesson tagging taxonomy, shared workspace/ infrastructure |

#### 🟢 Conventions — MUST follow (15 lessons)
- AGENTS.md provides mandatory startup instructions (conf=0.95)
- Documentation is generated, not written — source of truth is the session_memory.db (conf=0.90)
- Lesson tagging taxonomy enables cross-project filtering (conf=0.85)
- Lesson confidence must be honest — 0.5 = unknown, 0.95 = proven (conf=0.90)
- End-session review must include decision outcomes (conf=0.95)
- Every new lesson MUST include related_files and tags (conf=0.95)

#### ⚪ Test (1 lesson — deprecated)
- Test pattern for files → `src/foo.py`, `src/bar.py` (deprecated — placeholder, not a real lesson)

### Recent Sessions
- #28: Production wiring lessons (11 new), auto-regenerating docs on end_session(), WAL mode + PRAGMA tuning
- #27: /review command, lesson lifecycle tests (9 tests), check_integrity() + optimize() methods
- #26: Dashboard command working-directory fix, validate_lesson() session_id bump
- #24: Stale lesson cleanup (13 validated, 1 deprecated), per-project READMEs, lessons dashboard HTML

### 18 Decisions (all closed ✅)
All decisions confirmed correct — bootstrap removal, QL fixes, session_memory architecture, AGENTS.md restructuring, project lesson creation, stale validation, XSS-safe dashboard

### Health Report
- **Decision closure rate**: 18/18 closed ✅
- **Unclosed sessions**: 0 (auto-close in start_session() prevents accumulation)
- **Auto-closed sessions**: 11 (previous abandoned sessions, now properly ended)
- **Confidence tiers**: 47 high (≥0.8), 1 medium (PAMS 0.50), 0 low
- **Stale lessons**: 13 (all validated — stale ≠ obsolete, these core rules still apply)

---

## 🚨 STARTUP SEQUENCE — ONE COMMAND ONLY

Start the session recording (context is already loaded above). **Pass recently changed files for file-aware lesson ranking:**

```bash
python3 -c 'import sys; sys.path.insert(0, "azazael/src"); from session_memory import SessionMemory; sm = SessionMemory("workspace/session_memory.db"); sm.start_session("Brief description", "model-name"); print("Session started:", sm.current_session_id)'
```

You have 10 seconds to spawn this as a basher. It's a single simple command with no complex quoting.

---

## 🔄 DURING THE SESSION

Record decisions, changes, and lessons. **Always include related_files and tags on new lessons:**

```bash
python3 -c 'import sys; sys.path.insert(0, "azazael/src"); from session_memory import SessionMemory; sm = SessionMemory("workspace/session_memory.db"); sm.record_decision("context", "decision", "rationale"); sm.record_change("path/to/file", "modified", "what changed"); sm.record_lesson("pattern", "lesson", "category", 0.7, related_files="path/to/file", tags="tag1,tag2"); sm.set_goal("goal", "pending", priority="medium")'
```

---

## 🔚 AT SESSION END — FULL AWARENESS PROTOCOL

### Step 1: End the session (auto-regenerates docs)

```bash
python3 -c 'import sys; sys.path.insert(0, "azazael/src"); from session_memory import SessionMemory; sm = SessionMemory("workspace/session_memory.db"); result = sm.end_session("summary", total_changes=N, goals_completed=M, goals_total=K, regenerate_docs=True); import json; print(json.dumps(result, indent=2))'
```

The result includes `review_needed` and `docs_regenerated` dicts. Docs (dashboard HTML + project READMEs) are auto-regenerated.

### Step 2: Run the Full Awareness Report

```bash
python3 workspace/dump_memory_context.py
```

This outputs ALL DB state: stats, file-ranked lessons, sessions, decisions, hot-spots, goals, stale lessons, review counts, target files, and health report.

### Step 3: Close Open Decisions

The agent MUST review open decisions and record outcomes. At minimum, close the oldest open decisions:

```bash
python3 -c 'import sys; sys.path.insert(0, "azazael/src"); from session_memory import SessionMemory; sm = SessionMemory("workspace/session_memory.db"); sm.update_decision_outcome(1, "Correct — bootstrap removal was necessary"); sm.update_decision_outcome(2, "Correct — SHELL_ALIAS was missing from the hardcoded list"); print("Decisions 1-2 closed")'
```

### Step 4: Validate Stale Lessons

If `get_session_review()` shows stale lessons, validate them. `validate_lesson()` now bumps `session_id` so the lesson exits the stale list automatically:

```bash
python3 -c 'import sys; sys.path.insert(0, "azazael/src"); from session_memory import SessionMemory; sm = SessionMemory("workspace/session_memory.db"); sm.validate_lesson(LESSON_ID); print("Lesson validated")
```

### Step 5: Regenerate Project READMEs

```bash
python3 workspace/regenerate_readmes.py
```

### Step 6: Update AGENTS.md

Run `workspace/dump_memory_context.py` and update the "CURRENT MEMORY STATE" section above with the new data. This ensures the NEXT session gets the updated context automatically.

---

## 🐛 KNOWN PITFALLS

### Pitfall 1: File-Picker Hallucinations
**Fix:** Always verify with `ls`, `find`, or `glob` before acting. (conf=0.95)

### Pitfall 2: SQLite Commit-on-Close
**Fix:** Always `conn.commit()` before `conn.close()`, or use context manager. (conf=0.95)

### Pitfall 3: Hardcoded UI Dimensions
**Fix:** Compute dimensions from actual data. (conf=0.85)

### Pitfall 4: Print Statements Lie
**Fix:** Verify print statements correspond to actual I/O. (conf=0.85)

### Pitfall 5: Agent Spawning JSON Corruption
**Fix:** Keep basher commands simple. For complex scripts, write_file first, then execute. (conf=0.85)

### Pitfall 6: Missing Function Calls
**Fix:** Trace the full call chain. Verify functions are actually called. (conf=0.80)

### Pitfall 7: Relative Path Resolution
**Fix:** Use project-root-relative paths. (conf=0.85)

### Pitfall 8: Not Recording Session Memory
**Fix:** Execute the startup sequence above. Every time. No exceptions. (conf=0.95)

### Pitfall 9: Not Closing Decisions
**Fix:** At session end, review ALL open decisions and record outcomes. The oldest is from session #1. (conf=0.95)

### Pitfall 10: Lessons Without related_files or tags
**Fix:** Every new lesson MUST include `related_files` and `tags` params. Existing empty ones should be backfilled. (conf=0.95)

---

## 📐 PROJECT CONVENTIONS

- **Prefer `str_replace`** over `write_file` for targeted edits
- **Make minimal changes.** Assume every existing line has a purpose
- **Match existing style:** naming, formatting, structure, typing, patterns
- **Verify libraries exist** before using them
- **Don't use `any` type** or equivalent escape hatches
- **Remove unused imports, variables, and files** as part of any change
- **Update all references** when renaming/moving exported symbols
- Run tests after non-trivial changes; fix failures immediately

### Project Structure
- `azazael/src/` — source code (Python modules)
- `azazael/tests/` — test files
- `azazael/scripts/` — shell/bat scripts
- `workspace/` — databases and runtime state (graph.db, session_memory.db)

---

## 🧠 MEMORY SYSTEMS

1. **SQL Persistent Memory** (`workspace/graph.db`) — code structure graph
2. **Session Memory** (`workspace/session_memory.db`) ← **THIS IS IT**
3. Debug Sessions, Dynamic Logger, TELEMETRYZ, METRICZ, HYDRAMETA

---

## 🔑 KEY ARCHITECTURAL DECISIONS (DO NOT REVERSE)

- **Bootstrap removed**: `bootstrap.py` deleted
- **QL_ANALYSIS fixed**: SHELL_ALIAS in matrix, 90-char box, generate_report() called
- **Eve Unleashed**: `azazael/src/eve_unleashed/` — inference engine module
- **ORCHESTRATION cleaned**: duplicates deleted, unique docs moved to CODEX/DOCUMENTATION
- **Docs organized**: .txt docs → `src/docs/`, .bat files → `scripts/`
- **Persistent memory built**: `session_memory.py` + `session_memory.db`
- **DB migration system**: numbered MIGRATIONS list with schema_version tracking
- **Lesson system complete**: file-aware ranking, deprecation, decision links, staleness detection, goal priorities

---

## 📖 REFERENCE

- **Memory Protocol**: `azazael/MEMORY_PROTOCOL.md`
- **Session Memory Module**: `azazael/src/session_memory.py`
- **Code Structure DB**: `azazael/src/persistent_memory.py` → `workspace/graph.db`
- **Full Awareness Report**: `python3 workspace/dump_memory_context.py`
- **Lessons Dashboard**: open `workspace/lessons_dashboard.html` or run `python3 azazael/src/CLI/azazael_cli.py` and type `dashboard`
- **Project Knowledge Base**: browse `workspace/projects/` (regenerate with `python3 workspace/regenerate_readmes.py`)

To see past session history: `python3 azazael/src/session_memory.py --summary`

---

**⛔ The memory context at the TOP of this file is your pre-loaded session data. You already have it. Start a session recording, apply the lessons, and CLOSE OPEN DECISIONS at session end.**
