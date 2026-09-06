---
name: azazael-pkg-aioconsole
description: Callable skill for Python package aioconsole 0.8.2 — Asynchronous console and interfaces for asyncio
metadata:
  category: packages
  project: azazael
  priority: low
---

# aioconsole 0.8.2

> Asynchronous console and interfaces for asyncio

## Identity

| Field | Value |
|-------|-------|
| Distribution | `aioconsole` |
| Version | `0.8.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `apython`

Invocation pattern:

```bash
apython --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `aioconsole`

Invocation pattern:

```python
import aioconsole
print("aioconsole loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import aioconsole; print('aioconsole OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
