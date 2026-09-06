---
name: azazael-pkg-invoke
description: Callable skill for Python package invoke 2.2.1 — Pythonic task execution
metadata:
  category: packages
  project: azazael
  priority: low
---

# invoke 2.2.1

> Pythonic task execution

## Identity

| Field | Value |
|-------|-------|
| Distribution | `invoke` |
| Version | `2.2.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `inv`
- `invoke`

Invocation pattern:

```bash
inv --help
```

Alternates:

```bash
invoke --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `invoke`

Invocation pattern:

```python
import invoke
print("invoke loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import invoke; print('invoke OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
