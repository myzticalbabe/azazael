# Structural Flaws — deep dive, 2026-10-10

> Written for the **next** assistant session. Everything here is a measured
> finding or an explicitly-labelled limitation. Where an instrument produced a
> number, the instrument's own validity is stated — because the single most
> expensive failure class in this tree is an unvalidated instrument answering
> confidently.

## The one-line diagnosis

This tree systematically optimises for the **appearance** of capability — registry
counts, "adapters engaged", symbols present in modules — and has no mechanism that
distinguishes *appearance* from *reachability*. A technique can be fully written,
registered, exercised by a test, and still be unreachable when the system runs.
Until `tools/adoption_census.py` (this session) no instrument existed that could
tell the two apart; the counter that did exist read the registry back to itself.

Every flaw below is an instance of that root cause.

---

## S1 — Capability without reachability (orphaned host modules) · CONFIRMED

Whole modules exist that **no production module imports**:

| module | consequence |
|---|---|
| `src/CORE/structured_action.py` | the ASIL interface layer — `semantic_action` (EP168/269/327/382) cannot be adopted |
| `src/CORE/rubric_evolution.py` | `gate_distillation` (EP350/351) cannot be adopted |
| `src/CORE/cascade.py` | `CascadeRouter` (EP201); also named in `THEATER_REMOVAL_TASKS` as an **unverified worker draft** — should be dispositioned, not wired |

**Dispositioned 2026-10-10 (evening) — commit `3f8ad03f`:**

- `structured_action` → **ADOPTED.** `compliance/policy.py` consults `semantic_action`
  on its evaluate path and can deny on its verdict; production call sites at
  `policy.py:54,196,206`. EP168/269/327/382 score ADOPTED (EP269/EP327/EP382 were
  never blocked by reachability alone and now read the same way).
- `cascade` → **WIRED, against this report's own recommendation.**
  `sequential_analyzer` escalates a one-step chain to the deep tier below
  `CASCADE_THRESHOLD` (a one-step chain can never satisfy `check_convergence`, so the
  `fast` strategy previously accepted its cheap answer at any confidence), and the
  tests assert both directions. **This contradiction is deliberate and stays visible:**
  either `cascade.py` was good enough to adopt (in which case remove it from
  `THEATER_REMOVAL_TASKS`) or it was not (in which case revert the wiring). Leaving
  both statements standing is the defect.
- `rubric_evolution` → **ACCEPT-GAP.** `gate_distillation` (EP350/351) has no consumer,
  and GRPO does not run, so gating `GRPOTrainer.update_policy` would be theatre. A
  gain-gate integration was written into `learning_grpo.py` and **reverted** for exactly
  that reason; its test was removed with it.

**Scale (new this session) — `tools/orphan_scan.py`.** From the four shipped entry
points (`run_tests.py`, `health_server.py`, `cli_observability.py`, `CORE/__init__.py`):
**309 of 701 `src/` modules reachable, 392 unreachable**, of which **330 have no
importer at all**.

> **Instrument caveats, stated before the number is used.** (a) The scan treats
> only repo-root scripts as entries, so sub-apps with their own CLI inside `src/`
> (`AOA`, `CLI`, `CODEX`, `AZAZAEL_TOOLKIT`, `packages/`) appear as orphans
> legitimately. Their rows are a **worklist to classify, not a defect count**.
> (b) Prefix matching is deliberately broad (`from CORE.WORMS.expansion import X`
> marks every submodule of `expansion` reachable), which **under**-reports
> orphans. (c) A first version of this scan used "every `__init__.py` plus every
> non-CORE module" as the entry set and printed **ORPHANED 0 / 701 reachable** —
> a broken instrument reporting perfect health. It now hard-fails if no entry
> point resolves. (d) 54 orphans contain dynamic-import text and may be
> reachable by a path static analysis cannot see.

Worklist: `state/orphan_scan.json` (gitignored — see S6).

**Scanner repaired 2026-10-10** (defect found by a worker, then verified): it could not see RELATIVE imports, so `PERSEPHONE.lib` read as an orphan while its own facades import it. Now resolves `.`, `..` and `from . import member`: import edges 13,131 -> 13,222, `no_importer` 330 -> 306. The worker's conclusion was one level off and is worth remembering — `eve_unleashed.cache/engine/core` are FALSE for `no_importer` (the facade does import them, `__init__.py:8-11`) but correctly UNREACHABLE, because the `eve_unleashed` package itself has no reachable importer and reachability is transitive from the entry points. A sibling's import cannot confer reachability.

