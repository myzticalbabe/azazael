---
name: azazael-pkg-pyramid
description: Callable skill for Python package pyramid 2.0.2 — The Pyramid Web Framework, a Pylons project
metadata:
  category: packages
  project: azazael
  priority: low
---

# pyramid 2.0.2

> The Pyramid Web Framework, a Pylons project

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pyramid` |
| Version | `2.0.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pdistreport`
- `prequest`
- `proutes`
- `pserve`
- `pshell`
- `ptweens`
- `pviews`

Invocation pattern:

```bash
pdistreport --help
```

Alternates:

```bash
prequest --help
proutes --help
pserve --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pyramid`

Invocation pattern:

```python
import pyramid
print("pyramid loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pyramid; print('pyramid OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
