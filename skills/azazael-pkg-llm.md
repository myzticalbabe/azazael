---
name: azazael-pkg-llm
description: Callable skill for Python package llm 0.30 — CLI utility and Python library for interacting with Large Language Models from organizations like OpenAI, Anthropic and Gemini plus local models installed on yo
metadata:
  category: packages
  project: azazael
  priority: low
---

# llm 0.30

> CLI utility and Python library for interacting with Large Language Models from organizations like OpenAI, Anthropic and Gemini plus local models installed on yo

## Identity

| Field | Value |
|-------|-------|
| Distribution | `llm` |
| Version | `0.30` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `llm`

Invocation pattern:

```bash
llm --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `llm`

Invocation pattern:

```python
import llm
print("llm loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import llm; print('llm OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
