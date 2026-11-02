# PROTEUS — IMPLEMENTATION STATUS (2026-09-12)

What actually landed, what is verified, and what is deliberately still off.

Companion docs: `PROTEUS_DEEP_EXPANSION.md` (design), `EVOLUTION_SOTA_EXPANSION_PLAN.md`
(ANIMA tier), `EXOTIC_TECHNIQUE_CATALOG.md` (survey + reject list),
`EVOLUTION_50RUN_GAPS_AND_FIXES.md` (the E1–E10 evidence this responds to).

---

## 1. Landed

| Organ | Module | Replaces | Lines |
|---|---|---|---|
| **Morph** | `src/CORE/WORMS/expansion/morph.py` | fixed 4-gene vector | 500 |
| **Oracle** | `src/CORE/WORMS/expansion/oracle.py` | the "one number" gate | 345 |
| **Arena** | `src/CORE/WORMS/expansion/arena.py` | the fixed pool | 355 |
| **Nerve** | `src/CORE/WORMS/expansion/nerve.py` | 4 scalar learner HPs | 340 |
| **Loom** | `src/CORE/WORMS/expansion/loom.py` | scalar QD coverage | 350 |
| **Chorus** | `src/CORE/WORMS/expansion/chorus.py` | numeric-only variation | 390 |
| **Cranium** | `src/CORE/WORMS/expansion/evidence.py` | era-PINNED SPRT | 274 |
| **Circulation** | `src/CORE/WORMS/expansion/allocation.py` | the fixed `2x` arm gate | 195 |
| **CPPN** | `src/CORE/WORMS/expansion/cppn.py` | genome-size ceiling | 221 |
| **Device** | `src/CORE/device.py` | scattered `torch.xpu` probes | 217 |

Tests: `tests/test_proteus_organs.py` — **98 tests**.
Gate: `scripts/verify_proteus.py` — dual-interpreter smoke check, exits non-zero on failure.

## 2. Verified, not asserted

```
tests/test_proteus_organs.py ............................ 98 passed
scripts/verify_proteus.py   (GIL)            ALL ORGANS OK (GIL)
scripts/verify_proteus.py   (python3.14t)    ALL ORGANS OK (free-threaded)
tests/test_evolution_gates.py + helpers       171 passed (no regression)
```

Both interpreters is not ceremony: the pipeline runs free-threaded, where
`torch` and `numpy` **cannot load** (ABI `cp314` vs `cp314t`). Every organ
therefore carries a stdlib path, and `verify_proteus.py` proves it:
`get_device()` reports `torch=False numpy=False` under `python3.14t` and all
organs still pass.

The **Oracle artifact is 105 KB** (`state/fitness_oracle.pt`), well inside the
"if it does not fit in a few hundred MB, it does not ship" constraint — the
Arc 140T's 7.8 GiB is shared with 16 GB of system RAM.

## 3. The gate earned its keep — two real bugs

Both were invisible to inspection and to the pytest suite; only the free-threaded
run found them.

**Bug 1 — every structural mutation was lethal.** Production names the gene
`discount`; `train_from_memory` accepts `discount_factor`. `Genome.from_flat`
set `kwargs = name`, so `discount` resolved to an unknown kwarg and *every*
child inheriting it was rejected. Morph would have looked functional while
silently producing nothing. Fixed with `GENE_KWARG_ALIASES` + `resolve_kwarg()`,
normalised at `GeneSpec.__init__` so no caller can reintroduce it.
Regression test: `test_children_of_production_genome_are_viable`.

**Bug 2 — `UnboundLocalError` in Loom.** `spectral_summary` bound `eigs` only
inside `if _np is not None:`. Under free-threading `_np` is `None`, so the
fallback read an unbound local. Fixed by pre-binding, with a comment saying why.
Regression test: `test_spectral_summary_without_numpy`.

Two more issues were found in the same run — `dimension_report` silently merging
rows with no recorded dimension into a bucket labelled "dimension 0" (precisely
the cross-dimensional comparison it exists to prevent), and `viability` reporting
`out_of_range` for a `nan` because `nan` fails every comparison. Both fixed.

