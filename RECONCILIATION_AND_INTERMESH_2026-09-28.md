# Revision reconciliation + intermesh audit — 2026-09-28

Two pieces of work, both driven by the same failure mode: **an artifact that
answers for a tree it no longer describes.**

- Part 1 reconciles the three divergent revisions into one authoritative state.
- Part 2 audits the intermesh (the nature/contract integration map) and fixes
  what it was missing.

Everything below is measured, not inferred. Where a claim rests on a command,
the command's effect is stated so it can be re-run.

---

## Part 1 — Revision reconciliation

### 1.1 The problem

Three working copies have diverged:

| tree | state |
|------|-------|
| `C:\Users\clint\azazael` (Windows, live) | git HEAD + in-flight work |
| `/root/azazael` (WSL, Ubuntu-26.04) | holds a Sep-21 revision that Windows partially lost |
| `G:/source-of-truth/azazael` | stale non-git mirror |

Loss mechanism (established earlier): `git reflog` shows two
`reset: moving to HEAD` entries, i.e. `git reset --hard` discarded uncommitted
work. The WSL tree still holds parts of it.

### 1.2 Method — `tools/wsl_revision_diff.py` (new)

A read-only drift report over the two trees. It normalises newlines, counts
lines unique to each side with `difflib.SequenceMatcher`, and classifies:

| status | meaning |
|--------|---------|
| `WSL_SUPERSET` | local has **nothing** the mirror lacks — safe to copy across |
| `LOCAL_SUPERSET` | mirror has nothing this tree lacks |
| `DIVERGED` | **both** sides hold unique lines — needs a human decision |
| `MIRROR_ONLY` / `LOCAL_ONLY` | file absent on one side |

Two implementation notes that mattered:

- The mirror is reachable from Windows at
  `//wsl.localhost/Ubuntu-26.04/root/azazael`, so the scan runs from Windows
  Python without `wsl.exe` quoting hazards.
- The first version compared **every** file, including large binaries: a single
  `src/` sweep exceeded a 520 s budget. It now filters to
  `TEXT_EXTS` by default, caps files at 2 MB, and reads on a 24-thread pool.
  Sweep time went from "times out" to **1–2 s**.

`sweep of src + scripts + tools + tests: 1261 files compared`

| status | count |
|--------|-------|
| IDENTICAL | 887 |
| DIVERGED | 161 |
| LOCAL_ONLY | 188 |
| WSL_SUPERSET | 13 |
| MIRROR_ONLY | 8 |
| LOCAL_SUPERSET | 4 |

### 1.3 What the drift actually was

For each candidate, the local-only lines were inspected **before** copying. The
rule applied: if every local-only line is merely an older form of a line the
mirror extends, the mirror is a superset in capability, not a rival edit.

Evidence that the local tree was the incomplete artifact, not the newer one:
`src/CORE/spine_registry.py` documents that disk restore happens on
`startup_warm.restore_spine_state` — a function that **did not exist locally**.
The tree referenced its own missing half.

### 1.4 Restored (byte-verified, `md5sum` equal on both sides)

Source:

| file | md5 after restore | why |
|------|-------------------|-----|
| `src/CORE/startup_warm.py` | `98247abfdd97685ce4a5342e23c56e16` | 381 → 613 lines: `restore_spine_state`, `start_spine_heart`, `stop_spine_heart`, `spine_heart_status`, `get_spine_restore_status` |
| `src/AOA/core/arm_registry.py` | `a53bc4217120b63805f0552f0f40ae5d` | `_ensure_arms_imported` / `_alias_core_package`; without it `kali_arm` never fires `@register_arm` |
| `src/CORE/secrets_manager.py` | `7daa78e238f561aa8215ecc8002a5adb` | the `__new__` singleton the class docstring already promised |
| `src/CORE/WORMS/expansion/nerve.py` | byte-equal to mirror | `_LazyTorch`; local kept the eager `import torch` |
| `src/CORE/WORMS/expansion/tensorgene.py` | `5d733d522dfca95bb022ff3d42595eb9` | `boruta_relevance` |
| `src/CORE/worm_registry.py` | `9d10af20d64365440f931281a84fbfb6` | `_STDLIB_ROOTS`; stdlib `random.Random` was being registered as a worm |
| `src/CORE/PamsRecorder.py` | `359fe8a12a72476918f25095919e0f62` | documents why `__new__` is NOT cached (two conflicting suites) |
| `src/CORE/audit_trail.py` | `dae28c4af9b8e052f8c2ef308f608c08` | `payload.pop("signature")` before hashing |

