---
name: azazael-bin-nmap
description: Callable skill for nmap — Network discovery and security scanning
metadata:
  category: recon
  project: azazael
  priority: medium
---

# nmap

> Network discovery and security scanning

## Identity

| Field | Value |
|-------|-------|
| Tool | `nmap` |
| Version | `Nmap version 7.99 ( https://nmap.org )` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/nmap (Kali)
```

## EXECUTE — canonical invocations

**Scan a single host:**

```bash
nmap -sV -sC 192.168.1.1
```

**Full port sweep:**

```bash
nmap -p- -T4 target.example.com
```

**OS detection:**

```bash
nmap -O target.example.com
```

**Top 1000 ports, no ping:**

```bash
nmap -Pn --top-ports 1000 target.example.com
```

## Verify

```bash
nmap --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
