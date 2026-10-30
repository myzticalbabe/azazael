---
name: azazael-pkg-pyshark
description: Callable skill for Python package pyshark 0.6 — Python wrapper for tshark, allowing python packet parsing using wireshark dissectors
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyshark 0.6

> Python wrapper for tshark, allowing python packet parsing using wireshark dissectors

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyshark` |
| Version | `0.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `pyshark`

Invocation pattern:

```python
import pyshark
print("pyshark loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pyshark; print('pyshark OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