Tests (source-only restores are not reconciled until their coverage returns):

| file | delta |
|------|-------|
| `tests/test_startup_warm_wiring.py` | +82 |
| `tests/test_worm_registry.py` | +73 |
| `tests/test_full_integration.py` | +26 |
| `tests/test_provider_failover.py` | +23 |
| `tests/test_observability.py` | +22 |
| `tests/test_sb3_agent.py` | +19 |
| `tests/test_aoa_routing_telemetry.py`, `tests/test_cloud_tab_error_handling.py`, `tests/test_secrets_manager_thread_safety.py`, `tests/autodiff_skills_check.py` | +13 each |
| `tests/test_algorithm_coverage.py` | +12 |
| `tests/benchmark_autodiff_modes.py` | +10 |
| `tests/test_proteus_hooks.py` | +9 |
| `tests/test_boruta_relevance.py`, `tests/test_nerve_torch_import.py` | new |
| `src/CORE/qd_bridge.py` | new |
| `tests/test_spine_mesh.py`, `tests/test_pams_recorder.py` | corrected revisions (see 1.6) |

All 30 copies were `md5sum`-verified against the mirror and `py_compile`d.

### 1.5 Deliberately NOT restored

A superset is not automatically an upgrade. Three classes were excluded:

1. **The chain.** `run_azazael_chain.py` (mirror 842 lines vs local 303) and its
   tests. The chain was deleted on purpose and replaced by
   `scripts/chain_controller.py` ("Clean replacement chain controller for the
   current Azazael control plane"). Restoring the mirror's chain would have
   re-imported a superseded scheduler, and its refactor tests added 28 failures
   against a subsystem that is meant to be gone. Removed:
   `tests/test_chain_refactor.py`, `tests/test_chain_lock.py`.
2. **`scripts/run_full_pass.py`.** Its own deletion is recorded in the tree:
   `tests/test_track_registry_consumers.py:17` — "run_full_pass deleted
   2026-09-28 (forensic: phantom coverage, self-collision, stale
   architecture)". Removed after restoring it in error; the local marker is now
   the authority, and the mirror is the stale side.
3. **Tests whose subject exists in neither revision.**
   `tests/test_morphing_learn.py` needs `MAX_GENOMES` and
   `tests/test_session_operations.py` needs `build_next_task_scaffold`; a scan
   of `src/` in **both** trees found neither symbol. Restoring them would have
   imported two permanent collection errors, so both were dropped.

The WSL mirror is therefore a source of supersets **only for files that were
lost**, not a second source of truth. `DIVERGED` files with substantial
local-only content (e.g. `scripts/evolution_cycle.py`, `src/AOA/core/router.py`)
were left alone: those are live work, not loss.

### 1.6 Corrected revisions adopted for tests

Two test files were supersets in spirit but technically `DIVERGED`:

- `tests/test_spine_mesh.py` — the homeostat tests hard-coded `range(6)` while
  `HomeostatWorm.MIN_SAMPLES` was retuned to 8 (live) / 5 (fallback). The
  mirror's revision uses `MIN_SAMPLES + 1` and says so. Adopting it fixed two
  real failures.
- `tests/test_pams_recorder.py` — the singleton contract is `get_recorder()`,
  not `PamsRecorder()`; the mirror's revision tests the accessor. Adopting it
  fixed the third.

### 1.7 Result

`tests/test_spine_mesh.py` went 6 failed → 0. `tests/test_aoa_router_censored`
and the AOA arm-re-export assertions now see the restored registry.

Net effect measured on the affected files: 3 failures remained after the first
pass (2 homeostat + 1 Pams singleton), all three were test-revision gaps, and
all three are now green.

---

## Part 2 — The intermesh audit

### 2.1 What "intermesh" is

The audit that converts the wire-or-cut census (which functions nothing in
production names) into an **actionable plan**, by mapping each uncalled
capability onto the natures' own declared data contracts. It is the tool behind
`chain_controller.py`'s "2026-09-28 intermesh audit" note, and it renders
`NEURAL_MESH_INTEROP.mmd` — the only human-readable picture of the mesh.

Implementation: `tools/nature_integration_map.py` →
`NEURAL_MESH_INTEGRATION_MAP.json`, `NEURAL_MESH_INTEROP.mmd`,
`logs/capability_wiring_dataset.jsonl`.
Consumed by: `tools/refresh_all.py`, `tools/artifact_freshness.py`,
`tools/evolution_chain_audit.py`, `tests/test_mesh_wire_or_cut.py`.

Its premise, stated in its own docstring:

> `NATURE_DEFINITIONS` declares, per nature, what it EMITS, what it REQUIRES and
> which natures it FEEDS INTO ... so a consumer for a capability can be derived
> instead of invented.

### 2.2 What it was missing

Six gaps, each measured.

**G1 — 23 findings (22%) had no disposition at all.** Module-level functions hit
an early return with `disposition = "module_level"`, whose reason was that a
caller "needs [to be] decided per function, not per class". No consumer can act
on that, and the Mermaid emitter then skipped them
(`if item["kind"] == "module_level": continue`) — so a fifth of the backlog was
invisible in the one artifact meant to make it visible. Among them:
`spine_reset`, `get_gossip_trust_state`, `q_confidence`, `homeostat_reset`,
`audit_state`.

**G2 — the module→nature index could never match.** The census stores a short
module stem (`exmachina`); the registry stores `__module__`
(`CORE.WORMS.expansion.exmachina`). Fixed by keying on both. Modules mapped:
**94 → 188**.

**G3 — the dispositions were computed and thrown away.** The emitter built a
`style` value for every node and never used it: exactly **one** `classDef` was
emitted (`M`) and `C_wire` / `C_integrate` / `C_unresolved` were never attached
to any node, so wireable, orphaned and unresolved capabilities all rendered
identically. Per the Mermaid flowchart spec a class only takes effect when it is
BOTH declared with `classDef <name>` AND attached (`node:::name`, or
`class node name;`).

**G4 — "production" meant `src/` only.** `production_uses()` scanned `src/`, so
the schedulers and audit tools in `scripts/` and `tools/` were invisible as
consumers — even though they are the code that actually *runs*.
`get_gossip_trust_state` is called by `scripts/mesh_gossip_cycle.py` and still
landed in `unresolved`. Scan roots are now `src` + `scripts` + `tools`, and
every finding records `ref_scope` naming which root holds the referrer, so a
`src` referrer (library consumer) is distinguishable from a `scripts` one
(entry point).

**G5 — the data-contract half was never checked.** `emits`/`requires` are the
only evidence that can tell a real wiring from decoration — the
`SplitBrainResolverWorm.report_fork` failure the tool's own docstring cites
(a writer filled a box the reader never consulted). Nothing computed it, and
**only 4 of 26 natures declare a contract**, so for the other 22 the fields came
back as empty dicts that read as "clean". The plan now carries
`contract_coverage`, and the run prints it.

**G6 — the nature graph was partial.** `-.->|feeds|` edges were drawn only
between natures that happened to own a pending finding, so the inter-nature
picture looked sparse for a reason unrelated to the contracts. All contract
natures are now declared up front.

### 2.3 Before / after

| measure | before | after |
|---------|--------|-------|
| dispositions | `integrate_via_stage` 49, `module_level` **23**, `unresolved` 5, `wire_at_site` 26 | `integrate_via_stage` 43, `unresolved` 22, `wire_at_site` 38 |
| findings with no actionable disposition | 23 | **0** |
| modules mapped to a nature | 94 | 188 |
| `classDef` declarations in the graph | 1 | 4 |
| disposition classes actually applied to a node | **0** | 60 |
| `INTEROP.mmd` edges | 326 | 433 |
| contract coverage reported | no | yes (per nature + per unread field) |

### 2.4 What the corrected audit now says

```
natures with a declared contract : 4/26
no contract declared (22): backup, communication, config, consensus, container,
  engram, federated, immune, learning, mesh, migration, optimization,
  orchestration, profiling, repair, security, servemesh, synapse, sync,
  telemetry, visualization, xenomorph
declared-but-unread emits in diagnostic   affected, diagnosis
declared-but-unread emits in monitor      cpu_pct, disk_io, mem_pct
```

Two of those lines are the audit doing the job it was built for:

- **22 natures declare no contract**, which is why the derived-consumer rule
  falls back to `feeds_into[0]` for them. The declaration gap is now reported
  rather than passing as an empty dict.
- **`monitor` declares it emits `cpu_pct`, `mem_pct` and `disk_io`, and nothing
  in production names any of the three.** That is the "written but never read"
  (dead store) class, instantiated in this tree — the same shape as the
  `SplitBrainResolverWorm.report_fork` case that motivated the tool.

### 2.5 Regression guard

`tests/test_nature_integration_map.py` (14 tests, all passing) pins:

- a module-level capability with a production referrer is `wire_at_site`, one
  with a module nature but no referrer is `integrate_via_stage`, and one with
  neither is honestly `unresolved`;
- `module_level` never appears as a **disposition** again (only as a kind);
- `scripts`/`tools` are scanned and tagged by scope;
- undeclared contracts are named, and a declared-but-unread emit is reported;
- on the rendered artifact: every applied `:::class` was declared, each of
  `C_wire` / `C_integrate` / `C_unresolved` is both declared **and** attached,
  module-level capabilities appear as `D_` nodes, and the plan carries
  `contract_coverage`.

---

## Part 3 — Full suite baseline (#11)

Run: `tools/run_suite_chunked.py --out logs/suite_chunks_20260928c.json`,
8 chunks, 235 files, 600 s per chunk, wall **1202.6 s**.

### 3.1 The run itself was contaminated, and that matters

Two chunks reported `rc=4294967295` (0 passed, no output) and one timed out.
The cause was **me**: I ran per-file pytest loops in parallel with the suite, so
several interpreters wrote `.pyc` files into the same `__pycache__` while
others imported them. Re-running the affected chunks with nothing else running
settled it:

| chunk | whole-suite run | clean re-run | verdict |
|-------|-----------------|--------------|---------|
| 2 | TIMEOUT at 600 s | did not finish in 551 s | **real, unresolved** |
| 3 | `rc=-1` in 8.8 s | 485 passed, 9 failed, 165 s | contention |
| 5 | `rc=-1` in 47.1 s | 554 passed, 7 failed, 151 s | contention |

So the abort pattern is an artifact of concurrent runs, and chunks 3 and 5 are
both **faster and cleaner than the previous baseline** (chunk 3: 19 failed → 9;
chunk 5: 9 failed → 7).

### 3.2 Headline: chunk 4 no longer times out

| | baseline `20260928b` | this run |
|---|---|---|
| chunk 4 | **TIMEOUT at 600 s, 0 tests reported** | **556 passed, 4 failed, 338 s** |
| errors | 4 (2 collection) | **0** |
| failed (7 measured chunks) | 88 | **57** |
| passed (7 measured chunks) | 2311 | **3349** |
| wall | 1286.1 s | 1202.6 s |

Per chunk as measured (chunk 2 excluded, see 3.1):

| chunk | passed | failed | skipped | wall |
|-------|--------|--------|---------|------|
| 1 | 364 | 5 | 45 | 32.5 s |
| 3 | 485 | 9 | 5 | 165.0 s |
| 4 | 556 | 4 | 1 | 338.1 s |
| 5 | 554 | 7 | 0 | 151.0 s |
| 6 | 509 | 15 | 26 | 62.6 s |
| 7 | 498 | 2 | 2 | 64.3 s |
| 8 | 383 | 15 | 0 | 49.2 s |
| **total** | **3349** | **57** | **79** | ~863 s |

Two caveats stated plainly. First, the failure count is not directly
comparable to the old 88: chunk 2's 17 failures are missing from the new number,
and the restores added roughly 300 previously-absent tests. Second, `passed`
rose partly because chunk 4 now reports at all.

The honest claim is narrower and still strong: **the suite completes, errors are
zero, and the two largest frozen chunks (3 and 5) improved.**

### 3.3 Open items

1. **Chunk 2 needs >551 s against a 204.6 s baseline — a 2.7x slowdown that is
   not explained.** It is the single highest-priority item. It is NOT the
   psutil/service-probe defect (that is fixed and measured), so it is either new
   work in this window or contention from the other agent working concurrently
   in the same tree. Both `test_cloud_tab_error_handling.py` (restored) and
   `test_cluster_integration_p1.py` sit in it. A clean differential run — same
   chunk, HEAD sources vs current — is the next step, and it has to be run with
   no other interpreter active or it will measure the machine instead of the
   tree.
2. **Batch-only interactions.** Several files pass individually but hang or
   error when sharing one pytest process (e.g. `test_startup_warm_wiring.py`
   followed by `test_worm_registry.py`). Not root-caused; the chunked runner
   contains the blast radius by design.
3. **Do not run pytest concurrently with the suite.** The `rc=-1` aborts in
   3.1 are reproducible that way, and they poison any baseline they touch.
4. **`DIVERGED` files with real local-only work** remain unreconciled by design
   (`scripts/evolution_cycle.py` −54/+673, `src/AOA/core/router.py` −237/+496,
   `src/CORE/WORMS/CLUSTERWORMS.py` −161/+263, `scripts/sync_all.py` −28/+327,
   `scripts/live_monitor.py` −15/+193, `tests/test_brainstem_playing_field.py`
   −3/+216). Each needs a per-file merge decision; the drift report lists them.
5. **The `unresolved` 22** are now honest but not actionable: 5 are
   `class_unregistered` and 17 are module-level functions whose module the
   registry attributes to no nature. Either the registry should register those
   modules or the functions are genuinely cuttable.
6. **The remaining 57 failures are untriaged.** The largest clusters were not
   worked this session (`test_cluster_integration_p1.py` 8 — `_WatchdogThread`
   and `_dm` no longer importable from `CORE.WORMS.CLUSTERWORMS`,
   `set_partial_failure_threshold`/`overall_status` gone;
   `test_freethreadedagent.py` 6; `test_spawn_decision.py` 6). The first three
   look like an API refactor whose old tests survived, which is the same
   stale-test-vs-refactor shape as the homeostat and Pams cases in 1.6.

---

## 5. Execution-boundary deadlock — the real cause of the chunk-2 "regression"

Section 3 above flagged chunk 2 as needing >551 s against a 204.6 s baseline
(2.7x) and called it **unexplained**. It is now explained, and it was not a
slowdown at all — it was a **self-deadlock that never returned**.

### 5.1 The finding

A per-file timing sweep of chunk 2's 30 files isolated three slow files, and
the worst (`test_cluster_integration_p1.py`) never finished at all:

| file | before | after |
|---|---|---|
| `test_cluster_integration_p1.py` | never completed (261 s cap hit, 13 dots then stuck) | 48 s, 21 passed |
| `test_clusterworms_unit.py` | 51 s (not broken, just slow) | 51 s |
| `test_cross_nature_orchestration.py` | 51 s (not broken) | 51 s |

Two stack dumps pinned it. `faulthandler_timeout=45` on the single test shows
one frame chain only:

```
  File "src/CORE/WORMS/CLUSTERWORMS.py", line 1027 in execute_all
  File "tests/test_cluster_integration_p1.py", line 317 in test_direct_memory_record_called_on_execute
```

The test body holds the lock and then calls into code that takes it again:

```python
# tests/test_cluster_integration_p1.py
with _dm_lock:            # line 308 -- acquired by this thread
    cw._dm = mock_dm
    cluster.execute_all() # line 317 -- which does `with _dm_lock:` (line 1027)
```

And the lock was non-reentrant:

```python
_dm_lock = threading.Lock()   # src/CORE/WORMS/CLUSTERWORMS.py:47
```

Same thread, same lock, second acquisition: a permanent hang. The audit trail
had also narrowed it earlier in the investigation:

```
$ git blame -L 1020,1032 --date=short src/CORE/WORMS/CLUSTERWORMS.py
000000000 (Not Committed Yet 2026-09-28 1027)             with _dm_lock:
```

So the `_dm` / `_dm_lock` machinery in `execute_all` was **uncommitted** when the
baseline ran — which is why the baseline recorded 17 chunk-2 failures at 204.6 s
faster than these three files can even run. The regression was introduced
between the baseline and the re-measurement, not by the reconciliation.

### 5.2 The fix

`_dm_lock = threading.RLock()`. RLock keeps the property the lock exists for
(cross-thread exclusion of the `_dm` snapshot) while making the documented
re-entrant call legal. Verified:

```
$ pytest tests/test_cluster_integration_p1.py::test_direct_memory_record_called_on_execute
1 passed in 3.17s          # was: hung, killed at 100 s wall
```

### 5.3 Chunk 2 result

| | baseline | now |
|---|---|---|
| wall | 204.6 s | 221 s |
| passed | 504 | **530** |
| failed | 17 | **0** |
| skipped | 2 | 3 |

The identical wall clock with 18 more passing tests is the signature of a
removed hang rather than a real speed-up.

### 5.4 The other five chunk-2 failures (all triaged, all fixed)

| test | verdict | fix |
|---|---|---|
| `test_delegation_ask_owner.py` x3 | **missing feature** | `WormExecutor._execute_direct()` and `NatureCluster._run_worm_method()` now catch `NeedsClarification` / `ClarificationTimeout` and normalise them into `needs_input` / `timed_out` outcome rows instead of letting the ask surface as a generic crash. The question and `decision_id` survive, so the ask stays joinable to the choice log. |
| `test_colour_queens.py::test_quarantine_gate_holds_a_worm_out_of_the_pipeline` | **missing enforcement** | `NatureResult.quarantined_skipped` added; `NatureCluster.execute()` now consults the spine quarantine store and removes gated worms from the target list. |
| `test_colour_queens.py::test_black_force_channel_is_audited_and_effective` | **missing enforcement** | `NatureResult.retired_skipped` added; `execute()` also holds out worms whose registry `lifecycle_state == "retired"`. A retirement written to the registry is a claim; enforcing it at the execution boundary is what makes it true. Reported separately from quarantine because a hold is temporary and a retirement is permanent. |
| `test_colour_queens.py` (same test, first failure) | **real bug** | `mark_spawned()` did `WORM_REGISTRY[w]["spawn_count"] += 1`, which raised `KeyError` for any entry lacking the key — the only state in which it is ever called. Its sibling `get_unspawned_worms()` already read the key defensively; now so does this. |
| `test_cross_domain_integration.py::test_cd3_otel_tracing` | **optional extra** | `opentelemetry` is not a declared dependency. Now `pytest.importorskip(...)`, matching the `mygrad` treatment. |
| `test_command_center.py::test_web_cache_reuses_one_snapshot` | **missing function** | `scripts/live_monitor_web.py` had no `collect_snapshot()` / `snapshot_cached()`; every `/api` request opened its own SQLite connection and re-ran the full collect, so N open browser tabs drove N full collections per interval. Both functions added and `do_GET` now serves through the TTL cache. |

---

## 6. The "dodecahedron milestone" — what the search actually found

### 6.1 Result of the search: no such framework exists

Searched and found nothing usable as an engineering milestone:

* `"dodecahedron milestone"` (exact) returns a **LEGO Ideas product page** whose
  only relation to the phrase is the words "Milestone missed".
* `"dodecahedron" software architecture milestone project` returns sacred
  geometry, Euclid's construction, Archimedean-solid history and a bridge-scour
  sensor project. No software framework.

There is no established engineering artifact called a "dodecahedron milestone".
Reporting one by inventing a definition would have been the confidently-wrong
artifact this session already had to catch twice (see 6.3).

### 6.2 What IS applicable: the Twelve-Factor App (12 faces)

The nearest real 12-facet architecture framework is the **Twelve-Factor App**
(12factor.net, Heroku, 2011) — twelve factors, i.e. a 12-sided solid. It is
genuinely applicable to this project, so rather than assert that, the claim was
made measurable: `tools/twelve_factor_audit.py` audits the tree and reports each
face as `pass` / `partial` / `gap` / `manual`, writing
`TWELVE_FACTOR_AUDIT.json`.

`manual` is a first-class verdict: factors VI (stateless processes) is a runtime
property a static scan cannot decide, so it is reported unmeasured and is
**never counted as passing**. Result on this tree:

```
Twelve-Factor audit -- 11/12 faces solid, 1 open
1  Codebase          pass     1 mirrored file byte-identical (drift risk, not a defect)
2  Dependencies      pass     3 manifests, 237 pinned requirements
3  Config            pass     env-driven + declarative sample (.env.example)
4  Backing services  pass     no hardcoded credential literals
5  Build/release/run pass     5 build artifacts, 1 entry point
6  Processes         manual   runtime property; not decidable statically
7  Port binding      pass     22 bind sites, 3 from environment
8  Concurrency       pass     409 thread sites, 31 process sites
9  Disposability     pass     25 signal sites, 4 atexit handlers
10 Dev/prod parity   pass     237 test modules sharing project config
11 Logs              pass     14347 stream sites vs 8 file handlers
12 Admin processes   pass     2 admin entry points
```

### 6.3 The one real gap it found, and three false positives it nearly shipped

**Gap:** Factor III was `partial` — 468 environment reads with **no
`.env.example`**. The app was configuration-complete but operationally
undiscoverable: nothing in the tree told a new operator which variables exist.
Fixed by generating `.env.example` from the names the code actually reads
(`--write-env-example`), so the sample cannot silently drift from reality.

**Three false positives, each caught by validating the probe rather than the
verdict — this mattered more than the audit itself:**

1. *"8 hardcoded credential literals"* -> the real answer is **zero**. They were
   `api_key = "anonymous"`, a deliberate scanner fixture
   (`invalid_code_secret` in `enforcement_harness.py`), and a vendored Jinja2
   lexer (`token = 'block_begin'`) inside `archived/` and
   `nuitka_build_backup/`. The probe was counting frozen snapshots and upstream
   vendored code as application secrets.
2. *"scripts & src/SCRIPTS share filenames"* -> just `__init__.py` plus
   `monitor_learning.py`, a **deliberately** byte-identical mirror. Overlap is
   not drift; the probe now compares hashes and reports `gap` only on real
   divergence.
3. *First draft of `.env.example` was polluted* -> it scraped
   `archived/2026-05-31/onnxruntime-*` and emitted `AZURE_BLOB_SAS_TOKEN`,
   `BROWSERSTACK_TOKEN`, `JAVA_PGP_KEY` (upstream CI variables that are not this
   project's configuration) and leaked absolute `C:/Users/...` paths into a
   file destined for the repo. Both fixed; the artifact now has 0 absolute
   paths and 0 upstream variables.

A fourth defect was in the scanner's own file-selection: it tested the
substring `"test_"` against the whole path, which skipped unrelated files whose
names merely contain it and skipped every file under a pytest `tmp_path`
(named after the running test). Now matched structurally against test
*directories* and test *filenames*.

`tests/test_twelve_factor_audit.py` pins all of the above (19 passing),
including a **negative control** proving a real `ghp_...` token is still
reported. An exclusion rule that swallows everything is as wrong as one that
catches nothing, and only a negative control distinguishes them.

---

## 7. Corrections to earlier sections of this document

* **Section 3 is wrong about chunk 2.** "Chunk 2 needs >551 s against a 204.6 s
  baseline (2.7x)" — the true cause was the deadlock in 5.1, and the chunk is
  now 221 s with **0** failures. Also, "it is not the psutil defect — that's
  fixed" was correct but incomplete: the psutil fix and the deadlock were two
  different problems in two different chunks.
* **Section 4.6 is now partly stale.** Of the failures listed as untriaged,
  `test_cluster_integration_p1.py` (8) is fixed and green. The
  `_WatchdogThread` / `_dm` diagnosis there was a symptom of the same
  uncommitted `CLUSTERWORMS.py` edit.
* **The `DIVERGED` note in section 4.4 needs amending for
  `src/CORE/WORMS/CLUSTERWORMS.py`.** It was listed as "−161/+263 uncommitted
  local-only work awaiting a merge decision". It is no longer merely awaiting a
  decision: it contained a production self-deadlock, which is why it was fixed
  here rather than merged later.

---

## 8. Spine heartbeat leak, and the fresh baseline (2026-09-29)

### 8.1 The two "remaining" test_spine_mesh failures were flaky, not failing

They pass alone (63 passed) and pass on a re-run of the same four-file batch
(120 passed, 40 skipped). A first per-file sweep had capped each file at 40 s,
which made them look like hangs, so the next step was to stop assuming a fixed
failing set and find what made them intermittent.

`test_spine_cycle_throttle_and_reentry_guard` asserts that a second immediate
cycle is throttled with `skipped == "min_interval"`. That check sits *after*
the process-global cycle gate in `run_cycle()`. If a heartbeat already holds
that gate, the first cycle returns `skipped:
"cycle_already_running_global"` instead of running, so it never sets
`last_run_at`, the second call is not throttled, and the assertion sees `None`.

The heartbeat comes from the code this session restored: `startup_warm.py`
line 268 calls `start_spine_heart()`, which starts a daemon thread beating on
its own interval for the remainder of the session. `test_startup_warm_wiring`
triggers a synchronous warm, so `test_spine_mesh` inherits a live heartbeat.

Three-way control, run directly:

| control | global gate | cycle result |
|---|---|---|
| no heart | free | `skipped = None` (ran) |
| heart started | **held by a beat** | **`cycle_already_running_global`** |
| heart stopped | flag False | `skipped = None` (ran) |

Fix: an autouse `_quiesce_spine_heart` fixture in `tests/conftest.py` that
stops the heart after each test. It is teardown-only (the leak is created *by*
a test), and it reuses `stop_spine_heart()`, which already waits for an
in-flight beat. This is the same shape as the existing `_isolate_hlc_clock`
fixture: a process-wide singleton leaking across tests and making the failure
order-dependent. Cost is zero for the ~2000 tests that never start a heart.

Pinned by `tests/test_spine_heart_isolation.py` (3 passing). Its first test
starts a heart and asserts it beats; the second asserts it is already gone. The
second can only pass if the fixture works, so it cannot pass by accident.

### 8.2 Fresh baseline

`tools/run_suite_chunked.py --out logs/suite_chunks_20260928d.json`:

| | prior baseline (b) | fresh (d) |
|---|---|---|
| passed | 2311 | **3918** |
| failed | 88 | **57** |
| errors | 4 | **0** |
| skipped | 5 | 82 |
| wall | 1286 s + 1 chunk timed out | **1442.6 s, no chunk timed out** |

Per chunk: 1=39.7s, 2=271.4s, 3=199.6s, 4=327.1s, 5=268.4s, 6=132.7s,
7=131.2s, 8=72.6s. Chunk 2 is green (530 passed, 0 failed). Chunk 4, which
timed out at 600 s on the old baseline with zero tests run, now completes in
327 s with 569 passed.

The passed count rose 2311 -> 3918 mainly because this session restored 21
test files. The 82 skips are up from 5 and are worth a look: they are optional
-extras guards (`mygrad`, `opentelemetry`) plus environment-gated tests, so
"skipped" now hides more than it used to.

The 57 remaining failures are concentrated: chunk 8 has 15, chunk 6 has 15,
chunk 3 has 9, chunk 5 has 7, chunk 1 has 5, chunk 4 has 4, chunk 7 has 2.

### 8.3 Restoration attribution: could not be done reliably

All 8 followups were requested; the attribution step did not produce a
committable answer and pretending otherwise would have been worse than saying
so.

The intended signal was "byte-identical to the WSL mirror" -- files restored
verbatim should match it exactly. But that is also true of every file nobody
touched on either side, so it cannot separate my restorations from the
pre-existing untracked backlog. Measured: **157 untracked files are
also mirror-identical**, far more than the ~30 files actually restored this
session. Committing that set would have staged 157 files of unknown provenance
under a message claiming they were recovered.

The three source files that *could* be attributed by name and by the specific
failures they close were committed separately (`73ee26af`). The remaining
restorations stay in the working tree pending a real attribution signal (the
mirror's own git index, or mtime correlation across a snapshot).

Two useful numbers did fall out of the attempt:

* **5 files are still MIRROR_ONLY** -- `scripts/run_full_pass.py`,
  `tests/test_chain_lock.py`, `tests/test_chain_refactor.py`,
  `tests/test_morphing_learn.py`, `tests/test_session_operations.py`. Every
  one of these is a **deliberate** deletion (the chain removal and
  `run_full_pass.py`'s documented 2026-09-28 removal), not an accidental loss.
  The mirror is simply stale for them, which is the desired end state.
* **4 files are LOCAL_SUPERSET**, i.e. local has work the mirror lacks. Those
  are the only candidates worth syncing *to* the mirror; the direction of the
  next sync is not uniformly one way.

Overall drift on the last sweep: IDENTICAL 906, DIVERGED 158, LOCAL_ONLY 192,
MIRROR_ONLY 5, LOCAL_SUPERSET 4.

### 8.4 The dodecahedron rendering was attempted and NOT shipped

Rendering the twelve faces as a projected solid was implemented and then
reverted, because the geometry could not be validated.

Two approaches both produced a wrong shape, and both were wrong in the same
way -- they assumed an answer instead of measuring one:

1. Assuming the face normals were the 12 cyclic permutations of
   `(0, +-1, +-phi)` and taking each normal's top-5 vertices by dot product.
   Those are not the face normals of this vertex set, so the "nearest 5" hit a
tie and vertices ended up shared by 1, 2 and 6 faces instead of 3.
2. Deriving faces from nearest-neighbour corner triples. At a dodecahedron
   vertex the three neighbours are the DIAGONALS of the three pentagons meeting
   there, so a mutual-adjacency requirement rejected all 60 triples and
   produced zero faces.

A brute-force plane search then appeared to work (12 faces, 5 vertices each,
120 triples at C(5,3)=10 per face) but its incidence was wrong: the 12 faces
used only **12 of the 20 vertices, each in 5 faces**, not 20 vertices in 3.
Tightening the tolerance to 1e-12 did not change it, so those planes are not
this solid's faces.

Since the only thing verifying the picture was the picture, the renderer was
reverted rather than shipped with the solidity claim. The face data remains
available in `TWELVE_FACTOR_AUDIT.json`, and `_dodeca_geometry` is not called
by any remaining code path.
