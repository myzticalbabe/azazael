---
name: azazael-bin-hashcat
description: Callable skill for hashcat — Advanced password recovery / GPU hash cracking
metadata:
  category: cracking
  project: azazael
  priority: medium
---

# hashcat

> Advanced password recovery / GPU hash cracking

## Identity

| Field | Value |
|-------|-------|
| Tool | `hashcat` |
| Version | `v7.1.2` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/hashcat (Kali)
```

## EXECUTE — canonical invocations

**Crack MD5 with rockyou:**

```bash
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt
```

**List hash modes:**

```bash
hashcat --example-hashes | head
```

**Crack NTLM:**

```bash
hashcat -m 1000 ntlm.txt rockyou.txt
```

## Verify

```bash
hashcat --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
