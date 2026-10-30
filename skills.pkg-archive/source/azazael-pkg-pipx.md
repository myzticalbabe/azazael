---
name: azazael-pkg-pipx
description: Callable skill for Python package pipx 1.14.0 — Install and Run Python Applications in Isolated Environments
metadata:
  category: packages
  project: azazael
  priority: low
---

# pipx 1.14.0

> Install and Run Python Applications in Isolated Environments

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pipx` |
| Version | `1.14.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pipx`

Invocation pattern:

```bash
pipx --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show pipx
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
