---
name: azazael-pkg-gvm-tools
description: Callable skill for Python package gvm-tools 25.4.6 — Tools to control a GSM/GVM over GMP or OSP
metadata:
  category: packages
  project: azazael
  priority: low
---

# gvm-tools 25.4.6

> Tools to control a GSM/GVM over GMP or OSP

## Identity

| Field | Value |
|-------|-------|
| Distribution | `gvm-tools` |
| Version | `25.4.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `gvm-cli`
- `gvm-pyshell`
- `gvm-script`

Invocation pattern:

```bash
gvm-cli --help
```

Alternates:

```bash
gvm-pyshell --help
gvm-script --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show gvm-tools
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
