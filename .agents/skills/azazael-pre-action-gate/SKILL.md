---
name: azazael-pre-action-gate
description: PERMANENT PRE-ACTION GATE (RULE 0J/0S) — 13-question mandatory assertion block. MUST be printed before EVERY str_replace, write_file, or spawn_agents call. Never disableable. NOTE: auto_load is inert in this client (body never reaches agent unprompted); load explicitly via skill("azazael-pre-action-gate"). Checks whose agent is UNAVAILABLE per the AVAILABILITY PRE-CHECK resolve to N/A, not HALT.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael PRE-ACTION GATE — Permanent Assertion Banner

> **Canonical sources:** `SYSTEM_INSTRUCTIONS.md` (RULE 0J), `SOP.md` (RULE 0S)
> **This gate is PERMANENTLY ACTIVE. CANNOT BE DISABLED.**

---

## 🛑 THE PERMANENT GATE

**BEFORE EVERY** `str_replace`, `write_file`, or `spawn_agents` (for batch scripts) call,
you MUST print the following assertion block in your **response text** (NOT in a thinking/reasoning block).

### Assertion Format (13 Mandatory Checks)

```text
🛑 **[PRE-ACTION GATE ASSERTION]**
- **AP-1 (Scope Check):** Did the user explicitly ask for this EXACT change? (Explain)
- **RULE 0G (Gemini Phase):** Is this complex? Was thinker-with-files-gemini spawned for THIS phase? MUST CITE specific plan/verdict Gemini provided. (If none: HALT and spawn)
- **RULE 0H (Anti-Pattern Scan):** Scanned for emoji, backslash f-strings, t-strings, os.system, C:\ paths? — MUST cite scan method and results per RULE 0H-A (Passed/Found X/NOT SCANNED)
- **RULE 0I (Algorithms/Batch):** If batch script: Gemini designed? One-file test? Backup? (Yes/No/N/A)
- **RULE 0L (Test Failure):** Did a test just fail? If so, was thinker-with-files-gemini spawned to analyze the failure BEFORE this fix attempt? (Yes/No/N/A)
- **RULE 0M (Concurrent Inference):** If thinker-with-files-gemini was spawned, were ALL other inference agents spawned CONCURRENTLY? MUST CITE exactly which agents + their verdicts. (If none: HALT)
- **RULE 0Q-A (Post-Phase Verification):** Was the LAST phase verified via free inference? MUST CITE inference cache filepaths (e.g., .inference_cache/20260611_120000_gemini.log). (If no cache files exist: HALT and spawn now)
- **RULE 0U (System Reminders):** Did the last system prompt remind you to spawn Gemini or a Code Reviewer? If yes, are you spawning them INSTANTLY right now BEFORE any other tool calls? (Explain: [Yes, spawning now / No reminder / N/A])
- **RULE 0V (Code Reviewer):** Is a code change being made? Was code-reviewer-deepseek spawned BEFORE this change to review the plan? Will code-reviewer-deepseek be spawned AFTER to review the result? (Explain: [Yes, spawned before / About to spawn after / N/A no code change])
- **RULE 0W (Agent Utilization):** Are ALL applicable agents being spawned at 100% capacity for this task type? (Count spawned: [N] / Required minimum [M] — [PASS / UNDERUTILIZED — HALT and spawn more])
- **RULE 0Z (Spawn Mandate):** Were thinker-gpt + basher (diagnostic runner) + code-reviewer-deepseek spawned for THIS task/sub-task BEFORE any work began? (Explain: [Yes / No - CRITICAL violation])
- **RULE 0Z-A (Auto-Fallback):** If thinker-gpt was unavailable, was the auto-fallback executed (query ALL free models via providers.py) instead of proceeding without inference? (Explain: [Yes, fallback executed / No - CRITICAL violation])
- **GATE DECISION:** [PROCEED / HALT and ask user / HALT and spawn Gemini]
```

---

## Enforcement

