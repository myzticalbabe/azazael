---
name: azazael-pkg-maryam
description: Callable skill for Python package maryam 2.5.2.post2 — OWASP Maryam is a modular/optional open-source framework based on OSINT and data gathering.
metadata:
  category: packages
  project: azazael
  priority: low
---

# maryam 2.5.2.post2

> OWASP Maryam is a modular/optional open-source framework based on OSINT and data gathering.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `maryam` |
| Version | `2.5.2.post2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `maryam`

Invocation pattern:

```python
import maryam
print("maryam loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import maryam; print('maryam OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
