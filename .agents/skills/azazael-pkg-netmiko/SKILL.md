---
name: azazael-pkg-netmiko
description: Callable skill for Python package netmiko 4.6.0 — Multi-vendor library to simplify legacy CLI connections to network devices
metadata:
  category: packages
  project: azazael
  priority: low
---

# netmiko 4.6.0

> Multi-vendor library to simplify legacy CLI connections to network devices

## Identity

| Field | Value |
|-------|-------|
| Distribution | `netmiko` |
| Version | `4.6.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `netmiko-bulk-encrypt`
- `netmiko-cfg`
- `netmiko-encrypt`
- `netmiko-grep`
- `netmiko-show`

Invocation pattern:

```bash
netmiko-bulk-encrypt --help
```

Alternates:

```bash
netmiko-cfg --help
netmiko-encrypt --help
netmiko-grep --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show netmiko
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
