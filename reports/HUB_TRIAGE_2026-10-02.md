# Hub backlog triage — 2026-10-02

Scope: the hub (`C:\Users\clint\azazael`, @ `1e30c2c1`) working tree —
**54 modified tracked, 658 untracked, 7 deleted** — classified into *validated*
vs *not validated*, and the validation performed for each adopted entry.

Discipline applied: an entry is adopted only if it **compiles and its tests (or
runner) go green**; a change that breaks its own suite is not adopted, however
plausible it looks. (Two entries failed this bar this session: the raw
`proteus_hooks` candidate removal and the AOA router cluster.)

## Adopted (committed on `migration/baseline-20261001`)

| entry | commit | evidence |
|---|---|---|
| `expansion/allocation.py`, `evolution.py`, `dreaming.py` | `df2ecebf` | 298 passed; the `dreaming` fixes clear 3 pre-existing `test_learning_closure` failures |
| `CORE/PamsRecorder.py` + `test_pams_recorder.py` | `38dbbd87` | 12 passed, clearing a pre-existing singleton failure |
| `CORE/freethreading.py`, `secrets_manager.py`, `audit_trail.py`, `azazael_ctl.py` | `38dbbd87` | compile + import + secrets smoke (21) + observability runner (156) |
| `scripts/evolution_cycle.py` (EV-4…EV-7) | `7bb1922e` | 238 passed; replay `any_promotable=TRUE` |
| `proteus_hooks.py` rotation/registry split | `ed2bfc25` | 270 passed |
| `tools/evolution_progress.py`, `evolution_backfill.py`, `fitness_arm_liveness.py` | `7bb1922e` | relied on by the above |

Net: **4 pre-existing test failures cleared** (3 dreaming + 1 PamsRecorder).

## Rejected / not adopted (with reason)

| entry | reason |
|---|---|
| `src/AOA/core/router.py`, `event_bus.py`, `test_benchmark_workflow.py` | the hub's own `CrossArmRouter` lacks `capability_index`, which its updated test asserts — **incomplete**, would leave the failure in place. Reverted. |
| `proteus_hooks.py` as the hub wrote it | broke 17 tests; only the registry-split form (above) was adopted. |

## Modified code still awaiting per-entry validation

Each needs its own test/run evidence before adoption:

- `scripts/chain_controller.py` (+89), `scripts/monitor_learning.py` (+41),
  `src/SCRIPTS/monitor_learning.py` (duplicate of the former),
  `scripts/gosp_*` (+2…4 each), `scripts/rani_llm_test.py`,
  `scripts/train_gosp_curative.py`
- `src/ORCHESTRATION/HYDRA.py` (+24),
  `src/ORCHESTRATION/ml_platforms/install_manager.py` (+85)
- `src/CODEX/SESSION_TEMPLATE/generators/unified_generator.py` (+30)
- `tools/run_suite_chunked.py` (+35)
- `scripts/live_monitor.py` (deletion) — **no action**: HEAD already moved it to
  `archive/live-monitors-20261002/` (`3db131db`); the hub's deletion is a stale echo.

## Untracked code (335 `.py`) — inventory

| bucket | count | note |
|---|---|---|
| `src/CORE/**` | 112 | mostly worm/expansion modules not yet `git add`ed |
| `tests/` | 65 | new test files never committed |
| `scripts/` | 64 | one-off + real scripts |
| `tools/cain_*` | 34 | CAIN figure/deliverable scripts |
| `tools/other` | 30 | real tools |
| `src/CODEX` | 12 | |
| `src/AOA` | 5 | incl. `delegation_spec.py`, `contracts.py` (needed by the rejected router work) |
| `tools/scratch(_*)` | 4 | `_tmp_*` scratch |
| `src/ML`, `src/tests`, `src/TOOLS`, `src/SCRIPTS`, root | 9 | |

Untracked non-code: `state/` 98, `logs/` 79, `reports/` 20, `dashboard/` 19,
`skills/` 8, plus loose root docs.

These are predominantly **the hub's own project work** (deliverables, dashboards,
new tests), not branch-owned code. Recommendation: triage them **in the hub**,
where their intent and runtime context live, then commit; bulk-importing 335
unknown-provenance files into the canonical branch is the failure mode this
session has been correcting all day.

## The general rule this exercise produced

A change found in a working tree is a **claim**, not a result. Before it is
believed: does it compile, and does its suite stay green — proven per entry.
Two of the hub's most confident-looking entries (the raw morph candidate
removal, the AOA router) fail that bar. `genome_seed`'s "root cause" was a
third, in prose.
