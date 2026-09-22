# Architecture Decision Records

**Version:** 1.0.0  
**Date:** 2026-02-11

---

## ADR Index

| ID | Title | Status |
|----|-------|--------|
| ADR-001 | Tiered Architecture Design | ACCEPTED |
| ADR-002 | WORMZ Agent Design | ACCEPTED |
| ADR-003 | HYDRA Sequential Processing | ACCEPTED |
| ADR-004 | METAWORMS Composition | ACCEPTED |
| ADR-005 | HYDRAMETA Genetic Algorithm | ACCEPTED |
| ADR-006 | HORUS Animation System | ACCEPTED |
| ADR-007 | TERENCE Pattern Matching | ACCEPTED |
| ADR-008 | KLINK CLI Design | ACCEPTED |
| ADR-009 | Entry-point logging hygiene | ACCEPTED |

---

## ADR-001: Tiered Architecture Design

**Status:** ACCEPTED

### Context

The Azazael Ecosystem requires a structured approach to component organization that supports:
- Clear separation of concerns
- Scalable execution model
- Modular upgrades
- Cross-tier communication

### Decision

Implement a 7-tier hierarchical architecture:

| Tier | Name | Purpose |
|------|------|---------|
| 5 | DISTILLATION | Knowledge synthesis |
| 4 | HYDRAMETA | ML optimization |
| 3 | METAWORMS | Orchestration |
| 2 | CLUSTERWORMS | Coordinated execution |
| 1 | WORMS | Functional execution |
| 0 | CONCURRENCY | Parallel processing |
| -1 | OS_CONGRUENCY | OS integration |

### Consequences

**Positive:**
- Clear component boundaries
- Independent tier upgrades
- Focused testing strategies

**Negative:**
- Cross-tier dependencies require careful management
- Initial design complexity

---

## ADR-002: WORMZ Agent Design

**Status:** ACCEPTED

### Context

The system requires specialized functional agents for different system domains.

### Decision

Implement 6 functional worms:

| Worm | Domain | Responsibility |
|------|--------|----------------|
| WORMZ | Core | Discovery & crawling |
| SYSTEMZ | System | OS information |
| PROCESSZ | Processes | Process management |
| DISKZ | Storage | Disk analysis |
| CLOCKZ | Time | Synchronization |
| NETWORXZ | Network | Network analysis |

### Consequences

**Positive:**
- Focused responsibility per worm
- Easy to add new worms
- Clear testing boundaries

---

## ADR-003: HYDRA Sequential Processing

**Status:** ACCEPTED

### Context

ML pipeline requires structured, adaptive execution.

### Decision

Implement 6-stage sequential pipeline:

```
DISCOVER → ANALYZE → OPTIMIZE → VALIDATE → DEPLOY → FEEDBACK
```

Each stage:
- Receives input from previous stage
- Produces output for next stage
- Supports adaptive parameter tuning
- Can be executed independently

### Consequences

**Positive:**
- Clear data flow
- Stage-level error handling
- Parallel stage development

---

## ADR-004: METAWORMS Composition

**Status:** ACCEPTED

### Context

System requires higher-level static analysis and quality assurance.

### Decision

Implement 11 metaworms for Tier 3:

| Metaworm | Function |
|----------|----------|
| ERRORZ | Error pattern detection |
| TRIMZ | Content trimming |
| METAZ | Metadata extraction |
| DEPENDZ | Dependency mapping |
| VALIDZ | Syntax validation |
| DEADZ | Dead code detection |
| METRICZ | Code metrics |
| LOGZ | Log analysis |
| CHANGEZ | Change tracking |
| OPTIMIZ | Performance optimization |
| HEALTHZ | Health monitoring |

### Consequences

**Positive:**
- Comprehensive code analysis
- Modular improvement system

---

## ADR-005: HYDRAMETA Genetic Algorithm

**Status:** ACCEPTED

### Context

System requires adaptive optimization based on performance data.

### Decision

Implement genetic algorithm with:
- Population: 50-100 individuals
- Crossover rate: 0.8
- Mutation rate: 0.1 (Gaussian)
- Elitism: Top 10%
- Selection: Tournament method

