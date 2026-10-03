---
name: azazael-inference-providers
description: 16+ free inference APIs behind a unified OpenAI-compatible provider pattern with worm-based dispatch.
metadata:
  category: domain
  project: azazael
  priority: high
  auto_load: false
---

# Azazael Inference Provider Integration

## Overview
Azazael integrates 16+ free inference APIs via a unified OpenAI-compatible provider pattern:
```
providers.py (16 providers) --> api_client.py (ThreadSafeCall, retry, masking)
                                    |
                            INFERENCE_WORM.py (worm-based inference dispatch)
                            NIM_INFERENCE.py (NVIDIA-specific worm)
```

## Provider Registry (16 Providers)
| Provider | Base URL | Free Tier | Key Prefix |
|----------|----------|-----------|------------|
| Groq | api.groq.com/openai/v1 | 30 RPM, 6000 TPM | gsk_ |
| OpenRouter | openrouter.ai/api/v1 | Free models hub | — |
| Gemini | generativelanguage.googleapis.com | 10-15 RPM, 1M TPM | — |
| Cloudflare | api.cloudflare.com/client/v4/ | Neurons free | — |
| Cohere | api.cohere.ai/compatibility/v1 | 1K calls/mo trial | — |
| Cerebras | api.cerebras.ai/v1 | 1M tokens/day | — |
| NVIDIA NIM | integrate.api.nvidia.com/v1 | 40 RPM | nvapi- |
| Ollama | localhost:11434/v1 | Local, free, unlimited | — |
| Mistral | api.mistral.ai/v1 | ~1B tokens/mo | — |
| GitHub | models.github.ai/inference | 10-15 RPM | — |
| HuggingFace | router.huggingface.co/v1 | Free tier | hf_ |
| OVHcloud | endpoints.kepler.ai | 2 RPM, anonymous | — |
| SiliconFlow | api.siliconflow.com/v1 | 200+ models free | — |
| Together AI | api.together.xyz/v1 | Requires payment | — |
| Zhipu AI | api.z.ai/api/paas/v4 | GLM-4 free tier | — |


## Key Architecture Decisions
- All providers use the **same OpenAI-compatible `/v1/chat/completions` protocol**
- **Singleton cache** (`_provider_cache`) avoids redundant client creation
- **Config file fallback**: checks `~/.azazael/{provider}_config.json` after env vars
- **Rate limiting**: per-provider RPM tracking with sleep-based enforcement

## Priority Order (get_best_provider)
```
nvidia_nim > ollama > groq > cerebras > openrouter > gemini > together > github > mistral > huggingface > cloudflare > siliconflow > cohere > zhipu > ovhcloud
```

## API Client (api_client.py)
- **ThreadSafeCall**: wrapper with locking for 3.14t free-threading
- **Exponential backoff**: 0.5s → 1s → 2s → ... 60s cap
- **Error hierarchy**: RateLimitError, AuthError, TimeoutError
- **Key masking**: `mask_key()` for safe logging
- **Retry classification**: retryable vs fatal via HTTP status codes

## Key Files
| File | Purpose |
|------|---------|
| `CORE/inference/providers.py` | 17-provider registry, OpenAIProvider, get_provider, get_best_provider |
| `CORE/inference/nim_client.py` | NVIDIA NIM-specific client extending OpenAIProvider |
| `CORE/inference/api_client.py` | ThreadSafeCall, retry logic, error hierarchy, key masking |
| `CORE/secrets_manager.py` | Thread-safe API key rotation and audit |
