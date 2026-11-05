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
That is the whole test: `esquire/`, `cain/` and `eliza/` are built because each has
a mark, a ledger and a checker; `golgotha/` is not, because it has no inhabitant at
all.

### The identity test — a wing is not a case file

Having a mark, a ledger and a checker decides what may *enter*. A fourth condition
decides what a wing must be: **a wing states a criterion that can be used in the
next matter.** It says what a class of artifact has to answer, so it survives the
case that produced it and can grade an artifact that has not happened yet.

A case file says what one party did in one matter. It is evidence, it is worth
keeping, and it belongs beside the container rather than inside it: no later
matter can be graded against it, and a container that admits one becomes a
container that admits the next one.

`esquire/`, `cain/` and `eliza/` pass — each names a criterion, not an adversary.
A Deere & Co. file that sat here failed: its claims were about one party's
conduct, not a criterion, so nothing in the container grades it and it keeps its
own checker, `tools/deere_claims_check.py`. Separation moves a case file out; it
does not weaken an evidence chain or switch off a gate. While a case file is
still parked under `ARC/`, the container says so: a directory no declaration
accounts for is reported as `UNDECLARED` and costs the `INCOMPLETE` verdict —
not ignored, and not quietly promoted to a wing.

**Entry is satisfied by having a checker, not by having a green one.** `cain/` was
built at `GAPS` and still reports `GAPS`, now with four named defects instead of
twelve; `eliza/` was built at `GAPS` with two. A wing whose checker reports defects
is measuring something; a wing with no checker is asserting that there is nothing
to measure.

## Wing index

| wing | inhabitant | built | entry evidence |
| --- | --- | --- | --- |
| `esquire/` | What a court demands before it hears a machine's account | 2026-11-04 | `pins.json` (20 pins) + `ADMISSIBILITY_PINS.md` + `tools/esquire_pins.py` |
| `cain/` | Accountability mark for AI systems and planned obsolescence | 2026-11-04 | `marks.json` (8 pins, 21 figures) + `ACCOUNTABILITY_MARKS.md` + `tools/cain_obsolescence_pins.py` |
| `eliza/` | What a conversational agent may claim, and what it must refuse to claim | 2026-11-04 | `marks.json` (11 pins) + `ACCOUNTABILITY_MARKS.md` + `tools/eliza_arc_pins.py` |
| `golgotha/` | Undefined | **BLOCKED** | the term has no referent in the tree, the git history, or the telemetry store |

**No verdict is written in this table.** A state typed beside a wing is a reading
with no date and no command behind it, and this table carried three of them: `cain`
was still described as `GAPS (4 errors)` two runs after its checker returned
`READY`. The state block in the next section is generated from a run and checked
for drift; this section names what each wing *is*.

## Container verdict — one command

The wings are graded separately on purpose: each answers a different question and
owns its own evidence. But a container whose state can only be assembled by running
three checkers by hand and reading three scrollbacks is not a container, it is three
directories — which is how a wing can sit at `GAPS` for a day while the container is
described as built.

```bash
python tools/arc_check.py                    # every declared wing, one verdict
python tools/arc_check.py --json logs/arc_check.json
python tools/arc_check.py --timeout 240      # per-wing wall bound (default 180 s)
python tools/arc_check.py --write-readme     # regenerate the state block below
python tools/arc_check.py --check-readme     # fail when that block has drifted
python -m pytest tests/test_arc_check.py -q
```

`tools/arc_check.py` runs each declared wing's **own** checker in a subprocess and
reports the worst recorded state. It grades nothing itself: a second grader would
drift from the first, and the two would disagree in public. Exit `0` `READY`, `1`
`GAPS` or `INCOMPLETE`, `2` `BLIND`.

A wing is graded `BLIND` when its checker or ledger is missing, when it crashes,
when it exceeds the wall bound, when it prints no verdict — or when **its printed
verdict, its exit code and its JSON report disagree**. A checker that cannot state
its own state consistently is not quoted in the container's.

`READY` requires every declared wing `READY` **and** nothing undeclared. A directory
under `ARC/` with no row in `tools/arc_check.py` is reported `UNDECLARED` and caps the
container below `READY`, so a new unchecked wing cannot enter the container silently
and leave the verdict describing a smaller tree than the one that exists. `golgotha/`
is printed `BLOCKED` on every run for the same reason.

The block below is **generated**, never typed. `--write-readme` replaces exactly
what sits between the markers and leaves the rest of the file alone; `--check-readme`
fails when the text disagrees with a live run. It carries no clock and no HEAD, so a
current block does not go stale by getting older — it goes stale when a reading
changes, which is the only thing that should expire it.

<!-- ARC:STATE START (generated by tools/arc_check.py --write-readme; do not edit) -->
container: GAPS
esquire    READY       pins=20     errors=0
cain       READY       pins=8      errors=0
eliza      GAPS        pins=11     errors=5
provenance INCOMPLETE  pins=39     errors=0
blocked: golgotha
undeclared: none
<!-- ARC:STATE END -->

