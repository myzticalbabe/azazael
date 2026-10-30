---
name: azazael-pkg-publicsuffixlist
description: Callable skill for Python package publicsuffixlist 0.9.3 — publicsuffixlist implement
metadata:
  category: packages
  project: azazael
  priority: low
---

# publicsuffixlist 0.9.3

> publicsuffixlist implement

## Identity

| Field | Value |
|-------|-------|
| Distribution | `publicsuffixlist` |
| Version | `0.9.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `publicsuffixlist-download`

Invocation pattern:

```bash
publicsuffixlist-download --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `publicsuffixlist`

Invocation pattern:

```python
import publicsuffixlist
print("publicsuffixlist loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import publicsuffixlist; print('publicsuffixlist OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
