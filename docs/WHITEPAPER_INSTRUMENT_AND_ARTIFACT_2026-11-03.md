# Instrument and Artifact — what NIH's AI rule reaches, and what it does not

**Status:** evidentiary paper. Argument is confined to the primary text of
NOT-OD-25-132 plus what was read for it; everything weaker is tiered in Appendix A.
**Origin:** a declaration by the user on 2026-11-03 — "i do not believe that a
stand-alone executable is per se AI as defined-by-law" — made against an earlier
report of mine that had treated a model-embedding binary as caught by the rule.
That report was wrong on this point and this paper is the correction, argued rather
than asserted.
**Not legal advice.** No statute, regulation or case law was searched. See §7.

---

## 0. The question

A grant tool ships as a single self-contained executable. It embeds a model, runs on
the applicant's own machine, and emits text that becomes part of a research
application. NIH has rules about applications developed by AI. Does the executable
fall under them?

The answer this paper argues: **the rule does not classify instruments at all. It
classifies artifacts.** Being a binary settles nothing. Being a binary that
originated the substance of a submitted section settles a great deal.

That is a narrower answer than "we are exempt" and a wider one than "we are caught",
and the two errors it rules out are the ones actually being made in the field:
*local, therefore safe* and *uses a model, therefore prohibited*. Neither is
supported by the text.

---

## 1. What the primary text says

Source: `grants.nih.gov/grants/guide/notice-files/NOT-OD-25-132.html`,
*Supporting Fairness and Originality in NIH Research Applications*. Released
2025-07-17.

Four provisions matter.

**(a) The artifact test.**

> "NIH will not consider applications that are either substantially developed by AI,
> or contain sections substantially developed by AI, to be original ideas of
> applicants."

The grammatical subject is *applications* and *sections*. Not tools, not vendors, not
architectures. The predicate is *substantially developed by*, a claim about
provenance of content.

**(b) The harm named.**

> "NIH has recently observed instances of Principal Investigators submitting large
> numbers of applications, some of which may have been generated with AI tools …
> there is evidence that the use of AI tools has enabled Principal Investigators to
> submit more than 40 distinct applications in a single application submission
> round."

This is the load-bearing sentence for the instrument/artifact distinction, and it is
usually skipped. The stated harm is **volume and dilution of originality**, not the
existence of software. A rule aimed at volume has no business classifying what a
binary contains; it has every business measuring how many artifacts were produced
and whether they were the applicant's.

**(c) Tools are explicitly contemplated, not banned.**

> "AI tools may be appropriate to assist in application preparation for limited
> aspects or in specific circumstances, but researchers should be aware that using
> AI comes with its own risks."

A regime that banned instruments would not write this sentence.

**(d) Enforcement and consequence.**

> "NIH will continue to employ the latest technology in detection of AI-generated
> content…"
> "If the detection of AI is identified post award, NIH may refer the matter to the
> Office of Research Integrity … while simultaneously taking enforcement actions
> including but not limited to disallowing costs, withholding future awards, wholly
> or in part suspending the grant, and possible termination."

Plus, in the same notice, a volume cap: **six** new, renewal, resubmission or
revision applications per PI/MPI per calendar year, all activity codes except T and
R13. Effective for applications submitted to the **2025-09-25** receipt date and
beyond.

---

## 2. What the text does not say

Five absences, each of which someone has already filled with an assumption.

| Absent | Consequence |
| --- | --- |
| A definition of "AI" | No architectural element can be tested against it. "Not per se AI" is therefore not a defence that can be *won* on the text — it is a question the text leaves open (§3). |
| A threshold for "substantially developed" | Deliberate. No percentage, word count, prompt count or section list. Ambiguity is the enforcement mechanism. |
| Any list of prohibited tools | A local binary, a cloud API, a template engine and a hired editor are all unclassified by name. |
| Any exemption for local execution | Nothing privileges on-device processing. Local is not named as safe. |
| Any immunity for small scale | The cap is per-PI, not per-tool. |

The asymmetry matters: the absences cut **both** ways, and any argument that uses
them only in one direction is advocacy, not reading.

---

## 3. The distinction, stated precisely

Three terms, kept apart on purpose.

- **Instrument** — the executable, weights, runtime, pipeline. What compiled.
- **Artifact** — the application or the specific section submitted. What is judged.
- **Author** — the PI. Who must be able to stand behind the content.

The rule's subject is the artifact. Its predicate is a relation between artifact and
author. The instrument is, at most, evidence about that relation — never the thing
tested.

**Why this is not a technicality.** The notice's own justification is volumetric:
forty applications in one round, review capacity strained, originality diluted. That
harm is a property of *artifacts produced per author*, and it is measurable without
any knowledge of what software was used. Conversely a tool that helps one PI express
one argument better produces no volume harm at all, whatever it links against.

**Where the distinction stops helping.** A local tool can generate in bulk. Nothing
about being on-device limits throughput; `for i in range(40): generate()` runs as
well locally as remotely. So local execution is not immunity and must not be sold as
such. The instrument/artifact split relocates the question to output provenance — it
does not answer it.

**The honest formulation:** *a standalone executable is not, by itself, the condition
the rule names.* Whether a given artifact falls under the rule is decided by that
artifact's provenance, and by nothing about the binary.

---

## 4. The adjudication standard

If the test is provenance, it needs a standard of proof, or it is unadministrable.
NIH declines to supply one (§2). What can be built honestly in that gap:

**Principle of origination.** The instrument may *transform expression*; it may not
*originate substance*. Substance means: aims, rationale, study design, evidence,
interpretation, claims.

Laid out per section, this is decidable:

