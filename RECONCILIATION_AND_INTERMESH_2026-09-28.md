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

### 8.5 Restoration attribution: solved, and it supersedes 8.3

The signal that works is the mirror's OWN git index, not file content.

```
local   git ls-files                     -> 31354 tracked
mirror   git -C .../root/azazael ls-files ->  1458 tracked
mirror-tracked but NOT tracked here      ->    52
of those, existing on disk AND code      ->     2
```

Those two are the entire attributable set:

| file | md5 (identical both sides) |
|---|---|
| `src/CORE/logging.py` | `48477f4083a1164ba51b320a4d9ac459` |
| `tests/test_error_recovery.py` | `27caf467ff338eba4186020117f81abd` |

The other 50 are CODEX/OUTPUT `.mp4` renders, the compliance DB, `src/scripts`,
and temp files -- mostly absent locally or irrelevant. Committed as `efb76b61`;
27 tests pass across `tests/test_logging.py` + `tests/test_error_recovery.py`.

8.3's byte-identity-with-mirror signal was measured invalid and is retracted:
157 untracked files are also mirror-identical against roughly 30 files that were
actually restored, so identity is not provenance. Identity says "this content
exists in both" (true of every vendored copy); the mirror's index says "this path
was version-controlled over there and is not over here", which is the question.

`src/CORE/logging.py` is reachable only as `CORE.logging`, so it does not shadow
stdlib `logging`. One caveat worth recording: `tests/test_curative_pool.py:12`
puts `src/CORE` on `sys.path`, which WOULD make `import logging` resolve to this
file if stdlib `logging` were not already in `sys.modules`. Pytest imports it
first, so the shadowing is masked rather than impossible.

---

## 9. Triage of the 57 failures and the 82 skips (2026-09-29)

### 9.1 The single dominant cause is another agent's in-flight file

`src/AOA/core/router.py` in this checkout is 418 lines and has **no**
`RoutingPolicy`, **no** `select_arm`, and **no** `capability_index`. The WSL
mirror's copy is 678 lines and has all three. `tests/test_aoa_elastic_routing.py`
was edited on 2026-09-28 to add a **whole-module** skip, strip `RoutingPolicy`
and `ARM_ROUTE_NATURE` from its imports (stubbing the latter as the literal
`"quartet"`), and to add a `censored=` kwarg the router does not accept.

That is a deliberate redesign by the concurrent agent (the file shows as ` M`),
not a regression, and it must not be reverted from here. Its blast radius:

| outcome | tests |
|---|---|
| `test_aoa_router_censored` | 3 failing (`capability_index`) |
| `test_aoa_routing_telemetry` | 2 failing (`CrossArmRouter`) |
| `test_mesh_transport_e2e::test_router_learns_only_learnable_outcomes` | 1 failing (censoring) |
| `test_aoa_elastic_routing.py` | **40 skipped** by the module skip |

**46 of the 139 non-passing outcomes in the suite trace to this one file.**

### 9.2 Fixed (19 failures, 4 commits)

| commit | failures fixed |
|---|---|
| `f6b938b7` monitor helpers restored from the mirror (`max_rows` NameError, `LOG_MAX`/`append_log`, `_ex_now`, `_control_line` x3) | 9 |
| `4d79cb52` registry tests read `WORM_REGISTRY` instead of `discover_worms()`'s delta; canonical `VALID_CATEGORIES`; `SLOW_WORMS` module resolution | 7 |
| `3e72236e` `NeuralPipeline.replay_failed` executor contract | 3 |

The monitor helpers were not reinvented: the mirror still carried every one, so
they were restored from that reference. Note `_paint_in_place` read `max_rows`
-- a name defined NOWHERE in the module -- so every live paint raised NameError
and the window crash-looped while `--once` stayed green. A test existed for it
and the break had still shipped.

### 9.3 Attributed to concurrent work (14 failures)

| source (shows ` M`) | failing tests |
|---|---|
| `src/AOA/core/router.py` | 6 (9.1) |
| `src/CORE/WORMS/expansion/learning_rl.py` | 8 -- `test_policy_advice` 4 (`RLTrainLoop.recommend`), `test_replay_path` 3 (`train_from_memory(use_replay=...)`), `test_learning_evolution` 1 (GRPOPTUNE vs ALLPAR) |

### 9.4 Still open (24 failures), by assertion class

