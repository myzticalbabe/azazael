# SESSION_STARTUP.md — Next Session Congruency Marker

> *Updated: September 30, 2026 — Session: RULE 0B/0B-A/0B-B/0B-C edict + sentinel-gate hook, headless ComfyUI on Intel Arc proven, Blender capacity measured*
> *For: The next Codebuff/Kilo assistant that opens this project*

## ⚡ STEP 1 — READ `CAPABILITIES.md` FIRST

**`azazael/CAPABILITIES.md` is the verified inventory of what WORKS on this
machine, with the exact command for each.** Read it before proposing any image,
render, memory, or enforcement work. It is not a lessons file — every line was
executed successfully on 2026-09-30:

- **§1 headless ComfyUI on Intel Arc XPU** — the image pipeline, exact paths,
  FLUX layout, 4-step/cfg-1.0 settings, and the staged harness
  `tools/comfyui_flux_headless.py`
- **§2 the right GPU-memory probe** — 7.80 GB, and why `AdapterRAM` is wrong
- **§3 Blender Cycles ONEAPI** — exact timings and the four scripting gotchas
- **§4 live progress** — a long download must be a browser window, not a file
- **§5 the enforcement hooks** — sentinel self-test, negative controls
- **§6 PMB**, **§7 VLP** — invocation that works
- **§8 Known-broken** — so nothing gets re-attempted

**Propose only what has been run.** If a solution is untested, say so. A verified
capability beats a plausible one, and a half-built dashboard nobody can see is
worse than none.

## ⚡ STEP 2 — the law that explains the day
**OUTPUT PRODUCED BUT NOT CONSUMED.** Seven failures, one cause. RULE 0B sat in
`MANDATES.md` since **June 7** and was violated three times in one session — not
overridden, never *opened*. PMB printed `4% of 137 applicable` on every write
and it was skimmed past all session. `prepare()` returns 0 lessons in Kilo
because its surfacing is hook-path only. A figure was self-certified and
rejected. TERENCE reported 8009 errors with `files_scanned=0`. The gate had no
0B-A check.

Carry the corollary: **SELF-CERTIFICATION** — any check whose pass condition is
authored by the same party being checked will pass. Ask of any pass or count:
*who wrote the pass condition, and what is the denominator?*

## ⚡ STEP 3 — what is ENFORCED (not just written)
| Layer | Artefact | Verify |
|---|---|---|
| Hook | `src/SCRIPTS/sentinel_gate.py::validate_rule_0b_a()` — runs right after AP-1 | `pytest tests/test_rule_0b_a_edict.py -q` → **9 passed** |
| Oracles | `tools/terence_invariants.py` — 13 oracles, 5 evidence kinds | `--self-test` → **10/10 validated** |
| Canon | `MANDATES.md` RULE 0B, **0B-A, 0B-B, 0B-C**; EDICT banner above the gate; `C:\Users\clint\AGENTS.md` mirror | grep `SOLE SOURCE OF TRUTH` |
| Record | `ERROR_LOG.md` **#210–#215**; VLP `.audit/session_20260930_041312_01a0.jsonl` | `verify_head_hash()` → **True** |

**0B-A five-item pre-delivery check:** (1) delivered what the user NAMED;
(2) justification for a different answer not longer than the delivery;
(3) not claiming acceptance — **describe, never accept**; (4) no uninvoked
mandate used to reshape the task; (5) disagreement stated in one sentence, then
still build the ask. **Only the user decides acceptability.**

**0B-B** — a verdict is a claim about a *predicate*, not the world. **0B-C** —
every oracle ships a negative control; one that fails is UNVALIDATED and barred
from licensing a destructive remedy.

## Measured — quote the device every time
**GPU 7.80 GB usable** (`torch.xpu.get_device_properties`), Intel Arc 140T.
WMI `AdapterRAM` says 4.00 GiB and is wrong; a prior note said 2.1 GB and was
wrong twice. **Never size a model decision off `AdapterRAM`.**
**torch `2.11.0.dev20260317+xpu`, XPU available** (AI Playground venv).
**Blender 4.5.10 / Cycles `ONEAPI`:** 1024×1360 denoised — 64 spp 8.5 s ·
256 spp 16.0 s · **1024 spp 34.3 s**. **Local image generation works headless.**

