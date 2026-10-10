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

## S2 — Gates without actuators · CONFIRMED

The verifier class that computes a verdict and has **no consumer that acts on it**.
Grep-verified zero callers outside their own host and the exercise layer:

- `confirmed_revise` — *fixed this session*: `technique_runtime.revise_until_confirmed`
  now closes the gate→repair loop. Before that the gate could reject and nothing
  could respond.
- `rehearse_dispatch` — still zero callers; host `dispatch_plan.py` **is** reachable
  (`METACLUSTER.py:338`), so this needs a real consumer, not a wire.
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

## S6 — Evidence lives outside version control · CONFIRMED

`state/` is gitignored, so the artefacts that justify this session's claims —
`adoption_census.json`, `orphan_scan.json`, `suite_baseline.jsonl`, the
`sota_batches/batch06/` re-check docs — are **not committed**. A claim in a commit
message cannot be reproduced from the repo alone. Either commit the reports or move
them somewhere tracked.

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

## S8 — Multi-interpreter drift · CONFIRMED

Three interpreters: `.venvs/py315`, `.venvs/py315t`, `.venvs/build315t` — all
**3.15.0rc3**. Two flavours (GIL / free-threaded), and `build315t` for Nuitka. But
`pytest.ini`, `TODO_315T_BUILD.md` and several skills still describe **3.14t**
requirements and 3.14t wheel-ABI reasoning, which no longer matches the venvs. Docs
and reality have drifted; no single gate pins the suite to one interpreter.

---

## What to do next (ordered)

1. **Classify the orphan worklist** (`state/orphan_scan.json`): sub-app entry points
   vs genuine dead capability. Then decide, per row, wire-or-delete.
2. **Decide S1's module integrations.** This needs an owner decision — integrating
   `structured_action` (ASIL) and `rubric_evolution` changes runtime behaviour.
   Without it, mark EP168/269/327/382/350/351/201 as documented accept-gaps.
3. **Give `rehearse_dispatch` a real consumer** in the dispatch path (S2).
4. **Commit the evidence** or relocate it (S6).
5. **Finish and publish the suite baseline** (S7); then fix whatever it finds.
6. **Re-extract the ABSENT rows.** 19 remain in the map. Per the re-check docs
   (`state/sota_batches/batch06/recheck_part*.md`) they split into genuine infra
   with no host (EP11 ZeRO, EP14 ELECTRA, EP38, EP39, EP52, EP68 vLLM, EP226 MELT —
   Azazael consumes models as opaque providers, so these need an explicit
   accept-gap decision) and **buildable-with-a-real-host** rows (EP183 LogicLoc,
   EP206 ObjectGraph, EP237 cognitive map, EP245 measure-theoretic bounds, EP252
   Drop-Stable-Rampup, EP278 VATS, EP300 tensor rank gate, EP343 aTTT, EP141,
   EP153). Re-extraction rule from S3/S4: a new module with no external consumer
   becomes EXERCISE-ONLY by construction — build these **inside an existing
   production host with a real caller**, or do not build them.

## Do not repeat

- Do not report a counter without stating what makes the counter able to fail.
- Do not create a module for an ABSENT row without a production consumer.
- Do not adopt a row by calling it from the exercise layer (`technique_wiring/_l*.py`).
- Do not treat `import X` regex results as reachability.
