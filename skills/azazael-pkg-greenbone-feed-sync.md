---
name: azazael-pkg-greenbone-feed-sync
description: Callable skill for Python package greenbone-feed-sync 25.1.3.dev1 — A tool for downloading the Greenbone Community Feed
metadata:
  category: packages
  project: azazael
  priority: low
---

# greenbone-feed-sync 25.1.3.dev1

> A tool for downloading the Greenbone Community Feed

## Identity

| Field | Value |
|-------|-------|
| Distribution | `greenbone-feed-sync` |
| Version | `25.1.3.dev1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `greenbone-certdata-sync`
- `greenbone-feed-sync`
- `greenbone-nvt-sync`
- `greenbone-scapdata-sync`

Invocation pattern:

```bash
greenbone-certdata-sync --help
```

Alternates:

```bash
greenbone-feed-sync --help
greenbone-nvt-sync --help
greenbone-scapdata-sync --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show greenbone-feed-sync
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