## S2 — Gates without actuators · CONFIRMED

The verifier class that computes a verdict and has **no consumer that acts on it**.
Grep-verified zero callers outside their own host and the exercise layer:

- `confirmed_revise` — *fixed this session*: `technique_runtime.revise_until_confirmed`
  now closes the gate→repair loop. Before that the gate could reject and nothing
  could respond.
- `rehearse_dispatch` — **RESOLVED 2026-10-10** (commit `3f8ad03f`):
  `MetaCluster._plan_execution_order` rehearses the plan and its assignment before
  dispatch, and its verdict, predicted failures and pool load ride the plan note;
  `orchestrate()` calls that method. **The claim in this report was too generous and is
  corrected here:** `METACLUSTER.py:338` is an import *inside* a method that
  `orchestrate()` did not call, so the host was reachable in principle only. A reader
  who trusted "host is already reachable" would have wired the symbol into an uncalled
  method and moved the counter without moving behaviour.
- `gate_distillation` — zero callers, host orphaned (S1).

A gate nothing consumes is indistinguishable from verification and changes nothing.

## S3 — The exercise layer manufactures the appearance of wiring · CONFIRMED

`src/CORE/technique_wiring/_l*.py` call technique symbols so the registry reads as
engaged. Measured by the census: **92 rows were EXERCISE-ONLY in the sense that
their only caller was this layer** (23 → 8 after this session's wiring). The retired
"181/181 adapters engaged" counter was this layer read back to itself.

## S4 — Self-referential / unvalidated instrumentation · CONFIRMED, RECURRING

Three distinct instances in one session:
1. the retired adoption counter (registry reading itself) — cause of T-15;
2. **my own** `orphan_scan.py` reporting 0 orphans from an impossible entry set;
3. **my own** grep `import.*<module>` missing every `from X import y` form, which
   produced a false claim that *five* host modules were orphaned (only three are —
   `delegation`, `agent_registry`, `compliance_auditor`, `verification_gate` are
   all production-imported: `CLUSTERWORMS.py:83`, `Agent.py:129`, `broker.py:48`,
   `technique_runtime`).

Rule that follows: **an instrument's negative result is not evidence until the
instrument has been shown capable of producing a positive one.**

## S5 — The hand-maintained map bounds every adoption number · CONFIRMED

`technique_codebase_map.json` (141 rows) was wrong on **8 rows**: two targeted a
path missing the `CORE/` segment (`WORMS/expansion/synapse.py`; `SSMSequenceWorm`
is at `synapse.py:348`), and five named **prose instead of a symbol**
(`role-pool`, `DEPO rollout`, `structural exploration`, `test_theta_frozen`,
`reconstruct`). Corrected this session to real hosts / explicit `no-target`.
Adoption counts are therefore bounded by a file a human edits by hand.

**Worse than S6, found 2026-10-10 (evening):** that map is not in this checkout at
all. `state/sota_batches/batch06/technique_codebase_map.json` resolves to the **parent**
directory (`C:/Azazael/state/...`, while the repo root is `C:/Azazael/azazael`), so no
`.gitignore` rule here can version it — the file that bounds every adoption number is
absent from the repository. Recorded in `EVIDENCE.md`.

## S6 — Evidence lives outside version control · **RESOLVED 2026-10-10**

`state/` is gitignored, so the artefacts that justify this session's claims —
`adoption_census.json`, `orphan_scan.json`, `suite_baseline.jsonl`, the
`sota_batches/batch06/` re-check docs — were **not committed**. A claim in a commit
message could not be reproduced from the repo alone.

**Resolution** (commit `183ef1ec`): `.gitignore` re-includes exactly three artefacts
(`state/adoption_census.json`, `state/orphan_scan.json`, `state/suite_baseline.jsonl`)
and `EVIDENCE.md` at the repo root names each one, the claim it supports and the command
that regenerates it. The rules needed the **directory negation first** (`!state/`, then
`state/*`, then the file negations): git documents that a file negation is inert while a
parent directory is excluded — the same trap that forced `.githooks/pre-commit` to be
force-added. Verified with `git check-ignore -v`, which shows the three artefacts
matching their negation while a sibling (`state/evolved_rl_params.json`) stays ignored.
The one artefact this could **not** reach is the map itself — see S5.

## S7 — No green full-suite baseline · **RESOLVED — SUITE IS GREEN**

4068 tests collect; a single `pytest tests/` exceeds the 600 s command ceiling, so
"green" was never established. Fixed: `tools/suite_baseline.py` runs 264 test files
in bounded batches and journals each to `state/suite_baseline.jsonl`, so a run that
dies **resumes** instead of restarting. No deselects, no `--ignore`, no retries — a
failing batch stays failed.

**Result: 14/14 batches green.** 13 passed on the first pass; batch 7 found 2 real
failures in `tests/test_mesh_wire_or_cut.py`, both **caused by this session's own
changes**, both now fixed:

1. `engram:run_read_driven_consolidation` had no visible reference because
   `technique_runtime` imported it as `run_read_driven_consolidation as
   _read_driven_consolidation` — an alias import makes a real call invisible to
   static reachability, so `PF16` reported "no production reference of any kind".
   Fixed by resolving the name off the module (`getattr(_engram,
   "run_read_driven_consolidation")`) instead of aliasing it.
2. `engram:DreamConsolidatorWorm.read_pressure` was declared `dispatched` in the
   ledger while a static caller (`engram.py:728`, inside the restored
   `consolidate_from_reads`) reaches it. See **S9**.

Batch 7 re-run after the fix: **277 passed, 1 skipped**. Total suite: green.

> The two failures are the strongest evidence in this document that the mesh gate
> works: it caught a defect the session introduced, in the exact class this report
> is about, on the first complete run the suite has ever had.

## S8 — Multi-interpreter drift · CONFIRMED

Three interpreters: `.venvs/py315`, `.venvs/py315t`, `.venvs/build315t` — all
**3.15.0rc3**. Two flavours (GIL / free-threaded), and `build315t` for Nuitka. But
`pytest.ini`, `TODO_315T_BUILD.md` and several skills still describe **3.14t**
requirements and 3.14t wheel-ABI reasoning, which no longer matches the venvs. Docs
and reality have drifted; no single gate pins the suite to one interpreter.

---

## S9 — A generated ledger is a cache with no rebuild path · CONFIRMED

`NEURAL_MESH_WIRE_OR_CUT.json` is generated by `tools/mesh_function_preflight.py
--verdict`, committed, and asserted against by `tests/test_mesh_wire_or_cut.py`.
When this session restored the EP235 loop it made `read_pressure` statically
called, but the ledger still said `dispatched` — so the gate failed on state the
code had already moved past. Regenerating the ledger fixed it with no code change
for that row.

The failure mode is not the ledger, it is that **nothing regenerates it as part of
changing the code**. Any change that adds or removes a caller can invalidate it
silently, and the test then reports a defect that is stale rather than real (or,
worse, passes on a stale ledger). This is the same class as `PMB LESSONS #93`
("a measurement written inside a transition is a cache with no rebuild path").
**RESOLVED.** `mesh_function_preflight.py --check` now regenerates the table (with the committed map as prior, so hand-set decisions survive) and fails when the SET of unreferenced functions moved. It is wired as **Check 5** of `.githooks/pre-commit`, so a caller change can no longer leave the ledger silently stale.

> It deliberately does **not** compare statuses, and that is measured, not an omission: with the committed map as prior the comparison is self-fulfilling. Negative control 2026-10-10 flipped a status `pending`->`retired` and `--check` still reported "statuses unchanged" -- so that comparison was removed. Dropping a key *is* detected (exit 1, correct diagnosis). Status **legality** stays with `tests/test_mesh_wire_or_cut.py`, which re-derives evidence instead of trusting the file. A control the instrument cannot fail is not a control.

## S10 — The commit gate itself is outside version control · CONFIRMED

`core.hooksPath` points at `.githooks`, and **`.githooks` is gitignored** — so the pre-commit gate (focus, compliance scanner, canon drift, anti-pattern ratchet, mesh ledger freshness) exists only in this machine's working tree. A fresh clone has no gate, and any change to the gate is invisible in review. Found at 20:32 on 2026-10-10, when S9's own commit was refused with `The following paths are ignored by one of your .gitignore files: .githooks`.

Force-added `.githooks/pre-commit` so the gate is reviewable and reproducible. **Worth an explicit decision:** if `.githooks` is ignored deliberately, the alternative is to move the checks into a tracked runner (e.g. `tools/preflight_all.py`) that the hook merely calls, so the gate is versioned even when the hook file is not.

**RESOLVED 2026-10-15.** The decision was taken as the second option, because force-adding the hook only narrowed the problem: `.githooks` is still gitignored, so the hook is one `git rm --cached` -- or one clone on a host without the force-add -- away from vanishing again, and the checks were still assembled inline in shell, leaving "which gates exist" answerable only by reading a hook file.

`tools/preflight_all.py` now carries the registry (`--list`), the runner (`--check`) and the self-test (`--self-test`). The registry is transcribed from the hook, and `--self-test` **re-derives the hook's gate list from the hook text** and fails on any disagreement, so the table cannot silently drift from the gate that actually runs. Its first run reported two facts nobody had recorded:

* **`tests/test_index_drift_check.py` did not exist.** Check 1b is a BLOCKING hook gate whose fail-ability was asserted by nothing. It was written in the same session (76 tests, green on `py315t` and 3.14.7): a gate that cannot be shown to fail is not a gate.
* **the hook runs its gates on three different interpreters.** Check 1 invokes `python3` (3.13.14 on this host) while checks 1b--5 invoke `python` (3.14.7), and check 6 uses the PMB venv. Every gate passes on both today, so this is a **latent divergence, not a live false green** -- but "the pre-commit gate" is not one interpreter, and a gate resolved by NAME may land on either.

It also executes the false-green protocol's Enforcement clause, which until now was a requirement nobody ran ("every gate has tree hash + mtime + --force + missing evidence fail"): `--force` re-runs; a cached PASS is reused only while the gate's own bytes **and** the staged/worktree state it judged are unchanged; an unrunnable gate is a FAILURE unless declared with `--allow-unrunnable`; and gates with no control are COUNTED and printed rather than rounded to a pass.

**Not done, and named rather than implied:** the hook still assembles its checks inline, so it does not yet *call* this runner. Wiring it is a change to the commit gate itself and was left out of a session whose brief was to build the framework. Until then the registry is a second description of the hook -- which is precisely why `--self-test` fails when the two disagree.

## S11 — Tests under `src/` are never collected · CONFIRMED

`pytest.ini` sets `testpaths = tests`, so every `test_*.py` under `src/` is invisible to the suite. `src/AOA/conftest.py` admits it in its own docstring, and `src/AOA/test_arm_exports.py` records that it was written to prevent a regression that then RECURRED because it was never collected. A test that cannot run is worse than no test: it reads as coverage. (Found by worker 1.)

## S12 — Hardcoded absolute paths · CONFIRMED

`src/AOA/rebuild_html.py` reaches into `C:/Users/clint/Desktop/AOA/...`, and `src/AOA/arms/codex_arm.py` / `eve_arm.py` build `Path.home()`-relative paths. These break on any other machine, and nothing in the suite can see them because the modules are unreachable (S1). (Found by worker 1.)

## S13 — Duplicate modules inflate every census · CONFIRMED

`AzazaelDynamicLogger` exists three times (`UTILITIES/`, `TOOLS/`, `src/`) with the two non-root copies unreachable; `src/AOA/refresh_aoa_data.py` and `refresh_oa_data.py` are 414 lines each;`AUTO_DOC_GENERATOR`, `emoji_maker` and `enhanced_animations` exist at root AND under
`CODEX/CORE/`. Any count over files over-counts capability, and a fix applied to one
copy silently misses the others. (Found independently by workers 1 and 3.)

## S14 — `suite_baseline.py` answers "green" from a journal it never invalidates · CONFIRMED 2026-10-10

The resumable baseline journals one record per batch and skips any batch already
recorded green. There is **no staleness trigger**: no tree hash, no mtime check, no
`git rev` comparison, and no `--force`/`--redo` flag (`tools/suite_baseline.py:112-116`).
So a run *after* code changes reports `14 already ok` in ~0s and prints
`batches FAILED: 0` — having executed **nothing**.

This is flaw **S9's exact shape** (a generated artefact is a cache with no rebuild
path), on the artefact that answers the most load-bearing question in the project. The
measured demonstration: this session's own commits produced `14 already ok`, a result
that says nothing about them. A true full-suite answer requires deleting or moving
`state/suite_baseline.jsonl` first; only then does the 918 s run mean anything.
**Not fixed — recorded.** A `--force` flag plus a tree-hash stamp on each record is the
obvious repair.

