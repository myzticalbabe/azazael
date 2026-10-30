---
name: azazael-pkg-waybackpy
description: Callable skill for Python package waybackpy 3.0.6 — Python package that interfaces with the Internet Archive's Wayback Machine APIs. Archive pages and retrieve archived pages easily.
metadata:
  category: packages
  project: azazael
  priority: low
---

# waybackpy 3.0.6

> Python package that interfaces with the Internet Archive's Wayback Machine APIs. Archive pages and retrieve archived pages easily.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `waybackpy` |
| Version | `3.0.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `waybackpy`

Invocation pattern:

```bash
waybackpy --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `waybackpy`

Invocation pattern:

```python
import waybackpy
print("waybackpy loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import waybackpy; print('waybackpy OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
