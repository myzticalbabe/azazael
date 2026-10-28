# METHOD SELF-GRADE — META_HUBS_REDO against METHOD-STANDING-001

Grading of `docs/META_HUBS_REDO.md` + `alias_adjudication_report.json` +
`990_deep_report.json` against the 7 rules of METHOD-STANDING-001 (task
#45620). Each rule: PASS / FAIL with specifics. Patch gaps listed at the end.

## Rule (a) — Pre-registered method

STATUS: PARTIAL / FAIL

META_HUBS_REDO states its method ("five reads one build") and the technique
catalog lists 14 techniques, but the method was not pre-registered with pass
criteria before execution. The task row (#45612) said "five reads one build,
docs/META_HUBS_REDO.md, commit" — a deliverable spec, not a method with
falsifiable pass criteria. No pre-registered threshold for "hub" (e.g., "top-10
by betweenness, cutoff 0.05") was stated before computing. The centrality
numbers were computed, then the hub table was written to fit them.

PATCH: Add a "Method & pass criteria" section to META_HUBS_REDO stating, before
any numbers, the exact thresholds (top-10 by betweenness, articulation points
with >=2 components on removal, etc.) and what would fail.

## Rule (b) — ACH (2+ competing hypotheses)

STATUS: FAIL

Every conclusion in META_HUBS_REDO is single-hypothesis:
- "BCC is the dominant hub" — no competing hypothesis (e.g., "BCC is a
  pass-through with high degree but low brokerage" was never scored).
- "437K gap is explained by program-service revenue" — single hypothesis;
  alternatives (round-tripping, inflated contractor billing) were not scored
  against the same evidence.
- "No excess benefit / self-dealing" — single hypothesis; the alternative
  (related-party transactions below disclosure threshold) was not tested.

PATCH: Add an ACH table per major conclusion with 2+ hypotheses scored against
the same evidence (Heuer). Minimum: hub ranking, 437K gap, no-self-dealing.

## Rule (c) — Negative controls

STATUS: FAIL

- Centrality: no degree-shuffled null computed. Top-10 hubs reported as raw
  ranks with no z-score against a null. Per METHOD-STANDING-001, "centrality
  against degree-shuffled null (report z-score not raw rank)".
- verify_proofs: was run as a gate but not as a negative control on a known-bad
  edge during this block.
- Fetch oracle: no known-dead URL tested.

PATCH: Add a degree-shuffled null comparison for the top-10 hubs (z-scores).
Add a negative-control run of verify_proofs on 1 known-bad edge.

## Rule (d) — Re-performance over re-arithmetic

STATUS: PARTIAL / PASS

Centrality numbers were re-computed from network_edges_proofed.json (raw
re-performance, not re-arithmetic). Money-chain amounts were derived from
rel labels (re-performance from the graph, not from quoted figures). 990
indicators were re-extracted from raw XML. Partially compliant; the BCC
pass-through "in 1,409K / out 1,846K" is re-derived from edge rel labels,
not re-summed from kilo quotes. OK.

PATCH: None required; document the re-performance source for each number.

## Rule (e) — Source-limitation statement

STATUS: PASS (mostly)

- BOI report: universe label "FinCEN-BOI-registry-non-public-2026-10-25" —
  explicit source boundary. PASS.
- LIENS/UCC report: universe label "PA-UCC-and-Berks-recorder-not-searched" —
  explicit. PASS.
- 990-DEEP: scope note states available raws only (TY2024 for 3 orgs).
  PASS.
- MONEY-CHAIN: amounts from rel labels, noted. PASS.
- CENTRALITY: no source-limitation statement (graph is derived from
  network_edges_proofed.json, which is derived). Minor gap.

PATCH: Add a source-limitation line to the centrality report noting the graph
is a derived artifact (118 edges from 00_raw via beam1_apply).

## Rule (f) — Fetch-or-LEAD

STATUS: FAIL

- LIENS/UCC: 55 CUTs were recorded WITHOUT fetch rows (no portal was
  queried). Per METHOD-STANDING-001 and BCC-FETCH-RULE, an unsearched
  universe is a LEAD, never a CUT. The 55 lien CUTs must be relabeled LEAD
  until searched.
- BOI: 21 CUTs recorded without fetch rows (FinCEN BOI non-public). Same
  relabel needed.
- 990-DEEP: "no Schedule J/L/R filed" is an extract limitation (TEOS carries
  only Sched A/B/D/O), not a clean screen. The report already notes this
  but the conclusion ("no excess benefit") must be downgraded from a clean
  screen to a TEOS-limited finding.

PATCH: Relabel 55 lien CUTs -> LEAD. Relabel 21 BOI CUTs -> LEAD. Downgrade
990-DEEP "no excess benefit" conclusion to TEOS-limited.

## Rule (g) — Assumption ledger

STATUS: FAIL

META_HUBS_REDO has "Meta-reading" sections but no explicit top-3 load-bearing
assumptions with falsifiers. The 437K-gap conclusion, the hub ranking, and the
no-self-dealing conclusion all rest on unstated assumptions.

PATCH: Add an "Assumption ledger" section listing top-3 assumptions + what
would falsify each:
  1. BCC is a pass-through, not a round-tripper (assumption: program revenue
     covers the 437K gap). Falsified by: finding a circular money edge or a
     contractor that is a BCC affiliate.
  2. The graph is complete enough for centrality (assumption: 118 edges
     capture the key structure). Falsified by: discovering a high-degree node
     not in the graph.
  3. No excess benefit (assumption: 990 indicators are truthful). Falsified
     by: a Schedule L/R/J in the full filing (not TEOS extract) showing
     related-party transactions.

## Summary

| Rule | Status |
|---|---|
| (a) Pre-registered method | PARTIAL/FAIL |
| (b) ACH | FAIL |
| (c) Negative controls | FAIL |
| (d) Re-performance | PASS |
| (e) Source-limitation | PASS (minor gap) |
| (f) Fetch-or-LEAD | FAIL |
| (g) Assumption ledger | FAIL |

Score: 1 PASS, 1 PARTIAL, 5 FAIL.

## Patch plan (to be executed)

1. Relabel 55 lien CUTs -> LEAD in liens_ucc_report.json (and any edge rows).
2. Relabel 21 BOI CUTs -> LEAD in boi_report.json.
3. Downgrade 990-DEEP conclusion to TEOS-limited.
4. Add "Method & pass criteria" section to META_HUBS_REDO.md.
5. Add ACH tables for hub ranking, 437K gap, no-self-dealing.
6. Add degree-shuffled null z-scores for top-10 hubs.
7. Add assumption ledger (top-3) to META_HUBS_REDO.md.
8. Add source-limitation line to centrality report.

Opencode (methodology gate) will grade the patched version.