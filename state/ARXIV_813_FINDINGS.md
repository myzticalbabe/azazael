# Engram #813 — DEEPSEEK ARXIV-HARVEST: findings + SHAs

> File twin of Engram task #813 (lane: DeepSeek). Model ID string: GLM 5.3
> Flash (Freebuff agent) per the brief's worker routing. `git rev-parse
> --show-toplevel`: `C:/Azazael/azazael`. Lane branch: `deepseek-engram-813`
> (created against a sibling lane's sweep+reset incidents; see below).

## P0 — verified, no redo

- `#798 wire` — `_blend_intake_pool` at `scripts/evolution_cycle.py:2052`
  + 2 call sites, committed in HEAD (not re-done).
- `probe` — `tools/probe_intake_fitness_798.py` present.
- `map seam` — `step.map_advice` at `src/CORE/workflow.py:628` (EP237).
- Remainder opened: none of R1/R2/R3/F1/F2 existed (grep-verified) — all
  built here.

## Baseline, measured FIRST (before any change)

- Router: collinear batch, seed 7, switch mode → counts
  `[0,0,0,64,0,64,0,0]`, 2/8 experts, cumulative entropy **0.3333**
  (= log(2)/log(8) floor), **Gini 0.75**, min/extreme ratio 0/512.
- Pool: 500/500 rows severity `info`, `ok_rate=1.0` → **zero measured
  negatives** in the live stream; none rescueable by F1 today.

## Items, one variable each, with acceptance

| Item | Acceptance | Measured |
|---|---|---|
| Instr (A) | same gini/min_max/cumulative vocabulary on every path; switch byte-identical | landed; positive control: even load reads exactly 0.0 |
| R1 (B) Loss-Free bias, 2408.15664 | entropy up + all experts utilised (cumulative) + suite green | recovery at forward **#2148**: cumulative entropy 0.3333→**0.844**→(keeps rising, 0.876 after +200); 8/8 experts route real tokens; per-batch floor stays 2, named. Gate VALUES never distorted (asserted vs switch twin) |
| R2 (C) BIP quota, 2502.15451 | per batch (assignment side-steps the pinning argument) | exact quotas **[16]×8 in ONE batch**: 8/8 used, entropy **1.0**, **Gini 0.0**; remainder rotates; varied batches full; deterministic |
| R3 (D) LPR reading, 2506.21328 + SimBal 2505.22323/25|06.14038 | binding quotas across drift + diversity stats separate the fixtures | quotas hold across drifting batches; `orthogonality_loss` **0.985** (collinear, prototypes align) vs **0.81** (varied); `specialization_variance` reported; None+reason until measured |
| F1 (E) NAT, 2402.11651 | pool carries measured negatives + adapter tests pin marking + live INTAKE exit 0 | mechanism pinned (producer-declared warning/error rows become marked negatives, counted `n_nat_declared`); **live-pool gap recorded: 0 negatives today** — stated in a committed test, not hidden |
| F2 (F) Likra, 2503.14391 | near-miss segment marked + counted, no silent rewrite of verdicts | `data["near_miss"]` exclusive marking + `n_near_miss`; **no automatic weighting** — this module's own #382 lesson (no shaping until per-worm hook identity) is the boundary, stated in the commit and tests |

## LIVE RUN

`python scripts/run_training_orchestrator.py --algo INTAKE` → **exit 0**:
500 records, eval reward 15.3933, 12 hooks, `ok_rate=1.0`, `unmeasured=0`,
model v2, 5155ms. (Pre-#813 measured 15.62 — the pool shape changed by the
adapter's additive marks; both runs exit 0 on the same measured stream.)

## MEASURED STRUCTURAL FINDINGS

1. A fixed ±2.0 bias authority cannot flip ANY of 96 seeded fixed gates
   (all spreads > 4.0): the Loss-Free clamp is now the batch's own
   measured selection-score spread. Same shape as the existing
   `bias_clamp_exhausted` vocabulary.
2. Sibling-lane concurrency: Kilo #814's index-wide staging swept this
   lane's slice-A source into its own commit and its `git reset HEAD~1`
   discarded a clean DeepSeek commit in flight. Lane moved to
   `deepseek-engram-813` + per-commit ownership verification.

## SHAs (branch deepseek-engram-813)

- b6b5c712 — slice A (route_mode plumbing + gini/min_max/cumulative
  instrumentation + byte-identical switch contract).
- 791edecd — slice B (R1 Loss-Free bias).
- 027d4e99 — slice C (R2 BIP quota assignment).
- 125cfeda — slice D (R3 LPR + SimBal diversity; BULK declared via
  COMMIT_GATE_MAX_LINES=200 at 160 lines, justified in-message).
- 4fe079b7 — slice E (F1 NAT marking).
- c99fc2aa — slice F (F2 Likra near-miss marking) DISCARDED by a sibling-lane
  `git reset HEAD~1`; re-landed content-identical as **fed48de1** (verified
  20-test intake battery again).
- a6409591 — state/twin + bake lane.

## Checks

- #813 battery: 14 tests (both interpreters: GIL 40 passed incl. intake
  sets; ft 40 passed with `-p` plugin-autoload disabled — the ft side's
  installed pyarrow 25.0.1 wheel is GIL-ABI and fails `import`, a
  pre-existing environment gap that also breaks the
  `ci_two_interpreter_gate` (its `CORE.python_env` import seam is absent
  from this tree by the gate's own docstring). Manual dual-ABI run was
  used instead, honestly reported.
- Sibling batteries green with each slice: test_cutting_edge_production_fixes
  + test_neural_pipeline_cutting_edge + test_metamorphic_relations (55),
  intake batteries (27).
- Ratchet: 2670 findings / 705 files, no regressions (checked per commit
  and re-checked at end). Mesh ledger fresh (369 declarations, statuses
  unchanged). Bake merge dry-run: BASE=7469 ACCEPTED=3 MERGED=7472
  **DROPPED=0**, exit 0.

## Honest gaps

- The FULL 970-file suite sweep was not run in this session; the affected
  set (cutting-edge, metamorphic, pipeline, intake, pool-wire) ran green
  per slice and the repo's own gates ran on every commit.
- F2's emphasis is marking-only by design (see above); the trainer-side
  application is the next step and its absence is asserted, not hidden.
- Live pool has zero negatives/near-misses today; both live-shape twins
  pin that reading rather than letting a green mechanism test claim live
  coverage.