- **Missing module attribute** (7): `test_terminal_monitor_controls` is fixed, but
  `test_policy_advice` (`DatabaseMonitorWorm._policy_advice`) shares its class;
  `exmachina_mutagen` (float drift `158.8313808 != 158.8314559`), `local_memory`
  (`DID NOT RAISE RuntimeError`), `postgres_memory` (`'psycopg2' not found in []`),
  `versioner_write_on_change` (`assert 3 == 1`), `training_orchestrator`
  (`registry_category`).
- **Algorithm/rotation authority** (5): `track_registry_consumers` 3,
  `mesh_fabric_followups` 1 (`servemesh` vs `variation`), `servemesh_filter` 2
  (`env_error must arrive CENSORED`).
- **Decision/threshold logic** (5): `meta_escalation` 2 (`KeyError: 'tie'`),
  `morph_bypass` 2, `operator_scoring` 1 (`assert 0 > 0`), `plateau_persistence` 1.
- **Environment/artifact gates** (4): `request_auth` 2, `parallax_validator` 1
  (`.audit/gate_tokens/wrong_target.py.token`), `type_check_gate` 1 (committed
  baseline counts `error: 113` vs `error: 119`), `monitor_verdict_accuracy` 1
  (a 3-vs-5 arm count + a giant HTML diff from a redirected store).
- **Engine API** (2): `eve_unleashed` (`assert 'auto' == 'cpu'`;
  `FileNotFoundError: Model not found: fake.pt`).

None of these is a same-thread hang or a silent pass, so there is no equivalent
of the chunk-2 deadlock hiding here.

### 9.5 Why the skip count went 5 to 82 -- and what it hides

The 5-skip baseline (`suite_chunks_20260928b.json`) is NOT comparable: that run
had chunk 4 time out at 600 s with **zero** tests and 4 collection errors,
reporting 2311 passed against 3918 now. The suite gained +1607 passing tests
alongside the +77 skips, so this is not previously-running coverage going dark.

The 82 skips decompose exactly (measured with `-rs`, chunks 1 and 6 directly and
the remainder via a skip-construct-filtered run):

| n | cause | verdict |
|---|---|---|
| 40 | whole-module skip, `test_aoa_elastic_routing.py` | **hides a whole file** (in-flight redesign) |
| 24 | `psycopg2` not installed | honest; the Postgres backend is untested here |
| 5 | `CircuitBreaker` `error_rate` unimplemented | honest feature gap |
| 4 | whole-module skip, `test_era_windows.py` (pool-era rotation) | **hides a whole file** |
| 3 | `opentelemetry.sdk.trace` absent (`importorskip`) | honest; SDK genuinely missing |
| 2 | `Circuit breaker enabled - retry loop not active` | honest |
| 1 | live inference providers (needs `AZAZAEL_LIVE_NETWORK=1`) | honest |
| 1 | `mygrad` absent on the free-threaded build | honest |
| 1 | mesh artifact predates the ledger it checks | honest freshness gate |
| 1 | uncaptured | -- |

So the answer to "does any skip hide real coverage" is **yes, twice**: 44 tests
live behind two whole-file `pytestmark = pytest.mark.skip` marks, both written as
"skipped, not deleted: spec preserved". The 40 is the AOA redesign; the 4 is the
unimplemented pool-era rotation. Everything else is an absent dependency or a
documented unimplemented feature, and `psycopg2` being absent means the entire
Postgres memory backend has no coverage on this host.

Evidence files: `logs/chunk1_skips.txt`, `logs/chunk6_skips.txt`,
`logs/rest_skips.txt`, `logs/failed57.txt`, `logs/fail_lines.txt`.

---

## 10. Failure-triage batch 1 (2026-09-29)

Batch 1 was the scoped run of the 24 open cases: **15 failed / 140 passed**
(`logs/open_batch1.txt`). All 15 are now dispositioned: **13 fixed**, **2 attributed
to another author's in-flight work**. Re-runs across every touched file: 123
passed, 0 failed.

### 10.1 Fixed (5 commits)

| commit | fix | failures |
|---|---|---|
| `ab6d4921` | gate tokens could never verify (below) | 2 + 2 |
| `1763e25c` | `reasoning_overhead` declared and applied (below) | 1 |
| `16833a04` | `skipped_unresolvable` reported; fabric-stage set guard; `causal_emergence` `tie` | 4 |
| `910f254d` | versioner write-on-change; `training_plateau` persisted | 2 |
| `1a4bdbcd` | `load_model` validates the framework before the path | 2 |

