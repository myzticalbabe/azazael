---
name: azazael-pkg-httpie
description: Callable skill for Python package httpie 3.2.4 — HTTPie: modern, user-friendly command-line HTTP client for the API era.
metadata:
  category: packages
  project: azazael
  priority: low
---

# httpie 3.2.4

> HTTPie: modern, user-friendly command-line HTTP client for the API era.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `httpie` |
| Version | `3.2.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `http`
- `httpie`
- `https`

Invocation pattern:

```bash
http --help
```

Alternates:

```bash
httpie --help
https --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `httpie`

Invocation pattern:

```python
import httpie
print("httpie loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import httpie; print('httpie OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
