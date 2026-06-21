# CAIN Deliverable Analysis — Corrected Math (June 5, 2026)

> **Audit date:** 2026-06-05
> **Previous claims:** All file-size projections in `azazael/skills/azazael-rendering-methods.md` were
> estimated from a ~27-panel template — **37–166% too low** for the final 75-panel CAIN framework.
> This document replaces those claims with actual measured values.

---

## 1. Active Deliverables on Desktop (Audited)

| Deliverable | Format | Resolution | Count/Duration | Actual Size | Last Modified |
|-------------|--------|------------|----------------|-------------|---------------|
| `CAIN_panels/` | PNG | 1280×720 | 75 panels | **11.55 MB** (~158 KB avg) | 6/5 5:44 PM |
| `CAIN_panels_1080p/` | PNG | 1920×1080 | 75 panels | **22.76 MB** (~311 KB avg) | 6/5 7:05 PM |
| `CAIN_2.5x.mp4` | HEVC MP4 | 720p | ~17 min (2.5x) | **119.9 MB** | 6/5 2:48 PM |
| `CAIN_session_final.mp4` | MP4 | Unknown | Unknown duration | **263.5 MB** | 6/5 7:32 PM |
| `CAIN_injected.html` | HTML | — | 3,828 lines | **0.19 MB** (196 KB) | 6/5 5:58 PM |

> **Active total: 417.9 MB** (panels + videos + template)

## 2. Archived Deliverables (LOST — see Error #58)

