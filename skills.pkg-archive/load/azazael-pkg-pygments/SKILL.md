---
name: azazael-pkg-pygments
description: Callable skill for Python package Pygments 2.19.2 — Pygments is a syntax highlighting package written in Python.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Pygments 2.19.2

> Pygments is a syntax highlighting package written in Python.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Pygments` |
| Version | `2.19.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pygmentize`

Invocation pattern:

```bash
pygmentize --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show Pygments
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
