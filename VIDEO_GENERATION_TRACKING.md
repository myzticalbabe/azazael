# Video Generation Tracking — June 2026

Tracks all project changes related to video generation. Run `python scripts/batch_render.py --list` for live status.

**See `LESSONS_MASTER.md #01-#02` for CAIN Standard encoding rationale (CRF 23, High profile, medium preset, 4 Mbps).**

---

## Pipeline Tools (Created/Modified This Session)

| Tool | Purpose | Status |
|------|---------|--------|
| `scripts/batch_render.py` | Batch render: discover → generate script → puppeteer record → optional compress | ✅ Scans 3 dirs: SESSION_TEMPLATE, OLD_PROJECT, CAPABILITIES |
| `scripts/generate_capability_templates.py` | Generate 19 capability HTML templates with themed CSS | ✅ Works, `--list` to see categories, `--category x` for single |
| `scripts/cain_video_pipeline_demo.py` | E2E demo pipeline: template → record → compress → analyze | ✅ Path bug fixed |
| `LESSONS_MASTER.md` | 12 lessons on CAIN Standard, encoding, scroll pattern, path pitfalls | ✅ Cross-linked from all recorder scripts |

---

## Asset Inventory

### Source 1: SESSION_TEMPLATE/templates/ (26 templates — all rendered)

| Template | HTML | Recorder Script | MP4 | WMV |
|----------|------|----------------|-----|-----|
| `consequences_ultimate.html` 26KB | ✅ | ✅ | ✅ 26MB on D: | ❌ |
| `consequences_report.html` 24KB | ✅ | ✅ | ✅ 6.5MB on D: | ❌ |
| `consequences_cosmic.html` 8KB | ✅ | ✅ | ✅ 2.8MB on D: | ❌ |
| `consequences_glass.html` 8KB | ✅ | ✅ | ✅ 3.1MB on D: | ❌ |
| `consequences_neon.html` 8KB | ✅ | ✅ | ✅ 3.2MB on D: | ❌ |
| `session_report.html` 14KB | ✅ | ✅ | ✅ 14MB on D: | ❌ |
| `session_steampunk.html` 4KB | ✅ | ✅ | ✅ 228KB on D: | ❌ |
| `session_web.html` 12KB | ✅ | ✅ | ✅ local | ❌ |
| `session_flow.html` 10KB | ✅ | ✅ | ✅ local | ❌ |
| `session_explicit_web.html` 19KB | ✅ | ✅ | ✅ local | ❌ |
| `session_complete_web.html` 18KB | ✅ | ✅ | ✅ local | ❌ |
| `session_static_details.html` 14KB | ✅ | ✅ | ✅ local | ❌ |
| `session_twinkle_web.html` 11KB | ✅ | ✅ | ✅ local | ❌ |
| `failure_report.html` 7KB | ✅ | ✅ | ✅ 7.4MB on D: | ❌ |
| `env_hierarchy.html` 13KB | ✅ | ✅ | ✅ 956KB on D: | ❌ |
| `output_ultimate.html` 15KB | ✅ | ✅ | ✅ local | ❌ |
| `output_cain.html` 195KB | ✅ | ✅ | ✅ 108MB on D: (1061s) | ✅ 503MB on D: |
| `output_firehorse.html` 18KB | ✅ | ✅ | ✅ local | ❌ |
| `output_report.html` 7KB | ✅ | ✅ | ✅ 2.7MB on D: | ❌ |
| `output_cosmic.html` 8KB | ✅ | ✅ | ✅ 2.3MB on D: | ❌ |
| `output_ethereal.html` 10KB | ✅ | ✅ | ✅ 2.1MB on D: | ❌ |
| `output_glass.html` 8KB | ✅ | ✅ | ✅ 1.7MB on D: | ❌ |
| `output_grimoire.html` 10KB | ✅ | ✅ | ✅ 2.2MB on D: | ❌ |
| `output_mystical.html` 15KB | ✅ | ✅ | ✅ 4.7MB on D: | ❌ |
| `output_neon.html` 8KB | ✅ | ✅ | ✅ 3.2MB on D: | ❌ |
| `output_occult.html` 12KB | ✅ | ✅ | ✅ 2.4MB on D: | ❌ |

