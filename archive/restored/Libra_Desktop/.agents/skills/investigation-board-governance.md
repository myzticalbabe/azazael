---
name: investigation-board-governance
description: Board governance forensics — conflict of interest detection, board composition mapping, hidden network analysis, Schedule L cross-referencing, fiduciary duty breach patterns. Distilled from the BCC investigation.
metadata:
  category: investigation
  project: bcc-investigation
  auto_load: false
  date_created: 2026-08-01
---

# Investigation: Board Governance Forensics

## The Hidden Network Detection Framework

The BCC investigation uncovered a 4-layer hidden network of harm. Every nonprofit investigation should probe these same layers:

### Layer 1: Board-Employer Interlock
**Pattern:** Board members whose employers do business with the organization.

**Detection method:**
1. List every board member and their employer
2. For each employer, ask: could this entity provide services to the org?
3. Flag financial institutions, law firms, accounting firms, consulting firms, insurance companies, and real estate firms
4. Cross-reference against Schedule L Part IV (Business Transactions)

**Red flag threshold:** Any board member employer that operates in a sector the org purchases from. The 22% Edward Jones board control at BCC is the archetype.

### Layer 2: Governance-Capture via Board Composition
**Pattern:** The board is stacked with interests aligned with the executive, eliminating oversight.

**Detection method:**
- BCC: CEO + CFO sit ON the board as voting members (documented in Part VII)
- Count board members with financial ties to the org vs. truly independent members
- Check: do the CEO and CFO recuse from their own compensation votes?
- If the board approves CEO compensation without independent committee review → governance capture

### Layer 3: Funder-Fiduciary Nexus
**Pattern:** A funder's employee sits on the board, creating a circular oversight failure.

**Detection method:**
- Map every board member's employer to grant-makers
- Example: BCC board member Missy Orlando = United Way Berks employee; United Way funds BCC $685K+
- The funder's own employee is incentivized to protect the grant relationship
- No independent oversight exists — the funder and the funded share a board member

### Layer 4: Regulatory-Failure Cascade
**Pattern:** Every oversight body has a structural reason NOT to act.

**Detection method:**
- Map the oversight chain: DDAP → SAMHSA → HHS OIG → City Council → County Commissioners → PA AG
- For each, identify the structural incentive for non-enforcement
- DDAP: resource constraints, political pressure, licensee capture
- County Commissioners: BCC is a major service provider — cutting funding harms constituents
- PA AG: resource constraints, political considerations
- The result: a regulatory vacuum where no one acts

## COI Policy Analysis

### What to ask
1. **Does the COI policy exist?** Request it under IRC § 6104(d). If they refuse → § 6104(d)(4) penalty.
2. **Is it published?** 990 Part VI, Line 12a asks if the org has a COI policy. Line 12b asks if it's regularly monitored.
3. **Who enforces it?** If the board chair (who has the conflict) is the enforcer → the policy is theater.
4. **Is there a recusal process?** Does the policy require conflicted board members to recuse from votes AND be excluded from quorum counts?
5. **Are disclosures required annually?** Does the policy require annual disclosure of all business relationships?

### Red flags in COI responses
- 990 Part VI, Line 12a = YES (COI policy exists) but the policy is never provided on request
- 990 Part VI, Line 12b = YES (monitored) but no enforcement mechanism exists
- Schedule L = ALL-NO despite obvious conflicts → either COI policy is not enforced or Schedule L is fraudulent

## Board Composition Analysis

### Key metrics
| Metric | What to Calculate | Red Flag Threshold |
|--------|------------------|-------------------|
| **Tenure** | Years served per member | Any member >10 years without term limit |
| **Independence** | Members with no financial ties to org / total members | <50% independent |
| **Employer concentration** | Members from same employer or industry | >1 member from same employer |
| **Executive presence** | Do CEO/CFO sit on board? | Any voting executive on board |
| **Turnover** | New members added per year | Zero turnover in 5+ years |

### BCC archetype analysis
```
Board size: 9 voting members
Edward Jones: 2 members (22.2%) — Joseph Plageman Jr. (Chair), Tracy Krause
United Way: 1 member (11.1%) — Missy Orlando (UW employee)
GSK: 1 member (11.1%) — Dr. Jeffrey Ralph (Treasurer)
Vanguard (former): 1 member (11.1%) — John Robinson (Treasurer; owns consulting firm)
BCC management: 2 members (22.2%) — Axford (CEO), Little (CFO)
Other: 2 members (22.2%) — Deborah Scull, Janis Brooks

Independent count: 0-1 members (Scull, maybe Brooks)
Financial industry concentration: 33.3% (Plageman + Krause + Robinson/Vanguard)
```

