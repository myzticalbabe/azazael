---
name: azazael-sentinel-gate
description: COMPLIANCE SENTINEL (RULE 0C/0S) — Mandatory PRE-ACTION AUTHORIZATION GATE. 25-item self-audit checklist. NOT a post-action audit. HALT on any violation. NOTE: auto_load is inert in this client (body never reaches agent unprompted); load explicitly via skill("azazael-sentinel-gate"). Checks whose agent is UNAVAILABLE per the AVAILABILITY PRE-CHECK resolve to N/A, not HALT.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael COMPLIANCE SENTINEL — Pre-Action Authorization Gate

> **Canonical source:** `SYSTEM_INSTRUCTIONS.md` (RULE 0C)
> **The SENTINEL is a PRE-ACTION AUTHORIZATION GATE, NOT a post-action audit.**

---

## Core Mandate (RULE 0C)

**Before EVERY** code-modifying tool call (`str_replace`, `write_file`, `spawn_agents`),
execute this 25-item self-audit. If ANY check fails → **HALT**. Record the violation.
Do NOT proceed until the issue is resolved.

The sentinel must return a **PASS decision** before you are authorized to proceed.

## 25-Item COMPLIANCE SENTINEL Checklist

### RULE Compliance Checks (23 items)

```
[ ] RULE 0A: Verify every claim of completion is backed by running code
[ ] RULE 0B: Follow instructions literally — did not re-interpret
[ ] RULE 0C: This sentinel IS the gate — pre-action, not post-action
[ ] RULE 0D: Quota jail — checked failover before reporting failure
[ ] RULE 0E: 10-phase protocol — all phases completed
[ ] RULE 0F: Startup procedure executed at session start
[ ] RULE 0G: thinker-with-files-gemini spawned for THIS phase
[ ] RULE 0H: Anti-pattern instances recorded; repeats escalated
[ ] RULE 0H-A: Anti-pattern scan cited method + results (not mental assertion)
[ ] RULE 0I: No batch script without Gemini pre-analysis
[ ] RULE 0J: PRE-ACTION GATE assertion printed in response text
[ ] RULE 0K: Canonical docs loaded in PERMANENT order
[ ] RULE 0L: No test failure fix attempted without Gemini analysis
[ ] RULE 0M: ALL inference agents spawned CONCURRENTLY with Gemini
[ ] RULE 0Q: Last complex phase verified by Gemini + concurrent APIs
[ ] RULE 0Q-A: Inference claims cite specific model names + verdicts
[ ] RULE 0U: System reminders obeyed INSTANTLY on next turn
[ ] RULE 0V: code-reviewer-deepseek spawned BEFORE and AFTER code changes
[ ] RULE 0W: ALL applicable agents at 100% capacity
[ ] RULE 0X: State machine, Z3 verification, auto-telemetry tracked
[ ] RULE 0Y: Multi-agent judge consensus (≥2/3) + dual-ledger verified
[ ] RULE 0Z: thinker-gpt + basher + code-reviewer for THIS sub-task
[ ] RULE 0Z-A: Auto-fallback executed if thinker-gpt unavailable
```

### Recording Checks (2 items)

```
[ ] DirectMemory: Record this action BEFORE execution
[ ] ERROR_LOG: Record all errors BEFORE proceeding
```

## Sentinel Self-Recording (RULE 0T-A)

The sentinel gate MUST leave forensic footprints:
```python
audit_sentinel_run(result="AUTHORIZED" if passed else "DENIED", errors=[...])
if passed:
    audit_gate_passed(checks_passed=passed_count, checks_failed=failed_count)
```

## Enforcement

| Violation | Severity |
|-----------|:--------:|
| Taking action without sentinel pre-authorization | 🔴 CRITICAL |
| False PASS (mental assertion without actual checks) | 🔴 CRITICAL |
| HALT violation (proceeding despite failed check) | 🔴 CRITICAL |
| Sentinel run without self-recording to audit | 🔴 CRITICAL |

## Related Skills

- `azazael-pre-action-gate` — The 13-question assertion block (component of sentinel)
- `azazael-verifiable-truth` — Audit trail recording for sentinel decisions
- `azazael-compliance-orchestrator` — Programmatic compliance infrastructure
- `azazael-system-startup` — Activates compliance sentinel at session start
