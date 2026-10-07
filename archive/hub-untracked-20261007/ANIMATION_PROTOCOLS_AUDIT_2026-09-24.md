# Animation Protocols — Forensic Audit (2026-09-24)

**Scope:** every artifact that calls itself an animation protocol:
`src/ANIMATION_PROTOCOLS.py`, `src/CODEX/CORE/ANIMATION_PROTOCOLS.py` (shim),
`src/matrix_animation.py`, `src/CODEX/CORE/matrix_animation.py` (shim),
`src/CODEX/CORE/enhanced_animations.py`, `src/CODEX/ANIMATION_SHOWCASE.html`,
`templates/video/animation_protocols.json` (+ the `Animation_Protocols_314t` /
`Enhanced_Animations_314t` / `Matrix_Animation_314t` packaging specs).

**Method:** full read of the catalog and both shims; structural read of
`enhanced_animations.py`, `matrix_animation.py`, the showcase HTML and the video
storyboard; consumer search over `*.py/*.html/*.js/*.bat` (excluding
`archived_unified/`, `output/`, `graphs/`); CSS static checks over the showcase.
Every defect below is cited file:line.

---

## 0. Inventory — what exists

| Artifact | Lines | What it is | Live consumers |
|---|---|---|---|
| `src/ANIMATION_PROTOCOLS.py` | 313 | catalog: 24 named techniques in 8 categories + 3 functions | **none** |
| `src/CODEX/CORE/ANIMATION_PROTOCOLS.py` | 36 | deprecation shim → root copy (correct pattern) | archived only |
| `src/CODEX/CORE/enhanced_animations.py` | 459 | 30+ real `@keyframes` (`AnimationDef`, `generate_css()`) | `src/CORE/WORMS/CODEX_TOOLS.py` (AnimationWorm) |
| `src/matrix_animation.py` | 256 | PIL matrix-cascade renderer → ffmpeg (old pipeline) | `__main__` only |
| `src/CODEX/CORE/matrix_animation.py` | 36 | deprecation shim → root copy | archived only |
| `src/CODEX/ANIMATION_SHOWCASE.html` | 611 | demo page: 29 `@keyframes`, 29 `infinite` animations, canvas loop | demo |
| `templates/video/animation_protocols.json` | 51 | CODEX video storyboard (20 s, 720p, 30 fps) | `scripts/master_generate.py:42` |

The only **live** animation implementation in the ecosystem is
`enhanced_animations.py` via the `CODEX_TOOLS` worm wrapper. Everything else is
dead, demo, or packaging.

## 1. What is wrong

### 1.1 The catalog's CSS generator emits animations that cannot animate
`src/ANIMATION_PROTOCOLS.py:221-253` (`generate_animation_protocol`):
the output declares `animation: <slug>-anim 1s ease-in-out;` but **never emits
the `@keyframes` block that declaration references**, and the technique's
actual effect is emitted as comments (`/* clip-path - configured via animation
*/`, line 244) — `css_properties` stores property *names*; no values exist
anywhere in the file. The "generator" produces a stub that a browser silently
ignores. `templates/video/animation_protocols.json` nonetheless advertises
"Production-Ready" — that claim is false for this surface.

### 1.2 The recommendation engine recommends techniques that do not exist
`src/ANIMATION_PROTOCOLS.py:254-271` (`get_best_animation_for_result`):
`"error": "Shake"` (line 259) — **"Shake" is not one of the 24 techniques**
anywhere in the catalog. A caller asking what to show on an error gets a name
that resolves to nothing.

### 1.3 The performance tiers don't resolve, and "impact" means two things
`src/ANIMATION_PROTOCOLS.py:273-298` (`create_animation_system`):
`performance_tiers` names "Fade In", "Bounce", "Shimmer", "Slide In",
"**Pulse Scale**" (nonexistent), "Glitch", "3D Flip" — 7 of 8 do not match
catalog names ("Fade In Scale", "Bounce Dots", "Shimmer Bar", "Slide In Up",
"Glitch Status", "Flip 3D"). Meanwhile every technique carries `"impact"`
(lines 18-214) which reads as *visual* impact ("Creates urgency"), while
`performance_tiers` is *cost* — the same LOW/MEDIUM/HIGH vocabulary on two
different axes. "Matrix Rain" is impact MEDIUM / cost HIGH; a consumer picking
by `impact` for performance reasons selects the expensive one.

### 1.4 The generator fails silently on bad input
`src/ANIMATION_PROTOCOLS.py:230-233`: a missing/typo'd technique falls back to
`techniques[0]` — **absence reads as evidence**, returning working-looking CSS
for the wrong effect. This is the exact defect class the mesh audits keep
flagging (Rule 4 family: a path that cannot report failure).

