# EVOLUTION-PROCESS AUDIT — 2026-09-10

Scope: the **ongoing** (live, scheduled) evolution processes — the GA over RLTrainLoop
hyperparameters, its cycle driver, its promotion/canary guardrails, and the artifacts
they read and write.

Method: read-only inspection of the live process state. Evidence sources:
`logs/evolution_cycle.log` (9,034 lines, Sep 7–10), the live store
`C:\Users\clint\.azazael\memory_store.db` (read-only URI), the on-disk artifacts in
`config/` and `state/`, git state of the tracked artifact, and the project's own
monitor (`src/scripts/monitor_learning.py`).

> **No inference agents were spawned for this audit and no fixes were applied.**
> This is an observation pass; every claim below cites a file, log line, or DB row.

**Timestamps:** log lines are host-local (EDT, UTC−4). DB rows are UTC. Both are
labelled where they matter, because the canary/rollback sequence is only legible
when they are aligned.

---

## PASS 1 — INVENTORY (what is actually running)

### Processes

| Process | Driver | Nominal cadence | Observed cadence |
|---------|--------|-----------------|------------------|
| EvolutionCycle | `scripts/evolution_cycle.py` | "daily" (per `LEARNING_LOOP_AUDIT_20260907.md`) | **every 5 min** when host awake — 541 cycles Sep 7–10 |
| DreamCycle | `scripts/dream_cycle.py` | 5 min | 5 min (8 dreams in last hour) |
| MetacogCycle | `scripts/metacog_cycle.py` | 5 min | 5 min (last `mc_cycle` 03:35:41Z) |
| TrainingOrchestrator | — | — | last `training_*` 2026-09-10T14:54:59Z |

The Sep-7 audit's "daily" label for evolution is **stale**: the loop now runs every
5 minutes, i.e. ~288 evaluations/day, not 1. The conclusions drawn from a daily
cadence no longer describe this process.

### Engine

`src/CORE/WORMS/expansion/evolution.py` — `EvolutionEngine` v1.0.0 (993 LOC,
`@register_worm(category="learning", priority=6)`), plus `GeneticOptimizer`.

### Artifacts (live, 2026-09-10)

| Artifact | Content at audit | Tracked? |
|----------|------------------|:--------:|
| `config/evolved_rl_params.json` | 3 genes (lr .3312 / eps .0346 / disc .8189), `promoted_at` **2026-09-07T23:09:38**, fitness 14.82 | **yes (git)** |
| `config/evolved_rl_params.json.prev.json` | 4 genes (lr .5 / eps .2147 / disc .8254 / decay .0964), `promoted_at` 2026-09-10T**11:57:04** EDT, fitness 29.97 | no |
| `config/evolved_rl_params.json.prev2.json` | 4 genes (…eps .1818 / decay .0882), `promoted_at` **11:30:12** EDT, fitness 29.3537 | no |
| `config/evolved_rl_params.json.canary-failed.json` | lr .4867 / eps .3081 / disc .8483 / decay .0963, `failed_at` **13:29:31** EDT, `regress` 1.7475 | no |
| `config/evolved_meta_params.json` | mutation .2088, crossover .717, tournament 4, **patience 3**, tol .01 (runs 194, ema +1.73) | no |
| `state/evolution_pool_snapshot.json` | frozen 500+500 rows, `pool_id` 1789096771, saved 23:19:31 EDT | no |
| `state/holdout_cooldown.json` | `pool_id` 1789096771, margin 2.5062, 14:14:32 EDT | no |

### Store counters (live DB)

`evolution_result` **536** (last 03:34:49Z) · `evolution_promotion` **44** (last
2026-09-10T17:19:05Z) · `generation_complete` **4,108** · `optimization_complete` 125 ·
`thought_process` 206 · `checkpoint_saved` **17** (last 2026-09-09T05:01:06Z) ·
`strategy_adapted` **0**.

---

## PASS 2 — RATE (live health)

**Monitor verdict: `0 FAIL`, `1 WARN`** — `evolution trajectory flat (all gens same
reward - fitness has no gradient)`.

| Signal | Value | Read |
|--------|-------|------|
| adaptations / h | 25 | healthy |
| dreams / h | 8 | healthy |
| `state_saved` age | 1.8 min | healthy |
| switches (24h) | 9 | healthy |
| active strategy | `defensive` (steering active) | healthy |
| dream quality (1h) | 0.90 | healthy |
| metacog | fed=1, adapted=false, rec=defensive | healthy |
| evolution | 4 gens, flat trajectory | **WARN** |

