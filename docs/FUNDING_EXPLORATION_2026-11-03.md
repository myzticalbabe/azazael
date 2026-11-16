# FUNDING EXPLORATION — MORE STREAMS, AND THE REASON NONE ARE OPEN

**Date:** 2026-11-03 · **Question:** are there funding streams beyond the 38 the
profiles already carry, and are there other projects here that could be funded?
**Method:** four funder pages read (NLnet call, NLnet AI policy, GitHub Secure OSS
fund, an OSS grants index), six searches, two GitHub API reads, three local
measurements. Every claim below is tied to the page or command that produced it.

---

## 0. The answer

**Six streams are not in the register. One is open today. None is currently
applicable, and the reason is not the funder list.**

Measured against the door that is actually open right now (GitHub Secure OSS Fund),
this repository fails on three of its named criteria simultaneously:

| criterion on GitHub's own eligibility list | measured here |
| --- | --- |
| "Open source first project with demonstrated community traction and adoption" | **0 stars, 0 forks, 0 watchers, 0 open issues** (GitHub API, 2026-11-03) |
| "Clear open source license" | **CDDL-1.1, but the root did not say so** — no root licence file, so API returns `license: null`; `pyproject.toml` contradicted the seven project files with Apache-2.0 |
| "Clear governance structure prior to kick-off" | CONTRIBUTING + CoC exist per project; no top-level governance, and nine sibling projects with no stated relationship to each other |

The repository was created **2026-11-03T02:55:10Z** — it is hours old. There is no
adoption to demonstrate because there has been no time in which adoption could
happen. That is the finding: the constraint is evidence of use, not the number of
funders.

## 1. Four corrections to the register

Each of these changes something the register stated, so each is recorded against it.

### (a) NLnet's next deadline is 3 January 2027 — read, not guessed

The register deliberately left this unverified because guessing it is how the
retired batch row was wrong. It is now read from NLnet's own site:

> "Next deadline January 3, 2027" — banner, `nlnet.nl` (read 2026-11-03)
> "NLnet picks up on the rolling open calls it has had for the better part of two
> decades, with a deadline every two months … shifted the cadence from the even
> months to the odds, and from the first day to the third."

**Cadence: every two months, odd months, day 3.** So: 3 Jan 2027, then 3 Mar, 3 May…

**The programme changed too.** NGI has a successor, *Open Internet Stack*, and the
open theme funds are now **Restack** (scalable open internet stack), **CodeSupply**
(software supply-chain security via packaging metadata) and **GeoCommons**. These
are separate from the register's `nlnet` key, which describes the older open call.

### (b) NLnet now forbids generative AI for proposals *and* for artefacts

Published **2026-10-20**, policy v2.0, effective immediately and applying to **every
call whose deadline is after that date — which includes 3 January 2027**:

> "Generative AI can no longer be used for writing proposals — with the noted
> exception of supporting accessibility needs. For project development the use of
> LLMs and diffusion models is confined to read-only usage."
> "It is not allowed to use generative AI for producing artefacts of any kind,
> including code, design, and documentation."

The stated reason is directly relevant to this tree: NLnet says it received "an
avalanche of additional proposals lacking maturity and relevance", that AI-involved
proposals were "on the whole of much lower quality", and that evaluating them was
"very taxing and demotivating".

**This has two consequences, and the second is the serious one.**

1. **The four documents written earlier today are not submittable to NLnet.** The
   proposal, timeline, budget narrative and deck were produced by an LLM. They are a
   scaffold a human can rewrite in their own words and their own reasoning — the
   measured figures and the arithmetic survive — but submitting them as they stand
   would breach the policy the funder published two weeks ago.
2. **The 33-profile generator is the exact failure mode the policy names.** A tool
   that mass-produces proposals across projects and funders is what produced the
   avalanche. The `Project_Scribe` approach is not merely inefficient here; at
   NLnet it is now disqualifying in principle.

One carve-out worth knowing: applications *written with AI and submitted before
2026-10-20* need not be resubmitted. That does not help — nothing was submitted.

### (c) GitHub Secure OSS Fund takes applications on a rolling basis

The register listed it as a session-cadence programme (~2–3 per year, next date
announced). GitHub's own FAQ says otherwise:

> "Applications are open on a rolling basis and will be considered for all Program
> Sessions."

$10,000 per project ($6,000 during the 3-week programme, $2,000 at 6 months,
$2,000 at 12 months), plus **$10,000 in Azure credits**, with up to $150,000 in
Microsoft for Startups infrastructure credits for eligible projects. It is suited to
"individual maintainers or small teams".

**So this is the one stream that can be applied to today with no entity and no
deadline** — and it is gated on the three things measured as absent in §0.

### (d) Emergent Ventures — individuals, $1k–$50k, and also an AI ban

