---
name: azazael-pkg-penelope-shell-handler
description: Callable skill for Python package penelope-shell-handler 0.20.0 — Post-exploitation shell handler for authorized security testing
metadata:
  category: packages
  project: azazael
  priority: low
---

# penelope-shell-handler 0.20.0

> Post-exploitation shell handler for authorized security testing

## Identity

| Field | Value |
|-------|-------|
| Distribution | `penelope-shell-handler` |
| Version | `0.20.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `penelope`

Invocation pattern:

```bash
penelope --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show penelope-shell-handler
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
