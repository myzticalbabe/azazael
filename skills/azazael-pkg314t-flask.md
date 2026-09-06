---
name: azazael-pkg314t-flask
description: Callable skill for Python package Flask 3.1.3 — A simple framework for building complex web applications.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Flask 3.1.3

> A simple framework for building complex web applications.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Flask` |
| Version | `3.1.3` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `flask`

Invocation pattern:

```bash
flask --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Flask`

Invocation pattern:

```python
import Flask
print("Flask loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import Flask; print('Flask OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
