---
name: azazael-pkg-sprayhound
description: Callable skill for Python package sprayhound 0.0.4 — Password spraying with BloodHound integration
metadata:
  category: packages
  project: azazael
  priority: low
---

# sprayhound 0.0.4

> Password spraying with BloodHound integration

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sprayhound` |
| Version | `0.0.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `sprayhound`

Invocation pattern:

```bash
sprayhound --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `sprayhound`

Invocation pattern:

```python
import sprayhound
print("sprayhound loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import sprayhound; print('sprayhound OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
