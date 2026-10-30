---
name: azazael-pkg-ipython
description: Callable skill for Python package ipython 9.11.0 — IPython: Productive Interactive Computing
metadata:
  category: packages
  project: azazael
  priority: low
---

# ipython 9.11.0

> IPython: Productive Interactive Computing

## Identity

| Field | Value |
|-------|-------|
| Distribution | `ipython` |
| Version | `9.11.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `ipython`
- `ipython3`

Invocation pattern:

```bash
ipython --help
```

Alternates:

```bash
ipython3 --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show ipython
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