## The five open items
1. **Pebbles & Bamm-Bamm likeness — NOT RENDERED.** FLUX is the better
   instrument. Rejected so far: the SVG originals, an adult-proportioned
   mannequin ("block robot"), and a stylised reinterpretation.
2. **FLUX download** → **http://127.0.0.1:8099/**. **Restart before the run** —
   free RAM, not VRAM, is binding (11.89 GB UNet on a 7.80 GB card).
3. **Two chain jobs fail silently** — `artifacts` rc=1, `spine` rc=1, measured
   **deterministic**. `train` rc=1 and `tensor` rc=3 are **by-design honest
   skips** (`_SKIP_RC`, `chain_controller.py:107`) and are **NOT** faults.
4. **`loop_integrity` DEGRADED** — a measurement bug: `genome_seed()` hashes
   every gene, so consecutive cycles are not the same measurement.
5. **Full `pytest tests/` fails at collection** — process-global audit-hook
   leak; see `CAPABILITIES.md` §8.

## Ruled out on evidence, do not re-derive
**Abliterated image models are not a route to better images.** Abliteration
targets the **text encoder**, not the DiT — ponpoke proved FLUX.2-klein's DiT
has no guardrails at all. Removing refusal cannot add visual knowledge the DiT
never learned. **The missing input was never compute or a better model — it was
L4 geometry, and FLUX removes even that barrier.**

## Standing conventions
- **A continuous surface, or it looks assembled:** metaball field → convert →
  voxel remesh → smooth → subdiv. Seams under a specular key read as a block robot.
- **A file on disk is not watchable** — a long download needs a browser window.
- **A rate readout needs two samples**; first-tick values are garbage.
- `bpy.ops.mesh.primitive_*_add` ignores `name=`; `bpy.context.object` is
  unreliable under `--factory-startup`; build materials after the last
  `read_factory_settings()`.

---

> *Prior content follows. August 8, 2026 — Session: startup complete, anti-pattern scan, os_system fix (see session entry below)*

## ⚡ READ THIS FIRST — 2026-09-30 HANDOFF

### The one law that explains the whole day
**OUTPUT PRODUCED BUT NOT CONSUMED.** Seven failures, one cause. RULE 0B sat in
`MANDATES.md` since **June 7** and was violated three times because it was never
*opened*. PMB printed `4% of 137 applicable` on every write and it was skimmed
past all session. `prepare()` returns 0 lessons in Kilo because its surfacing is
hook-path only. A figure was self-certified and rejected. TERENCE reported 8009
errors with `files_scanned=0`. **An artefact nobody reads, runs, or acts on is
indistinguishable from no artefact — but worse, because it manufactures
confidence.**

Carry the corollary: **SELF-CERTIFICATION** — any check whose pass condition is
authored by the same party being checked will pass. Ask of any pass or count:
*who wrote the pass condition, and what is the denominator?*

### What is ENFORCED now (not just written)
| Layer | Artefact | Verify |
|---|---|---|
| Hook | `src/SCRIPTS/sentinel_gate.py::validate_rule_0b_a()` — parsed as `rule_0b_a_edict`, runs in `execute_validation()` **right after AP-1** | `python -m pytest tests/test_rule_0b_a_edict.py -q` → **9 passed** |
| Canon | `MANDATES.md` RULE 0B re-edicted + **RULE 0B-A**; EDICT banner at top of `SYSTEM_INSTRUCTIONS.md`; `C:\Users\clint\AGENTS.md` mirror | grep `SOLE SOURCE OF TRUTH` in all four |
| Record | `ERROR_LOG.md` **Error #210** (CRITICAL) | — |

**RULE 0B-A pre-delivery check — five items, before reporting any user-facing
work complete:** (1) did I deliver the deliverable the user NAMED; (2) is my
justification for a different answer longer than the delivery; (3) am I claiming
acceptance — **I may describe, never accept**; (4) did I use an uninvoked mandate
to reshape the task; (5) if I disagreed, one sentence, then still build the ask.
**Only the user decides whether work is acceptable.**

