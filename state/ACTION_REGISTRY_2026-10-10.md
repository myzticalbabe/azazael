# ACTION REGISTRY — blind + non-applied shelfware → integration

Date: 2026-10-10. Repo: `C:/Azazael/azazael`, branch `migration/baseline-20261001`.
HEAD at first write `52b7b453`; HEAD after wave 2 (2026-10-10 evening) `9552f8f5`.
Production interpreter: `C:/Azazael/.venvs/py315t` (3.15.0rc3 free-threaded, GIL off).
Source: audits of 2026-10-10 (MCP/architecture/tests/SOTA baseline, 3.15t reachability,
caller-census challenge, training-vs-harvest gap, orphan/subsystem/docs-TODO sweeps).

Status: OPEN (not started) / DOING / DONE (closed only with file:line evidence + 3.15t probe).
Rule: no item closes on a doc sentence; every CLOSE cites code.

## 0. GATES — precede all code work

- [ ] G-0a Snapshot the dirty tree (31 modified + 211 untracked at audit time): commit or `stash -u`.
  Why: failures unattributable without a baseline.
- [ ] G-0b Record a green 262-file suite run under `py -V:3.15t` (venv exe).
  Why: last real result covered ~1/3 of today's suite; no green baseline exists.
- [ ] G-0c Rebuild codegraph at HEAD (was built at `79f048a` vs HEAD `52b7b453`).
  Why: refactor mapping off a stale graph repeats the outlier failure.

## 1. HARVEST APPLICATION (the unapplied benefit)

