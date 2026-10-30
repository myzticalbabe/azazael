---
name: azazael-pkg-ropper
description: Callable skill for Python package ropper 1.13.8 — Show information about files in different file formats and find gadgets to build rop chains for different architectures.
metadata:
  category: packages
  project: azazael
  priority: low
---

# ropper 1.13.8

> Show information about files in different file formats and find gadgets to build rop chains for different architectures.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `ropper` |
| Version | `1.13.8` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `ropper`

Invocation pattern:

```bash
ropper --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `ropper`

Invocation pattern:

```python
import ropper
print("ropper loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import ropper; print('ropper OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