## 4. What is wired into production

**Exactly one thing: the Oracle counterfactual-era gate (Phase C).**

`scripts/evolution_cycle.py` gained `_oracle_gate()` — inserted **after** the
holdout, **before** the promotion write — behind an off-by-default flag:

```bash
AZAZAEL_PROTEUS_ORACLE=1        # enable (default 0)
AZAZAEL_PROTEUS_MIN_P=0.75      # era-robust probability required
AZAZAEL_PROTEUS_MIN_ROWS=60     # refuse below this much history
AZAZAEL_PROTEUS_EPOCHS=150
```

Live result on real history, candidate at `lr=0.6532 discount=0.5668`:

```
n_imagined_eras  : 74          (distinct era descriptors from evolution_result)
threshold        : 26.5        (= baseline 25.5875 + PROMOTE_MARGIN 0.75)
pred_mean        : 26.2384     <- clears the baseline on its point estimate
pred_sd          : 1.1244
era_robust_p     : 0.0         -> BLOCKED
```

That is the E9 fix working. The genome beats the baseline on its point estimate —
which is exactly what a margin-based gate would have promoted — but does not
clears `baseline + margin` across imagined eras once uncertainty is counted, so
it is refused. Falsifiable against ANIMA criterion 1 (holdout pass rate, 0/4).

Disabled, the cycle is byte-identical to before (verified: a live cycle with the
flag unset logs `beats=False`, promotes nothing, and writes zero extra state).

## 5. What is deliberately NOT wired

Everything else. Constraint 5 of the plan — *one variable per batch* — forbids
landing Morph (which changes the genome) and Arena (which changes the world)
before either is measured. Landing both now would reproduce the confounding we
avoided when we widened bounds *before* adding a gene.

Remaining phases, each independently falsifiable:

| Phase | Organ | Measured by | Status |
|---|---|---|---|
| **C** | Oracle gate | holdout pass rate > 0 | **wired, off by default** |
| **D** | Circulation + Cranium | operator spread; evidence spans ≥3 eras | modules ready |
| **E** | Morph | genome dimension grows then stabilises | modules ready |
| **F** | Arena | transfer success; novelty never zero | modules ready |
| **G** | Nerve, Loom, Chorus | learner ceiling; intrinsic dimension; proposal acceptance | modules ready |

Recommended order: run C to a *measured* verdict first. If imagined-era gating
does not move the holdout rate off 0/4, the Oracle is not modelling anything
useful and D–G are moot.

## 6. Honest risk, restated

Metamorphic genomes make results **incomparable**: once the genome can grow,
"fitness 25.04" no longer means the same thing between dimensions, and every
historical comparison in this repo becomes era-specific in a new way.

The mitigation is implemented, not just intended: `Genome.dimension` is part of
every genome, and `morph.dimension_report()` groups headline numbers by
dimension and **refuses to bucket rows with no recorded dimension** — so the
discipline cannot be skipped by omission.

## 7. Phase D and E — WIRED (2026-09-12)

`PROTEUS_ORACLE` (Phase C) is no longer the only organ reachable from the
pipeline. Three flags were added to `scripts/evolution_cycle.py`, all default
**off**, each moving exactly ONE variable per batch:

| Flag | Phase | Wires | Replaces |
|---|---|---|---|
| `AZAZAEL_PROTEUS_CRANIUM=1` | D | `cranium_decide` + `cranium_override` after the SPRT | a hard stop that reset evidence at every `pool_id` change |
| `AZAZAEL_PROTEUS_CIRCULATION=1` | D | `circulation_decide` / `circulation_update` | `_cma_wanted = margin < 2 * PROMOTE_MARGIN` |
| `AZAZAEL_PROTEUS_MORPH=1` | E | `morph_gene_specs` at population init + `morph_trainer_kwargs` in `_eval_salt` | the fixed 4-gene genome |

All three are **fail-open**: a hook error logs and the legacy path continues.
State lives in `state/proteus_circulation.json` and `state/proteus_morph.jsonl`.

