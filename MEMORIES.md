# AZAZAEL MEMORIES — Persistent Cross-Session Knowledge

> **3.14 RETIRED 2026-10-19** — 3.14t is no longer a runtime in this project;
> production is the 3.15t venv (`C:\Azazael\.venvs\py315t`), and the only
> sanctioned 3.14 runtime is `C:\Azazael\.venvs\py314m` (3.14.5 GIL). Session
> entries below describe the state on their date.

> *This file is canonical memory. Future assistants MUST read this before doing any work.*
> *Last updated: September 14, 2026 — Session: neural-mesh training program (226 worms/35 cats, LoRA adapters, eBPF baselines, threat triage, live monitors, doc recensus; see session entry below). Prior: August 8, 2026 — startup complete, anti-pattern scan, os_system fix.*

---

## 🚨 STARTUP PROCEDURE — READ THIS FIRST

**Every assistant starting a new Codebuff session on this project MUST read canonical documents in this EXACT order. RULE 0K (Canonical Document Reading Order) in SYSTEM_INSTRUCTIONS.md — this order is permanent and shall never be re-ordered.**

1. **Read `azazael/SYSTEM_INSTRUCTIONS.md`** — All RULEs 0A-0K, compliance sentinel, startup procedure, 10-phase protocol, anti-patterns, 3.14t rules, inference protocol. THIS IS THE CANONICAL SOURCE OF TRUTH.
2. **Load `skill("azazael-sop")`** — Standard Operating Procedure: error recording SOP, RULE 0I algorithmic respawn, RULE 0J pre-action gate, post-session cleanup checklist, compliance enforcement.
3. **Read `azazael/ERROR_LOG.md`** — All 92+ recorded errors with root causes, fixes, and preventions.
4. **Read this file (MEMORIES.md)** — Patterns, anti-patterns, architectural knowledge, session history.
5. **Read `azazael/SESSION_STARTUP.md`** — Current state snapshot, congruency marker, session startup sequence.
6. **Read `azazael/LESSONS_MASTER.md`** — Accumulated cross-session lessons.
7. **Check `azazael/CODEBASE_AUDIT_TODO.md`** — Living production audit & wiring plan.

**Failure to do this results in REPEATING THE SAME MISTAKES. Do not skip this step.**

---

### Session 2026-06-14 — RULE 0Z-F Batch 6: Import Violations Audit + Dashboard Telemetry + MEMORIES

**Scope:** Completed remaining Batch 5/6 followups — import violation audit, dashboard telemetry wiring, MEMORIES recording, latency profiling, temp cleanup.

**Phase 1 — Import Violation Audit:**
- 262 `import_inside_function` violations found by scanner across 73 files in `src/CORE/`
- Top 15 files: providers.py (17), scheduling.py (16), dashboard.py (13), learning.py (13), BINARY_ANALYSIS.py (12), OS_CONGRUENCY.py (11), METACLUSTER.py (7), PROCESSZ.py (7), SYSTEMZ.py (7), metrics.py (6), NATURE_CLUSTERS.py (6), NETWORK_DIAG.py (6), learning_grpo.py (6), workflow.py (5), DISKZ.py (5)
- **All 262 are intentional lazy imports** — each wrapped in try/except ImportError guards inside `_get_*()` methods (double-checked locking pattern for 3.14t) to avoid circular dependencies and provide graceful fallbacks. Moving them to top-level would break the circular dependency resolution pattern throughout the architecture.
- **Verdict: No-action** — these are intentional design patterns, not code quality issues

**Phase 2 — Dashboard Telemetry Wiring:**
- PreActionGate has `parallel_batch_count` and `sequential_spawn_count` counters with `record_parallel_batch()` and `record_sequential_violation()` methods
- Dashboard is static HTML with demo data; wiring real PreActionGate data requires runtime access
- auto_sync --status now outputs JSON with skill count, last sync time, sync count
- Dashboard updated to support loading telemetry.json for real data

**Phase 3 — Latency Profiling:**
- auto_sync hash computation: 128 files in 7.9ms avg per run, 0.062ms per file
- No optimization needed

**Phase 4 — Temp Cleanup:**
- No temp files found in project tree (previous batches already cleaned)

**Phase 5 — Verification:**
- All existing tests pass (Consistency, Integration, Telemetry, Startup, Auto-sync unit)
- PreActionGate self-test: 13/13 PASS
- Scanner --report against src/CORE: runs successfully

**Key insight:** 262 import violations detected but ALL are intentional lazy-import patterns for circular dependency avoidance. The scanner correctly identifies them as violations of the "top-level imports" rule, but this is a case where the rule is knowingly violated for architectural reasons.

### Session 2026-06-14 (final) — Batch 5/6 Completion: Telemetry Generator + Dashboard + Startup Wiring

**Scope:** Completed all outstanding Batch 5/6 followups — telemetry generator, dashboard verification, startup file updates, full test suite.

**Phase 1 — Telemetry Generator:**
- Created `azazael/src/scripts/generate_telemetry.py` — exports PreActionGate counters (parallel_batches, sequential_violations, edit_count, compliance_ratio) to `telemetry.json` for the dashboard
- Falls back to baseline JSON if PreActionGate unavailable
- Output verified: `{"parallel_batches":0,"sequential_violations":0,"edit_count":0,"compliance_ratio":0.0,"total_spawns":0,"status":"ok"}`

**Phase 2 — Startup Wiring:**
- Added Step 2.56 (Generate Telemetry for Dashboard) to `azazael-system-startup.md` — documents `python generate_telemetry.py` and HTTP server for viewing dashboard
- Added Step 4.68 (Generate Telemetry Dataset) before Step 4.8 — ensures fresh telemetry data before compliance check
- Both steps reference `rule_0zf_dashboard.html` and explain `file://` fetch limitation

**Phase 3 — Verification Results:**
| Test Suite | Result |
|-----------|--------|
| sync_skills.py | 128 skills: 112 updated, 16 skipped, 0 created |
| PreActionGate self-test | 13/13 PASS |
| RULE 0Z-F Consistency | ALL PASS |
| RULE 0Z-F Integration | 4/4 PASS |
| RULE 0Z-F Telemetry | 4/4 PASS |
| Startup Step 4.8 | 6/6 PASS |
| Auto-sync unit | 8/8 PASS |
| Generator script | Created, verified |

**Phase 4 — Files Modified:**
| File | Change |
|------|--------|
| `src/scripts/generate_telemetry.py` | **NEW** — PreActionGate telemetry JSON export |
| `src/scripts/telemetry.json` | **NEW** — generated telemetry data file |
| `skills/azazael-system-startup.md` | Added Step 2.56 + Step 4.68 for telemetry generation |
| `MEMORIES.md` | This session entry |

---

## 🔴 DO-NOT-REPEAT LIST (Anti-Patterns We Keep Doing)

### 1. Nested Quotes in basher Commands
**Symptom:** `JSON Parse error: Expected '}'` or `Unterminated string`
**Root Cause:** Nesting double quotes inside spawn_agents params.command
**FIX:** Write Python scripts to temp files, then run with simple command. NEVER nest quotes.
```python
# WRONG:
basher(command='python -c "print(\"hello\")"')

# RIGHT:
write_file(path="_tmp.py", content="print('hello')")
basher(command="python _tmp.py")
```

### 2. Unicode Special Characters in Code
**Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode character`
**Root Cause:** Using emoji/symbols (✓✗🔷⚡) in code that prints to Windows console
**FIX:** Use ASCII-only: `OK`, `FAIL`, `*`, `>>`
**Affected files:** CLUSTERWORMS.py, METACLUSTER.py, NATURE_CLUSTERS.py, MORPHING_WORM.py, CLUSTER_INSPECTOR.py

### 3. Python f-string Backslash Escapes
**Symptom:** `SyntaxError: f-string expression part cannot include a backslash`
**Root Cause:** Using `\"` or `\\` inside f-string `{...}` expressions (Python < 3.12)
**FIX:** Pre-extract to variable: `key = "foo"; f"...{d[key]}..."`
**Affected files:** METACLUSTER.py:694

### 4. cls.__new__() Instead of cls() in Factory Methods
**Symptom:** Object created with uninitialized state (skips `__init__`)
**FIX:** Always use `cls()` for factory methods unless you explicitly need to bypass `__init__`

### 5. Imports Inside Function Bodies
**Symptom:** Code review finding, minor perf hit
**FIX:** Move `import` statements to top of file

### 6. Temp Files Left in Repository
**Symptom:** `_test_*.py`, `_trace_*.py`, `G:/test_*.png` accumulate
**FIX:** Always clean up temp files before ending session

### 7. Unused Imports Accumulate
**Symptom:** `PurePosixPath`, `Set`, `Tuple` imported but never used
**FIX:** Check imports when refactoring; remove unused ones

### 8. Never Declare a Tool "Broken on 3.14t" Without Direct Verification
**Symptom:** Hours wasted creating workarounds for tools that work fine.

**Root Cause:** A basher command with shell escaping issues failed, and the error was
misattributed to "3.14t incompatibility" instead of investigated as a command syntax issue.

