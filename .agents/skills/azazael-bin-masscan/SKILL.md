---
name: azazael-bin-masscan
description: Callable skill for masscan — Internet-scale port scanner (scans entire internet in <5 min)
metadata:
  category: recon
  project: azazael
  priority: medium
---

# masscan

> Internet-scale port scanner (scans entire internet in <5 min)

## Identity

| Field | Value |
|-------|-------|
| Tool | `masscan` |
| Version | `Masscan version 1.3.2 ( https://github.com/robertdavidgraham/masscan )` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/masscan (Kali)
```

## EXECUTE — canonical invocations

**Scan top ports:**

```bash
masscan 192.168.1.0/24 --top-ports 100
```

**Full port range:**

```bash
masscan 10.0.0.0/8 -p0-65535 --rate 10000
```

**Output to file:**

```bash
masscan 192.168.1.1 --top-ports 1000 -oJ results.json
```

## Verify

```bash
masscan --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
