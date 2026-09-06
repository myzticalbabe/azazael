---
name: azazael-bin-exiftool
description: Callable skill for exiftool — Read/write/edit EXIF metadata in image/audio/video files (Phil Harvey)
metadata:
  category: osint
  project: azazael
  priority: medium
---

# exiftool

> Read/write/edit EXIF metadata in image/audio/video files (Phil Harvey)

## Identity

| Field | Value |
|-------|-------|
| Tool | `exiftool` |
| Version | `Syntax:  exiftool [OPTIONS] FILE` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/exiftool (Kali)
```

## EXECUTE — canonical invocations

**Read all metadata:**

```bash
exiftool image.jpg
```

**Extract GPS only:**

```bash
exiftool -gps* image.jpg
```

**JSON output:**

```bash
exiftool -j image.jpg
```

**Strip metadata:**

```bash
exiftool -all= image.jpg
```

## Verify

```bash
exiftool --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
