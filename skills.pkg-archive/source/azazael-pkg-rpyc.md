---
name: azazael-pkg-rpyc
description: Callable skill for Python package rpyc 6.0.2 — Remote Python Call (RPyC) is a transparent and symmetric distributed computing library
metadata:
  category: packages
  project: azazael
  priority: low
---

# rpyc 6.0.2

> Remote Python Call (RPyC) is a transparent and symmetric distributed computing library

## Identity

| Field | Value |
|-------|-------|
| Distribution | `rpyc` |
| Version | `6.0.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `rpyc_classic`
- `rpyc_classic.py`
- `rpyc_registry`
- `rpyc_registry.py`

Invocation pattern:

```bash
rpyc_classic --help
```

Alternates:

```bash
rpyc_classic.py --help
rpyc_registry --help
rpyc_registry.py --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show rpyc
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
