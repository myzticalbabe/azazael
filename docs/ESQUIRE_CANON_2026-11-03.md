# THE ESQUIRE CANON

### A whitepaper and advisory opinion on the human of record

**Version:** 1.0 — 2026-11-03
**Status:** advisory. Not legal advice, not an opinion of counsel, not a restatement.
**Derived from:** `docs/MEMORANDUM_WHEN_THE_MACHINE_DOES_THE_WORK_2026-11-03.md` (the memorandum),
`docs/PANEL_RULINGS_2026-11-03.md` (five seats, six questions, commits `e25ef8a1` and `48e49505`)
**Evidence:** `logs/legal_panel/2026-11-03/` and `logs/legal_panel/deepseek.json`

---

## Preface — why a canon and not another memorandum

The memorandum argued a thesis. The panel tested it and returned six rulings, five of which
qualified or narrowed the thesis and one of which falsified its central word. A thesis that
has been tested and narrowed does not remain a thesis: what survives is a **set of rules
about how to tell one kind of human-of-record requirement from another**, and a procedure
for applying them.

That set is this canon. It is written in articles because articles can be falsified one at a
time. Each article states a rule, the evidence behind it, the state of that evidence, and
the observation that would break it. An article with no falsifier is not in this document.

The canon is called *Esquire* for the thing it is about: the human installed at the point
where a machine did the work — the person whose name makes an instrument effective. The
canon's subject is not who may practise law. It is when the law requires a named human, and
what that requirement is *for*.

---

## Part I — Scope

### Article E-0 — What the canon governs, and what it does not

**E-0.1** The canon governs **human-of-record mandates**: any legal rule whose operative
effect is that a natural person must be named, must supervise, must sign, must author or must
be credited before a machine-produced output has legal effect.

**E-0.2** The canon does not govern:
(a) rules about who may appear before a tribunal (admission, standing, unauthorised practice);
(b) product-safety approval regimes that regulate the machine and not the human;
(c) evidentiary rules about authenticating machine output;
(d) contract terms between private parties, except where a mandate makes them enforceable.

**E-0.3** The canon is descriptive of a pattern and normative only in the weak sense that it
recommends which description to use. It creates no cause of action and bars none.

---

## Part II — The Canon

### Article E-1 — The naming rule

> **A requirement that installs a human where a machine performed the work is a
> *human-of-record mandate*. It is not featherbedding, and calling it that is an error of
> law as well as of usage.**

**Basis.** NLRA §8(b)(6) reaches a payment exacted by a labour organisation for services not
performed. *American Newspaper Publishers Assn. v. NLRB*, 345 U.S. 100 (1953) narrowed the
provision to that exaction. A state board, a court rule or a funder's policy is not a labour
organisation and its condition is not an exaction, so two of the term's three elements are
absent whenever the mandate is regulator-imposed.

**Evidence state.** Falsifier 1, run against five seats with no shared context: **5/5**
rejected the term; **3/5** also rejected the characterisation of oversight rules as
rent-seeking at all. The surviving narrow form — *a human is installed where a machine did the
work* — was conceded by every seat, including the ones that rejected the word.

**What would break it.** A decision applying §8(b)(6) language to a regulator-imposed
condition. None was produced. The proposition is therefore stated as a usage rule with a
statutory anchor, not as a holding.

**Consequence.** "Featherbedding" may appear in the canon exactly once: as the rejected
analogy, with the narrowing stated in the same breath.

### Article E-2 — The convergence rule

> **Five regimes converge on the same shape. They do not converge on the same rule, and the
> canon must say which is which.**

The shape: a human is named at the point of machine output. The rules differ in what the
naming protects:

| regime | what the named human protects | route to the rule |
| --- | --- | --- |
| copyright authorship | the public's interest in an author to whom rights and remedies attach | judicial construction of "originality", 17 U.S.C. §102(a) |
| patent inventorship | the statutory bargain, via a defined "individual" | statutory definition, 35 U.S.C. §100(f)–(g) |
| professional responsibility | the client | conduct rules and licensing |
| data protection | the data subject | GDPR Art. 22's "solely automated" trigger |
| funder originality | **the funder's own evaluation capacity** | programme policy |

**E-2.1** The first four protect a **third party's** rights or interests. The fifth protects
the **funder's own** screening function. That is a difference of species, not of degree, and
the canon treats it as the boundary of the class.

