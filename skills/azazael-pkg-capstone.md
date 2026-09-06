---
name: azazael-pkg-capstone
description: Callable skill for Python package capstone 5.0.7 — Capstone disassembly engine
metadata:
  category: packages
  project: azazael
  priority: low
---

# capstone 5.0.7

> Capstone disassembly engine

## Identity

| Field | Value |
|-------|-------|
| Distribution | `capstone` |
| Version | `5.0.7` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `capstone`

Invocation pattern:

```python
import capstone
print("capstone loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import capstone; print('capstone OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
