---
name: investigation-990-forensics
description: Nonprofit Form 990 forensic analysis — Schedule D investment tracking, Schedule L related-party detection, CFO/CEO compensation inversion, single-program reporting, contribution anomaly detection, multi-year z-score analysis. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-08-01
---

# Investigation: 990 Forensics

## Core Data Sources

| Source | URL | What You Get |
|--------|-----|-------------|
| **ProPublica Nonprofit Explorer** | `projects.propublica.org/nonprofits/organizations/{EIN}` | Full 990 e-files (PDF), 9+ years of filings, all schedules |
| **IRS TEOS** | `apps.irs.gov/app/eos` | 501(c)(3) status, revocation history, ruling year |
| **GuideStar/Candid** | `guidestar.org` | 990 filings, nonprofit profiles (some paywalled) |
| **USASpending.gov** | `usaspending.gov` | Federal grant data, obligated vs. outlaid amounts |
| **IRS FOIA Form 4506-A** | `irs.gov/pub/irs-pdf/f4506a.pdf` | Unredacted 990 including Schedule B |
| **Schedule O (Narrative)** | ProPublica — included in 990 PDF | Governance narratives: COI policy description, board independence determinations, CEO/CFO compensation methodology, whistleblower policy description |

## Schedule O — Governance Narrative Extraction

Schedule O is the MOST OVERLOOKED 990 schedule. It contains narrative explanations for Part VI governance questions in the org's own words:

- **COI policy description** (Line 12a-c): How the org defines conflicts, who enforces the policy, how compliance is monitored
- **Board independence determinations** (Line 1a-b): How the org determines which board members are "independent"
- **CEO/CFO compensation methodology** (Line 15a-b): How compensation is determined, who reviews it, whether comparability data is used
- **Whistleblower policy** (Line 13): Whether a whistleblower policy exists and how it operates
- **Document retention policy** (Line 14): Whether the org retains documents per Sarbanes-Oxley requirements

**Red flags in Schedule O:**
- Vague boilerplate COI description vs. a specific, enforceable process
- CEO compensation "reviewed by independent board members" — cross-reference against board composition to verify independence
- "All board members are independent" — cross-reference against employer mapping

## Schedule D — Investment Portfolio Forensics

**What to extract:**
- Part I, Line 1: Total non-interest-bearing cash
- Part I, Line 2: Savings and temporary cash investments
- **Part VI/Part VII: Publicly traded securities** — total value, % of total assets
- **Part VIII: Investments in alternative vehicles** (private equity, hedge funds)
- **Part IX: Other assets**
- **Part X: Other liabilities**

**Red flags:**
1. **Schedule D shows $0 real estate but organization operates multiple properties** — ownership vs. leasing undetermined. Cross-reference 990 Part III (programs) + Part IV (balance sheet).
2. **Schedule D shows 100% public securities with no named manager** — 990 does NOT require naming the investment manager. This is a structural opacity. The manager ID lives in audited financial statements, NOT the 990.
3. **Schedule L Part IV (Business Transactions) says ALL-NO while Schedule D shows $10M+ portfolio** — if the investment manager has a board member, this is a related-party disclosure failure.

**Pro tip:** When you can't determine investment manager from the 990, check:
- DOL Form 5500 (`efast.dol.gov` → EIN search) — retirement plan advisor on Schedule C
- SEC EDGAR (`sec.gov/edgar`) — only relevant if org files SEC reports
- EMMA/MSRB (`emma.msrb.org`) — municipal bond disclosures
- FINRA BrokerCheck (`brokercheck.finra.org`) — individual advisor records list firm affiliation
- **Audited financial statements** — the investment manager is typically named in the notes

## Schedule L — Related-Party Transaction Detection

**Schedule L has 4 parts:**
1. **Part I: Excess Benefit Transactions** — disqualified persons receiving excess comp
2. **Part II: Loans to/from Interested Persons** — board/officer loans
3. **Part III: Grants to Interested Persons** — scholarships, grants
4. **Part IV: Business Transactions** — ANY transaction between org and interested person

**Red flags:**
1. **ALL-NO across all 4 parts while board composition suggests conflicts** — cross-reference every board member's employer against Schedule L. If Plageman (Edward Jones) is on the board and Edward Jones manages the portfolio, Part IV should show "YES" with details.
2. **Treasurer owns a consulting firm (Robinson & Associates LLC) and Schedule L says ALL-NO** — all payments to the firm must be disclosed, including $0 transactions if they existed.
3. **Part I incomplete while CFO comp exceeds CEO** — excess benefit transactions under IRC § 4958 require disclosure if compensation exceeds fair market value.