### Consequences

**Positive:**
- Global optimization
- Automatic parameter tuning

**Negative:**
- Computational overhead
- Requires historical data

---

## ADR-006: HORUS Animation System

**Status:** ACCEPTED

### Context

Visual feedback requires engaging, informative animations.

### Decision

Implement 24 animation protocols:

| Category | Animations |
|----------|------------|
| Text | Glitch, Typewriter, Marquee |
| Glow | Neon Pulse, Shimmer |
| Motion | Slide, Bounce, Shake, Zoom |
| Background | Particles, Matrix Rain, Hex Grid |

### Consequences

**Positive:**
- Rich visual feedback
- Configurable effects

---

## ADR-007: TERENCE Pattern Matching

**Status:** ACCEPTED

### Context

Code quality requires automated pattern detection and fixing.

### Decision

Implement 26 fix patterns across categories:

| Category | Count | Examples |
|----------|-------|----------|
| Syntax | 6 | bare except, missing docstrings |
| Style | 8 | print statements, tab indentation |
| Security | 4 | hardcoded secrets |
| Performance | 8 | inefficient string concat |

### Consequences

**Positive:**
- Automated code improvement
- Consistent style enforcement

---

## ADR-008: KLINK CLI Design

**Status:** ACCEPTED

### Context

System requires unified command-line access.

### Decision

Implement hierarchical command structure:

```
klink <component> <action> [options]
```

Commands:
- `status` - Show ecosystem status
- `worms` - Run WORMZ
- `hydra` - Run HYDRA
- `metaworms` - Run METAWORMS
- `terence` - Run error resolution
- `horus` - Launch output formatter
- `all` - Full ecosystem run

### Consequences

**Positive:**
- Consistent interface
- Easy to extend

---

---

## ADR-009: Entry-point Logging Hygiene

**Status:** ACCEPTED  
**Date:** 2026-09-21

### Context

Entry points that import the worm registry used to quiet its one-INFO-per-worm
import chatter with `logging.disable(logging.CRITICAL)`. That switch is
process-wide: it silences WARNING and ERROR too. On 2026-09-21 the
proprioception gate refused to write for ~30 hours and emitted a WARNING from
inside exactly such a process, so the refusal read as success and nothing was
red. A sweep found ten entry points carrying the same blanket switch.

### Decision

1. **No entry point may call `logging.disable(...)`.** Silence noisy loggers by
   NAME instead, via `CORE.log_hygiene.quiet_noisy_loggers()`, which sets the
   known-chatty loggers (currently `worm_registry`) to WARNING and leaves
   WARNING+ live for the rest of the process.
2. **The canonical helper lives in `src/CORE/log_hygiene.py`** and imports only
   stdlib `logging`, so it is safe to import before the rest of CORE. Entry
   points reach it via the standard src path:

   ```python
   sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
   from CORE.log_hygiene import quiet_noisy_loggers
   quiet_noisy_loggers()
   ```

3. **No hardcoded user paths for the src root.** Entry points resolve src/
   from their own location (above) rather than `C:/Users/<user>/...`, so the
   same file works from Windows and from WSL (`/mnt/c/...`).
4. **A refusal must be visible.** A script that drives
   `SpineCycleWorm.run_cycle(apply=True)` must read `rep.get("skipped")` and
   report it; a refusal is not a success and must not print a success-shaped
   line.

### Enforcement

- `tests/test_logging_hygiene_sweep.py` fails on any AST-level `logging.disable`
  in `scripts/` or `src/`, and confines module-scope `logging.basicConfig` in
  `src/` to a documented allowlist.
- `tests/test_entry_point_smoke.py` runpy-executes every entry point and asserts
  logging is left on and `worm_registry` is quieted by name.
- `tests/test_spine_caller_refusals.py` fails if a gate caller omits the
  `skipped` check.

### Consequences

**Positive:** operator warnings survive in every scheduled process; a stalled
loop cannot read as green; the noisy-logger list has one home.

**Negative:** the known-noisy logger list must be maintained when a new chatter
appears (one edit, in one file).

