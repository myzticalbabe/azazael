---
name: azazael-bin-gobuster
description: Callable skill for gobuster — Directory/file and DNS subdomain brute-forcer
metadata:
  category: web
  project: azazael
  priority: medium
---

# gobuster

> Directory/file and DNS subdomain brute-forcer

## Identity

| Field | Value |
|-------|-------|
| Tool | `gobuster` |
| Version | `gobuster version 3.8.2` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/gobuster (Kali)
```

## EXECUTE — canonical invocations

**Directory brute-force:**

```bash
gobuster dir -u http://target -w /usr/share/wordlists/dirb/common.txt
```

**DNS subdomain brute-force:**

```bash
gobuster dns -d target.com -w subdomains.txt
```

**Vhost enumeration:**

```bash
gobuster vhost -u http://target -w vhosts.txt
```

## Verify

```bash
gobuster --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
