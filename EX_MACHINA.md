# EX MACHINA — the epistemic organ wallboard

**Status:** implemented, verified under both interpreters, live in `scripts/exmachina_live_monitor.py`
(its own viewer - the panel is NOT injected into `scripts/live_monitor.py`).
**Modules:** `src/CORE/WORMS/expansion/exmachina.py` (17 organs, severity model, mood band),
`src/CORE/WORMS/expansion/exmachina_operators.py` (operator tier, pure stdlib).
**Tests:** `tests/test_exmachina_operators.py`. **Gates:** `scripts/verify_exmachina.py`,
`scripts/verify_exmachina_panel.py`.

---

## 1. Why a wallboard and not a report

The evolution pipeline already produces a trajectory, an SPRT decision, a Pareto front, a
holdout result and a promotion flag. Every one of those is a **point estimate with no
self-doubt**. E9 is the concrete failure: a candidate showing `margin +3.3` on the snapshot
bought **0/4 holdout passes**. Nothing in the pipeline could say "the objective is rising
while the independent check is not", because every measurement was reported as though it were
evidence of quality.

Ex Machina is the layer that asks whether the numbers mean anything. Each organ is a
*falsifiable claim about a failure mode*, not a metric with a nicer name.

## 2. The 17 organs

Each entry: **thesis** (what it asserts) / *breaks* (the failure it exists to catch).

