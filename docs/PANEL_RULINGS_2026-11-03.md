# Panel rulings — *When the Machine Does the Work*

**Date:** 2026-11-03
**Subject document:** `docs/MEMORANDUM_WHEN_THE_MACHINE_DOES_THE_WORK_2026-11-03.md` (463 lines, 29,850 chars as sent)
**Brief under which this ran:** `docs/REVIEW_BRIEF_KILO_LEGAL_PANEL_2026-11-03.md` §5 (six questions, ≥5 providers, distinct angles, dissent preserved) and §6 (memo not edited; corrections proposed, citation marks applied)
**Harness:** `tools/legal_panel.py`
**Raw evidence:** `logs/legal_panel/2026-11-03/` (this pass) and `logs/legal_panel/` (first pass, same day)

> **This is not legal advice and is not an opinion of counsel.** It is the recorded output of
> five language-model seats asked six questions, plus the adjudication of where they split.
> No seat is a lawyer, none was given another seat's answer, and no authority any seat named
> has been read for this document. A model can produce a citation that looks exact and does
> not exist; the citation table below therefore marks every authority by its verification
> state, and most of the 2026-era sources are marked **UNVERIFIABLE**.

---

## 1. What actually ran

### 1.1 Seats that answered

| seat | provider / host | model | angle assigned before seeing the memo | time | raw |
| --- | --- | --- | --- | --- | --- |
| `gemini` | Google (direct API) | `gemini-3.1-flash-lite` | labour and employment law | 3.8 s | 3,447 ch |
| `cohere` | Cohere (direct API) | `command-r-plus-08-2024` | intellectual property | 102.3 s | 2,548 ch |
| `qwen` | OpenRouter (Alibaba model) | `qwen/qwen3-32b` | antitrust | 36.1 s | 1,783 ch |
| `openrouter` | OpenRouter (Meta model) | `meta-llama/llama-3.3-70b-instruct` | adversarial: break the memo | 18.1 s | 1,009 ch |
| `deepseek` | OpenRouter (DeepSeek model) | `deepseek/deepseek-v3.2` | professional regulation and licensing | 22.9 s, *first pass* | 2,662 ch |

Five distinct model labs, five distinct angles, no seat shown another's output. The brief's
count is met on labs, **not** on hosting: only three hosts are represented (Google, Cohere,
OpenRouter). That distinction matters and is not hidden — three of the five seats share one
account and therefore one rate-limit and one balance.

### 1.2 Seats that did not answer, and the measured reason

Recorded rather than dropped: a panel of five reported as eight is a false reading.

| seat | model | failure | verbatim |
| --- | --- | --- | --- |
| `opus` | `anthropic/claude-opus-5.5` | credit wall | `HTTP 402 ... You requested up to 2200 tokens, but can only afford 327` |
| `deepseek` (second pass) | `deepseek/deepseek-v3.2` | balance drained by the first pass | `HTTP 402: This request would exceed your available balance` |
| `groq` | `openai/gpt-oss-120b` | free-tier token-per-minute cap below the memo size | `HTTP 413: Request too large for model openai/gpt-oss-120b` |
| `mistral` | `mistral-small-latest` | free-tier rate limit, twice, 12 s apart | `HTTP 429 ... code 1300` |
| `cerebras` | `gpt-oss-120b` | payment required | `HTTP 402: Payment required to access this resource` |
| `zhipu` | `glm-4.5` | no resource package | `HTTP 429 code 1113: Insufficient balance or no resource package` |
| `nim` | `meta/llama-3.3-70b-instruct` | model retired; every live alternative 404s for this account | `HTTP 410: The model 'meta/llama...` / `404 Function ... not found for account` |
| `github` | `gpt-4o-mini` | endpoint unresolvable | `URLError: [Errno 11001] getaddrinfo failed` |

The zero-shot Opus seat the panel was asked to include **could not be bought for this
prompt**: the account could afford 327 completion tokens, which is one verdict short of
six. It is recorded as unavailable, not approximated by a cheaper model under an Opus label.

### 1.3 Two seats that answered but should be weighted low

- `openrouter` (Meta llama) returned the schema with **one-word verdicts** ("Misleading",
  "No", "Academic"). It is a real vote on direction and worthless on reasoning.
- `qwen` returned malformed JSON (unescaped quotes inside `authority`) and its prose is
  partly garbled ("without without", a Goldfarb citation attached to a featherbedding
  question). Its JSON was recovered by reading the raw reply; the recovered verdicts are
  quoted below with that defect stated.

---

## 2. The six rulings

Each ruling states the panel's disposition, the basis for it, and where a seat dissented —
verbatim, because the brief forbids synthesising dissent away.

### R1 — `featherbedding` is the wrong word, and affirmatively misleading

