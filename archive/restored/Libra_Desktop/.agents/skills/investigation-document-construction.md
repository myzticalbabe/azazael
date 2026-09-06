---
name: investigation-document-construction
description: HTML evidence document construction standards — citation patterns, cross-referencing, styling conventions, document structure, evidence anchoring, and deliverable taxonomy. Distilled from 60+ investigation documents in the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-08-01
---

# Investigation: Document Construction Standards

## Document Taxonomy

The BCC investigation produced 60+ HTML documents. This taxonomy ensures every future investigation is organized the same way:

| Type | Prefix/Pattern | Purpose | Examples |
|------|---------------|---------|----------|
| **Evidence Report** | `*_EVIDENCE.html` | Deep-dive on one investigative question | `INVESTMENT_MANAGER_EVIDENCE.html`, `CAMPAIGN_FINANCE_EVIDENCE.html`, `RECUSAL_EVIDENCE.html` |
| **Gap Audit** | `INVESTIGATION_GAPS.html` | Centralized gap tracker with all 50 gaps, status, and next actions | `INVESTIGATION_GAPS.html` |
| **Evidence Locations** | `EVIDENCE_LOCATIONS.html` | Field guide mapping every gap to exact lookup instructions | `EVIDENCE_LOCATIONS.html` |
| **Data Reference** | `DATA_REFERENCE.html` | Master data dictionary — all extracted data, sources, retrieval dates | `DATA_REFERENCE.html` |
| **Legal Memo** | `LEGAL_*.html` | Legal theories, statutes, referral packages | `LEGAL_REFERRAL_MEMO.html`, `LEGAL_TAXONOMY_OF_HARM.html` |
| **Complaint Letter** | `COMPLAINT_*.html` | Draft complaint letters for submission | `COMPLAINT_LETTER.html`, `COMPLAINT_LETTER_REDACTED.html` |
| **Regulatory Tip** | `FINRA_REGULATORY_TIP.html` | Agency-specific regulatory filings | `FINRA_REGULATORY_TIP.html` |
| **People Report** | `*_PEOPLE_*.html` | Individual person profiles with license/employment data | `INVESTMENT_PEOPLE_REPORT.html`, `PEOPLE_SEARCH_ALT.html` |
| **Financial Analysis** | `*_FINANCIAL_*.html`, `FUNDING_REVIEW.html` | Financial forensics and funding analysis | `BCC_FINANCIAL_WORM_MAP.html`, `FUNDING_REVIEW.html` |
| **Legal Counsel** | `QUI_TAM_COUNSEL.html` | Attorney contact info and consultation guidance | `QUI_TAM_COUNSEL.html` |
| **Strategic** | `STRATEGY_OVERVIEW.html`, `SYSTEMIC_*.html` | Strategy, justification, outreach planning | `STRATEGY_OVERVIEW.html`, `SYSTEMIC_CORRUPTION_JUSTIFICATION.html` |
| **Agent Setup** | `MOLTBOOK_AGENT_SETUP.html` | AI agent deployment packages | `MOLTBOOK_AGENT_SETUP.html` |

## Visual Style Convention

All investigation documents use a consistent dark-theme CSS:

```css
:root {
  --bg: #0d1117;      /* GitHub dark background */
  --card: #161b22;    /* Card background */
  --border: #30363d;  /* Card borders */
  --text: #c9d1d9;    /* Body text */
  --h: #f0f6fc;       /* Headers */
  --a: #58a6ff;       /* Links */
  --r: #f78166;       /* Red — critical/blocked */
  --g: #3fb950;       /* Green — resolved/confirmed */
  --y: #ffa657;       /* Yellow — pending/advanced */
  --p: #d2a8ff;       /* Purple — medium priority */
}
```

### Card border conventions
```css
.card { border-left: 5px solid [color]; }
```
- `.card-red` / `.card-r`: 5px left border `var(--r)` — Critical gaps, blocked methods
- `.card-yellow` / `.card-y`: 5px left border `var(--y)` — High priority, partial findings
- `.card-green` / `.card-g`: 5px left border `var(--g)` — Resolved gaps, completed work
- `.card-purple` / `.card-p`: 5px left border `var(--p)` — Medium priority

### Status badges
```css
.badge { display:inline-block; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-r { background:#2d1010; color:var(--r); }   /* Critical */
.badge-y { background:#2d1b00; color:var(--y); }   /* Advanced */
.badge-g { background:#1b3826; color:var(--g); }   /* Resolved */
.badge-p { background:#1d1530; color:var(--p); }   /* In Progress */
```

## Evidence Citation Pattern

Every factual claim must be anchored. Use this HTML pattern:

```html
<span class="cite">
  SOURCE: [Document Name], [Section/Line], retrieved [Date]
</span>
```

Multi-source claims:
```html
<span class="cite">
  SOURCES: (1) FINRA BrokerCheck API, CRD #5964768, Aug 1 2026;
  (2) BCC 990 FY2025, Part VII, retrieved May 2026 from ProPublica;
  (3) INVESTMENT_MANAGER_EVIDENCE.html, Section III
</span>
```

