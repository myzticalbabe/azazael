# REDO NECESSITY AUDIT — why the new data types force a re-derivation (2026-10-28)

**Trigger:** Kilo's Oct-27 additions (4 docs, `research/bcc_analysis/`, enriched JSONs,
modified `scripts/`) introduce new node types, new edge types, new metadata fields, and
new filter contracts. This audit maps every addition to the layer it invalidates and
specifies the redo in dependency order. Verified against working-tree files this date;
all paths repo-relative unless noted.

## 1. Inventory of the new data types

| # | Addition | Shape | Status |
|---|----------|-------|--------|
| N1 | 4 metadata schemas (D-grade×12 fields, gap×11, lead×11, audit-loop×12) + index + 4 filter contracts (`filter_for_press_pull`, `filter_for_action`, `filter_for_verification`, `filter_for_recovery`) | `docs/D_GRADE_METADATA_SCHEMA.md`, `METADATA_SCHEMAS_INDEX.md`; code in `scripts/gap_metadata.py`, `lead_metadata.py`, `d_grade_metadata.py`, `audit_loop_metadata.py` | schemas specified; filters exist |
| N2 | Enriched gap store: 66 gaps × 13 fields (`records_action`, `unblocker`, `evidence_completeness`, `corroboration_count`, `last_advanced`, `urgency` + originals) incl. 4 new gaps 63–66 | `bcc_gap_index.enriched.json` (root, untracked) | built, unwired |
| N3 | Tracked gap store mutation: `scripts/bcc_gap_index.json` +540 lines (dict keyed 1..N, original schema) | tracked, modified, uncommitted | forked from N2 |
| N4 | 4 new person edges (BCC→PA Superior Court, BCC→HUD, BCC→NextGen, BCC→Berks MH/DD), all grade D with full N1 metadata | `bcc_person_edges.enriched.json` (root, untracked; tracked `scripts/bcc_person_edges.json` is dict×5, Oct-2 vintage) | built, unwired |
| N5 | 4 new leads LEAD-09–12 (898 MDA opinion, HUD CoC grants, Annual Report EHR, Mobile Med) | prose in `research/bcc_analysis/BCC_REPROCESSING_ACTION_REPORT.md` + `scripts/bcc_lead_inference_evidence.enriched.json`; tracked `bcc_lead_inference_evidence.json` still LEAD-08-only, old 8-field schema | half-materialized |
| N6 | Person-ID canonicalization: `person_*` IDs, PERSON_ID_TO_NAME (15 entries), surname-fold aliasing, roster injection (`person_goodman`, `person_himeback`) | uncommitted diff in `scripts/bcc_open_tasks_join.py` (+55) only | lives in one script |
| N7 | Splink re-platform: bccpipe venv (splink 5 + duckdb on GIL-3.14), `--sna-results` arg, TRUE_SNA + PERSON_EDGES constants | uncommitted diff in `scripts/bcc_splink_linkage.py` (+27/−23 shown) | re-pointed, not re-run |
| N8 | SNA v3 file: `bcc_network_sna_results_v3.json` — `persons: {n_persons: 0}`, communities = **Azazael codebase modules** (CODEX/ORCHESTRATION/CORE…), not BCC entities | root, untracked | wrong graph for BCC reads |
| N9 | Pattern catalog: 1742 patterns (852 AST, 679 import, 28 decorator, 160 graph-motif, 7 bcc_network_motif, 8 training, 8 memory-event), created 2026-10-28T07:58 | `research/master_pattern_catalog.json` (untracked) | no consumer |
| N10 | META_HUBS_REDO (14-technique hub analysis on 118 edges) + METHOD self-grade (FAIL on pre-reg/ACH/negative-controls) | `docs/META_HUBS_REDO.md`, `METHOD_SELF_GRADE_META_HUBS.md` | conclusions unanchored |
| N11 | Orchestrator migration to trainers_v2 (GRPO + offline cycles, EXCLUDED_SOURCES +V2) | uncommitted diff in `scripts/run_training_orchestrator.py` (+71/−…) | **contains double-wrap bug** (see §3.7) |

## 2. Why each addition forces a redo (layer by layer)

