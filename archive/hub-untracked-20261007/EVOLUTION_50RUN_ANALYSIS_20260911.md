# EVOLUTION 50-RUN ANALYSIS — 2026-09-11

Evidence: 50 back-to-back invocations of the production entrypoint (`scripts/evolution_cycle.py`, free-threaded interpreter) via `scripts/run_evolution_n.py`, analysed from the pipeline's own timestamped stdout (`logs/evolution_runs/`) and the `evolution_result` rows it writes to the live store. Regenerate with `python scripts/analyze_evolution_runs.py`.

> Hand-written analysis (gaps, fixes, regressions) is NOT kept here: this
> file is regenerated on every analysis run. See
> `EVOLUTION_50RUN_GAPS_AND_FIXES.md` for the findings that accompany it.

## 1. Headline numbers

| Signal | Value |
|---|---|
| Cycles analysed | 50 |
| Matched `evolution_result` rows | 50 |
| Fatal cycles | 0 |
| Median cycle wall time | 20.0s |
| Promotions (this batch) | 0 |
| `beats_baseline` rate | 1.0 |
| SPRT decisions | {'promote': 50} |
| Blocked by gate | {'holdout gate': 4} |
| Generations used | {6: 49, 10: 1} |
| Converged early (<15 gens) | 50 |
| Flat best-trajectory cycles | 42 |
| Margin (median / min / max) | 3.3012 / 2.9125 / 3.385 |
| SPRT LLR (median / max) | 1222.4099 / 12421.69 |
| SPRT sigma (median / min) | 0.1121 / 0.035645 |
| Baseline drift inside batch | 1.9712 ((19.0588, 18.04)) |
| Pool eras in batch | 28 {1: 3, 2: 1, 3: 1, 5: 1, 6: 7, 7: 4, 8: 1, 10: 1, 12: 1, 15: 1, 16: 1, 23: 1, 35: 1, 37: 1, 39: 1, 58: 1, 64: 1} |
| Second-arm outcomes | {'skipped': 50} |
| QD coverage (final) | 0.75 |

## 2. Where the wall-clock goes

| Stage | Total s | Share |
|---|---:|---:|
| pareto_refine | 948.0 | 93.4% |
| ga_search | 43.0 | 4.2% |
| qd_update | 11.0 | 1.1% |
| other | 7.0 | 0.7% |
| startup | 4.0 | 0.4% |
| holdout_gate | 1.0 | 0.1% |
| baseline_eval | 1.0 | 0.1% |

## 3. Alert-objective margin over its own floor

Median `cand_alert - alert_floor` = 1.5676; violations = 0.

## 4. Per-cycle records

| # | seed | gens | margin | SPRT | streak | holdout | pareto | arm | promoted | blocked |
|---|---:|---:|---:|---|---:|---|---|---|---|---|
|  | 84129 | 10 | 2.9125 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84150 | 6 | 3.0462 | promote(n=7) | (3, 3) | fail | champion | skipped |  | holdout gate |
|  | 84170 | 6 | 3.0462 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84189 | 6 | 3.0462 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84209 | 6 | 3.0725 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84229 | 6 | 3.1388 | promote(n=7) | (3, 3) | fail | champion | skipped |  | holdout gate |
|  | 84248 | 6 | 3.3187 | promote(n=7) | (3, 3) | fail | champion | skipped |  | holdout gate |
|  | 84272 | 6 | 3.385 | promote(n=7) | (3, 3) | fail | champion | skipped |  | holdout gate |
|  | 84292 | 6 | 3.385 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84311 | 6 | 3.385 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84332 | 6 | 3.3287 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84355 | 6 | 3.3287 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84377 | 6 | 3.3287 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84397 | 6 | 3.3287 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84417 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84439 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84459 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84480 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84500 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84521 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84543 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84563 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84585 | 6 | 3.3812 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84607 | 6 | 3.3749 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84628 | 6 | 3.3749 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84650 | 6 | 3.3749 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84672 | 6 | 3.3749 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84694 | 6 | 3.0363 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84714 | 6 | 3.2062 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84735 | 6 | 3.2062 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84755 | 6 | 3.2062 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84776 | 6 | 3.2762 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84797 | 6 | 3.2762 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84818 | 6 | 3.2762 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84838 | 6 | 3.2762 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84858 | 6 | 3.3162 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84879 | 6 | 3.3162 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84899 | 6 | 3.3012 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84919 | 6 | 3.3012 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84941 | 6 | 3.3012 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84962 | 6 | 3.3012 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 84984 | 6 | 3.3012 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85004 | 6 | 3.3012 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85025 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85045 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85065 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85087 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85108 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85129 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |
|  | 85150 | 6 | 3.295 | promote(n=7) | (3, 3) | cooldown | champion | skipped |  |  |

