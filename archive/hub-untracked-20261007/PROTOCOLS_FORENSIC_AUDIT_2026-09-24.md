# Protocol Families — Forensic Audit (2026-09-24)

**Scope:** the non-animation protocol families — **CAIN** (psychoanalysis video
pipeline), **emotional emoji** (`emoji_maker`), and the remainder
(`VIDEO_GENERATION_PROTOCOL`, `hydra_protocols.py`, `AssistantLogProtocol(+_Enhanced)`,
`MEMORY_PROTOCOL.md`, `PROTOCOL_VIOLATIONS.md`). Companion to
`ANIMATION_PROTOCOLS_AUDIT_2026-09-24.md`; same method (every claim measured
against the thing it describes, file:line cited).

**Contract of record for CAIN:** the `azazael-cain-pipeline` skill (Puppeteer
capture, inject → record → encode, "CRF 23, medium, High profile, B-frames=2",
5.0 WPS rAF scroll, template `complete_remorse_analysis_cain_optimized.html`).

---

## 1. CAIN — the pipeline vs its own standard

| # | Finding | Evidence |
|---|---|---|
| 1.1 | **Three template identities; the documented one does not exist.** The skill names `complete_remorse_analysis_cain_optimized.html` (191KB) as input — absent from the tree. `complete_remorse_analysis_cain.html` (195KB, May 28) exists but nothing reads it. The live injector reads a third file. | `inject_session_cain.py:25` → `SESSION_TEMPLATE/templates/output_cain.html` (222KB, Jun 5) |
| 1.2 | **Recorder deviates from the CAIN standard.** Documented: "CRF 23, medium preset, **High profile, B-frames=2**". Actual config sets CRF/preset/pixfmt/**bitrate 4000**/fps — no profile, no B-frames. That is the LESSON #01 hazard (puppeteer-screen-recorder defaults to Constrained Baseline) left unguarded, and CRF + bitrate set together is ambiguous. | `record_session_cain.js:65-71` |
| 1.3 | **The full CAIN config exists — in the demo, not the production recorder.** `cain_video_pipeline_demo.py` generates recorder scripts with High profile / CRF 23 / GOP 250 / B-frames 2. The standard is implemented once and used by a demo. | `scripts/cain_video_pipeline_demo.py:187-244` |
| 1.4 | **Undocumented 6× recorder variant.** `record_session_cain_fast.js` differs from the contract recorder only by `WORDS_PER_SECOND 30.0` (vs 5.0) + 60s floor. Two recorders, one contract; 30 WPS makes the report unreadable. | diff `record_session_cain.js` vs `_fast.js` lines 59-60 |
| 1.5 | **Hardcoded machine paths.** Page loads `file:///C:/Users/clint/azazael/src/CODEX/CAIN_injected.html`; output goes to `C:/Users/clint/Desktop/CAIN_session_final.mp4` — outside the project, on one machine. | `record_session_cain.js:39,63` |
| 1.6 | **Stale duplicate output.** `CAIN_injected.html` exists twice with different bytes/dates (root 221,762 B Jun 5 vs `src/CODEX/` 225,423 B Jun 6). The recorder uses only the src copy; the root copy is an orphan. The skill's "Output: CAIN_injected.html (196KB)" matches neither. | ls + sha compare |
| 1.7 | **"Superseded" generator still shipped.** The skill marks `generate_session_cain.py` superseded by injection; 607 lines remain live in-tree. A datestamped generated artifact is committed beside it. | `src/CODEX/generate_session_cain.py`; `src/CODEX/CORE/CAIN_analysis_20260605_110918.html` |
| 1.8 | **"Session-specific injection" is one hardcoded session.** The injector bakes the May 28 / Jun 6 incidents into Python string replacements. A new session means editing source; replacement strings are brittle to template edits. | `inject_session_cain.py:37-167` |
| 1.9 | **The CAIN standard lives in 3 places** (skill, demo docstring, `compress_video.py --profile cain`) — and the skill's Key Files table is already stale (1.1). | — |

## 2. Emotional emoji (`emoji_maker`) — a protocol whose links are all broken

| # | Finding | Evidence |
|---|---|---|
| 2.1 | **Emoji→animation mappings resolve to nothing.** `EmojiDef.animation` values ("bounce", "elasticScale", "shake", "pulse", "drip", "flood", "glitch") match **zero** of `enhanced_animations.ANIMATIONS`' 31 keys (scaleBounce, glowPulse, rainDrop …). Same defect as the animation catalog: names promising CSS that does not exist. "shake" is the same phantom the catalog recommends. | `src/CODEX/CORE/emoji_maker.py:85-100` vs `enhanced_animations.py` keys |
| 2.2 | **The width validator crashes on startup.** `_emoji_mood_probe.py:48` calls `lm.detect_glyph_tier("auto")` on `live_monitor`, but that function lives in `exmachina_live_monitor.py:291`. `AttributeError` at first call — the instrument that arbitrates emoji-vs-terminal-width has never run in its current form. | reproduced: `python scripts/_emoji_mood_probe.py` → traceback |
| 2.3 | **Header drift.** Docstring lists 10 emotions; the `Emotion` enum has 15 (CURIOUS, PLAYFUL, RELIEVED, CONFUSED, PROUD undocumented). | `emoji_maker.py:1-10` vs `:22-38` |
| 2.4 | **The library is disconnected from where emotion surfaces.** The CAIN template's emotional emoji (😰😟📄 "emotion-tag" spans) are hardcoded literals in the injector's replacement strings — `EmojiMaker` is not used there at all. | `inject_session_cain.py:37-167` |
| 2.5 | **A generated staging worm sits unregistered.** `expansion/generated/_staging/gen_EmojiMakerWorm_unknown.py` — one of the 78 `Gen*` files outside the fleet census. | census 2026-09-24 |
| 2.6 | **Tension with the wallboard is unarbitrated.** `live_monitor.py`'s contract is "pure ASCII so cmd codepage never mangles"; the emoji family is the opposite bet. The probe that should settle it (2.2) is broken. | `live_monitor.py:84` |

