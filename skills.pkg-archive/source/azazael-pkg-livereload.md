---
name: azazael-pkg-livereload
description: Callable skill for Python package livereload 2.7.1 — Python LiveReload is an awesome tool for web developers
metadata:
  category: packages
  project: azazael
  priority: low
---

# livereload 2.7.1

> Python LiveReload is an awesome tool for web developers

## Identity

| Field | Value |
|-------|-------|
| Distribution | `livereload` |
| Version | `2.7.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `livereload`

Invocation pattern:

```bash
livereload --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `livereload`

Invocation pattern:

```python
import livereload
print("livereload loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import livereload; print('livereload OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
