# Audit task register — all projects, all environments (2026-11-02)

**What was audited, and by what.** Four surfaces, each read by the tree's own
instrument, not by inspection:

| surface | instrument | result |
| --- | --- | --- |
| Windows stack (pmb/proxy/supervisor/PAMS/lanes) | `tools/mcp_startup_gate.py --fix` | **9/9 PASS** in 12.0 s |
| Windows repo gates (31 registered) | `tools/preflight_all.py --check` | 31 ran, **3 gates failed (all blocking)** → 4 tasks |
| Windows repo tests (499 files) | `tools/golden_arrow.py --status` → `logs/golden_arrow.json` | 488 pass / **11 fail**, 6 662 tests pass / **19 fail**, 0 HUNG |
| Windows repo AST (3 822 files) | `tools/ast_audit.py --root .` | **0 syntax errors**; debt counts below |
| Sibling projects (6) | `python -m compileall -q` per project | **0 compile errors** anywhere |
| WSL Ubuntu-26.04 | `wsl -d Ubuntu-26.04` (2 690 `.py`) | **gate tool missing** |
| Kali | `wsl -d kali-linux` (3 170 `.py`), store row count | **no error found** |

**Board state at audit time:** 0 available, 0 open, 408 retired, **17 blocked**
(pre-existing, not created by this audit). Kali's store reads 45 056 rows and
Windows reads 45 056 — the shared store is genuinely shared, so the canon's
zero-row-store failure mode is not present.

**How to read a task.** Every task names the command that produced it. A task
marked *recorded debt* is already in `logs/golden_arrow_baseline.json`: it is a
known error that the gate tolerates, not a new breakage — `--strict` fails on all
of them.

---

## A. Blocking gate failures (Windows repo, 4)