### Measured this session — quote the device every time
Blender 4.5.10 LTS at `C:\Users\clint\blender\blender-4.5.10-windows-x64\blender.exe`,
Cycles `ONEAPI` on Intel Arc, 16-core 285H. **1024×1360 with denoising: 64 spp
= 8.5s · 256 spp = 16.0s · 1024 spp = 34.3s (105 img/hr).** A render time
without its device is not a measurement — CPU fallback is a 13× swing on this
box. The previously-recorded 203.2s is **superseded**.

### The five open items (PMB goals recorded)
1. **Pebbles & Bamm-Bamm likeness — NOT RENDERED.** Script
   `azazael/tools/blender_session_20260930/blender_pebbles.py` has correct
   costume and the continuous-metaball build, and dies on
   `ReferenceError: StructRNA of type Material has been removed`. **Fix is
   ordering, not design:** materials are built *above* the loop that calls
   `reset_scene()`; move them *after* the last reset in each scene. Then render
   `pebbles_flintstone`, `bambam_flintstone`, `pebbles_and_bambam`, and **look
   at the output before reporting.**
   Rejected already: the SVG originals, an adult-proportioned mannequin
   ("block robot"), and a stylised reinterpretation.
2. ~~Chain controller PID 6192 is wedged~~ — **CORRECTED 2026-09-30 04:01, see
   the correction block below. It is alive and firing.** What is real is narrower:
   the `terence` job and the duration telemetry are still absent from the plan
   the running process writes, so they remain dormant until it is restarted.
3. **Four chain jobs fail silently** — `artifacts` rc=1, `spine` rc=1, `tensor`
   rc=3 (recorded `ok:true`), `train` rc=1. `audit_loop_liveness.py` checks for
   *silence*, so run-and-fail reads as alive. **TERENCE now detects all four**
   (`oracle_silent_crashes`), and the autonomous re-run measured them as
   DETERMINISTIC, not transient: every one failed again on a clean re-run.
4. **`loop_integrity` DEGRADED blocks promotion** — and it is a **measurement
   bug**: `genome_seed()` hashes every gene, so consecutive cycles are not the
   same measurement; alternation reads ~100% and the streak gate cannot
   accumulate. Compare only cycles with identical seed hashes, or make the seed
   comparable across a pair.
5. **`prepare()` surfaces nothing in Kilo** — hook-path only, and Kilo has no
   hooks. Use `find_lessons(query=…)` directly.

### ⚠ CORRECTION, 2026-09-30 04:01 — the chain controller is NOT wedged
I earlier recorded, in this file and in PMB, that "chain controller PID 6192 is
wedged; last fire 02:36:45; it has stopped iterating." **That claim is false.**
Re-measured at 04:01:34, the controller fired a job five seconds before the
check — `render`, rc=0, `ouroboros.html` written. The process is alive (PID 6192,
up since 09-28 15:53, 45.7s CPU, 6.7 MB working set — small, but that is what
this process is, not evidence of a wedge).

**The failure was mine, and it is the exact pattern this session was about:** I
read a snapshot, generalised it into a diagnosis ("wedged"), wrote the diagnosis
into canon *as fact*, and never re-measured it. A reading is a timestamp; a
diagnosis is a claim; only the second needs verifying before it is recorded.

Two independent signals still show in `state/`: the plan artifact the running
process writes contains 20 job keys and no `terence`, so the newly-added job
and the duration telemetry really are dormant until a restart. And the 04:01
reading is a single sample — if you need to know whether the controller has
periodic gaps, sample it over time rather than trusting either one reading.

