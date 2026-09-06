---
name: azazael-pkg-adblockparser
description: Callable skill for Python package adblockparser 0.7 — Parser for Adblock Plus rules
metadata:
  category: packages
  project: azazael
  priority: low
---

# adblockparser 0.7

> Parser for Adblock Plus rules

## Identity

| Field | Value |
|-------|-------|
| Distribution | `adblockparser` |
| Version | `0.7` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `adblockparser`

Invocation pattern:

```python
import adblockparser
print("adblockparser loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import adblockparser; print('adblockparser OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
