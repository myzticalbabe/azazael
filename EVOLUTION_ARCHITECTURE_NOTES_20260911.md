# Evolution Architecture Notes — 2026-09-11

Working notes while implementing the four followups from
`EVOLUTION_PROCESS_AUDIT_20260910.md`. Recorded inline so the reasoning survives
the session, including the dead ends.

---

## 0. Orientation corrections (things I believed that were wrong)

Found by checking instead of assuming. All three changed the work.

**0.1 `code_search` returned false zeros.** Queries scoped to `azazael/src`
reported `Found 0 matches` for `EvolutionEngine` — a class I had read minutes
earlier in `src/CORE/WORMS/expansion/evolution.py`. Three separate architecture
claims I was about to make ("no NSGA-II", "no embeddings", "no BO") rested on
those zeros. Re-ran everything through `grep` instead. **Lesson: treat a
zero-result as a tool failure until a positive control validates the same
scope. `EvolutionEngine` was that control.**

**0.2 NSGA-II is real and wired.** `evolution.py` has `_non_dominated_sort`,
`_crowding_distance`, `optimize_multi_objective`; the production driver called
it at `evolution_cycle.py:1038`. So the gap was never "missing code".

**0.3 Embeddings are real.** `CORE/embedding_backend.py` does Ollama embeddings
(multi-model, 768/1024-dim, disk-cached) and `local_memory._cosine_similarity`
projects across dimensions. Lexical-only was wrong.

**0.4 `_SALTS` has THREE salts, not two.** The `fitness_genes` docstring says
"min over 2 exploration salts"; the constant is `('a', 'b', 'c')`. The stale
docstring matters: the salt spread is the only in-cycle noise estimate
available, and its size (3, not 2) is what makes it usable as an SPRT sigma
floor on cycle 1.

---

## 1. Followup #2 — SPRT replaces the fixed 3/3 streak

### Why the old gate was structurally weak
`PROMOTE_WINS = 3` required **exactly three** consecutive wins regardless of
magnitude. A +0.76 margin and a +10.0 margin were evidentially identical to the
gate. Worse, the gate had no variance model at all, which is *why* `pool_id`
era-pinning (EV-2) and `baseline_hash` had to be bolted on — those exist to stop
heterogeneous margins being compared, which a statistical test would handle
natively.

The deeper problem: `fitness_genes` is deterministic for a given (genome, pool),
so the per-cycle margin is not noisy in the measurement sense. The variability
that matters is **search** variability — which genome the GA happens to find —
plus evaluation robustness across salts. An SPRT over per-cycle margins models
exactly that: each cycle is one draw from the search distribution.

### Implementation
`SPRT_ALPHA=0.05`, `SPRT_BETA=0.10`, H0: margin=0, H1: margin=`PROMOTE_MARGIN`
(0.75). Per-observation increment:

```
LLR_step = ((d - d0)^2 - (d - d1)^2) / (2*sigma^2)
```

which is 0 at the indifference point `(d0+d1)/2`, positive for strong evidence,
negative against. `SPRT_UPPER = ln((1-beta)/alpha) ≈ 2.89`,
`SPRT_LOWER = ln(beta/(1-alpha)) ≈ -2.25`.

Sigma comes from `estimate_margin_sigma(prior_margins, salt_floor)`: the observed
dispersion of the era's margins with the `salt_spread` of the current champion as
a floor. With <2 observations it falls back to the floor, so cycle 1 still has a
defensible sigma.

Bounds kept deliberately: `PROMOTE_MIN_WINS=2` (a single observation can never
promote, however degenerate sigma becomes) and `PROMOTE_MAX_WINS=6` (evidence
that stays between the bounds forever is declared `inconclusive` and stops
accumulating rather than silently sitting one win from promotion forever).

`_compute_streak` is retained unchanged — it is still the era+baseline pinning
that makes margins comparable at all, and only its role changed (display /
compatibility counter rather than the promotion criterion).

### First live observation (2026-09-11T01:02:17)
```
promotion standing: beats=True margin=1.0063 sprt=promote(n=2 llr=20.4757 sigma=0.211938) streak=2/3
```
SPRT promoted at n=2 where the old rule demanded 3. sigma=0.2119 is the salt
spread (only 1 prior margin existed, so the floor applied). A margin of 1.0063
against an effect size of 0.75 with sigma 0.21 is genuinely strong evidence, so
n=2 is the correct call — the count-based rule was simply leaving evidence on
the table.

