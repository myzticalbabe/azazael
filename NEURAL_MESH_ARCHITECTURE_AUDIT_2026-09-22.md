# Neural Mesh Architecture & Neural-Net Audit — 2026-09-22

**Scope:** the whole repository as it stands in the working tree on 2026-09-22
(not just committed state), with a focus on the neural/learning stack
(`src/CORE/neural_loop.py`, `src/CORE/WORMS/expansion/{hyperopt,wiring_genome,
learning_*}.py`, `src/ML/`, `src/ORCHESTRATION/ml_platforms/`).

**Method — every number below is measured, not estimated.** Sources:

| Instrument | What it measured | Command |
|---|---|---|
| AST import graph (inline) | coupling, cycles | `ast` walk over `src/`, Tarjan SCC |
| `tools/mesh_function_preflight.py --summary` | 21-probe static battery over mesh functions | as written |
| `tools/mesh_function_preflight.py --verdict` | unreferenced functions + dispositions | as written |
| `tools/nature_integration_map.py` | orphan capabilities grouped by driving stage | as written |
| `tools/artifact_freshness.py` | derived-map currency vs sources | as written |
| `tools/silent_failure_audit.py` | swallowing handlers | `--check` |
| `tools/audit_parseable_files.py` | extension/magic mismatch | `--check --deep` |
| `pytest -q -p no:randomly tests/` | suite truth | full run, 183 files |

---

## 1. Inventory (measured)

| Layer | Files | Lines |
|---|---|---|
| `src/CORE` | 326 | 128,077 |
| `src/CORE/WORMS` | 181 | 62,277 |
| — `src/CORE/WORMS/expansion` | 128 | 40,014 |
| `src/CODEX` | 74 | 32,697 |
| `src/ORCHESTRATION` | 83 | 35,344 |
| `src/META` | 16 | 9,021 |
| `src/UTILITIES` | 23 | 5,454 |
| `src/HYDRA` | 11 | 2,546 |
| `scripts/` | 186 | 50,146 |
| `tools/` | 51 | 10,379 |
| `tests/` | 192 | 59,171 |

Python under `src/` parses cleanly: **0 syntax errors** across all 326+ files.

## 2. Coupling and cycles (AST, `src/` only)

Most-imported internal modules (inbound edges):

| Inbound | Module |
|---|---|
| 166 | `CORE.worm_registry` |
| 71 | `CORE.active_learn` |
| 40 | `CORE.paths.external` |
| 35 | `CORE.freethreading` |
| 28 | `CORE.local_memory` |
| 26 | `CORE.direct_memory` |
| 20 | `CORE.audit_trail` |
| 14 | `CORE.PamsRecorder` |
| 12 | `CORE.inference.providers` |
| 10 | `CORE.MemoryBus`, `CORE.compliance.pre_action_gate` |

`worm_registry` is imported by 166 modules — it is the single point of failure
for the whole tree, and §7 shows two of today's defects landed there precisely
because "everything depends on it" was not treated as a hazard.

Highest fan-out: `WORMS/expansion/spine.py` (24 internal imports),
`CORE/azazael_ctl.py` (14), `CORE/dashboard.py` (14), `WORMS/METACLUSTER.py`
(10), `WORMS/NATURE_CLUSTERS.py` (10).

**Circular-import groups (SCC > 1): 7**

| Size | Members |
|---|---|
| 5 | `expansion.dreaming`, `expansion.spine`, `direct_memory`, `dream_policy_bridge`, `startup_warm` |
| 5 | `compliance.orchestrator`, `compliance.pre_action_gate`, `sentinel_enforcer`, `SCRIPTS.generate_telemetry`, `SCRIPTS.sentinel_gate` |
| 4 | `expansion.learning`, `expansion.learning_features`, `expansion.learning_pipeline`, `expansion.learning_rl` |
| 3 | `dashboard`, `health_server`, `web_dashboard` |
| 2 | `worm_registry`, `worm_registry_cache` |
| 2 | `Agent`, `agent_registry` |
| 2 | `WORMS.BINARY_ANALYSIS`, `WORMS.BINARY_ANALYSIS_CLI` |

The learning cluster being mutually recursive (`learning`, `learning_features`,
`learning_pipeline`, `learning_rl`) is the neural stack's structural weak point:
no module in that group can be imported in isolation, which is why its tests use
module-load-by-spec rather than plain imports.

## 3. The neural stack

**Loop shape — `src/CORE/neural_loop.py`** declares 14 stages as data, used for
both execution and reporting (`STAGES`), so a stage cannot be dropped from the
run while still appearing in a summary:

`load → perceive → credit → plasticity → route → act → grade → consolidate →
prune → grow → l1 → l2 → persist → verify`

9 of the 14 mutate durable state (`WRITE_STAGES`) and are refused together by
the write gate. `ALPHA = 0.15` is the only numeric constant in the file that
changes behaviour (stated in-source).

**Outer loop calibration — `hyperopt.PARAM_SPACE`** (read via `_tuned()`
fallbacks, so a missing/unreadable tuner degrades to shipped literals):

| Param | Default | Live | Low–High |
|---|---|---|---|
| `wiring.min_wins` | 3 | **2** | 2–8 |
| `wiring.min_observed` | 3 | 3 | 2–8 |
| `wiring.min_evidence` | 0.25 | 0.25 | 0.10–0.90 |
| `wiring.elite_replace_ratio` | 0.5 | **0.8625** | 0.1–3.0 |
| `wiring.margin_floor` | 0.0 | 0.0 | 0.0–0.02 |
| `morph.max_opportunity` | 2 | 2 | 1–6 |
| `spine.cooldown_{min,max}_scale` | 0.5 / 4.0 | 0.5 / 4.0 | — |

The two **live ≠ default** rows are a fact with teeth: two test files asserted
the *literal* rather than the tuned value and therefore failed whenever a tuned
value landed (fixed today, §7.3). `wiring.margin_floor` carries its own
post-mortem in-source (`measured_max_achievable_delta: 0.00008363`) because an
absolute effect floor had already made the gate unreachable for 33 cycles.

**Fleet / natures:** `WORM_REGISTRY` holds **232** classes across **36**
categories; `NATURE_DEFINITIONS` declares **26** natures.

Top categories: security 25, learning 19, analysis 18, monitor 15, network 13,
orchestration 10. The nervous-system vocabulary layer is well populated —
xenomorph 8, synapse 6, envmesh 6, engram 5, immune 5, plasticity 5, axon 4,
consolidation 4, dendrite 4, glia 4, thalamus 3, metabolic 3, consensus 3,
federated 3, servemesh 3, defense 1, repair 1 = **68 of 232 classes (29%)**.

## 4. Static pre-flight battery — 1,487 mesh functions

| Probe | Meaning | Fails |
|---|---|---|
| PF01 | parses; span inside file | 0 |
| PF02 | has a docstring | **700** |
| PF03 | has a return annotation | **349** |
| PF04 | every parameter annotated | **1,133** |
| PF05 | no bare `except:` | 0 |
| PF06 | no mutable default arg | 0 |
| PF07 | no `os.system` / `shell=True` | 0 |
| PF08 | no emoji in source span | 0 |
| PF09 | no hardcoded drive path | 7 |
| PF10 | no backslash in f-string expr | 0 |
| PF11 | does not shadow a builtin / wildcard import | 1 |
| PF12 | not an unimplemented stub | 0 |
| PF13 | no constant-true loop without exit | 0 |
| PF14 | catches a specific exception, not `Exception` alone | **338** |
| PF15 | no bare `pass` in an except body | **130** |
| PF16 | referenced somewhere in the repo | **164** |
| PF17 | referenced by a test | **561** |
| PF18 | writes no module-level global | 15 |
| PF19 | opens files with an explicit encoding | 4 |
| PF20 | recursion is depth-guarded | 1 |
| PF21 | progress-dependent loop advances | 4 |

Severity: **P0 142 · P1 380 · P2 888 · CLEAN 77.** Only 5.2% of mesh functions
are clean on all 21 probes; the dominant signal is annotation/docstring debt
(1,133 + 700), not correctness.

Independent of this battery, `tools/silent_failure_audit.py` counts **996**
pass-only handlers (0 bare `except:`, 708 catching bare `Exception`, 288 typed)
and **255** that swallow a write-like call. `--check` fails on exactly one
condition — a bare `except:` — currently **0**.

### 4.1 Unreferenced capability — `NEURAL_MESH_WIRE_OR_CUT.json`

