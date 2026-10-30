---
name: azazael-pkg-sympy
description: Callable skill for Python package sympy 1.14.0 — Computer algebra system (CAS) in Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# sympy 1.14.0

> Computer algebra system (CAS) in Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sympy` |
| Version | `1.14.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `isympy`

Invocation pattern:

```bash
isympy --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `sympy`

Invocation pattern:

```python
import sympy
print("sympy loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import sympy; print('sympy OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
