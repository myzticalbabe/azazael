---
name: azazael-pkg-dask
description: Callable skill for Python package dask 2024.12.1+dfsg — Parallel PyData with Task Scheduling
metadata:
  category: packages
  project: azazael
  priority: low
---

# dask 2024.12.1+dfsg

> Parallel PyData with Task Scheduling

## Identity

| Field | Value |
|-------|-------|
| Distribution | `dask` |
| Version | `2024.12.1+dfsg` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `dask`

Invocation pattern:

```bash
dask --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `dask`

Invocation pattern:

```python
import dask
print("dask loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import dask; print('dask OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
