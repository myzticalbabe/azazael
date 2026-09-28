# STACK Track Design — Contextual Routing + Stacking over Training Tracks

Date: 2026-09-28. Status: DESIGN (no code). Forensic + literature basis below.
Related: `research/CROSS_DOMAIN.md` (CD1 join keys, CD3 spans), `scripts/meta_director.py`
(Thompson routing), `scripts/run_training_orchestrator.py` (18 tracks),
`src/CORE/WORMS/expansion/spawn_credit.py` (decision_id joins).

## 1. Problem

Five real absorption edges exist (DPO<-SB3, DPO<-thoughts, DREAMTUNE->dream,
evolution->RL params, all->director ledger). Everything else is routing:
the Thompson director picks ONE track per 5-minute slot globally. Per-worm
routing ("which policy governs *this* worm?") is learned by nothing. SB3
tracks share no weights (impossible across algorithms), OFFLINE/WORMGA/GRPO
read common substrate, meta reads code. Selection caps us at the best
single track; the union of track knowledge is unreachable.

## 2. Proposal: STACK track (contextual router + stacking meta-learner)

A 19th track that does not train policies at all. It trains *routing*:

- **L0 (existing, untouched):** all 18 tracks run as today.
- **L1 (new):** a contextual model mapping
  `(worm features, track predictions, track uncertainties)` -> track weights.
- **Artifact:** versioned weight table `state/stack_weights.json`
  `{worm_class: {track: weight}}` + calibration report, consumed by the
  director as priors (not overrides) and by ALLPAR as agent weights.
- **Training set (exists today):** per-track per-worm outcomes joined on
  `decision_id` (`spawn_credit.read_outcome_decisions`, limit 20000) plus
  per-worm-type statistics where ids are absent. No new data collection.
- **Failure default:** uniform weights (current behavior). A STACK that
  cannot beat uniform on holdout eras changes nothing downstream.

## 3. Novel modifications (2025-2026 literature, mapped to this system)

1. **Contextual LinUCB router (LinUCB 2010; AAAI-2026 myopic regret;
   EXP4-LoRA 2026).** Replace slot-global Thompson picks with per-context
   picks: context = worm features (nature, cluster, history), arms = tracks.
   EXP4-LoRA shows per-query routing with only binary correctness feedback
   beats EXP3 by 4+ points with zero offline router training — our
   success/failure outcomes are exactly that feedback. Keeps the
   cooldown/epsilon machinery; changes the decision from per-slot to
   per-decision.
2. **Surrogate-aware routing, decoupled (CABS-D 2026).** The tensor
   surrogate predicts margin cheaply; use it as a *surrogate signal* alongside
   bandit feedback, combined by adaptive expert aggregation (Hedge-style).
   Theory gives best-of-both-worlds: never worse than bandit-only, better
   when the surrogate is informative. Concretely: tensor margin + track
   rewards -> two experts -> mixed routing policy. This is also the
   principled use of the newly scheduled tensor track.
3. **Uncertainty-aware meta-learner (DML 2025).** L1 inputs = per-track
   predictions + uncertainties + worm features (their 23-dim meta-feature
   pattern). Per-track uncertainty proxies available now: SB3 eval_std,
   GRPO group std, dreamtune fitness spread, evolution margin. Three-way
   output per context: best single track / weighted hybrid / abstain.
4. **Attribution-informed meta-features (GeoAttribStack 2026, XStacking
   2025).** Where tracks expose feature attributions, feed them to L1 as
   context (not post-hoc diagnostics). Cheap start: per-track per-worm-class
   win rates (already in the ledger) as the attribution profile.
5. **Redundancy pruning (CoRe-Stack+ 2026).** Before stacking, measure
   inter-track prediction correlation (CKA-style; Pearson first). Tracks
   that duplicate each other add variance, not signal — prune or merge.
   Phase 0 below does this measurement; it may delete tracks, which is a
   feature (fewer tracks = less contention + faster cadence).
6. **Calibrated abstention (conformal prediction, GeoAttribStack 2026).**
   Adaptive intervals on the routing decision; abstain (fall back to
   director default) when the interval is wider than the best margin.
   Finite-sample coverage beats hand-tuned thresholds.
7. **GDCB framing (2026, unifying theory).** Our arm (director pick) +
   scaler (evolved hyperparams) + gate (promotion/SPRT) is already a Gated
   Decoupled Compositional Bandit. The theorem that matters: a calibrated
   scaler makes the bandit approximately stationary, and historical data
   under any prior policy warm-starts safely. Justifies training STACK on
   the existing ledger without importance correction.

Explicitly NOT adopted: full joint/differentiable co-training (depth 4) —
requires shared encoders across incompatible algorithms (PPO/DQN/SAC have
no common weight space); negative-transfer risk exceeds the evidence.
Revisit only if Phase 0 shows compatible track pairs.

## 4. Phased plan

- **Phase 0 — measurement (no behavior change).** Inter-track prediction
  correlation matrix from the existing outcome tap; redundancy report
  naming prune/merge candidates; per-track uncertainty audit (which
  tracks report usable spreads). Exit: report + prune list.
- **Phase 1 — contextual router (primary candidate).** LinUCB per
  worm-context alongside Thompson; shadow mode first (log picks, don't
  route), then 10% traffic, then full on win. Exit: beats Thompson on
  holdout eras with calibration intact.
- **Phase 2 — STACK track.** L1 meta-learner on the decision_id join
  dataset; weight artifact versioned; director consumes as priors;
  conformal abstention gate. Exit: beats uniform + Thompson on holdout.
- **Phase 3 — surrogate coupling (CABS-D).** Tensor margin as second
  expert; adaptive mixing. Exit: best-of-both-worlds holds on live data.

Each phase: holdout by ERA (never by row — cf. tensor model's era-split
discipline), champion/challenger promotion through the existing evolution
gates, automatic rollback on regression. A phase that cannot beat its
baseline changes nothing downstream (uniform-weight default).

## 5. Risks

- **Confident wrong router** (worse than no router): mitigated by shadow
  mode, holdout eras, conformal abstention, and the uniform default.
- **Negative transfer across worm classes**: mitigated by per-class
  weights (never one global blend) + redundancy pruning first.
- **Stale weights steering live traffic**: weight artifact carries a
  48h freshness guard (same pattern as `tuned_creativity.json`); stale =
  uniform.
- **Compute**: L1 is tabular (ridge/logistic on ~20k rows), seconds per
  run, hourly cadence like other tracks. No GPU, no LLM calls.

## 6. References

- LinUCB (Li et al. 2010); NeuralUCB (Zhou et al. 2020); Neural-sigma2-LinUCB
  (Bui et al. 2025, Inf. Fusion).
- EXP4-LoRA contextual routing (2026); CABS-D surrogate bandits (2026);
  GDCB theory (Miroshnichenko 2026).
- DML adaptive XGBoost-neural ensembles (2025); GeoAttribStack (2026);
  XStacking explanations-as-features (Inf. Fusion 2025); CoRe-Stack+
  (2026); SPIO sequential planning (ACL 2026).
- OTel sampling doctrine (head/tail composition); MLflow orchestration
  guide (DAGs, artifact passing, asset triggering 2026).
