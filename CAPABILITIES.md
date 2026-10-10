# CAPABILITIES.md — proven working, with the exact invocation

> *Every edit to this file is gated: `prepare_guard.py permit` is required, and
> a permit is only minted by a fresh `prepare()` call. Verified 2026-09-30 — the
> guard refused `Add-Content`, `open(...,'a')`, and this agent's own Edit tool
> until a receipt existed.*

> *Created 2026-09-30. Every line here was MEASURED on this machine on
> 2026-09-30, and every command was executed successfully. This is the
> opposite of a lessons file: it is the inventory of things that WORK, so a
> future session reuses them instead of re-deriving or half-building them.*

**The rule this file exists to enforce:** propose only what has been run. If a
solution is untested, say so. A verified capability is worth more than a
plausible one, and a half-built dashboard nobody can see is worse than no
dashboard.

---

## 1. IMAGE GENERATION — headless ComfyUI on Intel Arc (XPU)

**Status: PROVEN. Running now.**

Intel AI Playground 3.1.0 ships a complete ComfyUI backend plus a working
Intel XPU PyTorch. The Electron UI is not required.

```powershell
$py   = "C:\Users\clint\AppData\Local\Programs\AI Playground\resources\ComfyUI\.venv\Scripts\python.exe"
$app  = "C:\Users\clint\AppData\Local\Programs\AI Playground\resources\ComfyUI"
& $py "$app\main.py" --listen 127.0.0.1 --port 8188
```

Then POST a workflow to `/prompt`; results land in `/history/<prompt_id>`.
`--output-directory` and `--disable-auto-launch` are both accepted.

**Measured environment (quote this, it is why the model choice works):**

| property | value | measured by |
|---|---|---|
| torch | `2.11.0.dev20260317+xpu` | `torch.__version__` |
| XPU available | `True` | `torch.xpu.is_available()` |
| device | `Intel(R) Arc(TM) 140T GPU (8GB)` | `get_device_properties(0).name` |
| **usable GPU memory** | **7.80 GB** | `get_device_properties(0).total_memory` |
| python | 3.12.12 | the venv |

**Model layout** — `extra_model_paths.yaml` redirects lookup to
`...\resources\models\ComfyUI\`:

| folder | FLUX role |
|---|---|
| `diffusion_models/` | UNet |
| `text_encoders/` | T5-XXL |
| `clip/` | CLIP-L |
| `vae/` | VAE |
| `checkpoints/`, `loras/`, `controlnet/`, `upscale_models/`, `insightface/`, `facerestore_models/`, `inpaint/`, `nsfw_detector/` | also resolved |

**Ready-to-run harness (staged, preflight-verified):**
- `tools/comfyui_flux_headless.py` — preflight checks torch+XPU and every
  model's **exact byte count** before booting, then starts headless, confirms
  the device from `/system_stats`, queues, and reports the output path.
  `--preflight-only` to check without starting.
- `tools/flux_probe_api.json` — the API-format workflow.

**FLUX.1-schnell settings that are not arbitrary:** **4 steps, cfg 1.0**,
`EmptySD3LatentImage`, `DualCLIPLoader type=flux`. Schnell is
guidance-distilled — higher cfg and more steps *degrade* it rather than refine.
Its UNet is 11.89 GB on a 7.80 GB card, so **ComfyUI offloads to system RAM:
free RAM is the binding constraint, not VRAM.**

---

## 2. GPU MEMORY — the right probe, and the wrong one

| probe | says | trust? |
|---|---|---|
| `torch.xpu.get_device_properties(0).total_memory` | **7.80 GB** | **YES — this binds the device** |
| WMI `Win32_VideoController.AdapterRAM` | 4.00 GiB | **NO — a static aperture** |
| a note previously in canon | 2.1 GB | **NO — wrong twice** |

`src/TOOLS/hardware_deteck.py` / `hardware_detect.py` reads `AdapterRAM` and is
the origin of the bad number. **Never size a model decision off it.**

---

## 3. 3D RENDER — Blender Cycles on the same Arc, via ONEAPI

**Status: PROVEN. Blender 4.5.10 LTS installed.**

```powershell
& "C:\Users\clint\blender\blender-4.5.10-windows-x64\blender.exe" `
   --background --factory-startup --python "<script>.py"
```

**Measured**, 1024×1360, denoising on, 3 area lights, 85 mm lens:

