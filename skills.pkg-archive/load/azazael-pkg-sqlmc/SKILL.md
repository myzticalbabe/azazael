---
name: azazael-pkg-sqlmc
description: Callable skill for Python package sqlmc 1.1.0 — SQL Injection Massive Checker for a domain
metadata:
  category: packages
  project: azazael
  priority: low
---

# sqlmc 1.1.0

> SQL Injection Massive Checker for a domain

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sqlmc` |
| Version | `1.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `sqlmc`

Invocation pattern:

```bash
sqlmc --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `sqlmc`

Invocation pattern:

```python
import sqlmc
print("sqlmc loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import sqlmc; print('sqlmc OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
