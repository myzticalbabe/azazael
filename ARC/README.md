# ARC — the accountability container

ARC holds an AI accountability apparatus so that it can be handed to someone else
and still work. It has one rule about what may live here, and every inhabitant
must satisfy it.

## Entry rule

An inhabitant enters ARC only when all three are present:

1. **a mark** — what the artifact asserts, in a form a reader can test;
2. **an evidence state** — for each assertion, the tier at which its authority was
   read, the date, and what the assertion does *not* prove;
3. **a checker** — one command that returns `READY` / `GAPS` / `INCOMPLETE` /
   `BLIND` and a non-zero exit when the artifact stops matching its own evidence.

An artifact carrying assertions without a checker is a draft and stays outside.
That is the whole test: `esquire/` and `cain/` are built because each has a mark,
a ledger and a checker; `golgotha/` is not, because it has no inhabitant at all.

**Entry is satisfied by having a checker, not by having a green one.** `cain/`
returned `GAPS` on the day it was built, with twelve named defects. A wing whose
checker reports defects is measuring something; a wing with no checker is
asserting that there is nothing to measure.

## Wing index

| wing | inhabitant | state | entry evidence |
| --- | --- | --- | --- |
| `esquire/` | What a court demands before it hears a machine's account | **BUILT** 2026-11-04 | `pins.json` (20 pins) + `ADMISSIBILITY_PINS.md` + `tools/esquire_pins.py` |
| `cain/` | Accountability mark for AI systems and planned obsolescence | **BUILT** 2026-11-04, verdict `GAPS` | `marks.json` (8 pins, 21 figures) + `ACCOUNTABILITY_MARKS.md` + `tools/cain_obsolescence_pins.py` |
| `golgotha/` | Undefined | **BLOCKED** | the term has no referent in the tree, the git history, or the telemetry store |

## esquire/ — the admissibility wing

The wing answers one question with evidence rather than assertion: *what does a
court demand before a machine's account may be heard?* It is part of the Esquire
Canon as **Article E-11**
(`docs/ESQUIRE_CANON_2026-11-03.md`), whose proviso at E-0.2(c) keeps the canon's
scope unchanged: E-11 pins an instrument; it adds no member to the
human-of-record class defined at E-0.1.

Each pin is a **demand**, not a claim of admissibility. It records:

- the demand in plain language;
- the operative text that makes the demand, quoted;
- the tier at which that text was read — `A` read at source, `B` carried,
  `C` credible secondary, `UNVERIFIABLE-HERE` not fetched;
- the artifact that answers it;
- the instrument gate that tests the answer;
- what the answer does **not** prove.

A pin may not be quoted beyond its tier. That rule is why *Bullcoming v. New
Mexico* sits at tier B: its text returned HTTP 500 and then 404 on 2026-11-04.

### Measured state, 2026-11-04

```
$ python tools/esquire_pins.py --gates
verdict: READY
ledger: 20 pins, 10 implemented gates, 1 declared gaps
gate  proof    pins                               title
G1    tier A/B P7                                 Qualification and disclosure
...
G11   tier A/B P18,P19,P20                        Relevance and conditional relevance [declared, not implemented]
```

- 20 pins: **15 tier A, 3 tier B, 1 tier C, 1 UNVERIFIABLE-HERE**.
- 10 gates implemented (G1-G10), each mapped to proof-tier pins.
- G11 (relevance and conditional relevance) **declared, not implemented**:
  `grep -E "\b(401|402|403|104)\b" tools/esquire_admissibility.py` returned zero
  matches on 2026-11-04. A gate invented to fill a gap is the defect the gap
  exists to name.

### Verdict vocabulary

| verdict | exit | means |
| --- | --- | --- |
| `READY` | 0 | every implemented gate has proof-tier support and the ledger has no defect |
| `GAPS` | 1 | a gate lost its pins, a pin invented a gate, or the ledger is malformed |
| `INCOMPLETE` | 1 | no defect, but a gate's only support is a carried citation |
| `BLIND` | 2 | the ledger or the instrument could not be read — never a pass |

The checker never says "admissible". Admissibility is a ruling a court makes on a
record; a tool that conferred the label would be asserting what it exists to test.

## Running the wing

