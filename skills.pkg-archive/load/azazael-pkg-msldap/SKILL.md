---
name: azazael-pkg-msldap
description: Callable skill for Python package msldap 0.5.10 — Python library to play with MS LDAP
metadata:
  category: packages
  project: azazael
  priority: low
---

# msldap 0.5.10

> Python library to play with MS LDAP

## Identity

| Field | Value |
|-------|-------|
| Distribution | `msldap` |
| Version | `0.5.10` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `msldap`
- `msldap-bloodhound`

Invocation pattern:

```bash
msldap --help
```

Alternates:

```bash
msldap-bloodhound --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `msldap`

Invocation pattern:

```python
import msldap
print("msldap loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import msldap; print('msldap OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
