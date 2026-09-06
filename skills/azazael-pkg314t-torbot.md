---
name: azazael-pkg314t-torbot
description: Callable skill for Python package torbot 4.3.0 — TorBot is an OSINT tool for the dark web.
metadata:
  category: packages
  project: azazael
  priority: low
---

# torbot 4.3.0

> TorBot is an OSINT tool for the dark web.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `torbot` |
| Version | `4.3.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `torbot`

Invocation pattern:

```bash
torbot --help
```

## Verify

```bash
/usr/local/bin/python3.14t -m pip show torbot
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
