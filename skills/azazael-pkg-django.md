---
name: azazael-pkg-django
description: Callable skill for Python package Django 4.2.30 — A high-level Python web framework that encourages rapid development and clean, pragmatic design.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Django 4.2.30

> A high-level Python web framework that encourages rapid development and clean, pragmatic design.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Django` |
| Version | `4.2.30` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `django-admin`

Invocation pattern:

```bash
django-admin --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Django`

Invocation pattern:

```python
import Django
print("Django loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import Django; print('Django OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
