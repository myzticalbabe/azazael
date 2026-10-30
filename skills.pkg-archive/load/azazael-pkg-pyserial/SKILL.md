---
name: azazael-pkg-pyserial
description: Callable skill for Python package pyserial 3.5 — Python Serial Port Extension
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyserial 3.5

> Python Serial Port Extension

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyserial` |
| Version | `3.5` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pyserial-miniterm`
- `pyserial-ports`

Invocation pattern:

```bash
pyserial-miniterm --help
```

Alternates:

```bash
pyserial-ports --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show pyserial
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
