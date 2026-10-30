---
name: azazael-pkg-tenacity
description: Callable skill for Python package tenacity 9.1.4 — Retry code until it succeeds
metadata:
  category: packages
  project: azazael
  priority: low
---

# tenacity 9.1.4

> Retry code until it succeeds

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tenacity` |
| Version | `9.1.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `tenacity`

Invocation pattern:

```python
import tenacity
print("tenacity loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tenacity; print('tenacity OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
