---
name: investigation-legal-referral
description: Legal referral construction — FCA qui tam packaging, IRS fraud referral (Forms 13909, 211, 3949-A), PA Ethics Act complaints, multi-agency submission strategies, evidence anchoring patterns. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-08-01
---

# Investigation: Legal Referral Construction

## Multi-Agency Complaint Architecture

When investigating a nonprofit with regulatory violations, the evidence typically maps to multiple agencies. Package them into a unified referral memo.

### Agency-to-Theory Mapping

| Agency | Theory | Statutes | Evidence Needed |
|--------|--------|----------|----------------|
| **U.S. Attorney's Office (EDPA)** | FCA qui tam | 31 U.S.C. §§ 3729-3733 | False claims for federal funds, materiality, scienter |
| **HHS OIG Hotline** | Health care fraud | 18 U.S.C. § 1347; FCA | Medicaid billing fraud, CCBHC compliance failures |
| **IRS TE/GE Referrals** | 990 fraud / excess benefit | IRC §§ 7206, 4958, 6662, 6663 | False Schedule L/D, undisclosed compensation |
| **IRS Whistleblower Office** | Tax fraud bounty | IRC § 7623(b) | 15-30% of collected proceeds ($2M+ threshold) |
| **PA AG Charitable Trusts** | Breach of fiduciary duty | 71 P.S. § 732-204; 15 Pa.C.S. § 5712 | COI violations, board self-dealing, diversion of assets |
| **PA Ethics Commission** | Public official conflict | 65 Pa.C.S. §§ 1103, 1104 | Failure to recuse, failure to file disclosures |
| **PA DDAP** | Licensing violations | 55 Pa. Code § 1223.52 | Patient care deficiencies, documentation failures |
| **FINRA Enforcement** | Broker misconduct | FINRA Rules 2010, 3270 | Undisclosed outside business activities |

## IRS Fraud Referral — Complete Package

### Form 13909 (Tax-Exempt Organization Complaint)
- **Purpose:** Report tax-exempt organization noncompliance
- **Submit to:** `eoclass@irs.gov` OR mail to: TEGE Referrals Group, 1100 Commerce Street, MC 4910 DAL, Dallas TX 75242
- **Covers:** Private inurement, excess benefit, political activity, non-exempt purpose

### Form 211 (Application for Award for Original Information)
- **Purpose:** IRS whistleblower claim (bounty program)
- **Threshold:** $2,000,000+ in dispute for mandatory 15-30% award (§ 7623(b))
- **Confidentiality:** IRC § 6103 protects whistleblower identity
- **Warning:** This is SEPARATE from Form 13909 — both can be filed

### Form 3949-A (Information Referral)
- **Purpose:** General tax fraud referral (no bounty)
- **Covers:** False returns, failure to pay tax, unreported income

### IRS Key Statutes

| Statute | What It Covers | Penalty |
|---------|---------------|---------|
| **IRC § 7206** | Fraudulent return (felony) — false statements on 990 under penalties of perjury | $500K fine (corp) + 3 yrs imprisonment |
| **IRC § 4958** | Excess benefit transactions — 25% initial tax on disqualified person, 200% if uncorrected | 10% org manager tax (up to $20K/transaction) |
| **IRC § 501(c)(3)** | Revocation grounds — private inurement, private benefit, excess benefit | Loss of tax-exempt status |
| **IRC § 6662** | Accuracy-related penalty (20%) | 20% of underpayment |
| **IRC § 6663** | Civil fraud penalty (75%) | 75% of underpayment attributable to fraud |
| **IRC § 7623(b)** | Whistleblower bounty (15-30%) | Mandatory if $2M+ collected |
| **IRC § 6501(a)** | Assessment SOL: 6 years | Extended for fraud (no limit per § 6501(c)(1)) |
| **IRC § 6531(2)-(5)** | Criminal tax SOL: 6 years | From date of filing |

## FCA Qui Tam — Essential Elements

### 31 U.S.C. § 3729(a)(1) — False Claims
Seven theories of liability:
- **(A)** Knowingly presenting a false claim for payment
- **(B)** Knowingly making a false record material to a false claim
- **(C)** Conspiracy to defraud
- **(D)** Conversion of government property
- **(G)** Reverse false claim (avoiding obligation to pay government)

### Relator Requirements
1. **First-to-file bar:** 31 U.S.C. § 3730(b)(5) — ABSOLUTE and jurisdictional. First relator wins.
2. **Public disclosure bar:** 31 U.S.C. § 3730(e)(4) — if substantially the same allegations were publicly disclosed, relator must be "original source"
3. **Filed under seal:** Complaint filed in camera, served on government only. 60-day seal (extendable).
4. **Government intervention:** DOJ may intervene (intervened cases have 95%+ success rate)
5. **Relator share:** 15-25% if government intervenes; 25-30% if relator proceeds alone

### Evidence required for FCA complaint
1. **False claim:** Specific grant/contract number, specific billing, specific date
2. **Falsity:** What was false — missing signatures, undocumented services, inflated costs
3. **Materiality:** Why it mattered — condition of payment, compliance requirement
4. **Scienter:** Knowledge — actual knowledge, deliberate ignorance, or reckless disregard
5. **Damages:** Federal funds paid — exact amounts, dates, programs

### Public Disclosure Bar — CRITICAL
**DO NOT:**
- Blog, tweet, or post about the allegations
- File regulatory complaints (FINRA, IRS, AG) before the qui tam is under seal
- Discuss with reporters
- Post on Moltbook or any social platform

Any of these can trigger the public disclosure bar and kill the qui tam. All regulatory complaints must be coordinated with qui tam counsel.

## PA Ethics Act Complaint (65 Pa.C.S. § 1103)

### Elements
1. **Public official:** City council member, county commissioner, state employee
2. **Financial interest:** Direct or indirect (including employer's interest)
3. **Official action:** Vote, contract award, budget allocation
4. **Failure to recuse:** No public disclosure or abstention

### Filing
- PA State Ethics Commission: `ethics.pa.gov` → File a Complaint
- City/County ethics boards: Check local charter for complaint process (Reading has Board of Ethics per City Charter § 1201)

## Evidence Citation Pattern

Every legal claim must anchor to specific evidence:

```
<strong>VIOLATION 1: [Title]</strong>
<span class="cite">Source: [Document Name], [Section], [Date Retrieved]</span>
Elements satisfied:
  (a) [Element 1]: [Fact with citation]
  (b) [Element 2]: [Fact with citation]
```

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| File regulatory complaints before qui tam seal | Coordinate ALL filings with qui tam counsel |
| Cite legal theories without statutory elements | Every theory must list: statute, elements, facts-per-element |
| File IRS Forms 13909 + 211 simultaneously to same office | Form 211 goes to Whistleblower Office; Form 13909 goes to TE/GE — separate channels |
| Send § 6104(d) request directly when qui tam is planned | Route through third party — the request letter IS a public disclosure risk |
| Assume public disclosure bar won't apply | Consult qui tam counsel before ANY public communication |

## Related Skills
- `investigation-990-forensics` — 990 violations that feed IRS/AG complaints
- `investigation-board-governance` — Board-level violations that feed fiduciary duty claims
- `investigation-regulatory-licenses` — License revocation grounds that accompany legal theories
