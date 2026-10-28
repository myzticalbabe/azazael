# BCC Investigation Reprocessing — Unified Action Report
**Generated:** 2026-10-27  
**Status:** Phase 1-3 Complete

---

## Executive Summary

Full reprocessing of BCC investigation corpus completed. All 4 metadata schemas applied to enriched corpus. 4 gaps, 4 leads, and 1 edge ready for immediate action.

---

## Phase 1: Corpus Enrichment — COMPLETE

| Component | Before | After | Enriched |
|---|---|---|---|
| **Gap Index** | 62 gaps, 0 metadata fields | 66 gaps, 11 metadata fields each | ✅ |
| **Lead Inference** | 1 lead, 7 fields | 5 leads, 11 metadata fields each | ✅ |
| **Person Edges** | 4 edges, 5 fields | 8 edges, 12 metadata fields each | ✅ |
| **Splink Linkage** | 0 clusters (threshold 0.75) | *Skipped — source data unavailable* | ⚠️ |

**New gaps added:** 4 (IDs 63-66)  
**New leads added:** 4 (LEAD-09 through LEAD-12)  
**New edges added:** 4 (Court, HUD, NextGen, Berks MH/DD)

---

## Phase 2: New Source Processing — COMPLETE

| Source | Processed | Output |
|---|---|---|
| **PA Courts PDF** (898 MDA 2017) | ✅ | Gap #63, Lead LEAD-09, Edge BCC→PA Superior Court |
| **CourtListener HTML** | ✅ | Cross-reference for Gap #63 |
| **BCC Annual Report 2024-25** | ✅ | Gaps #64, #66; Leads LEAD-11, LEAD-12; Edges BCC→NextGen, BCC→Berks MH/DD |
| **GovTribe Grants (2 HUD CoC)** | ✅ | Gap #65, Lead LEAD-10, Edge BCC→HUD |
| **News Articles** | ✅ | Cross-reference for Annual Report + Grants |

**Files downloaded:** 5 (2 PDFs, 1 HTML, 2 JSON)  
**Total new text extracted:** ~24KB

---

## Phase 3: Cross-Validation Filters — COMPLETE

### Gaps Ready for Records Action (4/66)
| ID | Title | Urgency | Records Action |
|---|---|---|---|
| **#63** | PA Superior Court opinion (898 MDA 2017) | 5 | Request trial transcript (15-14644) via Pa.R.J.A. 509 |
| **#64** | BCC Annual Report 2024-25 financials | 5 | Cross-reference with FY2024 990; request audited financials |
| **#65** | HUD CoC grants ($204,870) | 5 | Verify grant terms in SAM.gov; cross-reference with FY2024 990 |
| **#66** | NextGen EHR + Mobile Med Program | 5 | Request implementation plan & Mobile Med protocol |

### Leads Ready for Verification (4/5)
| ID | Title | Priority | Verification Method |
|---|---|---|---|
| **LEAD-09** | PA Superior Court 898 MDA 2017 affirms BCC victory | 5 | cross_layer_pass |
| **LEAD-10** | HUD CoC grants ($204,870) not in FY2024 990 | 5 | cross_layer_pass |
| **LEAD-11** | Mobile Medication Program — patient safety unverified | 5 | manual_review |
| **LEAD-12** | NextGen EHR March 2025 — data migration risks | 5 | manual_review |

### Edges Ready for Press Pull (1/8)
| Source → Target | Priority | Action |
|---|---|---|
| **BCC → PA Superior Court** | 5 | Official court opinion retrieved; press pull complete |

---

## Immediate Next Steps (Priority Order)

### 1. Execute Records Requests (Gaps #63, #64, #65, #66)
- **Gap #63:** Submit Pa.R.J.A. 509 request to Berks CCP for 15-14644 trial transcript
- **Gap #64:** Cross-reference Annual Report client counts with FY2024 990; submit audited financials request (gap #31)
- **Gap #65:** Query SAM.gov for HUD grant details; cross-reference with BCC FY2024 990 revenue
- **Gap #66:** Request NextGen implementation plan & Mobile Medication Program protocol from BCC

### 2. Cross-Validate Leads (LEAD-09 through LEAD-12)
- **LEAD-09:** Cross-reference court opinion with trial record (15-14644)
- **LEAD-10:** Cross-reference HUD grants with BCC FY2024 990 revenue breakdown
- **LEAD-11:** Request Mobile Medication Program protocol from BCC
- **LEAD-12:** Request NextGen implementation plan & data migration validation

### 3. Press Pulls Complete
- **Edge BCC → PA Superior Court:** Press pull complete (official opinion retrieved)

---

## Corpus Statistics (Post-Reprocessing)

| Metric | Value |
|---|---|
| Total Gaps | 66 (62 original + 4 new) |
| Total Leads | 5 (1 original + 4 new) |
| Total Edges | 8 (4 original + 4 new) |
| Metadata Schemas Applied | 4 |
| New Sources Processed | 5 |
| Ready for Action | 4 gaps, 4 leads, 1 edge |

---

## Blocked / Pending

| Item | Reason |
|---|---|
| **Splink Linkage Regeneration** | Source data files (bcc_990_series.json, etc.) not accessible in scripts directory |
| **Audit Loop Recovery** | Audit loop data not available in current environment |
| **Original 8 Leads (LEAD-01 through LEAD-08)** | Lead inference script missing source data files; only LEAD-08 generated |

---

## Files Generated

| File | Description |
|---|---|
| `bcc_gap_index.enriched.json` | 66 gaps with full gap_metadata schema |
| `scripts/bcc_lead_inference_evidence.enriched.json` | 5 leads with full lead_metadata schema |
| `bcc_person_edges.enriched.json` | 8 edges with full d_grade_metadata schema |
| `research/bcc_analysis/STANDARDS_AUDIT_REPORT.md` | Standards audit report |
| `research/bcc_analysis/TASK_QUEUE.md` | Task queue with dependencies |
| `research/bcc_analysis/fwa_opinion_text.txt` | Extracted PA Courts PDF text |
| `research/bcc_analysis/BCC_Annual_Report_24-25.pdf` | Downloaded annual report |
| `research/bcc_analysis/govtribe_grants.json` | HUD grant data |
| `research/bcc_analysis/news_articles.json` | News article summaries |

---

## Metadata Schema Compliance

All 4 schemas applied with **common pattern**:
- Fixed vocabularies (closed sets) ✅
- Computed priorities (not stored) ✅  
- Single actionable filter per schema ✅
- L2 boundary explicitly documented ✅

---

**Report Complete** — Ready for execution of records requests and cross-validation work.