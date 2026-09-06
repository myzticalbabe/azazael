---
name: investigation-fetch-verification
description: Accuracy discipline for scripted data fetching — persist raw before classifying, match keywords to real phrasing (keyword traps), browser spot-check evidence, and maintain a corrections register (C1–C4) so corrected claims are never repeated. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-02
---

# Investigation: Fetch Verification

## Overview
The discipline that keeps scripted/automated fetching evidence-grade: everything classified must be re-checkable
against raw source, and every correction must be tracked so it is never reintroduced.

## Core Technique
1. **Persist raw before classifying** — save the exact fetched bytes/text untouched before any extraction or
   classification step.
2. **Match keywords to real phrasing** — automation keyword filters must match the *actual* page wording (e.g.,
   `not to be in compliance`), never a paraphrase. A keyword trap is a vocabulary mismatch, not a page failure.
3. **Browser spot-check** — any automated finding that becomes evidence gets a live-page confirmation
   (Chrome CDP / manual).
4. **Corrections register (C1–C4…)** — every superseded or corrected claim is recorded with ID + reason; corrected
   claims **must not be repeated** in later documents or scripts.

## Anti-Patterns
- Classifying from a post-processed string with no raw artifact saved.
- Filtering on your own paraphrase instead of the source's words.
- Silently repeating a previously corrected claim (the register exists precisely to prevent this).

## Case Example
- `scripted-fetch-verification` (case-scoped) — C1–C4 in DDAP_INVESTIGATION_EVIDENCE.html §0 (8-of-9 sample
  figures, "only" phrasing, CAPs-unavailable claim) superseded by the 24/24 verbatim enumeration.