---
name: azazael-bin-maigret
description: Callable skill for maigret — Username OSINT across 3,000+ sites
metadata:
  category: osint
  project: azazael
  priority: medium
---

# maigret

> Username OSINT across 3,000+ sites

## Identity

| Field | Value |
|-------|-------|
| Tool | `maigret` |
| Version | `0.6.4` |
| Status | INSTALLED |

## Install

```bash
pip install maigret (installed, 0.6.4)
```

## EXECUTE — canonical invocations

**Search username:**

```bash
maigret username
```

**With tags + output:**

```bash
maigret username -a --folderout results/
```

**Check specific site:**

```bash
maigret username --site github
```

## Verify

```bash
maigret --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
