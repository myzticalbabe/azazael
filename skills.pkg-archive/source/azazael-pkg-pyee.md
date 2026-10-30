---
name: azazael-pkg-pyee
description: Callable skill for Python package pyee 13.0.0 — A rough port of Node.js's EventEmitter to Python with a few tricks of its own
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyee 13.0.0

> A rough port of Node.js's EventEmitter to Python with a few tricks of its own

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyee` |
| Version | `13.0.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `pyee`

Invocation pattern:

```python
import pyee
print("pyee loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pyee; print('pyee OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