### Then the holdout blocked it
```
holdout: {'passed': False, 'cand': 30.9825, 'base': 31.1713, 'margin': -0.1888}
promotion BLOCKED by holdout gate
```
This is the reassuring part, not a failure. SPRT says "the frozen-pool evidence
is sufficient"; the holdout (`_holdout_gate`) re-tests on **freshly extracted**
pools and found the win was pool-overfit. Division of labour is right: SPRT is
the *evidence* gate, holdout is the *generalisation* gate. Faster promotion
decisions are safe precisely because holdout and canary are downstream.

**Open question worth watching:** now that SPRT can reach the holdout at n=2
instead of n=3, holdout is consulted ~1 cycle sooner and more often. If the
cooldown (`holdout_cooldown.json`) starts churning, that is the cause.

---

## 2. Followup #1 — Pareto knee into the promotion decision

### The dead end (worth recording)
The obvious wiring is "block promotion if the baseline Pareto-dominates the
candidate on (info, alert)". **That gate is provably vacuous.** Fitness is the
scalar sum `info + alert`, so if the baseline dominates on both objectives it
also has the larger total, and `beats` is already False. Dominance can never fire
on a candidate that passed the margin gate. Verified numerically:

```
balanced    cand_total=27.0 base_total=27.0 beats=False base_dominates=False
guts alert  cand_total=32.0 base_total=31.0 beats=True  base_dominates=False
```

The `guts alert` row is the real failure mode: total **rises** by 1.0 while the
critical-alert objective **collapses** by 13.0, and no dominance test notices.
This is exactly the shape of the defect the audit found (the hard pool starving
while the scalar total looked healthy).

### What was actually implemented
A **one-sided non-regression constraint** the scalar total cannot express: the
candidate must hold the alert objective within `PARETO_ALERT_TOL=0.25` of
production. If the champion regresses it but the NSGA-II **knee** (the balanced
point on the info/alert front) does not, and the knee still clears the margin
over baseline, the knee becomes the promotion candidate.

`_pareto_refine()` was extracted from `main()` and **moved ahead of the
promotion decision**, so the knee is an input rather than a post-hoc report —
that relocation is the substance of "wiring it in". `cand_genes` /
`cand_total` / `cand_info` / `cand_alert` now thread through the holdout and the
promotion write, so promoting the knee is coherent end to end.

### First live observation
```
pareto gate: {cand_total 32.4013, cand_info 17.2263, cand_alert 15.175,
              base_total 31.395, base_info 16.645, base_alert 14.75,
              alert_floor 14.5, source 'champion', passed True}
```
Champion held alert at 15.175 vs floor 14.5 and gained on both objectives — a
genuine balanced improvement, correctly passed.

---

## 3. Followup #4 — prioritized alert-pool sampling

Implemented `pool_priority()` (severity weight x recency half-life, floored) and
`prioritize_pool()` (proportional resampling by `p_i^alpha`, seeded). Applied at
the two places a pool enters evaluation: `_load_or_freeze_pools()` and
`_holdout_gate()`'s fresh extraction.

Three deliberate design choices:

* **The snapshot stores the RAW pool.** Prioritization is applied on the way out,
  so it is never double-applied on reuse and `pool_id` / `pool_fingerprint` keep
  meaning the same data era.
* **The prioritization seed is the era's `saved_at`, not the genome salt.** Every
  genome and every cycle within an era must see the SAME prioritized draw —
  otherwise prioritization becomes a second source of per-genome variance and
  silently corrupts the fitness comparison.
* **Honest scope: this is the SAMPLING half of PER only.** The importance-
  sampling *correction* half is not implemented, because
  `RLTrainLoop.train_from_memory()` accepts no per-sample weights. Calling it
  "full prioritized experience replay" would be false.

Measured: with a 50/50 pool of recent-critical vs old-info rows, the resampled
pool was 4/4 critical (uniform expectation 2/4). Deterministic for a fixed seed;
degrades to an unweighted draw when all priorities are equal.

Related structural finding while implementing this: `query_memories()` does
`min(limit, 500)`, so **`hard_count` saturates at 500 and can never reveal
starvation.** Only `hard_newest` carries signal. Any monitor that gates on
`hard_count` is measuring a constant.

---

## 4. Followup #3 — attribution of the 23:24:38 writer

### I have to retract my own correction first
In the previous session I said "git did not revert the params file; reflog is
clean, so the D-1 attribution is wrong." **That reasoning was invalid.**
`git checkout -- <file>` and `git restore <file>` are *file-level* operations:
they never move HEAD, so they never write a reflog entry. A clean reflog cannot
exonerate git for a single-file restore. Reflog only sees commits and ref"
updates.

### What the evidence now shows

