# TODO — 3.15t build plan (2026-10-09)

Scope: what still has to be built or fixed to run Azazael *only* on the 3.15t
production interpreter, with the meta-evolution loop actually closed. Every
line below is either something this session verified with a command whose output
is quoted, or it is marked `UNVERIFIED`.

Companion evidence (all in `azazael/state/`):
`dep_gap_315t.json`, `technique_deps_315t.json`, `repoint_315t.json`,
`py315t_suite.log`.

---

## 0. Hardware reality — read this before planning anything "GPU"

| | |
|---|---|
| GPU present | **Intel(R) Arc(TM) 140T iGPU, 8 GB shared** (`Win32_VideoController`; driver 32.0.101.8991) |
| CUDA | **none** — no NVIDIA device, no `nvidia-smi` anywhere on the box |
| torch in py315t | `2.16.0.dev20261006+cpu` → `torch.cuda.is_available() == False` |
| CPU | 16 threads, free-threaded 3.15.0rc3 (`gil_enabled=False`) |

**Superseded later the same day — see §5.** The first cut of this section
concluded the accelerator was unreachable. Measurement showed an Arc-binding
runtime *is* working on this box, in two interpreters that are not py315t. The
original reasoning is kept below because its scope limit still holds: there is
no CUDA target, and no in-process accelerator for py315t.

**Consequence, and it changes the plan:** "use the GPU for speed" is not
available in the way it usually means. There is no CUDA target to move work to,
and the Intel paths that *do* exist are the two currently blocked on wheels
(§3). So the honest sequencing is:

1. **GPU workstream is blocked on packaging, not on intent.** Unblocking it is
   T-6/T-7 below; until then, every acceleration claim must be CPU-side.
2. **The CPU-side speedup is real and already in place**: free-threaded 3.15t on
   16 threads is exactly what the parallel/worker machinery in this repo was
   written for, and the GIL is provably off. Optimise there first.
3. Any TODO line that assumes CUDA must be struck or rescoped.

---

## 1. Verified working (do not rebuild)

| Subsystem | Evidence |
|---|---|
| py315t is a real free-threaded env | `3.15.0rc3`, `free-threaded=True`, `gil_enabled=False`, 245 site-packages entries |
| Test suite collects on 3.15t | `4047 tests collected in 4.97s` |
| **LocalMemoryStore writes live** | probe: row `2201713` into `~/.azazael/memory_store.db`, `rows 94366 → 94367`, read back |
| **DirectMemory writes live** | probe: row `2201715`, `+2` rows, `memories_fts == memories` (94,369) — FTS in sync |
| PAMS installed in py315t | `persistent_ai_memory`, `aiohttp`, `mcp`, `fastapi`, `uvicorn`, `watchdog` all resolve |
| MCP `pams` repointed to py315t | `~/.agents/mcp.json` → `C:\Azazael\.venvs\py315t\Scripts\python.exe`, valid JSON, 4 servers |
| Chain controller inherits 3.15t | `_python()` returns py315t for all 22 jobs incl. `render` and `meta` |
| Ouroboros renderer runs on 3.15t | `render-ouroboros: wrote dashboard/ouroboros.html (88,277 bytes)` |
| 6 SOTA incorporation exercises run on 3.15t | all exit 0, `chain: true`, each cited to `.audit/session_*.jsonl` |
| Audit appender is now concurrency-safe | `audit_append_stress.py`: atomic `1000/1000` records, `chain_ok true`; buffered control loses 112 |

---

## 2. Build tasks

Ordered by dependency, not by appeal. `GPU` column answers the new question
directly: *can this be made faster with the Arc iGPU?*

