---
name: azazael-pkg-wordcloud
description: Callable skill for Python package wordcloud 1.9.4+dfsg — A little word cloud generator
metadata:
  category: packages
  project: azazael
  priority: low
---

# wordcloud 1.9.4+dfsg

> A little word cloud generator

## Identity

| Field | Value |
|-------|-------|
| Distribution | `wordcloud` |
| Version | `1.9.4+dfsg` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `wordcloud_cli`

Invocation pattern:

```bash
wordcloud_cli --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `wordcloud`

Invocation pattern:

```python
import wordcloud
print("wordcloud loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import wordcloud; print('wordcloud OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
