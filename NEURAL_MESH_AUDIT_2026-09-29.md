# Project Audit — 2026-09-29

Scope: every project the user could reasonably mean by "all projects" —
the 37 directories on `Desktop/`, the `azazael/` tree, every tool under
`tools/` and `scripts/`, every test under `tests/`, and the Windows/WSL
environment split. Four questions per area: false-PASS claims, dead or
wrong code, cross-environment consistency, and anything that cannot fail.

Everything below was measured on this machine. Where a number is quoted it
came from a command whose output is reproducible from the repo root. Where
something could not be established, it says so rather than estimating.

---

## Summary

| # | Finding | Severity | Status |
|---|---|---|---|
| 1 | `gen_everything.py` emitted corrupted PowerShell paths (tabs/backspaces) | **real bug** | fixed |
| 2 | Same file joined output with a literal `\n`, producing a 1-line script | **real bug** | fixed |
| 3 | `azazael-standalone` skill claimed 39 `.exe` files; there are 0 | **false claim** | corrected |
| 4 | `test_cross_domain_integration.py` reported PASS unconditionally | **false PASS** | fixed |
| 5 | Z3 model extraction always failed; exception swallowed as `{}` | **real bug** | fixed |
| 6 | Z3 path never emitted `violations`, only the fallback did | **real bug** | fixed |
| 7 | `get_summary()["total_checks"]` always 0 under Z3 | **real bug** | fixed |
| 8 | Build manifest: 9 of 39 entry points did not resolve | **stale data** | fixed |
| 9 | WSL is 2 months behind and is NOT the source of 5 "missing" files | **premise error** | documented |
| 10 | `invalidate_route` unreachable in production | by design | documented |

Four of the eight defects were invisible until something was made to fail.
That is the through-line of this audit and the reason it is written up at
all.

---

## 1. The false-PASS cluster (`test_cross_domain_integration.py`)

The file defines a local `check(label, condition)` helper. It printed
`[PASS]`/`[FAIL]`, incremented a module global, and **returned**. Nothing
ever asserted on the counter.

Five `test_cd*` functions contain roughly 60 `check()` calls between them.
Under pytest, every one of those checks could fail and all five tests would
still report PASS. The file's own `main()` returned `0 if failed == 0 else
1`, so the failure logic existed — it just was not on the pytest path.

Making `check()` raise `AssertionError` exposed three genuine defects on
first run. None of them had ever failed a build.

### 1a. Z3 model values were always discarded

```python
output["model_values"] = {
    str(d): str(model.eval(d, model_completion=True))
    for d in model.decls()
}
```

`model.decls()` yields `FuncDeclRef` objects — *declarations*, not
expressions. `model.eval(d)` therefore always raises
`Z3Exception: ast is not an expression`, and the surrounding
`except Exception` replaced the failure with `{}`. A caller could not
distinguish "satisfiable with no variables" from "extraction crashed", and
the dictionary came back empty every time.

The call needs `d()` — call the declaration to get the constant:

```python
str(d): str(model.eval(d(), model_completion=True))
```

Verified: `{name: ..., age: '30'}` now populates. The fix also records
`model_values_error` instead of returning a plausible-looking empty dict,
so a future failure is visible rather than silent.

### 1b. The Z3 path never reported violations

`verify_constraints` documents `violations - Counter-example details (if
UNSAT)`. Only `PurePythonVerifier` populated it. The Z3 path — the one that
runs whenever `z3-solver` is installed, which is the normal case — never
set the key, so the documented contract held only on the fallback.

Z3 proves a formula unsatisfiable but does not say *which* input constraint
is responsible, so the counter-example is now derived from the supplied
values using the fallback's own rules. Both paths report the same
violations for the same input.

### 1c. `get_summary()["total_checks"]` was always 0

It read `self._pure.check_count` — the **fallback's** counter. Under Z3 the
fallback is never consulted, so the number stayed 0 regardless of how much
had been verified. A session summary reporting zero work done is the kind
of figure that gets believed.

Now `max(len(self._history), self._pure.check_count)`.

### 1d. A pre-existing failure this audit did not cause

With `check()` raising, CD1's `correlation_id matches instance` began
failing in the sequential runner. Running the **pre-change** file
standalone reproduces it exactly — the original printed `[FAIL] CD1:
correlation_id matches instance` and then exited 0 anyway, because its
return code was never consulted by anything.

So the mismatch predates this audit; what changed is that it is now
visible. The current failure mode there is a SQLite `database is locked`
when DirectMemory is used concurrently, which is a different and more
honest symptom than a silent correlation mismatch. Left as a real,
separately-triageable issue rather than papered over.

### 1e. Two smaller corrections

* The five test functions returned `dict`s, tripping
  `PytestReturnNotNoneWarning`. The values are preserved in a module-level
  `_CD_RESULT` slot for the `python file.py` report path; the test functions
  return `None`.
* `test_cd4` asserted `len(targets) >= 39` — the manifest's historical size
  rather than any property of the build. Replaced with a non-empty check,
  since the existence check immediately below is the real invariant.

Result: **5 passed** with real assertions, versus 5 unconditional passes.

The sequential `python tests/test_cross_domain_integration.py` path was
repaired at the same time. It read the dicts the test functions used to
return, and it would now abort on the first raised assertion — trading a
false PASS for a false early exit. Each stage is wrapped so a failing
domain is recorded and the remaining four still run; the exit code still
reflects the failure count. Both paths verified:

```
standalone : 55 checks, 55 passed, 0 failed, rc=0
under pytest: 5 passed
```

---

## 2. Build manifest: 9 of 39 entry points did not resolve

`scripts/build_all_concurrent.py` is load-bearing: `cd4_pipeline`
validates it and the Nuitka build consumes it. CD4's check for this had
been failing silently for the reason in §1.

The check names 3. There are **9**. They split into two kinds:

**Moved (2) — corrected.** Tracked in git at a new path, manifest still
pointed at the old one:

| Manifest said | Actually at |
|---|---|
| `src/CORE/WORMS/METRICZ.py` | `src/META/METRICZ.py` |
| `src/CORE/WORMS/CODEX_Studio.py` | `src/CODEX/CODEX_Studio.py` |

**Never existed (7) — commented out, not deleted.**
`config_validator`, `container_manager`, `migration_engine`,
`communication_bus`, `profiling_engine`, `telemetry_collector`,
`security_auditor`. Zero matches in any commit on any branch, zero on disk.
They are intentions, not moved files.

Verified after the change: 32 live entries, 0 missing, 7 commented, 0
commented entries that actually exist.

This does **not** make the Standalone Suite work. See §3.

---

## 3. `azazael-standalone` claimed 39 executables that do not exist

The skill's description read:

> AZAZAEL Standalone Suite — 39 independent .exe files for every AZAZAEL
> function, built with Nuitka.

`Desktop/AZAZAEL_Standalone/` contains **zero** `.exe` files. Neither does
`build_all.py`, which the skill named as the build entry point.

`nuitka-crash-report.xml` and `build_eve_2026-08-27.log` record why:

```
File ".../nuitka/plugins/standard/TransformersPlugin.py", line 196,
  in _getImportStructureDefinition
