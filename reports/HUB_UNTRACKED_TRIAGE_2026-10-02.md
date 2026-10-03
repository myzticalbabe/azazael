# Hub untracked `.py` triage — 2026-10-02

Follow-up to `HUB_TRIAGE_2026-10-02.md` §"Untracked code". That section listed
**335 untracked `.py`** in the hub working tree and warned explicitly:

> triage them **in the hub**, where their intent and runtime context live, then
> commit; bulk-importing unknown-provenance files into the canonical branch is
> the failure mode this session has been correcting all day.

This report is that triage. It splits the untracked `.py` into three verdicts —
**adopt**, **delete**, **hold** — and records the evidence for each.

## Method

For every untracked `.py` under `tests/`, the file was copied into this tree
and run against the code that is **already tracked here**. A file is adopted
only if *every* test in it passes; a file that fails or errors is held, because
the code it pins is itself still orphaned. `comm` against
`git ls-tree -r HEAD --name-only` separates genuine orphans from files this
branch simply has not received.

Tests were run with `-p no:hypothesispytest -p no:fugue_test` (the environment
lacks `hypothesis._native`; `fugue_test` auto-loads and dies on a missing
`pyarrow.lib`).

## Adopted — 37 test files (`c2b6…`, this session)

The 60 untracked test files were run as one set: **472 passed, 20 failed,
14 errored**. That majority pass because they exercise code that is *already
tracked here* — the only thing missing was the tests. The 37 wholly-green
files (417 passed, 6 skipped on their own) were committed:

`test_allocator_explore`, `test_benchmark_estimator_era`, `test_boruta_relevance`,
`test_chain_controller`, `test_data_distillation`, `test_debate_patch`,
`test_era_windows`, `test_false_zero_audit`, `test_fs_probe_backend`,
`test_gossip_trust_allowlist`, `test_jev_advisor`, `test_learning_rl_keys`,
`test_levy_mutation`, `test_loop_liveness`, `test_meta_escalation`,
`test_meta_evolution`, `test_meta_fallback`, `test_monitor_learning_flatness`,
`test_morphogenesis_opportunity`, `test_nerve_torch_import`,
`test_plateau_persistence`, `test_quarantine_execution_gate`,
`test_record_retry`, `test_replay_failed`, `test_servemesh_filter`,
`test_spawn_credit`, `test_spine_cycle_visibility`,
`test_spine_mesh_ledger_striping`, `test_tensor_trainer`,
`test_tensorgene_correlate`, `test_terminal_monitor_controls`,
`test_thought_contrast_pairing`, `test_threat_feed_freshness`, `test_v2_engines`,
`test_versioner_write_on_change`, `test_web_search`, `test_wiring_genome`.

Two of these pin code adopted earlier the same day: `test_monitor_learning_flatness`
pins `monitor_learning.evolution_flatness()` (commit `b8bdd6d2`) and
`test_chain_controller` pins the TERENCE jobs / skip-code logic.

## Deleted — unambiguous scratch (in the hub)

Removed from the hub working tree; none were tracked, so this was a real delete:

| path | kind |
|---|---|
| `logs/gate_tmp/` (8 `.py` + `.txt`) | gate debug scratch (`fix_*`, `diag_*`, `gatetest_scratch`) |
| `tools/_tmp_probe_scan.py`, `_tmp_proc_list.py`, `_tmp_stage_timing.py`, `_tmp_tombstone_roundtrip.py` | `_tmp_*` probes |
| `tmp_bench_ft.py` (root) | throwaway benchmark |

Deliberately **not** deleted (held, not scrap): `scripts/_*.py` (11
underscore-prefixed probes, incl. a 15 KB `_exmachina_freeze.py`) — private by
naming convention but substantive; and `.deps-jiter/` (a pip `--target`
dependency tree, not authored code).

## Held — 288 orphans

| bucket | count | note |
|---|---:|---|
| `src/CORE/WORMS/**` | 91 | worm modules never committed — adopt per-entry with their tests |
| `src/CORE/*` (non-WORMS) | 21 | `active_learn`, `backend_bandit`, `cascade`, `device`, `dpo_losses`, `dream_arena`, `embedding_backend`, `env_id`, `escalation_sft`, `eval_utils`, `forecast_baselines`, `gguf_census`, `graph_learn`, `inference/inference_memory`, `layerwise`, `league`, `qd_bridge`, `redteam`, `robust`, `ttcompute`, `cluster_route` |
| `scripts/` | 64 | real scripts + `_*` probes |
| `tools/` | 63 | incl. 34 `cain_*` figure/deliverable scripts |
| `tests/` | 23 | the 22 non-green test files + `_binary_deps.py` |
| `src/CODEX/` | 12 | `cain_*` / `inject_cain_*` 2026-09-30 CAIN passes |
| `src/ML`, `src/tests`, `src/AOA`, `dashboard/…`, `reports/…` | 21 | |

### The 22 non-green test files (with why each is held)

**Failed (8)** — the API they pin has drifted or the module is orphaned:

- `test_algorithm_lab`, `test_algorithm_observers` — lab runner / observer path mismatch
- `test_hyperopt` — `write_json` Path handling, objective promotion
- `test_mesh_html_view` — `test_generator_draws_every_learned_route`
- `test_morph_bypass` (2) — round-robin covers new genes
- `test_policy_advice` (4) — recommend/monitor-advice shape
- `test_predict_patch` (4) — featurize/refuse paths
- `test_replay_path` (3) — `RLTrainLoop.train_from_memory` has no `use_replay` kwarg

**Errored (14)** — collection/import failure; the subject module is orphaned:

`test_audit_wiring`, `test_budget_policy`, `test_ci_two_interpreter_gate`,
`test_clean_windows`, `test_code_evo_pilot`, `test_command_center`,
`test_exmachina_freeze`, `test_graph_shard_refresh`, `test_import_map`,
`test_mesh_transport_hardening`, `test_mesh_trusted_key_cli`,
`test_operator_scoring`, `test_ops_tools`, `test_vacuous_audit`.

`tests/_binary_deps.py` is a helper with no importer — held only for completeness.

## Recommendation

The remaining 288 are **orphaned code**, not orphaned housekeeping: 112 new
`src/CORE` modules with their tests form a coherent body that cannot be
bulk-added — 91 of them are worm modules whose import would alter
`discover_worms()` and the registry the suite depends on. Each cluster must be
adopted the same way as the rest of this session: copy one entry, compile, run
its suite, keep only if green. The 22 held tests are the to-do list for that
work — each names the module whose adoption it would validate.

The green 37 are the part that was safe to close without porting code, and they
are now tracked.