**Investigation pattern:**
```
1. Identify every board member's employer (LinkedIn, web search, FINRA, PALS)
2. Map each employer to potential business relationships with the org
3. Cross-reference against Schedule L disclosures
4. Flag every gap where a potential relationship exists but no disclosure
```

## Compensation Forensics

**990 Part VII — Officer/Director Compensation:**
- Extract CEO and CFO compensation across ALL available years
- Calculate: base salary, other compensation, total, and year-over-year growth
- Flag: CFO total > CEO total (inversion), any officer with >3x growth in <5 years

**"Other Compensation" line demands scrutiny:**
- Request Schedule J (Compensation Information) — contains narrative explaining "other compensation"
- Schedule J is NOT in ProPublica e-files — must be requested from the org under IRC § 6104(d)
- "Other compensation" exceeding 3x another officer's is a red flag requiring explanation

**Multi-year compensation pattern:**
```
FY2019→FY2025 CFO compensation growth: $6,370 → $149,792 = 23.4x
CEO growth: $61,019 → $145,432 = 2.4x
→ The CFO growth is anomalous. Why?
```

## Single-Program Reporting Detection

**990 Part III — Statement of Program Service Accomplishments:**
- Organizations must report 3 largest program services (Line 4a, 4b, 4c)
- Legitimate nonprofits break out services: "Mental Health Services," "SUD Treatment," "Crisis Services"
- **Red flag:** ALL program expenses ($11.68M) reported under ONE line with a single vague description

This is technically compliant but structurally opaque — it prevents any analysis of per-service spending efficiency. Request detailed program budget from the org or from the state licensing agency (for CCBHCs, DDAP requires service-line budgets).

## Contribution Anomaly Detection

**990 Part VIII, Line 1 — Contributions:**
- Track year-over-year: $844,835 → $640,502 (−$204,333, −24.2%) is a red flag
- Investigate: did a major grant expire? Did a scandal cause donor flight? Is it a timing difference?
- Cross-reference with grant databases (USASpending, HigherGov, foundation annual reports)

## Z-Score / Anomaly Detection

**Multi-year metrics to compute as z-scores (using org's own mean as baseline):**
1. Revenue growth rate
2. Program expense ratio (program expenses / total expenses)
3. Administrative expense ratio
4. Fundraising efficiency
5. Investment income as % of total revenue
6. Cash reserves (cash / monthly expenses)

**Red flag:** Any metric exceeding 2.5 standard deviations from the org's own 5+ year mean. For BCC, the 23.4x CFO compensation growth and −$797K FY2025 deficit both exceed this threshold.

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| Accept Schedule L ALL-NO at face value when board composition suggests conflicts | Cross-reference every board member employer against potential business with the org |
| Assume 990 Schedule D names the investment manager | Request audited financial statements — the manager is in the notes |
| Trust "single program" reporting as adequate disclosure | Request service-line budget breakdown from org or licensing agency |
| Assume Schedule B is recoverable from e-filed 990s | Recognize structural redaction (IRS XML policy) vs. cosmetic redaction (paper PDFs) |
| Analyze one year in isolation | Compute multi-year z-scores using the org's own historical mean |

## Schedule B Structural vs. Cosmetic Redaction

**Critical distinction learned from the BCC investigation:**
- **E-filed 990s:** Schedule B is structurally excluded from the public XML by IRS policy. No black rectangles. No hidden text. Unrecoverable without FOIA.
- **Paper-filed 990s:** Schedule B has cosmetic black-box redaction. PDF parsers CAN sometimes recover underlying text. The "pdf-parser unredaction" technique ONLY works on paper-filed returns.
- Before attempting redaction recovery, check ProPublica for the filing method — if the 990 PDF was generated from IRS XML (not a paper scan), Schedule B is structurally gone.

## Key IRC Sections for 990 Forensics

| Section | Purpose |
|---------|---------|
| IRC § 6104(d)(1)(A) | Mandatory public disclosure — org MUST provide 990 + exemption application on request |
| IRC § 6104(d)(1)(B) | 30-day deadline for providing requested documents |
| IRC § 4958 | Excess benefit transactions — 25% initial tax, 200% second-tier |
| IRC § 7206 | Fraudulent return — personal criminal exposure for CFO/CEO signers |
| IRC § 6662/6663 | Accuracy-related penalty (20%) / fraud penalty (75%) |

## Related Skills
- `investigation-board-governance` — Board composition, COI detection, hidden network mapping
- `investigation-legal-referral` — Translating 990 findings into IRS/AG complaints
- `investigation-osint` — Finding board member employers and professional histories
