---
name: azazael-bin-spiderfoot
description: Callable skill for spiderfoot — Automated OSINT correlation across 200+ sources
metadata:
  category: osint
  project: azazael
  priority: medium
---

# spiderfoot

> Automated OSINT correlation across 200+ sources

## Identity

| Field | Value |
|-------|-------|
| Tool | `spiderfoot` |
| Version | `4.0.0` |
| Status | INSTALLED |

## Install

```bash
Kali package at /usr/share/spiderfoot (shebang fixed to python3.13, Aug 23 2026)
```

## EXECUTE — canonical invocations

**Run web UI:**

```bash
python3 sf.py -l 127.0.0.1:5001
```

**CLI scan:**

```bash
python3 sf.py -m all -s example.com
```

**List modules:**

```bash
python3 sf.py -M
```

## Verify

```bash
spiderfoot --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