- [ ] H-1 T-13 absorption: move each PARTIAL delta into its named host per
  `SOTA_ROW_RESCORE.md` (48 rows: A 17 / B 13 / C 19 / D 4), smallest-host-first.
  Why: 32/33 algos exercise-only; only EP171 DAG-half is host-integrated (and
  partially broken: CSE savings don't dedupe, TRT half missing).
- [ ] H-2 T-15 instrument swap: production-call-sites-per-technique; exercise-only = 0.
  Retire `exercise_technique_runtime.py` engaged=181 counter and `CAPABILITIES.md`-style
  registry self-reads. Why: current instrument measures the registry, not adoption.
- [ ] H-3 P10 trajectory→training edge: write run/exercise trajectories as rows
  `DataPipelineWorm` consumes (source/event_type trainers already read).
  Why: zero trainer←technique edge on any predicate today.
- [ ] H-4 Rows→live-config promotion: `ModelVersioner` rows → consumed weights/config;
  promote `evolved_rl_params` (only `.example.json` exists; `models/` dir absent).
  Why: training produces rows, nothing loadable.
- [ ] H-5 Dispose the 19 dangling adapters: 11 no-host (EP11,14,38,39,52,68,226,245,
  214,227,300 — ACCEPT-GAP or drop), 4 `scripts/meta_reflect` exercise refs
  (EP155,270,275,427), 2 `state/` artifacts (EP273,406), 1 self-ref (EP399),
  1 symbol-missing (EP308 `PSYCHE/distill.py:probe` — implement or drop).
- [ ] H-6 7/10 blueprint promises still paper-only (P1 ATP capsules hook, P4 skill
  families, P5 L3 acceptance gate, P6 workflow remediation, P7 every-transition,
  P9 role pools, P10 trajectory loop). Track inside H-1 per-row; listed here so the
  promise set isn't lost. (P2/P3/P8 already built.)

## 2. LOOP REVIVAL (make the regimen run, then feed it)

- [ ] L-1 T-1: enable `Azazael-Chain` on the CORRECT tree (`C:/Azazael/azazael`,
  not the stale `C:/Users/clint/azazael` checkout); `chain_controller_due.json` must appear.
- [ ] L-2 T-2: close the meta-evolution loop (log fired once manually 10/09, stale
  since; `loop_integrity.json`/`fitness_arms.json` hand-run, BLIND by design until fired).
- [ ] L-3 Schedule `tools/run_technique_exercises.py` (register the `techniques` job its
  docstring promises) or delete it; aggregate `state/technique_exercises.json` (8/8,
  read by nothing) or give it a consumer.
- [ ] L-4 Aggregate the 2 unaggregated exercises (`ep44_react_loop`, `ep370_epistemic`)
  or retire them.
- [ ] L-5 Un-blind the instruments: `evolution_progress`, `fitness_arm_liveness`,
  `render_ouroboros`, `chain_ops` (missing `chain_controller_due.json`),
  `capability_liveness` (itself unscheduled, reads blind outputs).

## 3. DEAD CODE + DUPLICATES (remove, don't carry)

- [~] D-1 PARTIAL — wave 2 (2026-10-10 evening) resolved three of these by EVIDENCE, not by
  wiring something up:
  - `discover_wirings` — **STALE ROW, DROPPED**: 0 occurrences in HEAD
    (`git show HEAD:src/CORE/technique_runtime.py | grep -c discover_wirings` -> `0`). The
    row cited a symbol that never existed, so nothing was removed.
  - `run_read_driven_consolidation` + `consolidate_from_reads` — **CLOSED, already wired by
    a later pass**: `read_pressure` (~674) <- `consolidate_from_reads` (:728) <-
    `run_read_driven_consolidation` (:787), and `_record_read_stats` is live on the read
    path through `RecallRouterWorm._note_read`, called from `route_recall` on all three
    branches (:424 owner_lookup, :446 semantic, :458 fallback). RESIDUAL: the only
    reference to the loop from outside is a STRING LITERAL at
    `technique_runtime.py:403` (`getattr(_engram, "run_read_driven_consolidation", None)`),
    which is why the mesh ledger still files it `dispatched`; naming it as an attribute
    would give a static caller. NOT DONE.
  - `recall_with_feedback` (`technique_runtime.py:362`) — EXISTS, deliberately restored; its
    only callers are the ARCHIVED `archive/theater-2026-10-10/exercise_technique_runtime.py:19,61`.
    The consumer to wire is `src/CORE/technique_wiring/_l1_memory.py:250-259`, whose adapter
    rebuilds `RecallRouterWorm().route_recall(...)` inline — a thinner duplicate of it.
    Owns the only NAMED reference to `engram.run_read_driven_consolidation`, so cutting it
    would re-break that. STILL OPEN.
  - `replan_after_failures` (`circuit_breaker.py:623`), `sentinel_enforcer.post_validate:435`,
    `enforce_replace:402` — STILL OPEN.
  - NEW, same defect class, FIXED this wave: `technique_runtime`'s recorder guard could never
    fire — an UNGUARDED `from CORE.failure_ledger import failure_notes, note_failure` with a
    redundant `try: from CORE.failure_ledger import note_failure / except ImportError:` block
    BELOW it, so the handler was unreachable in both branches (name already bound, or the
    module had already aborted). Removed; `failure_ledger` is a stdlib-only leaf, so the
    guard was never load-bearing.
- [x] D-2 **CLOSED** — wave 2 (2026-10-10 evening). Both halves have real readers, checked
  producer-against-consumer rather than trusted from a docstring:
  - `engram_read_pressure`: the writer (`engram.py` `_record_read_stats`, ~:744-761) emits
    `source="engram-read-pressure"`, `event_type="read_pressure"`, `data=pressure`; the
    reader `technique_runtime._read_pressure_summary` (:483) queries that exact `source` and
    reads `data["signal"]` and `data["abstention_rate"]` — the keys `read_pressure()`
    produces — and `fleet_link_health` folds it in (:570), which
    `scripts/technique_heartbeat.py:49,88` calls, itself driven by the scheduled
    `scripts/technique_heartbeat.bat`.
  - `technique-wiring` citations (`technique_runtime.py` `_cite`, used by `status()` and
    `run_all()`, ~:179/:217): the citation lands on the hash-chained ledger via
    `audit_trail.audit_verification_gate`, read by `audit_trail.verify_completeness`, which
    is called from `compliance/sentinel_gate.py`, `cli_audit.py`, `compliance/governance.py`,
    `audit_repair.py`, `scripts/close_audit_sessions.py`. Removing the emit would subtract
    from the audit trail, so it stays.
- [~] D-3 PARTIAL — wave 2 (2026-10-10 evening):
  - repo-root `METACLUSTER.py` — **STALE ROW, DROPPED**: absent from the repo root, from
    `..` (the session root) and from `/c/Azazael`. The row was kept alive by a misreading:
    `git ls-files --error-unmatch METACLUSTER.py` exiting non-zero asserts NOT TRACKED, which
    is not the claim "a file exists here". The production copy
    (`src/CORE/WORMS/METACLUSTER.py`, 1269 lines) is the only one present.
  - `archived_unified/` CLUSTERWORMS copy — EXISTS. STILL OPEN.
  - `packages/azazael-core` mirror — EXISTS, 0 `src/` references to `azazael_core`; the only
    `azazael-core` strings in `src/` are the `service_name` argument at
    `cd3_exporter.py:30,315,326`. Decide monorepo-import vs archive. STILL OPEN.
  - `*.pre_gate_backup` files — not yet counted. STILL OPEN.
- [ ] D-4 Triage orphan tools/scripts (**counts in this row are wrong by ~7-11x** —
  measured 2026-10-10 (worker 7) by counting the directory listings: `tools/` = **189
  entries (171 `.py` + 18 `.sh`/`.js`/`.ps1`/`.json`/`.txt`)**, not ~15; `scripts/` =
  **~258 entries, of which 24 are `.bat` (19 live + 5 `.bak-20261009-135335` stale
  copies)**, not ~40. The row's named set (9 tools + 5 scripts) is a *sample*, not the
  inventory. Sub-groups still hold as stated: `fix_swallows.py` et al are ONE-SHOT-DONE.
  Both totals are counted by hand from `list_directory`, so treat them as ±3, not exact;
  the ORDER OF MAGNITUDE is the finding. Original text follows; **the corrected counts
  are the ones to work from**):
  RE-MEASURED 2026-10-11 (worker 5) with machine-generated listings instead of a hand
  tally — `glob` returns its own `count`, and a `*.bat` pattern **cannot** match
  `x.bat.bak-...`, so live and stale counts separate exactly. **Three numbers in the
  block above are wrong; the ORDER OF MAGNITUDE finding holds and is strengthened.**
  - `scripts/*.bat` = **19 live — reproduces EXACTLY.** But the stale copies are
    **6, not 5** (`glob scripts/*.bak-*` = `open_aoa_monitor`, `open_lilith_live_monitor`,
    `refresh_oa_data`, `run_chain_live`, `run_evolution_cycle_314t`,
    `run_evolution_cycle_hyper` — all `.bat.bak-20261009-135335`), so the directory holds
    **25 `.bat`-named files, not 24**. The missed one is the `hyper` cycle.
  - `scripts/` = **279 visible files (+1 dotfile `.progress_anchor.md` = 280) + 6
    subdirectories**, so "~258" **understates it by ~21** — the row erred in the safe
    direction, but it is still a wrong number.
  - `tools/` = **191 files (173 `.py` + 18 non-`.py`) + 5 subdirectories.** The 18
    non-`.py` reproduces EXACTLY, but the total is **not stable**: it read 190 at an
    earlier listing in the same session and 191 minutes later, because concurrent work
    in this session created `tools/index_drift_check.py` while the row was being counted.
  - The named set (9 tools + 5 scripts) **reproduces** — all 9 exist (`claim_guard.py`,
    `hook_dispatch.py`, `learner_bridge.py`+`learner_bridge2.py`, `module_ownership.py`,
    `terence_watch.py`, `command_center.py`, `chain_watchdog.py`, `chain20.py`,
    `run_azazael_chain.py`).
  - **THE METHOD FINDING:** a hard-coded count in a row DECAYS, and this row's own
    directory demonstrated it by gaining a file mid-session. Any count here must carry
    the date AND the instrument that produced it; a bare number is a claim about a tree
    that no longer exists. `tools/chain_watchdog.py` is still the unscheduled supervisor
    the row flags.
  `claim_guard.py`, `hook_dispatch.py`, `learner_bridge*.py`, `module_ownership.py`,
  `terence_watch.py`, `command_center.py`, `chain_watchdog.py` (unscheduled supervisor!),
  `chain20.py`, `run_azazael_chain.py`, ~30 probe/patch one-shots (`fix_swallows.py` et al
  are ONE-SHOT-DONE — archive, don't schedule). Decide per item: schedule / archive / delete.
- [x] D-5 **CLOSED** — wave 2 (2026-10-10 evening), 6 of 7 items; `pygame` split out below:
  - the 5 self-circular `from X import main` shims — **already fixed and committed**: all five
    are CLEAN against `HEAD` (`git status --short` empty) and import package-qualified, e.g.
    `src/math_certainty.py:13` -> `from AZAZAEL_TOOLKIT.math_certainty import main`, with the
    reason recorded in-line at `src/COMPREHENSIVE_FIX.py:14-20`. The registry row was stale.
  - `opentelemetry.sdk` — **FIXED**. The SDK is genuinely absent on the production
    interpreter (`ModuleNotFoundError: No module named 'opentelemetry.sdk'`) while
    `cd3_exporter.py:49-50` imported it at MODULE level, so `import CORE.cd3_exporter`
    RAISED. Probes now: `OTEL_SDK_AVAILABLE False`; `SpanExportResult` =
    `_SpanExportResultFallback`; `SQLiteSpanExporter` present; `DB_PATH` =
    `C:\\Users\\clint\\.azazael\\memory_store.db`; `configure_otel_tracing()` raises a named
    `ImportError`. It also un-swallowed a live degradation: `tests/conftest.py:255` sat in a
    bare `except Exception: pass`, so its teardown silently skipped on this host.
  - `pygame` — **STILL OPEN**: `src/azazael_pygame.py:8` and a second copy at
    `src/CODEX/CORE/azazael_pygame.py:8`. Drop or vendor, and settle whether the pair is a
    duplicate to dedupe.

## 4. SUBSYSTEM WIRE-OR-CUT (one decision each, then execute)

- [ ] S-1 HYDRA: `src/HYDRA/*` + `ORCHESTRATION/HYDRA.py` + `hydra_bridge.py` — zero
  production callers. Wire a caller or cut.
  MEASURED 2026-10-10 (worker 7): **claim holds for `src/`-inward importers only.**
  `src/HYDRA/` exists (hydra_launcher.py, hydra_protocols.py, pipeline_specs.py,
  ml_platforms/, DOCUMENTATION/); `src/ORCHESTRATION/` holds HYDRA.py,
  HYDRA_ANALYZER.py, HYDRA_ANALYZER_V2.py, hydra_bridge.py. The importers are all
  OUTSIDE `src/`: `tools/flask_dashboard.py:91,105`, `tools/streamlit_dashboard.py:47`,
  `tools/hydra_api.py:21,73`, `tools/hydra_client.py:4`, `tools/hydra_graph.py:10`,
  `tools/hydra_test.py:12`, `tools/hydra_json_status.py:12`,
  `tools/hydra_integration_test.py:11`, `tools/hydra_verbose.py:14,35`, plus
  archived_unified/ and docs/. So it is tooling-invoked, not dead: DISPOSITION = WIRE
  (caller already named above; the missing piece is a *runtime* owner, not a caller).
  CUT would delete 3 ORCHESTRATION modules + src/HYDRA/ + 9 tools/hydra_* entry points.
  CAVEAT: the search window truncated at 96 matches, so absence of a further `src/`
  importer is not proven.
- [ ] S-2 META-4 (`InferenceBridge`, `DebugZ`, `DistillZ`, `MetaWormSpawner`): built at
  1ef29f87, reachable only via KLINK subprocess + tests. Import into runtime or cut.
  MEASURED 2026-10-10 (worker 7): all four files exist (`src/META/InferenceBridge.py`,
  `MetaWormSpawner.py`, `DebugZ.py`, `DistillZ.py` — 20 modules in src/META/). No
  `src/`-inward importer appeared in the match window; the only non-archive references
  are `.agents/skills`, ERROR_LOG.md, function_inventory.json and the graph/*.json
  exports. `InferenceBridge.py:35` `LLAMA_PORT = int(os.environ.get("LLAMA_SERVER_PORT",
  "18080"))` shows it is a client for the local llama-server. DISPOSITION = ACCEPT-GAP:
  the missing precondition is a decision on which runtime path should import them;
  CUT is not justified (tests exercise them, so they are not unverified capability).
  CAVEAT: search truncated — absence not proven.
- [ ] S-3 CODEX `unified_generator.py` (5.5k lines): sole caller is dead-end
  `batch_generator.py`. Wire a caller or cut. (`CODEX_Studio` stays AOA-gated: PARTIAL.)
  MEASURED 2026-10-10 (worker 7): **claim holds.**
  `src/CODEX/SESSION_TEMPLATE/generators/unified_generator.py` (5,536 lines per
  `docs/RUST_CONVERSION_PLAN.md:34`; 5,577 by REANALYSIS_DISCOVERIES) and the sibling
  `batch_generator.py` are the only two referents; REANALYSIS_DISCOVERIES.md:225 records
  it as "Referenced by: batch_generator.py, README.md, INDEX.md" — i.e. no code caller
  exists outside that pair. ORPHAN_TRIAGE_315T.md:196 classifies BOTH as
  **SUBAPP-ENTRY** (runnable app, no shipped launcher), which is the honest shape:
  DISPOSITION = ACCEPT-GAP on the same routing/registration question as the other 201
  SUBAPP-ENTRY rows, not a code defect. It also generates clean (CODEBASE_AUDIT_TODO.md
  S28-2: 11 styles, 0 defects), so CUT loses working capability. No first-class caller
  was invented to satisfy this row.
- [~] S-4 gateway (Rust :18080) + gateway-go (:18081): never run, unconfigured ports,
  zero `src/` refs. Run + configure or cut both. **The "cut both" half is now SETTLED —
  see the disposition below: RETAINED-WITH-REFERENT. The "never run" half stays open.**
  MEASURED 2026-10-10 (worker 7): **the port claim in this row is WRONG and must be
  corrected.** Both crate trees exist (`gateway/Cargo.toml` + `gateway/src/main.rs`;
  `gateway-go/go.mod` + `gateway-go/main.go`) and no `src/` module references either
  crate. But every `18080` in `src/` belongs to **llama-server / the dashboard, not the
  Rust gateway**: `CORE/inference/providers.py:604` ("the Rust supervisor on :8080 ...
  e.g. http://localhost:18080/v1"), `META/InferenceBridge.py:35`, and
  `CORE/web_dashboard.py:22` (`--port 18080`); `UTILITIES/KLINK/klink.py:564` merely
  probes `127.0.0.1:18080`; `config/ecosystem_config.yaml:55` sets `port: 18080`.
  So "gateway (Rust :18080)" conflates the crate with llama-server's port — a row that
  mis-states its own evidence. **That port correction HOLDS and is kept:** `18080` is
  llama-server's, confirmed at `config/config.yaml:21` and `config/production.yaml:35`
  (both `llama_url: "http://127.0.0.1:18080"`, inside a `llama:` block whose `backend:` is
  `"llama-server"`). Do NOT delete either believing it is the gateway's.
  MEASURED 2026-10-11 (worker 5) — **the DISPOSITION's premise is FALSE and is corrected:
  "nothing in `src/` loses a referent" is true of `src/` ONLY, and the row generalized it
  to the whole repo.** `tools/graph_semantic/` references both crates deliberately:
  - `coverage_layer.py:183-189` — a `POLYGLOT` entry `("proj_gateway_go", "gateway-go —
    OpenAI-compatible inference gateway", "gateway-go/go.mod", ...)` whose rationale is
    quoted from the crate's own manifest ("front end over llama-server backends ... go.mod
    module gateway-go, go 1.26.3").
  - `coverage_layer.py:208-217` — **the bridge.** Line 209 collects `go_sources` as every
    node whose `source_file` starts with `gateway-go/`; line 213 adds
    `add_edge("proj_gateway_go", n["id"], "references", ...)` for each, capped at 25
    (:215), and :217 prints `gateway-go nodes linked: N`. This is the fix for the
    degree-0 polyglot island (see `semantic_layer.py:461-462`, `graph_polyglot_islands`),
    so removing the tree makes the bridge dangle rather than disappear quietly.
  - `README.md:138-140` lists `gateway-go` among the polyglot islands the coverage layer
    closes; `semantic_layer.py:461-462` records the same node citing `gateway-go/go.mod`.
  Both crate trees exist: `gateway/Cargo.toml`, `gateway/Cargo.lock` (a file this row does
  not name), `gateway/src/main.rs`, `gateway-go/go.mod`, `gateway-go/main.go`.
  DISPOSITION = **RETAINED-WITH-REFERENT — nothing was cut.** CUT is not safe while the
  coverage layer bridges the tree; either the bridge is removed in the SAME change
  (`coverage_layer.py`'s `POLYGLOT` entry + the `go_sources`/`add_edge` block, plus the
  `README.md` and `semantic_layer.py` references) and the crate cut with it, or the crates
  stay and this row closes. Splitting the two would leave a graph edge into a deleted
  tree. The row's "never run / unconfigured ports" half is untouched here and remains open.
- [x] S-5 AOA: live standalone but inward-only (zero `CORE`/`ORCHESTRATION` importers).
  Invoke from runtime or accept standalone status explicitly.
  MEASURED 2026-10-10 (worker 7) — **CLOSED as ACCEPTED-STANDALONE.** A search of `src/`
  for `from AOA|import AOA|AOA.cli|AOA.core` returned **3 matches, all inside
  `AOA/core/arm_registry.py` itself** (its own docstrings, lines 130/142/145) — i.e.
  ZERO inward importers, confirming the claim on a full (untruncated) result set. `src/AOA/`
  is a live tree (cli/, arms/, core/, monitor, build.py, refresh_aoa_data.py, its own
  conftest.py/pytest.ini and 3 test modules), so it is an operational standalone app,
  not shelfware. Disposition executed as the row's own second option: standalone status
  is now explicit. Nothing to wire; no capability lost.
- [~] S-6 PARTIAL — the HORUS half is **REPAIRED and probe-verified** (wave 2, 2026-10-10
  evening); the `ouroboros.html` half is instrument blindness (L-5), not a stale file.
  HORUS defaulted its root to `Path.home() / "azazael"` — a DIFFERENT, stale checkout from
  this repo — at EIGHT sites (`:98 :118 :582 :688 :830 :840 :934 :1037` pre-fix), so with
  `HORUS_OUTPUT` and `AZAZAEL_ROOT` unset it read and wrote the wrong tree's output dir. It
  now resolves ONE module-level canonical root: `CORE.paths.get_project_root()` (which is a
  PACKAGE, `src/CORE/paths/__init__.py`), behind its own `src/CORE` sentinel, falling back to
  the module's own repo root. Precedence is unchanged at every site. Four probes:
  vars unset -> `C:\\Azazael\\azazael` (NOT `C:\\Users\\clint\\azazael`);
  `HORUS_OUTPUT=C:/probe/horus` -> that path;
  `AZAZAEL_ROOT` at a VALID root -> `C:\\temp_fakeroot`;
  `AZAZAEL_ROOT` at an INVALID path -> the shipping tree, which is the resolver's documented
  sentinel behaviour rather than a dropped override. (The last one is the easy misreading:
  the first probe of this looked like the override was ignored until a VALID alternative root
  was supplied.)
  NEW sub-item from the same worker, STILL OPEN, other files — the identical stale
  `~/azazael` fallback survives at `src/ORCHESTRATION/hydra_bridge.py:30`,
  `src/ORCHESTRATION/HYDRA.py:92,662`, `src/BIBL/bibl_map.py:672`.
  MEASURED 2026-10-10 (worker 7) — **two corrections to the claim, one part UNSETTLED.**
  (a) "points at non-existent paths" is STALE for the live module: `ORCHESTRATION/HORUS.py:98`
  defaults to `os.environ.get("HORUS_OUTPUT", os.environ.get("AZAZAEL_ROOT",
  str(Path.home() / "azazael")) + "/output/horus")`. Only the docstring at line 20 and
  the archived copy still say `C:/Users/clint/Desktop/HORUS`; BIBL/*.md prose repeats it.
  **New defect found instead:** that fallback resolves to `~/azazael`, which is the
  *stale second checkout* L-1 already warns about — so on a machine where `HORUS_OUTPUT`
  and `AZAZAEL_ROOT` are unset, HORUS reads and writes the WRONG tree's output dir. That
  is the repair worth doing, and it is a one-constant fix, not a data-flow rewrite.
  (b) `dashboard/ouroboros.html` is **generated, not hand-written**: `tools/render_ouroboros.py`
  declares `OUT = os.path.join(DASH, "ouroboros.html")` and stamps a timestamp
  (line 1024), and `tools/render_all_monitors.py:43` invokes it. "Static snapshot, no
  fetch" therefore describes the renderer's *inputs*, not a stale hand-edited file: the
  real defect is instrument blindness (L-5), not the HTML. DISPOSITION = REPAIR
  (HORUS fallback path), lower priority than L-5.
  UNSETTLED: whether `~/azazael/output/horus` and `Desktop/HORUS` exist on this box —
  both are outside the repo and could not be read with the tools available. Existence is
  asserted here as UNKNOWN, not as absent.
- [x] S-7 Accelerator sidecar (`tools/accelerator_sidecar.py`, registered in
  `providers.py:618-632`): zero selectors call it. Wire selection + env config or cut.
  MEASURED 2026-10-10 (worker 7) — **CLAIM IS STALE; CLOSED.** `accelerator_sidecar` is
  registered at `CORE/inference/providers.py:618` (base_url `http://localhost:18180/v1`,
  env override `ACCEL_SIDECAR_BASE_URL`) AND appears in `_LOCAL_PROVIDER_NAMES` at
  `providers.py:3077` — the very tuple the comment block at 3047-3072 introduces as the
  anonymous local providers whose existence is TCP-verified for failover ordering. So a
  *selector does call it*: it is in the local-provider selection set, and selection probes
  `host:port` rather than trusting a key. The row's residual work is therefore OPS, not
  code: the sidecar process must be running
  (`python tools/accelerator_sidecar.py --port 18180`, documented inside the registry
  entry itself). No wiring needed, nothing to cut.
- [ ] S-8 PAMS recorder contract: migrate the 12 `_pams = PamsRecorder()` import-time
  call sites to `get_recorder()` (`PamsRecorder.py:104-106` open question), or ratify
  the ctor deliberately.

## 5. MEMORY STACK HARDENING

- [ ] M-1 Fix `pams daemon_health` malformed `CallToolResult` (20 pydantic errors;
  `get_system_health` healthy — shape bug in the launcher/server, not the store).
- [ ] M-2 Repoint stale constants: `PamsRecorder` default `site-packages/memory_data`,
  `MemoryBus` port-file list (only `G:\...`, misses live `~/.pams`), single port-file
  discovery (server restart on new port silently drops clients).
- [ ] M-3 Diff the 5 skill copies (`azazael/skills`, `.agents/skills`,
  `~/.agents/skills`, `skills.win-backup`, plus catalog) — never diffed, may carry
  pre-0B-A text (`RULE_AUDIT_TODO.md` P4.3).
- [ ] M-4 De-venv-pin MCP servers (`py315t`/`Python314` absolute paths) or document the
  re-pin procedure for interpreter upgrades.

## 6. DEPS / ENV

- [ ] E-1 Resolve the 7 lockfile-missing packages: install (`mygrad, greenlet,
  ml_dtypes, optree, tiktoken, onnx, pywin32`) with 3.15t-compatible builds or remove
  from `requirements-3.15t.txt` — zero `src/` importers today, so either dead
  requirements or a need nobody can articulate.
- [ ] E-2 Reconcile `MarkupSafe` 2.1.5 vs pinned 3.0.4 and `pydantic_core` 2.46.5 vs
  2.49.0 (off the technique path, on the dashboard/html surface — verify there).

## 7. TEST / QUALITY BACKLOG (from docs-TODO consolidation, de-duplicated)

Quality gates: pytest-cov 60%+ gate + CI activation (C-11); worm regression smoke —
import+register+run for all 250 (C-6); startup registry validation + versioning (C-5);
parallel-execution + cross-nature integration tests (C-8); circuit-breaker/backoff/DLQ
tests (C-9); PAMS/MemoryBus recording mock tests (C-10); generator-behind-outputs test
strategy for 21 generated files (C-20); human-review 6 delete candidates (C-21);
re-run repo_audit+triage on every module change (C-22); T6 worm-count reconciliation
226/220 vs 250/35 (C-23); spine_mesh hang fix (C-7).
Hygiene/perf: autoflake 1,622 files + bare-except/`__all__`/litter sweep (C-24);
CORE/paths.py split — 139+ inbound deps (C-1); daemon-thread timeout kill (C-2);
partial-failure policy (C-3); sys.path-hack → editable install (C-4); 100-worm cProfile
+ registry/O(n)/executor/Mermaid perf pass (C-12); structured JSON logging + metrics +
health endpoint + drift alert (C-13); central timeout/retry config (C-14); desktop-path
consolidation ~10 hardcoded paths (C-18); wsl2_cleanup.sh eval→array (C-19, injection
surface); EXE/shim rebuild validation (C-16/C-17); single-entry CLI + Docker +
scheduled runs + pre-commit worm check (C-15). Ops: disk-80% alert, G: backup gap,
46.7 GB bloat audit, 22-html mirror (C-25).

## 8. WORKING METHOD (standing)

- Snapshot before surgery (G-0a); every CLOSE cites file:line + 3.15t probe output.
- Exercise-only engagement scores zero (T-15); production-call-sites-per-technique
  is the adoption metric. Instrument self-reads (`engaged=181`) are not evidence.
- Re-run the orphan/dead sweeps after each batch — the tree drifts faster than docs.

## 9. WAVE 2 (2026-10-10 evening) — what closed, what was corrected, what remains

Commits: `f448ae7c` (63 files, the SOTA fix + audit wave) and `9552f8f5` (3 files, this one).

Closed with evidence: D-2 (both halves), D-5 (6 of 7), S-6/HORUS, and D-1's
`run_read_driven_consolidation` branch.

Three registry rows were STALE and are corrected above rather than worked around. All three
failed the same way — a claim carried forward without re-measuring:
1. D-1 `discover_wirings` — the symbol has never existed (0 hits in HEAD).
2. D-3 repo-root `METACLUSTER.py` — the file does not exist; `git ls-files --error-unmatch`
   non-zero means NOT TRACKED, not EXISTS.
3. D-5 the 5 self-circular shims — fixed and committed before this wave.

Method that found them, worth repeating: try to FALSIFY the row against the tree first. A row
that cannot reproduce its own citation is a row to correct, not to implement.

Gates on the wave-2 tree: commit gate focused, staged scanner no new anti-patterns, canon
drift 1244/1244, anti-pattern gate 2670 == baseline, mesh ledger fresh at 174 declarations,
578 passed / 2 skipped / 0 failed on the 41-file sweep for the touched modules, 89 passed on
the four files covering them directly.

Still OPEN from this file: G-0a/G-0b/G-0c, H-1..H-6, L-1..L-5, D-1's remaining four items,
D-3's three, D-4, S-1..S-4 and S-8, M-1..M-4, E-1/E-2, and the whole section 7 backlog.
The D-4 counts in this file are corrected in place and are the ones to work from.

## 10. WAVE 3/4 (2026-10-11) — the stale-root class closed WITH a guard; instruments given exit codes

Commits: `f2b838e5` (29 files), `b0d3f2b4` (7 files).

### CLOSED, each with an executed probe or a test

- **[1] the stale-root fallback CLASS** (22+ sites, ~24 modules). The shared piece is
  `CORE.paths.get_project_root_safe()` — it honours `AZAZAEL_ROOT` first, never raises, and on a
  sentinel failure returns the tree it ships in. Bootstrap modules where importing CORE is
  circular by construction (`src/AOA`, `src/INTERPRETERS`, `src/TOOLS`, `src/UTILITIES`) derive
  `Path(__file__).resolve().parents[N]` instead, N counted per file.
  **The guard that was missing is now `tests/test_no_stale_root_fallback.py`** — AST-based, both
  quote styles, and carrying a NEGATIVE CONTROL. It caught 2 sites a truncated grep had hidden
  (`src/UVZ.py`/`src/META/UVZ.py` turned out to be FALSE POSITIVES of its own first needle, which
  is why the needle now requires the sibling to BE the `Path.home()` call).
  Two consequences of the old fallback were LIVE, not theoretical: `PamsRecorder.__init__`
  mkdir'd and wrote `C:/Users/clint/azazael/data/`, and both INTERPRETERS runners forwarded the
  stale root to their child process.
- **[4] pygame** — neither file failed honestly. `import pygame` was bare at MODULE level and
  pygame is NOT installed, so both modules died at import, which made the `__main__` handler
  advertising `pip install pygame` UNREACHABLE — and that handler exited 0 anyway. Now a guarded
  module-level import, `_PYGAME_AVAILABLE` read at two sites, and an entry point that exits 2.
  Canonical is `src/azazael_pygame.py` (`function_inventory.json:54`, `ERROR_LOG.md:1744`
  reference it; nothing references the copy); `src/CODEX/CORE/azazael_pygame.py` is a near-copy
  differing in 3 dead statements, and **D-3 should retire it**. Nothing imports either file.
- **[6] M-2 — BOTH halves.** *PamsRecorder:* its default already resolves the LIVE
  `~/.pams/memory_data`; there is no site-packages candidate left, so the registry's claim is
  STALE. *MemoryBus:* the candidate list already carries the live path best-first with the G:
  archive LAST (fixed in `cbacbbdb`), and its residual — `_pams_available` frozen at
  construction, so a bus built while PAMS was down stayed convinced for its whole life — is now
  a throttled re-check (`PAMS_RECHECK_SEC`, 15s) via `_ensure_pams_available()`.
- **[7] L-5, the four blind instruments** — code half DONE. The unifying defect: an instrument
  that cannot distinguish "nothing to report" from "I could not read anything", so it reports
  health it never measured. `evolution_progress`/`fitness_arm_liveness`: `if not
  os.path.exists(path): return {}` gave a MISSING log and an EMPTY log the same `NO_DATA` and the
  same exit 2; now `_input_state()` distinguishes them and the codes split, **3 NO_INPUT vs
  2 NO_DATA**. `capability_liveness`: `_load`'s error sentinel had NO reader, so a missing store
  made every check `dormant`/`ok` and exited 0; now `UNREADABLE` (not in `PASSING`) and a
  never-measured check returns `UNPROVEN` instead of OK. `render_ouroboros`: the stamp
  re-asserted liveness over stale data — it printed only `rendered <now>`; it now also carries the
  FRESHEST input's mtime and age plus an `INPUTS NOT READ` panel, and exits 1 when blind where it
  exited 0 while the page itself carried a "FAILED JOBS — non-zero return, invisible to liveness"
  table. **The SCHEDULING half is NOT closed**: nothing produces `chain_controller_due.json`,
  which is an ops change, not a file change.
- **[5] M-1 — premise STALE, real defect found and repaired.** `pams daemon_health` returns
  well-formed JSON; the malformed-CallToolResult / 20-pydantic-error shape does NOT reproduce.
  What the LIVE probe did surface is a genuinely broken hash chain: `~/.audit/daemon_health.jsonl`
  reported `record 346 (file line 346): prev_hash does not chain`, 8 genesis-linked records after
  the first, 847 parseable lines, 0 torn fragments. REPAIRED with the repo's own
  `tools/audit_chain_repair.py --apply` and re-verified: **chain validates YES, 0 genesis-linked,
  847 records, head `f8b4c41820e70159`**, with a size-verified pre-repair backup
  (`daemon_health.jsonl.pre_repair_20261011T014412Z`, 302556 bytes) kept alongside it. The tool
  quarantines torn bytes rather than deleting them; here there were none to quarantine.

### STALE ROWS CORRECTED — the 5th, 6th and 7th this session

- D-1 `replan_after_failures` (`circuit_breaker.py:623`) — **no definition anywhere in `src/`.**
- D-1 `enforce_replace` (`sentinel_enforcer:402`) — **no definition anywhere in `src/`.**
- D-1 `sentinel_enforcer.post_validate:435` — **HAS a caller**: `sentinel_enforcer.py:494` calls
  it from inside `enforce_write`. Live, not orphaned.

### STILL OPEN

G-0a/G-0b/G-0c; H-1..H-6; L-1/L-2/L-3 and L-4; D-1's `recall_with_feedback` (callers are the
ARCHIVED exercise only); D-3 (`archived_unified/`, `packages/azazael-core`, `*.pre_gate_backup`,
plus retiring the pygame copy); D-2's `METACLUSTER.export_state` write-only trio; D-4; S-1..S-4;
S-8; M-3; M-4; E-1; E-2; and the whole section 7 backlog.

### METHOD NOTES — both cost real wrong conclusions this session

- **A truncated view is not a result.** `| head -N` on a `git status` or a grep produced FOUR
  wrong conclusions: a "cleared" stale-root class that still had 2 sites, an "unmodified" file
  (`MemoryBus.py`) that was in fact already edited, and a missed set of files twice. Take the full
  listing or a COUNT; never conclude from a cut-off pipe. `&&` has the same shape — one failing
  `wc -l` silently prevented an entire test sweep from running.
- **The staged scanner reads the INDEX, not the worktree.** Two ratchet fixes (`allocation.py`,
  `scheduling.py`) were committed MISSING because the index held a pre-fix version while the
  worktree held the fix — and the scanner passed, because index-vs-HEAD looked unchanged. Before
  claiming "committed", read `git diff` (worktree vs index), never a staged-only grep.
- **A registry row is a claim, not a fact.** Seven rows so far could not reproduce their own
  citation. Falsify the row against the tree FIRST; a row that cannot reproduce is a row to
  correct, not to implement.

## 11. WAVE 4 VERIFICATION (2026-10-11) — a consumer in git whose supplier was not

Commit: `95c5371d` (4 files — the session-protocol tools plus the shared log vocabulary).

### A DEFECT THE WAVE 4 COMMITS THEMSELVES CREATED

`tools/evolution_log.py` was **untracked while three tracked files imported it at module level**
— `evolution_progress.py:96`, `fitness_arm_liveness.py:68`, `render_ouroboros.py:85`. So
`b0d3f2b4` landed three consumers of a module that existed on one disk only, and a fresh clone
would have raised `ImportError` on all three. Landed here, and verified satisfiable from the real
tree afterwards. Same shape as L-5 one level up: not an instrument that cannot see, but a repo
that cannot reproduce itself.

### CLASS-LEVEL SWEEP, not just the instance that was tripped over

Of the **22 untracked top-level `tools/*.py` modules**, none is IMPORTED by tracked code, and
exactly one is a documented PROCEDURE in tracked code:

- `tools/repoint_315t.py` — named by `tools/verify_engram_mcp.py` as `REPIN_REFERENCE` and in its
  docstring's re-pin procedure, so a tracked gate instructs the operator to run a tool that is not
  in git. **NOT landed, and deliberately**: the pre-commit scanner rejected it for
  `hardcoded_win_path 0 -> 2` (+2 against the repo-wide baseline), and the paths are intrinsic to
  what the tool does (it searches for literal interpreter paths and substitutes a literal one).
  It is also a NO-OP today — 11 rule MISMATCHes, `planned: 0 edits`. Landing it would raise the
  repo's permanent baseline for a tool that currently does nothing, so the honest state is
  recorded instead: it must be re-measured against this tree (TODO_315T_BUILD.md's repoint item)
  and its path literals derived per the scanner's own remedy (Path.home() / get_project_root())
  before it is landed. The gate's other route — baselining the +2 with an explanation — was NOT
  taken: a new file that adds findings to a ratcheted baseline defeats the ratchet's purpose.
- Four more are mentioned only by a TODO/handoff/census artifact — a record of what was used, not
  a dependency: `accelerator_bench.py` and `sota_dedup_check.py` (TODO_315T_BUILD.md),
  `install_technique_deps_315t.py` and `live_record_probe_315t.py`
  (state/adoption_census.json). Left untracked deliberately.

### THE PRE-COMMIT GATE CAUGHT THIS SESSION'S OWN DEFECT CLASS

The first attempt was REJECTED with two new `silent_except_pass` findings in the files being
landed (2,224-finding backlog class, added BY the commit). Fixed at the cause, not baselined:
`audit_chain_repair.py` now NAMES a temp file that survives a failed write instead of hiding the
cleanup failure, and `engram_supervise.py` now separates "the hook said nothing" from "the hook's
output could not be read" — a broken supervisor previously reported itself as `nudge: none due`,
a failure delivered as a clean verdict.

### THE ANCHOR RESIDUAL — expected, owned by the daemon, not fixable from here

`pams daemon_health` still reports `anchor_ok: false` / `severity: warning`: "anchored head
`0fab035c10253fd9` is no longer in the chain (records below it were rewritten)". This is the
repair's DOCUMENTED cost, stated in `tools/audit_chain_repair.py:43-47`: recomputing each `hash`
from its `prev_hash` means any external anchor over the old head cannot match — "it is the
definition of repairing a hash chain — and it is precisely why the pre-repair copy is mandatory".
The chain itself is sound (`chain_ok: true`, 847 entries, head `f8b4c41820e70159`). The anchor
store is `~/.audit/daemon_health.anchors.jsonl` (793 checkpoints; newest `2026-10-10T15:11:47`,
entry_count 847 carrying the OLD head) and it is written by the pmb daemon launcher, OUTSIDE this
repo; **no tool in this tree can re-anchor it**, and the repo's own `anchor_head_hash()`
(`CORE/audit_trail.py:443`) targets a different store (`.audit/anchors.jsonl`, the session chain).
A forced `pams trigger_database_maintenance` did NOT re-anchor. The next action therefore belongs
to the daemon's next checkpoint — an UNVERIFIED expectation, not a fact — and until then every
health check carries a warning whose cause is historical. Do NOT hand-write an anchor entry: a
fabricated Merkle root in the root-of-trust store is worse than a stale one.

### METHOD NOTE — the same trap, twice, and then its sibling

**Hit again in this very section.** `git commit` commits the INDEX, not the worktree. A commit was
REJECTED by the scanner, the file was then CORRECTED in the worktree, and the re-commit was run
without re-running `git add` — so the commit landed the pre-rejection version and the correction sat
unstaged. The tell was a staged diff of **68 insertions and 0 deletions** for an edit that REMOVED
words: read insertions-vs-deletions as a SHAPE, not just a count. After every rejected commit,
re-`add` the file before committing again.

### METHOD NOTE — the truncated-view trap has a cwd form

`cd C:/Azazael && ... git ls-files tools/session_start.py` ran the query from the PARENT tree, so
every file came back `UNTRACKED` — including five that are tracked. The `cd` in the command
silently overrode the tool's working directory. It was caught only because the parent tree has no
`tools/`, and corrected by re-running from `git rev-parse --show-toplevel`. Same family as
`| head -N`: a view that answers a question about a different thing.

### ALSO FOUND, NOT FIXED (open)

`repoint_315t.py` dry-runs cleanly and mutates nothing (`~/.agents/mcp.json` mtime unchanged) but
currently plans **0 edits against 11 rule MISMATCHes** — its rule table expects hit counts the tree
no longer has, so it refuses to act (by design: it will not apply approximately). The 3.15t
repoint it exists to perform cannot run until the rules are re-measured;
`state/repoint_315t.json` holds the per-rule detail (7 of the 11 printed by the dry run:
`run_evolution_cycle_314t.bat`, `open_aoa_monitor.bat`, `open_lilith_live_monitor.bat`,
`refresh_oa_data.bat`, `config/config.yaml`, `src/config/ecosystem_config.yaml`,
`src/config/pams_bridge.json` — each expecting 1-3 hits and finding 0).

## 12. WAVE 4 LANDED — and the gate REJECTED the wave's own fix (2026-10-11)

Commit: `a57ea026` (9 files, 704 insertions / 65 deletions) on `migration/baseline-20261001`.

### WHAT LANDED

`tools/index_drift_check.py` wired as pre-commit check 1b, `tests/test_tool_error_handlers.py`,
`tests/test_no_untracked_imported_module.py`, `scripts/chain_controller.py`,
`dashboard/ouroboros.html`, the two `archived_unified/ORCHESTRATION/scripts/` modules, and this file.

**The stale-index guard ran for real, on the very commit that shipped it:**
`[IndexDrift] 9 staged path(s); none edited after staging`. The class section 11 describes as a
method note is now mechanized, and its first execution was self-verifying.

All five gate checks passed on the real commit: focus gate (declared bulk), IndexDrift, staged
scanner (`6 staged .py file(s): no new anti-patterns`), canon drift `1244 == 1244` with
`substantive drift: 0`, ratchet `now 2670 == baseline 2670`, mesh ledger fresh at 174 declarations.

### THE FIX THAT CREATED A NEW FINDING — caught before it landed

The first attempt was REJECTED: `archived_unified/.../comprehensive_analysis.py:
hardcoded_win_path 3 -> 4 (+1)`. The `+1` was **my own escape fix**. `C:\ drive` (backslash then a
space) did NOT match the rule; rewriting it as `C:\\ drive` silenced the SyntaxWarning but matched
`[A-Z]:\\` for the first time. **The two gates pull in opposite directions on the same character.**
Resolved at the cause with ZERO backslashes — those docstring lines are now prose ("on the system
drive"), which satisfies both. NOT baselined: a deliberate `--baseline` bump for a docstring is
exactly the ratchet erosion the ratchet exists to prevent.

Residual, measured rather than assumed: the four `invalid escape` SyntaxWarnings still print during
the scanner run, and they are **HEAD-side** — the scanner compiles the pre-fix blob it is diffing
against. Per-file `py_compile` with `-W error::SyntaxWarning` over the staged snapshots emits
NOTHING, so the committed bytes are escape-clean. A gate is only as clean as the side of the diff
you are reading.

### THE CHAIN'S SCHEDULING HALF — root-caused, one artifact produced

Section 10 left this open. The writer is `_mark_completed`, reachable ONLY from the live loop
(`chain_controller.py:672`) and `catch_up (:595)`; `--job` never writes it. The task `Azazael-Chain`
reads `task_state: ok` / `Running` yet `last_fire: null` with `task_last_result: -2147020576`
(`0x800710E0` = Win32 4320). Its action `scripts\run_chain_live.bat` carries `Start In: N/A`, and
`logs/chain_controller.live.log` — the file that wrapper exists to write — was NEVER CREATED, so the
action never started, while `<ExecutionTimeLimit>PT0S</ExecutionTimeLimit>` (unlimited) explains a
stuck `Running` that holds no lock and writes nothing.
`state/chain_controller_due.json` now EXISTS (414 bytes) through the real writer path (bounded
`--live`), and the render job proved blind-input propagation end-to-end: exit 1 carrying
`BLIND on 1 input(s): state/chain_ops.json (absent)` inside `render-all`'s output.
**The scheduler fault is the operator's next action, not a file change** — the controller
deliberately never touches the scheduler.

### repoint_315t.py — CLOSED as ALREADY APPLIED, not patched

Section 11 said "re-measure before landing". Measured: `config/config.yaml:32` and
`run_chain_live.bat:22` ALREADY carry `C:/Azazael/.venvs/py315t/Scripts/python.exe`. So the 11
"expected 1, found 0" MISMATCHes are the signature of a repoint **already performed**, not a broken
rule table. `.venvs/py315t/Scripts/python.exe` exists and runs (probe returned `RAN`); the venv that
does NOT exist is `py314t` — the path this session's own fallback kept reaching for, which is why
the missing venv looked like the bat's fault. Corollary worth keeping: **the rule table is the
regression detector for the repoint** — "fixing" its expected counts to match today's tree would
delete the only signal that the repoint is still in force.

### .githooks/pre-commit — TRACKED and gitignored at the same time

`git add .githooks/pre-commit` was REFUSED ("The following paths are ignored"), and because the
staging command chained with `&&`, it short-circuited and staged NOTHING. The file IS in the index
(`git ls-files` lists it), so it was force-added at some earlier point while the path stayed
ignored. Consequence: **every future modification needs `git add -f`**, or HEAD silently keeps the
old gate — the same failure shape as section 11's `evolution_log.py`, one level down (a gate whose
mechanism is invisible to the thing that ships it). Never chain independent `git add` calls with
`&&`; a refusal in the first silently skips the rest.

## 13. WAVE 5 (2026-10-11) — S-8 CLOSED, the guard extended past `src/`, and Tier 4's premise was already satisfied

Commit: `97dcde73` (13 files, 392 insertions / 96 deletions) on `migration/baseline-20261001`.
Ten workers across three rounds; each change exercised, not merely compiled.

### CLOSED

- **S-8, PAMS recorder contract — CLOSED across 6 production sites.** `PamsRecorder.py:112-125`
  fixes the contract: `get_recorder()` is the singleton accessor and `__init__` is deliberately
  NOT one, so every module building its own instance is an uncoordinated writer on one
  `data/pams_fallback_records.json`. Sites: `WORMS/METACLUSTER.py`, `WORMS/BINARY_ANALYSIS_TYPES.py`,
  `WORMS/CLUSTERWORMS.py:203/234`, `WORMS/expansion/berks.py`, `WORMS/expansion/threatmon.py`,
  `worm_registry.py:_get_pams_recorder`.
  **Two were WORSE than the row described** — `berks.py` and `threatmon.py` cached the CLASS and
  constructed it on every call, i.e. a fresh recorder PER READ (threatmon's `_pams()` is reached
  hourly from `check_health`), not "one private instance per module".
  Probe, not inspection: two calls return the same object AND `a is get_recorder()` is True.
  **Two apparent sites were NOT the defect and were read and left alone**: `Agent.py:114` and
  `AgentPool.py:82-87` define a fake `PamsRecorder`/`get_recorder` inside `except ImportError:` —
  fallback stubs, while their real branch imports the singleton correctly. A grep-only sweep would
  have "fixed" them.
- **The stale-root guard's SCOPE gap** (found by this session's own review, in no row): the guard
  scanned `src/` only, while `scripts/sync_g_drive.py` set `SOURCE_ROOT = Path.home()/"azazael"`
  and its whole job is syncing THIS repo to G:. Fixed; the guard now scans `src/` + `scripts/` with
  exactly ONE named reviewed exception (`scripts/sna_scale_azazael.py:19`, whose external
  `graphify-out` target is the author's call, not a guard's). Two tests keep it honest: **a scan
  root yielding zero files FAILS** (the precise defect that let `scripts/` sit uncovered), and an
  exception outliving its site FAILS.
- **`.githooks` force-add — ROOT CAUSE, not workaround.** The rule was `.githooks/`, and git cannot
  re-include a file inside an excluded DIRECTORY, so the existing `!.githooks/pre-commit` negation
  was **inert**. `.githooks/*` makes it land. Acceptance-tested: `git add .githooks/pre-commit`
  succeeds WITHOUT `-f`.
- **D-1's `recall_with_feedback` consumer — WIRED.** `technique_wiring/_l1_memory.py`'s `ep235()`
  rebuilt `RecallRouterWorm().route_recall(...)` inline — a thinner duplicate that never read
  `recall_state()`. It now calls `CORE.technique_runtime.recall_with_feedback`, and
  `run_read_driven_consolidation` is bound bare after PROVING the import is not circular
  (`expansion/engram.py` imports stdlib only; its sole `technique_runtime` mention is a comment).

### THE MESH GATE BLOCKED THE COMMIT — and was right

First attempt refused: `[Mesh] ledger STALE -- 0 added, 1 removed`, naming
`engram:run_read_driven_consolidation`. That is the **intended effect** of the D-1 fix — the symbol
is no longer unreferenced — so the ledger was refreshed in the same commit (174 -> 173 declarations;
wired 0 / retired 3 / dispatched 60 / pending 110) rather than softening the reference to silence
the gate. Worth keeping: a change that makes a symbol referenced **must** move the ledger with it.

### TIER 4's BUILD-IN-HOST PREMISE WAS ALREADY SATISFIED — 2 rows corrected

Measured by workers who refused to implement:

- **EP252** — `src/CORE/WORMS/expansion/scheduling.py::rampup_data_limit` exists (~L180), is wired
  into `ScheduledTrainingWorm.execute()` (~L880), and `tests/test_drop_stable_rampup.py` (12 tests)
  was already on disk.
- **EP206** — `LocalMemoryStore.object_graph` (:1113), `traverse` (:1216), `object_graph_document`
  (:3067), `export_object_graph` (:3136), `load_object_graph` (:3167), with
  `tests/test_objectgraph_format.py` already on disk. (`ABSENT_TRIAGE`'s route and the registry both
  read as though this were pending.)
- A worker reported `STRUCTURAL_FLAWS_315T.md:255` records ALL THREE BUILD-IN-HOST rows (EP183,
  EP206, EP252) DONE on 2026-10-10 in commit `ac9dc46a`. **EP183 was NOT independently verified here.**
- **`ABSENT_TRIAGE_315T.md` is GENERATED** (`python tools/absent_triage.py`). Its "ABSENT" routing
  decays the moment a row lands; regenerate it rather than hand-editing the claim. The same lesson
  as the hard-coded counts in D-4: a generated artifact and a hand-written one rot differently.

### STILL OPEN / RESIDUALS — stated, not hidden

- **EP183 conflict UNRESOLVED.** `SOTA_BUILDABLE_SUBSET.md` rules it **EXCLUDED-with-an-option**
  ("counting 'a formal engine gates model output' as the shared mechanism would generalize the
  criterion until it stops excluding anything"); `ABSENT_TRIAGE_315T.md` routes it **BUILD-IN-HOST**
  to `cd2_verifier::SMTVerifier` / `compliance/state_machine.py::FormalVerifier`. Two docs, opposite
  verdicts, on the same row. Deliberately NOT implemented this wave; a human should rule.
- The guard parses `.py` only — a stale root in a `.bat`/`.ps1` is uncovered. And
  `packages/azazael-core/src/azazael_core/worms/clusters/METACLUSTER.py:839` still carries the
  fallback, deliberately outside `SCAN_ROOTS`: **D-3 still owes the monorepo-import-vs-archive call**.
- `ep235()` still returns `verified: True` unconditionally even when the call reports
  `{"routed": False}`, and its `payload["last_scores"]` is now always `[]` — `recall_with_feedback`
  does not surface `stats()["last_scores"]`. Both are decisions, not defects to guess at.
- `traverse(..., limit=1)` returns `[]` even when neighbours exist, because `_graph_peers` fetches its
  adjacency page with `LIMIT limit` too. Its docstring says that truncation is deliberate, so it was
  pinned by a test rather than reversed.
- Pre-existing `note_failure` line references are STALE in at least `CLUSTERWORMS.py`
  ("L182"/"L210"), `berks.py` ("L45"/"L49"), `threatmon.py` ("L43"/"L47") and `worm_registry.py`
  ("L1084"). Left alone on purpose: re-pointing them is unrelated to the defects fixed, and doing it
  blind would mask a real shift.
- **The ratchet baseline was NOT re-baselined** despite the gate inviting it:
  `import_inside_function 1061 -> 1060 (-1)`. Re-baselining now would bake in the unrelated
  uncommitted deletion `src/CORE/PamsBusBridge.py` sitting in this worktree. The 1-count headroom is
  the cheaper error.

## 14. WAVE 5 VERIFICATION PASS (2026-10-11) — L-5's residual closed, three more stale rows, one new class

Measured after `97dcde73` by PROBE and grep against the tree, not by reading the rows.

### L-5 residual — CLOSED for `chain_ops`

`state/chain_controller_due.json` exists (414 bytes, 2026-10-10 22:02) but is **THIN**:
`keys: ['render']` and **`last_fire: None`** — one job entry carrying no fire time. With the artifact
present, `tools/chain_ops.py` no longer prints `NO_DATA: chain_controller_due.json missing or
unreadable`. It produced a full report — `CHAIN OPS jobs=1`, DURATION `measurable 1/1`, reason
"the state file records fire time, not runtime, so duration is not measurable for ANY job until …" —
and exited **1**, which for this tool is it REPORTING findings, not crashing. The instrument that was
blind is reading. Still unverified: the other L-5 readers, `terence_invariants.py:751/864/1202/2433`
and `process_benchmark.py:54/135/222`.

### NEW CLASS, from that same instrument — 13 of 32 `state/` artifacts have NO READERS

`chain_ops.py`'s own CONSUMPTION section: `artifacts: 32`, `with NO readers: 13`, naming
`converge_315.partial.json`, `dep_gap_315t.json`, `orphan_scan.json` (+ 10 more). This is the
producer-without-consumer defect at the ARTIFACT level — the same shape as D-1/D-2 at the code level,
and no existing row covers it. The instrument found a class on its first honest run.

### STALE ROWS 8, 9 and 10 — all three falsified against the tree

1. **`replan_after_failures`** — `grep -rn replan_after_failures src --include=*.py` → **0 hits.** No
definition, no caller. Same class as `discover_wirings` (dropped in wave 2). The row cites
`circuit_breaker.py:623`; that line is not a definition. **CORRECT: drop the row.**
2. **`enforce_replace`** — `grep -n enforce_replace src/CORE/sentinel_enforcer.py` → **0 hits.** So
§10's "no definition anywhere in `src/`" is **CORRECT**. But this exposes a SECOND defect:
`SOTA_ROW_RESCORE.md:203` cites `src/CORE/sentinel_enforcer.py :: enforce_replace` as **EP125's HOST**,
and that symbol does not exist — an EP row's host attestation names nothing. The phantom came from
that row's own "symbol-scan" column (`enforce 236, enforce_write 373, enforce_replace 385,
get_status 550`): **a symbol scan that lists a name is not evidence the name is defined.**
**CORRECT: fix the EP125 host citation; do not implement a symbol nothing calls.**
3. **`chain_watchdog`** (D-4's "unscheduled supervisor") — no hit in any `scripts/*.bat`, and no hit
in `src/**/*.py` outside its own file. It exists at `scripts/chain_watchdog.py` and **nothing
schedules or calls it.** D-4's claim **HOLDS**; only that row's counts were wrong.

### ALSO STALE — `TODO_315T_BUILD.md:67` (row T-1)

That line states `chain_controller.py --status` reports `"task_state": "disabled"` /
`"task_detail": "Disabled"`. Measured 2026-10-11: `task_state: ok`, `task_detail: Running`,
`last_fire: null`, `task_last_result: -2147020576`. **The task is NOT disabled** — it runs and never
completes a fire. Unlike the generated `ABSENT_TRIAGE_315T.md`, this file is hand-written, so the line
should be corrected at the source. Recorded here so the next session does not act on "disabled" and
re-enable a task that is already enabled but broken at the action.

## 15. WAVE 6 (2026-10-11) — four residuals closed, one falsified claim, and a second ratchet that lies

Commits: `ecb34974` (labels), `61838878` (EP235), `73df012e` (guard/packages), `927e9cf7` (engram
guard), `5b5b3918` (pygame shim). Five focused commits, not one bulk op — see the gate note below.

### CLOSED

- **The stale `note_failure` line references — CLOSED, and the population was 17x the brief.** §13
  left these "alone on purpose"; the brief for this wave named ~6. The real population was **105
  sites** across four files: `berks.py` 12, `threatmon.py` 11, `CLUSTERWORMS.py` 41,
  `worm_registry.py` 41. Each is now named by its EVENT (`berks:pams-import`,
  `clusterworms:cancel` -> `clusterworms:future-cancel`, `worm_registry:discovery-cache-write`) with
  the stale number dropped. `grep -c ':L[0-9]'` is **0** in all four files.
  **Why this is safe, measured rather than assumed:** `failure_ledger.note_failure` builds
  `key = "%s:%s" % (where, type(exc).__name__)` — the label is an opaque dict key, and a repo-wide
  grep found **no code that parses the `:L<NN>` form**. The rename changes what a human reads, not
  what any consumer does.
  **Two labels were collapsed hazards, deliberately kept distinct:** `L313`/`L316` are the
  bare-import-then-full-path retry pair.
- **EP235's two residuals — CLOSED, and the RECORDED CAUSE WAS WRONG.** §13 and §14 both state
  `recall_with_feedback` "does not surface `stats()[\"last_scores\"]`". `RecallRouterWorm.recall_state()`
  **already returns `last_scores`** (`expansion/engram.py:544`); the defect was that the value was
  fetched and then thrown away. So the fix surfaces it rather than taking a second reading, and
  `ep235()`'s `verified` now follows the route outcome instead of being hard-coded `True`. Pinned by
  `tests/test_recall_feedback_contract.py`, whose failure case requires the `reader_to_writer` key —
  the property `_safe`'s fail-open shape (`{"verified": False, "reason": ...}`) does NOT carry, so a
  bare `verified is False` cannot pass merely because an exception was swallowed.
- **The guard's `packages/` blind spot — CLOSED.** §13 recorded
  `packages/azazael-core/.../METACLUSTER.py:839` as "deliberately outside `SCAN_ROOTS`". The needle
  regex over the WHOLE `packages/` tree returned **exactly one** match, so `SCAN_ROOTS` now includes
  `packages/` — safe rather than hopeful. The fork's own `paths.py` has no `get_project_root_safe`
  (only `get_project_root`), so the resolver is a three-tier chain rather than the twin's single
  import; the twin's verbatim import would have raised on the standalone package.
- **The engram guard naming an untracked tool — CLOSED.** `REPIN_REFERENCE` pointed at
  `tools/repoint_315t.py`, which is NOT in git, so a fresh clone was instructed to run a tool it does
  not have. The guard now probes the string it prints. Exit codes and the no-losses property held:
  `exit 0`, `PASS`.
- **D-5's pygame duplicate — CLOSED.** `src/CODEX/CORE/azazael_pygame.py` was a near-copy of
  `src/azazael_pygame.py` differing only in 3 dead statements; it is now a deprecation shim that
  re-exports the canonical surface (14 names + `_PYGAME_AVAILABLE`) and warns, with a structural test
  that fails if the retired implementation is pasted back.

### THE COMMIT GATE REFUSED — and the refusal was correct

First attempt: `BULK CHANGESET BLOCKED — 12 staged files exceed the bulk limit (8)`, plus
`azazael_pygame.py changes 704 lines (limit 150/file)`. **Resolved by splitting into five focused
commits, NOT by declaring the whole thing bulk.** Only the single-file 704-line retirement used
`ALLOW_BULK_COMMIT=1`, which its own message offered for exactly that case — a deletion cannot be
written to fit a 150-line file limit, and the alternative would have been five artificial partial
deletions of one duplicate.

### TWO METHODS FAILURES WORTH KEEPING

1. **A worker without ripgrep cannot finish a file-wide sweep.** The worker converted 3 files
   completely and had to leave `worm_registry.py` half in each convention (it correctly REFUSED to
   claim otherwise). The coordinator finished the remaining 42 sites with `grep -n ':L[0-9]'` +
   line-targeted edits. **A blind worker is the wrong owner for "every occurrence in a 2,206-line
   file".**
2. **A worker's own test could not run, and it did not know.** `test_recall_feedback_contract.py`
   died at COLLECTION with `ModuleNotFoundError: No module named 'CORE'` — the rootdir `conftest.py`
   redirects the stores but never puts `src/` on `sys.path`, so the repo's per-file idiom
   (`test_agent.py`: `sys.path.insert(0, .../src)`) is the bootstrap. Fixed; then
   **153 passed, 2 skipped** across the five affected suites. **A green-looking report is not a run.**

### FALSIFIED — a claim from this wave's own worker

Worker 1 reported the EP206 registration cited the wrong symbol (`document_graph_stats` vs
`get_knowledge_graph_stats`/`object_graph`/`traverse`) and flagged it "worth reconciling".
**Measured: FALSE.** `document_graph_stats` exists at `src/CORE/local_memory.py:2296`;
`get_knowledge_graph_stats` (:2986) is simply a DIFFERENT symbol. The registration's host citation is
correct and EP206 needs no correction. Recorded so the next session does not chase it — a
partial-inventory inference dressed as a symbol check is the §14 `enforce_replace` failure in reverse.

### NEW FINDING — `scripts/compliance_ratchet.py` is a second ratchet with a false verdict

Discovered by contradiction: the commit hook reported `import_inside_function 1061 -> 1059 (-2)` and
`OK: no anti-pattern regressions`, while `python scripts/compliance_ratchet.py` reported
`BLOCKED, category increased: import_inside_function 953 -> 1059`.

Both are real; they are different instruments:

| | authoritative | the stale one |
|---|---|---|
| tool | `tools/anti_pattern_gate.py --check` (hook check 4) | `scripts/compliance_ratchet.py` |
| baseline | `logs/anti_pattern_baseline.json` (rolling, 2026-10-10, 2670 findings) | `config/compliance_baseline.json` (**hand-recorded 2026-10-03**, 953) |
| called by | `.githooks/pre-commit` | **NOTHING** — repo-wide grep finds only its own docstring |

So the `+106` is **eight days of drift against a hand-recorded snapshot**, not this wave's change (the
real ratchet measured this wave as an IMPROVEMENT). Two consequences worth keeping:

- **Its verdict is false, and acting on the "fix" would be worse than ignoring it.** The tool's own
  remedy is `--record`, which would bake 106 findings into the baseline permanently — precisely the
  erosion §13 refused (`"a deliberate --baseline bump for a docstring is exactly the ratchet erosion
  the ratchet exists to prevent"`). **Do NOT `--record`.**
- **Recommended disposition: retire it in favour of `tools/anti_pattern_gate.py`**, or make it
  report its baseline's AGE and refuse to issue a verdict on a stale one. A gate that can never pass
  is not a gate; it is a producer with no consumer that still talks.

### STILL OPEN (unchanged where not noted)

EP183's conflict still needs a human ruling. D-3's monorepo-import-vs-archive call is still owed
(this wave removed the stale root and brought the tree under the guard WITHOUT deciding it). The 13
reader-less `state/` artifacts are enumerated in §14 but not dispositioned. The guard still parses
`.py` only, so a stale root in a `.bat`/`.ps1` is uncovered. `traverse(limit=1)`'s truncation stays
pinned rather than reversed. The ratchet headroom is now **`1061 -> 1059` (-2), deliberately NOT
banked** — `src/CORE/PamsBusBridge.py`'s uncommitted deletion still sits in this worktree and
re-baselining would bake it in. And the repo-wide `:L<NN>` convention elsewhere (~200 files still use
it) was NOT swept: this wave made the four files that carried the drift internally consistent, and
the divergence is recorded here rather than left to be discovered.
