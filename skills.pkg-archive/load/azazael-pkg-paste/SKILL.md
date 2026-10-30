---
name: azazael-pkg-paste
description: Callable skill for Python package Paste 3.10.1 — Tools for using a Web Server Gateway Interface stack
metadata:
  category: packages
  project: azazael
  priority: low
---

# Paste 3.10.1

> Tools for using a Web Server Gateway Interface stack

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Paste` |
| Version | `3.10.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `Paste`
- `PasteDeploy`
- `PasteScript`

Invocation pattern:

```python
import Paste
print("Paste loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import Paste; print('Paste OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
