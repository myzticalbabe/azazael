---
name: azazael-pkg-markdown
description: Callable skill for Python package Markdown 3.10.2 — Python implementation of John Gruber's Markdown.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Markdown 3.10.2

> Python implementation of John Gruber's Markdown.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Markdown` |
| Version | `3.10.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `markdown_py`

Invocation pattern:

```bash
markdown_py --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Markdown`

Invocation pattern:

```python
import Markdown
print("Markdown loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import Markdown; print('Markdown OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