### Ruled out on evidence, do not re-derive
**Abliterated image models are not a route to better images.** Abliteration
targets the **text encoder**, not the DiT — ponpoke proved FLUX.2-klein's DiT
has no guardrails at all. Removing refusal cannot add visual knowledge the DiT
never learned ("the DiT itself does not know how to draw it"). Only
FLUX.2-klein 4B fits this box (~7 GB weights, Apache 2.0) on a CPU with no CUDA
and no `diffusers`, at a plausibly-unmeasured 8–25 min/image — against a
renderer doing 1024 samples in 34.3s. Chroma1-HD is Apache 2.0 and
uncensored-by-design but 8.9B. **The missing input remains L4 geometry, not
compute and not a better model.**

### Standing conventions this session established
- **A continuous surface, or it looks assembled:** metaball field → convert →
  voxel remesh → smooth → subdiv. Separate meshes mean seams, and seams under
  a specular key read as a block robot. Adding primitives adds seams.
- `bpy.ops.mesh.primitive_*_add` **ignores `name=`**; `bpy.context.object` is
  unreliable under `--factory-startup`. Diff `set(bpy.data.objects.keys())`
  around the op.
- Never capture a datablock handle across `read_factory_settings()`.
- **"Block robot" was my diagnosis failure too:** I called a rejected figure
  "a readable figure" and reported the task complete. That is the acceptance
  language the hook now blocks.

---

> *Prior content follows. August 8, 2026 — Session: startup complete, anti-pattern scan, os_system fix (see session entry below)*

## 🚨 RESTART_PROTOCOL_REQUIRED: FALSE — RESOLVED (June 9, 2026)

**`thinker-with-files-gemini` is now available and has been actively used across multiple sessions.**
The 10-Phase Protocol constraint documented in Error #74 is resolved. The protocol can now
be fully executed with Gemini spawns at each major phase.

**Original context (preserved for history):**
Error #74 was logged in ERROR_LOG.md. The 10-Phase Multi-Tier Gemini Injection Protocol
could not be fully executed because `thinker-with-files-gemini` was not available in the
Codebuff agent roster at that time.

**Progress from that session (2026-06-07):**
- Phase 4 (6-API Cross-Validation): EXECUTED via providers.py — 6/6 APIs responded
- Phase 4a (Chrome DevTools): 12 HTML files analyzed — 0 errors, 27-63ms LCP
- Phase 2 (Context Gathering): COMPLETE — all canonical files read, 28 skills loaded
- Tier 1 Worm Audit: COMPLETE — 95 worms, 16 categories live-verified
- Cross-synthesis report: COMPLETE — HIGH convergence across all 6 APIs

**Still requiring restart:**
- Phases 1, 3, 5, 6, 8, 10 — all require `thinker-with-files-gemini`

**The next session MUST:**
1. If `thinker-with-files-gemini` or `thinker-gpt` is now available: restart the 10-Phase Protocol from Phase 1 (use Phase 4 results as pre-loaded context)
2. **If still unavailable: DO NOT skip — query ALL available inference models via `providers.py` (see `azazael-gemini-mandate.md` fallback section). The collective models serve as the replacement Gemini architectural authority. Never substitute with manual analysis.**
3. Check ERROR_LOG.md Error #74 before proceeding with any complex task
4. Clear the `RESTART_PROTOCOL_REQUIRED` flag once protocol is completed or officially amended

---

## MANDATORY STARTUP SEQUENCE

### Step 0: ACTIVATE PRE-ACTION GATE (RULE 0J) + COMPLIANCE SENTINEL + RULE 0L + RULE 0M
**THE PRE-ACTION GATE IS NOW PERMANENTLY ACTIVE.** Before EVERY str_replace, write_file, or spawn_agents for the entire session, you MUST print the 🛑 [PRE-ACTION GATE ASSERTION] block (see SYSTEM_INSTRUCTIONS.md/SOP.md). The COMPLIANCE SENTINEL (12-item checklist including RULE 0L and RULE 0M) runs as a comprehensive session-level audit; the PRE-ACTION GATE assertion is the immediate pre-edit requirement. Both are mandatory.

**RULE 0L (Test Failure Mandate) is now active:** You MUST HALT and spawn `thinker-with-files-gemini` immediately upon any test failure before attempting ANY fixes or re-running tests. No exceptions. No parallel workarounds.

