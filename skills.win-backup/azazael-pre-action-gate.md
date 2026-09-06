---
name: azazael-pre-action-gate
description: PERMANENT PRE-ACTION GATE (RULE 0J/0S) — 13-question mandatory assertion block. MUST be printed before EVERY str_replace, write_file, or spawn_agents call. Never disableable.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael PRE-ACTION GATE — Permanent Assertion Banner

> **Canonical sources:** `azazael/SYSTEM_INSTRUCTIONS.md` (RULE 0J), `azazael/SOP.md` (RULE 0S)
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
| Batch script with Gemini + one-file test + backup | **PROCEED** |

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
