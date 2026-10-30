---
name: azazael-pkg-tabulate
description: Callable skill for Python package tabulate 0.9.0 — Pretty-print tabular data
metadata:
  category: packages
  project: azazael
  priority: low
---

# tabulate 0.9.0

> Pretty-print tabular data

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tabulate` |
| Version | `0.9.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `tabulate`

Invocation pattern:

```bash
tabulate --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `tabulate`

Invocation pattern:

```python
import tabulate
print("tabulate loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tabulate; print('tabulate OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
