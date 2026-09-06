---
name: azazael-pkg-argcomplete
description: Callable skill for Python package argcomplete 3.6.3 — Bash tab completion for argparse
metadata:
  category: packages
  project: azazael
  priority: low
---

# argcomplete 3.6.3

> Bash tab completion for argparse

## Identity

| Field | Value |
|-------|-------|
| Distribution | `argcomplete` |
| Version | `3.6.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `activate-global-python-argcomplete`
- `python-argcomplete-check-easy-install-script`
- `register-python-argcomplete`

Invocation pattern:

```bash
activate-global-python-argcomplete --help
```

Alternates:

```bash
python-argcomplete-check-easy-install-script --help
register-python-argcomplete --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show argcomplete
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
