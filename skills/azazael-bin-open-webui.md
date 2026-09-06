---
name: azazael-bin-open-webui
description: Callable skill for open-webui — Self-hosted AI chat web UI (works with Ollama/OpenAI)
metadata:
  category: ai
  project: azazael
  priority: medium
---

# open-webui

> Self-hosted AI chat web UI (works with Ollama/OpenAI)

## Identity

| Field | Value |
|-------|-------|
| Tool | `open-webui` |
| Version | `not installed` |
| Status | NOT INSTALLED — install first |

## Install

```bash
pip install open-webui  (or docker run ghcr.io/open-webui/open-webui:main)
```

## EXECUTE — canonical invocations

**Start server:**

```bash
open-webui serve  (default http://localhost:8080)
```

**Docker run:**

```bash
docker run -d -p 3000:8080 ghcr.io/open-webui/open-webui:main
```

## Verify

```bash
command -v open-webui && echo 'open-webui installed OK'
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
