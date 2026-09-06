# investigation-people-discovery.md
## Board Member & Key Person Employer Verification — 14-Channel Discovery Protocol

**Created:** August 1, 2026 — distilled from BCC investigation (23 people, 34 data sources)

---

### 14-Channel Discovery Protocol (In Priority Order)

For each person being investigated, execute channels in this order. Stop when employer is confirmed with high confidence. Document every channel result — negative results are also evidence.

#### Channel 1: IRS Form 990 Part VII (Highest Priority — Always First)
- **Source:** ProPublica Nonprofit Explorer (projects.propublica.org/nonprofits)
- **What to look for:** Employer name, title, hours/week, compensation, board tenure
- **Red flags:** Employer field blank, "See Schedule O" without details, $0 compensation with full-time title
- **Tool:** Manual web search by EIN, or `extract_bcc_990_json.py` pattern for programmatic extraction

#### Channel 2: FINRA BrokerCheck (Financial Industry)
- **Source:** brokercheck.finra.org — individual search by name or CRD #
- **What to look for:** Current employer, branch address, registrations (Series 7/66/SIE), state registrations, disclosure events (customer disputes, regulatory actions, employment separations, criminal, civil judicial, financial — liens/bankruptcies/judgments), outside business activities (OBA section)
- **Red flags:** Zero OBAs when person holds known outside roles (Rule 3270 violation), disclosures in any category
- **Tool:** Manual web search; FINRA API (api.finra.org) for programmatic access

#### Channel 3: PA Dept of State Business Entity Registry
- **Source:** PA Dept of State — business entity search (file.dos.pa.gov)
- **What to look for:** Businesses registered to the person's name, entity status (ACTIVE/INACTIVE), incorporation date, principal address
- **Red flags:** ACTIVE business entity providing services the nonprofit could purchase
- **Tool:** Manual; also pennsylvaniadb.com, bizapedia.com as mirrors

#### Channel 4: LinkedIn (Manual)
- **Source:** linkedin.com — manual profile search
- **What to look for:** Current employer, prior employers, professional connections to other board members/staff
- **Caveat:** Automated access blocked; manual only. Profile may not exist or may be private.

#### Channel 5: Google/Bing Web Search (OSINT)
- **Source:** google.com, bing.com
- **Query patterns:**
  - `"[Full Name]" "[City]" "[State]"` — primary
  - `"[Full Name]" employer` — employer discovery
  - `"[Full Name]" "board of directors"` — other board memberships
  - `"[Full Name]" "[Nonprofit Name]"` — direct connection
  - `"[Full Name]" site:linkedin.com` — LinkedIn profile via search
- **What to look for:** Employer mentions, other board memberships, news articles, professional bios, conference speaker pages

#### Channel 6: FEC Individual Contributor Search
- **Source:** fec.gov — individual contributor search
- **What to look for:** Political contributions > $200, employer listed on contribution record
- **Tool:** fec.gov/data/receipts/individual — search by name + state

#### Channel 7: PA Campaign Finance Records
- **Source:** PA Dept of State — campaign finance search (campaignfinanceonline.pa.gov)
- **What to look for:** State/local political contributions, employer listed
- **Tool:** Manual; also followthemoney.org

#### Channel 8: PA Disciplinary Board (Attorney Check)
- **Source:** PA Disciplinary Board — attorney license search (padisciplinaryboard.org)
- **What to look for:** PA bar admission, current employment, license status
- **Purpose:** Rule out legal conflicts; confirm if person is an attorney

#### Channel 9: PA PALS License Verification (CPA / Professional)
- **Source:** pals.pa.gov — license verification portal
- **What to look for:** CPA license status, other professional licenses
- **Caveat:** JavaScript portal — not accessible programmatically. Manual lookup required.

#### Channel 10: GuideStar / Candid
- **Source:** guidestar.org — nonprofit profile search
- **What to look for:** Other nonprofit board memberships, compensation data, 990 filings

#### Channel 11: SEC EDGAR
- **Source:** sec.gov/edgar — company filings search
- **What to look for:** Insider trading reports (Form 4), beneficial ownership (Schedules 13D/G), company affiliations
- **Caveat:** Only for publicly traded companies and their insiders

#### Channel 12: EMMA / MSRB
- **Source:** emma.msrb.org — municipal bond database
- **What to look for:** Municipal bond disclosures listing person's name, government contractor disclosures

#### Channel 13: Edward Jones / Brokerage Advisor Search
- **Source:** edwardjones.com — advisor search, or specific brokerage website
- **What to look for:** Advisor profile page, branch location, team members
- **Purpose:** Confirm financial advisor employment and team structure

#### Channel 14: Grant Funder Reporting
- **Source:** United Way annual reports, foundation 990-PF filings, MacKenzie Scott grant databases
- **What to look for:** Grant amounts to target nonprofit, grant descriptions, funder staff who may serve on board

---

### 6-Channel Sweep Protocol (Rapid Elimination)

For initial screening when investigating multiple people, run these 6 channels in parallel:
1. PA Dept of State business entity search
2. PA Disciplinary Board attorney license search
3. PA CPA license verification (PALS)
4. Bing search (fast, less rate-limited than Google)
5. Google search (complementary to Bing)
6. GuideStar/Candid nonprofit profiles

**Document results** with timestamp and specific query strings used. Negative results across all 6 channels = "UNCONFIRMED employer."

---

### Verification Status Classification

| Status | Criteria |
|--------|----------|
| **✅ CONFIRMED** | Employer verified through 2+ independent sources (e.g., FINRA API + EJ website + 990) |
| **⚠ INFERRED** | Strong single-source lead but not independently corroborated |
| **🔍 UNCONFIRMED** | No employer found after exhaustive 6+ channel search |
| **🦉 CONFLICT** | Employer confirmed AND has direct business/funding relationship with target nonprofit |

---

### Common Pitfalls & Anti-Patterns

| Pitfall | Fix |
|---------|-----|
| **Name too common** (e.g., "James Brooks") | Narrow by city ("Reading PA"), middle initial, age range, prior known roles |
| **LinkedIn blocked** | Use site:linkedin.com Google search; accept that manual is the only reliable method |
| **FINRA API access issues** | brokercheck.finra.org web interface is the fallback; detailed endpoint may return 403 |
| **PA PALS JavaScript block** | Cannot automate — must be manual. Note "JS portal — not accessible remotely" |
| **990 Part VII employer blank** | Check Schedule O (supplemental info); check prior years; check nonprofit's own website "About Us" or "Leadership" page |
| **Website provides no bios** (BCC case) | This is itself a red flag — document as "Transparency Gap: no employer info on org website" |