**RULING: SUSTAINED — the memo's short answer should be struck.** All five seats rejected
the term. The reason is not tone: NLRA §8(b)(6) as narrowed by *American Newspaper
Publishers Assn. v. NLRB*, 345 U.S. 100 (1953) reaches a **union-exacted** payment for
services not performed. A state board's rule is not an exaction by a labour organisation,
so the statutory term imports two elements the memo's subject does not have — a union and
an illegal demand. Using it as the governing analogy is the memo's weakest single move.

The seats split on the replacement:

- `gemini`: **"regulatory credentialism"** or "occupational gatekeeping" — captures
  state-sanctioned exclusion of non-human labour.
- `deepseek`: **"regulatory rent-seeking"**, or the memo's own **"human of record"**.
- `cohere`: no replacement offered; holds only that the term implies a union exaction.
- `qwen` (low-reliability): proposed "Goldfarb's 'learned professions' framework", which is
  a category error of its own — *Goldfarb* is an antitrust case about fee schedules.

**Dissent (verbatim, `gemini`):** "I dissent from the characterization of all human-oversight
rules as 'featherbedding-shaped.' Many are legitimate responses to the 'black box' problem
where the law requires a human to bridge the accountability gap, not to preserve a job."

**Consequence for the memo:** the falsifier this panel was asked to test (§ below) fires on
the broad form of the claim. The defensible form keeps the *shape* (a human is installed
where a machine did the work) and drops the statutory term.

### R2 — The five mechanisms are not one mechanism; the fifth is a different species

**RULING: QUALIFIED — convergence is functional, not legal, and the memo's own §1.5 already
concedes the exception it then does not carry into the thesis.** Four seats said the
mechanisms are legally distinct while functionally converging on a human-of-record
requirement.

The sharpest distinction came from `deepseek`, and it is structural rather than doctrinal:
**the first four install a human to protect a third party's rights; the fifth installs a
human to protect the funder's own evaluation capacity.** That is not a difference of degree.
A funder screening for originality is protecting its own programme, not a client, a
patent's public bargain, or a data subject.

`gemini` supplied the doctrinal reason the two IP rules are not twins even though they
converge: authorship rests on judicial construction of "originality", inventorship on a
rigid statutory definition of "individual" in 35 U.S.C. §100(f) — so the latter is more
resistant to interpretive expansion and the former more exposed to it.

**Dissent (verbatim, `deepseek`):** "The memo understates that professional-responsibility
rules (like ABA Opinion 512) exist primarily for client protection, not guild rent-seeking."

**Consequence:** the thesis survives as "five regimes converge on a human-of-record
requirement", not as "five regimes are one rule". The funder case belongs in the thesis as
the exception that defines the boundary, not only in a subsection.

### R3 — The substitution axis survives, but only as a sufficient-shape claim, not a necessary one

**RULING: PARTIALLY SUSTAINED.** The axis describes the rules the memo is about; it does not
describe all human-oversight rules. Every seat produced a regime that bites a
non-substituting use, and they are not the same regime:

- `gemini`: **medical-device AI** oversight, required even where the machine performs what
  no human could (real-time genomic analysis) — risk mitigation, not job protection.
- `cohere` and `gemini`: **EU AI Act Art. 14**, human oversight for high-risk systems by
  risk classification, irrespective of whose work was displaced.
- `deepseek`: **NLnet's ban on all AI-generated artefacts** — a content/generation
  prohibition, not a substitution-triggered rule.
- `qwen` (low-reliability): the Act's watermarking deferral to 2027, cited as risk-driven.

`deepseek` puts the surviving form best: the axis "survives but is imperfect". `gemini`
declares it fragile and names the Act's risk-based classification as the kill shot; that
overstates, because a risk-based rule and a substitution-shaped rule can both be real and
the memo's claim is about the second class.

**Dissent (verbatim, `gemini`):** the axis "fails against 'safety-critical' disclosure
mandates."

**Consequence:** reword the axis as *"the rules that install a human of record are
substitution-shaped"* and add the boundary: risk-based oversight regimes exist that do not
depend on displacement, and they are the strongest counter-example the memo must answer.

### R4 — The antitrust lever is live in doctrine and unproven in fact; treat it as a theory with a standing problem

**RULING: SPLIT, AND THE SPLIT IS THE FINDING.** Two seats call the lever live, one calls it
academic, one calls it live but flags standing, and one returns "live" without reasons.
No seat produced a case in which *Goldfarb* or *Dental Examiners* reached a **state board's
AI-substitution rule**, and no seat addressed the three gates separately:

1. **Parker immunity** — a board exercising state-delegated police power is immune; the
   memo must show the rule is the board's own, not the legislature's.
2. **Active supervision** — *Dental Examiners* strips immunity from a market-participant
   board absent active state supervision. `deepseek` names this as "the key defense".
