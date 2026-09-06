---
name: azazael-bin-john
description: Callable skill for john — John the Ripper — offline password cracker
metadata:
  category: cracking
  project: azazael
  priority: medium
---

# john

> John the Ripper — offline password cracker

## Identity

| Field | Value |
|-------|-------|
| Tool | `john` |
| Version | `John the Ripper 1.9.0-jumbo-1+bleeding-aec1328d6c 2021-11-02 10:45:52 +0100 OMP [linux-gnu` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/sbin/john (Kali)
```

## EXECUTE — canonical invocations

**Crack with default wordlist:**

```bash
john hash.txt
```

**Show cracked:**

```bash
john --show hash.txt
```

**Wordlist mode:**

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

## Verify

```bash
john --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
