---
name: azazael-pkg-pure-eval
description: Callable skill for Python package pure_eval 0.2.3 — Safely evaluate AST nodes without side effects
metadata:
  category: packages
  project: azazael
  priority: low
---

# pure_eval 0.2.3

> Safely evaluate AST nodes without side effects

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pure_eval` |
| Version | `0.2.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `pure_eval`

Invocation pattern:

```python
import pure_eval
print("pure_eval loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pure_eval; print('pure_eval OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
