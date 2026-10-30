---
name: azazael-pkg-stone
description: Callable skill for Python package stone 3.3.9 — Stone is an interface description language (IDL) for APIs.
metadata:
  category: packages
  project: azazael
  priority: low
---

# stone 3.3.9

> Stone is an interface description language (IDL) for APIs.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `stone` |
| Version | `3.3.9` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `stone`

Invocation pattern:

```bash
stone --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `stone`

Invocation pattern:

```python
import stone
print("stone loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import stone; print('stone OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
