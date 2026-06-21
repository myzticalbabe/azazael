---
name: azazael-inference-worms
description: Azazael inference worms — InferenceWorm (provider-agnostic) and NimInferenceWorm (multi-provider). Load when using or modifying inference worm implementations.
metadata:
  category: architecture
  project: azazael
  parent: azazael-inference
  created: 2026-06-06
---
# Azazael Inference Worms

## Overview

Three inference worms provide LLM access to the Azazael ecosystem. All are registered in the worm registry (category: "analysis") and publish results to MemoryBus.

## InferenceWorm — `CORE/WORMS/INFERENCE_WORM.py` (v1.0.0)

Provider-agnostic worm that auto-selects the best available provider. Registered at priority 7, cooldown 15s.

### Key Features
- **Auto-selection**: Uses `get_best_provider()` to pick fastest available
- **Manual override**: Pass `provider="groq"` to force a specific provider
- **MemoryBus**: Publishes completion/error events to topic `inference.result`
- **Convenience methods**: `analyze()`, `summarize()`
- **Provider listing**: `list_providers()` shows all 11 with key status

### API
```python
from CORE.WORMS.INFERENCE_WORM import InferenceWorm
worm = InferenceWorm()

# Basic inference
result = worm.execute(prompt="Hello Azazael!", max_tokens=50)
# Returns: {success, content, model, provider, usage, elapsed_ms}

# Force provider
result = worm.execute("Hello", provider="groq")

# System prompt
result = worm.execute(
    prompt="some log data",
    system_prompt="Analyze for security issues"
)

# Convenience
result = worm.analyze("content to analyze")
result = worm.summarize("long text", max_words=50)

# Status
providers = worm.list_providers()
stats = worm.get_stats()  # {version, exec_count, total_tokens}
```

### Registration
```python
@register_worm(
    category="analysis",
    priority=7,
    cooldown_seconds=15.0,
    description="Provider-agnostic inference — auto-selects best available LLM API"
)
class InferenceWorm: ...
```

## NimInferenceWorm — `CORE/WORMS/NIM_INFERENCE.py` (v1.2.0)

Originally NVIDIA-only, now supports all providers. Registered at priority 6, cooldown 30s.

### Version History
- v1.0.0: NVIDIA NIM only, direct NimClient usage
- v1.1.0: NimClient subclasses OpenAIProvider, ~150 lines deduplicated, MemoryBus integration
- v1.2.0: Multi-provider support via `provider` param (`nvidia_nim`, `groq`, `gemini`)

### API
```python
from CORE.WORMS.NIM_INFERENCE import NimInferenceWorm
worm = NimInferenceWorm()

# Default: NVIDIA NIM (backward compatible)
result = worm.execute(prompt="Hello!", max_tokens=50)

# Multi-provider (v1.2.0+)
result = worm.execute("Hello!", provider="groq")
result = worm.execute("Hello!", provider="gemini")

# NIM-specific
models = worm.list_available_models()
providers = worm.list_all_providers()
stats = worm.get_stats()  # Includes client stats + model info
```

### Registration
```python
@register_worm(
    category="analysis",
    priority=6,
    cooldown_seconds=30.0,
    description="Multi-provider inference — NIM, Groq, Gemini via OpenAI-compatible API"
)
class NimInferenceWorm: ...
```

## Shared Infrastructure: InferenceBusPublisher

Both worms use `CORE/inference/bus_utils.py` for MemoryBus publishing:
```python
from CORE.inference.bus_utils import InferenceBusPublisher
pub = InferenceBusPublisher(source="inference_worm")
pub.publish({"event": "inference.complete", "provider": "groq", "tokens": 55})
```

Lazy initialization, best-effort (never raises), topic `inference.result`.

## Comparison

| Feature | InferenceWorm | NimInferenceWorm | InferenceSubscriberWorm |
|---------|:---:|:---:|:---:|
| Version | 1.0.0 | 1.2.0 | 1.0.0 |
| Priority | 7 | 6 | 5 |
| Cooldown | 15s | 30s | 30s |
| Auto-provider | ✅ get_best_provider() | ❌ defaults to NIM | ❌ passive listener |
| Provider override | ✅ provider param | ✅ provider param (v1.2.0+) | N/A |
| list_providers() | ✅ | ✅ list_all_providers() | ❌ |
| Convenience methods | analyze(), summarize() | analyze(), summarize() | analyze() |
| NIM models | ❌ | ✅ list_available_models() | ❌ |
| Client stats | ❌ | ✅ get_stats() includes client | ❌ events + alerts |
| MemoryBus | publish | publish | subscribe + publish alerts |

## Usage in Clusters

```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# Both worms are in the "analysis" category
cluster = ClusterWORMZ.build_from_nature("analysis")
results = cluster.execute_all()

# Or target individually
cluster = ClusterWORMZ.build_from_worms(["InferenceWorm", "NimInferenceWorm", "InferenceSubscriberWorm"])
results = cluster.execute_all()
```

## InferenceSubscriberWorm — `CORE/WORMS/INFERENCE_SUBSCRIBER.py` (v1.0.0)

Passive MemoryBus listener that detects anomalies via LLM analysis. Registered at priority 5, cooldown 30s.

### Key Features
- **MemoryBus subscriber**: Listens to `cluster.>`, `nature.>`, `inference.>` topics
- **Dual analysis**: Quick statistical checks + LLM deep analysis
- **Anomaly detection**: Failure spikes, timeout cascades, pattern anomalies
- **Alert publishing**: Publishes to `inference.alert` topic on MemoryBus
- **Thread-safe**: Event buffer with configurable capacity (200 events)

### API
```python
from CORE.WORMS.INFERENCE_SUBSCRIBER import InferenceSubscriberWorm
worm = InferenceSubscriberWorm()

# Start listening to MemoryBus
worm.start()

# ... cluster operations happen, events are buffered ...

# Run analysis
result = worm.analyze()
# Returns: {alerts, summary, event_count}

# View alerts
alerts = worm.get_alerts()
for alert in alerts:
    print(f"[{alert['type']}] {alert['message']}")

# Stop and clean up subscriptions
worm.stop()
```

### Registration
```python
@register_worm(
    category="analysis",
    priority=5,
    cooldown_seconds=30.0,
    description="MemoryBus inference subscriber — real-time anomaly detection via LLM"
)
class InferenceSubscriberWorm: ...
```

## Benchmark Reference

Groq vs NVIDIA NIM (same prompt, same model):
| Metric | Groq | NIM |
|--------|------|-----|
| Speed | **406ms** | 11,765ms |
| Speedup | — | **29x slower** |
| Tokens | 55 | 55 |
| Output | Identical | Identical |

## Related Skills
- `azazael-inference` — Parent: multi-provider system overview
- `azazael-inference-providers` — 11-provider registry reference
- `azazael-inference-integration` — Strategy + P0-P2 implementation details
- `azazael-codex` — PAMS/MemoryBus pub/sub patterns
- `azazael-registry` — @register_worm decorator, worm discovery
