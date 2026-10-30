---
name: azazael-pkg-distorm3
description: Callable skill for Python package distorm3 3.5.2 — The goal of diStorm3 is to decode x86/AMD64 binary streams and return a structure that describes each instruction.
metadata:
  category: packages
  project: azazael
  priority: low
---

# distorm3 3.5.2

> The goal of diStorm3 is to decode x86/AMD64 binary streams and return a structure that describes each instruction.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `distorm3` |
| Version | `3.5.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `distorm3`

Invocation pattern:

```python
import distorm3
print("distorm3 loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import distorm3; print('distorm3 OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
