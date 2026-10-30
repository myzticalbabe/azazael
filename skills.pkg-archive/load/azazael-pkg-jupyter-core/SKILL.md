---
name: azazael-pkg-jupyter-core
description: Callable skill for Python package jupyter_core 5.9.1 — Jupyter core package. A base package on which Jupyter projects rely.
metadata:
  category: packages
  project: azazael
  priority: low
---

# jupyter_core 5.9.1

> Jupyter core package. A base package on which Jupyter projects rely.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `jupyter_core` |
| Version | `5.9.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `jupyter`
- `jupyter-migrate`
- `jupyter-troubleshoot`

Invocation pattern:

```bash
jupyter --help
```

Alternates:

```bash
jupyter-migrate --help
jupyter-troubleshoot --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show jupyter_core
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