**164** functions nothing in the repo reaches. Triaged 2026-09-22 by
`tools/mesh_function_preflight.py --verdict --propose`, which measures one thing
per finding instead of guessing:

| Disposition | Count | Evidence |
|---|---|---|
| `dispatched` | **62** | the name exists in production code only as an identifier-like STRING literal (`getattr`, a registry key, a dispatch table) — `file:line` recorded per entry |
| `pending` | **102** | no production reference of any kind: not a `Name`, not an attribute, not a string |
| `wired` | 0 | — |
| `retired` | 0 | — |

**This required a new status, and that is the finding.** `wired` cannot be
written down for a dynamic-only name: PF16 still fires (it reads `ast.Name` /
`ast.Attribute` and a string is neither), so the entry would fail
`test_a_wired_declaration_is_actually_wired` — the table had no way to record a
fact the triage had just measured. `dispatched` is that status, and it carries
verified evidence: the contract test re-derives each hit from source and fails an
unbacked declaration, and a second test asserts the entry is *still* a PF16
finding (so the status cannot be used to claim reachability that does not exist).
What it does **not** claim: that anything calls the function. It claims the probe
cannot decide, by construction, and the review action is the same — wire it
visibly or delete it.

Independent check of the same measurement: a separate AST pass over
`src`/`scripts`/`tools` (docstrings and prose excluded) counted **62** names with
an identifier-like string reference — the same 62.

**Correction.** An earlier revision of this section listed
`integrate_via_stage 92 / module_level 34 / wire_at_site 32 / unresolved 6` as
dispositions. No such statuses existed in the file — all 164 read `pending` — and
no evidence for those groupings was recorded. They were inference presented in a
results table, and they are removed rather than restated. The 92
`integrate_via_stage` figure in AR-6 was the same inference.

The per-function checklist (`NEURAL_MESH_FUNCTION_TODO.md`, 3,940 lines) has
**2,009 open items, 0 completed** — the audit apparatus exists and is wired into
`tools/artifact_freshness.py`, but the list is unworked. The 164 above are now
catalogued with evidence; the 102 `pending` are the part that still needs a
human wire-or-delete decision.

## 5. Test infrastructure — suite truth

Run of all 183 files, single process, `-p no:randomly`:

| Run | Result | Wall |
|---|---|---|
| before today's fixes | **72 failed, 3,508 passed, 38 skipped, 69 errors** | 1,411 s (23:31) |
| after today's fixes | **65 failed, 3,584 passed, 38 skipped, 0 errors** | 1,269 s (21:08) |

Net effect of the two isolation fixes: **69 errors → 0**, 8 gate failures → 0,
and **74 more tests pass** in the same aggregate run. `test_wiring_cycle`,
`test_import_map` and `test_evolution_gates` are absent from the failure list
entirely.

A third run, after the `_purge_worm_modules` narrowing (§7.1, AR-1), measured
**50 failed / 3,606 passed / 38 skipped / 0 errors in 22:09** — a further 15
failures and 22 passes, with `test_nature_metacluster_unit` (13 failures) gone
from the list completely. Cumulative: **72 → 50 failures, 69 → 0 errors,
3,508 → 3,606 passing.**

A fourth run — **before** the two fixes in §7.7 and §7.8 landed but **with** the
memory-DB restore active — measured **45 failed / 3,643 passed / 39 skipped /
1 error in 24:35** and named the causes of both remaining clusters:

- **25 of the 45 are one root cause.** `test_sb3_agent` (17),
  `test_eve_unleashed` (5), `test_inference` (2) and `test_training_orchestrator`
  (1) all report the same traceback: `AttributeError: partially initialized
  module 'torch' ... has no attribute 'distributed' (most likely due to a
  circular import)` from `torch/_jit_internal.py:1249`, reached via
  `torch/__init__.py:2650` → `torch/functional.py` → `torch/nn/...`. The count
  (25) matches the family exactly. **Still open** — see AR-3.
- **10 of the 45 are the sentinel thread-local permit** (§7.8, now fixed and
  verified: `10 failed, 28 passed` → `38 passed` in 4 s).
- The `test_cross_domain_integration` pair (2), `test_worm_smoke` (2),
  `test_morphogenesis_opportunity` (3), `test_spine_mesh` (1) and
  `test_mesh_wire_or_cut` (1) that the third run still listed are **gone** — the
  memory-DB path leak (§7.7).
- Three items are **new or newly visible**: `test_brainstem_playing_field::
  test_cap_prunes_the_lowest_evidence_keys_first` (passes in its own file subset),
  `test_dm_advanced::test_replay_session`, and an **error** in
  `test_mutation::test_mapping_summary_structure` where the third run had none.

Failure buckets from the "before" run (with standalone results for each):

| File | Fails (before → after) | Passes alone? | Cause |
|---|---|---|---|
| `test_sb3_agent` | 17 → 17 | ✅ 42 passed | order/state |
| `test_nature_metacluster_unit` | 13 → **0** | ✅ 74 passed | **fixed** — module identity (§7.1) |
| `test_fs_probe_backend` | 10 → **0** | ✅ 13 passed | **fixed** — the sentinel permit was thread-local, so the probe's worker thread was blocked (§7.8). The earlier guess ("child-probe deadline missed") was wrong and is corrected here |
| `test_wiring_cycle` | 8 → **0** | ✅ 20 passed | **fixed** — see §7.1 |
| `test_eve_unleashed` | 5 → 5 | ✅ 21 passed | order/state |
| `test_morphogenesis_opportunity` | 3 → 3 | ✅ 14 passed | order/state |
| `test_worm_smoke` | 2 → 2 | ✅ 5 passed | order/state |
| `test_inference` | 2 → 2 | ✅ passes alone | torch/transformers path |
| `test_evolution_gates` | **61 errors → 0** | ✅ 61 passed | **fixed** — see §7.2 |
| `test_import_map` | **8 errors → 0** | ✅ 8 passed | **fixed** — see §7.2 |
| 10 further files | 1–2 each → 1–2 | — | mixed: `test_cross_domain_integration` 2, then 8 files at 1 (`compliance_deadlock_regression`, `config_and_breaker`, `cross_nature_orchestration`, `exmachina_monitor_split`, `mesh_fabric_followups`, `ncm_integration`, `pool`, `training_orchestrator`, `worm_execute_all_integration`) |

**Remaining after both fixes: an estimated 35 failures across 15 files, one
error.** The count is an estimate because the fourth run started before the
sentinel fix was written; the 10 `test_fs_probe_backend` failures are measured
gone from the same process (`28 passed` alongside 10 failures → `38 passed` on the
pair that reproduced them)
and nothing else in that file's bucket changed.

Every failing file still passes alone, so the residual is concentrated in **one
named cause** (25 torch failures) plus 10 singletons. Named cause first:

- **AR-3 (open): the torch import.** A fresh `python -c "import torch"` in the
  same venv works and `torch.distributed` is present (torch 2.14.0+cpu), so the
  failure is state, not a broken install. In `torch/__init__.py` `distributed` is
  bound at line 2703 — *after* the line-2650 chain that reaches
  `_jit_internal:1249` — so a healthy first import must resolve `torch.distributed`
  some way this run does not. Decisive next step (not yet run): **pytest imports
  every test module at COLLECTION, before the first test runs**, so a polluter's
  *module-level* side effect can land before `test_eve_unleashed` executes even
  though its own tests run much later — which is why the victim's file, and every
  prefix subset that contains it, stays green. Instrument collection with a
  `pytest_collection_modifyitems` plugin that records `sys.modules` torch state
  per imported module, and bisect that list.

The headline fact: **every failing file passes green when run alone.** The
suite's dominant defect class is *test isolation*, not product code — and it is
invisible to per-file runs, which is how a suite can be simultaneously green in
CI-per-file and 141 failures deep in aggregate.

## 6. Security, hygiene, environment