### 1.5 Four disjoint vocabularies; no single source of truth
- catalog: Glitch Status · Ring Pulse · Pie Fill · Hex Grid · Morph … (24 names)
- `enhanced_animations.py`: kenBurns · cinematicFade · confetti · shimmer ·
  ripple · mood-shift · fold … (30+ names, real keyframes)
- `ANIMATION_SHOWCASE.html`: auroraFlow · quantumFlicker · vortexSpin ·
  neuralPulse … (29 names)
- `animation_protocols.json`: `fade_in` / `slide_up` effects

Overlap between the catalog and the one working library is ~1 name
(Typewriter). The menu lists dishes neither kitchen makes. Nothing validates
any name against anything, so drift (already present: "Fade Scale" in the
storyboard vs "Fade In Scale") accumulates silently.

### 1.6 `matrix_animation.py` mutates the filesystem at import
`src/matrix_animation.py:20` runs `os.makedirs(OUTPUT_DIR)` at **module
import**. Root resolution (line 18) is `~/azazael` with two differently-cased
env vars (`AZAZAEL_ROOT` / `Azazael_ROOT`) instead of `CORE/paths.py`. It
renders 1,350 frames of 3,000-drop PIL cascades (lines 13-16) — the old CODEX
PIL pipeline, while the CAIN pipeline standard is Puppeteer capture ("NOT
PIL"). The ffmpeg call (line 232) is correctly list-args (no `shell=True`) and
gated behind `__main__` (line 204) — those parts are fine.

### 1.7 The showcase burns resources and ignores motion preferences
`src/CODEX/ANIMATION_SHOWCASE.html`: **29 `@keyframes`, 29 `infinite`
animations running simultaneously**, plus a canvas `requestAnimationFrame`
matrix loop (lines 439, 578) — never paused on tab hide, never throttled
offscreen. No `prefers-reduced-motion` in the showcase, `templates/`, or
`dashboard/` (only `enhanced_animations.py` emits it — its consumers don't).
Credit where due: the keyframes animate compositor-friendly properties
(no width/height/top/left inside `@keyframes` blocks — measured), though
`holographicGlitch` (clip-path) and `auroraBg` (300% `background-size` sweep)
are paint-heavy.

### 1.8 Packaging claims
The `Animation_Protocols_314t` / `Enhanced_Animations_314t` /
`Matrix_Animation_314t` specs package all three modules as standalone
products — including the dead catalog (1.1-1.4) and the import-mutating
renderer (1.6). A packaged stub is a shipped defect.

## 2. Suggested improvements (take order)

1. **One registry, one emitter.** Fold the catalog's 24 techniques into
   `enhanced_animations.py`'s `AnimationDef` format (name, category, keyframes,
   duration, timing, iteration) so `generate_css()` is the only CSS emitter.
   The catalog then becomes the metadata layer (use_case, cost) over *implemented*
   keyframes. Delete `generate_animation_protocol`'s stub output or make it emit
   class + `@keyframes` from the registry.
2. **Validate every name against the registry, in tests.** One test: every name
   in `get_best_animation_for_result`, `performance_tiers`, and the storyboard
   subtitles resolves to a registry key (catches "Shake", "Pulse Scale",
   "Fade Scale" at once). One test: every `animation:` declaration in generated
   CSS has a matching `@keyframes` (catches 1.1 forever).
3. **Fail loudly.** Unknown technique → explicit error (or `None`), never
   `techniques[0]` fallback (1.4).
4. **Split the axes.** Rename `impact` → `visual_impact` and
   `performance_tiers` → `cost_tier`, define both scales in one place (1.3).
5. **Fix `matrix_animation.py` hygiene:** move `os.makedirs` into the render
   entry point, resolve the root via `CORE/paths.py`, and decide its fate —
   either state its PIL use case (no-browser batch) or deprecate it to a shim
   like its siblings (1.6).
6. **Showcase performance + a11y:** add `prefers-reduced-motion` (copy the
   pattern from `enhanced_animations.py`), pause the canvas loop on
   `visibilitychange`, and `animation-play-state: paused` for offscreen
   sections via `IntersectionObserver`; prefer transform/opacity over
   clip-path/background-size where equivalent (1.7).
7. **Truthful storyboard:** generate `animation_protocols.json`'s section text
   from the registry (so names cannot drift) and drop "Production-Ready" for
   any surface without an implementation (1.1, 1.5).
8. **Re-scope the specs** to package only what works (`enhanced_animations`)
   until 1 lands (1.8).
9. **Keep the two shims** — they follow the deprecation-shim pattern exactly;
   schedule their removal for the release after 1.

## 3. The one-line verdict

The animation "protocols" are **one working library (`enhanced_animations.py`),
one broken catalog, one import-mutating legacy renderer, and two vocabularies
that don't meet** — the fix is consolidation into a single validated registry,
not more animations.

---

## 4. Stack gaps + candidate OSS (research 2026-09-24)

What we are missing for our animation purposes, measured against what we have,
with candidates from a 2026-09-24 web survey. Order is priority.

### 4.1 A scene clock / timeline engine (the biggest gap)

We render video by capturing HTML in Puppeteer and encoding frames (CAIN
standard), but nothing ties animations to a **seekable timeline**. Storyboard
text says `fade_in` at some second; the CSS runs on wall-clock `animation`
duration; the recorder captures whenever. There is no `t`.

Candidates:

- **GSAP (gsap.com)** — as of the Webflow acquisition it is **100% free for
everyone**, including the formerly-paid ScrollTrigger/Flip/Text plugins.
`timeline.pause(t)` is a deterministic seek: the right primitive for frame
capture (seek t -> screenshot -> next frame).
- **anime.js v4 (animejs.com)** — MIT, lightweight, timeline + scroll triggers;
enough if we only need sequencing.
- **Motion (motion.dev)** — MIT, WAAPI-based, hardware-accelerated scroll
themselves advertise against GSAP.

Recommendation: **don't take a dependency for the registry (1) — take one for
the clock.** A 30-line `window.__CAIN_TIME__` driver using the Web Animations
API (`animation.currentTime = t`) removes the need for any library in the
capture path; GSAP earns its place only for the scroll/interactive surfaces.

### 4.2 Scroll-driven effects — native CSS first, JS fallback

CSS scroll-driven animations (`animation-timeline: scroll()/view()`) tie
`@keyframes` to scroll progress with no JS (Smashing Magazine 2024-12;
Chrome's own performance case study shows it beats scroll-listener JS because
it runs on the compositor). Chrome/Edge are solid; Firefox/Safari support is
still rolling out (the community's standing advice is check caniuse and ship
a fallback — GSAP ScrollTrigger or the `scroll-timeline` polyfill).

### 4.3 Glassmorphism — it's a recipe, not a library

The effect is ~50 lines we can own: `backdrop-filter: blur() saturate()` +
`rgba()` pane + 1px light border + layered shadow. The 2026 trend everyone
is cloning is Apple's **Liquid Glass**, which adds an SVG
`feTurbulence`/`feDisplacementMap` refraction layer (freeFrontend snippet
galleries and several MIT React kits implement exactly this). What we're
missing is the boring parts, not the effect:

1. **`-webkit-backdrop-filter` + a non-blur fallback** (solid rgba pane) for
   engines without it.
2. **A contrast scrim** — glass on busy backgrounds breaks WCAG text contrast
   (setproduct's 2026 comparison calls this out as the way it "breaks").
3. **Capture cost** — `backdrop-filter` over video is GPU work; in headless
   Chrome it software-rasterizes and screenshots can differ from the live
   page. Pin the rendering mode in the CAIN recorder before designing on it.
4. **Reduced-motion** for any animated glass sheen.

So: vendor a `glass.css` + one SVG filter. Don't adopt FlyonUI/Tailwind for
this — our templates are plain HTML/CSS.

### 4.4 HTML5 vs CSS for a scrolling .mp4 — it's a false dichotomy

They answer different halves, and neither can do the other's job:

- **CSS cannot play, decode, or scrub video.** There is no CSS property that
  drives `currentTime`. If the .mp4 must scroll/scrub with the page, the
  playback layer is the HTML5 `<video>` element and the scrub is JS
  (`requestAnimationFrame` + `video.currentTime`, ideally with
  `requestVideoFrameCallback` for frame-accurate paint).
- **CSS does the motion, not the media.** Parallax/translate of the video
  pane, fades, sticky pinning — all CSS transforms on the compositor,
  cheaper and smoother than JS layout animation.
- **For scrubbing mp4s, encode dense keyframes** (`-g 15` or all-intra):
  seeking between sparse keyframes forces full decode chains and the scrub
  stutters. This is an ffmpeg setting, not an HTML/CSS choice.
- **Our real path is the inverse**: HTML -> frames -> .mp4 (CAIN). There the
  answer is "neither": drive a seekable timeline (4.1), capture in Puppeteer,
  encode HEVC CRF 26-28 per the CAIN standard. Nothing to scroll.

**Bottom line:** `<video>` for playing video, CSS for moving it, JS only for
the scroll->`currentTime` bridge — and for our pipeline, a deterministic scene
clock instead of all three.

### 4.5 Gap checklist (what to actually build)

1. Validated `AnimationDef` registry + `generate_css()` as sole emitter (the 9
   improvements above; kills the phantom/broken-catalog defects).
2. Scene clock (`__CAIN_TIME__` / WAAPI seek) shared by storyboard, templates,
   and the recorder.
3. Dense-keyframe scrub encoding + `requestVideoFrameCallback` where we do
   ship scroll-scrub video.
4. Vendored `glass.css` + SVG refraction filter + scrim + fallback.
5. `prefers-reduced-motion` + visibility pausing everywhere (audit defect 7).
6. The two registry tests (every name resolves; every `animation:` has its
   `@keyframes`) as permanent guards.
