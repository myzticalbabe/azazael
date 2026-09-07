# Training Day Trend Report — 2026-09-07

Live analysis of the 5-minute learning loop against the hot Windows DB
(`C:\Users\clint\.azazael\memory_store.db`). Windows local time ≈ UTC−4.

## Strategy vs outcome (last 6h)

### Dream quality by active strategy

| strategy    | n    | avg quality |
|-------------|------|-------------|
| (no steer)  | 595  | 0.745       |
| aggressive  |  56  | 0.666       |
| conservative|  26  | 0.423       |

### Policy application rate by active strategy

| strategy    | applied | rate |
|-------------|---------|------|
| aggressive  |  7/7    | 1.00 |
| (no steer)  | 47/51   | 0.92 |
| conservative|  2/13   | 0.15 |

**Reading:** aggressive is the only steered strategy with a perfect application
rate, and it out-produces conservative dreams (0.666 vs 0.423). Conservative —
with creativity tuned to 0.15 — produces tepid dreams that mostly fail the
0.5 adoption bar, which is by design after the churn fix. The evidence-driven
metacog channel (success-rate mining) is what pushes the system to aggressive.

## Steering activity (last 24h)

- steering events: 17 (every 5-min cycle fires)
- switches (24h): 10 — evidence-driven, no blind churn since the 0.5 adoption gate
- live steering distribution: conservative 13, aggressive 7

Recent switches (all `should_adapt=1`):

```
18:13  -> aggressive     18:33  -> batched       19:56  -> aggressive (evidence, conf 0.784)
18:18  -> staged         18:38  -> adaptive
18:23  -> staged         18:43  -> conservative
18:28  -> aggressive     18:48  -> conservative
```

The 19:56 switch is the first *evidence-driven* adaptation: metacog fed 44
cluster outcomes (n=38, success 94.7%) and recommended aggressive at
confidence 0.784 — above the 0.5 adoption bar.

## Evolution

- non-flat trajectory confirmed: gen 0 → 3 improving 11.23 → 11.29 → 11.38,
  then converged (patience). Reward is now action-dependent, so fitness has a
  gradient.
- latest best fitness seen by the long-watch: 13.32 (still improving).

## Caveats

- `clusterwormz_execute_complete` events are stale (last: 2026-07-30) — the
  aggressive recommendation rests on old cluster data until a fresh cluster
  run happens. Dream quality + policy application are measured on live data
  and favor aggressive.
- "no steer" rows predate the steering fix or fall outside steered windows;
  they are the historical baseline, not a strategy choice.

## Watch

`logs/training_day_watch.csv` (WSL) — long-horizon watcher sampling every
15 min for 24 samples, started 20:17 UTC. Columns: active_strategy,
state_age_min, steering_24h, switches_24h, dreams_1h, avg_quality_1h,
policy_applied_rate, mc_evidence_n, mc_success_rate, evolution_flat,
evolution_best_fitness. First sample: aggressive, quality 0.729, evolution
not flat (13.32).