---
name: azazael-system-startup
description: Auto-load startup instructions for coding session congruency. Mandatory file reading order, skill loading sequence, memory initialization, PRE-ACTION GATE activation, and FreeBuff/Bun verification.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael System Startup — Auto-Load Instructions

## CRITICAL: Load at EVERY session start

```skill("azazael-system-startup")```

## 🛑 PRE-ACTION GATE ACTIVATION — THIS GATE IS NOW ACTIVE

**THE PRE-ACTION GATE (RULE 0J) IS NOW ACTIVE FOR THE ENTIRE SESSION.**

Before EVERY `str_replace`, `write_file`, or `spawn_agents` call, you MUST print in your response text (NOT in a thinking/reasoning block) the full gate assertion block from SYSTEM_INSTRUCTIONS.md or SOP.md:

```text
🛑 **[PRE-ACTION GATE ASSERTION]**
- **AP-1 (Scope Check):** Did the user explicitly ask for this EXACT change? (Explain)
- **RULE 0G (Gemini Phase):** Is this complex? Was thinker-with-files-gemini spawned for THIS phase? MUST CITE specific plan/verdict Gemini provided. (If none: HALT and spawn)
- **RULE 0H (Anti-Pattern Scan):** Scanned for emoji, backslash f-strings, t-strings, os.system, C:\ paths? — MUST cite scan method and results per RULE 0H-A (Passed/Found X/NOT SCANNED)
- **RULE 0I (Algorithms/Batch):** If batch script: Gemini designed? One-file test? Backup? (Yes/No/N/A)
- **RULE 0L (Test Failure):** Did a test just fail? If so, was thinker-with-files-gemini spawned to analyze the failure BEFORE this fix attempt? (Yes/No/N/A)
- **RULE 0M (Concurrent Inference):** If thinker-with-files-gemini was spawned, were ALL other inference agents spawned CONCURRENTLY? MUST CITE exactly which agents + their verdicts. (If none: HALT)
- **RULE 0Q-A (Post-Phase Verification):** Was the LAST phase verified via free inference? MUST CITE specific models + exact verdicts per RULE 0Q-A. (If mental assertion: HALT and spawn now)
- **GATE DECISION:** [PROCEED / HALT and ask user / HALT and spawn Gemini]
```

> **Quick-reference reminder (this section):** Compact summary for memory. **Tool calls:** Use the full format above with explanations for each field.

