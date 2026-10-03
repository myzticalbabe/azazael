# Error → Lesson audit — 2026-10-03

Does each recorded error have its lesson **learned** and **applied**? "Applied"
is held to Lesson #86's own standard: this codebase *documents* what it learned
better than it *checks* it still holds. So a prose "Prevention" section does not
count. A lesson counts as applied only when a **mechanism that can catch its
recurrence** exists — a test, a guard, a scanner, a gate — and that mechanism is
demonstrably wired in.

## Method

- Inventory: 160 unique `## Error #N` entries in `ERROR_LOG.md` (range #16–#218).
- Cluster by title keyword (an entry may belong to more than one class; the
  dominant class is used).
- For each cluster, three probes:
  1. **Mechanism?** — does a test / guard / tool exist for the class?
  2. **Wired?** — is that mechanism referenced from the code it protects?
  3. **Recurred after writeup?** — did the same class re-appear *after* the entry
     that supposedly closed it? Recurrence is the strongest evidence of "not
     applied", because it is measured, not inferred.
- Limitations: title-keyword clustering is coarse; "wired" is checked by
  existence and reference, not by mutation-testing each guard.

## Cluster scorecard

| cluster | entries | mechanism exists? | wired? | recurred after writeup? | verdict |
|---|---|---|---|---|---|
| 3.14t wheel / ABI / free-threading | 8 | **YES** — `src/CORE/native_guard.py`, child-process probe | yes — engram, onnx_integration, eve_unleashed, error_triage | no (the Oct-2 guard caught the live onnx segfault) | **APPLIED** |
| memory / recording channel | 15 | **YES** — `test_memory_db_isolation`, `test_memory_db_module_teardown`, `test_memory_dir_caching`, `test_pams_recorder`, `test_record_retry`; now `tools/pmb_client.py` | yes | **YES** — #196 recurred 2026-10-03 in a module-scope shape the conftest fixture could not see | **CLOSED THIS SESSION** |
| test isolation / aggregate | 5 | **YES** — `test_aggregate_suite_gate`, `test_ci_two_interpreter_gate` | yes | partially (#84-class red-only-in-aggregate recurred 2026-10-03; localized and fixed) | **APPLIED (strengthened)** |
| VLP / audit | 8 | **YES** — `test_aoa_session_audit`, audit-trail + Ed25519 + Merkle | yes | gaps G1–G5 recorded, fixes landed | **APPLIED** |
| G: drive / file ops | 3 | partial — `azazael-crossplat-fileops` skill, no test | no | no recent | **DOCUMENTED ONLY** |
| code defect (one-off logic) | 7 | n/a — each is a distinct bug | n/a | no | **LEARNED (no recurrence class)** |
| shell / path escaping | 6 | **NO** — three skills (`azazael-fix-gitbash-paths`, `azazael-powershell-escape`, `azazael-crossplat-fileops`), **zero tests or lints** | no | low recent recurrence | **NOT MECHANIZED** |
| process violation (gemini / gate / sentinel / mandate) | 39 | **YES** — `sentinel_enforcer.py`, `compliance_auditor.py`, 13 gate/compliance tests | yes | **YES** — #210 (Sept 30) "RULE 0B violated 3× because it was never opened"; #218 (Oct 3) TEST_FAILURE_MANDATE not executed | **NOT APPLIED** |
| anti-pattern backlog | 54 | **YES** — `src/CORE/compliance/scanner.py` (RULE 0X-7, AST, 7 categories) + `tests/test_scanner.py` + `scripts/worm_pre_commit_hook.sh` | **NO** — the pre-commit hook is **not installed** in `.git/hooks/` | backlog partly reduced, 2,224 findings remain | **MECHANIZED BUT NOT ENFORCED** |

## The four genuine gaps

### 1. Anti-pattern backlog — 54 entries, MECHANIZED but NOT ENFORCED

**Correction to the first version of this audit, which claimed there was no
scanner. That was wrong.** `src/CORE/compliance/scanner.py` is a full RULE 0X-7
AST scanner covering exactly the seven categories #81–#86 recorded, with
`tests/test_scanner.py`, a `--fail-on`/`--ci` exit code, and a
`scripts/worm_pre_commit_hook.sh` that runs it as check 3 of 5.

What is actually true, measured by running the scanner over `src/`:

| category | findings now | backlog entry | note |
|---|---|---|---|
| `unicode_emoji` | **1,260** | #81 (2,378), #94–#143 | still large |
| `import_inside_function` | **950** | #83 (564) | grew past the recorded figure |
| `hardcoded_win_path` | **14** | #85 (56) | reduced |
| `t_string` | **0** | #82 (45) | **driven to zero** |
| `os_system` | **0** | #84 (5) | **driven to zero** |
| `cls_new` | **0** | #86 (4) | **driven to zero** |

So the mechanism exists and three categories were fully closed. The gap is
**enforcement**: `.git/hooks/pre-commit` is absent, so the hook script never
runs, and the default `pytest` suite does not gate on the scanner. A commit that
adds 500 emoji still passes. This is Lesson #86 in its purest form — the check
was built and is not wired to anything that blocks.

### 2. Process violations — 39 entries, the class recurred into October
`sentinel_enforcer.py`, `compliance_auditor.py` and 13 gate/compliance tests
exist, so the mechanism is real. It is nonetheless violated repeatedly — #74–#96
and #144–#159 in June, then #210 (Sept 30) and #218 (Oct 3). The gate is
**available and not enforced at the point of action**. Error #210's own words:
RULE 0B "was violated three times because it was never opened."

This session added one more instance (#218). The mechanism's existence is not the
problem; nothing forces the agent through it before a write.

### 3. Shell / path escaping — 6 entries, three skills, zero checks
`azazael-fix-gitbash-paths`, `azazael-powershell-escape` and
`azazael-crossplat-fileops` are thorough. There is no test or lint for the class.
Low recent recurrence, but the class is held only by prose.

### 4. G: drive / file ops — 3 entries, skill only
Same shape as (3): `azazael-crossplat-fileops` documents the shutil/robocopy
hazards (#53, #58, #89); no mechanism.

## What is genuinely applied

- **3.14t / native-wheel safety** is the model for the rest. #48–#54 were
  scattered ad-hoc guards; `597d9eb1` centralised them into `native_guard.py`,
  and the consolidation immediately found a **live segfault** (unguarded
  `onnx`/`onnxruntime` import, `rc=0xC0000005`). A mechanism found a real defect
  the docs had not.
- **Memory DB-path isolation** was closed for the per-test shape in September and,
  this session, for the **module-scoped** shape it could not previously see
  (`test_memory_db_module_teardown.py`), plus the pmb client that survives a
  daemon restart.
- **VLP / audit** and **test-isolation** clusters have real, wired mechanisms.

## Recommendations, in priority order

1. **Enforce the scanner that already exists.** Install
   `scripts/worm_pre_commit_hook.sh` as `.git/hooks/pre-commit` (or add the
   scanner to the CI/test gate). The mechanism is built and thorough; it is simply
   not connected. Then ratchet: record the current counts (1,260 / 950 / 14) as a
   baseline and fail on increase, the way `tools/type_check_gate.py` does.
2. **Force the process gate to the point of action.** The gate exists; make the
   write itself impossible without a fresh permit — which is what
   `tools/prepare_guard.py` already attempts for canon files. Extend it to
   `str_replace`/`write_file` targets rather than relying on the agent to run it.
3. **Add a shell-escaping regression test.** A small pytest that runs the
   documented dangerous invocations (backslash paths, `$` in PowerShell, MSYS
   translation) against a temp dir. Cheap, and it converts three skills into one
   check.
4. **Keep the 3.14t pattern as the template.** When closing a class, add the
   mechanism in the same commit; the mechanism is what finds the next defect.

## Honest limitation

This audit measures mechanism **existence and wiring**, not mechanism
**effectiveness**. A guard that cannot fail (Lesson #86) would pass this audit.
Mutation-testing each guard is the natural next step and was not done here.

It also **got one finding wrong on the first pass**: it asserted the anti-pattern
backlog was unmechanized when `src/CORE/compliance/scanner.py` already existed
and had closed three of the six categories. The error was reading the cluster
by *title keyword* and concluding "no scanner" from the absence of a file named
`anti_pattern*.py` — an inference, not a measurement. The correction came from
running the scanner, not from re-reading the log. That is itself the audit's
thesis: measure, do not infer.
