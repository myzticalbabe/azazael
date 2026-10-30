---
name: azazael-pkg-wifiphisher
description: Callable skill for Python package wifiphisher 1.4 — Automated phishing attacks against Wi-Fi networks
metadata:
  category: packages
  project: azazael
  priority: low
---

# wifiphisher 1.4

> Automated phishing attacks against Wi-Fi networks

## Identity

| Field | Value |
|-------|-------|
| Distribution | `wifiphisher` |
| Version | `1.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `wifiphisher`

Invocation pattern:

```bash
wifiphisher --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `wifiphisher`

Invocation pattern:

```python
import wifiphisher
print("wifiphisher loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import wifiphisher; print('wifiphisher OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
