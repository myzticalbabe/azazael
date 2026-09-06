---
name: investigation-990-data-access
description: Form 990 data access patterns — ProPublica Nonprofit Explorer endpoints that return JSON vs the JS-rendered /full view (browser required), IRS bulk-XML 302/404 handling, EIN-keyed lookups. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-09-02
---

# Investigation: 990 Data Access

## Overview
How to reliably pull nonprofit Form 990 data — which endpoints are machine-readable and which require a browser.

## Core Technique
- **JSON-returning endpoints:** `projects.propublica.org/nonprofits/organizations/{EIN}` serves machine-readable
  990 e-file data (filings list, totals, schedules) directly — full multi-year coverage without a browser.
- **The JS-rendered `/full` trap:** the ProPublica `/full` (full-text) view renders client-side — plain HTTP
  fetches (read_url/curl) see no document text. Use the JSON API or the original IRS e-file PDF on the same host
  instead.
- **IRS bulk-XML handling:** `bulk.data.irs.gov` returns 302 redirects (follow explicitly) and 404s for
  missing/renamed files — treat 404 as "no file this quarter," not a scraper failure.
- **Always carry the EIN** — every ProPublica URL is EIN-keyed; never search by name.

## Companion Sources
- **IRS TEOS** (`apps.irs.gov/app/eos`) — 501(c)(3) status, revocation history; watch for WAF blocks (Akamai).
- **USASpending.gov v2 API** — federal grant data (obligated vs outlaid).
- **GuideStar/Candid** — profiles, sometimes paywalled.

## Case Example
- `bcc-propublica-990` (case-scoped) — BCC EIN 23-2043478; results in FUNDING_REVIEW.html,
  INVESTMENT_PEOPLE_REPORT.html, CAMPAIGN_FINANCE_EVIDENCE.html. See also `investigation-990-forensics` (#1230)
  for the analysis patterns.