The two counts above the table are `request_auth` (2) plus `parallax_validator`
(1) grouped under one cause, and `meta_escalation` (2) grouped under
`16833a04`'s `tie`.

### 10.2 Two production defects found while triaging tests

Neither was a test defect, and both sat behind a test that could not pass:

**The gate token could never verify.** `_ED25519_AVAILABLE` was initialised to
`False`, which the "already tried and failed -- don't retry" guard cannot tell
apart from "never tried", so `_get_ed25519_key()` returned `None` on its first
call and the whole `try:` block -- key load AND key generation -- was
unreachable. Ed25519 was never used. The BLAKE2b fallback then signed
`blake2b(payload + os.urandom(16))` and returned the salt inside the signature,
so a verifier recomputing the digest generated a *different* salt and never
matched: `is_token_valid()` returned `False` for every token. That is a
deny-everything gate, not a cosmetic failure. Fixed by making the flag tri-state
and deriving the salt from the payload -- which also keeps the 3-part
`blake2b:<digest>:<salt>` shape `parallax_validator.verify_token` parses, so the
daemon's check still agrees.

**A reasoning model's cap had no budget for its thinking.** The local
llama-server entries document that chain-of-thought goes to `reasoning_content`
and `content` stays EMPTY until it ends, so an unpadded cap is spent on thinking
and the turn reads as blank. `reasoning_overhead` existed only as a name read by
`azazael_operator_task.py` (outside this project), whose docstring claimed
`providers.py` pads `max_tokens` by it -- which was false: no such field or pad
existed anywhere in `src/`. Declared it on the qwopus entry and applied it in
`OpenAIProvider._default_max_tokens()`, used by `chat()` and `chat_stream()`. An
explicit caller cap is never padded.

### 10.3 Attributed, not fixed -- another author's in-flight port

`tests/test_morph_bypass.py` (untracked) requires `lr_ep0` / `lr_ep15` /
`lr_ep30` to be in the round-robin candidate pool, and the 2 failures are real:
the local pool holds only the 2 switch genes, so no novel candidate can exist.
The feature exists in the **mirror** (`proteus_hooks.py` carries the 3 schedule
genes, `learning_rl.py` carries `lr_ep0/15/30` and builds `lr_schedule` from
them) but not in this tree -- and neither in `HEAD` (`git show
HEAD:...learning_rl.py` has 0 occurrences). Both files are modified in the
working tree by the concurrent author, so this is a mid-port state: **reported,
not touched.** Adding the genes locally without the trainer kwargs would make
`morph_trainer_kwargs` pass `lr_ep*` to a signature that does not accept it.

### 10.4 Running tally of the original 57

| disposition | count |
|---|---|
| fixed in the earlier session | 19 |
| fixed in this batch | 13 |
| attributed to the concurrent author's in-flight files | 4 |
| still open | 21 |

The 4 attributed are `test_morph_bypass` (2, above) and `test_aoa_router_censored`
/ `test_aoa_routing_telemetry` (2), which need `src/AOA/core/router.py` -- 418
lines here against 678 in the mirror, missing `RoutingPolicy`, `select_arm` and
`capability_index`. Nothing has been staged from any file another author has open.

---

## 11. Fresh baseline and triage batch 2 (2026-09-29)

### 11.1 The baseline moves

| | passed | failed | errors | skipped | wall |
|---|---|---|---|---|---|
| `20260928d` | 3918 | 57 | 0 | 82 | 1442.6 s |
| `20260929e` | 3965 | 25 | 0 | 82 | 1105.7 s |
| delta | **+47** | **-32** | 0 | 0 | **-337 s** |

Per chunk (passed / failed / skipped / wall): 1: 364/5/45/27.7 s -- 2: 525/0/3/238.9 s
-- 3: 496/1/5/130.6 s -- 4: 564/3/1/364.5 s -- 5: 575/3/0/168.4 s -- 6: 525/8/26/62.8 s
-- 7: 503/0/2/63.3 s -- 8: 413/5/0/49.5 s. Chunks 2 and 7 are fully green; chunk 6 is
the only one still in double digits, and chunk 1's 5 failures are all AOA router.
Skipped is unchanged at 82, so the whole gain is real execution, not more skipping.

Report `logs/suite_chunks_20260929e.json`, log `logs/suite_run_20260929e.log`,
failure IDs `logs/failed_next.txt`.

