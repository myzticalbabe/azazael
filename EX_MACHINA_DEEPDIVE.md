# EX MACHINA — deep dive: techniques considered, and the MUTAGEN organ

**Status:** design note + implementation record for the 17th organ (`MUTAGEN`), 2026-09-12
**Companion to:** `EX_MACHINA.md` (the 16 organs as shipped)
**Modules:** `src/CORE/WORMS/expansion/exmachina.py` (judge tier), viewer `scripts/exmachina_live_monitor.py`

This file is referenced from the `exmachina.py` module docstring ("see
`EX_MACHINA_DEEPDIVE.md` for the techniques that were considered and rejected"). It did not
exist until now. It records the techniques that were evaluated for the genome layer and the
one that survived into an organ.

---

## 1. The gap

Every organ in the judge tier reads the **outcome series** — margin, holdout, promotion — or a
derived artifact (the QD archive, the tensor genome's usefulness). None of them reads
`state/proteus_morph.jsonl`, and that is the ledger that decides the genome's *shape*.

Phase E (Morph) appends one row per cycle: which extra gene was trialled, the genome's
dimension, the trial fitness, and the baseline it was compared against. **That file is the
genome's own record of whether adding a gene helped.** It had no organ. In a tier whose entire
purpose is "decide whether to believe the optimiser", that is the largest remaining unread
artifact — the fitness function for growing the genome, believed on faith.

## 2. What the ledger actually says (measured, not asserted)

Read from `state/proteus_morph.jsonl` and `state/tensor_genome.json`, 2026-09-12:

```
trials 59   contiguous cycle_index 0..58 (no gaps)   distinct genes 2
retained (dF > 0) 58 / 59        retention 0.9831
dF  mean +0.9341  sd 0.6211  min -0.0537  max +2.0526
corr(dF, baseline_fitness) = -0.1962
all rows at dimension 5  ->  no dimensional background variation
```

A 98.3% retention rate is not a result, it is a **red flag**. A selection operator that rejects
1 in 59 candidate changes is not selecting. Binomial P(>=58 of 59 | p=0.5) = **1.0e-16**.

So the obvious next question is: what did the retained genes *do*? The ledger records the gene's
raw value in `extra`, and the producer resolves that value to its effective switch through
`proteus_hooks.morph_trainer_kwargs` -> `_as_bool`, which **thresholds at 0.5**. Resolving every
trial the way the trainer does:

```
gene                  trials  retained   provably-INERT trials   mean dF on inert trials
use_schema_features     30     30/30        30/30 (100%)          +0.9308  all positive  P=9.31e-10
by_session              29     28/29        15/29 ( 52%)          +0.9367                P=3.05e-05
------------------------------------------------------------------------------
TOTAL                   59     58/59        45/59 ( 76.3%)        +0.9328  44/45 positive  P=1.31e-12
```

`use_schema_features` was trialled **thirty times with the switch resolved OFF in all thirty**
(raw values `0.0563`, `0.0686`, `False` — nothing that clears 0.5). The trial arm and the
baseline arm therefore compute the *same* model. And it was retained 30/30, mean dF **+0.93**.

A gene that is switched off in the trial arm cannot have produced the gain. The conclusion is
forced and it is narrow:

> `fitness - baseline_fitness` in this ledger is not measuring the gene. It is measuring the
> **comparison**. The Morph phase has been growing the genome for free, and no organ noticed.

Two further readings agree that the gene's value is inert rather than merely weak:

* `by_session` resolves True in 13 trials and False in 15; mean dF **+0.8526 vs +0.9367** — the
  *off* value scores **higher** than the on value, so the value is not weakly predictive, it is
  anti-predictive.
* `corr(dF, baseline_fitness) = -0.1962`: when the baseline is higher the gain is smaller, which
  is the signature of a comparison against a systematically stale reference rather than of a
  gene effect.

Meanwhile `state/tensor_genome.json` reads the *same* gene the other way round:
`use_schema_features |rho| = 0.3347` — the most "useful" gene in the genome. The tier now holds
two artifacts that contradict each other about the same coordinate, and nothing compared them.

## 3. The genomics mapping — used, not decorative

The organ is named for biological mutagenesis because the mapping is exact, not because it
sounds well.

| Genomics | Here |
|---|---|
| **dN/dS (omega)** — nonsynonymous vs synonymous substitution rates; >1 positive selection, <1 purifying, ~1 neutral drift | structural retention (a gene's *existence/kind* changes) vs the value-level differential within a gene. Structural retention 0.983 with a value differential of **-0.084** is the "elevated dN/dS with no adaptive signal" case — apparent positive selection that is an artifact |
| **provably inert allele** | a trial whose gene resolves OFF: behaviourally identical to the baseline arm, so any dF is unattributable |
| **genetic load** — the fitness burden of deleterious alleles a population carries | `1 - mean(|rho|)/max(|rho|)` over the tensor genome = **0.3924**, with `learning_rate` (0.145) and `epsilon` (0.0365) below the 0.15 floor and `epsilon` carried for 297 samples |
| **mutational spectrum** — which mutation *types* a system actually suffers | `scripts/mutate.py`'s five AST operators. **Not recorded per-operator**, so the spectrum is not measurable today (see §6) |

## 4. The organ

**MUTAGEN** (17th, judge tier) — *thesis*: a genome can grow without selection, retaining
structural mutations whose added gene was switched off in the trial that justified it.
*Breaks*: Phase E retains on an unattributable dF, so genetic load accumulates and the genome's
dimension stops meaning anything.

`mutagenesis(morph_rows, genome=None, mutation=None, floor=None) -> dict` — pure stdlib, never
raises, mirrors the tier's contract. It reports:

```
trials, retained, retention          the selection rate, with the binomial that says
                                     whether it is distinguishable from no selection
inert_trials, inert_share            trials whose gene resolved OFF
inert_gain, inert_positive, inert_p  mean dF on those trials  <- THE claim
value_effect[gene]                   mean dF(on) - mean dF(off); ~=0 means the value is inert
load_share, load_below               genetic load from the tensor genome
tests: mutants, killed, score,       the test suite's own mutational evidence
       lower (Wilson 95%), age_h
resolver                             "producer" | "threshold:0.5" | "none"  <- which
                                     resolution path was used, stated not assumed
free_growth                          the severity signal in [0,1]
```

`free_growth = inert_share * (1 - min(1, p/0.05))`, i.e. the share of the ledger that is
provably unattributable, discounted by how strong the evidence is. On today's data: **0.7627**.

Two design rules are inherited deliberately:

* **Absence is not calm.** With no `morph_rows`, MUTAGEN reports `unavailable` and contributes
  *no* signal, rather than scoring 0.0 — the rule SPECULUM already carries.
* **The producer owns the threshold.** The effective value is resolved by calling
  `proteus_hooks.morph_trainer_kwargs` (the function the trainer itself calls). Only if that
  import is unavailable — the tier is loadable as a bare directory, and `proteus_hooks` is
  not, because it uses package-relative imports — does it fall back to the documented 0.5
  threshold, and it then *says so* in `resolver`. A hand-written constant that disagrees with
  the producer is the exact defect this codebase has now paid for three times
  (`morph_switch`, the two stale monitor paths, and the `kind` map).

## 5. Signal and severity

`SEVERITY_WEIGHTS["mutagenesis"] = 1.2` ("the genome grows on trials where the added gene was
switched off"), placed just under `contradiction` (1.3) because it is the same class of claim —
an improvement asserted with evidence that does not support it — asserted about the genome
instead of about the margin. It does **not** duplicate BREVIS (description length) or TENSOR
(per-gene association): those report what the genome *costs* and what it *correlates with*;
MUTAGEN reports whether the ledger that grew it can support attribution at all.

## 6. Techniques considered and REJECTED

Recorded so they are not re-proposed.

1. **dN/dS as a literal ratio.** A rate ratio needs a *denominator of opportunities* — mutations
   attempted that were not retained. No artifact records rejected trials: `morph_record` is
   called once per cycle after the trial and the ledger is outcome-only. A ratio with a
   fabricated denominator would be worse than no ratio, so MUTAGEN reports the retention rate
   and the binomial that bounds it instead. **Rejected as unmeasurable; the retention rate is
   the honest surrogate.**
2. **Epistasis / landscape ruggedness** (Bank 2022; Diaz-Colunga 2023). Needs the *same* gene
   tried against *different* backgrounds. Every row is `dimension = 5` — the round-robin never
   varies the background — so the effect's context-dependence is not estimable. **Rejected: no
   dimensional variation exists in the data.** `PERENNIS` already covers the era-level form of
   the same question.
3. **COSMIC-style mutational spectrum over the test suite.** `mutate.py` records only
   `{mutants, killed, score, survived[]}` — no per-operator breakdown — so "which kind of fault
   can the suite not see" is unanswerable from the artifact. **Rejected pending a producer
   change; MUTAGEN reports the score with its Wilson lower bound and age instead.** With
   n=30, k=30 the honest statement is "kill probability >= 0.887 at 95%", not "score 1.0" —
   and a 17-hour-old measurement is evidence about yesterday.
4. **Genetic load in bits** (charging the genome's length directly). BREVIS already computes the
   two-part MDL share of the genome. **Rejected as a duplicate**; MUTAGEN carries load as a
   reported ratio, not a second severity term.
5. **Neutrality test on the value series alone.** Tried and kept only as `value_effect`: with
   the gene inert in 76% of trials the series is dominated by the artifact, so a neutrality
   index computed from it would inherit the bias it is meant to detect.

## 7. Honest limits

* **MUTAGEN does not prove the genes are useless.** It proves the ledger cannot *attribute* the
  gain. `use_schema_features` may well be valuable — `tensor_genome.json` thinks it is — but
  the Morph trial as recorded cannot demonstrate it. That distinction is the organ's whole
  claim and is stated so it cannot be over-read.
* **The root cause is not identified.** A stale `baseline_fitness`, a mismatched pool, or an
  evaluation that differs in more than the gene would all produce this. MUTAGEN reports the
  symptom precisely enough to act on and deliberately does not guess the mechanism.
* **`inert_share` depends on the resolution rule.** For `use_schema_features` it does not: every
  observed raw value (0.0563, 0.0686, `False`) is below any threshold in (0.07, 1.0]. For
  `by_session` it does, since 0.5142 sits just above 0.5. `resolver` records which path resolved
  it so the number can be re-derived.
* **The 59 rows are one dimension and two genes.** This is a finding about the current history,
  not about Morph in general.

## 8. Wiring

* `_ORGAN_ROWS` gains the 17th entry (`mutagen`); `organ_readings()` and `epistemic_report()`
  iterate the registry, so the panel needed no registry change.
* `organ_readings(..., morph_rows=, genome=, mutation=)` — new optional inputs, defaulting to
  `None` so every existing caller is unchanged and MUTAGEN reports `unavailable` rather than a
  false calm.
* `collect_state(root)` reads the three artifacts and passes them, so any non-viewer consumer
  (the verify gates) gets the same reading as the panel.
* `state_paths(root)` is corrected: `allocator` -> `state/proteus_circulation.json` and
  `morph_history` -> `state/proteus_morph.jsonl`. Both previously pointed at files no producer
  writes (§5.7 of `EX_MACHINA.md` fixed these **in the viewer only**), so `collect_state()` — the
  module-level function — was still reporting MORPH and CIRC absent. That is the same
  "component exists, is correct, and is never reached" defect the notes already flag twice.
* The panel gains a `MUTAGEN` row plus one expanded per-gene line, both height-gated.
