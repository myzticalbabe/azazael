---
name: azazael-pkg-commonmark
description: Callable skill for Python package commonmark 0.9.1 — Python parser for the CommonMark Markdown spec
metadata:
  category: packages
  project: azazael
  priority: low
---

# commonmark 0.9.1

> Python parser for the CommonMark Markdown spec

## Identity

| Field | Value |
|-------|-------|
| Distribution | `commonmark` |
| Version | `0.9.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `cmark`

Invocation pattern:

```bash
cmark --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `commonmark`

Invocation pattern:

```python
import commonmark
print("commonmark loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import commonmark; print('commonmark OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
