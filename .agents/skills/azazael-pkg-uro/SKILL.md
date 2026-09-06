---
name: azazael-pkg-uro
description: Callable skill for Python package uro 1.0.2 — A python tool to declutter url lists for crawling/pentesting
metadata:
  category: packages
  project: azazael
  priority: low
---

# uro 1.0.2

> A python tool to declutter url lists for crawling/pentesting

## Identity

| Field | Value |
|-------|-------|
| Distribution | `uro` |
| Version | `1.0.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `uro`

Invocation pattern:

```bash
uro --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `uro`

Invocation pattern:

```python
import uro
print("uro loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import uro; print('uro OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