| # | Task | Why it exists (evidence) | GPU | Est. |
|---|---|---|---|---|
| **T-1** | **Re-enable and re-point the `Azazael-Chain` scheduled task** | `chain_controller.py --status`: `"task_state": "disabled"`, `"task_detail": "Disabled"`. Consequence: no `chain_controller_due.json` ever exists → `chain_ops.py` prints `NO_DATA: chain_controller_due.json missing` → the ouroboros MEASURE arc and DEAD-STORES card read a file nothing writes | n/a | S |
| **T-2** | **Close the meta-evolution loop: schedule the producer hop** | `logs/evolution_cycle.log` was **0 bytes** until this session ran the cycle; `evolution_progress.py` → `NO_DATA - no cycles parsed`; `fitness_arm_liveness.py` → `NO_DATA`; `evolution_cycle.py` itself logs `loop_integrity.json absent -- BLIND`. Running the cycle then the instruments produced `loop_integrity.json` + `fitness_arms.json` — the loop works, it is simply never fired | n/a | S |
| **T-3** | **Make the promotion gate actually gate** | `evolution_cycle.py` EV-7 line: `absent -- BLIND, not treated as healthy and not treated as blocking`, returns `(True, None)`. The prompt calls it "the last ouroboros arrow", and `render_ouroboros.py:888-892` bakes the claim *"promotion is currently blocked"* into the page — a static assertion of a live condition inside a data-driven readout. Either the gate blocks on staleness or the page must stop claiming it does | n/a | M |
| **T-4** | **Stop rendering faster than the inputs change** | `render` fires every **300 s** (`chain_controller.py:37`) while its inputs change at **600 s** (`evolution`) and **1800 s** (`terence`). One-line cadence change; 2×–6× fewer full ring rebuilds | n/a | S |
| **T-5** | **Collapse the four independent parsers of one log** | `logs/evolution_cycle.log` is parsed by `render_ouroboros.py:117-140`, `evolution_progress.py:112+`, `fitness_arm_liveness.py:63+`, `process_benchmark.py:93-99`, each with its own regex vocabulary and its own capture groups for the same line (`RE_PROMO` in two files). Extract one parser module; every consumer imports it | n/a | M |
| **T-6** | **Unblock the Intel GPU paths** | `--only-binary` installs: `faiss-cpu`, `hdbscan`, `igraph`, `rustworkx`, `psycopg2-binary` → `BLOCKED_NO_WHEEL`; `chromadb` → dependency conflict; `onnxruntime`/`openvino`/`ray`/`llama-cpp-python` are sdist-only per `requirements-3.15t.txt`. Intel acceleration for Arc (oneAPI/OpenVINO/IPEX) needs these wheels to exist before any GPU claim can be made | **THIS IS the GPU unlock** | L |
| **T-7** | **Evaluate `torch` XPU for Arc, or document the refusal** | torch here is `+cpu`. Arc is reachable in principle via `torch.xpu` (oneAPI), but no 3.15/free-threaded XPU wheel was found. Decide with a measurement, then record the verdict so this is not re-litigated every session | **the other GPU unlock** | M |
| **T-8** | **Repair the torn audit records** | `~/.audit/daemon_health.jsonl` has 345 records + **2 orphan fragments** (lines 42, 110) plus 2 genesis-linked records (lines 346-347) written by the buggy writer. The writer is fixed; the existing file still fails `verify_audit_chain` | n/a | M |
| **T-9** | **Reconcile the 18 duplicate SOTA records** | `SOTA_STEAL_AUDIT.md` §7.8: 18 episode codes are one paper entered twice under two names, deliberately left in place because deleting stored observations is a memory-store mutation. Needs a decision + a merge path | n/a | S |
| **T-10** | **Prune the memory-store debt** | `MEMORY_FORENSIC_REPORT`: ~2.6 GB stale DirectMemory backups, 657,817 `otel_spans`, 10 empty duplicate PAMS dirs, 6 sessions left open | n/a | S |
| **T-11** | **Build the L1/L3 blueprint items that need real work** | `SOTA_INTEGRATION_BLUEPRINT.md` P0/P1: ATP ledger proofs + MAFIA retrieval audits + MemHarness reconstructive recall; then the unified acceptance gate. Everything else in the blueprint depends on the gate | CPU (16 threads) | L |
| **T-12** | **Re-audit for 3.15.0 final** | All of the above sits on `3.15.0rc3`. The `requirements-3.15t.txt` note says the sdist-only set is to be re-resolved "at 3.15.0-final re-audit" | n/a | M |

---

## 3. Blocked on wheels (verbatim tool output)