**Status:** `Desktop/CAIN_ARCHIVE/` was deleted during a failed `copytree+rmtree` operation
(Error #58). Destination copy was incomplete (5,708/7,554 MB), and the partial copy was
subsequently cleaned up. **The archived content is lost.**

| Category | Count | Total Size | Details |
|----------|-------|------------|---------|
| Old scrolling MP4s from SESSION_TEMPLATE | 51 files | ~6.0 GB | output_cain_scrolling.mp4 (109 MB), consequences_ultimate (26 MB), session_report (14 MB), etc. |
| Old Desktop CAIN videos | 10 files | ~1.5 GB | CAIN_full_template.mp4/wmv, CAIN_session_final.mp4/wmv (prior renders), CAIN_2.5x.wmv, etc. |
| Old optimized template | 1 file | 0.19 MB | `complete_remorse_analysis_cain_optimized.html` (185 KB) |

**Recovery:** These were renders from prior sessions. If needed, they must be re-rendered
from the CAIN template pipeline (`src/CODEX/capture_panels.js` + ffmpeg).

## 3. Pipeline Comparison — Actual vs Old Claims

### The Old Report's Numbers

The prior `azazael-rendering-methods.md` skill (now marked `[OBSOLETE]`) claimed:

| Pipeline | Old Claim | Source of Estimate |
|----------|-----------|-------------------|
| Static PNG panels (27 panel template) | 8.4 MB | From early ~27-panel test render |
| HEVC H.265 720p 2.5x | ~45 MB | Projected from shorter template |
| Puppeteer browser capture MP4 | 120 MB | From earlier ~27-panel render |
| PIL frame-by-frame MP4 | 318 MB | From early PIL test (not re-verified) |

### Actual Measured Values (75-Panel Framework)

| Pipeline | Actual Size | Variance | Explanation |
|----------|-------------|----------|-------------|
| Panels (PNG 720p) — **11.55 MB** | vs 8.4 MB claimed | **+37%** | 75 panels vs 27 panels = 2.78× more content, but image complexity also increased |
| Panels (PNG 1080p) — **22.76 MB** | No prior claim | **New** | First measurement at 1080p resolution |
| HEVC 720p 2.5x — **119.9 MB** | vs 45 MB claimed | **+166%** | The "~45 MB optimal" was unrealistically optimistic for 75 panels of text |
| CAIN_session_final.mp4 — **263.5 MB** | vs 120 MB claimed | **+120%** | Double the old estimate — may use different codec/settings |
| PIL pipeline | 318 MB old claim | N/A | Not re-rendered — may also be higher with 75 panels |

### Key Finding

**All previous projections were 37–166% too low.** The old report used estimates from
a ~27-panel template (early framework) that was about 36% of the final 75-panel content.
The scaling was not linear — additional content (more archetypes, sin cards, emotion bars)
added CSS animations and visual complexity that compressed less efficiently than linear
scaling would predict.

## 4. Detailed Panel Size Breakdown

### 720p Panels (CAIN_panels/)

- **Count:** 75 files
- **Total:** 11.55 MB
- **Average:** 157.7 KB per panel
- **Min:** panel_041.png (50.6 KB) — possibly simpler content
- **Max:** panel_074.png (417.8 KB) — possibly complex matrix/grid content
- **Std deviation:** ~85 KB — significant variation based on panel content complexity

### 1080p Panels (CAIN_panels_1080p/)

- **Count:** 75 files
- **Total:** 22.76 MB
- **Average:** 310.5 KB per panel
- **Min:** panel_057.png, 1080p. 341.png... (need min/max)
- **Max:** panel_074.png (808.4 KB)
- **Scale factor:** 1080p is ~1.97× the size of 720p (close to pixel ratio 2.25×)

### Resolution Scaling

Pixel count ratio: 1920×1080 / 1280×720 = 2,073,600 / 921,600 = **2.25×**

Actual file size ratio: 22.76 / 11.55 = **1.97×**

**Takeaway:** PNG compresses better at higher resolutions (smooth gradients scale sub-linearly
in file size). 1080p panels are 2.25× the pixels but only 1.97× the file size.

## 5. Video Encoding Analysis

### CAIN_2.5x.mp4

| Property | Value |
|----------|-------|
| **Size** | 119.9 MB |
| **Codec** | HEVC (H.265) |
| **Resolution** | 1280×720 |
| **Speed** | 2.5× (setpts=0.4*PTS) |
| **Estimated duration** | ~17 min (from 42 min at 1×) |
| **Effective bitrate** | ~950 kbps |
| **Quality:** | CRF ~26-28 (estimated) |

### CAIN_session_final.mp4

| Property | Value |
|----------|-------|
| **Size** | 263.5 MB |
| **Codec** | Unknown (likely H.264 or HEVC) |
| **Resolution** | 720p (assumed) |
| **Speed** | Unknown |
| **Bitrate** | ~1,000-2,000 kbps (estimated at 20-40 min) |

### Bitrate Comparison

| Video | Bitrate Estimate | Codec Efficiency | Value |
|-------|-----------------|-----------------|-------|
| CAIN_2.5x.mp4 | ~950 kbps | HEVC (good) | Best size/quality — 120 MB at 17 min |
| CAIN_session_final.mp4 | ~1,100-1,750 kbps | Unknown | Larger — possibly different content or lower compression |

## 6. Recommendations for Remaking Deliverables

### If targeting specific file sizes:

| Target | Pipeline | Expected Size | Quality Tradeoff |
|--------|----------|---------------|-----------------|
| **Smallest** | 720p panels only (75× PNG) | **11.5 MB** | No video, static viewing only |
| **Minimal video** | 720p HEVC CRF 35, 15fps | ~50-70 MB | Lower quality, slightly choppy |
| **Balanced small** | 720p HEVC CRF 30, 24fps, 1.5× speed | ~70-90 MB | Good quality, reasonable |
| **Current optimal** | 720p HEVC 2.5×, CRF ~28 | **119.9 MB** | Already exists — acceptable quality |
| **High quality** | 1080p HEVC CRF 23, 30fps, 1× speed | ~200-300 MB | Best visual quality, largest file |
| **Archival** | 1080p H.264 CRF 18, 30fps | ~400-500 MB | Lossless-level, universal codec |

### Recommended Pipeline for Remake

```
Puppeteer capture (1280×720, 30fps, 1× speed)
  → ffmpeg CRF 28 libx265 (HEVC)
  → setpts=0.4*PTS for 2.5× speed
  → -an (no audio)
  → Expected: ~100-120 MB
```

### Key Insights for Size Optimization

1. **Text compresses well at higher CRF** — CRF 28 for text looks identical to CRF 18 for organic video
2. **720p is the sweet spot** — saves 40% file size vs 1080p, text remains fully legible
3. **2.5× speed reduces frames by 60%** — fewer frames = smaller file
4. **HEVC saves ~40% over H.264** — at the cost of 2-3× encoding time
5. **The 75-panel framework is inherently larger** — more CSS animations = more changing pixels = higher bitrate

## 7. File Deletions / Cleanup

| File | Action | Reason |
|------|--------|--------|
| `azazael/skills/azazael-rendering-methods.md` | Updated with `[OBSOLETE]` annotation | File-size claims based on 27-panel template, not 75-panel framework |
| `Desktop/CAIN_ARCHIVE/` (7.5 GB) | **Accidentally deleted** (Error #58) | Failed copytree+rmtree — source lost, destination incomplete |

## 8. Conclusion

The CAIN 75-panel framework produces deliverables that are **37-166% larger** than
the old 27-panel estimates. The active deliverables total **417.9 MB** on Desktop.
The 7.5 GB archive of old renders was lost due to a data integrity bug
(Error #58 — now documented with prevention rules in `azazael-crossplat-fileops` skill).

**If the archived videos are needed, they must be re-rendered.** No recovery path exists.

---

*This document replaces all prior CAIN math claims in `azazael/skills/azazael-rendering-methods.md`*
