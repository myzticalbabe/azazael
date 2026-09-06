---
name: azazael-bin-vllm
description: Callable skill for vllm — High-throughput LLM serving engine (PagedAttention)
metadata:
  category: ai
  project: azazael
  priority: medium
---

# vllm

> High-throughput LLM serving engine (PagedAttention)

## Identity

| Field | Value |
|-------|-------|
| Tool | `vllm` |
| Version | `not installed` |
| Status | NOT INSTALLED — install first |

## Install

```bash
pip install vllm
```

## EXECUTE — canonical invocations

**Serve OpenAI-compatible API:**

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct
```

**Serve with tensor parallelism:**

```bash
vllm serve model --tensor-parallel-size 2
```

## Verify

```bash
command -v vllm && echo 'vllm installed OK'
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