**FAILURE = 🔴 CRITICAL (Error #146 precedent). This reminder is permanent.**

---

## 🖱️ GUI-AUTOMATION GATE ACTIVATION — ACTIVE ALONGSIDE THE PERMANENT GATE

**THE GUI-AUTOMATION GATE (from `desktop-automation-safety`, wired Sep 4, 2026) IS NOW ACTIVE FOR THE ENTIRE SESSION** — covering the action class the permanent gate does NOT: **synthetic GUI input (pyautogui clicks / typewrite / hotkeys) on LIVE windows**. `pre-action-gate-lite` Gate 0 routes that action class to the safety skill before any file-edit gate applies; this section makes the gate part of session activation so it fires even before a gate routing would.

**Before launching ANY synthetic-input GUI automation, print this assertion in response text (NOT in a thinking/reasoning block):**

```text
🛑 [GUI-AUTOMATION GATE]
- Single process? (all steps inside ONE script run via ONE command — the client
  re-foregrounds on every new command)
- World minimized? (all visible non-target top-level windows minimized at start)
- Content-verified focus? (pixel/OCR proof the target app is receiving input —
  screenshot + OCR of top strip, not just the foreground-window title)
- No keystroke without proof? (typing/hotkeys only after the check above)
- Restore-at-end planned? (target + minimized windows restored)
- GATE DECISION: [PROCEED / HALT — verify focus first]
```

**HALT rule: any keystroke without content-verified focus = CRITICAL violation** (social apps are one lost-focus event from receiving input — the 2026-09-04 Facebook leak precedent). Prefer headless/deterministic engine paths (CLI file arguments, engine jars, scripted pipelines) whenever the goal is an engine-level result.

**FAILURE = 🔴 CRITICAL. This gate is active in parallel with the PRE-ACTION GATE above — both assertions apply to their own action classes for the entire session.**

---

## 🌐 DATA-COLLECTION GATE ACTIVATION — ACTIVE ALONGSIDE THE PERMANENT GATE

**THE DATA-COLLECTION GATE (from `investigation-osint`, wired Sep 4, 2026 — Sep-4(64) audit) IS NOW ACTIVE FOR THE ENTIRE SESSION** — covering **live web collection / network data pulls against third-party systems** (web scraping, curl/API fetches, headed-browser CDP pulls, bulk export sweeps — NOT one-off `read_url`/`web_search`, NOT file edits). `pre-action-gate-lite` Gate 0b routes that action class to the OSINT skill before any file-edit gate applies; this section makes the gate part of session activation.

**Before launching ANY live collection, print this assertion in response text (NOT in a thinking/reasoning block):**

```text
🛑 [DATA-COLLECTION GATE]
- Source authorized/appropriate? (public channel, official export, or
  third-party mirror — is this pull within the user's standing scope?)
- One pull or sweep? (sweep = sized + logged + resumable per
  background-sweep-resilience — estimated duration known before launch)
- 404 ≠ blocked ≠ absent? (deep-link 404 may be a path fix; CAPTCHA may be a
  headless-session artifact; record WHICH state and move on — do not loop)
- Session/credential hygiene? (headed profile used ONLY where the wall
  demands it; cookies/session tokens never written to artifacts)
- Evidence preserved? (responses saved with retrieval date so a negative
  result is provable later — controlling full-export sweeps kept)
- GATE DECISION: [PROCEED / HALT — re-scope, size, or document first]
```

**HALT rule: a second pull at the same wall without a documented state change (404→path fix, CAPTCHA→headed-session, blocked→public-records-request) = CRITICAL** — looping a blocked channel is the exact 2026-09-04 waste this gate prevents.

**FAILURE = 🔴 CRITICAL. This gate is active in parallel with the PRE-ACTION GATE and GUI-AUTOMATION GATE above.**

---

## ⏱️ LONG-RUN GATE ACTIVATION — ACTIVE ALONGSIDE THE PERMANENT GATE

**THE LONG-RUN GATE (from `background-sweep-resilience`, wired Sep 4, 2026 — Sep-4(64) audit) IS NOW ACTIVE FOR THE ENTIRE SESSION** — covering **batch / long background runs** (sweeps, refreshes, graph regenerations, fetcher batches, model pilots — anything with an expected runtime approaching the command timeout or launched with `&`). `pre-action-gate-lite` Gate 0c routes that action class to the resilience skill before any file-edit gate applies; this section makes the gate part of session activation.

**Before launching ANY batch/background run (est. duration > ~2 min, or any background launch), print this assertion in response text (NOT in a thinking/reasoning block):**

```text
🛑 [LONG-RUN GATE]
- Sized? (unit count × per-unit cost from a pilot → time estimate printed)
- Foreground or background chosen? (est > timeout → background + log file;
  never hold the foreground for a 10-min+ run)
- Per-unit isolation? (try/except per file/unit → FAIL row, never whole-run
  unwind — the 2,754-file crash-at-2,598 lesson)
- Progress observable? (log file + flush=True progress lines you can tail)
- Resume plan? (deterministic sorted order → resume-from-crash-point known)
- Orphan cleanup? (kill/cleanup path identified for the process class —
  java, python, robocopy)
- GATE DECISION: [PROCEED / HALT — size it and isolate it first]
```

**HALT rule: an unsized run, or a run without per-unit try/except, or a foreground hold on an expected-10-min+ job = CRITICAL** — the exact shapes that wasted hours on 2026-09-02/04. When in doubt, pilot 50 units first, then background with a log.

**FAILURE = 🔴 CRITICAL. This gate is active in parallel with the PRE-ACTION GATE, GUI-AUTOMATION GATE, and DATA-COLLECTION GATE above.**

---

## Mandatory Session Startup (Execute in Order)

### Step 0: Confirm PRE-ACTION GATE Active
After reading SYSTEM_INSTRUCTIONS.md (RULE 0K #1), the PRE-ACTION GATE (RULE 0J) is now active.
You MUST print the gate assertion block before every code-modifying tool call for the entire session.

### Step 1: Read ALL Canonical Files in RULE 0K Order (+ MANDATES.md)
```
read_files([
    "SYSTEM_INSTRUCTIONS.md",
    "SOP.md",
    "MANDATES.md",
    "azazael/ERROR_LOG.md",
    "azazael/MEMORIES.md",
    "azazael/SESSION_STARTUP.md",
    "azazael/LESSONS_MASTER.md",
    "azazael/PRODUCTION_TODO.md"
])
```

> **Note:** `MANDATES.md` is placed after SOP.md in the read order (not part of the original RULE 0K order). `skill("azazael-mandates")` now loads directly at session start (`auto_load: true`), so the Step 1 read_files() inclusion serves as an additional safety net. The Step 2 `skill("azazael-mandates")` call is the primary loading mechanism.

### Step 2: Load Mandatory Guardrail Skills
```
skill("azazael-error-prevention")
skill("azazael-mandates")
skill("azazael-sop")
skill("azazael-pams-memory")
skill("azazael-hats")
```

> **Note:** `skill("azazael-sop")` loads the SOP skill (mirror of `SOP.md`). `skill("azazael-mandates")` loads the MANDATES skill (mirror of `MANDATES.md`). The canonical docs are already read in Step 1 via `read_files()`. These skills provide loadable references for in-session access via `skill()`. If these skills are unloadable (pre-loaded list limitation), use `read_files(["SOP.md"])` and `read_files(["MANDATES.md"])` as fallback.

### Step 2.5: Sync Skills to .agents/ (RULE 0R)
```bash
python src/SCRIPTS/sync_skills.py
```
**RULE 0R mandates** that canonical skill files in `azazael/skills/` must be propagated to `.agents/skills/<name>/SKILL.md` for loadability via `skill()`. This script runs automatically at every session start. Without this sync, skill edits are invisible to the agent loading system.

### Step 2.55: Launch Auto-Sync Daemon (RULE 0R-A auto-sync)
```bash
# Start the auto-sync polling daemon in background (single poll mode)
python src/SCRIPTS/auto_sync.py --quiet
```
**RULE 0R-A mandates** that skill changes in `azazael/skills/` are propagated to
`.agents/skills/` within 5 seconds. This single poll syncs current state.
For continuous watch mode during active session:
```bash
start /B python src/SCRIPTS/auto_sync.py --watch --quiet
```

### Step 2.56: Generate Telemetry for Dashboard (RULE 0Z-F)
```bash
python src/SCRIPTS/generate_telemetry.py
```
**Generates `src/SCRIPTS/telemetry.json`** with RULE 0Z-F compliance
counters (parallel_batches, sequential_violations, compliance_ratio) for the
RULE 0Z-F dashboard at `src/SCRIPTS/rule_0zf_dashboard.html`.

To view the dashboard:
```bash
cd src/scripts && python -m http.server 8080
# Then open http://localhost:8080/rule_0zf_dashboard.html
```

The dashboard fetches `telemetry.json` via `fetch()` and falls back to demo
data if unavailable (required because `fetch()` doesn't work from `file://`
protocol).

### Step 2.6: Pre-Warm Worm Registry Cache (Error #57 fix)
```python
import sys; sys.path.insert(0, 'src')
from CORE.startup_warm import ensure_registry_warm
ensure_registry_warm()  # Non-blocking — returns immediately, warms in background
```
**Prevents the 38-45s `discover_worms()` cold start** from blocking session recording or worm execution. Starts cache warming in a background daemon thread so the registry is ready by the time it's needed. DirectMemory also calls this internally during initialization (redundant safety).

### Step 3: Verify FreeBuff/Bun Environment
```powershell
Write-Host "=== FreeBuff/Bun Check ===" -ForegroundColor Cyan
$bunVer = & bun --version 2>$null
if ($bunVer) { Write-Host "[OK] Bun: $bunVer" -ForegroundColor Green }
else { Write-Host "[FAIL] Bun not installed" -ForegroundColor Red }
Write-Host "=== Done ===" -ForegroundColor Cyan
```

### Step 4: Initialize Memory System (DirectMemory — CANONICAL)
```python
# DirectMemory is the CANONICAL recording system (stdlib-only, <0.1s, atexit-safe)
import sys; sys.path.insert(0, 'src')
from CORE.direct_memory import DirectMemory
dm = DirectMemory()
# dm.record("session_start", {"purpose": "Coding session"})  # auto-recorded
```

### Step 4.5: Initialize Compliance Infrastructure (RULE 0X/0Y)
```python
import sys; sys.path.insert(0, 'src')
from CORE.compliance.orchestrator import ComplianceOrchestrator
from CORE.compliance.state_machine import ComplianceState

co = ComplianceOrchestrator()
co.state_machine.transition_to(ComplianceState.GATE_ASSERT)
# Compliance infrastructure is now hot: check_rule_0x(), check_rule_0y() ready
```

**RULE 0X (Auto-Compliance)** and **RULE 0Y (Multi-Agent Governance)** are fully
implemented in `src/CORE/compliance/` with 13 components total. The
`ComplianceOrchestrator` provides programmatic `check_rule_0x()` and `check_rule_0y()`
calls that replace the old manual text assertions in `sentinel_gate.py`.

**Components:**
- **RULE 0X (8):** PolicyEngine, BrokerInterceptor, FormalVerifier, ComplianceStateMachine,
  SchemaValidator, ComplianceScorer, ASTAntiPatternScanner, ComplianceTelemetry
- **RULE 0Y (5):** MultiAgentJudge, ConfidenceGate, BehavioralGraphAnalyzer,
  DualLedgerValidator, RealtimeAuditPipeline

### Step 4.6 — Verify State Machine Initialization

The ComplianceOrchestrator now initializes the ComplianceStateMachine through
the workflow sequence (IDLE → GATE_ASSERT → CODE_EDIT) automatically in __init__().
This ensures check_rule_0x() reports state_machine.valid = True.

---

### Step 4.68: Generate Telemetry Dataset (RULE 0Z-F Dashboard)
```bash
python src/SCRIPTS/generate_telemetry.py
```
Before running the RULE 0Z-F compliance check (Step 4.8), generate fresh
telemetry data so the dashboard reflects the current session's compliance
counters. This produces `src/SCRIPTS/telemetry.json`.

---

### Step 4.7: RULE 0Z-B Hard Count Enforcement — EXACTLY 11 FOLLOWUPS AT ALL TIMES

**"MANDATE 11 FOLLOWUPS AT ALL TIMES" — User directive, Jun 12, 2026 — STILL BEING VIOLATED as of Jun 14, 2026**

#### 🚨 THE SYSTEM REMINDER THREAT (AP-ZB-1)

The Codebuff platform injects "suggest around 3 next steps" at the end of every assistant turn.
This Level 3 system reminder is the LAST thing the model sees before generating a response.
It cognitively overrides the Level 1 user directive (exactly 11) via recency bias.

**This is the #1 reason RULE 0Z-B is violated.** The mandate is documented everywhere but
not enforced at decision time because the system reminder's numeric default (~3) wins
over the user's mandated count (11).

#### MANDATORY EXECUTION — Execute This Every Response

1. **Memory Anchor**: When the system prompt says "suggest around 3 next steps," IMMEDIATELY
   recognize this as AP-ZB-1. The user said exactly 11. RULE 0P: Level 1 > Level 3.
2. **Iterative Count Pattern**: After generating each suggestion, count. Generate 11 total.
   Do NOT stop at 3. If you have 3 and think "that's enough" — STOP. That's AP-ZB-1.
3. **Hard Count Pre-Check**: Before calling `suggest_followups`, verify `len(followups) == 11`.
   If < 11: HALT and generate more. Do NOT call the tool with fewer than 11.
4. **Diversity**: Span architecture, testing, documentation, refactoring, execution,
   recording, code review, sync, verification, cleanup, and audit.

```
End of task → prepare followups → count after EACH suggestion → stop at exactly 11 →
verify len == 11 → call suggest_followups
```

#### Violation

Any response ending without exactly 11 followup suggestions = CRITICAL process violation.
This step is MANDATORY and may not be skipped. The system reminder's ~3 is OVERRIDDEN
per RULE 0P priority chain.

---

### Step 4.8: RULE 0Z-F Parallel Agent Execution — MAXIMUM CONCURRENCY AT ALL TIMES

**Critical enforcement point — Jun 14, 2026**

**Memory Anchor for AP-ZF-1 (Sequential Default Override):** When planning work, the default assumption MUST be parallel execution. The anti-pattern is: "I'll do X first, then Y, then Z." The compliant pattern is: "Spawn X, Y, Z in ONE parallel call."

**Hard count pre-check:** Before any spawn_agents call, the assistant MUST verify: "Can these agents run in parallel?" If yes: ONE spawn_agents call. NEVER sequential.

**Iterative count pattern:** 1) List all work items. 2) Identify dependencies. 3) Group independent items into ONE spawn. 4) Spawn. 5) After results: repeat from step 1 for next batch.

