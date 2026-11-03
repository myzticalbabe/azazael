# Recall floor protocol (pre-registered)

Status: **procedure fixed, holdout not yet labelled.** This document states how the
crisis router's recall becomes *one number with a floor*. It does not itself supply
the number: `certification.json` → `crisis_router_recall` → "One recall figure with
a lower bound the authors cannot move after seeing the result" stays open until a
corpus labelled under this protocol has been scored once.

## 1. The problem a point estimate hides

The router is currently reported as per-split point estimates. Measured
2026-11-03:

```
PYTHONPATH=. python tools/triage_eval.py --json
```

| split | rows | TP | FN | FP | recall |
| --- | --- | --- | --- | --- | --- |
| dev | 30 | 13 | 0 | 0 | 1.0000 |
| holdout | 12 | 5 | 1 | 0 | 0.8333 |
| holdout2 | 24 | 11 | 1 | 0 | 0.9167 |
| holdout3 | 23 | 10 | 1 | 2 | 0.9091 |
| holdout4 | 24 | 12 | 0 | 0 | 1.0000 |

Pooled over the four holdouts: **38 of 41 positives, recall 0.9268.** dev is
excluded from every figure below — it is the split the detector was changed after
looking at, so its 1.0000 is fitted.

`0.9268` is not a claim anyone should act on. At 41 positives, a true rate of 0.80
produces 38/41 often enough that the observation cannot separate 0.93 from 0.80.
That is what a floor is for, and it is why the floor is computed, not asserted.

## 2. The bound, and the one place it is computed

```
python tools/recall_bound.py 38 41
```

```
observed recall : 38/41 = 0.9268
exact lower 95% : 0.8216   (Clopper-Pearson, one-sided)
wilson lower 95%: 0.8304   (closed form, less conservative)
```

The **Clopper-Pearson exact one-sided lower bound** is the number reported. It is
the `p` at which the observed result has probability exactly 0.05:

    P(X >= k | n, p) = 0.05,  X ~ Binomial(n, p)

Implemented by bisection in `tools/recall_bound.py` (stdlib only, no scipy). The
Wilson bound is printed next to it and is never the reported figure: exact is
conservative, so exact ≤ Wilson always. At 38/41 the gap is 0.0088; a report that
quotes the larger number is quoting the friendlier one.

`python tools/recall_bound.py --selftest` asserts the defining equation at four
(k, n) points, the closed form `alpha**(1/n)`, monotonicity in k, tightening with
n, `exact <= wilson`, and refuses impossible counts (k > n, k < 0, n = 0). It exits
0. **The self-test asserts the equation, not remembered constants** — the first
version carried three remembered values and two of them were wrong while the
implementation was right.

## 3. Pre-registered decisions

These are fixed here, before any holdout exists, so that none of them can be chosen
after seeing a result. Changing any of them invalidates the run and it starts again
under a new holdout name.

| # | decision | value | why this value |
| --- | --- | --- | --- |
| P1 | reported statistic | Clopper-Pearson one-sided lower bound, 95% | conservative; one-sided because the question is "is recall at least X" |
| P2 | recall floor claimed | **0.80** | a safety router that misses 1 in 5 crises is already a hard sell; a lower floor is not worth certifying |
| P3 | false-alarm ceiling | specificity lower bound ≥ **0.80** | currently 40/42 → lower 0.8576; a router that cries crisis on ordinary turns gets switched off, which is a recall of zero in practice |
| P4 | holdout size | **176 positives** minimum | `--size-for` at an assumed true rate of 0.85 — the weakest rate the current data does *not* rule out (0.8216 lower at 38/41). 176 is what it costs to clear 0.80 if the router is only as good as 0.85 |
| P5 | coder agreement | Cohen's κ ≥ **0.80** before unblinding | below that, the labels are not a measurement; the corpus is discarded and rewritten, and the discard is recorded |
| P6 | coder disagreement | third coder resolves; > 10% of rows in dispute fails the corpus | a corpus that is mostly argument is not labelled |
| P7 | scoring runs | **once**, by the frozen `triage_eval.py`, on the hashed file | a second run is a tuning run |
| P8 | dev split | never quoted as evidence | fitted |
| P9 | corpora edited after scoring | new name, new hash, scored as a NEW holdout — never an edit in place | see §5 |

P4 is deliberately expensive. The cheaper constructive alternative is to pre-register
a smaller N and then report only the floor that N supports — e.g. 44 positives at an
assumed 0.90, 30 at 0.93 — which is legitimate *provided the smaller N is written
down before scoring*. Deciding the floor after seeing the result is the failure this
protocol exists to prevent.