| # | Observation | Implication |
|---|---|---|
| 1 | Exactly ONE file modified in 23:20-23:30: `config/evolved_rl_params.json` @ 23:24:38 | not a sync sweep, not a bulk operation |
| 2 | Content became byte-identical to git HEAD | a *restore-to-committed-state* action |
| 3 | **61 of the 68 dirty tracked files still carry 2026-09-08 mtimes** | **refutes `git checkout .` / `git restore .`** — a bulk restore would have touched all 61 |
| 4 | No reflog entry | consistent with (and evidence for) a file-level restore |
| 5 | ZERO DirectMemory events 23:15-23:35 | no instrumented component did it |
| 6 | No ERROR_LOG.md entry (stale since 2026-08-29); `.audit/gate_tokens/` empty | no gate violation was recorded |
| 7 | `.git/index` mtime 23:40:51 | explained by my own later `git rm --cached`; cannot confirm or exclude a 23:24:38 index write (mtime keeps only the last write) |

### Conclusion
A **targeted single-file** `git checkout`/`git restore` of
`config/evolved_rl_params.json`, issued from **outside the instrumented
pipeline** (IDE/GUI client or a manual command). It is not a bulk restore, not a
sync agent, not the DB mirror (`data_retention.py` mirrors only
`db-backup/memory_store.*.db.gz`), and not the parallax gate daemon.

The one in-repo component that does *exactly* this and would produce
byte-exact-HEAD content is `src/DAEMONS/parallax_validator.py::revert_file()`,
which shells `git checkout -- <file>`. It is nonetheless a weak suspect: it logs
a CRITICAL violation plus a DirectMemory record, and both are **absent**, so it
was not running (or was in `--dry-run`) at that moment. Residual uncertainty
stays on exactly that point.

### Why it no longer matters operationally
EV-1 moved live genes out of git-tracked `config/` into gitignored `state/`
(committed `git rm --cached`), so **any** future file-level restore can no longer
touch production hyperparameters. The root cause is closed regardless of which
untraced process ran it — which is the right way to fix an unattributable
single-file writer.

---

## 5. Status

All four followups implemented; 73 tests green (SPRT, Pareto gate, prioritized
sampling, plus the new TERENCE self-guard suite). Live-cycle observations
recorded in sections 1-3. Remaining watch item: SPRT now reaches the holdout one
cycle sooner than the old 3/3 rule, so `holdout_cooldown.json` is the thing to
watch for churn.

---

## 5a. EV-8 — the flat-trajectory WARN was a false diagnosis

**I have to correct a claim from the previous turn.** I wrote that the
flat-trajectory WARN was "gone" after EV-4. It was not: it had merely not been
re-rendered yet, because the monitor reads the *persisted* artifact from a cycle
that ran before the EV-4 edits landed. It came straight back on the next cycle.

### The claim under test

The WARN read `evolution trajectory flat (all gens same reward - fitness has no
gradient)`. That asserts the objective is gradient-free. I measured it:

| Probe | Result |
|---|---|
| 40 **random** genomes on the frozen pool | **40 distinct** fitness values, range 4.27 – 11.47 |
| Same genome evaluated 3x | identical to 6 dp (deterministic) |
| `EvolutionEngine` on a synthetic unimodal fitness | best climbs -0.0946 -> -0.0148, converging on the target |

So the objective has a rich, deterministic gradient and the GA engine is
healthy. The WARN was wrong about the cause.

### The real cause

`evaluate_population` sorts the population and reports
`best_fitness = population[0].fitness`. Under elitism the elite **survives with
its cached fitness** (it is never re-evaluated), so `best_fitness` is flat *by
construction* until some child beats the elite. The genuine signal is the
**population mean**, which the artifact did not record.

### Fix

`evolution_cycle.py` now records `trajectory_avg` alongside `trajectory`, and the
monitor distinguishes the two cases:

- best flat **and** mean flat -> "objective has no usable gradient on this pool";
- best flat **while the mean moves** -> "converged to a plateau at the seeded
  champion ... search is running, not stuck".

### Live confirmation (artifact 2026-09-11T05:41:34Z)

```
best traj: [13.7381, 13.7381, 13.7381, 13.7381, 13.7381, 13.7381]
avg  traj: [ 9.3158, 11.7155, 12.1122, 12.4657, 12.6891, 12.6669]
```

The mean climbs 9.32 -> 12.69 in six generations. The population is converging
on an unbeaten seeded champion - a plateau, not a stall. The corrected message
now says so.

**Generalisation:** a metric that is flat *by construction* (elitism keeps the
best unevaluated) must never be used as evidence about the underlying landscape.
Record the distribution, not just the extremum.

---

## 6. TERENCE — the trainer was the thing that needed training

