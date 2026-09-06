# BCC_SERVICES_VULNERABILITIES.md -- Berks County Court Full Disclosure

> **Purpose:** Complete disclosure of Berks County Court of Common Pleas (Reading, PA)
> services, abilities, and vulnerabilities -- compiled from extensive web research of official sources.
> **Created:** July 9, 2026 (Session 6-7) — Initial compilation + second-round targeted deep-dive
> **Scope:** 23rd Judicial District -- 633 Court Street, Reading, PA 19601. All civil, family,
> orphans, criminal, domestic relations, and landlord-tenant divisions. Prothonotary, Court
> Administration, UJS portal, statewide infrastructure, and Magisterial District Court.
> **Template:** Modeled after DISCLOSURE_WHITEPAPER_TODO.md section structure.
> **Research Sources:** berkspa.gov, pacourts.us, ujsportal.pacourts.us, prothy.countyofberks.com,
> palawhelp.org, palegalaid.net, Pennsylvania Bulletin.
> **Key Date:** August 1, 2026 — Pro se e-filing **UNCONFIRMED** (researcher found NO official source for this date; may be rumor or from another jurisdiction). Verify with Prothonotary at 610-478-6970 before relying.
> **Vulnerabilities:** 15 total (3 HIGH, 9 MEDIUM, 3 LOW)
> **Automation Opportunities:** 13 (D1-D13)

---

## State Snapshot (July 9, 2026)

| Metric | Value | Notes |
|--------|-------|-------|
| **Court** | Berks County Court of Common Pleas | 23rd Judicial District |
| **Address** | 633 Court Street, 2nd Floor, Reading, PA 19601 | Courthouse |
| **Prothonotary** | Jonathan K. Del Collo | Elected position |
| **Prothonotary Phone** | 610-478-6970 | Civil, family, judgments, liens |
| **Prothonotary Hours** | M-F 8:00 AM -- 4:00 PM | Closed federal holidays, Good Friday, Election Day, day after Thanksgiving |
| **Court Admin Phone** | 610-478-6208 | Scheduling, forms, jury |
| **Orphans Court Phone** | 610-478-6600 | Register of Wills/Clerk |
| **E-filing (current)** | Attorneys only | Civil Electronic Filing System (NOT PACFile) |
| **E-filing (pro se)** | **UNCONFIRMED** (rumored Aug 1, 2026) | No official source found for this date; verify with Prothonotary |
| **PACFile integration** | NO | Berks uses independent county system |
| **UJS Portal** | ujsportal.pacourts.us | Docket search only (no e-filing for Berks civil) |
| **Legal Aid** | Mid-Penn Legal Services: 1-800-326-9177 | Free/reduced legal representation |
| **Bar Referral** | Berks County Bar Association: 610-375-4591 | Attorney referral service |
| **Interpreter Services** | interpreter@berkspa.gov | Free, LEP + deaf/HoH |
| **Libra project coverage** | Partial | Fee schedule + court info in data layer; no jurisdiction code yet |

---

## TABLE OF CONTENTS

