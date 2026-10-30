---
name: azazael-pkg-hashid
description: Callable skill for Python package hashID 3.1.4 — Software to identify the different types of hashes
metadata:
  category: packages
  project: azazael
  priority: low
---

# hashID 3.1.4

> Software to identify the different types of hashes

## Identity

| Field | Value |
|-------|-------|
| Distribution | `hashID` |
| Version | `3.1.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `hashid`

Invocation pattern:

```bash
hashid --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `hashID`

Invocation pattern:

```python
import hashID
print("hashID loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import hashID; print('hashID OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
