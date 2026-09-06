---
name: azazael-bin-rustscan
description: Callable skill for rustscan — Ultra-fast port scanner written in Rust (feeds nmap)
metadata:
  category: recon
  project: azazael
  priority: medium
---

# rustscan

> Ultra-fast port scanner written in Rust (feeds nmap)

## Identity

| Field | Value |
|-------|-------|
| Tool | `rustscan` |
| Version | `rustscan 2.3.0` |
| Status | INSTALLED |

## Install

```bash
apt install rustscan  (or cargo install rustscan)
```

## EXECUTE — canonical invocations

**Fast scan all ports:**

```bash
rustscan -a 192.168.1.1 -- -sV
```

**Batch scan with nmap args:**

```bash
rustscan -a 10.0.0.0/24 -b 1000 -- -sC -sV
```

**Scan with custom range:**

```bash
rustscan -a 192.168.1.1 -r 1-65535
```

## Verify

```bash
rustscan --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
