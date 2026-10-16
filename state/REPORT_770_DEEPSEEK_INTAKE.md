# REPORT — Engram #770 DEEPSEEK TRAINING-INTAKE (wire harvest into trainers)

Model ID: **DeepSeek V4.1 Flash Fast**
`git rev-parse --show-toplevel`: `C:/Azazael/azazael`
Branch `migration/baseline-20261001` · lane commits `07fcb0bd`, `a1ef6189`, `940ec23f`, `8959a791` (2026-10-15).

## P0 — #755 confirmed landed, without redoing

Evidence read, not assumed: `state/ORPHAN_TRIAGE_2026-10-15.md` (classes APP-ENTRY 233 /
SCRIPT-DIR 3 / DYNAMIC 87 / TEST-ONLY 15 / TEST-INERT 8 / DEAD 1 / MISSING 0),
`state/orphan_scan_2026-10-15.json`, lane commits `d41ad1db` (false-DEAD fix) and
`abd79287` (refuse a no-verdict aggregate run). Brief twin present. Nothing re-run.

## The gap, measured rather than inherited

"1/33 algos applied, zero trainer intake" is a claim about a tree, and #635 falsified a
sibling of it by re-measuring. `tools/training_intake_audit.py` re-measures: per technique,
does any trainer edge exist, and which of four predicates proves it.

**Result (this tree).** General technique→trainer intake edge: **PRESENT**.
Per-EP: **1 APPLIED** (EP412) · **4 PARTIAL** · **28 ACCEPT-GAP** — every ACCEPT-GAP carries
its missing precondition in `state/training_intake_audit.json`. Table:
`state/TRAINING_INTAKE_AUDIT.md`.

TWO gaps were real, and only one of them was "wiring":

1. **No trainer was pointed at the stream.** `technique-link` rows existed — every live hook
   call writes one — and zero trainer filtered on that source (predicate P3). So the harvest's
   measured outcomes reached monitors, fitness text and ledgers, and no learning signal.
2. **The row's verdict was only half-visible.** `technique_runtime.record_link()` declares
   `severity="info" if ok else "warning"` and puts the outcome in `data["ok"]`, while the
   trainers' reward model `learning_rl._compute_reward` reads a top-level `severity` plus the
   refinement field `data["success"]`. Severity landed; the refinement did not, so the
   `log`/`ignore` bonus a known-good outcome earns (+0.1) never fired, and any producer
   declaring `error` lost the remediation bonus/penalty entirely.

## What was built

| piece | file | role |
|---|---|---|
| adapter | `src/CORE/training_intake.py:143 build_training_records()` | preserves the producer's severity (re-labelling would overrule the hook author and change the incentive), adds `data["success"]`, skips + COUNTS a row whose `ok` is absent or not a real bool, writes nothing |
| track | `scripts/track_registry.py:65` `"INTAKE"` | a rotation track with a reward event, so the existing scheduler picks it up |
| runner | `scripts/run_training_orchestrator.py:370 run_intake_cycle()` | drives `RLTrainLoop.train_from_memory(records=...)` — a frozen pool, the real trainer, warm-started, persisted |
| instrument | `tools/training_intake_audit.py` | the per-EP measurement + the general-edge headline |

`RLTrainLoop` was chosen because it is one of the four trainers #770 names, it already has a
`records=` entry point, and its fallback state key is `source:severity` — which is what makes
the verdicts differentiable at all.

## Proof (executed, not asserted)

* Adapter/track tests: **15 passed** on both interpreters (`tests/test_training_intake_records.py`);
  fixtures are transcribed from `record_link()` and the reward table, not invented beside them.
* End-to-end through the production CLI on a **copy** of the live store:
  `AZAZAEL_MEMORY_DIR=<copy> python scripts/run_training_orchestrator.py --algo INTAKE`
  → `Records used: 500`, `Eval reward: 15.88`, `q_table_size 74`, `warm_started True`, one
  `intake_training_orchestrated` artifact, **exit 0**.
* Same run on the **production interpreter** `C:/Azazael/.venvs/py315t/Scripts/python.exe`
  (3.15.0rc3 free-threading, `sys._is_gil_enabled()` False — the interpreter this repo's
  registry names as production): `Records used: 500`, `Eval reward: 17.5233`, 12 hooks,
  **exit 0**; 79 focused tests green there too. The edge is proven to EXECUTE in the
  production runtime, not merely to import in it.
* Starved path (fresh empty store): `STATUS: INTAKE TRAINING SKIPPED/FAILED`, note
  `no MEASURED technique outcomes (0 rows seen, 0 unmeasured)`, **exit 1**, **no artifact row**.
* **Live store untouched**: 0 `intake_training_orchestrated` rows after the whole session
  (`C:\Users\clint\.azazael\memory_store.db`).
* Covering suites on both interpreters: 129 + 88 tests green
  (intake/track_monitor/algorithm_lab/learning_closure/grpo/local_memory/rl_keys/replay/sb3/
  thought_contrast/worm_smoke/worm_registry).
