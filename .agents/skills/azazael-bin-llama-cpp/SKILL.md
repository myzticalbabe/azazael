---
name: azazael-bin-llama-cpp
description: Callable skill for llama-cpp — LLM inference engine for GGUF models (llama.cpp)
metadata:
  category: ai
  project: azazael
  priority: medium
---

# llama-cpp

> LLM inference engine for GGUF models (llama.cpp)

## Identity

| Field | Value |
|-------|-------|
| Tool | `llama-cpp` |
| Version | `not installed` |
| Status | NOT INSTALLED — install first |

## Install

```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp && cmake -B build && cmake --build build --config Release -j
```

## EXECUTE — canonical invocations

**Run chat with GGUF model:**

```bash
llama-cli -m model.gguf -p 'Hello' -n 128
```

**Serve OpenAI-compatible API:**

```bash
llama-server -m model.gguf --port 8080
```

**List supported models:**

```bash
llama-cli --help | grep -i model
```

## Verify

```bash
command -v llama-cpp && echo 'llama-cpp installed OK'
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
