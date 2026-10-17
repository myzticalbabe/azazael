---
name: azazael-cain-pipeline
description: CAIN video rendering pipeline — Puppeteer browser capture (NOT PIL), session-specific HTML injection, optimal encoding settings (HEVC 1080p CRF 26-28), inject → record → encode workflow. Load when rendering or troubleshooting CAIN psychoanalysis videos.
metadata:
  category: codex
  project: azazael
  priority: high
---

# CAIN Video Rendering Pipeline — Puppeteer Capture & Session Injection

## Overview

The CAIN (Cognitive Accountability & Introspective Navigation) video rendering pipeline produces psychoanalysis session reports as MP4/WMV videos. **CRITICAL: Always use Puppeteer (browser capture), never PIL frame-by-frame rendering.** Only browser capture preserves CSS animations (rainbow borders, neon glows, emoji dance, money snake coils, flow chart arrows).

## Why Puppeteer, Not PIL

| Factor | PIL (CODEX_Studio.py) | Puppeteer (browser) |
|--------|----------------------|---------------------|
| File size | 318 MB @ 1234 kbps | 194 MB @ 637 kbps |
| CSS animations | ❌ NOT captured | ✅ All 15 @keyframes captured |
| Sub-pixel noise | Creates temporal noise → defeats H.264 | Perfect compositor motion vectors |
| Scroll smoothness | Frame-by-frame stutter | Native browser compositor |
| Recommendation | **NEVER use for CAIN** | **ALWAYS use** |

**Technical reason:** PIL re-rasterizes text every frame, creating micro-variations that H.264 can't compress. Puppeteer captures the browser's hardware compositor — scrolling produces mathematically perfect translation vectors that encode as cheap P/B-frame motion.

## Complete Pipeline

```
1. GENERATE → inject_session_cain.py
   ├── Input:  complete_remorse_analysis_cain_optimized.html (template)
   ├── Inject: 6 session incidents, $590 damage, prevention rules
   └── Output: CAIN_injected.html (196KB)

2. RECORD → record_session_cain.js (Puppeteer)
   ├── Viewport: 1920×1080
   ├── Scroll: requestAnimationFrame at 5.0 WPS
   ├── Config: CRF 23, medium preset, High profile, B-frames=2
   └── Output: CAIN_session_final.mp4

3. ENCODE → ffmpeg (see encoding sections below)
   ├── Primary: 1080p HEVC CRF 26-28 (~80-120 MB, -tune grain for text)
   ├── WMV: wmv2, 4000k bitrate, 1920×1080
   └── Speed: 2.5x (setpts=0.4*PTS) if requested
```

## Optimal Encoding Settings

### 1080p HEVC — smallest file (recommended for sharing)
```bash
# Puppeteer already records at 1920×1080, then transcode to HEVC:
ffmpeg -i puppeteer_output.mp4 \
  -c:v libx265 -crf 28 -preset medium \
  -tune grain \
  -s 1920x1080 -r 25 -an \
  -tag:v hvc1 \
  CAIN_1080p_hevc.mp4  # → ~80-120 MB (text compresses very well)
```

### 1080p H.264 — archival quality (universal compatibility)
```bash
ffmpeg -i puppeteer_output.mp4 \
  -c:v libx264 -crf 23 -preset medium -tune grain \
  -s 1920x1080 -r 25 \
  CAIN_1080p_h264.mp4  # → ~150-200 MB
```

### 1080p WMV (Windows legacy)
```bash
ffmpeg -i puppeteer_output.mp4 \
  -c:v wmv2 -b:v 4000k \
  -s 1920x1080 -r 25 \
  CAIN_1080p.wmv  # → ~500 MB
```

### 2.5x speed (any format)
```bash
ffmpeg -i puppeteer_output.mp4 \
  -filter:v "setpts=0.4*PTS" \
  -c:v libx265 -crf 28 -preset medium -tune grain \
  -s 1920x1080 -r 25 -an \
  CAIN_2.5x_1080p.mp4
```

## Quick Render Commands

```bash
# Generate injected HTML
cd azazael && python src/CODEX/inject_session_cain.py --output src/CODEX/CAIN_injected.html

# Record with Puppeteer (captures all CSS animations, 1920×1080)
cd src/CODEX && node record_session_cain.js

# Encode to 1080p HEVC (smallest, recommended)
ffmpeg -y -i Desktop/CAIN_session_final.mp4 \
  -c:v libx265 -crf 28 -preset medium -tune grain \
  -s 1920x1080 -r 25 -an -tag:v hvc1 \
  Desktop/CAIN_1080p_hevc.mp4

# Create 2.5x speed HEVC version
ffmpeg -y -i Desktop/CAIN_session_final.mp4 \
  -filter:v "setpts=0.4*PTS" -an \
  -c:v libx265 -crf 28 -preset medium -tune grain \
  -s 1920x1080 -r 25 \
  Desktop/CAIN_2.5x_1080p.mp4

# Convert to 1080p WMV
ffmpeg -y -i Desktop/CAIN_session_final.mp4 \
  -c:v wmv2 -b:v 4000k \
  -s 1920x1080 -r 25 \
  Desktop/CAIN_1080p.wmv
```

## Key Files

| File | Purpose |
|------|---------|
| `src/CODEX/complete_remorse_analysis_cain_optimized.html` | Optimized CAIN template (191KB) |
| `src/CODEX/inject_session_cain.py` | Injects session data into template |
| `src/CODEX/record_session_cain.js` | Puppeteer recorder with smooth scrolling |
| `src/CODEX/capture_panels.js` | Sequential panel screenshot capture |
| `src/CODEX/generate_session_cain.py` | Superseded — standalone generator (replaced by injection) |

## Anti-Patterns

| ❌ NEVER | ✅ ALWAYS |
|----------|----------|
| Render CAIN videos with PIL/CODEX_Studio.py | Use Puppeteer (browser compositor) |
| Use generic CAIN_DATA.py constants | Inject session-specific incident data |
| Use Constrained Baseline H.264 | Use High profile with B-frames=2 |
| Use 720p as standard | Use 1080p for all CAIN deliverables |
| Use WMV as primary format | Use HEVC MP4 (smallest) or H.264 (compatible) |
| Skip the template injection step | Always inject session data before rendering |
| Use setInterval for scrolling | Use requestAnimationFrame for smooth scroll |
| Re-interpret pipeline instructions | Follow the documented pipeline exactly |

## Related Lessons

- LESSONS_MASTER.md #76 — CAIN Reports Must Be Session-Specific
- LESSONS_MASTER.md #77 — Why PIL Fails for CSS Animation-Rich Templates
- LESSONS_MASTER.md #78 — CAIN Video Pipeline: Puppeteer → ffmpeg End-to-End
- LESSONS_MASTER.md #79 — CAIN Video Rendering Methods — File Size Comparison
- LESSONS_MASTER.md #01 — puppeteer-screen-recorder defaults to Constrained Baseline
- LESSONS_MASTER.md #02 — CAIN Standard encoding parameters

## Related Skills

- `azazael-cain-template` — Template optimization, injection patterns
- `azazael-rendering-methods` — File-size comparison, codec tradeoffs
- `azazael-codex` — CODEX video generation overview
- `azazael-codex-video` — HTML animation patterns, ffmpeg commands
- `azazael-codex-studio` — CODEX Studio desktop app