The loop is **genuinely closed and wired** — this is the strongest part of the
system, and the Sep-7 fixes (steering, adoption gate, reward gradient) held.

This audit **answers AR-5** from `LEARNING_LOOP_AUDIT_20260907.md` ("watch 24h for the
evolution WARN to clear"): the WARN did **not** clear. It changed shape. The reward
gradient exists (fitness now spans ~28–31, not the flat 50.0 of Sep-7), but the
*trajectory within a cycle* is flat because the GA stops after 3–4 generations
(finding D-3).

---

## DEFECT LOG (evidence-backed)

### D-1 — 🔴 HIGH — Live production state is git-tracked; a restore silently reverted production hyperparameters, bypassing all four promotion gates in reverse

`config/evolved_rl_params.json` is **tracked in git**, and its on-disk content is
**byte-identical to HEAD** (`git diff -- config/evolved_rl_params.json` → empty).
Its `promoted_at` is **2026-09-07T23:09:38** and it carries a **3-gene** genome with no
`epsilon_decay`, no `holdout`, and no `pool_id`.

But the pipeline's **last real promotion** was `2026-09-10T17:19:05Z` (= **13:19 EDT**),
genes `lr .4867 / eps .3081 / disc .8483 / decay .0963` (fitness 30.7225 vs baseline
29.3488, wins=3) — exactly the genome in `.canary-failed.json`. The one-shot canary
fired at **13:29:31 EDT** and failed (`regress` 1.7475), correctly rolling production
back to `.prev`; the runs at 14:44 and 20:46 confirm production then held the
**11:57 genome** (`lr 0.5` → baseline fitness 29.4563 / 29.2963).

Then, between the 23:24:37 and 23:29:30 runs, production changed:

```
23:24:37  production baseline: {'learning_rate': 0.5,      ... 'epsilon_decay': 0.0964} -> 29.6725
23:29:30  production baseline: {'learning_rate': 0.3312,   ... 'epsilon_decay': 0.0}    -> 28.2312
```

`config/evolved_rl_params.json` has **mtime 23:24:38.364** and content == HEAD, and
**no `evolution_promotion` row exists after 13:19 EDT**. So an **external writer**
(a `git checkout`/`git restore`/sync against the tracked file) reverted production to
the committed Sep-7 genome — after the pipeline had deliberately rolled it back.

**Impact:**
1. Production RL hyperparameters regressed from a 29.67-fitness genome to a 28.23 one,
   losing `epsilon_decay` entirely.
2. The four gates (streak → holdout → promote → canary) are bypassable in reverse by any
   repo operation. **This is the highest-severity finding.**
3. The era-pinned streak did **not** reset: `pool_id` stayed `1789096771`, so the
   standings `1/3` (23:19, measured vs baseline 29.6725) and `2/3` (23:34, measured vs
   baseline 28.2312) are counted as **one streak across two different baselines**.

### D-2 — 🔴 HIGH — The seed chain is a fixed point; the primary seed never advances

`champion_genes` is **identical in the last 7 consecutive artifacts**:
`{lr 0.3918, eps 0.0451, discount 0.9533}` (3 genes, no `epsilon_decay`), while
`best_genes` (the actual winner) differs every run. `champion_reeval` is frozen at
**21.815** (it was 25.6175 / 26.2737 while the chain still moved).

**Root cause:** the driver records `'champion_genes': seed_genes` — the *input seed* —
while `last_best_genes()` prefers `champion_genes` over `best_genes`. Therefore
`seed(n+1) = seed(n)`. The inline comment claims `champion_genes` is "the genome that
actually earned champion_reeval"; it is the seed, so it never advances.

**Impact:** every cycle spends seed slots on a genome scoring 21.8 against ~30 for
fresh draws, and `champion_reeval` — the intended drift detector — is a constant. The
hall-of-fame path (margin +2.2837, re-eval 29.38) is the only continuity still working,
and it *also* returns the same top-margin row every run within an era.

### D-3 — 🟡 MEDIUM — Early stopping fires at gen 3–4 of 15 on nearly every cycle

Every cycle in the window logs `converged at gen 3/4, stopping early` against a budget
of 15 generations (`population_size=24`, `elitism_count=3`). The latest artifact's
trajectory is `[30.3112, 30.3112, 30.3112, 30.3112]` — the monitor's flat-trajectory
WARN.

**Contributing cause:** meta-evolution has driven its own `early_stop_patience` to the
**lower bound of its own search space (3)** with tolerance 0.01
(`config/evolved_meta_params.json`). The meta-search is optimizing the GA *toward
stopping sooner*. Combined with `has_converged()` measuring a relative improvement over
only the last `patience` entries of a `_generation_history` that is **rebuilt per
process** (each cycle is a fresh process), "converged" is declared on 3 samples of
within-process history. Real productive search is ~1–2 generations.

### D-4 — 🟡 MEDIUM — Hard-example pool is frozen (alert objective re-mastering stale rows)

Latest artifact `pool_fingerprint`: `hard_count` 500, **`hard_newest`
2026-09-09T15:47:02Z** — no new critical-alert rows for ~36h at audit time. The driver's
own docstring flags this exact failure ("if hard_count stalls for days, evolution is
re-mastering frozen rows and needs fresh production errors"). The frozen snapshot also
diverges from live extraction: snapshot info=500 (476 info / 24 error) vs live 300-row
info=287 / error=13.

### D-5 — 🟢 LOW — Hygiene / documentation drift

- **Backwards version control:** the *promoted* file is tracked while `.prev`,
  `.prev2`, `.canary-failed` and `evolved_meta_params` are untracked — precisely
  inverted from a safety standpoint, and the enabling condition for D-1.
- `checkpoint_saved` = 17 total, none since 2026-09-09. The driver never calls
  `save_checkpoint()`, so `EvolutionEngine`'s advertised checkpoint/restore continuity
  is **not part of the live loop**.
- `generation_complete` = 4,108 rows (one per generation) written to the live store.
- `strategy_adapted` = 0 — metacog/strategy actually emits `strategy_adaptation`; the
  name is a query trap for anyone auditing by event name.
- Cadence gaps are host-sleep, not scheduler failure: 14 gaps > 5.5 min; 6 multi-hour
  (largest 8:51:39, 2026-09-08). Knowledge of this belongs in the cadence docs, since
  it invalidates "daily run" baselines.

---

## PASS 3 — SCORECARD (evolution sub-loop)

| Dimension | Score | Assessment |
|-----------|:-----:|------------|
| Loop closure / wiring | 9.0 | Genuinely closed: dreams→metacog→policy→steering→evolution, evidence-gated, state persisted |
| Guardrail design | 8.0 | 3-salt min, pool-era tagging, holdout on fresh pools, depth-2 backup, one-shot canary — strong design |
| Guardrail **integrity** | 4.0 | D-1: a git restore bypassed all four gates; D-2: era streak not pinned to baseline genome |
| Search effectiveness | 4.5 | D-3: 3–4 of 15 generations used; flat trajectories; meta-search minimizing its own patience |
| Continuity / seeding | 3.0 | D-2: primary seed is a fixed point; HOF seed deterministic within an era |
| Data freshness | 5.0 | D-4: hard pool 36h stale; snapshot vs live divergence |
| Observability | 8.0 | Excellent: per-gen log, artifact row, fingerprint, pool-id, thought_process CoT |
| Persistence hygiene | 4.0 | D-5: tracked live state; checkpoint path unused |
| **Overall** | **5.7/10** | **Healthy, genuinely autonomous, and guardrailed — but the guardrails are bypassable by repo operations and the search is budget-starved** |

---

## IMPROVEMENT ITEMS

No evolution TODO doc exists, so all items are **ADDITIVE** and cross-referenced to
`LEARNING_LOOP_AUDIT_20260907.md` (AR-1…AR-8).

| ID | Item | Effort | Impact | Pri |
|----|------|--------|--------|-----|
| EV-1 | Untrack live state: `.gitignore` the runtime artifacts, `git rm --cached config/evolved_rl_params.json`, commit a `*.example.json` template instead. Prefer writing promotions to `state/` | 0.5h | 🔴 | P0 |
| EV-2 | Pin the promotion streak to the **baseline genome**, not just `pool_id` — record `baseline_genes_hash` per artifact and break the streak when it changes. This is the check that would have caught D-1 | 1h | 🔴 | P0 |
| EV-3 | Fix the seed chain: record the winner as `champion_genes` (or add `seed_genes` and make `last_best_genes()` prefer `best_genes`) | 0.5h | 🔴 | P1 |
| EV-4 | Give the search its budget: raise the `early_stop_patience` floor in `META_BOUNDS` from 3 to ≥5, or exempt patience/tolerance from meta-evolution (search-integrity params like `PROMOTE_MARGIN`). Enforce a minimum generation count before convergence is honoured | 1h | 🟡 | P1 |
| EV-5 | Re-arm hard-example inflow: schedule chaos drills / watchdog re-arming so `db_health_alert` does not stall for days; alert in the monitor when `hard_newest` exceeds 48h (AR-5 companion) | 1h | 🟡 | P1 |
| EV-6 | Reconcile the cadence docs (5 min, not daily) + record D-1's "who touched the file at 23:24:38" as a follow-up once the sync/git writer is identified (AR-8 companion) | 0.5h | 🟢 | P2 |
| EV-7 | Either wire `save_checkpoint()` into the driver or drop the checkpoint claim from the engine's documented feature set | 0.5h | 🟢 | P2 |

### Baseline metrics (recorded so improvement is measurable)

- Cycle count Sep 7–10: 1,116 / 1,404 / 2,910 / 3,604 log lines; **541 cycles**
- Production baseline drift observed **within one pool era**: 29.6725 → 28.2312 (−1.44)
- Frozen seed re-eval: **21.815** constant (was 25.6175 / 26.2737 when the chain moved)
- HOF seed: margin +2.2837, re-eval 29.3837–29.9487 (constant within era)
- Generations used per cycle: 3–4 of 15; meta patience pinned at its floor (3)
- `hard_newest` staleness at audit: ~36h

---

## IMPLEMENTATION STATUS — EV-1…EV-7 (applied 2026-09-10, same session)

| ID | Status | What landed |
|----|:------:|-------------|
| EV-1 | ✅ DONE | `.gitignore` now excludes `config/evolved_rl_params.json*`, `config/evolved_meta_params.json`, `state/evolved_rl_params.json*`, `state/evolution_pool_snapshot.json*`, `state/holdout_cooldown.json`. `git rm --cached config/evolved_rl_params.json` run (**staged deletion, no commit**; working file preserved). Live writes moved to `state/evolved_rl_params.json` (`PROMOTE_JSON`), with `config/` read-only as a legacy fallback in both `evolution_cycle.py::production_genes()` and `scheduling.py::ScheduleConfig.apply_evolved_overrides()`. One-time copy-don't-move migration (`_migrate_legacy_promotions()`) preserves `.prev`/`.prev2` rollback depth. New committed template: `config/evolved_rl_params.example.json` |
| EV-2 | ✅ DONE | `baseline_hash()` + `baseline_hash` field on every artifact; the streak loop now breaks on a changed baseline genome as well as a changed `pool_id` (fails closed on pre-fix rows) |
| EV-3 | ✅ DONE | `champion_genes` now records the **winner** (`best.genes`); the input seed is recorded separately as `seed_genes`; `last_best_genes()` prefers `best_genes`; stale docstring corrected |
| EV-4 | ✅ DONE | `META_BOUNDS['early_stop_patience']` floor 3 → 5; new `META_EXPLORE_KEYS` excludes search-integrity knobs (`early_stop_patience`, `early_stop_tolerance`) from perturbation; loaded meta params are clamped into bounds; new `MIN_GENS = 6` gate before a convergence claim is honoured |
| EV-5 | ✅ DONE | `monitor_learning.py` parses the artifact's `pool_fingerprint`, reports `hard_pool_newest` / `hard_pool_age_h` / `hard_pool_count`, and raises a WARN when the newest critical-alert row exceeds 48h |
| EV-6 | ✅ DONE | `LEARNING_LOOP_AUDIT_20260907.md` carries a dated cadence correction (daily → 5 min), answers **AR-5**, and its scheduler table + data-flow block are corrected |
| EV-7 | ✅ DONE | the driver now calls `evo.save_checkpoint('cycle-<seed>')` once per cycle (one row: full population + best genome), making the engine's advertised continuity real instead of dead code |

### Still open (deliberately NOT actioned)

1. **Writer identification (D-1 attribution).** The revert at `23:24:38` is proven (content == HEAD, no promotion event), but which process/command performed it is **not** identified. Candidates to check on the host: `git restore`/`checkout` in a session hook, `scripts/auto_sync.py`, `scripts/sync_canonical_docs.py`, `sync_all.py`, and any G:-archive restore step. **EV-1 makes the consequence harmless whether or not the writer is found** — `state/` now wins over `config/` — but attribution should still be closed so the sync path is fixed at source.
2. **Production genome not restored.** The pipeline rolled production back to the 11:57 genome (fitness 29.97, held from 13:29 to ~23:24) and something reverted it to the Sep-7 genome (28.23). Seeding `state/evolved_rl_params.json` from `config/evolved_rl_params.json.prev.json` would restore the gate-approved genome, but that mutates live production hyperparameters, so it is **left to the operator** rather than done silently: `copy config/evolved_rl_params.json.prev.json state/evolved_rl_params.json`.
3. **Streak reset expected.** Because pre-fix rows carry no `baseline_hash`, the current streak breaks by design on the next cycle (fails closed). Promotion will need 3 fresh wins — the intended behaviour, not a regression.
