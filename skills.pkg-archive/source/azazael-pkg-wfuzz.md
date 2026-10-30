---
name: azazael-pkg-wfuzz
description: Callable skill for Python package wfuzz 3.1.0 — Wfuzz - The web fuzzer
metadata:
  category: packages
  project: azazael
  priority: low
---

# wfuzz 3.1.0

> Wfuzz - The web fuzzer

## Identity

| Field | Value |
|-------|-------|
| Distribution | `wfuzz` |
| Version | `3.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `wfencode`
- `wfpayload`
- `wfuzz`

Invocation pattern:

```bash
wfencode --help
```

Alternates:

```bash
wfpayload --help
wfuzz --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `wfuzz`

Invocation pattern:

```python
import wfuzz
print("wfuzz loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import wfuzz; print('wfuzz OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
