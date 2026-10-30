---
name: azazael-pkg-dfvfs
description: Callable skill for Python package dfvfs 20251019 — Digital Forensics Virtual File System (dfVFS).
metadata:
  category: packages
  project: azazael
  priority: low
---

# dfvfs 20251019

> Digital Forensics Virtual File System (dfVFS).

## Identity

| Field | Value |
|-------|-------|
| Distribution | `dfvfs` |
| Version | `20251019` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `dfvfs`

Invocation pattern:

```python
import dfvfs
print("dfvfs loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import dfvfs; print('dfvfs OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