### Measured, live (`scripts/run_evolution_n.py`, production `python3.14t.exe`)

```
flags OFF      3 cycles   0 new log lines, 0 errors       <- regression clean
MORPH         10 cycles   rotation 0..9; dims {5:9, 4:1}     <- 4 was defect #6
MORPH (fixed) 12 cycles   dims {5:12}, genes 6/6, 1 promotion
CIRCULATION    6 cycles   arm set {ga,cma,de}; credited arm == funded arm, 6/6
CRANIUM       15 cycles   0 beats=True  -> organ not reached (see below)
ALL ON        12 cycles   0 errors, 0 FATAL, dims {5:24} across batches
```

Live defect discovery timeline (each found only by running the real pipeline):

| Defect | Symptom on the wire | Found by |
|---|---|---|
| `"kind"` vs `"type"` | bool gene sampled as a continuous coordinate | engine round-trip test |
| Phantom arms credited | `arena` funded, `cma` credited | circulation log vs allocator state |
| Repeated margin as evidence | 58 rows of identical 3.295 counted as 58 obs | real-store dedup count (201/400) |
| Unidentifiable variance | `sd 5.8e-07` -> `p 1.0000` -> promote | degeneracy probe |
| Seed gene accumulation | `dimension: 6`, both genes present | morph artifact histogram |
| Arm win drops the gene | `dimension: 4`, `extra: {}` | morph artifact histogram |

### Four real defects the wiring exposed

Every one of these was invisible to unit tests that exercised the hooks alone.

1. **`"kind"` vs `"type"`.** `morph_gene_specs` emitted `"kind"`; the engine reads
   `spec.get("type", "float")`. A gene declared `bool` became a **continuous
   coordinate**, then collapsed to `True` by `bool(v)`. The engine's own sampling
   was the only thing that could reveal it, so the round-trip test now drives
   `EvolutionEngine` itself.

2. **Phantom arms credited to a real one.** The allocator chose from the
   plan-level `PROTEUS_ARMS` (7 organs). It drew `arena`, `morph`, `chorus`; the
   cycle ran the slot-alternating `cma` arm; feedback credited **`cma`** — three
   posterior updates for an arm never selected. A decision set wider than the
   executable set cannot help but mislabel. Fixed by narrowing to `SEARCH_ARMS
   = (ga, cma, de)`.

3. **A re-recorded margin counted as new evidence.** One live era held **58 rows
   with margin 3.295 on every one**. Identical margins are the same evaluation
   repeated, but they shrink the posterior sd and push `p_above` toward
   certainty. On the real store **201 of 400 rows were repeats** (evidence units
   401 -> 199). The verdict held (mean 1.081 -> 1.111), so this was overcounting
   rather than a wrong answer — but it was overcounting.

4. **Unidentifiable variance reported as certainty.** Three coincident era means
   gave `sd = 5.8e-07` against a 0.75 threshold — ~1.3M sigma of claimed
   clearance — hence `p_above = 1.0000` and a proposed promotion. Two guards:
   Cranium now **defers to the SPRT when `n_eras < 2`** (it is a pooling organ;
   with one era it has nothing to pool), and the sd floor scales with the
   threshold instead of being an absolute epsilon. `deferred` is surfaced in the
   reading so a refusal is distinguishable from a finding.

5. **Dimension crept 4 -> 5 -> 6 and never came back.** Seeds come from
   `last_best_genes()`, i.e. the PREVIOUS cycle's winner, which carries whatever
   extra gene that cycle trialled. `EvolutionEngine.initialize_population`
   fills MISSING genes from the current specs but never **prunes** extras, so a
   seed carrying `by_session` entered the next cycle (which added
   `use_schema_features`) and left with both. The live artifact contained a
   row with `dimension: 6` and `extra: {by_session, use_schema_features}`.
   Fitness stopped being comparable across rows AND the per-gene verdict was
   confounded. Fixed by `morph_strip()` on every seed.