---

## ADR-010 — Quality Gates Compare Against a Committed Baseline, and Persist Their Evidence

**Status:** Accepted (2026-09-22)

### Context

Two quality dimensions were effectively unenforced. The per-file test runner
cannot see a defect that only exists across files in one interpreter — measured
2026-09-22, one process returned 72 failures and 69 errors while every failing
file passed alone. And type checking had no working instrument at all (see
ADR-011).

Both dimensions have large pre-existing counts (50 aggregate failures, 1,377
type diagnostics). A plain "exit non-zero on any finding" gate would be red on
day one and would be switched off on day two, which is how a quality gate dies.

### Decision

1. **Baseline, not zero.** `tools/aggregate_suite_gate.py` and
   `tools/type_check_gate.py` each compare against a committed baseline under
   `logs/`. A finding **not** in the baseline exits 1; a baseline finding that
   disappeared is reported and exits 0, with a hint to re-baseline.
2. **Identity excludes prose.** Diagnostic identity is
   `file:line:col:rule` (or the failing `nodeid`) — never the message. Rewording
   a message must not read as a fix, and a changed message must not read as a
   regression.
3. **Not running is failing.** A timeout, a missing checker, and non-JSON
   output each exit 1. An unmeasured tree must never read as a clean one.
4. **A missing baseline is not a pass.** With no baseline file the gate refuses
   to reassure.
5. **The evidence travels with the report.** The aggregate gate writes the raw
   pytest output beside its JSON (Error #194: five runs' worth of failures were
   counted and unreadable because the text died in a captured pipe).
6. **CI profiles are explicit and dependency-light.**
   `--profile isolation` names the 8 files that reproduce the cross-file defect
   class without the ML stack, so the same baseline is valid on a laptop and a
   runner. The full-suite run stays a local/self-hosted instrument because its
   failures are environment-specific.

### Enforcement

- `tests/test_aggregate_suite_gate.py` — new id blocks, disappeared id only
  reports, timeout blocks, missing baseline refuses, message rewording is not a
  change, the isolation profile's files exist and import nothing heavy (AST-level
  check: the profile *discusses* `torch` in one docstring, which a substring test
  cannot tell from importing it).
- `tests/test_type_check_gate.py` — the same set, plus a committed-baseline vs
  committed-report agreement check.
