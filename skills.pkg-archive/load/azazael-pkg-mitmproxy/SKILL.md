---
name: azazael-pkg-mitmproxy
description: Callable skill for Python package mitmproxy 12.2.3 — An interactive, SSL/TLS-capable intercepting proxy for HTTP/1, HTTP/2, and WebSockets.
metadata:
  category: packages
  project: azazael
  priority: low
---

# mitmproxy 12.2.3

> An interactive, SSL/TLS-capable intercepting proxy for HTTP/1, HTTP/2, and WebSockets.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `mitmproxy` |
| Version | `12.2.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `mitmdump`
- `mitmproxy`
- `mitmweb`

Invocation pattern:

```bash
mitmdump --help
```

Alternates:

```bash
mitmproxy --help
mitmweb --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `mitmproxy`

Invocation pattern:

```python
import mitmproxy
print("mitmproxy loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import mitmproxy; print('mitmproxy OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
