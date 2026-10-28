# D-Grade Edge Metadata Schema

**Purpose**: Replace "more grades" with structured metadata for prioritization within D-grade tier.

## Schema (per edge)

| Field | Type | Required | Vocabulary | Description |
|-------|------|----------|------------|-------------|
| `edge_id` | string | yes | - | Unique identifier |
| `grade` | string | yes | `["D"]` | Always "D" for this module |
| `source_type` | string | yes | `portal`, `html`, `pdf`, `json`, `api`, `manual` | How the edge was sourced |
| `retrieval_method` | string | yes | `headed_chrome`, `headless`, `api_call`, `manual_copy`, `ocr` | Retrieval mechanism |
| `confidence_score` | float | yes | 0.0-1.0 | Model probability / OCR confidence / manual certainty |
| `retrieval_date` | string | yes | ISO date (YYYY-MM-DD) | When edge was retrieved |
| `universe` | string | yes | `UJS`, `DOS`, `IRS`, `campaign_finance`, `courtlistener`, `propublica`, `pacourts`, `splink`, `sna`, `local_html`, `manual` | Source universe/domain |
| `verifier` | string | yes | `splink`, `manual`, `named_entity`, `regex`, `headless_captcha` | Verification method |
| `tier_evidence` | array[string] | no | - | Evidence tags: `sha_verified`, `model_probability`, `sna_results_v3`, `networkx_graph`, `gap_index_v2`, `propublica_profile`, `watchdog_hits`, `canonical_names`, `manual_reviewed`, `court_opinion_pdf` |
| `status` | string | yes | `unsaved`, `saved_browser_view`, `gated_unverified`, `dossier`, `dormant` | Retrieval/save state |
| `priority` | integer | computed | 1-5 | Triage priority (computed) |
| `notes` | string | no | - | Free text |

## Priority Computation

```
priority = f(confidence_score, tier_evidence_count, verifier_strength, source_type_value)
range: 1-5 (5 = highest)
```

**Weights**:
- confidence_score: 40%
- tier_evidence completeness: 30%
- verifier strength: 20%
- source_type value: 10%

## Press Pull Filter

An edge is ready for press/threshold pull iff:
1. `grade == "D"`
2. `priority >= 3`
3. `status != "dormant"`
4. `universe` in `{UJS, DOS, IRS, campaign_finance, courtlistener, propublica, pacourts}`
5. `source_type` in `{portal, html, pdf, json}`

## Usage

```python
from scripts.d_grade_metadata import enrich_d_grade_edges, filter_for_press_pull

# Enrich edges with metadata (adds defaults, computes priority)
enriched = enrich_d_grade_edges("edges.json", "edges.enriched.json")

# Filter for press pull
ready = filter_for_press_pull(enriched)
```

## Example

```json
{
  "edge_id": "splink_001",
  "grade": "D",
  "source": "splink",
  "pair": ["Joseph Plageman Jr", "Joseph Plageman Jr."],
  "match_probability": 0.72,
  "source_type": "pdf",
  "retrieval_method": "headed_chrome",
  "confidence_score": 0.72,
  "retrieval_date": "2026-10-27",
  "universe": "pacourts",
  "verifier": "splink",
  "tier_evidence": ["sha_verified", "model_probability", "court_opinion_pdf"],
  "status": "dossier",
  "priority": 5,
  "notes": "PA Superior Court opinion 898 MDA 2017"
}
```

## Why This Replaces More Grades

| Old Approach | New Approach |
|--------------|--------------|
| Add D+, D-, D1, D2, D3... | Single D-grade + metadata |
| "Is it D or D+?" | "priority=5, confidence=0.85, verifier=splink" |
| 10+ grade letters | 1 grade + 10 metadata fields |
| No triage within tier | Computed priority 1-5 within tier |
| Manual sorting | Automated filter_for_press_pull() |

## Integration Points

- `bcc_splink_linkage.py` → emit edges with `source_type: pdf`, `verifier: splink`, `universe: pacourts`
- `bcc_network_sna.py` → emit edges with `source_type: json`, `verifier: named_entity`, `universe: UJS`
- `bcc_lead_inference.py` → emit edges with `verifier: named_entity`, `tier_evidence: watchdog_hits`
- `bcc_gap_index.json` → emit edges with `universe: IRS/DOS/campaign_finance`