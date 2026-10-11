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
- [ ] S-4 gateway (Rust :18080) + gateway-go (:18081): never run, unconfigured ports,
  zero `src/` refs. Run + configure or cut both.
  MEASURED 2026-10-10 (worker 7): **the port claim in this row is WRONG and must be
  corrected.** Both crate trees exist (`gateway/Cargo.toml` + `gateway/src/main.rs`;
  `gateway-go/go.mod` + `gateway-go/main.go`) and no `src/` module references either
  crate. But every `18080` in `src/` belongs to **llama-server / the dashboard, not the
  Rust gateway**: `CORE/inference/providers.py:604` ("the Rust supervisor on :8080 ...
  e.g. http://localhost:18080/v1"), `META/InferenceBridge.py:35`, and
  `CORE/web_dashboard.py:22` (`--port 18080`); `UTILITIES/KLINK/klink.py:564` merely
  probes `127.0.0.1:18080`; `config/ecosystem_config.yaml:55` sets `port: 18080`.
  So "gateway (Rust :18080)" conflates the crate with llama-server's port — a row that
  mis-states its own evidence. DISPOSITION = CUT both crates (nothing in `src/` loses a
  referent) — owner executes; the port attribution must be fixed first, or a future
  reader will delete llama-server's configuration believing it is the gateway's.
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
