---
name: azazael-pkg-bluepy
description: Callable skill for Python package bluepy 1.3.0 — Python module for interfacing with BLE devices through Bluez
metadata:
  category: packages
  project: azazael
  priority: low
---

# bluepy 1.3.0

> Python module for interfacing with BLE devices through Bluez

## Identity

| Field | Value |
|-------|-------|
| Distribution | `bluepy` |
| Version | `1.3.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `blescan`
- `sensortag`
- `thingy52`

Invocation pattern:

```bash
blescan --help
```

Alternates:

```bash
sensortag --help
thingy52 --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `bluepy`

Invocation pattern:

```python
import bluepy
print("bluepy loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import bluepy; print('bluepy OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