3. **Antitrust injury and standing** — a plaintiff not yet in the market (an AI vendor, or a
   client who would have bought machine work) must show injury of the type the antitrust
   laws were intended to prevent. `qwen`, despite its garbled answer, is the only seat that
   raised this: "standing for non-market plaintiffs is unproven."

**Verbatim dissent (`gemini`, for academic):** "State boards acting under clear legislative
mandates for 'public safety' enjoy Parker immunity; proving that a board is merely
protecting incumbents rather than exercising state-delegated police power is a near-
impossible evidentiary burden."

**Verbatim dissent (`cohere`, for live):** "I disagree with the memo's assertion that the
antitrust lever is purely academic. Goldfarb and Dental Examiners provide a strong basis for
challenging professional bodies' rules that suppress machine performance."

**Consequence:** keep the lever, downgrade its tense. It is not "live"; it is "available and
unlitigated", with immunity, supervision and standing as three independent ways to lose.

### R5 — The humanwashing / Art. 22 reading is right in mechanism and overstated in effect

**RULING: QUALIFIED — "extinguish" is too strong; "displace" is accurate.** Four seats accept
the mechanism: Art. 22 governs decisions based *solely* on automated processing, so inserting
a human removes the trigger and with it the data subject's Art. 22 safeguards. `deepseek`
states it cleanly: the human "function[s] as a waiver of procedural protections."

What the panel splits on is whether that extinguishes recourse. `gemini` argues the opposite
direction: the inserted human acquires **non-delegable duties of supervision**, so the
requirement "increase[s], rather than extinguish[es], the human's legal exposure." Both can
be true at once — the data subject loses the Art. 22 route and gains a human defendant — and
the memo currently records only the loss.

On the withdrawn AI Liability Directive, the panel is unanimous in substance and the memo
should follow it: a withdrawn instrument can prove that a regime was proposed and abandoned.
It cannot prove what liability rule would have applied, and it cannot be cited as authority
for the waiver reading. `deepseek` names this as the memo's killable claim.

**Dissent (verbatim, `deepseek`):** "The claim that 'the human-of-record requirement can
extinguish the rights of the person it is said to protect' relies on a tier-C preprint
(humanwashing) and a withdrawn directive; a court may reject it as speculative."

**Consequence:** split the sentence in two — the trigger is displaced (defensible on the
text of Art. 22), the rights are extinguished (needs the tier-C preprint and a liability
theory the memo does not yet have).

### R6 — The honesty section is incomplete in both directions, and the panel found the gaps

**RULING: NOT COMPLETE.** The memo records relaxations (EU, Colorado) and the federal
preemption push. The seats name three omissions, all in the same direction — **drivers other
than substitution that the memo does not concede** — and one omission in the other
direction:

1. **Tort / non-delegable duty as an independent driver.** `gemini`: oversight is required
   "not as a rent-seeking device, but as a necessary condition for liability to attach to a
   legal person." If that is right, some human-of-record rules are accountability
   infrastructure, and the memo's rent-seeking frame mislabels them.
2. **The corporate-personhood analogy's limits.** `cohere`: the EU's rejection of electronic
   personhood is "a choice, not a necessity."
3. **The funder species split** (see R2) — stated in §1.5, absent from the thesis.
4. **Other direction — the memo understates its own case on professional regulation.**
   `deepseek` dissent: client-protection rules exist and are not guild rent-seeking.

---

## 3. Falsifier 1 — the `featherbedding` claim, tested

The question was whether the memo's broad form ("courts only regulate drafting") survives,
and whether the narrow form does.

| form | test | result |
| --- | --- | --- |
| broad: oversight rules are featherbedding-shaped, full stop | 5 seats, no shared context | **FALSIFIED** — 5/5 reject the term; 3/5 also reject the characterisation of oversight rules as rent-seeking |
| narrow: identity/authorship-substitution rules install a human where a machine did the work | same seats, Q2/Q3 | **SURVIVES** — the shape is conceded even by the seats that reject the word |

Evidence grade: the seats are tier-C reasoning sources, not authorities. The primary order
text that would settle R1 — the narrowing in *American Newspaper Publishers* — is a 1953
reporter volume, not re-read for this document; the narrowing proposition is standard, the
application to a state board is the memo's own step and is not supported by any authority the
panel produced.

---

## 4. Citation table, by verification state

`CONFIRMED` = the citation exists and the proposition stated is standard; not re-fetched today.
`QUALIFIED` = the citation exists but the memo's use of it is narrower or wider than the source.
`MISSTATED` = the memo attributes something the authority does not say.
`UNVERIFIABLE` = could not be checked here; treat as the memo's assertion, not as law.

