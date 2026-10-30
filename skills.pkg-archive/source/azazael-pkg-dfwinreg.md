---
name: azazael-pkg-dfwinreg
description: Callable skill for Python package dfwinreg 20240316 — Digital Forensics Windows Registry (dfWinReg).
metadata:
  category: packages
  project: azazael
  priority: low
---

# dfwinreg 20240316

> Digital Forensics Windows Registry (dfWinReg).

## Identity

| Field | Value |
|-------|-------|
| Distribution | `dfwinreg` |
| Version | `20240316` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `dfwinreg`

Invocation pattern:

```python
import dfwinreg
print("dfwinreg loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import dfwinreg; print('dfwinreg OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
