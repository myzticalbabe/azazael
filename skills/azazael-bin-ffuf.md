---
name: azazael-bin-ffuf
description: Callable skill for ffuf — Fast web fuzzer written in Go
metadata:
  category: web
  project: azazael
  priority: medium
---

# ffuf

> Fast web fuzzer written in Go

## Identity

| Field | Value |
|-------|-------|
| Tool | `ffuf` |
| Version | `Fuzz Faster U Fool - v2.1.0-dev` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/ffuf (Kali)
```

## EXECUTE — canonical invocations

**Directory fuzzing:**

```bash
ffuf -w wordlist.txt -u http://target/FUZZ
```

**Vhost fuzzing:**

```bash
ffuf -w hosts.txt -u http://target -H 'Host: FUZZ.target.com' -fs 1234
```

**Extension fuzzing:**

```bash
ffuf -w wordlist.txt -u http://target/FUZZ -e .php,.asp
```

## Verify

```bash
ffuf --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
