# Project JAEGER — Decision Brief

> ## STATUS 2026-11-02 — the three follow-on rows are CUT (board 47193 / 47194 / 47195 retired)
>
> Reading **(A) tracer of this tree** stands as the intent. The *scope* below it does not, because
> two of the three rows rest on premises this tree falsifies, and the third depends on a span
> source that is not installed.
>
> | row | claim as written | measured 2026-11-02 |
> |---|---|---|
> | 47195 | "0 refs to otlp/opentelemetry in src, tools, Project_*" | **False.** `src/CORE/cd3_exporter.py` is a full OTel `SpanExporter`: `SQLiteSpanExporter` → `otel_spans` (trace_id / session / correlation indexes), `query_trace_by_id`, `query_unified_trace` (ATTACH join to `memories` on `correlation_id`), `purge_old_spans`, and it imports **without** the SDK by design. |
> | 47195 | "the trace-correlation field `DelegationSpec` currently lacks" | **False.** `trace_id` / `span_id` / `parent_span_id` exist, with present-only serialisation, `spawn_child()` inheriting `trace_id`, and `attach()` stamping them onto routed results; covered by `tests/test_delegation_trace_ids.py`. |
> | 47194 | a seventh AOA arm to export spans | **No span source.** `opentelemetry.sdk` is not installed on the production interpreter (`ModuleNotFoundError: No module named 'opentelemetry.sdk'`), so no spans exist to export; `_ARM_MODULES` already holds six arms (`azazael_arm`, `libra_arm`, `codex_arm`, `eve_arm`, `kali_arm`, `support_arms`). |
> | 47193 | scaffold `Project_JAEGER/` to `Project_CRADLE`'s shape | **No consumer.** `otel_spans` holds **0** rows in the live `telemetry_store.db` (the 6 rows in `memory_store.db` predate the 2026-09-28 split), and `configure_otel_tracing` / `SQLiteSpanExporter` have **zero** production callers — only `archive/scripts/` and one docstring. A fourth installable package would publish a mapping table, not a mechanism. |
>
> **What survived was built the same day — as one wiring point, not a project.** The brief's core
> diagnosis held and is why the idea was not dropped: `ArmResult` carries `produced_at`,
> `stale_after_s` and `provenance`, `check_result()` grades freshness, and the only durable record of
> a delegation was a **violation count** (`ContractViolationLog.record`, in-memory, bounded at 100,
> warn-only) — successes were written nowhere, so "was this arm the right choice" was answerable only
> from a live process.
>
> | piece | where |
> |---|---|
> | `record_span()` — write one span with **no OTel SDK** | `src/CORE/cd3_exporter.py` |
> | semconv mapping + `emit_delegation()` + `delegation_outcomes()` | `src/AOA/core/delegation_tracer.py` |
> | call site: both the success and the exception path of `route_task` | `src/AOA/core/router.py` |
> | 18 tests, including the off-switch negative control | `tests/test_delegation_tracer.py` |
>
> Measured 2026-11-02 on the production interpreter, SDK still absent (`OTEL_SDK_AVAILABLE: False`),
> against an isolated `AZAZAEL_MEMORY_DIR`: a routed success and a pinned failure each wrote one row
> (`delegation discover_worms -> azazael`, status_code 1, verdict `accepted`; `-> broken`, status_code
> 2, verdict `rejected`), and `delegation_outcomes(trace_id)` read both back. The route result gains
> `flat["trace"] = {"trace_id", "span_id"}`; telemetry failure never fails a route, and
> `AZAZAEL_AOA_TRACING=off` writes nothing.
>
> **Still not built, deliberately:** an OTLP wire exporter to a collector. There is no collector on
> this host, so it would ship traffic to nothing. `configure_otel_tracing()` remains the interop entry
> point for the day one exists — it writes to the same `otel_spans` rows this path does.

**Task:** Board 47192 / jaeger-000
**Date:** 2026-11-02
**Decider:** opencode lane (max reasoning)

## Question

Is Jaeger (A) the TRACER OF THIS TREE — consuming AOA's DelegationSpec + ArmResult and turning
routing decisions into spans, closing "nothing measures whether a delegation was right" — or
(B) a thin Jaeger/OTLP client other systems push to, duplicating an existing OSS component?

## Decision: (A) Tracer of this tree

### Reading rejected: (B) thin OTLP client

Jaeger as a thin OTLP client is rejected because:

1. **It duplicates an existing OSS component.** OpenTelemetry Collector, Jaeger agent, and
   OTLP exporters already exist. Wrapping them adds no value — it's a pass-through with
   a new name. The tree already has zero OTLP references (confirmed by grep: 0 refs to
   otlp/opentelemetry in src, tools, Project_*).

2. **It solves no problem this tree has.** The tree's problem is not "we can't send spans
   to Jaeger" — it's "we can't tell whether a delegation was right." A client doesn't
   solve that; it just moves spans somewhere else.

3. **It creates a maintenance burden.** A wrapper around an OSS component must track
   upstream changes, handle version compatibility, and debug integration issues — all
   for functionality that already exists.

### Reading accepted: (A) tracer of this tree

Jaeger as the tree's own tracer is accepted because:

1. **It closes a real gap.** AOA's EventBus is threading.Lock + in-memory _history capped
   by max_history — no socket, no HTTP, no serialization. DelegationSpec and ArmResult
   carry provenance (arm_declared vs router_observed) and staleness (stale_after_s), but
   nothing records whether a delegation SUCCEEDED. A tracer that consumes these and turns
   routing decisions into spans makes "was this arm the right choice" answerable from
   the ledger.

2. **It is NOT a duplicate.** No existing component in this tree measures delegation
   outcomes. The OTel semconv draft (docs/OSS_OTEL_SEMCONV_AGENT_DELEGATION_2026-11-02.md)
   defines 10 attributes mapping DelegationSpec fields to OTel spans. This is new
   functionality, not a wrapper.

3. **It builds on existing infrastructure.** AOA's DelegationSpec (instruction, context,
   tools, model) and ArmResult (produced_at, stale_after_s, provenance) already exist.
   The tracer consumes them — it doesn't replace them.

4. **It has a clear scope.** "Tracer of this tree" means: measure delegation decisions
   within AOA, not export to external systems. Export is a separate concern (jaeger-003).

### What Jaeger measures (and what it refuses to claim)

**Measures:**
- Delegation decisions (which arm was chosen for which capability, and why)
- Delegation outcomes (accepted/rejected/unverified, who judged)
- Delegation chains (parent_span_id linking)
- Provenance (arm_declared vs router_observed)
- Staleness (stale_after_s, is_stale)

**Refuses to claim:**
- That a delegation was "correct" (outcome is recorded, not judged)
- That an arm is "the best" (success rates are observed, not proven)
- That spans are "complete" (EventBus has no persistence; spans are in-memory)

### Architecture

```
DelegationSpec (instruction, context, tools, model)
    ↓
AOA Router (selects arm, executes)
    ↓
ArmResult (status, data, produced_at, stale_after_s, provenance)
    ↓
Jaeger Tracer (consumes DelegationSpec + ArmResult → span)
    ↓
Span (agent.delegation with 10 attributes)
    ↓
Sink (JSONL or OTLP — decided in jaeger-003)
```

### Deliverable checklist

- [x] Decision: (A) tracer of this tree
- [x] Reading (B) rejected with 3 reasons
- [x] Reading (A) accepted with 4 reasons
- [x] What Jaeger measures and refuses to claim
- [x] Architecture diagram
- [x] OTel semconv already drafted (docs/OSS_OTEL_SEMCONV_AGENT_DELEGATION_2026-11-02.md)