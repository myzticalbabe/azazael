---
name: azazael-pkg-evdev
description: Callable skill for Python package evdev 1.9.3 — Bindings to the Linux input handling subsystem
metadata:
  category: packages
  project: azazael
  priority: low
---

# evdev 1.9.3

> Bindings to the Linux input handling subsystem

## Identity

| Field | Value |
|-------|-------|
| Distribution | `evdev` |
| Version | `1.9.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `evdev`

Invocation pattern:

```python
import evdev
print("evdev loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import evdev; print('evdev OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
