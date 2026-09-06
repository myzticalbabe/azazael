---
name: azazael-pkg314t-psutil
description: Callable skill for Python package psutil 7.2.2 — Cross-platform lib for process and system monitoring.
metadata:
  category: packages
  project: azazael
  priority: low
---

# psutil 7.2.2

> Cross-platform lib for process and system monitoring.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `psutil` |
| Version | `7.2.2` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — Python API

Importable top-level module(s):

- `psutil`

Invocation pattern:

```python
import psutil
print("psutil loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import psutil; print('psutil OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
