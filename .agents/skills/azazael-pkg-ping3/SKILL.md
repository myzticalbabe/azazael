---
name: azazael-pkg-ping3
description: Callable skill for Python package ping3 4.0.4 — A pure python3 version of ICMP ping implementation using raw socket.
metadata:
  category: packages
  project: azazael
  priority: low
---

# ping3 4.0.4

> A pure python3 version of ICMP ping implementation using raw socket.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `ping3` |
| Version | `4.0.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `ping3`

Invocation pattern:

```bash
ping3 --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `ping3`

Invocation pattern:

```python
import ping3
print("ping3 loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import ping3; print('ping3 OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
