---
name: azazael-pkg-ipwhois
description: Callable skill for Python package ipwhois 1.3.0 — Retrieve and parse whois data for IPv4 and IPv6 addresses.
metadata:
  category: packages
  project: azazael
  priority: low
---

# ipwhois 1.3.0

> Retrieve and parse whois data for IPv4 and IPv6 addresses.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `ipwhois` |
| Version | `1.3.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `ipwhois_cli`
- `ipwhois_utils_cli`

Invocation pattern:

```bash
ipwhois_cli --help
```

Alternates:

```bash
ipwhois_utils_cli --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `ipwhois`

Invocation pattern:

```python
import ipwhois
print("ipwhois loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import ipwhois; print('ipwhois OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
