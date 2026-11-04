# Commit slices — 2026-11-02

Source of truth: `git status --porcelain` captured at `.live/uncommitted_2026-11-02.txt`
(199 lines: **83 modified**, **2 deleted**, **114 untracked**). Every grouping below is
derived from a status line or from reading the file. Where intent could not be
established from the tree, the entry says **UNKNOWN** rather than guessing.

Branch at capture: `deepseek-engram-813 [renamed to azazael-intel-ultra-9-evo 2026-11-04]`. `origin` is a **local path**
(`C:\Users\clint\azazael`), not GitHub — see the publish notes at the end.

---

## 0. Read this first: 7 items must NOT be committed on autopilot

`git add -A` or `git add .` on this tree is unsafe today. These need a decision first:

| Item | Why it must not be staged blindly |
| --- | --- |
| `NEURAL_MESH_WIRE_OR_CUT.json` (468 KB) | Regenerated declaration table. Lesson 6375: a regeneration **dropped the `link_evidence` annotation** on `config:SecretRotator.rotate_secret` and the `wire-evidence` gate failed. Run `python tools/wire_evidence_audit.py --apply` **after** regenerating and **before** staging. `.gitignore` states this file IS deliberately tracked, so the fix is re-annotation, not un-tracking. |
| `src/META/reports/diagnostic_*.json` ×8, `fleet_*.json` ×8 | Timestamped run output (epoch-keyed filenames). `.gitignore` ignores `reports/env_inventory/` but has **no rule** for `src/META/reports/`. These are artefacts; 16 files of telemetry in a source commit is noise. |
| `swarm_results.json` | Root-level run artefact. `.gitignore` has `/*_report*.json` but nothing matching this name. |
| `src/src/` | Nested `src/src/ORCHESTRATION/BIBL` — the only content is a `BIBL` directory that already exists at `src/ORCHESTRATION/BIBL`. Looks like an accidental copy. **UNKNOWN** whether intentional; do not commit until someone confirms which copy is canonical. |
| `tools/supervisor_mcp.py.bak-20261029-freebuff` | A backup file. `.gitignore` has `*.bak`, which does **not** match this name (it ends `-freebuff`), so git would happily stage it. |
| `.opencode/` | Contains `plugin/bible.mjs`. `.gitignore` excludes `.claude/` but has no `.opencode/` rule. Whether client-local plugin config belongs in the published repo is **UNKNOWN** — it is a publishing decision, not a code decision. |
| `src/RUST_WASM/pkg/`, `pkg.baseline-2026-11-01/`, `pkg.nosimd/` | `wasm-pack` build output. `target/` **is** ignored by the existing rule, but `pkg*/` is not. Decide whether the built wasm is a shipped artefact or regenerate-only. |

Also flagged for a decision, lower risk: `docs/audit/` (new untracked dir),
`tools/budget.json` (**UNKNOWN** — config or emitted measurement?), `src/CODEX/package-lock.json`
(large; commit it if `package.json` lands, or the install is not reproducible), and
`logs/*.json` (see S7 — `logs/` is gitignored as a bucket, yet six files inside it are
already **tracked**, so they keep surfacing as modified; decide whether baselines are
durable evidence or regenerable telemetry).

---

## 1. Slices

Ordered roughly by blast radius: gates and canon first (they change what other commits
must satisfy), leaf work after.

### S1 — CI workflows (2 files)
```
git add .github/workflows/compliance.yml .github/workflows/test-3.15t.yml
```
Subject: `Give CI the gate set the local pre-commit runs, so a green build means something`
Why alone: workflow changes alter what every later push is judged by; they must be
reviewable without source noise. Intent of the edit is **UNKNOWN** (no diff was read) —
check these two files before staging.

