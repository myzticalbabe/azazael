---
name: azazael-pkg-crit
description: Callable skill for Python package crit 4.2 — CRiu Image Tool
metadata:
  category: packages
  project: azazael
  priority: low
---

# crit 4.2

> CRiu Image Tool

## Identity

| Field | Value |
|-------|-------|
| Distribution | `crit` |
| Version | `4.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `crit`

Invocation pattern:

```bash
crit --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `crit`

Invocation pattern:

```python
import crit
print("crit loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import crit; print('crit OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