6. **A secondary-arm win silently dropped the extra gene.** `_run_cma_arm`
   built its optimiser from the 4-key `GENE_BOUNDS`, so when CMA/DE won, the
   winner had no extra gene at all (measured: cycle 8, `dimension: 4`,
   `extra: {}`). The cycle now passes 4+1 bounds, with the switch offered to the
   continuous optimiser as a `(0.0, 1.0)` coordinate. That in turn required
   thresholding numeric bools at **0.5** in `morph_trainer_kwargs` — `bool(0.3)`
   is True, so without it almost every CMA candidate would have read as
   "switch on" and the relaxed search would not have agreed with the GA.

After both fixes, 12 live cycles record `dims {5: 12}` with a clean 6/6
rotation, and a 24-row history is `{5: 24}`.

### Morph cannot promote, by design

A 5-gene genome is scored **with** the extra gene active (`_trainer_extra_kwargs`),
but production evaluates with only the four genes unless Morph is also on —
`production_genes()` deliberately reads just the four. Promoting it would write a
champion whose recorded fitness does not describe how it will be scored, which is
precisely the incomparability the plan warned about. So the promotion is
**withheld** while a trial gene is present, the log says so, and
`proteus_morph_gene` is written into any promotion artifact for traceability.

### Cranium: wired and correct, but NOT REACHED

This is the honest headline. Cranium is guarded by `beats` — it only supplies
cross-era evidence for a candidate that already cleared the margin gate.
**25/25 live cycles had `beats=False`** (margins 0.02–0.5 against a 0.75 gate),
so the organ never executed in production.

It is not broken. `scripts/_cranium_reality_check.py` runs it against the real
store under **both** interpreters with identical output:

```
23 eras pooled, 199 evidence units
posterior 1.1113 +- 0.1705   p_above = 0.983   -> promote -> rescue
```

So the finding is: Cranium is reachable only in a regime the current pool does
not produce. It is verified by construction (`cranium_override` extracted as a
pure function with 12 tests) precisely because it cannot be verified by
observation right now.

### Circulation: the feedback signal is currently degenerate

Every funded secondary returned outcome `flat`, because `flat` is what a cycle
that never beats the baseline earns. Both `cma` and `de` therefore decay toward
the floor while `ga` holds its prior — the allocator is working correctly on a
signal that carries no information yet. **It cannot say anything until at least
one cycle reaches `beat_baseline`.**

### Morph: first measurement verdict

`use_schema_features` and `by_session` both landed at `False` in 4/4 cycles.
A probe (`scripts/_morph_polymorphy_probe.py`) rules out flattening: the switch is
sampled ~50/50 at gen 0, stays `bool`-typed through crossover and mutation, and
converges to `True` under a `True`-favouring fitness. So the live `False` winners
are **selection**: both flags genuinely score worse on the real objective so far.
Four cycles is not a verdict — it is the first data point, and it is recorded
per-dimension by `morph_record` exactly because fitness is only comparable within
one.

## 8. Reproduce

```bash
C:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest tests/test_proteus_organs.py tests/test_proteus_hooks.py -q
python scripts/verify_proteus.py
C:/Azazael/.venvs/py315t/Scripts/python.exe scripts/verify_proteus.py

# Phase C
AZAZAEL_PROTEUS_ORACLE=1 python scripts/evolution_cycle.py

# Phase D (one variable at a time) — NOTE: run_evolution_n.py retired 2026-10-11
# (see archive/retired-trainers-2026-10-11/); Phase D steps need a live runner
AZAZAEL_PROTEUS_CRANIUM=1 python scripts/run_evolution_n.py --runs 10
AZAZAEL_PROTEUS_CIRCULATION=1 python scripts/run_evolution_n.py --runs 10

# Phase E
AZAZAEL_PROTEUS_MORPH=1 python scripts/run_evolution_n.py --runs 10
python scripts/_morph_polymorphy_probe.py

# Cranium on real history, both interpreters
python scripts/_cranium_reality_check.py
C:/Azazael/.venvs/py315t/Scripts/python.exe scripts/_cranium_reality_check.py
```
