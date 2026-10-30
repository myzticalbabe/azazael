---
name: azazael-pkg-hupper
description: Callable skill for Python package hupper 1.12 — Integrated process monitor for developing and reloading daemons.
metadata:
  category: packages
  project: azazael
  priority: low
---

# hupper 1.12

> Integrated process monitor for developing and reloading daemons.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `hupper` |
| Version | `1.12` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `hupper`

Invocation pattern:

```bash
hupper --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `hupper`

Invocation pattern:

```python
import hupper
print("hupper loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import hupper; print('hupper OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
