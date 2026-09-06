---
name: azazael-pkg-phpserialize
description: Callable skill for Python package phpserialize 1.3 — a port of the serialize and unserialize functions of php to python.
metadata:
  category: packages
  project: azazael
  priority: low
---

# phpserialize 1.3

> a port of the serialize and unserialize functions of php to python.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `phpserialize` |
| Version | `1.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `phpserialize`

Invocation pattern:

```python
import phpserialize
print("phpserialize loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import phpserialize; print('phpserialize OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