AttributeError: 'NoneType' object has no attribute 'key'
FATAL: transformers: Plugin issue while working on 'module transformers'.
```

This is upstream in Nuitka 4.1.2, triggered by a `transformers` import in
`EveUnleashed_Selector/eve_unleashed_app.py`. The 3.14t patches do not
address it. The skill has been rewritten to say NOT BUILT, name the
upstream error, and instruct against substituting a Python path silently.

---

## 4. `gen_everything.py` was generating a broken PowerShell launcher

Found via a syntax-warning sweep of all 211 `.py` files on `Desktop/`.
The file emits a PowerShell launcher; four of its string literals mixed
valid and invalid backslash escapes, and two of the valid ones were doing
real damage.

**Paths were corrupted.** `\t` and `\b` are *valid* Python escapes, so they
compiled without complaint while evaluating to a TAB and a BACKSPACE:

```
Exe="$US<TAB>emp_llama_cpp_build<BSP>uild_server_simple..."
```

Four literals affected (`\t` on the `$US\...` paths, `\b` inside
`\bin\Release`, and a `\n` that was becoming a newline mid-statement).
Doubling only the *invalid* escapes would have silenced the warnings while
leaving the corruption in place.

**The join was wrong.** `out.write_text('\\n'.join(lines))` wrote a literal
backslash-n, so the generated `.ps1` was a single 6 KB line instead of 37
lines. PowerShell cannot run that.

**One parse error remained** after both fixes, and it was pre-existing:
`"$k:$($s.Port)"` makes PowerShell read the colon as a namespace separator
and try to resolve a variable named `k:`. Corrected to `"${k}:..."`.

End-to-end verification, not just "the warning went away":

```
generated: 37 lines, 6038 bytes
control characters in output: 0
PSParser::Tokenize -> PARSE OK
```

The other warning source, `probe_all.py`, was **deliberately left alone**.
Its `\c` sits in a docstring that also contains `\\`; prefixing it raw
would have doubled the backslashes and changed the text. Recorded rather
than silently changed.

---

## 5. Environment: WSL is behind, and the premise was wrong

An earlier working note described 5 files existing only in WSL
(`tests/test_chain_lock.py`, `test_chain_refactor.py`,
`test_session_operations.py`, `test_morphing_learn.py`,
`scripts/run_full_pass.py` — 995 lines) and queued them for commit as
"Windows-behind" work worth recovering.

They were copied across and SHA-256 verified byte-identical. They should
**not** be committed. The measurements:

| | Windows | WSL |
|---|---|---|
| HEAD | `cac421dd` 2026-09-29 | `7d883ba` **2026-07-29** |
| dirty files | ~40 (live controller) | 1018 |
| untracked | — | 453 |

* WSL is **two months behind**, not ahead. "Windows-behind" is backwards.
* None of the 5 has ever existed in Windows git history.
* **2 of the 4 test files fail in WSL too** —
  `test_session_operations.py` cannot import `build_next_task_scaffold`
  and `test_morphing_learn.py` cannot import `MAX_GENOMES`; neither symbol
  exists in WSL either. They test code that exists in neither tree.
* `test_chain_lock.py` needs `_acquire_chain_lock`, which exists in WSL's
  842-line `run_azazael_chain.py` but not in Windows' 303-line copy.

These are abandoned experiments against code that was never written, not
lost work. The files were removed again after verification.

---

## 6. Known gap, not a bug: `invalidate_route` is unreachable

`MeshRouterWorm.invalidate_route` (`src/CORE/WORMS/expansion/mesh.py:258`)
is the only caller of `spine_registry.invalidate_q`. Nothing calls
`invalidate_route`. It is not dispatched through `execute()`. The single
reference in the codebase is a comment at `spine.py:2313`.

That comment is correct and should be preserved. It explains that an
earlier draft *did* call it on route failure, and that this inverts the
contract: `invalidate_route` exists to discount a penalty *because the
cause is fixed*, so firing it while a route is still failing would erase
the evidence at the exact moment the evidence says the route is bad.

Consequence, stated plainly: the evidence-floor machinery fixed in
`3a948a26` is correct and tested, but in production it is currently reached
by nothing. `capability_liveness` reports `invalidation_persisted: ok`
because the floors in the ledger are honoured on read — not because any
live path writes new ones. Wiring it needs a real repair path, which does
not exist yet. Recorded rather than "fixed" by adding a caller, because a
caller that looks wired and inverts the contract is the worse outcome.

---

## 7. What the audit found *clean*

Stated so the negative results are on the record:

* **211/211** `.py` files on `Desktop/` parse. Only the escape warnings in
  §4.
* **0** unresolvable internal imports across `src/`.
* `artifact_freshness` returns **1** when artifacts are made stale and **0**
  when fresh — bite-tested by touching a source file, not assumed. (An
  earlier reading of mine reported 0 here; that was `tail`'s exit code
  leaking through a pipe, not the tool's.)
* `capability_liveness` reports `unproven` rather than `ok` for the check
  it cannot settle.
* `tools/vacuous_check_audit.py` already exists and covers the
  vacuous-assertion class. Its HIGH list is mostly benign on inspection —
  `aggregate_suite_gate.py`'s two `except Exception: pass` are a pipe
  reader thread and a best-effort reap after the verdict is decided.
* The 12 assertion-free test functions found by AST scan are mostly
  legitimate *negative* tests ("must not raise") which do fail via
  exception. One flagged "all skipped" file (`test_cluster_worms.py`)
  actually passes 5/5 — my detector matched the substring `skip`.

---

## 8. Suite state

Full suite re-run after every change above: **245/245 files recorded, 14
flagged by the parallel runner**. Re-verified individually, per the
runner's own rule ("discovery in parallel, truth in sequence").

Four were parallel-worker artifacts and pass alone:
`test_code_evo_pilot`, `test_cross_nature_orchestration`,
`test_exmachina_monitor_split`, `test_mesh_audit_insights`.

**Nine fail when run alone. All nine are pre-existing.** Established by
stashing this audit's four source changes and running the identical
command — every one produced byte-identical results with and without my
work:

| Test | With audit changes | At baseline |
|---|---|---|
| `test_aoa_routing_telemetry` | 2 failed, 13 passed | 2 failed, 13 passed |
| `test_exmachina_mutagen` | 1 failed, 33 passed | 1 failed, 33 passed |
| `test_learning_evolution` | 1 failed, 74 passed | 1 failed, 74 passed |
| `test_morph_bypass` | 2 failed, 1 passed | 2 failed, 1 passed |
| `test_policy_advice` | 4 failed | 4 failed |
| `test_replay_path` | 3 failed | 3 failed |
| `test_spine_mesh_wiring` | 1 failed, 9 passed | 1 failed, 9 passed |
| `test_track_registry_consumers` | 3 failed, 1 passed | 3 failed, 1 passed |
| `test_wiring_cycle` | 3 failed, 17 passed | 3 failed, 17 passed |

**Zero regressions.** `test_cross_domain_integration.py` went from
5 unconditional passes to 5 real ones, and now passes.

### Why these nine cannot be triaged normally

**Most of the failing test files are untracked.** `test_morph_bypass`,
`test_policy_advice`, `test_replay_path`, `test_aoa_router_censored` are
machine output from the live `chain_controller`, not committed code. A
pristine `git worktree` at HEAD could not run them either — the controller
generates tests and their target modules together, both uncommitted, so
`git worktree` has neither. A test whose subject does not exist in version
control cannot be tested against version control.

`test_track_registry_consumers` and `test_wiring_cycle` *are* tracked, but
fail on missing modules that are themselves untracked.

`test_optimizers_convergence` is the known-benign case: it skips at module
level because mygrad→numba faults at C level in a free-threaded build, and
a segfault cannot be caught. The runner reports it separately for exactly
this reason.

**Recommendation:** stop the controller, or commit its output, before
treating any of these nine as a regression to fix. Right now the suite is
partly describing a filesystem rather than a commit, which is why the
baseline comparison above had to be done by stashing rather than by
checking out a revision.
