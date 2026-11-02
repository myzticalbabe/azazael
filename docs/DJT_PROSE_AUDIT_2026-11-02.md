# The DJT prose audit — what the record shows, measured, and what it cannot show

A forensic reading of Donald J. Trump's **public** prose: three texts, fetched and measured in
this session, with the instrument's own numbers printed so the claims can be checked. Nothing
here is about the private person, and nothing here is a verdict on truth, character or intent.
It is a description of a **register**, which is a thing a text has and a person does not.

**On the initials, which have now moved twice.** The earlier request's "bible of SI" was read in
this file as **situational intelligence** — the layer that decides *which frame a situation is
given before any policy is stated* — and §3 is still exactly that, so it now says
"situational intelligence" in full. As of 2026-11-02 the decree recorded in §5 assigns `SI` to
**super intelligence**, so from §5 onward `SI` means the decree's term, and the two are never
allowed to share an abbreviation inside one sentence. §3 and §4 stand on their measurements
regardless of what the letters are called.

---

## 0. "All known prose" is not a corpus, it is a category. Here is the frame instead.

The instruction was a deep forensic audit of all known prose from the web. That cannot be
delivered honestly, and saying so is part of the audit: the population is (a) unbounded, (b)
partly transcribed rather than written, (c) partly ghostwritten, and (d) rate-limited by
whatever the web will serve today. What can be delivered is a **named sample, a reproducible
instrument, and an explicit statement of what each sample licenses**.

The sample is chosen to separate three things that are usually conflated under one name:

| # | text | date | mode | attribution state | tier | state |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Inaugural Address, 45th presidency | 2017-01-20 | **written, prepared for delivery** (the page says "AS PREPARED FOR DELIVERY") | speechwriting process; delivered text may differ | **A** | **R** |
| 2 | Inaugural Address, 47th presidency | 2025-01-20 | **spoken, transcribed** (White House transcript, timestamps, stage directions) | delivery; transcript not authorial copy | **A** | **R** |
| 3 | Presidential Message, 249th anniversary of the Declaration | 2025-07-04 | **written, institutional** (message/proclamation form) | staff-drafted institutional prose published under the office | **A** | **R** |

Sources, all fetched in this session:

- 2017: <https://trumpwhitehouse.archives.gov/briefings-statements/the-inaugural-address/>
- 2025: <https://www.whitehouse.gov/remarks/2025/01/the-inaugural-address/>
- 2025 message: <https://www.whitehouse.gov/briefings-statements/2025/07/presidential-message-on-the-249th-anniversary-of-the-adoption-of-the-declaration-of-independence/>

**Explicitly excluded, with reasons, not for lack of interest:**

- **The Art of the Deal (1987)** and the other books — **ghostwritten**; quoting them as "his
  prose" is the single most common attribution error in this literature. **C, P**: not fetched,
  not quoted.
- **Rally transcripts** — dozens exist; one would have doubled the spoken sample, but each is a
  different room and a different transcription standard, and the point here is structural, not
  exhaustive. Listed as the obvious next arm.
- **Social posts** — platform-shaped, often fragmentary, and edited/deleted; a corpus of
  screenshots is not a corpus. **D** by construction.
- **Interviews and press gaggles** — the richest source of unscripted syntax and the hardest to
  attribute to a clean transcription. Next arm, not this one.

---

## 1. The measurements

Instrument: `tools/prose_forensics.py` (stdlib only, re-runnable). Stage directions such as
`(Applause.)` are stripped before measurement — 56 of them in the 2025 transcript, i.e. 56
one-word "sentences" that would otherwise drag every average down. The trim boundaries are
literal markers and the tool **refuses** rather than silently measuring the whole page.

