---
name: azazael-pkg-pacu
description: Callable skill for Python package pacu 1.6.0 — The AWS exploitation framework, designed for testing the security of Amazon Web Services environments.
metadata:
  category: packages
  project: azazael
  priority: low
---

# pacu 1.6.0

> The AWS exploitation framework, designed for testing the security of Amazon Web Services environments.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pacu` |
| Version | `1.6.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pacu`

Invocation pattern:

```bash
pacu --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show pacu
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
