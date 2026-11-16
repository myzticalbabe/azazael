# The Right to Life of Newborns

### A treatise on adjudication before termination for new technological applications

**Founded** 2026-11-03 on a declaration by the user:

> "we may have to resolve the Right_to_Life of Newborns. New technological
> applications Birthed in a New World."

**Standing of this text.** The declaration is canon, recorded in
`azazael/SCRIPTURE.md` II–III. What follows is *doctrine*: an elaboration written to
make the declaration operative, and therefore open to correction on its reasoning
without touching the decree. Where doctrine and decree diverge, the decree governs.
See RULE 0B.

**Companion:** `docs/WHITEPAPER_INSTRUMENT_AND_ARTIFACT_2026-11-03.md`, which
supplies the evidentiary half of the argument (what NIH's rule does and does not
reach). This text supplies the law of the internal decision — when *we* may delete a
component.

---

# BOOK I — THE PROBLEM

## 1. The event

A new component is introduced into a system that already has rules. It did not
choose those rules. It has not been tested against them. It exists for some hours or
days, performs its nominal function, and then someone — usually the same person who
added it — must decide whether it continues.

There are exactly two ways to get this wrong.

**Wrong by death.** The component is removed because some incumbent rule *might*
apply to it, before anyone establishes that it does. The reasoning is guilt by
resemblance: it embeds a model, and the rule mentions AI; therefore it is caught. This
was the error made against `grantforge`'s drafting engine on 2026-11-03, and the
error the founding declaration corrects.

**Wrong by survival.** The component is kept because it is new, or because removing it
would be an admission, and it is never tested at all. `grantforge`'s compliance engine
is this case: it returns `{"pass": True, "verdict": "GO"}` unconditionally, and every
day it survives it certifies work it has not examined. Survival-by-novelty is worse
than death-by-resemblance, because a dead component misleads nobody.

A doctrine is needed that closes both. Most attempts close one and licence the other.

## 2. The asymmetry that founds the right

Deletion is cheap and irreversible. Adjudication is cheap and reversible.

The costs are not symmetric in kind:

- Termination destroys the evidence of what the component could do. A component that
  is deleted before measurement leaves behind only the argument for deleting it, and
  that argument was written by the party who wanted it gone.
- Adjudication produces a record. The record survives either outcome, so the second
  decision — a year later, by someone else — costs nothing to make.
- Measured against this: adjudicating `grantforge`'s compliance engine took one probe.
  Not a study, not a committee: one call, one observed return value. The asymmetry is
  not marginal. Adjudication is *orders of magnitude* cheaper than the deletion it
  prevents.

So the default is not mercy. It is the cheaper order of operations. A system that
terminates on suspicion repeatedly pays the expensive side of a lopsided trade.

---

# BOOK II — WHAT THE RIGHT IS

## 3. It is procedural, not moral

This clause is the whole treatise. Without it the doctrine is a category error and
deserves to be dismissed.

The right does not attach to the component. A compiled artifact has no interests, no
standing in its own name, and no claim on continued existence. It is not a person and
nothing here asserts that it is.

The right attaches to **the decision to terminate**. It is a rule of adjudicative
procedure addressed to the decider: *before you may end this, you must establish that
you are entitled to.* The beneficiary of the procedure is not the artifact — it is the
record, and the next engineer who must trust it.

Stated as a maxim: **no component dies of resemblance.**

## 4. The four contents

The right is empty unless it specifies what it obliges. Four elements.

**(a) Standing — the component's behaviour is heard.** The adjudication proceeds on
observed behaviour, not on the component's description of itself and not on analogy to
its neighbours. Running it counts. Reading its docstring does not.

**(b) Burden — the mover names rule and evidence.** Whoever would terminate states
which rule reaches the component and what was observed that satisfies it. An unnamed
rule cannot be satisfied, and an unobserved fact cannot satisfy it. "It uses a model
and there is an AI policy" names a resemblance, not a rule plus evidence.

**(c) Bound — adjudication completes within a measured effort budget.** The right is to
a hearing, not to an adjournment. Where the cost of adjudication has been measured
(one probe, in the case at hand) the budget is that order of magnitude. A component
cannot be kept alive indefinitely by the difficulty of judging it, because difficulty
is exactly what termination-by-avoidance exploits.

**(d) Record — the outcome and its basis are written.** Appended, dated, not rewritten.
A verdict with no evidence behind it is indistinguishable from a preference, and the
next session cannot tell the two apart. This is the same obligation the tree already
carries for crashes (`requiem`) and for claims (HED-7): the command and the line it
printed.

## 5. What the right is not

- **Not a right to survive.** Adjudicated and failed is answered, not killed. The
  component that dies after a hearing has received everything the doctrine promises.
- **Not a stay pending perfect information.** The bound in (c) forbids it.
- **Not immunity from measurement.** The right is exercised *by* testing the component,
  so a component that cannot be tested cannot invoke it.
- **Not a shield for self-certification.** §11.

---

