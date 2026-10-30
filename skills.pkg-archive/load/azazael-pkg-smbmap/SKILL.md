---
name: azazael-pkg-smbmap
description: Callable skill for Python package smbmap 1.10.7 — SMBMap is a handy SMB enumeration tool 
metadata:
  category: packages
  project: azazael
  priority: low
---

# smbmap 1.10.7

> SMBMap is a handy SMB enumeration tool 

## Identity

| Field | Value |
|-------|-------|
| Distribution | `smbmap` |
| Version | `1.10.7` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `smbmap`

Invocation pattern:

```bash
smbmap --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `smbmap`

Invocation pattern:

```python
import smbmap
print("smbmap loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import smbmap; print('smbmap OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
