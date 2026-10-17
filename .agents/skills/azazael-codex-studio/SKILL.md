---
name: azazael-codex-studio
description: CODEX Studio standalone desktop app v3.1 — HTML to MP4/WMV video generation with Tkinter GUI, scene management, FFmpeg encoding, PIL frame rendering.
---

# CODEX Studio Skill

## Overview
Standalone Tkinter desktop app for HTML→MP4/WMV video generation.
**Location:** `src/CODEX/CODEX_Studio.py` | **Version:** 3.1.0

## Launch
```bash
python CODEX_Studio.py                          # GUI
python CODEX_Studio.py --cli --input X --output Y.mp4  # CLI
python CODEX_Studio.py --cli --scenes ...       # Scene mode
Desktop/CODEX_Studio_Launcher.bat               # Windows launcher
```

## Features
- **Scroll Mode:** Text extraction + vertical scroll with grid/gradient
- **Scene Mode:** HTML section detection, multi-scene with color-preserving crossfades
- **Output:** MP4 (H.264) + WMV (wmv2)
- **Resolutions:** 720p/1080p/4K | FPS: 1-60 | Duration: 5-300s
- **Shared engine:** `render_frames_to_png()` + `render_scenes_to_png()` for GUI+CLI

## Dependencies
| Component | Install |
|-----------|---------|
| Python 3.10+ | python.org |
| Pillow | `pip install Pillow` |
| FFmpeg 8.1.1+ | `winget install Gyan.FFmpeg` |
| Tkinter | Built-in |

## Architecture
```
HTMLSceneExtractor → render_scenes_to_png → _render_crossfade_transition
HTMLTextExtractor  → render_frames_to_png
_load_fonts / _calc_line_heights / _pick_text_style / _blend_color
CODEXStudio (Tkinter GUI) / cli_mode (argparse)
```

## Related Skills
- `azazael-codex` — CODEX systems overview
- `azazael-codex-video` — Video generation workflow + all 18 HTML templates
- `azazael-deploy` — Deployment and .exe packaging
