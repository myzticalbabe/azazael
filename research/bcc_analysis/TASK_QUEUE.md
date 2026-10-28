# BCC Investigation Reprocessing Task Queue
**Generated:** 2026-10-27  
**Status:** Prioritized, sequential, with dependencies noted

---

## Phase 1: Enrich Existing Corpus (No External Dependencies)

### 1.1 Enrich Gap Index → `bcc_gap_index.enriched.json`
- **Script:** `scripts/gap_metadata.py`
- **Input:** `scripts/bcc_gap_index.json`
- **Output:** `bcc_gap_index.enriched.json`
- **Action:** Run `enrich_gap_dispositions()` on all 62 gaps
- **Depends on:** None
- **Estimated:** 5 min

### 1.2 Enrich Lead Inference → Regenerate `bcc_lead_inference_evidence.json`
- **Script:** `scripts/lead_metadata.py`
- **Input:** Run `bcc_lead_inference.py` first, then enrich
- **Output:** `bcc_lead_inference_evidence.enriched.json`
- **Action:** Run `bcc_lead_inference.py` → `enrich_leads()`
- **Depends on:** 1.1 (gap IDs referenced by leads)
- **Estimated:** 10 min

### 1.3 Enrich Person Edges → Apply D-grade Schema
- **Script:** `scripts/d_grade_metadata.py`
- **Input:** `scripts/bcc_person_edges.json` → extract `edges` array
- **Output:** `bcc_person_edges.enriched.json`
- **Action:** Run `enrich_d_grade_edges()` on 4 edges
- **Depends on:** 1.1 (for universe/topic alignment)
- **Estimated:** 5 min

### 1.4 Regenerate Splink Linkage + Enrich
- **Script:** `scripts/bcc_splink_linkage.py` (lower threshold) → `d_grade_metadata.py`
- **Input:** Same sources as original splink
- **Output:** `bcc_splink_linkage.enriched.json`
- **Action:** Lower threshold to 0.65, regenerate clusters, then enrich
- **Depends on:** 1.1 (for gap/lead cross-reference)
- **Estimated:** 15 min

---

## Phase 2: Process New Web Sources (Sequential, Each Creates Metadata)

### 2.1 Process PA Courts PDF (898 MDA 2017)
- **Source:** `research/bcc_analysis/fwa_opinion_898_mda_2017.pdf`
- **Creates:** Gap entries, Lead entries, Edge entries
- **Metadata:** Full D-grade + Gap + Lead schemas
- **Key extractions:** Court ruling details, FWA policy, BCC v Community Care facts, docket 15-14644
- **Depends on:** Phase 1 complete (schemas validated)
- **Estimated:** 20 min

### 2.2 Process CourtListener HTML
- **Source:** `research/bcc_analysis/fwa_opinion_courtlistener.html`
- **Creates:** Cross-validation leads for PDF facts
- **Metadata:** Lead schema (verification_method: cross_layer_pass)
- **Key extractions:** Same case, different format, citation graph
- **Depends on:** 2.1
- **Estimated:** 10 min

### 2.3 Process BCC Annual Report 2024-25
- **Source:** `research/bcc_analysis/BCC_Annual_Report_24-25.pdf`
- **Creates:** Financial gaps, governance leads, person edges (board/staff)
- **Metadata:** Gap + Lead + D-grade schemas
- **Key extractions:** 251,868 clients, board roster, financials, CEO Christine Axford, board chair Joe Plageman
- **Depends on:** 2.2
- **Estimated:** 25 min

### 2.4 Process GovTribe Grants (2 HUD CoC)
- **Source:** `research/bcc_analysis/govtribe_grants.json`
- **Creates:** Funding gap updates, COCA→BCC/TASC edges
- **Metadata:** Gap + D-grade schemas
- **Key extractions:** $113K (Nov 2024), $91K (Apr 2024), HUD CoC program
- **Depends on:** 2.3
- **Estimated:** 10 min

### 2.5 Process News Articles
- **Source:** `research/bcc_analysis/news_articles.json`
- **Creates:** Verification leads, public record flags
- **Metadata:** Lead schema (verification_method: manual_review)
- **Key extractions:** Annual report public release, grant announcements
- **Depends on:** 2.4
- **Estimated:** 10 min

---

## Phase 3: Cross-Validation & Actionable Outputs

### 3.1 Run Gap Action Filter
- **Script:** `gap_metadata.filter_for_action()`
- **Input:** Enriched gaps from 1.1 + 2.1-2.5
- **Output:** `gaps_ready_for_action.json`
- **Action:** Identify records requests to execute
- **Depends on:** All Phase 1 + Phase 2 complete
- **Estimated:** 2 min

### 3.2 Run Lead Verification Filter
- **Script:** `lead_metadata.filter_for_verification()`
- **Input:** Enriched leads from 1.2 + 2.1-2.5
- **Output:** `leads_ready_for_verification.json`
- **Action:** Prioritize cross-validation work
- **Depends on:** 3.1
- **Estimated:** 2 min

### 3.3 Run Edge Press Pull Filter
- **Script:** `d_grade_metadata.filter_for_press_pull()`
- **Input:** Enriched edges from 1.3 + 1.4 + 2.1-2.5
- **Output:** `edges_ready_for_press_pull.json`
- **Action:** Identify press/threshold pulls
- **Depends on:** 3.2
- **Estimated:** 2 min

### 3.4 Run Audit Loop Recovery Filter (if audit data available)
- **Script:** `audit_loop_metadata.filter_for_recovery()`
- **Input:** Audit loop data from `audit_loop_liveness.py`
- **Output:** `loops_needing_recovery.json`
- **Action:** Identify system health interventions
- **Depends on:** 3.3 (optional, independent)
- **Estimated:** 5 min

### 3.5 Generate Unified Action Report
- **Output:** `BCC_REPROCESSING_ACTION_REPORT.md`
- **Content:** All filter outputs + next steps + responsible parties
- **Depends on:** 3.1-3.4
- **Estimated:** 5 min

---

## Execution Order Summary

```
1.1 → 1.2 → 1.3 → 1.4 → 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 3.1 → 3.2 → 3.3 → 3.4 → 3.5
```

**Total Estimated Time:** ~2 hours  
**Blocking Dependencies:** Sequential within phases, Phase 2 depends on Phase 1, Phase 3 depends on Phase 1+2

---

## Ready-to-Run Commands

```bash
# Phase 1
cd C:\Azazael\azazael
python scripts\gap_metadata.py scripts\bcc_gap_index.json -o bcc_gap_index.enriched.json
python scripts\bcc_lead_inference.py
python scripts\lead_metadata.py bcc_lead_inference_evidence.json -o bcc_lead_inference_evidence.enriched.json
python -c "import json; d=json.load(open('scripts/bcc_person_edges.json')); json.dump(d['edges'], open('person_edges_raw.json','w'))"
python scripts\d_grade_metadata.py person_edges_raw.json -o bcc_person_edges.enriched.json

# Phase 2-3: Manual scripting for PDF/HTML processing
```

---

## Notes
- All scripts use Python 3.15t (GIL sidecar): `C:\Azazael\.venvs\py315\Scripts\python.exe`
- LaneMessageBoard updates after each major step
- Engram/PMB recording for decisions
- CourtListener HTML needs parsing (BeautifulSoup)
- PDF extraction: pdfplumber or PyMuPDF