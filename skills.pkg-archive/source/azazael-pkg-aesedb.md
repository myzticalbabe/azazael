---
name: azazael-pkg-aesedb
description: Callable skill for Python package aesedb 0.1.4 — NTDS parser toolkit
metadata:
  category: packages
  project: azazael
  priority: low
---

# aesedb 0.1.4

> NTDS parser toolkit

## Identity

| Field | Value |
|-------|-------|
| Distribution | `aesedb` |
| Version | `0.1.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `antdsparse`

Invocation pattern:

```bash
antdsparse --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `aesedb`

Invocation pattern:

```python
import aesedb
print("aesedb loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import aesedb; print('aesedb OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
