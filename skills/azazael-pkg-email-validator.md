---
name: azazael-pkg-email-validator
description: Callable skill for Python package email_validator 2.2.0 — A robust email address syntax and deliverability validation library.
metadata:
  category: packages
  project: azazael
  priority: low
---

# email_validator 2.2.0

> A robust email address syntax and deliverability validation library.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `email_validator` |
| Version | `2.2.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `email_validator`

Invocation pattern:

```bash
email_validator --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `email_validator`

Invocation pattern:

```python
import email_validator
print("email_validator loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import email_validator; print('email_validator OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
