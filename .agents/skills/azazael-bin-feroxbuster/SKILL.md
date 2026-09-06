---
name: azazael-bin-feroxbuster
description: Callable skill for feroxbuster — Fast, simple content discovery tool
metadata:
  category: web
  project: azazael
  priority: medium
---

# feroxbuster

> Fast, simple content discovery tool

## Identity

| Field | Value |
|-------|-------|
| Tool | `feroxbuster` |
| Version | `feroxbuster 2.13.1` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/feroxbuster (Kali)
```

## EXECUTE — canonical invocations

**Content discovery:**

```bash
feroxbuster -u http://target
```

**With wordlist + threads:**

```bash
feroxbuster -u http://target -w wordlist.txt -t 50
```

**Recursive scan:**

```bash
feroxbuster -u http://target -r
```

## Verify

```bash
feroxbuster --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
