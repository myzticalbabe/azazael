---
name: azazael-pkg-pycparser
description: Callable skill for Python package pycparser 3.0 — C parser in Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# pycparser 3.0

> C parser in Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pycparser` |
| Version | `3.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `pycparser`

Invocation pattern:

```python
import pycparser
print("pycparser loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pycparser; print('pycparser OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
