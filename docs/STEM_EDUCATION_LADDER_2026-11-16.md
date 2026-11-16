# STEM EDUCATION LADDER — K-12 through postdoctoral, one instrument per rung

**Proposed 2026-11-16 at HEAD `cd908411`.** Status: PROPOSAL. Nothing below is
wired to a gate yet; §6 names exactly what would have to be built, and §7 names
the commands that can be run today. Every level here is written the way this
tree already writes claims: *a rung is not reached until an artifact exists that
something can re-read.*

---

## Executive summary

| Rung | Who | The one-sentence standard | Machine-re-readable artifact | Instruments that exist today |
|---|---|---|---|---|
| E0 | K–5 | Represents a quantity, and shows the reasoning, not just the answer | no | none in this tree |
| E1 | 6–8 | Separates a measurement from an opinion about the measurement | no | none in this tree |
| E2 | 9–12 | Designs an investigation, reports uncertainty, argues from evidence | partly (lab report as text) | none in this tree |
| E3 | Undergraduate, lower division | Reproduces a published result from its stated method | yes | `check_corpus_quotes.py` (the quote-vs-producer discipline) |
| E4 | Undergraduate, capstone | Ships a study a stranger can re-run from the repo alone | yes | `golden_arrow.py`, `arc_provenance.py` |
| E5 | Master's | Registers a question before the data, then answers it | yes | `arc_provenance.py` tier A (retained bytes + digest) |
| E6 | Doctoral candidacy | Defends a method choice against the alternatives | yes | `reading_audit.py` (denominator on the claim) |
| E7 | Doctoral dissertation | Original contribution, defended, null results included | yes | `leg_ledger.py` (no leg state collapsed into prose) |
| E8 | Postdoctoral / independent | A funded line of work that outlives the advisor, with a trainee | yes | `pmb__lesson_impact` MCP tool (did the lesson change an outcome) |

**The gap this closes.** Every rung above E2 is normally measured by *inspection
of prose*: a thesis is read, a defense is attended, a grant is funded. This tree
already refuses that shape for its own claims — a claim without a command is a
recollection (HED-7) — and the ladder applies the same refusal to education: one
rung, one artifact, one instrument, and an explicit "no instrument exists" where
that is the truth (E0–E2).

---

## 1. What already exists here, and what does not

Measured 2026-11-16, in this worktree:

| Thing | Reading | Command that produced it |
|---|---|---|
| Evidence tiers A/B/C in use | `3 wings, 43 items, 23 backed, 14 instruments, 0 defects, 0 coverage gaps` | `python tools/arc_provenance.py --check` |
| Esquire wing fully backed | `esquire READY 20 items 16 backed 0 defects 0 coverage gaps` | same, after the 14 tier-A pins were backed with retained bytes |
| A lesson ladder with a stop rule | `META L0-L2 + Heaven excluded` | `AGENTS.md` → META-LEVELS-CANON |
| An evidence ladder with five floors | `FLOOR L0-L4` | same |
| Any education/curriculum ladder | **none** — `find . -iname "*POSTDOC*"` returns nothing; the only "curriculum" hits are a training-worm backlog item | `find`, `grep -rniE "k-12\|postdoc\|curriculum"` |
| A machine-readable industry-standards baseline | **broken** — `docs/INDUSTRY_STANDARDS_BASELINE_2026-11-02.json` fails `json.load` with `Invalid \escape: line 7 column 24` (a Windows path written with single backslashes) | `python -c "import json;json.load(open('docs/INDUSTRY_STANDARDS_BASELINE_2026-11-02.json'))"` |

So: the **vocabulary** this ladder needs already exists (tiers, floors, ladders,
denominators, leg states). What does not exist is an education rung between them,
and the one file that claimed to be a standards *baseline* cannot be parsed. The
proposal reuses the vocabulary rather than inventing a second one.

---

## 2. The ladder

Each rung states four things: **the standard**, **the artifact**, **the
instrument**, **the characteristic failure**. The failure column is the useful
one — every rung fails in its own way, and naming it is what makes a gate
possible.

### E0 — K–5: representation before answer
- **Standard.** Given a quantity, produces a representation (tally, array, number
  line) and an explanation a listener can follow.
- **Artifact.** None that a machine can re-read. A drawing is evidence to a
  teacher, not to a program.
- **Instrument.** None in this tree. **Declared blind, not faked.**
- **Characteristic failure.** Answer-getting: the number is right and nothing
  about it can be explained or reused.

### E1 — 6–8: measurement versus opinion
- **Standard.** Takes a measurement, states its unit and its repeat, and
  distinguishes "I measured 3.2 cm" from "it is big".
- **Artifact.** A notebook entry with a prediction, a measurement, and a
  comparison between them.
