---
name: azazael-pkg-ropgadget
description: Callable skill for Python package ROPGadget 7.7 — This tool lets you search your gadgets on your binaries to facilitate your ROP exploitation.
metadata:
  category: packages
  project: azazael
  priority: low
---

# ROPGadget 7.7

> This tool lets you search your gadgets on your binaries to facilitate your ROP exploitation.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `ROPGadget` |
| Version | `7.7` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `ROPGadget`

Invocation pattern:

```python
import ROPGadget
print("ROPGadget loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import ROPGadget; print('ROPGadget OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