### 11.2 The 25, by disposition

| disposition | count |
|---|---|
| fixed here (below) | 3 |
| attributed to the concurrent mirror port | 14 |
| still open | 8 |

The 14 attributed are not one cause but one shape -- **the feature exists in the
mirror and nowhere in this tree**, measured directly:

| failures | what the mirror has, this tree does not |
|---|---|
| `test_aoa_router_censored` (3), `test_aoa_routing_telemetry` (2) | `src/AOA/core/router.py` (418 lines here, 678 there) |
| `test_policy_advice` (4), `test_replay_path` (3) | `RLTrainLoop.recommend` + `use_replay` (mirror: 3 occurrences; local working tree: 0; `HEAD`: 0) and `db_monitor.py`'s `_policy_advice` (mirror has it, this tree has no file containing the name) |
| `test_morph_bypass` (2) | the `lr_ep0/15/30` schedule genes |

`src/CORE/WORMS/expansion/db_monitor.py` is CLEAN in this tree, so the
`_policy_advice` half could be ported -- but its tests also need
`RLTrainLoop.recommend`, which lives in the file another author has open, so
porting half of it would build the same kind of broken seam the morph genes
would. Both are reported, not touched.

The 8 open are `test_exmachina_mutagen` (1), `test_learning_evolution` (1),
`test_mesh_transport_e2e` (1), `test_track_registry_consumers` (3),
`test_training_orchestrator` (1) and `test_type_check_gate` (1). The last compares
a committed baseline count against live measurement (119 vs 113 errors) and is
expected to move while another author edits the tree; the track-registry trio and
`test_training_orchestrator` all concern the same track table (`GRPOTUNE` vs
`ALLPAR`, 144 vs 171), so they are one cluster worth doing together.

### 11.3 Fixed here (2 commits)

**`KaliArm` was missing from `arms/__init__.py` again.**
`src/AOA/test_arm_exports.py` documents this exact omission as found and fixed on
2026-09-14 -- and its own docstring still reports the fix as in place while the
import is absent. That test is under `src/`, and the suite runs `tests/`, so
nothing executes it; `tests/test_monitor_verdict_accuracy.py` found it instead as
`not_reexported == ['kali_arm']`. The omission is functional: `@register_arm`
fires only on IMPORT, so an unexported arm never enters `ARM_REGISTRY`, cannot be
pinned by id and is invisible to capability routing -- and KaliArm registers one
capability per mapped tool, the largest such surface in the system.
`test_arm_exports.py` is green again (3/3, including the `KALI_TOOLS` count and
the capability-per-tool shape).

**Two tests that could not fail on this host.**
`test_import_error_without_psycopg2` asserted `"psycopg2" in (sys.modules if
_HAS_PSYCOPG2 else [])` -- membership in the empty list exactly when psycopg2 is
absent, which is this host. Its body comment ("This test always passes") was the
false belief that kept it; it now asserts the ImportError
`PostgresMemoryStore.__init__` actually raises, and its message.
`test_backup_raises_on_bad_path` targeted `/proc/self/...`, arguing that /proc
denies writes even as root -- correct on Linux and toothless on Windows, where
that is an ordinary path on the current drive: the backup SUCCEEDED and the test
left a real 110 KB backup database **outside the repository** on every run
(reported, not deleted -- it is outside the project). It now uses a path whose
parent is an existing file, which cannot be created on any platform.

Running total, counted against the original 57 and reconciled with the current
25-failure baseline: 19 + 13 + 3 = **35 fixed**, **14 attributed** (the AOA router
5, the policy/replay 7, the morph genes 2), **8 open**. The attributed count is
larger than batch 1's 4 because three of those clusters were still classified as
"open" then and were proved to be mirror-only here by direct measurement.

# 11. Web-search papers wired into the intermesh (2026-09-29 addendum)

Three papers researched 2026-09-28/29, none previously referenced anywhere in
the tree (verified: zero hits for all three arXiv ids before this addendum).
Each maps to one concrete intermesh mechanism with file:line hooks. Status is
stated per paper: SEED means the first hook landed, GATE means the enforcing
mechanism is still open.

## 11.1 PivoARL — pivotal-aware credit (`arXiv:2607.03702`, Guo et al.)

Pivotal-Aware Self-Feedback Retry: failed trajectory → structured reflection
finds the pivotal erroneous turn → local retry from that state, reusing the
correct prefix. Pivotal-aware credit rewards the correct prefix and isolates
the erroneous suffix (+11.5% Pass@2/3 over MetaRL, +45% over GiGPO on
Minesweeper, −42% turns vs full retry).

