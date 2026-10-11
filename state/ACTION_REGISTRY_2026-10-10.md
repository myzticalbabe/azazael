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
