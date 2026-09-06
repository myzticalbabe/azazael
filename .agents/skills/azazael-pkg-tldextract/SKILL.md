---
name: azazael-pkg-tldextract
description: Callable skill for Python package tldextract 5.3.1 — Accurately separates a URL's subdomain, domain, and public suffix, using the Public Suffix List (PSL). By default, this includes the public ICANN TLDs and their
metadata:
  category: packages
  project: azazael
  priority: low
---

# tldextract 5.3.1

> Accurately separates a URL's subdomain, domain, and public suffix, using the Public Suffix List (PSL). By default, this includes the public ICANN TLDs and their

## Identity

| Field | Value |
|-------|-------|
| Distribution | `tldextract` |
| Version | `5.3.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `tldextract`

Invocation pattern:

```bash
tldextract --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `tldextract`

Invocation pattern:

```python
import tldextract
print("tldextract loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import tldextract; print('tldextract OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