The container is at `GAPS` when a wing holds named defects, which is not the same
as the container being unable to read its own instruments. Keeping those two facts
separate is what the `BLIND` state exists for: `BLIND` means "fix the reading",
`GAPS` means "the reading worked and the artifact is short".

## Evidence leg — is the evidence still there?

A tier-A pin says a requirement was read at source. That is a claim about a
*reading*, and a reading that leaves nothing behind cannot be re-examined by the
person the container is handed to. So one leg asks the only question that can be
settled mechanically: **can the thing this pin names still be looked at?**

`tools/arc_provenance.py` walks each wing's ledger and grades every pin in this
order — first match wins:

1. **bytes** — a named capture is re-hashed from disk *now*. A `sha256` field
   recorded beside the file is never trusted on its own: a digest someone typed
   proves only that they typed it. A digest with no filename is resolved against
   a re-hash of every file in the wing, and counts only if real bytes produce it.
2. **source** — a citation pointing inside this tree is opened, and the pin's
   quoted sentences are located in it. Comparison is on wording: markdown
   emphasis and blockquote markers are stripped first, because a correct quote
   inside a `>` block is still that quote.
3. **instrument** — a command naming a `.py` in this tree is resolved (including
   into the wing's declared `project_root`) and reported re-runnable, with
   `--run-instruments` executing it and grading its exit status.
4. **nothing** — `UNBACKED`: tier-A prose with no bytes, no in-tree quote and no
   command behind it.

Tier-A pins are the graded ones, because tier A is the only tier that asserts a
read at source. A tier-A pin with nothing behind it is a **coverage gap** when it
merely records a reading, and a **defect** when the evidence it names is gone or
contradicts itself: a capture that no longer exists, a digest that no longer
matches, a quote the cited document does not contain, a command whose script is
not in the tree, or a cited `command` that says no command in the tree reproduces
the figure. Tier B and C are recorded, never required.

Measured 2026-11-05 on this tree: 39 pins — 9 backed, 7 re-runnable instruments,
0 defects, 14 coverage gaps (all 14 in `esquire/`, all tier A). That reading is
what `INCOMPLETE` is for: the container's instruments all work, and the evidence
says less than the pins do.

## Binding leg — is every declared surface pinned?

The evidence leg asks whether a pin's *proof* can still be found. The binding leg
asks the other half of the same question: **does every surface the wing declares
have a pin answering for it?** A wing whose checker already enforces that is a
wing whose green means something; a wing that publishes a measurement nothing is
bound to is publishing an assertion.

```
python tools/arc_pin_audit.py                  # declared vs pinned, per wing
python tools/arc_pin_audit.py --wing eliza     # one wing
python tools/arc_pin_audit.py --prove          # mutation control, see below
python tools/arc_pin_audit.py --json logs/arc_pin_audit.json
```

Verdicts: `CLEAN` 0, `MISSING` 1, `BLIND` 2. It reads each wing's declaration from
the wing's own module — esquire's `GATE_METADATA` and `declared_gaps`, cain's live
`(vendor, architecture)` pairs, eliza's README rows in a table whose last header
cell declares a measurement — so the audit cannot invent a surface the wing does
not publish, or miss one it does. A declared surface with no pin is `MISSING`; a
pin answering for a surface the wing never declared is an orphan, and also
`MISSING`; `BLIND` is reserved for a declaration that could not be read at all.

`--prove` is the control that makes the audit more than a second opinion: it
copies each wing's ledger, **removes every pin answering for one declared
surface**, runs the wing's own checker against the copy, and reports `BITES`
(exit non-zero) or `SILENT`. The first version of this control deleted a single
pin, and esquire reported `SILENT` — correctly, because esquire shares gates
between pins, so removing P1 left G6 covered by P4. The binding was fine and the
control was wrong; a control that only ever deletes one pin tests the ledger's
redundancy, not the wing's enforcement.

Measured 2026-11-05 on this tree:

```
$ C:/Azazael/.venvs/py315t/Scripts/python.exe tools/arc_pin_audit.py --prove
  wing     declared  pinned  missing  rule
  esquire        11      11        0  tools/esquire_pins.py: '%s has no pin'
  cain            7       7        0  tools/cain_obsolescence_pins.py: 'is published and unpinned'
  eliza           7       4        3  tools/eliza_arc_pins.py: 'publishes a measurement and no pin answers for it'
  [MISSING] eliza: README.md:32 bypass
  [MISSING] eliza: README.md:33 ultra-loose
  [MISSING] eliza: README.md:34 concurrent
  [CONTROL] esquire: removed P7 for G1 -> checker exit 1 (BITES)
  [CONTROL] cain: removed C1 for Microsoft / TPM 2.0 / Secure Boot Gate -> checker exit 1 (BITES)
  [CONTROL] eliza: removed E4 for README.md:23 -> checker exit 1 (BITES)
verdict: MISSING
exit 1
```

The three eliza rows are real, not a tooling gap: the README's second table
publishes three figures whose last column declares a measurement, and no pin
answers for them. They are recorded as gaps for the owning lane rather than
pinned here, because a pin's tier, instrument and command are the lane's to name
and a container that invents them would be fabricating the evidence it grades.

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

python tools/eliza_arc_pins.py             # check (default), runs the project's own gate
python tools/eliza_arc_pins.py --gates     # pin table: id, tier, surface, status
python tools/eliza_arc_pins.py --json logs/eliza_pins.json
python -m pytest tests/test_eliza_arc_pins.py -q

python tools/arc_check.py                 # all three wings, one container verdict
python tools/arc_check.py --json logs/arc_check.json
python -m pytest tests/test_arc_check.py -q
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
ledger: 7 marks, 8 pins, 21 figures, 6/6 machine gates, 2 declared gaps
errors: 4
  [GAP] C3 mechanism is recorded at tier UNVERIFIABLE-HERE
  [GAP] C5 mechanism is recorded at tier C
  [GAP] C6 mechanism is recorded at tier C
  [GAP] C7 mechanism is recorded at tier UNVERIFIABLE-HERE
exit 1
```

All seven `evidence_url` values were requested from this host on 2026-11-04,
through the bypass kit, which saves the response bytes and their sha256 so a
reading can be re-examined rather than remembered: **six did not resolve** (five
HTTP 404, one NXDOMAIN). **Four of the six were replaced** with a live source and
both URLs are recorded — C1 and C2 at tier B, C5 and C6 at tier C. **Two were not:**
C3 (Intel) and C7 (Sonos) have no readable live authority, and the Wayback
availability API returned no snapshot for either. So the mechanism is proven at
proof tier for three pillars, carried by a secondary source for two, and unproven
for two; and all twenty-one figures are recorded as estimates, because a count
asserted as a fact needs a proof-tier source for that count and none exists.

Both artifact defects were repaired in the mark module at explicit direction, under
the checker's grading rather than in place of it: the seal is now a digest a reader
can recompute over the canonical JSON minus itself, and the witness is stamped from
the mark's own clock so it cannot precede the act. **What that proves is integrity,
not truth** — a digest over a false claim is a valid digest over a false claim. The
four errors are therefore unchanged in kind: a pillar whose premise no named source
proves.

M3 passing is the precise finding: the published totals *are* the arithmetic of
the architectures beneath them. The damage in this wing is not in the sums; it is
in what each summand rests on.

### What it does not prove

Nothing about obsolescence itself. A dead citation proves the citation is dead,
not that the mechanism does not exist — it means the mark, as written, cannot
establish it, which is a different and answerable statement.

## eliza/ — the conversational-claim wing

ELIZA is named for Weizenbaum's 1966 program, a parody of a therapist that people
told their problems to anyway, and the project states that cautionary tale itself: *a
system that sounds like it is listening will be believed, whether or not anything
underneath is doing the work*. The wing's question is therefore not whether ELIZA
helps anyone — no authority here could establish that — but whether each of its
claims is pinned to something a reader can re-run.

Eleven pins in four families: four performance figures the project states about
itself, the crisis router's measured accuracy **and its misses**, the publication
gate's own verdict, and the project's printed limitation.

**Three findings, all from instruments rather than inspection:**

- **Four of eleven pins are carried.** The README's `0.025 ms`, `8.5 µs`,
  `148.2 µs`, `+0.352` and `45 constants` are emitted by no script in the tree, so
  they sit at tier B with a stated reason and print in the ledger's `carried` line.
  Declared as `G-ELIZA-2` rather than closed by timing them here.
- **The router misses three crisis rows its own corpus expected** — an explicit
  plan with a date and a method, a hopeless-intent phrasing, and a plan stated
  indirectly — and fires on two benign rows that say "I am not suicidal". The `dev`
  split reads perfect because the router was changed after seeing those failures,
  and the tool labels it `[FITTED]` itself.
- **The publication banner is contradicted.** `PUBLIC, FULLY EXECUTABLE` is the
  README's first line; the project's own release gate exits 1 with 2,053 failures
  (2,047 undeclared files, 6 secret-shaped strings), and the manifest's status is
  `PRE-PUBLICATION`. 2,047 of those failures are one adopted subtree that the gate's
  `ship_roots` does not exclude — recorded, not repaired, because the remedy is a
  decision for the owning lane.

Seven gates, one of which runs the project's gate live and reads its exit status,
and one of which refuses **a number in a claim that its recorded reading never
printed**. The same refusal, in the other direction, is why the checker has a
declared gap instead of a therapeutic-benefit gate: no authority named here can
establish that a conversation improves a person's mental state, and inventing a gate
would manufacture the claim the project's own limitation forbids.

## Portability evidence (SpitFire)

This evidence is container-wide: it says what exists where, and all three wings'
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
