---
name: azazael-pkg-h8mail
description: Callable skill for Python package h8mail 2.5.6 — Email OSINT and password breach hunting. Use h8mail to find passwords through different breach and reconnaissance services, or using your local data
metadata:
  category: packages
  project: azazael
  priority: low
---

# h8mail 2.5.6

> Email OSINT and password breach hunting. Use h8mail to find passwords through different breach and reconnaissance services, or using your local data

## Identity

| Field | Value |
|-------|-------|
| Distribution | `h8mail` |
| Version | `2.5.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `h8mail`

Invocation pattern:

```bash
h8mail --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `h8mail`

Invocation pattern:

```python
import h8mail
print("h8mail loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import h8mail; print('h8mail OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
