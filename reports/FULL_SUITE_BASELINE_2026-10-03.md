# Full-suite baseline — 2026-10-03

Second complete `tests/` run on `migration/baseline-20261001`, taken after the
orphan-recovery and failure-closing work of the previous session. Supersedes
`FULL_SUITE_BASELINE_2026-10-02.md`.

## Result

| | |
|---|---|
| passed | **3518** |
| failed | **0** |
| errors | **0** |
| skipped | **72** |
| subtests passed | 59 |
| files run | 226 of 233 |
| wall | ~12 min (three slices: 115 s + 429 s + 108 s) |

Every test file that failed in the 2026-10-02 baseline now passes, and the two
previously-crashing files (`test_eve_unleashed`, `test_inference`) run to
completion.

Command per slice (`-p no:hypothesispytest`; the environment lacks
`hypothesis._native`, and `pytest.ini` already disables `fugue_test`, which
would otherwise abort on a missing `pyarrow.lib`):

```
python3.14t -m pytest $(cat slice_NN | tr '\n' ' ') -p no:hypothesispytest -q --tb=no
```

## Excluded — 7 files (each documented)

**Hang (do not complete in a 90 s per-file budget):**

| file | note |
|---|---|
| `tests/test_cluster_integration_p1.py` | >90 s |
| `tests/test_clusterworms_integration.py` | >90 s |
| `tests/test_clusterworms_unit.py` | >90 s |
| `tests/test_metacluster_orchestration.py` | >90 s |
| `tests/test_worm_regression.py` | >60 s |
| `tests/test_worm_regression_smoke.py` | matched by the same `test_worm_regression` filter |

**Collection error:**

| file | note |
|---|---|
| `tests/test_sprt_remeasurement.py` | `PermissionError: CRITICAL: Unauthorized` at import — the compliance gate refuses the collection itself |

These hangs are the reason `tools/run_suite_chunked.py` stalls: with 8 chunks it
reached chunk 2 and never finished, having inherited one hang per chunk. A
future baseline should drop the chunk count well below the hang count, or move
these files behind a marker.

## What changed since 2026-10-02

### The 26 failures — all closed

| test file | was | now |
|---|---|---|
| `test_aggregate_suite_gate.py` | 2 — isolation profile named absent files | pass |
| `test_config_and_breaker.py` | 1 — `TestPamsConfig::test_from_dict` | pass |
| `test_eve_unleashed.py` | 1 — torch C extensions | pass (torch loads) |
| `test_inference.py` | 1 — torch C extensions | pass |
| `test_inference_pool.py` | 1 | pass |
| `test_mandate_verification.py` | 1 | pass |
| `test_mesh_fabric_gaps.py` | 3 | pass |
| `test_mesh_wire_or_cut.py` | 1 | pass |
| `test_nature_integration_map.py` | 1 | pass |
| `test_optimizers_convergence.py` | 2 (errors) | pass |
| `test_sb3_agent.py` | 3 | pass |
| `test_spine_mesh.py` | 4 | pass |
| `test_startup_warm_wiring.py` | 1 | pass |
| `test_thought_corpus_integrity.py` | 4 | pass |
| `test_worm_execute_all_integration.py` | 2 | pass |

### `test_thought_corpus_integrity` — aggregate-only isolation defect

The 4 "typed writer" tests pass alone and, until this session, failed inside the
full slice with `IndexError: query_memories(...)[0]`. They assert on the newest
`thought_process` row read back through the shared `get_memory_store()`
singleton, while the writer path (`DirectMemory.record_thought`) opens the
module-level `DB_PATH`.

Root cause: `tests/test_session_mappings.py` rewrote the **module** global
`CORE.direct_memory.DB_PATH`, but its teardown captured the old value from
`DirectMemory.__dict__` — and `DB_PATH` is not a class attribute, so that lookup
was always `''` and the `if _orig_db:` guard never restored it. The module was
left pointing at a `tempfile.mktemp` path that teardown then deleted, so every
later test wrote to the temp DB through `DirectMemory` and read the real one
through `get_memory_store`. Fixed at the source: capture and restore the module
global unconditionally.

### `test_worm_smoke` — 6 learning worms had no `get_summary()`

`DataPipelineWorm`, `FeatureEngineer`, `GRPOTrainer`, `ModelVersioner`,
`PrioritizedReplayBuffer` and `SchemaAwareFeatureExtractor` were split out of
the `learning.py` monolith but never inherited `BaseWormMixin` and never defined
`get_summary()`. They are auto-registered (they carry `VERSION`) but return
`None` to the registry, so the definitive ecosystem health check failed 6/233.
Each now reports an explicit `{"success": True, "method": ..., "result": ...}`
envelope describing instance state, without side effects (no live pipeline run,
no record extraction).

## Regressions introduced by this session

**None.** All 3518 executed tests pass; the only red is the environment-gated
`test_sprt_remeasurement` collection, which is excluded by `pytest.ini` and
unchanged.

## How to reproduce

```bash
ls tests/test_*.py | grep -vE \
  'test_cluster_integration_p1|test_clusterworms_integration|test_clusterworms_unit|test_metacluster_orchestration|test_worm_regression|test_sprt_remeasurement' \
  > /tmp/run_tests.txt
split -n l/3 -d /tmp/run_tests.txt /tmp/slice_
for s in /tmp/slice_0*; do
  python3.14t -m pytest $(cat $s | tr '\n' ' ') -p no:hypothesispytest -q --tb=no
done
```