| Organ | Thesis | Breaks |
|---|---|---|
| **SPECULUM** | reward hacking: objective rising while a held-out proxy falls | E9 went undetected for 50 cycles |
| **FULCRUM** | compression-based novelty (normalised compression distance) | Loom's spectral ID measures spread, not information |
| **TESTUDO** | conformal prediction: finite-sample coverage, no distributional assumption | `min_prob=0.75`, `z=1.0` in the oracle gate are asserted, not calibrated |
| **RADIX** | causal discovery (PC/GES/FCI) over the evidence graph | the graph audit called person-to-harm attribution the highest-leverage task |
| **CATENA** | trust-region Bayesian optimisation over a deep ensemble | one global surrogate is flat exactly where it matters |
| **NAVIS** | reservoir computing (echo-state): train only the readout | reaches past the tabular Q-table with no backprop and no C extension |
| **VELA** | hyperdimensional binding of (entity, relation, claim) | string-keyed lookup cannot answer "what else looks like this lie?" |
| **NEXUS** | sparse mixture-of-experts routing across evidence types | raises capacity inside the 8 GB shared budget via top-k |
| **OPUS** | Kolmogorov–Arnold spline-edge backbone as an Oracle alternative | more expressivity per parameter than an MLP at equal memory |
| **LIMEN** | active learning: rank missing documents by expected information gain | outreach is ordered by narrative, not information value |
| **VIGIL** | anytime-valid evidence: a test martingale (e-process) | SPRT is a 1945 fixed-sample test and we peek every cycle |
| **FILUM** | degeneracy and memory of the outcome series (permutation entropy + DFA) | Loom measures genome spread, not whether the search still finds anything |
| **PERENNIS** | era invariance: which predictors keep the same slope in every era | E9 *is* a non-invariant fitness→quality relation |
| **COMPAGES** | cointegration: is there a long-run link between margin and the independent check | a margin trending up while the holdout never moves is non-cointegrated by definition |
| **BREVIS** | two-part MDL: bits for the genome plus bits for the residuals | "fitness up" is not free evidence if description length grew to buy it |
| **EMERGON** | causal emergence: effective information of the macro grain minus the micro grain | organs may be most legible grouped (belief-organs vs measure-organs) |
| **MUTAGEN** | genome selection: did the genome grow, or was it given away? | Phase E retains a structural mutation on a trial that never changed the trainer call (the added gene resolved to the trainer's own default — for `by_session`, default **True**, that is the *on* value), so dF measures the comparison, not the gene |

`ORGANS` in `exmachina.py` is the single registry; `organ_readings()` and
`epistemic_report()` iterate it, so adding an organ does not mean editing the panel.

## 3. Severity, mood, vitality, heartbeat

* `severity_vector(signals)` → weighted severity with a **worst-signal** term, so one organ at
  hard alarm cannot be averaged away by twelve healthy ones.
* `mood_for(sev)` → a band, with hysteresis so the display does not flicker between adjacent
  cycles. Live reading on the current store: **`alarmed`**, driven by
  `non_invariance = 1.00` (PERENNIS: 0 of 6 predictors stable across eras).
* `vitality(rows, field="margin", order=3)` → permutation entropy + DFA over the outcome
  series; separates "still exploring" from "repeating itself".
* `heartbeat()` → phase of the 30 s cycle the panel is drawn against, which is what makes the
  panel look *alive* rather than merely current.

## 4. The panel

The Ex Machina panel is one screen, ASCII-safe by default, restructured around:

```
|-- EX MACHINA -- :O ALARMED 0.32 | 10 judged + 7 operators -------|
| :O o [===-] alive [|||||...]  ~ vitality 0.86 exploring          |
| SEVERITY [####--------] 0.32  active 12 worst non_invariance 1.00|
| ! non_invariance  [##########] 1.00  <claim>                     |
| ~ VITALS x 3/6     alloc 7m  archive 4m  gate 1h STALE  morph 7m  |
|  SPECULUM  + OK      gaming 0.00 margin +1.59 hold 2/6           |
| + OPERATORS + 7   RADIX 6n/4e linked  CATENA r=0.040  ...        |
| o ORACLE + on     500 rows 87 eras 5 models 510KB loss 0.324     |
| m MORPH + grown   6 gene  dims [4, 5, 6]  best4=24.234           |
| # PROTEUS x BLOCKED gate=BLOCKED era_robust_p=0.0                |
```

The **CRANIUM** row reports the cross-era verdict when one exists and otherwise states
`not reached — margin gate has not passed (no cross-era test)`. That distinction is deliberate:
Cranium fires only after the margin gate passes, so "no test" and "no evidence" are different
facts, and conflating them is the E2 failure this codebase already paid for once.

### Glyph tiers — measured, not assumed

Emoji are `No` by default, and that is a measurement rather than a preference:

* **Width.** `△ ◇ ◎ ◆ □ ↻` are East-Asian-**Ambiguous**: under a CJK font they render two
  columns and wrap the panel. They were replaced with verified N-neutral glyphs
  (`+ - x ! ~ o #`), and the rule is enforced in code.
* **Codepage.** The Windows console codepage is not UTF-8 by default, so non-ASCII glyphs can
  arrive as mojibake.
* **Tiering.** `_GLYPH_TIERS` provides `ascii` → `unicode` → `emoji`, selected by
  `detect_glyph_tier()` from the console's actual capability, with
  `AZAZAEL_EMOJI=1` as an override. Every tier is render-checked at 120 columns and at a
  narrow 80 columns, and the verifier asserts **no tier wraps** — wrapping is the failure mode
  that destroys a fixed-layout panel, whereas truncation is survivable.

`_vis_len` measures printable width so colour escapes contribute zero columns; a `%-7s` applied
to a colour code pads the escape sequence rather than the text, which is a real bug that the
width guard caught.

## 5. What verification actually found

The gate is `scripts/verify_exmachina.py` (organs) and `scripts/verify_exmachina_panel.py`
(render). They are what turned these up:

1. **Misaligned columns.** Per-key column lists were not row-aligned, so every correlation
   described a dataset that does not exist. Fixing it **flipped RADIX's verdict**
   (`independent_of_check` → False), confirming the earlier reading was the misalignment.
2. **A constant column read as d-separation.** `causal_absence = 1.0` came from a constant
   `_promoted` column — "absence of evidence" reported as "evidence of absence". The same
   pattern had already been caught once in COMPAGES cointegration.
3. **COMPAGES calibration.** A single sample looked like a false positive; a size/power study
   over many draws showed size ≈ 2–6% and power ≈ 1.0, i.e. well calibrated. The one bad draw
   was the 5% case, so the organ was right and the test was wrong.
4. **A bump-basis KAN was not a spline.** The original basis interpolated only mildly better
   than linear; it was replaced with a proper Cox–de Boor B-spline.
5. **Narrow-width truncation.** At 80 columns the operator row silently dropped `LIMEN`, so the
   panel could report 7 operators while showing 6.
6. **`_vis_len` guard claimed a rule it did not implement.** The width guard documented an
   ambiguous-width rule it never enforced; two emoji glyphs were in fact narrow. Both fixed and
   locked by the verifier.
7. **Two stale artifact paths made the panel lie.** The monitor watched
   `proteus_allocator.json` and `logs/morph_history.jsonl`; the cycle writes
   `proteus_circulation.json` and `state/proteus_morph.jsonl`. Nothing produces the former
   paths, so the allocator's age was never reported and the **CIRC row read "idle" while the
   allocator was actively learning**, exactly the failure this panel exists to prevent. Both
   paths now match their producers, and VITALS reports `alloc 7m` / `morph 7m`.
8. **`\u25cb` for the new CRANIUM row was EAW-ambiguous.** The obvious white-circle glyph
   would have wrapped under a CJK font — the precise trap documented three lines above it.
   Candidates were measured (`EAW=A` → reject) and `U+229A` (`EAW=N`) was used instead; the
   emoji tier uses MICROSCOPE rather than BRAIN, since BRAIN is already the PROTEUS glyph and
   a duplicate glyph makes two rows read as one.

## 6. Verification record

```
verify_exmachina.py          (GIL, python.exe)   ALL OK  (0 failures)
verify_exmachina.py          (python3.14t.exe)   ALL OK  (0 failures)   <- identical output
verify_exmachina_panel.py                        ALL OK  (0 failures)   3 sizes, 2 tiers
tests/test_exmachina_operators.py                36 passed
cost per full report                             0.043 s  (safe in a 30 s loop)
```

Both interpreters produce **byte-identical** organ reports, which matters because the
production runner executes every cycle under `python3.14t.exe` where `numpy` and `torch`
cannot load at all. The operator tier is therefore pure stdlib by construction, not by luck.

## 7. Honest limits

* **TESTUDO is uncalibrated.** It reports achieved coverage **0.225 against a 0.90 target**.
  The panel shows this as `UNCAL` rather than hiding it; a conformal band that does not cover
  is worse than no band, and the organ is reporting its own failure correctly.
* **PERENNIS reports 0/6 invariant predictors**, which is what drives the `alarmed` mood. That
  is a finding about the data, not a bug in the organ.
* **COMPAGES currently reports `NO LINK`** (`t = -2.7675` against a critical value of
  `-3.396`). Margin and the independent check are not cointegrated on the current history.
* **EMERGON reports negative emergence** (`-0.157 bits`, best grain `bit0+1`): the macro
  grouping carries *less* effective information than the micro grain, so grouping the organs
  is currently not justified by the data. The organ says so rather than inventing a grouping.
* `LIMEN` reports `idle` until it is handed an evidence set; it is an operator, not a
  passive meter, so it has nothing to say without a candidate queue.

---

## 8. Hyperoptimized run — all phases live (2026-09-12)

### 8.1 What changed

The scheduled task `Azazael-EvolutionCycle` ran
`scripts/run_evolution_cycle_314t.bat`, which sets **no** PROTEUS flags. Every phase was
therefore running at its default, and the default is **OFF** — so the scheduler had been
running the *baseline* search the entire time while the phases sat wired, tested, and
inactive. That is the same class of failure as the two stale monitor paths: a component
that exists, is correct, and is never reached.

Created `scripts/run_evolution_cycle_hyper.bat`, which enables every wired phase for that
process only:

| Flag | Phase | Effect |
|---|---|---|
| `AZAZAEL_PROTEUS_ORACLE` | C | imagined-era robustness pre-gate |
| `AZAZAEL_PROTEUS_TRAIN` | C | allow GIL-side oracle retraining |
| `AZAZAEL_PROTEUS_CRANIUM` | D | cross-era pooled decision at the SPRT site |
| `AZAZAEL_PROTEUS_CIRCULATION` | D | Thompson allocator replaces the fixed 2x gate |
| `AZAZAEL_PROTEUS_MORPH` | E | one extra structural gene, round-robin trialled |
| `AZAZAEL_TENSOR_GENOME` | — | genes as self-declaring tensors (the deliverable) |

`Azazael-EvolutionCycle` was repointed to this launcher. The previous task XML is backed
up under `state/task_backups/`. Cadence unchanged (`PT5M`).

### 8.2 Proof it runs

A 24-cycle batch through the production runner (`run_evolution_n.py`, which spawns every
cycle under `python3.14t.exe`) — runner retired 2026-10-11, see `archive/retired-trainers-2026-10-11/`:

```
circulation: arm=            24 / 24 cycles
cranium: action=             24 / 24 cycles
oracle gate:                 28 evaluations
tensor genome:               32 artifact writes
promotion BLOCKED by oracle  23
morph gene present           132 rows
FATAL / Traceback / error:   0
```

Then a live run through the **scheduler itself** (`Start-ScheduledTask`):
`LastTaskResult = 0`, full cycle in ~25 s, next run scheduled. That cycle shows all five
phases in one pass:

```
morph: stripped prior extra genes from 3 seed genome(s)
morph: cycle 47 adds gene by_session (kind=bool)
circulation: arm=ga weights={'cma': 0.6122, 'de': 0.5366, 'ga': 0.5} -> secondary skipped
cranium: action=agree (sprt promote -> promote) deferred='single era: no cross-era pooling available'
promotion standing: beats=True margin=1.33 sprt=promote(n=7 llr=82.26)
promotion BLOCKED by oracle counterfactual-era gate: era_robust_p=0.0345 < 0.75
tensor genome: 5 genes width 20 identifiable 5/5 most=discount
```

### 8.3 The result that matters

**The Oracle pre-gate blocked a promotion that had already passed `beats`, `sprt=promote`
and `pareto`.** In the batch it did so 23 times. Phase C is not decorative — it is the
only gate in the chain that reads *counterfactual* eras, and on this history it is
strictly more conservative than the gates downstream of it.

That is a finding, not a success to be assumed: a gate that blocks ~100% of promotions is
as uninformative as one that passes everything. The honest reading is that the current
champion is predicted at `pred_mean 22.43` against a required `threshold 21.58` with
`pred_sd 1.29` — i.e. the candidate is *individually* fine but does not clear the bar in
enough of the 87 imagined eras. Whether the bar is set right is an open question, and it
is recorded as such rather than tuned until the gate agrees.

Separately, `cranium` reports `deferred: 'single era: no cross-era pooling available'` in
every cycle. The guard added on 2026-09-12 is working: one era cannot support a pooled
decision, so Cranium defers to the SPRT instead of manufacturing confidence from a
single-observation variance.

### 8.4 Defect the run exposed

The morph gene rotation holds two candidates, `use_schema_features` and `by_session` —
**neither is named `morph_switch`**. The tensor-genome builder hardcoded that name, so the
real gene was declared `kind=float`, `provenance=unknown` for every row that ever carried
one. Fixed by deriving the kind and provenance maps from `MORPH_CANDIDATES` itself, which
is the single source of truth:

```
before   use_schema_features   kind=float  prov=unknown   rho=-0.3572
after    use_schema_features   kind=bool   prov=morph     rho=-0.3572
```

This is the third instance of the same failure mode in this workstream: a name written by
hand that the producer never emits. The lock for it is that the maps are now *read from*
the producer rather than restated.

### 8.5 Verification

```
324 passed    tensorgene(63) + proteus_hooks(59) + proteus_organs(98) + operators(40)
              + monitor paths(9) + monitor split(10) + mutagen(27)
              + sprt remeasurement(18)                          [python.exe]
ALL OK        verify_exmachina.py          python.exe  and  python3.14t.exe
ALL OK        verify_exmachina_panel.py    python.exe  and  python3.14t.exe
ALL ORGANS OK verify_proteus.py            GIL and free-threaded
```

The panel now carries the deliverable:

```
 t TENSOR + declared 4 genes  width 16  2/4 above floor  500 rows
   + discount       [###-----] -0.313 down  n=265
   + epsilon_decay  [##------] +0.230 up    n=265
   z compiles to in=16 hidden=32x16  UNTRAINED spec
```

Reachability is now **checked rather than assumed**: the first version of these rows was
gated at `height >= 40` while `live_monitor` defaults to a 100x30 window, so the
deliverable would have been invisible in the default window. `verify_exmachina_panel.py`
now asserts that every declared row appears at the default window and that no height
overflows.

### 8.6 Follow-through: the producer stopped crediting inert trials

MUTAGEN measuring the defect is not the same as the defect being fixed, and the measurement
was only ever half the problem: **nothing in the producer refused to credit a null trial**. A
cycle whose added gene resolved to the trainer's own default still appended a row whose
`fitness - baseline_fitness` looked like a win.

The correction rests on one fact read from the trainer itself
(`RLTrainLoop.train_from_memory`, `learning_rl.py:302-303`): the defaults are
`use_schema_features=False` and **`by_session=True`**. So "inert" is not "off" — it is "the
trainer was called exactly as production calls it", and for `by_session` that is the *True*
value. Re-measured on the ledger, that reclassification is not cosmetic:

```
before (resolved-True == treatment)      after (resolved == trainer default)
rows 69   inert 45/69 (65%)              rows 69   inert 52/69 (75.4%)
by_session    29 trials 15 inert         by_session    34 trials 17 inert, 17 CHANGED
use_schema_features 30 trials 30 inert   use_schema_features 35 trials 35 inert, 0 changed
```

`proteus_hooks.py` now carries `MORPH_TRAINER_DEFAULTS`, `morph_effective` and `morph_is_inert`;
`morph_record` stamps `applied` (the kwargs the trainer actually received) and `inert` on every
row; `morph_dimension_summary` computes its per-gene verdict from EFFECTIVE trials only and
reports a never-treated gene as `tested: False` with a note instead of as a winner. Rows written
before the stamp are re-derived on read, so the fix is retroactive rather than prospective.
`evolution_cycle.py` logs the verdict at record time, so a null cycle is distinguishable from a
win in the place anyone looks first.

And the trial itself is now informative rather than merely labelled. Each morph
cycle runs a **matched A/B**: the same champion on the same frozen pools, with one
gene moved from the trainer's default to the value that changes the call
(`use_schema_features` -> True, `by_session` -> False). `ab.delta = treatment -
control` is attributable to that gene by construction, because nothing else
differs, and it costs ~4% of a generation. MUTAGEN reports it separately
(`measured_trials`, `ab_mean`, `ab_p`, `never_measured`) instead of folding it into
the confounded fitness comparison.

The mirror is locked to the producer twice over: `MORPH_TRAINER_DEFAULTS` is asserted against
`inspect.signature(RLTrainLoop.train_from_memory)` in the tests, and on the tier side
`_MORPH_TRAINER_DEFAULTS` is asserted equal to the producer's table. The organ also prefers the
ledger's own stamp and counts `inert_disagreements` when its mirror would have said otherwise,
because that drift is the one failure a mirror cannot detect by itself.

### 8.7 Known pre-existing failures (not introduced here)

Four failures exist in the wider suite and are unrelated to this workstream:

```
tests/test_concurrency_200.py::test_200_concurrent_writes   database is locked
tests/test_concurrency_200.py::test_session_gc_under_load   DirectMemory has no session_gc
tests/test_config_and_breaker.py::TestPamsConfig::test_from_dict   url mismatch
tests/test_dm_advanced.py::TestSessionGC::test_close_stale  no such table: sessions
```

They are recorded here so they are not mistaken for regressions from this change.