| Layer of the application | Must originate with | Instrument may |
| --- | --- | --- |
| Specific Aims | PI | reformat, tighten, check consistency |
| Significance / innovation argument | PI | structure, cross-reference the PI's own citations |
| Approach / methods | PI | enforce house style, flag unsupported claims |
| Literature synthesis | PI (selection and judgement) | retrieve, verify that cited works exist, detect retraction |
| Budget, biosketch, formatting, compliance | either | generate freely |
| Disclosure of AI assistance | PI | prompt for it, draft the wording |

Two consequences follow directly.

1. **Fabrication is the sharpest test.** The notice names "fabricated citations" as a
   misconduct risk. Any tool that emits citations it has not verified is producing
   exactly the artifact the rule is worried about, at any level of locality. A tool
   that *verifies* citations is doing compliance work, and is squarely on the right
   side.
2. **Detection is behavioural and unreliable, and saying so is not evasion.** NIH
   enforces by detecting AI-generated content. Detector accuracy is unmeasured here
   (see §7); it is widely reported to be poor on edited text. This cuts against the
   applicant regardless of which instrument was used, which is precisely why the
   applicant's *record of authorship* — inputs, drafts, disclosure — is the only
   durable protection. A tool that keeps that record is worth more than a tool that
   writes faster.

---

## 5. What this buys a local-first architecture, and what it does not

**Not a moat:** "AI-native". A current search returns 15+ AI grant tools and a
catalogue comparing 36 of them. Every entrant claims this; it differentiates nothing.

**A real moat, and the one the plan never stated:** confidential proposal text never
leaves the machine. The surrounding practice has moved toward exactly that constraint
— reviewers are barred from putting application content into generative tools, with
the prohibition framed as confidentiality rather than influence (secondary source,
tier C, §7). For applicants the same pressure produces a simpler requirement: the
proposal is unpublished, competitive and someone else's intellectual property until
award. A tool that needs a cloud round-trip to function asks the PI to upload it.

This is a claim competitors built on hosted APIs structurally cannot copy without
rebuilding. It is also, awkwardly, the *only* claim in the plan that the policy
environment actively supports.

---

## 6. The six-application cap inverts the product

If a PI gets six slots a year across all council rounds, the binding question stops
being *how fast can I produce an application* and becomes *which six*.

That promotes fit and prioritisation — discovery, eligibility, funder-mechanism
matching, honest probability of success — above drafting, and it demotes bulk
generation from feature to liability. It also makes the cap itself a feature surface:
a tool that tracks a PI's six slots is immediately useful to a compliance office.

Worth stating plainly because it inverts the build order in the plan under review:
`drafting` is currently the centre of gravity and `eligibility` is the module that
returns `career_stage=('eligible','senior')` for a senior PI against an ESI-only
criterion.

---

## 7. Where this paper stops

Unresolved, and not to be filled by assertion:

- **No statutory definition was sought.** This paper read one NIH notice. Whether some
  statute, regulation or guidance defines "AI" in a way that binds a research
  application was not investigated. The claim above is an absence of finding, not a
  finding of absence.
- **The NSF contrast is unverified.** A secondary source characterises NSF as moving
  in the opposite direction. Not checked against NSF primary text; not relied on.
- **The May 2026 Extramural Nexus restatement** (reviewer AI prohibition,
  confidentiality framing) comes from that same secondary source and was not read in
  the original.
- **Detector reliability is unmeasured.** No data collected.
- **No case law.** No enforcement action under NOT-OD-25-132 was located or examined,
  so nothing here rests on how NIH has actually applied the rule — only on what it
  says.

**What would falsify §3:** a statute or NIH FAQ defining AI by architecture, or any
NIH statement that local tools are exempt. Either would collapse the distinction into
a bright line, in one direction or the other. Neither was found; the absence is thin
evidence and is labelled as such.

---

## Appendix A — Provenance

| Claim | Source | Tier |
| --- | --- | --- |
| Artifact test, volume rationale, tool tolerance, detection, ORI referral, six-app cap, 2025-09-25 effective date | NOT-OD-25-132 (read in full, 2026-11-03) | A |
| "Legacy" characterisation of Pivot-RP; competitor comparison | `atomgrants.com/blog/pivot-vs-atom-grants` | C — competitor marketing |
| NSF direction, Extramural Nexus restatement, reviewer confidentiality prohibition | `atomgrants.com/blog/nih-and-nsf-ai-policy-…` | C — not verified against primary text |
| 15+ tools / 36-tool catalogue | `proposia.ai/materials/ai-tools`, `grantcopilot.ai/…` | C — vendor catalogues |
| grantforge behaviour (`pass True` unconditional, ESI misclassification, `KeyError: 'execute'`) | re-run probes under `C:/Azazael/.venvs/py315t` with `PYTHONPATH=src`, 2026-11-03 | A — executed |

## Appendix B — What the code does, as measured

Recorded so §6 is not a reading of intent:

- `compliance._run_check` returns `{"pass": True, "verdict": "GO"}` unconditionally,
  with a hardcoded audit timestamp and `dlv_recorded: True`.
- `eligibility` returns `career_stage=('eligible','senior')` for a senior PI against a
  criterion requiring an early-stage investigator; `rfp.raw_text` is never read.
- `drafting` emits a literal placeholder string with `word_count=150`.
- `export` writes a 47-byte PDF with no `%%EOF`; docx and xlsx raise `BadZipFile`.
- `__main__` builds inputs via `engine.__annotations__["execute"]` → `KeyError:
  'execute'` on six of eight commands.

The gap between this and either the plan's claims or the policy's requirements is
larger than the gap between the plan and its competitors.

---

*Companion document: `docs/TREATISE_RIGHT_TO_LIFE_OF_NEWBORNS_2026-11-03.md` — the
doctrinal argument for why a component born into a regime it did not choose is owed
adjudication before termination. This paper supplies its evidence; that one supplies
its law.*