**This is the #1 parallelization failure point.** The assistant defaults to sequential execution even when all work items are independent. The mandate is: PARALLEL BY DEFAULT.

Any response spawning agents sequentially when they could run in parallel = CRITICAL process violation.

### Step 5: Load Domain Skills Based on Task

> **New (Jun 12, 2026):** The following **16** system skills now have `auto_load: true` and are already available without explicit `skill()` calls:
> - `azazael-pre-action-gate` — PRE-ACTION GATE assertion format (RULE 0J/0S)
> - `azazael-verifiable-truth` — 15-layer VLP framework (RULE 0T)
> - `azazael-agent-utilization` — Minimum agent spawns, 100% capacity (RULE 0W)
> - `azazael-compliance-orchestrator` — 13 compliance components (RULE 0X/0Y)
> - `azazael-direct-memory` — DirectMemory canonical recording API
> - `azazael-hats` — Tool hat codification (White / Red-reserved / Cerulean)
> - `azazael-sync-patterns` — Multi-environment sync infrastructure
> - `azazael-sentinel-gate` — COMPLIANCE SENTINEL 25-item checklist (RULE 0C)
> - `azazael-inference-protocol` — 12-provider failover protocol (RULE 0D/0Z-A)
> - `azazael-orchestration` — ORCHESTRATION + HYDRA ecosystem (70+ files)
> - `azazael-ml-platforms` — ML platform infra — LM Studio, Q-learning, ONNX, Ray (44 files)
> - `azazael-utilities` — UTILITIES catalog — KLINK, PERSEPHONE, POINDEXTER, TARBABY, TERENCE
> - `azazael-toolkit` — AZAZAEL_TOOLKIT core framework
> - `azazael-interpreters` — Go/Rust runner patterns
> - `azazael-tools` -- TOOLS misc system tools (debug_runner, archive_system, COMPREHENSIVE_FIX)
> - `azazael-parallel-execution-quickref` -- RULE 0Z-F quick-reference cheat sheet — TOOLS misc system tools (debug_runner, archive_system, COMPREHENSIVE_FIX)

