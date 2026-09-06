---
name: azazael-pkg-portend
description: Callable skill for Python package portend 3.2.0 — TCP port monitoring and discovery
metadata:
  category: packages
  project: azazael
  priority: low
---

# portend 3.2.0

> TCP port monitoring and discovery

## Identity

| Field | Value |
|-------|-------|
| Distribution | `portend` |
| Version | `3.2.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `portend`

Invocation pattern:

```python
import portend
print("portend loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import portend; print('portend OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