| samples | wall clock | images/hr |
|---|---|---|
| 64 | 8.5 s | 423 |
| 256 | 16.0 s | 225 |
| **1024** | **34.3 s** | **105** |

**Always quote the device with a render time.** CPU fallback is a 13× swing on
this machine; a time without a device is not a measurement.

**Gotchas that cost real time:**
- `bpy.ops.mesh.primitive_*_add` **ignores `name=`** → `KeyError`. Diff
  `set(bpy.data.objects.keys())` around the op to get the handle.
- `bpy.context.object` is unreliable under `--factory-startup`.
- Build materials **after** the last `read_factory_settings()`, or
  `ReferenceError: StructRNA of type Material has been removed`.
- `MetaBall` has no `use_even_offset` in Blender 4.x.
- Separate meshes = visible seams under specular light. For a continuous
  surface: metaball field → convert → **voxel remesh** → smooth → subdiv.
  Seams are what made a figure read as a "block robot".

---

## 4. LIVE PROGRESS — must be watchable, not just written

**Status: PROVEN. Running at http://127.0.0.1:8099/**

```powershell
python azazael\tools\flux_dash.py --port 8099     # opens the browser itself
```

A 1.5-hour download that reports only into an assistant's tool output feels
broken and forces a check every thirty seconds. **A file on disk is not
watchable.** The working shape is: an HTTP server that samples the real file
sizes on **every request** and serves HTML with a 2-second `<meta refresh>`,
opened in a real browser window. A PNG that re-renders on a timer
(`tools/capture_flux_download.js` → `dashboard/flux_download.png`) is a
*secondary* artefact — good for a record, not a substitute for a live view.

**A rate readout needs two samples before it means anything.** First-tick
values are garbage: a delta over a near-zero interval, or an average over zero
elapsed. Both monitors shipped this bug; show `--` rather than `0.0 MB/s`
until the second sample lands.

---

## 5. ENFORCEMENT — the hooks, and how to prove they work

**Status: PROVEN. 13/13 oracles run, 10/10 negative controls pass.**

```powershell
cd C:\Users\clint\azazael
python tools\terence_invariants.py --self-test          # negative controls
python tools\terence_invariants.py --coverage           # the gap list
python tools\terence_invariants.py --autonomous --dry-run
python -m pytest tests\test_rule_0b_a_edict.py -q       # 9 passed
```

- **RULE 0B-A** — `sentinel_gate.py::validate_rule_0b_a()` fails a gate on
  acceptance language ("this passes", "clears the rule", "good enough"). 9 tests.
- **RULE 0B-C** — every oracle ships a **negative control**; an oracle whose
  control fails is UNVALIDATED and **barred from licensing a destructive
  remedy**. This caught 3 of 8 oracles being wrong on its first run.
- A detector reporting an **absence** needs a **positive capability test**, not
  a negative control — write a fixture that really invokes the thing and prove
  the detector finds it.
- `_run()` in terence_invariants **already prepends `sys.executable`**; pass
  arguments only.
- `permit_here()` is `@contextmanager` and therefore **single-use**; a fresh one
  per iteration. The enforcer's audit hook denies ungated writes *anywhere*.

