---
name: investigation-survey-enumeration
description: Complete regulatory survey-portal enumeration — retrieve and classify EVERY record from a licensing/survey portal (detail-page URL pattern, verbatim classification of official comments, keyword-traps in agency phrasing, published-correction records). Distilled from the BCC DDAP investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-02
---

# Investigation: Survey Portal Enumeration

## Overview
When an agency (e.g., a state licensing body) publishes survey records for licensed providers, the evidence-grade
answer is to enumerate **100%** of the records — never a partial sample — and classify each from verbatim official
text.

## Core Technique
1. **Find the detail-page URL pattern** — each record links to a detail page; enumerate every ID.
2. **Enumerate 100%** — open and classify every record. Coverage must be stated exactly (24/24, never rounded, and
   never implied from a partial review).
3. **Classify from verbatim official fields** (e.g., INITIAL COMMENTS) — do not paraphrase or translate agency
   language into your own words.
4. **Watch for keyword traps** — agency phrasing like `not to be in compliance` is *not* a clean finding; quote it
   verbatim rather than converting it into a plain-English claim.
5. **Corrections register** — every superseded claim gets an ID (C1–C4…) with reason; corrected claims must not be
   repeated in later work.

## Anti-Patterns
- Partial-sample figures presented as the full picture (e.g., "8-of-9 (89%)" when 24 records exist).
- Paraphrased compliance language instead of the official phrasing.
- Claiming records (e.g., Corrective Action Plans) are unavailable when they are published portal records.

## Case Example
- `bcc-ddap-portal-enumeration` (case-scoped) — PA DDAP 24/24 survey enumeration (2006–2026), 21 of 24
  non-compliant, superseding the 9-of-24 partial review. Artifacts: `ddap_full24.py` + `ddap_full24.json` +
  DDAP_INVESTIGATION_EVIDENCE.html §0–§0C.