---
name: azazael-pkg-defusedcsv
description: Callable skill for Python package defusedcsv 3.0.0 — Drop-in replacement for Python's CSV library that tries to mitigate CSV injection attacks
metadata:
  category: packages
  project: azazael
  priority: low
---

# defusedcsv 3.0.0

> Drop-in replacement for Python's CSV library that tries to mitigate CSV injection attacks

## Identity

| Field | Value |
|-------|-------|
| Distribution | `defusedcsv` |
| Version | `3.0.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `defusedcsv`

Invocation pattern:

```python
import defusedcsv
print("defusedcsv loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import defusedcsv; print('defusedcsv OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
