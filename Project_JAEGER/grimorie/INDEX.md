# Jaeger Grimorie

*The Spellbook of the Azazael Internal Tracer*

> "A grimoire is not a manual. A manual tells you how to use a tool. A grimoire tells you what the tool *is*, why it exists, and what happens when you misuse it."

---

## Table of Contents

1. [Incantations (API Reference)](#incantations-api-reference)
2. [Wards (Validation & Protection)](#wards-validation--protection)
3. [Rituals (Workflows)](#rituals-workflows)
4. [Runes (Configuration)](#runes-configuration)
5. [Wards (Protection Spells)](#wards-protection-spells)
5. [Runes (Configuration Runes)](#runes-configuration-runes)

---

## Incantations (API Reference)

### The Tracer (`jaeger.tracer`)

```python
from jaeger.tracer import JaegerTracer
from jaeger.context import DelegationSpec, ArmResult

tracer = JaegerTracer(config)
span = tracer.start_span(
    name="delegation.execute",
    delegation=DelegationSpec(...),
    arm_result=ArmResult(...)
)
span.end()
```

**Incantation Rules:**
- Every span **must** carry `DelegationSpec` + `ArmResult` attributes
- Spans without both are **rejected** at creation (ward)
- `start_time` set at creation; `end_time` set at `.end()`
- Spans are **immutable** after `.end()` — any mutation raises `SpanFrozenError`

### The Span (`jaeger.span`)

```python
from jaeger.span import Span, SpanKind, SpanStatus

span = Span(
    trace_id="0af2e3c4d5f6a7b8",
    span_id="1a2b3c4d5e6f7890",
    name="delegation.execute",
    kind=SpanKind.INTERNAL,
    attributes={
        "delegation.id": "del-abc123",
        "delegation.instruction": "analyze user intent",
        "arm.id": "arm-psyche-triage",
        "arm.provenance": "arm_declared",
    },
    events=[
        SpanEvent(name="delegation.received", timestamp=...),
        SpanEvent(name="arm.dispatched", timestamp=...),
    ]
)
```

**Span Fields (Immutable After Creation):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trace_id` | `str` | ✅ | 16-byte hex |
| `span_id` | `str` | ✅ | 8-byte hex |
| `parent_span_id` | `str` | ❌ | 8-byte hex or null |
| `name` | `str` | ✅ | Operation name |
| `kind` | `SpanKind` | ✅ | INTERNAL/CLIENT/SERVER/PRODUCER/CONSUMER |
| `start_time` | `datetime` | ✅ | UTC with ns precision |
| `end_time` | `datetime` | ❌ | Set by `.end()` |
| `attributes` | `dict` | ✅ | Must include `delegation.*` + `arm.*` |
| `events` | `list[SpanEvent]` | ❌ | Timestamped annotations |
| `status` | `SpanStatus` | ✅ | OK/ERROR/UNSET |
| `links` | `list[SpanLink]` | ❌ | Cross-span references |

### The Context (`jaeger.context`)

```python
from jaeger.context import DelegationSpec, ArmResult, ArmProvenance

spec = DelegationSpec(
    id="del-abc123",
    instruction="analyze user intent",
    context="user said: help me sleep",
    tools=["triage", "psyche_fit"],
    model="gpt-4",
    metadata={"priority": "high"}
)

result = ArmResult(
    id="arm-psyche-triage",
    capability="crisis_detection",
    result="crisis",
    provenance=ArmProvenance.ARM_DECLARED,
    stale_after_s=300,
    metadata={"confidence": 0.94}
)
```

**DelegationSpec Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | ✅ | Unique delegation ID |
| `instruction` | `str` | ✅ | What was asked |
| `context` | `str` | ✅ | Full context text |
| `tools` | `list[str]` | ✅ | Tools available |
| `model` | `str` | ✅ | Model identifier |
| `metadata` | `dict` | ❌ | Additional context |

**ArmResult Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | ✅ | ARM identifier |
| `capability` | `str` | ✅ | Capability name |
| `result` | `str` | ✅ | Result value |
| `provenance` | `ArmProvenance` | ✅ | `ARM_DECLARED` / `ROUTER_OBSERVED` |
| `stale_after_s` | `int` | ✅ | Freshness window |
| `metadata` | `dict` | ❌ | Additional data |

---

## Wards (Validation & Protection)

### Span Creation Ward

```python
# In jaeger.span.Span.__new__
def __new__(cls, *args, **kwargs):
    # Ward 1: Must have delegation + arm attributes
    attrs = kwargs.get("attributes", {})
    required = ["delegation.id", "arm.id", "arm.provenance"]
    missing = [k for k in required if k not in attrs]
    if missing:
        raise SpanCreationError(f"Missing required attributes: {missing}")
    
    # Ward 2: provenance must be valid enum
    prov = attrs.get("arm.provenance")
    if prov not in ("arm_declared", "router_observed"):
        raise SpanCreationError(f"Invalid provenance: {prov}")
    
    # Ward 3: stale_after_s must be positive int
    stale = attrs.get("arm.stale_after_s")
    if not isinstance(stale, int) or stale <= 0:
        raise SpanCreationError("arm.stale_after_s must be positive int")
    
    return super().__new__(cls, *args, **kwargs)
```

### Span Freeze Ward

```python
# In jaeger.span.Span.__setattr__
def __setattr__(self, name, value):
    if getattr(self, "_frozen", False) and name not in ("_frozen",):
        raise SpanFrozenError(f"Cannot modify frozen span: {name}")
    super().__setattr__(name, value)
```

### Export Ward

```python
# In jaeger.exporter.Exporter.export
def export(self, spans: list[Span]) -> ExportResult:
    # Ward: All spans must be frozen (ended)
    unfinished = [s for s in spans if not s._frozen]
    if unfinished:
        raise ExportError(f"{len(unfinished)} spans not ended")
    
    # Ward: All spans must have trace_id
    no_trace = [s for s in spans if not s.trace_id]
    if no_trace:
        raise ExportError(f"{len(no_trace)} spans missing trace_id")
    
    return self._do_export(spans)
```

### Configuration Ward

```python
# In jaeger.config.Config.__post_init__
def __post_init__(self):
    if self.tracer.sample_rate < 0 or self.tracer.sample_rate > 1:
        raise ConfigError("sample_rate must be 0.0-1.0")
    if self.exporter.batch_size < 1:
        raise ConfigError("batch_size must be >= 1")
    if self.span.stale_after_s < 1:
        raise ConfigError("stale_after_s must be >= 1")
```

---

## Rituals (Workflows)

### Ritual 1: The Daily Trace (Tracing a Delegation)

```python
# 1. Receive DelegationSpec from AOA
spec = DelegationSpec.from_aoa(aoa_message)

# 2. Create tracer span
with tracer.start_span(
    name="delegation.execute",
    delegation=spec,
    arm_result=None  # Not yet known
) as span:
    
    # 3. Dispatch to ARM
    arm_result = await arm_dispatcher.dispatch(spec)
    
    # 3. Attach ArmResult to span
    span.set_arm_result(arm_result)
    
    # 4. Span auto-ends on context exit
    # Span now carries: DelegationSpec + ArmResult + timing

# 5. Span automatically exported (batch)
```

**Ritual Rules:**
- Never create span without `DelegationSpec`
- Never end span without `ArmResult` attached
- Spans batch-export every `batch_size` or `flush_interval_s`

### Ritual 2: The Freshness Check (Staleness Ward)

```python
# Runs every flush_interval_s
def check_staleness(spans: list[Span]) -> list[Span]:
    stale = []
    now = datetime.utcnow()
    for span in spans:
        stale_after = span.attributes.get("arm.stale_after_s", 300)
        age = (now - span.start_time).total_seconds()
        if age > stale_after:
            span.add_event(SpanEvent(
                name="span.stale",
                timestamp=now,
                attributes={"age_s": age, "stale_after_s": stale_after}
            ))
            stale.append(span)
    return stale
```

### Ritual 3: The Export Rite (OTLP/JSONL)

```python
# JSONL Export
def export_jsonl(spans: list[Span], path: Path):
    with path.open("a") as f:
        for span in spans:
            f.write(json.dumps(span.to_otlp_dict()) + "\n")

# OTLP Export (jaeger-003)
async def export_otlp(spans: list[Span], endpoint: str):
    exporter = OTLPExporter(endpoint)
    await exporter.export(spans)
```

### Ritual 4: The Freshness Audit

```python
# Runs daily
def audit_freshness(store: SpanStore) -> FreshnessReport:
    now = datetime.utcnow()
    report = FreshnessReport()
    
    for span in store.recent(24 * 3600):  # last 24h
        stale_after = span.attributes.get("arm.stale_after_s", 300)
        age = (now - span.start_time).total_seconds()
        if age > stale_after:
            report.stale_spans.append(span.span_id)
    
    report.total_spans = store.count(24 * 3600)
    report.stale_count = len(report.stale_spans)
    report.staleness_rate = report.stale_count / max(report.total_spans, 1)
    
    return report
```

---

## Wards (Protection Spells)

### Ward of the Frozen Span

> *"A span that has ended cannot be changed. Its truth is sealed."*

```python
class SpanFrozenError(Exception):
    """Raised when attempting to modify a frozen span."""
    pass

# Applied to all Span mutators after .end()
```

### Ward of the Required Attributes

> *"A span without DelegationSpec and ArmResult is a lie."*

```python
class SpanCreationError(Exception):
    """Raised when span creation violates wards."""
    pass
```

### Ward of the Freshness

> *"A span that outlives its stale_after_s is a ghost."*

```python
class StalenessWarning(UserWarning):
    """Emitted when span exceeds stale_after_s."""
    pass
```

### Ward of the Export

> *"An unfinished span does not leave the circle."*

```python
class ExportError(Exception):
    """Raised when export conditions not met."""
    pass
```

---

## Runes (Configuration Runes)

### Tracer Runes (`tracer:`)

| Rune | Type | Default | Description |
|------|------|---------|-------------|
| `service_name` | `str` | `"azazael-jaeger"` | Service identifier |
| `sample_rate` | `float` | `1.0` | Sampling probability (0.0-1.0) |
| `max_spans_in_memory` | `int` | `10000` | Memory limit |

### Exporter Runes (`exporter:`)

| Rune | Type | Default | Description |
|------|------|---------|-------------|
| `type` | `str` | `"jsonl"` | `jsonl` or `otlp` |
| `endpoint` | `str` | `"spans.jsonl"` | File path or OTLP endpoint |
| `batch_size` | `int` | `100` | Spans per batch |
| `flush_interval_s` | `float` | `5.0` | Auto-flush interval |
| `compression` | `str` | `"gzip"` | `gzip`/`none` |

### Span Runes (`span:`)

| Rune | Type | Default | Description |
|------|------|---------|-------------|
| `stale_after_s` | `int` | `300` | Max age before stale warning |
| `include_attributes` | `bool` | `true` | Include attributes in export |
| `include_events` | `bool` | `true` | Include events in export |
| `attribute_filter` | `list[str]` | `["delegation.*", "arm.*"]` | Attributes to include |

### Example Complete Rune Set

```yaml
# config.yaml
tracer:
  service_name: "azazael-jaeger"
  sample_rate: 1.0
  max_spans_in_memory: 10000

exporter:
  type: "jsonl"
  endpoint: "spans.jsonl"
  batch_size: 100
  flush_interval_s: 5.0
  compression: "gzip"

span:
  stale_after_s: 300
  include_attributes: true
  include_events: true
  attribute_filter: 
    - "delegation.*"
    - "arm.*"
    - "azazael.*"
```

---

## The Jaeger Oath

> **I trace what happens, not what should happen.**  
> **I record the delegation, the arm, the result — not the intent.**  
> **I freeze the span when the arm completes; I do not rewrite history.**  
> **I export what happened, not what was meant to happen.**  
> **I warn when spans grow stale; I do not hide them.**  
> **I am the witness, not the judge.**

---

*Grimorie version 0.1.0 — Updated 2026-11-03*  
*Next: jaeger-001 scaffolding → jaeger-002 AOA-ARM → jaeger-003 OTLP export*

---

## License

CDDL-1.1 — see `../../LICENSE`.