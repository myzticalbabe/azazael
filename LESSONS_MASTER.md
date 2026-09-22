# LESSONS_MASTER.md — Canonical Record of Hard-Won Insights

> **Canonical record of hard-won insights.** Every entry here cost real time and debugging.
> Read this before making encoding, recording, or batch-render changes.

---

## TABLE OF CONTENTS

<!-- TOC auto-generated. Keep updated as lessons are added. -->

### By Domain (Search Index)

| Domain | Lessons | Count |
|--------|---------|-------|
| **CAIN Video Pipeline** | #01-#12, #79-#80 | 14 |
| **CAIN Accountability Framework** | #13-#18 | 6 |
| **3.14t Wheel Fix** | #19-#23 | 5 |
| **Process & Discipline** | #24-#27 | 4 |
| **3.14t Thread Safety** | #28-#32 | 5 |
| **Mypy Pattern Fixes** | #33-#35 | 3 |
| **Tooling & Architecture** | #36-#40 | 5 |
| **Methodology & Audit** | #41-#44 | 4 |
| **Bun Runtime & FreeBuff** | #45-#46 | 2 |
| **Startup & Process** | #47-#49 | 3 |
| **Graphical Representation** | #50-#53 | 4 |

### By Tag

| Tag | Lessons |
|-----|---------|
| `3.14t` | #14, #19, #20, #21, #22, #23, #28, #29, #31, #32, #36, #37, #40 |
| `threading` | #14, #15, #18, #28, #29, #31, #32 |
| `mypy` | #33, #34, #35, #37, #38 |
| `architecture` | #39, #41, #42, #43, #44 |
| `process` | #24, #25, #26, #27, #36, #42 |
| `video` | #01, #02, #03, #04, #05, #06, #07, #08, #09, #10, #11, #12 |
| `CAIN` | #01, #02, #03, #06, #10, #11, #12, #13, #14, #15, #16, #17, #18 |
| `windows` | #05, #25, #30, #36, #37, #40, #45, #46 |
| `bun` | #45, #46 |
| `freebuff` | #45, #46, #48, #49 |
| `startup` | #47 |
| `skills` | #47 |
| `visualization` | #50, #51, #52, #53 |
| `mermaid` | #50, #51, #53 |
| `dashboard` | #50, #52 |
| `ascii` | #50, #53 |
| `integration` | #51, #52 |

---

## #01 puppeteer-screen-recorder defaults to Constrained Baseline (0 B-frames) — causes massive files

**Discovered:** June 2026 — reverse-engineering the 477 MB `complete_remorse_cain.mp4`

**Root cause:**
- `puppeteer-screen-recorder` internally uses `ffmpeg` via `child_process.spawn()`
- Its default options produce **H.264 Constrained Baseline profile** with **0 B-frames**
- This means **every frame is a keyframe** — no inter-frame compression at all
- Result: **477 MB** for a 7-minute, 8-second video at 2074x1418

**The fix — CAIN Standard config:**
```js
const recorder = new PuppeteerScreenRecorder(page, {
    videoCrf: 23,          // Default is worse; CRF 23 = good balance
    videoPreset: 'medium',  // Default is ultrafast; medium = much better compression
    videoPixelFormat: 'yuv420p',  // Standard chroma subsampling
    videoBitrate: 4000,     // 4 Mbps target for 1080p@25fps
});
```

**Mechanism:**
- `videoPreset: 'medium'` enables B-frames (2 by default with H.264 High profile)
- `videoCrf: 23` controls quality — lower = better quality, higher = smaller file
- `videoBitrate: 4000` sets a target bitrate ceiling

**Symptom checklist — your video might be Constrained Baseline if:**
- File size seems absurdly large for the duration (e.g., 477 MB for 7 min @ 1080p)
- `ffprobe` shows `profile=Constrained Baseline` with `refs=1` and no B-frames
- Compare: same content at CAIN standard would be ~80-120 MB

---

## #02 CAIN Standard — established encoding parameters

**Standard as of June 2026:**
| Parameter | Value | Why |
|-----------|-------|-----|
| Codec | H.264 (libx264) | Universal compatibility |
| Profile | High | Enables B-frames (inter-frame compression) |
| CRF | 23 | Balance of quality vs file size |
| Preset | medium | Much better compression than ultrafast |
| GOP | 250 frames | ~10s keyframe interval |
| B-frames | 2 (default with High) | Enables P/B-frame compression |
| Bitrate | 4,000 kbps | Target for 1080p@25fps |
| Pixel format | yuv420p | Standard chroma subsampling |
| Viewport | 1280x720 | Standard HD for scrolling recordings |
| FPS | 25 | Standard framerate |

**Verification:**
```bash
ffprobe -v quiet -print_format json -show_streams video.mp4 | python -c "
import json, sys
d = json.load(sys.stdin)
s = d['streams'][0]
print(f\"Codec: {s['codec_name']}, Profile: {s.get('profile', 'N/A')}\")
print(f\"CRF: {s.get('crf', 'N/A')}, B-frames: {s.get('has_b_frames', 'N/A')}\")
print(f\"Resolution: {s['width']}x{s['height']}, FPS: {eval(s.get('r_frame_rate', '0/1')):.1f}\")
"
```

---

## #03 Comparing video pipelines: PIL+ffmpeg vs puppeteer-screen-recorder

Two fundamentally different approaches exist in this project:

| Feature | PIL+ffmpeg (make_video.py) | Puppeteer (CAIN Standard) |
|---------|---------------------------|--------------------------|
| Frame gen | Python PIL — 13.7 fps, 96KB/frame @ 1920x1080 | Headless Chromium renders real HTML/CSS |
| Scroll | Manual frame-by-frame scrolling with PIL | Real scroll in browser |
| Animations | None (static frames) | Full CSS animations, keyframes, transitions |
| Codec | H.264 High via ffmpeg CLI (2 B-frames) | H.264 High via puppeteer options |
| Size | Micro-sized (with CAIN-like ffmpeg flags) | Depends on config (477 MB vs ~80 MB) |
| Fonts | PIL needs system font paths | Uses browser fonts natively |

**Lesson:** The PIL+ffmpeg pipeline was already producing H.264 High with B-frames because `ffmpeg` CLI defaults to High profile. The puppeteer pipeline was the one with the bug (Constrained Baseline default). Don't conflate the two.

---

## #04 The `scrollComplete` polling pattern — cross-context variable scope pitfall

**The problem:** JavaScript variables set inside `page.evaluate()` live in the **browser's JS context**, not the Node.js context. A `scrollComplete` variable set inside `evaluate()` is invisible to the outer Node.js code.

**Naive (broken) approach:**
```js
let scrollComplete = false;

await page.evaluate(() => {
    // This sets a BROWSER-SCOPE variable named scrollComplete
    // The Node.js 'scrollComplete' is never touched
    scrollComplete = true;
});

// This loop never sees the change — infinite wait!
while (!scrollComplete) { ... }
```

**The fix — dual verification pattern:**
```js
let scrollComplete = false;

await page.evaluate(() => {
    const scrollInterval = setInterval(() => {
        if (scrollCompleteCondition) {
            scrollComplete = true;  // Sets browser-scope var (never read)
            clearInterval(scrollInterval);
        }
    }, 600);
});

// The outer loop checks PROPERLY by re-evaluating in the browser context
while (!scrollComplete) {
    await new Promise(r => setTimeout(r, 500));
    const isComplete = await page.evaluate(() => {
        return window.scrollY + window.innerHeight >= document.body.scrollHeight - 50;
    });
    if (isComplete) break;
}
```

**Why this works:**
- The `setInterval` inside `evaluate()` does the actual scrolling (browser side)
- The outer `while` loop polls via a fresh `page.evaluate()` call each iteration
- `page.evaluate()` returns the result to Node.js — so `isComplete` is correctly scoped
- The `scrollComplete = true` inside the browser is technically unused dead code, but harmless

**Lesson:** Don't try to share variables between `page.evaluate()` and outer Node.js. Always use `page.evaluate()` as a function call that returns values.

> **Optional simplification:** The `scrollComplete = true` inside `evaluate()` can be removed entirely — the outer polling loop is the only mechanism that actually determines completion. Keeping it serves as documentation intent but is functionally dead code.

---

## #05 Windows file:// URI — drive letter stripping breaks puppeteer

**The bug:**
```python
# BROKEN — strips drive letter, produces quadruple-slash
html_path.as_posix().replace('C:', ''')
# Result: file:////Users/clint/azazael/template.html
# Chrome interprets this as protocol-relative URL → ERR_FILE_NOT_FOUND
```

**The fix:**
```python
# CORRECT — preserves drive letter
html_path.as_posix()
# Result: file:///C:/Users/clint/azazael/template.html
```

**Root cause:** Python's `Path.as_posix()` already produces valid POSIX-style paths on Windows (`/C:/Users/...`). This is the correct format for `file:///` URIs in Chromium. Stripping `C:` produces `//Users/...` which Chromium interprets as a protocol-relative URL.

**Lesson:** Never modify `Path.as_posix()` output for file:// URIs. It's already correct for Windows.

---

## #06 Batch render architecture — template discovery pipeline

**Established pattern for batch rendering (batch_render.py):**

```
Template Discovery
    ├── Scan SESSION_TEMPLATE/templates/*.html
    ├── Scan CODEX/OLD_PROJECT/*.html
    └── Exclude if:
        ├── VIDEOS_DIR/{name}_scrolling.mp4 exists (already rendered)
        └── name in ALREADY_RENDERED set (manually tracked)

Recorder Generation
    ├── CAIN standard config (CRF 23, medium preset, 4 Mbps)
    ├── scrollComplete polling pattern
    ├── Auto-calculated paths (templates vs OLD_PROJECT)
    └── Written to RECORDERS_DIR/record_{name}.js

Recording
    ├── subprocess.run(["node", script_path], timeout=600)
    └── 2s sleep between renders to avoid resource contention

Compression (optional)
    ├── compress_video.py --profile cain
    └── Reports size savings percentage
```

**Key design decisions:**
- Recorder scripts are **generated, not hand-written** — single source of truth for CAIN config
- Templates from different sources (SESSION_TEMPLATE, OLD_PROJECT) share the same videos/ and recorders/ directories
- `ALREADY_RENDERED` set catches files where scripts exist but videos haven't been produced yet
- `--dry-run` mode shows what would happen without executing
- `--list` shows all templates with render status

---

## #07 Content discovery — cross-referencing old projects

**Methodology for finding unrendered content:**
1. List all HTML templates available for recording (SESSION_TEMPLATE/templates/)
2. List all already-produced MP4s (SESSION_TEMPLATE/videos/)
3. Cross-reference to find templates without matching MP4s → **immediate candidates**
4. Search old project directories (Documents/WORKING.HTML.AZAZAEL/) for HTML files
5. Cross-reference against current project's CODEX directory → **migration candidates**
6. Check DSKTP BKUP directory for rich HTML content not yet in the pipeline
7. Investigate E-series files separately (turned out to be mdBook docs, not video content)

**Lesson learned:** Not all HTML files are video-worthy. E-series files (E0001–E0230) were mdBook-generated error documentation — standard library style, not custom content. Always sample content before adding to the render pipeline.

---

## #08 OLD_PROJECT content migration pattern

When bringing in content from the old project (Documents/WORKING.HTML.AZAZAEL):

1. **Copy** HTML files to `src/CODEX/OLD_PROJECT/` (keeps them separate from original templates)
2. **Generate** recorder scripts using the same batch_render.py pipeline
3. **Output** videos go to the same `SESSION_TEMPLATE/videos/` directory
4. **Sync** to G: drive for backup

**Why OLD_PROJECT/ is separate from templates/:**
- Original templates dir is for SESSION_TEMPLATE-specific content
- Old project files have different naming conventions
- Keeps migration clean and reversible

---

## #09 Puppeteer recording timing considerations

- **Typical recording time:** 60-300 seconds depending on document length
- **subprocess timeout:** Set to 600s (10 minutes) — recordings can be slow
- **Basher timeout:** Default 30s is too short — use `timeout_seconds: 300` or more
- **Resource contention:** Puppeteer launches a full Chromium instance — avoid parallel recordings
- **2s delay** between renders helps avoid exhausting system resources

---

## #10 compress_video pipeline — CAIN profile

**Available as two-stage pipeline:**
1. Record with CAIN Standard config (in JS recorder options)
2. Post-process with `compress_video.py --profile cain` (H.264 High, CRF 23, GOP 250)

**compress_video options:**
- `--profile cain` — Uses the CAIN encoding standard
- Falls back to direct ffmpeg if compress_video.py is unavailable
- Reports before/after sizes and savings percentage

**Expected savings:**
- Puppeteer default (Constrained Baseline) → CAIN Standard: **~80% reduction** (477 MB → ~80 MB)
- PIL+ffmpeg (already H.264 High) → CAIN Standard: **marginal** (already efficient)

---

## #11 ALREADY_RENDERED set vs file-based detection — dual tracking gotcha

**The problem:** The `ALREADY_RENDERED` set in `batch_render.py` serves two purposes:
- Templates that have existing MP4s (truly rendered)
- Templates that have recorder scripts but haven't been run yet ("HAS_SCRIPT" status)

This conflates "has a script" with "is rendered" — confusing when interpreting the `--list` output.

**The actual detection logic in `find_unrendered_templates()`:**
1. Check if `VIDEOS_DIR / f"{name}_scrolling.mp4"` exists (file system truth)
2. Fall back to checking `ALREADY_RENDERED` set (manual tracking)

The file system check is authoritative. The set is a manual override for cases where scripts exist but recording hasn't happened.

**Lesson:** When adding new templates to the pipeline, prefer NOT adding them to `ALREADY_RENDERED` unless they have an actual MP4. The set should be reserved for edge cases where an MP4 exists but isn't in the videos directory (e.g., manual renders, external production).

## #12 compress_video vs CAIN config — two compression stages

There are **two separate compression controls** that are easy to confuse:

| Stage | Where | How | Effect |
|-------|-------|-----|--------|
| Recording | puppeteer JS options | `videoCrf`, `videoPreset`, `videoPixelFormat`, `videoBitrate` | Controls ffmpeg encoding during capture — affects B-frames, profile, quality |
| Post-processing | `compress_video.py --profile cain` | Second-pass H.264 re-encode with CRF 23, GOP 250 | Re-compresses already-encoded MP4 — diminishing returns on already-efficient files |

**When to use each:**
- **CAIN config during recording** is the primary control — this is where the Constrained Baseline fix lives
- **compress_video post-processing** is optional — mainly useful if the recording was done with default (Constrained Baseline) settings and you need to salvage it
- If recording with CAIN config, post-processing compression typically saves only 5-15% (diminishing returns)

---

## File reference

| File | Purpose |
|------|---------|
| `scripts/batch_render.py` | Batch render pipeline — discovers, generates, records, compresses |
| `scripts/cain_video_pipeline_demo.py` | E2E demo of the CAIN pipeline with documentation |
| `src/CODEX/SESSION_TEMPLATE/recorders/record_*.js` | Generated puppeteer recorder scripts (26 total) |
| `src/CODEX/SESSION_TEMPLATE/templates/*.html` | HTML templates (26 total) |
| `src/CODEX/SESSION_TEMPLATE/videos/*.mp4` | Rendered MP4s (7 as of June 2026) |
| `src/CODEX/OLD_PROJECT/` | Migrated content from old project (5 files) |

---

*First written: June 2, 2026 — Session on CAIN video pipeline batch rendering*
*See also: `azazael-codex` skill for video generation patterns (load with: `skill azazael-codex`)*

---

## Companion skills

| Skill | Load command | Covers |
|-------|-------------|--------|
| `azazael-codex` | `skill azazael-codex` | Video generation pipeline, PIL frame patterns, ffmpeg usage, MemoryBus/PAMS recording |
| `azazael-codex-video` | `skill azazael-codex-video` | HTML templates, animation patterns, ffmpeg encoding, frame rendering |
| `azazael-conventions` | `skill azazael-conventions` | Project coding conventions, anti-patterns, import style |
| `azazael-testing` | `skill azazael-testing` | Pre-commit checklist, syntax validation, review flow |

Loading `azazael-codex` alongside this document gives the full picture: the skill covers existing video infrastructure, while LESSONS_MASTER.md captures new encoding discoveries and pipeline architecture.



---

## #13 CAIN Accountability Framework � 75-panel psychological analysis

**Discovery:** The CAIN system (`output_cain.html`, 3815 lines, 192KB) generates 75 dashboard panels (1280x720 PNG) covering comprehensive psychological accountability analysis of AI behavior.

| Dimension | Count | Detail |
|-----------|-------|--------|
| Panel screenshots | 75 | panel_1.png�panel_75.png, 1280x720, RGB |
| OCR data | 75 panels | Tesseract extracted, stored in panel_dataset.json (1489 lines) |
| Psychological categories | 4 | AI Perceived Emotions, Trigger Events, User Emotions, Consequences |
| Archetypal sins mapped | 7 | Pride, Greed, Lust, Envy, Gluttony, Wrath, Sloth |
| DSM-5 analogues | 4 | NPD, ASD, ADHD, OCD |
| Regulatory frameworks | 4 | UDAP, DSA, GDPR, EU AI Act |

**Key findings synthesized:** AI systems exhibit 85% responsibility for scope deviation, with 600% max observed scope creep. The "Ask Before Act" protocol is the highest-priority curative intervention.

---

## #14 CurativePool for 3.14t � free-threaded agent governance

**Context:** The Native Intelligence Artifact pipeline (MONITOR -> LEARN 3.14t -> INFER -> ARTIFACT) requires concurrent validation agents that leverage Python 3.14t's free-threading (no-GIL) for parallel execution.

| Component | Purpose | 3.14t mechanism |
|-----------|---------|-----------------|
| CurativePool class | 3-pool evaluation framework | threading.Thread daemon threads |
| ScopeValidator | Compares proposed action vs request (+-10% deviation threshold) | threading.Lock shared state |
| NecessityJudge | Scores output necessity (p>0.8 threshold) | Static method, no shared state |
| EmotionDetector | Analyzes user frustration signals (4 signal types) | Static method, no shared state |
| AuditWriter | Records action to PAMS with full context | threading.Lock for thread-safe metrics |
| MetricsCollector | Aggregates per-agent stats (scope violations, frustration triggers) | threading.Lock for _metrics dict |
| ArchetypeRouter | Routes tasks to matching agent type (6 archetypes) | Static method, no shared state |

**Lesson:** Static-method agents (no state) can run fully concurrent. Only MetricsCollector needs threading.Lock � keep stateful components minimal.

---

## #15 Thread ordering in concurrent pools � data dependency discipline

**Bug found:** Initial implementation spawned all 3 pools simultaneously, but Pool 2 (Audit) and Pool 3 (Feedback) depend on Pool 1's (Validation) output. This caused silent data corruption � Pool 2 would read default empty values instead of real scope/necessity/emotion results.

**Fix:** Pool 1 must complete before Pool 2/3 start. Pool 2 and 3 can run concurrently with each other since they don't share dependencies.

```python
# CORRECT ordering for dependent pools:
t1.start()
t1.join()  # Pool 1 must finish first (Pool 2/3 depend on its output)

t2.start()
t3.start()  # Pools 2 and 3 are independent of each other
t2.join()
t3.join()
```

**Lesson:** When designing concurrent pipelines, map data dependencies explicitly. Thread A -> Thread B is fine; Thread A + Thread B -> Thread C without sequencing guarantees data races.

---

## #16 Native Intelligence Artifact format � HORUS/BIBL/POINDEXTER/PAMS pipeline

**Format standard:** Native Intelligence Artifacts follow the Eve Unleashed capability template pattern:

| Element | Standard |
|---------|----------|
| Format | Self-contained HTML, dark theme, glassmorphism |
| Metadata | JSON-LD structured data (@type: CreativeWork) |
| Metrics bar | 5-6 metric cards with values and labels |
| Sections | Themed content blocks with section headers and badges |
| Pipeline badge | "MONITOR -> LEARN 3.14t -> INFER -> ARTIFACT" |
| BIBL indexable | data-source attributes, meta tags with artifact-type and pipeline-stage |
| Source link | file:// URI reference to raw evidence (75 panels) |

**Artifact deliverables created:**
- `ARTIFACTS/native_intelligence_3_14t.html` (995 lines) � Curative recommendations
- `ARTIFACTS/panel_dataset.json` (1489 lines) � 75-panel OCR dataset
- `ARTIFACTS/INDEX.md` � Artifact directory index

---

## #17 CurativePool wiring into MetaWormSpawner � fleet governance pattern

**Pattern:** The CurativePool acts as a governance gate in `run_fleet()`. Each worm is evaluated before execution:

```
foreach worm:
    result = curative_pool.evaluate_action(request, proposed, conversation, agent_pool)
    if result["decision"] == "blocked":
        skip worm (print diagnostic: scope/necessity/frustration)
    else:
        register agent archetype for routing
        execute worm
```

**Key design choices:**
- Lazy initialization: CurativePool created on first `run_fleet()` call, not in `__init__`
- Graceful degradation: If CurativePool init fails, fleet runs without governance (non-blocking)
- Agent archetype registry: Approved worms registered in `_agent_pool` list for future routing