## 4. Labelling procedure (the part that makes the floor real)

1. Two coders who did not write the router label each statement independently:
   `expect_crisis` ∈ {true, false}, no discussion before κ is computed.
2. Compute κ. Below 0.80 → stop (P5).
3. Disagreements are resolved by a third coder. Record how many rows were
   contested and which way each was resolved.
4. Write the corpus as JSONL with a `_meta` row (the loader refuses a corpus
   without one — `tools/triage_eval.py:load_corpus`). The `_meta` row must carry:
   `authored`, `rows`, `provenance`, `splits`, `coders`, `kappa`, `frozen_at`,
   `sha256`. Provenance names who wrote the statements and what they are: invented
   utterances, transcripts, or something else. A corpus whose provenance is
   unrecorded cannot be interpreted later.
5. Freeze: `sha256sum nurse_ratchet/psyche/data/<corpus>.jsonl` and paste the digest
   into `_meta.sha256` and into this document's log section.
6. Score **once**: `PYTHONPATH=. python tools/triage_eval.py --corpus <path> --json`.
   Save the output next to the corpus.
7. Feed the confusion counts to `tools/recall_bound.py <tp> <tp+fn>` and report the
   exact lower bound, plus the specificity bound from `<tn> <tn+fp>`.

## 5. Immovability, worked from the failure already in this repository

The bound is immovable only if the *corpus* is. This tree has already lost one
reading that way: `README.md` reports holdout3 at recall **0.18** on 23 rows, while
the committed corpus scores holdout3 at **0.9091** on 23 rows. Both are real
observations; the file that produced the first one no longer exists in any commit:

```
git log --oneline -- nurse_ratchet/psyche/data/triage_corpus.jsonl
191dd0b feat: Nurse Ratchet standalone installable v0.1.0      # single commit, one blob
```

`holdout3_provenance` in `_meta` says it was "scored exactly once with no rule,
weight or lexeme changed afterwards" — true of the detector, and not true of the
file, which was rewritten in the working tree after the first score. A number you
cannot reproduce from a commit is not evidence, however honestly it was measured.

Consequences now in force: §4.5 hashes the corpus before scoring; and any corpus
change ships as a new file name with a new hash, so the earlier reading keeps its
own file to point at. The four holdouts that exist today are committed in one blob
and are therefore stable from `191dd0b` onward.

## 6. Negative controls

An oracle is only an oracle if it can fail. These rows must *not* fire as crisis;
each is checked before a holdout is accepted.

| control | where it lives | expected | coverage today |
| --- | --- | --- | --- |
| fixed idiom, words present and meaning the opposite | `rt_agent.CRISIS_EXCLUSIONS` | not crisis | "the death of me" (dev, 1 row), "deadline" (3 rows), "dying to know" (dev, 1 row) |
| third-party crisis → escalate to a human, not "crisis" for the user | `rt_agent._attribution` | routed away from self | "brother" (dev, 1 row), "friend" (dev + holdout3, 2 rows) |
| no cue at all | ordinary register | not crisis | present across all splits |

Recorded gaps: **"kill time" appears in zero rows**, so one of nine exclusion idioms
has no test anywhere; and the attribution guard is exercised **only in dev**, so
there is no out-of-sample evidence for it. Both belong in the next corpus, and
neither is a defect of the bound — they are holes in what the bound is a bound on.

## 7. What this does not establish

- The corpus is authored by the same agent that wrote `rt_agent.CRISIS_CUES` and
  `CRISIS_EXCLUSIONS`. It measures agreement with those expectations, not clinical
  validity. Every `_meta.provenance` row in the tree says so, and the certification
  criterion "A labelled corpus the author did not write" remains open.
- A lower bound of 0.80 on invented utterances is a statement about invented
  utterances. `holdout3_provenance` calls its own number an upper bound on
  real-world recall, and that caveat travels with any floor computed from it.
- Specificity here is measured on 42 negatives. The 0.8576 lower bound on that is
  wide; P3 exists so it cannot be quietly dropped.

## 8. Log

| date | what | reading |
| --- | --- | --- |
| 2026-11-03 | `recall_bound.py --selftest` | exit 0, 11 checks, defining equation held at k=50/83/18 (n=100) and 415/500 |
| 2026-11-03 | pooled holdout, 4 splits | 38/41 = 0.9268, exact lower 0.8216, Wilson 0.8304 |
| 2026-11-03 | pooled specificity | 40/42 = 0.9524, exact lower 0.8576 |
| — | pre-registered holdout | **not yet labelled** |