```bash
python tools/esquire_pins.py            # check (default)
python tools/esquire_pins.py --gates    # gate -> pin table
python tools/esquire_pins.py --json logs/esquire_pins.json
python -m pytest tests/test_esquire_pins.py tests/test_esquire_admissibility.py -q

python tools/cain_obsolescence_pins.py            # check (default)
python tools/cain_obsolescence_pins.py --gates    # architecture -> evidence table
python tools/cain_obsolescence_pins.py --json logs/cain_pins.json
python -m pytest tests/test_cain_obsolescence_pins.py -q
```

Production interpreter: `C:/Azazael/.venvs/py315t/Scripts/python.exe`.

## cain/ — the obsolescence wing

The wing grades the mark's *claims about vendors*, not the vendors. It answers:
for each pillar, what does the mark assert, at what tier may that be quoted, and
what does the assertion fail to prove?

Two halves, because they fail differently:

- **machine gates** (M1-M6) are answered by running the mark — does every pillar
yield a mark, does it serialize, do the ten published totals equal the sum of the
parts they publish, is the seal a digest, is the witness dated before the act it
witnesses, is the compliance score its own formula. A total that does not add up
is a defect in the artifact and no ledger can answer it;
- **evidence pins** (C1-C7, one per architecture, three figures each) record a
tier, a read date, and what the figure does *not* prove. A count presented as a
*fact* needs a source read at proof tier; an *estimate* needs a named method; a
citation that did not resolve is recorded as a negative reading, never as support.

Drift is fatal in both directions: a figure that changed in the mark while the
ledger kept the old number, and a ledger pin naming an architecture or a figure
the mark does not publish.

### Measured state, 2026-11-04

```
$ python tools/cain_obsolescence_pins.py --gates
verdict: GAPS
ledger: 7 marks, 8 pins, 21 figures, 4/6 machine gates, 1 declared gaps
errors: 12
```

All seven `evidence_url` values were requested from this host that day: **six
did not resolve** (four HTTP 404, one 404 PDF, one NXDOMAIN) and the seventh
returned a product overview that carries no population figure. So the mark's
mechanism is documented for one pillar of seven and asserted for the other six,
and none of its four fact-counts is supported at proof tier. The two artifact
defects are named rather than repaired — the seal is a label, not a digest, and
the witness is stamped after the mark it witnesses.

M3 passing is the precise finding: the published totals *are* the arithmetic of
the architectures beneath them. The damage in this wing is not in the sums; it is
in what each summand rests on.

### What it does not prove

Nothing about obsolescence itself. A dead citation proves the citation is dead,
not that the mechanism does not exist — it means the mark, as written, cannot
establish it, which is a different and answerable statement.

## Portability evidence (SpitFire)

This evidence is container-wide: it says what exists where, and both wings'
checkers remain Windows-only (`environments/ENVIRONMENT_INVENTORY.md`).

SpitFire (`src/spitfire`) is the tree-swarming census tool. Its census is the one
command here that reads the **worktree** rather than the ledger, so it is the
measurement that says what exists where. No console script is installed, so the
CLI is reached through the package entry point. Measured 2026-11-04 on the
production interpreter:

```bash
py315t -c "import sys; sys.path.insert(0,'src'); from spitfire.cli import main; raise SystemExit(main())" \
    census --save /tmp/arc_census.jsonl
# spitfire census: 12 paths, 32 workers (free-threaded), 0.06s
#     11  source-or-doc
#      1  unknown
```

**Proves:** the census executes on the 3.15t free-threaded interpreter and returns
a machine-readable row per dirty path, with status, bytes, mtime and category.
**Does not prove:** that the pins are portable. The census classifies paths, not
evidence; portability of the wing remains the checker's job, and the checker is
still Windows-only (`environments/ENVIRONMENT_INVENTORY.md`).

SpitFire's own CLI dispatch was **dead** the first time it was invoked here:
`AttributeError: module 'spitfire.compat.impl_free_threaded' has no attribute
'run'`. The tests were green because they asserted `main` existed and that
`run_dispatcher` worked, and nothing called `run` — the function the launcher
actually uses. The contract is now implemented on both implementations and has a
test that exercises the launcher
(`tests/test_spitfire_shared.py::test_launcher_contract_is_implemented`).

## What ARC is not

- Not a finding of admissibility for any AI system, in any forum.
- Not a substitute for a ruling: the pins describe demands, the instrument tests
  artifacts, and a court decides.
- Not portable yet: the pins and the checker exist only in the Windows production
  tree. `environments/ENVIRONMENT_INVENTORY.md` records that measurement, and the
  conditions that would change it.
