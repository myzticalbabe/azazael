# Ladder / Level / Metadata Gaps — Investigation 2026-10-28

Follow-up to `WEEK_ADDITIONS_AND_GAPS_2026-10-28.md` (G1–G12). This pass audits the
grading ladders, gate levels, and metadata stores themselves. Verified by direct
reads, not assertion. Severity: **H** = blocks a claim, **M** = inconsistency to resolve, **L** = cleanup.

## LADDERS (evidence grades L0–L3)

### LG1 (M) — L1 promotion queue is now identifiable: 3 of 42 L1 edges carry verifiable digits
`00_EDGE_VERIFICATION_LEDGER.md`: 42 L1 edges, of which only 3 contain digits
(79 NextGen w/ dates, 106 TLOS, 119 forum w/ docket). These three are promotion
candidates to L2/L3 on Kilo/beam review. The other 39 are digit-less and form a
natural **demotion queue** for the next re-grade — their "lead" status currently
rests on assertion alone. No promotion/demotion pass has been run since R2.

### LG2 (H) — 9 L0 edges are proof-vacant, including two load-bearing ones
9 edges have NO raw, NO sha, NO quote — not low-grade, *unproofed*:
| idx | edge | why it matters |
|---|---|---|
| 59 | BERKS_COMM AUTHORIZED_25M COCA | **$25M assertion with zero proof** |
| 81 | TREATCT ASSESS TASC | chain link for the P7 re-hang (PMB 15061) |
| 83, 95, 101, 102, 107–109, 111–113, 116, 117 | (assorted L0) | — |
Recommend a distinct `L0-UNPROOFED` label (vs L0-graded) and a priority re-proof
queue headed by 59 and 81. Note: 59's $25M also affects the 437K/self-dealing
ACH tables' completeness (R4) — an authorization figure that large, unproofed, is
a hole in the money-flow narrative either way it resolves.

### LG3 (M) — L3 promotion rule for edge 119 is undefined
R2 beam-tagged 119 as 1.1 (gate green), but the forensic floor's L3 rule doesn't
say whether a Superior Court opinion counts as L3-primary-source. Related: how
Aug-corpus L3-verified edges map onto the new shadow/quote schema is unmapped —
the 92-verified count at 108 edges has no stated carry-over rule at 120.

### LG4 (L) — `audit_loop_metadata.py` is an orphan schema
4th schema/filter (`filter_for_recovery`) has **zero consumers and zero data files**.
Either wire it to something (recovery-tracking) or delete it — dead code inside
the grading ladder invites future misuse.

### LG5 (M) — no published verified/lead/cut tally at 120 edges
Beam canon was 92 verified / 16 lead / 0 cut at 108. At 120 edges (9 L0s, 42 L1s)
the ledger split is unstated. One `verifier` run from tally; publish it.

## LEVELS (gates, method, tallies)

### LV1 (L) — UBO tally wrinkle in `docs/META_HUBS_REDO.md:152`
"0 LEAD-OUT (UBO is N-A with a LEAD-OUT note)" — UBO is simultaneously N-A *and*
a lead-out. Fix to 12 APPLIED / 1 N-A / 1 LEAD-OUT, or define N-A to absorb it.
One-line fix; the join JSON (`research/bcc_motif_technique_join.json`, dict keyed
by motif, 7 motifs × 14 techniques) is self-consistent — only the prose tally is off.

### LV2 (M, known) — motif counts still cosmos-derived (G12); SNA recompute pending (G11)
Join carries the caveat honestly. No change; listed here so the ladder audit is
complete. Re-derivation on the proofed layer unblocks citing any count.

## METADATA / STORES

### MS1 (H) — R0 single-writer rule is violated in the letter
Banners name `build_gap_index.py` (tracked) and `gap_metadata.py` (enriched) as
sole writers, but:
- `scripts/land_all_results.py:114` writes `GAP_INDEX` (the tracked dict) **plus**
  a desktop mirror copy (a *third* copy → mirror-drift risk).
  **RESOLVED 2026-10-28**: banner amended — `build_gap_index.py` = structural writer,
  `land_all_results.py` = field-update writer (named fields only); dead Desktop-mirror
  branch removed (target never existed).
- ~~`scripts/d_grade_metadata.py:182-183` writes the enriched file~~ **RETRACTED on
  deeper dive**: `d_grade_metadata.py` enriches D-grade *evidence-edge* files only
  and never touches `bcc_gap_index.enriched.json`. No action needed; noted in the
  `gap_metadata.py` banner.

### MS2 (M) — gap stores themselves are clean (verified, no action)
Tracked = 62, enriched = 66, enriched ⊃ tracked (all tracked IDs present, +4 new),
no drift. Filters read the enriched store (4/66 ready). The +4 delta is the known
R-series addition, not divergence.

### MS3 (H) — SHA256SUMS coverage ≠ its claim
The manifest covers `research/` only. It does **not** cover `.bcc_audit/01_verified/`
(the actual proof-layer raws!), the cosmos outputs, or `scripts/`. The asserted
`sha_verified` tier therefore protects the *analysis* directory while the *evidence*
directory it vouches for sits outside the manifest. Extend the manifest to
`01_verified/` + cosmos outputs, or scope its claim to research/.

### MS4 (M) — cosmos outputs live outside the repo, unversioned
`bcc_cosmos_build.py` writes to `C:/Users/clint/BCC_COSMOS/` (graph JS + manifest).
Nothing in the repo pins or versions these artifacts. If that path is lost or
edited, the R5 regen is unrepeatable from the repo alone. Recommend: repo-local
build outputs (or at minimum a manifest copy in-repo), consistent with how the
proof layer is kept in `.bcc_audit`.

### MS5 (L, known) — week-memo outcomes appendix deferred pending worktree review
`REDO_NECESSITY_AUDIT_2026-10-28.md` still describes pre-R-series state. Already
flagged; unchanged.

## Priority order
1. MS1 (writer rule) + LG2 (59/81 re-proof) — integrity of stores and money narrative.
2. MS3 (manifest coverage) + MS4 (cosmos versioning) — make verification claims true.
3. LG5 (120-edge tally) + LG1 (promotion/demotion pass) — close the R-series loop.
4. LG3 (119 L3 rule — needs your ruling: does a court opinion clear L3?) + LV1 (one line).
5. LG4 (delete or wire orphan schema) + MS5 (memo appendix, with worktree review).