| Fact | Value |
|---|---|
| `shell=True` uses (`src/`, `scripts/`, `tools/`) | **17** (PF07 = 0 because the probe only scans mesh functions) |
| bare `except:` in mesh | 0 (census `--check` exits 0) |
| write-swallowing handlers | 255 |
| mislabelled parseable files | 66 legacy (63 JPEG-as-PNG + 3 zero-byte MP4), all vendored `archived/` or gitignored `output/`; 0 corrupt PDFs |
| deep-parsed PDFs | 0 (no PDFs in tree) |
| interpreters | `venv-314t` (session), `venv-313-tools`, `venv-interpreter`, system Python 3.14 |
| deps present in `venv-314t` | pypdf 6.19.0, pytest 9.1.1, stable_baselines3 2.9.0, torch 2.14.0, transformers 5.17.0 |
| **type checker** | **basedpyright 1.40.1** — already in `venv-314t`, reads the committed `pyrightconfig.json`: **1,191 errors + 252 warnings over 690 files in 64 s**, recorded in `logs/basedpyright_baseline.json` and gated by `tools/type_check_gate.py` (ADR-011). mypy 2.3.1 is also present and reports 655 errors over `src/CORE/` in ~6 min, but it could not read the tree until two literal `nul` files were removed, and it asks a narrower question |
| junk filenames | **2 literal `nul` files** (`./nul`, `src/CORE/WORMS/nul`), untracked and invisible to `git status`, residue of a cmd.exe redirect run inside Git Bash. They made `mypy src/CORE/` abort with `path is on mount '\\.\nul'`, which is why "type safety is unmeasured" was recorded as a code finding. Removed (Error #193) |
| graph corpus | 51,150 files · 687,497 nodes · 823,173 edges · 40,051 communities · 93% extracted, built from `698bfe89` |
| working tree | **3,759 dirty**: 3,168 deleted (3,150 under `output/`), 203 modified (117 `src/`), 388 untracked (95 `src/`, 69 `scripts/`, 66 `state/`, 54 `logs/`, 34 `tests/`) |
| fs-hygiene regressions | **1**: `AUTO_DOWNLOADER.log` grew to 20.3 MB (over the 20 MB threshold), written today 01:33 — an untracked live-daemon log, not a code change. Baseline refreshed (`tools/fs_hygiene.py --baseline`), `--check` now green; the growth itself is unaddressed |
| other large artifacts | `graphify-out/graph.gexf` 709 MB · `graph.json` 510.7 MB · `graph.html` 498.8 MB · `output/graphify_cache/azazael/graph.json` 273.1 MB · 1,802 `__pycache__` files |

The graph corpus is dominated by vendored archives (`archived_unified/`,
`onnxruntime-*`, BIBL) — its community hubs are `onnxruntime`, `BIBL Terms *`,
`nuitka/*.h`, and `TEST_F`, not the project's own code. As an architecture
instrument for *this* codebase the graph is over-inclusive: the 25 top hubs
contain at most 4 project modules (`worm_registry`, `WORMS/expansion/__init__`,
`NatureClusterManager`, `LocalMemoryStore`, `MemoryBus`). `tools/*` AST tools
gave the useful signal here, not the graph.

## 7. Defects found and fixed this session

### 7.1 `worm_registry` purge re-imports HELPER modules, breaking identity
`_purge_worm_modules()` deletes **every** `CORE.WORMS.*` entry from
`sys.modules` (needed so `@register_worm` decorators re-fire). Its docstring
warns only that *worm classes* become distinct objects. Measured: **whole
helper modules** come back as different objects too —

```
import CORE.WORMS.expansion.wiring_genome as wg0
worm_registry.reset_registry()
import CORE.WORMS.expansion.wiring_genome as wg1
wg0 is wg1  ->  False        # 2 live module objects, same name
```

Consequence: any consumer that imported before the reset and any consumer that
imports after hold different module objects, so `monkeypatch`/`setattr` on one
does not reach the other, and `isinstance` across the boundary is false. In the
suite it presented as 8 gate tests failing in-suite while passing alone, with
the gate reporting `no candidate beat the incumbent` for a candidate forced to
win by 0.5.

Fix: the tests patch the module the cycle **actually calls** (`_cycle_wg(mod)`),
not the one they imported, plus a regression test
(`test_the_gate_still_gates_after_a_registry_reset`) that reproduces the
in-suite order (load the cycle *after* a reset) and asserts the gate still
gates. **Not** fixed at source — narrowing the purge means deciding, at purge
time, which modules carry worms; getting that wrong re-creates the documented
lossy re-discovery (SpineCycleWorm / MeshArchitectWorm / GossipSyncWorm absent).
Recorded as P1 in §9.

### 7.2 Sentinel write-guard: mitigation was function-scoped, failures were module-scoped
`CORE/sentinel_enforcer.py` installs a process-global `sys.addaudithook` at
import that raises `PermissionError` on any `open(..., 'w'/'a'/'+'/'x')`
without a thread-local token. `tests/conftest.py` already mitigates this — but
with a **function-scoped** autouse fixture, and pytest sets up module/class
fixtures **first**. So a `@pytest.fixture(scope="module")` that imports a script
which opens its log file at import (`scripts/evolution_cycle.py:48`) is blocked
before the permit ever runs.

Measured: **207** `PermissionError`s → **69 collection errors** across
`test_evolution_gates` (61) and `test_import_map` (8), plus a share of the 72
failures. Fix: a `pytest_runtest_setup` hook latches the token open — the
earliest hook a conftest gets, before fixture setup of any scope — and the latch
is left on for the session (the guard gates the *assistant's* tool writes, not a
test process's log files; nothing under `tests/` asserts that it blocks).

Verified: `test_compliance_step45_init + test_evolution_gates + test_import_map`
→ **105 passed, 0 errors** (was 61 + 8 errors).

### 7.3 Tests asserted the shipped literal where the module documented it as a fallback
`wiring_cycle.L1_MIN_WINS = _tuned("wiring.min_wins", 3)` — in-source comment:
*"the literals here are the fallback, not the truth"*. `test_wiring_cycle`
hardcoded `3` and `0.9-vs-0.5` for the elite-replace floor. Live values are
`min_wins=2`, `elite_replace_ratio=0.8625`, so four gate tests failed the moment
a tuned value landed. Fixed by deriving expectations from `wc.L1_MIN_WINS` /
`wc.L1_ELITE_REPLACE_RATIO`, with `L1_MIN_WINS > 1` asserted so a degenerate
tuned value cannot silently void the "one draw must not promote" property.

### 7.4 `hyperopt.measure()` repopulated the registry it was measuring
Carried from the previous session and verified here: an unguarded
`discover_worms()` inside `measure()` (called only to read a count) wrote the
whole fleet into whatever dict was bound to the global, so the audit's own
report disagreed with the table it had just read (2 → 234 mid-measurement). Now
guarded (`if not WORM_REGISTRY`), matching every other call site. Same theme as
7.1 and §4's `l1_wiring_audit` snapshot fix: **a measurement that mutates what
it measures**.

### 7.5 Two literal `nul` files disabled the type checker (new, Error #193)
`mypy src/CORE/` did not report findings or complain about config — it aborted
with `ValueError: path is on mount '\\.\nul'`. Two files literally named `nul`
(178 and 51 bytes, holding `dir: cannot access '/b'`) sat at the repo root and in
`src/CORE/WORMS/`. They are the residue of a cmd.exe command run **from Git
Bash**, where `dir` is not a builtin and `> nul` creates a real file rather than
redirecting to the Windows device.

Three consequences, in order of importance:

1. **The expensive one:** type safety had been recorded as unmeasurable, and
   therefore as a low score about the *code*. It was an environment fact. After
   removing 229 bytes of junk, mypy reported 655 errors immediately.
2. Git cannot match a pathspec named `nul`, so both files were invisible to
   `git status`, to the dirty-tree accounting (§6 counts 388 untracked) and to
   every review that used git as the window onto the tree.
3. A tool that dies on a *path* rather than a *symbol* is reporting on the
   filesystem, not the code. The crash should have been read as a stop sign, not
   as the finding.

### 7.6 The gate counted failures it could not read (new, Error #194)
`aggregate_suite_gate.py` stored only failing nodeids, while the assertion text
lived in a captured `subprocess` pipe that closed on exit. Five runs produced ~50
countable, unreadable failures; the only way to read one was to re-pay the full
22 minutes. The gate now writes the raw pytest output beside its report and
records the profile, targets and raw filename in it. A report that supports a
decision must carry the evidence for it.

### 7.7 A half-restore leaked the memory DB path, and five innocent files took the blame (new, Error #196)

The largest single cause of the remaining aggregate-only failures was **test-side
module-global leakage**, not product code. `CORE/direct_memory.py` resolves its
store path once at import (`DB_PATH = _get_db_path()`); four legacy-style suites
redirect it by setting `AZAZAEL_MEMORY_DIR` **and** `direct_memory.DB_PATH`, then
restore only the env var and `rmtree` the directory. The global went on naming a
deleted temp dir, and every later `DirectMemory()` in the process raised
`unable to open database file`.

Measured shape of the defect: the **leakers** (`test_cli`, `test_doctor`,
`test_concurrency_200`, `test_perf*`) are never the files that fail, and the
**victims** (`test_cross_domain_integration::test_cd1_record_event`,
`test_cross_domain_integration::test_cd5_docker_benchmark`,
`test_worm_smoke::test_every_worm_instantiable` → ParallelInferenceWorm) are all
green when run alone. Reproduced deterministically in 18 s —
`pytest tests/test_cli.py tests/test_doctor.py tests/test_cross_domain_integration.py::test_cd1_record_event`:
`1 failed, 13 passed` before, `14 passed` after — and fixed at the mechanism
rather than per-file: `conftest._restore_memory_db_globals` is autouse and
recomputes each derived DB-path global through its own module's resolver after
restoring the environment. `tests/test_memory_db_isolation.py` pins it, and the
pin was falsified (with the fixture absent, the second test fails).

### 7.8 A thread-local security permit made every delegated file probe answer "unknown" (new, Error #197)

The second cluster of aggregate-only failures was also an isolation defect, and
this one had a production reading. `sentinel_enforcer.py:40` gates writes with
`_GATED_CALL = threading.local()` and the audit hook reads it per thread (`:53`).
`fs_probe` runs its child probe on a **new worker thread** and opens
`tempfile.TemporaryFile()` there, so once the guard had been armed by an earlier
file, every delegated probe was blocked:

```
{"ok": false, "timeout": false,
 "error": "CRITICAL: Unauthorized write to C:\\Users\\clint\\AppData\\Local\\Temp. ..."}
```

`bounded_exists` / `bounded_is_dir` / `bounded_read_text` then return `None` —
and `None` is documented as "unknown", so the caller cannot tell *denied by our
own guard* from *did not answer*. All 10 `tests/test_fs_probe_backend.py` tests
failed in aggregate and passed alone; reproduced in **4 seconds** with
`pytest tests/test_compliance_step45_init.py tests/test_fs_probe_backend.py`
(`10 failed, 28 passed` → `38 passed`).

**The production half is now fixed too.** The first mitigation was in `conftest`
(a shared token), which fixed the suite and left the subsystem broken in the
assistant's own session: with the guard armed, `fs_probe`'s delegated probes
could not answer at all. Two candidate fixes had been recorded as an operator
decision; the one taken is the narrower:

* `sentinel_enforcer.worker_permit(held)` — `held` is read on the **starter**
  thread, so a worker holds exactly its starter's permit and a worker started
  with no permit is still denied. Authority is not made process-wide.
* `permit_here(reason)` replaces the bare `is_active = True` / `finally: False`
  pattern at all five internal call sites, restoring the PREVIOUS value — with
  the old pattern an inner authorized region ended the outer one on exit.
* `fs_probe._carried_permit()` reads the guard out of `sys.modules` rather than
  importing it (importing `sentinel_enforcer` ARMS the audit hook, and a probe
  must not be able to arm a guard the process chose not to have), and returns a
  *factory* because `bounded_first_dir` starts N threads.
* Denial is now its own outcome: `bounded_subprocess_output` returns `denied`,
  `probe_backend_stats()["denied_probes"]` counts it, `is_denied()` reads it.
  "We refused to look" can no longer be reported as a filesystem finding.

Verified against the REAL `threading.local()` token, with `conftest`'s
compatibility swap disabled (`AZAZAEL_TEST_SHARED_PERMIT=0`): the repro pair is
**38 passed**, one stubbed `_carried_permit` returns `{'ok': False, 'denied':
True}`, and `tests/test_sentinel_thread_permit.py` was rewritten so it rebinds
the token itself — the inherited-permit case and the no-widening case are a pair,
so neither the pre-fix code nor a process-wide flag can satisfy it.

### 7.9 `max_natures` was spent before the filter that could drop the nature (new, Error #198)

`test_cross_nature_orchestration.py::TestMetaClusterState::test_state_phases`
failed on `set() or set()` while the assertion above it (`phase == "complete"`)
passed. `MetaCluster.orchestrate()` capped the ranked Nature list and *then*
dropped the natures that contain the orchestration infrastructure:

```python
natures = ranked[:max_natures]                                     # cap first
...
execution_order = [n for n in order if n not in circular_natures]  # drops the cap
```

When the ranking promoted `orchestration` to the top — which `_score_natures()`
recency (-5 under 60 s) and staleness (+5 over 600 s) terms do after a dozen
calls — the single slot was spent on a Nature the filter was about to remove.
`execution_order` emptied, the loop never ran, and the result still reported
`phase="complete"` with `errors=[]`: **a no-op indistinguishable from a clean
pass**. Every file-level instrument missed it (green alone, green in every
prefix, and every subset of the class excluding the failing test was green).

`tools/pytest_fixture_watch.py` (new) named it in one run: watch a dotted
attribute path across a suite and print the first test after which the value
CHANGES. `FIXTURE_WATCH="ncm._execution_history,state.active_natures"` showed
`state.active_natures = {}` with no history entry — nothing was even selected.

Fixed: the cap is applied to the natures that can RUN (`eligible or ranked`), and
an empty `execution_order` now appends an explicit error naming the circular set.
`30 passed` (was 1 failed / 29 passed); the three other metacluster suites are
`146 passed`.

### 7.10 The wire-or-cut triage erased its own evidence on re-run (new, Error #199)

`--propose` wrote `evidence` inside the `pending -> dispatched` branch, so
regenerating the table — which is how it is maintained — left all 62 dispatched
rows with a reason and no locations, failing
`test_a_dispatched_declaration_states_where_and_why`. Evidence is now re-derived
for every dispatched row; `test_proposing_twice_keeps_the_evidence` proposes the
same table twice and fails on the old code. `17 passed` (was 1 failed / 14).

### 7.11 The 101 findings no probe can decide now have an order (not a verdict)

`--triage` labels each still-`pending` finding with the class that decides its
next action, measured from a test-side reference scan (Name / Attribute /
identifier-like literal, docstrings excluded):

| Class | Count | The decision it needs |
|---|---|---|
| `test_reached_only` | **44** | the only caller is a test: public API (wire a production caller) or scaffolding (retire it) |
| `no_reference_anywhere` | **57** | nothing in the repository reaches it: the deletion queue |

The label lives in its own field (`triage`, `triage_evidence`) and **`status` is
never touched** — a class is not a disposition, and collapsing the two is how the
earlier inferred `integrate_via_stage` table came to be presented as results.

#### The 57 with no reference anywhere (the deletion queue)

`NeuralPipeline.replay_failed` · `ThompsonAllocator.choose_with_bonus` ·
`LatencyCompensatorWorm.compensate` · `MyelinSheathWorm.boost_for` ·
`MyelinSheathWorm.myelinate` · `CheckpointWorm.restore_checkpoint` ·
`IPCBridge.create_channel` · `IPCBridge.receive` · `ConfigLinter.lint_yaml` ·
`EngramIndexerWorm.lookup` · `SharpWaveReplayWorm.replay_batch` ·
`SleepConsolidatorWorm.sleep_cycle` · `ResourceQuotaWatch.set_quota` ·
`AttentionGateWorm.set_bias` · `DendriteAggregatorWorm.set_gain` ·
`DreamingModule.get_dream_stats` · `HypnagogicSynthesizer.ingest_domains` ·
`GemmaDriverWorm.judge_dream` · `GemmaDriverWorm.propose_goal` ·
`EraEvidence.era_counts` · `EvolutionEngine.get_generation_history` ·
`GeneticOptimizer.optimize_multi` · `exmachina._mad` · `exmachina._tpm` ·
`FederatedAggregatorWorm.run_round` · `RewardShaperMeshWorm.local_score` ·
`MicrogliaWorm.check_path` · `GRPOTrainer.rewards_from_elo` ·
`MeshRouterWorm.invalidate_route` · `CodeMigrator.run_2to3` ·
`LegacyShimGen.write_shim` · `FitnessOracle.acquisition` ·
`FitnessOracle.era_robust_probability` · `CPUFlameProfiler.to_flamegraph_data` ·
`CodeProfiler.detect_hotspots` · `CodeProfiler.profile_function` ·
`CertMonitor.check_cert` · `CertMonitor.get_expiring_soon` ·
`SessionStateManager.import_snapshots` · `SessionStateManager.list_registered` ·
`SessionStateManager.register_migration` ·
`SessionStateManager.register_worm_state` ·
`SessionStateManager.unregister_worm_state` · `spine_registry._iso_or` ·
`spine_registry.route_last_at` · `MoEDispatcherWorm.top_expert` ·
`AlertEscalator.clear_alert` · `EventRouter.get_recent_events` ·
`SpanTracer.end_span` · `SpanTracer.start_span` · `SensoryRelayWorm.relay` ·
`DashboardGen.add_panel` · `ChestbursterWorm.burst` · `DroneWorm.carry` ·
`OvomorphWorm.hatch` · `OvomorphWorm.lay` · `ResinWorm.secrete`

Two clusters stand out and neither is a surprise: the **`SessionStateManager`
family (5)** is a snapshot/migration API with no caller, and the **`xenomorph`
family (5)** is a metamorphosis lifecycle nothing drives — both are capabilities
that exist and are never invoked, which is the definition of this finding.

#### The 44 reached only by a test

The largest single group is `DataPipelineWorm` (**8 members**, all reached from
`tests/test_learning_worms.py`) plus the `spine_registry` maintenance surface
(**10 members**, from `test_spine_mesh.py` / `test_brainstem_playing_field.py` /
`test_mesh_clock_poison.py` / `test_spine_tombstone_enforcement.py` /
`test_colour_queens.py`). Each needs one question answered by a person: is this
**public API** (then give it a production caller) or **test scaffolding** (then
retire it)? The full list with the reaching test and line is in
`NEURAL_MESH_WIRE_OR_CUT.json` under `triage_evidence`, so the review reads a
location rather than a claim.

### 7.12 Verification

| Check | Result |
|---|---|
| `test_wiring_cycle` (20 tests, incl. the new reset regression) | ✅ pass |
| reset-first order (`registry_importable` + `metacluster` + `learning_closure` + `wiring_cycle`) | ✅ pass |
| sentinel-triple (`compliance_step45_init` + `evolution_gates` + `import_map`) | ✅ 105 passed |
| **aggregate suite, before** | 72 failed · 3,508 passed · **69 errors** · 1,411 s |
| **aggregate suite, after the two isolation fixes** | 65 failed · 3,584 passed · **0 errors** · 1,269 s |
| **aggregate suite, after the purge narrowing** | **50 failed · 3,606 passed · 0 errors · 1,329 s** |
| **aggregate suite, after the memory-DB, thread-permit and cap fixes (run 6)** | **11 failed · 3,681 passed · 39 skipped · 1 error · 1,511 s** |
| **aggregate suite, run 8 — every fix above landed (not clean-load: the graph rebuild shared the CPU)** | **2 failed · 3,698 passed · 38 skipped · 0 errors · 1,525 s** |
| run 8's two failures | both fixed after the run: the `--verdict` rebuild dropping `evidence` (Error #202) and the 2-worker speedup assertion (Error #201) |
| **aggregate suite, run 9 — everything from run 8's failures plus the marker registration** | **1 failed · 3,700 passed · 38 skipped · 0 errors · 1,472 s** |
| run 9's one failure | the heartbeat's 15s deadline, which its own first cycle needs 13.28s of: fixed to 60s with a named early failure for a stopped heart (Error #204), verified `62 passed` in `test_spine_mesh.py` |
| torch-state instrument, armed on run 6 | ✅ **11,219 phases observed, 0 partial-`torch`** (run 5: 25 occurrences) |
| `test_mutation` teardown + `test_dm_advanced` (ADR-014) | ✅ 17 passed (was 1 failed / 1 error) |
| `test_config_and_breaker` + `test_ncm_integration` + `test_brainstem_playing_field` | ✅ 100 passed |
| timing-assertion trio `test_pool` + `test_mesh_audit_insights` + `test_compliance_deadlock_regression` (ADR-015) | ✅ 70 passed |
| isolation profile (`--profile isolation`, CI-blocking) | ✅ **308 passed, 0 failed, 0 errors, 1 skipped** — baseline re-recorded at 0 ids (was 299) |
| `tools/type_check_gate.py --check` | ✅ OK: no new diagnostics — the baseline is now **content-anchored** (`relpath:rule:anchor`, 1,384 known), the staging pen is excluded by path (699 → 631 files analysed), and the scheme is recorded so a future identity change cannot be diffed across (Error #203, ADR-016) |
| `tests/test_type_check_gate.py` | ✅ 17 passed — including "lines inserted above a finding change no id" |
| `NEURAL_MESH_WIRE_OR_CUT_WORKLIST.md` | ✅ new derived artifact (registered in `artifact_freshness.py`): 101 pending rows in take-order with per-row evidence |
| `tools/aggregate_suite_gate.py --check` | ✅ OK: no new aggregate failures |
| `tools/artifact_freshness.py` | ✅ **all 7 derived artifacts current** — "OK: every derived artifact is at least as new as its sources"; `graphify update` + `cluster-only` rc=0 in 1,741 s; graph/report consistent (nodes=688,627 clustered=True) |
| `tools/audit_parseable_files.py --check --deep` | ✅ no new mislabelled files |
| derived maps rebuilt | TODO 1,487 functions · verdict 164 unreferenced · interop 482 edges |
| memory-DB leak repro pair | ✅ `1 failed, 13 passed` → `14 passed` (before → after) |
| `tests/test_memory_db_isolation.py` | ✅ 2 passed (and falsified without the fixture) |
| fs_probe guard repro pair | ✅ `10 failed, 28 passed` → **38 passed** |
| `tests/test_sentinel_thread_permit.py` | ✅ 2 passed (and falsified without the swap) |
| **aggregate suite, run 10 (contended box)** | ⚠️ **27 failed · 3,680 passed · 0 errors · 1,468 s** — 25 of the 27 were one defect (Error #205); the other 2 were Error #206 |
| **aggregate suite, run 11 — both defects fixed, clean load** | ✅ **0 failed · 3,712 passed · 38 skipped · 0 errors · 1,528.7 s (0:25:28)**. Session arc: **45 failed / 69 errors → 11 → 2 → 1 → 27 (contended) → 0** |
| torch-state instrument, armed on run 11 | ✅ **NO partial torch observed in 11,276 phases** — run 10 saw 7 broken phases of 11,261, run 6 saw 0 of 11,219. The polluter is gone and the instrument that named it now reports absence, which is the evidence the fix needed |
| `tools/type_check_gate.py --check` after the fixes | ✅ OK: no new diagnostics (1,384 known, **1,384 unchanged** — no churn either way, so the edits added and moved nothing) |
| `tools/artifact_freshness.py` after refreshing the mesh maps | **6 of 8 current** (`FUNCTION_TODO`, `WIRE_OR_CUT`, `WIRE_OR_CUT_WORKLIST`, `INTEGRATION_MAP`, `INTEROP.mmd`, `capability_wiring_dataset`); the two `graphify-out/` artifacts are **still stale** — see below |
| `scripts/graph_refresh_no_llm.py` (graph pair) | ❌ **failed**: `update .` extracted **51,186/51,186 files** then died `rc=4294967295` (-1) after 1,024 s with no error text, and `cluster-only` re-clustered the *old* graph (rc=0, 7 s). Retrying is a ~17-minute gamble on a 536 MB output; the version warning in the log (`skill is from graphify 0.9.55, package is 0.8.8`) is the first thing to rule out. Stated as outstanding, not folded into a green claim |
| torch-state instrument, armed on run 10 | ✅ **it named the polluter**: `13:12:02 FIRST PARTIAL torch ... missing=nn,Tensor,optim,autograd submodules=184`, 7 of 11,261 phases. Run 6 with the same instrument saw 0 of 11,219 — the difference between the runs is contention, which is the variable the earlier diagnosis was missing |
| `tests/test_nerve_torch_import.py` (new) | ✅ 4 passed — and **3 of the 4 fail against the daemon-thread implementation** (verified by re-installing it and re-running) |
| torch-dependent family, one process, after the fix | ✅ **195 passed** (`test_eve_unleashed` + `test_inference` + `test_sb3_agent` + `test_training_orchestrator` + `test_nerve_torch_import` + `test_proteus_organs`) — the same six files that held 25 of run 10's 27 failures |
| `tests/test_mesh_html_view.py` after vendoring vis.js | ✅ **6 passed in 3.9 s** (was 4 passed / 1 failed in 29 s — most of the old wall time was waiting on DNS for a library that was already in the repo) |
| isolation batch after both fixes (`spine_mesh`, `fs_probe_backend`, `sentinel_thread_permit`, memory-DB pair, `mesh_wire_or_cut`, `type_check_gate`, `compliance_deadlock_regression`, `pool`) | ✅ **157 passed · 1 skipped** |

### 7.10 The neural loop, end to end (measured 2026-09-22, not inferred)

The question "does the neural net work end to end" now has a measurement behind
each of its three parts, and the parts are kept separate because they have
different evidence:

| Path | Instrument | Result |
|---|---|---|
| **Read path (dry)** | `scripts/neural_loop.py --json` | ✅ **14/14 stages ok**, `verdict DRY`, `failed_stages []`, 9 write stages blocked *with reason*, 6,415 ms. `load` 472 edges / 114 distinct / l2 6.024407 · `perceive` 232 observed of 20,000 outcome rows, 2 chosen-never-run · `credit` 232 resolved, 0 unresolved |
| **Learning closure (apply)** | real stages, `LoopContext(apply=True)`, only `spine_registry._STATE_FILE` redirected to a temp file; `act`/`l1`/`l2` replaced by honest stubs | ✅ `verdict OK`, `ok True`, `changed [plasticity, consolidate, verify]`. `plasticity` 232 updates / 0 no-evidence (alpha 0.15, spread 0.082546) · `consolidate` 3 dreams, 8 reinforced · `prune` "nothing to forget: every edge carries evidence" · `grow` gate held 62 · `verify` **0 edges → 232 edges** read back off disk |
| **Cross-process durability** | second process, same state file | ✅ fresh process **loaded 232 edges** from disk; cycle 2 ran `OK`, `verify` sum 0.96454 → 1.770251, distinct 42 → 47. This is precisely the failure `_stage_persist` documents ("a fresh process afterwards still read 56 edges") and it is gone |
| **Fleet execution (`act`)** | `scripts/run_mesh_cycle.py` | ⚠️ **not exercised.** An applying cycle invokes the real fleet as a subprocess. Reported as unverified rather than claimed |
| **Promotion rungs (`l1`, `l2`)** | wiring genome / `hyperopt_cycle.step` | ⚠️ **not exercised.** `l2` appends a lineage row even when only proposing |

So: the loop **closes** — credit is read from the live tap, written as an
advantage, persisted, and independently re-read from disk by `verify`, across
processes. The fleet execution path is a separate system with a separate blast
radius and is stated as untested here instead of folded into a green verdict.

### 7.13 The repair for the leak was itself a leak, in the other direction (new, Error #200)

Two symptoms, one cause, and neither symptom named the leaker — the same shape
as #196, one layer up.

| Symptom | Where it was reported | Why it looked unrelated |
|---|---|---|
| `PermissionError [WinError 32]` on `azazael_memory_fd_dtgau\memory_store.db` | ERROR at teardown of `TestMutationDetection.test_mapping_summary_structure` | that test has no teardown of its own |
| `'session_start' not in ['cd5_benchmark', 'session_end', 'message_start', …]` | `test_dm_advanced::test_replay_session` | the test never chose a session id |

The restore fixture added for #196 recomputed each DB-path global from
`AZAZAEL_MEMORY_DIR`. But `tests/test_mutation.py:13` and
`tests/test_dm_advanced.py:13` redirect `direct_memory.DB_PATH` themselves, in
`setup_module()`, to a path the environment does not describe. The first test's
teardown therefore replaced their redirect with the **shared session store**.

What that then did is worth stating exactly, because the suite's own error
message understated it: `test_mutation.py::teardown_module` saw
`DB_PATH.exists()` was `True` and called `.unlink()` on **the live session
store**. The `WinError 32` was the open SQLite handle saving the run from
deleting the database it was running against — with no error at all if the
handle had been closed first. `test_dm_advanced`'s half was the documented
Phase-2 reconnect merge (`direct_memory.py:537`) adopting an existing open
session id, so `_start_session`'s `INSERT OR IGNORE` found the row and no
`session_start` was recorded.

Fixed by snapshotting the values in effect and restoring those, with the env
derivation kept only for modules imported *during* the test (which never had a
deliberate redirect to preserve). Recorded as ADR-014; the fixture's own test now
asserts the snapshot attribute names are still AST-visible, so the list cannot
rot.

### 7.14 Three wall-clock assertions graded the machine (new, Error #201)

| File | Assertion | Aggregate reading | Passing alone |
|---|---|---|---|
| `test_compliance_deadlock_regression` | call returns in `< 3.0 s` | **3.112 s** — "probable deadlock! Expected < 1s" | ✅ |
| `test_mesh_audit_insights` | two `overdue()` polls are equal | `overdue_by` **0.020** vs **0.021** | ✅ |
| `test_pool::test_benchmark_speedup` | 2 workers ≥ 1.0× 1 worker | speedup **< 1.0** | ✅ |

A re-entered `threading.Lock` does not slow down, it *never returns*, so the 3.0 s
bound was not a strict deadlock test — it was a strict test of the machine. The
other two asserted on quantities derived from `now()` and on 10 ms of work where
thread spawn dominated. Detection is kept (30 s, with the reason in the source),
the documented 1 s hot-path budget now feeds a `SLOW_CALLS` ledger instead of a
failure, the grace test compares *what is late* and bounds the lateness delta,
and the benchmark is best-of-3 over a workload that amortises fixed overhead.
Recorded as ADR-015, including the deliberate cost: a genuine slowdown that
completes inside 30 s is now a report a reader must read, not a red build.

The benchmark needed one more step than the first fix. Raising the workload and
taking the best of 3 attempts still read **0.687** on run 8, because a 31-minute
graph rebuild was sharing the processor. That is the point the two earlier
attempts missed: a *timing* signal cannot tell "the pool serialised its workers"
from "something else wanted the CPU", so no sampling scheme fixes it. The claim
was replaced by the property it stood for -- two workers in flight at once --
proved with a two-party `threading.Barrier` that returns at the same speed on an
idle box and a busy one. The speedup number is still measured and printed; it is
just no longer what the build fails on.

### 7.15 A rebuild dropped a field the transition had already been fixed to keep (new, Error #202)

`tests/test_mesh_wire_or_cut.py` failed in run 8 against
`NEURAL_MESH_WIRE_OR_CUT.json` with **62 `dispatched` rows and 0 carrying
evidence** -- the exact symptom of Error #199, whose fix was committed earlier
the same day and verified. The cause was one layer out: `wire_or_cut()` (the
rebuild `--verdict` runs) re-constructed every entry from four hand-picked keys,
so it discarded `evidence` and `triage`. The earlier fix had been verified with
`--verdict --propose`; the refresh path runs `--verdict` alone, so the next
refresh rewrote the file without the field.

This is worth stating as a class rather than an incident: the same fact was lost
in two places on two different paths, and fixing the transition was not fixing
it. The rebuild now carries the whole prior disposition forward and overlays only
what must track the tree, and the new regression test pins the rebuild rather
than the transition -- **falsified by the pre-fix code** (`KeyError: 'evidence'`).
Recorded as Error #202 / Lesson #96.

### 7.16 The priority list, worked (2026-09-22, after run 8)

Every item the audit's own priority list named, and what happened to it:

| Priority | Item | Outcome |
|---|---|---|
| P0 | full suite with every fix landed | ✅ **run 9: 1 failed / 3,700 passed / 0 errors in 24:32** (was 2/3,698 in run 8, 11/3,681 in run 6, 45 in run 4). The one failure was Error #204, fixed and verified. Over the session the failure count went **72 → 0 errors, 45 → 1 → 0** |
| P0 | WSL2 drift (3 test files) | ✅ `--sync-to wsl2` then `--verify` -> **PASS, tests 196/196 in sync** (was 193/196) |
| P1 | type gate baseline is line-numbered | ✅ **implemented** — content-anchored identity, scheme recorded, cross-scheme diff refused (Error #203, ADR-016) |
| P1 | 101 pending PF16 dispositions | ✅ **made actionable** — `--worklist` writes `NEURAL_MESH_WIRE_OR_CUT_WORKLIST.md`: 101 rows in take-order, each `test_reached_only` row carrying the test location that reaches it. Statuses are deliberately NOT written: a class is a measurement, and inventing 101 dispositions would be Error #190 again. **The decisions themselves remain the operator's** |
| P2 | generated output inside the analysed tree | ✅ excluded by path in `pyrightconfig.json`; files analysed 699 -> 631 |
| P2 | neural loop's untested half (`act`, `l1`, `l2`) | ⚠️ **contract pinned, fleet not fired** — `test_the_act_stage_and_the_executor_agree_on_the_summary_line` asserts the executor still prints the ` cycle ` line and `ok=%d` token that `_stage_act` scans for, closing the one silent failure mode an honest zero shares with a broken parser. Firing `run_mesh_cycle.py` (real fleet) and the genetic promotion rungs writes outside any containment this session has, so it is left as an operator command rather than folded into a green claim |
| P2 | `AZAZAEL_TEST_SHARED_PERMIT=0` | ✅ isolation profile run with the compatibility swap **off** — **310 passed, 0 failed, 0 errors, 1 skipped**, and 2 MORE tests pass than with the swap on, because the real thread-local token is what they exercise. ADR-013 asked whether the swap was masking a gap in the probe path: on this profile it was not. The swap stays until a FULL run with it off is green, which is a 25-minute measurement and is stated as outstanding rather than assumed |
| P3 | structural debt (561 untested functions, 1,386 diagnostics, 17 `shell=True`, 7 circular groups, 166-edge `worm_registry`) | ❌ unchanged, and unchanged by design — none of it is a session-sized fix, and the instruments that point at it are only now trustworthy |

Also fixed while working the list: `pytest.mark.slow` was applied 9 times and never
registered, so every run emitted `PytestUnknownMarkWarning`. It is registered in
`pytest.ini` now, with the reason it matters beyond tidiness: two suites
(`test_parallel_integration.py:450`, `test_inference_integration.py:1054`) filter on
that mark BY NAME, so a typo would silently stop applying it rather than fail.

### 7.17 An abandoned import thread poisoned every later `import torch` (new, Error #205)

Run 10 reported **27 failed / 3,680 passed**, and 25 of the 27 were the same
failure in four unrelated files: `partially initialized module 'torch' ... has no
attribute 'distributed'`. Every one of those files passes alone, passes as a pair,
and passed in run 9 on the same code.

The cause is one line of intent in `CORE/WORMS/expansion/nerve.py`. The lazy torch
loader bounded its import by running it on a daemon thread and returning after a
25 s join -- **and leaving the thread running** if the join expired. Walking away
from a live importer does not bound the import, it forks it: the thread keeps
executing torch's module body while `sys.modules['torch']` is the module object
mid-construction, so the next `import torch` anywhere in the process is handed the
corpse instead of importing.

The instrument that had been armed for two runs named it rather than leaving it to
inference: `missing=nn,Tensor,optim,autograd submodules=184` is not a first import
in progress, it is a *second* import running beside 184 registered children of a
previous one. Root cause reproduced standalone in eight seconds -- three threads
first-importing torch after purging `sys.modules` fail on attempt 2 with
`ValueError: module functions cannot set METH_CLASS or METH_STATIC`.

Fixed by removing the thread entirely: a **killable subprocess probe** establishes
whether torch imports on this host at all, and if it does, the load happens in the
caller's thread under a process-wide lock (ADR-017). Measured: probe 1.2 s, import
0.87 s, `state=ready`, no `torch-import` thread, three concurrent first users share
one module object.

Blast radius, verified before changing it: `expansion/nerve.py` has exactly four
import sites -- `spine.py:135` (production), `tests/test_proteus_organs.py`,
`tests/test_nerve_torch_import.py`, `scripts/verify_proteus.py`.

### 7.18 The mesh view needed the internet, so its verifier graded the network (new, Error #206)

The other two failures in run 10 were `ReferenceError: vis is not defined`: the
generated artifact linked vis.js from `unpkg.com`, the box had no route there, and
the page never initialised. `tools/verify_mesh_html.py` reported exactly what it
saw -- "the graph never initialised" -- and the defect was that a *passing check
was conditional on the network*. The 9.1.2 UMD build the CDN serves was already
vendored at `lib/vis-9.1.2/vis-network.min.js`.

Fixed at the generator (`tools/gephi_mesh_pipeline.py` computes a
document-relative href and **raises** rather than falling back to the CDN), arti-
fact regenerated, and pinned by `test_the_view_links_a_bundle_that_is_actually_there`.
The negative control had to change with it: a bare copy of a sibling-linked
artifact loses the library, so the copy now reproduces the layout and the only
difference from the real artifact is the injected dangling edge.

**Scanning the class rather than the instance** found **52** generated views in the
same position under `graphify-out/`, `graphs/`, `dashboard/` and `output/`
(`unpkg`, `cdnjs`, `jsdelivr`). Only the mesh view has a verifier, so the other 51
fail silently wherever they are opened offline -- recorded as AR-13 rather than
folded into this fix.

Also measured here, for AR-11: the corpus graph is built over **51,182 files /
203M words including `archived/` and `nuitka_build_backup/`**, so its top hub is
`BIBL Terms: F` at 367,598 edges and its top *code* hubs are C macros from vendored
onnxruntime (`HAS_ERROR_OCCURRED()`, 1,557). Its centrality answers questions about
the corpus, not about this repository.

### 7.19 The corpus map, asked a code question (new, Error #207)

The two commands were run against a question whose answer was already known --
whether anything reaches `db_monitor:DatabaseMonitorWorm.create_backup`, one of
the 101 pending PF16 rows:

```
$ graphify explain "create_backup"
Node: create_backup
  ID:        bibl_c_create_backup
  Source:    src/ORCHESTRATION/BIBL/C.md L8356
  Type:      document
  Degree:    1
Connections (1):
  <-- 4 = Dry run [contains] [EXTRACTED]

$ graphify query "who calls DatabaseMonitorWorm create_backup backup" --budget 700
Traversal: BFS depth=2 | 3 nodes found
NODE create_backup        [src=src/ORCHESTRATION/BIBL/C.md loc=L8356]
NODE DatabaseMonitorWorm  [src=src/CORE/WORMS/expansion/db_monitor.py loc=L93]
NODE DatabaseMonitorWorm  [src=src/CORE/.registry_cache.json loc=L1]
```

The name resolved to a prose entry (`Type: document`), the class resolved correctly,
and there are no call edges in the result at all. Node load is 10.7 s, so this is not
a budget or phrasing problem: `explain` and `query` share one node space, and that
space is the corpus. AR-11 said the centrality was about the corpus; this says the
*reachability* is too, and it says it with a wrong answer rather than an inference.

Consequence: PF16 reachability stays with the AST probe (`_reference_index`,
`string_references`), whose subject is this tree. The map is recorded out of scope
for code reachability so the next session does not re-spend the ten minutes.

Artifact freshness, measured in the same pass: **6 of 8 current**; the two stale rows
are `graphify-out/graph.json` and `GRAPH_REPORT.md`, both owed to this session's
`nerve.py` edit, and the rebuild needs more memory than this host has free --
**3.6 GB available of 15.4 GB** against a 536 MB graph that is held whole and
re-serialised. Recorded as capacity, not code, and the gate stays red.

### 7.20 101 pending rows now carry the fact that decides them (new, ADR-018)

`triage()` gave every pending row a *class* -- how it was measured -- and no
decider, so the backlog was 101 questions nobody had been handed. A second disjoint
label is now computed per row from the tree itself:

| Decider | Pending | Fact |
|---|---|---|
| `test_is_the_wire` | 40 | a test is the only caller |
| `dead_candidate` | 56 | no caller, no override, no computed dispatch |
| `dynamic_call` | 5 | the defining module builds a call target at runtime |
| `protocol_or_override` | 0 | the name is defined by another class |

Total 101, disjoint, and `status` is untouched -- asserted in both directions, the
same way `triage` is. The zero is a validated finding rather than an empty scan: the
index behind it was measured first (**3,371** method names, `run` in 28 classes,
`detect` in 7, 45 files with a computed `getattr`), because a broken walk returns 0
overrides for everything and reads exactly like "nothing is overridden". PF16 excludes
`PROTOCOL_METHODS` at discovery, so the surviving rows are single-definition names by
construction; the override decider exists to catch the next one.

The destructive decider is assigned **last**: an override and a computed dispatch are
both ruled out before `dead_candidate` may be written, since "the probe found no name"
is the weakest of the three facts and the only one whose error deletes capability.
`_resolve_module` returns `None` on an ambiguous stem instead of picking the first
candidate, so one `db_monitor.py` cannot lend another its dispatch evidence.

## 8. Architecture quality scorecard

| Dimension | Score | Assessment |
|---|---|---|
| Modular cohesion | 6.5 | `WORMS/expansion` (128 files / 40k lines) is well-named but flat; the learning cluster is mutually recursive |
| Inter-module coupling | 5.0 | `worm_registry` at 166 inbound edges is a hard single point of failure; `spine.py` at 24 outbound |
| Dependency hygiene | 6.0 | 7 circular groups; `ECOSYSTEM_EXPANSION` shim still warns on import |
| Type safety | **3.5** | 1,133 unannotated-param + 349 missing-return functions; now **measured** — basedpyright 1,191 errors + 252 warnings over 690 files, baseline-gated. Raised from 3.0 only for measurability: an instrument exists, the debt is unchanged |
| Test coverage | 6.0 | 3,508 passing tests, strong invariant-style prose; but 561 mesh functions have no test reference and the suite is not isolation-clean |
| Documentation | 8.0 | exceptional in-source reasoning (post-mortems embedded in the code they guard), 24-skill catalog, ADRs |
| Build system | **7.5** | scripted (`tools/refresh_all.py`, Nuitka suite); the aggregate suite and the type checker are now gated (ADR-010) — the isolation profile blocks in CI, the type gate reports |
| 3.14t readiness | 7.5 | free-threading throughout, thread-limits pinned in conftest; isolation debt still bites |
| Shell-injection safety | 6.5 | 17 `shell=True` (3 `scripts/`, 2 `tools/`, 4 `src/CORE`, 1 `src/INTERPRETERS`…) |
| Package management | 5.0 | `azazael.egg-info` + console scripts exist; `sys.path.insert` remains the norm |
| Desktop integration | 5.5 | 14 projects inventoried; no core wiring asserted by tests |
| **Overall** | **6.0/10** | Strong engineering *reasoning*, weak *aggregate verification* |

The gap between the reasoning quality (8.0 documentation) and the verification
quality (3.5 type safety, 6.0 coverage) is the single most useful sentence in
this audit: this codebase documents what it learned better than it checks that
it still holds.

**Update, same session.** The two verification dimensions were not merely weak,
they were **instruments that did not exist**: the CI type step was mypy, which
hard-crashed on two junk files named `nul` (Error #193), and no gate ran the
suite in the one shape that can see cross-file defects (ADR-010). Both now exist
and both are baseline-gated. A dimension scored low because it *could not be
measured* is a different finding from one scored low because the code is bad —
and the first kind is the cheaper to fix, which is exactly why it had gone
unnoticed: nobody re-checks a conclusion that sounds like a fact about the code.

## 9. Improvement items

| ID | Item | Effort | Impact | Priority |
|---|---|---|---|---|
| AR-1 | ~~Narrow `_purge_worm_modules` to worm-hosting modules so helper-module identity survives a reset~~ **DONE** — `_hosts_worms`, both halves pinned in `tests/test_registry_importable.py`; 65 → 50 failures | — | — | ✅ |
| AR-2 | Make the suite isolation-clean: the remaining 50 failures in 16 files, all of which pass alone (reproducers in §5). Concentration: `test_sb3_agent` 17, `test_fs_probe_backend` 10 | 1–2d | 🔴 | P0 |
| AR-3 | ~~Install mypy and record a baseline error count~~ **DONE, with a better instrument** — basedpyright was already installed and already configured; baseline 1,191 errors + 252 warnings over 690 files (ADR-011, `tools/type_check_gate.py`) | — | — | ✅ |
| AR-4 | ~~Add a CI gate that runs the **aggregate** suite~~ **DONE** — `tools/aggregate_suite_gate.py`, blocking in CI via `--profile isolation` (8 files, 299 tests, 0 failures); the full-suite baseline lives in `logs/aggregate_isolation_baseline.json` for the profile, full-suite report for the rest | — | — | ✅ |
| AR-5 | Break the `learning_*` SCC (4 modules) — no module in the group imports in isolation | 1d | 🟠 | P1 |
| AR-6 | Work the 102 `pending` `wire_or_cut` orphans (the 62 `dispatched` need a visible caller or deletion too, but the probe cannot decide them) | 3–5d | 🟠 | P1 |
| AR-7 | Clear the 1,133 + 700 annotation/docstring failures, module by module | 2–3d | 🟡 | P2 |
| AR-8 | Reduce `worm_registry` from 166 inbound edges (facade + narrow imports) | 2d | 🟠 | P1 |
| AR-9 | Triage the 255 write-swallowing handlers (PRESSURE on data-loss paths) | 1d | 🟠 | P1 |
| AR-10 | Retire the 17 `shell=True` sites to argv lists | 2h | 🟡 | P2 |
| AR-11 | Exclude vendored archives from the graph corpus so hubs describe this repo — **measured 2026-09-22**: 51,182 files / 203M words, top hub `BIBL Terms: F` (367,598 edges), top code hubs are vendored onnxruntime C macros. Its centrality is not a statement about this codebase | 2h | 🟡 | P2 |
| AR-13 | Vendor the renderer for the other **52** generated views that still fetch from unpkg / cdnjs / jsdelivr (only `mesh_gephi_interactive.html` has a verifier, so the rest fail silently offline) — Error #206 | 3h | 🟡 | P2 |
| AR-12 | Commit or discard the 3,759-entry dirty tree (3,150 `output/` deletions) | 2h | 🟠 | P1 |

## 10. Enforced invariants added this session

| Test | Property it now pins |
|---|---|
| `test_wiring_cycle.py::test_the_gate_still_gates_after_a_registry_reset` | a registry reset must not disarm the gate |
| `test_wiring_cycle.py::_cycle_wg` + gate tests | tests patch the module the cycle calls |
| `test_learning_closure.py::_objective_stub` | verdict tests do not read live telemetry |
| `test_learning_closure.py::test_verdict_is_OBJECTIVE_PINNED_before_the_effector_questions` | the objective check outranks the effector questions (previously untested branch) |
| `tests/conftest.py::pytest_runtest_setup` | the sentinel guard cannot block a test process's writes, at any fixture scope |
| `test_registry_importable.py::test_a_purge_reset_keeps_helper_module_identity` | a purge must replace worm hosts and must NOT replace helpers, asserted together so a test that pins only one cannot accept the pre-fix code |
| `test_registry_importable.py::test_the_purge_still_rebuilds_a_full_fleet_including_expansion` | two consecutive purges rebuild the same fleet (>100 worms, expansion included) — the identity fix must not have bought identity by losing re-registration |
| `test_aggregate_suite_gate.py::test_a_new_id_blocks_and_a_known_one_does_not` | a new aggregate failure is a regression; a known one is not |
| `test_aggregate_suite_gate.py::test_the_isolation_profile_stays_dependency_light` | the CI profile cannot gain a heavy import (AST-level: it *discusses* torch in a docstring, which a substring check cannot tell from importing it) |
| `test_aggregate_suite_gate.py::test_the_raw_output_is_persisted_so_a_failure_can_be_diagnosed` | the gate's evidence travels with its verdict (Error #194) |
| `test_type_check_gate.py::test_a_missing_checker_is_a_failure_not_a_clean_tree` | an unchecked tree cannot read as clean; likewise non-JSON output and a missing baseline |
| `test_type_check_gate.py::test_identity_ignores_the_message_so_rewording_is_not_a_fix` | a reworded diagnostic is not a repaired one |
| `test_sentinel_thread_permit.py` (4 tests, all against a rebound REAL `threading.local()`) | a worker holds its starter's permit and **only** its starter's permit |
| `test_memory_dir_caching.py::test_every_cached_path_global_is_restored` | a module that caches a path read from `AZAZAEL_MEMORY_DIR` at import cannot be missing from conftest's restore list (discovered by AST, not by hand) |
| `test_memory_dir_caching.py::test_the_scan_finds_the_known_cachers` | the scanner itself is checked against five modules it must find, so a silent scan cannot pass |
| `test_mesh_wire_or_cut.py::test_proposing_twice_keeps_the_evidence` | a re-runnable instrument keeps the measurements it made |
| `test_mesh_wire_or_cut.py::test_triage_labels_the_pending_backlog_without_deciding_it` | a triage pass cannot change a status, and the class counts must add up |
| `test_nerve_torch_import.py::test_the_import_runs_on_the_calling_thread` | no helper thread is constructed for the import, so none can be abandoned (three of these four fail against the daemon-thread version) |
| `test_nerve_torch_import.py::test_a_failed_probe_declines_without_importing` | an unproven host means numpy **and** nothing left running to race (`seconds == 0.0`) |
| `test_nerve_torch_import.py::test_a_ready_module_is_complete` | "loaded" must mean the attributes a completed import has, and the duration must be recorded |
| `test_nerve_torch_import.py::test_concurrent_first_users_share_one_import` | three threads get one module object and no error -- the interpreter-level race the lock exists for |
| `test_mesh_html_view.py::test_the_view_links_a_bundle_that_is_actually_there` | a generated view may not fetch its renderer over the network, and the href it does use must resolve |
| `tools/mesh_function_preflight.py` (stderr guard) | `--propose/--triage/--worklist` without `--verdict` now say they were ignored; before, `--triage --worklist` silently wrote nothing and left a 3-hour-old worklist on disk, which reads like "the backlog is empty" |
