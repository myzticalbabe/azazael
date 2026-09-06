---
name: azazael-bin-amass
description: Callable skill for amass — OWASP attack-surface enumeration and mapping
metadata:
  category: recon
  project: azazael
  priority: medium
---

# amass

> OWASP attack-surface enumeration and mapping

## Identity

| Field | Value |
|-------|-------|
| Tool | `amass` |
| Version | `installed (version unknown)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/amass (Kali)
```

## EXECUTE — canonical invocations

**Passive subdomain enum:**

```bash
amass enum -passive -d example.com
```

**Full enum with output:**

```bash
amass enum -d example.com -o results.txt
```

**Intelligence gathering:**

```bash
amass intel -whois -d example.com
```

## Verify

```bash
amass --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
