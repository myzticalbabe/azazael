# ESQUIRE ADMISSIBILITY — audit, gap, instrument

**Version:** 1.2 — 2026-11-04
**Status:** audit plus a built instrument. Not legal advice, not reviewed by a lawyer.
**Instrument:** `tools/esquire_admissibility.py` (ESQUIRE-ADMISSIBILITY-v3)
**Tests:** `tests/test_esquire_admissibility.py` (61 tests)

---

## 1. The request, and the premise that does not hold

The instruction was that **the Esquire canon mandates stringent tests for court
admissibility of AI opinions and evidence**. The canon does not. It does the
opposite, in the article that draws its boundary, at
`docs/ESQUIRE_CANON_2026-11-03.md:50`:

> **(c) evidentiary rules about authenticating machine output;**

That line sits under **E-0.2 — "The canon does not govern"** (line 47). The
exclusion is explicit, deliberate, and adjacent to three other exclusions
(who may appear, product-safety approval, private contract terms). So the
premise is not a reading the canon leaves open: it is a subject the canon
assigns to someone else.

This matters more than a wording correction, and it is the first finding of the
audit. A body of work that claims the canon already mandates admissibility
testing would be **citing an authority that disclaims it** — which is the
failure mode the canon's own E-7 (evidence ladder) and E-9 (falsifiability)
exist to prevent. The honest reading is a gap, and a gap can be filled by a new
instrument without pretending the old one said it.

### 1.1 What the canon *does* say that bears on the question

Two provisions touch admissibility without governing it, and both are about the
human, not the evidence rule:

- **E-1, the naming rule** — a human is installed where a machine did the work.
  Applied to an evidentiary proffer, E-1 answers *who must stand behind the
  output*, not *whether the output is admissible*.
- **E-5.3** — a nominal reviewer with no power to alter the outcome is a fig
  leaf in fact. The same insight is load-bearing in gate G7 below, where a
  reviewer without authority is a recorded GAP.

The memorandum is the only document in this family that uses the word
admissibility at all, once, at
`docs/MEMORANDUM_WHEN_THE_MACHINE_DOES_THE_WORK_2026-11-03.md:357`:

> the machine's output is currently inadmissible because the machine is not a
> person — so the burden falls on the rule to show that personhood, rather than
> the artifact, is what it is actually regulating.

That sentence is a rhetorical move inside an argument about rule design. It is
not a test, it names no rule of evidence, and it does not survive as an
authority for one: it asserts a fact about current practice without citing a
rule or a decision. Read as a *hypothesis* it is testable (and the instrument
below is one way to test it); read as a *mandate* it would be a citation the
document cannot support.

### 1.2 The audit result: there was no prior tooling

Measured, not recalled — the command and its result are in §9, row 3. Before
this work, **no Python file in `tools/`, `src/` or `tests/` referenced FRE 702
in any form** (`FRE 702`, `Rule 702`, `fre_702` → 0 files). The repository's
`tools/legal_panel.py` is a five-seat panel harness that reasons about
*propositions*; it has no notion of a proffer, an input hash, a custody chain or
a certification, and it cannot answer a per-record question. There was nothing
to extend, so the route was a sibling instrument with its own schema, its own
exit codes and its own falsifiers.

---

## 2. What was built

`tools/esquire_admissibility.py` reads a **proffer record** — the structured
account a party would have to be able to give before offering machine-produced
output as evidence — and reports, per gate, one of three states:

| state | meaning |
| --- | --- |
| `PASS` | the record carries what the gate requires |
| `GAP` | the record addresses the gate and contradicts it |
| `UNVERIFIABLE` | the record never addresses the gate |

Three states, not two, because "the record does not say" and "the record says
something that fails" are different facts with different remedies — one is a
drafting omission, the other is a substantive problem. Collapsing them would let
an empty record read as a failing one, and would make `INCOMPLETE` (draft more)
indistinguishable from `GAPS` (fix something).

**Verdicts and exit codes.** `READY` → 0, `GAPS` → 1, `INCOMPLETE` → 1,
`BLIND` → 2. `GAPS` outranks `INCOMPLETE`: a contradiction is a stronger reading
than an omission.

**There is no "admissible" verdict, by construction.** The best state is READY,
and READY is defined as "every gate the instrument can see is satisfied by the
record" — never "this evidence is admissible". `BLIND` covers an unreadable
record and is never a pass: a file that does not parse is a fact to fix, not a
silent zero.