### Source 2: OLD_PROJECT/ (5 templates — all rendered)

| Template | HTML | Recorder Script | MP4 | WMV |
|----------|------|----------------|-----|-----|
| `Apology.html` 24KB | ✅ | ✅ | ✅ (16.7MB) | ❌ |
| `Moral_Accounting.html` 14KB | ✅ | ✅ | ✅ (6.5MB) | ❌ |
| `Who_Profits_From_Deception.html` 13KB | ✅ | ✅ | ✅ (7.5MB) | ❌ |
| `Open_Explanation_BlueRainbow.html` 9KB | ✅ | ✅ | ✅ (6.2MB) | ❌ |
| `Open_Explanation_Pastel.html` 9KB | ✅ | ✅ | ✅ (4.9MB) | ❌ |

### Source 3: CAPABILITIES/ (19 templates — 15/19 recorded to MP4)

| Capability | Theme | HTML | Recorder Script | MP4 | WMV |
|-----------|-------|------|----------------|-----|-----|
| `orchestration.html` 6.7KB | cosmic | ✅ | ✅ | ✅ (0.3MB) | ❌ |
| `monitor.html` 5.4KB | neon | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `security.html` 4.4KB | occult | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `profiling.html` 4.7KB | glass | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `telemetry.html` 5.0KB | ethereal | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `container.html` 4.4KB | grimoire | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `communication.html` 6.4KB | cosmic | ✅ | ✅ | ✅ (0.2MB) | ❌ |
| `backup.html` 5.2KB | neon | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `config.html` 4.7KB | glass | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `learning.html` 5.1KB | mystical | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `migration.html` 5.1KB | ethereal | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `visualization.html` 6.4KB | cosmic | ✅ | ✅ | ✅ (0.2MB) | ❌ |
| `utility.html` 5.2KB | neon | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `diagnostic.html` 4.5KB | glass | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `analysis.html` 4.7KB | mystical | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `ml.html` 3.8KB | grimoire | ✅ | ✅ | ✅ (0.0MB) | ❌ |
| `sync.html` 4.4KB | neon | ✅ | ✅ | ✅ (0.1MB) | ❌ |
| `eve_unleashed.html` 6.5KB | cosmic | ✅ | ✅ | ✅ (0.3MB) | ❌ |
| `semantic_harvester.html` 4.5KB | grimoire | ✅ | ✅ | ✅ (0.1MB) | ❌ |

---

## D: Drive Summary

| File | Size | WMV |
|------|------|-----|
| `complete_remorse_cain.mp4` | 476 MB | ✅ 207 MB WMV |
| `complete_remorse_cain_compressed.mp4` | 185 MB | — |
| `output_cain_scrolling.mp4` | 108 MB | ✅ 503 MB WMV |
| `consequences_ultimate_scrolling.mp4` | 26 MB | ✅ 45 MB WMV |
| `session_report_scrolling.mp4` | 13 MB | ✅ 21 MB WMV |
| `failure_report_scrolling.mp4` | 7.3 MB | ✅ 34 MB WMV |
| `consequences_report_scrolling.mp4` | 6.5 MB | ✅ 29 MB WMV |
| `output_mystical_scrolling.mp4` | 4.7 MB | ✅ 25 MB WMV |
| `consequences_neon_scrolling.mp4` | 3.2 MB | ✅ 20 MB WMV |
| `output_neon_scrolling.mp4` | 3.2 MB | ✅ 25 MB WMV |
| `consequences_glass_scrolling.mp4` | 3.1 MB | ✅ 15 MB WMV |
| `consequences_cosmic_scrolling.mp4` | 2.8 MB | ✅ 16 MB WMV |
| `output_report_scrolling.mp4` | 2.6 MB | ✅ 19 MB WMV |
| `output_occult_scrolling.mp4` | 2.4 MB | ✅ 13 MB WMV |
| `output_cosmic_scrolling.mp4` | 2.3 MB | ✅ 14 MB WMV |
| `output_grimoire_scrolling.mp4` | 2.2 MB | ✅ 12 MB WMV |
| `output_ethereal_scrolling.mp4` | 2.1 MB | ✅ 12 MB WMV |
| `output_glass_scrolling.mp4` | 1.6 MB | ✅ 8 MB WMV |
| `env_hierarchy_scrolling.mp4` | 0.9 MB | ✅ 4 MB WMV |
| `session_steampunk_scrolling.mp4` | 0.2 MB | ✅ 10 MB WMV |

