# Unified media tree (2026-10-28) — one home for animation, image, audio, video

Scatter it replaces: Desktop root (`*.mp4`, `KLEIN4B_*.png`, `QD_*`), `screen_clips/`,
`REC_60MIN/`, `HTML_MP4/`, `AZAZAEL_COSMOS_VIEWER/`, `DisclosureWhitepaper/*.mp4`,
`FACEBOOK/*.mp4`, `src/CODEX/VIDEOS/`, `src/CODEX/OUTPUT/`, `src/CODEX/*.html` one-offs.

## Layout

- `video/` — rendered outputs (MP4/WebM). **Gitignored (`*.mp4`)**: tree is the path convention, git holds the recipe (HTML + command), not the binary.
- `animation/` — animation sources (HTML/CSS/JS scenes, Puppeteer recorder scripts).
- `image/` — PNG/JPG/WebP stills, panel captures, storyboards-as-images.
- `audio/` — narration, scores, SFX.
- `storyboard/` — versioned HTML twins + render notes (word count, WPS, duration, command).

## Rules (from the protocol index §5–§6)

1. Duration derived from word count @ 5.0 WPS (30.0 fast variant) — never a round guess.
2. Recorder: 1920×1080 @30fps rAF, CRF 26/medium/yuv420p; `file://` assets inlined.
3. Nothing lives only on Desktop — storyboard HTML twins here; binaries gitignored by rule.
4. Migration backlog (hardcoded paths to move here): `src/CODEX/record_session_cain.js`
   (`C:/Users/clint/azazael/...` source, Desktop output), `screen_recorder.py` outputs,
   per-report MP4s under `DisclosureWhitepaper/` + `FACEBOOK/`. Move in lane order, one
   producer at a time, pipeline green after each.