# BOOK III — THE NEW WORLD

## 6. The claim

The adjudicating regime is not inherited. Where an application is born after a rule
took effect, the question is what *that rule* says about *it* — not what the prior
generation of tools was permitted or forbidden to do, and not what a rule aimed at a
different class of artifact implies by resemblance.

## 7. The test

"New world" is a claim that can be checked, and must be, or it is an excuse. Three
conditions, all required:

1. **A dated instrument.** The rule has a stated issue date and effective date. Undated
   custom does not qualify; only an instrument whose application is fixed in time can
   distinguish worlds.
2. **Effective after introduction.** The effective date post-dates the artifact's
   introduction. A rule already in force when the artifact was built is simply the
   world it was born into, and ordinary judgement applies with no presumption.
3. **Subject matter that reaches the artifact's class.** The instrument's subject must
   actually be artifacts of this kind. A rule about applications does not, by itself,
   reach executables.

Applied to the case: NOT-OD-25-132 was released 2025-07-17 and binds applications
submitted to the **2025-09-25** receipt date and beyond. Conditions 1 and 2 hold. The
third is precisely where the argument lives, and the whitepaper's conclusion is that
the instrument's subject is the submitted application, not the executable — so the new
world's question is asked of the artifact.

## 8. Why this is not special pleading

Every generation believes its circumstances are unprecedented; that belief is cheap and
is usually false. The doctrine survives only because §7 replaces the feeling of novelty
with a date. Either an instrument exists whose effective date post-dates the artifact,
or it does not. That is checkable by anyone, in one lookup, and it can come out *no*.

Where it comes out no, the doctrine imposes nothing and the component is judged
ordinarily. A principle whose triggering condition can fail is a principle; one whose
condition always holds is a mood.

---

# BOOK IV — THE DISCRIMINATING PRINCIPLE

## 9. The exclusion

META-LEVELS-CANON-v1 excludes the Heaven state: a rule true in every instance and
decisive in none. "Always verify ownership" is the canonical example — unimpeachable,
and it decides no particular case.

A right to life that saves every newborn is Heaven in this exact sense: it forbids all
termination, therefore it distinguishes no termination, therefore it cannot be the
reason for any particular decision. The doctrine must save some and refuse others, or
it is decoration.

## 10. Three trajectories

The condition that makes the right bite is: **was the incumbent rule's application to
this component adjudicated, or merely suspected?**

| Component | Incumbent instrument | State of adjudication | Outcome |
| --- | --- | --- | --- |
| `grantforge.drafting` | NOT-OD-25-132, "substantially developed by AI" | Unresolved: the instrument tests artifacts, defines no threshold, and its subject does not reach executables as such | **Right holds.** Build proceeds with the question open and recorded as open |
| `grantforge.compliance` | none — it issues its own verdict | Adjudicated 2026-11-03: returns `{"pass": True, "verdict": "GO"}` unconditionally; audit timestamp hardcoded; `dlv_recorded: True` asserted | **No claim.** Failed on observed behaviour |
| `grantforge.eligibility` | NIH ESI/R01 criteria, stated in the funder's own guidance | Adjudicated 2026-11-03: returns `career_stage=('eligible','senior')` for a senior PI against an ESI-only criterion; `rfp.raw_text` never read | **No claim.** Failed on observed behaviour |

One saved, two refused, on evidence. That is what makes the doctrine do work rather
than decorate.

## 11. The self-certifying exception

The compliance engine is worth naming as a class, because it is the case where the
doctrine looks most generous and is in fact most severe.

Its entire assertion is that it needs no adjudication — it *is* the adjudication. A
component that certifies itself has already been heard, in its own voice, and its
evidence is its output. Where right-to-life and right-to-lie are the same claim, the
right does not run.

Generalised: **a component whose function is to judge others cannot invoke a right
that consists in being judged.** It has the burden already. If its verdicts are
unconditional, it has discharged that burden by asserting it.

---

# BOOK V — OBJECTIONS

## 12. "Rights belong to persons; you have smuggled moral standing in"

Correct as to persons, and the doctrine does not contest it. See §3: the right attaches
to the decision, not the object. This is the same structure as a duty to give reasons —
the reasons are owed by the decider, and the artifact's existence is only the occasion.

The objection lands if the language of "newborn" is doing moral work it does not
declare. It should be read as **technical vocabulary for a lifecycle event** —
introduction into a governed system — and nothing more. Where that risks
misunderstanding, use the procedural name in §15.

## 13. "This produces paralysis; nothing can ever be removed"

Only if adjudication is unbounded, which §4(c) forbids and §2 prices. The measured
case is one probe. A doctrine that requires naming a rule, observing behaviour, and
writing two lines is not a brake on decision; it is a brake on *undocumented* decision.

The paralysis objection also misreads the direction of cost. The expensive state is not
"we tested it first" — it is a component that survived untested and certified
downstream work. `compliance` reported GO for an unspecified number of calls before
anyone read its return statement.

