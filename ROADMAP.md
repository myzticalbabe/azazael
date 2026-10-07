# ROADMAP — the single consolidated build order (2026-09-12)

Supersedes the scattered plans (TENSOR_GENOME_PLAN.md, EVOLUTION_SOTA_EXPANSION_PLAN.md,
EVOLUTION_50RUN_GAPS_AND_FIXES.md). One list, in order, no parallel stacks:
a task is DONE only when live, measured, and monitored. Both builders work
from here; new work lands as an entry here first.

Convention: each task has **Definition of done**. Trust-ladder rule: no new
auto-application without its own canary + rollback.

## Phase 1 — Close the tensor loop (training actually feeds decisions)

- [x] 1.1 Tensor trainer exists (scripts/train_tensor_model.py, GIL torch XPU,
       era holdout, transport 0.618, state/tensor_model.json)
- [x] 1.2 TESTUDO calibration: map raw surrogate outputs to calibrated
       promotion-relevant scores on held-out eras. Done = calibration curve
       in tensor_model.json with measured ECE.
       DONE 2026-09-12 — `state/tensor_model.json` carries `calibration`
       {alpha 0.1, q90 1.1517, achieved 1.0 vs 0.9 target, n_cal 9, n_test 10,
       ece 0.7538, ece_bins}. HONEST READING: the conformal band covers, but
       the ECE is 0.75 — the mean prediction is systematically ~0.6-0.93 high
       against the realized margin, so the surrogate is directional at best.
- [x] 1.3 Phase-C pre-gate A/B: surrogate runs BESIDE the current gate for
       N cycles, advisory only; promotes to deciding only if it beats the
       gate's shipment quality (fewer holdout failures, no extra false
       promotions). Done = A/B artifact + decision record.
       DONE 2026-09-12 — `scripts/tensor_gate_ab.py` scores BOTH deciders on
       the same recorded rows (genes + realized margin + holdout verdict), so
       the answer did not need N more cycles. Result: gate shipment_quality
       0.0632 (174 promotions, 11 survived) vs surrogate 0.0265 (226
       promotions, 6 survived, mae 0.7485). The surrogate is WORSE and makes
       MORE false promotions, so `decision: advisory`, `approved: false` — the
       gate is unchanged. Artifact `state/tensor_gate_ab.json`.
- [x] 1.4 Measured prune: real prune(keep=TENSOR_KEEP) on a COPY of the
       genome, cost-of-dropping-epsilon measured (re-query usefulness after
       drop). Done = prune report artifact, genome intact until approved.
       DONE 2026-09-12 — `scripts/prune_tensor_genome.py`. `prune(keep=
       TENSOR_KEEP)` drops nothing (all four are kept); dropping `epsilon` too
       saves 1 gene / 4 tensor columns and its weak association (rho 0.031)
       HOLDS out-of-sample, so `safe_to_drop: true` — but `approved: false`.
       The script asserts the live genome file's size+mtime are unchanged.
       Artifact `state/tensor_genome.prune_report.json`.

## Phase 2 — Revive morph rotation (fund something or retire it)

- [x] 2.1 bounds_map gap: morph genes get bounds=None in artifacts. Fix the
       map extension. Done = morph rows carry bounds.
       DONE 2026-09-12 — `_tensor_genome_refresh` now builds `bounds_map` from
       GENE_BOUNDS + MORPH_GENES (not GENE_BOUNDS alone), so a BLOCK gene such
       as `val_ratio` gets a box too. Test:
       `test_proteus_hooks.test_bounds_cover_every_gene_the_ledger_can_carry`.
