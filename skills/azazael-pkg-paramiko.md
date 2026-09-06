---
name: azazael-pkg-paramiko
description: Callable skill for Python package paramiko 4.0.0 — SSH2 protocol library
metadata:
  category: packages
  project: azazael
  priority: low
---

# paramiko 4.0.0

> SSH2 protocol library

## Identity

| Field | Value |
|-------|-------|
| Distribution | `paramiko` |
| Version | `4.0.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `paramiko`

Invocation pattern:

```python
import paramiko
print("paramiko loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import paramiko; print('paramiko OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