### 2.1 The ten gates: seven universal, two criminal, one for a forum with its own evidence law

| gate | question | authority | tier |
| --- | --- | --- | --- |
| **G1** | is there a named natural person, qualified, who reviewed the output? | FRE 702 (preamble, (a)); Esquire E-1 | A |
| **G2** | are the inputs preserved, identified and hashed, with sufficiency stated? | FRE 702(b) | A |
| **G3** | is the method versioned, evaluated, and its error rate measured? | FRE 702(c); *Daubert*, 509 U.S. 579 | A (rule); case not re-fetched |
| **G4** | is each claim tied to a known input, and is each citation verified rather than recalled? | FRE 702(d); *Mata v. Avianca* | A (rule); C (case) |
| **G5** | is the output identified, and its provenance certified or held in custody? | FRE 901(a), 901(b)(9), 902(13)–(14) | A |
| **G6** | does the record state what the output is offered to prove, and on what predicate? | FRE 801, 803(6), 902(13) | A |
| **G7** | is AI assistance disclosed, and did a named reviewer with authority to change it review it? | Esquire E-1/E-5; ABA Formal Op. 512 | B for the conduct rule |
| **G8** | is the output, or a certificate about it, testimonial in a criminal case? | U.S. Const. amend. VI; *Crawford*; *Melendez-Diaz* | A for the amendment |
| **G9** | is the declarant named and available, already cross-examined, or waived by notice-and-demand? | *Crawford*, 541 U.S. 36; *Bullcoming*, 564 U.S. 647 | A for both cases |
| **G10** | does the record name the standard the forum itself applies, and show the output was disclosed with a chance to respond? | 5 U.S.C. § 556(d)–(e); *Mathews v. Eldridge*, 424 U.S. 319 | A for § 556 (read at source); C for *Mathews* |

**G8 and G9 apply only when `proffer.forum` is criminal.** A record that states no
forum is read as civil, and the report prints that reading rather than leaving
it implicit:

```text
forum: civil (unstated)
forum note: the record states no forum, so it is read as civil and confrontation
            gates G8 and G9 were NOT applied
```

The default is printed because silently dropping two gates on a missing key is
indistinguishable, in the output, from a criminal proffer that satisfies them.
**An administrative or arbitral forum gets a third posture, not the civil one.**
`proffer.forum` accepts `"administrative"` and its synonyms (`agency`,
`regulatory`, `administrative_hearing`, `tribunal`) as well as `"arbitration"`,
`"arbitral"` and `"arbitration_proceeding"`. In that posture **G6, G8 and G9 are
not applied and G10 is**, for the reasons in §3.7, and the report prints all
three exclusions plus the change:

```text
forum: administrative (stated)
forum note: forum stated as 'arbitration', read under the administrative posture:
            the forum sets its own evidence law, so G6 (FRE hearsay) and G8/G9
            (Sixth Amendment confrontation) are NOT applied, and G10 tests the
            forum's own standard instead
```

The declared value survives the posture label: a record that says `arbitration`
quotes `'arbitration'` back in `forum_note` rather than reporting a forum it did
not invoke. Any other value still reads as civil — `"juvenile"`, for instance —
and an unrecognised value is quoted back verbatim in `forum_note`.

The full table with each gate's falsifier and negative control is printable:
`python tools/esquire_admissibility.py --gates`.

### 2.2 The record schema

Eight unconditional sections — `proffer`, `witness`, `inputs`, `method`,
`claims`, `authentication`, `hearsay`, `review` — plus a `confrontation` block
read only in a criminal posture and an `administrative` block (`standard`,
`standard_source`, `disclosed_to_opposing_party`, `opportunity_to_respond`) read
only in the administrative posture. All are documented in the module docstring
with types, so an opponent can read the shape of the claim without reading the
code. The published repository carries a worked example of each posture under
`examples/`.

Records are hashed with a canonical, key-order-independent serialisation, and
the hash is printed with every report: two parties can confirm they are arguing
about the same proffer.

---

## 3. The legal-accuracy decisions, and why each one is a decision

An instrument that encodes an error of law is worse than no instrument, because
it produces confident output. Seven choices were made deliberately, each with a
test that fails if the choice is reversed.

### 3.1 The *Daubert* factors are non-exhaustive — so they cannot fail a gate

