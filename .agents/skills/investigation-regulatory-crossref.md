# investigation-regulatory-crossref.md
## Multi-Agency Regulatory Cross-Referencing — FINRA, IRS, HUD, SAMHSA, State Ethics, Charitable Trusts

**Created:** August 1, 2026 — distilled from BCC investigation (6 regulatory agencies, 5 complaint channels)

---

### Agency-by-Agency Cross-Reference Protocol

When investigating a nonprofit with employee/officer conflicts, cross-reference each person against ALL applicable regulatory databases. A single clean record in one agency does not mean clean across all.

---

#### 1. FINRA (Financial Industry Regulatory Authority)
- **Database:** brokercheck.finra.org
- **When to check:** Any person whose employer is a brokerage, investment advisory, or financial services firm
- **What to extract:**
  - CRD number (unique identifier)
  - Current employer, branch address, registration dates
  - **ALL 6 disclosure categories:** Customer disputes, Regulatory actions, Employment separations, Criminal, Civil judicial, Financial (liens/bankruptcies/judgments)
  - **Outside Business Activities (OBA):** Critical — if person serves on a nonprofit board, this MUST appear on CRD under Rule 3270
  - State registrations (how many states, all active?)
  - Exam history (Series 7, 66, SIE — what level?)
- **Red flags:**
  - **ZERO OBAs when person chairs a nonprofit board** → Rule 3270 violation → FINRA Regulatory Tip
  - **Any disclosure in any category** → pull full report
  - **No principal-level exams** but managing institutional money → competency question
- **Filing:** FINRA Regulatory Tip at finra.org/investors/need-help/file-a-complaint citing FINRA Rules 2010 and 3270

#### 2. IRS (Internal Revenue Service)
- **Databases:**
  - ProPublica Nonprofit Explorer (public 990 access)
  - IRS Tax Exempt Organization Search (apps.irs.gov/app/eos)
  - IRS Form 4506-A (request copies of filed 990s)
- **Key 990 sections to cross-reference:**
  - **Part VII (Compensation):** Cross-ref board members' employer affiliations against Part VII
  - **Schedule D (Investments):** Cross-ref portfolio manager against board member employers
  - **Schedule L (Related-Party Transactions):** Cross-ref ALL-NO answers against known board employer-vendor relationships
  - **Schedule J (Compensation Methodology):** If not public → request under §6104(d)
  - **Part VI (Governance):** Line 12a (COI policy exists?), Line 12b (annual disclosures?), Line 15 (board reviewed 990?)
- **Filing options:**
  - **Form 211 (Whistleblower):** For tax violations — confidential under §6103. 15-30% award under §7623(b) if $2M+ collected. Mail to Ogden UT.
  - **Form 3949-A (Information Referral):** For non-award referrals. Can be anonymous.
  - **IRS TE/GE Referrals:** eoclass@irs.gov for 990 fraud / private inurement

#### 3. HUD (Housing & Urban Development)
- **Databases:**
  - HUD CoC grant records (hudexchange.info)
  - HUD REAC inspection scores (physical property inspections)
  - HUD environmental review records
- **When to check:** Any nonprofit operating supportive housing with HUD Continuum of Care funding
- **Key cross-references:**
  - **CoC grants vs. board vendor conflicts:** If a board member sells furniture and the nonprofit has 8 HUD properties with furniture as eligible cost (24 CFR §578.55(b)(6)) → undisclosed procurement risk
  - **Property ownership vs. leasing:** Cross-ref BCC's property records against HUD CoC grant addresses
- **Filing:** HUD OIG Hotline — hotline@hudoig.gov, (800) 347-3735
- **FOIA:** HUD FOIA request (5 U.S.C. §552) for REAC inspection scores and CoC monitoring records on specific properties

#### 4. SAMHSA (Substance Abuse & Mental Health Services Administration)
- **Databases:**
  - SAMHSA grant awards (samhsa.gov/grants)
  - TAGGS (HHS Tracking Accountability in Government Grants System)
- **When to check:** Any nonprofit receiving CCBHC or other SAMHSA grant funding
- **Key cross-references:**
  - **Grant award date → regime change boundary:** The award date cleanly divides financial behavior into pre/post
  - **Grant purpose vs. 990 program service reporting:** If 990 reports all $11.68M under ONE program line, cannot verify grant-authorized purposes
  - **Grant expiration → fiscal cliff:** Sept 2027 expiry of $3.94M grant with no visible diversification plan
