---
name: azazael-pkg-psutil
description: Callable skill for Python package psutil 7.1.0 — Cross-platform lib for process and system monitoring.
metadata:
  category: packages
  project: azazael
  priority: low
---

# psutil 7.1.0

> Cross-platform lib for process and system monitoring.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `psutil` |
| Version | `7.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

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
/usr/bin/python3.13 -c "import psutil; print('psutil OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
