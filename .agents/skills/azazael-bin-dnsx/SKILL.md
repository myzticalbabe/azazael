---
name: azazael-bin-dnsx
description: Callable skill for dnsx — Fast and multi-purpose DNS toolkit (ProjectDiscovery)
metadata:
  category: recon
  project: azazael
  priority: medium
---

# dnsx

> Fast and multi-purpose DNS toolkit (ProjectDiscovery)

## Identity

| Field | Value |
|-------|-------|
| Tool | `dnsx` |
| Version | `Current dnsx version 1.2.3 (outdated)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/dnsx (Kali)
```

## EXECUTE — canonical invocations

**Resolve subdomains:**

```bash
dnsx -l subs.txt -a -resp
```

**A record lookup:**

```bash
dnsx -u example.com -a
```

**CNAME enumeration:**

```bash
dnsx -l subs.txt -cname
```

## Verify

```bash
dnsx --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
