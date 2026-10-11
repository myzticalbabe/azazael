# Retired trainers & loops — Wave 1 (2026-10-11)

User order: stop using old trainers and loops; retire all old; new shall be
made as needed. Full-retirement scope confirmed with the user (including the
wired stack — that follows in later waves).

## This wave: dead driver scripts (zero importers, zero schedules, zero tests)

Each file below had no production/scheduled caller and no test importer
(verified 2026-10-11 by repo-wide caller search; only `train_fleet.py`,
`train_today.py`, `evolve_loop.py` appeared in
`tests/test_entry_point_smoke.py`, whose ENTRY_POINTS list was trimmed in
the same commit). Moved with `git mv`, so history follows the files.

- scripts/train_fleet.py — fleet GRPO scoring driver (manual-only)
- scripts/train_today.py — full-day mesh training run (manual)
- scripts/evolve_loop.py — route-preference genome loop (manual)
- scripts/run_training_cycles.py — DREAM→EVOLVE→METACOG→AUDIT catch-up (no callers)
- scripts/scenario_a_full_pipeline.py — GRPO→ONNX→deploy demo
- scripts/scenario_b_compressed_pipeline.py — SB3→ONNX→quant demo
- scripts/scenario_c_distillation_pipeline.py — RL teacher→SB3 student demo
- scripts/scenario_d_nas_pipeline.py — evolutionary NAS→GRPO→ONNX demo
- scripts/train_thought_reward.py — hand-rolled SGD thought-reward model (no class)
- tools/learner_bridge.py — tabular-Q control/treatment harness
- tools/learner_bridge2.py — 3-arm extension (tabular/replay/SB3-DQN)
- scripts/watch_training_day.py — long-horizon CSV watcher
- scripts/analyze_evolution_runs.py — batch analyser for run_evolution_n output
- scripts/plot_evolution_rewards.py — fitness-landscape plotter
- scripts/compare_training.py — side-by-side SB3 view (read-only reporter)
- scripts/gosp_learner_train.py — GOSP RecursiveLearner trainer (WSL)
- scripts/gosp_learner_divergence.py — native-intel divergence probes (WSL)
- scripts/sync_training_rows.py — WSL→Windows row merge tool (one-shot)
- scripts/run_evolution_n.py — evolution stat-sample runner
- scripts/train_gosp_curative.py — GOSP training pipeline (WSL manual)

## Deliberately NOT in this wave

- Chain-job drivers (`run_training_orchestrator.py`, `evolution_cycle.py`,
  `dream/metacog/nightshift/tensor` cycles): chain frozen until refactor.
- Audit instruments (`benchmark_evolution.py`): read-only, tested.
- Wired trainers (RL/SB3/GRPO/scheduling/evolution/dreaming) and dormant
  classes: Waves 2–3 with test updates and fail-open shims.
- `train_fitness_oracle.py`: sole caller (`evolution_cycle.py`) is chain-frozen.

## Restore

`git log --follow -- <file>` traces each file back; `git mv` it home or
`git revert` the wave commit. Chain-controller string refs to retired names:
none (verified) — except frozen-job strings, which were never touched.
