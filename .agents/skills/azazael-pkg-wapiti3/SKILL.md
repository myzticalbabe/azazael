---
name: azazael-pkg-wapiti3
description: Callable skill for Python package wapiti3 3.2.10 — A web application vulnerability scanner
metadata:
  category: packages
  project: azazael
  priority: low
---

# wapiti3 3.2.10

> A web application vulnerability scanner

## Identity

| Field | Value |
|-------|-------|
| Distribution | `wapiti3` |
| Version | `3.2.10` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `wapiti`
- `wapiti-getcookie`
- `wapiti-install-headless-browser`

Invocation pattern:

```bash
wapiti --help
```

Alternates:

```bash
wapiti-getcookie --help
wapiti-install-headless-browser --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show wapiti3
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
