# CRADLE — a verification chain for claims made by AI agents

**Proposal to the NLnet Foundation / NGI Zero**
**Applicant:** Clint Oxford (individual), United States
**Project:** Project CRADLE — `https://github.com/myzticalbabe/azazael/tree/main/Project_CRADLE`
**Licence:** CDDL-1.1 (see `LICENSE`, `NOTICE`, and the licence ruling recorded in
`docs/LICENSE_PRECEDENT_CDDL11_2026-11-03.md`)
**Amount requested:** €49,500 over 12 months
**Document date:** 2026-11-03

---

## 1. The problem

An AI agent that can edit files, run commands and answer users will assert things
that are not true. Not maliciously — structurally. It produces a sentence that
*reads* like a verified claim ("I updated the config, tests pass"), and nothing in
the loop checks whether any path it names exists, whether the command it quotes
was run, or whether the outcome it reports matches what happened.

The usual mitigations do not close this:

- **Bigger models** reduce the rate; they do not make the claim checkable.
- **Cloud guardrails** move the verification into a vendor's process, on a vendor's
  terms, with the user's prompts on the vendor's disk.
- **Evaluation harnesses** score a model offline. They do not stand between an
  agent's claim and the user who is about to believe it.

What is missing is small, local and boring: a component that takes an agent's
claim, resolves every path and every act against a closed vocabulary, and
**refuses the frame** when it does not resolve — before the user reads it.

## 2. What CRADLE is

CRADLE is a composition and verification layer. It wires four existing parts into
one command and one local endpoint:

| part | source | what it does |
| --- | --- | --- |
| **FLAMING SWORD** (sword) | `Project_FLAMING_SWORD/tools/sword.py` | find → queue → fix → prove → land across a codebase |
| **defender** | `tools/defender.py` | turns a user prompt into a frame that can be satisfied or refused |
| **sentinel** (REAPER) | `tools/sentinel.py` | stat's every path, requires every act from a closed vocabulary, removes a frame that does not resolve from play |
| **memory** (GRIMOIRE) | `tools/memory_bridge.py` | one line per failure, written at the moment it failed; recalled by the next frame, or reported `UNMEMORED` with its reason |

CRADLE adds no judgement of its own. It launches them in the order that makes each
answer meaningful.

Three commands:

```bash
python Project_CRADLE/cradle.py --doctor   # per-requirement readiness, exit 1 on failure
python Project_CRADLE/cradle.py --demo     # end-to-end proof, no model required
python Project_CRADLE/cradle.py --serve --model-url http://127.0.0.1:11434/v1 --model-name llama3.1
```

Local endpoints: `GET /health`, `GET /frames`, `POST /aio`, `POST /ask`,
`POST /verify`. The refusal is the point: `POST /aio` returns **422 with the
failed claims and no prompt** when a frame does not resolve. `POST /ask` returns
`503 NO-MODEL` rather than an invented answer when no model is configured.

## 3. Why this is NGI infrastructure and not an application

- **Local-first.** CRADLE never holds weights, never needs an API key, and never
  sends a prompt anywhere except the endpoint the user names. It speaks the
  OpenAI chat shape, so Ollama, llama.cpp, LM Studio and vLLM all work.
- **No dependency surface.** The Python side is standard library only, so the
  verification layer cannot itself become the supply-chain risk it audits.
- **Vendor-neutral by construction.** The same claim-check runs against any model
  the user already has, including the next one they install.
- **A commons artefact, not a service.** CDDL-1.1, with the failure vocabulary and
  the lesson format documented as a spec that other tools can implement.

## 4. Current state — what exists and what does not

Stated together, because either half alone is misleading.

**Exists and is measurable:**

- The four parts, the composition, `--doctor`, `--demo` and `--serve`, and the five
  endpoints, documented in `CRADLE.md`.
- A demo that includes **a deliberate failed verification**, so a lesson is seen to
  be written and then recalled. A happy-path demo teaches nothing about refusals.
- Eight chain tests that **skip when a sibling part is absent and are never
  weakened** — a missing part is reported `N/A`, not counted as a pass.
- Reference platform documented in `HARDWARE.md`: Intel Core Ultra 9 285H, Intel
  Arc 140T (8 GB shared), 32 GB LPDDR5x, Windows 11 Pro, CPython 3.14.7 and
  3.15.0rc3 free-threaded. **No discrete GPU is owned. There is no training step in
  this project and none is proposed.**

