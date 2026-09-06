---
name: azazael-pkg-uvloop
description: Callable skill for Python package uvloop 0.22.1 — Fast implementation of asyncio event loop on top of libuv
metadata:
  category: packages
  project: azazael
  priority: low
---

# uvloop 0.22.1

> Fast implementation of asyncio event loop on top of libuv

## Identity

| Field | Value |
|-------|-------|
| Distribution | `uvloop` |
| Version | `0.22.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `uvloop`

Invocation pattern:

```python
import uvloop
print("uvloop loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import uvloop; print('uvloop OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
