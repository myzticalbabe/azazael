# Orphan adoption — mesh cluster, and hub reconciliation — 2026-10-02

Two follow-ups from the full-suite baseline, both closed on
`migration/baseline-20261001`.

## 1. Hub working tree reconciled with the canonical branch

The hub (`C:/Users/clint/azazael`) held a **second, uncommitted layer** of work
that the live tree (`C:/Azazael/azazael`) never had. It was folded in with a
three-way merge — hub HEAD (`1e30c2c1`) as base, live tree as *ours*, hub
working tree as *theirs* — so neither side was dropped.

Adopted from the hub layer:

| area | change |
|---|---|
| standalone harnesses | pytest entry points (`run_standalone_script`) for `test_algorithm_coverage`, `test_cloud_tab_error_handling`, `test_provider_failover`, `test_secrets_manager_thread_safety`, `test_observability` |
| free-threading | `sysconfig.get_config_var("Py_GIL_DISABLED")` guard for the `mygrad`→`numba` path in `test_optimizers_convergence`, `autodiff_skills_check`, `benchmark_autodiff_modes` |
| AOA | the probe now persists the write-back it measures (`test_aoa_routing_telemetry`) |
| wiring | `test_startup_warm_wiring` registry-size fix + the "validation must not run on the caller" test |
| evolution | `test_evolution_gates` additions |
| PROTEUS | `_apply_explore_env` (`PROTEUS_EXPLORE` override) in `proteus_hooks.py` |
| paths | GOSP path `…/gossamer-oxford-parser`, staging path for `vermillion_lightfury` |
| docs/logs | `MANDATES`, `SOP`, `SESSION_STARTUP`, `SYSTEM_INSTRUCTIONS`, `NEURAL_MESH_*`, `ERROR_LOG`, `MIGRATION_LEDGER`, `docker/Dockerfile.ubuntu` |

Kept whole (live tree supersedes the hub variant): `src/AOA/core/router.py`,
`src/AOA/core/event_bus.py`, and the `MORPH_KNOWN_GENES` evolution path.

The hub's `scripts/live_monitor.py` deletion was **not** adopted — the file is
the live wallboard, and an archive copy already exists at
`archive/live-monitors-20261002/`. Six archived `graphify-out/<date>` snapshots
were dropped.

The hub was then fast-forwarded to the canonical commit; its tracked working
tree is clean and the two HEAD trees are byte-identical. The pre-reconcile
working tree is preserved in `git stash` on the hub, and 50 untracked duplicates
of files the live tree now tracks were removed (49 identical, 1 superseded).

**Commit:** `d95b1d3a`.

## 2. Mesh orphan cluster adopted

Four `src/CORE` / script modules that existed only in the hub were adopted with
their tests, per-entry, until green:

| file | why |
|---|---|
| `src/CORE/env_id.py` | the **ONE** canonical env identity: five tracked call sites (`mesh`, `envmesh`, `xenomorph`, `spine`, `spine_registry`) had drifted copies. Imported by tracked code, absent here. |
| `src/CORE/embedding_backend.py` | real 768-dim semantic embeddings with disk cache and fail-open chain; `engram`/`code_audit` import it. |
| `scripts/mesh_trusted_key.py` | the allowlist **writer** the reader (`spine_registry._load_trusted_keys`) needs; hand-editing the JSON fails closed. |
| `tools/gephi_mesh_pipeline.py` | the mesh HTML generator's route-edge collectors. |
| `tests/test_mesh_trusted_key_cli.py`, `tests/test_mesh_html_view.py` | the held tests for the two above. |

One latent native crash was fixed in the process: `engram._ensure_backend`
imported `faiss` inside `try/except`, but its GIL-ABI wheel faults at C level
under a free-threaded build — a segfault no `try/except` can catch. Adopting
`embedding_backend` made the semantic path reachable and exposed it. Guarded by
runtime (`Py_GIL_DISABLED`), the same pattern used for `onnxruntime`/`bcrypt`.

### Effect on the baseline failures

Cluster failures went **9 → 2** (the two remaining are unrelated
wire-or-cut/contract-coverage checks):

| test | before | after |
|---|---|---|
| `test_mesh_fabric_gaps` | 3 failed | pass |
| `test_spine_mesh` | 4 failed | pass (63) |
| `test_mesh_wire_or_cut` | 1 failed | 1 failed (unrelated) |
| `test_nature_integration_map` | 1 failed | 1 failed (unrelated) |
| newly adopted | — | 14 passed, 5 skipped |

`test_mesh_transport_hardening` was **not** adopted: it imports `hypothesis`,
whose `_native` extension is absent from this environment — it cannot be green
here.
