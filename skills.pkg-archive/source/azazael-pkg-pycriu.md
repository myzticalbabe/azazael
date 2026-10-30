---
name: azazael-pkg-pycriu
description: Callable skill for Python package pycriu 4.2 — Python bindings for CRIU
metadata:
  category: packages
  project: azazael
  priority: low
---

# pycriu 4.2

> Python bindings for CRIU

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pycriu` |
| Version | `4.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `pycriu`

Invocation pattern:

```python
import pycriu
print("pycriu loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pycriu; print('pycriu OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