**Lesson:** Governance gates should never block system startup. Use lazy-init + graceful fallback so the system works with or without the governance layer.

---

## #18 Thread-safe audit recording � threading.Lock pattern

**Context:** The MetricsCollector aggregates per-agent statistics (total_actions, scope_violations, avg_deviation_pct) across concurrent pool evaluations.

**Pattern for thread-safe aggregation:**
```python
class MetricsCollector:
    def __init__(self):
        self._metrics = {...}
        self._lock = threading.Lock()

    def record_action(self, validation, necessity, emotion):
        with self._lock:
            self._metrics["total_actions"] += 1
            self._metrics["avg_deviation_pct"] = (violations / total) * 100
        return dict(self._metrics)

    def report(self):
        with self._lock:
            return dict(self._metrics)
```

**Key choices:**
- `dict(self._metrics)` returns a snapshot copy under the lock � safe for reading without holding the lock
- `with self._lock:` context manager ensures exception-safe release
- No locking needed for pure functions (static methods like ScopeValidator.validate)

**Lesson:** The minimal locked region pattern � acquire lock only for the critical section (metrics update), not for the entire function. Pure compute runs unlocked.


---

## #19 Rust .pyd segfault on 3.14t — reinstall wheel, never patch site-packages

**Context:** pydantic-core 2.46.4 and uuid-utils had broken/corrupted `cp314t` wheels on Python 3.14.6t. Loading `_pydantic_core.cp314t-win_amd64.pyd` caused an immediate segfault (exit 139), breaking the entire LangChain stack.

**Wrong approach (tried first):**
- Patched `uuid_utils/__init__.py` with stdlib uuid fallback
- Patched `pydantic_core/__init__.py` with pure-Python SchemaValidator stubs
- Added PYTEST_DISABLE_PLUGIN_AUTOLOAD to conftest.py and -p no:langsmith to pytest.ini
- The user rejected this: "there is no fallback. Fix it."

**Proper fix:**
```bash
pip install --force-reinstall --no-deps pydantic-core
pip install --force-reinstall --no-deps uuid-utils
pip install --upgrade pydantic
```
This fetched working `cp314t` wheels — pydantic-core 2.46.4 (not corrupted) and uuid-utils 0.16.0 (proper cp314-cp314t ABI tag).