### S2 — Canon sources + the generator that keeps them in sync (9 files)
```
git add SOP.md docs/agent_orders/00_session_order.md docs/agent_orders/flock_canon.md \
        docs/agent_orders/03_lane_queue.md docs/agent_orders/04_domain_trees.md \
        docs/MANDATE_PROVENANCE.md tools/agent_orders_sync.py tests/test_agent_orders_sync.py
```
Subject: `Make the lane queue and domain trees canon, and carry the sync tool that lands them`
Why alone: `AGENTS.md` blocks are **generated** from `docs/agent_orders/*` by
`tools/agent_orders_sync.py`. Landing the canon without the tool is an unenforceable
rule; landing the tool without the canon is dead code.
**Gate:** `canon-drift` and `orders-in-sync` will FAIL on a part-landed slice. Run
`python tools/agent_orders_sync.py --fix` and let it rewrite the generated targets
before committing, so the committed canon and the generated copies agree.

### S3 — Bible corpus, its checker, and its theme generator (8 files)
```
git add docs/bible/README.md docs/bible/bible.json docs/bible/PUSH_INJECTION.md \
        docs/bible/themes/ tools/bible_check.py tools/bible_theme.py \
        tests/test_bible_check.py tests/test_bible_ship.py tests/test_bible_theme.py
```
Subject: `Give the bible a theme generator and a ship check, so every claim cites a verse`
Why alone: data (`bible.json`), its checker, and its two new tests are one contract; the
`bible-citations` gate reads the JSON and `requires=("docs/bible/bible.json",)` — a
missing corpus is BLIND, not green.

### S4 — Platform claims engine + platform docs (9 files)
```
git add docs/platforms/README.md docs/platforms/BOX_PROMPTS.md docs/platforms/macos.md \
        docs/platforms/windows.md docs/platforms/claims.json tools/platform_claims.py \
        tools/box_profile.py tests/test_platform_claims.py
```
Subject: `Score the platform docs against a claims file instead of asserting fit`
Why alone: the `platform-claims` gate scores docs against `claims.json`; docs and the
engine must move together or the gate scores a claim set that does not exist yet.

### S5 — Memory/store hardening (9 files)
```
git add src/CORE/atomic_store.py src/CORE/data_retention.py src/CORE/direct_memory.py \
        src/CORE/local_memory.py src/CORE/recorder_guard.py tools/trim_episode_events.py \
        tests/test_data_retention_quota.py tests/test_memory_dir_caching.py \
        tests/test_recorder_guard.py
```
Subject: `Guard the production memory store on the write path, not only at the reader`
Why alone: touches the durability of every other subsystem; the `recorder_guard` +
`atomic_store` pair is the actual mechanism and its tests are the acceptance.

### S5b — Secret rotation (2 files)
```
git add tools/rotate_secret.py tests/test_secret_rotation.py
```
Subject: `Rotate a secret through one audited path instead of hand-editing each consumer`
Why alone: security-relevant and independently revertible; do not bury it in S5.

### S6 — MCP startup/gate stack (11 files)
```
git add tools/mcp_startup_gate.py tools/session_start.py tools/engram_supervise.py \
        tools/supervisor_mcp.py tools/pmb_client.py tools/pmb_floor_proxy.py \
        tools/mcp_eight_verify.py tools/verify_engram_mcp.py \
        tools/test_supervisor_load.py tools/test_verify_engram_mcp_siblings.py \
        tests/test_gate_lane_config.py tests/test_mcp_eight_verify.py
```
Subject: `Verify all eight MCP servers by spawning them, and gate on the differential`
Why alone: this is the stack every session starts through. It is also the one slice
whose failure is immediately visible (no memory load), so it should land early and clean.

### S7 — Quality gates, their baselines, and audit tooling (10 files)
```
git add tools/anti_pattern_gate.py tools/evidence_gate.py tools/ast_audit.py \
        tools/ast_drift.py tools/ast_drift_manifest.sh \
        tests/test_anti_pattern_gate.py tests/test_evidence_gate.py
# then, only if baselines are judged durable evidence:
git add logs/anti_pattern_baseline.json logs/basedpyright_baseline.json \
        logs/basedpyright_report.json logs/aggregate_isolation_baseline.json \
        logs/aggregate_isolation_report.json logs/aggregate_isolation_report.raw.txt
```
Subject: `Make the ratchets read a committed baseline so a green run means no regression`
Why alone / **HAZARD**: `anti-pattern-ratchet` compares the tree against
`logs/anti_pattern_baseline.json`. If the baseline is staged **in the same commit** as
the code it measures, the ratchet can pass by reading a baseline that already includes
the new violations. Land the code first, then rebaseline deliberately, and say so in the
commit message. If `logs/` is meant to be regenerable, drop the second `git add`
entirely — but then the ratchet has no baseline in a fresh clone, which is the defect
the `state/` block in `.gitignore` already documents at length.