### 2.1 Gap layer is forked — R0 blocker
Two canonical gap stores now disagree in shape, count, and schema:
`scripts/bcc_gap_index.json` (dict, 62+ gaps, original fields, +540 uncommitted lines) vs
`bcc_gap_index.enriched.json` (list, 66 gaps × 13 fields). Consumers split:
`run_final_filters.py` reads the enriched file; `process_new_sources.py` probes it behind
`os.path.exists` (silent skip if absent); `bcc_lead_inference.py` docstring still cites the
tracked file ("gap ledger (62)"). No artifact may cite "the gap index" until one store is
declared canonical and the other regenerated from it. The 4 new gaps (63–66: 898 MDA
opinion, HUD CoC $204,870, NextGen EHR, Mobile Med) exist only in the enriched fork.

### 2.2 Lead layer is half-materialized — nothing to filter
`filter_for_verification` (N1) has no valid input: the tracked evidence file holds only
LEAD-08 under the old 8-field schema, and `render_bcc_lead_findings.py` still renders that
file ("1 evidence-grounded lead + watchdog" subtitle baked in). LEAD-09–12 are prose in the
action report; `bcc_lead_inference.py` lists `bcc_network_sna_results_v3.json` and
`bcc_record_linkage.json` as input layers but the reprocessing report marks splink linkage
"SKIPPED — source data unavailable" while the linkage script was simultaneously re-platformed
(N7) — the skip rationale and the re-platforming are unreconciled. Redo: materialize
LEAD-09–12 as records in the new 11-field schema, regenerate the evidence file, re-render.

### 2.3 Person layer is void at the exact point new consumers assume it
N8's `persons` block is `{n_persons: 0, connected: 0}`. Against that void:
- N6 folds SNA full-name labels into roster entries **by surname** — folding zero persons.
- N4's 4 new org edges reference person-adjacent nodes (Court, HUD, NextGen, MH/DD) with
  `verifier`/`tier_evidence` values drawn from universes (UJS, DOS, courtlistener) whose
  pulls are the retired-lane DOS items — provenance for the D-grade metadata fields
  (`retrieval_method`, `confidence_score`, `retrieval_date`) is asserted, not attached.
- The enriched person edges (N4) duplicate 4 pre-existing edges (plageman→krause/bromley,
  axford→little, malley→axford) now re-graded D with metadata, while the tracked
  `scripts/bcc_person_edges.json` (Oct-2, dict×5) still carries whatever grades it had —
  same pairs, two grades, two files.
Redo: re-run splink on the bccpipe venv (N7) to populate the person layer, then re-derive
N6/N4/N8 from it — not the reverse.

### 2.4 The edge layer grew 118 → 122 everywhere except the proof layer
N4 adds 4 edges. The proof layer (`.bcc_audit/01_verified/network_edges_proofed.json`,
separate repo) still holds 118 with floor grades L3-66/L2-3/L1-40/L0-9; the Oct-28 floor
audit and the 12-edge verified→lead demotion both cover exactly those 118. The 4 new edges
have **no proof blocks, no raw shas, no floor grades** — they are D-grade by assertion.
META_HUBS_REDO's technique reads (KPP seed set {BCC,PC,COCA,UWBERKS,QUEST}, BCC=36-component
fragmentation risk) were computed on the 118-edge graph and must be recomputed at 122 once
the new edges are proofed; hub ranks can shift (HUD/NextGen/MH-DD attach directly to BCC,
the highest-degree node — degree-weighted reads like PageRank are the most sensitive).

### 2.5 SNA v3 cannot anchor any BCC conclusion
`communities[0]` (n=302) enumerates Azazael source files; `core_clique`/`rankings` inherit
that population. Any BCC-side claim citing "SNA v3 communities" cites a codebase-import
graph. Meanwhile `bcc_lead_inference.py`'s docstring describes SNA v3 as a "48-node
documented network" — the docstring describes the intended file, not the actual one. The
BCC-side SNA (centrality/money-chain/timeline reports in `.bcc_audit`) is unaffected but
also unextended: no BCC SNA has ever been computed at 122 edges. Redo: compute BCC SNA on
the proofed 122-edge graph; either replace or rename the current v3 file so the two graphs
cannot be confused again.