Mercatus's Emergent Ventures funds individuals ($1k–$50k) with no entity required,
which would have made it a strong Tier A addition. Its application page states:

> "Emergent Ventures no longer accepts AI-written applications. We will test all
> submissions and reject those using AI for anything other than…"

**Two of the three doors open to a natural person now reject AI-written
applications.** That pattern is the most important thing in this document, because
it invalidates the strategy the profiles encode rather than any single funder row.

## 2. Streams not in the register

| stream | gate | status 2026-11-03 | fit here | confidence |
| --- | --- | --- | --- | --- |
| **GitHub Secure OSS Fund** *(already in register, but rolling)* | individual maintainer, 18+, GitHub Sponsors region, **traction**, **licence**, governance | **open, rolling** | security-shaped work only; traction is 0 | **checked** (fund page read) |
| **NLnet Restack / CodeSupply / GeoCommons** | individual or org; **no AI-written proposals**; no AI-generated artefacts | deadline **3 Jan 2027** | CodeSupply (supply-chain/packaging) is the closest of the three; CRADLE is the weakest | **checked** |
| **Emergent Ventures** | individual, application form | open | none — AI ban | **strong** (search result quoting their page) |
| **Manifund** | individuals post a project; regrantors allocate | open, AI-safety regranting active in 2026; past grants $500–$13k | only if framed as agent-governance / audit research, which is a stretch | **unverified** — scope and AI policy not read |
| **Sovereign Tech Agency / STF** | open to applicants worldwide per EU case study; cycle-based | 2026 cycles ran spring (fellowship applied by 6 Apr 2026); no current call seen | funds *critical infrastructure*; none of the nine projects is depended on | **unverified** — programme page not read for a live call |
| **PSF Grants Program** | individuals and orgs | 2026 round closed 25 Aug 2026; **scoped to conferences and workshops** | no — it funds events, not software | **checked** |
| **NumFOCUS Small Development Grants** | NumFOCUS-sponsored or affiliated projects only | n/a | no | **checked** (index) |
| **OpenSSF technical initiative funding** | OpenSSF technical-initiative communities | n/a | no — community membership is the gate | **checked** (index) |
| Awesome Foundation microgrants ($1k) | anyone, monthly chapters | not checked | possible, small | **unverified** |

Six are new relative to the register's 38 keys. **None converts a zero-traction
repository into an eligible one.**

## 3. Project by project — what is actually fundable-shaped

The register chose CRADLE from these nine. That choice deserves a second look now
that NLnet's AI policy has changed, because CRADLE's fit was already the thinnest
part of it.

| project | what it is (from its own README) | fundable shape? | the honest problem |
| --- | --- | --- | --- |
| **FLAMING_SWORD** | finds defect classes a review cannot, queues them, fixes in batches, **proves each batch with the project's own test command**, lands with a decision trail | **the strongest** — verification-first code repair is a real security story | zero users; "proves with the project's own tests" is exactly what a security funder wants to hear and exactly what needs a dependent project to demonstrate |
| **CRADLE** | runs a prompt through four parts and **refuses to land a frame whose claims do not resolve**, plus a doctor | plausible for a verification/trust funder | **not open-internet infrastructure**, which is what NLnet funds; and it is an LLM pipeline, so NLnet's read-only rule bites twice |
| **ELIZA** | therapeutic agent + the instruments that prove what it cannot do | health/mental-health funders | the mental-health funders in the register (`openai_mental_health`) are entity-gated, and clinical claims invite a review no one here can pass |
| **Nurse_Ratchet** | behavioural package, "live counselor" role, six requirements it does not yet meet | same as ELIZA | same gate; also the profile with `nlnet: null` (recorded defect) |
| **FLAME** | game engine + conversion of a **discontinued game** into a shard | no | copyright exposure is the whole premise; no funder will underwrite it |
| **SHARDEX** | builds a shard, renders its mesh, **checks the result rather than trusting a digest written by the same code** | niche tooling | verification angle is good, audience is a handful of people |
| **JAEGER** | internal tracer consuming the tree's own specs | no | explicitly *not* an OTLP client — it is deliberately not interoperable, which removes the ecosystem story |
| **Oxenford** | a written paradigm for evolving a tool against a world it does not own | not software | it is a method essay; it could be an article, not a grant deliverable |
| **Scribe** | the grant-application automation tool | no | it is the thing that produced 1,155 unusable rows |

**The pattern:** the two projects with a genuine funder story (FLAMING_SWORD,
SHARDEX) share one property — **they check results instead of trusting the code that
produced them**. That is a coherent thesis and it is the same thesis as this tree's
audit-trail work. That is the sentence a proposal should be built on. CRADLE is the
weakest of the strong set and it was chosen first.

## 4. Two defects found while measuring

