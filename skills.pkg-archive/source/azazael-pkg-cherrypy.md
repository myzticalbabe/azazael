---
name: azazael-pkg-cherrypy
description: Callable skill for Python package CherryPy 18.10.0 — Object-Oriented HTTP framework
metadata:
  category: packages
  project: azazael
  priority: low
---

# CherryPy 18.10.0

> Object-Oriented HTTP framework

## Identity

| Field | Value |
|-------|-------|
| Distribution | `CherryPy` |
| Version | `18.10.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `cherryd`

Invocation pattern:

```bash
cherryd --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `CherryPy`

Invocation pattern:

```python
import CherryPy
print("CherryPy loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import CherryPy; print('CherryPy OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
