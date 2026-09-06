---
name: investigation-evidence-location
description: Evidence location mapping and gap management — IRC § 6104(d) disclosure requests, FOIA/Right-to-Know procedures, government portal navigation with blocked-method workarounds, gap classification system. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-08-01
---

# Investigation: Evidence Location & Gap Management

## Gap Classification System

Use this 4-tier system for every investigation:

| Tier | Label | Criteria | Action |
|------|-------|----------|--------|
| 🔴 **Critical** | Blocks all action | Without this evidence, no complaint can be effectively filed | Resolve FIRST — this is the bottleneck |
| 🟠 **High** | Severely limits action | Complaint can be filed but will be weak or incomplete without it | Resolve before filing any complaint |
| 🟣 **Medium** | Strengthens existing case | Complaint is viable without it, but evidence adds weight | Resolve in parallel with complaint filing |
| 🔵 **Low** | Nice-to-have context | Background enrichment; filing is complete without it | Resolve opportunistically |

## Gap States

Track every gap through these states:
- `OPEN` — Not yet investigated
- `PARTIAL` — Some data obtained, more needed
- `ADVANCED` — Primary paths exhausted, secondary/tertiary paths identified
- `RESOLVED` — Answer found and verified
- `BLOCKED` — All reasonable paths exhausted without legal compulsion; workaround documented

## IRC § 6104(d) — The Nonprofit Public Disclosure Swiss Army Knife

This is the SINGLE MOST POWERFUL tool for nonprofit investigations. Every 501(c)(3) organization MUST:

**What they must provide on request:**
1. Form 990 (all schedules) for the last 3 years
2. Form 1023 (exemption application) and all supporting documents
3. **Any document required to be kept by the organization** — including:
   - Conflict of interest policy
   - Whistleblower policy
   - Document retention policy
   - **Board meeting minutes** (990 Part VI, Line 8)
   - **Audited financial statements**
   - Bylaws

**How to request:**
```
"Pursuant to IRC § 6104(d)(1)(A), I request a copy of [specific document]
from [organization name], EIN [number]. Please provide it within 30 days
as required by § 6104(d)(1)(B)."
```

**Critical rules:**
- Request must be made in writing (email qualifies as "in writing")
- Organization has **30 days** to respond (§ 6104(d)(1)(B))
- Organization can charge reasonable copying costs but CANNOT charge for staff time
- If they refuse, file a complaint with the IRS TE/GE Division
- **Penalty for non-compliance:** $20/day, up to $10,000 per return (IRC § 6685, cross-referenced by § 6104(d)(4))

**⚠ Security consideration for hostile investigations:**
- Sending a § 6104(d) request directly to the target tips them off
- Alternative: route through a third party (attorney, reporter, community member)
- Alternative: file through a regulatory agency that can demand documents under its own authority
- **For the BCC investigation, the recommendation was to route through PA AG Charitable Trusts rather than send directly**

## FOIA / Right-to-Know Requests

### Federal FOIA (5 U.S.C. § 552)
- **SAMHSA FOIA Office:** `SAMHSAFOIA@samhsa.hhs.gov`, 5600 Fishers Lane, Rockville MD 20857
- **HHS FOIA:** `foia.hhs.gov`
- **IRS FOIA Form 4506-A:** Mail to IRS, Ogden UT 84201-0024. Check appropriate boxes for Schedules B, J, etc. Fee: ~$40/return year.

### PA Right-to-Know Law (65 P.S. §§ 67.101-67.3104)
- **Standard form:** `openrecords.pa.gov` → File a Request
- **Berks County:** `countyofberks.com/departments/open-records`
- **PA DHS/OMHSAS:** `dhs.pa.gov/contact/Pages/Right-to-Know.aspx`
- County may charge duplication costs (~$0.25/page)

### What to request via RTK
- County contracts, MOUs, payment records naming the target
- State audit reports, survey findings, corrective action plans
- Grant sub-agreements between county authorities and the target
- Property acquisition records related to HUD/ CoC programs

## Portal Classification — Access Patterns

### Category 1: Direct API (automated) ✅
- FINRA BrokerCheck search API: `api.brokercheck.finra.org/search/individual/{CRD}`
- USASpending.gov API: `api.usaspending.gov`
- SEC EDGAR: `sec.gov/edgar`
- ProPublica Nonprofit Explorer: `projects.propublica.org/nonprofits`

### Category 2: JavaScript SPA (browser required) ⚠️
- PA PALS (`pals.pa.gov`): License verification. CAPTCHA + SPA.
- SAM.gov (`sam.gov`): Entity registration. JavaScript-heavy.
- HHS TAGGS (`taggs.hhs.gov`): Grant/PRF tracking. JavaScript-heavy.
- PA Campaign Finance (`campaignfinanceonline.pa.gov`): Imperva CAPTCHA.

### Category 3: CAPTCHA-Gated (manual browser only) ❌
- PA UJS Portal (`ujsportal.pacourts.us`): Court records
- Berks County Property Records (`berks.pa.publicsearch.us`): Deed search
- IRS TEOS API (`apps.irs.gov`): Akamai WAF blocks residential IPs

### Category 4: Structurally Inaccessible (legal compulsion only) 🚫
- Schedule B via IRS e-file: structurally redacted (not cosmetic)
- Schedule J: not in ProPublica e-files
- PA BCO-10: 404 on EIN search
- BrokerCheck detailed API: HTTP 403 Forbidden

## Evidence Location Template

For every gap, document:

```
GAP #[N]: [Title]

PRIMARY PATH:
  Where: [URL / portal / email]
  What to type: [exact search terms]
  What to request: [specific document or data point]

SECONDARY PATH:
  Where: [fallback if primary fails]
  What to do: [alternative approach]

TERTIARY PATH:
  Where: [if all else fails]
  What to do: [legal compulsion, subpoena, insider access]

BLOCKED PATHS ATTEMPTED:
  - [method]: [reason blocked]
  - [method]: [reason blocked]

STATUS: [OPEN / PARTIAL / ADVANCED / RESOLVED / BLOCKED]
```

## Contact Directory Pattern

Every investigation document should include a verified contact directory:

| Target | Method | Address / URL / Email / Phone |
|--------|--------|------------------------------|
| Org CEO | Email | `ceo@target.org` |
| Org CFO | Email | `cfo@target.org` |
| Auditor | Email/Phone | `auditor@firm.com` · (555) 555-5555 |
| State licensing agency | Email/Phone | `licensing@state.gov` |

**Key rule:** Verify emails before using them. SMTP verification confirms mailbox existence without sending a message.

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| List a gap without a specific lookup instruction | Every gap must have: URL/portal, search terms, expected output |
| Say "request this" without specifying WHERE to send the request | Include: email address, URL, form number, phone number |
| Send § 6104(d) requests to hostile targets without routing strategy | Route through a regulatory agency or third party |
| Give up after one blocked portal | Document ALL paths attempted: curl, browser, API, mirror sites, OSINT |
| Mark a gap "RESOLVED" without citing the evidence source | Every resolved gap must cite: data source, retrieval date, limitation caveats |
| Rely on web search for JavaScript portals | Recognize that JS SPAs are invisible to search engines — manual browser or API only |

## Related Skills
- `investigation-990-forensics` — 990 data that drives gap discovery
- `investigation-osint` — OSINT techniques for finding what portals hide
- `investigation-legal-referral` — Using gathered evidence in legal complaints
