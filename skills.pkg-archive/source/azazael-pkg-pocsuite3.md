---
name: azazael-pkg-pocsuite3
description: Callable skill for Python package pocsuite3 2.1.0 — Open-sourced remote vulnerability testing framework.
metadata:
  category: packages
  project: azazael
  priority: low
---

# pocsuite3 2.1.0

> Open-sourced remote vulnerability testing framework.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pocsuite3` |
| Version | `2.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `poc-console`
- `pocsuite`

Invocation pattern:

```bash
poc-console --help
```

Alternates:

```bash
pocsuite --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pocsuite3`

Invocation pattern:

```python
import pocsuite3
print("pocsuite3 loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pocsuite3; print('pocsuite3 OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