- `.github/workflows/test-3.14t.yml` — the isolation gate is **blocking**; the
  type gate is non-blocking *with its condition written in the step* (the
  baseline was recorded against a venv with the ML stack installed, so a CI
  runner's diff is not yet evidence of a regression).

### Consequences

**Positive:** both dimensions are now measurable, adversarially pinned, and can
only get better — a new finding blocks, a fixed one is reported, and the count
trends where a monitor can read it.

**Negative:** the baselines must be re-recorded when a fix lands, or the gate
keeps a stale id and reports it as "no longer failing" until someone re-runs
`--baseline`. That is deliberate: tightening a gate should be a decision.

---

## ADR-011 — Types Are Checked With basedpyright, Not mypy

**Status:** Accepted (2026-09-22). Supersedes the mypy step in
`.github/workflows/test-3.14t.yml`.

### Context

mypy could not be made to work on this tree, and the reasons were not cosmetic:

- **It could not read the repository.** `mypy src/CORE/` aborted with
  `ValueError: path is on mount '\\.\nul'` — two literal files named `nul`,
  residue of a cmd.exe redirect run inside Git Bash, both invisible to git.
  (Removed; see Error #193.)
- **It asks a narrower question.** On the same tree: 655 errors over `src/CORE/`
  (329 files) in ~6 minutes, versus **1,191 errors + 252 warnings over 690 files
  in 64 seconds** from basedpyright. The classes basedpyright adds are the ones
  this codebase suffers from: `reportUndefinedVariable` 94,
  `reportOptionalMemberAccess` 120, `reportPossiblyUnboundVariable` 17.
- **Nothing new was needed.** `basedpyright 1.40.1` was already installed in the
  canonical 3.14t venv, and the repo already commits `pyrightconfig.json` with
  `typeCheckingMode: "basic"` and the excludes it needs.

### Decision

`basedpyright` is the type checker of record, driven through
`tools/type_check_gate.py` (baseline-compared per ADR-010). mypy stays installed
and remains a valid *second opinion* on a single file; it is no longer the gate.

### Enforcement

- `tests/test_type_check_gate.py`, and the `Type safety` row of
  `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md` now reports a measured baseline
  instead of "cannot be measured".

### Consequences

**Positive:** a type-check run costs ~1 minute instead of ~6, which is short
enough to be run per change rather than per session, and produces findings in
categories that map to this codebase's actual failure modes.

**Negative:** 1,377 diagnostics are now a recorded number that will be quoted.
A recorded number that nobody reduces is still a liability; the baseline gate
prevents *growth*, not debt. The debt is tracked in the audit as AR-7.

---

## ADR-012 — A Derived Artifact's Path Follows Its Scope, Not Its Label

**Status:** Accepted (2026-09-22). Applies to every gate that writes evidence.

### Context

`tools/aggregate_suite_gate.py` pinned its evidence by **profile**:
`--profile isolation` reads and writes `logs/aggregate_isolation_report.json` and
`logs/aggregate_isolation_baseline.json`. But `--only` narrows the pytest
**scope**, and the path did not follow. A one-file smoke test of the stall
watchdog wrote `1 passed in 1s` over a `301 passed` run of all eight profile
files (Error #195). The artifact remained valid JSON, its counts remained
plausible, and it named a profile it no longer described — the success-shaped
artifact defect, produced by the gate written to catch it.

Two secondary facts made this worse than a lost log:

1. The file is **tracked**, so the corruption is a commit away from being the
   project's record of CI health.
2. The suite itself reached the real path
   (`test_the_isolation_profile_pins_its_own_files_and_baseline` ran `--report`
   with no `--report-file`), so a test run could corrupt the same evidence.

### Decision

1. **Evidence paths are computed from the run's scope.** `is_narrowed()` compares
the effective selection against the profile's declared target set by membership
(so the same files in another order are still the profile). A narrowed run with
no explicit path is redirected to a `.partial` sibling and prints why. An
explicit `--report-file` / `--baseline-file` is obeyed as written — the caller
has then said where the evidence belongs.
2. **A narrowed run refuses rather than borrows.** With its own baseline absent,
`--check` exits 1 (`no baseline`) instead of diffing against the profile's set,
which would have reported every unrun file as "no longer failing" — green
because it looked at less.
3. **Tests redirect the artifact root, never the real path.** `default_evidence()`
is the single seam; tests point it at `tmp_path`.

### Enforcement

- Five tests in `tests/test_aggregate_suite_gate.py`: narrowed report lands in
  `*.partial.json` while the profile's files stay absent; a reordered full
  profile still writes the profile report; a narrowed `--check` exits 1; the
  mapping is asserted through `evidence_path()`, not by writing.
- `logs/aggregate_isolation_report.json` was regenerated by a real profile run
  (`0 failed / 301 passed / 0 errors / 1 skipped`, 116 s) and
  `tools/artifact_freshness.py` re-run, so the recorded evidence describes a run
  that happened.

### Consequences

**Positive:** the CI gate's baseline can only be written by the run it claims;
a dev smoke test cannot silently narrow the project's recorded health.
`tools/type_check_gate.py` has the same latent shape (`--paths` narrows the scope
while `BASELINE`/`REPORT` stay profile-pinned), and is now covered by this rule —
it is named in the lesson as the next place to apply it rather than left as a
second instance to discover.

**Negative:** two more filenames to know about (`.partial.json`,
`.partial.raw.txt`), and a narrowed run now needs `--baseline --baseline-file` to
be gated against itself. That is the intended cost: naming the evidence location
is what makes the scope explicit.

---

## ADR-013 — Authority Crosses a Thread Boundary Only When It Is Carried, and a Limit Applies After Every Filter

**Status:** Accepted · **Date:** 2026-09-22 · **Supersedes:** the operator
decision left open by Error #197

### Context

Two defects, one shared shape: a mechanism that was correct in isolation and
wrong about *when* it applied.

1. `sentinel_enforcer` gates writes with `_GATED_CALL = threading.local()`
   (`:40`), read per thread by a process-global audit hook (`:53`). `fs_probe`
   delegates its first probe of a path to a worker thread and opens
   `tempfile.TemporaryFile()` there, so **every delegated probe was denied by our
   own guard** and reported `None` — which the module documents as "unknown".
   The first fix (Error #197) was in `tests/conftest.py`, which made the suite
   green and left the subsystem broken wherever the guard is armed.
2. `MetaCluster.orchestrate(max_natures=N)` applied `[:N]` to the ranked Nature
   list *before* removing natures that contain the orchestration infrastructure,
   so a request for one Nature could execute zero and still return
   `phase="complete"` with `errors=[]`.

Both were found by watching a *value* rather than bisecting files
(`tools/pytest_fixture_watch.py`), and both had been invisible to per-file runs.

### Decision

1. **Authority is carried explicitly, never inferred from the process.**
   `worker_permit(held)` takes the permit state read on the STARTER thread and
   re-establishes it on the worker. A worker started with no permit is still
   denied, so using a thread cannot widen authority. `permit_here(reason)`
   replaces the bare `is_active = True` / `finally: is_active = False` pattern at
   every internal call site, restoring the previous value so nested authorized
   regions compose. `fs_probe._carried_permit()` reads the guard out of
   `sys.modules` instead of importing it, because importing `sentinel_enforcer`
   ARMS the audit hook, and returns a factory because `bounded_first_dir` starts
   N threads.
2. **A denial is its own outcome.** `bounded_subprocess_output` returns
   `denied`; `probe_backend_stats()["denied_probes"]` counts it; `is_denied()`
   reads it. A probe that reports "unknown" for a path it was forbidden to look
   at is reporting our own control as a filesystem fact.
3. **Limits apply after the filters that can discard.** `max_natures` caps the
   natures that can RUN; if every requested Nature is circular the selection is
   kept as-is so the no-op stays visible, and an empty execution order now
   appends an explicit error naming the circular set. A result may not report
   completion without a record of what completed.

### Consequences

**Positive:** the probe backend answers in the assistant's own session, not only
in the test process; the regression test pins both directions of the permit
boundary by rebinding the REAL thread-local token (so `conftest`'s compatibility
swap cannot satisfy it); and a caller can no longer mistake "nothing was
eligible" for "everything was fine".

**Negative:** two new conceptual pieces to know — a carried permit and a denial
counter. Both are named after the thing they measure, and both are asserted by
tests that fail without them (`test_sentinel_thread_permit.py`,
`test_cross_nature_orchestration.py::TestMetaClusterState::test_state_phases`).

**Left open here (deliberate):** `conftest`'s process-shared token is now
redundant for the probe path and is kept only until a full run with
`AZAZAEL_TEST_SHARED_PERMIT=0` is green; other legacy suites write from worker
threads through paths this decision does not cover.

### Related

Error #197, Error #198, Error #199, Lesson #91, Lesson #92, Lesson #93,
`tests/test_memory_dir_caching.py` (the same rule for a cached path: discover
the set by AST so the list cannot rot).

---

## ADR-014 — A Test's Restore Is a Snapshot of the Value, Never a Recomputation of It

**Status:** Accepted · **Date:** 2026-09-22 · **Supersedes:** the restore
mechanism chosen for Error #196

### Context

`tests/conftest.py` repairs the leaked memory-dir globals of Error #196 by
restoring, after every test, four module attributes
(`CORE.direct_memory.DB_PATH`, `CORE.local_memory.DB_PATH`,
`CORE.record_session.DB_PATH`, `CORE.MemoryBus._MEMORYBUS_DB_PATH`) plus two
reloaders (`CORE/backup.py:45`, `CORE/cd3_exporter.py:79`).

The first implementation restored by **recomputing** each value from
`AZAZAEL_MEMORY_DIR`. That is correct for the leak it was written for, and wrong
for a different, equally legitimate case: `tests/test_mutation.py:13` and
`tests/test_dm_advanced.py:13` redirect `direct_memory.DB_PATH` to their own temp
file in `setup_module()`, which is deliberately not derived from the environment.
The recompute therefore replaced their redirect with the shared session store
after the first test — and `test_mutation.py::teardown_module` then called
`.unlink()` on the live session store (Error #200: reported as a `WinError 32`
teardown ERROR only because the file happened to still be open).

### Decision

`_restore_memory_db_globals()` snapshots `(module, attribute, value)` for every
known global before the test and restores those exact values afterwards.
Recomputation survives in exactly one place: a module that was **imported during
the test** had no snapshot, has no deliberate redirect to preserve, and is still
computed from the restored environment.

`_MEMORY_DB_RELOADERS` entries carry an explicit attribute tuple, because
`backup` and `cd3_exporter` each recompute two globals and a single resolver name
could not express that; `tests/test_memory_dir_caching.py::test_the_restore_list_is_not_stale`
asserts every named attribute is still AST-visible as an env-derived global.

### Consequences

**Positive:** one mechanism now covers both shapes — a leaked global is repaired,
and a deliberate redirect is preserved. The rule generalises: restoring "the
state you changed" is what makes a fixture composable, and only the snapshot
knows what that state was.

**Negative:** the fixture holds references across the test, so a test that
rebinds a module by `importlib.reload` is not covered by the snapshot (it is
covered by the late-import recompute). The fixture is also no longer a pure
function of the environment, which is the point.

### Related

Error #200, Error #196, Lesson #94, `tests/conftest.py`,
`tests/test_memory_db_isolation.py`, `tests/test_memory_dir_caching.py`

---

## ADR-015 — A Timing Assertion States One Claim: "It Returns" or "It Is Fast", Never Both

**Status:** Accepted · **Date:** 2026-09-22

### Context

Three suite files asserted on wall-clock measurements and failed in the
aggregate run while passing alone (Error #201): a 3.112s call against a 3.0s
"probable deadlock" bound whose message said "Expected < 1s"; two `overdue()`
polls compared for float equality on a value computed from `now()` (0.020 vs
0.021); and a 2-worker benchmark that lost to its own 1-worker baseline with a
workload small enough that thread spawn dominated it.

### Decision

1. **Deadlock detection is a liveness claim, not a performance claim.** A
   re-entered `threading.Lock` never returns, so the guard only has to outlive
   any plausible load: `_DEADLOCK_TIMEOUT = 30.0`, with the reason in the source.
2. **Slow-but-complete is recorded, not asserted.** Calls at or above the
documented 1s hot-path budget append to a module-level `SLOW_CALLS` ledger that
the failure message reports.
3. **Never compare a `now()`-derived value for equality across two calls.**
   Compare the reported fields; bound the delta of the quantity that moves.
4. **A performance claim on a shared machine needs best-of-N and a workload
   large enough that fixed overhead is a small fraction of it** -- and if it
   still reports the load, replace the proxy with the property it stood for.
   The 2-worker speedup assertion survived best-of-N at a raised workload and
   then read 0.687 with a graph rebuild on the CPU. What it was really claiming
   is "two workers are in flight at once", which a two-party
   `threading.Barrier` proves at the same speed on an idle box and a busy one
   (`test_two_workers_run_concurrently`). The throughput numbers are still
   measured and printed; they are simply not the thing the build fails on.

### Consequences

**Positive:** a green suite no longer requires an idle machine, so the gate's
signal is the code again. The deadlock regression the file exists for is still
caught — 30s is exceeded by any real recurrence.

**Negative:** a genuine slowdown that completes inside 30s no longer fails the
suite; it appears in `SLOW_CALLS` instead. That is a deliberate trade, and it
means `SLOW_CALLS` is a report a reader must actually read.

### Related

Error #201, Error #193 (an unmeasured dimension read as a code problem),
Lesson #95, `tests/test_compliance_deadlock_regression.py`,
`tests/test_mesh_audit_insights.py`, `tests/test_pool.py`

---

*Generated: 2026-02-11*
