# Metadata Schemas Index

## Four Minimal Schemas (L1 Sweet Spots)

| Schema | Entity Type | File | Fields | Actionable Filter |
|---|---|---|---|---|
| **D-grade edges** | Evidence edges | `d_grade_metadata.py` | 12 | `filter_for_press_pull()` |
| **Gap dispositions** | Investigation gaps | `gap_metadata.py` | 11 | `filter_for_action()` |
| **Lead triage** | Investigation leads | `lead_metadata.py` | 11 | `filter_for_verification()` |
| **Audit loops** | System loops | `audit_loop_metadata.py` | 12 | `filter_for_recovery()` |

---

## Common Pattern (all four)

```python
# 1. Fixed vocabularies (closed sets)
TYPES = {"portal", "html", "pdf", "json", "api", "manual"}

# 2. Computed, not stored
priority = compute_priority(entity)  # derived from evidence

# 3. Single actionable filter per schema
ready = filter_for_press_pull(edges)
ready = filter_for_action(gaps)
ready = filter_for_verification(leads)
ready = filter_for_recovery(loops)
```

---

## Invariant Checklist (enforced by architecture)

- [ ] **Falsifiability**: Every field testable against ≥3 trajectories
- [ ] **Boundedness**: L2 boundary explicitly lists what's NOT covered
- [ ] **Evidence-linkage**: Every field maps to specific evidence source
- [ ] **Actionability**: Schema changes a CLASS of decisions via filter
- [ ] **No Heaven**: No maximal schema, no L3+ rungs
- [ ] **Stop rule**: Instance → rule → applicability → STOP

---

## Usage

```python
# D-grade edges
from scripts.d_grade_metadata import enrich_d_grade_edges, filter_for_press_pull
edges = enrich_d_grade_edges("edges.json")
ready = filter_for_press_pull(edges)

# Gap dispositions
from scripts.gap_metadata import enrich_gap_dispositions, filter_for_action
gaps = enrich_gap_dispositions("bcc_gap_index.json")
ready = filter_for_action(gaps)

# Lead triage
from scripts.lead_metadata import enrich_leads, filter_for_verification
leads = enrich_leads("bcc_lead_inference_output.json")
ready = filter_for_verification(leads)

# Audit loops
from scripts.audit_loop_metadata import enrich_audit_loops, filter_for_recovery
loops = enrich_audit_loops("audit_entries.json")
ready = filter_for_recovery(loops)
```

---

## Why Four Schemas, Not One

| Attempted Merge | Why It Fails |
|---|---|
| Edge + Gap schema | Edges are relationships; gaps are questions. Different evidence, different actions. |
| Lead + Loop schema | Leads are investigation hypotheses; loops are system health. Different lifecycles. |
| All four | 80% fields optional per entity; no single evidence source validates all; no filter drives decisions for all. |

**Each entity type gets its own minimal schema at its L1 sweet spot. The ladder stops at L2 (applicability boundary).**