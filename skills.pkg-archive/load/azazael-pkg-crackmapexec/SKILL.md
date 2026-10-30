---
name: azazael-pkg-crackmapexec
description: Callable skill for Python package crackmapexec 5.4.0 — A swiss army knife for pentesting networks
metadata:
  category: packages
  project: azazael
  priority: low
---

# crackmapexec 5.4.0

> A swiss army knife for pentesting networks

## Identity

| Field | Value |
|-------|-------|
| Distribution | `crackmapexec` |
| Version | `5.4.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `cme`
- `cmedb`
- `crackmapexec`

Invocation pattern:

```bash
cme --help
```

Alternates:

```bash
cmedb --help
crackmapexec --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show crackmapexec
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
