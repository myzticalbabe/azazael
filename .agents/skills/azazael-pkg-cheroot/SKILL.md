---
name: azazael-pkg-cheroot
description: Callable skill for Python package cheroot 11.1.2+ds1 — Highly-optimized, pure-python HTTP server
metadata:
  category: packages
  project: azazael
  priority: low
---

# cheroot 11.1.2+ds1

> Highly-optimized, pure-python HTTP server

## Identity

| Field | Value |
|-------|-------|
| Distribution | `cheroot` |
| Version | `11.1.2+ds1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `cheroot`

Invocation pattern:

```bash
cheroot --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `cheroot`

Invocation pattern:

```python
import cheroot
print("cheroot loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import cheroot; print('cheroot OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
