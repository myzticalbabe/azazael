---
name: azazael-pkg314t-librt
description: Callable skill for Python package librt 0.11.0 — Mypyc runtime library
metadata:
  category: packages
  project: azazael
  priority: low
---

# librt 0.11.0

> Mypyc runtime library

## Identity

| Field | Value |
|-------|-------|
| Distribution | `librt` |
| Version | `0.11.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — Python API

Importable top-level module(s):

- `librt`

Invocation pattern:

```python
import librt
print("librt loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import librt; print('librt OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