**E-2.2** The two IP rules are not twins even where they converge. Authorship rests on
construction and is therefore exposed to interpretive expansion; inventorship rests on a
definition and is therefore resistant to it. A change in one does not predict the other.

**Evidence state.** Four seats independently drew the legal/functional distinction; one seat
(`deepseek`) supplied the third-party/funder split unprompted. Tier C reasoning evidence.

**What would break it.** A regime whose human requirement is enforced *by* the funder *for*
the funder's own liability to a third party — that would collapse the species split.

### Article E-3 — The shape test, not the trigger test

> **The substitution axis describes the class; it does not define it. A mandate can bite a
> non-substituting use, and those mandates are the canon's boundary cases.**

**E-3.1** The test for membership is whether the mandate installs a human **at the point
where a machine produced the output**, not whether a human's paid work was displaced.

**E-3.2** Boundary cases, each named by a seat and each real:

- **EU AI Act Art. 14** — oversight required by risk classification (Art. 6, Annex III),
  irrespective of whose work was displaced.
- **Medical-device AI** — oversight required even where the machine performs what no human
  could perform at all.
- **A funder's artefact ban** — a prohibition on machine-generated content, which is a
  generation rule and not a substitution rule.

**E-3.3** The canon therefore states the axis as *sufficient-shape*: mandates that install a
human where a machine did the work are substitution-shaped; mandates may exist that install a
human without any displacement, and they are not thereby outside the law — they are outside
this canon's thesis.

**Evidence state.** Every answering seat produced at least one counter-example, and no two
seats produced the same one first. The counter-examples are the canon's most valuable output
and are preserved in `PANEL_RULINGS` §R3 verbatim.

**What would break it.** A risk-based oversight regime that, on its face, applies only where
a human role existed and was displaced. That would make the axis a trigger after all.

### Article E-4 — The beneficiary test

> **For any human-of-record mandate, ask: who is protected — a third party, or the
> profession's market? The answer is a fact about the rule's operation, not about its
> preamble.**

**E-4.1** A mandate whose operative effect is to make the human's *licence* the condition of
the output's validity protects the licensee's market. A mandate whose operative effect is to
make a *responsible person* answerable for the output protects the third party.

**E-4.2** Both can be present. The canon does not require a single motive; it requires the
drafter to state which effect the rule actually produces, and to name the evidence.

**E-4.3** The client-protection case must be stated, not assumed away. Professional-conduct
rules on technology (ABA Formal Opinion 512 is the standard example) impose competence and
confidentiality duties that run to the client; a canon that treats every such rule as
rent-seeking misdescribes the target and weakens the claim it is trying to make.

**Evidence state.** This is the canon's sharpest live disagreement: one seat dissented that
the memorandum "understates that professional-responsibility rules ... exist primarily for
client protection, not guild rent-seeking." The dissent is part of the article, not a
footnote to it.

### Article E-5 — Displacement is not extinguishment

> **Inserting a human removes the "solely automated" trigger. It does not remove the right;
> it reroutes it to a human defendant.**

**E-5.1** GDPR Art. 22(1) governs decisions based *solely* on automated processing. A human
in the loop defeats the trigger, and with it the Art. 22(3) safeguards. That is a real and
adverse effect on the data subject, and the canon records it.

**E-5.2** The effect is not extinction. The inserted human acquires duties of supervision,
and the data subject acquires a defendant with assets and a duty of care. The correct verb is
**displace**, not extinguish; the correct claim is *the procedural route is closed*, not
*the right is destroyed*.

**E-5.3** A withdrawn instrument proves only that a regime was proposed and abandoned. It
cannot supply the content of the liability rule that would have applied, and it cannot carry
the waiver reading. Where the waiver reading rests on a preprint and a withdrawal, it is
marked tier C and may not be pleaded as settled.

**Evidence state.** Four seats accepted the trigger analysis; one argued the opposite
direction on duties (non-delegable supervision); one named this as the memorandum's most
exposed claim. All five treated the withdrawn directive as incapable of proving the
substantive rule.

**What would break it.** Authority holding that a nominal human reviewer, with no power to
alter the outcome, nonetheless satisfies Art. 22 — that would make the human a fig leaf in
law and not only in fact, and would restore part of the extinction reading.

### Article E-6 — The three gates

> **An antitrust challenge to a human-of-record mandate must pass three independent gates.
> Failing any one ends the claim; passing one proves nothing about the others.**

1. **State action (Parker).** Is the mandate the board's own, or the legislature's? A mandate
   that merely implements a statutory command is not the board's restraint.
