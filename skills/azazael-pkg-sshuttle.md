---
name: azazael-pkg-sshuttle
description: Callable skill for Python package sshuttle 1.3.2 — Transparent proxy server that works as a poor man's VPN. Forwards over ssh. Doesn't require admin. Works with Linux and MacOS. Supports DNS tunneling.
metadata:
  category: packages
  project: azazael
  priority: low
---

# sshuttle 1.3.2

> Transparent proxy server that works as a poor man's VPN. Forwards over ssh. Doesn't require admin. Works with Linux and MacOS. Supports DNS tunneling.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sshuttle` |
| Version | `1.3.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `sshuttle`

Invocation pattern:

```bash
sshuttle --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show sshuttle
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
