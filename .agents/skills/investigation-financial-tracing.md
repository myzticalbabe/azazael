# investigation-financial-tracing.md
## Nonprofit Financial Anomaly Detection — Z-Score, 990 Forensics, Investment Tracing

**Created:** August 1, 2026 — distilled from BCC investigation (activate_bcc_analysis.py, CCBHC regime change analysis)

---

### Phase 1: 990 Data Extraction

#### Source: ProPublica Nonprofit Explorer (E-File Viewer)
- **URL:** projects.propublica.org/nonprofits — search by EIN
- **Target years:** Minimum 5 years (ideally 6+ to establish pre/post baseline)
- **Key fields to extract:**
  - Part I (Summary): Revenue, Expenses, Net Income, Total Assets, Total Liabilities, Net Assets
  - Part III (Program Services): Program service expenses, number of program lines
  - Part VII (Compensation): CEO, CFO, key employees — base comp, bonus, other comp, total
  - Part VIII (Revenue): Program service revenue, investment income, contributions & grants
  - Part X (Balance Sheet): Total assets, net assets, publicly traded securities
  - Schedule D: Investment portfolio composition, investment manager name
  - Schedule J: Compensation methodology (if publicly filed)
  - Schedule L: Related-party transactions — ALL FOUR questions (Lines 25a-28)
- **Tool:** `extract_bcc_990_json.py` pattern — extract structured JSON from ProPublica e-file viewer

#### Gap: Schedule B (Major Donors)
- Schedule B is REDACTED in public 990 — donor identities are not public
- Cross-reference against funder reporting (United Way annual reports, foundation 990-PF, MacKenzie Scott grant databases)
- Gap resolution: search for the nonprofit's name in funders' own public disclosures

---

### Phase 2: Z-Score Baseline Establishment

#### Step 1: Define Regime Boundary
- Identify a clean temporal boundary dividing the data into pre/post periods
- **BCC example:** SAMHSA CCBHC grant award (Sept 30, 2023) → FY2023 is first post-grant year
- Pre-grant = baseline (train); post-grant = test

#### Step 2: Compute Baseline Statistics (Pre-Grant)
For each financial metric, compute mean (μ) and standard deviation (σ) from pre-grant years:
```
μ = Σ(x_i) / n
σ = sqrt( Σ((x_i - μ)²) / n )
```
- **Minimum n:** 3 baseline years for meaningful σ (with caveat that σ from n=3 has wide confidence intervals)
- **Metrics to baseline:** Revenue, Investment Income, Contributions, Net Income, Program Service Revenue, Total Assets

#### Step 3: Compute Per-Year Z-Scores
For each year (both pre and post), compute z-score for each metric:
```
z_metric = |x - μ_baseline| / σ_baseline
```

#### Step 4: Compute Composite Z-Score
Weighted sum to produce a single anomaly score per year:
```
Composite Z = 0.40 × z_revenue + 0.35 × z_investment_income + 0.25 × z_contributions
```
- **Weight rationale:** Revenue = primary financial health (40%), Investment income = key anomaly target per governance investigation (35%), Contributions = diversification context (25%)
- **Customize weights** based on investigation focus — if investigating compensation, weight compensation metrics higher

#### Step 5: Classify Each Year
| Composite Z | Classification | Interpretation |
|-------------|---------------|----------------|
| 0.00 – 0.80 | **NORMAL** | Within expected range of pre-grant behavior |
| 0.81 – 1.50 | **ELEVATED** | Above baseline but not definitively anomalous |
| > 1.50 | **ANOMALOUS** | Statistically significant divergence from baseline |

#### Step 6: Statistical Significance Testing
- **Fisher's Exact Test** (one-tailed): Compare count of ANOMALOUS years in pre vs. post
  - 3/3 post anomalous vs 0/3 pre anomalous → p = 0.05 (significant at α = 0.05)
- **Caveat:** Small n (3 per regime) limits formal test power. Treat as indicative, not definitive.
- **Document limitation:** "n=3 baseline years means each σ estimate has wide confidence intervals."

---

### Phase 3: Schedule D — Investment Portfolio Analysis

#### What to Extract
- Line 1: Publicly traded securities (beginning of year / end of year)
- Lines 2-10: All other categories (corporate stock, bonds, govt obligations, real estate, program-related investments)
- **Red flag:** 100% in public equities with NO bonds or alternatives — unusual concentration for a nonprofit
- **Red flag:** Investment manager name NOT provided (Schedule D asks for manager/custodian)

#### Portfolio Yield Calculation
```
Yield ≈ Investment Income / Average Portfolio Value
```
- **BCC example:** $446K / ~$10M = ~4.4% — reasonable for balanced portfolio
- **Benchmark comparison:** Compare yield against S&P 500 returns for same period
- **Red flag:** If portfolio growth far exceeds market returns, investigate active management