## 3. The "etc." protocols

| # | Finding | Evidence |
|---|---|---|
| 3.1 | **`VIDEO_GENERATION_PROTOCOL.md` duplicated byte-identical** in `docs/` and `src/CODEX/DOCUMENTATION/` (sha `e4c9a047…` ×2), plus a third `.txt` copy that **differs** (`fc989f27…`). Twins + one divergent sibling — the dupe-drift pattern again. | sha256 compare |
| 3.2 | **`hydra_protocols.py` header is corrupt.** `# coding: utf-8` and the module docstring appear *after* imports — the coding cookie is invalid outside the first two lines, and the "docstring" is a plain expression, so `__doc__` is `None`. `sys` is imported twice. The module's self-documentation is silently dead. | `src/HYDRA/hydra_protocols.py:1-14` |
| 3.3 | **ALP pair divergent and both live.** `AssistantLogProtocol.py` (376 ln) and `AssistantLogProtocol_Enhanced.py` (653 ln, "ADLP v2.0.0") are siblings, not shim+canonical; both consumed (`ADLP_SystemTools`, `FusionHealer`, `health_check_azazael`, `memory_profile`, `ADLP_Test`). | consumer grep |
| 3.4 | `MEMORY_PROTOCOL.md` and `PROTOCOL_VIOLATIONS.md` are documentation-only and structurally sound. Notable: V01 ("Re-interpreting instructions instead of following literally", 10+ repeats) is the same failure shape as 1.1/1.4 — a documented contract diverging from what actually runs. | `PROTOCOL_VIOLATIONS.md:13-17` |

## 4. Cross-cutting verdict

Every family shows the same three failure shapes:

1. **Names that reference implementations that don't exist** — animation
   catalog's generator/recommendations, emoji animation fields, the CAIN
   skill's template name, the probe's API target (1.1, 2.1, 2.2).
2. **Duplicate artifacts that drift** — CAIN_injected ×2, VGP ×3, ALP ×2,
   animation modules ×2 (1.6, 3.1, 3.3).
3. **Documented contracts the production path doesn't follow** — CAIN recorder
   config + the fast variant (1.2, 1.4).

## 5. Suggested improvements (take order)

1. **Fix the two broken instruments first (cheap, high value):**
   `_emoji_mood_probe.py` import fix (or re-export `detect_glyph_tier` from
   `live_monitor`), then run it and record its verdict. Add the meta-rule as a
   test: every probe script must at least import and start — a guard that
   cannot run is worse than no guard.
2. **One CAIN emitter:** generate recorder scripts from
   `cain_video_pipeline_demo.py`'s CAIN-config generator (High profile,
   B-frames=2, GOP 250) and delete the hand-rolled configs; fold
   `record_session_cain_fast.js` into a `--wps` flag on one recorder.
3. **Single template identity:** one constant (imported by injector and
   recorder), delete/relocate the orphan root `CAIN_injected.html`, demote
   `generate_session_cain.py` to a shim or delete it, and update the skill's
   Key Files table to match reality.
4. **Parameterize the session data:** move the incident/replacement content
   into a JSON input (`--session session.json`) so a new session is data, not
   source edits (1.8).
5. **Kill hardcoded paths:** recorder takes input/output as argv/env with
   project-relative defaults (`CORE/paths.py`), never `C:/Users/clint` (1.5).
6. **Name-resolution tests across families:** one test asserting every
   `EmojiDef.animation`, catalog recommendation, and skill-named file resolves
   — the same two tests proposed in the animation audit, extended (2.1, 1.1).
7. **Dedup with shims:** VGP `.txt` generated from `.md` or dropped; the two
   `.md` twins → one canonical + redirect note; declare `AssistantLogProtocol`
   vs `_Enhanced` canonical explicitly (3.1, 3.3).
8. **Fix `hydra_protocols.py` header** (cookie line 1-2, docstring first,
   drop duplicate imports) and correct the emoji header count (2.3, 3.2).
9. **Decide `gen_EmojiMakerWorm_unknown.py`:** register it properly or retire
   it at the next generated-staging sweep (2.5).

## 6. One-line verdict

**CAIN's knowledge is better than its code** (the right config exists in a
demo while the production recorder runs the anti-pattern), **emoji's protocol
is a library of links to nowhere** (mappings to nonexistent animations, a
validator that crashes), and the remaining protocols are the familiar dupe +
stale-header pattern — fix the instruments first, then consolidate.