- **Instrument.** None in this tree.
- **Characteristic failure.** Correlation claimed as cause ("it went up when I
  did X, so X did it") with no alternative considered.

### E2 — 9–12: investigation design under uncertainty
- **Standard.** Designs an investigation that could fail, reports uncertainty,
  and argues from the evidence rather than from authority (NGSS practice 6–8;
  AP/IB capstone shape).
- **Artifact.** A lab report with a stated prediction, a method another student
  could repeat, and an uncertainty statement.
- **Instrument.** Partly: the report is text, so `check_corpus_quotes.py` can
  prove a quotation against the producer's own text — but nothing here reads a
  lab report for competence.
- **Characteristic failure.** Iterating the analysis until it is significant and
  reporting the iteration as if it were the plan.

### E3 — Undergraduate, lower division: procedural fluency plus one reproduction
- **Standard.** Reproduces a published result from its stated method, in an
  environment they did not author.
- **Artifact.** A reproduction log: source cited, inputs retained, the exact
  command, and the number that came out — matching or not matching.
- **Instrument (exists).** `tools/check_corpus_quotes.py` is the same discipline
  at document scale: it proves each quoted block against the producer's text and
  prints a denominator (`proven 26/26 (0 unproven, 0 NO-TEXT)`). A reproduction
  log is the numeric analogue.
- **Characteristic failure.** "It worked on my machine" — no environment, no
  version, no inputs retained.

### E4 — Undergraduate, capstone: a study a stranger can re-run
- **Standard.** Designs and executes a small study whose data, code and README
  let someone else get the same table without asking a question.
- **Artifact.** A repository: raw data retained, one command, one expected
  output, one hash per input.
- **Instrument (exists).** `tools/arc_provenance.py` grades exactly this shape —
  a named file re-hashed against a recorded digest, with `0 defects` possible
  only when the bytes are actually there — and `tools/golden_arrow.py` is the
  "one command, bounded, names what hung" runner.
- **Characteristic failure.** Cherry-picked runs: the one seed that produced a
  clean figure, presented without the nine that did not.

### E5 — Master's: register the question before the data
- **Standard.** States a question and its analysis plan *before* collecting
  data, then reports the answer including the parts that disappointed.
- **Artifact.** A pre-registration plus a replication package (data, code,
  digests) plus the thesis.
- **Instrument (exists).** Tier A as defined in `ARC/esquire/pins.json` — the
  operative text read at source, retained, and re-hashable — is the exact
  standard a replication package must meet.
- **Characteristic failure.** HARKing: the hypothesis is written after the
  results are known, and the pre-registration is written afterwards too.

### E6 — Doctoral candidacy: defend the method against its alternatives
- **Standard.** Chooses a method because it answers the question, and can say
  why the rejected methods would have answered a different one.
- **Artifact.** A prospectus with a pilot: question, method, alternatives,
  power/precision argument, and the pilot's actual numbers.
- **Instrument (exists).** `tools/reading_audit.py` — a verdict must carry its
  denominator, or it is `denominator_free`. A prospectus that says "promising
  pilot results" without the population is that defect in prose.
- **Characteristic failure.** The method is the one the lab already runs.

### E7 — Doctoral dissertation: original, defended, and honest about nulls
- **Standard.** An original contribution, defended, with the null and negative
  results reported at the same prominence as the positive ones.
- **Artifact.** Dissertation + defense record + replication package + a
  negative-results appendix.
- **Instrument (exists).** `tools/leg_ledger.py` — `ok`, `empty`, `skipped` and
  `error` may never collapse into one line of prose, and a PASS over a failed
  leg is `verdict_mismatch`. That is the dissertation's honesty requirement,
  already implemented for pipeline legs.
- **Characteristic failure.** Salami slicing, and a methods chapter that omits
  the four analyses that did not work.

### E8 — Postdoctoral / independent researcher: a line of work, not a project
- **Standard.** A funded line of work that continues without the doctoral
  advisor, that produces at least one other researcher, and whose claims survive
  an outside replication.
- **Artifact.** Grant award + first-author work outside the advisor's
  supervision + a trainee's first independent artifact + an external
  replication.
- **Instrument (exists, as an MCP tool rather than a file).** `pmb__lesson_impact`
  — which lessons actually moved an outcome, with lift against a no-lesson
  baseline. It was written as `tools/lesson_impact.py` in the first draft of this
  document; no such file exists anywhere in the tree, and `tools/stem_pins.py`
  failed the rung for it on 2026-11-16. Run live the same day it answered with
  37,793 outcome turns against 13,213 baseline turns and `signal_sufficiency
  "ok"`, so the capability is real and the path was not. A research line is
  the same question at career scale: not "was it published" but "did it change
  what happened next".
- **Characteristic failure.** An empire of trainees doing the work while the
  claims outrun the evidence; independence asserted rather than shown.

---

## 3. How the ladder maps onto this tree's existing tiers

Two different questions are being answered, and they must not be confused:

- **Source tier (A/B/C)** answers *how close to the primary object was this
  reading*. Already implemented, already graded (`arc_provenance.py`).
- **Rung (E0–E8)** answers *what must a person be able to do*. New.

The binding rule that makes them one system:

| Rungs | Minimum source tier for the rung's central artifact | Why |
|---|---|---|
| E0–E2 | C (credible secondary: a teacher's record, a moderated report) | the primary object is a child's reasoning; a program cannot read it |
| E3–E4 | B (official index / reproduction log) | the artifact is a log of a run, not the run's raw bytes |
| E5–E8 | A (retained bytes + recorded digest, re-hashable) | the artifact must survive a stranger's re-read |

Below E5, tier A is neither available nor honest to demand. Above E5, anything
less is a claim about a claim.

---

## 4. What "training" means at each rung

Training here is a loop, not an exposure: **predict → measure → compare →
record**. The recording surface differs by rung, and this tree already has three:

| Rung | Loop | Recording surface in this tree |
|---|---|---|
| E0–E2 | predict, measure, compare, explain the difference | none (human record) |
| E3–E4 | predict, run, diff against the published number | reproduction log + `state/bake_harvest_*.jsonl` for near-misses |
| E5–E6 | pre-register, run, compare to the registered plan | pre-registration + `pmb` lesson at `META L1` |
| E7–E8 | run a line, measure what moved, prune what did not | `pmb__lesson_impact` (retrieval count, never age) |

The META stop rule applies unchanged: a lesson climbs instance → rule →
applicability and **stops**. An E8 researcher who states "always verify
ownership" has produced an L3 Heaven-rule — true everywhere, deciding nowhere,
retrieved never.

---

## 5. The upgrades proposed

Numbered, each with the failure it prevents.

1. **An instrument per rung, named.** No rung may be satisfied by assertion. Where
   no instrument exists (E0–E2), the ladder says so in the row rather than
   leaving the cell blank — a blank reads as "fine".
2. **Replication moves from graduate to E3.** Reproducing someone else's result
   is a lower-division skill; waiting until a master's to demand it is why
   "replication crisis" is a phrase.
3. **Uncertainty is an E2 standard, not a graduate elective.** A number without a
   repeat is an E1 answer wearing lab clothes.
4. **Null results are a required appendix at E7.** A dissertation that reports
   only successes has an undisclosed denominator; `reading_audit.py` already
   names that defect in JSON artifacts, and the same standard applies to prose.
5. **Pre-registration at E5 and E6.** This kills HARKing by construction rather
   than by exhortation.
6. **Independence is the E8 gate**, and it is checkable: first-author work not
   supervised by the doctoral advisor, plus one trainee's independent artifact.
7. **A machine-readability column in the ladder itself.** Every rung says whether
   a program can re-read its artifact. The honest "no" at E0–E2 is the point —
   HED-9's blindness index, applied to education rather than to reports.
8. **A denominator on every level claim.** "N of M learners produced a passing
   artifact at rung X." A rate without its population is the defect the tree
   already refuses in its own readings.
9. **Ethics, consent and IRB at E5+**, as an admissibility question: what a court
   (or an ethics board) demands before it hears an account. The esquire wing is
   the working model — 20 pins, tier-graded, now 16 backed with retained bytes.
10. **Mentoring counted at E8.** A researcher who cannot produce another
    researcher has produced output, not a line of work.

---

## 6. What would have to be built (honest gaps)

- **An `ARC/stem/` wing.** `tools/arc_check.py` discovers wings by declaration
  (`WINGS`, one row: `wing`, `checker`, `ledger`, `inhabitant`), so a STEM
  standards wing is a ledger of pins (`ARC/stem/pins.json`) plus a checker
  (`tools/stem_pins.py`) — then `arc_provenance.py --check` grades it with the
  same code that grades esquire, cain and eliza. No renderer or grader changes.
- **A rung registry.** E0–E8 as data (`tools/stem_ladder.py` reading a JSON
  table) so a claim can cite a rung the way a pin cites a tier.
- **Nothing for E0–E2.** There is no learner data in this tree and inventing a
  proxy would be a worse defect than the gap. Those rows stay
  `instrument: none`, permanently, until a real corpus exists.
- **`docs/INDUSTRY_STANDARDS_BASELINE_2026-11-02.json` must parse** before any
  standards work can cite it: it currently fails `json.load` at
  `line 7 column 24` (`Invalid \escape` — a Windows path with single
  backslashes). It is reported here, not repaired here: it is outside this
  proposal's scope.

---

## 7. Verify this document's own claims

```bash
# the tiers and wings this proposal reuses, as they stand today
C:/Azazael/.venvs/py316t/Scripts/python.exe tools/arc_provenance.py --check

# the esquire wing the ladder's E5 standard is modelled on
C:/Azazael/.venvs/py316t/Scripts/python.exe tools/arc_provenance.py --wing esquire

# no education ladder existed before this file
find . -iname "*POSTDOC*" -o -iname "*CURRICUL*" | grep -v node_modules

# the standards baseline cited above does not parse
C:/Azazael/.venvs/py316t/Scripts/python.exe -c "import json;json.load(open('docs/INDUSTRY_STANDARDS_BASELINE_2026-11-02.json'))"
```

Every number quoted in §1 came from one of those commands on 2026-11-16. The
rung standards themselves are a proposal: they are asserted, not measured, and
they say so.
