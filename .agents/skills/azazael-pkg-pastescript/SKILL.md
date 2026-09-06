---
name: azazael-pkg-pastescript
description: Callable skill for Python package PasteScript 3.7.0 — A pluggable command-line frontend, including commands to setup package file layouts
metadata:
  category: packages
  project: azazael
  priority: low
---

# PasteScript 3.7.0

> A pluggable command-line frontend, including commands to setup package file layouts

## Identity

| Field | Value |
|-------|-------|
| Distribution | `PasteScript` |
| Version | `3.7.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `paster`

Invocation pattern:

```bash
paster --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show PasteScript
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
