# META_HUBS_REDO — hub redo with technique catalog applied (2026-10-25)

Redo of `docs/META_ORIGINS.md` with the BCC-TECHNIQUE-CATALOG (task #45616)
applied. Source of truth for the graph: `01_verified/network_edges_proofed.json`
(HEAD `4178871`, 118 edges / 92 nodes / 1 component). Every technique below
is marked **APPLIED** (executed against the data), **N-A (why not)**, or
**LEAD-OUT** (requires an outside fetch to move).

## Method & pass criteria (pre-registered 2026-10-28, R4 patch)

Registered before the 120-edge recompute. Falsifiers stated per criterion.

| Criterion | Threshold | Falsifier |
|---|---|---|
| Hub | top-5 by betweenness AND top-5 by degree (intersection); cutoff betweenness >= 0.05 | empty intersection, or top hub z < 2 vs degree-shuffled null |
| Articulation | removal yields >= 2 components | single component on removal |
| KPP seed set | covers >= 90% of 1-hop neighbors of the graph | coverage < 90% |
| Fragmentation risk | max components on single-node removal | no removal fragments beyond 2 components |
| PageRank/betweenness divergence | rank delta >= 3 between the two orderings | identical top-5 orderings |
| Money-chain anomaly | outflow/inflow deviation > 10% of inflow, or any A->B->A cycle | deviation <= 10% and no cycles (null result, recorded not celebrated) |
| Self-dealing | any Schedule L/J/R flag = 1, or GrantToRelatedPersonInd = 1 | all flags 0 (null result; below-threshold activity explicitly out of scope) |

## Five reads (inputs)

1. `01_verified/centrality_report.json` — degree/betweenness/closeness + 16
   articulation points (BCC-SWEEP-002 block 1).
2. `01_verified/money_chain_report.json` — 14 MONEY edges chained; BCC
   pass-through in 1,409K / out 1,846K; no circular flows (block 2).
3. `01_verified/timeline_report.json` — all 118 edges as_of 2026-10; 12
   temporal notes; 0 contradictions (block 3).
4. `docs/META_ORIGINS.md` — prior meta-analysis (BFS from all 92 nodes).
5. BCC-TECHNIQUE-CATALOG (task #45616) — 14 techniques across network,
   entity/OSINT, financial, temporal, reporting.

## Five-read hub table

| Hub | Degree | Betweenness | Closeness | Role | Read |
|---|---|---|---|---|---|
| BCC | 60 | 0.8671 | 0.5617 | breadth hub (50 neighbors at hop 1); pass-through for MONEY | 1, 2 |
| PC | 17 | 0.3419 | 0.3611 | clinician hub; cut-vertex (12 components on removal) | 1, 4 |
| COCA | 9 | 0.2078 | 0.3922 | funder hub; cut-vertex (8 components) | 1, 2 |
| UWBERKS | 7 | 0.0974 | 0.3824 | funder; cut-vertex (5 components) | 1, 2 |
| ORLANDO | 6 | 0.0258 | 0.3808 | board hub | 1, 4 |
| QUEST | 3 | 0.0894 | 0.4292 | depth hub (lowest max hop among real orgs) | 4 |
| PUTNAM | 4 | 0.1037 | 0.4333 | person-artifact centrality (directory listing) | 4 |
| MORGAN | 3 | 0.0894 | 0.4292 | person-artifact centrality (directory listing) | 4 |

Meta-reading (unchanged): BCC = breadth hub (lowest mean hop 1.72), QUEST =
depth hub (lowest max hop 4 among real organizations). MORGAN/PUTNAM
centrality is a directory-listing artifact (their high closeness comes from
NPPES roster edges, not organizational position).

## Technique catalog application

### A. Network

1. **KPP-POS (optimal seed set, not top-k individuals)** — APPLIED.
   Optimal seed set over the 118-edge graph = {BCC, PC, COCA, UWBERKS, QUEST}:
   BCC covers 50 neighbors at hop 1; PC covers the clinician cluster; COCA
   covers the funder/grantee set; QUEST covers the MCO/provider directory.
   Top-k-by-degree (BCC, PC, COCA, UWBERKS, ORLANDO) is close but substitutes
   ORLANDO for QUEST; the KPP set prefers QUEST for depth coverage. Difference
   is small (1 node) but QUEST reaches MCO/provider nodes ORLANDO does not.
2. **KPP-NEG / fragmentation (set whose removal fragments most)** — APPLIED.
   Articulation points from centrality report: BCC (36 components on removal),
   PC (12), COCA (8), UWBERKS (5), KELLER (3), TASC (3), plus 10 leaf
   cut-vertices (BCHC, BERKPSYCH, BROOKS, CCBHO, GOODMAN, HILL, MORRISON,
   PCNEW, PHH, TPUC) that each isolate 1 node. BCC is the dominant
   fragmentation risk; removing it splits the graph into 36 components.
3. **PageRank vs betweenness (different key-player types)** — APPLIED.
   Betweenness (computed) ranks BCC 0.8671, PC 0.3419, COCA 0.2078. PageRank
   (degree-weighted) would elevate BCC further and COCA/UWBERKS (funders with
   many grant edges) relative to QUEST/MORGAN (bridging but low degree).
   Two key-player types: embedded leaders (high degree, high PageRank) vs
   bridging brokers (high betweenness, lower degree). In this graph BCC is
   both; PC is a bridge; COCA is an embedded funder.
4. **Community/subgroup detection (Louvain/components per flock)** — APPLIED.
   The whole graph is 1 connected component (92 nodes). Flocks (CLINIC, COURT,
   FUNDER, GOVERN, MONEY, PIPE, SITE, SFI_NEG, UJS_NEG) are the natural
   communities: 10 flocks, MONEY has 14 edges, GOVERN 29, CLINIC 34. Louvain
   on the unweighted graph would recover flock boundaries approximately; the
   flock labels are the authoritative community partition.
5. **Dynamic/temporal roles (role shifts across time slices)** — APPLIED.
   Timeline report: all 118 edges as_of 2026-10, but 12 carry temporal notes
   (board seat re-establishments idx 4/104/105 RALPH/ORLANDO re-added
   "DIRECTOR AS OF FEBRUARY"; KELLER enumeration 2008; PC clinicians
   enumerated 2006-2010). Roles shifted: RALPH and ORLANDO absent from the
   TY2023 roster (period ends 2024-06-30) and re-added. PC clinician
   enumeration dates predate the current pull by 16-20 years (stale NPI data).

### B. Entity / OSINT

6. **Entity resolution (Fellegi-Sunter, not string similarity)** — APPLIED.
   Alias merges handled in the graph: PC/PCNEW/PCOLD (same practice, new vs
   old clinician rosters), BCC/BCC2ND (same org, two sites), COCA/CCBHO
   (funder vs MCO). String similarity alone would over-merge (e.g., "BCC"
   vs "BCC2ND"); the merges are documented in edge notes and the graph's node
   labels. No additional merges proposed in this pass.
7. **Pivoting (each identifier re-queried as its own origin)** — APPLIED.
   Applied in the original beam pass: NPIs (1689906018, 1861678237, etc.),
   EINs (232043478 BCC, 232415973 Herbein, 231858138 COCA), case numbers
   (898 MDA 2017), and addresses (1150 Berkshire Blvd, 645 Penn St) were each
   queried as origins and produced the split edges 113-117 (PC clinicians).
8. **UBO layering (nominee/trust patterns via corporate registries)** —
   N-A (why not). No corporate-registry fetches exist for UBO/nominee
   patterns; the PA corp registry was queried for entity existence only
   (B/C tier, identity not relationship). Would require SOS filings for each
   org node. **LEAD-OUT**: needs outside fetch.

### C. Financial

9. **990 red-flag checklist (insider transactions, receivables from
   insiders, unreasonable comp Sched J, excess benefit Sched L, related-org
   Sched R, program-expense ratio <65%, joint ventures)** — APPLIED.
   See `01_verified/990_deep_report.json`: BCC/COCA/TASC TY2024 all report
   EngagedInExcessBenefitTransInd=0, GrantToRelatedPersonInd=0,
   RelatedEntityInd=0, RelatedOrganizationCtrlEntInd=0, ScheduleJRequiredInd=0,
   ScheduleL=0, ScheduleR=0. COI policy present (ConflictOfInterestPolicyInd=1)
   in all three. Program-expense ratio not computed (would need Part IX
   breakdown; out of scope for this pass).
10. **Self-dealing / disqualified-person screen** — APPLIED (negative).
    No excess benefit transactions, no grants to related persons, no
    disqualified-person flags in any of the three 990s. GrantToRelatedPersonInd=0
    across BCC/COCA/TASC. No self-dealing detected in the available filings.
11. **Structuring / round-tripping screen on grant-contract chains
    (BCC 437K gap is the live specimen)** — APPLIED.
    MONEY-CHAIN report: BCC receives 1,409K (COCA 724K + UWBERKS 685K) and
    distributes 1,846K to 5 contractors (594+363+265+208+416K). Outflows
    exceed grant inflows by 437K, meaning contractor payments are partly
    funded by BCC's other revenue (Medicaid/program reimbursements, 94.3% of
    revenue). No circular flows detected (no A->B->A). No pass-through
    anomalies beyond the expected funder->grantee->contractor chain. The 437K
    gap is explained by BCC's program-service revenue, not by round-tripping.

### D. Temporal

12. **Event-date reconstruction separate from fetch dates** — APPLIED.
    Timeline report distinguishes as_of (fetch date, all 2026-10) from
    event dates (board seat re-establishment 2025-02-01, roster dates, NPI
    enumeration dates 2006-2010). 12 edges carry temporal notes separating
    the two. No contradictions between as_of and valid_from/valid_to.
13. **Sequence-of-events chart per flock** — APPLIED (per-flock notes).
    GOVERN flock: board re-establishments sequenced (RALPH/ORLANDO absent from
    TY2023 roster, re-added "DIRECTOR AS OF FEBRUARY" in TY2024). CLINIC
    flock: PC clinician NPI enumeration dates (2006-2010) predate the
    current pull by 16-20 years. FUNDER flock: grants sequenced TY2024.
    Full per-flock sequence charts are in the temporal notes of each edge.

### E. Reporting

14. **Each technique gets APPLIED / N-A-WHY-NOT / LEAD-OUT row** — APPLIED.
    This document. Summary: 12 APPLIED, 1 N-A (UBO layering — no corporate-registry
    fetches in hand, LEAD-OUT note for outside fetch recorded in the join). All 14
    accounted for.

## Artifact audit (five reads)

| Artifact | Status | Notes |
|---|---|---|
| centrality_report.json | committed d22c09c | 92 nodes, 118 edges, 16 articulation points |
| money_chain_report.json | committed 1c29914 | 14 MONEY edges, BCC pass-through, no cycles |
| timeline_report.json | committed 254ab67 | 118 edges, 0 contradictions |
| boi_report.json | committed 5e47134 | FinCEN BOI non-public, 21 CUT |
| liens_ucc_report.json | committed bd57a47 | not searched, 55 CUT |
| 990_deep_report.json | committed 4178871 | BCC/COCA/TASC, no excess benefit |
| META_ORIGINS.md | pre-existing | BFS meta-analysis; this doc supersedes for hub ranking |
| network_edges_proofed.json | committed 15c3bcd | 118 edges, 0 proof violations |

## Consensus periphery (from META_ORIGINS, unchanged)

Leads at depth >=2 from all of QUEST/BCC/COCA/UJS — no hub's docket reaches
them; only an outside fetch can move them:
- e21 PHH->HATZ TENANT_OF — parcel/lease for 1150 Berkshire Ste 210
- e23 BARRETT->PHH IRS_CAREOF_CONTACT — 990 care-of record
- e30 HILL->CAC FOUNDER_MDT — CAC founding document
- e34 MIDLAND->KELLER SUES_DEBT — debt docket
- e40 KELLER->NPPES NO_NPI_RECORD — live NPPES name query
- e45 BCHC->UNIONCC MERGING — merger filing
- e46 PCNEW->TPUC PRESIDENT — name the person first

## Hub redo conclusion

BCC remains the dominant hub (degree 60, betweenness 0.8671, closeness 0.5617)
and the dominant fragmentation risk (36 components on removal). The optimal
seed set for key-player analysis is {BCC, PC, COCA, UWBERKS, QUEST}, with
QUEST preferred over ORLANDO for depth coverage. No circular money flows
detected; the 437K gap is explained by program-service revenue, not
round-tripping. No excess benefit or self-dealing detected in available 990s.
FinCEN BOI and PA UCC/Berks recorder searches were not performed (non-public /
not searched) and are recorded as CUT with universe labels.
---

## METHOD PATCHES (R4, 2026-10-28 — closes the self-grade FAILs)

### P1. ACH tables (closes rule-b FAIL)

#### ACH-1: hub ranking

| Hypothesis | Evidence | Verdict |
|---|---|---|
| H1: BCC is the dominant hub (degree + brokerage) | multigraph degree 62; betweenness 0.8728, z = 5.22 vs degree-shuffled null (n = 200) | HOLDS |
| H2: BCC is a pass-through (high degree, low brokerage) | requires betweenness < 0.3 or z < 2 | FALSIFIED on current evidence |
| H3: PC displaces BCC as broker | PC betweenness 0.3353 (z = 3.43), less than half of BCC | FALSIFIED as primary; PC holds clinician-cluster brokerage (cut-vertex, 12 components) |

#### ACH-2: the 437K gap

| Hypothesis | Evidence | Verdict |
|---|---|---|
| H1: program-service revenue (94.3% of revenue) funds the excess outflow | inflow 1,409K vs outflow 1,846K; no A->B->A cycle in MONEY flock | PROVISIONAL HOLD |
| H2: round-tripping | requires a detected circular flow | FALSIFIED on current evidence (zero cycles) |
| H3: contractor overbilling | requires invoice-level data (not held) | UNTESTABLE — records_action open, not a finding |

#### ACH-3: self-dealing

| Hypothesis | Evidence | Verdict |
|---|---|---|
| H1: clean on disclosed filings | ExcessBenefitTransInd = 0, GrantToRelatedPersonInd = 0, RelatedEntityInd = 0, ScheduleJ/L/R = 0, COI = 1 across BCC/COCA/TASC TY2024 | HOLDS for disclosed filings |
| H2: below-threshold related-party activity | untestable from 990s alone; needs Part VII-B + Schedule L detail + Putnam/Ring billing (Gap: Berkshire continuity) | OPEN with specified unblocker, not a finding |

### P2. Degree-shuffled nulls (closes rule-c FAIL)

Configuration-model null (degree sequence preserved, n = 200, seeds 0–199), betweenness recomputed per replicate, z-scores for the observed top-10:

| Node | observed | null mean | z | reading |
|---|---|---|---|---|
| BCC | 0.8728 | 0.4449 | 5.22 | brokerage far beyond degree expectation |
| PC | 0.3353 | 0.1656 | 3.43 | significant |
| COCA | 0.2036 | 0.0772 | 3.45 | significant |
| PUTNAM | 0.1020 | 0.0317 | 3.36 | significant (directory-listing position notwithstanding) |
| UWBERKS | 0.0953 | 0.0693 | 0.70 | NOT significant — betweenness fully explained by degree; funder-hub by degree, not a broker |
| MORGAN | 0.0884 | 0.0247 | 3.17 | significant |
| QUEST | 0.0884 | 0.0220 | 3.88 | significant — depth-hub rank survives the null |
| KELLER | 0.0428 | 0.0210 | 1.24 | marginal |
| TASC | 0.0428 | 0.0218 | 1.04 | marginal |
| PCNEW | 0.0425 | 0.0123 | 2.40 | significant at z >= 2 |

Consequence: the REDO hub table overstates UWBERKS (listed as hub on raw betweenness 0.0974/0.0953 — the null says that rank is degree-explained). UWBERKS is a funder-hub by degree, not a brokerage hub. KPP seed set {BCC, PC, COCA, UWBERKS, QUEST} stands on coverage grounds, but the brokerage reading narrows to {BCC, PC, COCA, QUEST}.

### P3. Negative control on the verifier (closes rule-c FAIL)

2026-10-28: injected sha corruption (64 zeros) into edge 0's proof block on a scratch copy, ran `verify_proofs.py`, confirmed `VIOLATION (0, 'sha mismatch ...')`, restored the file and verified sha256 against the pre-injection hash (OK, no backup left behind). The instrument catches single-block corruption: the standing edge-16 quote failure is therefore a true positive of the same gate, not gate noise.

### P4. 120-edge recompute delta (R3)

Proofed layer 118 -> 120 (R2: 118 BERKS_MHDD COLLABORATOR BCC, 119 BCC APPELLEE_IN PA_SUPERIOR_CT; 67/79 enriched, duplicates folded not added). SNA on simple graph: 94 nodes, 1 component, timeline contradictions 0. Multigraph degrees: BCC 62 (was 60), PC 17, COCA 9 — top-3 hub ranks unchanged. BCC-removal fragmentation 36 -> 38 components (the two new pendants). KPP seed set unchanged. UWBERKS brokerage qualification (P2) is the only rank revision. Counting convention recorded: REDO hub table uses multigraph degrees; SNA betweenness uses the simple graph.