**Does not exist yet — the work this grant would fund:**

- **No independent security review.** The refusal logic has never been examined by
  anyone who did not write it.
- **One maintainer.** Bus factor one, and the documentation assumes the author's
  machine and vocabulary.
- **Windows-first validation.** The free-threaded interpreters are validated on
  Windows; Linux and macOS behaviour is untested.
- **No falsifiable efficacy result.** Nothing measures the rate at which a
  confabulated claim is caught, because no labelled corpus of such claims exists.
  Until it does, no efficacy claim should be made for this project.

## 5. Deliverables and acceptance criteria

Each row is written so it can fail.

| # | deliverable | acceptance criterion (falsifiable) |
| --- | --- | --- |
| D1 | **Claim corpus** — 300 labelled agent claims (150 resolving, 150 confabulated), published with provenance | A second person can score a frame using only the published rubric and agree with the label; disagreements reported, not silently adjudicated |
| D2 | **Refusal precision/recall** measured on D1 | Reported as a confusion matrix with a lower bound; **a poor number is published as it stands** |
| D3 | **Portability** — Linux and macOS validation | `--doctor` and `--demo` pass on both; the free-threaded interpreter matrix documented per platform |
| D4 | **Independent security review** of the refusal path and the endpoint surface | Reviewer's findings published in full, including unfixed ones |
| D5 | **Vocabulary and lesson-format spec** extracted from the implementation | A third party implements a conforming checker from the spec alone; conformance suite published |
| D6 | **Packaging and docs for non-authors** — install, first refusal, how to add a vocabulary term | A first-time user reaches a refusal without reading the source |

D2 is the deliverable that makes the rest honest. A verification layer whose
own catch rate is unmeasured is a claim, not a control.

## 6. Risks, and what would falsify this plan

| risk | what it would look like | response |
| --- | --- | --- |
| Refusal rate is poor | D2 shows low recall on confabulated claims | Publish it; the corpus and harness remain useful to anyone building a better checker |
| Corpus is unrepresentative | Reviewers dispute D1's labelling | Provenance published per claim; labels are per-claim, not aggregate |
| Bus factor | Maintainer unavailable → project stalls | D5's spec allows independent implementation; that is precisely why it is a deliverable |
| Refusals annoy users into disabling them | Frames refused that a human would accept | False-positive rate is reported alongside recall; threshold documented and adjustable |
| Scope creep into "agent framework" | New features that do not serve verification | Every deliverable maps to D1–D6; anything else is out of scope for this grant |

## 7. Prior work

The four parts ship today and run today; CRADLE composes them and reports a missing
sibling rather than failing (a part that was never going to be in this repository is
not a defect in this repository). The surrounding ecosystem — FLAMING SWORD,
SHARDEX, FLAME — is public in the same repository under CDDL-1.1. This proposal
concerns CRADLE only.

## 8. Budget

€49,500 total, fully itemised in `cradle_budget.xlsx`. Summary:

- Personnel, 0.5 FTE lead over 12 months plus a second contributor: €31,000
- Independent security and privacy review: €6,000
- **Rented compute** (GPU-hours for runtime-compatibility testing, CI): €2,500
- Documentation, packaging, spec extraction: €3,500
- Dissemination (two events): €2,000
- Contingency (10%): €4,500

**Equipment purchase: €0.** No GPU, workstation or server is requested. The compute
line is rented hours at published on-demand rates, because CRADLE's compute need is
model-serving compatibility testing, not training. A justification of the form
"RTX 4090 for stdlib-only orchestration" would be neither true nor necessary, and is
not made here.

## 9. Disclosure of AI use

In line with the call's requirement to declare it:

- **AI was used in the development of this codebase.** The prompt in the source
  profile records AI assistance for orchestration logic and `--doctor` sibling
  detection. This is disclosed rather than minimised.
- The codebase **contains AI-generated code**, reviewed and tested by the applicant;
  the eight chain tests and the `--demo` failure path exist because review alone was
  not trusted.
- **This proposal was drafted with AI assistance**, from the project's own
  documentation and measured values. Every number in §4 and §8 is traceable to a
  file in the repository or to the budget workbook; no capability is claimed that
  the repository does not show.

## 10. Contact

Clint Oxford, individual applicant, United States. Contact details as given in the
application form. Repository: `github.com/myzticalbabe/azazael`, directory
`Project_CRADLE`.
