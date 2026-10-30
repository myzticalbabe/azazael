---
name: azazael-pkg-instaloader
description: Callable skill for Python package instaloader 4.15.1 — Download pictures (or videos) along with their captions and other metadata from Instagram.
metadata:
  category: packages
  project: azazael
  priority: low
---

# instaloader 4.15.1

> Download pictures (or videos) along with their captions and other metadata from Instagram.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `instaloader` |
| Version | `4.15.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `instaloader`

Invocation pattern:

```bash
instaloader --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `instaloader`

Invocation pattern:

```python
import instaloader
print("instaloader loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import instaloader; print('instaloader OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
