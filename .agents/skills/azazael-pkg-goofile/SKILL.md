---
name: azazael-pkg-goofile
description: Callable skill for Python package goofile 1.6 — Update of https://code.google.com/archive/p/goofile/ for Python 3
metadata:
  category: packages
  project: azazael
  priority: low
---

# goofile 1.6

> Update of https://code.google.com/archive/p/goofile/ for Python 3

## Identity

| Field | Value |
|-------|-------|
| Distribution | `goofile` |
| Version | `1.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `goofile`

Invocation pattern:

```bash
goofile --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `goofile`

Invocation pattern:

```python
import goofile
print("goofile loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import goofile; print('goofile OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
