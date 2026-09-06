---
name: azazael-pkg314t-greenlet
description: Callable skill for Python package greenlet 3.5.5 — Lightweight in-process concurrent programming
metadata:
  category: packages
  project: azazael
  priority: low
---

# greenlet 3.5.5

> Lightweight in-process concurrent programming

## Identity

| Field | Value |
|-------|-------|
| Distribution | `greenlet` |
| Version | `3.5.5` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — Python API

Importable top-level module(s):

- `greenlet`

Invocation pattern:

```python
import greenlet
print("greenlet loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import greenlet; print('greenlet OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
