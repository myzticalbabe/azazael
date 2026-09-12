# Tensor Genome — the compiled-model deliverable

**Status:** shape layer IMPLEMENTED and LIVE · training layer SPECIFIED, not built
**Date:** 2026-09-12
**Modules:** `src/CORE/WORMS/expansion/tensorgene.py` (new), `scripts/evolution_cycle.py` (wired)

---

## 1. The deliverable, stated precisely

Everything upstream searches a genome that **cannot say what it is worth**. A gene's
*value* is known; its *contribution* is not. That is the root cause of three separate
defects already paid for in this codebase:

| Symptom | Root cause |
|---|---|
| `morph_trainer_kwargs` had to be hand-written to stop a gene being inert | a gene could be added without any consumer being declared |
| "fitness went up" could be bought with description length | no per-gene accounting of what the fitness was bought with |
| the Phase E verdict needed a dedicated per-dimension ledger | the genome carried no self-description, so the ledger had to be external |

The deliverable is a genome whose every coordinate is a **typed tensor that carries its
own measured usefulness**, and which therefore **compiles**: genes below the usefulness
floor are prunable, and what remains declares the input layer of a model that predicts
fitness from genes.

**What that is not:** it is not "train a big model". The genome has ~5 coordinates. The
honest deliverable is a *small, fully-attributed predictor* whose inputs are each
justified by a measured association, plus the machinery that keeps that attribution true
as the genome changes.

---

## 2. What is live right now

`TensorGenome.declare()` reads the same history feed the Oracle uses and writes two
artifacts every cycle:

```
state/tensor_genome.json         the self-describing genome (with usefulness_floor)
state/tensor_genome.spec.json    the model SHAPE this genome compiles to
state/tensor_genome.last.json    the panel's read model
```

Measured on real history, 2026-09-12T04:49:

```
rows 500   genes 5   width 20   above floor 3/5   identifiable 5/5

  use_schema_features   kind=bool    prov=morph   rho=-0.3572  down  n=51
  discount              kind=float   prov=core    rho=-0.2804  down  n=288
  epsilon_decay         kind=float   prov=core    rho=+0.2105  up    n=288
  learning_rate         kind=float   prov=core    rho=+0.1173  up    n=288   <- below floor
  epsilon               kind=float   prov=core    rho=-0.0274  down  n=288   <- below floor
```

This is a real result, not a smoke test. Three things in it matter:

1. **`epsilon` is dead weight** (ρ = −0.027). It has been an evolved gene since the
   beginning and carries essentially no association with fitness. The genome now says so.
2. **The morph gene is the strongest signal** (ρ = −0.357) on only **n = 51** — far fewer
   observations than the core genes' 288, because it is only trialled on the cycles that
   rotate to it. Its usefulness is real but its sample is thin, and the artifact states
   the sample so that is visible rather than averaged away.
3. **241 of 500 rows were repeats.** `samples = 288`, not 500. The pool snapshot is reused
   for up to `POOL_MAX_AGE_S = 1800`, so consecutive cycles record bit-identical genes and
   fitness. Correlating over raw rows would treat one measurement as many — the same
   defect already fixed in `cranium_decide` and `_sprt_collapse`.

---

## 3. The four rules the module enforces

Each rule exists because its violation already cost something in this repo.

**Rule 1 — a gene that is not consumed is worse than no gene.**
`TensorGenome.prune()` exists so an unconsumed coordinate is *removable* rather than
silently inert. `_eval_salt` reads exactly four genes by name; a fifth added to
`GENE_BOUNDS` would have been ignored entirely. `compile_spec()["below_floor"]` reports
candidates **without removing them**, because the search is still using them and a spec
that removed them would desynchronise from the genome it describes.

**Rule 2 — fitness is only comparable within a dimension, and an absent gene is skipped.**
`correlate()` skips rows that lack the gene and **never imputes**. A gene absent from a row
was not searched in that row, so it has no observation to contribute. `morph_switch`-style
hardcoding is what this prevents: the real morph genes are `use_schema_features` and
`by_session`, and the first live run typed one of them as a continuous `float` with
`unknown` provenance until the maps were derived from `MORPH_CANDIDATES` itself.

**Rule 3 — re-measurement is not evidence.**
`dedupe_observations()` and `correlate()` dedupe on `(gene vector, fitness)` first.