### S8 — CORE package markers (2 files)
```
git add src/CORE/__init__.py src/CORE/camel/__init__.py
```
Subject: `Export the core package surface so integrators stop reaching into modules`
Why alone: trivial and load-bearing; if it breaks imports, it should be the only thing
to revert. `tests/test_pool.py` (modified) most likely belongs with the pool work —
**UNKNOWN** which slice owns it; read it first.

### S8a — Training / evolution loop (4 files)
```
git add src/CORE/WORMS/expansion/config.py src/CORE/WORMS/expansion/trainers_v2.py \
        src/CORE/sb3_agent.py
```
Subject: `Keep the expansion trainers and the SB3 agent on one config`
Why alone: reward/training semantics; a change here silently moves every measured score.

### S8b — New CORE integrations (5 files)
```
git add src/CORE/async_core.py src/CORE/failure_shim.pyi src/CORE/feast_feature_store.py \
        src/CORE/langgraph_integration.py src/CORE/parallel/__init__.py
```
Subject: `Add the integration seams — async core, feature store, graph runner — without wiring them`
Why alone: five independent new modules; if one is not ready, the others should not be
held hostage. Confirm none of them is import-time-required by `src/CORE/__init__.py`
(the failure would land in S8's commit, not this one).

### S8c — Sentinel enforcement (2 files)
```
git add src/CORE/sentinel_enforcer.py src/SCRIPTS/sentinel_gate.py
```
Subject: `Run the sentinel from the enforcer rather than from whoever remembered to call it`
Why alone: compliance-relevant; it is the mechanism a dozen other rules assume exists.

### S9 — Inference provider chain (1 file)
```
git add src/CORE/inference/providers.py
```
Subject: `Keep provider failover in one ordering instead of per-call fallbacks`
Why alone: single file, and every other subsystem's behaviour depends on which provider
answers. A regression here looks like a flaky model, not a code error, so it deserves its
own bisect point.

### S10 — Interpreters (3 files)
```
git add src/INTERPRETERS/node_runner.py src/INTERPRETERS/pwsh_runner.py \
        src/INTERPRETERS/sh_runner.py
```
Subject: `Give all three language runners the same timeout and error contract`
Why alone: three implementations of one contract; splitting them invites exactly the
drift the change is removing.

### S11 — FLAMING SWORD (5 files)
```
git add Project_FLAMING_SWORD/tests/test_sword.py Project_FLAMING_SWORD/tests/test_disposition.py \
        Project_FLAMING_SWORD/tools/disposition.py tools/sword_2600.py
```
Subject: `Record a disposition per swept file so a skip is a decision, not a silence`
Why alone: a self-contained sub-project; its tests are the acceptance.

### S12 — Retire two CAIN tools into the archive (3 paths)
```
git rm --cached tools/cain_fix_checks.py tools/cain_render_gate.py   # already deleted on disk
git add archive/retired-tools-20261101/
```
Subject: `Retire the two CAIN gates whose subject no longer exists, and keep the reason`
Why alone: this is **one** change, not a delete plus an add. `RETIREMENT.md` records both
sha256s, the measured `FileNotFoundError`, why nothing replaces them, and that the
copy-not-move pattern was followed. It also states
`test_retired_tools_stay_retired` keeps them from reappearing — so **the archive dir must
be committed or that test has nothing to check.**
The only references to the two paths anywhere in the tree are in `ast_audit/*.json`,
which are generated reports; nothing in code imports them.

### S13a — CODEX package markers (3 files)
```
git add src/CODEX/POPUPS/__init__.py src/CODEX/SESSION_TEMPLATE/generators/__init__.py \
        src/CODEX/comprehensive/__init__.py
```
Subject: `Make the CODEX subpackages importable so a missing __init__ stops reading as a missing module`

### S13b — CAIN session render (3 files)
```
git add src/CODEX/CAIN_injected.html src/CODEX/record_session_cain.js \
        src/CODEX/test_inject_session_cain.py
```
Subject: `Inject the session into the CAIN template from a testable recorder`
Why alone: the artefact, the script that fills it, and the test that proves the fill.

### S13c — CODEX test suite (4 files)
```
git add src/CODEX/TESTING/INTEGRATION/test_ecosystem_integration.py \
        src/CODEX/TESTING/PERFORMANCE/test_performance.py \
        src/CODEX/TESTING/UNIT/test_hydra.py src/CODEX/TESTING/UNIT/test_metaworms.py
```
Subject: `Bring the CODEX unit, performance and integration suites back in line with HEAD`
Why alone: tests-only, so a failure is unambiguous.

### S13d — CODEX video pipeline + npm manifest (3 files)
```
git add src/CODEX/dit_video_pipeline.py src/CODEX/package.json
# package-lock.json: commit WITH package.json or the install is not reproducible
git add src/CODEX/package-lock.json
```
Subject: `Add the DiT video pipeline and the node manifest its renderer needs`

### S14 — Rendering package skeleton (4 files)
```
git add src/RENDERING/characters/oxman/__init__.py src/RENDERING/characters/wraith/__init__.py \
        src/RENDERING/pipeline/__init__.py \
        RENDERING_SERIES_PLAN_Headless_Oxman_Lilith_Wraith.md
```
Subject: `Scaffold the character and pipeline packages the series plan names`

### S15 — Rust acceleration + wasm (3 paths + decision)
```
git add src/RUST_ACCEL/Cargo.toml src/RUST_ACCEL/Cargo.lock src/RUST_ACCEL/src \
        src/RUST_WASM/Cargo.toml src/RUST_WASM/Cargo.lock src/RUST_WASM/src \
        src/RUST_WASM/bench.mjs src/RUST_WASM/MEASURED_2026-11-01.md src/RUST_WASM/.cargo \
        tools/rust_accel_wrapper.py
# package the pkg*/ dirs ONLY after the decision in section 0
```
Subject: `Add the Rust and wasm accelerators with the wrapper that refuses a missing build`
Why alone: `target/` is already ignored, so this is source-only — but the `pkg*/`
directories are not, and that is the one way this slice can drag binaries into history.

### S16a — Graph / atlas / census tooling (15 files)
```
git add tools/atlas_to_graph3d.py tools/build_tree_network_3d.py tools/tree_sitter_census.py \
        tools/cpg_lite.py tools/cpg_joern_integration.py tools/gnn_tree_boundary.py \
        tools/graph_rag.py tools/graphrag_integration.py tools/semantic_zoom_ux.py \
        tools/unified_tree_map.py tools/dev_stack_census.py tools/precompute_force_layout.py \
        tools/domain_trees.py docs/UNIFIED_TREE_MAP.json tools/yggdrasil_atlas.py
```
Subject: `Read the tree through one atlas, with the census tools that build it`
Why alone: these tools share the `docs/UNIFIED_TREE_MAP.json` artefact; splitting them
leaves a generator whose output has no consumer.

### S16b — Triage / repo-audit tooling (6 files)
```
git add tools/backlog_triage.py tools/todo_triage.py tools/audit_growth_controls.py \
        tools/git_repo_doctor.py tools/git_stack_plan.py tools/cleave_check.py
```
Subject: `Make backlog triage and repo diagnosis commands instead of one-off sweeps`

### S16c — Single-purpose utilities (7 files)
```
git add tools/fast_json.py tools/floor_measure.py tools/metthew_bench.py \
        tools/nature_swarm.py tools/redispose_bare_token_wired.py tools/second_opinion.py \
        tools/go_census.go
```
Subject: `Add the small standalone tools, one job each`
Why one slice: each is independent and unimported by the rest; eleven separate commits for
eleven small files would bury the log. If any one is unfinished, split it out.

### S17a — Yggdrasil docs (6 files)
```
git add docs/YGGDRASIL_CLEAVE.html docs/YGGDRASIL_SHARD_01_WORMS.html \
        docs/YGGDRASIL_3D_BLOOM_2026-10-31.html docs/YGGDRASIL_CLEAVE_FORENSIC_AUDIT_2026-10-31.md \
        docs/YGGDRASIL_CLEAVE_LANE_INSTRUCTIONS_2026-10-31.md \
        docs/YGGDRASIL_COMPLETE_TREE_REGISTRY.md docs/YGGDRASIL_TREES_SEMANTIC_RENDERING_GUIDE.md
```
Subject: `Document what the Yggdrasil renders measure, and what they refuse to claim`

### S17b — Triage / restart records (8 files)
```
git add RESTART_TASKS_2026-10-31.md RESTART_TASKS_INDEX.md _file_restart_tasks.py \
        tools/restart_tasks_index.py docs/ALERT_ARM_ARCHITECTURAL_REDESIGN.md \
        docs/DEAD_CODE_TRIAGE_2026-11-01.md docs/NOTE_FAILURE_REFACTORING_STRATEGY.md \
        docs/TODO_TRIAGE_2026-10-31.md docs/VULTURE_DEAD_CODE_REPORT_2026-10-31.txt
```
Subject: `Hand off the restart queue as files, with the triage they came from`
Why alone: `_file_restart_tasks.py` + `restart_tasks_index.py` generate the two
`RESTART_TASKS*` files — generator and output are one change.

### S18 — AOA documentation surfaces (3 files)
```
git add src/AOA/AOA_DISCLOSURE.html src/AOA/AOA_STRUCTURE.html src/AOA/CROSS_ENV_MANIFEST.md
```
Subject: `Disclose the AOA structure and cross-environment manifest as generated views`
**UNKNOWN**: the two `.html` files look generated. If they are produced by a script,
land the script here too (none appears in this changeset) or they are un-reproducible.

### S19 — SCRIPTS dashboard + telemetry (2 files) — decision needed
```
git add src/SCRIPTS/rule_0zf_dashboard.html
# src/SCRIPTS/telemetry.json: LIVE runtime state. Decide durable-evidence vs telemetry
# before staging; `.gitignore` ignores `logs/` and `state/` for exactly this reason.
```
Subject: `Render the RULE 0ZF dashboard from the state it measures`

### S20 — Skills (7 files)
```
git add skills/azazael-bin-httpx.md skills/azazael-compliance-deep-dive.md \
        skills/azazael-pre-action-gate.md skills/azazael-rendering-methods.md \
        skills/azazael-sentinel-gate.md skills/azazael-session-recording.md \
        skills/azazael-sync-kali.md
```
Subject: `Correct the seven skills whose instructions no longer match the system they describe`

### S21 — Bleeding-edge / tree-of-life prose (5 files)
```
git add docs/AZAZAEL_TREE_OF_LIFE.md docs/ORPHAN_TRIAGE_2026-10-03.md \
        docs/GIT_FLEET_BLEEDING_EDGE_2026-11-01.md docs/GIT_TOOLING_BLEEDING_EDGE_2026-11-01.md \
        docs/OPUS_BLEEDING_EDGE_PRACTICE.md
```
Subject: `Record the bleeding-edge practice the fleet actually follows, not the one it declared`

### S22 — Daemons package (1 file)
```
git add src/DAEMONS/__init__.py
```
Subject: `Make the daemons package importable before anything can register into it`

### S23 — Orchestration, evolution, board (6 files)
```
git add scripts/evolution_cycle.py scripts/evolution_dashboard.py \
        src/ORCHESTRATION/ml_platforms/universal_converter.py \
        src/ORCHESTRATION/ray_serve_deployment.py src/CORE/LaneMessageBoard.py \
        tools/mesh_function_preflight.py tools/swarm_arena/arena.py
```
Subject: `Keep the evolution cycle, the board and the preflight census on one HEAD`
Why alone: three integration points that each other's tests assume; note
`evolution_cycle.py` writes the `config/evolved_*` and `state/*` files that `.gitignore`
explicitly protects — **never** widen this commit to include those.
`tools/mesh_function_preflight.py` regenerates `/NEURAL_MESH_FUNCTION_TODO.md`, which is
deliberately untracked.

---

## 2. Landing order

1. **S1** CI, then **S2** canon+sync (run `agent_orders_sync.py --fix` first), then
   **S3**, **S4** — these define what the gates check, so they go before anything the
   gates will judge.
2. **S6** MCP stack — verify with `mcp_startup_gate.py` and `mcp_eight_verify.py` before
   committing; it is the stack the next session inherits.
3. **S12** retirement (with its archive), **S8 / S13a / S22** package markers — small,
   unblocking, low risk.
4. **S5, S5b, S8a, S8b, S8c, S9, S10** core behaviour, one at a time.
5. **S11, S13b–d, S14, S15, S16a–c** feature/tooling slices.
6. **S17–S23** docs and everything else.
7. **S7 last** — land the gates and rebaseline only once the tree they measure is settled,
   or the ratchet records the wrong baseline.
8. **`NEURAL_MESH_WIRE_OR_CUT.json` last of all**, after `wire_evidence_audit.py --apply`.

---

## 3. Which slices can fail a commit gate, and why

- **`canon-drift` / `orders-in-sync` (S2):** FAIL if `docs/agent_orders/*` lands without
  regenerating the AGENTS.md family. Non-negotiable ordering inside the slice.
- **`wire-evidence` / `mesh-ledger-freshness` (wire-or-cut ledger):** FAIL if the
  regenerated declaration table is staged without `wire_evidence_audit.py --apply`.
  This has happened before (lesson 6375).
- **`bible-citations` (S3):** FAIL if `bible.json` is missing or a cited verse does not
  resolve. An absent corpus is BLIND rather than green, per the gate's own `requires`.
- **`anti-pattern-ratchet` (S7 and every `src/` slice):** will read
  `logs/anti_pattern_baseline.json`. Staging a baseline together with the code it
  measures can produce a **false pass**. Rebaseline in its own commit and name it.
- **`staged-scanner` (all):** scans the staged diff. Any secret-shaped string blocks the
  commit regardless of slice. Do not "fix" a finding by rebaselining.
- **`changeset-focus` (all):** this is the gate that punishes exactly the failure mode
  this document exists to prevent. One slice = one reason.
- **`platform-claims` (S4), `evidence-gate` (~30 s) and the ~3-minute evidence tier
  (pre-push, not pre-commit):** a push runs the long tier. Budget for it; do not read a
  fast local commit as a passing gate.
- **`unresolved-refs-ratchet` and `stale-index-guard` (S16a, S17a):** moving or adding
  docs can orphan references; the atlas slice is the likeliest offender.

**Not verified in this document:** no gate was executed, no diff of the two
`.github/workflows` files was read, and no untracked file was opened except
`archive/retired-tools-20261101/RETIREMENT.md`. Every pathspec above comes from the
captured status listing; the grouping rationale comes from the file's location, its
name, and — where stated — its content.

---

## 4. Publish notes (outside this document's scope, recorded so they are not lost)

- `origin` is `C:\Users\clint\azazael`, a local path. There is no GitHub remote yet.
- Two blobs in history exceed GitHub's 100 MB hard limit
  (`archived/2026-05-31/onnxruntime.tar.gz` 272.3 MB and
  `archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz` 228.8 MB). A push will be
  **rejected** until history is rewritten or a fresh history is published.
- `git count-objects -vH` reports `size-pack: 954.92 MiB`.
- No `LICENSE` file exists at the repo root, and `README.md` is present (374 lines).
