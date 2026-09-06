---
name: azazael-pkg-stem
description: Callable skill for Python package stem 1.8.2 — Stem is a Python controller library that allows applications to interact with Tor (https://www.torproject.org/).
metadata:
  category: packages
  project: azazael
  priority: low
---

# stem 1.8.2

> Stem is a Python controller library that allows applications to interact with Tor (https://www.torproject.org/).

## Identity

| Field | Value |
|-------|-------|
| Distribution | `stem` |
| Version | `1.8.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `stem`

Invocation pattern:

```python
import stem
print("stem loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import stem; print('stem OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
