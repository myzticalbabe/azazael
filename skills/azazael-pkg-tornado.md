---
name: azazael-pkg-tornado
description: Callable skill for Python package tornado 6.5.5 — Tornado is a Python web framework and asynchronous networking library, originally developed at FriendFeed.
metadata:
  category: packages
  project: azazael
  priority: low
---

# tornado 6.5.5

> Tornado is a Python web framework and asynchronous networking library, originally developed at FriendFeed.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tornado` |
| Version | `6.5.5` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `tornado`

Invocation pattern:

```python
import tornado
print("tornado loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tornado; print('tornado OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
