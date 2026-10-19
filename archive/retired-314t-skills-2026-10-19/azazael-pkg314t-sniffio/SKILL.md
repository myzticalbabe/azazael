---
name: azazael-pkg314t-sniffio
description: Callable skill for Python package sniffio 1.3.1 — Sniff out which async library your code is running under
metadata:
  category: packages
  project: azazael
  priority: low
---

# sniffio 1.3.1

> Sniff out which async library your code is running under

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sniffio` |
| Version | `1.3.1` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — Python API

Importable top-level module(s):

- `sniffio`

Invocation pattern:

```python
import sniffio
print("sniffio loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import sniffio; print('sniffio OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
