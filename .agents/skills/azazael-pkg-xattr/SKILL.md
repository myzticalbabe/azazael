---
name: azazael-pkg-xattr
description: Callable skill for Python package xattr 1.3.0 — Python wrapper for extended filesystem attributes
metadata:
  category: packages
  project: azazael
  priority: low
---

# xattr 1.3.0

> Python wrapper for extended filesystem attributes

## Identity

| Field | Value |
|-------|-------|
| Distribution | `xattr` |
| Version | `1.3.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `xattr`

Invocation pattern:

```bash
xattr --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `xattr`

Invocation pattern:

```python
import xattr
print("xattr loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import xattr; print('xattr OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
