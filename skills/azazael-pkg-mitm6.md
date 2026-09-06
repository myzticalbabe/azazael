---
name: azazael-pkg-mitm6
description: Callable skill for Python package mitm6 0.3.0 — Pwning IPv4 via IPv6
metadata:
  category: packages
  project: azazael
  priority: low
---

# mitm6 0.3.0

> Pwning IPv4 via IPv6

## Identity

| Field | Value |
|-------|-------|
| Distribution | `mitm6` |
| Version | `0.3.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `mitm6`

Invocation pattern:

```bash
mitm6 --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `mitm6`

Invocation pattern:

```python
import mitm6
print("mitm6 loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import mitm6; print('mitm6 OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