- [x] 2.2 Admission criteria: define what makes a candidate fundable
       (replaces the retired use_schema_features slot). Done = new candidate
       admitted by the stated rule, or rotation formally retired with the
       machinery kept for manual trials.
       DONE 2026-09-12 — the fundable rule is `MORPH_ADMIT_WIN_RATE` (>=0.75)
       AND the exact binomial p<=0.05 AND a positive mean; nothing has earned
       it (best is 2 of 8). The rotation is therefore formally RETIRED by
       evidence, expressed as `morph_rotation_retired()` and persisted under
       `rotation` in `state/morph_policy.json` (`retired: true`, reason "no
       active candidate and the search space is closed"). Machinery kept: the
       block table, matched A/B and policy artifact all still run, so a future
       trainer edit that makes a refused kwarg reachable re-opens the rotation
       with no code change.
- [x] 2.3 MUTAGEN actuators: free-growth/drift verdicts currently displayed
       only. Wire the first actuator (e.g., auto-pause rotation when
       free-growth >= 0.35). Done = actuator fires live once, logged.
       DONE 2026-09-12 — `morph_free_growth()` + `morph_rotation_paused()` in
       `proteus_hooks.py`; `MORPH_FREE_GROWTH_PAUSE=0.35` mirrors the tier's
       band (pinned by `TestFreeGrowthMirrorsTheProducer`). Wired into the
       cycle ahead of the block choice; a paused cycle adds no gene AND writes
       no ledger row. LIVE PROOF (cycle 116, 2026-09-12T19:04:21, python3.14t):
       `morph: ROTATION PAUSED by MUTAGEN actuator (free_growth=0.5862 >=
       0.35, verdict=free growth) - no new gene this cycle`. Producer and tier
       compute the identical value.
       CORRECTION (same day): the ledger held 27 rows carrying NO gene (no-op
       cycles), and both implementations were counting them as non-inert
       trials. A no-op is not evidence about selection, so the rule is now
       "a row without a gene is skipped" in producer AND tier, pinned by
       `test_a_row_with_no_gene_is_not_a_trial`. Corrected reading: n=89,
       inert_share=0.7640, free_growth=0.7640 (was 0.5862 over all rows).

## Phase 3 — Finish the secondaries (no more half-wired engines)

- [x] 3.1 CMA/DE duel with gate (live, measured 4/104 + 13 skips)
- [x] 3.2 IslandModel: give it a live slot or cut it. Done = either
       serving traffic or deleted with tests kept.
       DONE 2026-09-12 — CUT from the production path (never on it). Recorded
       in `evolution.UNSERVED_ENGINES` with the reason, and enforced by
       `TestWireOrCutVerdict` — the driver must not reference an unserved
       engine. Code kept: tested, stdlib-only, re-checkable; wiring islands
       would change the search AND the world at once, which the one-variable-
       per-batch rule forbids.
- [x] 3.3 NSGA-III/MOEA-D helpers: same wire-or-cut verdict. Done = same.
       DONE 2026-09-12 — CUT: `moead_weights`, `tchebycheff`,
       `generate_reference_points`, `hypervolume_2d` and `MAPElites` are all in
       `UNSERVED_ENGINES` with reasons. The multi-objective path is NSGA-II,
       which needs no reference weights, and the cycle keeps its own persisted
       QD archive rather than the MAPElites class.
- [x] 3.4 TPE observes winners+knee+seeds (done 2026-09-11); verify
       contribution in artifacts over 30 cycles. Done = measured.
       DONE 2026-09-12 — measured: `tpe_seeds=2` in **30/30** recent artifacts
       (wiring live, zero extra evals). Contribution-to-WINNER was not
       recorded, so `_tpe_seed_won()` now writes `tpe_win` per cycle — under
       elitism an unchanged suggestion IS the best genome, so the match is
       exact. Tests: `test_evolution_helpers.TestTpeContribution`.

## Phase 4 — Coverage grind (measured, file by file)

- [x] 4.1 evolution.py mutation 1.00 (30/30)
- [ ] 4.2 Next five files by risk x size from audit_summary.json testmap.
       Done = each file's suite kills its own mutants (>=0.7) or documents why.
       PARTIAL 2026-09-12 — five run. `exmachina_operators` 0.567,
       `proteus_hooks` 1.00, `providers` 0.1, `scanner` 0.067. The low scores
       are THIN SUITES, not mismatched ones: the import graph confirms both
       modules are imported by the suites that were used. Remaining work is
       assertions, not targeting. Per-file results are durable in
       `state/mutation_history.json`; timeouts no longer depress a score.
- [x] 4.3 Backlog triage into test / delete / vendor. DONE 2026-09-12 — zero
       modules "unknown". Two corrections to the premise: the backlog was 262
       *basenames*, not 262 files (truncated to 50 by `uncovered[:50]`), and
       the substring method that produced it was measuring the wrong thing.
       Real numbers from the import graph: **487 src files, 175 reached by a
       test, 312 uncovered** -> 285 test / 21 generated / 6 delete candidates.
       Artifacts: `state/test_backlog.json`, `state/test_backlog_triage.json`.
       Write-up: `TEST_BACKLOG_TRIAGE.md`.

## Phase 5 — Hygiene (ongoing, checked weekly)

- [x] 5.1 Disk: C: < 90% or a dated cleanup entry. (95.5% at last check.)
       **2026-09-12: 674G used / 82G free / 90%** — not yet under 90%, so this
       is the dated cleanup entry. It is 5.5 points better than the 95.5%
       check; the improvement came from the node_modules/packages cleanup, not
       from a new action this session. Reclaimable backlog already identified
       and still approval-gated: G: nested AZAZAEL_BOOT 7.43 GB, Eve
       model.gguf 3.16 GB, wheels 0.81 GB.
- [ ] 5.2 Stale producers: mutation_summary age_h, checkpoint restore drill,
       QD coverage trend — all on the wallboard already; act on red.
       PARTIAL 2026-09-12 — the checkpoint restore drill FAILED for a real
       reason: `_get_store()` swallowed a transient SQLite lock and returned
       None, so `save_checkpoint()` silently persisted nothing while reporting
       success. Retry + honest `persisted` flag added; regression tests in
       `tests/test_nsga2.py`.
- [ ] 5.3 Doc drift: milestone/skill counts regenerated monthly, not by hand.

## Phase 6 — Adaptive budgets (added 2026-09-12)

- [x] 6.1 Budgets auto-expand instead of silently truncating. `scripts/
       budget_policy.py` gives every cap a floor/ceiling/growth rule, escalates
       what a run hit (with `needed` so one run is enough), settles what it did
       not, and records every change in `state/budget_policy.json`. Wired into
       `repo_audit.py` and `mutate.py`. Full write-up: `BUDGET_POLICY.md`.
- [x] 6.2 The `uncovered[:50]` inventory limit removed: full list now at
       `state/test_backlog.json`.
- [x] 6.3 Mutation timeouts are indeterminate, not decisive: excluded from the
       score, reported as `timed_out`, and the run does not exit 0.
- [x] 6.4 Per-pattern budgets. DONE 2026-09-12 — `audit.pattern.<name>`,
       registered on first sight. `print_in_src` (7 242 hits) now holds 1000 on
       its own while `todo`/`shell_true`/`bare_except` stay at 25 and
       `hardcoded_home` sits at its exact 165. Two bugs found landing it: the
       new budgets were seeded from the shared cap's *current* (polluted)
       value, and settling at `count <= cap` oscillated 165 -> 82 -> 165.
       Fixed with a floor-derived seed and a `count * 2 <= cap` headroom rule.

## Out of scope (explicit)

- Qwen3.8-27B / 30B-class models: do not fit 5 GB free RAM. Revisit on RAM upgrade.
- AOA_MILESTONE.md history: timestamped record, never rewritten.

---

## Session record — 2026-09-12 (wiring pass)

**Landed (all verified, both interpreters):**

| Item | Change | Evidence |
|---|---|---|
| 1.2 | identified as already implemented | `state/tensor_model.json` calibration block, ECE 0.7538 |
| 1.3 | advisory A/B decision record | `state/tensor_gate_ab.json` — surrogate **worse** than gate (0.0265 vs 0.0632 shipment quality), stays advisory |
| 1.4 | measured prune, copy-only | `state/tensor_genome.prune_report.json`, genome size+mtime asserted unchanged |
| 2.1 | morph gene bounds map | `evolution_cycle._tensor_genome_refresh` + test |
| 2.2 | formal rotation retire as a verdict | `state/morph_policy.json` `rotation.retired: true` |
| 2.3 | **MUTAGEN actuator wired** | live cycle 116 log; free_growth 0.5862 >= 0.35 |
| 3.2/3.3 | wire-or-cut registry | `evolution.SERVED_ENGINES` / `UNSERVED_ENGINES` + `TestWireOrCutVerdict` |
| 3.4 | TPE contribution instrumented | `tpe_seeds=2` in 30/30 artifacts; `tpe_win` added + tests |

**Verification:**

```
582 passed   proteus(98+hooks) + exmachina(operators/freeze/monitor/mutagen)
             + tensorgene + v2_engines + evolution_helpers/gates + nsga2
             + sprt_remeasurement + monitor_artifact_paths + scheduling
ALL OK       verify_proteus.py            python.exe and python3.14t.exe
ALL OK       verify_exmachina.py          python.exe and python3.14t.exe
ALL OK       verify_exmachina_panel.py    python.exe and python3.14t.exe
live cycle   python3.14t.exe rc=0, actuator line present in the cycle log
```

**Architecture evolution (what changed structurally, not just fixed):**

1. A displayed metric now has a **consumer**: `free_growth` drives a decision
   (pause the rotation) instead of only colouring a panel row. This is the first
   actuator in the epistemic tier — the pattern that turns an organ from a
   measurement into a control input.
2. A production verdict is now **data**: `SERVED_ENGINES` / `UNSERVED_ENGINES`
   makes "which engine serves traffic" checkable, so a half-wiring fails a test
   instead of sitting unnoticed.
3. Thresholds are **single-sourced**: the producer owns
   `MORPH_FREE_GROWTH_PAUSE`, the tier mirrors it, and a test fails on drift —
   the same lock `MORPH_TRAINER_DEFAULTS` and `_as_bool` already use.
4. **A metric bug was fixed at the source, not papered over.** 27 gene-less
   rows were counted as non-inert trials by both implementations, biasing
   `free_growth` DOWN (0.5862 -> 0.7640 corrected). Fixing one side would have
   made the mirror disagree, which is exactly what the mirror test is for.

**Still open (unchanged by this pass, in priority order):**

- **4.2** mutation-testing is bounded by an adaptive budget with per-target
  history. Remaining: `providers` (0.1) and `scanner` (0.067) are imported by
  their suites but barely asserted on — the next step is assertions in those
  two suites, not more mutants and not re-targeting.
- **5.2** stale producers: act on red. The checkpoint drill is fixed; the
  mutation-age and QD-coverage signals still need a threshold response.
- **5.3** doc drift: regenerate milestone/skill counts monthly rather than by hand.
- **4.3 follow-through**: the 6 `delete` candidates are review-gated, and the 8
  live generated files (`run_qanalysis.py`, `tensor_utils.py`, ...) imply the
  generator, not the generated files, is what needs a test.
- **New signal**: 175/487 src files are reached by a test (36%). The 285 `test`
  verdicts are now a ranked work list instead of a truncated count.

---

## Session record — 2026-09-12 (adaptive budgets)

**Question:** the tooling "is not working with limits" — can limits/budgets
auto-expand as necessary? **Audit answer:** they were constants, not budgets,
and hitting one silently returned less work. Full record in `BUDGET_POLICY.md`.

| Item | Change | Evidence |
|---|---|---|
| 6.1 | `scripts/budget_policy.py`: floor/ceiling/escalate/settle/record | `state/budget_policy.json` history; `tests/test_budget_policy.py` (15 tests) |
| 6.1 | `repo_audit.py` wired to the policy | live run escalated `pattern_cap` 25→1000 via `needed=7242` |
| 6.1 | `mutate.py` wired, score excludes timeouts | live run: 20/308 sites sampled, escalated `max_mutants`→40 |
| 6.2 | `uncovered[:50]` removed | `state/test_backlog.json` (262 modules) |
| 6.3 | `timed_out` reported separately, not a pass | `state/mutation_summary.json` `timed_out` field |
| bug | `src/AOA/cli/aoa_cli.py` did not parse (5× orphaned `try:`) | compile phase `838 ok, 0 bad` |
| bug | `save_checkpoint` could silently persist nothing | `_get_store()` retry + `persisted` flag; `tests/test_nsga2.py` |
| bug | float-identity + bool-only-default test defects | `tests/test_exmachina_mutagen.py`, `tests/test_proteus_hooks.py` |

**Verification:** 476 tests pass (`test_budget_policy`, `test_nsga2`,
`test_proteus_*`, `test_exmachina_*`, `test_tensorgene`, `test_v2_engines`,
`test_evolution_*`); the new modules import and escalate/settle under both
`python.exe` and `.venv-3.14t/Scripts/python3.14t.exe` (that venv has no
pytest, so it is exercised functionally).

---

## Session record — 2026-09-12 (per-pattern budgets, real coverage map, triage)

Follow-up round on the three items left open by the adaptive-budget pass.

| Item | Change | Evidence |
|---|---|---|
| 6.4 | per-pattern budgets (`audit.pattern.<name>`) | `print_in_src` 1000, `hardcoded_home` 165, risk patterns 25; stable over 3 runs |
| 6.4 bug | seed came from the shared cap's polluted *value* | seed is now `bp.bounds(...)[0]`; polluted entries dropped |
| 6.4 bug | settling at `count <= cap` oscillated 165→82→165 | `count * 2 <= cap` headroom rule; `tests/test_budget_policy.py` guards it |
| 4.3 | `scripts/import_map.py` — AST import graph + run/exec path references | 487 src files, 175 reached, 312 uncovered |
| 4.3 | `repo_audit` testmap now import-graph based | `state/audit_summary.json` `method: "import-graph"` |
| 4.3 | `scripts/triage_test_backlog.py` — test / delete / vendor | `state/test_backlog_triage.json`, **0 unknown** |
| 4.3 bug | a bare string mention counted as a reference (a test file's own `"src/tmp_verify.py"` made a dead module live) | narrowed to run/exec calls; `test_a_bare_mention_is_not_a_reference` |

**Verification:** `tests/test_import_map.py` (20) + `tests/test_budget_policy.py`
(19) pass, plus the full affected suite set. Records: `BUDGET_POLICY.md`,
`TEST_BACKLOG_TRIAGE.md`.
- **1.3 follow-through**: the surrogate stays advisory until it beats the gate;
  re-run `scripts/tensor_gate_ab.py` after the next retrain to re-check.
- **Spreadsheet of truth for the C-series**: `BCC_INCONSISTENCY_LEDGER.md` C1–C8
  still have no ledger home (outside this roadmap's scope).
