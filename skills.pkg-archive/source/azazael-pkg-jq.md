---
name: azazael-pkg-jq
description: Callable skill for Python package jq 1.11.0 — jq is a lightweight and flexible JSON processor.
metadata:
  category: packages
  project: azazael
  priority: low
---

# jq 1.11.0

> jq is a lightweight and flexible JSON processor.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `jq` |
| Version | `1.11.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `jq`

Invocation pattern:

```python
import jq
print("jq loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import jq; print('jq OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