The user directive was "train TERENCE to fix these errors". The honest finding is
that TERENCE was not yet fit to train: its reward signal was unverifiable and
several of its rules were destructive. Recording because the reasoning is
reusable.

### 6.1 Orientation (a correction)

TERENCE had **zero** rows in the memory store before today. Its proficiency
ladder (scan / preview / fix_all / _apply_verified / _record_outcome /
pattern_scores) was fully built but had never actually run. "Training" therefore
had to start with making the loop safe to run at all.

### 6.2 Three defects that made it net-destructive

1. **Fix semantics.** `_scan_file` stored `original = line.strip()[:50]` and
   `_apply_verified` did a whole-line `.replace()`. So a rule whose replacement
   was a comment (`print(x)` -> `# print(  # Debug`) deleted the whole
   statement. `py_compile` still passed, so `_record_outcome` recorded
   `success=True` — the loop *reinforced* code deletion.
2. **Inverted comparisons.** `==\s*None|!=\s*None` had a single fix of
   `is None`, so `x is not None` became `x is None`. Same shape for
   `== True|== False` -> `is True`.
3. **Unfalsifiable reward.** Because deletion compiles, the success flag could
   not distinguish "fixed" from "removed".

Measured impact before the fix: a scan of `src/{ORCHESTRATION,UTILITIES,META,CORE}`
produced **6,326** destructive auto-appliable fixes across 317 files, every one
of which would have been recorded as a success.

### 6.3 The fix (2026-09-11)

- `original` is now the **matched span**; `fixed` is that span after
  substitution — never the whole line.
- `RULE_SUBSTITUTIONS` gives every auto-appliable rule an explicit, *correct*
  substitution, narrowing patterns that were too broad (e.g. `== None` only).
- `UNSAFE_RULES` makes anything that deletes/comment-out code, or is not
  actually equivalent, **advisory only**. `_gutted()` refuses any edit that
  leaves no executable content on the line.
- `EXTRA_RULES` adds the cases the original set got wrong *by omission*
  (`!= None`, `== False`), so neither comparison can be rewritten into its
  opposite. Strict UTF-8 decode replaces `errors="ignore"`.

### 6.4 The second-order error: TERENCE edited itself

Running a bounded training pass (§ the pass that "trained" it) made TERENCE
rewrite **its own rule table**. Root cause: several rule *descriptions* embed the
very pattern they detect, so a self-scan matches its own metadata.

| Field | Before | After self-scan |
|---|---|---|
| None rule `desc` | `"Use 'is None' instead of '== None'"` | `"...instead of 'is None'"` |
| list rule `desc`/`match` | `Simplify list(d.keys())` | `Simplify list(d)` |
| assert rule `pattern` | `assertEquals\|assert_` | `assertEqual\|assert_` |
| EXTRA_RULES `desc` | `...instead of '!= None'` | `...instead of 'is not None'` |

Because `RULE_SUBSTITUTIONS` is keyed on `desc`, my own newly-written keys were
rewritten in lockstep, which is why the tool kept passing while its
documentation went quietly wrong.

**Root-cause fix:** `SELF_DIR` + `_is_self()`, enforced at three points — the
`scan()` loop, `run_quick_fix()`, and `_apply_verified()` — plus a guard in
`_scan_file()` so direct callers cannot bypass it. All six corrupted fields were
repaired, and 8 new tests in `tests/test_evolution_helpers.py::TestTerenceSelfGuard`
assert that no module in TERENCE's package can ever yield or receive a fix.

### 6.5 The training signal is now correct (measured)

After the fixes, a fresh bounded pass reports:

- `evolved skip (poor verify history): ['Comment out print statement',
  'Replace magic numbers with constants']` — the loop now *suppresses* the two
  worst rules from their recorded 0.000 verify rate. That is the learning working.
- `6407 advisory findings withheld from apply` out of 6,408 total.
- **1** legitimate fix applied, **0** targeting TERENCE's own package.
- Stored outcomes now separate cleanly: destructive rules n=27/7 rate 0.000;
  safe equivalences (`list(d.keys())`, `== None`, `!= None`, `assertEquals`)
  rate 1.000 over 40 successes.

Every fix TERENCE applied outside its own package was verified as a true
semantic equivalence before I accepted it (`list(x.keys())` -> `list(x)`, etc.);
all 15 touched modules compile.

### 6.6 Reorientation note for the next session

The durable lesson is the shape, not the rules: **a self-modifying tool needs an
explicit exclusion for its own source, because its documentation and its targets
overlap.** The same trap applies to any future "meta" worm that embeds patterns
it then scans for.
