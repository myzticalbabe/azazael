# BCC Investigation Standards Audit Report
**Date:** 2026-10-27  
**Status:** Incongruent — multiple standards across corpus

---

## Executive Summary

The BCC investigation corpus is a **palimpsest of standards** built over months with evolving schemas. Early artifacts (Aug-Sep) lack metadata fields that new schemas require. Recent artifacts (Oct) have partial metadata. New web sources found today are downloaded but not yet processed through any schema.

**Verdict:** Full corpus reprocessing required through current schemas.

---

## Component Audit

### 1. Gap Index (`scripts/bcc_gap_index.json`) — 62 gaps
| Metadata Field | Present | Missing | Standard |
|---|---|---|---|
| `topic` | 62/62 | 0 | ✅ Original |
| `disposition` | 62/62 | 0 | ✅ Original |
| `records_action` | 0/62 | 62 | ❌ New schema |
| `unblocker` | 0/62 | 62 | ❌ New schema |
| `evidence_completeness` | 0/62 | 62 | ❌ New schema |
| `corroboration_count` | 0/62 | 62 | ❌ New schema |
| `last_advanced` | 0/62 | 62 | ❌ New schema |

**Disposition Distribution:**
- OPEN: 26
- OPEN (advanced): 12
- OPEN (advanced Sep 6): 7
- RESOLVED: 9
- EXEC-READY: 2
- OPEN-MONITOR: 2
- BLOCKED: 1
- RESOLVED (Sep 4): 1
- OPEN (UNVERIFIED source): 1

### 2. Lead Inference (`scripts/bcc_lead_inference.py`) — 8 leads generated
| Field | Present | Missing | Standard |
|---|---|---|---|
| `id`, `class`, `title`, `basis`, `gap_refs`, `action`, `integrity_note` | 8/8 | 0 | ✅ Original |
| `corroboration_layers` | 0/8 | 8 | ❌ New schema |
| `records_action` | 0/8 | 8 | ❌ New schema |
| `verification_method` | 0/8 | 8 | ❌ New schema |
| `evidence_strength` | 0/8 | 8 | ❌ New schema |
| `triage_priority` | 0/8 | 8 | ❌ New schema |

### 3. Person Edges (`scripts/bcc_person_edges.json`) — 4 edges
| Metadata Field | Present | Missing | Standard |
|---|---|---|---|
| `source`, `target`, `type`, `detail`, `evidence` | 4/4 | 0 | ✅ Original |
| `grade` | 0/4 | 4 | ❌ New schema (D-grade) |
| `confidence_score` | 0/4 | 4 | ❌ New schema |
| `source_type` | 0/4 | 4 | ❌ New schema |
| `universe` | 0/4 | 4 | ❌ New schema |
| `verifier` | 0/4 | 4 | ❌ New schema |
| `tier_evidence` | 0/4 | 4 | ❌ New schema |
| `priority` | 0/4 | 4 | ❌ New schema |

### 4. Splink Linkage (`scripts/bcc_splink_linkage.json`) — 0 clusters
- File exists but 0 clusters at threshold 0.75
- Member fields: `source`, `name` only
- Missing: `match_probability`, `grade`, `confidence_score`, `source_type`, `universe`, `verifier`, `tier_evidence`, `priority`

### 5. New Web Sources (Downloaded Today, Unprocessed)
| Source | Path | Status |
|---|---|---|
| PA Courts PDF (898 MDA 2017) | `research/bcc_analysis/fwa_opinion_898_mda_2017.pdf` | ✅ Downloaded (243KB) |
| CourtListener HTML | `research/bcc_analysis/fwa_opinion_courtlistener.html` | ✅ Fixed (was 0 bytes) |
| BCC Annual Report 2024-25 | `research/bcc_analysis/BCC_Annual_Report_24-25.pdf` | ✅ Downloaded (455KB) |
| GovTribe Grants (2 HUD CoC) | `research/bcc_analysis/govtribe_grants.json` | ✅ Saved |
| News Articles (Annual report + grants) | `research/bcc_analysis/news_articles.json` | ✅ Saved |

---

## Standards Congruity Matrix

| Component | Original Standard | D-grade Schema | Gap Schema | Lead Schema | Audit Loop Schema |
|---|---|---|---|---|---|
| Gap Index | ✅ | — | ❌ (0%) | — | — |
| Lead Inference | ✅ | — | — | ❌ (0%) | — |
| Person Edges | ✅ | ❌ (0%) | — | — | — |
| Splink Linkage | ✅ | ❌ (0%) | — | — | — |
| New Web Sources | N/A | ❌ | ❌ | ❌ | ❌ |

---

## Required Reprocessing Actions

### Phase 1: Enrich Existing Corpus
1. **Gap Index** → Run `gap_metadata.enrich_gap_dispositions()` on all 62 gaps
2. **Lead Inference** → Run `lead_metadata.enrich_leads()` on all 8 leads (regenerate output)
3. **Person Edges** → Apply `d_grade_metadata.enrich_d_grade_edges()` to all 4 edges
4. **Splink Linkage** → Regenerate with lower threshold, then enrich with D-grade schema

### Phase 2: Process New Sources
1. **PA Courts PDF** → Extract text, create gap/lead/edge entries with full metadata
2. **CourtListener HTML** → Parse for additional facts, cross-reference with PDF
3. **BCC Annual Report** → Extract financial data, update T1 report, create gaps/leads
4. **GovTribe Grants** → Add to funding gaps, create COCA→BCC/TASC edge metadata
5. **News Articles** → Extract new facts, create leads for verification

### Phase 3: Cross-Validation
1. Run `filter_for_action()` on enriched gaps → identify records requests
2. Run `filter_for_verification()` on enriched leads → prioritize cross-validation
3. Run `filter_for_press_pull()` on enriched edges → identify press pulls
4. Run `filter_for_recovery()` on audit loops (if audit loop data available)

---

## Metadata Schema Compliance Target

All four schemas share the **common pattern**:
- Fixed vocabularies (closed sets)
- Computed priorities (not stored)
- Single actionable filter per schema
- L2 boundary explicitly documented

**Target:** 100% of corpus entities enriched with their respective schema fields.

---

## Next Steps

1. Run enrichment scripts on all existing corpus components
2. Process 5 new web sources through appropriate schemas
3. Cross-validate enriched corpus against each other
4. Update LaneMessageBoard with actionable items from filters

**Estimated effort:** 2-3 passes over corpus with current scripts.