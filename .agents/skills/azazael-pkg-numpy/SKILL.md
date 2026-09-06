---
name: azazael-pkg-numpy
description: Callable skill for Python package numpy 2.3.5 — Fundamental package for array computing in Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# numpy 2.3.5

> Fundamental package for array computing in Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `numpy` |
| Version | `2.3.5` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `f2py`
- `f2py3`
- `f2py3.13`
- `f2py3.14`
- `numpy-config`

Invocation pattern:

```bash
f2py --help
```

Alternates:

```bash
f2py3 --help
f2py3.13 --help
f2py3.14 --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show numpy
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