| Violation | Severity |
|-----------|:--------:|
| Executing str_replace/write_file/spawn_agents without gate | 🔴 CRITICAL |
| Printing gate in thinking block instead of response text | 🔴 CRITICAL (Error #148) |
| AP-1 violation (fixing things user didn't ask for) | 🔴 CRITICAL |
| RULE 0I violation (batch script without Gemini) | 🔴 CRITICAL |

## Quick Reference

| Situation | Gate Result |
|-----------|:-----------:|
| User says "fix X", you write fix for X | **PROCEED** |
| User says "analyze X", you write fix for X | **HALT** — AP-1: user didn't ask for fix |
| You notice a bug and want to fix it | **HALT** — AP-1: user didn't ask |
| Batch script without Gemini + one-file test + backup | **HALT** — RULE 0I |
| Batch script with Gemini + one-file test + backup | **PROCEED** |## Action-Class Routing (additive — does not alter the 13 checks above)

This gate covers file-edit actions. Three OTHER action classes sit outside the
13 checks — route each to its gate-owner skill before acting (all wired
2026-09-04, Sep-4(58)/(64)):

1. **Synthetic GUI input on LIVE windows** (pyautogui clicks/typewrite/hotkeys)
   → run `desktop-automation-safety`'s GUI-AUTOMATION GATE (single process,
   minimize-world, content-verified focus, no keystroke without pixel proof,
   restore-at-end). Keystrokes without content-verified focus are a CRITICAL
   violation (lost focus once sent input to Facebook/Messenger — Sep-4(55)).
2. **Live web collection / network data pulls** (scraping / curl-API / headed-
   browser CDP / bulk export sweeps vs third-party systems) → run
   `investigation-osint`'s DATA-COLLECTION GATE (404-≠-blocked-≠-absent;
   no second pull at the same wall without a documented state change;
   official-export / records-request when public channels are exhausted).
3. **Batch / long background runs** (sweeps, refreshes, fetchers, model
   pilots, est. runtime approaching the command timeout) → run
   `background-sweep-resilience`'s LONG-RUN GATE (size from a pilot,
   background + log over foreground hold, per-unit isolation, resume plan).

4. **External sends / filings** (emails, complaints, RTK/FOIA, records
   requests) → **user-executed ONLY** — absolute rule, never an agent action
   (Sep-4(65) audit). All items stay DRAFT/UNSENT in the corpus send matrix
   until the user executes; BCC excluded from all recipient lists.
5. **Tool / package installs** (pip / winget / apt / go install) →
   `azazael-environment` (3.14t-only discipline) + `azazael-error-resolution`
   Step 4 (cp314t wheel selection).

Agent spawns stay inside this gate's RULE 0I / 0W / 0Z checks (no separate
route). Prefer headless/deterministic execution whenever the engine result is
what matters.

## Related Skills

> **All skills below have `auto_load: true` — they are already loaded and available without explicit `skill()` calls.**

- `azazael-sop` — SOP mirror (RULE 0S defines the gate)
- `azazael-mandates` — MANDATES mirror (RULE 0J defines the gate)
- `azazael-verifiable-truth` — 15-layer VLP framework (RULE 0T citations verified in gate's 0Q-A check)
- `azazael-agent-utilization` — Minimum agent spawns, 100% capacity (RULE 0W checked in gate assertion)
- `azazael-compliance-orchestrator` — Programmatic compliance infrastructure (RULE 0X/0Y gate checks)
- `azazael-sentinel-gate` — Pre-action authorization sentinel (25-item checklist)
- `azazael-inference-protocol` — 12-provider failover (RULE 0Z-A auto-fallback checked in gate)
- `azazael-direct-memory` — Canonical recording (gate decisions must be recorded)
- `azazael-sync-patterns` — Multi-environment sync (RULE 0R sync check after gate pass)
- `azazael-system-startup` — Activates the gate at session start

- `desktop-automation-safety` *(auto_load: false — load on demand)* — the gate for synthetic-input GUI automation (routing note above)
- `investigation-osint` *(auto_load: false — load on demand)* — the DATA-COLLECTION GATE for live web collection / network pulls (routing #2 above)
- `background-sweep-resilience` *(auto_load: false — load on demand)* — the LONG-RUN GATE for batch / background runs (routing #3 above)
