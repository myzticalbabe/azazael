---
name: azazael-bin-subfinder
description: Callable skill for subfinder — Passive subdomain discovery (ProjectDiscovery)
metadata:
  category: recon
  project: azazael
  priority: medium
---

# subfinder

> Passive subdomain discovery (ProjectDiscovery)

## Identity

| Field | Value |
|-------|-------|
| Tool | `subfinder` |
| Version | `Current Version: v2.14.0` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/subfinder (Kali)
```

## EXECUTE — canonical invocations

**Enumerate subdomains:**

```bash
subfinder -d example.com
```

**With sources and output:**

```bash
subfinder -d example.com -all -o subs.txt
```

**Passive only:**

```bash
subfinder -d example.com -passive
```

## Verify

```bash
subfinder --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