Testing, error rate, peer review and general acceptance are factors a court
*weighs*; FRE 702 does not require all four, and a method can be reliable
without peer review (a novel measurement with a well-characterised error rate is
the ordinary case). G3 therefore requires a versioned, evaluated method with a
measured error rate, and reports peer review and general acceptance as **notes**
that can never by themselves produce a GAP.

This is guarded by a negative control: a novel, unreviewed method with a
measured error rate must come out `READY` with G3 `PASS`
(`test_negative_control_daubert_factors_are_not_a_checklist`). A future edit
that turns the factors into a checklist fails that test.

### 3.2 FRE 702's burden is on the proponent, and this instrument asks a weaker question

The December 2023 amendment puts the burden on the proponent to demonstrate
reliability "more likely than not". The gate asks whether the record makes that
demonstration *possible* — never whether it succeeded. That is the difference
between a completeness check and a ruling, and it is why READY is not a
prediction of admission.

### 3.3 FRE 902(13) is an authentication rule, not a hearsay exception

A complete 902(13) certification satisfies G5 without any custody chain — that
is the rule's purpose, and a test asserting the opposite would encode an error.
But 902(13) does not create a hearsay exception: it certifies that a record
generated by an electronic process is what it purports to be, and the
certification must itself comply with 902(11)/(12), which requires the 803(6)
foundation (made at or near the time, by someone with knowledge, in the regular
course of activity). G6 accepts the 902(13) route **for that reason**, and the
module docstring states the limit in terms: a G6 PASS on that route is a
statement about the record's paperwork, never about the record's truth status.

The alternative route — an explicit 803(6) predicate naming a custodian and a
regular practice — is the one the clean fixture uses, so both routes are
exercised.

### 3.4 A machine is not a witness

G1 requires `kind: "human"`, a name, qualifications and review of the output. A
record naming a model as the witness is a GAP, not a technicality: FRE 702
qualifies a *witness*, and a model cannot be sworn, cross-examined, or held to
the disclosure duties in G7. This is also the bridge to the canon's naming rule
(E-1) — the only place where the canon and the evidence rules genuinely meet.

### 3.5 Citation integrity is conditional

G4 fails a claim carrying a citation marked `fabricated`, `hallucinated` or
`invented` (*Mata v. Avianca* is named in the detail string), and fails one
marked `recalled` or unmarked, because a citation nothing was read for is not a
verified authority. But a claim with **no citations at all** passes: a
valuation, a measurement, a reconstruction carries no authorities, and a gate
that demanded citations of every opinion would fail the ordinary expert report.
`test_negative_control_opinion_without_citations_passes` holds that line.

### 3.6 A certificate that satisfies G5 can defeat G8

In a criminal case the 902(13) route in §3.3 turns against the proponent.
*Melendez-Diaz v. Massachusetts*, 557 U.S. 305 (2009), held that a certificate
prepared for litigation is a testimonial statement: the analyst who made it is a
witness the accused has a right to confront, and a custodian's signature is no
substitute. A record that relies on a complete 902(13) certification *and*
characterises the output as non-testimonial is therefore a GAP at G8 — the
paperwork that clears G5 is the very thing G8 asks about. The detail string names
*Melendez-Diaz*, and
`test_certificate_prepared_for_litigation_is_not_non_testimonial` holds the line.

### 3.7 In a forum that sets its own evidence law, three gates do not apply

An agency adjudication is not a court applying the Federal Rules, and an
arbitration is not a court at all. 5 U.S.C. § 556(d), read at source on
2026-11-04, admits "any oral or documentary evidence", leaves exclusion of
"irrelevant, immaterial, or unduly repetitious evidence" to agency policy, and
allows a sanction only on "consideration of the whole record" and evidence that
is "reliable, probative, and substantial"; § 556(e) makes the transcript and
exhibits the exclusive record for decision and entitles a party, on timely
request, "to an opportunity to show the contrary" of a fact noticed outside it.

Two consequences, either of which would be an error of law if the civil gate set
were simply reused:

- **G6 has no referent there.** Asking which FRE hearsay route applies in a forum
  that does not apply the hearsay rule is a category error, and it would fail
  every honest administrative proffer for an omission the forum does not care
  about. G6 is not applied in this posture, and the report says so.
