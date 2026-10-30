---
name: azazael-pkg-pyinstaller
description: Callable skill for Python package pyinstaller 6.18.0 — PyInstaller bundles a Python application and all its dependencies into a single package.
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyinstaller 6.18.0

> PyInstaller bundles a Python application and all its dependencies into a single package.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyinstaller` |
| Version | `6.18.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pyi-archive_viewer`
- `pyi-bindepend`
- `pyi-grab_version`
- `pyi-makespec`
- `pyi-set_version`
- `pyinstaller`

Invocation pattern:

```bash
pyi-archive_viewer --help
```

Alternates:

```bash
pyi-bindepend --help
pyi-grab_version --help
pyi-makespec --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show pyinstaller
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
