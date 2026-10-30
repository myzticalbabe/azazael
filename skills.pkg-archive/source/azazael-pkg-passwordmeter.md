---
name: azazael-pkg-passwordmeter
description: Callable skill for Python package passwordmeter 0.1.8 — A password strength measuring library.
metadata:
  category: packages
  project: azazael
  priority: low
---

# passwordmeter 0.1.8

> A password strength measuring library.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `passwordmeter` |
| Version | `0.1.8` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pwm`

Invocation pattern:

```bash
pwm --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `passwordmeter`

Invocation pattern:

```python
import passwordmeter
print("passwordmeter loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import passwordmeter; print('passwordmeter OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
