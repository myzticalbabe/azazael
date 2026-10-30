---
name: azazael-pkg-fqdn
description: Callable skill for Python package fqdn 1.5.1 — Validates fully-qualified domain names against RFC 1123, so that they are acceptable to modern bowsers
metadata:
  category: packages
  project: azazael
  priority: low
---

# fqdn 1.5.1

> Validates fully-qualified domain names against RFC 1123, so that they are acceptable to modern bowsers

## Identity

| Field | Value |
|-------|-------|
| Distribution | `fqdn` |
| Version | `1.5.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `fqdn`

Invocation pattern:

```python
import fqdn
print("fqdn loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import fqdn; print('fqdn OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
