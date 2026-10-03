# Orphan Adoption — scripts/, tools/, src/ extras (2026-10-02)

The hub tree (`C:\Users\clint\azazael`) held an untracked layer of work that the
live tree (`C:\Azazael\azazael`) never saw. This round reconciles the remaining
non-test orphans: `scripts/`, `tools/` and four `src/` clusters. Every adopted
file was `py_compile`-clean; every adopted test was run against the live tree
before it was committed. Anything that did not go green was **not** adopted.

## Method

For each untracked hub `.py` under `scripts/` and `tools/`, its basename was
`git grep`-ed across the tracked tree (code, docs, configs, skills). A file with
at least one tracked reference is wired into the project and was adopted; a file
with zero references is one-off session scratch and was quarantined. The test
side (below) additionally forced the adoption of modules that only an adopted
test names (`db_top`, `freeze_pool`, `triage_test_backlog`).

## Adopted — scripts/ (29 files)

Wired tooling recovered from the hub's untracked layer:

    _emoji_mood_probe.py   _exmachina_freeze.py     algorithm_lab_cycle.py
    audit_wiring.py        audit_wiring_allow.txt   budget_policy.py
    build_runtime_baseline.py  ci_two_interpreter_gate.py  clean_windows.py
    code_evo_pilot.py      db_top.py                 false_zero_audit.py
    freeze_pool.py         graph_shard_refresh.py    graphify_refresh.py
    hyperopt_cycle.py      import_map.py             mesh_gossip_cycle.py
    mutate.py              neural_loop.py            predict_patch_success.py
    repo_audit.py          run_evolution_n.py        run_full_suite.py
    tensor_gate_ab.py      train_fitness_oracle.py   triage_test_backlog.py
    verify_proteus.py      wire_or_cut_queue.py

`predict_patch_success.py` and `triage_test_backlog.py` were adopted purely
because an adopted test imports them.

## Adopted — tools/ (14 files)

    chain_ops.py   claim_guard.py   comfyui_flux_headless.py   command_center.py
    install_dual_abi.py   lesson_liveness.py   model_driver.py   prepare_guard.py
    process_benchmark.py   render_all_monitors.py   terence_watch.py
    vacuous_check_audit.py   verify_mesh_html.py   verify_python_stack.py

## Adopted — src/ extras (8 files + 3 tests)

Four clusters, all `py_compile`-clean:

    src/ML/dream.py            src/ML/evolve.py          src/ML/metacog.py
    src/CORE/WORMS/TOOLBELTZ.py
    src/AOA/refresh_oa_data.py src/AOA/test_arm_exports.py
    src/SCRIPTS/generate_tool_skills.py
    src/TOOLS/qwythos_proxy.py     (named by the azazael-tool-qwythos-proxy skill)
    src/tests/test_ml_dream.py  test_ml_evolve.py  test_ml_metacog.py   (14 passed)

`src/tests/` and `src/AOA/test_arm_exports.py` sit outside `testpaths = tests`,
so they are not collected by the default run; `test_arm_exports` passes (3) when
invoked with the stray plugins explicitly disabled.

## Adopted — hub orphan tests (13 modules, 152 passed / 8 skipped)

    test_audit_wiring.py        test_budget_policy.py        test_ci_two_interpreter_gate.py
    test_clean_windows.py       test_command_center.py       test_exmachina_freeze.py
    test_graph_shard_refresh.py test_import_map.py           test_ops_tools.py
    test_vacuous_audit.py       test_algorithm_observers.py  test_hyperopt.py
    test_predict_patch.py

`test_import_map` carries 8 skips: they need `state/test_backlog.json`, the
output of `scripts/repo_audit.py`, which was not regenerated here.

## Quarantined — tests (7 modules, never tracked in any commit)

These are test-first for features that exist in **neither** tree; the target
symbols are absent from the tracked code. They are WIP aspirational tests, not
orphaned tests of landed code, so adopting them would only add red:

    test_policy_advice.py    RLTrainLoop.recommend / DatabaseMonitorWorm._policy_advice
    test_replay_path.py      RLTrainLoop.train_from_memory(use_replay=...)
    test_morph_bypass.py     morph candidate-evidence / round-robin genes
    test_algorithm_lab.py    env-coupled: needs state/algorithm_lab/regression_report.json
    test_code_evo_pilot.py   env-coupled: its gate subprocess dies on hypothesis._native
    test_operator_scoring.py imports `azazael_operator_task`, an external home-dir harness
    test_mesh_transport_hardening.py   needs hypothesis._native

`git log --all -- <file>` returns nothing for the first five, confirming they
were never committed anywhere.

## Quarantined — scripts/ (36) and tools/ (48)

Zero tracked references; one-off session probes and CAIN authoring passes, left
on the hub and out of the canonical tree:

- **scripts/** — `_compages_study`, `_cranium_*`, `_db_rows`, `_db_shape`,
  `_evo_graph_build`, `_ex_timing`, `_glyph_widths`, `_morph_polymorphy_probe`,
  `analyze_evolution_runs`, `apply_runtime_baseline`, `audit_loop_budgets`,
  `bcc_open_tasks_join`, `bcc_part7_officers`, `chain_watchdog`,
  `check_runtime_baseline`, `compare_training`, `diagnose_fitness_gradient`,
  `diagnose_margin_gate`, `embedding_dashboard`, `env_drift_alarm`,
  `fix_poindexter_indent`, `inject_alert_drill`, `jev_advise`,
  `launch_live_windows`, `make_task_xml_utf16`, `neural_loop_monitor`,
  `observation_coverage`, `promotion_signals`, `prune_tensor_genome`,
  `rate_promotion`, `run_db_monitor`, `run_training_cycles`,
  `scrub_probe_telemetry`, `verify_oracle_parity`.
- **tools/** — the 34 `cain_*` authoring passes, `blender_session_20260930/*`,
  `flux_dash`, `hook_dispatch`, `learner_bridge`, `learner_bridge2`,
  `mesh_repaird`, `meta_reflect_run_20260930`, `mete_reflect_20260930`,
  `module_ownership`, `render_ouroboros`, `revert_selftest`,
  `vlp_reflect_20260930`.

## Verification

- `py_compile` over every copied `scripts/*.py` and `tools/*.py`: 0 failures.
- Adopted tests as a group: **152 passed, 8 skipped**.
- `src/tests/test_ml_*.py`: 14 passed. `src/AOA/test_arm_exports.py`: 3 passed.
- No adopted module changed the default suite's collection (testpaths = `tests`).