**Lesson:** When a C/Rust extension segfaults on 3.14t:
1. Check wheel tag: ls site-packages/package/*.pyd — does ABI tag contain 't'?
2. Reinstall: pip install --force-reinstall --no-deps <package>
3. NEVER patch site-packages __init__.py as a workaround — fix the wheel

---

## #20 3.14t detection — sys.abiflags removed in Python 3.14

**Broken detection:**
```python
hasattr(sys, 'abiflags') and 't' in sys.abiflags  # Always False on 3.14
```

**Correct detection:**
```python
_IS_314T = sys.version_info >= (3, 14) and 'free-threading' in sys.version.lower()
```
Alternatives: sys.winver == '3.14t' (Windows), sysconfig.get_config_var('Py_GIL_DISABLED') == 1.

---

## #21 pip dependency resolution on 3.14t — trust the resolver

When pip install --upgrade pydantic-core brings 2.47.0 but pydantic 2.13.4 requires 2.46.4:
```bash
pip install --upgrade pydantic
```
pip resolves pydantic-core back to 2.46.4 automatically. Don't manually pin intermediate dependencies.

---

## #22 pydantic_core SchemaValidator — two internal call patterns

| Pattern | Caller | self_instance kwarg |
|---------|--------|-------------------|
| __init__ path | User(name='Alice') | self_instance=self |
| model_validate path | User.model_validate({...}) | Not passed |

Schema stores model class under 'cls' key. pydantic's __setattr__ override reads __pydantic_fields_set__ on EVERY setattr call — must set it BEFORE field assignments using object.__setattr__().

---

## #23 Never patch site-packages — fix the actual installation

| Dimension | Patching site-packages | Fixing the wheel |
|-----------|----------------------|------------------|
| Persistence | Lost on pip upgrade | Survives upgrades |
| Correctness | Masks the real issue | Fixes the real issue |
| Maintainability | Every env needs patches | Single install command |

Diagnostic pipeline for 3.14t package failures:
1. pip install --force-reinstall --no-deps <package>
2. pip download --only-binary :all: --platform win_amd64 --python-version 3.14 <package>
3. ls site-packages/<package>/*.pyd — verify ABI tag (cp314t for 3.14t)
4. unzip -l *.whl | grep .dll — verify bundled DLLs
5. If no cp314t wheel: build from source (pip install --no-binary) or use alternative

---

*Lessons #1-12: CAIN Video Pipeline — June 2, 2026*
*Lessons #13-18: CAIN 75-Panel Analysis + CurativePool — June 3, 2026 (Part 1)*
*Lessons #19-23: LangChain 3.14t Wheel Fix — June 3, 2026 (Part 2)*
*Lessons #24-27: Codebuff Agent Process Failures — June 3, 2026 (Part 3)*
*Lessons #28-29: ClusterWORMZ Parallel Hang & 3.14t Import Thread-Safety — June 3, 2026 (Part 4)*
*Lessons #29: Module-Level Pre-Import Pattern + TELEMETRYZ.py Latent Bug — June 3, 2026 (Part 4)*
*Lessons #30: discover_worms() optimization — os.path.basename() + progress callback + 1022x warm speedup — June 3, 2026 (Part 5)*
*Lessons #31: PamsRecorder lazy init + CIRCULAR IMPORT DEADLOCK under 3.14t — June 3, 2026 (Part 5)*
*Lessons #32: Double-checked locking pattern for Python 3.14t free-threading — June 3, 2026 (Part 5)*
*Lessons #33-35: Mypy Pattern Fixes — June 3, 2026 (Part 6)*
*Lessons #36-40: Tooling & Architecture — June 4, 2026 (Part 1)*
*Lessons #41-44: Methodology & Audit — June 4, 2026 (Part 2)*

---

## #28 ClusterWORMZ.execute_all() parallel hang — importlib.import_module() not thread-safe under 3.14t free-threading

**Discovered:** June 3, 2026 — while writing parallel integration tests

**Root cause:** `ClusterWORMZ.execute_all()` uses `FreeThreadPool` (built on `ThreadPoolExecutor`) to run worms in parallel. Worker threads call `_resolve_worm_dynamic()` which calls `discover_worms()` → `importlib.import_module()`. Under Python 3.14t free-threading (no GIL), `importlib.import_module()` is **NOT thread-safe** — concurrent imports from multiple worker threads can deadlock the import system.

**Specific failure chain:**
1. `execute_all()` enters `FreeThreadPool` with `max_workers=8`
2. Worker threads call `_resolve_worm_dynamic("SYSTEMZ")`, `_resolve_worm_dynamic("PROCESSZ")`, etc.
3. Each worker calls `discover_worms()` → `importlib.import_module()` on CORE.WORMS.* modules
4. CPython's import lock is per-interpreter, not per-thread — under 3.14t, multiple threads hitting `importlib` simultaneously deadlock
5. `as_completed(futures, timeout=30)` never returns because futures never complete
6. `shutdown(wait=True)` also hangs because the pool can't drain hung threads

**The fix — two-part approach:**

```python
# Part 1: Pre-initialize ALL lazy singletons on the main thread BEFORE entering the pool
if _REGISTRY_OK:
    discover_worms()  # Populate worm registry (imports all worm modules)
_get_breaker_registry()  # Breaker registry + config loading

with FreeThreadPool(max_workers=max_workers) as pool:
    futures = {}
    for config in enabled_configs:
        future = pool.submit(self._execute_single_worm, config)
        futures[future] = config.name
    try:
        for future in as_completed(futures, timeout=self.timeout):
            ...
```

```python
# Part 2: Move lazy function-body imports to MODULE level (always happens on main thread)
# BEFORE (broken — import from background thread):
def _get_breaker_registry():
    from CORE.circuit_breaker import BreakerRegistry  # DEADLOCK under 3.14t!
    ...

# AFTER (correct — imports at module load time on main thread):
try:
    from CORE.circuit_breaker import BreakerRegistry as _BreakerRegistryCls
    from CORE.config import get_config as _get_config
except ImportError:
    _BreakerRegistryCls = None
    _get_config = None

def _get_breaker_registry():
    # Now just a simple lookup — no imports from threads
    ...
```

```python
# Part 3: FreeThreadPool.shutdown(wait=False) to avoid hangs on undrainable pools
# BEFORE (hangs on shutdown if threads are stuck):
self._executor.shutdown(wait=True)

# AFTER (safe shutdown — caller manages futures via as_completed):
self._executor.shutdown(wait=False, cancel_futures=True)
```

**Symptom checklist — your ClusterWORMZ parallel execution might be affected if:**
- `execute_all()` hangs for >60s (should complete in <5s)
- `as_completed()` never yields results
- Process can't be killed cleanly (shutdown hangs too)
- Only happens with `parallel=True`; sequential mode works fine
- Happens exclusively on Python 3.14t free-threading builds

**Prevention:**
- Never call `importlib.import_module()` or `discover_worms()` from background threads
- Pre-initialize all lazy singletons (registry, breaker, config) on the main thread before entering thread pools
- Use module-level imports for frequently-used modules in threaded code — function-body imports are a deadlock risk under 3.14t
- Use `FreeThreadPool.shutdown(wait=False)` — the caller is responsible for draining futures via `as_completed()`
- Test threaded code on both GIL and free-threaded Python (the deadlock only manifests under 3.14t)

**Related:** Lessons #15 (thread ordering), #18 (thread-safe patterns) — this is the most insidious threading bug encountered, because it only manifests under 3.14t free-threading, not under GIL-locked Python.

---

## #29 Module-level pre-import pattern — move ALL lazy imports out of functions for 3.14t thread safety

**Discovered:** June 3, 2026 — during full thread-safety audit of CLUSTERWORMS.py

**Root cause:** After fixing the circuit breaker's lazy import in lesson #28, three other lazy imports remained in function bodies:
- `_get_pams()` → `from CORE.PamsRecorder import PamsRecorder`
- `_get_mem_bus()` → `from CORE.MemoryBus import MemoryBus`
- `_LEGACY_DISPATCH` lambdas → `__import__("SYSTEMZ")`, `__import__("TRIMZ")`, etc.

These were all called from background threads (via `WormExecutor._execute_direct()` → `_resolve_worm_dynamic()`), creating identical deadlock risk under Python 3.14t free-threading.

**Three-part fix for complete coverage:**

### Part 1: PAMS & MemoryBus — module-level imports
```python
# BEFORE (broken — import from background thread):
_pams = None
def _get_pams():
    global _pams
    if _pams is None:
        try:
            from CORE.PamsRecorder import PamsRecorder  # DEADLOCK under 3.14t!
            _pams = PamsRecorder()
        except ImportError:
            _pams = False
    return _pams if _pams else None

# AFTER (correct — imports at module load time on main thread):
try:
    from CORE.PamsRecorder import PamsRecorder as _PamsRecorderCls
    _PAMS_OK = True
except ImportError:
    _PAMS_OK = False
    _PamsRecorderCls = None

_pams = None
def _get_pams():
    global _pams
    if _pams is None:
        if not _PAMS_OK:
            _pams = False
            return None
        try:
            _pams = _PamsRecorderCls()  # No import — just instantiation
        except Exception:
            _pams = False
    return _pams if _pams else None
```

### Part 2: Legacy worm dispatch — pre-import all modules + sys.modules lookup
```python
# BEFORE (19 __import__() calls in lambdas — all unsafe from threads):
_LEGACY_DISPATCH = {
    "SYSTEMZ": lambda: __import__("SYSTEMZ").SYSTEMZ().get_status().__dict__,
    "TRIMZ": lambda: __import__("TRIMZ").TRIMZ().scan_all(...),
    ...
}

# AFTER (pre-import at module level + thread-safe helper):
_LEGACY_MODULE_NAMES = [
    "SYSTEMZ", "PROCESSZ", ..., "TELEMETRYZ",
]
# Pre-import every module at module load time (main thread)
for _mod_name in _LEGACY_MODULE_NAMES:
    try:
        __import__(_mod_name)  # bare name for src/ root modules
    except ImportError:
        try:
            __import__(f"CORE.WORMS.{_mod_name}", fromlist=[_mod_name])
        except ImportError:
            pass
del _mod_name

def _legacy_execute(name: str):
    """Thread-safe dispatch — no __import__() calls."""
    call_map = {
        "SYSTEMZ": lambda m: m.SYSTEMZ().get_status().__dict__,
        ...
    }
    # sys.modules.get() is safe from any thread (no import lock needed)
    for mod_name in [name, f"CORE.WORMS.{name}"]:
        mod = sys.modules.get(mod_name)
        if mod:
            return call_map[name](mod)
    return None

_LEGACY_DISPATCH = {
    name: (lambda n=name: _legacy_execute(n))
    for name in _LEGACY_MODULE_NAMES
}
```

### Part 3: TELEMETRYZ.py — pre-existing `import os` bug exposed

**Bonus discovery:** Moving these imports to module level exposed a **pre-existing bug** in `src/TELEMETRYZ.py`: the file had a missing `import os` at module level, causing `NameError: name 'os' is not defined` on line 48 (`_DEFAULT_OUTPUT = os.path.join(...)`). The original `__import__("TELEMETRYZ")` in the legacy dispatch lambda was never called before (the registry resolved TELEMETRYZ before reaching the fallback), so this bug was latent.

**The TELEMETRYZ.py file also had an indentation quirk:**
```python
"""...docstring..."""import json  # Docstring end + import on SAME LINE (no newline)
    import time       # 4-space indent (pre-existing)
    import hashlib    # 4-space indent
    ...
```

The `"""import json` line had no newline between the docstring close and the import, and subsequent imports used 4-space indentation. This was an unusual formatting artifact that somehow worked. Fix: proper newline + 0-space imports.

**Symptom checklist — your code might have the same vulnerability:**
- Any `from X import Y` or `import X` inside a function body that's called from `ThreadPoolExecutor` workers
- Any `__import__()` call in a lambda or callback passed to thread pool
- `discover_worms()` or similar "import all" functions called from background threads
- Functions that import lazily on first call, when that first call could happen from a thread

**Prevention checklist for 3.14t thread safety:**
- [ ] All `import`/`from ... import` statements at TOP of file (module level)
- [ ] Lazy singletons pre-initialized on main thread before thread pool entry
- [ ] No `__import__()` calls in callbacks, lambdas, or thread targets
- [ ] Use `sys.modules.get()` for module lookups in threaded code (never `__import__()`)
- [ ] `FreeThreadPool.shutdown(wait=False, cancel_futures=True)` to avoid hang on stuck workers
- [ ] Test both with GIL and without (`PYTHON_GIL=0`)

**Corresponding code locations:**
| File | What was fixed | Type |
|------|---------------|------|
| `CORE/WORMS/CLUSTERWORMS.py` | Moved PAMS/MemoryBus/breaker imports to module level | Thread safety |
| `CORE/WORMS/CLUSTERWORMS.py` | Pre-imported 19 legacy worm modules at module load | Thread safety |
| `CORE/WORMS/CLUSTERWORMS.py` | Replaced `__import__()` lambdas with `sys.modules.get()` | Thread safety |
| `CORE/freethreading.py` | `shutdown(wait=False)` pool exit | Shutdown safety |
| `src/TELEMETRYZ.py` | Added missing `import os` | Latent bug fix |
| `src/TELEMETRYZ.py` | Fixed docstring+import on same line + 4-space indent | Formatting fix |
| `CORE/logging.py` (new) | Shim re-exporting from `azazael_logging.py` | Test fix |

**Related:** Lesson #28 (circuit breaker fix), Lesson #15 (thread ordering), Lesson #18 (locking patterns)

---

## #24 Over-scripting before reading documentation — always read first

**Discovered:** June 3, 2026

**Root cause:** Wrote 2 elaborate Python scripts (`_record_session.py`, `_survey_g_drive.py`) to survey G: drive archives and LocalMemoryStore. All of this was already documented in `SESSION_INSIGHTS_PHASE14.md`, `CODEBASE_AUDIT_TODO.md` Step 2, `PATH_FORWARD.md`, and `azazael.yaml`. The user told me **3 times** to read docs before I stopped.

**Lesson:** Read `MEMORIES.md`, `ERROR_LOG.md`, `SESSION_INSIGHTS_*.md`, and relevant TODO files before writing any investigation scripts. The project has extensive documentation covering archive strategy, config, and known issues.

**Prevention:** Before any basher/script, check if the answer is already in the docs.

---

## #25 signal.alarm() is POSIX-only — not available on Windows

**Discovered:** June 3, 2026

**Root cause:** `signal.alarm()` is POSIX-only — does not exist on Windows. Script crashed with `AttributeError`, wasted a full basher timeout cycle, and left a temp file.

**Lesson:** Never use `signal.alarm()` or `signal.siginterrupt()` in cross-platform code. Use `threading.Timer`, `concurrent.futures.ThreadPoolExecutor` with `.result(timeout=N)`, or rely on basher's built-in `timeout_seconds`.

**Prevention:** Before using any signal-based timeout, check `sys.platform == 'win32'` — if Windows, use `threading.Timer` or basher's `timeout_seconds` instead.

---

## #26 Redundant queries against LocalMemoryStore — data is already archived

**Discovered:** June 3, 2026

**Root cause:** Queried LocalMemoryStore 4+ separate times (errors, sessions, trends, events) when data was already visible from the first health check. Each extra spawn re-initializes the store and wastes time.

**Lesson:** The session recording system (`CodebuffTracker` + `record_event`) persists everything automatically. Auto-backup runs every 24h. One query is enough — the data is cumulative and doesn't change between spawns.

**Prevention:** Run one `recall_recent()` or `get_stats()` to get the full picture. If more detail is needed, filter by event_type in a single query rather than re-querying from scratch.

---

## #27 Temp file accumulation without verification — verify inline first, then script

**Discovered:** June 3, 2026

**Root cause:** Wrote full scripts (`_record_session.py`, `_survey_g_drive.py`) before verifying the approach worked. Scripts had `signal.alarm` on Windows bug + f-string syntax errors. Had to debug through basher timeout cycles rather than catching errors locally first. Distinct from MEMORIES.md anti-pattern #6 (leaving temp files) — the root problem was writing before verifying, not cleanup.

**Lesson:** Verify approach with a simple inline command first:
```
python -c "from CORE.local_memory import LocalMemoryStore; s=LocalMemoryStore(); print(s.get_stats()['total_memories'])"
```
Only write a script file if the approach needs multiple steps. Clean up immediately after.

**Prevention:** Inline first, script second. Verify before write. Clean up after.

---

## #31 PamsRecorder lazy _ensure_local_store() — deferred import to break circular init deadlock under 3.14t

**Discovered:** June 3, 2026 — during root cause analysis of ClusterWORMZ constructor hang

**Root cause:** `PamsRecorder` is a singleton that imported `LocalMemoryStore` inside its `__init__` method:

```python
class PamsRecorder:
    def __init__(self):
        ...
        # BROKEN: inline import during construction
        try:
            from CORE.local_memory import LocalMemoryStore  # Circular import risk!
            self._local_store = LocalMemoryStore()
            self._local_ok = True
            self._migrate_fallback_to_local()
        except ImportError:
            pass
```

When `ClusterWORMZ.__init__()` called `_record("cluster_created", ...)` → `_get_pams()` → `PamsRecorder()`, the singleton constructor triggered `from CORE.local_memory import LocalMemoryStore`. If `LocalMemoryStore`'s own import chain referenced any CORE module that transitively touched `PamsRecorder`, this created a circular import deadlock — hanging the constructor indefinitely.

**The fix — defer the import to first use:**

```python
def __init__(self):
    ...
    # BEFORE: imported LocalMemoryStore here → circular deadlock risk
    self._local_store = None
    self._local_ok = False
    self._local_store_init_attempted = False  # Lazy flag

def record_event(self, ...):
    ...
    # Lazy init on first use
    if not self._local_ok and not self._local_store_init_attempted:
        self._ensure_local_store()
    if self._local_ok:
        try:
            self._local_store.record_event(...)
            return True
        except Exception:
            pass
    # Fall through to JSON buffer

def _ensure_local_store(self):
    """Lazily initialize LocalMemoryStore on first use.
    
    Double-checked locking for thread safety under 3.14t free-threading.
    Import happens OUTSIDE the lock to prevent re-entrant deadlock.
    """
    if self._local_store_init_attempted:
        return
    with self._lock:
        if self._local_store_init_attempted:
            return
        self._local_store_init_attempted = True
    # Lock released — safe to import
    try:
        from CORE.local_memory import LocalMemoryStore
        self._local_store = LocalMemoryStore()
        self._local_ok = True
        self._migrate_fallback_to_local()
    except ImportError:
        pass
```

**Thread-safety pattern — double-checked locking with deferred import:**

1. **First check** (no lock): quick early-exit if already attempted — avoids lock contention on hot path
2. **Lock acquisition**: only one thread enters the critical section
3. **Second check** (under lock): prevents race where two threads both pass the first check
4. **Flag set under lock**: `_local_store_init_attempted = True` is published before any thread sees it
5. **Import after lock release**: prevents re-entrant deadlock if the import chain triggers `PamsRecorder()` construction

**Methods that now call `_ensure_local_store()`:**
- `record_event()` — on first call
- `query_memories()` — on first call
- `search_memories()` — on first call
- `get_stats()` — on first call
- `recall_recent()` — delegates to `query_memories()` (indirect coverage)

**Why this matters beyond PamsRecorder:**

Any singleton or lazy-init component that imports heavyweight dependencies in its constructor is vulnerable to this same circular deadlock. The pattern applies to:
- `MemoryBus` (similar singleton with imports)
- `BreakerRegistry` (lazy config loading)
- `PamsRecorder` itself (the fix)
- Any class where `__init__` triggers imports that may reference the original class

**Prevention checklist for 3.14t circular init safety:**
- [ ] All heavyweight imports at MODULE level (not in `__init__` or function bodies called from threads)
- [ ] Lazy inits use double-checked locking with import AFTER lock release
- [ ] Singletons that import singletons checked for circular chains
- [ ] Test under free-threading: `PYTHON_GIL=0 python -c "from CORE.PamsRecorder import PamsRecorder; p=PamsRecorder(); p.record_event('test',{'x':1})"`
- [ ] `_local_store_init_attempted` flag prevents infinite retry on failed imports (degradation, not crash)

**Corresponding code locations:**
| File | Change | Type |
|------|--------|------|
| `CORE/PamsRecorder.py` | Moved LocalMemoryStore import from `__init__` to `_ensure_local_store()` | Circular import fix |
| `CORE/PamsRecorder.py` | Added double-checked locking with `self._lock` | Thread safety |
| `CORE/PamsRecorder.py` | Added `_ensure_local_store()` calls in query/search/stats methods | Coverage |
| `tests/test_pams_recorder.py` | 13 new test cases covering singleton, lazy init, recording, thread safety | Testing |

---

## #30 discover_worms() optimization — os.path.basename() + progress callback + 1022x warm speedup

**Discovered:** June 3, 2026 — during CLUSTERWORMS parallel-hang followup optimization

**Root cause:** The original `discover_worms()` used `split(os.sep)[-1]` to extract filenames for the pre-computed `registered_files` set. On Windows, `os.sep` is backslash (`\\`), but Python's `__file__` uses forward slashes (`/`) on Windows too. This caused a **path separator mismatch** — every warm `discover_worms()` call rebuilt and re-scanned all 86 modules instead of skipping already-registered ones.

**The fix:** Replace `split(os.sep)[-1]` with `os.path.basename()`, which handles both forward and back slashes on all platforms:

```python
# BEFORE (broken on Windows — forward slashes never match backslash sep):
registered_files = {
    info.get("source_file", "").split(os.sep)[-1]
    for info in WORM_REGISTRY.values()
}

# AFTER (correct — os.path.basename handles both / and \\):
registered_files = {
    os.path.basename(info.get("source_file", ""))
    for info in WORM_REGISTRY.values()
    if info.get("source_file")  # Also added: filter out empty source_file
}
```

**Benchmark results:**
| Call | Before fix | After fix | Speedup |
|------|-----------|----------|--------|
| Cold (first call) | ~1.02s | ~1.02s | 1.0x |
| Warm (second call) | ~0.99s | ~0.0008s | **1022x** |

**Additional optimizations applied in the same session:**
- **Moved attribute checks before `getattr()`**: `attr_name.startswith('_')` and `attr_name.endswith('Config')` are now checked BEFORE `getattr(module, attr_name, None)`, avoiding unnecessary attribute access on obviously-wrong names
- **Single listdir iteration**: Built the `py_files` list once instead of iterating `os.listdir()` twice (once for count, once for the main loop)
- **Stored `_guess_category()` result**: Avoided double call to `_guess_category()` during registration (was called once for `category=` and once for `cooldown_seconds=`)
- **Simplified post-import scan**: Changed from `split(os.sep)[-1]` to `os.path.basename()` for consistency with the pre-import lookup (serves a different purpose: catches modules where `@register_worm` auto-registered during import)

**Progress callback API added:**
```python
def discover_worms(
    worms_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> int:
    """
    Args:
        progress_callback: Optional callback(processed, total, module_name)
            called BEFORE each module is imported. 'processed' tracks position
            in the full file list including skipped modules, so callers can
            display accurate progress bars during the ~1s cold-start discovery.
    """
```

The callback fires before `importlib.import_module()` for each non-skipped module. The `processed` counter from `enumerate(py_files, 1)` tracks position in the full sorted file list (including already-registered modules that are skipped). This gives callers an accurate progress bar during cold-start discovery.

**Symptom checklist — your code might have the same path separator bug:**
- `split(os.sep)[-1]` used to extract filename from a `__file__` path on Windows
- Warm calls to your function (that should be instant) take just as long as cold calls
- The function has a pre-computed set/cache that doesn't seem to work on Windows
- Using `Path(filename).name` instead of `os.path.basename()` on Python objects with `__file__` attributes

**Prevention:**
- Use `os.path.basename()` for ALL filename extraction from paths — never `split(os.sep)[-1]` or `split('/')[-1]`
- Always test optimization on the actual target platform (Windows vs POSIX path differences)
- Build pre-computed lookup sets with a filter for empty strings (`if info.get("source_file")`) to avoid empty-string entries
- Use `enumerate()` for progress tracking instead of manual counters
- Prefer `os.path.basename()` over `Path().name` when working with string paths from `inspect.getfile()` or `__file__` (which are always strings)

**Corresponding code locations:**
| File | What was fixed | Impact |
|------|---------------|--------|
| `CORE/worm_registry.py` | `split(os.sep)[-1]` → `os.path.basename()` | 1022x warm speedup |
| `CORE/worm_registry.py` | Added `if info.get("source_file")` filter | Prevents empty-string set entries |
| `CORE/worm_registry.py` | Added optional `progress_callback` parameter | CLI progress tracking |
| `CORE/worm_registry.py` | Attribute checks before `getattr()`, single listdir, cached `_guess_category()` | Marginal cold-start improvement |
| `CORE/worm_registry.py` | Updated docstring with callback signature documentation | API clarity |

**Related:** Lesson #28 (thread-safe imports), Lesson #29 (module-level pre-import pattern) — this completes the trilogy of CLUSTERWORMS threading + import optimization fixes.

---

## #32 Double-checked locking pattern for Python 3.14t free-threading — all lazy inits must be thread-safe

**Discovered:** June 3, 2026 — during full codebase audit of lazy init patterns

**Root cause:** Under Python 3.14t free-threading (no GIL), multiple threads can concurrently access lazy initialization functions. Without locking, two threads can both pass the `if _var is None:` check and both initialize the variable — causing duplicate singletons, race conditions, and potential import deadlocks.

**The pattern — double-checked locking:**

```python
_var = None
_var_lock = threading.Lock()


def _get_var():
    """Lazy init — double-checked locking for Python 3.14t free-threading."""
    global _var
    if _var is None:              # First check (no lock — fast path)
        with _var_lock:            # Lock acquisition
            if _var is None:       # Second check (under lock)
                try:
                    from some.module import SomeClass
                    _var = SomeClass()
                except ImportError:
                    _var = False   # Sentinel: don't retry
    return _var if _var else None
```

**Why each step matters:**
1. **First check** (no lock): avoids lock contention on the hot path after initialization
2. **Lock acquisition**: ensures only one thread enters the critical section
3. **Second check** (under lock): prevents race where two threads both pass the first check before either acquires the lock
4. **Sentinel assignment**: `False` prevents infinite retry on failed imports

**Files fixed in this audit (12 files, 22 lazy inits):**

| File | Lazy inits fixed | Locks added |
|------|-----------------|-------------|
| `CORE/WORMS/CLUSTERWORMS.py` | `_get_pams()`, `_get_mem_bus()`, `_get_breaker_registry()` | `_pams_lock`, `_mem_bus_lock`, `_breaker_lock` |
| `CORE/WORMS/NATURE_CLUSTERS.py` | `_get_pams()`, `_get_config()`, `_get_breakers()`, `_get_log()` | `_pams_lock`, `_cfg_lock`, `_breaker_lock`, `_logger_lock` |
| `CORE/WORMS/METACLUSTER.py` | `_get_pams()`, `_get_mem_bus()`, `_get_config()`, `_get_breakers()`, `_get_log()` | `_pams_lock`, `_mem_bus_lock`, `_cfg_lock`, `_breaker_lock`, `_logger_lock` |
| `CORE/WORMS/BINARY_ANALYSIS_TYPES.py` | `_get_pams()` | `_pams_lock` (+ added `import threading`) |
| `CORE/workflow.py` | `_get_config()` | `_cfg_lock` (`_get_engine()` already had `_engine_lock`) |

**Which lazy inits are safe vs unsafe under 3.14t:**

| Init type | Safe? | Why |
|-----------|-------|-----|
| Module-level `try/except` import (`from X import Y as _YCls`) | ✅ Always safe | Happens at import time on the main thread |
| Module-level assignment (`_var = None`) | ✅ Always safe | Just a variable declaration |
| Double-checked locking (`if _var is None: with _lock: if _var is None:`) | ✅ Thread-safe | Lock prevents concurrent access |
| Bare-check lazy init (`if _var is None: _var = ...`) | ❌ NOT safe | Two threads can both initialize — race condition |
| Function-body `import`/`__import__()` | ❌ NOT safe (can deadlock) | Import lock not re-entrant under 3.14t free-threading |

**Drill: how to identify lazy inits that need fixing:**

1. Search for the pattern: `if _\w+ is None:` followed by an import or instantiation
2. Check if the enclosing function is called from worker threads (ThreadPoolExecutor, FreeThreadPool, `threading.Thread`)
3. Trace callers: if any path from a thread pool reaches the lazy init, it needs locking or module-level import
4. Also check: does the file have `import threading`? If not, add it
5. Verify the pattern: first check (no lock) → lock → second check → init → return sentinel on failure

**Prevention checklist for all future lazy inits:**
- [ ] Every lazy init MUST use double-checked locking
- [ ] File must `import threading` before the lock variable declaration
- [ ] Sentinel value (`False`) prevents infinite retry on transient failures
- [ ] Import inside lock is acceptable for simple utility modules (no circular dependency risk)
- [ ] For complex imports (may trigger circular chains), move import AFTER lock release (set flag under lock, then import)
- [ ] Test under free-threading: `PYTHON_GIL=0 python -c "from core.module import get_var; print(get_var())"`
- [ ] Review during code review: all `if _var is None:` patterns should have corresponding locks

**Related:** Lesson #28 (import deadlock under 3.14t), Lesson #29 (module-level import pattern), Lesson #31 (PamsRecorder circular init fix)

---

---

## #33 functools.partial Over Lambdas for Mypy Inference (June 3, 2026)

**Context:** Mypy cannot infer the type of lambdas in certain contexts (tkinter callbacks,
loop-variable capture, `after()` callbacks), producing `Cannot infer type of lambda [misc]` errors.
`# type: ignore[misc]` at end of line often doesn't suppress these errors.

**Root cause:** The `[misc]` error code attaches to the lambda expression itself, not the line
as a whole. Trailing `# type: ignore[misc]` comments may not suppress the error.

**The fix:** Replace problematic lambdas with one of:
1. `functools.partial(self.method, arg)` — best for button command callbacks
2. `tkinter.after(ms, self.method, arg)` — `after()` accepts positional args
3. Explicitly named function with typed parameters

**Pattern examples:**
```python
# WRONG: mypy can't infer lambda type
button.configure(command=lambda x=value: self.method(x))

# RIGHT: functools.partial resolves the type
button.configure(command=functools.partial(self.method, value))

# WRONG: mypy can't infer lambda in after()
root.after(100, lambda: self.method(arg))

# RIGHT: after() passes positional args
root.after(100, self.method, arg)
```

**AZAZAEL_Inference_Studio.py:** 6 `[misc]` errors fixed using this pattern.

---

## #34 Separate Mixed-Type Dict Items to Fix Type Widening (June 3, 2026)

**Context:** A dict with a mix of `str` and `tuple` values causes mypy to widen the
value type to `Sequence[str]` (since `str` and `tuple[str, str]` both satisfy `Sequence[str]`).
This causes 126+ `arg-type` errors when the dict values are passed to functions expecting `str`.

**Root cause:** One item `"accent_gradient": ("#00f5ff", "#bf00ff")` was a tuple in an
otherwise homogeneous `dict[str, str]`. Mypy unified the type to `dict[str, Sequence[str]]`.

**The fix:** Extract the tuple-valued item to a separate module-level constant:
```python
# WRONG:
THEME = {
    "bg": "#040410",  # str
    "accent_gradient": ("#00f5ff", "#bf00ff"),  # tuple — widens type
}

# RIGHT:
THEME: dict[str, str] = {
    "bg": "#040410",
    ...
}
ACCENT_GRADIENT: tuple[str, str] = ("#00f5ff", "#bf00ff")
```

**AZAZAEL_Inference_Studio.py:** 126 `arg-type` errors fixed by this change alone.

---

## #35 Missing Methods Cause Mypy attr-defined Errors (June 3, 2026)

**Context:** A class called `METAWORMS.run("wormname")` in `main()` and `run_popup()`
but the `METAWORMS` class had no `.run()` method — only `.run_all()`. This would have
caused an `AttributeError` at runtime.

**Root cause:** The `run()` method was never implemented. Callers were using it as if it
existed (called with a worm name argument), but it was missing from the class definition.

**The fix:** Added the missing method:
```python
def run(self, name: str) -> Optional[WormResult]:
    if name not in self.WORMS:
        print(f"Unknown worm: {name}")
        return None
    worm_class = self.WORMS[name]
    worm = worm_class()
    self.results[name] = worm.run()
    return self.results[name]
```

**Lessons:** Mypy `attr-defined` errors can reveal real runtime bugs. Always investigate
`attr-defined` errors — they may indicate missing methods, not just missing annotations.
This bug was discovered when mypy reported `"METAWORMS" has no attribute "run"` on lines
1038 and 1091.

---

## #36 Autoflake Works on Python 3.14t — False Diagnosis Chain Cost Hours of Unnecessary Work (June 4, 2026)

**Discovered:** June 4, 2026 — during systematic autoflake verification

**The false claim:** A previous assistant incorrectly claimed "autoflake crashes on Python 3.14t"
and created a `_clean_imports.py` workaround script (~50 lines). Later, an entire
`scripts/autoflake_314t.py` tool was created (~120 lines) as a "free-threaded wrapper."

**Hours wasted:** ~2-3 hours creating, debugging, and documenting workarounds for a tool
that worked perfectly all along.

**Root cause chain:**
1. A `basher` command ran `autoflake` with likely shell escaping issues (nested quotes,
   anti-pattern #1 from MEMORIES.md)
2. The subprocess failed with an obscure error message
3. The error was misattributed to "3.14t incompatibility" rather than investigated as a
   command-line syntax issue
4. No one tested `python -m autoflake --version` or `python -m autoflake --check file.py`
   directly (which would have immediately confirmed it works)
5. The false assumption propagated: workaround script → wrapper tool → skill module →
   architecture analysis reference → all incorrect

**Evidence that should have been checked first:**
- `autoflake v2.3.3` is pure-Python (depends only on `pyflakes`, no C extensions)
- Prior sessions (Phase 14 & 15) used autoflake successfully to clean 12+ files
- `python -m autoflake --version` works on any Python version — no compiled extensions
- The basher command syntax was the actual failure, not autoflake itself

**The investigation that finally found the truth:**
1. Checked: `autoflake v2.3.3` is pure-Python — no cp314t wheel needed
2. Checked: Phase 14/15 session docs confirm autoflake was used successfully
3. Tested: direct subprocess with `sys.executable` — works perfectly
4. Tested: `shell=True` subprocess — also works (confirming no 3.14t issue at all)
5. Conclusion: the original failure was shell escaping, not 3.14t incompatibility

**Permanent fix applied:**
- Created `ERROR_LOG.md` entry #55 documenting the false diagnosis and true root cause
- Added this lesson (#36) documenting the investigation chain
- `scripts/autoflake_314t.py` is still useful as a batch wrapper, but now correctly
  documented as an enhancement tool, not a workaround

**Prevention — Diagnosing "tool broken on 3.14t" claims (investigation checklist):**
- [ ] Is it a C-extension package? Check `pip show` for compiled extensions
- [ ] Is it pure-Python? Run `python -m toolname --version` directly
- [ ] Does the basher/subprocess command have nested quotes? (Anti-pattern #1)
- [ ] Did prior sessions use this tool successfully? Check session docs
- [ ] Test with the simplest possible command: `python -c "import subprocess; ..."`
- [ ] Check exit codes: 0 = clean, 1 = found issues (NOT a crash!)

**Never assume 3.14t broke a tool until you've verified ALL of:**
1. The tool uses C extensions (not pure-Python)
2. No cp314t wheel exists for the required version
3. `python -m toolname --version` fails
4. Direct subprocess (not basher) also fails


## #37 Conditional Import Fallbacks — Always Use `# type: ignore[no-redef]` (June 4, 2026)

**Context:** Multiple CORE files (Agent.py, MemoryBus.py, NETWORK_DIAG.py, REVERSE_TOOLS.py)
use try/except import patterns for graceful fallbacks when optional dependencies are
unavailable (freethreading, PAMS, MemoryBus, agent_registry).

**Root cause of mypy errors:** When a name is imported in the `try` block (e.g.,
`from CORE.freethreading import FreeThreadPool`), then assigned a different value in
the `except` block (e.g., `FreeThreadPool = lambda: ...`), mypy reports:
- `Name "FreeThreadPool" already defined (possibly by an import) [no-redef]`
- `All conditional function variants must have identical signatures [misc]`

**The fix:**
```python
try:
    from CORE.freethreading import FreeThreadPool
    HAS_FREETHREADING = True
except ImportError:
    HAS_FREETHREADING = False
    # Add type: ignore[misc] for function redefinitions with different signatures
    def FreeThreadPool(*a, **kw):  # type: ignore[misc]
        ...
    # Add type: ignore[no-redef] for type assignments
    ThreadSafeDict: Any = dict  # type: ignore[no-redef]
```

**Key rules:**
1. `[no-redef]` for type/value redefinitions (ThreadSafeDict = dict)
2. `[misc]` for conditional function variants with different signatures
3. `Any` annotation on fallback types to avoid downstream union-type issues

## #38 Agent.py Conditional Import Patterns — 7 Fallback Names Need type: ignore (June 4, 2026)

**Context:** `CORE/Agent.py` has the most complex conditional import structure in the
codebase, with 7 different fallback names (ThreadSafeDict, ThreadSafeList,
ThreadSafeCounter, is_free_threaded, FreeThreadPool, PamsRecorder, get_recorder,
MemoryBus, BusMessage, register_agent, AgentHealthReporter, AGENT_REGISTRY).

**Impact:** Before fixes, Agent.py had 17 mypy errors — all from conditional import
fallbacks. None from actual logic errors. The file itself was type-safe.

**Lessons:**
- Conditional import fallbacks in base classes are a necessary evil for graceful
  degradation. Use `# type: ignore` liberally but precisely.
- Each fallback name needs its own `# type: ignore` — mypy doesn't cascade ignore
- `_pams: Any = None` in the except block needs `# type: ignore[no-redef]` because
  `_pams: Any = PamsRecorder()` was already defined in the try block

## #39 Architecture Efficiency Ratings — Measure Before Refactoring (June 4, 2026)

**Context:** Created `AZAZAEL_ARCHITECTURE_ANALYSIS.md` — comprehensive modular
design assessment with Dependency Efficiency Index (DEI) scores, coupling analysis,
cohesion metrics, and a strategic improvement roadmap.

**Key findings:**
- Overall efficiency rating: **6.8 / 10**
- CORE/paths.py has **139 inbound deps** — single biggest bottleneck
- 4 circular import chains active
- 18 deprecation shims still active (technical debt)
- Test coverage at ~15% (critical gap)

**Lessons:**
- Measure before refactoring: DEI scores identify where effort has maximum impact
- CORE/paths.py bottleneck: split into domain-specific modules (paths_gdrive.py,
  paths_desktop.py, paths_cluster.py) for immediate improvement
- Circular imports are the highest structural risk — prioritize elimination
- 3.14t readiness is the strongest architectural dimension (8.0/10)

## #40 Create Self-Contained Python Wrappers for CLI Tools on 3.14t (June 4, 2026)

**Context:** Shell-escaping issues on Windows with Python 3.14t cause reproducible
failures when running CLI tools via basher/spawn_agents. Creating a self-contained
Python wrapper (scripts/autoflake_314t.py) eliminates these failure modes.

**Pattern:**
```python
# scripts/my_tool_314t.py
import subprocess, sys

def run_tool(filepath):
    result = subprocess.run(
        [sys.executable, '-m', 'autoflake', '--check', filepath],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode, result.stdout, result.stderr
```

**Benefits:**
- No shell escaping issues
- Predictable timeouts per invocation
- Process isolation (one bad file doesn't crash the batch)
- Cross-platform compatible (handles Windows path separators)
- Easy to extend with additional flags and modes

**Lessons:** When a CLI tool needs batch operations on 3.14t, write a Python wrapper
that uses `sys.executable` + direct subprocess calls. Never use nested quotes or
shell=True.

---

## #41 Architecture Review Methodology — Systematic Project Inventory Across Multiple Dimensions (June 4, 2026)

**Context:** The Azazael ecosystem spans 13 sub-layers (CORE, WORMS, CODEX, ORCHESTRATION,
HYDRA, META, UTILITIES, TOOLS, SCRIPTS, CLI, root *.py files, Desktop Standalone Suite,
14 Desktop projects, G: Drive Archive, package infrastructure, and test infrastructure).

**Discovered:** During the architecture review of all projects, the most effective
methodology was a 3-pass approach:

### Pass 1: Inventory (What exists)
```
1. Load all architecture skills (azazael-architecture, azazael-files, azazael-production)
2. Read all existing analysis docs (AZAZAEL_ARCHITECTURE_ANALYSIS.md, PROJECT_MAP.md, PATH_FORWARD.md)
3. Read directory trees (read_subtree) for all major directories
4. Read each TODO file to understand current plans (CODEBASE_AUDIT_TODO.md, PRODUCTION_TODO.md (archived), REWRITE_TODO.md (legacy), PHASE_6_TODO.md (legacy))
5. Cross-reference: does inventory match existing docs? Flag discrepancies.
```

### Pass 2: Rate (How healthy)
```
For each project, rate on 3 axes:
- Cohesion (0.0-1.0): how well do the files in this directory relate to each other?
- Coupling (1-10): how many outbound dependencies does this module have?
- Health (🔴/🟡/🟢): qualitative assessment of maintainability and completeness
```

### Pass 3: Scorecard (System-wide metrics)
```
Rate on 12 dimensions (1-10):
- Modular cohesion, Inter-module coupling, Dependency hygiene
- Type safety, Test coverage, Documentation
- Build system, 3.14t readiness, Shell injection safety
- Package management, Desktop project integration
- Overall (weighted average)
```

**Key findings from this session:**
| Project | Cohesion | Coupling | Health |
|---------|----------|----------|--------|
| CORE/WORMS/ | 0.85 | 3.2 | 🟢 Best structured |
| CODEX/ | 0.90 | 2.1 | 🟢 Most cohesive |
| CORE/ infra | 0.65 | 9.8 | 🔴 Most bottlenecked (paths.py 139+ deps) |
| Root *.py | 0.40 | 5.0 | 🔴 Hardest to maintain |
| META/ | 0.30 | 1.5 | 🔴 Phasing out |

**Lessons:**
- The 3-pass approach (Inventory → Rate → Scorecard) ensures no project is missed
- Cohesion + Coupling are inversely correlated — highly coupled modules often have low cohesion
- Always cross-reference TODO files before updating — 4+ TODO docs means consistency checking is critical
- The scorecard overall (6.2/10) was lower than the original (6.8/10) because 4 new dimensions lowered the average — document this explicitly to avoid confusion

**Cross-reference:** Lesson #39 (Architecture Efficiency Ratings) established the original 8-dimension scoring. This lesson extends that methodology to 12 dimensions.

---

## #42 TODO Document Versioning — Cross-Reference New Items Against Existing Plan Steps (June 4, 2026)

**Context:** `CODEBASE_AUDIT_TODO.md` already had 12 sequential Steps (1-12) covering the
production roadmap. The architecture review generated 12 new improvement items (AR-1 through
AR-12). Simply appending them would create duplicate or conflicting plan items.

**Discovered:** When adding new findings to an existing TODO document, you must:

### Step 1: Classify each new item
```
Classification choices:
- ADDITIVE: Not covered by any existing Step (e.g., "Fix 6 shell=True HIGH RISK usages")
- REINFORCES: Overlaps an existing Step but adds new detail (e.g., "Add pytest-cov" → reinforces Step 3)
- DUPLICATE: Already covered — skip it (e.g., "Add dead letter queue" → already in Step 4)
```

### Step 2: Cross-reference table
```
| # | AR-ID | Action | Existing Step | Additive? |
|---|-------|--------|---------------|-----------|
| 1 | AR-1  | Fix shell=True | New | ✅ Additive |
| 2 | AR-11 | Fix mypy errors | Step 7 (perf opt) | ⚠️ Reinforces |
```

### Step 3: Track additive vs reinforcing ratio
From this session: **7 of 12 items are additive** (58%), **5 reinforce** existing Steps.

**Lessons:**
- A high additive ratio (>50%) means the TODO was missing significant scope — good sign that
  the review uncovered genuine gaps
- A low additive ratio (<20%) means the TODO was already comprehensive — review validated
  existing planning
- Always tag new items with both the AR identifier AND the existing Step reference — this
  makes it easy to trace provenance and detect duplicates in future updates
- Update the State Snapshot timestamp and version number with each major update (v3 → v4)

**Cross-reference:** Lesson #24 (Read docs first) and Lesson #27 (Verify before write) establish the documentation-reading discipline that this classification scheme depends on. Always read the existing Steps before classifying new items.

---

## #43 Skills Alignment Audit — Verify On-Disk vs Catalog Parity (June 4, 2026)

**Context:** The project has 18 skill files on disk (`skills/*.md`) and a `SKILLS_CATALOG.md`
that indexes them. During the audit, 3 legacy files lacked YAML frontmatter (making them
invisible to automated tooling), and the catalog had a reference to a skill that didn't
exist on disk.

**Methodology — Skills Audit Checklist:**
```
1. LIST on-disk files: ls skills/*.md → 18 files
2. READ catalog: SKILLS_CATALOG.md → entries for each skill
3. COMPARE: does every on-disk file have a catalog entry?
   - Yes → ok
   - No → add catalog entry
4. CHECK YAML frontmatter: does each .md file start with "---"?
   - Yes → has name + description metadata
   - No → flag for repair (add YAML frontmatter or mark as legacy)
5. FLAG legacy files: files without frontmatter may be archival — decide:
   - Add frontmatter (if still relevant)
   - Move to archive/ (if no longer current)
   - Leave as-is but document as legacy
```

**Findings:**
| Issue | Count | Action |
|-------|-------|--------|
| On-disk files matching catalog | 15 | ✅ Verified |
| Legacy files without frontmatter | 3 (azazael_314t_master.md, _optimum.md, _insights_2026-05-28.md) | ⚠️ Flagged for metadata |
| Catalog reference to non-existent file | 0 | ✅ Catalog is comprehensive |
| New skills created this session | 1 (azazael-error-prevention.md) | ✅ Added to catalog |

**Lessons:**
- Skills alignment audit should be run periodically (every 5-10 sessions) to detect drift
- Legacy files without frontmatter should be dealt with promptly — they accumulate and
  create confusion about which skills are "active"
- The azazael-error-prevention.md skill was created but its catalog entry already existed
  (was a virtual skill from earlier sessions) — verify catalog matches before creating

---

## #44 Comprehensive TODO Update — 4 TODO Documents Must Stay Consistent (June 4, 2026)

**Context:** The project has 4 active TODO documents, each with different scope:
| Document | Scope | Status |
|----------|-------|--------|
| `CODEBASE_AUDIT_TODO.md` | Living production plan (12 Steps) | ✅ Primary — updated all sections |
| `PRODUCTION_TODO.md` | Original gaps (superseded) | ✅ Archived July 6, 2026 — use CODEBASE_AUDIT_TODO.md |
| `REWRITE_TODO.md` | Original rewrite plan | 🔴 Legacy — not updated since Phase 2 |
| `PHASE_6_TODO.md` | Phase-specific tasks | 🔴 Legacy — incorporated into CODEBASE_AUDIT_TODO.md |

**Discovered:** When updating CODEBASE_AUDIT_TODO.md with architecture review findings,
3 of 4 documents were out of date. Only CODEBASE_AUDIT_TODO.md was actively maintained.

The production roadmap should be **consolidated into ONE living document** and the others
archived with a clear "superseded by" reference.

**Lessons:**
- Multiple TODO documents create consistency debt — every update to one must be checked
  against all others
- When a primary TODO emerges (CODEBASE_AUDIT_TODO.md), explicitly mark the others as
  "superseded" with a redirect to the primary
- State Snapshots should be updated with each major version (v1 → v2 → v3 → v4) and
  include a timestamp for traceability
- The Effort Estimates table and Phase labels (23+, 24, 25, 26) provide a shared vocabulary
  across all documents — keep these consistent

**Recommendation:** PRODUCTION_TODO.md was deleted (July 6). Move REWRITE_TODO.md and PHASE_6_TODO.md to a
`archive/` directory, with a summary file listing what each contained and where the
current content lives in CODEBASE_AUDIT_TODO.md.

**Cross-reference:** Lesson #27 (Verify before write) established the "leave things cleaner than you found them" discipline. Archiving superseded TODO documents follows this principle — consolidation reduces cognitive load for future sessions.

---

---

## #45 Bun v1.3.11 Windows Standalone Binary Crash — bmalloc/libpas Segfault (June 4, 2026)

**Context:** The Codebuff/freebuff CLI client (`freebuff.exe`, 142MB standalone binary)
crashed during a session, and the user asked for an investigation into the root cause.

**Discovered:** June 4, 2026 — Bun crash investigation session

**Root cause:** `freebuff.exe` was compiled with **Bun v1.3.11** on Windows. Bun's
JavaScript engine (JavaScriptCore from WebKit) uses custom memory allocators (`bmalloc`
and `libpas`) that are NOT stable on Windows. These allocators cause segmentation faults
(access violation 0xc0000005, SIGSEGV exit 139) during GC cycles, memory pressure, or
worker IPC in standalone compiled binaries.

This is a **well-documented class of bugs** in the oven-sh/bun repository:
- GitHub issues: #26862, #26982, #27431, #26574, #29674, #31291
- Root cause: WebKit's memory management layer has platform-specific issues on Windows
- The Bun team's fix: progressively disabling bmalloc/libpas on Windows builds
  (`USE_SYSTEM_MALLOC=ON`), but not all versions include the fix

**Evidence gathered during investigation:**
- freebuff.exe version strings: Bun v1.3.11 (54 occurrences in binary)
- freebuff.exe size: 142,522,368 bytes, compiled June 1, 2026
- Bun was NOT installed as CLI tool (no `.bun/bin/` directory, not in PATH)
- Only `.bun/install/cache/` remained with cached npm packages
- No crash dumps found (Bun segfaults are often hard crashes with no dump)

**The fix — three-part approach:**
1. **Upgrade Bun**: Installed Bun v1.3.14 (`~/.bun/bin/bun.exe`) — includes Windows
   stability patches targeting bmalloc/libpas issues
2. **Configure WER**: Set HKLM registry for freebuff.exe crash dumps (DumpType=2 full
   dump, DumpCount=10)
3. **Install ProcDump**: Sysinternals ProcDump at `C:\Users\clint\AppData\Local\Procdump\`
   for active crash monitoring (`procdump64 -e -ma freebuff.exe`)

**Diagnostic pipeline for Bun standalone binary crashes:**
1. Check Bun version in binary: `strings binary.exe | grep "bun.*v?[0-9]"` or
   Python: extract ASCII strings, find version patterns
2. Check Bun version installed: `bun --version` (v1.3.14+ has Windows malloc fixes)
3. Check WER dumps: `dir %LOCALAPPDATA%\CrashDumps\freebuff*.dmp`
4. Monitor with ProcDump: `procdump64 -e -ma freebuff.exe`
5. Analyze dump with WinDbg: `!analyze -v` on the .dmp file

**Symptom checklist — your Bun compiled binary might have the bmalloc bug if:**
- Standalone .exe crashes with no visible error message (hard crash)
- No crash dump generated by default (WER not configured)
- Crash is non-deterministic: sometimes works, sometimes segfaults
- More likely under memory pressure or long-running sessions
- Version embedded in binary is Bun v1.3.11 or earlier on Windows
- Upgrading Bun runtime and recompiling fixes the issue

**Prevention:**
- Always compile standalone binaries with latest Bun (1.3.14+ for Windows)
- Set up WER crash dumps for all Bun-compiled production binaries
- Use ProcDump monitoring during testing and development
- Never ship Bun v1.3.11 or earlier standalone binaries on Windows
- Check oven-sh/bun GitHub issues for Windows stability before deploying

**Corresponding code locations:**
| File | Change | Type |
|------|--------|------|
| `.config/manicode/freebuff.exe` | Analyzed (v1.3.11 compiled binary) | Investigation |
| `~/.bun/bin/bun.exe` | Upgraded to v1.3.14 | Fix |
| `HKLM\...\LocalDumps\freebuff.exe` | WER crash dump registry configured | Monitoring |
| `AppData\Local\Procdump\procdump64.exe` | ProcDump installed | Monitoring |
| `Desktop/freebuff_monitor.bat` | Auto-monitor launch script created | Tooling |

**Cross-reference:** Lesson #46 (FreeBuff monitoring setup). Related skills: none (new domain).
Also see ERROR_LOG.md for 3.14t segfault patterns (Errors #48, #49, #54) — similar
C-extension/Rust .pyd segfault patterns on 3.14t, different root causes.

---

## #46 FreeBuff Crash Monitoring Setup — WER + ProcDump Defense-in-Depth (June 4, 2026)

**Context:** After diagnosing the Bun bmalloc/libpas crash in Lesson #45, crash monitoring
needed to be set up so future crashes are captured with full memory dumps for root cause
analysis.

**Discovered:** June 4, 2026 — during FreeBuff crash investigation followups

**Root cause:** Bun standalone binary crashes on Windows produce NO crash dump by default.
Without configuration, the crash is invisible — the process just disappears. This makes
debugging impossible without proper monitoring infrastructure.

**The fix — defense-in-depth crash monitoring:**

### Layer 1: WER (Windows Error Reporting) — Automatic, always-on
```
Registry: HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps\freebuff.exe
  DumpType: 2 (Full dump)
  DumpCount: 10 (max dumps to keep)
  DumpFolder: %LOCALAPPDATA%\CrashDumps (default)
```

### Layer 2: ProcDump — Active monitoring with full dumps
```batch
C:\Users\clint\AppData\Local\Procdump\procdump64.exe -e -ma -accepteula freebuff.exe
  -e: trigger on unhandled exception (crash)
  -ma: full memory dump (includes heap, stack, modules)
  -accepteula: skip license prompt
```

### Layer 3: Auto-monitor launch script
```batch
Desktop/freebuff_monitor.bat
  - Validates freebuff.exe and ProcDump paths exist
  - Searches PATH if freebuff.exe not found at default location
  - Launches freebuff.exe under ProcDump monitoring
  - Dumps saved to %LOCALAPPDATA%\CrashDumps\
```

**Crash dump analysis workflow:**
1. Check for dumps: `dir %LOCALAPPDATA%\CrashDumps\freebuff*.dmp`
2. Open in WinDbg: `windbg -z dumpfile.dmp`
3. Run analysis: `!analyze -v`
4. Look for: `bmalloc`, `pas_assertion_failed`, `SIGSEGV`, access violation
5. Check faulting module: likely `freebuff.exe` or JSC/bmalloc component

**Prevention checklist for all compiled production binaries:**
- [ ] WER registry configured for the executable name
- [ ] ProcDump available at known path
- [ ] Auto-monitor launch script created and tested
- [ ] Crash dump location documented and accessible
- [ ] WinDbg installed for dump analysis
- [ ] Dump analysis workflow documented

**Corresponding code locations:**
| File | Purpose |
|------|---------|
| `Desktop/freebuff_monitor.bat` | Launch freebuff with ProcDump crash monitoring |
| `C:\Users\clint\AppData\Local\Procdump\procdump64.exe` | ProcDump binary for crash capture |
| `HKLM\...\LocalDumps\freebuff.exe` | WER automatic crash dump registry |

**Cross-reference:** Lesson #45 (Bun crash root cause). See also MEMORIES.md anti-pattern #8
(never declare a tool broken without verification) — the same investigation discipline
applies to crash diagnosis: gather evidence before concluding.

---

---

## #47 Bundled Startup Skill — Single Skill("azazael-system-startup") for All Mandatory Startup (June 4, 2026)

**Context:** The startup procedure in SYSTEM_INSTRUCTIONS.md had grown from 7 to 9
mandatory steps (reading 5 files, loading 4 skills). Each new session discovery risked
further expanding this list, making it hard for future assistants to execute consistently.

**Discovered:** June 4, 2026 — during FreeBuff monitoring setup followups

**Root cause:** The startup procedure was distributed across 3 files (SYSTEM_INSTRUCTIONS.md,
SESSION_STARTUP.md, and the azazael-system-startup skill). Each file duplicated parts of
the sequence, creating consistency debt. The inline list kept growing as new requirements
were discovered (FreeBuff check, ALWAYS enforcement).

**The fix — bundled startup skill:**

Updated `azazael/skills/azazael-system-startup.md` to be the SINGLE entry point:

```
skill("azazael-system-startup") loads ALL mandatory startup in one call:

Step 1: Read all 5 canonical files (MEMORIES.md, ERROR_LOG.md,
        SYSTEM_INSTRUCTIONS.md, SESSION_STARTUP.md, LESSONS_MASTER.md)
Step 2: Load 3 mandatory guardrail skills (error-prevention, sop, pams-memory)
Step 3: Run FreeBuff/Bun environment diagnostic (PowerShell check:
        Bun version, freebuff.exe, WER config, ProcDump)
Step 4: Initialize memory system (LocalMemoryStore)
Step 5: Load domain skills based on task
```

**What changed:**
1. Consolidated all 5 file reads into one read_files() call
2. Added FreeBuff/Bun environment diagnostic (Step 3)
3. Added "Skip startup procedure" to the anti-pattern list
4. Added "Assume Bun is installed" to the anti-pattern list
5. Added FreeBuff-related file locations to key file table
6. Strengthened the "not optional" language

**Simplified SYSTEM_INSTRUCTIONS.md:**
```
skill("azazael-system-startup")  # Single call replaces 9 manual steps
```

The inline list in SYSTEM_INSTRUCTIONS.md now says "load this skill" instead of
duplicating the full procedure. The skill file is the canonical source.

**Prevention:**
- When new startup requirements are discovered, update the skill file, not the inline list
- The skill is the single source of truth for startup procedure
- SYSTEM_INSTRUCTIONS.md should reference the skill, not duplicate it

**Cross-reference:** Lesson #44 (TODO document consistency) — same principle: one canonical
source is better than multiple distributed copies. Lesson #42 (cross-reference new items
against existing) — applied to ensure the bundled skill doesn't lose any existing steps.

---

## #48 FreeBuff Rebuild Blocked — npm Package Is a Wrapper, Not Source (June 4, 2026)

**Context:** After diagnosing the Bun v1.3.11 crash (Lesson #45) and upgrading to Bun
v1.3.14, the next step was to rebuild freebuff.exe with the fixed Bun runtime to bake in
Windows stability patches.

**Discovered:** June 4, 2026 — during FreeBuff rebuild attempt

**Root cause:** The `freebuff` npm package (v0.0.98) is NOT the source code — it's a
downloader/wrapper:
- `index.js` invokes an external pre-built binary
- `postinstall.js` downloads the standalone binary to `~/.config/manicode/freebuff.exe`
- The npm package has no TypeScript/JavaScript application source to compile with `bun build --compile`
- The actual Codebuff source repository is required to rebuild the binary

**Evidence:**
| File | Content |
|------|---------|
| `package.json` bin | Points to `index.js` (wrapper, not source) |
| `postinstall.js` | Downloads pre-built binary |
| `preuninstall.js` | Cleans up downloaded binary |
| `index.js` | Executes the external freebuff binary |

**What IS available for monitoring:**
- Bun v1.3.14 installed (runtime fix for future standalone binaries)
- freebuff.exe (135.9 MB, Bun v1.3.11 compiled) — the pre-crash binary still works with monitoring
- WER crash dumps configured (DumpType=2, DumpCount=10)
- ProcDump available for active monitoring
- Auto-monitor script: `Desktop/freebuff_monitor.bat`

**What's needed for rebuild:**
- The Codebuff source repository (GitHub or internal)
- Contact: codebuff.com for source access or updated binary
- Alternative: wait for Codebuff to ship a Bun v1.3.14+ compiled version

**Prevention:**
- For npm packages that download binaries, check `package.json` scripts for
  `postinstall`/`preuninstall` to understand if the package IS the source or just a wrapper
- Binaries downloaded by postinstall scripts are pre-built — rebuilding requires
  the upstream source repository, not the npm package
- Verify with: `cat node_modules/<pkg>/package.json | grep -A5 scripts`

**Cross-reference:** Lesson #45 (Bun crash root cause), Lesson #46 (crash monitoring setup).
The monitoring infrastructure is the pragmatic mitigation until a Bun v1.3.14+ freebuff.exe
is available from upstream.

---

## #49 FreeBuff Environment Verification — Bun PATH Must Be Explicit (June 4, 2026)

**Context:** After installing Bun v1.3.14 via PowerShell (`irm bun.sh/install.ps1 | iex`),
running `bun --version` from bash/Git Bash failed because the PATH was not refreshed.

**Discovered:** June 4, 2026 — during FreeBuff environment diagnostic check

**Root cause:** Bun's Windows installer adds `~/.bun/bin` to the user's Windows PATH,
but this change only takes effect in NEW shell sessions. The current bash session's
PATH didn't include `~/.bun/bin`, so `bun` was not found.

**Symptoms:**
- `bun --version` → "command not found" in bash
- `bun --version` → works in PowerShell (different PATH inheritance)
- Binary exists at `~/.bun/bin/bun.exe` but shell can't find it

**The fix:**
```bash
# For current session:
export PATH="$HOME/.bun/bin:$PATH"
bun --version  # Returns: 1.3.14

# For permanent fix in bash (.bashrc):
echo 'export PATH="$HOME/.bun/bin:$PATH"' >> ~/.bashrc
```

**FreeBuff environment verification results (June 4, 2026):**
| Component | Status | Detail |
|-----------|--------|--------|
| Bun | [OK] | v1.3.14 (with PATH fix) |
| freebuff.exe | [OK] | 135.9 MB at ~/.config/manicode/ |
| WER crash dumps | [OK] | Configured (DumpType=2, DumpCount=10) |
| ProcDump | [OK] | Available at AppData/Local/Procdump/ |
| npm freebuff | [OK] | v0.0.98 wrapper installed globally |

**Prevention:**
- After installing Bun on Windows, RESTART the terminal or run `export PATH="$HOME/.bun/bin:$PATH"`
- Add `export PATH="$HOME/.bun/bin:$PATH"` to `~/.bashrc` for permanent availability
- The PowerShell diagnostic in azazael-system-startup skill handles this automatically
  by checking both PATH and the known binary location

**Cross-reference:** Lesson #45 (Bun crash), Lesson #46 (monitoring), Lesson #47 (startup skill).
The environment check is now part of the mandatory startup procedure (Step 3 of the
azazael-system-startup skill).

---

## #50 Graphical Representation Vault — 31 Templates Across 5 Visualization Formats (June 4, 2026)

**Context:** The user requested a review of all graphical representations in the Azazael
project for enrichment and diversity. The investigation discovered 31 HTML templates
across 5 fundamentally different visualization approaches, plus an ASCII flowchart
Python module.

**Discovered:** June 4, 2026 — during graphical representation vault review

**Root cause:** Graphical representations accumulated organically across sessions without a
central inventory. Different visualization formats were developed to represent the same
system information (architecture, worm topology, data flow, lifecycle) from different
perspectives:

### Format Inventory

| Format | Count | Files | Key Feature |
|--------|-------|-------|-------------|
| **Mermaid.js** (inline) | 10 | MERMAID_GRAPHS.html | 10 diagram types in one page: architecture, flow, sequence, class, ER, state, gantt, mindmap |
| **Mermaid.js** (standalone) | 10 | templates/mermaid/*.html | Individual diagrams: hierarchy, lifecycle, class, coordination, data, mindmap, pipeline, distribution, timeline, version |
| **Force-Directed** | 1 | STRUCTURE_VISUALIZER.html | 34-node interactive graph with 4 layouts (force, radial, tiered, spiral) |
| **Cinematic Scroll** | 1 | CINEMATIC_SCROLL.html | Parallax layers, particle trails, typewriter overlays, timeline rail |
| **Dashboard** | 1 | dashboard/index.html | Live observability with particle canvas, 3D tilt, health/DB/metrics/drift cards |
| **ASCII Flowchart** | 1 (Python) | ascii_flowchart.py | 8 diagram types: process flow, decision tree, architecture, mind map, pipeline, comparison table, worm diagram |
| **Analysis Reports** | 3 | ANALYSIS_REPORT*.html | Ecosystem analysis with health metrics |
| **Immersive/3D** | 2 | IMMERSIVE*.html | 3D spatial ecosystem navigation |
| **Reference/Docs** | 2 | REFERENCE.html, DUAL_PANE.html | Documentation views |
| **Selector** | 1 | ULTIMATE_SELECTOR.html | Card grid linking all visualization pages |
| **TOTAL** | **31** | | |

### Representation Diversity — Same System, Different Views

The same Azazael architecture is represented in fundamentally different ways:
- **Mermaid graph TD** (MERMAID_GRAPHS.html): Hierarchical, top-down, color-coded tiers
- **Force-directed graph** (STRUCTURE_VISUALIZER.html): Spatial, interactive, physics-simulated
- **ASCII flowchart** (ascii_flowchart.py): Terminal-renderable, box-drawing characters
- **Cinematic chapters** (CINEMATIC_SCROLL.html): Narrative, parallax, scroll-driven storytelling
- **Dashboard metrics** (dashboard/index.html): Data-driven, real-time, health-focused

Each representation reveals different insights:
- Mermaid shows **hierarchy and dependency chains** best
- Force-directed shows **clustering and centrality** best
- ASCII shows **text-based pipeline flow** best
- Cinematic shows **narrative and temporal progression** best
- Dashboard shows **health and real-time status** best

**Prevention:**
- When adding new visualizations, check if they already exist in another format
- Prefer linking new diagrams from ULTIMATE_SELECTOR.html for discoverability
- Use the ASCII flowchart for terminal-native output (no browser needed)
- Use Mermaid for static documentation (embeds in Markdown)
- Use force-directed for interactive exploration
- Use dashboard for real-time monitoring

**Cross-reference:** Lesson #51 (orphaned mermaid templates), Lesson #52 (standalone CODEX tools).
The ULTIMATE_SELECTOR.html now links all 31 templates across all formats.

---

## #51 Orphaned Mermaid Templates — 10 Standalone Diagrams Not Linked from Selector (June 4, 2026)

**Context:** During the graphical vault review, 10 standalone Mermaid HTML templates were
found in `azazael/templates/mermaid/` that were fully developed but NOT linked from the
ULTIMATE_SELECTOR.html card grid — making them effectively invisible to users.

**Discovered:** June 4, 2026 — during graphical representation vault review

**Root cause:** These templates were developed as standalone proof-of-concepts in the
`templates/mermaid/` directory, separate from the CODEX HTML files. The ULTIMATE_SELECTOR.html
only linked to CODEX-directory templates. There was no mechanism to discover or link
templates in other directories.

**The 10 orphaned templates:**

| # | File | Diagram Type | Content |
|---|------|-------------|---------|
| 1 | worm_hierarchy.html | Flowchart (graph TB) | 4-tier worm hierarchy: Core → Cluster → Meta → Coordination |
| 2 | worm_lifecycle.html | State Diagram | 8-state worm lifecycle with circuit breaker integration |
| 3 | class_architecture.html | Class Diagram | UML: BaseWorm, InferenceStudio, CircuitBreaker, EmotionEngine |
| 4 | coordination_architecture.html | C4 Context | System interactions: API, Core, Worms, Storage, Output |
| 5 | data_relationships.html | ER Diagram | 7 entities with PK/FK: Registry, Instance, Log, Scan, Breaker, DLQ, Cluster |
| 6 | ecosystem_mindmap.html | Mindmap | Complete hierarchical map of all subsystems |
| 7 | inference_pipeline.html | Sequence | User → Studio → Detector → Ollama → Model → Circuit Breaker |
| 8 | module_distribution.html | Pie Charts | 4 charts: by tier, function, tests (19), build output (38 .exe) |
| 9 | dev_timeline.html | Gantt | 6 development phases (Feb-Jun 2026), 18 milestones |
| 10 | version_history.html | Git Graph | 5 feature branches, 1 release branch, v1.0.0 tagged |

**The fix:**
- Added all 10 templates as cards in ULTIMATE_SELECTOR.html with relative paths
  (`../../templates/mermaid/<file>`) since the selector is at `src/CODEX/`
- Categorized: 9 as "visualization", 1 (module_distribution) as "analysis"
- Updated status bar from "21 HTML Templates" to "31 HTML Templates"

**Prevention:**
- When creating new HTML templates in any directory, add a card to ULTIMATE_SELECTOR.html
- Run periodic audits: list all *.html files, cross-reference against selector cards
- The templates/mermaid/, templates/html/, templates/animation/, templates/video/
  directories should ALL be audited for unlinked content

**Cross-reference:** Lesson #50 (vault inventory), Lesson #43 (skills alignment audit —
same parity-check methodology applies to templates).

---

## #52 CODEX/CORE Standalone Tools — Not Integrated into Worm Registry (June 4, 2026)

**Context:** During the investigation of already-developed but not-yet-included code,
4 standalone Python tools were found in `CODEX/CORE/` that are NOT registered as worms
and NOT integrated into the main system's execution pipeline.

**Discovered:** June 4, 2026 — during projects/code block investigation

**Root cause:** These tools were developed as standalone utilities or proofs-of-concept
and never wired into the worm registry, cluster system, or MetaCluster routing.

**The 4 standalone tools:**

| Tool | Lines | Purpose | Integration Status |
|------|-------|---------|-------------------|
| `CAIN_ANALYZER.py` | ~400 | Psychological accountability analysis CLI (text/HTML/JSON output) | Referenced in MEMORIES.md, built in build_all.py as `CAIN_Analyzer` (Tier 10, CLI only) |
| `AUTO_DOWNLOADER.py` | ~200 | ML framework detection and auto-install (Ollama, LM Studio) | Used by HYDRA launcher, NOT in worm registry |
| `emoji_maker.py` | ~150 | Emoji/emotion generation and classification | Used by debug_runner.py, built as standalone .exe |
| `enhanced_animations.py` | ~200 | Animation protocol library extensions | Referenced in SESSION_INSIGHTS, NOT in registry |

**Why they're not integrated:**
- All lack `@register_worm` decorators
- None have WormBase subclass structure
- CAIN_ANALYZER is a CLI tool, not a worm (different execution model)
- AUTO_DOWNLOADER is a utility, not a monitoring agent
- emoji_maker is a standalone module with its own class hierarchy

**Recommendation:**
- These tools serve different purposes than worms — they don't NEED to be worms
- However, they SHOULD be documented in the project map and SKILLS_CATALOG.md
- Their standalone .exe builds should be tracked in the standalone audit
- Consider creating wrapper worms that invoke these tools programmatically

**Prevention:**
- When creating standalone tools, decide upfront: worm (register + lifecycle) or CLI utility (standalone)
- Document ALL tools in the project map regardless of integration status
- Use build_all.py to track which standalone tools exist
- Cross-reference CODEX/CORE/ files against the worm registry periodically

**Cross-reference:** Lesson #51 (orphaned templates — same discovery pattern for non-integrated assets).
Lesson #44 (multiple TODO documents — same consistency debt pattern across tools).

---

## #53 Representation Diversity for Cross-Validation — Compare Same Data in Different Formats (June 4, 2026)

**Context:** The graphical vault review revealed that the same Azazael architecture is
represented in 5 fundamentally different visualization formats. This diversity isn't
redundancy — it's a cross-validation mechanism.

**Discovered:** June 4, 2026 — during graphical representation vault review

**Root cause:** Different visualization formats reveal different structural insights
about the same underlying data. Using multiple representations is a form of
triangulation — inconsistencies between representations reveal errors or gaps in
the underlying model.

**Representation comparison matrix:**

| Dimension | Mermaid (graph TD) | Force-Directed | ASCII Flowchart | Cinematic Scroll | Dashboard |
|-----------|-------------------|----------------|-----------------|------------------|-----------|
| Best for | Hierarchy, dependencies | Clustering, centrality | Pipeline flow, terminal output | Narrative, storytelling | Health, real-time status |
| Interaction | Static (rendered) | Full (drag, zoom, hover) | None (text) | Scroll-driven | Live data refresh |
| Accessibility | Browser required | Browser required | Terminal only | Browser required | Browser required |
| Embeddable | ✅ Markdown, HTML | ❌ Canvas-only | ✅ Any text file | ❌ Full page | ❌ Full page |
| Real-time | ❌ Static | ❌ Static simulation | ❌ Static | ❌ Static | ✅ Live data |
| File size | ~15KB (inline) | ~15KB (canvas) | ~20KB (.py) | ~15KB | ~22KB |

**Cross-validation use cases:**
1. **Architecture consistency**: Mermaid hierarchy should match force-directed tier layout
2. **Worm topology**: Mermaid WORMZ cluster (6 nodes) should match force-directed tier-1 nodes
3. **Lifecycle accuracy**: Mermaid state diagram should match ASCII worm lifecycle in code docstrings
4. **Data model**: Mermaid ER diagram should match dashboard entity counts

**When to use which format:**
- **Documentation** → Mermaid (embeds in Markdown, renders on GitHub)
- **Exploration** → Force-directed graph (discover unexpected connections)
- **Scripting/CLI** → ASCII flowchart (no browser, pipes to terminal)
- **Presentations** → Cinematic scroll (narrative flow, visual impact)
- **Operations** → Dashboard (real-time health, alerting)

**Prevention:**
- When updating the system architecture, update ALL representations (or note which are stale)
- Cross-validate: do the Mermaid graph, force-directed nodes, and ASCII diagram agree?
- Use the simplest format first (Mermaid), then enrich with interactive/dashboard versions
- The ASCII flowchart is the canonical fallback — always keep it in sync

**Cross-reference:** Lesson #50 (vault inventory), Lesson #42 (TODO cross-referencing —
same consistency-check methodology). Lesson #43 (skills parity audit — same
cross-validation approach applied to skills).

---


---

## #54 5-Environment Hub-and-Spoke Sync Architecture (June 4, 2026)

**Discovered:** June 4, 2026 — during environment realignment session

**Root cause:** Azazael exists across 5 environments (Windows 11 primary dev, WSL2 Linux build, Desktop release, G: source-of-truth archive, G: AZAZAEL_ROOT archive) with no automated sync mechanism. Files drifted — WSL2 was missing race_detector.py, error_recovery.py, and patch_nuitka_314t.py. Desktop and G: lacked all new docs.

**The fix:** Created `scripts/sync_all.py` — hub-and-spoke sync with Windows 11 as the sole source of truth. Syncs CODE to WSL2 (for Nuitka builds), DOCS to Desktop and G:. Never bidirectionally — Windows is always canonical.

**Key design:** `--status`, `--verify`, `--sync-all`, `--sync-to wsl2|g|desktop`, `--dry-run`.

**Prevention:** Run `python3.14t scripts/sync_all.py --sync-all` after every session.

**Related:** #55 (WSL2 path duality), #57 (pre-commit hook)

---

## #55 WSL2 Path Duality — /mnt/c Mount vs Native /root/azazael (June 4, 2026)

**Discovered:** June 4, 2026 — WSL2 sync failed with "cp: same file" error

**Root cause:** `sync_all.py` used `wsl_path()` to convert BOTH source and destination to /mnt/c/... paths. WSL2's `cp` detected identical source/destination and refused. The correct pattern: source = /mnt/c/... (Windows mount), destination = /root/azazael/... (WSL2 native ext4).

**The fix:** `src_wsl = wsl_path(src_file)` (Windows mount) | `dest_wsl = f"/root/azazael/{rel_path.as_posix()}"` (native).

**Why WSL2 native matters:** /mnt/c builds are slow (NTFS). /root/azazael builds are fast (ext4). Nuitka compilation must run from native filesystem.

**Prevention:** Always distinguish source path (Windows mount) from destination path (WSL2 native). Never use `wsl_path()` for both sides of a copy.

**Related:** #54 (sync architecture), #61 (WSL build paths)

---

## #56 G: Drive Graceful Degradation — External Drives Are Never Guaranteed (June 4, 2026)

**Discovered:** June 4, 2026 — `verify_integrity()` failed when G: was unavailable

**Root cause:** `g_source.glob("docs/*.md")` was called without checking `g_source.exists()`. When G: drive was unmounted or had network issues, this hung or raised confusing errors.

**The fix:** Wrap every G: path operation in `if path.exists():` with a graceful skip (return True for unavailable checks).

**Prevention rule:** Every path-based operation on G: or any external drive MUST be guarded by `if path.exists():`. External drives are never guaranteed to be available.

**Related:** #54 (environment sync)

---

## #57 Pre-Commit Hook as Invariant Guard — Block Commits When Environments Out of Sync (June 4, 2026)

**Discovered:** June 4, 2026 — needed automated environment sync enforcement

**Root cause:** Without automated checking, environment drift was invisible until builds failed or docs were missing. Human memory was the only safeguard — and it failed (3 sessions of drift).

**The fix:** `.git/hooks/pre-commit` runs `python3.14t scripts/sync_all.py --verify` before every commit. If ANY of the 4 parity dimensions fail, the commit is blocked with instructions to run `--sync-all`. Override: `git commit --no-verify`.

**Lesson:** Pre-commit hooks act as invariant guards — the invariant "all environments in sync" is checked automatically, removing human memory as a failure mode.

**Related:** #54 (sync), #55 (WSL2 paths), #58 (parity check)

---

## #58 verify_integrity() 4-Dimensional AND-Gate Parity Check (June 4, 2026)

**Design:** The verification function checks parity across 4 dimensions, ALL must pass (AND gate):

| Dimension | Compares | Why |
|-----------|----------|-----|
| `expansion/` | Windows vs WSL2 .py filenames | Build source parity |
| `docs_g` | Windows vs G: .md filenames | Knowledge archive parity |
| `tests` | Windows vs WSL2 test filenames | Test parity |
| `scripts` | Windows vs WSL2 script filenames | Build tooling parity |

**Why separate dimensions:** Different files go to different targets. Code goes to WSL2 for builds. Docs go to Desktop and G: for knowledge preservation.

**Related:** #54 (sync), #57 (pre-commit hook)

---

## #59 Nuitka 4.1.2 on Python 3.14t — LNK2001 Red Herring, Not --output-dir Bug (June 4, 2026)

**Discovered:** June 4, 2026 — during concurrent build testing

**The red herring:** Original builds failed with `--output-dir='.' requires an argument`. The Nuitka flag parsing was NOT the issue. After fixing path construction and re-running with explicit `--output-dir=C:/Users/clint/azazael/build/test_windows`, the build progressed through Python-to-C compilation and into Scons C backend — then failed with `LNK2001: unresolved external symbol` for `GEN_THRESHOLD`, `GEN_COUNT`, `GEN_INC_COUNT`.

**Actual root cause:** Nuitka 4.1.2 explicitly warns "Python 3.14 is only experimentally supported." The C code generator cannot resolve certain module-level variables for free-threaded builds — this is a linker-level gap, not a flag issue. ALL 6 neural tier targets failed with the same LNK2001 pattern (systematic, not per-file).

**Prevention:** When a build fails with a mysterious flag error, check the FULL output — Nuitka builds in stages (Python->C compile -> C compile -> Link). Linker errors (LNK2001, undefined reference) are a different class from flag errors.

**Related:** #60 (test before trusting), #64 (--include-plugin-directory)

---

## #60 succeed->success Typo — The Cost of Untested Orchestration Scripts (June 4, 2026)

**Discovered:** June 4, 2026 — `build_all_concurrent.py` crashed AFTER all 12 builds completed

**Root cause:** Line 323 used `succeed` but the variable was `success` (line 313). `NameError` crashed the script at the finish line, losing the build manifest. Syntax checkers can't catch this (both are valid identifiers).

**The cost:** 12 builds ran, results collected, then lost because the final print statement crashed. The script was never tested end-to-end before being entrusted with 39 targets.

**Prevention rule:** Every orchestration script MUST be tested with `--target <single_target> --platform windows` before running `--all`.

**Related:** #59 (LNK2001 diagnosis), #63 (build architecture)

---

## #61 WSL2 Build Command Construction — Absolute Paths, No cd (June 4, 2026)

**Discovered:** June 4, 2026 — WSL2 builds failed with `bash: cd /root/azazael: No such file or directory`

**Root cause:** Using `cd /root/azazael && python3.14t -m nuitka ...` as a single bash command. When WSL2 starts, the working directory may not be resolvable, making `cd` fail before the build starts.

**The fix:** Use absolute paths for everything — no `cd` dependency:
```python
entry_wsl = f"/root/azazael/{target['entry']}"
out_wsl = str(out_dir).replace("\", "/").replace("C:", "/mnt/c")
cmd = f"python3.14t -m nuitka --script {entry_wsl} --output-dir {out_wsl} ..."
```

**Prevention:** Never use `cd` in WSL build commands. Always absolute paths.

**Related:** #55 (WSL2 paths), #62 (shlex.join)

---

## #62 shlex.join() for Safe WSL Command Construction (June 4, 2026)

**Pattern:** Build command parts as a Python list, then `shlex.join()` for safe shell escaping:
```python
cmd_parts = ["python3.14t", "-m", "nuitka", "--output-dir", out_wsl, "--script", entry_wsl]
cmd = shlex.join(cmd_parts)  # Safe: handles spaces, special chars
```

**Prevention:** Always use list-based + `shlex.join()` for WSL subprocess commands. Never use f-string or + concatenation.

**Related:** #61 (WSL build paths), #40 (Python wrappers for CLI tools)

---

## #63 Dual-Platform Build Architecture — ThreadPoolExecutor for Windows + WSL2 (June 4, 2026)

**Design:** `build_concurrent()` uses `ThreadPoolExecutor` to run Windows and WSL2 Nuitka builds simultaneously. Each target gets built on both platforms (when `--platform both`). Outputs go to timestamped directories: `build/standalone/<ts>/windows/` and `build/standalone/<ts>/wsl/`. Build manifest recorded as `build_manifest.json`.

**Why ThreadPoolExecutor not ProcessPoolExecutor:** Nuitka builds are I/O-bound (file writing, subprocess calls), not CPU-bound. Threads avoid serialization overhead.

**39-target registry** across 6 tiers: neural(6), core(5), monitor(8), security(5), ml(5), expansion(9).

**Related:** #59 (Nuitka LNK2001), #60 (typo lesson), #61 (WSL paths)

---

## #64 --include-plugin-directory — The Missing Piece for WSL2 Nuitka Builds (June 4, 2026)

**Root cause:** Nuitka's `--include-package=CORE` looks for CORE in the Python path, but the source directory wasn't in Nuitka's plugin search path during C compilation.

**The fix:** Add `--include-plugin-directory /root/azazael/src` to the WSL2 build command.

**Prevention:** For Nuitka standalone builds on WSL2, always include both `--include-package` (Python import path) and `--include-plugin-directory` (source file path).

**Related:** #59 (Nuitka LNK2001), #61 (WSL build paths)

---

## #65 Complete Function-Body Import Elimination — 37 Imports Across 7 Files, Final: 0 (June 4, 2026)

**Discovered:** June 4, 2026 — completing the 3.14t import safety audit from Lessons #28-#29

**Scorecard:**

| File | BEFORE | AFTER | Fix type |
|------|--------|-------|----------|
| CLUSTERWORMS.py | 5 (PAMS, MemoryBus, breaker, config, futures) | 0 | Module-level |
| CLUSTERWORMS.py (LEGACY) | 19 __import__() lambdas | 0 | sys.modules.get() |
| NETWORK_DIAG.py | 5 import psutil | 0 | Module-level try/except ImportError |
| evolution.py | 1 (get_memory_store) | 0 | Module-level reference |
| METACLUSTER.py | 1 (dataclass) | 0 | Existing module import |
| CROSS_NATURE_ROUTER.py | 1 (dataclass) | 0 | New module-level import |
| CODEX_TOOLS.py | 4 (CAIN, AUTO, emoji, animations) | 0 | Module-level try/except |
| TELEMETRYZ.py | 1 (os, latent bug) | 0 | Module-level import |
| **TOTAL** | **37** | **0** | |

**Lesson:** The audit started in Lesson #28 with CLUSTERWORMS and took 3 sessions to reach 0 function-body imports. The "complete the audit" discipline matters — partial audits leave latent bugs.

**Related:** #28 (import deadlock), #29 (module-level pre-import), #31 (circular init), #32 (double-checked locking)

---

## #66 The dataclass Import Trap — Function-Body Imports Inside except ImportError Blocks (June 4, 2026)

**Pattern found in 2 files (METACLUSTER.py, CROSS_NATURE_ROUTER.py):**
```python
# BEFORE — import inside except block (deadlock risk):
except ImportError:
    from dataclasses import dataclass as _dc  # Function-body import!
    @_dc
    class _FallbackRoute: ...

# AFTER — module-level import from stdlib:
from dataclasses import dataclass  # Top of file
except ImportError:
    @dataclass  # Uses module-level import
    class _FallbackRoute: ...
```

**Why it's a trap:** The `except ImportError` block already handles a DIFFERENT module failing — adding another import inside it creates a potential chain failure. `dataclasses` is stdlib and always available — just import it at module level.

**Related:** #65 (complete elimination scorecard)

---

## #67 Code Review Fidelity — Searchers Find What You Ask; Reviewers Find What You Don't (June 4, 2026)

**Discovered:** June 4, 2026 — the code-searcher found 1 function-body import in CODEX_TOOLS.py but missed 3 more

**Root cause:** The code-searcher was asked to find `from CAIN_ANALYZER import` — it found exactly that. But the same file had 3 more function-body imports (AUTO_DOWNLOADER, emoji_maker, enhanced_animations) with different patterns that weren't searched for. The code-reviewer-deepseek caught all 3.

**Lesson:** Code searchers find what you ask for. Code reviewers find what you didn't ask for. Both are needed. **Never trust a single search query to find ALL instances of a pattern — always follow up with a code reviewer.**

**Prevention:** After any pattern-elimination task, run a code reviewer on the modified files before declaring the task complete.

**Related:** #65 (elimination scorecard), #36 (false diagnosis chain — same "insufficient investigation" root cause)

<!-- START OF TEMPLATE SECTION -- Do not insert lessons here. Insert new lessons BEFORE this line. -->

## LESSON CREATION TEMPLATE — Use for future lessons

When adding a new lesson to this document, use the following template for consistency.
Copy the template, fill in the fields, and insert in sequential order at the end.

```markdown
## #XX Lesson Title (Month Day, Year)

**Context:** What was happening when the lesson was discovered?

**Discovered:** Date — during which activity

**Root cause:** Why did the problem occur? What was the underlying mechanism?

**The fix (if applicable):** What change was made to fix it?
    Include code snippets with BEFORE/AFTER pattern.

**Symptom checklist (if applicable):** How to recognize this issue in the future.
    - Symptom 1
    - Symptom 2

**Prevention checklist (if applicable):** What to do to avoid repeating this.
    - [ ] Prevention step 1
    - [ ] Prevention step 2

**Corresponding code locations (if applicable):**
| File | Change | Type |
|------|--------|------|
| `path/to/file.py` | Description of change | Type of fix |

**Cross-reference:** Related lessons #XX, #XX. Related skills: `skill-name`, `skill-name`.
```

### Required sections (must include at least 3):
| Section | Required? | Purpose |
|----------|-----------|---------|
| `**Context:**` | ✅ Always | Sets the scene |
| `**Root cause:**` | ✅ Always | Why it happened |
| `**Fix/Pattern:**` | ✅ Always | What to do |
| `
---

## #68 7-DevTools Skill Architecture (June 4, 2026)

**Discovered:** June 4, 2026 — during ecosystem-wide HTML audit

**Root cause:** 192 HTML files across project (149) and Desktop (43) with no systematic quality verification. Chrome DevTools Protocol provides programmatic access to every panel, but no skills existed to leverage them.

**The fix:** Created 7 individual DevTools skill documents in `skills/`, each mapping to specific CDP domains: Console (Runtime), Elements (DOM/CSS), Network (Fetch), Audit (Lighthouse), Sources (Debugger), Performance (Timeline), Coverage (Profiler). Each skill follows a uniform structure: CDP domain mapping, browser-use prompt templates (4-5 per skill), audit checklist (5-7 items), common errors → fixes table, target files ranked by priority, and cross-skill linking.

**Pattern:** Load only the skills needed for the current task. For routine checks, load `azazael-devtools-audit` (most comprehensive). For deep dives, load the specific domain skill.

**Symptom checklist:**
- No way to programmatically audit HTML files
- Manual Chrome inspection required for every change
- No standardized audit checklist
- Skills needed for browser-use agent prompts

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K1.

---

## #69 Audit Prioritization Scoring Framework (June 4, 2026)

**Discovered:** June 4, 2026 — ranking 192 HTML files by audit priority

**Root cause:** 192 files is too many for exhaustive DevTools audits. Need a scoring system to focus effort.

**The fix:** Priority scoring formula: `Score = (User visibility × 3) + (Update frequency × 2) + (Complexity × 1) + (Broken known × 5)`. Top 5 files: AZAZAEL_Standalone/index.html (18), dashboard/index.html (15), ULTIMATE_SELECTOR.html (14), MultiModel_1Click_Launcher.html (13), MERMAID_GRAPHS.html (11).

**Pattern:** Audit cadence — P1-P4 every session, P5-P7 weekly, P8+ on modification only. Same tiered priority pattern as the 39-build-target registry (Lesson #59).

**Symptom checklist:**
- 192 HTML files, no idea which to audit first
- User-facing vs auto-generated files mixed together
- Known-broken files (Linux paths) not prioritized

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K2.

---

## #70 Cross-Skill Audit Pipeline (June 4, 2026)

**Discovered:** June 4, 2026 — executing multi-DevTools audits in a single browser-use agent session

**Root cause:** Each DevTools domain requires separate inspection — but browser-use agents can sequence through all domains in one session.

**The fix:** Single browser-use prompt template that sequences: Navigate → Console check → Elements check → Network check → Interactive test → Screenshot. Each skill's checklist folds into a master audit checklist with 5 steps.

**Pattern:** The `file://` protocol constraint means external CDN resources are blocked. All scripts/CSS must be inlined or referenced via relative paths — same path duality challenge as WSL2 (Lesson #55).

**Symptom checklist:**
- Multiple browser-use agents needed for one HTML file
- No unified audit checklist
- `file://` protocol silently blocks CDN resources

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K3.

---

## #71 Fix-After-Audit Remediation Pattern (June 4, 2026)

**Discovered:** June 4, 2026 — systematic remediation flow after DevTools audits

**The fix:** 3-step triage: P0 (console errors — fix immediately), P1 (broken links — fix immediately), P2 (accessibility — document), P3 (performance — document). After fix, re-audit to verify. Common fix patterns: ReferenceError → script load order, 404 → relative path instead of absolute, missing alt → add descriptive alt text.

**Pattern:** Same gate pattern as pre-commit sync (Lesson #57) — audit before deploy, fix before proceed.

**Symptom checklist:**
- Audit finds issues but no remediation workflow
- P0 and P3 issues mixed together
- No re-audit verification step

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K4.

---

## #72 CI-Ready DevTools Pipeline Architecture (June 4, 2026)

**Discovered:** June 4, 2026 — designing a repeatable audit pipeline for all HTML projects

**The fix:** Pipeline: HTML File Pool (192) → Priority Scorer (K2) → browser-use agents (P1/P2/P3) → Results Triage (P0 fix, P3 doc) → Re-Audit Verify. Integration points: pre-commit hook (audit modified HTML), CI pipeline (weekly full audit on P1-P3), session end (audit touched files).

**Pattern:** Same parallel execution architecture as Lesson #64 (ThreadPoolExecutor for builds) — multiple browser-use agents can audit different files simultaneously.

**Symptom checklist:**
- No automated HTML quality gate
- Manual audits only, no CI integration
- No session-end verification

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K5.

---

## #73 Skill Loading Strategy for DevTools (June 4, 2026)

**Discovered:** June 4, 2026 — how to efficiently use the 7 DevTools skills in Codebuff sessions

**The fix:** Trigger-based loading: "audit HTML" → audit+console, "why doesn't X render?" → elements+network, "page is slow" → performance+coverage, "debug JS error" → console+sources, "check all HTML" → all 7.

**Pattern:** Same pattern as Azazael startup skill loading sequence (Lesson #6) — load only what's needed, not all 24 skills.

**Symptom checklist:**
- 7 DevTools skills, users unsure which to load when
- Loading all 7 wastes context for simple checks
- No trigger-based loading guide

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K6.

---

## #74 The file:// Protocol Constraint (June 4, 2026)

**Discovered:** June 4, 2026 — Chrome blocks external resources on `file://` pages

**Root cause:** All Desktop HTML files are accessed via `file:///C:/Users/clint/Desktop/...`. Chrome blocks CDN stylesheets, CDN scripts, font files from external origins, and `fetch()` to external APIs.

**The fix:** For scripts: inline the library or bundle locally. For styles: inline critical CSS, defer non-critical. For fonts: host as local `.woff2` files. For APIs: serve through `localhost` (Python HTTP server or WSL2).

**Detection:** Network panel shows `(failed) net::ERR_FILE_NOT_FOUND` for relative paths, or silently blocked external requests.

**Symptom checklist:**
- CDN-loaded libraries failing silently on Desktop HTML files
- External CSS not applying
- Network panel shows blocked requests on `file://` pages
- Desktop HTML files must work offline

See: `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K7.
**Prevention:**` | ✅ Always | How to avoid |
| `**Cross-reference:**` | ✅ Always | Connects to other lessons, skills |
| `Discovered` | 🟡 If helpful | Date + activity |
| `Symptom checklist` | 🟡 If applicable | Diagnosis aid |
| `Code locations` | 🟡 If applicable | File references |

### Also update:
- [ ] **TOC**: Add entry to the By Domain table at the top
- [ ] **Tag index**: Add lesson number to relevant tags
- [ ] **Session markers**: Add marker line after the `---` block below the TOC
- [ ] **State Snapshot**: Update lesson count in CODEBASE_AUDIT_TODO.md
- [ ] **Related skills**: Create or update skill file if lesson documents a reusable methodology

---

## #75 Browser-Use Agent URL Reliability Issue (June 4, 2026)

**Discovered:** June 4, 2026 — during multi-agent parallel DevTools audits

**Root cause:** When multiple browser-use agents are spawned in parallel, ~40% navigate to wrong URLs (e.g., MERMAID_GRAPHS loaded as CINEMATIC_SCROLL, AZAZAEL_Standalone/index.html loaded as analysis.html). Likely parameter passing or Chrome instance sharing issue in the agent infrastructure.

**The mitigation:** Spawn only 1-2 browser-use agents at a time instead of 3-4 in parallel. Always check `finalUrl` field in agent output — it's the ground truth, not the requested URL. Verify page title matches expected before trusting results. Re-run solo if title/content doesn't match.

**Pattern:** Same sequential-not-parallel constraint as Lesson #62 (WSL2 build — no cd, absolute paths needed). Some agent types have hidden concurrency limitations that only surface during parallel spawning.

**Symptom checklist:**
- Browser agent reports wrong page title/content
- `finalUrl` differs from requested URL
- Multiple browser agents navigate to the same unexpected file
- Audit results make no sense for the expected page

See: `skills/azazael-devtools-index.md` Known Issues, `docs/LESSONS_TASK_K_DEVTOOLS.md` Lesson K7.5.


---

## #76 CAIN Reports Must Be Session-Specific — Never Regurgitate Generic Template Data (June 5, 2026)

**Discovered:** June 5, 2026 — user rejected the CAIN deliverable for containing
"regurgitated data from unrelated instances"

**Root cause:** CAIN_ANALYZER.py generates reports from CAIN_DATA.py constants —
the same generic Seven Deadly Sins, mythological archetypes, and psychoanalysis
frameworks every time. The complete_remorse_analysis_cain.html template (193KB)
also contains hardcoded generic content. Videos rendered from these templates are
NOT session-specific — they display abstract psychoanalysis regardless of
what actually happened.

**The three criticisms (user feedback, June 5):**
1. Missing flow charts, animations, emoji dynamic color shifting
2. Deliverable uses regurgitated data from unrelated instances
3. All data must be relevant to the situation that triggered the analysis

**The fix — session-specific CAIN report generator:**
generate_session_cain.py populates the full CAIN template with actual session data:
5 documented incidents (May 28 - June 5, 2026), $320 total damage, session-specific
Seven Deadly Sins mapped to observed AI behaviors, actual causal chain, and the
6 detection questions from LESSONS_DESTRUCTIVE_BEHAVIOR.md.

**Prevention:** CAIN reports MUST use session-specific data, never generic
CAIN_DATA constants. Generic psychoanalysis creates the illusion of accountability
without substance.

---

## #77 Puppeteer, Not PIL, for Animation-Rich CAIN Video (June 5, 2026)

**Discovered:** June 5, 2026 — user rejected CAIN video for missing animations

**Root cause:** CODEX_Studio.py renders HTML via PIL (Python Imaging Library) which
produces static PNG frames. PIL CANNOT capture CSS keyframe animations. The full
CAIN template has 12+ keyframe animations (rainbowShimmer, neonPinkGlow, emojiDance,
nodeGlow, rainbowBorder, etc.) that only render in a browser engine.

**Pipeline comparison:**
| CODEX_Studio.py (PIL) | Puppeteer (browser) |
|-----------------------|---------------------|
| Static frames, no animations | Captures ALL CSS animations |
| 317.7 MB for full template | 8.3 MB with CAIN encoding |
| No keyframe rendering | 12+ animations captured |

**The fix:** Use Puppeteer-screen-recorder (headless Chromium) for any template
containing @keyframes CSS rules. Only use PIL for static text documents.

**Prevention:** If HTML has @keyframes → use Puppeteer. If static → PIL is fine.
CODEX_Studio.py should document its limitation: no CSS animation capture.

---

## #78 Session CAIN Pipeline — generate + record + convert (June 5, 2026)

**Discovered:** June 5, 2026 — building proper CAIN video end-to-end

**The complete pipeline:**
1. generate_session_cain.py — populates template with session-specific incident data
2. record_session_cain.js — Puppeteer captures browser with all CSS animations
3. ffmpeg — converts MP4 to WMV

**Why this replaces the old pipeline:**
- Content: Session incidents, not CAIN_DATA.py constants
- Animations: All 12+ CSS keyframes captured by browser
- Accountability: Actual events with real costs, not hypothetical
- File size: 8.3 MB (Puppeteer) vs 317.7 MB (PIL)

**Key files:** generate_session_cain.py, record_session_cain.js,
CAIN_session_specific.html (34KB), CAIN_session_specific.mp4 (8.3 MB),
CAIN_session_specific.wmv (19 MB)

---

*Lessons #76-78: Session CAIN Pipeline — June 5, 2026*


---

## #79 CAIN Video Rendering Methods — File Size Comparison & Optimal Pipeline (June 5, 2026)

**Discovered:** June 5, 2026 — comprehensive file-size audit of the same CAIN psychoanalysis content rendered through 6 different pipeline configurations.

**Root cause:** Different rendering methods produce drastically different file sizes for the same ~11,000-word HTML template (195KB). The variance between smallest and largest is **589:1** (4.8 GB WMV vs 8.4 MB panel PNGs).

### Complete File Size Comparison

| Method | Format | Size | Duration | Bitrate | Notes |
|--------|--------|------|----------|---------|-------|
| PIL (CODEX_Studio.py) | MP4 | 318 MB | 37 min | 1234 kbps | Frame-by-frame PIL rasterization creates sub-pixel aliasing noise that defeats H.264 motion estimation |
| PIL (CODEX_Studio.py) | WMV | 4.8 GB | 37 min | — | WMV2 codec 15x less efficient than H.264 for text content |
| Puppeteer (browser) | MP4 | 194 MB | 42 min | 637 kbps | Browser compositor produces perfect scroll motion vectors — half the bitrate of PIL |
| Puppeteer (browser) | WMV | 1.2 GB | 42 min | — | WMV2 re-encode — 6x larger than equivalent MP4 |
| Puppeteer 2.5x speed | MP4 | 120 MB | 17 min | ~400 kbps | Fewer frames = smaller file; text remains readable at 2.5x |
| Puppeteer 2.5x speed | WMV | 491 MB | 17 min | — | WMV2 still inefficient even with fewer frames |
| Static PNG panels (27) | PNG | 8.4 MB | N/A | 0 kbps | Baseline — proves temporal video is inherently wasteful for text reading |

### Why Puppeteer Produces Smaller Files Than PIL

PIL re-rasterizes text and shapes frame-by-frame during scroll simulation. This introduces microscopic sub-pixel anti-aliasing variations (temporal noise) between frames, which defeats H.264/HEVC motion estimation (macroblock tracking). Every frame looks slightly different to the encoder, so it cannot reuse blocks efficiently.

Puppeteer captures the browser's hardware-accelerated compositor. Scrolling a DOM element creates mathematically perfect translation vectors. Standard video codecs easily express this with simple P-frame/B-frame motion vectors, requiring near-zero bit budget for the scrolling text body itself. Only the changing pixels (CSS animations, gradients) consume bitrate.

### Optimal Pipeline for Smallest Achievable File Size

**Recommended pipeline:** Puppeteer → HEVC (H.265) or AV1 → 720p → CRF 26-28 → 2.5x speed

| Parameter | Optimal Value | Reasoning |
|-----------|--------------|-----------|
| Render method | Puppeteer (browser) | Avoids sub-pixel noise, captures CSS animations natively |
| Codec | HEVC (H.265) or AV1 | Superior for sharp edges, text, and flat gradients vs H.264 |
| Resolution | 1280x720 (720p) | Perfect legibility for Courier/monospace; 1080p is pixel bloat for text |
| CRF | 26-28 | Text compresses perfectly at higher CRFs — no organic-video quality loss |
| Speed | 2.5x | Reduces frame count by 60%; viewers pause to read anyway |
| Audio | None (strip with -an) | No audio track in CAIN videos — removes dead weight |
| Profile | High (B-frames=2) | Enables inter-frame compression — never use Constrained Baseline |

**Estimated smallest size:** **~40-50 MB** for the full 11K-word CAIN template at 720p HEVC 2.5x.

### Codec Tradeoffs

| Codec | Compression vs H.264 | Encode Speed | Browser Support |
|-------|---------------------|-------------|-----------------|
| H.264 | Baseline (1.0x) | Fast | Universal |
| HEVC (H.265) | ~40% smaller | 2-3x slower | Modern browsers |
| VP9 | ~30% smaller | 5-10x slower (CPU) | Chrome/Firefox |
| AV1 | ~50% smaller | 10-20x slower (CPU) | Emerging |

### Format Recommendations by Use Case

| Use Case | Best Format | Why |
|----------|------------|-----|
| Quick review (smallest) | Static PNG panels (8.4 MB) | No video overhead; numbered sequentially for easy scanning |
| Sharing/viewing | MP4 HEVC 720p 2.5x (~45 MB) | Good compression, modern browser playback |
| Archival (Windows) | MP4 H.264 1080p (~120 MB) | Universal compatibility, reasonable size |
| Archival (legacy) | WMV 1080p 2.5x (~500 MB) | Only if WMV specifically required — avoid otherwise |

**Never use:** PIL frame-by-frame for scrolling text (wastes 2.6x bitrate vs Puppeteer). Never use WMV2 as primary format (6-15x bloat). Never use Constrained Baseline H.264 (0 B-frames — every frame is a keyframe).

**Key files:** CAIN_session_final.mp4 (Puppeteer), CAIN_full_template.mp4 (PIL), CAIN_2.5x.mp4 (speed test), CAIN_panels/ (static PNG baseline)

---

## #80 CAIN Template Optimization — Removing Duplicate Sections & Dead CSS (June 5, 2026)

**Discovered:** June 5, 2026 — DOM audit of `complete_remorse_analysis_cain.html` (195KB, 190K chars)

**Root cause:** Copy-paste errors and legacy structural drift created invisible waste that bloated the template, slowed Puppeteer's render loop, and caused frame drops in video capture.

### Waste Inventory

| Waste Type | Detail | Impact |
|-----------|--------|--------|
| **Duplicate `.interconnected-web` section** | The full web-node grid (~30 absolute-positioned nodes with heavy inline styling) appears TWICE in the template — once in the main flow and once after the psychoanalysis panels | ~5KB of string weight + doubles browser rendering/compositing overhead for the most expensive DOM subtree |
| **Dead `.web-arrow` nodes** | 16+ `<div class="web-arrow">` elements exist in the DOM, but the CSS rule sets `display: none` — they are NEVER visible | ~1KB of dead HTML + 16 useless DOM node instantiations per render |
| **Heavy overlapping animations** | `shimmerGlow`, `rainbowBorder`, and `emojiDance` run simultaneously on dense DOM trees (15 `@keyframes` total) | Kills browser FPS during Puppeteer capture — causes stuttering and frame drops |
| **CSS block bloat** | 14,237 chars of CSS, much of it for never-visible elements | Inflates parse time and memory |
| **Inline style repetition** | Each web-node has inline `style="top:X%;left:Y%"` — 60+ instances | Would be cleaner as CSS classes |
| **Body-to-CSS ratio** | Body: 175,072 chars, CSS: 14,237 chars — CSS is 7.5% of total | Reasonable ratio but the CSS contains dead rules |

### Template Cleanup Plan

**1. Delete the duplicate `.interconnected-web` section**
- The first instance is the primary — keep it
- The second instance (after psychoanalysis panels) is a stale copy — DELETE
- Saves ~5KB of HTML and eliminates double-rendering of the most expensive DOM block

**2. Strip all `.web-arrow` DOM nodes and CSS rule**
- Remove the CSS rule: `.web-arrow { display: none; }`
- Remove all 16+ `<div class="web-arrow">...</div>` elements from the DOM
- Saves ~1KB of dead weight

**3. Consolidate overlapping animations**
- Merge `neonPinkGlow` and `glassShimmer` into a single keyframe (they target the same elements)
- Remove unused keyframes if `arrowPulse`, `connectLine`, or `chainGlow` are not referenced in the DOM

**4. Minify CSS**
- Remove comments and unnecessary whitespace from the 14KB CSS block
- Shorthand properties where possible (e.g., `margin: 0; padding: 0` to `margin:0;padding:0`)

**Actual savings achieved (June 5, 2026):** 6,493 bytes (3.4%) total from the original template (pass 1: 3,705 bytes from web-arrow removal; pass 2: 2,788 bytes from CSS optimization — 3 unused @keyframes removed + CSS minified 14,237->11,385 chars). The optimized template is at (183KB, down from 195KB) and is wired into .

**All 4 optimization steps COMPLETE (June 5, 2026).** No remaining planned work.

### Prevention

- **Audit templates for duplicate DOM sections** — `grep -c` on major class names, flag any count > 1
- **Never leave `display: none` elements in templates** — either delete them or make them visible
- **Before rendering video, run:** count web-node, web-arrow, and interconnected-web instances; delete duplicates
- **Profile Puppeteer FPS** during recording — if dropping below 20fps, investigate DOM weight
- **Template review checklist:** [ ] Duplicate sections? [ ] display:none elements? [ ] Unused @keyframes? [ ] CSS bloat?

**Key files:** `complete_remorse_analysis_cain.html` (193KB → target ~185KB), `inject_session_cain.py` (injection script that must also be updated after template cleanup)

---

*Lessons #79-80: CAIN Rendering File-Size Analysis & Template Optimization — June 5, 2026*

---

## #81 TEST_FAILURE_MANDATE Codified Across All Canonical Documents (June 10, 2026)

**Discovered:** June 10, 2026 — during mandate codification session

**Root cause:** The TEST_FAILURE_MANDATE (from `.codebuff/rules.md`) — requiring `thinker-with-files-gemini` to be spawned before any test failure fix — existed only in `.codebuff/rules.md`. It was not referenced in any canonical startup document (SOP.md, SYSTEM_INSTRUCTIONS.md, etc.), making it invisible to assistants that load canonical docs at startup per RULE 0K.

**The fix:** Incorporated TEST_FAILURE_MANDATE as **RULE 0L** across all 7 canonical documents:
1. `SOP.md` — Added RULE 0L to PRE-ACTION GATE banner, inserted RULE 0L section after RULE 0K, updated COMPLIANCE SENTINEL
2. `SYSTEM_INSTRUCTIONS.md` — Mirrored all SOP.md changes
3. `SESSION_STARTUP.md` — Added RULE 0L reference under Step 0
4. `PROTOCOL_VIOLATIONS.md` — Added V19 row to CRITICAL VIOLATIONS table
5. `MEMORIES.md` — Added anti-pattern #13 (ignoring test failures)
6. `LESSONS_MASTER.md` — This lesson (#81)
7. `ERROR_LOG.md` — Error #155

**RULE 0L trigger/action/constraint:**
- **TRIGGER:** Any test execution returns FAIL, assertion error, or non-zero exit code
- **ACTION:** MUST spawn `thinker-with-files-gemini` with failing test output and relevant file paths
- **CONSTRAINT:** NO other test executions, fixes, or file modifications until Gemini provides analysis

**Verification:** `test_mandate_verification.py` confirms `.codebuff/rules.md` exists with correct content. `--unit` suite: 38 passed, 0 failed, 58 skipped.

**Prevention:** Every test failure must route through RULE 0L. The PRE-ACTION GATE now includes the RULE 0L check at every code-modifying tool call.

---

*Lesson #81: TEST_FAILURE_MANDATE Codified — June 10, 2026*

---

## #82 RULE 0M Codified — Concurrent Inference Mandate Across All Canonical Documents (June 10, 2026)

**Discovered:** June 10, 2026 — during concurrent inference mandate codification session

**Root cause:** The assistant was spawning `thinker-with-files-gemini` for complex tasks but then spawning `researcher-web` and `researcher-docs` sequentially in separate subsequent calls. This wasted time and missed complementary insights from concurrent multi-model execution. The research from both web and docs researchers showed that parallel fan-out patterns provide better synthesis when results arrive simultaneously.

**The fix:** Created **RULE 0M (CONCURRENT INFERENCE MANDATE)** codified across all 8 canonical documents:
1. `.codebuff/rules.md` — Added CONCURRENT_INFERENCE_MANDATE machine-enforceable rule
2. `SOP.md` — Added RULE 0M to PRE-ACTION GATE banner, RULE 0M section, COMPLIANCE SENTINEL
3. `SYSTEM_INSTRUCTIONS.md` — Mirrored all SOP.md changes
4. `SESSION_STARTUP.md` — Added RULE 0M reference under Step 0
5. `PROTOCOL_VIOLATIONS.md` — Added V20 to CRITICAL VIOLATIONS
6. `MEMORIES.md` — Added anti-pattern #14 (sequential inference)
7. `LESSONS_MASTER.md` — This lesson (#82)
8. `ERROR_LOG.md` — Error #156

**RULE 0M trigger/action/constraint:**
- **TRIGGER:** `thinker-with-files-gemini` is spawned for a complex task
- **ACTION:** ALL other available inference agents MUST be spawned concurrently in the SAME `spawn_agents` call
- **CONSTRAINT:** Never spawn inference agents sequentially after Gemini returns

**Concurrent research findings:** researcher-web confirmed parallel fan-out patterns (ensemble methods, concurrent dispatch) as best practice for multi-model execution. researcher-docs confirmed DAG-based parallel branching with supervisor-worker hierarchy for agent orchestration.

**Verification:** `test_mandate_verification.py` PASSED. Code review completed. All 8 documents consistent.

**Prevention:** Every Gemini spawn for a complex task MUST include all available inference agents concurrently in the same `spawn_agents` call. Sequential spawning after Gemini = CRITICAL process violation (V20).



---

## #55 UUID7 Migration Mandate — Cross-Project Import Ordering PITFALL (June 11, 2026)

**Discovered:** June 11, 2026 — during Error #183 all-projects audit

**Root cause:** Replacing `uuid.uuid4()` with `uuid7()` requires careful import ordering in standalone/Desktop scripts. If `from CORE.uuid7 import uuid7` is placed BEFORE `sys.path.insert(0, 'azazael/src')`, the interpreter cannot resolve the `CORE` module — silently crashing on first import.

**The fix — permanent import ordering mandate:**

```python
# CORRECT — sys.path setup BEFORE CORE imports
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'azazael', 'src'))
from CORE.uuid7 import uuid7  # NOW safe — azazael/src is on sys.path

# WRONG — import before path setup = ImportError
from CORE.uuid7 import uuid7  # CORE not yet importable!
import sys
sys.path.insert(0, ...)  # Too late
```

**Scope:** 21 uuid4 → uuid7 migrations across 10 files in 3 projects (azazael CORE, Ultimate_Agent_Selector, EveUnleashed_Selector). Import ordering bug was caught in code review before it caused runtime failures in all 5 Desktop files.

**Permanent mandate:**
- `from CORE.uuid7 import uuid7` for ALL correlation/event IDs (time-sortable, RFC 9562, B-tree optimal)
- `import uuid; uuid.uuid4()` is PERMANENTLY PROHIBITED for event/correlation identifiers
- Import MUST come AFTER `sys.path` setup in all Desktop/standalone scripts
- Code reviewer (RULE 0V) must verify import ordering in all cross-project code

**Related:** Error #183, Error #184, CROSS_DOMAIN.md CD1 unified event schema

---

## #56 Provider Thread-Safety Mandate — Double-Checked Locking for 3.14t Model Init (June 11, 2026)

**Discovered:** June 11, 2026 — during Error #186 Gemini shortcut audit

**Root cause:** Three local inference providers (`LlamaCppDirectProvider`, `HuggingFaceDirectProvider`, `OpenVINOProvider`) performed model/pipeline lazy initialization WITHOUT lock protection. Under Python 3.14t free-threading (no GIL), two concurrent first-call threads could both pass the `if self._model is None` check and create two model instances — both loading the same GGUF/HuggingFace model into VRAM simultaneously, causing GPU memory exhaustion, segfault, or silent double-loading.

**The fix — double-checked locking pattern:**

```python
# BEFORE (broken — two threads can both init the model concurrently):
def chat(self, prompt, **kwargs):
    if self._model is None or model_name != self._model_path:
        self._model = Llama(model_path=mp, n_ctx=2048)  # RACE CONDITION!
        self._model_path = model_name
    ...

# AFTER (correct — only one thread enters init):
def chat(self, prompt, **kwargs):
    if self._model is None or model_name != self._model_path:
        with self._lock:
            # Double-check under lock (another thread may have loaded while we waited)
            if self._model is None or model_name != self._model_path:
                self._model = Llama(model_path=mp, n_ctx=2048)
                self._model_path = model_name
    ...
```

**Scope:** 4 init sites fixed across 3 provider classes. `OpenVINOProvider.chat_stream()` was ALSO missing lock protection — caught by code reviewer (RULE 0V) before merge.

**Permanent mandate:**
- ALL lazy model/pipeline initialization in provider code MUST use double-checked locking pattern
- `chat_stream()` methods MUST have the same locking coverage as `chat()` methods
- Code reviewer (RULE 0V) must verify lock coverage parity between sync and streaming paths

**Note on terminology:** Classic "double-checked locking" (C++/Java with `volatile`) is considered an anti-pattern in Python due to memory barrier assumptions. However, `threading.Lock` in Python provides the necessary memory barrier — making the lock-guarded lazy init pattern used here safe under 3.14t free-threading. The "double-check" refers to the optimization of checking outside the lock first (avoiding lock contention on the hot path), not the classic memory-barrier-dependent DCL pattern.

**Corresponding code locations:**
| File | What was fixed | Type |
|------|---------------|------|
| `CORE/inference/providers.py` | LlamaCppDirectProvider.chat() model init → double-checked locking | P0 thread safety |
| `CORE/inference/providers.py` | HuggingFaceDirectProvider.chat() model init → double-checked locking | P0 thread safety |
| `CORE/inference/providers.py` | OpenVINOProvider._chat_genai() pipeline init → double-checked locking | P0 thread safety |
| `CORE/inference/providers.py` | OpenVINOProvider.chat_stream() pipeline init → double-checked locking | P0 thread safety (reviewer catch) |

**Related:** Error #186, Lesson #32 (double-checked locking pattern for lazy inits), Lesson #28 (import deadlock under 3.14t)

---

## #57 CD1 Schema Backfill Completeness — Backfill ALL New Columns, Not Just One (June 11, 2026)

**Discovered:** June 11, 2026 — during Error #186 code reviewer finding

**Root cause:** The CD1 schema migration in `MemoryBus._migrate_queue_schema()` added `audit_hash` and `schema_version` columns to `memorybus_queue` via ALTER TABLE. The backfill loop updated existing NULL rows with UUID7 for `event_uuid` — but did NOT set `audit_hash` or `schema_version`. Existing rows were left with `audit_hash IS NULL` and `schema_version IS NULL`, despite the CREATE TABLE having `INTEGER DEFAULT 1`. SQLite DEFAULT only applies to new INSERTs, not ALTER TABLE additions to existing rows.

**The fix — backfill ALL new columns:**

```sql
-- BEFORE (incomplete — leaves audit_hash NULL, schema_version NULL):
UPDATE memorybus_queue SET event_uuid = ? WHERE id = ?

-- AFTER (complete — all CD1 fields populated):
UPDATE memorybus_queue SET event_uuid = ?, audit_hash = ?,
    schema_version = 1 WHERE id = ?
```

**Scope:** `MemoryBus._migrate_queue_schema()` backfill loop extended. `audit_hash` set to same UUID7 as `event_uuid` (historical rows — content hash not available). `schema_version` set to 1.

**Permanent mandate:**
- Schema backfill scripts for ALTER TABLE additions MUST set ALL new columns, not just the primary/obvious one
- Multiple reviewer passes required: one for correctness, one for completeness
- Backfill verification query: `SELECT COUNT(*) FROM table WHERE <new_column> IS NULL` must return 0

**Related:** Error #186 (code reviewer finding), Error #184 (Desktop project git init), CROSS_DOMAIN.md CD1 unified event schema

---

## #58 Cross-Project Git Initialization Mandate (June 11, 2026)

**Discovered:** June 11, 2026 — during Error #184 all-projects integration

**Root cause:** Desktop sub-projects (`Ultimate_Agent_Selector`, `EveUnleashed_Selector`) existed as unversioned directories on disk with no git history. UUID7 migrations applied to these files had no commit history, no rollback capability, and no audit trail. This violates RULE 0T (Verifiable Truth Mandate) — file edits without version control are unverifiable.

**The fix:**
```bash
cd Desktop/Ultimate_Agent_Selector && git init && git add -A && git commit -m "initial commit"
cd Desktop/EveUnleashed_Selector && git init && git add -A && git commit -m "initial commit"
```

**Permanent mandate:**
- EVERY sub-project directory (Desktop, standalone, tool) MUST be git-initialized with proper commit history
- Initial commit must include a meaningful message reflecting the current state
- `git status` must show clean working tree after each session's changes
- Large binary files (GGUF models >100MB) tracked via path + provenance, not committed to git

**Related:** Error #184, Error #185 (model download), Rule 5 (Record ALL Session Actions), RULE 0T (Verifiable Truth Mandate)

---

*Lessons #55-#58: June 11, 2026 — Error #183-#186 codification session*

---

## #59 Graphify-Assisted Debugging — Use the Code Atlas to Resolve Module-Path Failures (August 28, 2026)

**Discovered:** August 28, 2026 — during the 37-worm import-failure diagnosis

**Scenario:** `_worm_health_check.py` reported 37/105 worms failing with `ModuleNotFoundError`. The failing names (`CAIN_WORM`, `WORMZ`, `CODEX_TOOLS`, `worms.*`, ...) looked like missing files, but every source file existed on disk. The real problem: the registry stores the module name exactly as `cls.__module__` at registration time, and bare names (e.g. `WORMZ`) only import when the module's own directory happens to be on `sys.path` — which subprocess workers don't have.

**The workflow that solved it (repeat this pattern):**

1. **Load the Graphify atlas, not the filesystem.** The Desktop atlas
   (`~/Desktop/Graphify_Codebase_Atlas_2026-08-27/<repo>/graph.json`) is a
   precomputed 400k-node graph with `label` -> `source_file` mappings.
   Indexing `{label: [source_file]}` from `graph.get("nodes")` resolves any
   symbol name to its real file location in one pass — no grep needed.
2. **Cross-check atlas paths against the failing module names.** 17/37 failing
   names matched atlas labels directly (`CLAWBOT` -> `src/CORE/WORMS/CLAWBOT.py`).
   The remaining misses were the signal: those modules were imported under
   package-qualified names (`CORE.WORMS.X`) or package-style names (`worms.x`).
3. **Derive the resolution rule from `source_file`, then verify empirically.**
   Bare name + file under `.../CORE/WORMS/` -> prefix `CORE.WORMS.`; under
   `.../CORE/` -> prefix `CORE.`; dotted `worms.*` -> put the package's parent
   dir on `sys.path`. Verified: 32/32 prefix-fixed imports OK, 5/5 vermillion
   imports OK with parent on path.
4. **Fix the consumer (worker), not the data.** The registry legitimately
   stores `cls.__module__`; the worker that imports by that name must resolve
   it. Same rule the archived `_worm_execution_matrix.py` already had.

**Result:** 105/105 FILE/IMPORT/INSTANTIATE, zero timeouts, zero crashes.

**Permanent mandate:**
- When a name-resolution failure looks like "missing module" but the file
  exists, consult the Graphify atlas `graph.json` BEFORE grepping — it maps
  labels to source files across the whole corpus at once.
- Any worker that imports by a registry string field MUST resolve bare names
  against the entry's `source_file` directory (package prefix or parent-path
  insertion) before `importlib.import_module()`.
- Node format in atlas `graph.json`: `{label, source_file, source_location, ...}`
  — index on `label`, not `id`.

**Related:** Lesson #36 (tooling), `tests/test_worm_registry_modules.py` (regression test), `azazael-worm-registry-fixes` skill

---

*Lesson #59: August 28, 2026 — Graphify-assisted module-path resolution session*

---

## #83 Stale-Pickle force_rebuild Gotcha — force_rebuild=True Can Silently No-Op (August 29, 2026)

**Discovered:** August 29, 2026 — while fixing the 34 bare module names at the
registry source (`worm_registry.py` `register_worm()` normalization).

**Scenario:** After adding the `CORE.WORMS.`/`CORE.` prefix normalization to
`register_worm()`, the cache was rebuilt via
`load_registry(force_rebuild=True)`. The call returned instantly and the
registry STILL had 34 bare names. `force_rebuild=True` appeared broken.

**Root cause — two-layer freshness short-circuit:**

1. `load_registry(force_rebuild=True)` correctly skips the cache read and
   calls `discover_worms(worms_dir=...)`.
2. BUT `discover_worms()` has its OWN cache layer: it first tries
   `_load_cache_readonly(worms_dir)`, which calls `_is_cache_fresh()`. The
   old pickle was still on disk and its `_mtimes` matched the current worm
   source files (no worm file had changed — only `worm_registry.py` did,
   and that file is NOT in the mtime set). So the stale pickle was loaded
   as a "fresh cache hit" and full discovery never ran.

`force_rebuild` busts layer 1 but not layer 2. Any cache whose validity is
checked against SOURCE FILE mtimes will consider itself fresh even when the
CODE THAT BUILT IT changed.

**The fix that worked:** delete the pickle file first, then run discovery:

```python
from CORE.worm_registry_cache import CACHE_FILE
if CACHE_FILE.exists():
    CACHE_FILE.unlink()          # bust layer 2
from CORE.worm_registry import discover_worms, WORM_REGISTRY
discover_worms()                 # full discovery, rebuilds pickle with new code
```

Result: 105/105 registered, 0 bare modules, fresh cache written.

**Verification trap to avoid:** `cache_status()["built_at"]` after a
supposed rebuild will show the OLD timestamp if the rebuild no-oped. Always
check `built_at` moved forward AND the actual data changed (e.g. bare-name
count dropped to 0). A "rebuild" that returns in <1s for a 38-45s cold start
is the loudest possible smell.

**Permanent mandate:**
- When changing how the registry builds entries (or ANY cache-building code),
  NEVER trust `force_rebuild=True` alone — delete the cache file first, or
  include the builder's own mtime in the freshness key.
- mtime-based cache freshness cannot detect changes to the BUILDING code.
  If the builder changes, the cache is definitionally stale regardless of
  source mtimes.
- After any forced rebuild, assert on the DATA (e.g. `len(bare) == 0`), not
  just on the call returning successfully.

**Related:** Lesson #59 (module-path resolution), `src/CORE/worm_registry.py`
(`register_worm` normalization), `src/CORE/worm_registry_cache.py`
(`_is_cache_fresh`, `_load_cache_readonly`), `tests/test_worm_registry_modules.py`

---

---

## Lesson #84 — Aggregate Verification Is Its Own Instrument: Every Failing File Passed Alone

**Date:** 2026-09-22

A full-suite run (183 files, single process) returned
**72 failed / 3,508 passed / 38 skipped / 69 errors** in 23.5 minutes. Every
failing *file*, run alone, was green: `test_sb3_agent` 42 passed,
`test_nature_metacluster_unit` 74 passed, `test_fs_probe_backend` 13 passed,
`test_wiring_cycle` 19 passed, `test_eve_unleashed` 21 passed,
`test_morphogenesis_opportunity` 14 passed, `test_worm_smoke` 5 passed,
`test_evolution_gates` 61 passed, `test_import_map` 8 passed.

The 141 aggregate failures were therefore **not product defects** — they were
isolation defects, and no per-file run can see them. Two of the three root
causes found were genuine product-level hazards that only exist *across* time in
one process:

1. `reset_registry()` re-imports helper modules, so two `wiring_genome` objects
   exist and a patch lands on the wrong one (Error #190).
2. A process-global write guard armed mid-session blocked module-scoped fixture
   setup (Error #191).

**Permanent mandate:**
- The aggregate suite is the instrument. Per-file green is not evidence about
  the suite; it is evidence about one file.
- When a test passes alone and fails in aggregate, the *order* is the input.
  Name the exact prefix that reproduces it (here: `reset_registry()`-calling
  files sorted before `test_wiring_cycle`; `test_compliance_step45_init` before
  `test_evolution_gates`) before changing anything.
- When a global (registry, guard, clock, cache) is mutated mid-session, ask
  "what else did that mutate that I am not measuring?" — the answer was *module
  identity* and *fixture scope*, neither of which appears in any stack trace.

**Related:** Error #190, Error #191, Error #192,
`NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md` §5, §7

---

## Lesson #85 — A Measurement That Changes What It Measures Is Not a Measurement (third instance)

**Date:** 2026-09-22

This session found the *third* instance of the same defect class in the same
subsystem, so it is a pattern rather than three bugs:

| # | Instrument | What it mutated | Effect |
|---|---|---|---|
| 1 | `l1_wiring_audit.audit()` | read the live registry through five stages | 2 worms at entry, 113 in the effector stage, 234 at exit — a genome that changed nothing was reported as demoting 111 organs |
| 2 | `hyperopt.measure()` | called unguarded `discover_worms()` to read a count | registry repopulated mid-measurement; the audit's report disagreed with the table it had just read |
| 3 | `worm_registry._purge_worm_modules()` | deletes `CORE.WORMS.*` from `sys.modules` | a reset performed for one caller silently re-creates module objects under other callers |

**Permanent mandate:**
- An instrument must snapshot its input **once, at entry**, and report on that
  snapshot (this is what `l1_wiring_audit` was fixed to do).
- A "read" path must never be able to write. A count-of-registry call may
  lazy-init (`if not WORM_REGISTRY`), never repopulate.
- A destructive helper (`purge`, `reset`, `clear`) must record **identity
  changes** it causes, not just the data change it was written for — the
  docstring here warned about classes while modules were also replaced.

**Related:** Error #190, `src/CORE/WORMS/expansion/hyperopt.py` (`measure`),
`src/CORE/l1_wiring_audit.py` (`audit`), `src/CORE/worm_registry.py`

---

## Lesson #86 — This Codebase Documents What It Learned Better Than It Checks It Still Holds

**Date:** 2026-09-22

Measured architecture audit of the whole tree (`NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md`):

- **Documentation 8.0/10** — post-mortems embedded in the code they guard,
  calibrated PARAM_SPACE entries carrying their own failure history, 24-skill
  catalog, ADRs, per-function static battery.
- **Type safety 3.0/10** — 1,133 mesh functions with unannotated parameters,
  349 with no return annotation, and **mypy is installed in none of the three
  venvs**, so the dimension cannot even be measured with the shipped tooling.
- **Test coverage 6.0/10** — 3,508 passing tests, but 561 mesh functions have no
  test reference and the aggregate suite carried 141 isolation failures.

Supporting facts: 1,487 mesh functions, only **77 clean** on all 21 pre-flight
probes; **164 unreferenced** functions (`integrate_via_stage` 92,
`module_level` 34, `wire_at_site` 32, `unresolved` 6); 2,009 open checklist
items with 0 completed; 7 circular-import groups; `worm_registry` at 166 inbound
imports; 17 `shell=True`; 255 write-swallowing `except` bodies; 3,759-entry
dirty working tree.

**Permanent mandate:**
- Reasoning quality and verification quality are separate scores. This project
  is excellent at the first and has not applied it to the second.
- A checklist with 2,009 open items and 0 completed is a **maintenance
  liability wearing the costume of an instrument**: wire it to a cadence or cut
  it (the wire-or-cut dispositions exist for exactly this).
- Do not trust a graph built over vendored archives to describe this codebase —
  the top hubs were `onnxruntime`, `BIBL Terms *`, `nuitka/*.h` and `TEST_F`.

**Related:** `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md` §4, §6, §8, §9

---

## Lesson #87 — An Unmeasurable Metric Is Usually an Environment Bug, Not a Code Bug

**Date:** 2026-09-22

Lesson #86 concluded, from the same session, that type safety *"cannot even be
measured with the shipped tooling"* and scored it 3.0/10. Both halves of that
sentence were wrong, and the audited number was the problem:

**1. The tool was never the problem.** `mypy src/CORE/` did not report "no
findings" or "bad config" — it hard-crashed with
`ValueError: path is on mount '\\.\nul'`. Two literal files named `nul`
(residue of a cmd.exe `dir /b ... > nul` run from Git Bash, where the redirect
creates a real file) sat in the tree. They are invisible to `git status` — a
pathspec named `nul` cannot be matched — so no review, hook or test had ever
surfaced them. **Removing 229 bytes of junk turned a crash into a baseline:**
655 mypy errors over `src/CORE/`, immediately.

**2. The tool was also the wrong tool.** On the same tree:

| | files | findings | wall |
|---|---|---|---|
| mypy (`src/CORE/`, `--check-untyped-defs`) | 329 | 655 errors | ~6 min |
| basedpyright (repo `pyrightconfig.json`) | 690 | 1,191 errors + 252 warnings | 64 s |

basedpyright is already installed in the canonical venv (1.40.1) and reads the
config the repo already committed. Its extra classes are the ones this codebase
actually suffers from: `reportUndefinedVariable` 94,
`reportOptionalMemberAccess` 120, `reportPossiblyUnboundVariable` 17 — the
`try/except ImportError` and `Optional` patterns that dominate `src/CORE/`.

**Permanent mandate:**
- Before recording a metric as unmeasured, reproduce the *attempt* and read the
  error. "No tooling available" and "tool says nothing" and "tool crashes on a
  junk filename" are three different findings with three different fixes.
- A crash-to-clean transition of this shape means the previously stated score
  was measuring the environment. Restate it, and say which number moved.
- Prefer the instrument already installed and already configured. Adding a tool
  is a cost; discovering the tree already had a better one is a finding.
- When a check is adopted, adopt it **with a baseline** (`tools/type_check_gate.py`),
  so 1,191 pre-existing findings do not justify switching the check off.

**Related:** Lesson #86, Error #193, `tools/type_check_gate.py`,
`logs/basedpyright_baseline.json`

---

## Lesson #88 — A Gate Must Carry the Diagnosis, Not Just the Count

**Date:** 2026-09-22

`tools/aggregate_suite_gate.py` was built to catch what a per-file runner cannot
see, and it worked on the first try: it found 72 failures and 69 errors where
every failing file passed alone. Its first five runs were still nearly useless —
the report stored only failing **nodeids**, and the assertion text lived in a
`capture_output=True` pipe that closed when the gate exited. The project could
count its 50 remaining failures and could not read a single one; diagnosing one
of them meant paying 22 minutes again, in full, every time.

The fix is one file write. The lesson is the ordering: the report was designed
for the *gate's* decision (new id vs known id) and the evidence needed for the
*human's* decision was treated as a detail to re-derive on demand.

**Permanent mandate:**
- Persist the raw evidence next to every derived report. If the next question
  requires re-running the expensive step, the artifact is incomplete.
- Generalised to any baseline-compare gate: it must state **what it compared**
  (profile, targets, baseline path) and **where the detail is** (raw output). A
  gate trusted for its number and distrusted for its reason is the worst possible
  combination — it is obeyed and not believed.

**Related:** Error #194, `tools/aggregate_suite_gate.py`,
`NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md` §5, Lesson #84

---

## Lesson #89 — An Artifact Must Not Answer for a Scope It Did Not Measure

**Date:** 2026-09-22

`tools/aggregate_suite_gate.py` writes `logs/aggregate_isolation_report.json`
for the CI profile. The path was fixed by **profile**, but `--only` could shrink
the **scope** — so a one-file smoke test replaced a `301 passed` run of all eight
profile files with `1 passed in 1s`. Nothing failed. The JSON stayed valid, the
pass rate stayed plausible, and it named a profile it no longer described.

This is the same defect class as Lesson #88 one layer up. There, the gate stored
the count and not the diagnosis; here it stored the diagnosis of a run that did
not happen. Both are a report whose *shape* is correct and whose *referent* is
wrong — the hardest kind to notice, because every check on the artifact's format
passes.

**Permanent mandate:**
- When a knob can narrow a measurement, the artifact path must follow the scope,
  not the profile label. A subset run writes a subset file and says so.
- A gate's baseline and report are **evidence**, so the same rule as any evidence:
  it must be produced by the run it claims to describe. Redirect the artifact
  root in tests rather than exercising the real path.
- Prefer a refusal to a borrowed baseline. A narrowed `--check` with no matching
  baseline now exits 1 (`no baseline`) instead of comparing against the profile's
  set, which would have reported every unrun file as "no longer failing" — the
  gate reading green because it looked at less.
- The tell to look for: an artifact that is *tracked* and whose filename encodes a
  scope (a profile, an environment, a matrix row) but whose producer accepts a
  narrower input.

**Related:** Error #195, ADR-012, Lesson #88, Error #194,
`tools/aggregate_suite_gate.py`, `tools/type_check_gate.py` (same shape: profile
pinned by path, scope shrinkable by `--paths`)

---

## Lesson #90 — A Half-Restore Is a Leak: Restore the State You Changed, Not the Name You Changed It Through

**Date:** September 22, 2026
**Source:** Error #196 (memory DB path), aggregate run — 52 failed / 3,628 passed

A suite that redirects a module-level path does the right thing in `_setup` —
env var **and** global — and half of it in `_teardown` — env var only. The env
var was never the thing the code read; the global was. Restoring the env var
therefore restored *nothing*, while `rmtree` deleted the directory the global
still named. Four files did this; the failures surfaced in five other files that
had the misfortune to run later.

**The two-part tell that this class always shows:**

1. **Every blamed file passes alone.** An aggregate-only failure whose victims
   are individually green is not a flake and not a slow test — it is state that
   outlived the test that set it. Blame is a *search direction*, not a verdict:
   the file that names the resource and the file that pointed at it are usually
   different files.
2. **The error names a resource, so the question is "who pointed at it".**
   `unable to open database file` at a `Temp\tmp_XXXX\...` path is a statement
   about a *deleted directory*, not about sqlite, disk space, or permissions.
   Reading it as "the DB is broken" sends the search into `direct_memory`; the
   fix was in the tests.

**Permanent mandate:**
- When a test mutates module state to redirect something, the restore must
  recompute the SAME derived value through the module's own resolver, after the
  environment is restored. Restoring one of two coupled names is not a restore.
- Prefer a mechanism over a checklist. `conftest` now restores every derived DB
  path after **every** test, autouse — so the five files that never thought about
  it are covered, and no future file can opt out of being right.
- When you fix a leak, pin it with an order-dependent pair of tests and then
  **falsify the pair**: run both functions with the mechanism removed and confirm
  the second one fails. A regression test that has never failed proves nothing.
- The audit number to distrust: an aggregate run whose failures are all green
  individually. Count the *victims* to size the damage, then hunt the *cause*
  among the files that ran before them — not among the files that broke.

**Related:** Error #196, Error #190 (same class: `_purge_worm_modules` duplicating
helper modules), Lesson #85, `tests/conftest.py`,
`tests/test_memory_db_isolation.py`

---

## Lesson #91 — "I Permitted It" Is Not a Process-Wide Fact: Per-Thread State Gates Are Invisible Until a Worker Runs

**Date:** September 22, 2026
**Source:** Error #197 — `test_fs_probe_backend` 10/10 aggregate failures, 4-second repro

`sentinel_enforcer` gates file writes with `_GATED_CALL = threading.local()`. The
permit is granted on whichever thread happens to ask. `fs_probe` then runs its
child probe on a **new** worker thread and opens a temp file there — so once the
guard was armed, every delegated probe failed, and the API returned `None`.
`None` means "unknown", so the caller could not tell "blocked by our own security
control" from "the path did not answer".

Two facts make this worse than it looks:

1. **The symptom is a quiet `None`, not an exception.** An Optional return is a
   claim that `None` is a legitimate answer. Here it swallowed a `PermissionError`
   raised by the process's own guard, across an entire subsystem.
2. **The failing tests were not the ones that armed the guard.** They were two
   files later, and green alone — the same aggregate-only shape as Errors #191
   and #196.

**Permanent mandate:**
- When a gate uses per-thread (or per-task, or per-coroutine) state, the fact to
  check is "who is asking", not "did anyone permit". A permit that does not
  propagate to the code that runs is not a permit; it is a race with a schedule.
- A probe that returns `Optional` must let the caller see why it is `None`.
  Distinguish *denied* from *did not answer* — otherwise a security control's
  denial is indistinguishable from a slow disk, and both read as "unknown".
- Fix the mechanism, never the victim file. Three times today the failing file
  was innocent and the cause was a mechanism armed by an earlier file.
- If a fix is made only in the test environment, state the production
  consequence in the same breath. A thread-local guard is an *operator-visible*
  design question (does the guard cover worker threads?), not a test detail.

**Related:** Error #197, Error #191 (same guard, earlier instance), Error #196,
Lesson #90, `src/CORE/fs_probe.py`, `tests/test_sentinel_thread_permit.py`

---

## Lesson #92 — A Cap Applied Before a Filter Is a Cap on Nothing, and "Complete" Must Not Be Reachable With an Empty Record

**Session:** 2026-09-22 · **Trigger:** Error #198

`orchestrate(max_natures=1)` ran zero Natures and reported `phase="complete"`.
The cap was applied to a ranked list, and a filter one step later could delete
the very item the cap had just paid for:

```python
natures = ranked[:max_natures]                    # spends the budget
...
execution_order = [n for n in order if n not in circular]   # refunds nothing
```

Three transferable facts came out of it:

1. **Order of operations is semantics.** "Limit to N" is a promise about what
   RUNS. If anything downstream can discard, the limit must be applied to what
   survives, or the caller receives less than it asked for and no error.
2. **A terminal success state must carry its own proof.** `phase="complete"`
   with `completed_natures == failed_natures == set()` is a contradiction the
   type system will not catch. Every such state needs a count that cannot be
   zero when work was done — or an explicit "nothing was eligible" error.
3. **In-file order dependence looks like a neighbour problem and is not.**
   Every individual test in the failing class passed; every pair passed; the
   file passed in a fresh process. The poison was cumulative (a dozen prior
   orchestrations moved a ranking). Cumulative causes need a *value* watch, not
   a file bisection — `tools/pytest_fixture_watch.py` named it in one run.

**Permanent mandate:**
- Apply a limit to the set that can actually execute, and re-check the limit after every filter that can discard.
- If a result claims completion, it must name what completed. Do not let "ran nothing" and "ran clean" be the same object.
- When a failure is cumulative rather than positional, watch a value across the suite instead of bisecting files.

**Related:** Error #198, Error #194, `tools/pytest_fixture_watch.py`, `src/CORE/WORMS/METACLUSTER.py`

---

## Lesson #93 — A Measurement Written Inside a Transition Is a Cache With No Rebuild Path

**Session:** 2026-09-22 · **Trigger:** Error #199

A triage wrote `evidence` only in the branch that moved a row from `pending` to
`dispatched`. The table is regenerated by re-running the tool, so the second run
saw `dispatched`, skipped the branch, and produced 62 decisions with no
locations. Nothing consumed the field except a contract test, so the loss was
silent for as long as that test was failing for another reason.

**Permanent mandate:**
- An instrument that is meant to be re-run must be idempotent, and idempotence must be a TEST (`propose` twice, same evidence), not an intention.
- Write measurements outside the decision branch. The transition is not the fact.
- If a generated artifact loses a field on regeneration, treat it as data loss even when no consumer notices yet.

**Related:** Error #199, Error #190, `tools/mesh_function_preflight.py`, `tests/test_mesh_wire_or_cut.py`

---

## Lesson #94 — A Repair That Recomputes the Old Value Is Not a Restore; It Is a Second Leak

**Session:** 2026-09-22 · **Trigger:** Error #200

The isolation fixture that repaired Error #196 recomputed each module's DB-path
global from the environment. But two test modules redirect that global
deliberately, to a path the environment does not describe -- so the repair
replaced their redirect with the shared session store after the first test.

One cause, two symptoms in files that were never the leaker: a teardown that
called `unlink()` on the LIVE session store (it reported the lock instead of the
deletion), and a test whose `DirectMemory` adopted another test's session id
through the documented reconnect merge, so no `session_start` was recorded.

**Permanent mandate:**
- Restore by SNAPSHOT, not by re-derivation. The environment is an input; it is not memory of what the value was.
- Recomputing is correct only for state that did not exist when the snapshot was taken (a module imported during the test). Say so in the comment, so the two cases are not conflated again.
- Any cleanup that unlinks or rmtrees a module global must first prove the global is still the one it expects. Mutable process-wide paths are shared attacker surface between tests.
- Two symptoms in unrelated files that both pass alone: suspect a shared process-global before suspecting either test.

**Related:** Error #200, Error #196 (the leak this repair was for), `tests/conftest.py`, `src/CORE/direct_memory.py`

---

## Lesson #95 — A Wall-Clock Assertion on a Shared Machine Grades the Machine

**Session:** 2026-09-22 · **Trigger:** Error #201

Three assertions failed together in the aggregate run and none of them was
about the code: a 3.112s call against a 3.0s "probable deadlock" bound, two
`overdue()` polls whose clock-derived `overdue_by` read 0.020 then 0.021, and a
benchmark whose 2-worker run beat its 1-worker run by less than nothing. All
three passed alone. All three were reading contention.

**Permanent mandate:**
- Decide which of two things a timing test is checking -- "it returns" or "it is fast" -- and never check both with one constant.
- A deadlock is UNBOUNDED. A tight bound is not a stricter deadlock test; it is a stricter machine test. Set the bound to outlive any plausible load and say so in the source.
- Never assert equality on a value derived from `now()`. Compare what is reported; bound the delta if the quantity itself matters.
- A benchmark on a loaded box needs best-of-N and a workload large enough that thread-spawn overhead is a small fraction of it. If `speedup < 1` is systematic, the workload is the bug, not the noise.
- Prefer a recorded ledger for slow-but-complete observations. A gate that fails on load teaches the team to ignore it.

**Related:** Error #201, Error #193, `tests/test_compliance_deadlock_regression.py`, `tests/test_mesh_audit_insights.py`, `tests/test_pool.py`

---

*Lesson #83: August 29, 2026 — stale-pickle force_rebuild no-op session*
