---
name: azazael-inference
description: Azazael multi-provider AI inference — 11 free LLM providers, OpenAI-compatible API, NimClient, InferenceBusPublisher, provider registry. Load when working with AI inference, LLM integration, or the inference module.
metadata:
  category: architecture
  project: azazael
  created: 2026-06-06
  session: inference-providers-buildout
---
# Azazael Inference — Multi-Provider AI System

## Overview

Azazael's inference module (`CORE/inference/`) provides a unified, OpenAI-compatible API across **11 free LLM providers**. Zero credit card required. Built during the June 2026 multi-provider buildout session.

## Architecture

```
CORE/inference/
├── __init__.py        # v1.1.0 — Multi-provider exports
├── providers.py       # 11-provider registry, OpenAIProvider, ProviderConfig
├── nim_client.py      # v1.1.0 — NimClient subclasses OpenAIProvider
└── bus_utils.py       # InferenceBusPublisher — shared MemoryBus publisher

CORE/WORMS/
├── INFERENCE_WORM.py  # v1.0.0 — Provider-agnostic worm (auto-selects best)
└── NIM_INFERENCE.py   # v1.2.0 — Multi-provider worm (NIM, Groq, Gemini)
```

## Key APIs

### Quick Provider Selection
```python
from CORE.inference.providers import get_provider, get_best_provider, list_providers

# Use a specific provider
groq = get_provider("groq")
result = groq.chat("Hello!")

# Auto-select best available
best = get_best_provider()
result = best.chat("Analyze this log...")

# List all providers with status
for p in list_providers():
    print(f"{p['id']}: key={'YES' if p['has_api_key'] else 'no'}")
```

### Worm-Based Inference
```python
from CORE.WORMS.INFERENCE_WORM import InferenceWorm
worm = InferenceWorm()
result = worm.execute("Summarize this...")  # Auto-selects Groq (fastest)

# Force provider
result = worm.execute("Hello", provider="nvidia_nim")

# List providers
for p in worm.list_providers():
    print(f"{p['id']}: {'LIVE' if p['has_api_key'] else 'no key'}")
```

### NimInferenceWorm (Backward Compatible)
```python
from CORE.WORMS.NIM_INFERENCE import NimInferenceWorm
worm = NimInferenceWorm()
result = worm.execute("Analyze this...")  # Default: NIM

# Multi-provider support (v1.2.0+)
result = worm.execute("Hello", provider="groq")
```

## Live Providers (as of June 2026)

| # | Provider | Key | RPM | Speed |
|---|----------|:--:|-----|-------|
| 1 | **Groq** ⚡ | LIVE | 30 | **~400ms** |
| 2 | **NVIDIA NIM** | LIVE | 40 | ~12s |
| 3 | **Google Gemini** | LIVE | 15 | ⏳ quota |
| 4 | **xAI Grok** | LIVE | 20 | ❌ credits |
| 5-11 | 7 others | — | — | Ready |

## Provider Priority Order

`get_best_provider()` selects the first with a valid key:
1. `nvidia_nim` — Most generous free tier (40 RPM, 5 models)
2. `xai` — Grok models (20 RPM)
3. `groq` — Fastest inference (30 RPM, 406ms avg)
4. `openrouter` — Model hub (20 RPM)
5. `gemini` — Google AI Studio (15 RPM, most generous quota)
6-11. cloudflare, cohere, fireworks, mistral, github_models, ovhcloud

## Config File Fallback

Each provider reads from `~/.azazael/{name}_config.json` as fallback when the env var isn't set:
```json
{
  "api_key": "gsk_...",
  "base_url": "https://api.groq.com/openai/v1",
  "model": "llama-3.3-70b-versatile"
}
```

**Special case:** NVIDIA NIM also checks `~/.azazael/nim_config.json` (legacy NimClient naming).

## MemoryBus Integration

All inference results are published to MemoryBus topic `inference.result`:
```python
# Worm automatically publishes:
# - Topic: "inference.result"
# - Events: "inference.complete", "inference.error"
# - Source: "inference_worm" or "nim_inference"

# Shared publisher via InferenceBusPublisher:
from CORE.inference.bus_utils import InferenceBusPublisher
pub = InferenceBusPublisher(source="my_worm")
pub.publish({"event": "inference.complete", "provider": "groq", "tokens": 55})
```

## Clipboard-Based Key Capture

Keys can be read from Windows clipboard (user copies from browser, script reads via PowerShell):
```python
import subprocess
r = subprocess.run(['powershell','-Command','Get-Clipboard'], capture_output=True, text=True)
key = r.stdout.strip()
# Save to ~/.azazael/{provider}_config.json
```

## Related Skills
- `azazael-inference-providers` — Full 11-provider reference with models, URLs, auth
- `azazael-inference-worms` — InferenceWorm and NimInferenceWorm API details
- `azazael-clusters` — ClusterWORMZ, NatureClusters, MetaCluster (consumers)
- `azazael-codex` — PAMS/MemoryBus memory systems
- `azazael-registry` — Worm registry API, @register_worm decorator