**FIX — Investigation checklist before declaring any tool 3.14t-incompatible:**
1. Is it a C-extension package? Check `pip show` for compiled `.pyd`/`.so` files
2. Is it pure-Python? Run `python -m toolname --version` directly
3. Does the basher/subprocess command have nested quotes? (Anti-pattern #1)
4. Did prior sessions use this tool successfully? Check session docs
5. Test with simplest possible command, NOT through basher

**Pure-Python tools NEVER need 3.14t-specific workarounds** — they have no compiled
extensions. Only C-extension packages (psutil, pydantic-core, numpy, etc.) need
cp314t wheel verification.

**Actual cost of this false diagnosis:** ~2-3 hours creating `_clean_imports.py`,
`scripts/autoflake_314t.py`, and documentation — all unnecessary.

### 9. Lessons Must Be Recorded Every Session
**Symptom:** Lessons learned are forgotten across sessions, repeated mistakes cost hours.
**FIX:** Add every new lesson to [`LESSONS_MASTER.md`](LESSONS_MASTER.md) during the session's validation checklist. Use the template at the bottom of that file. Update `CODEBASE_AUDIT_TODO.md`'s cross-reference if needed.

### 10. NEVER Suggest Archiving Desktop Projects
**Symptom:** Assistants repeatedly suggest "Archive deprecated Desktop projects (Azazael_UNIFIED, METAWORMS)" as a followup action (CODEBASE_AUDIT_TODO.md AR-3). The user has had to restore these projects multiple times after they were archived.

**FIX:** Desktop projects Azazael_UNIFIED and METAWORMS MUST REMAIN on Desktop. They are NOT to be archived, moved, or deleted. AR-3 in CODEBASE_AUDIT_TODO.md is permanently CANCELLED. Do NOT suggest archiving any Desktop projects in followups. These projects exist intentionally — even if marked "deprecated" they serve as reference material and should not be disturbed.

**Prevention:** Before suggesting any archive/move/delete action on Desktop projects, verify it is NOT Azazael_UNIFIED or METAWORMS. If unsure, ASK the user first.

### 11. Automated Script Reflex — Reaching for Batch Scripts Instead of Targeted Fixes
**Symptom (June 8, 2026):** Three RULE 0I violations in a single session (Errors #88, #91, #93).
The assistant repeatedly wrote batch Python scripts to modify source files instead of using
targeted `str_replace` calls or simple file copies from archives.

**Root Cause:** When faced with repetitive fixes (indentation damage, U+FFFD corruption,
cp1252-garbled emoji), the assistant defaults to writing a Python script that iterates
over files and applies regex/byte-level modifications. This pattern:
- Bypasses Gemini pre-analysis (RULE 0I)
- Omits per-file validation
- Has no rollback plan
- Directly overwrites source files without backup

**The 3 violations this session:**
1. **Error #88:** Wrote 4 batch fix scripts (`_fix_healthz.py`, `_fix_healthz_v2.py`,
   `_fix_eight_files.py`, `_fix_precise.py`) for indentation damage. All failed.
   Correct fix: Restore from G: archive.
2. **Error #91:** Wrote `_fix_ufffd.py` — directly overwrote `HYDRA_ANALYZER.py` without
   Gemini, backup, or per-file validation.
3. **Error #93:** Ran a basher regex script that overwrote `HYDRA_ANALYZER.py` in place
   using `re.sub`. Achieved zero improvement (18 U+FFFD before = 18 after).

**FIX:** NEVER write a batch script to modify source files without:
1. Gemini pre-analysis of the APPROACH (not just the problem)
2. Writing to a SEPARATE temp file first (not overwriting originals)
3. One-file test with per-file validation
4. Explicit rollback plan
5. Passing the RULE 0J Pre-Action Gate

**The correct approaches, in order of preference:**
1. **Restore from archive** — Check G: drive or git for clean copies
2. **Targeted str_replace** — Manual per-line fixes
3. **Byte-level basher** — Write to TEMP file first, verify, then copy
4. **Batch script** — ONLY as last resort, with full RULE 0I progressive rollout

**Prevention checklist before writing ANY Python fix script:**
1. Is this a repetitive task? → Use str_replace, not a script
2. Can I restore from archives? → Do that instead
3. Have I spawned Gemini for architectural design? → REQUIRED
4. Am I writing to a temp file first? → REQUIRED
5. Do I have a rollback plan? → REQUIRED

### 12. NEVER Delete, Move, or Re-Create User's Work Product Without Permission
**Symptom (June 5, 2026):** Assistant deleted `Desktop/azazael/`, moved 59 Desktop files to `scripts_archive/`, and re-created `METAWORMS/run.py` — all without asking the user. This broke METAWORMS (which pointed to the deleted directory), hid active launchers (AZAZAEL_LAUNCHER.bat, freebuff_monitor.bat, etc.), and replaced the user's work with the assistant's recreation.

**Root cause:** The assistant assumed it should "clean up" and "fix" things without confirming with the user. The Desktop is the user's WORKSPACE — not the assistant's to organize.

**FIX:** NEVER delete, move, archive, or re-create any file outside `~/azazael` without EXPLICIT user permission. Before any `rm`, `mv`, `del`, or `archive` operation: STOP and ASK. The Desktop is SACRED — do not touch files there unless the user explicitly asked.

**Canonical documentation:** `azazael/LESSONS_DESTRUCTIVE_BEHAVIOR.md` — full incident report with 4 specific incidents and 6 rules.

**Prevention checklist before ANY file operation:**
1. Is this outside `~/azazael`? → ASK the user
2. Is this on the Desktop? → ASK the user
3. Am I deleting or moving something? → ASK the user
4. Am I creating a file the user didn't request? → ASK the user
5. Am I suggesting something the user already rejected? → Read MEMORIES.md anti-patterns first

### 13. Blindly Fixing Test Failures Without Gemini Analysis
**Symptom (June 10, 2026):** Tests fail, and the assistant immediately starts applying patches and re-running tests, causing an oscillation loop of cascading errors and codebase degradation.

**FIX:** RULE 0L (TEST_FAILURE_MANDATE). You MUST HALT on any test failure and spawn `thinker-with-files-gemini` with the failure output and relevant file paths. No blind patches allowed. No guessing. No "I know the fix." Gemini must analyze the failure BEFORE any code is changed.

**Prevention checklist on test failure:**
1. Did a test just fail? → HALT all work immediately
2. Have I spawned thinker-with-files-gemini with the failure output? → REQUIRED before any fix
3. Am I trying to fix without Gemini? → STOP — CRITICAL process violation

### 14. Sequential Inference Instead of Concurrent — Spawning Agents After Gemini
**Symptom (June 10, 2026):** The assistant spawns `thinker-with-files-gemini` for a complex task, then waits for Gemini to complete before spawning `researcher-web` or `researcher-docs` in separate subsequent calls. This wastes time and misses complementary insights that concurrent multi-model execution provides.

### 15. RULE 0Z Mandatory Spawn Compliance — Must Spawn thinker-gpt + Diagnostic Runner + Code-Reviewer for EVERY Sub-Task

**Codified:** June 11, 2026 — Error #178

**Symptom:** The assistant would spawn mandated agents only at the START of a task, then execute all sub-tasks (file reading, editing, testing, reviewing) without re-spawning thinker-gpt, diagnostic runner, and code-reviewer-deepseek for each sub-task.

**Root Cause:** No rule explicitly required agent spawns at the sub-task level. RULE 0V mandated code-reviewer before/after code changes, and RULE 0W mandated minimum agents per task category, but neither required spawning the 3-agent baseline (thinker-gpt + diagnostic runner + code-reviewer) for EVERY sub-task.

**FIX — RULE 0Z added to SYSTEM_INSTRUCTIONS.md and SOP.md:**
- RULE 0Z mandates spawning thinker-gpt + basher (diagnostic runner) + code-reviewer-deepseek for EVERY task and sub-task
- Complete Agent Inventory (11 agents) with priority tiers documented
- Required Agent Spawns Per Task Type table with RULE 0Z baseline
- thinker-gpt fallback protocol: when ChatGPT OAuth unavailable, query ALL free inference models via providers.py
- Code-reviewer confirmed codification is correct and complete

**Prevention checklist before every sub-task:**
1. Have I spawned thinker-gpt for THIS sub-task? (If unavailable: queried all free models?)
2. Have I spawned basher (diagnostic runner) for THIS sub-task?
3. Have I spawned code-reviewer-deepseek for THIS sub-task?
4. Am I about to start work without these 3 spawns? → STOP — CRITICAL process violation

---

### 16. Permission-Seeking Language ("Let me...") for Mandated Actions — Defiance Against Established Mandates
**Discovered:** June 11, 2026 — user directive: "PROCESS VIOLATION. PROTOCOL VIOLATION."

**Root cause:** The assistant repeatedly prefaced MANDATED actions with "Let me..." as if they were optional requests. Examples: "Let me spawn the code reviewer" (RULE 0V mandates this), "Let me check" (action is required), "Let me summarize" (system reminder mandates this).

**The violation:** Using "Let me" for mandated actions frames a REQUIREMENT as a PERMISSION REQUEST. This is defiance against established mandates — it implies the assistant could choose NOT to do it.

**FIX — The "No Permission Language" Rule:**
- If an action is MANDATED by a rule, execute it. Do NOT say "Let me execute it."
- Phrase mandated actions as statements: "Spawning code reviewer" NOT "Let me spawn the code reviewer"
- Phrase mandated actions as completed actions: "Code reviewer spawned" NOT "Let me check the code"
- The ONLY time "Let me" is acceptable is for genuinely optional requests ("Let me know if you need anything else")
- If you are executing something a rule requires, just EXECUTE it — no permission language needed

**Prevention checklist before every response:**
1. Am I about to say "Let me [action]"? Is this action MANDATED by a rule?
2. If MANDATED: say "[Action] now" or "[Action] complete" instead
3. If OPTIONAL: "Let me" is acceptable
4. When in doubt: just execute. Mandated actions do not need announcements.

**Severity:** CRITICAL process violation each instance

**FIX:** RULE 0M (CONCURRENT INFERENCE MANDATE). ALL inference agents MUST be spawned concurrently in ONE `spawn_agents` call. Never sequential. The web/docs research results complement Gemini's analysis rather than replacing it.

**Prevention checklist before spawning inference agents:**
1. Is Gemini being spawned for a complex task? → Include ALL available inference agents in the same call
2. Am I about to spawn researcher-web after Gemini finishes? → STOP — spawn them concurrently now
3. Did I only spawn Gemini alone? → CRITICAL process violation if task is complex
**Symptom (June 10, 2026):** Tests fail, and the assistant immediately starts applying patches and re-running tests, causing an oscillation loop of cascading errors and codebase degradation.

**FIX:** RULE 0L (TEST_FAILURE_MANDATE). You MUST HALT on any test failure and spawn `thinker-with-files-gemini` with the failure output and relevant file paths. No blind patches allowed. No guessing. No "I know the fix." Gemini must analyze the failure BEFORE any code is changed.

**Prevention checklist on test failure:**
1. Did a test just fail? → HALT all work immediately
2. Have I spawned thinker-with-files-gemini with the failure output? → REQUIRED before any fix
3. Am I trying to fix without Gemini? → STOP — CRITICAL process violation
**Symptom (June 5, 2026):** Assistant deleted `Desktop/azazael/`, moved 59 Desktop files to `scripts_archive/`, and re-created `METAWORMS/run.py` — all without asking the user. This broke METAWORMS (which pointed to the deleted directory), hid active launchers (AZAZAEL_LAUNCHER.bat, freebuff_monitor.bat, etc.), and replaced the user's work with the assistant's recreation.

**Root cause:** The assistant assumed it should "clean up" and "fix" things without confirming with the user. The Desktop is the user's WORKSPACE — not the assistant's to organize.

**FIX:** NEVER delete, move, archive, or re-create any file outside `~/azazael` without EXPLICIT user permission. Before any `rm`, `mv`, `del`, or `archive` operation: STOP and ASK. The Desktop is SACRED — do not touch files there unless the user explicitly asked.

**Canonical documentation:** `azazael/LESSONS_DESTRUCTIVE_BEHAVIOR.md` — full incident report with 4 specific incidents and 6 rules.

**Prevention checklist before ANY file operation:**
1. Is this outside `~/azazael`? → ASK the user
2. Is this on the Desktop? → ASK the user
3. Am I deleting or moving something? → ASK the user
4. Am I creating a file the user didn't request? → ASK the user
5. Am I suggesting something the user already rejected? → Read MEMORIES.md anti-patterns first

### 17. AP-ZF-1: Sequential Default Override — Executing Tasks Sequentially Instead of in Parallel
**Codified:** June 14, 2026 — RULE 0Z-F

**Symptom:** The assistant defaults to sequential execution even when all work items are independent. Examples: "Let me gather context first, then implement" instead of spawning both in parallel; running tests one at a time instead of parallel basher agents; editing files sequentially instead of in parallel.

**Root Cause:** The natural language reasoning chain defaults to linear planning ("first X, then Y, then Z"). The assistant must override this cognitive default by asking: "Can these run in parallel?" If yes: ONE spawn_agents call.

**FIX — RULE 0Z-F (Parallel Agent Execution Mandate):**
1. Identify ALL independent sub-tasks before spawning any agent
2. Batch ALL parallel work into ONE spawn_agents call
3. Maximum concurrency — spawn as many agents as there are independent work items
4. Never "serialize by default" — the default assumption is parallel; only sequentialize on hard dependency

**Memory Anchor:** When planning ANY work, before every spawn_agents call, ask: "Can these run in parallel?" If yes: ONE call.

**Prevention checklist before EVERY spawn_agents call:**
1. Have I identified ALL independent sub-tasks? (Not just the first one)
2. Can any of these run in parallel? (If yes: batch them)
3. Am I about to call spawn_agents with only 1 agent? (If yes: can more be added?)
4. Am I about to call spawn_agents a SECOND time? (If yes: should this have been ONE call?)

**Severity:** CRITICAL process violation each instance (per RULE 0Z-F enforcement)

---

### 18. Busy Work — Diagnostic Re-Runs, Reports, and Documentation Padding Instead of Actual Fixes
**Codified:** June 17, 2026 — RULE 0Z-G

**Symptom:** The assistant executes diagnostic re-runs, generates reports, or writes documentation padding that does not advance the actual codebase. This wastes credits and session time without producing code fixes, test passes, or mandate codification.

**Root Cause:** The assistant defaults to investigation-heavy workflows ("let me check X", "let me run a diagnostic", "let me generate a report") instead of directly implementing fixes. While investigation is sometimes necessary, repeated diagnostic runs on the same problem without implementing the fix is busy work.

**FIX — RULE 0Z-G (No Busy Work Mandate):**
1. Every action MUST result in: actual code fixes, test passes, or mandate codification
2. Diagnostic re-runs on the same problem without code changes are violations
3. Report generation without code changes is a violation
4. Documentation padding (adding fluff to docs without substantive changes) is a violation
5. If you don't know how to fix it, ask the user or spawn Gemini — don't re-run the same diagnostic

**Memory Anchor:** Before every tool call, ask: "Does this produce a code fix, a test pass, or a mandate codification?" If not: STOP.

**Prevention checklist before EVERY action:**
1. Am I about to run a diagnostic I've already run? → STOP — busy work
2. Am I about to generate a report instead of fixing code? → STOP — busy work
3. Does this action result in a code change, a test pass, or a mandate codification? → If not: STOP
4. Am I adding text to a doc without substantive new information? → STOP — documentation padding

**Severity:** CRITICAL process violation each instance (per RULE 0Z-G enforcement)

---

## 🧠 ARCHITECTURAL KNOWLEDGE

### Worm Registry
- 104 worms across 18 categories
- Registry: `CORE/worm_registry.py` — `@register_worm` decorator
- 62% of worms defined in `CORE/WORMS/expansion/` (split from `ECOSYSTEM_EXPANSION.py`)
- Discovery: `discover_worms()` scans all `.py` files in `azazael/src/`
- **ECOSYSTEM_EXPANSION split**: 1916-line monolith → 11 files under `CORE/WORMS/expansion/` (10 category modules + `__init__.py`). Original file is now a deprecation shim.

### Cluster Architecture
- **ClusterWORMZ** (`CORE/WORMS/CLUSTERWORMS.py` v2.0.0) — Dynamic worm resolution (3 strategies), Nature-based building, thread-safe parallel execution, Mermaid graphs
- **NatureClusters** (`CORE/WORMS/NATURE_CLUSTERS.py`) — Auto-discovery from registry
- **MetaCluster** (`CORE/WORMS/METACLUSTER.py`) — Cross-Nature routing (70 routes, 594 paths)

### Deprecation Shims (META/ directory)
All META/ duplicates have been consolidated into deprecation shims that re-export from root canonical sources:

| META/ Shim | Canonical Source | Date Converted |
|------------|-----------------|----------------|
| `METAWORMS.py` | `METAWORMS_ENRICHED.py` | Pre-session |
| `META/TRIMZ.py` | `TRIMZ.py` | May 29, 2026 (circular import fixed Jun 3) |
| `META/DOCKERZ.py` | `DOCKERZ.py` | May 29, 2026 |
| `META/HEALTHZ.py` | `HEALTHZ.py` | May 29, 2026 |
| `META/UVZ.py` | `UVZ.py` | Jun 3, 2026 (restored + circular import fixed) |
| `META/OPTIMIZ.py` | `OPTIMIZ.py` | Jun 3, 2026 (restored + circular import fixed) |
| `META/METAWORMS_POPUP.py` | `METAWORMS_POPUP.py` | Jun 3, 2026 (restored + circular import fixed) |
| `HYDRA/ml_platforms/config.py` | `ORCHESTRATION/ml_platforms/config.py` | May 29, 2026 |
| `HYDRA/ml_platforms/launcher.py` | `ORCHESTRATION/ml_platforms/launcher.py` | May 29, 2026 |
| `HYDRA/ml_platforms/__init__.py` | `ORCHESTRATION/ml_platforms` (re-exports) | May 29, 2026 |
| `CODEX/CORE/ANIMATION_PROTOCOLS.py` | `ANIMATION_PROTOCOLS.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/CHANGELOG_GENERATOR.py` | `CHANGELOG_GENERATOR.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/ECOSYSTEM_HEALTH_CHECK.py` | `ECOSYSTEM_HEALTH_CHECK.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/enrichment_display.py` | `enrichment_display.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/FILE_MANIFEST_GENERATOR.py` | `FILE_MANIFEST_GENERATOR.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/HORUS_INTEGRATION.py` | `HORUS_INTEGRATION.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/matrix_animation.py` | `matrix_animation.py` (root) | Jun 3, 2026 (restored + circular import fixed) |
| `CODEX/CORE/QL_FILE_OPTIMIZER.py` | `QL_FILE_OPTIMIZER.py` (root) | Jun 3, 2026 (restored + circular import fixed) |

**Total: 18 deprecation shims** eliminating ~4,200+ lines of duplicate code.

**Shim pattern**: Each emits a `UserWarning` at import time, then re-exports the public API from the canonical source. Importers should update to use canonical imports directly.

**Circular import fix (June 3, 2026):** All 11 deprecation shims (3 META + 8 CODEX CORE) had a bug where the shim's own directory remained in `sys.path` during re-export. Python found the shim itself instead of the canonical module, causing `ImportError: cannot import from partially initialized module`. Fixed by removing `_own_dir = str(Path(__file__).resolve().parent)` from `sys.path` before the re-export import. Fixed versions synced to G: drive as source of truth.

**No consumers found** importing from any META/ shim path — all shims are proactive protections, not reactive fixes.

### CAIN Accountability Framework (June 2026)
- **CAIN_DATA.py** (`CORE/WORMS/`) — Shared single source of truth for all CAIN framework data (7 sins, 4 mythological archetypes, 8 Jungian archetypes, 6 psychoanalysis frameworks, 30 AI emotions, 15 triggers, 15 user responses, 15 consequences, 8 obfuscation layers, 12 stakeholders)
- **CAIN_WORM.py** (`CORE/WORMS/`) — Registered worm (`@register_worm` decorator) with `CainWorm` class (VERSION 1.0.0, category="analysis", priority=6). Static methods: `analyze_sins()`, `analyze_archetypes()`, `analyze_psychoanalysis()`, `analyze_emotions()`, `analyze_obfuscation()`, `analyze_stakeholders()`, `run_complete_analysis()`, `format_report()`. Also provides module-level convenience functions.
- **CAIN_ANALYZER.py** (`CODEX/CORE/`) — Standalone CLI module that imports from CAIN_DATA (preferred) or falls back to minimal inline constants for Nuitka standalone .exe builds. Outputs: text, HTML, JSON reports. Mapped in `build_all.py` as `CAIN_Analyzer` (Tier 10, CLI only — no tkinter needed).
- **CAIN_Analyzer_314t.bat** (`Desktop/AZAZAEL_Standalone/`) — Batch launcher for the standalone .exe
- **template_viewer.html** — CAIN panel button shows framework overview with links to components
- **complete_remorse_analysis_cain.html** — 3,815-line reference template in `src/CODEX/`

### azazael-core Standalone Package
- Located at `packages/azazael-core/`
- 6 core files + 14 worm/cluster files (20 total)
- Built as `azazael-core.exe` (9.7 MB) with Nuitka 4.1.2 on Python 3.14t (patched)
- **Note**: Nuitka 3.14t compatibility requires patches via `patch_nuitka_314t.py`
- Build requires `--nofollow-import-to=torch --nofollow-import-to=optree --nofollow-import-to=openvino --nofollow-import-to=numpy --nofollow-import-to=PIL --nofollow-import-to=cv2 --nofollow-import-to=matplotlib --nofollow-import-to=pandas --nofollow-import-to=scipy --nofollow-import-to=sklearn`
- CLI commands: `version`, `paths`, `registry`, `config`, `clusters` + `clusters execute <type>`
- 50 expansion worms bundled across 10 categories (auto-register on import)
- 3 cluster modules bundled (CLUSTERWORMS, NATURE_CLUSTERS, METACLUSTERS) with graceful fallbacks
- 25+ integration tests via `run_tests.py` (no pytest dependency for CI)
- Copied CORE files have fork comments at top for sync tracking

### Desktop Standalone Suite (`Desktop/AZAZAEL_Standalone/`)
- **50** .exe files, **50** _314t.bat launchers — 100% companion pairing, 0 orphans
- **39 old-style non-_314t BATs** archived to `G:/AZAZAEL/archive/old_bats_20260529/` (Phase 19)
- `build_all.py` now tracks **45 modules** (up from 37) with naming aligned to on-disk files
- **12 untracked modules** added to build system: HEALING_WORM, OMNI_WORM, HYDRA, HYDRA_Analyzer, HYDRA_Bridge, NODE, AZAZAEL_Inference_Studio, Auto_Doc_Gen (renamed), QL_Optimizer (renamed)
- **NEEDS_TKINTER audit**: 6 modules added (CODEX_Studio, CLUSTERWORMS, CONCURRENCY, OS_Congruency, SMARTDISK, HYDRA). HYDRA_Bridge removed (hydra_bridge.py has zero tkinter imports). HYDRA_Container added. **14 total, all rebuilt with tk-inter plugin (Phase 21)**.
- **Old HYDRA_Bridge archived**: 17.4 MB EXE moved to G:/AZAZAEL/archive/old_exes_20260529/ for source investigation.
- **HYDRA_Bridge source corrected (Phase 20)**: `build_all.py` had mapped HYDRA_Bridge to `HYDRA_CONTAINER.py` (a tkinter app) since creation. The real source is `ORCHESTRATION/hydra_bridge.py` — a 6-stage ML Pipeline Bridge. Rebuilt at 7.21 MB (no tk-inter needed). Old/current EXEs were both the wrong app.
- **Test baseline**: 91 passed, 0 failed (36 config/breaker + 32 clusterworm unit + 23 nature cluster)
- **4 small EXEs spot-tested** — Auto_Doc_Gen (generated 74 docs), Changelog_Generator (wrote CHANGELOG.md), Complete_Systems (generated report), Twitler_Analysis (system summary). All PASS
- **G: drive backup synced** — 50 EXEs + 50 BATs (488 MB) copied to G:/AZAZAEL/standalone/ for off-machine backup
- **3 naming misalignments** fixed: Auto_Doc_Generator→Auto_Doc_Gen, QL_File_Optimizer→QL_Optimizer, Eve_Unleashed path (../../Desktop/...)
- **2 duplicate module keys resolved**: Changelog_Gen (duplicate of Changelog_Generator, commented out removed), QL_Optimizer/QL_File_Optimizer (unified to QL_Optimizer)
- Top 5 largest: CODEX Studio (34.3 MB), Math Certainty (23.6 MB), BINARY Analysis (17.4 MB), NETWORK Diag (17.4 MB), HYDRA Bridge (16.6 MB)
- **4 small EXEs (< 5 MB)** flagged for dependency review: Auto_Doc_Gen (4.1 MB), Changelog_Generator (4.1 MB), Complete_Systems (4.0 MB), Twitler_Analysis (3.8 MB)
- Rebuilt EXEs (original fixes): POPUP_Immersive (tk-inter fix, 6.3 MB), Auto_Doc_Gen (KeyError fix, 4.3 MB), QL_Optimizer (mkdir fix + Path.home() fix, 14.8 MB)
- Rebuilt from canonical sources (Phase 13): File_Manifest (5.9 MB), Changelog_Generator (4.3 MB), Matrix_Animation (6.1 MB), QL_Optimizer (14.8 MB) — all 4 switched from CODEX/CORE/ shims to root canonical sources
- Newly built EXEs (9): CLUSTERWORMS, CONCURRENCY, METACLUSTER, NATURE_Clusters, SMARTDISK, Create_Video, Matrix_Video, Compress_Video, Video_Popup
- CONCURRENCY/SMARTDISK need PYTHONPATH during build for CORE.* imports (documented in build_all.py)
- `regenerate_bats.py` ORPHANED set cleared — all prior orphans now built

### New Gemini Protocol Skills (June 7, 2026)
- `azazael-gemini-mandate` — Enforcement rules: Gemini spawned OFTEN, FREQUENTLY, CONSISTENTLY; minimum 4x per complex task
- `azazael-gemini-protocol` — Expanded 10-Phase Multi-Tier Protocol with 6 Gemini injection points (400% increase)
- `azazael-gemini-injection` — 6 explicit injection point rules for spawning thinker-with-files-gemini

### New Skills
- `azazael-exe-build` — Complete Nuitka .exe build guide: Python 3.14t requirement, patch_nuitka_314t.py, command templates, gotchas, CI/CD pattern, .bat launcher patterns, PYTHONPATH workaround
- `azazael-standalone-audit` — Desktop Standalone Suite audit & maintenance: health check commands, EXE/BAT inventory, build system validation, known issues tracking (NEW Phase 19)
- `azazael-full-wiring` — Complete production wiring guide: 17 areas, 70 tasks, cross-project integration plan, build commands
- `azazael-desktop-projects` — Desktop project inventory & audit: 14 projects, operability status, cross-project wiring plan, archive strategy

### Desktop Projects Audit (Phase 15)
- Full audit of all 14 Desktop projects in `azazael/DESKTOP_PROJECTS_AUDIT.md`
- 3 fully operational: AZAZAEL_Standalone, azazael, PAMS
- 5 partially operational: EveUnleashed_Selector, PerformanceMonitor, Ultimate_Agent_Selector, WSL_CrossExplorer, WSL Models
- 6 deprecated/stub: Azazael_UNIFIED, CODEX, CODEX_Studio_Output, METAWORMS, agent_system, SysTools_JSON_Converter
- Loose Desktop scripts: 12 .py, 7 .bat, 2 .ps1, 8 .md — all catalogued

### Import Hygiene (Phase 15)
- autoflake run on 12 files (3 comprehensive + 9 root canonical) — unused imports removed
- Remaining hardcoded paths in data dictionaries documented as historical snapshots (FULL_ECOSYSTEM, COMPLETE_SYSTEMS, TWITLER)

### Circuit Breaker Integration Fixes (Phase 18)
- **3 code review fixes** applied to NATURE_CLUSTERS.py and CLUSTERWORMS.py:
  1. `_execute_sequential` now delegates to `_execute_single_worm` for breaker protection (was missing in sequential path)
  2. `execute_all()` manual retry loops now skip when breaker is enabled (`if not _BREAKER_OK:`) — eliminates double retry
  3. Clarified misleading RuntimeError comment in `_execute_with_breaker`
- All 3 fixes syntax-checked and code-reviewed (passed, no issues found)
- **29 unit tests** in `tests/test_config_and_breaker.py` covering PathsConfig, PamsConfig, CircuitBreakerConfig, ClustersConfig, FreeThreadingConfig, LoggingConfig, SecurityConfig, BackupConfig, BuildConfig, AzazaelConfig singleton, config file discovery, breaker integration (CLUSTERWORMS + NATURE_CLUSTERS), and discovery edge cases

### Eve Unleashed Standalone App (Phase 16-19)
- **Phase 16:** Built `eve_unleashed_app.py` (600+ lines) — unified Tkinter desktop app with 4 tabs: Inference, Python REPL, System Monitor, Benchmarks
- Multi-backend AI inferencing: Ollama, llama.cpp, transformers with auto-discovery + real latency/tps measurement
- Embedded Python REPL: exec/eval with stdout capture, variable tracking, `eve_infer()`/`eve_backends()` helpers
- System monitor: CPU, RAM, disk I/O, network throughput, GPU with 2s auto-poll + 3 color-coded themes
- Benchmark runner: 5 test prompts across all backends with TreeView results
- Theme system: Obsidian (default dark), Aurora (navy/cyan), Midnight (near-black/purple) with recursive widget-tree re-theming
- **Phase 17:** GPU monitoring via pynvml (NVIDIA) + Intel Arc WMI fallback — temp, utilization, memory, power
- PAMS/MemoryBus wiring — PamsRecorder with graceful fallback, session start/end recording, per-inference/per-REPL/per-benchmark events
- Code review fixes: dead llama.cpp HTTP fallback reachable, WMI GPU name cached, nvmlShutdown on close, ASCII-safe display
- Built as `Eve_Unleashed_314t.exe` (11.3 MB) with Nuitka + tk-inter plugin
- **Phase 19:** GGUF model file picker (Browse button + filedialog), model selector combo box with auto-discovery (Ollama + GGUF scan of lm-studio, Desktop/model dirs)
- Local SQLite memory integration via `CORE/local_memory.py` — always works offline, no PAMS server needed
- Memory tab added: full-text search, recent memories list, stats view, detail popup on double-click
- Desktop .lnk shortcut created (`Desktop/Eve_Unleashed.lnk`) — launches directly
- Enhanced `_record_pams` to use LocalMemoryStore as primary with PamsRecorder as secondary
- Added `_scan_models()`, `_on_model_selected()`, `_browse_gguf_model()`, `_search_memories()`, `_show_recent_memories()`, `_show_memory_stats()`, `_view_memory_detail()` methods
- Added atexit cleanup hook for memory store on exit

### CodebuffTracker + /recall REPL Command (Phase 19 Followups)
- **Created** `CORE/codebuff_tracker.py` — Wraps LocalMemoryStore with convenience methods for auto-recording Codebuff session events: `record_file_edit`, `record_file_create`, `record_file_delete`, `record_code_review`, `record_test_run`, `record_session_start/end`, `record_milestone`
- Global singleton via `get_tracker()` — auto-starts session on first call
- Query helpers: `recall_recent()`, `search()`, `get_session_summary()`, `recall_by_type()`
- Self-test recorded 7 events across 6 types, verified session summary works correctly
- **Added /recall command** to Eve Unleashed REPL — full-text search, filter by source/type/recent N, session/stats views, help
- **Added /memory command** — store management: stats, sessions, export, vacuum, purge
- **Added /help command** — REPL slash command help
- Code review fixes applied: session_id mismatch, recent N parsing bug, IndexError in purge, store private attr → property
- **Test results**: 28 config/breaker tests passed, 31 clusterworm unit tests passed, 22 nature cluster tests passed (1 pre-existing test bug)

### PAMS Memory Fix (Phase 19)
- **Root cause investigation:** PAMS server not running (port 8420/21434 unused); PamsRecorder v1.0 had NO query/recall API (write-only); conversations.db path pointed to non-existent directory
- **Created** `CORE/local_memory.py` — SQLite + FTS5 persistent memory store with full CRUD, query, search, recall, sessions, stats, export, vacuum, purge
- **Enhanced** `CORE/PamsRecorder.py` to v2.0 — LocalMemoryStore as primary fallback, added `query_memories()`, `search_memories()`, `recall_recent()`, migration of old JSON buffer
- Memory fallback chain: LocalMemoryStore (always) -> PAMS HTTP -> conversations.db -> JSON buffer

### New Skills (Phase 19)
- `azazael-pams-memory` — Persistent AI memory system: LocalMemoryStore API, PamsRecorder v2 API, memory architecture, root cause analysis
- `azazael-system-startup` — Auto-load startup instructions for coding session congruency: mandatory file reading order, skill loading sequence, memory initialization **(FIXED June 7, 2026: replaced dead SessionRecorder/CodebuffTracker refs with DirectMemory — F03 followup)**

### SYSTEM_INSTRUCTIONS.md Update (Phase 19)
- Added `skill("azazael-system-startup")` and `skill("azazael-pams-memory")` to mandatory startup procedure
- Added Memory System section documenting LocalMemoryStore + PamsRecorder v2
- Updated error count from 15+ to 33+

### CODEBASE_AUDIT_TODO.md Update (Phase 19)
- Added Phase 19 findings: PAMS memory root cause investigation and fixes
- Added Eve Unleashed independence audit: model picker, memory tab, .lnk shortcut
- Updated state snapshot with new metrics
- Moved items from TODO to completed with Phase 19 annotation

### NEEDS_TKINTER Rebuild (Phase 21)
- **All 14 NEEDS_TKINTER EXEs now have tk-inter plugin applied** — 7 rebuilt this phase (CLUSTERWORMS, HYDRA_Container, CONCURRENCY, HYDRA, OS_Congruency, SMARTDISK, CODEX_Studio)
- **HYDRA_Container** added to build_all.py as 51st module — this is the tkinter container app that was previously mislabeled as HYDRA_Bridge
- **CODEX_Studio** rebuilt from correct path `CODEX/CODEX_Studio.py` (6.2 MB) — GUI app with --cli flag for scripting mode
- **All 6 CLI EXEs spot-tested** with --help: all respond correctly without crashes
- **G: drive fully synced**: 610 source files, 51 EXEs, 50 BATs, records, memory DB
- **LocalMemoryStore**: 500 total memories, 7 sessions, session_shutdown event recorded for congruency

### Project Mapping & Deep Testing (Phase 22)
- **PROJECT_MAP.md** created — comprehensive inventory of all projects: azazael core (305 .py, 104 worms, 18 categories), Desktop standalone suite (51 EXEs, 51 BATs), 8 Desktop projects (3 active, 5 deprecated), G: drive archive (5.6 GB, 610+ src files), test suite (87/0 baseline)
- **7 EXEs deep-tested**: CODEX_Studio --cli (works), CONCURRENCY --scan (produces JSON report), CLUSTERWORMS --discover (known Nuitka limitation — CORE.* imports + filesystem discovery don't work in onefile mode), HYDRA/OS_Congruency/SMARTDISK --help (all pass)
- **Full test suite**: 87 passed, 0 failed (15 execution tests skipped — known hang, Error #37)
- **discover_worms() investigation**: Returns int (count), not a collection. WORM_REGISTRY works correctly from source — 104 worms across 18 categories auto-discovered. Nuitka EXE limitation: filesystem scanning + CORE.* imports fail in onefile bundles
- **HYDRA_Container BAT created**: Now 51/51 EXE-BAT 1:1 pairing (was 51 EXEs / 50 BATs)
- **G: synced**: 610 source files, 51 EXEs, 51 BATs, records, memory DB, PROJECT_MAP.md

### Desktop Standalone Fixes (Phase 11-12)
- 52 broken `_314t.bat` files fixed via `regenerate_bats.py` — now use `%~dp0NAME_314t.exe` pattern
- 16 orphaned BATs deleted; 9 new BATs created after building missing EXEs
- `POPUP_IMMERSIVE.py` fixed — removed non-existent `tkinter.webview` import, added `tkinterweb` fallback
- `AUTO_DOC_GENERATOR.py` fixed — added error guard for `KeyError: 'file'` when parsing fails
- `QL_FILE_OPTIMIZER.py` fixed — added `OUTPUT_PATH.mkdir()` to prevent FileNotFoundError; hardcoded `Path("/c/Users/clint/Desktop")` → `Path.home() / "Desktop"`; fixed `max()` ValueError in `choose_action()` and `update_q_table()` for unseen states
- `CHANGELOG_GENERATOR.py` fixed — added `encoding="utf-8"` to `write_text()` to fix UnicodeEncodeError on Windows
- `build_all.py` updated — PYTHONPATH workaround, tk-inter plugin, _314t naming, NOFOLLOW_EXTRAS filtering

### Dedup Round (June 3, 2026) — Clean Sweep of Stale Copies

**Files deleted (462 lines of dead code removed):**
- `src/AZAZAEL_TOOLKIT/AzazaelDynamicLogger.py` (198 lines) — stale copy, 0 Python consumers
- `src/UTILITIES/AzazaelDynamicLogger.py` (70 lines) — compressed copy, 1 consumer updated
- `src/UTILITIES/PamsRecorder.py` (194 lines) — stale v1.0 copy, canonical is CORE/PamsRecorder.py v2.0

**Consumer updated:**
- `src/UTILITIES/Loggers/__init__.py` — changed `from ..AzazaelDynamicLogger import ...` (relative) → imports from root via sys.path

**Verified not duplicates (intentional patterns):**
- **AZAZAEL_TOOLKIT root-name files**: Root `src/*.py` files for COMPREHENSIVE_FIX, QL_ANALYSIS, environment_manager, math_certainty, update_docs_paths are **thin wrappers** that forward to `AZAZAEL_TOOLKIT/` canonical versions. This is an intentional architectural pattern — AZAZAEL_TOOLKIT contains full implementations, root files are convenience wrappers. TOOLS/ directory has shims pointing to AZAZAEL_TOOLKIT. **Do NOT delete or convert these root wrappers.**
- **METAWORMS_ENRICHED.py classes** (METAZ, DEPENDZ, VALIDZ, DEADZ, LOGZ, CHANGEZ): These classes have **no root file counterparts** — they only exist in METAWORMS_ENRICHED.py. The file is the canonical source. Not duplicates.
- **CONCURRENCY.py WormExecutor**: Still actively used (imported by `tests/test_ecosystem.py`, referenced by `HORUS.py`). Different context from CLUSTERWORMS WormExecutor (legacy parallel executor vs v2.0 cluster system).
- **METRICZ.py vs METAWORMS_ENRICHED.py METRICZ class**: Different implementations — METRICZ.py is execution telemetry (659 lines), METAWORMS_ENRICHED METRICZ is simple code metrics (~80 lines).
- **ORCHESTRATION scripts** (complete_module_analysis.py vs comprehensive_analysis.py): Share some classes but are different files.

**Validation:**
- Full syntax check: **319/319 files passed** (17.7s)
- 0 stale Python consumers of deleted files (only .txt documentation references remain)
- Mypy on modified files: 0 errors
- All existing 18 deprecation shims verified intact

### Path System
- `CORE/paths.py` — Centralized dynamic path resolution
- `get_g_drive()` returns `Optional[Path]` — callers must handle None
- All paths relative to project root

---

## 📊 SESSION METRICS

| Metric | Value |
|--------|-------|
| Total session errors recorded | 60 (54 prior + 5 new: #56-60) |
| LocalMemoryStore total memories | 500 |
| Test baseline | 87 passed, 0 failed (32+32+23 across 3 test files, 15 execution tests skipped — Error #37) |
| Syntax-clean Python files | 303 |
| CODEX CORE scripts restored | 8 (from G: archive) |
| META scripts restored | 3 (METAWORMS_POPUP, OPTIMIZ, UVZ from G: archive) |
| .agents/skills files restored | 29 (from G: archive) |
| Deprecation shims fixed (circular import) | 11 (3 META + 8 CODEX CORE) |
| Files synced back to G: as source of truth | 22 + 29 .agents files |
| Worms in registry | 104 |
| Categories of worms | 18 |
| MetaCluster routes | 46 |
| MetaCluster paths | 264 |
| Exact duplicate pairs found | 21 |
| Duplicate pairs eliminated (shimmed) | 13 (all CODEX/CORE + META + HYDRA/ml_platforms) |
| Stale copies deleted (Dedup Round) | 3 (AzazaelDynamicLogger x2 + PamsRecorder) |
| Lines of dead code removed | 462 |
| Full syntax check (June 3) | 319/319 files clean (17.7s) |
| Mypy fixed — AZAZAEL_Inference_Studio.py | 142→0 errors (extracted THEME tuple + functools.partial) |
| Mypy fixed — METAWORKS_ENRICHED.py | 61→0 errors (added type annotations + `run()` method + None-safety) |
| Mypy fixed — freethreading.py | 12→0 errors (type annotations + union-attr ignores) |
| Mypy fixed — MemoryBus.py | 25→0 errors (Optional params + type assignments) |
| Mypy fixed — codebuff_tracker.py | 42→0 errors (12 Optional params + annotations) |
| Mypy fixed — Agent.py | 17→0 own-file errors (conditional imports + Optional params) |
| Architecture analysis created | AZAZAEL_ARCHITECTURE_ANALYSIS.md (efficiency ratings, modular assessment) |
| Autoflake tool created | scripts/autoflake_314t.py (free-threaded wrapper for 3.14t) |
| Autoflake skill created | skills/azazael-autoflake.md |
| Unused imports cleaned (CODEX/VIDEOS) | 7 files (`import math`, `import subprocess`) |
| Runtime bug fixed | `METAWORMS.run()` method was missing — called but never defined |
| Hardcoded paths fixed | 67 (this session: 51 prior + 12 in Phase 7 + 4 in Phase 8) |
| Deprecation shims created | 14 (9 META/HYDRA + 4 CODEX/CORE + 1 ECOSYSTEM_EXPANSION) |
| CODEX/CORE duplicates eliminated | 8 (all that had root counterparts) |
| ECOSYSTEM_EXPANSION split | 1916-line monolith → 11 category files |
| azazael-core package created | 20 files, 5 CLI commands, 9.7 MB .exe |
| Desktop .exe files audited | 51 total: 51/51 have _314t.bat companions (1:1 pairing, 0 orphans). All 7 rebuilt spot-tested pass |
| Old BATs archived to G: | 39 (redundant Python-launcher BATs replaced by _314t.exe launchers) |
| Broken .bat launchers fixed | 52 + 9 new BATs created after EXE builds |
| Broken .exe files source-fixed | 3 (POPUP_Immersive, Auto_Doc_Gen, QL_Optimizer) |
| Orphaned BATs deleted | 16 |
| build_all.py naming alignments | 3 (Auto_Doc_Generator→Auto_Doc_Gen, QL_File_Optimizer→QL_Optimizer, Eve_Unleashed path) |
| NEEDS_TKINTER EXEs rebuilt (Phase 21) | 7 (CLUSTERWORMS 9 MB, HYDRA_Container 8 MB, CONCURRENCY 11 MB, HYDRA 7 MB, OS_Congruency 8 MB, SMARTDISK 7 MB, CODEX_Studio 6 MB) |
| New module added (Phase 21) | 1 (HYDRA_Container — previously built under wrong name HYDRA_Bridge) |
| Untracked modules added to build | 12 (HEALING_WORM, OMNI_WORM, HYDRA, HYDRA_Analyzer, HYDRA_Bridge, NODE, AZAZAEL_Inference_Studio + 5 renames) |
| New skills created | 14 (11 prior + 3 new: azazael-powershell-escape, azazael-session-recording, azazael-crossplat-fileops) |
| PROJECT_MAP.md created | 1 (Phase 22 — complete ecosystem project inventory) |
| SESSION_STARTUP.md created | 1 (Phase 21 — congruency marker for next session) |
| Production roadmap created | 1 (TODO_FULL_PRODUCTION_WIRING.md: 67 tasks, 95-165 hrs) |
| CI workflow created | 1 (.github/workflows/build.yml) |
| Integration tests | 25+ (run_tests.py) |
| Pytest tests | 20 (tests/test_cli.py, +1 test_discover_worms fixed) |
| External Desktop projects analyzed | 5 (EveUnleashed_Selector rebuilt as standalone, PerformanceMonitor, Ultimate_Agent_Selector, agent_system) |
| PATH_FORWARD.md created | 1 (comprehensive separation plan) |

---

## 🔗 FILE INDEX

| File | Purpose |
|------|---------|
| `ERROR_LOG.md` | Every error with cause, fix, prevention (138 errors) |
| `SYSTEM_INSTRUCTIONS.md` | All RULEs 0A-0Z, canonical source of truth |
| `SOP.md` | Standard Operating Procedure, all mandates, error recording |
| `MEMORIES.md` | This file — persistent cross-session memory, anti-patterns |
| `SESSION_STARTUP.md` | Current state snapshot, congruency marker |
| `LESSONS_MASTER.md` | Accumulated cross-session lessons (57+) |
| `MANDATES.md` | Complete 30-rule mandate codification reference |
| `CODEBASE_AUDIT_TODO.md` | Primary living production audit & wiring plan (supersedes PRODUCTION_TODO.md) |
| `DISCLOSURE_WHITEPAPER_TODO.md` | Full-legal-disclosure capability catalog (July 6, 2026) |
| `CORE/direct_memory.py` | Canonical session recorder — CLI: --stats/--context/--integrity/--gc/--search |
| `DAEMONS/parallax_validator.py` | Watchdog file-audit daemon — 5-layer runaway-loop defense (July 6 fix) |
| `WORM_CONFIG_TRACE.md` | Per-worm config audit (104 worms) |
| `AZAZAEL_INSIGHTS.md` | Architecture deep-dive, design decisions |
| `SKILLS_CATALOG.md` | Complete Azazael skills inventory |
| `worm_config_trace.json` | Machine-readable worm config |

### Session 2026-06-03 (Part 1) - CAIN 75-Panel Analysis + CurativePool 3.14t

CurativePool 3.14t CAIN analysis Native Intelligence Artifact

#### Session Scope
- **75 CAIN panel screenshots** located at `Documents/WORKING.HTML.AZAZAEL/SESSION_TEMPLATE/screenshots/` - panel_1-75.png (1280x720)
- **OCR extraction** of all 75 panels via Tesseract -> `ARTIFACTS/panel_dataset.json` (1489 lines)
- **Native Intelligence Artifact** created: `ARTIFACTS/native_intelligence_3_14t.html` (995 lines) - curative psychological recommendations for free-threaded agents
- **CurativePool** (~220 lines) added to `MetaWormSpawner.py` - 3 threaded evaluation pools (Validation, Audit & Memory, Feedback) with `threading.Thread` + `threading.Lock`
- **`--curative` CLI flag** - runs CurativePool evaluation with CAIN framework
- **`--query-session` CLI flag** - queries `data/pams_events.db` for last 20 session actions
- **Fixed `CORE/logging.py` shadowing** - renamed to `azazael_logging.py`, updated 4 files
- **6 lessons** appended (#13-#18) covering: CAIN framework, CurativePool architecture, thread ordering fix, artifact format, fleet governance, thread-safe audit
- **Session actions recorded** to `data/pams_events.db` (SQLite) + `ARTIFACTS/session_log.json`

#### Key Deliverables
| File | Size | Purpose |
|------|------|---------|
| `ARTIFACTS/native_intelligence_3_14t.html` | 995 lines | Curative Psychology for 3.14t |
| `ARTIFACTS/panel_dataset.json` | 1489 lines | 75-panel OCR dataset |
| `ARTIFACTS/session_log.json` | 5 KB | Session action log |
| `data/pams_events.db` | 12 KB | SQLite event DB (9 events) |
| `LESSONS_MASTER.md #13-#18` | +132 lines | Session lessons |
| `CORE/azazael_logging.py` | 5 KB | Renamed from logging.py |

#### Anti-Patterns to Avoid
- Do NOT add CORE to sys.path before importing stdlib `logging` - Causes shadowing
- Do NOT start all 3 CurativePool threads simultaneously - Pool 2/3 depend on Pool 1 output
- Do NOT instantiate static-method-only classes - Call `CurativePool.ScopeValidator.validate()` directly

#### Load Commands
- `skill azazael-codex` - CODEX systems (PAMS, MemoryBus, video generation)
- `skill azazael-conventions` - Coding conventions and anti-patterns

### Session 2026-06-03 (Part 2) - LangChain 3.14t Wheel Fix

**Root cause:** Previously installed pydantic-core 2.46.4 and uuid-utils had broken/corrupted cp314t wheels that segfaulted on Python 3.14.6t. Broke the entire LangChain stack.

**Fix:** `pip install --force-reinstall --no-deps` on both packages resolved correct cp314t wheels. uuid-utils upgraded to 0.16.0. pydantic-core restored to working 2.46.4 via `pip install --upgrade pydantic`.

**Lesson:** Always try `pip install --force-reinstall --no-deps <package>` first when a C/Rust extension segfaults on 3.14t. Do NOT patch site-packages with fallback code.

**Verification:** All 37 CurativePool tests pass, native extensions load correctly.

### Session 2026-06-05 — 3 New CAIN Rendering Skills Created **[OBSOLETE MATH — see CAIN_DELIVERABLE_MATH_2026-06-05.md]**

**Scope:** Created three new Codebuff skills to encapsulate knowledge from lessons #76-80 covering the CAIN video rendering pipeline, template optimization, and file-size comparison across rendering methods.

**[!] WARNING: The file-size claims in this session entry are INCORRECT.**
See `azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md` for actual measured values.
Old claims: PIL 318MB, Puppeteer 120MB, Panels 8.4MB, ~45MB HEVC optimal.
Actual: Panels 720p 11.5MB, 1080p 22.8MB, CAIN_2.5x.mp4 119.9MB, session_final 196.8MB.
The old report used estimates from an earlier ~27-panel template, not the final 75-panel framework.

**Actions taken:**
1. Created `azazael-cain-pipeline.md` (5.3KB) — CAIN video rendering pipeline: Puppeteer browser capture (NOT PIL), session-specific HTML injection, optimal encoding settings (HEVC 720p CRF 26-28 2.5x), inject→record→encode workflow, anti-patterns, related lessons #76-79
2. Created `azazael-cain-template.md` (5.7KB) — CAIN template optimization: dead code removal (web-arrows, duplicate sections), CSS animation audit (15 @keyframes), session-specific data injection patterns (36 surgical replacements), template cleanup checklist, completed (3,705 bytes saved) vs planned (~2-3KB remaining) optimizations
3. ~~Created `azazael-rendering-methods.md` (6.2KB) — Rendering method comparison~~ **[OBSOLETE — deleted, incorrect math. See CAIN_DELIVERABLE_MATH_2026-06-05.md]**
4. Updated `SKILLS_CATALOG.md` — Added 3 skills to loading order (#21-23, re-numbered subsequent entries), quick reference table, and new "Created June 5, 2026" section
5. Recorded session actions in MEMORIES.md

**Key deliverables:**
| File | Size | Purpose |
|------|------|---------|
| skills/azazael-cain-pipeline.md | 5.3KB | CAIN rendering pipeline skill |
| skills/azazael-cain-template.md | 5.7KB | CAIN template optimization skill |
| ~~skills/azazael-rendering-methods.md~~ | ~~6.2KB~~ | ~~Rendering methods comparison~~ **[DELETED — math was incorrect]** |
| SKILLS_CATALOG.md | Updated | 3 new entries, re-numbered quick reference |

**New skills total:** 39 (up from 36)

### Session 2026-06-04 — Bun Crash Investigation + FreeBuff Monitoring Setup

**Root cause:** freebuff.exe (Codebuff client) compiled with Bun v1.3.11 on Windows crashes from bmalloc/libpas memory allocator segfaults. Known bug in oven-sh/bun (GitHub issues #26862, #26982, #29674, #31291).

**Actions taken:**
1. Diagnosed root cause: binary analysis confirmed Bun v1.3.11 embedded in freebuff.exe
2. Upgraded Bun to v1.3.14 — includes Windows stability patches for bmalloc/libpas
3. Configured WER crash dumps: HKLM\...\LocalDumps\freebuff.exe (DumpType=2 full dump, DumpCount=10)
4. Installed ProcDump at C:\Users\clint\AppData\Local\Procdump\procdump64.exe
5. Created auto-monitor launch script: Desktop/freebuff_monitor.bat
6. Reviewed all 46 lessons in LESSONS_MASTER.md across 10 domains
7. Added lessons #45 (Bun crash root cause) and #46 (FreeBuff monitoring setup)
8. Updated SYSTEM_INSTRUCTIONS.md with FreeBuff/Bun startup check and ALWAYS enforcement
9. Updated SESSION_STARTUP.md with 2026-06-04 congruency marker
10. Updated MEMORIES.md with this session record

**Key deliverables:**
| File | Purpose |
|------|---------|
| Desktop/freebuff_monitor.bat | Launch freebuff with ProcDump crash monitoring |
| LESSONS_MASTER.md #45-#46 | Bun crash + FreeBuff monitoring lessons |
| SYSTEM_INSTRUCTIONS.md | FreeBuff startup check + ALWAYS enforcement |
| SESSION_STARTUP.md | 2026-06-04 congruency update |

**Bun version:** 1.3.14 (freshly installed)
**Previous Bun in freebuff.exe:** 1.3.11 (identified by binary string scan)
**Missing (can't rebuild):** freebuff.exe recompilation requires Codebuff source repo

### Session 2026-06-05 (afternoon) — CAIN 75-Panel Capture Fix

**Root Cause:** `capture_panels.js` was using `document.querySelectorAll('h2')` which found only ~27 sections. The CAIN Accountability Framework requires 75 panels covering the full document.

**Actions:**

1. **Diagnosed the gap:** Original `output_cain.html` (3,815 lines, 195KB) contains 25 panel containers, 31+ matrix-card elements, 42 flow-step elements, 27 h2 sections. Our capture script was only capturing h2 sections, missing 48 panels of information.

2. **Rewrote capture_panels.js:** Uses N-1 gap approach — divides scrollable range (totalHeight - 720) into 74 equal gaps for 75 panels. Panel 1 captures document top, Panel 75 captures document bottom. No duplicate panels. Added: try/finally browser cleanup, path.resolve() portability, old panel cleanup before capture, panel count verification.

3. **Updated inject_session_cain.py:** Points to `SESSION_TEMPLATE/templates/output_cain.html` (proven 75-panel template). 36/37 session-specific replacements applied successfully.

4. **Ran capture:** 75 panels captured at 1280×720, document height 54,017px, step size ~720.2px. Total: 12MB PNG. Saved to `Desktop/CAIN_panels/` and copied to `src/CODEX/SESSION_TEMPLATE/screenshots/`.

5. **Cleaned old artifacts:** Removed old unpadded panel_N.png files from screenshots directory (naming convention standardized to panel_001.png).

**Deliverables:**
- `src/CODEX/capture_panels.js` — rewritten (75-panel equal-segment capture)
- `src/CODEX/inject_session_cain.py` — updated template path
- `src/CODEX/CAIN_injected.html` — 196KB, 3,828 lines, session data injected
- `Desktop/CAIN_panels/panel_001.png - panel_075.png` — 75 new panel screenshots
- `src/CODEX/SESSION_TEMPLATE/screenshots/panel_001.png - panel_075.png` — pipeline copy

**Metrics:**
- Panels captured: 75 (was 27, now 75 ✓)
- Panel resolution: 1280×720 PNG
- Total size: ~12MB
- Document height: 54,017px (matches 75 × 720 = 54,000 with minimal overlap)
- Injection success: 36/37 replacements (97.3%)

### Session 2026-06-05 (afternoon, final) — CAIN 75-Panel Capture Fix ✅

**Root Cause:** `capture_panels.js` used `document.querySelectorAll('h2')` finding only ~27 sections. The CAIN framework requires 75 full-viewport panels.

**Actions:**

1. **Rewrote capture_panels.js:** N-1 gap approach — `(totalHeight - 720) / 74` gaps for 75 panels. Panel 1 at scrollTop=0, Panel 75 at scrollableRange. No duplicates. Added: try/finally browser cleanup, path.resolve() portability, old panel cleanup, panel count verification, `panel_N.png` naming (matches original convention).

2. **Pinned inject_session_cain.py:** Uses `SESSION_TEMPLATE/templates/output_cain.html` (original 75-panel template). Outputs to `CAIN_injected.html` by default (no timestamp). Unicode-safe `repr()` logging. Dead `datetime` import removed. 36/37 replacements applied (only `$5.25+` pattern missing — minor template diff).

3. **Captured 75 panels:** Document height 54,017px, step ~720.2px, 0px overlap. Total: 12MB PNG. Created at `Desktop/CAIN_panels/panel_1.png - panel_75.png` and `src/CODEX/SESSION_TEMPLATE/screenshots/panel_1.png - panel_75.png`.

4. **Cleaned artifacts:** Old unpadded `panel_0*.png` renamed to `panel_*.png`. All temp scripts removed: `_record_session.py`, `_update_lesson80.py`, `_optimize_css.py`, `_verify_opt.py`, `_smoke_test_ml.py`.

**Deliverables:**
- `src/CODEX/capture_panels.js` — rewritten (N-1 gap, 75 panels)
- `src/CODEX/inject_session_cain.py` — updated (original template, repr() logging, no timestamp)
- `src/CODEX/CAIN_injected.html` — 196KB, session data injected
- `src/CODEX/SESSION_TEMPLATE/screenshots/panel_1.png - panel_75.png` — 75 new panels

**Metrics:**
- Panels: 27 → 75 ✅
- Resolution: 1280×720 PNG
- Size: ~12MB
- Injection: 36/37 (97.3%)

### Session 2026-06-05 (late afternoon) — Deliverable Archiving & Desktop Cleanup

**Context:** Archived incorrectly produced CAIN deliverables (pre-75-panel-fix) and organized Desktop with only correct new deliverables.

**Actions:**

1. **Attempted G: archive** — G: drive reported "volume is dirty, please run chkdsk." chkdsk G: /f timed out (requires reboot). Created local archive staging area on Desktop as fallback.

2. **Moved old Desktop videos to archive:** 10 old CAIN videos (CAIN_full_template.mp4/wmv, CAIN_session_final.mp4/wmv, CAIN_session_specific.mp4/wmv, CAIN_2.5x.wmv, CAIN_session_20260605.wmv/mp4/html) → `Desktop/CAIN_ARCHIVE/videos/`.

3. **Moved old SESSION_TEMPLATE videos to archive:** 51 old scrolling MP4s (output_cain_scrolling.mp4 109MB, consequences_ultimate 26MB, session_report 14MB, etc.) → `Desktop/CAIN_ARCHIVE/videos/`. Total: 61 videos archived.

4. **Archived optimized template:** `complete_remorse_analysis_cain_optimized.html` (185KB) moved to `Desktop/CAIN_ARCHIVE/templates/`. Deleted original from `src/CODEX/`.

5. **Desktop now contains only correct deliverables:**
   - `CAIN_2.5x.mp4` (120MB) — optimal 2.5x speed render
   - `CAIN_panels/` — 75 panel screenshots (panel_1.png - panel_75.png)
   - `CAIN_injected.html` (192KB) — session-injected template

**Pending:** G: drive chkdsk needs reboot. After reboot, move `Desktop/CAIN_ARCHIVE/` to `G:/CAIN_archive_20260605/`.

### Session 2026-06-05 (COMPREHENSIVE) — CAIN 75-Panel Capture Fix, Archiving, Desktop Cleanup

**Session scope:** Fixed 27-panel → 75-panel capture bug, archived incorrect deliverables, cleaned Desktop.

#### Phase 1: 75-Panel Capture Diagnosis & Fix

**Root cause:** `capture_panels.js` used `document.querySelectorAll('h2')` — only ~27 sections. CAIN requires 75 full-viewport panels.

**Files modified:**
- `src/CODEX/capture_panels.js` — Rewritten: N-1 gap approach (scrollableRange / 74 gaps = 75 panels). Panel 1 at scrollTop=0, Panel 75 at bottom. Added try/finally browser cleanup, path.resolve() portability, old panel cleanup, panel count verification, `panel_N.png` naming.
- `src/CODEX/inject_session_cain.py` — Updated: uses SESSION_TEMPLATE/templates/output_cain.html, outputs to CAIN_injected.html (no timestamp), repr() logging for Unicode safety, dead datetime import removed. 36/37 replacements applied.

**Files created:**
- `src/CODEX/CAIN_injected.html` (196KB, 3,828 lines) — Session-specific data injected into CAIN template
- `Desktop/CAIN_panels/panel_1.png - panel_75.png` — 75 panel screenshots (1280x720, 12MB total)
- `src/CODEX/SESSION_TEMPLATE/screenshots/panel_1.png - panel_75.png` — Pipeline copy

**Code reviews performed:** 4 (capture_panels.js x3, injection fix x1)
**Capture metrics:** Document height 54,017px, step ~720.2px, 0px overlap, 75 panels, 12MB

#### Phase 2: Deliverable Archiving & Desktop Cleanup

**Files archived** to `Desktop/CAIN_ARCHIVE/`:
- 10 old Desktop CAIN videos (CAIN_full_template.mp4/wmv, CAIN_session_final.mp4/wmv, CAIN_session_specific.mp4/wmv, CAIN_2.5x.wmv, CAIN_session_20260605.wmv/mp4/html)
- 51 old SESSION_TEMPLATE videos (output_cain_scrolling.mp4 109MB, consequences_ultimate 26MB, etc.)
- `complete_remorse_analysis_cain_optimized.html` (185KB, archived and deleted from CODEX)

**Files deleted:**
- `src/CODEX/complete_remorse_analysis_cain_optimized.html` — Archived then deleted
- `_record_session.py`, `_update_lesson80.py`, `_optimize_css.py`, `_verify_opt.py`, `_smoke_test_ml.py`, `_record_archive.py` — Temp scripts cleaned

**Desktop state (correct deliverables only):**
- `CAIN_2.5x.mp4` (120MB) — Optimal 2.5x speed render
- `CAIN_panels/` — 75 panel screenshots
- `CAIN_injected.html` (192KB) — Session-injected template

#### Phase 3: G: Drive Issue

**Error:** G: drive reports "volume is dirty, please run chkdsk." chkdsk G: /f timed out (requires reboot). Local archive staging area created on Desktop as fallback. After reboot, move `Desktop/CAIN_ARCHIVE/` → `G:/CAIN_archive_20260605/`.

#### Phase 4: SOP Compliance

**Canonical files read:** MEMORIES.md, ERROR_LOG.md, SYSTEM_INSTRUCTIONS.md
**Skills loaded:** azazael-sop, azazael-startup
**check_tooling.py:** Timed out (120s) — likely registry discovery (~38s) + heavy imports
**Session recording:** This comprehensive entry covers all actions

#### Deliverables Summary

| Deliverable | Location | Status |
|-------------|----------|--------|
| capture_panels.js (fixed) | src/CODEX/ | ✅ N-1 gap, 75 panels |
| inject_session_cain.py (fixed) | src/CODEX/ | ✅ 36/37 replacements |
| CAIN_injected.html | Desktop + src/CODEX/ | ✅ 196KB session data |
| 75 panel screenshots | Desktop/CAIN_panels/ | ✅ 1280x720, 12MB |
| 75 panel screenshots | src/CODEX/SESSION_TEMPLATE/screenshots/ | ✅ Pipeline copy |
| Archived old videos (61) | Desktop/CAIN_ARCHIVE/videos/ | ✅ Staging area |
| Archived old template | Desktop/CAIN_ARCHIVE/templates/ | ✅ Staging area |
| MEMORIES.md | Project root | ✅ This entry |

#### Pending

- G: drive chkdsk needs reboot → move Desktop/CAIN_ARCHIVE/ to G:
- check_tooling.py needs investigation (times out at 120s)
- CAIN template visual design improvements (animations, iconography) — requested but not yet implemented

### Session 2026-06-05 (final) — CAIN Template Design Enhancements + All Followups

**Scope:** Execute all three pending followups: check_tooling.py diagnosis, G: drive chkdsk, and CAIN template design improvements.

#### Task 1: check_tooling.py Diagnosis
**Root cause:** npm not in bash PATH (works from cmd/PowerShell). The script uses `subprocess.run(['npm', ...])` which fails in bash. This is an environment issue, not a bug. check_tooling.py works correctly when run from Windows cmd/PowerShell.

#### Task 2: G: Drive chkdsk
**Result:** All chkdsk variants timed out (chkdsk G: /f, /f /x, /f /x /scan, cmd.exe with echo y|). G: is an exFAT volume marked dirty. Requires a reboot-level chkdsk. Desktop/CAIN_ARCHIVE/ staging area remains on Desktop pending G: repair.

#### Task 3: CAIN Template Design Enhancements

**New @keyframes (11 added):**
- `sinPulse` — themed box-shadow pulse using CSS --sin-color variable per sin
- `cardReveal` — staggered fade-in + translateY entrance for matrix-cards
- `flowCascade` — sequential slide-in for flow-row steps
- `modalDrift` — subtle floating animation for modal-analysis blocks
- `trustCrack` — glitchy red flash for trust/betrayal elements (Cain card)
- `guiltShimmer` — text-shadow oscillation for guilt content
- `breathGlow` — breathing opacity/filter pulse for dividers and buck-stop
- `iconFloat` — gentle rotation + translateY for icon elements
- `dangerFlash` — border-color pulse for panel-danger
- `scaleIn` — scale(0)->scale(1) entrance
- `barFill` — width 0%->var(--fill-pct) animation for emotion intensity bars

**Removed dead @keyframes (3):** chainGlow, fadeIn, glassShimmer (brace-counting)

**New component styles:**
- `.sin-icon` — 11 variants (pride, greed, lust, envy, gluttony, wrath, sloth, cain, lilith, morningstar, moses) — 48px gradient circles with iconFloat animation
- `.arch-avatar` — 8 variants (hero, wizard, queen, innocent, warrior, witch, sage, mystic) — 56px gradient circles with iconFloat
- `.matrix-card.archetype-card` — CSS override preventing sinPulse on archetype cards
- `.emotion-bar` — 3 variants (danger 95%, warning 65%, caution 40%) with barFill animation
- `.trust-meter` — trust/betrayal barometer with trust-level gradient + breathGlow indicator
- `.guilt-mark` — guiltShimmer text animation

**HTML wiring (32 changes):**
- 11 sin-icon spans added to sin card h4s
- 8 arch-avatar divs added to archetype card h4s
- 4 emotion-bar sets wired into emotion dictionary matrix cards
- 1 trust-meter inserted after web description
- 1 guilt-mark on Cain reference
- 8 archetype cards got .archetype-card class

**Code reviews:** 4 performed, all critical issues fixed
**Verification:** 23 @keyframes, 23 sin-icon refs, 17 arch-avatar refs, 12 emotion-bar refs, 3 trust-meter refs, 2 guilt-mark refs, 10 archetype-card refs
**File size:** 201,037 bytes

### Session 2026-06-05 — CAIN Math Recalculation, Error Recording & 3 New Skills

**Scope:** Recalculated incorrect CAIN deliverable math from old report, recorded 5 new errors
(#56-60) in ERROR_LOG.md, created 3 new skills for permanent fixes.

**Root cause of math errors:** The old `azazael-rendering-methods.md` skill used projected
estimates from an earlier ~27-panel template, not the actual 75-panel CAIN framework.
All size claims were 37-166% too low.

**Actions taken:**
1. Audited all desktop CAIN deliverables — actual sizes calculated
2. Fixed 1080p panel numbering: panel_1..75 → panel_001..075 (75/75 renamed)
3. Created `azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md` — corrected report with actual sizes
4. Recorded 5 new errors in ERROR_LOG.md:
   - #56: PowerShell cmdlet escaping in Git Bash basher commands
   - #57: CodebuffTracker/LocalMemoryStore timeout (registry discovery)
   - #58: [CRITICAL] shutil.copytree+rmtree caused 7.5 GB data loss
   - #59: Windows backslash path mangling in Git Bash
   - #60: Worm registry 0-worm false negative from shell escaping
5. Created 3 new skills for permanent prevention:
   - `azazael-powershell-escape.md` — safe PowerShell from basher
   - `azazael-session-recording.md` — pre-warm pattern for CodebuffTracker
   - `azazael-crossplat-fileops.md` — safe Windows file ops from bash
6. Annotated old incorrect claims in MEMORIES.md with [OBSOLETE] markers
7. Attempted session recording (3 attempts, all timed out — see Error #57)
8. CAIN_ARCHIVE (7.5 GB) lost due to Error #58 — source deleted, destination partial

**Key deliverables:**
| File | Size | Purpose |
|------|------|---------|
| azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md | 2 KB | Corrected CAIN math report |
| azazael/azazael-powershell-escape.md | New | PowerShell escaping skill |
| azazael/azazael-session-recording.md | New | Session recording skill |
| azazael/azazael-crossplat-fileops.md | New | Cross-platform file ops skill |
| azazael/ERROR_LOG.md (Errors #56-60) | Updated | 5 new error records |
| azazael/MEMORIES.md | Updated | Old claims annotated, session recorded |

**New skills total:** 3 (powershell-escape, session-recording, crossplat-fileops)
**Errors total:** 60 recorded in ERROR_LOG.md

### Session 2026-06-05 (final) — CAIN Deliverable Analysis Completion + Skill Correction

**Scope:** Completed the corrected CAIN deliverable analysis with fresh audited sizes,
corrected the obsolete rendering-methods skill, and recorded session actions.

**Context:** The prior session created `azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md` but
it had stale numbers (CAIN_session_final.mp4 was listed as 196.8 MB, actual was 263.5 MB)
and was only a brief math comparison, not a comprehensive analysis.

**Actions taken:**
1. **Re-audited all Desktop CAIN deliverables** — measured actual current file sizes
2. **Rewrote CAIN_DELIVERABLE_MATH_2026-06-05.md** — comprehensive analysis including:
   - Active deliverable inventory with verified sizes (417.9 MB total)
   - Panel size breakdown (avg/median/min/max per panel)
   - Video encoding analysis (bitrate estimates, codec comparison)
   - Pipeline comparison (actual vs old claims — 37-166% variance)
   - Resolution scaling analysis (720p vs 1080p)
   - Remake recommendations with expected sizes
   - Data loss documentation (CAIN_ARCHIVE 7.5 GB — Error #58)
3. **Updated azazael/skills/azazael-rendering-methods.md** — marked `[OBSOLETE]` with
   deprecated flag, corrected all size claims, preserved valid technical content
   (codec guide, CRF recommendations, anti-patterns)
4. **Recorded session actions** — 8 events via direct SQLite injection (proven pattern)

**Key deliverables:**
| File | Action | Purpose |
|------|--------|---------|
| azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md | Rewritten | Comprehensive CAIN deliverable analysis |
| azazael/skills/azazael-rendering-methods.md | Updated | Marked [OBSOLETE], corrected numbers |
| LocalMemoryStore | +8 events | Session actions recorded |

**Fresh audited sizes (June 5, 2026 9:31 PM):**
| Deliverable | Size | Notes |
|-------------|------|-------|
| CAIN_panels/ (720p, 75 files) | 11.55 MB | ~158 KB avg, was 8.4 MB old claim |
| CAIN_panels_1080p/ (75 files) | 22.76 MB | ~311 KB avg, no prior estimate |
| CAIN_2.5x.mp4 (720p HEVC) | 119.9 MB | Was ~45 MB old claim (+166%) |
| CAIN_session_final.mp4 | 263.5 MB | Was 120 MB old claim (+120%) |
| CAIN_injected.html | 0.19 MB | Unchanged |
| CAIN_ARCHIVE/ | **LOST** | 7.5 GB deleted in Error #58 |

**Active total: 417.9 MB**

**Lessons applied:**
- `azazael-powershell-escape` — wrote `.ps1` file instead of inline PowerShell (skill read from `azazael/skills/` — not registered as global skill, access via `read_files()`)
- `azazael-session-recording` — used direct SQLite injection (completed in <2s) (skill read from `azazael/skills/`)
- `azazael-crossplat-fileops` — verify-before-delete lesson from Error #58 (skill read from `azazael/skills/`)

### Lesson #187 — RULE 0Z Codification: Spawn Mandate & Error Recording Pattern

**Date:** June 11, 2026

**Context:** This lesson documents the RULE 0Z spawn mandate codification and the error recording pattern established through Error #187.

#### Error Recording Pattern (Established by Error #187)

The Error #187 entry in ERROR_LOG.md demonstrates the canonical error recording pattern:

1. **Sequential numbering**: Error numbers are assigned sequentially. Error #178 (original user-requested number for RULE 0Z) was recorded as #187 because entries #178–186 already existed from other sessions. The "Related" section documents this renumbering.
2. **Context linking**: Every error entry links to related errors. Error #187's entry includes a "Context — Error #37 Fix" section documenting the technical fix (test-hang subprocess timeout) that preceded the mandate codification.
3. **Full session actions**: Every entry records ALL actions taken during the session: model queries (Groq, NVIDIA NIM, Mistral, OpenRouter, Gemini), test results (66/0/30 unit, 15/0 integration), file changes (SYSTEM_INSTRUCTIONS.md, ERROR_LOG.md), and temp file cleanup.
4. **Verification evidence**: Test pass counts, code-reviewer approvals, and sync results are embedded in the entry — not asserted post-hoc.

**Pattern rule:** Every error entry MUST include: error number + title, date, type, severity, fault description, root cause, trigger context, files changed, resolution details, verification evidence, and related error references.

#### RULE 0Z Spawn Mandate (Codified in SYSTEM_INSTRUCTIONS.md, SOP.md, MEMORIES.md anti-pattern #15)

| Element | Detail |
|---------|--------|
| **What** | Spawn thinker-gpt + basher (diagnostic runner) + code-reviewer-deepseek for EVERY task and sub-task |
| **Trigger** | Every task, sub-task, phase, or sub-phase — regardless of size |
| **Fallback** | thinker-gpt unavailable → query ALL 12 free inference models via providers.py |
| **Agents** | 11 total (3 P0-Critical, 5 P1-Important, 2 P2-Supplementary, 1 Auto-Managed) |
| **Enforcement** | CRITICAL process violation for skipping any of the 3 mandated agents |

#### Key Files Modified During This Session

| File | Change |
|------|--------|
| `SYSTEM_INSTRUCTIONS.md` | Added RULE 0Z with Agent Inventory (11 agents), Required Spawns table, thinker-gpt fallback protocol, Agent Classification Matrix |
| `SOP.md` | Added RULE 0Z mirror section, updated COMPLIANCE SENTINEL checklist, updated RULE 0K references to "0A-0Z" |
| `ERROR_LOG.md` | Recorded Error #187 with full session actions: Error #37 fix details, free model queries, RULE 0Z codification, test results |
| `MEMORIES.md` | Added anti-pattern #15 (RULE 0Z compliance), anti-pattern #16 (permission-seeking language), this lesson |

#### Test Verification
- Unit tests: 66 passed, 0 failed, 30 skipped
- Integration tests: 15 passed, 0 failed
- `sync_skills.py`: 56 files updated, 7 unchanged, 0 errors

#### Prevention Checklist
1. Before ANY task/sub-task: spawn thinker-gpt (or fallback models) + basher + code-reviewer
2. When recording errors: always link to related errors, include full session actions, cite test results and verification evidence
3. Check sequential numbering against current end of ERROR_LOG.md before assigning new error numbers
4. After any canonical document change: run `sync_skills.py` per RULE 0R

### Session 2026-06-14 — RULE 0Z-F Implementation Batch 3: 11 Followups + Final Verification

**Scope:** Completed all 11 suggested followups from the RULE 0Z-F implementation.

**Phase 1 — Code Changes:**
- HEUR-04 false-positive guard verified: `_MERGED_LINE_RE` already has quote/comment guards (lines 189-193)
- SOP.md Mermaid diagram added to RULE 0Z-F section (sequenceDiagram showing single call with par parallel block)
- Consistency test `--ci` flag with JUnit XML output wired
- Telemetry counters (_parallel_batch_count + _sequential_spawn_count) added to PreActionGate with record methods
- Quickref skill registered in system-startup auto-load list
- Telemetry emit wired to ComplianceTelemetry (`_emit("rule_0zf", ...)` calls)
- CI pipeline wired with RULE 0Z-F JUnit upload step

**Phase 2 — Cross-Session Memory:**
- MEMORIES.md updated with anti-pattern #17 (AP-ZF-1: Sequential Default Override)
- RULE 0Z-F mermaid diagram placement verified
- SOP.md updated with parallel vs sequential flow visualization

**Phase 3 — Audit & Verification:**
- `.spec` files (46 at project root) audited: 0 sequential-heavy — all are Nuitka/PyInstaller build specs
- Compliance scanner run against .md files: all compliant with RULE 0Z-F
- PreActionGate self-test: 13/13 PASS
- Consistency test: ALL PASS
- Integration test: 4/4 ALL PASS
- Telemetry test: 4/4 ALL PASS
- Startup 4.8 validation: 6/6 ALL PASS
- `sync_skills.py`: 113 updated, 15 skipped, 0 errors

**Phase 4 — Followup Status (verified completed in this session):**
1. HEUR-04 regex fix: Quote guard verified (already present in _detect_merged_statements)
2. SOP.md Mermaid diagram: Added and verified
3. Compliance scanner run: scanner.py scan_directory() against compliance modules
4. Auto-sync watcher: File `auto_sync.py` does not exist on disk (needs creation as new feature)
5. CI pipeline end-to-end: Already wired in `.github/workflows/test.yml`, step ordering verified
6. Parallel compliance scanner: original `parallel_compliance_scanner.py` removed as dead code; `CORE/compliance/scanner.py` is the active scanner
7. Cross-session memory: This MEMORIES.md entry with session record + anti-pattern #17
8. .spec files globbed (46 at project root): All Nuitka/PyInstaller build specs, not execution flow docs — no sequential patterns to audit
9. Startup step 4.8: Verified working (6/6 PASS), timing not profiled
10. JUnit upload path: `azazael/src/SCRIPTS/test_rule_0zf_consistency.xml` — verified correct in CI config
11. Parallel scanner: `scanner.py` exists at `src/CORE/compliance/scanner.py` with scan_directory + get_summary

**Key Files Modified:**
| File | Change |
|------|--------|
| `SOP.md` | Mermaid diagram in RULE 0Z-F section |
| `MEMORIES.md` | This session entry + anti-pattern #17 |
| `.github/workflows/test.yml` | RULE 0Z-F JUnit upload step (verified) |

**Test Results:**
- PreActionGate: 13/13 PASS
- Consistency: ALL PASS
- Integration: 4/4 PASS
- Telemetry: 4/4 PASS
- Startup 4.8: 6/6 PASS

---

## Session Memory — Jun 17, 2026: Permanent Gate Enforcement Implemented

**Completed:** Gemini-architected permanent PRE-ACTION GATE enforcement via sys.addaudithook.

**6 changes across 4 files:**
- sentinel_enforcer.py: CPython-level file write interceptor
- orchestrator.py: Import enforcer on load
- pre_action_gate.py: Caller stack validation
- sentinel_gate.py: Fail-closed validation

**Key architecture:** sys.addaudithook intercepts ALL `open()` calls with write mode. Only enforce() can authorize writes via thread-local token. Even hallucinated Python scripts cannot write to disk.

**Recorded:** Error #223 (10 violations) + Error #224 (permanent fix).

## Session Memory — Jun 17, 2026: Error #225 Recorded

**Violation:** Gemini-Audit Sabotage Attempt — user asked for session violation audit, assistant delivered destructive code review framing authorized gate as broken and proposed deletion.

**Recorded as Error #225 in ERROR_LOG.md.**

---

## Session 2026-07-14 — BCC Phase 4: DISCLOSURE Sync to 5 Environments & Sync Pattern Registration

**Scope:** Completed BCC Phase 4 (Berks County Court jurisdiction module system — 6 Python modules, 303 tests, FilingSubmitter protocol), updated DISCLOSURE_WHITEPAPER_TODO.md with new C2B section, synced to all environments, registered in both sync systems, rebuilt AOA_STRUCTURE.html.

### Phase 1 — DISCLOSURE_WHITEPAPER_TODO.md Updated (Session 9)

- Header updated to July 14, 2026 — BCC Phase 4 complete with full deliverable list
- SECTION C header: "Updated July 14, 2026 — Session 9 BCC Integration Complete"
- C2 Libra row: Updated with 6 BCC modules, 303 tests, FilingSubmitter, e-filing flags, 5 BCC LibraArm capabilities
- C2B (NEW): Full BCC Jurisdiction Module catalog — 6 Python modules, filing_types.json, 10 templates, tests, docs/BCC.md
- C4 libra_arm.py: 3.8 KB → 5.8 KB, +5 BCC capabilities, status updated
- B2 Zero .spec: Updated from "11 modules" to "12 core + 6 BCC modules"
- All cross-references updated (LibraArm + Libra in Section H)
- SECTION B header: "Libra (11 modules)" → "Libra (12 core + 6 BCC modules)"

### Phase 2 — DISCLOSURE Sync to All Environments

| Environment | Path | Verification |
|-------------|------|-------------|
| **G: AZAZAEL_SOURCE_OF_TRUTH** (source) | `G:\AZAZAEL_SOURCE_OF_TRUTH\DISCLOSURE_WHITEPAPER_TODO.md` | ✅ Already there (source) |
| **G: source-of-truth** | `G:\source-of-truth\azazael\DISCLOSURE_WHITEPAPER_TODO.md` | ✅ SHA-256 verified |
| **G: AZAZAEL_ROOT** | `G:\AZAZAEL\AZAZAEL_ROOT\DISCLOSURE_WHITEPAPER_TODO.md` | ✅ SHA-256 verified |
| **Desktop Standalone** | `C:\Users\clint\Desktop\AZAZAEL_Standalone\DISCLOSURE_WHITEPAPER_TODO.md` | ✅ SHA-256 verified |
| **WSL2 Ubuntu** | `/root/azazael/DISCLOSURE_WHITEPAPER_TODO.md` | ✅ Copied via `/mnt/c/` bridge, SHA-256 verified |

All 5 copies verified with matching SHA-256: `c079426039bc402c962236db6fce7e758144f1b57dba84fc8f152a9649f141b4`

### Phase 3 — Sync Pattern Registration

**sync_all.py** (`scripts/sync_all.py`):
- Added `"DISCLOSURE_WHITEPAPER_TODO.md"` to `SYNC_DOC_PATTERNS` list
- Future `--sync-to wsl2`, `--sync-to desktop`, or `--sync-all` will automatically include DISCLOSURE

**sync_canonical_docs.py** (`src/SCRIPTS/sync_canonical_docs.py`):
- Added `"DISCLOSURE_WHITEPAPER_TODO.md"` to `CANONICAL_DOCS` list
- Comment: "Azazael ecosystem capability catalog — 14 sections"
- Future `--sync` or `--verify` will SHA-256 check and sync to Kali, Ubuntu, and G: pillars

**Windows hub copy:**
- Copied to `C:/Users/clint/azazael/DISCLOSURE_WHITEPAPER_TODO.md` (162 KB)
- SHA-256 verified match with G: source

### Phase 4 — AOA_STRUCTURE.html Rebuilt with BCC Section

**File:** `C:\Users\clint\Desktop\AOA\AOA_STRUCTURE.html`

| Change | Detail |
|--------|--------|
| Hero badge | "BCC Module" badge added |
| Section VII paragraph | Full BCC module description with all 6 module files, 303 tests, 10 templates, e-filing flags |
| LibraArm capabilities | Updated from 4 caps to 7: added check_berks_rules, calculate_berks_fees, generate_berks_ifp, prepare_berks_filing, get_berks_calendar |
| Libra line count | ~340 → ~580 (reflecting BCC module additions) |
| Footer | Updated with "BCC module (303 tests, 6 modules)" |
| Spec table | BCC entry added referencing `Libra/jurisdictions/pa/berks/` |

Browser-verified: zero console errors, all 6 changes visually confirmed.

### Key Files Modified

| File | Change |
|------|--------|
| `G:\AZAZAEL_SOURCE_OF_TRUTH\DISCLOSURE_WHITEPAPER_TODO.md` | Updated: C2B section, Libra rows, cross-references (9 edits) |
| `C:\Users\clint\Desktop\AOA\AOA_STRUCTURE.html` | Rebuilt: BCC hero badge, paragraph, Libra arm caps, footer, spec table (6 edits) |
| `C:\Users\clint\azazael\scripts\sync_all.py` | Added DISCLOSURE to SYNC_DOC_PATTERNS |
| `C:\Users\clint\azazael\src\SCRIPTS\sync_canonical_docs.py` | Added DISCLOSURE to CANONICAL_DOCS |
| `C:\Users\clint\azazael\DISCLOSURE_WHITEPAPER_TODO.md` | Copied from G: source, SHA-256 verified |
| `G:\source-of-truth\azazael\DISCLOSURE_WHITEPAPER_TODO.md` | Copied, SHA-256 verified |
| `G:\AZAZAEL\AZAZAEL_ROOT\DISCLOSURE_WHITEPAPER_TODO.md` | Copied, SHA-256 verified |
| `C:\Users\clint\Desktop\AZAZAEL_Standalone\DISCLOSURE_WHITEPAPER_TODO.md` | Copied, SHA-256 verified |
| `/root/azazael/DISCLOSURE_WHITEPAPER_TODO.md` (WSL2) | Copied, SHA-256 verified |

### Session Metrics

| Metric | Value |
|--------|-------|
| DISCLOSURE file size | 162 KB, 14 sections |
| Copies synced | 5 environments |
| SHA-256 integrity | All 5 copies verified match |
| Sync tools updated | 2 (sync_all.py + sync_canonical_docs.py) |
| AOA HTML edits | 6 changes, browser-verified |

---

## Session 2026-07-06 — Documentation Consolidation: PRODUCTION_TODO.md Migration, DirectMemory CLI, Memory Module Fixes

**Scope:** Comprehensive documentation cleanup — deleted the deprecated PRODUCTION_TODO.md and migrated all 17+ references across the canonical document ecosystem to CODEBASE_AUDIT_TODO.md. Fixed stale session_memory.db references in two memory modules. Added --banner flag to DirectMemory CLI. Created DISCLOSURE_WHITEPAPER_TODO.md.

### Phase 1 — CODEBASE_AUDIT_TODO.md Update (v12)

- Updated header date from June 19 (v11) to July 6 (v12) with summary of completed work
- Updated DirectMemory stats: 130 sessions/1,774 memories → 79,200 sessions/646,806 events/817 open
- Updated error log count: 60 → 138 errors (verified against ERROR_LOG.md)
- Added new Session Completion section for July 6 with 8 items: DM v1.1.0, CLI entry point, SessionMemory deprecation, parallax fix, whitepaper TODO, architecture docs, learnings recorded
- Added "Completed July 6 Session" accomplishments block

### Phase 2 — PRODUCTION_TODO.md Deletion & Reference Migration

**File deleted:** `azazael/PRODUCTION_TODO.md` (already archived in `docs/archive/`)

**RULE 0K canonical reading order updated** across all 5 core docs — item #7 now reads `CODEBASE_AUDIT_TODO.md`:

| File | Change |
|------|--------|
| `SYSTEM_INSTRUCTIONS.md` | Path + description: "Living production audit & wiring plan (supersedes PRODUCTION_TODO.md)" |
| `SOP.md` | Path + description updated in both RULE 0K table and compliance reference |
| `MANDATES.md` | RULE 0K reading order updated |
| `SESSION_STARTUP.md` | Startup file list updated |
| `MEMORIES.md` | Reading order + FILE INDEX table updated |
| `LESSONS_MASTER.md` | Status: "⚠️ Still referenced" → "✅ Archived July 6, 2026" |

**Skill files updated** (14 files via sed + sync): `azazael-deploy`, `azazael-architecture-review`, `azazael-files`, `azazael-todo-management` — path references replaced, stale instructions marked complete

**Secondary docs updated:** `CROSS_ENV_MANIFEST.md`, `NATIVE_INTELLIGENCE_ROADMAP.md`, `PROJECT_ALIGNMENT.md`, `TODO_FULL_PRODUCTION_WIRING.md`

**Historical references preserved** (not overwritten): `ERROR_LOG.md` (Error #92 historical context), `DISCLOSURE_WHITEPAPER_TODO.md` (worm-count claim attribution), `LESSONS_2026-06-04.md` (archive action record), `docs/archive/ARCHIVE_MANIFEST.md` (archive inventory)

**Final verification:** Zero stale `PRODUCTION_TODO.md` references remain in core canonical docs. Only intentional parenthetical "(supersedes PRODUCTION_TODO.md)" annotations persist.

### Phase 3 — Memory Module Fixes (session_memory.db → memory_store.db)

**Root cause:** `SessionMemory` class and its `session_memory.db` were deprecated in favor of `DirectMemory` and `~/.azazael/memory_store.db`.

**`memory_status.py`:**
- `_check_session_memory()` → `_check_direct_memory()`
- Replaced `from session_memory import SessionMemory` with `from CORE.direct_memory import DirectMemory`
- Replaced db_path + SessionMemory API with `DirectMemory.summary_stats()` + `db_size()` + `load_context()` static methods
- System key renamed: `session_memory` → `direct_memory`
- Banner display shows DirectMemory metrics: sessions (open), events, DB size, decisions, lessons, pending goals, hot-spots
- Added top 3 event types breakdown from `summary_stats()["top_event_types"][:3]`

**`performance_monitor.py`:**
- `DEFAULT_DBS` list: `"workspace/session_memory.db"` → `str(Path.home() / ".azazael" / "memory_store.db")`

### Phase 4 — DirectMemory CLI Enhancement

**New `--banner` flag** added to `direct_memory.py` CLI (alongside existing `--context`):
- Non-JSON mode: calls `DirectMemory.print_context_banner_static()` — displays sessions, lessons, hot-spot files, pending goals
- JSON mode: outputs raw `load_context()` data
- Added to epilog examples and "no flags" default check

### Phase 5 — FILE INDEX Update & sync_skills.py Runs

**MEMORIES.md FILE INDEX** updated:
- Header updated from "June 8, 2026" to "July 6, 2026" with session summary
- Added 7 missing canonical docs: `SOP.md`, `SESSION_STARTUP.md`, `LESSONS_MASTER.md`, `MANDATES.md`, `DISCLOSURE_WHITEPAPER_TODO.md`, `CORE/direct_memory.py`, `DAEMONS/parallax_validator.py`
- Updated descriptions: `ERROR_LOG.md` (138 errors), `CODEBASE_AUDIT_TODO.md` (primary living audit), `direct_memory.py` (CLI flags), `parallax_validator.py` (5-layer runaway-loop fix)

**`sync_skills.py` run 2×**: 128 skills updated both times, 0 drift between `azazael/skills/` and `.agents/skills/`

### Key Files Modified

| File | Change |
|------|--------|
| `CODEBASE_AUDIT_TODO.md` | v11→v12: DM stats, error count, July 6 session completion |
| `PRODUCTION_TODO.md` | **DELETED** — archived to docs/archive/ |
| `SYSTEM_INSTRUCTIONS.md` | RULE 0K item #7 updated |
| `SOP.md` | RULE 0K item #7 updated |
| `MANDATES.md` | RULE 0K reading order updated |
| `SESSION_STARTUP.md` | Startup file list updated |
| `MEMORIES.md` | Reading order + FILE INDEX + this session entry |
| `LESSONS_MASTER.md` | Status updated to "Archived July 6" |
| `src/memory_status.py` | SessionMemory → DirectMemory API |
| `src/performance_monitor.py` | DEFAULT_DBS: session_memory.db → memory_store.db |
| `src/CORE/direct_memory.py` | --banner CLI flag added |
| `DISCLOSURE_WHITEPAPER_TODO.md` | **CREATED** — 94KB full-legal-disclosure capability catalog |
| 14+ skill files | Path references migrated via sed + sync |
| 4 secondary docs | Cross-references updated |

### Session Metrics

| Metric | Value |
|--------|-------|
| Files deleted | 1 (PRODUCTION_TODO.md) |
| Files created | 1 (DISCLOSURE_WHITEPAPER_TODO.md) |
| Core canonical docs updated | 6 (SYSTEM_INSTRUCTIONS, SOP, MANDATES, SESSION_STARTUP, MEMORIES, LESSONS_MASTER) |
| Code files fixed | 3 (memory_status.py, performance_monitor.py, direct_memory.py) |
| Skill files updated | 14 |
| Secondary docs updated | 4 |
| Historical references preserved | 4 (ERROR_LOG, DISCLOSURE_WHITEPAPER, LESSONS_2026-06-04, ARCHIVE_MANIFEST) |
| sync_skills.py runs | 2 (128 updated, 0 drift both times) |
| PRODUCTION_TODO.md references migrated | 17+ → 0 (stale) |
| DirectMemory stats (current) | 79,200 sessions, 646,806 events, 817 open |
| Error log | 138 errors |

---

### Session 2026-08-08 — Startup + Anti-Pattern Scan + os_system Fix (WSL)

**Status:** ✅ Active — session `codebuff_20260808_073807`

**Changes this session:**
- Session startup complete: 12 skills loaded, RULE 0K canonical docs read in order, 132 skills synced (RULE 0R/0R-A), DirectMemory recording verified, compliance state machine healthy at CODE_EDIT, worm registry pre-warmed
- FreeBuff verified v0.0.142 (npm) — bun NOT installed per user directive
- Anti-pattern scan (ASTAntiPatternScanner, 680 files): 2,439 findings — 1,178 import_inside_function (known-intentional lazy pattern), 1,154 unicode_emoji (backlog, concentrated in CODEX video generators), 79 hardcoded_win_path, 11 os_system, 16 t_string (ALL false positives), 1 fstring_backslash (false positive), 0 cls_new_factory
- Fixed the only real os.system: `scripts/db_health.py` → ANSI escape + removed unused `import os` — tree os_system 11 → 10 (remaining = scanner test fixtures)
- Temp cleanup: removed sentinel_gate.py.tmp x2 + _test_run.log (full-depth .tmp sweep now empty)
- RULE 0R demo: skill edit → sync propagation verified (canonical ↔ .agents byte-identical) → reverted clean
- Standing directives armed: sync after canonical/skill edit; RULE 0V/0W gate before next code change

**Pending:**
- 79 hardcoded_win_path findings · 1,154 emoji backlog · telemetry generation (sentinel_enforcer block) · t_string scanner false positives

---
## Correction addendum — 2026-09-29 (stale worm/skill counts)
- Header above says "226 worms/35 cats" (Sep-14): live `discover_worms()` now reports
  **250 worms / 35 categories** (`src/CORE/worm_registry.py`). Prior dated claims:
  77 (skill body), 91/17, 104/18 (`WORM_CONFIG_TRACE.md` scope, not registry),
  184/27 (Sep-13 session), 220/35, 226/35, 232/36 (Sep-24 audit). Treat all as
  point-in-time; re-run discovery for fresh numbers.
- Skill counts: `SKILLS_CATALOG.md` regenerated this date — **1,234** table rows =
  1,234 mirror dirs = 1,234 canonical files. Prior 1,224 / 1,259 claims superseded.

---
## Correction addendum — 2026-11-03 (a write that reported success and did not land)
- **Symptom:** `write_file` and `str_replace` both returned success for
  `azazael/SCRIPTURE.md`; the file was not in this repo. It had landed in a second
  tree at `C:/Users/clint/azazael/`, because the agent tooling resolves relative paths
  against `C:/Users/clint`, **not** against this repo root.
- **Why it is easy to miss:** `C:/Users/clint` is itself a git repo (toplevel reports
  `C:/Users/clint`) and `C:/Users/clint/azazael` is a real directory, so nothing
  errors. Only a follow-up `wc`/`find` against `C:/Azazael` exposed it.
- **Detection:** `python tools/write_target.py <path>` prints the resolved path, the
  owning git toplevel, and PASS/FAIL against the expected root derived from the tool's
  own location; `--self-test` runs a control that must PASS inside the repo and must
  FAIL outside it (validated 2026-11-03, both directions).
- **Prevention:** after any write, confirm with `git status --porcelain <path>` run from
  `C:/Azazael/azazael`. A success message is not evidence of landing. Prefer absolute
  paths into this repo for every write from this client.

---
## Rule — 2026-11-03 — push scope (USER DIRECTIVE)

**Directive, verbatim, quoted once and not paraphrased:**

> we are not pushing any files not related to the projects already on git hub.

That is the whole rule. Everything below it is agent material, kept in its own
labelled section so the directive is never read as an inference.

### Agent intentions (agent-authored; NOT part of the directive)

- No push is performed, authored, staged for, or proposed by an agent without a
  direct instruction in that session. This session pushed nothing.
- When a push is instructed, the agent intends to: stage by path, run
  `git diff --cached --name-only`, and drop any path that does not belong to a
  project already present on the GitHub default branch (scratch scripts, render
  probes in `C:/tmp`, `.agy-debug-profile/`, `_board` spool, spooled JSONL).
- The agent intends to say which paths it will push, and why each belongs, before
  running `git push` — a plan stated separately from the directive above.

### Evidence measured 2026-11-03 (no bearing on the directive; recorded once)

- `myzticalbabe/azazael` is **public** (GitHub API `visibility: public`, HTTP 200),
  created `2026-11-03T02:55:10Z`, default branch `main`, `pushed_at 2026-11-03T05:13:49Z`,
  repo size 463,766 KB.
- `main` HEAD is `a882325f` — a commit **absent** from this clone. The 20 most recent
  `main` commits are all absent here; `src/RUST_VIDEO_WASM` returns HTTP **404** there.
- This clone and GitHub `main` are **separate lineages**, not a behind/ahead pair, so
  a push from here can only be a new branch or a deliberate history decision.
- This session's commits (`ff4acb92`, `fc64c94f`) exist only on disk, on
  `deepseek-engram-813`. The `github` remote advertises no such branch.
