---
name: azazael-bin-seclists
description: Callable skill for seclists — SecLists — massive collection of wordlists for security testing (Daniel Miessler)
metadata:
  category: data
  project: azazael
  priority: medium
---

# seclists

> SecLists — massive collection of wordlists for security testing (Daniel Miessler)

## Identity

| Field | Value |
|-------|-------|
| Tool | `seclists` |
| Version | `2026.1 (data package at /usr/share/seclists)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/share/seclists (Kali data package)
```

## EXECUTE — canonical invocations

**Find relevant wordlists:**

```bash
find /usr/share/seclists -name '*.txt' | head
```

**Use with ffuf:**

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u http://target/FUZZ
```

**Use with gobuster:**

```bash
gobuster dir -u http://target -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
```

## Verify

```bash
seclists --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
