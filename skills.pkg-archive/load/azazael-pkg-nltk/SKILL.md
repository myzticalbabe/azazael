---
name: azazael-pkg-nltk
description: Callable skill for Python package nltk 3.9.3 — Natural Language Toolkit
metadata:
  category: packages
  project: azazael
  priority: low
---

# nltk 3.9.3

> Natural Language Toolkit

## Identity

| Field | Value |
|-------|-------|
| Distribution | `nltk` |
| Version | `3.9.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `nltk`

Invocation pattern:

```bash
nltk --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `nltk`

Invocation pattern:

```python
import nltk
print("nltk loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import nltk; print('nltk OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