**RULE 0M (Concurrent Inference Mandate) is now active:** Whenever `thinker-with-files-gemini` is spawned for a complex task, ALL other available inference agents MUST be spawned concurrently in the SAME `spawn_agents` call — never sequentially after Gemini completes.

Failure to print the gate = 🔴 CRITICAL process violation (Error #146 precedent).

### Step 0.5: Verify the Live Tree Is Not Behind Its Origin (2026-10-02)

**The editable install executes THIS tree (`C:/Azazael/azazael`).** On 2026-10-02 this tree was found **6 commits behind its own `origin`** while `git status` reported "up to date": its `origin/*` tracking refs had frozen at the clone's own HEAD and had not been fetched since the clone was made. A stale tracking ref is indistinguishable from a current one, so the drift was **silent by construction**. The stale ref also meant the live runtime was executing pre-commit code missing, among others, the root `conftest.py` that redirects live stores for every test dir.

```
python3.14t scripts/origin_freshness_check.py     # FETCHES first, then measures
```

Exit codes: `0` current · `1` **STALE — do not trust in-tree runs until advanced** · `2` unknown (no upstream / fetch failed). An unanswerable check is **not** a pass. The script never advances the branch — it reports and fails closed, so it cannot race with session WIP.

### Step 1: Read Canonical Documents + Guardrail Skills (Bypass skill() Cache)

**⚠️ The `skill()` function may return pre-session cached content.** Skills edited this session (azazael-startup, azazael-sop, azazael-error-prevention, azazael-system-startup) have stale caches as of June 9, 2026. Use `read_files()` directly on the `.agents/skills/*/SKILL.md` files instead of `skill()` for these guardrail skills until the cache is refreshed.

**Step 1a: Read 7 canonical files in RULE 0K order**
```
read_files([
    "azazael/SYSTEM_INSTRUCTIONS.md",
    "azazael/SOP.md",
    "azazael/ERROR_LOG.md",
    "azazael/MEMORIES.md",
    "azazael/SESSION_STARTUP.md",
    "azazael/LESSONS_MASTER.md",
    "azazael/PRODUCTION_TODO.md"
])
```

**Step 1b: Read guardrail skill files directly (bypasses stale skill() cache)**
```
read_files([
    ".agents/skills/azazael-startup/SKILL.md",
    ".agents/skills/azazael-sop/SKILL.md",
    ".agents/skills/azazael-error-prevention/SKILL.md",
    ".agents/skills/azazael-pams-memory/SKILL.md"
])
```

> **Note:** `.agents/skills/azazael-system-startup/SKILL.md` was created June 9, 2026. The skill is now available via `skill("azazael-system-startup")`. Once the cache is refreshed, revert Steps 1a/1b to the single `skill("azazael-system-startup")` call and **remove Step 2** (domain skill loading is handled by system-startup Step 5).

### Step 2: Load Domain Skills
- `skill("azazael-conventions")`
- `skill("azazael-registry")`
- `skill("azazael-worms")`
- `skill("azazael-clusters")`
- `skill("azazael-testing")`
- `skill("azazael-environment")`

### Step 3: Initialize Memory (DirectMemory — CANONICAL)
```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.direct_memory import DirectMemory
dm = DirectMemory()  # Auto-starts session, stdlib-only, <0.1s
# dm.record("session_start", {"purpose": "..."})  # auto-recorded
```

> **SessionRecorder and CodebuffTracker are DEPRECATED and hard-blocked (raise ImportError).** Use DirectMemory for ALL session recording.

### Step 4: Check Current State
- **Python 3.14t ONLY**
- **Bun v1.3.14** for Windows stability
- **Worm registry cache** at `~/.azazael/worm_registry_cache.pkl` (pickle)
- **DirectMemory** at `CORE.direct_memory` — CANONICAL, stdlib-only, <0.1s, atexit-safe
- TEST_BASELINE: 87 passed, 0 failed (requires pytest stub on 3.14t)
- LESSONS: 87 in LESSONS_MASTER.md
- ERROR LOG: 138 errors logged (highest ID #187) in ERROR_LOG.md

---

## CURRENT STATE SNAPSHOT (June 14, 2026 — Session 2)

### Mypy + Pyright Type Audit (This Session)
- **2 skills created**: `azazael-mypy` (#59), `azazael-pyright` (#60) — both `auto_load: true`
- **pyrightconfig.json** created with balanced strictness (basic mode, excludes build artifacts)
- **7 `__init__.py`** files added to resolve module naming conflicts
- **3 files fixed**: `install_manager.py`, `rust_runner.py`, `go_runner.py` — complete indentation rewrites (method bodies were at class level)
- **mypy**: 1,466 → 1,248 errors (-218, -14.9%)
- **pyright**: 1,976 → 1,224 errors (-752, -38.1% with pyrightconfig.json filtering)

### Autodiff Suite (Previous Session — June 14, Session 1)
- **4 skills created & registered** (#55-58, `auto_load: true`): forward-mode, backprop, gradient optimizers, higher-order derivatives
- **3 test files**: `test_autodiff_skills.py` (34/35 pass), `test_optimizers_convergence.py` (46/46 pass), `benchmark_autodiff_modes.py` (4 benchmarks)
- **Skills on disk**: 39 .md files (was 36), pre-loaded skills: 72 (was 68)
- **Mygrad 2.3.0 on 3.14.5t**: 4 limitations diagnosed, 3 workarounds implemented across skill docs
- **Test coverage**: 3.5 → 4.0 (115+ new tests), Architecture quality: 6.2 → 6.3

### Architecture State
- **DirectMemory is the CANONICAL memory system** — Session ID `codebuff_20260614_124931` active
- **No inference/NIM/Hermes code exists.** The codebase documents but has zero implementation.
- **Worm registry cache** at `~/.azazael/worm_registry_cache.pkl` — <0.1s warm load
- **Tests fixed** with pytest stubs; use `python tests/test_*.py` directly (pytest segfaults on 3.14t)

### Known Issues
- G: drive is slow (SD card) — use 600s+ timeouts
- pytest segfaults on 3.14t (Error #48) — use `python tests/test_*.py` directly
- Nuitka 4.1.2 builds fail with LNK2001 on 3.14t free-threading
- **NEVER delete, move, or re-create files outside ~/azazael** without permission
- **Desktop is SACRED** — do not touch without user asking
- Worm registry cache uses pickle — invalidate manually if worms are added/removed
- `jacobian()` in skill docs has auto-fallback to finite differences when seeded backward fails
- `clip_gradients()` uses `p.grad[:] *= x` to bypass mygrad 2.3.0 property setter limitation

### Files to Read First
- `azazael/SYSTEM_INSTRUCTIONS.md` — All RULEs 0A-0K, COMPLIANCE SENTINEL, 🛑 PRE-ACTION GATE banner
- `azazael/SOP.md` — All canonical mandates, error recording, cleanup
- `azazael/ERROR_LOG.md` — 138 errors logged (highest ID #187)
- `azazael/MEMORIES.md` — Anti-patterns #1-11
- `azazael/LESSONS_MASTER.md` — 57+ lessons
- `azazael/LESSONS_DESTRUCTIVE_BEHAVIOR.md` — ⚠️ CRITICAL: 4 incidents, 6 prevention rules
- `azazael/CODEBASE_AUDIT_TODO.md` — Living production plan (v9)

### Session 2026-06-16 — WSL Canonical Merge Complete

**Status:** ✅ WSL canonical version at /root/azazael/ fully merged to Windows

**Changes this session:**
- Found WSL canonical at /root/azazael/ (475 .py files, 286 .md, 87 skills)
- Synced all source files: zero differences between WSL and Windows src/
- ANIMATION_PROTOCOLS.py case conflict resolved
- 839M build artifacts archived to archive/build_artifacts/
- 42 root .json files → archive/data/
- 11 root _*.py scripts → archive/scripts/
- 6 root .txt files → archive/logs/
- 5 Windows-only source files copied to WSL canonical
- 97 test files synced from WSL to Windows
- .gitignore created (13 pattern groups)
- 4 autoflake unused imports fixed
- 4 inference skills synced to WSL
- DirectMemory initialized (session codebuff_20260616_232033, 37+ events)

**Current state:**
- Python 3.14.5t
- 37 worms discovered
- ClusterWORMZ: OK, NatureCluster: OK
- DirectMemory: 22,442 events, 803 sessions, 47.7MB
- Skills: 92 WSL, 91 Windows
- Tests: 97 files synced (pytest timed out, azazael-core 1 failure)
- Archive: 841M organized in archive/

**Pending:**
- G: drive sync (robocopy timed out at 600s)
- Full pytest run (timed out at 300s)
- Mypy re-run from azazael/ directory
- BAT file tests (0% pass rate in orchestration)

**RESTART_PROTOCOL_REQUIRED:** FALSE

### Session 2026-06-17 — Post-WSL Merge Fixes

**Status:** ✅ Active — fixes in progress (session codebuff_20260617_020546)

**Changes this session:**
- RULE 0Z-G (No Busy Work) codified in MANDATES.md
- RULE 0Z-B bridged to 0Z-G — 11 followups must be actionable fixes
- PRE-ACTION GATE now includes RULE 0Z-G check
- Agent inventory clarified: 10 spawnable + 1 auto-managed
- Gate check counts corrected: 14→17, 17→18
- Cross-document audit by Gemini: 5 inconsistencies found, 4 fixed in MANDATES.md
- Shell=True fixes completed (11 fixed, 5 intentional)
- nim_client.py docstring API key fixed
- threading_utils.py syntax error fixed
- azazael_cli.py + dashboard.py clear screen → ANSI escape (os.system removed)
- .gitignore expanded (7 pattern groups)
- MANDATES.md RULE 0Z-B override removed
- SESSION_HANDOFF.md deleted (busy work)
- CODEBASE_AUDIT_TODO.md session notes reverted (busy work)

**Current state:**
- Python: 3.14.5t
- WSL canonical: /root/azazael/ (synced)
- Source diff: 0
- DirectMemory: 22,803 events, 803 sessions
- Mypy: 2,843 errors baseline
- Ruff: 922 remaining (400 auto-fixed)
- Shell=True: 11 fixed, 5 intentional
- Bare excepts: 0 remaining in live project (src/ + scripts/, AST-verified; was 68 in src/CORE)
- Over-broad catch-alls (`except Exception`/`except BaseException`): 1241 in src/ + scripts/, budget-capped by `scripts/check_no_catch_alls.py` and CI `catchall-guard.yml` (can never regress)
- Test failures: 1 (test_cancellation_integration)

### Session 2026-08-08 — Startup + Anti-Pattern Scan + os_system Fix (WSL)

**Status:** ✅ Active — session `codebuff_20260808_073807`

**Changes this session:**
- Session startup complete: 12 skills loaded, RULE 0K canonical docs read in order, 132 skills synced (RULE 0R/0R-A), DirectMemory recording verified, compliance state machine healthy at CODE_EDIT, worm registry pre-warmed
- FreeBuff verified v0.0.142 (npm) — bun NOT installed per user directive
- Anti-pattern scan (ASTAntiPatternScanner, 680 files): 2,439 findings — 1,178 import_inside_function (known-intentional lazy pattern), 1,154 unicode_emoji (backlog, concentrated in CODEX video generators), 79 hardcoded_win_path, 11 os_system, 16 t_string (ALL false positives), 1 fstring_backslash (false positive), 0 cls_new_factory
- Fixed the only real os.system: `scripts/db_health.py` → ANSI escape + removed unused `import os` — tree os_system 11 → 10 (remaining = scanner test fixtures)
- Temp cleanup: removed sentinel_gate.py.tmp x2 + _test_run.log (full-depth .tmp sweep now empty)
- RULE 0R demo: skill edit → sync propagation verified (canonical ↔ .agents byte-identical) → reverted clean
- Standing directives armed: sync after canonical/skill edit; RULE 0V/0W gate before next code change

**Pending:**
- 79 hardcoded_win_path findings · 1,154 emoji backlog · telemetry generation (sentinel_enforcer block) · t_string scanner false positives