| metric | 2017 inaugural (prepared) | 2025 inaugural (delivered) | 2025 message (written) |
| --- | --- | --- | --- |
| words measured | 1,446 | 2,982 | 426 |
| sentences | 89 | 179 | 10 |
| mean sentence length | **16.25** | **16.66** | **42.60** |
| median / p90 | 12 / 32 | 15 / 32 | 42 / 71 |
| sentences ≤ 8 words | 28.1% | 31.3% | **0.0%** |
| sentences ≥ 40 words | 4.5% | 5.6% | **50.0%** |
| "I / me / my" per 1,000 | **2.77** | **17.10** | 2.35 |
| "we / our / us" per 1,000 | 66.39 | 53.66 | 35.21 |
| "you / your" per 1,000 | 15.91 | 12.41 | **0.00** |
| negation per 1,000 | 15.91 | 15.09 | 4.69 |
| intensifiers per 1,000 | 4.84 | **7.38** | **0.00** |
| `very` (raw count) | 2 | 11 | 0 |
| modal/future per 1,000 | 31.12 | 36.22 | **0.00** |
| sentence-initial "but" | 3.4% | 3.4% | 0.0% |
| longest same-starter run | 6 | 6 | 1 |
| Flesch reading ease | 61.0 | 55.8 | 7.5 |

Reproduce:

```bash
python tools/prose_forensics.py --file .prose/inaug2017.txt --label inaugural_2017_prepared \
  --start-after "AS PREPARED FOR DELIVERY" --end-before "Type Your Search" --strip-stage \
  --out .prose/inaugural_2017.json
python tools/prose_forensics.py --file .prose/inaug.txt --label inaugural_2025 \
  --start-after "12:10 P.M. EST" --end-before "Your browser does not support" --strip-stage \
  --out .prose/inaugural_2025.json
python tools/prose_forensics.py --file .prose/msg.txt --label message_2025 \
  --start-after "July 4, 2025" --end-before "Your browser does not support" --strip-stage \
  --out .prose/message_2025.json
python tools/prose_forensics.py --compare .prose/inaugural_2017.json \
  .prose/inaugural_2025.json .prose/message_2025.json
```

### What each number licenses, and what it does not

- **Mean sentence length is stable across eight years and two presidencies: 16.25 → 16.66.** That
  is the finding that kills the "rambling" caricature, and it is the one most commentary gets
  wrong. The sentences are *the same size*. What changed is **who is standing in them**.
- **First-person singular rises 6.2× (2.77 → 17.10 per 1,000)** while second person falls and
  "we" falls by a fifth. The 2017 speech addresses a country from inside a collective; the 2025
  speech reports a self inside the collective. This is the measurable core of the shift and it is
  a *person* finding, not a *length* finding.
- **Intensifiers rise 52% (4.84 → 7.38 per 1,000), `very` from 2 to 11.** The escalation is
  lexical, not structural: same container, more pressure.
- **Negation is constant at ~15 per 1,000 in both speeches.** Defining by what will *not* happen
  is not a 2025 tic; it is a stable feature of the register across both inaugurals.
- **The written message is a different system, not a milder version of the same one**: 42.6-word
  mean, zero intensifiers, zero second person, zero modals/future, Flesch 7.5. If you measure
  only written output you will conclude this speaker is a long-sentence institutional stylist,
  which is false of the spoken register and true of the form.