```
BLOCKED_NO_WHEEL  faiss-cpu  hdbscan  igraph  rustworkx  psycopg2-binary
FAILED            chromadb     (dependency conflict — read the resolver output)
sdist-only        onnx (no 3.15 wheel of ANY kind), onnxruntime, openvino, ray, llama-cpp-python
```

Installed this session (12): `z3-solver, stable-baselines3, sb3-contrib,
optuna, matplotlib, pyvis, loguru, msgpack, wrapt, pypdf, openai,
sentence-transformers`.

Each blocked name is a capability that is currently *switched off*, not merely
missing: `faiss` gates vector search in `engram.py`, `hdbscan` gates density
clustering in `cluster_route.py`, `onnxruntime` gates the compression pipeline.
`install_technique_deps_315t.py --check` re-measures the set on demand.

---

## 4. Sequencing rule

T-1 and T-2 before anything else: a loop that never fires cannot be made
efficient, and every "is the loop healthy" question is unanswerable while its
instruments have no data. T-3/T-4/T-5 are CPU-only correctness and efficiency
fixes that can land today and are not blocked by any accelerator question.

> **Correction (same day).** §4 originally called T-6/T-7 "the only real GPU
> unlocks". §5 replaces that: the accelerator is reachable *today* out-of-process,
> so T-6/T-7 are downgraded from unlocks to cleanups.

---

# §5 — THE CUDA RECIPE, STOLEN AND PORTED TO ARC 140T

Measured 2026-10-09 on this machine. Every value below came from a command whose
output is quoted in this section; nothing is carried over from a document.

## 5.0 The steal, layer by layer

"Steal the CUDA recipe" means: take each layer the CUDA stack gives you, find the
Intel-stack equivalent, and mark the one layer that has no equivalent. That last
row is the whole design constraint.