| authority | mark | note |
| --- | --- | --- |
| NLRA §8(b)(6) | CONFIRMED | the text requires a union-exacted payment for services not performed |
| *American Newspaper Publishers Assn. v. NLRB*, 345 U.S. 100 (1953) | CONFIRMED | narrows §8(b)(6) to exactions; its application to a state board is the memo's step, not the Court's |
| *Goldfarb v. Virginia State Bar*, 421 U.S. 773 (1975) | QUALIFIED | learned professions are not exempt from Sherman Act §1; it does not hold that a state board's AI rule is unlawful |
| *N.C. State Bd. of Dental Examiners v. FTC*, 574 U.S. 494 (2015) | CONFIRMED | market-participant board needs active supervision for Parker immunity |
| *Parker v. Brown*, 317 U.S. 341 (1943) | CONFIRMED | state-action immunity |
| 17 U.S.C. §102(a) | CONFIRMED | originality; authorship of works |
| 35 U.S.C. §100(f)–(g) | CONFIRMED | "individual"/"joint inventor" as natural person |
| *Thaler v. Perlmutter* | CONFIRMED | no inventorship for a machine; D.C. Circuit affirmed |
| GDPR Art. 22 | CONFIRMED | solely-automated decisions; the "solely" trigger is the load-bearing word |
| EU AI Act Art. 14 (and Annex III) | CONFIRMED | human oversight for high-risk systems, by risk class |
| EU Parliament resolution, 16 Feb 2017 (civil-law rules on robotics) | CONFIRMED | rejected electronic personhood |
| ABA Formal Opinion 512 (2024) | CONFIRMED | generative-AI competence/confidentiality duties to clients |
| Wilson et al., "humanwashing" preprint (cited by memo as arXiv 2605.13723) | UNVERIFIABLE | not fetched; the memo's Q5 depends on it |
| NOT-OD-25-132 (NIH funder originality) | UNVERIFIABLE | not fetched |
| NLnet GenAI policy v2.0 | UNVERIFIABLE | not fetched; two seats rely on it as the counter-example |
| withdrawal of the AI Liability Directive | UNVERIFIABLE | asserted by the memo; not checked today |
| Colorado AI Act relaxations | UNVERIFIABLE | asserted by the memo |
| Restatement (Second) of Torts §424 / (Third) of Agency (seat-supplied) | UNVERIFIABLE | produced by `gemini`, not checked; §424's subject is statutory/regulatory precautions, so the non-delegable-duty use needs its own cite |

---

## 5. Proposed corrections to the memo — proposed, not applied

The brief §6 forbids editing the memorandum inside the panel document. These are proposals
for the memo's own next revision.

1. **§0/short answer:** replace "featherbedding" with **"human of record"** as the governing
   term, and mention featherbedding once as the *rejected* analogy with the §8(b)(6)
   narrowing stated. (R1)
2. **§2 (nexus):** add the boundary sentence the panel demanded — risk-based oversight
   regimes (EU AI Act Art. 14, medical-device rules) require a human without any
   substitution, so the axis is substitution-*shaped*, not substitution-*triggered*. (R3)
3. **§1.5 → thesis:** move the funder species split out of the subsection and into the
   thesis, as the exception that defines the boundary: the first four protect a third
   party's rights, the fifth protects the funder's own screen. (R2)
4. **§5 (antitrust):** change "live" to "available and unlitigated"; add the three gates —
   Parker immunity, active supervision, antitrust injury/standing for a non-market
   plaintiff — each as an independent way to lose. (R4)
5. **§6 (humanwashing):** split the sentence. "Art. 22's trigger is displaced by inserting a
   human" is defensible on the text; "the rights are extinguished" needs the tier-C preprint
   and a liability theory, and the withdrawn directive proves only that a regime was
   proposed and abandoned. (R5)
6. **§7 (honesty):** add tort non-delegable duty as an independent driver, the limits of the
   corporate-personhood analogy, and — in the other direction — that professional-conduct
   rules also serve clients, not only the guild. (R6)
7. **Every 2026-era source in §4 above marked UNVERIFIABLE** should carry its mark in the
   memo itself until fetched, so a reader cannot mistake an unretrieved instrument for
   authority.

---

## 6. What this panel does not establish

- It does not establish that any of these rulings is correct law. Five models agreeing is
  five models agreeing; it is not a court.
- It does not establish provider independence for three of the five seats, which share one
  account and one balance.
- It does not test the memo's factual claims about 2026 instruments, none of which were
  fetched.
- It does not include the Opus seat, which the account could not afford (327 tokens against
  a ~2,200-token answer).

## 7. Reproduce

```bash
python tools/legal_panel.py --dry-run     # endpoints, models, key presence, prompt sizes
python tools/legal_panel.py               # all seats; writes logs/legal_panel/<date>/<seat>.json
python tools/legal_panel.py --seats gemini,cohere
```

Exit 0 only when every configured seat answered and parsed. Today's run exits **1**, and
that is the honest reading: five of eight seats answered, four of those in this pass.
