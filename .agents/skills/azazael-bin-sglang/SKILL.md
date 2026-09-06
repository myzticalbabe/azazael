---
name: azazael-bin-sglang
description: Callable skill for sglang — Fast serving framework for LLMs and VLMs
metadata:
  category: ai
  project: azazael
  priority: medium
---

# sglang

> Fast serving framework for LLMs and VLMs

## Identity

| Field | Value |
|-------|-------|
| Tool | `sglang` |
| Version | `not installed` |
| Status | NOT INSTALLED — install first |

## Install

```bash
pip install sglang[all]
```

## EXECUTE — canonical invocations

**Serve model:**

```bash
python3 -m sglang.launch_server --model-path meta-llama/Llama-3.1-8B-Instruct --port 30000
```

**Run with torch compile:**

```bash
python3 -m sglang.launch_server --model-path model --torch-compile
```

## Verify

```bash
command -v sglang && echo 'sglang installed OK'
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
