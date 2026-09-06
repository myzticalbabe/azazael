---
name: azazael-pkg-unicorn
description: Callable skill for Python package unicorn 0.0.0 — Unicorn CPU emulator engine
metadata:
  category: packages
  project: azazael
  priority: low
---

# unicorn 0.0.0

> Unicorn CPU emulator engine

## Identity

| Field | Value |
|-------|-------|
| Distribution | `unicorn` |
| Version | `0.0.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `unicorn`

Invocation pattern:

```python
import unicorn
print("unicorn loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import unicorn; print('unicorn OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
