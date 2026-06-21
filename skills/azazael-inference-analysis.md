# azazael-inference-analysis
**Category:** Domain Knowledge
**Priority:** HIGH
**Dependencies:** azazael-secrets-manager, azazael-cloud-tab
**Created:** June 7, 2026

## Purpose
Documents the multi-API inference subsystem: providers.py (14 providers), api_client.py (unified retry/backoff), secrets_manager.py (12 API keys), cloud_tab.py (GUI inference tab).

## Key Files
- `CORE/inference/providers.py` — 14 providers, OpenAI-compatible API, get_best_provider()
- `CORE/inference/api_client.py` — Base APIClient, InferenceError hierarchy, retry/backoff
- `CORE/inference/cloud_tab.py` — Tkinter Cloud inference tab, async provider refresh
- `CORE/secrets_manager.py` — Unified secrets manager, 12 providers, audit, .env management
- `AZAZAEL_Inference_Studio.py` — Delegates Cloud tab to CloudTab module

## Working Free Providers (no credit card)
1. Groq (llama-3.3-70b, ~1s)
2. OpenRouter (llama-3.3-70b, ~8s)
3. NVIDIA NIM (llama-3.3-70b, ~30s)
4. Mistral (mistral-large, ~9s)
5. GitHub (gpt-4o-mini, ~6s)

## Usage
```python
from CORE.inference.providers import get_provider
prov = get_provider("groq")
result = prov.chat("Hello!", max_tokens=100)
print(result["content"])
```

## Thread Safety
All providers are thread-safe for Python 3.14t free-threading. Use FreeThreadPool for parallel inference.
