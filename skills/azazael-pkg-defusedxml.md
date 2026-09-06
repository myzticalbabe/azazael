---
name: azazael-pkg-defusedxml
description: Callable skill for Python package defusedxml 0.7.1 — XML bomb protection for Python stdlib modules
metadata:
  category: packages
  project: azazael
  priority: low
---

# defusedxml 0.7.1

> XML bomb protection for Python stdlib modules

## Identity

| Field | Value |
|-------|-------|
| Distribution | `defusedxml` |
| Version | `0.7.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `defusedxml`

Invocation pattern:

```python
import defusedxml
print("defusedxml loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import defusedxml; print('defusedxml OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
