# Project Jaeger

**Azazael's Internal Tracer** — Consumes AOA `DelegationSpec` + `ArmResult`, emits spans within the tree. Not an OTLP client.

> "Jaeger as the tree's own tracer is accepted because it consumes AOA's `DelegationSpec` + `ArmResult` and turns them into spans **within AOA**, not export to external systems." — *JAEGER_BRIEF_2026-11-02.md*

---

## Decision (jaeger-000): Tracer of This Tree ✅

> **Accepted:** Jaeger as the tree's own tracer — consumes AOA's `DelegationSpec` + `ArmResult` → spans within AOA.  
> **Rejected:** Jaeger as thin OTLP client (duplicates OSS, no defect hit, would contribute to software not built against).

---

## What Jaeger Measures (and Refuses to Claim)

| Measures | Refuses to Claim |
|----------|------------------|
| `DelegationSpec` + `ArmResult` → span | Clinical validity of traces |
| Span with `provenance` (`arm_declared` vs `router_observed`) | Whether a delegation was *right* |
| `stale_after_s`, `age_s` for freshness | Clinical outcomes |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AOA Kernel                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Delegation  │───►│   Jaeger     │───►│   Span Store │  │
│  │    Spec      │    │   Tracer     │    │  (JSONL/OTLP)│  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ ArmResult    │    │  Jaeger      │    │  OTLP/JSONL  │  │
│  │ (provenance) │    │  Exporter    │    │  Export      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## What Jaeger Measures (and Refuses to Claim)

| Measures | Refuses to Claim |
|----------|------------------|
| `DelegationSpec` + `ArmResult` → span | Clinical validity of traces |
| Span with `provenance` (`arm_declared` vs `router_observed`) | Whether a delegation was *right* |
| `stale_after_s`, `age_s` for freshness | Clinical outcomes |
| `DelegationSpec.instruction`, `context`, `tools`, `model` | Whether a decision was *correct* |
| `ArmResult.provenance` (`arm_declared` vs `router_observed`) | User intent |

---

## Task Board (jaeger-000 → 003)

| Task | ID | Status | Description |
|------|----|--------|-------------|
| **jaeger-000** | 47192 | ✅ | **DECIDED**: Tracer of this tree (not OTLP client) |
| **jaeger-001** | 47193 | 🔄 | Scaffold `Project_JAEGER/` to `Project_CRADLE` shape |
| **jaeger-002** | 47194 | ⏳ | AOA-ARM integration: `BaseArm` + `@register_arm` + `_ARM_MODULES` |
| **jaeger-003** | 47195 | ⏳ | OTLP Export (transport AOA lacks; trace correlation field `DelegationSpec` lacks) |

**Blocking order:** jaeger-001..003 sit behind jaeger-000. jaeger-003 must not start until 001-002 complete.

---

## Quickstart

```bash
# Install
pip install -e ./Project_JAEGER

# Run tracer (consumes AOA DelegationSpec + ArmResult)
jaeger-tracer --config config.yaml

# Export spans (OTLP/JSONL)
jaeger-export --input spans.jsonl --output otlp
```

---

## Configuration

```yaml
# config.yaml
tracer:
  service_name: "azazael-jaeger"
  sample_rate: 1.0
  
exporter:
  type: "jsonl"  # or "otlp"
  endpoint: "spans.jsonl"
  batch_size: 100
  
span:
  stale_after_s: 300
  include_attributes: true
  include_events: true
```

---

## Span Format

```json
{
  "trace_id": "0af2e3c4d5f6a7b8",
  "span_id": "1a2b3c4d5e6f7890",
  "parent_span_id": null,
  "name": "delegation.execute",
  "kind": "INTERNAL",
  "start_time": "2026-11-03T03:15:22.123Z",
  "end_time": "2026-11-03T03:15:22.456Z",
  "attributes": {
    "delegation.id": "del-abc123",
    "delegation.instruction": "analyze user intent",
    "delegation.context": "user said: help me sleep",
    "delegation.tools": ["triage", "psyche_fit"],
    "delegation.model": "gpt-4",
    "arm.id": "arm-psyche-triage",
    "arm.capability": "crisis_detection",
    "arm.provenance": "arm_declared",
    "arm.result": "crisis",
    "arm.stale_after_s": 300,
    "azazael.delegation_spec": true,
    "azazael.arm_result": true
  },
  "events": [
    {"name": "delegation.received", "time": "2026-11-03T03:15:22.123Z"},
    {"name": "arm.dispatched", "time": "2026-11-03T03:15:22.124Z"},
    {"name": "arm.completed", "time": "2026-11-03T03:15:22.456Z"}
  ],
  "status": {"code": "OK"}
}
```

---

## Grimorie (Spellbook)

The **Grimorie** is Jaeger's spellbook — the definitive reference for every incantation (API), ward (validation), and ritual (workflow).

See [`grimorie/`](grimorie/) for the complete spellbook.

---

## Project Structure

```
Project_JAEGER/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── CONFIGURATION.md
├── grimorie/
│   ├── INDEX.md           # Master index
│   ├── INCANTATIONS.md    # API reference
│   ├── WARDS.md           # Validation rules
│   ├── RITUALS.md         # Workflows
│   ├── WARDS.md           # Protection spells
│   └── RUNES.md           # Configuration runes
├── src/
│   └── jaeger/
│       ├── __init__.py
│       ├── tracer.py      # Core tracer
│       ├── span.py        # Span types
│       ├── exporter.py    # OTLP/JSONL export
│       ├── context.py     # DelegationSpec + ArmResult
│       └── config.py      # Configuration
├── tests/
│   ├── test_tracer.py
│   ├── test_span.py
│   └── test_exporter.py
├── tools/
│   ├── jaeger_trace.py    # CLI tracer
│   └── jaeger_export.py   # CLI exporter
└── grimorie/              # The Spellbook
```

---

## License

CDDL-1.1 — see `LICENSE`.