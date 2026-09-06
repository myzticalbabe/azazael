---
name: azazael-pkg-distributed
description: Callable skill for Python package distributed 2024.12.1 — Distributed scheduler for Dask
metadata:
  category: packages
  project: azazael
  priority: low
---

# distributed 2024.12.1

> Distributed scheduler for Dask

## Identity

| Field | Value |
|-------|-------|
| Distribution | `distributed` |
| Version | `2024.12.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `dask-scheduler`
- `dask-ssh`
- `dask-worker`

Invocation pattern:

```bash
dask-scheduler --help
```

Alternates:

```bash
dask-ssh --help
dask-worker --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `distributed`

Invocation pattern:

```python
import distributed
print("distributed loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import distributed; print('distributed OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
