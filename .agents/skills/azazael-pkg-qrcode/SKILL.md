---
name: azazael-pkg-qrcode
description: Callable skill for Python package qrcode 8.2 — QR Code image generator
metadata:
  category: packages
  project: azazael
  priority: low
---

# qrcode 8.2

> QR Code image generator

## Identity

| Field | Value |
|-------|-------|
| Distribution | `qrcode` |
| Version | `8.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `qr`

Invocation pattern:

```bash
qr --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show qrcode
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