**Rule 4 — correlation is not causation, and the module says so.**
`usefulness` is `|rho|`; the signed coefficient is stored separately as `rho`. Every
statistic is labelled an association. The tests assert that no effect-size vocabulary
(`effect`, `effect_size`, `caused_by`, `impact`) can appear in the output, so nothing
downstream can read a rank correlation as an effect size.

---

## 4. The compilation path

```
 history rows (memory store)
        |
        v
 TensorGenome.declare()      <- kinds, bounds, provenance from the producers
        |                       correlates each gene, deduped
        v
 prune()  below usefulness_floor 0.15
        |
        v
 to_tensor()  ->  [value, usefulness, direction_sign, identifiable]   x gene
        |
        v
 compile_spec()  ->  input {width, rows, feature_order}
                     hidden [max(8, w*2), max(4, w)]
                     output best_total (linear), loss huber
        |
        v
 trained: false      <-- THIS is the boundary that is not built yet
```

`compile_spec()` emits a **shape declaration**, and it is labelled as such
(`"trained": false`). The panel renders it as `UNTRAINED spec` rather than as a model.
A spec that claimed to be a model would be the single most misleading artifact in the
system, because nothing downstream could tell.

### Why training is a separate, GIL-side step

`torch` cannot load under `python3.14t` — the production runner's interpreter — because
the free-threaded build shares `site-packages` with the GIL build and the wheels are
abi-incompatible (`cp314t` vs `cp314`). This is the same constraint the Oracle already
solved: train under the GIL interpreter as a subprocess, and let **only JSON** cross back.
`era_robust_decision_pure()` is the existing proof that the cross-interpreter path works —
verified byte-identical to the torch path to float32 (7e-6).

### Why the module is pure stdlib

`tensorgene.py` imports `json`, `math`, `typing` only. It therefore runs **identically**
under both interpreters, which is why the genome artifact is refreshed *inside* the cycle
rather than in a subprocess. Verified: `verify_exmachina.py` and
`verify_exmachina_panel.py` both report `ALL OK` under `python.exe` and `python3.14t.exe`.

---

## 5. Steps to the trained model

Ordered by what unblocks the most.

1. **Train the predictor** — `scripts/train_tensor_model.py`, GIL-side, mirroring
   `train_fitness_oracle.py` exactly (subprocess, JSON artifact, freshness marker,
   exit code 3 for "not enough history"). Target `best_total`; features are the
   `compile_spec()` tensor rows. Given ~5 genes and ~300 deduped rows this is a
   seconds-scale CPU job, not a GPU one.
2. **Hold out by era, not by row.** The Oracle already does this. A row-wise split leaks,
   because the pool freeze means adjacent rows are the same measurement.
3. **Report calibration, not just error.** `TESTUDO` is the existing conformal organ and it
   currently reports achieved coverage 0.225 against a 0.90 target. The trained predictor
   must be scored by that same organ, or its intervals are decoration.
4. **Close the loop.** Feed the predictor back as an additional pre-gate (the Oracle slot,
   Phase C) and measure whether the promotion verdict improves. Without this step the model
   is an artifact, not a component.
5. **Prune for real.** Only after (1)–(4): `prune()` with `keep=TENSOR_KEEP` protecting the
   four genes a downstream consumer reads by name, and measure the fitness cost of dropping
   `epsilon` (currently ρ = −0.027, predicted cost ≈ 0).

---

## 6. Honest limits

* **The usefulness floor is a judgement, not a measurement.** 0.15 is a hard floor rather
  than a p-value, deliberately: with frozen-pool rows the effective sample size is
  unknowable, so a significance test would be theatre. It is a single constant in one
  module and it is printed in the artifact.
* **ρ is an association over a *searched* distribution.** The genes were not sampled
  independently of fitness — the search selected them. `usefulness` therefore describes
  the joint history, not a causal effect, and Rule 4 is the only thing standing between
  that number and a false claim.
* **`learning_rate` sits at 0.117, just under the floor.** It may be genuinely weak or the
  history may be too confounded to tell. The module reports `below_floor` as a candidate
  list precisely so this stays a question rather than becoming a deletion.
* **The spec's hidden sizes are conventional, not tuned.** `[2w, w]` is a default. Nothing
  has been fitted; it is a shape.
* **The tensor genome is refreshed per cycle but the model is not.** They will drift apart
  until (1) exists. The artifact carries `rows` and `trained_at` so the drift is visible.
