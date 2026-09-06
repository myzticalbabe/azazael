---
name: azazael-bin-foremost
description: Callable skill for foremost — File carving / data recovery from disk images (foremost)
metadata:
  category: forensics
  project: azazael
  priority: medium
---

# foremost

> File carving / data recovery from disk images (foremost)

## Identity

| Field | Value |
|-------|-------|
| Tool | `foremost` |
| Version | `foremost: invalid option -- '-'` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/foremost (Kali)
```

## EXECUTE — canonical invocations

**Carve from image:**

```bash
foremost -i disk.img -o /tmp/carved
```

**Specific file types:**

```bash
foremost -t jpeg,png -i disk.img
```

**Verbose carve:**

```bash
foremost -v -i disk.img -o /tmp/out
```

## Verify

```bash
foremost --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