## Schedule L vs. Board Reality Cross-Reference

This is the single most powerful governance audit technique:

```
FOR EACH board member:
  Is the member's employer a vendor, service provider, funder, or potential
  beneficiary of the organization?

IF YES:
  Check Schedule L Part IV — is this relationship disclosed?

IF NO:
  → Schedule L is false → IRC § 7206 (fraudulent return) + § 4958 (if excess benefit)
  → COI policy is either nonexistent or unenforced
  → Board minutes should show recusal on relevant votes — request them
```

## Fiduciary Duty Framework

Board members of PA nonprofits owe:
1. **Duty of Care** (15 Pa.C.S. § 5712(a)): discharge duties in good faith, with care of ordinarily prudent person
2. **Duty of Loyalty** (15 Pa.C.S. § 5712(b)): act in best interests of the corporation, not personal interests
3. **Duty of Obedience**: ensure the org complies with laws and its own mission

### Breach indicators
- Board approves transactions benefiting its own members without competitive bidding
- Board fails to maintain and enforce COI policy
- Board does not review audited financial statements
- Board allows CEO/CFO to set their own compensation without independent review
- Board minutes do not reflect recusal from conflicted votes

## Dual-Pattern Detection

**Technique:** When a board member holds governance roles at TWO organizations simultaneously, check whether the SAME conflict pattern appears at both.

**BCC archetype:** Joseph Plageman Jr. serves as:
- Board Chair, Berks Counseling Center (14+ yrs) — $10.48M portfolio, Edward Jones on the board
- President, Trustees of the Pennsylvania Universalist Convention (TPUC, 2026-present) — religious trust with its own endowment

**Detection method:**
1. For each board member with a detected conflict at Organization A, search for their other governance roles
2. Check whether the SAME conflict pattern (financial advisor on board, undisclosed portfolio management) replicates
3. A dual pattern transforms a "possible oversight" into a "pattern of conduct" — far stronger for FINRA and AG complaints
4. FINRA Rule 3270 applies per-organization — two undisclosed roles = two violations

## Recusal Record Reconstruction

**Technique:** Prove the COI policy is theater by reconstructing whether conflicted members actually recused.

**Method:**
1. Request board meeting minutes under IRC § 6104(d) — 990 Part VI, Line 8 mandates meeting documentation
2. Identify votes where conflicted members should have recused (investment contract renewal, audit firm engagement, budget approval)
3. Check minutes for: (a) recusal notation, (b) abstention in vote tally, (c) exclusion from quorum count
4. If minutes show conflicted members voting on conflicted matters → COI policy is unenforced → Schedule L is false
5. If minutes are refused or don't exist → § 6104(d)(4) penalty + adverse inference

**For public officials (city council):**
1. Request council meeting minutes via PA RTK
2. Search for votes involving the target organization
3. Check whether the conflicted council member (Goodman-Hinnershitz at Reading City Council) recused per 65 Pa.C.S. § 1103(a)
4. 20 years of minutes may need manual review — most municipal minute archives are not full-text searchable online

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| Accept "9-member volunteer board" at face value | Map every member's employer and flag every potential conflict |
| Assume Schedule L ALL-NO is truthful | Cross-reference every board member employer against org's vendors/service providers |
| Treat board members as independent because they're volunteers | A volunteer with a financial conflict is MORE conflicted — they gain indirect benefit without accountability |
| Focus on one governance failure in isolation | Map the cascade: COI failure → Schedule L failure → audit failure → regulatory failure |
| Assume funder board members create oversight | A funder's employee on the board creates circular oversight — the funder is captured |

## Related Skills
- `investigation-990-forensics` — Schedule L and Part VII data that reveals governance failures
- `investigation-regulatory-licenses` — Board members' professional licenses that can be revoked
- `investigation-legal-referral` — Translating governance findings into AG fiduciary breach complaints
- `investigation-osint` — Finding board member employers and professional histories
- `investigation-evidence-location` — IRC § 6104(d) requests for board minutes and COI policy
