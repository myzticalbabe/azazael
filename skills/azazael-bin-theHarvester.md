---
name: azazael-bin-theHarvester
description: Callable skill for theHarvester — Email, subdomain and hostname enumeration
metadata:
  category: osint
  project: azazael
  priority: medium
---

# theHarvester

> Email, subdomain and hostname enumeration

## Identity

| Field | Value |
|-------|-------|
| Tool | `theHarvester` |
| Version | `v0.6.4 (source clone, /root/osint-tools/theHarvester)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/theHarvester (Kali)
```

## EXECUTE — canonical invocations

**Passive recon:**

```bash
theHarvester -d example.com -b all
```

**Baidu + Bing sources:**

```bash
theHarvester -d example.com -b baidu,bing
```

**DNS lookup:**

```bash
theHarvester -d example.com -b dns
```

## Verify

```bash
theHarvester --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
