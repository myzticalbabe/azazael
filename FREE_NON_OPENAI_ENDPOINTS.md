# Free Non-OpenAI-Compatible API Endpoints

> *Canonical source: `azazael/FREE_NON_OPENAI_ENDPOINTS.md`*
> *Effective: June 9, 2026*
> *Purpose: Complete registry of all free internet API endpoints that do NOT use the OpenAI /v1/chat/completions format*

These endpoints can be integrated via `NativeAPIProvider` in `CORE/inference/providers.py`.

---

## ACTIVE FREE INTERNET API ENDPOINTS

| # | Provider | Native Endpoint | Protocol | Auth | Free Tier | Framework Ready |
|---|----------|----------------|----------|------|-----------|-----------------|
| 1 | **Google Gemini** | `generativelanguage.googleapis.com/v1beta/models/{model}:generateContent` | Google RPC (contents/parts) | API key (query param `?key=`) | Yes, generous | ✅ `GeminiNativeProvider` |
| 2 | **Hugging Face** | `api-inference.huggingface.co/models/{model_id}` | Task-specific (`inputs` field) | Bearer token (`hf_`) | Yes, rate-limited | ✅ `HuggingFaceNativeProvider` |
| 3 | **Mistral FIM** | `api.mistral.ai/v1/fim/completions` | Fill-in-the-Middle (prompt+suffix) | Bearer token (`MISTRAL_API_KEY`) | Free experiment, ~1B tokens/mo | ✅ `MistralFIMNativeProvider` |
| 4 | **Anthropic Claude** | `api.anthropic.com/v1/messages` | Proprietary (messages, system top-level) | `x-api-key` header | Trial credits only | ✅ `AnthropicNativeProvider` |

## LOCAL-ONLY ENDPOINTS (not internet APIs)

| # | Provider | Native Endpoint | Protocol | Auth | Free Tier |
|---|----------|----------------|----------|------|-----------|
| 5 | **Ollama (Native)** | `localhost:11434/api/generate` | Own format (model/prompt) | None (local) | Unlimited (local) |

## STREAMING SUPPORT

All `NativeAPIProvider` subclasses support streaming via `chat_stream()`:

```python
provider = get_provider('gemini_native')
for chunk in provider.chat_stream('Tell me a story', max_tokens=100):
    print(chunk, end='')
```

The base class handles SSE (`data:` line parsing, `[DONE]` detection). Subclasses can override `_parse_stream_chunk()` for custom SSE event types (e.g., Anthropic's `content_block_delta`).

## FULL PROVIDER LIST (as of June 9, 2026)

| # | Provider ID | Class | Type | Status |
|---|-------------|-------|------|--------|
| 1 | `gemini_native` | `GeminiNativeProvider` | Internet API | ✅ Live (rate-limited) |
| 2 | `huggingface_native` | `HuggingFaceNativeProvider` | Internet API | ✅ Registered |
| 3 | `mistral_fim_native` | `MistralFIMNativeProvider` | Internet API | ✅ Live (449ms) |
| 4 | `anthropic_native` | `AnthropicNativeProvider` | Internet API | ✅ Registered (no key) |
| 5 | `ollama_native` | `OllamaNativeProvider` | Local | ✅ Live (3309ms) |
| 6 | `llama_cpp_direct` | `LlamaCppDirectProvider` | Local/In-process | ✅ Registered |
| 7 | `huggingface_direct` | `HuggingFaceDirectProvider` | Local/In-process | ✅ Registered |
| 8-22 | (15 OpenAI-compatible) | `OpenAIProvider` | Internet API (OpenAI compat) | Various |

## FRAMEWORK INTEGRATION PATTERN

```python
from CORE.inference.providers import NativeAPIProvider, NativeFrameworkConfig

class MyFreeAPIProvider(NativeAPIProvider):
    def _get_framework_config(self) -> NativeFrameworkConfig:
        return NativeFrameworkConfig(
            endpoint='/v1/custom/path',
            method='POST',
            prompt_field='input',
            model_field='model',
            requires_auth=True,
            auth_scheme='header',
        )
    
    def _build_request(self, prompt: str, **kwargs) -> dict:
        return {
            'input': prompt,
            'model': kwargs.get('model', self.config.model),
            'max_output': kwargs.get('max_tokens', self.config.max_tokens),
        }
    
    def _parse_response(self, data: dict) -> dict:
        return {
            'content': data.get('output', ''),
            'model': data.get('model', self.config.model),
            'usage': {
                'prompt_tokens': data.get('input_tokens', 0),
                'completion_tokens': data.get('output_tokens', 0),
                'total_tokens': 0,
            },
        }
```

## REGISTRATION PATTERN

```python
'my_free_api': {
    'name': 'My Free API',
    'description': 'Free internet API, non-OpenAI format',
    'base_url': 'https://api.myprovider.com',
    'default_model': 'model-name',
    'rate_limit_rpm': 30,
    'env_var': 'MY_API_KEY',
    'signup_url': 'https://myprovider.com/signup',
    'requires_auth': True,
}
```

## PRIORITY FOR INTEGRATION

| Priority | Provider | Reason |
|----------|----------|--------|
| 1 | Google Gemini (Native) | Most generous free tier, widely used |
| 2 | Hugging Face (Native) | Task-specific, thousands of models |
| 3 | Mistral FIM (Native) | Fill-in-the-middle, code completion |
| 4 | Anthropic Claude | Trial credits if needed |

## Related Documents

- `azazael/src/CORE/inference/providers.py` — NativeAPIProvider framework
- `azazael/skills/azazael-inference-providers.md` — Provider integration skill
