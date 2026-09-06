---
name: azazael-bin-naabu
description: Callable skill for naabu — Fast port scanner (ProjectDiscovery)
metadata:
  category: recon
  project: azazael
  priority: medium
---

# naabu

> Fast port scanner (ProjectDiscovery)

## Identity

| Field | Value |
|-------|-------|
| Tool | `naabu` |
| Version | `Current naabu version 2.6.1 (latest)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/naabu (Kali)
```

## EXECUTE — canonical invocations

**Scan top ports:**

```bash
naabu -host example.com
```

**Full port range:**

```bash
naabu -host 10.0.0.1 -p -
```

**With nmap service detection:**

```bash
naabu -host example.com -sV
```

## Verify

```bash
naabu --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
