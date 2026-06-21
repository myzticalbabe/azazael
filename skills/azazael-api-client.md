# azazael-api-client
**Category:** Domain Knowledge
**Priority:** HIGH
**Dependencies:** azazael-inference-analysis, azazael-secrets-manager
**Created:** June 7, 2026

## Purpose
Documents the APIClient base class: unified retry/backoff, structured InferenceError hierarchy, thread-safe call tracking, key masking.

## Key File
`CORE/inference/api_client.py` — Base APIClient with:
- `InferenceError` hierarchy: `RateLimitError`, `AuthError`, `TimeoutError`
- Exponential backoff: 0.5s → 1s → 2s → ... → 60s cap
- `_request_with_retry()` — callable with retry
- `_safe_call()` — zero-arg wrapper with structured error dicts
- `ThreadSafeCall` — thread-safe call/error tracking
- `mask_key()` — API key masking for safe display
- `safe_error_message()` — truncation + ASCII safety

## Usage
```python
from CORE.inference.api_client import APIClient, mask_key

class MyProvider(APIClient):
    def chat(self, prompt):
        return self._safe_call(lambda: self._call_api(prompt))

print(mask_key("nvapi-secretkey12345"))  # nvapi-s...2345
```

## Retryable vs Fatal
- Retryable: 429, 502, 503, 504, timeout, connection errors
- Fatal: 400, 401, 402, 403, 404