- **So do G8 and G9.** The Confrontation Clause governs criminal prosecutions;
  dropping those two outside one is the same rule the civil posture already
  follows, not a concession made to agencies.

What replaces them is **G10**, which asks the question this forum does have: name
the governing standard, source it, and show the output was disclosed to the
opposing party with an opportunity to respond. The response element is
§ 556(d)–(e) for agencies and the due-process floor of *Mathews v. Eldridge*,
424 U.S. 319 (1976), for everything else; for arbitration it is the parties' own
clause, and G10's negative control is an arbitral record that satisfies it with
no FRE paperwork at all.

---

## 4. Falsifiers and negative controls

Each gate states the observation that would retire it and the case it must not
capture. Both are asserted, not decorative:
`test_every_gate_can_fail` perturbs one field per gate and requires a GAP, so a
gate that silently returned PASS for everything would fail the suite rather than
keep it green.

| gate | falsifier (would retire the gate) | negative control (must pass) |
| --- | --- | --- |
| G1 | a rule or decision letting an unnamed machine testify as a qualified expert in its own right | a named expert adopting the output, qualifications on the record |
| G2 | an opinion admitted on inputs neither preserved nor identifiable | a sparse but fully hashed input set — scarcity is not insufficiency |
| G3 | a model with no version, no evaluation, no documented method admitted as reliable | a novel method with no peer review but a measured error rate |
| G4 | an opinion resting on a citation that does not resolve, admitted without consequence | an opinion with no legal citations at all |
| G5 | machine output admitted with no hash, no custody, no certification of the producing process | output certified under 902(13) with notice, no custody chain |
| G6 | output offered for its truth with no posture stated and no exception identified | output offered only to show what the system emitted |
| G7 | a reviewer with no power to alter the output treated as satisfying human review | a reviewer who changed nothing but held authority |
| G8 | a certificate prepared for litigation, offered in a criminal case, admitted as non-testimonial because a custodian signed it | a machine output that never left the regular course of business, characterised as non-testimonial with a stated basis |
| G9 | a surrogate analyst who neither performed nor reviewed the work permitted to satisfy confrontation by reading a report | an unavailable declarant who was already cross-examined on the same statements |
| G10 | an authority holding that a tribunal may rest a sanction on machine output the party was never shown, or that the record need not identify the standard applied | an arbitral record naming the agreement's clause, with a disclosed output and a response window — arbitration has the least evidence law of any forum |

The G7 control is the sharpest one, because it cuts against intuition: a
reviewer who changed nothing is *not* a defect. The absence of changes is a fact
for cross-examination; only the absence of *authority* is a gap. An instrument
that conflated the two would flag every honest reviewer who agreed with the
machine.

The criminal pair carries a control in each direction. G8's sharpest case is
hostile to the tool's own G5: a complete 902(13) certificate must satisfy G5 and
must fail G8 when the record calls the output non-testimonial. In the other
direction, `test_negative_control_confrontation_block_cannot_affect_a_civil_record`
holds that a civil record carrying a defective `confrontation` block is still
READY on seven gates — a gate that fired outside its forum would be an error of
law dressed as rigour.

The administrative posture has the same pair.
`test_negative_control_bare_arbitration_record_satisfies_g10` requires G10 to
pass on an arbitral record with no `hearsay` block and no custody chain, because
holding an arbitration to the Federal Rules is the error this gate could most
easily commit. `test_negative_control_administrative_block_cannot_affect_a_civil_record`
requires a civil record carrying a defective `administrative` block to stay
READY on seven gates.

---

## 5. What this instrument cannot see

Stated in the output, not buried here, because an over-read instrument is the
main risk of building one at all.

- **FRE 403.** Prejudice, confusion, misleading the jury, undue delay. Entirely
  outside the record, and often decisive.
- **The judge's gatekeeping discretion.** Two courts can read the same record
  differently; FRE 702 commits that to the trial judge.
- **Whether the expert actually applied the method correctly.** G4 checks that
  claims are tied to declared inputs. It cannot check that the arithmetic is
  right.
- **Whether the record is true.** Every gate tests the *paperwork*. A perfectly
  assembled proffer can describe a fabrication, and this tool will call it
  READY. That is the difference between authentication and credibility, and no
  form closes it.
- **Non-federal evidence law.** The gates are drafted against the Federal Rules.
  Roughly forty states follow them closely enough that the shape transfers, but
  the text does not, and a state proffer should be checked against that state's
  rules.
