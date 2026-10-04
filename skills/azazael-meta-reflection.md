---
name: azazael-meta-reflection
description: Meta-reflection protocol - distill generalized instructions from past trials (success AND failure), validate before storing, retrieve into future work. Use after any multi-step task, failed verification, or production incident.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: false
---

# Azazael Meta-Reflection - Learning From Trials, Not Just Logging Them

> Research basis: MetaReflection (offline RL from trial reflections into
> validated semantic memory), Reflexion (verbal RL over episodic critique
> memory), metacognition monitoring→control loops. Local rule: **an
> instruction earns its place by validation, never by eloquence.**

## The Protocol (5 steps, in order)

### 1. MONITOR — collect trajectories, not conclusions
Gather the raw material: what was attempted, what happened, what changed.
Sources in this repo: `state/meta_evolution/lineage.jsonl` (verdicts),
evolution memory rows (margins, trajectories), test results, production
log deltas. Record successes AND failures — successes carry the
counterfactuals failures hide.

### 2. REFLECT — generalize exactly once removed
Turn instances into a rule that would have changed a *class* of decisions,
not a diary entry about one event. Test: if the instruction only makes
sense with the original incident attached, it is not general enough —
rewrite or drop. One instruction per reflection; no batch dumps.

### 3. VALIDATE — dedicated step, never skipped
A candidate instruction must pass ALL of:
- **Non-empty and material** (says something falsifiable, not a platitude).
- **Non-duplicate** (normalized match against `state/meta_reflections.jsonl`).
- **Evidence-linked** (names the trajectories/rows that produced it).
- **Bounded scope** (states where it does NOT apply, if anywhere).
Rejects are logged with the reason. A validation that cannot fail is theater.

### 4. STORE — append-only ledger + memory row
Validated instructions append to `state/meta_reflections.jsonl`
(schema: `azazael.meta-reflection.v1`) and record a memory row. Cap the
ledger (default keep 200); prune by lowest retrieval count, never by age
alone. Never rewrite history: superseded instructions are marked, not edited.

### 5. RETRIEVE — surface where decisions happen
An unread instruction is write-only optimism. Current surfaces: the RL
monitor "Meta-Reflections" card (latest + count) and `scripts/meta_reflect.py
--list`. Future: inject top-relevance instructions into proposal prompts.

## Anti-Patterns (all observed in production, all with incident tags)

- **Polluting shared state from probes.** Unit tests calling cycle helpers
  wrote tmp-path rows into the live log, mimicking a snapshot anomaly.
  Rule: probes run under quarantine env (`AZAZAEL_CYCLE_LOG=/dev/null`
  pattern); conftest enforces it repo-wide.
- **Manual runs breaking streak counters.** An observation-only DRY run
  reset a live BLOCKED streak. Rule: counters skip non-attempts (DRY),
  break only on genuine outcome changes; regression-test the skip.
- **Over-generalization from sparse signal.** One quiet hour is not a trend;
  one failure is not a class. Rule: minimum evidence thresholds before a
  reflection (default: 3+ supporting trajectories).
- **Downgrade rationalization.** "Working as designed" must name the design
  doc AND the mechanism, or it is an excuse. Every downgrade carries both.
- **Validation theater.** A check that cannot fail (always-green linter on
  generated code, tier lists without teeth) reports confidence, not truth.

## Session Records

- 2026-09-26: protocol distilled from a full forensic session (4 self-caught
  defects incl. log pollution, streak pollution, test-math errors ×3,
  premature downgrades corrected on re-evidence).
