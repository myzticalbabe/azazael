---
name: azazael-pkg-bloodhound
description: Callable skill for Python package bloodhound 1.9.0 — Python based ingestor for BloodHound
metadata:
  category: packages
  project: azazael
  priority: low
---

# bloodhound 1.9.0

> Python based ingestor for BloodHound

## Identity

| Field | Value |
|-------|-------|
| Distribution | `bloodhound` |
| Version | `1.9.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `bloodhound-python`

Invocation pattern:

```bash
bloodhound-python --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `bloodhound`

Invocation pattern:

```python
import bloodhound
print("bloodhound loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import bloodhound; print('bloodhound OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