* Gates at commit time: canon drift OK, ratchet **2670 findings unchanged**, mesh ledger fresh
  **368**; both lane commits landed through the full six-check hook (no `--no-verify`).

## Full-suite result and the red inventory (both interpreters)

`python -m pytest tests/ -q` on **GIL 3.14.7**: `16 failed, 4639 passed, 49 skipped` in 44m24s.
On **py315t** (3.15.0rc3, GIL off): `20 failed, 4634 passed, 51 skipped` in 57m30s. Every red was
triaged; none touches this item's modules, and the evidence is recorded rather than asserted.

| red cluster | count | disposition | proof |
|---|---|---|---|
| stale anti-pattern baseline | 2 (1 per interpreter) | **FIXED** in-slice, `8d6fb28f` | baseline recorded `files_scanned` 708 vs live 705 — the three shims #755 retired. Re-record diffed against the committed file: findings **2670 unchanged**, category counts identical, **zero** files with an increase. `test_anti_pattern_gate` 18 passed, and the `test_preflight_all` cascade (it executes that file as a control artifact) 86 passed |
| `test_gguf_quantize_refusal` | 6 (both) | owned by the #755 lane, already recorded | row **755-A2**: a forward-written spec for a capability that never existed (`GGUFAnalyzer.convert` is absent from tracked history; `git log -S "def find_quantizer"` empty). Owner: the lane that last touched `universal_converter.py` (`7df2d06e`); spec side `ffd13e34` |
| `test_inference::test_sklearn_inference`, `test_memorybus*`, `test_mesh_transport_hardening`, `test_cd5_docker_benchmark`, `test_neural_pipeline_cutting_edge`, `test_cutting_edge_production_fixes` | 10 (GIL) / 8 (py315t) | **ordering/isolation-dependent**, not broken features — and already a documented set | `test_sklearn_inference` passes alone on py315t (`1 passed` in 2.92s); re-run together the whole cluster gives 46 passed, 1 failed. This rediscovers independently what `state/ORDERING_QUARANTINE_2026-10-15.md` (the #712 Phase 3-B quarantine) already proved by same-invocation exoneration, and extends it: `test_mesh_transport_hardening` and `test_neural_pipeline_cutting_edge` belong on that list too |
| `test_worm_smoke::test_every_worm_has_get_summary` | 1 (both) | real, small, unattributed | `PlasticityEngineWorm: instantiation failed: TIMEOUT (>10s)` — one worm's constructor exceeds the smoke test's bound. Unrelated to this item; needs its own owner |

## Errors hit (attested, per phase — including the zeroes)

* **PHASE A (measure)** — none. The instrument ran clean first try after its host source was
  repointed from the batch06 map (which covers 0 of the 33) to `SOTA_FULL_REVIEW_2026-10-09.md`
  section 1, whose `wiring action` column names each EP's host.
* **PHASE B (adapter)** — one, caught by the test I wrote for it: an unreachable store was
  reported only to the failure ledger, so an unreadable store returned an empty pool with
  `records == []` and **no diagnosis** — indistinguishable from "nothing was measured".
  Fixed by naming `read_error` in the result as well (`store_error` covers open-failure).
  Row 770-E1.
* **PHASE C (edge)** — one: the first version of the phase-C test asserted against a fake
  store, which cannot intercept the orchestrator's own artifact write. Rewritten to assert
  against the session's redirected real store, which is strictly stronger (it proves the
  artifact row's shape end to end). Row 770-E2.
* **PHASE D (verify)** — one, and it was mine: the free-threaded interpreter I first picked
  (`Python314/python3.14t.exe`) lacks `hypothesis._native`, so it cannot collect at all, and I
  concluded the pair on this host was `venv-314t` + `python-std.exe`. Incomplete — the
  PRODUCTION interpreter is `C:/Azazael/.venvs/py315t` and the registry header says so. Both
  the 3.14 pair and a py315t probe are now recorded; row 770-E3 was corrected by row 770-E3b
  rather than rewritten. `scripts/ci_two_interpreter_gate.py` also cannot resolve roles here
  (no `src/CORE/python_env.py` in this tree) and correctly reports an environment error
  (exit 2) instead of a verdict.

## Limitations, stated rather than smoothed

* The **live stream is currently single-class**: all 500 fetched `technique-link` rows are
  successes (`ok_rate 1.0`), so the failure half of the pool is proven by tests that transcribe
  `record_link`, not by live traffic. The edge is correct on both classes; live data does not
  yet exercise one.
* The store clamps a query to 500 rows (`MAX_QUERY_LIMIT`), so an intake run sees the newest
  500 outcomes. Pagination is available if a longer history is ever wanted.
* 28 of 33 techniques remain per-EP ACCEPT-GAPs: their own host must reach a trainer, which is
  a per-host slice (H-1's shape), not the shared channel this item asked for.
* The full-suite reds include a cluster that only fails inside the full run (nine on GIL, seven on
  py315t — all pass when re-run together). That is a test-isolation defect, not a code defect, and
  it is the first thing #784's campaign should attack rather than a curiosity.