- **Filing:** SAMHSA FOIA — SAMHSAFOIA@samhsa.hhs.gov; HHS OIG Hotline — (800) HHS-TIPS

#### 5. PA Attorney General — Charitable Trusts & Organizations Section
- **Jurisdiction:** 15 Pa.C.S. Ch. 55 (Nonprofit Corporations); common law charitable trust oversight
- **Database:** PA AG charities registry (not all filings public)
- **When to file:** Any governance conflict, self-dealing pattern, or board transparency failure
- **Key legal theories:**
  - **15 Pa.C.S. §5508(b):** Fiduciary duty of loyalty — board members must act in best interest of the nonprofit, not their employer
  - **15 Pa.C.S. §5712:** Breach of fiduciary duty
  - **Charitable trust doctrine:** PA AG has parens patriae authority over charitable assets
- **Filing:** info@attorneygeneral.gov, (717) 783-2853 — Charitable Trusts & Organizations Section

#### 6. PA Ethics Commission
- **Statute:** 65 Pa.C.S. §1103 (Public Official & Employee Ethics Act)
- **When to file:** When an elected official or public employee has a conflict of interest with a nonprofit they oversee
- **Key cross-reference:** City Council member employed by organization that funds nonprofit the Council oversees → §1103 conflict
- **Filing:** ethics.pa.gov — complaint form

#### 7. PA Bureau of Charitable Organizations
- **Database:** PA Dept of State — charitable organization registration
- **When to check:** All PA-registered charities
- **Key cross-reference:** Cross-ref filed registration against 990 — do they match?
- **Contact:** ST-CHARITIES@pa.gov, (717) 783-1720

---

### Cross-Reference Matrix Template

For each regulatory action, document:

```
PERSON: [Name]
EMPLOYER: [Confirmed employer]
CONFLICT: [Description of conflict type]

REGULATORY CROSS-REFERENCES:
  FINRA: [CRD # / Rule 3270 OBA check / disclosure check] → STATUS: [Clean/Flagged]
  IRS: [Sch. L exposure / §4958 risk / §501(c)(3) inurement] → STATUS: [Risk Level]
  HUD: [CoC grant nexus / procurement risk] → STATUS: [Risk Level]
  SAMHSA: [Grant award / program reporting] → STATUS: [Risk Level]
  PA AG Charities: [Fiduciary duty / self-dealing] → STATUS: [Risk Level]
  PA Ethics: [§1103 conflict] → STATUS: [Risk Level]

DOLLAR AMOUNT AT STAKE: $[amount]
FILING STATUS: [Ready/Not Ready] — [Filing type]
```

---

### Regulatory Filing Priority Order

1. **IRS Form 211** (confidential — file first, no tipping off)
2. **FINRA Regulatory Tip** (confidential — file second)
3. **HHS OIG Hotline** (federal grant fraud — file with IRS)
4. **PA AG Charitable Trusts** (state fiduciary — file after federal filings)
5. **PA Ethics Commission** (public official conflict — file when ready for public disclosure)
6. **Public Complaint Broadcast** (46 recipients — file LAST, after qui tam counsel clearance)

---

### Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| **Filing public complaint before qui tam** | IRS Form 211 and FINRA tip are CONFIDENTIAL and don't trigger FCA public disclosure bar (§3730(e)(4)). But public complaint broadcast DOES. Coordinate with qui tam counsel. |
| **One agency clean = no problem** | FINRA clean doesn't mean IRS clean doesn't mean HUD clean. Cross-reference ALL agencies independently. |
| **Schedule L ALL-NO accepted at face value** | Cross-ref every board member's employer against potential vendor/funder relationships. The ALL-NO is the claim to be tested, not the ground truth. |
| **Not checking outside business activities on CRD** | ZERO OBAs when person has known outside roles = Rule 3270 violation. This is independently actionable even if all other agencies are clean. |
| **Ignoring fiscal year boundaries** | A board member joining in Aug 2025 falls in FY2026 (if FY ends June 30). Their Schedule L exposure begins FY2026, not FY2025. Verify fiscal year dates. |
