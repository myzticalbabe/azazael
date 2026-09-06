---
name: azazael-pkg-netexec
description: Callable skill for Python package netexec 1.5.1 — The Network Execution tool
metadata:
  category: packages
  project: azazael
  priority: low
---

# netexec 1.5.1

> The Network Execution tool

## Identity

| Field | Value |
|-------|-------|
| Distribution | `netexec` |
| Version | `1.5.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `netexec`
- `nxc`
- `nxcdb`

Invocation pattern:

```bash
netexec --help
```

Alternates:

```bash
nxc --help
nxcdb --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show netexec
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