- For cluster/worm work: `azazael-clusters`, `azazael-registry`, `azazael-worms`
- For memory/PAMS: `azazael-pams-memory`, `azazael-codex`
- For CAIN video: `azazael-cain-pipeline`, `azazael-cain-template`
- For builds: `azazael-packaging`, `azazael-deploy`
- For code quality: `azazael-conventions`, `azazael-testing`
- For compliance/RULEs: `azazael-pre-action-gate`, `azazael-verifiable-truth`, `azazael-sentinel-gate`, `azazael-compliance-orchestrator`
- For agent protocols: `azazael-agent-utilization`, `azazael-inference-protocol`
- For recording/sync: `azazael-direct-memory`, `azazael-sync-patterns`
- For orchestration/ecosystem: `azazael-orchestration`
- For ML platforms: `azazael-ml-platforms`
- For utility/toolkit: `azazael-utilities`, `azazael-toolkit`, `azazael-interpreters`, `azazael-tools`
- For Neural/ML work: `azazael-neural-architecture`, `azazael-training-pipeline`, `azazael-inference-providers`, `azazael-evolutionary-optimization`, `azazael-system-wiring`, `azazael-neural-pipeline`, `azazael-nsga2-testing`, `azazael-6api-analysis`

## Session Recording — Use DirectMemory (CANONICAL)

