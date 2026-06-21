# Azazael Inference Provider Integration

## Overview
Azazael integrates 14+ free inference APIs via a unified OpenAI-compatible provider pattern:
```
providers.py (14 providers) --> api_client.py (ThreadSafeCall, retry, masking)
                                    |
                            INFERENCE_WORM.py (worm-based inference dispatch)
                            NIM_INFERENCE.py (NVIDIA-specific worm)
```

## Provider Registry (14 Providers)
| Provider | Base URL | Free Tier | Key Prefix |
|----------|----------|-----------|------------|
| Groq | api.groq.com/openai/v1 | 30 RPM, 6000 TPM | gsk_ |
| OpenRouter | openrouter.ai/api/v1 | Free models hub | — |
| Gemini | generativelanguage.googleapis.com | 10-15 RPM, 1M TPM | — |
| Cloudflare | api.cloudflare.com/client/v4/ | Neurons free | — |
| Cohere | api.cohere.com/v2 | Trial keys | — |
| Fireworks | api.fireworks.ai/inference/v1 | $1 trial | — |
| NVIDIA NIM | integrate.api.nvidia.com/v1 | 40 RPM | nvapi- |
| Mistral | api.mistral.ai/v1 | ~1B tokens/mo | — |
| GitHub | models.github.ai/inference | 10-15 RPM | — |
| xAI | api.x.ai/v1 | Prepaid credits | xai- |
| OVHcloud | oai.endpoints.kepler.ai.cloud.ovh.net | 2 RPM | — |
| HuggingFace | router.huggingface.co/v1 | Free tier | hf_ |
| Together | api.together.xyz/v1 | $5-25 free | — |

## Key Architecture Decisions
- All providers use the **same OpenAI-compatible `/v1/chat/completions` protocol**
- **Singleton cache** (`_provider_cache`) avoids redundant client creation
- **Config file fallback**: checks `~/.azazael/{provider}_config.json` after env vars
- **Rate limiting**: per-provider RPM tracking with sleep-based enforcement

## Priority Order (get_best_provider)
```
nvidia_nim > groq > openrouter > gemini > github > mistral > huggingface > together
> cloudflare > cohere > fireworks > ovhcloud > xai
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
| `CORE/inference/providers.py` | 14-provider registry, OpenAIProvider, get_provider, get_best_provider |
| `CORE/inference/nim_client.py` | NVIDIA NIM-specific client extending OpenAIProvider |
| `CORE/inference/api_client.py` | ThreadSafeCall, retry logic, error hierarchy, key masking |
| `CORE/secrets_manager.py` | Thread-safe API key rotation and audit |