#### Investment Manager Discovery (When Not Disclosed)
1. Check Schedule D for manager/custodian name → if blank, that IS the finding
2. Cross-reference board members' employers against known investment firms
3. Check DOL Form 5500 (retirement plan) for plan advisor — may reveal investment relationships
4. SEC EDGAR — if nonprofit has any filing obligations
5. EMMA/MSRB — municipal bond disclosures
6. **Acceptance:** If investment manager is genuinely not publicly named anywhere, document as "Investment Manager Identity — CONCEALED"

---

### Phase 4: Schedule L — Related-Party Transaction Cross-Reference

#### Four Questions to Check
| Line | Question | Implication if Answered NO |
|------|----------|---------------------------|
| 25a | Excess benefit transactions? | Organization certifies no insider benefited from any transaction |
| 25b | Loans to interested persons? | No loans to board members, officers, or their businesses |
| 27 | Grants to interested persons? | No grants to board members or their organizations |
| 28a-c | Business transactions with interested persons? | No payments to any entity where a board member has a financial interest |

#### Cross-Reference Protocol
For each board member with a confirmed employer:
1. Does their employer provide services the nonprofit could purchase? (investment management, consulting, furniture, grant funding)
2. If YES → the ALL-NO Schedule L certification may be materially false
3. Document as: "Schedule L ALL-NO × [Board Member]'s employer provides [service] = undisclosed related-party transaction risk"

#### The Herbein Problem (Auditor Independence)
- If the same firm prepares the 990 AND conducts the independent audit → reduced independence check
- AICPA rules permit this for non-issuers with separate engagement teams
- **Investigation action:** Send engagement letter to auditor asking: (a) separate teams for 990 vs audit, (b) whether Schedule L ALL-NO was ever questioned, (c) request management letter for key years

---

### Phase 5: Compensation Anomaly Detection

#### Key Metrics
- **CFO/CEO ratio:** CFO comp > CEO comp = inversion (rare in 501(c)(3) — BCC: $149,792 vs $145,432)
- **"Other compensation" ratio:** CFO's other comp > CEO's other comp (BCC: $17,350 vs $5,428 = 3.2×)
- **Growth trajectory:** Compute compound growth for each officer over available years
- **Crossover analysis:** Find the year CFO first surpassed CEO — this is the inflection point

#### §4958 Rebuttable Presumption Analysis
Under Treas. Reg. §53.4958-6, compensation is presumed reasonable if:
1. Approved by board/committee composed entirely of individuals **without a conflict of interest**
2. Board relied on **appropriate comparability data**
3. Board **concurrently documented** the basis for its determination

**If element (1) fails** (board members from investment firm, funder-employed directors, Treasurer with own consulting firm) → the rebuttable presumption is UNAVAILABLE → compensation must be justified through other means → if not, it's a potential §4958 excess benefit.

---

### Phase 6: Regime Change Documentation

#### When to Declare a Regime Change
- 3+ consecutive post-boundary years classified ANOMALOUS
- 0 pre-boundary years ANOMALOUS
- Clean separation with no overlap between regimes
- Fisher's exact test significant at α = 0.05 (one-tailed, directional hypothesis)
- **7.00× or greater post/pre divergence ratio** is a strong signal

#### Documentation Template
```
FORMAL FINDING: [Boundary Event] Regime Change — STATISTICALLY CONFIRMED

The [boundary event] cleanly divides [Organization]'s financial behavior into two 
statistically distinct regimes. All [n] pre-event years cluster at composite z-scores 
of [range]. All [n] post-event years jump to [range] — a [X]× average increase with 
no overlap between regimes.

The regime change is driven entirely by [primary driver metrics] (with z-score 
increases of [X]× and [Y]×), not by [non-driver metrics] (which remained stable).

These anomalous metrics align with known governance red flags: [correlate each anomaly 
to a specific governance conflict].
```

---

### Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| **Small n (3 baseline years)** | Acknowledge limitation explicitly. σ from n=3 has wide CIs. Each additional baseline year significantly improves stability. |
| **Correlation ≠ Causation** | Document alternative hypotheses (bull market, one-time grants, manager change). Frame as "behavioral divergence coincident with [event]" not "[event] caused divergence." |
| **Market returns confound** | Compare portfolio growth to S&P 500 returns for same period. If growth dramatically exceeds market → stronger case for active management change. |
| **Schedule B redacted** | Cannot verify major donors. Cross-reference against funders' own public reporting. Accept the gap and document it. |
| **Investment manager not in Schedule D** | This IS the finding. Document all databases searched. The opacity itself is evidence. |
| **Only checking Schedule L ALL-NO** | Also check if ANY board member's employer could be a vendor/funder → if yes, ALL-NO may be false even if technically correct (standard fees may not trigger disclosure) |
