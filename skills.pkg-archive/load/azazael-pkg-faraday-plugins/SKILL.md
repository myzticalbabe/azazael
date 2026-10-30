---
name: azazael-pkg-faraday-plugins
description: Callable skill for Python package faraday_plugins 1.27.2 — Faraday plugins package
metadata:
  category: packages
  project: azazael
  priority: low
---

# faraday_plugins 1.27.2

> Faraday plugins package

## Identity

| Field | Value |
|-------|-------|
| Distribution | `faraday_plugins` |
| Version | `1.27.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `faraday-plugins`

Invocation pattern:

```bash
faraday-plugins --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `faraday_plugins`

Invocation pattern:

```python
import faraday_plugins
print("faraday_plugins loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import faraday_plugins; print('faraday_plugins OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