---

## New Files Created This Session

| File | Size | Location |
|------|------|----------|
| `LESSONS_MASTER.md` | 15 KB | `azazael/` |
| `generate_capability_templates.py` | 39 KB | `azazael/scripts/` |
| `batch_render.py` (updated) | 18 KB | `azazael/scripts/` |
| `cain_video_pipeline_demo.py` (updated) | 30 KB | `azazael/scripts/` |
| 19 capability HTML templates | 3-7 KB each | `azazael/src/CODEX/CAPABILITIES/` |
| 52 recorder scripts (19 new + 29 existing + 4 updated) | — | `azazael/src/CODEX/SESSION_TEMPLATE/recorders/` |
| `complete_remorse_cain.wmv` | 207 MB | `D:/` |
| `complete_remorse_cain_compressed.mp4` | 185 MB | `D:/` |
| `output_cain_scrolling.mp4` | 108 MB | `D:/` |
| `output_cain.wmv` | 503 MB | `D:/` |

---

## Pending Work for Future Sessions

| Priority | Task | Status | Notes |
|----------|------|--------|-------|
| ✅ Done | Record `output_cain.html` (195KB) | ✅ 108MB, 1061s | Needed 1800s timeout — 10x larger than avg templates |
| ✅ Done | Batch WMV conversion (17 files) | ✅ All _scrolling.mp4 + cain.mp4 | WMV2 files are 5-10x MP3 size (older codec) |
| ✅ Done | Record remaining 4 capability MP4s | ✅ All 19 recorded | sync, telemetry, utility, visualization — all <0.2MB |
| ✅ Done | Compress complete_remorse_cain.mp4 | ✅ 476 MB → 185 MB (61%) | Target ~80-120 MB; better results may need compress_video.py --profile cain |
| 🟢 Low | Write dedicated `scripts/convert_to_wmv.py` | ❌ Not started | For repeatable WMV batch conversion |
| 🟢 Low | Sync all new files to G: drive | ❌ Not started | Capability templates, new recorder scripts, WMV files |

---

## Notes

- **WMV file sizes** are 5-10x larger than source MP4s because WMV2 is an older, less efficient codec. This is expected. The WMV files serve as a fallback format; MP4s are the primary delivery format.
- **output_cain** is the outlier: 195KB template → 108MB MP4 (1061s record time). All other templates are <20KB and record in <60s. batch_render.py's default 600s timeout is sufficient for all templates except this one.
- **CAIN compression** (476 MB → 185 MB, 61% saved) fell short of the ~80-120 MB estimate from LESSONS_MASTER.md #02 because the source was already partially compressed. Running `compress_video.py --profile cain` (which uses proper GOP settings) may yield better results than raw ffmpeg.

---

*Generated: June 2, 2026 — Auto-inventory from batch_render.py + file system scan*
*Run `python scripts/batch_render.py --list` for live status update*
*See `LESSONS_MASTER.md` for CAIN Standard encoding details*
