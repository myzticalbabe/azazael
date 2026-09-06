---
name: azazael-bin-ollama
description: Callable skill for ollama — Run open-source LLMs locally with one command (170K+ stars)
metadata:
  category: ai
  project: azazael
  priority: medium
---

# ollama

> Run open-source LLMs locally with one command (170K+ stars)

## Identity

| Field | Value |
|-------|-------|
| Tool | `ollama` |
| Version | `0.32.15 (WSL + Windows, Vulkan/Arc GPU enabled)` |
| Status | INSTALLED |

## Install

```bash
Installed: WSL (0.32.15) + Windows (0.32.15, GPU-enabled: OLLAMA_VULKAN=1 OLLAMA_IGPU_ENABLE=1, Intel Arc 140T via Vulkan)
```

## EXECUTE — canonical invocations

**Pull a model:**

```bash
ollama pull llama3
```

**Run chat:**

```bash
ollama run llama3
```

**Serve API:**

```bash
ollama serve  (default :11434)
```

## Verify

```bash
ollama --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
