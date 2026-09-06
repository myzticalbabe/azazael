---
name: azazael-pkg-dnstwist
description: Callable skill for Python package dnstwist 20250130 — Domain name permutation engine for detecting homograph phishing attacks, typo squatting, and brand impersonation
metadata:
  category: packages
  project: azazael
  priority: low
---

# dnstwist 20250130

> Domain name permutation engine for detecting homograph phishing attacks, typo squatting, and brand impersonation

## Identity

| Field | Value |
|-------|-------|
| Distribution | `dnstwist` |
| Version | `20250130` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `dnstwist`

Invocation pattern:

```bash
dnstwist --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `dnstwist`

Invocation pattern:

```python
import dnstwist
print("dnstwist loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import dnstwist; print('dnstwist OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
