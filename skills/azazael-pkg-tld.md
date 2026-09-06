---
name: azazael-pkg-tld
description: Callable skill for Python package tld 0.13 — Extract the top-level domain (TLD) from the URL given.
metadata:
  category: packages
  project: azazael
  priority: low
---

# tld 0.13

> Extract the top-level domain (TLD) from the URL given.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tld` |
| Version | `0.13` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `tld`

Invocation pattern:

```python
import tld
print("tld loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tld; print('tld OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
