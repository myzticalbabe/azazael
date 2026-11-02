# OpenTelemetry Semantic Conventions for Agent Delegation

**Task:** Board 47212 / oss-otel-semconv
**Date:** 2026-11-02
**Status:** DRAFT — do not open a PR before jaeger-000 decides the project shape

## Overview

This document drafts OpenTelemetry semantic convention fields for **agent delegation** —
the act of one agent (the delegator) handing a task to another agent (the delegatee)
and receiving a result. The concrete instance is AOA's `DelegationSpec` and `ArmResult`.

### Justification

An operator judging a delegation needs to answer five questions:
1. **Why was this delegation made?** (selection reason)
2. **What evidence supported the choice?** (context snapshot)
3. **Where was it sent?** (tool address)
4. **What model was expected?** (model hint)
5. **Was the result trustworthy?** (provenance + staleness)

These five are derived from AOA's `DelegationSpec` (instruction, context, tools, model)
and `ArmResult` (provenance: arm_declared vs router_observed, stale_after_s).

## Attribute Table

### Delegation Spec Attributes (set at delegation time)

| Attribute | Type | Requirement Level | Description | Example |
|---|---|---|---|---|
| `agent.delegation.instruction` | string | Required | The selection reason — why this delegatee was chosen for this capability. Human-readable or machine-parseable. | `"capability=discover_worms, arm=azazael has highest success rate"` |
| `agent.delegation.context` | string (JSON) | Recommended | Evidence snapshot at delegation time — the state that informed the decision. Serialized as JSON. | `{"capability": "discover_worms", "available_arms": ["azazael", "codex"], "load": 0.3}` |
| `agent.delegation.arm_id` | string | Required | The delegatee's identity — which arm/agent received the delegation. | `"azazael"` |
| `agent.delegation.capability` | string | Required | The tool address — what capability was delegated. | `"discover_worms"` |
| `agent.delegation.model` | string | Recommended | Model hint — the model the delegator expected the delegatee to use. | `"qwen3.5-9b"` or `null` |

### Delegation Result Attributes (set at completion time)

| Attribute | Type | Requirement Level | Description | Example |
|---|---|---|---|---|
| `agent.delegation.provenance` | string (enum) | Required | Who attests to the result's freshness: `arm_declared` (the arm set produced_at itself) or `router_observed` (the router stamped it). | `"arm_declared"` |
| `agent.delegation.stale_after_s` | double | Recommended | Declared lifetime in seconds. None means unaged (no freshness claim). | `300.0` |
| `agent.delegation.produced_at` | string (ISO 8601) | Required | When the result was produced. | `"2026-11-02T05:30:00"` |
| `agent.delegation.is_stale` | boolean | Recommended | Whether the result is past its declared lifetime at observation time. Three states: true, false, null (undecidable). | `false` |
| `agent.delegation.status` | string (enum) | Required | Result status: `ok`, `error`, `partial`, `skipped`. | `"ok"` |

### Trace Correlation Attributes (for span linking)

| Attribute | Type | Requirement Level | Description | Example |
|---|---|---|---|---|
| `agent.delegation.trace_id` | string | Optional | W3C trace ID linking this delegation to its parent trace. | `"4bf92f3577b34da6a3ce929d0e0e4736"` |
| `agent.delegation.span_id` | string | Optional | W3C span ID for this delegation's span. | `"00f067aa0ba902b7"` |
| `agent.delegation.parent_span_id` | string | Optional | Parent span ID, enabling delegation chains. | `"00f067aa0ba902b6"` |

## Span Structure

A delegation produces a span with the following structure:

```
Span: agent.delegation
├── Attributes (delegation spec)
│   ├── agent.delegation.instruction
│   ├── agent.delegation.context
│   ├── agent.delegation.arm_id
│   ├── agent.delegation.capability
│   └── agent.delegation.model
├── Events
│   └── agent.delegation.completed
│       ├── agent.delegation.provenance
│       ├── agent.delegation.stale_after_s
│       ├── agent.delegation.produced_at
│       ├── agent.delegation.is_stale
│       └── agent.delegation.status
└── Links
    └── parent span (if parent_span_id is set)
```

## Justification for the Five Core Fields

1. **instruction (selection reason):** Without this, an operator cannot tell why a particular
   arm was chosen. "It was routed" is not actionable; "it was routed because it had the
   highest success rate for this capability" is.

2. **context (evidence snapshot):** The state at delegation time. Without this, a delegation
   that was correct at the time but wrong in retrospect cannot be distinguished from one
   that was wrong from the start.

3. **arm_id + capability (tool address):** Where the delegation went and what it asked for.
   Without these, the delegation is unaddressable — no monitor can route feedback to the
   right arm.

4. **model (model hint):** Which model the delegator expected. Without this, a delegation
   that used a different model than intended is invisible.

5. **provenance + staleness (trustworthiness):** Whether the result's freshness claim is
   self-attested (arm_declared) or observed (router_observed), and whether it has expired.
   Without these, a stale result is indistinguishable from a fresh one.

## Compatibility

- All attributes are OPTIONAL on the span (OTel convention: attributes are never required
  for a span to be valid). The Required/Recommended levels above are guidance for emitters.
- `agent.delegation.instruction` and `agent.delegation.arm_id` and
  `agent.delegation.capability` and `agent.delegation.produced_at` and
  `agent.delegation.status` are Recommended (not Required) at the OTel level, because
  OTel does not mandate attributes. The "Required" in the table means "emit this if you
  have it."
- Backward compatibility: a delegation without these attributes is still a valid span.
  The attributes are purely additive.

## Source

Concrete instance: AOA's `DelegationSpec` (src/AOA/core/delegation_spec.py) and
`ArmResult` (src/AOA/core/contracts.py). Field names mapped:
- DelegationSpec.instruction → agent.delegation.instruction
- DelegationSpec.context → agent.delegation.context
- DelegationSpec.tools → agent.delegation.arm_id + agent.delegation.capability
- DelegationSpec.model → agent.delegation.model
- ArmResult.provenance → agent.delegation.provenance
- ArmResult.stale_after_s → agent.delegation.stale_after_s
- ArmResult.produced_at → agent.delegation.produced_at
- ArmResult.is_stale → agent.delegation.is_stale
- ArmResult.status → agent.delegation.status

## Deliverable checklist

- [x] Attribute table with types, requirement levels, descriptions, examples
- [x] Span structure defined
- [x] Justification for the five core fields
- [x] Compatibility statement
- [x] Source mapping to AOA's DelegationSpec and ArmResult
- [x] Draft status: do not open a PR before jaeger-000 decides project shape