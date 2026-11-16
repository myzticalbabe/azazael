# What females need, and what the evidence will not say

Explanation, not instruction. The data is
`nurse_ratchet/psyche/data/female_needs_hyperedges.json`; the instrument that
judges it is `tools/validate_female_needs_corpus.py`.

## The question, and why it is asked this way

"What do females need" is answerable in two useless registers. In one it gets a
list: safety, housing, childcare, dignity, a say — every item true, none ranked,
nothing a service could act on differently tomorrow. In the other it gets a
single statistic quoted as though it were a design.

This corpus refuses both by keeping three things separate that prose normally
merges:

- a **need** (eight of them, `N-SAFETY` through `N-VOICE`) — a claim about what
  absence of the thing costs;
- an **edge** (22 of them) — one specific assertion linking the need to a
  concrete condition, with its own tier, state, claim type and denominator;
- an **answer** — the ranked ordering, plus the note that says in writing the
  rank is an argument from the evidence's own logic and *not* a measured effect
  ranking. No study in the corpus compared these eight against each other.

That third part matters most. The rank says safety underlies the rest; it does
not say need five is less urgent than need two for a particular woman, and the
file says so in `answer.ordering_note` rather than in a footnote a reader skips.

## The eight needs, as the evidence leaves them

| need | what it actually asks for | edges |
|---|---|---|
| `N-SAFETY` | safety from retraumatisation, not the absence of a logged incident | 3 |
| `N-COOCCURRING` | mental health and substance use treated together, by people who expect both | 3 |
| `N-MOTHERHOOD` | to be treated as a mother, not as a risk to be managed | 3 |
| `N-HEALTH` | care that starts from female bodies having their own trajectory | 3 |
| `N-MENSTRUAL` | products as a necessity with a quantity, a quality and a cost | 3 |
| `N-ECONOMIC` | money, a job that survives a record, childcare to get to it | 3 |
| `N-HOUSING` | a bed that is not the house the violence happened in | 2 |
| `N-VOICE` | a hand in designing the thing meant to help her | 2 |

Counts above are derived, not authored: they are whatever
`needs[].edges` holds, and `_meta.counts` is checked against them on every run.

The two needs with fewer edges are the honest ones. `N-HOUSING` and `N-VOICE`
have less because the maintained evidence is thinner in the tiers this corpus
accepts, not because they matter less — and the validation run fails if anyone
"balances" the table by inventing an edge.

## The discipline every edge has to satisfy

Each edge carries `tier`, `state`, `claim_type`, `sources`, and — whenever
`claim_type` is `prevalence` — a `denominator`. The states are `VERIFIED`,
`LEAD`, `BLIND` and `CUT`; the tiers run `A` (primary document) through `D`
(snippet or hearsay). The rule the instrument enforces is one-directional:

> A claim may be **weaker than its source**. It may never be **stronger**.

So `E-MENSES-03` cites a tier-A source and is published as `guidance`, and
`E-HOUSE-02` cites tier-A and stays a `qualitative` claim. Those are allowed and
intentional. What the run rejects is an edge whose state is `VERIFIED` while its
strongest source is tier C or D — because a `VERIFIED` label is consumed
downstream as if the document had been read, and a claim that reaches
`VERIFIED` on a secondary description is the specific failure this corpus was
built to stop.

Current spread, measured: 8 tier-A, 5 tier-B, 9 tier-C sources across 22 edges;
13 `VERIFIED`, 9 `LEAD`; claim types 8 qualitative, 5 guidance, 5 policy, 4
prevalence.

Three edges were downgraded from `VERIFIED` to `LEAD` during construction, and
their `provenance` records why. Three corroborations were asserted in quorum
prose and two of them were not supported by the lines quoted — the text was
fetched and read before the claim survived. That is the normal cost of writing
this kind of file: the prose is where unsupported confidence hides, because
prose has no denominator.

## Why `LEAD` is a real state and not a soft failure

A `LEAD` edge is queued, not dropped. It says: this is probably true, here is
who says so, and nobody in this repository has yet opened the document that
would make it `VERIFIED`. Publishing nine of those next to thirteen verified
ones is more useful than publishing thirteen and quietly deleting the rest,
because the nine name exactly what the next pass has to fetch.

## Running it

```bash
python tools/validate_female_needs_corpus.py          # PASS/FAIL, exit 0/1/2
python tools/validate_female_needs_corpus.py --self-test
python -m pytest tests/test_female_needs_corpus.py -q
```

20 checks. `--self-test` mutates a loaded copy six ways and requires all six to
be caught, so a validator that has silently stopped checking anything cannot
report a clean run. Exit `2` is *could not run* — no corpus, unparseable JSON —
and is never a pass.

The validator is deliberately **read-only**. It has no `--write-counts`. A
validator that rewrites the file it judges can launder a defect into a pass;
when `_meta.counts` drifts the run prints the exact block to paste instead.

## What this corpus does not claim

- It is not a measure of what any individual woman needs. It is a map of what
  the literature says absence costs, and the ranking is an argument.
- It is not exhaustive. Some needs have two edges because that is what cleared
  the tier bar, and the bar was not lowered to fill the table.
- It is not a prevalence estimate for any population not named in an edge's own
  `denominator`. A figure without one does not appear here as `prevalence`.
- It does not resolve the tension in
  [`why-nurse-ratchet.md`](why-nurse-ratchet.md): a corpus built from what
  services measure will describe needs in the shape services already recognise.
  `N-VOICE` exists in this file partly as the control on that bias — the need
  that says the list should have been written with her, not about her.
