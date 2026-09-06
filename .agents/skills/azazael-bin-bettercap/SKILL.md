---
name: azazael-bin-bettercap
description: Callable skill for bettercap — Swiss-army knife for MITM attacks, network recon, and monitoring
metadata:
  category: intercept
  project: azazael
  priority: medium
---

# bettercap

> Swiss-army knife for MITM attacks, network recon, and monitoring

## Identity

| Field | Value |
|-------|-------|
| Tool | `bettercap` |
| Version | `bettercap v2.41.5 (built for linux amd64 with go1.24.9)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/bettercap (Kali)
```

## EXECUTE — canonical invocations

**Start interactive session:**

```bash
bettercap -iface eth0
```

**Run net.recon module:**

```bash
bettercap -iface eth0 -eval 'net.recon on; net.show'
```

**Start HTTP server UI:**

```bash
bettercap -httpd
```

## Verify

```bash
bettercap --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
