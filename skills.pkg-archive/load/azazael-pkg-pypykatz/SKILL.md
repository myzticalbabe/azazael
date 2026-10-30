---
name: azazael-pkg-pypykatz
description: Callable skill for Python package pypykatz 0.6.13 — Python implementation of Mimikatz
metadata:
  category: packages
  project: azazael
  priority: low
---

# pypykatz 0.6.13

> Python implementation of Mimikatz

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pypykatz` |
| Version | `0.6.13` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pypykatz`

Invocation pattern:

```bash
pypykatz --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pypykatz`

Invocation pattern:

```python
import pypykatz
print("pypykatz loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pypykatz; print('pypykatz OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