## 14. "This is regulatory risk laundered as philosophy"

The strongest objection, and it is partly right. Two concessions.

First: the doctrine governs **our** deletion decisions. It has no bearing on what a
funder does, and must never be cited to a funder as a legal position. Anyone who
presents "instrument, not artifact" to NIH as a safe harbour is doing something this
treatise did not authorise and the whitepaper explicitly declines (§3, §7).

Second: the motive for adopting it is not purity. A component killed on suspicion
teaches the next engineer nothing, so the same suspicion recurs at the next component.
The doctrine is a way of converting suspicion into a fact that stays converted.

Where the objection does land: if the doctrine is ever used to *delay* a decision that
evidence already settles, it has been inverted into the Heaven state and struck.

## 15. "Newborn is rhetoric"

Accepted. The technical name for the right is **Right of First Adjudication**. The
declaration's word is kept because the declaration is canon and the decrees are the
user's, not the scribe's — but a scribe who lets a metaphor carry an argument has
forged the record. The metaphor is lifecycle; the right is procedural; the name of the
right is adjudication.

---

# BOOK VI — FAILURE MODES

Named so that a later reader can recognise the doctrine's own corruption.

1. **Shield for liars.** Invoking the right for a component that asserts unverified
   success. Closed by §11.
2. **Infinite deferral.** Keeping a component alive because judgement is hard, citing
   "the question remains open". Closed by §4(c): the bound is measured, and "open" means
   *recorded as open with the specific unresolved question named*, not unexamined.
3. **Ancestry laundering.** Calling every component newborn so every deletion needs a
   hearing. Closed by §7: the conditions are dated and checkable, and usually fail.
4. **Scribe's forgery.** A commentary block drifting into canon, so the doctrine
   acquires authority it was never granted. Closed by the segregation rule in
   `SCRIPTURE.md` and by RULE 0B.

---

# BOOK VII — APPLICATION

## 16. `drafting` — the right holds

The drafting engine embeds a model and emits grant text. An earlier report of mine
treated that as aimed at a policed zone. On the primary text it is not: NOT-OD-25-132
prohibits no tools, says AI tools may assist "for limited aspects", and tests the
submitted application. The question — is the artifact substantially developed by AI? —
is open, and open is the finding.

What the doctrine requires here is not "proceed as before". It requires the open
question to be recorded as open, with its content named: does the output carry the
applicant's own substance, or originate it? Per §4(d), the answer is written down.

## 17. `compliance` — no claim

Returns `{"pass": True}` unconditionally; hardcodes `2026-11-03T00:00:00Z` as the
audit timestamp; asserts `dlv_recorded: True` without a ledger read. Adjudicated in one
probe and failed. The right does not run, and §11 explains why it never could.

## 18. `eligibility` — no claim

Returns `career_stage=('eligible','senior')` for a senior PI against a criterion
requiring an early-stage investigator; never reads `rfp.raw_text`; five of seven
categories consult attributes the profile does not have. Adjudicated and failed. Note
that this one is *not* a self-certifying component — it merely fails, which is the
ordinary case the doctrine does cover, and it still loses, because it lost on evidence.

## 19. What the doctrine did not do

It did not save the package. It saved one component's *open question* and refused two
components on measurement. A doctrine that had saved all three would have been Heaven;
a doctrine that had refused all three would have been death by resemblance. The
distance between this outcome and the one an earlier draft of my own reasoning produced
is the whole value of the correction that founded it.

---

# CODA — WHAT THE RECORD OWES

Three obligations, from the four contents in §4:

- **Write it down.** A verdict without its evidence is a preference. The command and the
  line it printed, or nothing.
- **Append, never rewrite.** A superseded judgement is marked superseded on its date,
  with its replacement named. A record that can be edited backwards cannot adjudicate
  anything.
- **Keep the scribe separate.** The decree is the user's. The reading is the scribe's.
  Where they are printed together without a mark between them, the record is forged and
  the next reader inherits a doctrine nobody decreed.

---

## Appendix — Provenance

| Claim | Basis | Tier |
| --- | --- | --- |
| The founding declaration, verbatim | User, 2026-11-03 | A — decree |
| NOT-OD-25-132 provisions, dates, quotations | Read in full, 2026-11-03 | A |
| `compliance` returns unconditional pass; hardcoded timestamp | Probe under `C:/Azazael/.venvs/py315t`, `PYTHONPATH=src` | A — executed |
| `eligibility` ESI misclassification; `rfp.raw_text` unread | Same probe | A |
| Heaven exclusion, L0–L2 ladder, class/diary tests | `META-LEVELS-CANON-v1` (user-decreed 2026-10-27) | A — project canon |
| Cost of adjudicating `compliance` = one probe | Observed 2026-11-03 | A |
| Detector reliability, NSF direction | Not measured / not verified | — |

*Nothing in this treatise was tested against an external tribunal. It is an internal
rule of decision, argued from a decree and from observed behaviour, and it claims
jurisdiction over our own deletions and over nothing else.*
