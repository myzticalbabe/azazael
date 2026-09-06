---
name: azazael-pkg-myst-parser
description: Callable skill for Python package myst-parser 5.1.0 — An extended [CommonMark](https://spec.commonmark.org/) compliant parser,
metadata:
  category: packages
  project: azazael
  priority: low
---

# myst-parser 5.1.0

> An extended [CommonMark](https://spec.commonmark.org/) compliant parser,

## Identity

| Field | Value |
|-------|-------|
| Distribution | `myst-parser` |
| Version | `5.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `myst-anchors`
- `myst-docutils-demo`
- `myst-docutils-html`
- `myst-docutils-html5`
- `myst-docutils-latex`
- `myst-docutils-pseudoxml`
- `myst-docutils-xml`
- `myst-inv`

Invocation pattern:

```bash
myst-anchors --help
```

Alternates:

```bash
myst-docutils-demo --help
myst-docutils-html --help
myst-docutils-html5 --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show myst-parser
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
