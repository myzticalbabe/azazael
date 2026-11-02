# The DJT prose audit — what the record shows, measured, and what it cannot show

A forensic reading of Donald J. Trump's **public** prose: three texts, fetched and measured in
this session, with the instrument's own numbers printed so the claims can be checked. Nothing
here is about the private person, and nothing here is a verdict on truth, character or intent.
It is a description of a **register**, which is a thing a text has and a person does not.

`SI` is read here as **situational intelligence**: the layer that decides *which frame a
situation is given before any policy is stated*. If the estate means something else by the
initials, only the subtitle changes — §3 and §4 stand on the measurements.

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

## 3. The bible of SI — the situational layer, specified

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