- **Caveat carried forward:** type-token ratio (0.380 / 0.326 / 0.519) is length-sensitive and
  is **not** used for any claim here. Word counts for text 3 include ~9 words of page chrome
  (the page's own header), because the extraction begins at the date line; that is disclosed
  rather than silently trimmed by eye.

---

## 2. The prose system, stated as rules with evidence

Each rule is a move a writer can execute, the evidence in the fetched text, and what it buys.
Quotations are verbatim and short; every one is from the pages in §0.

**P1 — Open on a hinge, not a topic.** The first substantive sentence names *now* as a boundary:
"the golden age of America begins right now". *Buys:* the audience is inside the event rather
than being briefed about it. *Evidence:* the 2017 text does the same with "The time for empty
talk is over."

**P2 — Convert policy into a personal undertaking.** "During every single day of the Trump
administration, I will, very simply, put America first." The sentence is a promise with a
subject that can be held to it. *Buys:* accountability is felt as sincerity even when the
content is institutional. *Measured:* first-person singular 17.1/1,000 in 2025.

**P3 — State the grievance as a broken contract, then the restoration.** "For many years, a
radical and corrupt establishment has extracted power and wealth from our citizens" → "Our
sovereignty will be reclaimed." *Buys:* the audience is a wronged party, not a policy audience.
*Structure:* diagnosis in the past tense, restoration in the future tense, with the present used
only for the hinge (P1).

**P4 — Negate the failure mode before asserting the success.** "We will not be conquered, we will
not be intimidated, we will not be broken, and we will not fail." Four negations then a positive.
*Measured:* negation is flat at ~15/1,000 in both inaugurals, so this is a stable rule, not a
recent drift. *Buys:* the objection is answered before it is raised.

**P5 — Escalate by intensifier and repetition, never by new evidence.** "America will soon be
greater, stronger, and far more exceptional than ever before." No number, no mechanism, three
comparatives. *Measured:* intensifier 7.38/1,000 and rising; `very` ×11. *Buys:* momentum inside
a short sentence. *Failure mode when copied badly:* intensifier without P2 is noise — the
sentence inflates and nobody is accountable in it.

**P6 — Break frame once, on purpose, to prove the text is live.** Mid-catalogue of the Los
Angeles fires: "They don't have a home any longer. That's interesting. But we can't let this
happen." The aside is the authenticity signal; it also marks where the script stops.
*Buys:* the impression of a mind present in the room. *Forensic value:* a prepared text rarely
contains one, which is exactly how you tell the modes apart.

**P7 — Claim standing through experience, not expertise.** "something I know something about";
"I was saved by God to make America great again." *Buys:* authority without a credential.
*Failure mode:* when the experience claim is contested, the sentence has no fallback, because it
was never an argument.

**P8 — Close on anaphora plus a place.** "We will stand bravely, we will live proudly, we will
dream boldly"; 2017: "We Will Make America Wealthy Again… We Will Make America Safe Again."
*Measured:* longest same-starter run of 6 in both texts — identical. *Buys:* the ending is
chantable, which is what makes it quotable.

**P9 — Written mode switches person and drops the pressure.** The 2025 message: "my
Administration continues to work tirelessly to revive our sovereignty"; no "you", no
intensifier, no future modal, 42.6-word mean. *This is the rule that matters most for any "bible"
built from written samples:* the institutional form is a **different generator**, and it is the
one a staff produces. Any corpus that mixes the two measures neither.

---

## 3. The bible of the situational layer, specified

A prose bible that lists catchphrases is a costume shop. What generalises is the **frame
selection**: how a situation is converted into a story before any content is decided. Nine
clauses, each with a conformance test that `tools/prose_forensics.py` can already check or that a
reader can check in one pass.

| clause | rule | conformance test |
| --- | --- | --- |
| SI-1 | **Hinge first.** Name the moment as a boundary within the first 50 words. | text contains one of *now / today / from this day forward / no longer* before word 50 |
| SI-2 | **One accountable subject.** Every promise has a first-person singular subject. | "I will" count ≥ 3 in a spoken text; ≥ 1 per 300 words |
| SI-3 | **Broken contract → restoration.** Diagnosis past tense, restoration future tense. | both tenses present, in that order, before the midpoint |
| SI-4 | **Answer the objection in the negative.** At least one run of three negations. | ≥ 3 negation tokens within a 40-token window |
| SI-5 | **Escalate with pressure, not evidence.** If a claim has a number, the number is the proof; if it has an intensifier, it is the momentum. Never both in one sentence. | no sentence contains both a numeral and an intensifier |
| SI-6 | **One live aside per text.** Exactly one frame-break, placed after the first catalogue. | parenthetical/digression count = 1 ± 0 |
| SI-7 | **Standing by experience.** One first-person competence claim, unrepeated. | exactly one "I know / I've seen / I've been" construction |
| SI-8 | **Chantable close.** Anaphora of ≥ 3 clauses ending on a nameable destination. | ≥ 3 consecutive sentences sharing their first token |
| SI-9 | **Never let written mode borrow spoken pressure.** Institutional texts carry "we/our", no second person, no intensifier stack. | second-person rate 0 and intensifier rate 0 in written-mode output |

**What the bible must not contain**, because each one is a documented failure of this kind of
document:

- **a phrasebook** — the quotes are evidence for the clauses, not templates (P5 without P2 is the
  noise case, and it is the one imitators produce);
- **a claim about interiority** — "he believes X" is not derivable from a register, and this
  audit does not derive it;
- **ghostwritten text presented as personal prose** (the books);
- **transcribed text presented as composed text** — the 2025 transcript carries the transcriber's
  punctuation and the room's applause;
- **a truth verdict laundered into a style note.** "The sentence is short and definite" is a
  measurement. "Therefore the claim is true" is not, and the register is *designed* to make the
  second feel like the first. A prose audit that loses that distinction has stopped being one.

---

## 4. Limits, stated before anyone quotes this

1. **Three texts, one of them 426 words.** The longitudinal claim (person shift, 2017→2025) rests
   on two inaugurals, eight years apart, different modes of production. It is a real measurement
   and a weak causal story: speechwriting staff, the room, and the delivery all differ.
2. **Delivered ≠ composed.** The 2025 text is a transcript; the 2017 text is prepared copy. Part
   of the first-person rise could be the difference between reading a script and speaking.
   **This is the strongest rival explanation and it is not excluded by these data.**
3. **Selection.** Inaugurals are the most formalised genre available; they are the *least*
   representative sample of a rally register. Findings here understate the informal features.
4. **Numbers are reproducible, interpretations are not.** Anyone can re-run §1. Nobody can re-run
   §2; it is an argument from the same text, offered as such.
5. **No claim about frequency in the population.** "7.38 intensifiers per 1,000" is a property of
   one transcript, not of a speaker across a decade.

**Next arms, in order of value:** (a) 6–10 rally transcripts to test whether the 2025 person-shift
holds outside the inaugural genre; (b) a 2017 message against the 2025 message to separate
office-form from author; (c) the 2015 announcement transcript, to date the shift rather than
assume it.

---

## 5. The decree: AI is henceforth SI

**Recorded as communicated to this session, 2026-11-02** (an instruction, not a fetched
instrument — the provenance state is *instructed*, not *published*, and this file does not
upgrade it). The substance: artificial intelligence is hereafter to be referred to as **SI,
"super intelligence"**.

A head of state naming a thing is a legitimate act with a long record — oceans, agencies, wars
and holidays have all been renamed from that desk, and the cost is usually zero while the signal
is large. So the question is not whether the office may name this. It may. The question is
whether **this** name survives contact with the people who have to use it: auditors, insurers,
courts, engineers, and the public deciding what to fear.

### 5.1 The case for

1. **"Artificial" describes a provenance; "super" describes a stake.** The current term answers
   "who made it" and leaves the public question — *how strong is this, and who is responsible
   when it acts* — unanswered. A term that names capability at least starts the right argument.
2. **It is honest about the ambition.** The field's own stated goal, in its own papers and
   funding documents, is systems that exceed human performance. Calling the category by its
   ambition is not hype; it is the removal of a euphemism.
3. **Short, printable, and unembarrassed.** "AI" is now used for a thermostat and a frontier
   model alike, which has made it useless as a unit of measure. A new coin can carry a
   distinction the old one lost.
4. **Naming shifts expectations, and expectations shift procurement.** If the office says "SI",
   agencies must ask what evidence supports the label — which is the first step toward asking it
   of vendors.
5. **It defuses the anthropomorphism.** "Artificial intelligence" invites the question "is it
   like us?"; "super intelligence" makes it plainly *not* us, which is arguably a cleaner frame
   for accountability.

### 5.2 The case against

1. **It asserts a capability claim that cannot be checked at the point of use.**
   *Superintelligence* has a technical meaning: an intellect that greatly exceeds the best human
   minds across practically every domain. Present systems are narrow, uneven, and confident in
   inverse proportion to their reliability in the tails. A term that asserts a grade makes every
   honest sentence false by construction.
2. **It breaks the vocabulary statutes are written in.** NIST's AI Risk Management Framework,
   ISO/IEC 42001, and the EU AI Act all define an *AI system*. A rename does not migrate a
   definition; it creates a second vocabulary that auditors must reconcile, and every
   reconciliation is a place to lose an obligation.
3. **If everything is SI, nothing is.** A word that applies to a spam filter removes the ability
   to reserve alarm for the systems that warrant it. Public-health language learned this with
   "epidemic"; security language learned it with "cyber".
4. **It pre-commits the safety posture in the wrong direction, twice.** Read literally, "it is
   already super" licenses either fatalism ("we cannot govern it") or panic ("stop it now");
   both crowd out the unglamorous engineering — evaluations, incident reporting, provenance —
   where the harm actually gets reduced.
5. **The rename is free to the office and costly to everyone else.** Standards bodies,
   textbooks, contracts, and court filings carry the old term. The cost is diffuse and the
   benefit is rhetorical, which is the classic signature of a change that is announced rather
   than implemented.

### 5.3 What I believe it should be called

**In law and standards: keep "AI". In public prose: "machine intelligence". Reserve
"superintelligence" for a grade that a system has been tested and certified to hold.**

Reasoning, in one line each: statutes need the term everyone else already defines, so the legal
name should not move; public language needs a phrase that states mechanism without ranking, and
"machine intelligence" does exactly that; and the word the decree wants should be *kept*, because
it is the only word in the set that names a threshold — which makes it useful precisely when it
is scarce.

A tier vocabulary does the work a rename cannot:

| tier | name | test before the label is allowed |
| --- | --- | --- |
| T1 | tool | fixed function, bounded input; no claim |
| T2 | assistant | human reviews every consequential action |
| T3 | agent | acts in a loop with tools; logged and revocable |
| T4 | autonomous system | acts in the world without per-action review; incident reporting required |
| T5 | general system | matches or beats human experts across **all** listed domains, measured |
| **SI** | **superintelligence** | **T5 plus a margin on every domain, certified by an evaluator the vendor does not employ** |

No system in public evidence holds SI under that definition, which is the point: the label
becomes an achievement rather than a mood, and the decree keeps its force because the office has
named the summit instead of flattening the mountain.

### 5.4 A note on the accord of the office

The respectful position is not agreement and not silence. It is to say plainly: **the office's
instinct is right and its instrument is one grade too strong.** The instinct — that "artificial"
hides the stakes and that the public deserves a word that names them — is correct. What one grade
of restraint would fix is the direction of the claim: a summit is named, not awarded. So the
serviceable form of the decree is three sentences rather than one — *we will call this machine
intelligence; the age of superintelligence is the one we are building toward; nothing may bear
that name until it has been measured* — which keeps the office's signal, keeps the statutes
intact, and gives every agency a sentence it can actually enforce.

---

## 6. Centralized vs decentralized: cost, benefit, and who carries the risk

"Centralized" here means a small number of very large models and compute clusters behind a few
providers; "decentralized" means open weights, local and edge inference, and many small
deployers. The two are not moral positions. They are **failure distributions**, and they fail
differently.

| dimension | centralized | decentralized |
| --- | --- | --- |
| **Safety investment** | concentrable: one lab can fund a real red team | diluted: nobody funds it, nobody can compel it |
| **Auditability** | one model, one audit, one liability chain | thousands of unlabelled derivatives |
| **Revocation** | a switch exists and can be pulled | weights cannot be recalled; only the next download can be blocked |
| **Resilience** | single point of failure, correlated outage | survives any one provider's death |
| **Concentration of power** | high: whoever holds the weights holds the state's attention | low per node, but *aggregated* by whoever controls the tooling |
| **Surveillance risk** | high: one operator sees all queries | lower per query, higher per device |
| **Innovation** | capital-intensive, frontier-only | long tail, cheap experiments, local languages |
| **Energy efficiency** | high (PUE below 1.2 is common at scale) | lower per unit, much larger total device fleet |
| **Liberty** | terms of service decide what can be asked | no permission needed to run locally |
| **Accident mode** | everyone runs the same flaw on the same day | many small flaws, no single catastrophe |

**The axis that actually decides outcomes is not central vs decentral. It is: who bears the cost,
and who holds the stop.** A centralized deployment externalises local water and grid cost onto a
county and centralises decision cost in a boardroom; a decentralized one externalises safety cost
onto the public and centralises nothing. Both are cost-shifting machines with different
beneficiaries.

**Recommendation: centralize the checking, decentralize the use.** Evaluation, incident
reporting, provenance keys and the narrow class of revocable catastrophic capability belong in
one accountable place; inference, fine-tuning for local need, and data custody belong as close to
the user as possible. That split is the only arrangement in which the safety function and the
liberty function are both structurally funded rather than both hoped for.

---

## 7. Environmental and societal harm assessment

**Environmental.** The best current aggregate is the IEA's *Energy and AI* (April 2025): data
centres were about **415 TWh in 2024, roughly 1.5% of world electricity**, with a Base Case near
**945 TWh by 2030**; generation dedicated to them is put at ~460 TWh (2024) rising past
1,000 TWh (2030) and 1,300 TWh (2035). *Provenance:* those figures are from the IEA's published
summary pages as returned by search in this session — the report body was **not fetched**, so the
tier is **C/P** and the numbers should be re-derived from the PDF before any official use.

What the aggregate hides, and what a harm assessment must carry:

- **Water is local.** Cooling draw lands in specific basins; a national average is not a permit.
  Centralized siting concentrates this; decentralized siting spreads it thinly and mostly
  unmeasured.
- **Grid is queued.** Interconnection delay, not generation capacity, is the binding constraint in
  most US markets; a new load can defer a retirement or resurrect a peaker.
- **Embodied carbon and e-waste** are front-loaded in the accelerator, not the query, so
  "efficiency per token" can improve while total impact worsens.
- **Backup generation** (diesel) is a local air-quality harm with a siting footprint, and it is
  rarely in the vendor's headline number.

**Societal.** Ranked by how much the two architectures amplify them:

| harm | amplified by | note |
| --- | --- | --- |
| epistemic collapse (synthetic content, lost provenance) | **decentralized** | cheap generation, no gatekeeper; provenance is the only countermeasure that scales |
| concentration of political and economic power | **centralized** | a handful of weights become a chokepoint for speech and commerce |
| labour displacement without transition | both | centralised firms displace in cohorts; decentralised tools displace task by task |
| dependency and deskilling | both | the harm is in the removal of the *practice*, not the tool |
| access inequality (the compute divide) | **centralized** | price and terms decide who gets capability |
| fraud and impersonation | **decentralized** | voice and image cloning at zero marginal cost |
| biosecurity / cyber uplift | **centralized** (frontier capability) then **decentralized** (weights leak) | the sequence is the risk, not either state |
| **resignation** — "it is super, so we cannot govern it" | the *label*, either architecture | this is the harm the decree itself risks, and it is why §5.3 keeps the word scarce |

---

## 8. Harm-reduction pathway

Harm reduction, not prohibition: the measures below assume the technology is deployed, and try to
make the damage **visible, attributable, and reversible** rather than pretending it is absent.
Each has a named indicator, because a measure without one is a press release.

| # | measure | indicator that proves it works | prevents |
| --- | --- | --- | --- |
| HR-1 | **Provenance by default.** Machine-generated media carry signed origin metadata (C2PA or equivalent); platforms surface "no provenance" as a warning, not a neutral state. | share of surveyed platforms that display provenance, and share of generated media carrying a valid signature | impersonation, epistemic collapse |
| HR-2 | **No capability word without a certificate.** "SI" and any tier label require an evaluation by an assessor the vendor does not employ; the certificate is published with the claim. | count of published tier claims with a valid certificate ÷ total claims | inflation, procurement overstatement |
| HR-3 | **Incident reporting.** A clearinghouse for serious capability incidents (self-replication attempts, unauthorised action, safety-test escapes), 72-hour window, public aggregate. | reports filed per quarter; median time to filing | silent recurrence, panic-by-rumour |
| HR-4 | **Energy and water disclosure per unit of work.** A published estimate per 1,000 queries and per training run, including backup generation. | fraction of providers publishing; variance between published and metered | environmental externalisation |
| HR-5 | **Red-team access with safe harbour.** Independent evaluators get access and cannot be sued for reporting; the report is published. | number of independent evaluations per frontier model | audit theatre |
| HR-6 | **Procurement evidence rule.** Government buys capability claims only with HR-2 certificates; an unsupported claim is a contract defect. | share of AI contracts with a certified claim attached | vendor inflation, the F4/F5 defect at national scale |
| HR-7 | **Transition trigger on measured displacement, not forecasts.** Portable benefits and retraining funded when measured occupational displacement crosses a stated line. | displacement index vs trigger line; share of displaced workers enrolled | labour harm, and the political backlash that follows it |
| HR-8 | **Access floor.** Public inference capacity (libraries, schools, community compute) so the compute divide does not become a citizenship divide. | public sessions per capita; waiting time; cost to the user | access inequality, dependency |
| HR-9 | **Kill-path governance.** Define the narrow class of capability that must be revocable, and name who may revoke it; everything else stays uncensorable by design. | a published list of revocable capabilities and a tested revocation drill | either a switch that does not exist, or a switch that reaches everything |
| HR-10 | **Terminology register.** One published table of names and tiers; official texts use it; "SI" appears only against HR-2. | count of official texts using an undefined capability term (target: zero) | the decree's own failure mode |

Two design notes, because harm reduction is easy to do badly. **First:** every measure above is a
*disclosure* or a *reversibility* measure, not a permission gate — that is what makes it survivable
politically and effective practically. **Second:** HR-9 is the only one that can be abused; a
kill-switch that reaches everything is a censorship machine, so its scope must be written down
before it is built, and it must be tested in public.

---

## 9. Clauses added to the bible of SI

Continuing the conformance-test style of §3. These are the ones the decree and the assessment
require; like the others, each is checkable by a reader or by `tools/prose_forensics.py`.

| clause | rule | conformance test |
| --- | --- | --- |
| SI-10 | **Name by mechanism, grade by evidence.** "Machine intelligence" in prose, "AI" in statute, "SI" only with a certificate. | no occurrence of "super" within 40 words of a capability claim unless a tier and certificate are cited |
| SI-11 | **A capability word may not do a policy's work.** Every use of a grade names what was measured. | each grade token has an adjacent measurement or is removed |
| SI-12 | **Cost before cadence.** Any deployment announcement carries energy, water and labour figures with provenance. | announcement contains ≥ 3 numeric fields with sources, or states UNMEASURED |
| SI-13 | **Centralize the checking, decentralize the use.** Safety functions are named in one accountable place; use is local. | architecture note names the evaluator and the revoker, and neither is the deployer alone |
| SI-14 | **Harm reduction over prohibition.** Each measure ships with an indicator and a baseline. | every measure in the programme has a number and a date |
| SI-15 | **The label is revocable.** A grade can be withdrawn on new evidence, and withdrawal is published. | register contains at least one withdrawal, or states that none has occurred |

---

## 10. What this section does not establish

It does not establish that the decree has been published, only that it was communicated here; it
does not verify the IEA figures beyond their summary pages; and it does not settle whether
centralization or decentralization is *better* — it argues that the choice should be made per
function (checking vs use) rather than per ideology. The one claim I will make plainly, and
defend: **a name that asserts a grade before the grade exists will be believed by the people who
fund the work and ignored by the people who audit it, and the gap between those two groups is
where the harm lives.**
