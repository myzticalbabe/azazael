# CRADLE — 12-month timeline

**Companion to** `cradle_proposal.md`. Each work package ends at a gate; the gate is
a measurement, not a status report. A gate that fails changes the *next* package,
never the gate's own wording.

Month 0 is the month the grant is signed. All durations in calendar months.

---

## Overview

| WP | months | deliverable | gate question |
| --- | --- | --- | --- |
| WP0 Setup and baseline | 0–1 | — | Does the chain run on the machine of someone who is not the author? |
| WP1 Claim corpus | 1–4 | D1 | Can a second person score a frame from the rubric alone and agree? |
| WP2 Efficacy measurement | 4–5 | D2 | What is the false-negative rate on confabulated claims, with a lower bound? |
| WP3 Portability | 3–6 | D3 | Do `--doctor` and `--demo` pass on Linux and macOS? |
| WP4 Independent security review | 6–8 | D4 | Has someone who did not write it read the refusal path and published findings? |
| WP5 Spec extraction | 7–10 | D5 | Can a third party implement a conforming checker from the spec alone? |
| WP6 Packaging and docs | 9–11 | D6 | Does a first-time user reach a refusal without reading the source? |
| WP7 Dissemination and close | 11–12 | — | Are D1–D6 published, including the ones that went badly? |

WP1 is the long pole. WP2 cannot start before it and WP5 inherits its vocabulary.
WP3, WP4 and WP6 run in parallel with the others because they do not depend on the
corpus.

---

## WP0 — Setup and baseline (month 0–1)

- Freeze the current behaviour as a baseline: run `--doctor` and `--demo` on the
  reference platform and record the output verbatim.
- Record the eight chain tests' present state: pass, skip, or absent — with the
  reason for each skip. A skip is recorded, never converted to a pass.
- Publish the baseline artefact before any change, so later claims can be checked
  against it.

**Gate:** a reader on a different machine reproduces the baseline.
**If it fails:** the reproducibility gap is the first deliverable, and WP1 slips.

## WP1 — Claim corpus, 300 labelled claims (month 1–4)

- 150 claims that resolve (path exists, act is in the vocabulary, outcome observed)
  and 150 that do not, taken from real agent sessions rather than invented ones.
- One row per claim: the claim text, the frame, the label, the rubric clause it
  exercises, the provenance of the session it came from.
- Labels are per claim. No aggregate label that hides a disagreement.
- Adversarial sub-set: claims that are *true but unverifiable* (the action happened,
  no evidence survives) kept as their own class, because conflating them with
  confabulation is the most likely error in this project.

**Gate:** blind re-scoring by a second person, disagreement rate published.
**If it fails:** the rubric is rewritten and the corpus re-scored. The failure is
published, not replaced with a friendlier corpus.

## WP2 — Efficacy measurement (month 4–5)

- Run the sentinel over the corpus; produce a confusion matrix over the classes in
  WP1, including the unverifiable class.
- Report **recall on confabulated claims with a lower bound**, and the false-positive
  rate on resolving claims, side by side. One without the other is an advertisement.
- Publish the threshold used and what happens to both rates when it moves.

**Gate:** a number with a stated bound, published whether or not it flatters the
project. **If recall is poor:** publish it, and the remaining months deliver the
corpus, harness and spec so that a better checker can be built on them.

## WP3 — Portability (month 3–6)

- Linux (x86-64) and macOS (arm64) validation of `--doctor`, `--demo` and the five
  endpoints.
- Free-threaded interpreter matrix documented per platform: which CPython builds the
  project is actually validated on, and which are untested.
- Fixes for path handling, stdio framing and process launch that are Windows-shaped.

**Gate:** `--doctor` and `--demo` pass on both platforms from a clean environment.
**If a platform cannot be supported:** it is documented as unsupported with the
reason, not left ambiguous.

## WP4 — Independent security review (month 6–8)

- Scope: the refusal path (does a frame ever pass with an unresolved claim?), the
  endpoint surface, the state directory, and the model bridging.
- Reviewer is not the author and has not previously reviewed the tree.
- All findings published, including unfixed ones, with severity and disposition.

**Gate:** a written report exists and is published in full.
**If findings are severe:** remediation takes priority over WP5/WP6 within the same
grant, and the schedule moves rather than the disclosure.

## WP5 — Spec extraction (month 7–10)

- Extract the claim vocabulary, the frame lifecycle, the refusal reasons, and the
  lesson format into a spec independent of the implementation.
- Publish a conformance suite: fixtures a conforming implementation must accept or
  refuse identically.
- Implement one deliberately minimal reference checker *from the spec* to test
  whether the spec is sufficient.

**Gate:** the reference checker is written using only the spec, and the conformance
suite distinguishes it from a non-conforming stub.
**If it fails:** the spec has a gap; the gap is the deliverable that month.

## WP6 — Packaging and docs (month 9–11)

- Install path for a person who is not the author: one command, one refusal, one
  explanation.
- "Add a vocabulary term" walkthrough — the most common extension.
- Rewrite the docs that assume the author's machine, vocabulary or Windows paths.

**Gate:** an unassisted first-time user reaches a refusal and can say why it
happened. **If it fails:** the transcript of the failure ships with the docs.

## WP7 — Dissemination and close (month 11–12)

- Publish D1–D6 with the negative results intact.
- Two events: one developer-facing, one standards/verification-facing.
- Close-out note: what was claimed at the start, what was measured, and where the
  two differ.

---

## Standing rules across all work packages

1. **A gate that fails is published as a failure.** No deliverable is redefined to
   match its result.
2. **A skip is never a pass.** Absent siblings are reported `N/A` with the reason.
3. **No claim without its command.** Every rate quoted in a report names the run
   that produced it.
4. **The corpus is the asset.** If the checker underperforms, D1 remains valuable;
   this is the plan's main hedge and it is deliberate.
5. **Compute stays rented.** No hardware purchase is scheduled in any month.

## Schedule risk

The single largest risk is WP1: real confabulated-claim sessions may not exist in
sufficient number, in which case the corpus is smaller and the lower bound in WP2 is
wider. A smaller corpus with an honest bound is the acceptable outcome; a padded
corpus is not.
