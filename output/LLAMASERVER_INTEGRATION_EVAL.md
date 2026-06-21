# LlamaServer Integration Evaluation (AR-12)

**Date:** 2026-06-04
**Assessor:** Codebuff
**Status:** ✅ Complete

---

## Overview

LlamaServer (at `%UserProfile%/Desktop/LlamaServer/`) provides a **local LLM inference stack** combining a Rust SYCL/Level Zero server with a native llama.cpp backend (via Jan). It exposes an **OpenAI-compatible API** on `localhost:8080/v1`, making it directly usable as an agent inference backend for CORE worms.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              LlamaServer (Python shell)          │
│  run.py  ───  orchestrates build/start/chat/stop │
│  llama_client.py  ───  OpenAI-compatible client  │
├─────────────────────────────────────────────────┤
│         Rust llama-server (SYCL/Level Zero)      │
│  Build: ~/llama-server/target/release/           │
│  Config: ~/llama-server/config.toml              │
│  Models: ~/llama-server/models/                  │
│  Port: 8080 (public API)                        │
├─────────────────────────────────────────────────┤
│       Native llama.cpp (Jan backend)             │
│  Path: %APPDATA%/Jan/data/llamacpp/backends/...  │
│  Port: 12780 (auto-started by Rust server)      │
└─────────────────────────────────────────────────┘
```

---

## Capabilities

| Capability | Supported | Details |
|-----------|-----------|---------|
| **Chat completions** | ✅ | `POST /v1/chat/completions` |
| **Model listing** | ✅ | `GET /v1/models` |
| **Health check** | ✅ | `GET /health` |
| **Streaming** | ✅ | OpenAI SSE streaming (native llama.cpp) |
| **Reasoning** | ✅ | `reasoning_content` field supported |
| **Multiple models** | ✅ | Any GGUF in `~/llama-server/models/` |
| **API key auth** | ⬜ | Not configured (local-only) |

---

## Integration Points

### 1. Direct HTTP (no dependency)

The `LlamaClient` class in `llama_client.py` is a standalone 54-line file with zero external dependencies (only `requests`). It can be:

- **Copied directly** into `src/CORE/llama_client.py`
- **Used via subprocess** from any worm (calling `llama_client.py` directly)
- **Embbeded inline** in agent code that needs local inference

### 2. CORE Agent Integration

Since CORE worms already use a `run()` → `async_run()` pattern, integration is straightforward:

```python
# In any CORE worm:
from CORE.llama_client import LlamaClient
client = LlamaClient()

async def analyze(data):
    response = client.chat([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(data)}
    ])
    return response["choices"][0]["message"]["content"]
```

### 3. Replacement for Cloud APIs

Currently, several CORE components may depend on cloud-based LLM APIs (OpenAI, Anthropic). LlamaServer provides a zero-cost local alternative:

| Cloud API | Local Equivalent | Benefit |
|-----------|-----------------|---------|
| OpenAI chat completions | `POST /v1/chat/completions` | Same API shape |
| OpenAI model list | `GET /v1/models` | Same response format |
| Streaming | SSE streaming | Same event format |

---

## Strengths for CORE Integration

1. **Zero API costs** — All inference runs locally on Intel SYCL/Arc GPU
2. **Low latency** — Local inference, no network hop (sub-100ms for small models)
3. **Privacy** — No data leaves the machine
4. **OpenAI-compatible** — Drop-in replacement for existing cloud API calls
5. **Resilient** — Works offline, no rate limits
6. **GGUF models** — Huge ecosystem of open-weights models (Llama, Mistral, Gemma, etc.)

---

## Limitations

1. **Requires Rust build** — `python run.py build` needs cargo + Intel oneAPI (~30 min initial build)
2. **GPU requirement** — SYCL backend needs Intel Arc GPU; fallback to CPU is slow
3. **Single model** — Only one model loaded at a time (no multi-model routing)
4. **No built-in sandboxing** — Prompt injection could execute arbitrary model behavior
5. **Not production-hardened** — No authentication, rate limiting, or monitoring built in
6. **Windows-only** — Relies on `taskkill`, `tasklist`, Jan appdata paths

---

## Recommendation

**Adopt as optional inference backend** — integrate `LlamaClient` into CORE as a
secondary/fallback inference provider. Primary cloud APIs remain the default;
LlamaServer activates when available (health check passes).

### Implementation Plan

| Step | Effort | Description |
|------|--------|-------------|
| 1. Copy `llama_client.py` → `src/CORE/llama_client.py` | 5 min | Pure copy, no changes needed |
| 2. Add `LlamaInferenceProvider` to agent framework | 30 min | Wraps LlamaClient in CORE's Provider ABC |
| 3. Add health-check auto-detection | 15 min | Probe `/health` at startup, fall back to cloud |
| 4. Document in OBSERVABILITY.md | 10 min | Usage, config, troubleshooting |

### Quick-start

```bash
# On the Desktop machine with LlamaServer:
cd ~/Desktop/LlamaServer
python run.py build   # One-time Rust compile
python run.py start   # Start the server
python run.py chat    # Verify it works

# Then from any CORE worm:
python -c "from CORE.llama_client import LlamaClient; c = LlamaClient(); print(c.health())"
```
