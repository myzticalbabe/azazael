---
name: azazael-pkg-raven
description: Callable skill for Python package raven 1.1.0 — A lightweight file upload service used for penetration testing and incident response.
metadata:
  category: packages
  project: azazael
  priority: low
---

# raven 1.1.0

> A lightweight file upload service used for penetration testing and incident response.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `raven` |
| Version | `1.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `raven`

Invocation pattern:

```bash
raven --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `raven`

Invocation pattern:

```python
import raven
print("raven loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import raven; print('raven OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
