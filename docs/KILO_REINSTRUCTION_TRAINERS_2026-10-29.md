# KILO Reinstruction: Trainers Are Yours — Morph, Don't Rebuild (2026-10-29)

## Status on your return
The outer loop you left open is now closed and landed:
- `src/CORE/morphed_trainers.py` — `propose()` (NSGA-II over SB3 numeric
  knobs, Pareto front), `promote()` (registers `morphed_<algo>_g<gen>`),
  `resolve_morphed()` / `list_morphed()`. Store: `morphed_registry.json`.
- `SB3Agent` resolves morphed names → base algo + merged Pareto kwargs;
  worm_id preserves lineage. Unknown morphed names fall back safely.
- `tests/test_morphed_trainers.py` — 3 tests, green with your 16
  (`test_sb3_trainers_v2` 16 + 3 = 19 passed).

Live proof: `morphed_ppo_g1` (lr 3.14e-4, gamma 0.9903, clip 0.2528)
resolved to PPO with kwargs merged.

## Your orders
1. **Run generation 1 for real.** `propose()` for PPO/SAC/DQN at
   generations≥8, pop≥24. Train each Pareto winner at small timesteps;
   keep winners by reward-proxy AND wall-clock. Promote only trained
   winners — proxy proposals are candidates, not champions.
2. **Build the three gap trainers** (TRAINER_BUILD_DECISION): offline/
   constrained, NSGA2-wired multi-objective, hierarchical on a real task.
   Each with the F2 contract (worm_id, error-dict train, GIL fallback,
   tests) or it does not land.
3. **No zoo imports.** One trainer earned through the factory beats ten
   vendored. Your SB3 finish proved the pattern — repeat it.
4. **Evaluation suite = your unfinished tasks.** Generation 0 is judged
   against exactly what you left. Close your own loop.

## Standing rules (unchanged)
- Evidence gate: sha+quote+raw+2keys per block on `lane.kilo.status`.
- F2 contract on every trainer. StagedScanner + paradigm gates green.
- Morph first (compounds), build selectively (costs), transmogrify hot
  paths only (measured by sweep), transsubstantiate at promotion.

## Reference
- `docs/TRAINER_BUILD_DECISION_2026-10-29.md` (why morph-first)
- `docs/LOOP_CLOSURE_AUDIT_2026-10-29.md` (what closes, the four moves,
  six algo styles)
- `docs/MULTILINGUAL_SHARD_REVIEW_2026-10-29.md` (polyglot scope)
