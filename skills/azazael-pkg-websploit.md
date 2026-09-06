---
name: azazael-pkg-websploit
description: Callable skill for Python package websploit 4.0.4 — Websploit is a high level MITM framework
metadata:
  category: packages
  project: azazael
  priority: low
---

# websploit 4.0.4

> Websploit is a high level MITM framework

## Identity

| Field | Value |
|-------|-------|
| Distribution | `websploit` |
| Version | `4.0.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `websploit`

Invocation pattern:

```bash
websploit --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `websploit`

Invocation pattern:

```python
import websploit
print("websploit loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import websploit; print('websploit OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
