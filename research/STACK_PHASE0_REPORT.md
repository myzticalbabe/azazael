# STACK Phase 0 Report — Redundancy + Feasibility (measurement only)

Date: 2026-09-28. Tool: `scripts/stack_phase0.py` (read-only).
Basis: 15-42 recent runs per track (all 18 measurable), 5,000 outcome rows.

## 1. Redundancy: nothing to prune

Max pairwise trajectory correlation |r| = 0.725 (DREAMTUNE x WORMGA);
109 pairs below 0.3. No pair reaches the 0.9 prune bar. Tracks are
genuinely diverse, with complementary pairs (PPO x A2C r=-0.66,
A2C x MaskablePPO r=-0.65) — anti-correlation is stacking upside, not
overlap. Verdict: keep all 18; diversity is the asset.

## 2. Uncertainty: thin

Only GRPO / DPO / OFFLINE report spreads (coverage 1.0); the other 15
tracks report point rewards only. An uncertainty-aware meta-learner
would fly blind on 5/6 of the pool. Two cures, cheapest first: (a)
rolling std of recent rewards computed in L1 (free, no instrumentation);
(b) emit eval_std from SB3 runs (the value exists in-process today —
PPO logs `226.4 ± 121.3` — but the stored row drops the spread).

## 3. Class routing on win rates: INFEASIBLE today

15 nature families have healthy volume (n=10-50 per 5k window), but
win_rate = 1.000 in all 500 sampled outcomes, zero failures anywhere.
A router keyed on success has nothing to separate — either the fleet
is genuinely near-perfect (then routing adds nothing) or success is
recorded loosely (a 500/500 clean sheet across security worms strains
credulity and deserves its own forensic). Either way, win-rate L1 is
vacuous until the outcome signal carries variance.

## 4. The feasible L1 signal: regime-conditioned track rewards

Track rewards DO vary (PPO 226±121, WORMGA 0.99, OFFLINE holdout
margins). What is missing is the *context* each reward was earned in:
track runs do not stamp the regime (data volume, DB size, active
families, wall-clock era). Without context features, no router —
LinUCB, Thompson, or neural — can learn "which track, when".

## 5. Phase 1 prerequisites (instruments, not models)

1. Stamp every track run with regime context (volume, DB MB, top
   active families, slot). Small change in `run_training_orchestrator`,
   biggest enabler on this page.
2. Emit SB3 eval spreads into stored rows (one-line change at the
   record site; PPO already logs it).
3. Forensic the 100%-success outcome tap (credibility of the base
   signal everything else learns from).

Then: contextual LinUCB on (regime -> track reward), shadow mode,
holdout by era. The decision_id join dataset already exists for the
per-decision level once contexts are stamped.
