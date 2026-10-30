---
name: azazael-pkg-sphinx
description: Callable skill for Python package Sphinx 9.1.0 — Python documentation generator
metadata:
  category: packages
  project: azazael
  priority: low
---

# Sphinx 9.1.0

> Python documentation generator

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Sphinx` |
| Version | `9.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `sphinx-apidoc`
- `sphinx-autogen`
- `sphinx-build`
- `sphinx-quickstart`

Invocation pattern:

```bash
sphinx-apidoc --help
```

Alternates:

```bash
sphinx-autogen --help
sphinx-build --help
sphinx-quickstart --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show Sphinx
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