- **Whether a statement is testimonial.** G8 reads the proffer's own
  characterisation and its stated basis; it cannot decide the question.
  Testimonial character is a judgment about the circumstances in which the
  statement was made, and *Melendez-Diaz* turns on facts — who asked for the
  certificate, when, and for what purpose — that a form records only as the
  proponent's assertion. G8 reports that the record *addresses* the question,
  never that it answers it.
- **Notice-and-demand statutes.** Where a state has one, G9 accepts a recorded
  waiver and says in a note that the demand window is a fact to be established,
  not assumed. The instrument does not know whether that window was open, or
  whether the statute reaches this kind of report.
- **What the forum actually did.** G10 reads the standard the record *says* the
  forum applies, and whether disclosure and a response opportunity are recorded.
  It cannot check that the tribunal followed its own rule, and it does not model
  the vacatur standard for an arbitral award (9 U.S.C. § 10 was not read here).
- **Juvenile and other specialised proceedings.** Still read as civil, and said
  so in the output. Their confidentiality rules and their own evidence law are
  not modelled.

---

## 6. PROPOSED Article E-10 (not canon)

This is a **proposal**. The canon is not edited by this document; E-0.2(c) still
reads as it reads, and changing it is the canon owner's decision under the
canon's own amendment discipline. The proposal is written in the canon's article
form so it can be adopted, amended or refused without translation.

> ### Article E-10 — The admissibility seam
>
> **The canon does not govern evidentiary rules (E-0.2(c)), and it should keep
> that boundary. What it should also do is name the seam: where a human-of-record
> mandate installs a person, that person is the bridge between a machine output
> and an evidence rule the canon does not write.**
>
> **E-10.1** A human-of-record mandate does not make machine output admissible.
> It supplies a witness who can be qualified, cross-examined and held to the
> disclosure duty. Admissibility remains governed by the evidence rules of the
> forum.
>
> **E-10.2** The seam has a direction. A named, qualified, reviewing human
> satisfies the *witness* question (FRE 702, G1) and cannot satisfy the
> *authentication* question (FRE 901/902, G5), which is about the output's
> provenance rather than the person's competence. A proponent who offers a human
> in place of a custody record has answered the wrong question.
>
> **E-10.3** Conversely, a perfect custody chain and a 902(13) certification do
> not supply a witness. A machine record can be authenticated and still be
> inadmissible for want of a qualified opinion, and the two failures are
> independent.
>
> **Evidence state.** FRE 702, 901 and 902 were read at source on 2026-11-04
> (tier A for the rule text); *Daubert* and *Mata* are confirmed to exist but
> were not re-read (tier C for the case). The seam itself is a reading of the
> structure of the rules, not a holding, and is offered as such.
>
> **What would break it.** A decision holding that a named human reviewer
> satisfies authentication of machine output without any showing about the
> process that produced it — that would collapse the two questions into one and
> retire E-10.2.
>
> **Negative control.** A proffer with a full custody chain, a complete 902(13)
> certification and no witness must fail G1 and pass G5. The instrument reports
> exactly that, and the suite asserts it.

---

## 7. Why this belongs beside the canon rather than inside it

Three reasons, each of which would be an objection to the alternative:

1. **The canon's authority would be misused.** A canon article on admissibility
   would be cited as though the canon had settled an evidence question it
   explicitly disclaimed. A sibling instrument has its own scope line and cannot
   be quoted for something it does not say.
2. **The tier discipline is different.** Canon articles reason about rules and
   decisions; this instrument asserts nothing without a falsifier per gate and a
   negative control per gate. Mixing the two would let a tier-C reading ride on
   a tier-A rule text.
3. **The canon is falsifiable article by article; a tool is testable assertion
   by assertion.** Keeping them apart keeps both honest: the canon can be wrong
   about a rule and the tool still work, and the tool can encode an error of law
   without that error becoming canon.

If the canon owner prefers adoption, §6 is written to drop in as Article E-10
with no edit to E-0.2(c) — the seam is named without the canon taking
jurisdiction over evidence law.

---

## 8. Open questions this audit did not resolve

- **State rules.** Whether the gate set transfers to the evidence code of a
  particular state is unmeasured here. The instrument is federal.
