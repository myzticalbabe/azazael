---
name: azazael-pkg-wsgidav
description: Callable skill for Python package WsgiDAV 4.3.3 — Generic and extendable WebDAV server based on WSGI
metadata:
  category: packages
  project: azazael
  priority: low
---

# WsgiDAV 4.3.3

> Generic and extendable WebDAV server based on WSGI

## Identity

| Field | Value |
|-------|-------|
| Distribution | `WsgiDAV` |
| Version | `4.3.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `wsgidav`

Invocation pattern:

```bash
wsgidav --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `WsgiDAV`

Invocation pattern:

```python
import WsgiDAV
print("WsgiDAV loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import WsgiDAV; print('WsgiDAV OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
