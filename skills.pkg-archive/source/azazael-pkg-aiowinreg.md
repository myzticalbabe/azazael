---
name: azazael-pkg-aiowinreg
description: Callable skill for Python package aiowinreg 0.0.7 — Windows registry file reader
metadata:
  category: packages
  project: azazael
  priority: low
---

# aiowinreg 0.0.7

> Windows registry file reader

## Identity

| Field | Value |
|-------|-------|
| Distribution | `aiowinreg` |
| Version | `0.0.7` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `awinreg`

Invocation pattern:

```bash
awinreg --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `aiowinreg`

Invocation pattern:

```python
import aiowinreg
print("aiowinreg loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import aiowinreg; print('aiowinreg OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
