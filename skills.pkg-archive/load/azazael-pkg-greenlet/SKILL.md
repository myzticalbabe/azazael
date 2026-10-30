---
name: azazael-pkg-greenlet
description: Callable skill for Python package greenlet 3.3.2 — Lightweight in-process concurrent programming
metadata:
  category: packages
  project: azazael
  priority: low
---

# greenlet 3.3.2

> Lightweight in-process concurrent programming

## Identity

| Field | Value |
|-------|-------|
| Distribution | `greenlet` |
| Version | `3.3.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

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
/usr/bin/python3.13 -c "import greenlet; print('greenlet OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