1. [SECTION A: Services](#section-a-services) — Prothonotary, Court Admin, Self-Help, IFP, Language, Payment, MDJ Districts (A7), Domestic Relations (A8)
2. [SECTION B: Abilities](#section-b-abilities) — Case Types, Filing Methods, Filing Requirements (B2-A), UJS Technical (B3-A), UJS Portal (B3), Hearings, Judicial
3. [SECTION C: Vulnerabilities](#section-c-vulnerabilities) — 15-item catalog + severity summary + county comparison
4. [SECTION D: Libra Automation Opportunities](#section-d-libra-automation-opportunities) — 13 opportunities (D1-D13) + cross-reference
5. [SECTION E: Key Contacts & Resources](#section-e-key-contacts--resources)
6. [SECTION F: Regulatory Timeline](#section-f-regulatory-timeline)

## SECTION A: Services

### A1 -- Prothonotary Office Services

| Service | Detail | Public Access | Online? |
|---------|--------|--------------|---------|
| **Civil filings** | Complaints, motions, appeals, equity actions | Yes -- in person or by mail | Partial (attorney e-filing only; pro se date unconfirmed) |
| **Family court filings** | Divorce, custody, PFA | Yes | Partial |
| **Judgment docketing** | Federal, state, local, municipal liens | Yes | Yes (docket search) |
| **Arbitration filings** | Civil arbitration cases | Yes | No |
| **License suspension appeals** | PennDOT appeals | Yes | No |
| **Docket access** | Public dockets 1996--present | Yes | Yes (prothy.countyofberks.com/cms/) |
| **Certified copies** | In person or by mail (fee + SASE) | Yes | Request form online |
| **Historical records** | Genealogical and archival records | Yes | No |
| **Passport services** | **PERMANENTLY DISCONTINUED** (2025) | N/A | N/A |
| **Notary services** | Not available on-site | No | No |
| **Copy/scanning services** | Public copy machine available; staff cannot assist | Yes (self-service) | No |

### A2 -- Court Administration Services

| Service | Detail |
|---------|--------|
| **Daily schedules** | Published online -- judges, times, courtrooms for criminal and civil |
| **Forms distribution** | Court forms available on berkspa.gov and in person |
| **Jury management** | Jury duty administration and summons |
| **Interpreter services** | Free for LEP and deaf/hard-of-hearing; request form to interpreter@berkspa.gov |
| **ADA accommodations** | Reasonable disability accommodations; advance request through Court Administration |
| **Civil Argument Court** | 1st and 3rd Monday each month -- preliminary objections, summary judgment, motions to compel |

### A3 -- Self-Help & Pro Se Resources

| Resource | Detail | Limitations |
|----------|--------|-------------|
| **Self-help custody/divorce page** | berkspa.gov -- forms, procedures, service instructions | No legal advice |
| **Statewide forms** | pacourts.us/learn/representing-yourself | Generic PA forms (not Berks-specific) |
| **Law Library** | Legal research materials available | Staff CANNOT give legal advice |
| **IFP forms** | Separate IFP forms for civil and family matters | Financial disclosure required |
| **Mid-Penn Legal Services** | 1-800-326-9177 | Income-qualified only |
| **Bar Association referral** | 610-375-4591 | Paid attorney referral |

**Critical note:** Court staff, Prothonotary staff, and Law Library staff are STRICTLY PROHIBITED from giving legal advice, assisting with form completion, or recommending which documents to file. Pro se litigants are held to the SAME standards as licensed attorneys.

### A4 -- IFP (In Forma Pauperis) Process

| Aspect | Detail |
|--------|--------|
| **Statutory basis** | Pa.R.C.P. 240 |
| **Forms** | Separate IFP forms for civil matters and family court matters |
| **Requirements** | Full financial disclosure: income, assets, expenses, dependents |
| **Filing method** | Paper only -- submit to Prothonotary with complaint/petition |
| **Review** | Judicial determination based on financial need |
| **Effect** | Waives all filing fees and costs if approved |
| **Common rejection reasons** | Incomplete financial disclosure, insufficient documentation, court finds applicant has sufficient resources |
| **If rejected** | Must pay filing fee to proceed; can re-apply with corrected information |
| **Attorney certification** | If represented by free legal services, attorney can certify financial status (no full petition needed) |

### A5 -- Language Access & ADA

| Service | Detail |
|---------|--------|
| **LEP interpreter** | Free interpreter services for Limited English Proficiency |
| **Deaf/HoH interpreter** | Free sign language interpretation |
| **Request process** | Submit Language Access Request Form to interpreter@berkspa.gov |
| **ADA accommodations** | Advance request through Court Administration |

### A6 -- Payment & Filing Logistics

| Aspect | Detail |
|--------|--------|
| **Filing by mail** | Accepted for civil, custody, divorce; include cover letter, fees, SASE for return copy |
| **Drop box** | **UNCERTAIN** -- must call 610-478-6970 to confirm availability for legal filings |
| **Payment methods** | Call to verify accepted forms (check, money order, credit/debit vary by transaction) |
| **Returned check fee** | $50.00 (recently added) |
| **Recent fee increase** | Act 45 of 2025 — JCP/ATJ/CJEA surcharge increased from $40.25 to $41.25 (+$1.00) |
| **Fee schedule source** | "Fee Bill effective 1/1/2026" PDF at berkspa.gov/departments/prothonotary |
| **Sheriff service fees** | Separate fee schedule at berkspa.gov/departments/sheriff (610-478-6240); varies by service type |

### A7 -- Magisterial District Courts (Reading Area)

| District | Judge | Address | Phone |
|----------|-------|---------|-------|
| **23-1-01** | Carissa L. Johnson | 1150 Muhlenberg St, Reading, PA 19602 | 610-374-9288 |
| **23-1-02** | Kyley L. Scott | 633 Court St, 3rd Floor, Reading, PA 19601 | 610-378-5101 |
| **23-1-03** | Alvin B. Robinson | 633 Court St, Reading, PA 19601 | 610-373-2127 |
| **23-1-05** | Colleen Dugan Schearer | 3200 Reading Crest Ave, Reading, PA 19605 | 610-929-4440 |
| **23-1-06** | Priscilla Campos | 441 Morgantown Rd, Reading, PA 19611 | 610-375-7101 |
| **23-3-07** | Tonya A. Butler | 2312 Fairmont Ave, Suite 500, Reading, PA 19605 | 610-373-4424 |

**Key MDJ Facts:**
- **Small claims limit:** $12,000 (excludes court costs and interest)
- **Filing fees:** $60-$130+ (varies by claim amount, defendant count, service method — call specific MDJ)
- **Appeal to Common Pleas:** 30-day deadline, de novo (case restarts from scratch)
- **2026 redistricting:** West Reading/Wyomissing MDJ seat proposed for dissolution, areas redistributed to neighboring districts (pending PA Supreme Court approval)
- **Forms:** Standard UJS forms — Civil Complaint, Landlord-Tenant Complaint, IFP Affidavit
- **Service:** Typically via certified mail or constable (arranged by court)

### A8 -- Domestic Relations Section (DRS)

| Aspect | Detail |
|--------|--------|
| **Address** | Berks County Services Center, 6th Floor, 633 Court Street, Reading, PA 19601 |
| **Phone** | 610-478-2900 |
| **Fax** | 610-478-6583 |
| **Hours** | M-F 8:00 AM – 4:30 PM (in-person support filing until 3:30 PM) |
| **Services** | Child support establishment/modification/enforcement, spousal support/alimony pendente lite, paternity establishment, medical support orders, payment collection/disbursement |
| **Filing fee** | **None** (no filing fee to open a support case) |
| **Process** | Conference-first model with Conference Officer → if no agreement, recommendation issued → hearing before Hearing Officer or Judge if disputed |
| **System** | PACSES (Pennsylvania Automated Child Support Enforcement System) |
| **Online filing** | PA Child Support e-services portal (childsupport.state.pa.us) |
| **Oversight** | PA Department of Human Services / Bureau of Child Support Enforcement sets statewide policy; Berks DRS handles local case management |

---

## SECTION B: Abilities

### B1 -- Case Types Handled

| Division | Case Types | Clerk Office |
|----------|-----------|-------------|
| **Civil** | Complaints, equity actions, contract disputes, torts, declaratory judgments | Prothonotary |
| **Family** | Divorce, custody, Protection From Abuse (PFA) | Prothonotary |
| **Orphans Court** | Estates, guardianships, adoptions, trust audits, will probate appeals | Register of Wills/Clerk of Orphans Court |
| **Criminal** | Felonies, misdemeanors, summary appeals | Clerk of Courts |
| **Landlord-Tenant** | Evictions, landlord-tenant complaints | Prothonotary / Magisterial District Court |
| **Expungement / Sealing** | Criminal record sealing, summary offense expungement | Clerk of Courts |
| **Domestic Relations** | Child support, spousal support, paternity | Domestic Relations Office |
| **Judgments/Liens** | Federal, state, local, municipal tax liens, arbitrations | Prothonotary |
| **Appeals** | License suspension appeals, appeals to Superior/Commonwealth Court | Prothonotary |

### B2 -- Filing Methods

| Method | Available To | Details |
|--------|-------------|---------|
| **In-person filing** | All litigants | 2nd Floor, 633 Court Street, M-F 8AM-4PM |
| **Mail filing** | All litigants | Include cover letter, fees, SASE for return copy |
| **E-filing (county system)** | **Attorneys only** | Civil Electronic Filing System at prothy.countyofberks.com/efs/ |
| **E-filing (pro se)** | **UNCONFIRMED** (rumored Aug 1, 2026) | No official source; verify with Prothonotary |
| **PACFile** | NOT available for Berks civil | Berks uses independent county system, not statewide PACFile |
| **Orphans Court** | Paper only | No e-filing; original signatures required (blue ink recommended); do not staple |
| **Magisterial District Court** | Paper + in-person | Small claims up to $12,000; landlord-tenant; traffic; summary offenses |

### B2-A -- Additional Filing Requirements

| Requirement | Rule | Detail |
|-------------|------|--------|
| **Civil cover sheet** | BCR 205.4 | Required for all civil filings; includes case type, parties, counsel info |
| **Confidential information form** | Pa.R.C.P. 205.5 | Required if filing contains SSNs, financial account numbers, minor names |
| **Sheriff service** | Pa.R.C.P. 400 | Sheriff's office handles service of process; separate fees apply |
| **Certificate of service** | BCR 440 | Required for all motions, petitions, discovery; proof of service on all parties |

### B3-A -- UJS Portal Technical Architecture

| Aspect | Detail |
|--------|--------|
| **Search parameters** | Docket number, participant name, OTN, citation number, filing date range, police incident number, SID |
| **Data returned** | Party names, case status, filing dates, judge assignments, docket entries, financial info (costs, fines, payments), court calendars |
| **Public API** | **None** — no public-facing API for automated data extraction |
| **Automated access** | **BLOCKED** — CAPTCHA (reCAPTCHA) + IP rate-limiting prevent scraping |
| **Document PDFs** | Available for most public filings (criminal complaints, orders, dockets); sealed/sensitive docs restricted |
| **RSS/Email alerts** | **None** — no built-in alerts for case updates; must manually re-search |
| **Bulk access** | Available for qualified entities (background check companies, researchers) via formal administrative process |
| **Attorney vs public** | Same docket info publicly; attorneys use PACFile for e-filing + sealed document access |
| **Berks County portal** | Separate: prothy.countyofberks.com/cms/ for Berks-specific civil dockets |

### B3 -- UJS Portal Capabilities (Berks County)

| Capability | Available? | Detail |
|-----------|-----------|--------|
| **Docket search** | YES | ujsportal.pacourts.us/CaseSearch -- search by name, docket number |
| **Civil case info** | Limited | Berks civil cases primarily on county portal (prothy.countyofberks.com/cms/), not UJS |
| **Criminal dockets** | YES | Statewide UJS portal |
| **Magisterial District Court** | YES | Statewide UJS portal |
| **Appellate court dockets** | YES | Statewide UJS portal |
| **E-filing for Berks** | NO | Must use county EFS (not UJS) |
| **Public vs attorney** | Same docket info | Attorneys have additional case management features |

### B4 -- Hearing Types & Scheduling

| Hearing Type | Schedule | Notes |
|-------------|----------|-------|
| **Civil Argument Court** | 1st & 3rd Monday each month | Preliminary objections, summary judgment, motions to compel |
| **Daily criminal/civil** | Published online daily | Judges, times, courtrooms listed |
| **Argument Court listing** | Separate docket issued Thursday prior | Must be listed by attorney or party |

### B5 -- Judicial Information

| Aspect | Source |
|--------|--------|
| **Judicial assignments** | berkspa.gov/departments/court-administration/schedules-and-forms |
| **Individual judge schedules** | Published on Court Administration website |
| **Chambers contact** | Through Court Administration (610-478-6208) or Prothonotary (610-478-6970) |

---

## SECTION C: Vulnerabilities

### C1 -- Vulnerability Catalog (15 Items)

| # | Vulnerability | Severity | Detail | Libra Opportunity |
|---|-------------|----------|--------|-------------------|
| **V1** | **Pro se e-filing gap** | HIGH | Self-represented litigants CANNOT e-file. Must file in person or by mail during business hours only. No 24/7 online portal for pro se. **August 1, 2026 date is UNCONFIRMED** — no official source found. | Build pro se e-filing assistant (ready whenever e-filing launches) |
| **V2** | **No PACFile integration** | HIGH | Berks uses independent county EFS, not statewide PACFile. Attorneys who practice across counties must learn multiple systems. No unified filing interface. | Build Berks-specific EFS integration module |
| **V3** | **IFP complexity** | HIGH | Financial disclosure requirements are burdensome for pro se litigants. Common rejections for incompleteness. No automated IFP eligibility checker. No IFP form auto-fill. | Automate IFP petition generation with eligibility pre-check |
| **V4** | **No legal advice from staff** | MEDIUM | Prothonotary, Court Admin, and Law Library staff CANNOT give legal advice. Pro se litigants held to attorney standards with no help. No navigator program. | Build Libra as AI legal document assistant (not advice, but automation) |
| **V5** | **Limited pro se forms** | MEDIUM | Only custody and divorce have self-help pages. Other civil matters lack pro se guidance. Forms are Pennsylvania-generic, not Berks-specific. | Build BCC-specific form templates (motion, IFP, cover sheet) |
| **V6** | **Drop box uncertainty** | MEDIUM | Cannot confirm after-hours drop box availability for legal filings. Must call to verify. No published drop box policy. | Document drop box policy; build filing packet with drop box instructions |
| **V7** | **Paper-only Orphans Court** | MEDIUM | Orphans Court has NO electronic filing. Original signatures required in blue ink. Documents must not be stapled (for scanning). Manual processing bottleneck. | Generate Orphans Court documents (estate, guardianship) with proper formatting |
| **V8** | **Fee burden** | MEDIUM | Recent fee increases (Act 45 of 2025, JCP surcharge). Civil complaint: $225+. Returned check fee: $50. IFP is the only relief, but process is complex. | Calculate fees accurately; auto-generate IFP when eligible |
| **V9** | **County system fragmentation** | LOW | 67 PA counties with different e-filing systems. Berks has its own. No unified statewide civil e-filing. AOPC working toward integration but no timeline. | Design Libra for multi-jurisdiction (Berks + Northampton + Federal) |
| **V10** | **Passport services discontinued** | LOW | Prothonotary no longer processes passports. Minor service gap. | N/A -- not relevant to legal automation |
| **V11** | **No published backlog data** | MEDIUM | Court does not publish case processing times or backlog statistics. Delays are assumed but unquantified. Access-to-justice barrier: litigants cannot plan timelines. | Track filing-to-disposition timelines via UJS docket scraping |
| **V12** | **Service complexity for pro se** | MEDIUM | Pa.R.C.P. 440 governs service of legal papers. Pro se litigants must understand and properly execute service. No automated certificate of service generation on county site. Sheriff fees add cost burden. | Auto-generate Certificates of Service per BCR 440 and Pa.R.C.P. 440 |
| **V13** | **Venue/jurisdiction confusion** | MEDIUM | Pro se litigants often file in wrong court: Common Pleas vs Magisterial District Court (small claims up to $12,000) vs Orphans Court. No online triage tool to route litigants to correct venue. | Build venue-routing wizard based on case type + amount in controversy |
| **V14** | **Confidential info compliance risk** | MEDIUM | Pa.R.C.P. 205.5 requires redaction of SSNs, financial account numbers, minor names from public filings. Pro se litigants often unaware of this requirement. No automated redaction checker. | Build confidential-info form auto-generation and filing redaction scanner |
| **V15** | **No on-site notary or copy services** | LOW | No notary public at the courthouse. Public copy machine available (self-service only). Pro se litigants must arrange notarized verifications elsewhere. | Include notary-check flag in document generator; pre-mark notarization blocks |

### C2 -- Vulnerability Severity Summary

| Severity | Count | Items |
|----------|-------|-------|
| **HIGH** | 3 | V1 (pro se e-filing gap), V2 (no PACFile), V3 (IFP complexity) |
| **MEDIUM** | 9 | V4 (no legal advice), V5 (limited forms), V6 (drop box), V7 (paper Orphans), V8 (fee burden), V11 (no backlog data), V12 (service complexity), V13 (venue confusion), V14 (confidential info) |
| **LOW** | 3 | V9 (fragmentation), V10 (passports), V15 (no notary/copy) |

### C3 -- County Comparison: Berks vs Northampton

| Aspect | Berks County | Northampton County |
|--------|-------------|-------------------|
| **E-filing system** | Independent county EFS | CountySuite |
| **Attorney e-filing** | Mandatory for civil | Encouraged |
| **Pro se e-filing** | **UNCONFIRMED** (rumored Aug 1, 2026) | Available (hybrid) |
| **PACFile** | No | No |
| **IFP process** | Standard UJS form, paper filing | Standard UJS form, mandatory e-filing system |
| **Filing fee** | $225.00 (civil complaint; from fee_schedule.json: berks_county) | $178.25 (pa_courts.json data; Northampton) |
| **Pro se resources** | Custody/divorce self-help pages | Self-help page + forms |
| **Libra coverage** | Partial (fee schedule + court info) | Partial (fee schedule) |

---

## SECTION D: Libra Automation Opportunities

### D1 -- High-Priority (Immediate — Pro Se E-Filing Readiness)

| # | Opportunity | Vulnerability Addressed | Libra Module | Effort |
|---|------------|----------------------|-------------|--------|
| **D1** | Pro se e-filing assistant | V1 | EFS integration module | Large |
| **D2** | IFP auto-generation with eligibility pre-check | V3 | IFP automation | Medium |
| **D3** | BCC-specific form templates (motion, cover sheet, cert of service, confidential info) | V5, V12, V14 | Template generation | Medium |
| **D4** | Filing fee calculator with IFP routing | V8 | Fee schedule integration | Small |
| **D5** | Venue-routing wizard (CP vs MDJ vs Orphans) | V13 | Jurisdiction router | Medium |
| **D6** | Confidential information redaction scanner | V14 | Document scanner | Medium |

### D2 -- Medium-Priority (Next Phase)

| # | Opportunity | Vulnerability Addressed | Libra Module | Effort |
|---|------------|----------------------|-------------|--------|
| **D7** | Orphans Court document generation (estate, guardianship) | V7 | Document generator | Medium |
| **D8** | Multi-county filing (Berks + Northampton + Federal) | V9 | Concurrent filer | Medium |
| **D9** | UJS docket scraper for case timeline tracking | V11 | Docket parser | Medium |
| **D10** | MDJ small claims automation (up to $12,000) | V13 | MDJ module | Medium |
| **D11** | Landlord-tenant / eviction document generation | V15 | Template generator | Medium |
| **D12** | Expungement / record sealing automation | V5 | Document generator | Medium |
| **D13** | Domestic relations / child support automation | V5 | DR module | Medium |

### D3 -- Cross-Reference: BCC_READING_PA_TODO.md

| BCC_TODO Item | This Document Section | Status |
|---------------|----------------------|--------|
| Court rules module (BCR 205.2, 208.2, etc.) | A2 (local rules summary) | Research complete |
| Prothonotary integration | A1 (full service catalog) | Research complete |
| Filing types | B1 (case types) | Research complete |
| IFP automation | A4 + C1-V3 | Research complete |
| Local forms | A3 + C1-V5 | Research complete |
| E-filing readiness | C1-V1 (date **UNCONFIRMED**; prepare regardless) | Research complete |

---

## SECTION E: Key Contacts & Resources

### E1 -- Official Contacts

| Entity | Phone | Website | Notes |
|--------|-------|---------|-------|
| **Prothonotary** | 610-478-6970 | berkspa.gov/departments/prothonotary | Civil, family, judgments, liens; Fee Bill 1/1/2026 |
| **Court Administration** | 610-478-6208 | berkspa.gov/departments/court-administration | Scheduling, forms, jury |
| **Register of Wills / Orphans Court** | 610-478-6600 | berkspa.gov | Estates, guardianships, adoptions |
| **Domestic Relations Section** | 610-478-2900 | berkspa.gov/departments/dro | Child support, spousal support, paternity; 6th Floor, Services Center |
| **Sheriff's Office** | 610-478-6240 | berkspa.gov/departments/sheriff | Service of process, fee schedule |
| **Interpreter Services** | interpreter@berkspa.gov | berkspa.gov/departments/court-administration/language-access | LEP + deaf/HoH |
| **Mid-Penn Legal Services** | 1-800-326-9177 | midpenn.org | Free/reduced legal representation |
| **Berks County Bar Association** | 610-375-4591 | berksbar.org | Attorney referral service |

### E2 -- Online Resources

| Resource | URL |
|----------|-----|
| **Prothonotary docket search** | prothy.countyofberks.com/cms/ |
| **Attorney e-filing portal** | prothy.countyofberks.com/efs/ |
| **UJS Portal (statewide)** | ujsportal.pacourts.us |
| **PA Courts pro se resources** | pacourts.us/learn/representing-yourself |
| **Civil Rules PDF** | berkspa.gov (search: Civil Rules) |
| **Court forms & schedules** | berkspa.gov/departments/court-administration/schedules-and-forms |
| **PA Legal Help** | palawhelp.org |
| **PA Legal Aid Network** | palegalaid.net |
| **Pennsylvania Bulletin** | pacodeandbulletin.gov |

---

## SECTION F: Regulatory Timeline

| Date | Event | Impact |
|------|-------|--------|
| **2025** | Act 45 of 2025 passed | JCP/ATJ/CJEA combined surcharge increased from $40.25 to $41.25 (+$1.00); applies to civil and criminal filings |
| **2025** | Returned check fee added | $50 fee for returned checks |
| **2025** | Passport services discontinued | Prothonotary no longer processes passports |
| **2026 (June)** | MDJ redistricting proposed | West Reading/Wyomissing MDJ seat proposed for dissolution; areas redistributed to neighboring districts (pending PA Supreme Court) |
| **2026** | COVID-19 emergency orders rescinded | All pandemic-era restricted access, mask mandates, and emergency procedures terminated; standard operations resumed |
| **August 1, 2026** | **Pro se e-filing RUMORED** | **UNCONFIRMED** — no official source found. Self-represented litigants should verify with Prothonotary before relying on this date. |
| **Ongoing** | AOPC PACFile expansion | Eventual statewide civil e-filing integration (no timeline) |
| **Ongoing** | Budget constraints | County operating under tight budgets; static staffing levels; MDJ consolidation to maximize efficiency |
| **Ongoing** | Local rules amendments | Monitor Pennsylvania Bulletin for BCR updates |

---

## Research Methodology

| Source | Method | Date |
|--------|--------|------|
| berkspa.gov/departments/prothonotary | Direct web research | July 9, 2026 |
| berkspa.gov/departments/court-administration | Direct web research | July 9, 2026 |
| prothy.countyofberks.com | E-filing and docket portal review | July 9, 2026 |
| pacourts.us | PA statewide court infrastructure | July 9, 2026 |
| ujsportal.pacourts.us | UJS portal capabilities | July 9, 2026 |
| palawhelp.org, palegalaid.net | Legal aid resources | July 9, 2026 |
| Pennsylvania Bulletin (pacodeandbulletin.gov) | Rule amendments | July 9, 2026 |
| **SECOND ROUND (Session 7)** | | |
| Fees, MDJ districts, DRS, UJS API, Act 45, Aug 1 verification | Targeted deep-dive | July 9, 2026 |
| berkspa.gov/departments/sheriff | Sheriff fee schedule | July 9, 2026 |
| readingeagle.com | Local news (MDJ redistricting) | July 9, 2026 |
| childsupport.state.pa.us | DRS online services | July 9, 2026 |

**Disclaimer:** This research is for informational and automation development purposes only. Court rules, fees, and procedures can change. Always verify with the official Berks County Prothonotary office. Libra is an automation tool, not a substitute for legal advice.
