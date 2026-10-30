---
name: azazael-pkg-babel
description: Callable skill for Python package babel 2.17.0 — Internationalization utilities
metadata:
  category: packages
  project: azazael
  priority: low
---

# babel 2.17.0

> Internationalization utilities

## Identity

| Field | Value |
|-------|-------|
| Distribution | `babel` |
| Version | `2.17.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pybabel`

Invocation pattern:

```bash
pybabel --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `babel`

Invocation pattern:

```python
import babel
print("babel loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import babel; print('babel OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
