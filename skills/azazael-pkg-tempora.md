---
name: azazael-pkg-tempora
description: Callable skill for Python package tempora 5.7.0 — Objects and routines pertaining to date and time (tempora)
metadata:
  category: packages
  project: azazael
  priority: low
---

# tempora 5.7.0

> Objects and routines pertaining to date and time (tempora)

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tempora` |
| Version | `5.7.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `calc-prorate`

Invocation pattern:

```bash
calc-prorate --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `tempora`

Invocation pattern:

```python
import tempora
print("tempora loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tempora; print('tempora OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
