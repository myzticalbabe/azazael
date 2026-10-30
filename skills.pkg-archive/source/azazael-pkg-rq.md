---
name: azazael-pkg-rq
description: Callable skill for Python package rq 2.9.1 — RQ is a simple, lightweight, library for creating background jobs, and processing them.
metadata:
  category: packages
  project: azazael
  priority: low
---

# rq 2.9.1

> RQ is a simple, lightweight, library for creating background jobs, and processing them.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `rq` |
| Version | `2.9.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `rq`
- `rqinfo`
- `rqworker`

Invocation pattern:

```bash
rq --help
```

Alternates:

```bash
rqinfo --help
rqworker --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show rq
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