**Audited canon:** `MANDATES.md` (RULE 0B, 0B-A, 0B-B, 0B-C), pre-action gate
checklist in `SYSTEM_INSTRUCTIONS.md`, `AGENTS.md` mirror, `ERROR_LOG.md`
(#210–#215), `RULE_AUDIT_TODO.md`.

---

## 6. MEMORY — PMB, the durable store

**Status: PROVEN. ~300 events, workspace `04a151a73354`.**

```powershell
$env:PYTHONIOENCODING = "utf-8"     # set this or non-ASCII raises on Windows
& C:\Users\clint\.pmb-venv\Scripts\python.exe <script>.py
```

- daemon `http://127.0.0.1:8765/mcp`, token `C:\Users\clint\.pmb\daemon.token`
  (**bearer auth is unconditional**; `/health` is not an MCP route)
- tools: `prepare`, `record_batch`, `recall`, `find_lessons`, `recall`,
  `mark_lesson_followed`, `lesson_impact`, `store_ai_reflection`
- **`prepare()` returns 0 lessons in Kilo** — its surfacing is hook-path only
  and Kilo has no hooks. Call `find_lessons(query=…)` directly instead.
- **`recall()` takes `query` only** — no `limit`; passing one raises.
- Reflections go through `scripts/meta_reflect.py`, which validates: material,
  **≤280 chars**, evidence-linked, non-duplicate. Feed it **one class plus its
  incidents**; feed it incidents alone and it enumerates them and gets
  **rejected as an essay**.

---

## 7. VLP — signed, hash-chained audit trail

```python
sys.path.insert(0, r"C:\Users\clint\azazael\src")
from CORE.audit_trail import (audit_session_start, audit_error_occurrence,
                              audit_file_edit, verify_head_hash, anchor_head_hash)
```

**The anchor is written by an `atexit` hook.** A script that calls
`close_session()` without anchoring leaves a trail that
`verify_head_hash()` correctly reports as `(False,'','')`. Anchor explicitly,
then verify — verified `True` on
`.audit/session_20260930_041312_01a0.jsonl`, head `c009072d…`.

---

## 8. Known-broken, do not re-attempt

- **Full `pytest tests/` fails at collection** —
  `tests/test_replay_failed.py - PermissionError`. That file **passes alone**
  (3 passed). Cause: the enforcer's audit hook is process-global, so once any
  earlier test imports it, later tests run under write interception. Not fixed.
- **Semantic duplicate-rule detection has no working threshold.** Over 741 title
  pairs, the true pair `0J`/`0S` scores 0.308 and the false pair `0C`/`0J` also
  scores 0.308. Declared pairs instead: `0E`/`0E-1`, `0J`/`0S`.
- **`prepare()` lesson surfacing — BROKEN, see §8** — and the lesson loop is
  therefore **not** listed as a working capability anywhere in this file. The
  `4% follow-through` figure it prints measures a step that never runs.
- **The daemon selectively refuses connections** (pid 7896, 585 min, warm):
  `recall` and `record_batch` succeed while `find_lessons` failed on two
  consecutive attempts. Undiagnosed. `pmb daemon restart` is the obvious probe
  and **had not been run** — itself an instance of RULE 0B-D: recommending a
  probe is not running it.
- **Pebbles & Bamm-Bamm likeness is not rendered.** Script
  `tools/blender_session_20260930/blender_pebbles.py`; FLUX is the better
  instrument for it once §1 is up.
- **Rule-copy drift unchecked** — the 0B family now exists in `MANDATES.md`,
  `SYSTEM_INSTRUCTIONS.md` and `AGENTS.md` (all three verified), and in the
  skill copies under `azazael/skills`, `.agents/skills`, `~/.agents/skills` and
  `skills.win-backup`, which were **never diffed** and may still carry the
  pre-0B-A text. `RULE_AUDIT_TODO.md` P4.3.

---

## 9. TECHNIQUE LAYER — how much is actually adopted (measured 2026-10-09)

Call path: `src/CORE/technique_runtime.py` registers 181 harvested techniques, and
(historically) `tools/exercise_technique_runtime.py` reported `corpus 181 / wired 181 /
engaged 181 / errored 0` — archived 2026-10-10 to `archive/theater-2026-10-10/`, so
quote the registry numbers (`load_slices` 9/9 ok, 181 wired, verified 2026-10-10),
not the archived script. **That is a statement about the registry, not about the
codebase** — read alone it overstates capability, so it must not be quoted as coverage.

Production call sites into the layer, measured by grep over `src/` excluding the
layer itself and `tools/`:

| technique boundary | production caller |
|---|---|
| plan modelling (3 symbols) | `WORMS/METACLUSTER.py` (`plan_dag`, `eliminate_common_subgraphs`, `record_dispatch_plan`) |
| edit verification | `sentinel_enforcer.py` (`verify_boundary`, advisory-only) |
| failure reflection | `circuit_breaker.py`, `WORMS/METACLUSTER.py` (`reflect_on_failure`, fail-open) |

So: **181 techniques have a call path; 4 production call-site locations (6 symbol
invocations) reach it** (corrected 2026-10-10: the earlier count of 5 included
`WORMS/expansion/engram.py` read-pressure, which is intra-module — defined at
`engram.py:673`, consumed at `:725`/`:738` in the same file, with zero imports of
any technique module — so it is not a call site *into the layer*). The
remaining adoption work is T-13 in `TODO_315T_BUILD.md`; the reassignment of the 48
rows that pointed at the wrong host is in `SOTA_ROW_RESCORE.md`. Coverage must
be counted as production call sites per technique, with exercise-only engagement
scored zero.
