---
name: azazael-rendering-methods
description: **[OBSOLETE MATH]** CAIN video rendering method comparison — see `azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md` for corrected file-size data. The technical codec and pipeline guidance below is still valid.
metadata:
  category: codex
  project: azazael
  priority: low
deprecated: true
superseded_by: azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md
---

# CAIN Rendering Methods — File Size Comparison & Codec Guide

> **⚠️ WARNING: The file-size claims in this skill are OBSOLETE.**
>
> All size estimates below were based on a ~27-panel template. The final 75-panel
> CAIN framework produces files **37–166% larger**. See the corrected analysis at:
> **`azazael/CAIN_DELIVERABLE_MATH_2026-06-05.md`**
>
> The technical guidance below (codec comparisons, pipeline patterns, anti-patterns)
> remains valid. Only the specific file-size numbers are incorrect.

## Overview

The same CAIN template produces different file sizes depending on rendering method.
The variance between smallest and largest is significant. This skill documents every
method, explains why, and specifies exactly which pipeline to use for each use case.

> **Note:** The old 6-method file-size comparison table (based on a ~27-panel template)
> has been removed and replaced by `CAIN_DELIVERABLE_MATH_2026-06-05.md` which contains
> actual measured sizes for the 75-panel framework.
>
> Key differences from the old (incorrect) claims:
> - Panels: **11.5 MB** (old claim was 8.4 MB — 27-panel estimate)
> - HEVC 720p 2.5x video: **119.9 MB** (old claim was ~45 MB — projection was unrealistic)
> - Puppeteer final video: **263.5 MB** (old claim was 120 MB — based on shorter template)

## Why Puppeteer Beats PIL (Technical)

**PIL:** Re-rasterizes text frame-by-frame. Sub-pixel anti-aliasing varies between frames → temporal noise → H.264 can't reuse macroblocks → every frame looks unique to the encoder → bitrate blows up.

**Puppeteer:** Captures browser hardware compositor. Scrolling creates mathematically perfect translation vectors → P/B-frames express motion with near-zero bit budget → only changing pixels (CSS animations) consume bitrate.

**Result:** Puppeteer needs **half the bitrate** of PIL for identical visual quality.

## Codec Tradeoffs

| Codec | Compression vs H.264 | Encode Speed | Browser Support | Best For |
|-------|---------------------|-------------|-----------------|----------|
| H.264 (libx264) | Baseline 1.0x | Fast | Universal | Archival, compatibility |
| HEVC/H.265 (libx265) | ~40% smaller | 2-3x slower | Modern browsers | Sharing, smallest files |
| VP9 (libvpx-vp9) | ~30% smaller | 5-10x slower (CPU) | Chrome/Firefox | Web streaming |
| AV1 (libaom-av1) | ~50% smaller | 10-20x slower (CPU) | Emerging | Future-proof archival |

## Format Recommendations by Use Case

| Use Case | Best Format | Pipeline | Target Size |
|----------|------------|---------|-------------|
| **Quick review** | Static PNG panels | `capture_panels.js` | **11.5 MB** (75 panels at 720p) |
| **Sharing/viewing** | MP4 HEVC 720p 2.5x | ffmpeg libx265 CRF 28 | **~80-120 MB** |
| **Archival (universal)** | MP4 H.264 1080p 2.5x | ffmpeg libx264 CRF 23 | **~150-200 MB** |
| **Archival (Windows)** | WMV 1080p 2.5x | ffmpeg wmv2 -b:v 4000k | **~500 MB** |

## Optimal Pipeline (Smallest File)

```
Puppeteer capture (1280×720, 30fps)
  → ffmpeg: setpts=0.4*PTS (2.5x speed)
  → ffmpeg: libx265 CRF 28 (HEVC)
  → ffmpeg: -an (strip audio)
  → ~80-120 MB (depending on content complexity)
```

## Profile & Bitrate Guide

| Profile | B-frames | Use Case |
|---------|----------|----------|
| **High** (always use) | 2 | Enables inter-frame compression — standard for all CAIN |
| Main | 1 | Slightly less compression |
| **Constrained Baseline** | 0 | ❌ NEVER USE — every frame is a keyframe, massive files |

### CRF Guide for Text/CSS Content

| CRF | Quality | Size vs CRF 23 | Best For |
|-----|---------|---------------|----------|
| 18 | Visually lossless | +50% | Not recommended (overkill for text) |
| 23 | Excellent | Baseline | Archival |
| 26 | Very good | -25% | Sharing |
| 28 | Good | -40% | Smallest viable — text still perfectly legible |
| 30+ | Degraded | -50%+ | Not recommended (text artifacts appear) |

**Key insight:** Text compresses perfectly at higher CRFs. CRF 26-28 for text looks identical to CRF 18 for organic video. Don't waste bits encoding sharp monospace edges.

## Resolution Guide for Text Content

| Resolution | Pixels | File Size vs 1080p | Legibility |
|-----------|--------|--------------------|------------|
| 1920×1080 (1080p) | 2.07M | 1.0x | Perfect — but pixel bloat for text |
| 1280×720 (720p) | 0.92M | ~0.6x | Perfect for Courier/monospace at video scale |
| 960×540 | 0.52M | ~0.4x | Still legible but smaller margins |
| 640×360 | 0.23M | ~0.2x | Hard to read — NOT recommended |

**Recommendation:** 720p is the sweet spot. Text at video scale (not screenshot scale) is fully legible at 720p, and you save 40% file size vs 1080p.

## Anti-Patterns

| ❌ NEVER | ✅ ALWAYS |
|----------|----------|
| PIL frame-by-frame for scrolling text | Puppeteer browser compositor |
| WMV as primary format | H.264 or HEVC MP4 |
| Constrained Baseline profile | High profile with B-frames=2 |
| CRF < 20 for text content | CRF 23-28 for text |
| 1080p for sharing | 720p for sharing |
| Audio track in CAIN videos | Strip audio (-an) |

## Related Lessons

- LESSONS_MASTER.md #79 — CAIN Video Rendering Methods — File Size Comparison & Optimal Pipeline
- LESSONS_MASTER.md #01 — puppeteer-screen-recorder defaults to Constrained Baseline
- LESSONS_MASTER.md #02 — CAIN Standard encoding parameters
- LESSONS_MASTER.md #03 — Comparing video pipelines: PIL+ffmpeg vs puppeteer-screen-recorder

## Related Skills

- `azazael-cain-pipeline` — Puppeteer rendering pipeline, injection workflow
- `azazael-cain-template` — Template optimization, session data injection
- `azazael-codex` — CODEX video generation overview
- `azazael-codex-video` — HTML animation patterns, ffmpeg commands