Intermesh mapping (credit path):

| hook | file:line | status |
|---|---|---|
| `decision_id` join key minted | `src/CORE/WORMS/expansion/spawn_credit.py:293` | DONE (pre-existing) |
| `decision_id` threaded through Cluster/CONCURRENCY emitters | `src/CORE/WORMS/CLUSTERWORMS.py:874,1217,1254`, `src/CORE/WORMS/CONCURRENCY.py:88,272` | SEED (2026-09-29) |
| NATURE path stamps `did` per worm | `src/CORE/WORMS/NATURE_CLUSTERS.py:748` | DONE (pre-existing) |
| standby excluded from `ok` (`WormOutcome.n_standby`) | `src/CORE/WORMS/expansion/spawn_credit.py:389,417` | SEED (2026-09-29) |
| pivotal retry (retry from pivotal state, not full restart) | — | GATE (open: `decision_id` coverage is 0/44,846 live, so there is nothing to attach pivotal credit to yet) |

## 11.2 Auto: The AGI Compiler (`arXiv:2607.04542`, Jaber & Jaber)

Records live agent behavior, measures what is secretly deterministic, extracts
verified programs/distilled specialists, emits WASM cognition binaries behind
conformally calibrated guards; guard trip deopts to the reference agent and the
trace recompiles. AUTO-BENCH: 87.1% of 560 spans witnessed-deterministic.
Failure modes quantified: loose guard silently mislabels 48.9%; unfaithful
deopt reference blocks recompilation. (Not AutoTVM/MetaSchedule — that was a
wrong turn on 2026-09-28, corrected same night.)

Intermesh mapping (verification path):

| hook | file:line | status |
|---|---|---|
| grade row-gain check (executor cannot claim rows it did not write) | `src/CORE/neural_loop.py:529-538` | DONE (pre-existing) |
| grade records `win_rate` + `n_standby` + `uncalibrated_perfect` | `src/CORE/neural_loop.py:533` | SEED (2026-09-29) |
| promote requires attestation + quorum | `src/CORE/WORMS/expansion/spine.py:3658`, `src/CORE/spine_registry.py:492-495` | DONE (pre-existing) |
| differential-replay gate before promotion (Auto's verification gate) | — | GATE (open: `uncalibrated_perfect` is evidence only, not a block) |
| morph stages named signatures only (no `unknown` drip) | `src/CORE/WORMS/expansion/spine.py:3382` | SEED (2026-09-29, 91-stub drip stopped) |

## 11.3 SAIL single transformer (`arXiv:2504.10462`, ByteDance-Seed, ICCV'25 Highlight)

Single transformer over raw pixels + text (mixed attention, multimodal RoPE),
no separate ViT; steeper data-scaling than modular MLLMs; doubles as vision
backbone. SAIL-VL2 pairs SAILViT-Huge with Qwen3 backbones. (Note: `BSLM`
alone resolves to the unrelated Bayesian Latent Space Model R package.)

Intermesh mapping (architecture shape — already decided, now cited):

| claim | file:line | status |
|---|---|---|
| keep modular tracks, unify routing context only (no joint co-training) | `research/STACK_TRACK_DESIGN.md:76-79` | DONE (pre-existing decision, cited 2026-09-29) |
| diversity is the asset (`\|r\|` max 0.663–0.725, 109 pairs < 0.3, prune nothing) | `research/STACK_PHASE0_REPORT.md:6-12` | DONE (pre-existing) |
| 22/26 natures no-contract → merge context, not policies | `RECONCILIATION_AND_INTERMESH_2026-09-28.md:242-262` | DONE (this doc) |

## 11.4 What closes the two GATEs

1. PivoARL gate closes when `decision_id` coverage is non-zero on the live tap
   (choice rows and outcome rows sharing ids), at which point `joined_decisions`
   (`spawn_credit.py:526-544`) becomes non-empty and per-decision pivotal
   credit can replace Wilson-on-liveness.
2. Auto gate closes when promotion/grade requires differential replay at
   declared thresholds (measured, including refusals) with reference fidelity
   — calibration and reference fidelity decide, per Auto §6, not model
   capability. Free-Jev constraint holds throughout: no paid model calls are
   part of either gate (`jev_advisor.py` stays fail-open).