2. **Active supervision.** A board that is a market participant — its members are the
   competitors the rule benefits — loses immunity absent active state supervision.
   *N.C. State Bd. of Dental Examiners v. FTC*, 574 U.S. 494 (2015).
3. **Injury and standing.** A plaintiff outside the market the rule protects must show
   antitrust injury of the type the statutes address. A vendor who would have sold machine
   work, or a client who would have bought it, has a standing question that no seat resolved.

**E-6.1** *Goldfarb v. Virginia State Bar*, 421 U.S. 773 (1975) establishes that the learned
professions are not exempt from §1. It does not establish that any particular board rule is
unlawful, and the canon does not treat it as doing so.

**E-6.2** The correct description of the lever is **available and unlitigated**. No decision
reaching a state board's AI-substitution rule was produced by any seat or found for this
canon.

**Evidence state.** Split panel: two seats live, one academic, one live-with-standing-caveat,
one unreasoned. The split is itself the finding and is preserved.

### Article E-7 — The evidence ladder

> **A canon article carries the tier of its weakest load-bearing source.**

| tier | source | may carry |
| --- | --- | --- |
| A | primary instrument (statute, rule, order) | a rule statement |
| B | official index or reporter | identity and existence |
| C | reasoned secondary source, preprint, model seat | a hypothesis, explicitly marked |
| D | commentary, snippet, social | a lead, never a rule |

**E-7.1** A model seat is tier C by construction: it reasons from training data, may
hallucinate a citation, and cannot be cross-examined. Five seats agreeing raises confidence
in a *reading*; it does not raise the tier of the underlying authority.

