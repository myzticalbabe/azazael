---
name: azazael-improve
description: Structured improvement pass grounded in session observations. Use after completing a task, before claiming done, before handoff, or when asked what can be improved. Surfaces concrete suggestions with file and line evidence.
metadata:
  category: process
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-10-05
  adapted_from: alleneubank improve skill (session-grounded [IMP-N] format)
---

# Improve — Session-Grounded Improvement Pass

Run after completing a task, before claiming done, before handoff, or when asked what can be improved. Every suggestion must be grounded in something observed THIS session — no generic advice.

## When to use

- After completing a significant chunk of work.
- Before claiming done or generating a handoff.
- When the user asks "what can be improved?" or "knowing what you know now...".
- Before closing a converge loop iteration as green.

## Procedure

1. **Gather context**: files changed, commands run, errors encountered, tests written/failing, measurements taken, patterns established. Re-read the session's own evidence (tool outputs, manifests like `state/converge_315.json`, PMB records), not memory of intent.
2. **Analyze each dimension**; skip dimensions with nothing grounded to say:
   - Correctness: failing tests, wrong results, misdiagnoses corrected mid-session.
   - Flakiness: order-dependent, load-dependent, timing-sensitive behavior seen.
   - Measurement: numbers reported without baselines, truncated outputs, unverified claims.
   - Process: repeated manual steps that deserve a script, gate, or skill.
   - Debt: shortcuts taken (quarantines, skips, TODOs) that need tracked follow-ups.
   - Docs/memory: findings that belong in PMB, skills, or code comments but were not recorded.
3. **Structure each suggestion**:

```
[IMP-N] effort/gate: summary
  Observation: what was seen (file:line, error text, test gap, measurement)
  Suggestion: concrete change
  Grounded: yes/no
```

4. **Sort by impact**, highest first. Effort scale: trivial (seconds), small (minutes), medium (needs a decision first).
5. **Present as an actionable list.** Fix trivial items inline. Log medium items as PMB decisions/follow-ups instead of expanding scope.

## Azazael-specific rules

- Failing or quarantined tests: every entry needs the nodeid, the measured failure text, and the triage verdict (pre-existing / environmental / 3.15-specific / upstream-suspect).
- Never weaken a gate to make red green (no widened thresholds, no deleted assertions without a recorded reason).
- Quarantine entries must carry a re-probe condition, not just a reason.
- Performance claims need before/after numbers from the same machine and interpreter.
