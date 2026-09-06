---
name: azazael-pkg-pyinotify
description: Callable skill for Python package pyinotify 0.9.6 — Linux filesystem events monitoring
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyinotify 0.9.6

> Linux filesystem events monitoring

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyinotify` |
| Version | `0.9.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `pyinotify`

Invocation pattern:

```python
import pyinotify
print("pyinotify loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pyinotify; print('pyinotify OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