### T-01 — `changeset-focus`: 15 files staged against a bulk limit of 8
**Evidence:** `python tools/preflight_all.py --check` → `[FAIL] changeset-focus`;
`git diff --cached --name-only | wc -l` = 15.
Fifteen paths are staged in the index (from more than one lane's work). The gate
cannot tell a bulk operation from a careless commit, so it blocks. Fix: `git
reset` the index and stage by path, or declare `ALLOW_BULK_COMMIT=1` in the
message for a genuine bulk op.

### T-02 — `changeset-focus`: `03_tooling/verify_proofs.py` changes 193 lines (limit 150/file)
**Evidence:** same gate, second line: `03_tooling/verify_proofs.py changes 193
lines (limit 150/file). Split it, or set ALLOW_BULK_COMMIT=1.`
A single file changed by more than the per-file budget. Either split the change
into two commits or declare it.

### T-03 — `staged-scanner`: `03_tooling/verify_proofs.py` adds 2 `silent_except_pass`
**Evidence:** `[StagedScanner] Anti-pattern(s) ADDED by this commit:
03_tooling/verify_proofs.py: silent_except_pass 0 -> 2 (+2)`.
A new commit is introducing swallowed exceptions in a verification tool — the
worst place for a silent failure, because the tool's whole job is to report. Fix
the two handlers, or re-baseline with an explanation if the swallow is deliberate.

### T-04 — `anti-pattern-ratchet` cannot evaluate: baseline and gate disagree on scope
**Evidence:** `python tools/anti_pattern_gate.py --check --tracked-only` →
`baseline ... was recorded over the whole worktree but this run scans tracked
files only -- not comparable.`
The gate is **structurally blind**, not reporting a finding. Every run fails
without telling anyone whether the anti-pattern count rose. Fix: re-record with
`python tools/anti_pattern_gate.py --baseline --tracked-only`, then re-run
`--check` and confirm the ratchet actually compares.

---

## B. Failing tests (Windows repo, 19 tests in 11 files — all *recorded debt*)

Each is a separate error. All were reproduced by the last full
`tools/golden_arrow.py` run; the report is `logs/golden_arrow.json`.

| # | task | failing test | file |
| --- | --- | --- | --- |
| T-05 | Concurrent writes lose rows | `test_200_concurrent_writes` — `AssertionError` | `tests/test_concurrency_200.py` |
| T-06 | Monitor worm reports wrong metrics | `TestScheduledDbMonitorWorm::test_execute_reports_metrics` | `tests/test_db_monitor_worm.py` |
| T-07 | Backup is not a valid SQLite file | `TestDatabaseMonitorWormIntegrity::test_create_backup_is_valid_sqlite` | `tests/test_db_monitor_worm.py` |
| T-08 | Eve arm orchestration: `assert 3 == 0` | `test_arm_orchestrate` | `tests/test_eve_arm.py` |
| T-09 | SB3Agent does not drop unknown registry keys | `test_sb3agent_drops_unknown_registry_keys` | `tests/test_morphed_trainers.py` |
| T-10 | SB3Agent does not resolve morphed → base | `test_sb3agent_resolves_morphed_to_base` | `tests/test_morphed_trainers.py` |
| T-11 | An ML module with a src test is still on the dead list | `test_every_ml_module_with_a_src_tests_file_is_out_of_the_dead_list` | `tests/test_orphan_triage.py` |
| T-12 | Persisted payload capsule is not bound to HEAD | `test_persisted_payload_carries_capsule_bound_to_head` | `tests/test_pipeline_provenance_capsule.py` |
| T-13 | Temp store loses concurrent writes | `test_a_temp_store_keeps_every_concurrent_write` | `tests/test_race_shared_structures.py` |
| T-14 | Credit weights non-empty when nothing is pivotal | `test_credit_weights_are_empty_when_nothing_is_pivotal` | `tests/test_reflexion_sota_rows.py` |
| T-15 | `fetch_all` does not read past the clamp | `test_fetch_all_pages_past_the_clamp` | `tests/test_thought_corpus_integrity.py` |
| T-16 | The clamp evicts the rows that carry signal | `test_the_clamp_evicts_exactly_the_rows_that_carry_signal` | `tests/test_thought_corpus_integrity.py` |
| T-17 | `fetch_all` ignores its limit | `test_fetch_all_honours_its_limit_exactly` | `tests/test_thought_corpus_integrity.py` |
| T-18 | `record_thought` writes a shape consumers do not read | `test_record_thought_writes_the_shape_consumers_read` | `tests/test_thought_corpus_integrity.py` |
| T-19 | `record_thought` does not truncate long traces | `test_record_thought_truncates_long_traces` | `tests/test_thought_corpus_integrity.py` |
| T-20 | WAL checkpoint never fires on a tmp store | `test_checkpoint_fires_on_tmp_store` | `tests/test_wal_autocheckpoint_proof.py` |
| T-21 | **3 tests fail with no `FAILED` line** — process-level failure, not assertions | *unnamed in the report* | `tests/test_enforce_global_quota_victim_rule.py` |

**T-21 is the worst entry on this list.** The report's tail for that file is a
pytest/pluggy frame stack, not a `FAILED ...` summary: three tests took 93.76 s
and died without naming themselves. A test that fails without an assertion is
either crashing the interpreter or being killed, and the corpus-wide thought
tests (T-15…T-19, 5 of 5 failing) suggest the same subsystem is involved.

---

## C. Code-health debt measured by the AST audit (Windows repo, 4)

`tools/ast_audit.py --root . --out logs/ast_audit.json` printed
`py=3822 parsed=3822 syntax_err=0 loc=906208 cls=4033 fn=36382 methods=17242
bare_except=112 except_pass=810 except_continue=240 markers=375 orphans=2677
dupgroups=63`.

No syntax error exists in the tree. The following are the four counts large
enough to be their own task; each task is the enumeration, because the individual
sites have never been listed.

### T-22 — 810 `except ...: pass` sites
The same anti-pattern T-03 blocks new instances of. 810 existing ones mean the
ratchet protects a tree that already swallows errors at scale.

### T-23 — 112 bare `except:`
`except:` catches `KeyboardInterrupt` and `SystemExit` as well as errors, so a
Ctrl-C can be absorbed by any of them. Enumerate, then narrow to
`except Exception`.

### T-24 — 2 677 orphan modules
Modules nothing imports. This is the class that hid `src/CORE/langgraph_integration.py`'s
live `NameError` (canon HED-1) for months, because nothing imported it and nothing
ran it.

### T-25 — 63 duplicate code groups
Same logic in more than one place, which is how two copies drift and only one
gets fixed.

---

## D. Environment errors (1)

### T-26 — Ubuntu-26.04 mirror has no `tools/mcp_startup_gate.py`
**Evidence:** `wsl -d Ubuntu-26.04 -- bash -lc 'test -f
/root/azazael/tools/mcp_startup_gate.py && echo gate-present || echo gate-MISSING'`
→ `gate-MISSING`; `find /root/azazael -name "*.py" | wc -l` → 2 690;
`python3 -V` → `Python 3.14.7`.
The Ubuntu tree holds 2 690 Python files and **cannot run step 0 of the session
order**. Every session on that environment therefore starts without the gate or
the floor differential, and any claim made there about memory recall is unverified
by construction. The follow-up is a diff, not a copy: enumerate every tool the
Windows tree registers that Ubuntu lacks before syncing anything.

**Kali:** `/root/azazael` (3 170 `.py`), `/root/BCC-REINVESTIGATION` and the board
store all present; store row count matches Windows exactly. No error found.

---

## E. Project-level gaps (2)

### T-27 — `pams-source` has 0 test files
16 Python modules, no tests at all. PAMS backs memory for every other project, so
its untested surface is load-bearing for all of them.

### T-28 — `C:/Azazael/training` holds 0 Python files
A project directory with no code. Either the content moved and the directory is a
stale pointer, or work was expected there and never landed. Decide which, then
delete or populate.

---

## F. What the audit did NOT find — so this is not re-run

- **No syntax error anywhere:** 3 822 files in the repo, 0 parse failures.
- **No compile error in any sibling project:** `azazael-coord` (4 978 `.py`),
  `azazael-forensics` (10), `pams-source` (16), `vermillion_lightfury` (38),
  `desktop` (134), and the six `Project_*` trees (9, 1 248, 6, 23, 41, 31) all
  compile clean.
- **No stack fault:** all nine gate checks pass, including the floor differential
  (daemon 5 rows, best 0.64 → proxy 0) and `floor-origin` (logon-started, not
  session-scoped).
- **No lane misconfiguration:** kilo, freebuff and opencode all route `pmb`
  through :8766.
- **No cross-environment board divergence:** both stores read 45 056 rows.

## G. Coverage limits, stated

1. **Stopped environments were probed, not audited.** Ubuntu and Kali were
   stopped; I started each long enough to run `find`/`test`/one SQLite count.
   Their own gates, test suites and AST audits were **not** run — T-26 is what a
   probe can see, and the real audit of those trees is its own session.
2. **Test results are the recorded run, not a run I performed.** The 19 failures
   come from `logs/golden_arrow.json` as written; I verified the report's contents
   and totals, not the failures' reproducibility today. Re-running 499 files is a
   separate job and would overwrite the full-suite artifact.
3. **`except_pass`, `orphans` and `dupgroups` are counts, not lists.** The task is
   the enumeration; no individual site has been inspected, so no severity is
   claimed beyond the class.
4. **`G:` was not audited.** The archive drive was referenced by canon but not
   enumerated in this pass.