**E-7.2** Every 2026-era instrument cited in the memorandum (the funder policy, the preprint,
the withdrawal, the state statute's amendments) is **UNVERIFIABLE** in this canon's evidence
record until fetched, and is marked so in the citation table.

### Article E-8 — Honesty in both directions

> **A canon that records only the evidence against its thesis is a brief, not a canon.**

Each article must record: the strongest counter-example, the seat that dissented, and the
observation that would falsify it. The canon currently carries four counter-drivers that cut
against its own framing — risk-based oversight, tort accountability, client-protection rules,
and the funder species split.

### Article E-9 — Falsifiability

> **No article enters the canon without a falsifier and a negative control.**

**E-9.1** The falsifier names the observation that would retire the article.
**E-9.2** The negative control names a case the article must *not* capture — a mandate the
canon agrees is legitimate — and the canon must be shown not to mislabel it. For E-1 the
negative control is a genuine §8(b)(6) exaction; for E-4 it is a competence rule with no
market effect.

---

## Part III — The procedure

Applying the canon to a novel mandate takes five steps, in order. Stop at the first step that
fails, and record which step failed.

1. **Is it a human-of-record mandate?** Does a natural person have to be named, supervise,
   sign, author or be credited before the output has effect? (E-0.1)
2. **What does the naming protect?** Third party, or the profession's/funder's own capacity?
   (E-2, E-4) If the funder's own screen: the mandate is outside the class. (E-2.1)
3. **Is it substitution-shaped or risk-based?** If risk-based, it is a boundary case: the
   canon's thesis does not reach it, and the canon says so. (E-3)
4. **If the mandate is regulatory, run the three gates.** Parker, supervision, standing — each
   independent. (E-6)
5. **If the mandate is said to defeat a right, ask which right and which route.** Displacement
   of a procedural trigger is not extinction of the right. (E-5)

A mandate that survives all five is a candidate for the class. A mandate that fails at step 2
or 3 is not a counter-example to the thesis — it is outside it, and the canon's honesty
requirement (E-8) is to say so before an opponent does.

---

## Part IV — Application

| mandate | step 1 | step 2 | step 3 | step 4 | step 5 | canon verdict |
| --- | --- | --- | --- | --- | --- | --- |
| copyright: human authorship required | yes | third party (public) | substitution-shaped | n/a (judicial) | n/a | **in class**; authorship route is construction, not definition |
| patent: human inventorship required | yes | third party (public bargain) | substitution-shaped | n/a (statutory) | n/a | **in class**; definition route resists expansion |
| professional responsibility / supervision | yes | client (and market, in operation) | substitution-shaped where it names a human for machine output | gates live but unlitigated | n/a | **in class, contested beneficiary** |
| data protection: human in the loop | yes | data subject | substitution-shaped | n/a | **displaces** the Art. 22 route | **in class**; extinction claim barred |
| funder originality | yes | **the funder** | generation rule, not substitution | n/a | n/a | **outside the class**; boundary case |
| EU AI Act Art. 14 oversight | yes | third party (affected persons) | **risk-based** | n/a (regulatory, not competition) | n/a | **outside the class**; boundary case |
| medical-device AI oversight | yes | patient | **risk-based** | n/a | n/a | **outside the class**; boundary case |

---

## Part V — The opinion

*Advisory. Written in the register of an opinion because a canon without a holding is a
glossary; it is not the opinion of counsel and binds no one.*

**On the question whether the law installs a human where a machine does the work:** it does,
in at least five regimes, and the installation is the same shape in each.

**On the question whether that shape is one rule:** it is not. Two of the five are
construction, two are statutory or regulatory command, one is private programme policy. The
convergence is functional and the canon's authority stops at the function.

**On the question whether the requirement protects the public or the profession:** the answer
is not uniform and cannot be assumed. Where the mandate makes a licence the condition of
validity, it protects the market. Where it makes a person answerable, it protects the third
party. Most real mandates do both, and the canon requires the drafter to say which effect is
operative.

**On the question whether the requirement can defeat the rights it is said to protect:** it
can close a procedural route — Art. 22 is the clearest case — and it cannot be said, on the
evidence assembled here, to extinguish the right. The stronger claim depends on a preprint
and a withdrawn instrument, and the canon marks it tier C.

**On the question whether competition law reaches the mandate:** it can, in principle, where
the mandate is a market participant's own restraint without active supervision. It has not
been made to reach one, and a plaintiff outside the protected market must first establish
injury. The lever is available and unlitigated; the canon declines to call it live.

**On the question what the canon forbids:** it forbids three things. It forbids calling a
regulator's condition "featherbedding". It forbids treating five convergent rules as one rule.
And it forbids describing a displaced procedural route as an extinguished right.

---

## Part VI — What would change the canon

| observation | article retired or amended |
| --- | --- |
| a decision applying §8(b)(6) language to a regulator's condition | E-1 |
| a regime whose human requirement is enforced by the funder for the funder's liability to a third party | E-2.1 |
| a risk-based oversight rule that applies only where a human role was displaced | E-3.2 |
| authority holding a nominal reviewer satisfies Art. 22 | E-5.3 |
| a judgment reaching a board's AI-substitution rule on the merits | E-6.2 |
| a fetched primary text contradicting any tier-C reading above | E-7 |

---

## Part VII — Verification ledger

| claim | command | result |
| --- | --- | --- |
| panel ran on five labs, distinct angles | `python tools/legal_panel.py` | 5 seats answered across two passes; 5/8 in the dated pass; exit 1 |
| featherbedding falsified | `logs/legal_panel/2026-11-03/gemini.json`, `cohere.json`, `qwen.json`, `openrouter.json`, `logs/legal_panel/deepseek.json` | 5/5 reject; 3/5 reject rent-seeking framing |
| antitrust split preserved | same files | live: cohere, deepseek; academic: gemini; standing caveat: qwen |
| harness commits | `git show --stat e25ef8a1` | 2 files, 686 insertions |
| raw replies committed | `git show --stat 48e49505` | 9 files, 328 insertions |

**Citation marks.** CONFIRMED: NLRA §8(b)(6); *American Newspaper Publishers Assn.*; *Goldfarb*;
*N.C. State Bd. of Dental Examiners*; *Parker v. Brown*; 17 U.S.C. §102(a); 35 U.S.C.
§100(f)–(g); *Thaler v. Perlmutter*; GDPR Art. 22; EU AI Act Art. 14 and Annex III; the
European Parliament's 16 February 2017 resolution; ABA Formal Opinion 512.
UNVERIFIABLE here: the funder policy, the humanwashing preprint, the AI Liability Directive's
withdrawal, and the state statute's amendments — all asserted by the memorandum, none fetched.

---

## Part VIII — Provenance

This canon is downstream of a document it does not edit. The memorandum stands as written;
the panel's proposed corrections are in `PANEL_RULINGS` §5 and are proposals. Where the canon
states a rule the memorandum states differently — the naming rule (E-1), the species split
(E-2.1), the shape test (E-3), the displacement rule (E-5) and the three gates (E-6) — the
canon is the later instrument and the difference is deliberate.

Nothing in this document has been reviewed by a lawyer. Its citations are marked by
verification state precisely so that a lawyer can see, in one table, which of its load-bearing
authorities were read and which were not.