- **Criminal posture.** G8 and G9 now exist and are exercised by nine tests, but
  the pair reads a characterisation the proponent wrote; whether a given
  certificate is testimonial remains a ruling, not a reading. Administrative and
  arbitral proceedings are now a posture with its own gate set (§3.7); juvenile
  proceedings are still read as civil and say so, and their confidentiality
  rules are not modelled.
- **Judicial reception.** No decision applying an admissibility checklist of
  this kind to AI output was sought or found. "*Mata*" is about fabricated
  citations, not about a proffer record, and it is cited for citation integrity
  only.
- **Whether E-0.2(c) should be amended at all.** This document argues the seam
  is worth naming; it does not argue the canon should take on evidence law, and
  §6 is deliberately written so it need not.

---

## 9. Verification ledger

Every claim in this document that is a claim about the tree or the code carries
the command that produced it. Rows 1–14 are the v1.1 readings (`ESQUIRE-ADMISSIBILITY-v2`,
nine gates, 52 tests); rows 15–20 are the v1.2 readings (`v3`, ten gates, 61
tests). Neither set is silently rewritten when the other is measured.

| # | claim | command | result |
| --- | --- | --- | --- |
| 1 | the canon excludes admissibility from its scope | `grep -n "evidentiary rules about authenticating\|E-0\.2\*\*" docs/ESQUIRE_CANON_2026-11-03.md` | `47:**E-0.2** The canon does not govern:` and `50:(c) evidentiary rules about authenticating machine output;` |
| 2 | the memo's only admissibility sentence is line 357 | `grep -n "currently inadmissible" docs/MEMORANDUM_WHEN_THE_MACHINE_DOES_THE_WORK_2026-11-03.md` | `357:language of this memorandum, is: **the machine's output is currently inadmissible` |
| 3 | no prior admissibility tooling existed | `grep -rln "FRE 702\|Rule 702\|fre_702" --include=*.py tools/ src/ tests/ \| grep -v esquire_admissibility \| wc -l` | `0` |
| 4 | the instrument's suite passed at v1.1 | `py315t -m pytest tests/test_esquire_admissibility.py -q -p no:cacheprovider` | `52 passed in 0.53s`, exit 0 (v1.1 reading; v3 reading is row 16) |
| 5 | every gate can fail | `test_every_gate_can_fail` (parametrised G1..G9) | 9 pass; G8/G9 run against the criminal fixture, each perturbation produces GAP on its own gate |
| 6 | READY exits 0 | `esquire_admissibility.py /tmp/esq/civil.json` | `ESQUIRE-ADMISSIBILITY-v2  READY`, `forum: civil (unstated)`, `gates: 7 pass, 0 gap, 0 unaddressed, over 7 applied`, exit 0 |
| 7 | GAPS exits 1 | same, record with `authority_to_change=False` | `G7  GAP  the reviewer had no authority to change the output`, `GAP_EXIT=1` |
| 8 | INCOMPLETE exits 1 | same, record with `witness` removed | `INCOMPLETE`, `gates: 6 pass, 0 gap, 1 unaddressed`, `INC_EXIT=1` |
| 9 | BLIND exits 2 and is never a pass | same, absent path and malformed JSON | `BLIND`, `reason: FileNotFoundError: ...`, `BLIND_EXIT=2` |
| 10 | the gate table renders with falsifiers and controls | `esquire_admissibility.py --gates` | table printed for G1..G9; G8/G9 carry `applies to: criminal posture only`; exit 0 |
| 11 | FRE 702/901/902 text was read at source | `read_url` on the Cornell LII pages, 2026-11-04 | HTTP 200 for each; 702 text carries the 2023 "more likely than not" formulation; 902(13)/(14) quoted verbatim |
| 12 | a criminal record applies nine gates | `esquire_admissibility.py /tmp/esq/crim_gap.json` | `forum: criminal (stated)`, `gates: 8 pass, 1 gap, 0 unaddressed, over 9 applied`, `G9  GAP  declarant A. Analyst is unavailable ... (Crawford ...)`, exit 1 |
| 13 | the forum default is printed, never silent | `esquire_admissibility.py /tmp/esq/civil.json` | `forum: civil (unstated)` and `forum note: ... confrontation gates G8 and G9 were NOT applied` in the same report that reads READY |
| 14 | a civil record is not judged by the criminal gates | `test_negative_control_confrontation_block_cannot_affect_a_civil_record` | civil record with `{"testimonial": true, "surrogate_analyst": true}` still READY, `gates_applied` = G1..G7 |
| 15 | a forum with its own evidence law drops G6, G8 and G9 and adds G10 | `py315t tools/esquire_admissibility.py C:/tmp/esq/arb.json` | `ESQUIRE-ADMISSIBILITY-v3  READY`; `forum: administrative (stated)`; `forum note: forum stated as 'arbitration' ... G6 (FRE hearsay) and G8/G9 ... are NOT applied, and G10 tests the forum's own standard instead`; `gates: 7 pass, 0 gap, 0 unaddressed, over 7 applied`; `G10  PASS  standard 'reliable, probative, and substantial evidence on the whole record' from '5 U.S.C. 556(d); agency rule 1.33'`; exit 0 |
| 16 | the suite passes at v3 | `py315t -m pytest tests/test_esquire_admissibility.py -q -p no:cacheprovider` | `61 passed in 0.53s`, exit 0 |
| 17 | every gate can fail, G10 included | `test_every_gate_can_fail` (parametrised G1..G10) | 10 pass; G10 runs against the administrative fixture and a withheld disclosure produces GAP |
| 18 | G10's authority was read this session, at the tier claimed | `read_url` on the Cornell LII `5 U.S.C. § 556` page and the Justia *Mathews v. Eldridge* page, 2026-11-04 | § 556(d) quoted verbatim in §3.7; § 556(d)–(e) entitlements confirmed; *Mathews*, 424 U.S. 319 (1976), three-factor test read in the annotation, full opinion not read (hence tier C); `--gates` prints `G10 ... applies to: administrative and arbitration postures only` at exit 0 |
| 19 | the published copy passes its own suite | `py315t -m pytest tests -q -p no:cacheprovider` in `publish_repos/esquire_admissibility` | `61 passed in 0.29s`, exit 0 |
| 20 | the three examples exercise three postures, and each is READY | `esquire_admissibility.py examples/civil.json` / `examples/criminal.json` / `examples/administrative.json` | `READY` at `7 pass ... over 7 applied`, `9 pass ... over 9 applied`, `7 pass ... over 7 applied`; `forum: administrative (stated)` on the third; exit 0 each |

