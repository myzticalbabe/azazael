---
name: azazael-codex-video
description: CODEX video generation workflow — HTML templates, animation patterns, ffmpeg encoding, PIL frame rendering, batch generation scripts.
---

# CODEX Video Generation Skill

## Overview
Complete workflow for generating MP4/WMV videos from CODEX HTML templates.
Covers HTML animation patterns, frame rendering, FFmpeg encoding, and batch automation.

## HTML Templates (18 total)

### Enhanced Templates (v3.1)
| File | Size | Features |
|------|------|----------|
| `CODEX_IMPROVED.html` | ~9KB | Canvas particles, 3D perspective, matrix rain, glass-morphism cards, glitch text, scene transitions |
| `AZAAZEL_VIDEO_ENHANCED.html` | ~14KB | 5-scene architecture workflow, canvas particle web, 3D grid, floating orbs, progress bar |
| `SCROLL_VIDEO_ENHANCED.html` | ~18KB | Parallax layers, trail canvas, intersection observers, typewriter animation, keyframe effects |

### Analysis Reports
| File | Size |
|------|------|
| `ANALYSIS_REPORT.html` | ~14KB |
| `ANALYSIS_REPORT_DIVERSE.html` | ~30KB |
| `ANALYSIS_REPORT_V2.html` | ~47KB |
| `FULL_ECOSYSTEM_ANALYSIS.html` | comprehensive/ |
| `ALL_11_SYSTEMS_RICH.html` | comprehensive/ |

### Interactive & Visualization
| File | Size |
|------|------|
| `ANIMATION_SHOWCASE.html` | ~8KB |
| `Azazael_DUAL_PANE.html` | ~33KB |
| `Azazael_REFERENCE.html` | ~102KB |
| `IMMERSIVE_AZAZAEL.html` | ~29KB |
| `IMMERSIVE_V2.html` | ~18KB |
| `MERMAID_GRAPHS.html` | ~6KB |
| `STRUCTURE_VISUALIZER.html` | ~8KB |
| `ULTIMATE_SELECTOR.html` | ~10KB |
| `CINEMATIC_SCROLL.html` | ~5KB |
| `SCROLL_VIDEO_GENERATOR.html` | ~12KB |
| `popup.html` | ~6KB |

### Session & Special
| File | Source |
|------|--------|
| `AZAAZEL_VIDEO.html` | Original video template |
| `complete_remorse_analysis_cain.html` | G:\ analysis |
| SESSION_TEMPLATE/ | G:\ session system |

## Video Generation Scripts (VIDEOS/)

### Primary Pipeline
- `CODEX_Studio.py` — Standalone GUI + CLI (v3.1, recommended)
- `create_video.py` — MoviePy + ffmpeg PPM pipeline
- `make_video.py` — PIL frames → ffmpeg encoding
- `create_scrolling_video.py` — Scrolling text video generator

### Batch Scripts
- `generate_video.bat` — Quick video generation
- `make_azazael_video.bat` — Full Azazael video production
- `make_video.bat` — Standard video build
- `generate_comprehensive.bat` — Comprehensive analysis video

### Specialty Generators (from E:\ backup)
- `create_azazael_educational_video.py` — Educational content
- `create_dual_pane_popup.py` — Dual pane + popup effects
- `create_dual_pane_video.py` — Dual-pane HTML preview generator (canonical producer of `AZAAZEL_DUAL_PANE.html` → `Azazael_DUAL_PANE.html`; see builder status below)
- `create_reference_video.py` — Reference documentation video
- `generate_matrix_video.py` — Matrix-style effects
- `generate_video.py` / `generate_video_v2.py` — Alternative pipelines
- `make_video_docs.py` — Documentation video

### Builder status map (audited 2026-09-02)

Know which producer owns which HTML before editing:

| Artifact | Canonical producer | Status | Notes |
|---|---|---|---|
| `Azazael_DUAL_PANE.html` (in VIDEOS/) | `create_dual_pane_video.py` | ✅ **CANONICAL** | Generates the HTML preview; flat `src/CODEX/Azazael_DUAL_PANE.html` + archived copies (Documents, archived_unified, G: FROM Z) are historical/older-generation — do NOT edit those; regenerate through the script |
| Any CODEX video HTML | `CODEX_Studio.py` (v3.1, recommended) or the named `create_*` script | ✅ **CANONICAL** | Script is the producer; the .html is a build artifact |

**REAL INCIDENT (2026-09-02, multi-line-string defect):** `Azazael_DUAL_PANE.html`
carried a JS `SyntaxError` — an `alert('...')` single-quoted string spanned real
newlines (lines 558–562) with plain-text lines inside, stranding the closing
`');`. Root cause was in the GENERATOR: `create_dual_pane_video.py` wrote the alert
as `'…' + scenes.length + '…'` with literal `\n` inside a regular triple-quoted
Python string — Python turned those `\n` into REAL newlines in the emitted HTML,
which is illegal inside a JS single-quoted string. **Fix:** the emitted JS now uses
a backtick template literal (`` `Frame export would generate ${scenes.length} …` ``)
— real newlines are legal inside backticks, and `${…}` survives verbatim because
the Python string is not an f-string. Verified: regenerated output renders in
headless Chrome with **0 console errors / 0 exceptions** (the same defect class as
the AOA literal-`\n` join — see `html-render-verification` skill). Lesson: **when
you fix a generated .html, also fix its generator — otherwise the next run
reintroduces the bug.**
- `make_video_quad.py` / `make_video_v2.py` / `make_video_v3.py` — Multi-panel variants
- `make_video_vibrant.py` — High-saturation rendering
- `make_video_zip.py` / `make_video_zipper.py` — Compression-focused
- `video_popup.py` — Popup overlay effects

### Utilities
- `compress_video.py` — Video compression with codec detection
- `frame_sequence.json` — Frame sequence configuration

## FFmpeg Commands

### MP4 (H.264)
```bash
ffmpeg -y -framerate 30 -i frame_%06d.png -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p output.mp4
```

### WMV (Windows Media)
```bash
ffmpeg -y -framerate 30 -i frame_%06d.png -c:v wmv2 -q:v 2 output.wmv
```

### Installation
```bash
# Windows
winget install Gyan.FFmpeg

# Verify
ffmpeg -version
ffmpeg -encoders | grep -E "libx264|wmv2"
```

## Animation Patterns

### Canvas-Based
- Particle webs with connecting lines (CODEX_IMPROVED.html)
- Matrix rain effect using Katakana characters
- Trail/fade effects with requestAnimationFrame

### CSS 3D
- Perspective grid floor (transform: perspective + rotateX)
- Floating stat rings with pulse animations
- Orbiting nodes with CSS animations

### Scene Transitions
- Fade In/Out overlays
- Parallax scroll layers
- Intersection Observer triggers
- Typewriter text effects
- Keyframe slide/fade sequences

## Workflow

```
1. Author HTML template with animations
2. Launch CODEX_Studio.py (GUI or CLI)
3. Select HTML → Configure resolution/FPS/duration
4. Optional: Enable Scene Mode for section detection
5. Generate → PIL renders frames → FFmpeg encodes video
6. Output: Desktop/CODEX_Studio_Output/
```

## Related Skills
- `azazael-codex` — CODEX systems overview
- `azazael-codex-studio` — Standalone desktop app
- `azazael-files` — File structure and conventions
- `azazael-deploy` — Deployment and .exe packaging
- `html-render-verification` — CDP render gate; every generated .html must pass 0 console errors (the 2026-09-02 multi-line-string defect was caught only by rendering)
