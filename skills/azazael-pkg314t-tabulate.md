---
name: azazael-pkg314t-tabulate
description: Callable skill for Python package tabulate 0.10.0 — Pretty-print tabular data
metadata:
  category: packages
  project: azazael
  priority: low
---

# tabulate 0.10.0

> Pretty-print tabular data

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tabulate` |
| Version | `0.10.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

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
/usr/local/bin/python3.14t -c "import tabulate; print('tabulate OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
