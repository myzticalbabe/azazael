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

## Mandatory Session Startup (Execute in Order)

### Step 0: Confirm PRE-ACTION GATE Active
After reading SYSTEM_INSTRUCTIONS.md (RULE 0K #1), the PRE-ACTION GATE (RULE 0J) is now active.
You MUST print the gate assertion block before every code-modifying tool call for the entire session.

### Step 1: Read ALL Canonical Files in RULE 0K Order
```
read_files([
    "azazael/SYSTEM_INSTRUCTIONS.md",
    "azazael/SOP.md",
    "azazael/ERROR_LOG.md",
    "azazael/MEMORIES.md",
    "azazael/SESSION_STARTUP.md",
    "azazael/LESSONS_MASTER.md",
    "azazael/PRODUCTION_TODO.md"
])
```

### Step 2: Load Mandatory Guardrail Skills
```
skill("azazael-error-prevention")
skill("azazael-sop")
skill("azazael-pams-memory")
```

> **Note:** `skill("azazael-sop")` loads the SOP skill (mirror of `azazael/SOP.md`). The canonical SOP is already read in Step 1 via `read_files(["azazael/SOP.md"])`.

### Step 2.5: Sync Skills to .agents/ (RULE 0R)
```bash
python azazael/src/scripts/sync_skills.py
```
**RULE 0R mandates** that canonical skill files in `azazael/skills/` must be propagated to `.agents/skills/<name>/SKILL.md` for loadability via `skill()`. This script runs automatically at every session start. Without this sync, skill edits are invisible to the agent loading system.

### Step 2.6: Pre-Warm Worm Registry Cache (Error #57 fix)
```python
import sys; sys.path.insert(0, 'azazael/src')
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
import sys; sys.path.insert(0, 'azazael/src')
from CORE.direct_memory import DirectMemory
dm = DirectMemory()
# dm.record("session_start", {"purpose": "Coding session"})  # auto-recorded
```

### Step 5: Load Domain Skills Based on Task
- For cluster/worm work: `azazael-clusters`, `azazael-registry`, `azazael-worms`
- For memory/PAMS: `azazael-pams-memory`, `azazael-codex`
- For CAIN video: `azazael-cain-pipeline`, `azazael-cain-template`
- For builds: `azazael-packaging`, `azazael-deploy`
- For code quality: `azazael-conventions`, `azazael-testing`
- For Neural/ML work: `azazael-neural-architecture`, `azazael-training-pipeline`, `azazael-inference-providers`, `azazael-evolutionary-optimization`, `azazael-system-wiring`, `azazael-neural-pipeline`, `azazael-nsga2-testing`, `azazael-6api-analysis`

## Session Recording — Use DirectMemory (CANONICAL)

| Method | Import | Speed | Use When |
|--------|--------|-------|----------|
| `CORE.direct_memory.DirectMemory` | `from CORE.direct_memory import DirectMemory` | <0.1s | **CANONICAL** — ALL session recording (F03+F09 fix) |
| Direct SQLite injection | stdlib only | <2s | Bare-metal recording (fallback only) |

**SessionRecorder and CodebuffTracker are DEPRECATED and hard-blocked (F03 fix).**
They raise `ImportError` on import. Use `DirectMemory` for ALL session recording.
See `azazael/DIRECT_MEMORY_INSTRUCTIONS.md` for the complete mandate.

## Known Architecture Issues (2026-06-06)

### Worm Execution Blocked by Import Chain
`discover_worms()` scans 300+ Python files and imports ~91 worm modules on cold start
(38-45s). This makes running worms from fresh processes impractical. The function is
needed for registry-based worm resolution but blocks all CORE imports.

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
| DirectMemory (CANONICAL) | `azazael/src/CORE/direct_memory.py` |
| LocalMemoryStore (FTS5 queries) | `azazael/src/CORE/local_memory.py` |
| Eve Unleashed app | `Desktop/EveUnleashed_Selector/eve_unleashed_app.py` |
| FreeBuff binary | `~/.config/manicode/freebuff.exe` |
| Skills catalog | `azazael/SKILLS_CATALOG.md` |