| Method | Import | Speed | Use When |
|--------|--------|-------|----------|
| `CORE.direct_memory.DirectMemory` | `from CORE.direct_memory import DirectMemory` | <0.1s | **CANONICAL** — ALL session recording (F03+F09 fix) |
| Direct SQLite injection | stdlib only | <2s | Bare-metal recording (fallback only) |

**SessionRecorder and CodebuffTracker are DEPRECATED and hard-blocked (F03 fix).**
They raise `ImportError` on import. Use `DirectMemory` for ALL session recording.
See `azazael/DIRECT_MEMORY_INSTRUCTIONS.md` for the complete mandate.

## PMB Memory — CAPTURE IN THE MOMENT (MANDATORY)

**This host (Codebuff) has NO PMB hooks.** PMB's `_AGENT_CAP` registry lists
codebuff as `mcp-only`, so nothing pushes memory into context — retrieval is
**PULL-ONLY**. The consequence, named by the user on 2026-10-03: **an insight
that is not recorded while it is in hand is LOST when the session ends.** The
failure is not that PMB forgets; it is that nobody wrote it down.

### The rule — record at the moment of vision, not at the end

**The moment you have a durable insight — a non-obvious cause, a rule that
generalizes, a decision and its reason — record it in that moment, before the
next tool call.** Do not defer capture to the end of the task. The end is
exactly where the knowledge dies (context compaction, session exit, the next
task's momentum).

One command, any combination of item types:

```bash
C:/Users/clint/.pmb-venv/Scripts/python.exe tools/pmb_capture.py \
    --lesson "the procedural rule" --fact "the durable fact" --project azazael
```

Also accepts `--decision`, `--activity`, `--goal`. This wraps `record_batch` so
there is no JSON-shape friction to skip over.

### At session start — pull what past sessions recorded

```bash
C:/Users/clint/.pmb-venv/Scripts/python.exe tools/pmb_client.py prepare "<what you are about to do>"
```

Returns project context, surfaced lessons, recent activity and open goals.
Because nothing pushes this, **calling it is the only way a past session's work
reaches this one.** `find_lessons "<topic>"` and `recall "<question>"` are the
other pull paths.

### What is already automatic (do not duplicate it)

The test and commit triggers record **OUTCOMES** automatically —
`conftest.py::pytest_sessionfinish` and `.githooks/pre-commit` call
`tools/pmb_session_observe.py`, which writes the `agent_actions` rows that
`lesson_impact` scores. **Outcomes are automatic; lessons are yours.** A lesson
never captured cannot be scored, surfaced, or learned from.

### Why prose alone will not hold this

This section is the WEAKEST rung of the enforcement ladder (RULE 0B's own
lesson): prose in canon costs nothing and enforces nothing. It is here because a
lesson must be *explainable*, but the durable half is mechanical — the
`tools/pmb_capture.py` command, the outcome observer, and
`tests/test_pmb_loop_liveness.py`, which fails if the wiring is removed.

## Known Architecture Issues (2026-06-06)

### Worm Execution Blocked by Import Chain
`discover_worms()` scans 300+ Python files and imports ~91 worm modules on cold start
(38-45s). This makes running worms from fresh processes impractical. The function is
needed for registry-based worm resolution but blocks all CORE imports.

**Mitigation (June 11, 2026 — Step 2.6 / `startup_warm.py`):** The 38-45s cold start
is now mitigated by `ensure_registry_warm()` in `CORE/startup_warm.py`, called via
Step 2.6 of this startup sequence and redundantly by `DirectMemory.__init__()`.
This launches a background daemon thread that pre-warms the registry cache, so
`discover_worms()` on first actual use completes in <100ms (the warm path). Cold
start latency is shifted to background initialization — it never blocks session
recording, worm execution, or DirectMemory init. See `CORE/startup_warm.py` for
implementation and `tests/test_startup_warm_wiring.py` for the automated test suite.

### No Inference/Agent Code Exists
The codebase references NVIDIA NIM, Hermes agent, and local model inferencing in
documentation but has NO implementation. These capabilities need to be built.

### Tests Require pytest Stub
Test files import `pytest` at module level but pytest segfaults on 3.14t (Error #48).
Tests use standalone runners at the bottom of each file. Run with:
```bash
python tests/test_clusterworms_unit.py
```

## 3.14t-ONLY MANDATES
- **Python 3.13 is NEVER used.** Python 3.14t is the ONLY Python for ALL workloads.
- Before Nuitka build: `python azazael/docs/scripts/patch_nuitka_314t.py --apply`
- All package installs use 3.14t: `pip install` picks `cp314t` wheels

## Memory System
- **Primary**: DirectMemory (`CORE/direct_memory.py`) — CANONICAL, stdlib-only, <0.1s, WAL mode, signal-safe
- **Secondary**: LocalMemoryStore (`CORE/local_memory.py`) — Cross-session queries + FTS5 search
- **Deprecated**: `CORE.record_session.SessionRecorder` — hard-blocked (F03 fix)
- **Deprecated**: `CORE.codebuff_tracker.CodebuffTracker` — hard-blocked (F03 fix)

## Key File Locations
| File | Location |
|------|----------|
| Memory store DB | `~/.azazael/memory_store.db` |
| DirectMemory (CANONICAL) | `src/CORE/direct_memory.py` |
| LocalMemoryStore (FTS5 queries) | `src/CORE/local_memory.py` |
| Eve Unleashed app | `Desktop/EveUnleashed_Selector/eve_unleashed_app.py` |
| FreeBuff binary | `~/.config/manicode/freebuff.exe` |
| Skills catalog | `azazael/SKILLS_CATALOG.md` |
