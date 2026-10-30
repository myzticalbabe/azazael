---
name: azazael-pkg-tables
description: Callable skill for Python package tables 3.11.1 — Hierarchical datasets for Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# tables 3.11.1

> Hierarchical datasets for Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tables` |
| Version | `3.11.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pt2to3`
- `ptdump`
- `ptrepack`
- `pttree`

Invocation pattern:

```bash
pt2to3 --help
```

Alternates:

```bash
ptdump --help
ptrepack --help
pttree --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `tables`

Invocation pattern:

```python
import tables
print("tables loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tables; print('tables OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