### 2.6 The pattern catalog floats free
N9's 7 `bcc_network_motif` patterns and 8 `training_pattern` patterns have no consumer:
no script imports `master_pattern_catalog.json` (consumer grep §4 confirms), and the
14-technique catalog applied in META_HUBS_REDO is a different catalog (task #45616) with no
mapping to the 1742 mined patterns. Until `by_source_category` is joined against the
technique catalog, the catalog cannot justify or extend any BCC read. Redo: join them or
quarantine the catalog out of the BCC evidence chain.

### 2.7 The training leg is broken at the seam
N11's `run_training_orchestrator.py` diff double-wraps: `ctx = create_trainer(...)` already
returns a `GRPOTrainerV2`/`RLTrainLoopV2` instance, then `GRPOTrainerV2(ctx)` /
`RLTrainLoopV2(ctx)` passes a trainer where a `TrainerContext` is expected. Also drops the
`snapshot_anchor("orchestrated")` call (V2 has no such method — confirm deliberate, else
restore via `gather`). Kilo wrote against pre-commit trainers_v2; the committed `b4d37cd1`
changed the factory (case-insensitive algo resolution), the step hook (real `BaseCallback`),
and `_evaluate` (gymnasium-0.26). Redo: rebase N11 onto `b4d37cd1`, fix the double-wrap,
re-run GRPO + offline cycles.

### 2.8 The hub conclusions are unanchored by their own grading
The METHOD self-grade (N10) records FAIL on (a) pre-registered method, (b) ACH, (c)
negative controls. Under METHOD-STANDING-001 those are load-bearing: the KPP seed set, the
437K-gap explanation, and the no-self-dealing read are all single-hypothesis. The redo of
the analysis must include the self-grade's own patch list (pass-criteria section, ACH
tables for hub ranking/437K/self-dealing, degree-shuffled nulls with z-scores, one
known-bad negative-control `verify_proofs` run) — otherwise the 122-edge recompute repeats
the same structural defect at higher cost.

## 3. Redo specification (dependency order)

- **R0 — Canonicalize stores.** Declare one gap store canonical (recommend: enriched list
  schema; regenerate the tracked dict from it or retire it). Materialize LEAD-09–12 as
  11-field records; regenerate `bcc_lead_inference_evidence.json`; re-render findings.
  Single-writer rule per store from here on.
- **R1 — Person layer.** Re-run splink on bccpipe venv (N7 as documented); populate SNA
  persons; reconcile N6 canonicalization into a registry both scripts import (not a
  per-script constant); resolve N4-vs-tracked grade duplications pair by pair.
- **R2 — Edge ingestion.** Write proof blocks + raws for the 4 new edges (LEAD grade,
  D evidentiary tier); attach `retrieval_method`/`confidence_score`/`retrieval_date`
  provenance per N1 schema instead of asserting it.
- **R3 — Floor + SNA at 122.** Re-run floor grader (mechanical once R2 lands); compute BCC
  SNA on the 122-edge proofed graph; recompute KPP/fragmentation/PageRank reads;
  fix-or-rename SNA v3 so the codebase graph can never be cited as BCC evidence.
- **R4 — Method patches.** Apply N10's own patch list (pre-reg thresholds, ACH tables,
  shuffled nulls, negative control) before publishing any 122-edge conclusion.
- **R5 — Downstream regeneration.** Cosmos build, open-tasks join, gephi launcher, lead
  findings render, board packets — all re-run against R0–R3 outputs; docstrings updated
  to name actual files (fix the "48-node" description).
- **R6 — Training seam.** Fix N11 double-wrap, rebase onto `b4d37cd1`, re-run cycles.
- **R7 — Catalog join or quarantine.** Map N9 motifs to the technique catalog or exclude
  the catalog from the evidence chain explicitly.

## 4. Consumer map (how verified)

`grep -rln` over `scripts/`, `src/`, `barta-employment-gui/` for the six store filenames
→ 18 consuming scripts. Read in full: `bcc_lead_inference.py` (docstring layer list),
`bcc_cosmos_build.py` (reads both person-edge files), `render_bcc_lead_findings.py`
(pinned to old evidence file + baked subtitle), `run_final_filters.py` (reads enriched
gap + `scripts/bcc_lead_inference_evidence.enriched.json` + enriched person edges),
`process_new_sources.py` (exists-guarded reads = silent skips). Existence checks: enriched
lead file present at both root and `scripts/`; `_gap_status.json` absent (listed as a lead
layer — another void input); tracked person edges Oct-2 vintage.

