---
name: azazael-pkg-recommonmark
description: Callable skill for Python package recommonmark 0.7.1 — A docutils-compatibility bridge to CommonMark, enabling you to write CommonMark inside of Docutils & Sphinx projects.
metadata:
  category: packages
  project: azazael
  priority: low
---

# recommonmark 0.7.1

> A docutils-compatibility bridge to CommonMark, enabling you to write CommonMark inside of Docutils & Sphinx projects.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `recommonmark` |
| Version | `0.7.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `cm2html`
- `cm2latex`
- `cm2man`
- `cm2pseudoxml`
- `cm2xetex`
- `cm2xml`

Invocation pattern:

```bash
cm2html --help
```

Alternates:

```bash
cm2latex --help
cm2man --help
cm2pseudoxml --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `recommonmark`

Invocation pattern:

```python
import recommonmark
print("recommonmark loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import recommonmark; print('recommonmark OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