| CUDA layer | Intel-Stack Equivalent | State on this box | Evidence |
|---|---|---|---|
| NVIDIA driver + `nvidia-smi` | Intel graphics driver | **present** — driver `32.0.101.8991`; no CLI telemetry tool exists | `Win32_VideoController.DriverVersion` |
| CUDA runtime | oneAPI **Level Zero** | **partial** — `ze_loader.dll` present, **`ze_intel_gpu.dll` ABSENT** (only `ze_intel_gpu_raytracing.dll`) | `ls /c/Windows/System32/ze_intel*.dll` |
| `torch.cuda` device | `torch.xpu` | **works — in a different interpreter.** `torch 2.11.0.dev20260317+xpu`, `xpu.is_available() True`, `device_count 1`, `Arc(TM) 140T GPU (8GB) 7.8 GB`. The venv is **Python 3.12.12** (AI Playground ComfyUI) | direct probe |
| `nvidia-smi -q` / device props | `torch.xpu.get_device_properties` | **works** in that same 3.12 venv → **7.80 GB** (the probe `CAPABILITIES.md` §2 validated; WMI's 4 GiB aperture is wrong) | direct probe |
| cuBLAS/cuDNN + `nvcc` | oneAPI **2026.0**: oneMKL, oneDNN, DPC++/`icpx`, `ocloc` | **present** at `C:\Program Files (x86)\Intel\oneAPI` | `ls` of the toolkit tree |
| vLLM / TensorRT-LLM serving | **OpenVINO GenAI 2026.4.0** (py314) — enumerates `CPU`, `GPU` → `Intel(R) Arc(TM) 140T GPU (8GB) (iGPU)`, `NPU` → `Intel(R) AI Boost`; GPU `arch=v12.74.4` | **works today** | `ov.Core().available_devices` |
| — (second serving path) | **llama.cpp Vulkan** `llama-server.exe` | **works today** — `--list-devices` → `Vulkan0: Intel(R) Arc(TM) 140T GPU (8GB) (8972 MiB, 8267 MiB free)`. The sibling CPU build reports `(none)` | `--list-devices` |
| Stable Diffusion on CUDA | ComfyUI on XPU (AI Playground venv) | **proven** — FLUX.1-schnell, 4 steps, cfg 1.0 | `CAPABILITIES.md` §1 |
| OptiX / CUDA render | Blender Cycles **ONEAPI** | **proven** — 34.3 s @ 1024 samples | `CAPABILITIES.md` §3 |
| **in-process `torch.cuda` in your own venv** | **in-process `torch.xpu` on 3.15t** | **DOES NOT EXIST.** py315t torch is `2.16.0.dev20261006+cpu` → `xpu False, count 0`; py314 torch is `2.14.0+cpu` → `xpu False, count 0`. Only the py3.12 venv has a `+xpu` build | direct probe of all four interpreters |

## 5.1 The load-bearing conclusion

Exactly one CUDA affordance is unavailable: **the production interpreter's torch
talking to the accelerator in-process.** Everything else has a working
equivalent, and two of them are already up.

So the correct port is the design a CUDA user reaches for when the GPU is on
another box: **put the accelerator behind an OpenAI-compatible HTTP boundary and
talk to it from 3.15t.** That converts a packaging problem (find a
free-threaded 3.15 XPU wheel that does not exist) into a service problem (start
a process), and it is available today. It also removes the single largest risk
in T-6/T-7 — waiting on wheels that may never ship — by making them optional.

## 5.2 The three numbers that look contradictory, and are not

| Probe | Says | What it actually measures |
|---|---|---|
| `torch.xpu.get_device_properties(0).total_memory` (py3.12) | **7.80 GB** | bindable budget for torch allocations |
| Vulkan `--list-devices` | 8972 MiB total, **8267 MiB free** | Vulkan heap over the same aperture |
| WMI `AdapterRAM` | 4.00 GiB | a static aperture field — **do not size anything off it** |

All three describe **one 8 GB aperture shared with system RAM.** They are not
additive, and a model that fits "in 7.8 GB" still competes with the OS and the
CPU-side copies. This is the structural difference from a discrete CUDA card, and
it is why §5.4's measurement gate is not optional.

## 5.3 Tasks

| # | Task | Why (evidence) | Depends | Est. |
|---|---|---|---|---|
| **G-1** | **Build the accelerator sidecar** — `tools/accelerator_sidecar.py`: pick a backend in priority order, expose `/v1/chat/completions` + `/health`, and have `/health` report the device that is **actually bound**, read from the backend rather than from config | This is the port in §5.1. Backends, in preference order: (1) OpenVINO GenAI **GPU** on py314, (2) llama.cpp **Vulkan** `llama-server.exe`, (3) OpenVINO **NPU**, (4) CPU | — | M |
| **G-2** | **Register the sidecar in `providers.py`'s chain** | The chain already carries a `llamaserver` entry and an `OpenVINOProvider`, so the failover machinery exists. This is what lets the loop *use* it instead of burning cloud quota | G-1 | S |
| **G-3** | **Feed the meta-evolution loop from it** | The `meta` hop is the loop's own evaluation step and the natural consumer: free local inference there means the loop can afford more cycles. Add an ACCELERATOR arc to the ouroboros with the sidecar's `/health` device field as its real instrument — no literal-`True` arcs (see T-3's finding) | G-2 | M |
| **G-4** | **Benchmark before claiming** — per backend × per device, prefill and decode tok/s, device string recorded next to every number | §5.4. Honest prior: shared-memory iGPU is bandwidth-bound, so **decode** on the Arc may not beat a 16-thread free-threaded CPU while **prefill** may win clearly. The measurement decides which backend gets priority (1) — **measured, and it REFUTED the prior: see §5.6** | G-1 | **DONE** |
| **G-5** | **Route the dashboard's image work to the proven XPU path** | `capture_archetypes.js` renders ouroboros archetype PNGs; `CAPABILITIES.md` §1 already proves ComfyUI on XPU on this card | — | S |
| **G-6** | **Close the Level Zero gap, or record the refusal** | `ze_loader.dll` present but `ze_intel_gpu.dll` absent. Not blocking today (OpenVINO and Vulkan each bind the device), but it is the prerequisite for any future in-process XPU. Install the full compute runtime **or** write the refusal down | — | S |
| **G-7** | **Document the in-process refusal and stop re-litigating it** | Record: XPU wheels track CPython releases; **no free-threaded 3.15 XPU build exists**; the py3.12 venv is the only `+xpu` torch on the box; therefore py315t will never be the host of `torch.xpu`. This closes T-7 with a measurement instead of a hope | G-4 | S |
| **G-8** | **Optional higher ceiling: SYCL rebuild via oneAPI 2026.0** | `-DGGML_SYCL=ON -DGGML_SYCL_F16=ON`. Carries a **known failure**: the prior `ipex-sycl` build dies loading `api-ms-win-crt-filesystem-l1-1-0.dll`, and Jan's Vulkan `b9967` was the working substitute. Attempt only after G-1/G-3/G-4 are stable | G-4 | L |

## 5.4 The measurement gate (non-negotiable)

A speed claim about this device is only admissible with all four of:

1. the **device string** the backend bound (`Vulkan0 …`, `GPU Intel(R) Arc(TM) 140T`, `NPU Intel(R) AI Boost`);
2. **tok/s reported separately for prefill and decode** — they are different bottlenecks and averaging them hides the answer;
3. the **same model and the same prompt** on the CPU baseline, on the same run;
4. the **free-memory state** at start, because the aperture is shared and a benchmark run next to a loaded ComfyUI is not a benchmark.

`CAPABILITIES.md`'s Blender line already encodes this rule for renders — *"a
time without a device is not a measurement"*. §5.4 is the same rule for tokens.

## 5.5 Do not build these (known-bad outcomes)

- **A `torch.xpu` build for py315t from source.** `docs/TORCH_BUILD_TROUBLESHOOTING.md`
  records SYCL toolkit detection failing (`Can not run SYCL_CMPLR_TEST`), and the
  archive notes show the cp314t torch build only succeeded with `USE_XPU=0
  USE_KINETO=0`. The previous "GPU inference blocked by Intel oneAPI compiler
  bug" note was retired on that basis. Re-doing this costs days for a known result.
- **`torch-directml`.** Already characterised as having no wheel for modern Python
  (`PROTEUS_DEEP_EXPANSION.md`).
- **Assuming the NPU is a fast LLM device.** It enumerates and it works, but it is a
  low-power accelerator: published and community results put NPU token generation
  below CPU for several quantised LLMs, with the wins in power efficiency and in
  CNNs/VLM prefill. It earns its place as backend (3) behind a measurement, not by
  assumption.
- **Sizing any model off WMI `AdapterRAM`.** 4 GiB is wrong; `CAPABILITIES.md` §2
  already flags it as the origin of a bad number.

---

## 5.6 MEASURED VERDICT (G-4 closed) — the GPU LOSES on this box

Run 2026-10-09 with `tools/accelerator_bench.py`. One model
(`gemma-4-E2B-it-IQ4_XS/model.gguf`), one prompt, the same 128-token cap, three
runs per backend, the figure taken as the **median**. The sidecar itself ran on
**py315t** in both cases, so the client interpreter was held constant and only the
backend changed.

| Backend | Device as reported by the backend | prefill tok/s | decode tok/s | wall (s) |
|---|---|---|---|---|
| `llamacpp-vulkan` (Arc) | `Vulkan0: Intel(R) Arc(TM) 140T GPU (8GB) (8972 MiB, 8267 MiB free)` | **22.84** | **21.05** | 6.84 |
| `llamacpp-cpu` (baseline) | `(none)` — the CPU build enumerates no device, correctly | **58.01** | **27.56** | 4.72 |

**prefill: CPU 2.54× faster. decode: CPU 1.31× faster.**

This is the opposite of the naive expectation, and it is exactly why §5.4 is a gate
and not a formality. The mechanism is not mysterious: the Arc 140T is an
**integrated** part drawing on the same 8 GiB aperture as the host, so a decode
step that is memory-bandwidth bound gains nothing from 28 fewer effective SMs while
still competing with the CPU for the same memory bus. The gap should narrow as the
model grows (the CPU's advantage is cache, which a larger model overflows), so this
verdict is **model-size conditional** — re-measure before quoting it for a 7B model.

Variance, recorded rather than hidden: first-run prefill was 44.62 (GPU) and 150.55
(CPU) against steady-state medians of 22.84 and 58.01 — both first runs include
load/warm-up. Medians are used because a single run would have produced a **wrong**
answer on this very data.

**Consequences for the plan:**

1. G-1's priority order is kept **for capability, not for speed.** The sidecar remains
   the right shape because it makes the accelerator reachable at all — but nobody
   should reach for it expecting a speedup on a small model.
2. Any future "use the GPU for speed" claim in this repo must cite a run in
   `state/accelerator_bench.jsonl`, or it does not exist.
3. On this hardware the CPU path is not a fallback; it is the **fast path** for small
   models. The 16 threads and the free-threaded interpreter are the real asset, which
   reorders the intuition behind §0.

Two defects in the harness were found by running it and are fixed: it printed
`device(s) UNREPORTED` because llama.cpp echoes no device in the completion body (it
now falls back to the device `/health` bound, never to the one requested), and its
free-RAM probe returned an empty string that rendered as "GiB RAM free" — a
machine-readable field reporting nothing while looking filled in.

## 7. T-5 — one shared evolution-log parser (2026-10-09)

Four tools had each grown their own regexes for `logs/evolution_cycle.log`; five
literals were byte-identical copies. They now come from one module,
`tools/evolution_log.py`, which also supplies `iter_lines()` in place of four copies
of the same `open(..., errors="replace")` loop.

Migrated: `tools/evolution_progress.py`, `tools/fitness_arm_liveness.py`,
`tools/render_ouroboros.py`, `tools/process_benchmark.py` — 23 pattern literals → 17
definitions, and `import re` dropped from the three that no longer need it.

**Two families are kept apart on purpose.** The analysts anchor with `^(\S+)` and
capture the subject as group 1; the renderer scans for substrings and captures no
subject, so its group numbering sits one field later. Folding them together would
renumber capture groups and hand every consumer the wrong field. `_SUB` marks the
substring family.

Equivalence, and why the first check was not enough:

- Comparing both families over the real log agreed on all 15 matching lines — but the
  log is only 29 lines, so 652 of 667 comparisons were vacuous. A weak oracle, and it
  was reported as weak rather than as proof.
- The decisive check: every shared `.pattern` is **byte-identical** to the literal it
  replaced (17/17). That is equivalence for all inputs, not just this log.
- End-to-end: 20/20 `loop_integrity` and 7/7 `fitness_arms` analysis fields identical
  to the pre-migration output. The only differing keys are `generated_at` plus the
  run-history pair `previous_verdict`/`reoriented`, shown to be state carried between
  runs by running the tool twice — not assumed.
- `dashboard/ouroboros.html` differs only because it embeds `time.strftime` (line 1024).
- Producer cross-check: `scripts/evolution_cycle.py` still emits this vocabulary.
- Re-check any time with `python tools/evolution_log.py` (exit 0 = patterns agree).

## 8. Suite triage — 6 failures, 4 classes (3.15t, exit 1)

`state/py315t_suite.log`: **6 failed, 3991 passed, 52 skipped** in 19m52s. None is
attributable to this session, which touched neither `src/` nor `tests/`.

1. **A dependency error message that is false — 3 failures** (`test_sb3_agent.py` ×2,
   `test_training_orchestrator.py`): `ImportError: gymnasium is required for
   environment creation`. gymnasium 1.4.0 **is** installed in py315t and imports
   cleanly, and `HAS_GYM` is `True` on a fresh `from CORE.sb3_agent import`. The guard
   at `sb3_agent.py:849` catches bare `ImportError` and reports "missing dependency"
   for *any* import failure. The armed mechanism is a self-shadowing circular import:
   `src/CORE/logging.py:24` reads `logging.DEBUG`, and once `src/CORE` is on
   `sys.path` (which `tests/test_curative_pool.py:12` does) `import logging` resolves
   to that very file → `AttributeError: partially initialized module 'logging'`.
   **Not a wheel gap**, despite the earlier read of §3.
2. **Legitimate baseline invalidation — 1 failure** (`test_anti_pattern_gate.py`): live
   counts exceed the committed baseline (`import_inside_function` 965 vs 954,
   `except_return_default` 276 vs 275, `silent_except_pass` 811 vs 800) because six
   `src/` files changed today. The test names its own remedy (`--baseline`), but
   re-baselining would silently accept 11 new `silent_except_pass` and 11 new
   `import_inside_function`, so it was **not** done: updating an expectation to turn a
   gate green is not a fix.
3. **Load-sensitive timing — 1 failure** (`test_cd5_docker_benchmark`): carries
   `@pytest.mark.slow` and the note "run in the quiet solo pass, not under full-suite
   load" — and ran under full-suite load.
4. **Graph invariant — 1 failure**
   (`test_graph_multigraph_invariants.py::test_no_self_loops`): 77 self-loop edges
   (`X -> X`, relation `calls`, `_origin: ast`) while every committed
   `graphify-out/*/graph.json` holds 0 — so the test builds a fresh graph rather than
   reading those artifacts.

## 9. SOTA duplicates — 18 pairs judged, non-destructively (2026-10-09)

18 episode codes were each carried by two live `sota-steal` records under two
different slugified topic keys. Every pair was confirmed to be the **same paper by
identical arXiv id**, 18/18 — not by title similarity, which is misleading here
("EP11 zero-memory-optimization" vs "EP11 zero-redundancy-elimination" read as
different papers and are not):

EP11 1910.02054 · EP14 2001.04451 · EP34 2201.11903 · EP63 2305.13048 ·
EP110 2601.12307 · EP141 2602.06855 · EP150 2601.12538 · EP151 2601.13060 ·
EP155 2602.03279 · EP172 2603.19461 · EP206 2604.27820 · EP226 2605.07721 ·
EP236 2605.13821 · EP253 2605.25746 · EP262 2605.31365 · EP318 2606.24855 ·
EP354 2607.07321 · EP383 2607.18366

Verdict is `not_conflict`, not `supersedes` — neither record succeeds the other; they
are two ingestions of one paper. Verified in-store: 18 new `memory_relations` rows,
`judgment_status=judged`, `marked_by_actor=engram`, taking `not_conflict` to 61 rows.
No observation was deleted, edited or merged. Plan: `state/sota_dedup_plan.json`.

**`tools/sota_dedup_check.py` could not have found these.** It reads the batch
*batch01–04 spec files*, not the store, prints `VERDICT: CLEAN — 33 distinct, zero
duplicates of held bank` and exits 0 — a clean bill of health that says nothing about
the 172 `sota-steal` records actually in Engram. Treat its PASS as scoped to the file
corpus only; the store needs the query used here.

---

## 10. Technique-layer adoption — the outlier defect, measured (2026-10-09)

Basis: `SOTA_OUTLIER_DIAGNOSIS.md` (why), `SOTA_ROW_RESCORE.md` (48 rows
reassigned), `SWALLOW_INVENTORY.md` (swallow census).

Measured shape: 18 new files / 6,322 lines carry 181 techniques; production call
sites into that layer = **5** (4 added 2026-10-09), and the only other consumers are
6 exercise scripts. **48 of the 141 map rows point at the new layer instead of a
host.** The plan had no refactor task, which is why no host was ever edited.

| # | Task | Why it exists | Est. |
|---|---|---|---|
| **T-13** | Host remediation programme: work `SOTA_ROW_RESCORE.md` row by row, moving each delta into the host it names | the blueprint asks for adoption ("extends the engram gate", "extends clusters"), not adjacency | L |
| **T-14** | Add a plan task type for host refactors, so a technique cannot be marked satisfied without an edit to its host | mechanism 2 of the diagnosis: no refactor task existed in T-1..T-12 | S |
| **T-15** | Replace the adoption instrument: count production call sites per technique and score exercise-only engagement as **zero** | mechanism 3: `exercise_technique_runtime.py` reports `engaged=181` while production callers were 1 | M |
| **T-16** | Swallow remediation: ~~2,561 certified-silent handlers~~ **DONE 2026-10-10 — premise was stale.** Re-measured on today's tree the inventory reports **26** rows, not 2,994: commit `30836145` (2026-10-09) had already swept it, and `SWALLOW_INVENTORY.json` was a pre-refactor artifact whose line numbers had drifted. 23 of the 26 were repaired in an 8-worker fan-out; **3 remain by design** (the recorder's own handler + 2 optional-import guards) — see the SUPERSEDED banner in `SWALLOW_INVENTORY.md` | an unrecorded swallow is indistinguishable from success | L |

Do NOT: build one new module per technique to close these rows. That is the defect
T-13 exists to remove.
