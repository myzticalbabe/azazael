---
name: azazael-pkg-evil-winrm-py
description: Callable skill for Python package evil-winrm-py 1.6.0 — Execute commands interactively on remote Windows machines using the WinRM protocol
metadata:
  category: packages
  project: azazael
  priority: low
---

# evil-winrm-py 1.6.0

> Execute commands interactively on remote Windows machines using the WinRM protocol

## Identity

| Field | Value |
|-------|-------|
| Distribution | `evil-winrm-py` |
| Version | `1.6.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `evil-winrm-py`
- `ewp`

Invocation pattern:

```bash
evil-winrm-py --help
```

Alternates:

```bash
ewp --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show evil-winrm-py
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