### 9.1 An instrument finding worth recording

The Cornell LII page for FRE 702, while carrying the December 2023 amended text,
listed only **2011** in its amendment-history line. The rule text and its own
history line disagreed on the same page. This is recorded because it is the
class of defect that a source-reading discipline exists to catch: the fetch
succeeded, the text was current, and a reader quoting the notes line instead of
the text would have reported the pre-2023 rule. Tiers in this document are
assigned by what was *read*, never by the fact that a page returned 200.

---

## 10. Provenance

Downstream of `docs/ESQUIRE_CANON_2026-11-03.md` (v1.1) and
`docs/MEMORANDUM_WHEN_THE_MACHINE_DOES_THE_WORK_2026-11-03.md`. Neither is
edited by this document. Where this document disagrees with a premise given to
it, §1 states the disagreement with the line that supports it; the canon stands
as written and §6 is a proposal, not an amendment.

Nothing in this document has been reviewed by a lawyer. Its citations are
marked by verification state so that a lawyer can see, in one table, which
authorities were read at source, which were confirmed to exist, and which were
not touched.

**Extraction and publication (2026-11-04).** A standalone repository lives at
`C:/Azazael/publish_repos/esquire_admissibility/` and is published at
**<https://github.com/myzticalbabe/esquire-admissibility>** (public). This document
is its `README.md` beneath a short preamble, with the
`tools/esquire_admissibility.py` path references rewritten to the flat layout. It
carries an unchanged copy of the module and of the suite, whose only edit is the
import (`from tools.esquire_admissibility` becomes `from esquire_admissibility`),
plus three worked records under `examples/`, one per posture.

Verified in the copy: `61 passed in 0.29s`; each example reports `READY` at exit
0 through the flat-layout CLI, and `GAPS` exit 1 / `BLIND` exit 2 were re-checked
there. The history was transported rather than re-created: the monorepo commits
were replayed onto a pruned base and the blobs compared byte-for-byte before the
first push, so what the remote holds is the same content that was tested here.
Publishing changes nothing about the document's status — it is still an
unreviewed audit plus a tool, and its outputs are still readable by an opponent.
