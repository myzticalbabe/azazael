---
name: azazael-pkg-theharvester
description: Callable skill for Python package theHarvester 4.10.1 — theHarvester is a very simple, yet effective tool designed to be used in the early stages of a penetration test
metadata:
  category: packages
  project: azazael
  priority: low
---

# theHarvester 4.10.1

> theHarvester is a very simple, yet effective tool designed to be used in the early stages of a penetration test

## Identity

| Field | Value |
|-------|-------|
| Distribution | `theHarvester` |
| Version | `4.10.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `restfulHarvest`
- `theHarvester`

Invocation pattern:

```bash
restfulHarvest --help
```

Alternates:

```bash
theHarvester --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show theHarvester
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