**(a) The licence is CDDL-1.1, and the root did not say so.** This one needed a
correction mid-review, because the convenient reading was wrong. The GitHub API
returns `"license": null`, but that is a statement about *detection at the
repository root*, not about whether licence files exist. Measured:

| location | licence |
| --- | --- |
| `Project_CRADLE`, `_ELIZA`, `_FLAME`, `_FLAMING_SWORD`, `_JAEGER`, `_Nurse_Ratchet`, `_SHARDEX` | **CDDL-1.1** (7 of 8, read from each file) |
| `Project_Oxenford` | none |
| repository root | **none at the time of measurement** — no `LICENSE`, `LICENCE` or `COPYING` |
| `pyproject.toml:7` | `license = {text = "Apache-2.0"}` — **contradicted the seven files** |

The owner's ruling (2026-11-03) is that the licence is **CDDL-1.1**; the Apache-2.0
line was the deviation, not a second decision. A byte-identical copy of
`Project_CRADLE/LICENSE` now sits at the repository root (sha256 `64660678…4b7b`,
both files), which is the location GitHub actually reads.

The `pyproject.toml` half is corrected in the working tree but **not committed**:
the file carries 46 lines of another lane's uncommitted rewrite (118 lines working
vs 59 at HEAD), so staging it would sweep unrelated work into this change. Two TOML
defects had to be repaired for the declaration to be readable at all — a multi-line
inline table at line 96 and `warn_unused_ignores` set twice in `[tool.mypy]` — and
the file now parses, reporting `license = {'text': 'CDDL-1.1'}`. HEAD still says
Apache-2.0 until that file is committed deliberately.
`Project_Oxenford` still has no licence file.

Why it mattered: GitHub's fund lists "clear open source license" as a criterion, and
a reviewer's first click is the repository page, which reported nothing. GitHub
detects licences at the root only, so the seven correct files were invisible to it.

**(b) The public repository carries 2.0 GB, mostly vendored tarballs.** Largest
tracked files, measured with `du`:

```
272 MB  archived/2026-05-31/onnxruntime.tar.gz
229 MB  archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz
 31 MB  archived/.../coreml_Resnet50_ImageNet-dq.onnx   (three copies)
```

Three copies of onnxruntime (one tarball, one extracted source, one git checkout)
account for most of it. A 2 GB clone is the opposite of "traction", and it makes the
one thing a reviewer does — clone and read — expensive. (Untracked browser-profile
directories are also present in the working tree; they are **not** tracked, which
was checked, so no cookies are published.)

## 5. What to do, in order

1. ~~**Add a root licence and settle which one is real.**~~ **Half done 2026-11-03:**
   CDDL-1.1 now sits at the root, which is what GitHub detects. Outstanding: commit the
   `pyproject.toml` correction once that file's 46 lines of foreign uncommitted work are
   settled (HEAD still declares Apache-2.0), give `Project_Oxenford` a licence file, and
   push — detection updates only on push, so the API keeps reporting `null` until then.
2. **Split the repository.** Nine sibling projects with no stated relationship, in a
   2 GB tree, reads as one unpublished workspace. A funder needs a project that can
   be depended on, named, and versioned.
3. **Pick the verification thesis, not the project.** FLAMING_SWORD and SHARDEX both
   sell the same claim: *this does not accept a result it cannot check*. That is
   fundable, it is true here, and it does not depend on LLM-generated artefacts.
4. **Then submit to GitHub's fund** — rolling, so the date is yours, and the
   programme is 20 hours over a year. Expect rejection while traction is zero; the
   application is also the cheapest way to learn which criterion is binding.
5. **Manifund, only if** the project can be honestly described as agent-governance
   or audit research. Post it as a project and let regrantors decline it; there is
   no application fee. Read Manifund's own scope first — that was not done here.
6. **NLnet on 3 January 2027, human-written**, aimed at **CodeSupply**, with the
   proposal typed by the applicant and LLMs used only read-only. Do not resubmit the
   documents produced today.
7. **One 0DIN report** to test the bounty stream against real effort, as the
   register already says.

## 6. Limits

- Six pages were read and six searches were run. Nothing was verified by contacting
  a funder, and no application was opened.
- Emergent Ventures' AI rule is quoted from a search snippet of its own page, not
  from a page read in full.
- Manifund's scope and its own AI policy were **not** read; treat that row as a lead,
  not a plan.
- Sovereign Tech Agency's current call status was not established; the register's
  cycle reference is from 2026 spring.
- The traction measurements are a single API read at one moment on a repository
  created the same day. They will change if anything is published.
- Nothing here is legal, tax or financial advice.

**Expiry: 2026-12-03** — deadlines, programme scopes and AI policies have all moved
within the last three weeks; assume they move again.