## S15 — an order-dependent failure hides in the existing suite · CONFIRMED 2026-10-10

`tests/test_cross_domain_integration.py::test_cd5_docker_benchmark` **fails** when that
file runs after other files in one process, and **passes alone** (2.6 s). The control
that makes this a pre-existing defect and not this session's work: the same 11-file
invocation with **all four of this session's new test files excluded** still fails
(`1 failed, 161 passed`) — reverting today's commits would not clear it.

So "the suite is green" is **ordering-dependent** for at least one test, which is what
makes S14 dangerous: the journal's batch boundaries decide whether this shows up, and
a skipped batch can never re-expose it.

## What to do next (ordered)

1. **Act on the orphan classification — it is DONE** (`ORPHAN_TRIAGE_315T.md`, 392/392 rows): 201 SUBAPP-ENTRY, 99 DEAD, 52 FACADE, 40 UNCLEAR. Because the large class is sub-apps, the live decision is a **launch/registration policy** for apps no shipped entry point starts, not wholesale deletion. Start with the 99 DEAD and the 52 FACADE.
2. ~~**Decide S1's module integrations.**~~ **DONE 2026-10-10 (`3f8ad03f`).** `structured_action` adopted (EP168/269/327/382); `cascade` wired but **contradicting this report — resolve one way or the other**; `rubric_evolution` marked accept-gap (EP350/351).
3. ~~**Give `rehearse_dispatch` a real consumer** in the dispatch path (S2).~~ **DONE 2026-10-10 (`3f8ad03f`)** — and note the host was *not* in fact reachable until `orchestrate()` was wired to `_plan_execution_order` (see S2).
4. ~~**Move the evidence into version control** (S6).~~ **DONE 2026-10-10 (`183ef1ec`)** for the three artefacts; the map and the batch06 re-check docs are outside the checkout entirely (S5), so they remain unreproducible.
5. ~~**Build the three BUILD-IN-HOST ABSENT rows** — EP183 (LogicLoc), EP206 (ObjectGraph), EP252 (Drop-Stable-Rampup).~~ **DONE 2026-10-10 (`ac9dc46a`)**, each inside its named host with both directions asserted. **The residual limit is measured, not waved away:** each new function is reached from *inside* its host, so the census credits the row on the **host symbol**, not on the new function. A caller in a different production module does not exist, and manufacturing one to move the counter is the failure this list forbids. EP206's build also exposed a stale flag — `document_graph_stats` reported `typed_nodes: false` beside a built typed layer, i.e. a **missing measurement read as a fact**.
6. **Decide S10's open question** — whether `.githooks` stays gitignored. If it does, the checks belong in a tracked `tools/preflight_all.py` that the hook merely calls.
7. ~~**Then re-check the suite** (`python tools/suite_baseline.py`).~~ **Attempted 2026-10-10 — NOT AN ANSWER.** The run reported `14 already ok / FAILED 0` in seconds by resuming a journal that predates today's commits (see **S14**). The targeted evidence that does cover the changes: **180 passed** across the 15 test files touching the changed modules, with one order-dependent failure that is pre-existing (**S15**), plus 105 and 28 passed on the per-integration sets. A real full-suite answer must first invalidate the journal.

**Closed this session, do not redo:** S7 (suite baseline — 14/14 batches green, 264 files, 918 s) and S9 (`--check` + pre-commit Check 5, negative-controlled both ways).

## Do not repeat

- Do not report a counter without stating what makes the counter able to fail.
- Do not create a module for an ABSENT row without a production consumer.
- Do not adopt a row by calling it from the exercise layer (`technique_wiring/_l*.py`).
- Do not treat `import X` regex results as reachability.
