---
name: azazael-pkg-netaddr
description: Callable skill for Python package netaddr 1.3.0 — A network address manipulation library for Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# netaddr 1.3.0

> A network address manipulation library for Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `netaddr` |
| Version | `1.3.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `netaddr`

Invocation pattern:

```bash
netaddr --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `netaddr`

Invocation pattern:

```python
import netaddr
print("netaddr loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import netaddr; print('netaddr OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
