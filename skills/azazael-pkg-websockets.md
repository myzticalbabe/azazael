---
name: azazael-pkg-websockets
description: Callable skill for Python package websockets 16.0 — An implementation of the WebSocket Protocol (RFC 6455 & 7692)
metadata:
  category: packages
  project: azazael
  priority: low
---

# websockets 16.0

> An implementation of the WebSocket Protocol (RFC 6455 & 7692)

## Identity

| Field | Value |
|-------|-------|
| Distribution | `websockets` |
| Version | `16.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `websockets`

Invocation pattern:

```bash
websockets --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `websockets`

Invocation pattern:

```python
import websockets
print("websockets loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import websockets; print('websockets OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
