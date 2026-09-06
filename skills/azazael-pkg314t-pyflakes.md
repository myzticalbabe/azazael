---
name: azazael-pkg314t-pyflakes
description: Callable skill for Python package pyflakes 3.4.0 — passive checker of Python programs
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyflakes 3.4.0

> passive checker of Python programs

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyflakes` |
| Version | `3.4.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `pyflakes`

Invocation pattern:

```bash
pyflakes --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pyflakes`

Invocation pattern:

```python
import pyflakes
print("pyflakes loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import pyflakes; print('pyflakes OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
