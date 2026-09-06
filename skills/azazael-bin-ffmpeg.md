---
name: azazael-bin-ffmpeg
description: Callable skill for ffmpeg — Universal audio/video transcoding and processing (FFmpeg)
metadata:
  category: media
  project: azazael
  priority: medium
---

# ffmpeg

> Universal audio/video transcoding and processing (FFmpeg)

## Identity

| Field | Value |
|-------|-------|
| Tool | `ffmpeg` |
| Version | `ffmpeg version 8.1.1-3 Copyright (c) 2000-2026 the FFmpeg developers` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/ffmpeg (Kali, installed Aug 23 2026)
```

## EXECUTE — canonical invocations

**Convert video:**

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4
```

**Extract audio:**

```bash
ffmpeg -i video.mp4 -vn -acodec libmp3lame audio.mp3
```

**Resize video:**

```bash
ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
```

**Screenshot frame:**

```bash
ffmpeg -ss 00:01:00 -i input.mp4 -frames:v 1 frame.png
```

## Verify

```bash
ffmpeg --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
