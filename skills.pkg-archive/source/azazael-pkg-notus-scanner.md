---
name: azazael-pkg-notus-scanner
description: Callable skill for Python package notus-scanner 22.7.2 — A vulnerability scanner for creating results from local security checks (LSCs) 
metadata:
  category: packages
  project: azazael
  priority: low
---

# notus-scanner 22.7.2

> A vulnerability scanner for creating results from local security checks (LSCs) 

## Identity

| Field | Value |
|-------|-------|
| Distribution | `notus-scanner` |
| Version | `22.7.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `notus-scan-start`
- `notus-scanner`
- `notus-subscriber`

Invocation pattern:

```bash
notus-scan-start --help
```

Alternates:

```bash
notus-scanner --help
notus-subscriber --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show notus-scanner
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