## 5. What does NOT need redo

The 118-edge floor grades and the 12-edge demotion stand for those 118 edges. The SB3
worm-identity migration (`b4d37cd1`, 16 new + 66 existing tests green). The PY2025 5500
watch (still unfiled, re-checked Oct-28). The floor tooling itself (`floor_audit.py`,
`floor_demote.py`, `verify_proofs.py`) reruns mechanically once R2 lands.

## 6. Open decisions (operator)

1. Canonical gap store: enriched list vs tracked dict (recommend enriched list).
2. SNA v3 file: replace with BCC-graph computation or rename to `*_codebase_*`.
3. Pattern catalog: join to technique catalog or quarantine.
4. Retired-lane DOS pulls underlying N4/N5 provenance fields: re-source or flag as
   asserted-until-pulled.

## 7. Outcomes appendix (2026-10-28 — all R-series items implemented)

Operator rulings received: keep both gap stores (single-writer rule per store);
rename-now/recompute-after-R1–R2; join motifs to catalog; re-source the DOS pulls.
- **R0** — ownership banners in `build_gap_index.py` (structural) + `gap_metadata.py`
  (enriched sole writer); MS1 amendment: `land_all_results.py` is the field-update
  writer (named fields only, dead Desktop-mirror branch removed), `d_grade_metadata.py`
  confirmed as edge-enrichment only (never wrote the gap store — earlier claim retracted).
- **Rename** — `bcc_network_sna_results_v3.json` → `bcc_codebase_import_sna_v3.json`,
  4 consumers re-pointed, zero old-name references.
- **R7** — `research/bcc_motif_technique_join.json` (7 motifs × 14 techniques, 98 cells),
  counts flagged cosmos-derived until proof-layer re-derivation (G12).
- **DOS re-source** — GovTribe/990/opinion/annual-report provenances verified against held
  raws; `00_raw/SHA256SUMS` (202 files, all green) + `research/.../SHA256SUMS` scope note
  + in-repo `cosmos_snapshot_2026-10-28/` (manifest-verified).
- **R2** — HUD/NextGen deduplicated in place (were parallel to edges 67/79); 118 BERKS_MHDD
  + 119 BCC-appellee added (119 beam-tagged 1.1). 8 UNPROOFED + 1 PARTIAL proof-states
  labeled (LG2); 81 carries TASC-990 corroboration (direction still unproven, stays lead).
- **R1** — splink 5 re-run on bccpipe: 71 records, 11 clean clusters @0.75.
- **R3** — SNA @120 edges: BCC deg 62, btw 0.8728, 36→38 components; UWBERKS downgraded
  (z=0.7, funder-hub not broker). Grade tally @120: **verified 49 / lead 70 / cut 1**.
- **LG1 promotion pass** — 106 (SFI) promoted lead→verified (verifier-clean); 79 held
  (quote fails round-trip, OCR class); 119 promotion reverted (see LG3).
- **R4** — pre-reg + 3 ACH tables + nulls + passing negative control.
- **R5** — filters green, renderer on enriched lead store, join + cosmos rebuilt.
- **Verifier hardening** — `verify_proofs.py` + `beam1_apply.py` now accept dict-form
  paired_raws (R2's rich form crashed the run once a verified edge carried one).
- **LG4** — `audit_loop_metadata.py` quarantined to `scripts/_quarantine_LG4/` (orphan
  schema, zero consumers; revivable with rationale in README).
- **LV1** — UBO tally prose fixed in META_HUBS_REDO.md.

## 8. Rulings still needed (operator / kilo-beam lane)

1. **LG3 / 119 held-primary admission** — the Superior Court opinion PDF is a held copy,
   absent from the fetch log, so the verifier recomputes class U vs claimed tier A.
   Options: (a) admit held-primary raws to the fetch log with held-basis records,
   (b) add a verifier held-primary rule, (c) tier-A-aspiration with grade lead stands.
   Blocks 119's promotion; also affects every DOS-era held file. No fetch record was
   fabricated — the bar held.
2. **Retired-lane DOS pulls** (original §6.4) — unchanged, still operator call.
3. **Commit of `.bcc_audit`** — note: the repo root is `C:/Users/clint` (home); the proof
   layer is an untracked dir inside it. Committing needs an explicit home-repo decision.
