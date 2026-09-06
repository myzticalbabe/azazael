---
name: azazael-pkg314t-pygments
description: Callable skill for Python package Pygments 2.20.0 — Pygments is a syntax highlighting package written in Python.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Pygments 2.20.0

> Pygments is a syntax highlighting package written in Python.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Pygments` |
| Version | `2.20.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `pygmentize`

Invocation pattern:

```bash
pygmentize --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Pygments`

Invocation pattern:

```python
import Pygments
print("Pygments loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import Pygments; print('Pygments OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