## Cross-Referencing Convention

Every document should link to related documents. Use relative links:

```html
See: <a href="INVESTIGATION_GAPS.html" style="color:var(--a);">INVESTIGATION_GAPS.html</a>
Full analysis: <a href="INVESTMENT_MANAGER_EVIDENCE.html" style="color:var(--a);">INVESTMENT_MANAGER_EVIDENCE.html</a>
```

**Document footer:** Every document should include a cross-reference footer:
```html
<p class="subtitle">
  Cross-ref:
  <a href="INVESTIGATION_GAPS.html">INVESTIGATION_GAPS.html</a> ·
  <a href="LEGAL_REFERRAL_MEMO.html">LEGAL_REFERRAL_MEMO.html</a> ·
  <a href="DATA_REFERENCE.html">DATA_REFERENCE.html</a>
</p>
```

## Finding Box Patterns

Use these consistently for status callouts:

### Critical finding (red left border)
```html
<div class="locate locate-r">
  <strong>⚠ CRITICAL:</strong> [action required]
</div>
```

### Partial/advanced finding (yellow left border)
```html
<div class="locate locate-y">
  <strong>ADVANCED (Date):</strong> [what was found, what remains]
</div>
```

### Resolved finding (green left border)
```html
<div class="locate locate-g">
  <strong>✅ RESOLVED (Date):</strong> [what was found, source]
</div>
```

## Table Patterns

### Evidence table (standard)
```html
<table>
  <tr><th style="width:25%;">Detail</th><th>Finding</th></tr>
  <tr><td><strong>Item</strong></td><td>Value <span class="cite">Source</span></td></tr>
</table>
```

### Gap status table
```html
<table>
  <tr><th>Gap</th><th>Status</th><th>Finding</th></tr>
  <tr>
    <td><strong>#[N] Title</strong></td>
    <td><span class="badge badge-g">RESOLVED</span></td>
    <td>[Finding details with citations]</td>
  </tr>
</table>
```

## Document Structure Template

Every investigation document should follow this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>[DOC TITLE] — [SHORT DESC] — [DATE]</title>
  <style>
    /* Standard dark theme CSS */
  </style>
</head>
<body>
<div class="container">

  <!-- HEADER -->
  <h1>[ICON] [TITLE]</h1>
  <p class="subtitle">[Brief description, date, status]</p>

  <!-- EXECUTIVE SUMMARY (for long docs) -->
  <div class="locate">[1-paragraph summary of key findings]</div>

  <!-- MAIN SECTIONS -->
  <h2>[SECTION TITLE]</h2>
  <div class="card">
    <!-- content -->
  </div>

  <!-- FOOTER -->
  <p class="subtitle">
    <strong>[DOC].html</strong> — [Date] — [Counts/stats]<br>
    Cross-ref: [links to related docs]
  </p>

</div>
</body>
</html>
```

## Document Metadata

Every document should include in its subtitle:
- **Date created/updated:** "August 1, 2026" or "Updated August 1, 2026"
- **Status:** "DRAFT" / "READY FOR SUBMISSION" / "IN PROGRESS"
- **Counts:** "42 gaps mapped" / "5 legal theories" / "24 portals"
- **Coverage:** "Gaps #1-49" / "FY2017-FY2025"

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| Create a document with no cross-references | Link every doc to its related docs in the footer |
| Leave claims uncited | Every factual claim gets a `class="cite"` span with source and date |
| Mix status colors inconsistently | Red=critical, Yellow=pending, Green=resolved, Purple=medium |
| Write "Part III" without specifying WHICH document's Part III | Always specify: "990 Part III" or "Schedule L Part IV" |
| Create duplicate data across documents | One canonical source per data point. Cross-reference, don't duplicate. |
| Omit the date from a document | Every document has a creation/update date in the subtitle |
| Use inconsistent gap numbering | Once assigned, gap IDs are permanent. Do not renumber. |

## Document Lifecycle

```
DRAFT → IN PROGRESS → READY FOR SUBMISSION → SUBMITTED
  ↓           ↓               ↓
  ABANDONED   SUPERSEDED      ARCHIVED
```

Mark the status clearly in the document subtitle.

## Privacy Rule

**DO NOT include in any document:**
- Complainant personal identifiers (name, address, phone)
- Patient names or identifying details
- Whistleblower contact information
- Unredacted legal complaints with complainant details

**CREATE REDACTED VERSIONS** for external sharing. The naming convention: `COMPLAINT_LETTER_REDACTED.html` (shareable) vs. `COMPLAINT_LETTER.html` (access-controlled).

## Related Skills
- `investigation-990-forensics` — 990 data that populates evidence documents
- `investigation-legal-referral` — Legal memo format and evidence anchoring
- `investigation-evidence-location` — Gap tracking and evidence status
