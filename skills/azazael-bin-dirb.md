---
name: azazael-bin-dirb
description: Callable skill for dirb — Web content scanner / directory brute-forcer
metadata:
  category: web
  project: azazael
  priority: medium
---

# dirb

> Web content scanner / directory brute-forcer

## Identity

| Field | Value |
|-------|-------|
| Tool | `dirb` |
| Version | `DIRB v2.22` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/dirb (Kali)
```

## EXECUTE — canonical invocations

**Scan with default wordlist:**

```bash
dirb http://target.com
```

**Custom wordlist:**

```bash
dirb http://target.com /usr/share/wordlists/dirb/big.txt
```

**Recursive with extension:**

```bash
dirb http://target.com -r -X .php
```

## Verify

```bash
dirb --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
