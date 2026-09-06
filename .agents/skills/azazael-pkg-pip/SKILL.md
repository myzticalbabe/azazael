---
name: azazael-pkg-pip
description: Callable skill for Python package pip 26.1.1 — The PyPA recommended tool for installing Python packages.
metadata:
  category: packages
  project: azazael
  priority: low
---

# pip 26.1.1

> The PyPA recommended tool for installing Python packages.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pip` |
| Version | `26.1.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pip`
- `pip3`

Invocation pattern:

```bash
pip --help
```

Alternates:

```bash
pip3 --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show pip
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
