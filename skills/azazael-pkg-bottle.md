---
name: azazael-pkg-bottle
description: Callable skill for Python package bottle 0.13.2 — Fast and simple WSGI-framework for small web-applications.
metadata:
  category: packages
  project: azazael
  priority: low
---

# bottle 0.13.2

> Fast and simple WSGI-framework for small web-applications.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `bottle` |
| Version | `0.13.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `bottle`

Invocation pattern:

```bash
bottle --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `bottle`

Invocation pattern:

```python
import bottle
print("bottle loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import bottle; print('bottle OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
