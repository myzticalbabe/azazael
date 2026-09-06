---
name: azazael-pkg-dnsgen
description: Callable skill for Python package dnsgen 1.0.4 — Generates DNS possibilities from existing domain names.
metadata:
  category: packages
  project: azazael
  priority: low
---

# dnsgen 1.0.4

> Generates DNS possibilities from existing domain names.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `dnsgen` |
| Version | `1.0.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `dnsgen`

Invocation pattern:

```bash
dnsgen --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `dnsgen`

Invocation pattern:

```python
import dnsgen
print("dnsgen loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import dnsgen; print('dnsgen OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
