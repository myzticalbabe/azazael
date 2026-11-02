# AUDIT — tests/ (2026-11-02)

**Auditor:** worker 10 of 18, full-audit fan-out.
**Scope:** `C:/Azazael/azazael/tests/`, `pytest.ini`, root `conftest.py`.
**Status: READ-ONLY. Nothing was executed.** No test was run, so no test in this
document is described as passing or failing except where a prior run in this
session is quoted as a measurement with its command.

---

## 0. Instrument warning, stated first because it limits this document

`code_search` returned **0 matches** for `negative|RULE 0B-C` scoped to `tests/`,
while the string `RULE 0B-C` is verbatim at `tests/test_prose_forensics.py:4`,
which I read directly. The same search tool *did* return correct results for
simple single-token patterns (`pytest.mark.skip`, `Users.clint`,
`mark.timeout`). Conclusion: **alternation and `-l` patterns silently return
zero in this environment.** Every "no matches" in this report is therefore a
statement about the tool, not about the tree, unless a file read confirms it.

Where a count could not be established by reading, this document says
**NOT ENUMERATED** rather than quoting a guess. The command that would settle
each is named.

---

## 1. Inventory

`pytest.ini` sets `testpaths = tests`, so a bare `pytest` collects **only**
`tests/`. The directory holds several hundred `test_*.py` modules plus support
files (`conftest.py`, `_env_315t.py`, `_timer_utils.py`, `ADLP_Test.py`,
`ML_GUI_Test.py`, `benchmark_autodiff_modes.py`, `autodiff_skills_check.py`).

Exact module count: **NOT ENUMERATED.** `pytest --collect-only -q | tail -1`
produces it.

**Grouping is by subsystem, not by layer** — roughly: `test_aoa_*`, `test_psyche_*`,
`test_eve_*`, `test_spine_*`, `test_mesh_*`, `test_grpo_*` / `test_learning_*` /
`test_evolution_*`, `test_worm_*` / `test_cluster*`, `test_compliance_*` /
`test_*_gate.py` (the commit/preflight gates), `test_*_sota_rows.py` (ledger row
walkers), and one `test_*.py` per instrument under `tools/`.

### 1.1 A coverage gap the suite documents about itself

Root `conftest.py:1-50` states that `src/tests/` holds **14 test modules and its
own `__init__.py`**, and that it had no conftest — so its fixtures wrote into the
live choice tap (408 of 608 `spawn_selected` rows were unit-test fixtures). The
root conftest was added to contain it.

But `pytest.ini`'s `testpaths = tests` still **excludes `src/tests/` from every
default run**. The containment is fixed; the *coverage* is not. Those 14 modules
execute only under IDE discovery or an explicit `pytest src/tests/...`, which the
conftest's own docstring calls "exactly the runs nobody watches." A test that is
contained but never run is a test that cannot fail.

---

## 2. Count and derived-number assertions — the live exemplar

`tests/test_prose_forensics.py` is the clearest case in the suite, and it is the
one that actually broke this session.

**The failure, quoted from the run:**
`pytest tests/test_receipt_guard.py tests/test_delegation_trace_ids.py tests/test_prose_forensics.py`
→ `46 passed, 1 failed`; failure is
`test_prose_forensics.py::test_stage_directions_are_removed_and_counted`,
`assert 6 == 5`.

**The class:** the test pins hand-counted numbers — `words == 19`,
`sentences == 4`, `mean == 4.75`, `pct_under_9 == 75.0`, `max == 10`,
`negation_per_1000 == round(2*1000/19, 2)` (lines 32-46). Any change to
tokenisation or sentence splitting moves several of these at once, so one
behaviour edit produces a wall of red that reads like five defects.

### 2.1 Why this matters for the repair: the failure is not explained by the code as read

I traced `split_sentences` (`tools/prose_forensics.py:196-230`) by hand over the
exact fixture (`test_prose_forensics.py:49-52`):

| step | boundary | sentence |
|---|---|---|
| `three.` → `Four` uppercase | split | "One two three." |
| `seven.` → `This` uppercase | split | "Four five six seven." |
| `bad.` → `Eight` uppercase | split | "This is not very good and it is not bad." |
| `nine.` → `(` | split | "Eight nine." |
| `(Applause.)` terminal is last char → `next_index >= length` → `break` | tail | "(Applause.)" |

That is **5 sentences**, and `measure` returns `"sentences": len(sentences)`
verbatim (`tools/prose_forensics.py:283`). So the current source should produce
5, and the run reported 6.

**Do not resolve this by editing the assertion from 5 to 6.** That converts a
control into a rubber stamp, which is the defect this file exists to prevent
(its own docstring: an instrument that quietly miscounts "is indistinguishable
from an argument"). The repair must print the actual split:

```bash
python -c "import sys; sys.path.insert(0,'tools'); import prose_forensics as P; \
t=('One two three. Four five six seven. This is not very good and it is not bad. '
   'Eight nine. (Applause.)'); print(P.split_sentences(t)); print(P.measure(t)['sentences'])"
```

Until that runs, the honest state is **UNEXPLAINED-BY-READING**: either the file
changed between the worker's edit and the run, or a stale `__pycache__/*.pyc`
was loaded by the free-threaded interpreter. Both are ordinary causes; neither
is excluded.

**Siblings: NOT ENUMERATED.** `["sentences"]` appears only in this file (3
hits), but the general class — `assert <derived> == <literal>` — is spread
across the suite and was not swept, because the alternation search needed for it
is the pattern this environment silently zeroes.

**Structural recommendation:** where a metric is legitimately expected to move,
assert the *relationship* (monotonic, or "stripped < untouched") rather than the
literal, and keep one file of pinned hand-counted numbers as the control. That
keeps the control strong and the brittleness in one place.

---

## 3. Timeouts — the suite is bounded (positive finding)

This is the one class that is clean, and it is clean deliberately.

`pytest.ini` sets:

```
timeout = 120
timeout_method = thread
faulthandler_timeout = 20
```

- **Every test is bounded at 120 s.** No `@pytest.mark.timeout(...)` override
  exists anywhere in `tests/` — verified by search (0 hits), so nothing disables
  the bound. That is the check that would have caught a test opting out.
- `timeout_method = thread` is the choice that dumps **all** stacks, and the
  file records why: it named `governance.py:791` in one run instead of costing a
  session of guessing.
- `faulthandler_timeout = 20` is a CORE pytest option requiring no plugin, so a
  hang still yields a traceback on an interpreter without `pytest-timeout`.
- The file's header records that the previous `-n auto` addopt **broke argument
  parsing** on an interpreter without `pytest-xdist` — so the suite reported
  nothing at all, "not a skip, not a failure." Its removal is correct and the
  reasoning is sound; parallelism is now opt-in per interpreter.

### 3.1 One residual risk in this class

`@pytest.mark.slow` is applied **12 times across 6 files**
(`test_cluster_integration_p1.py:57,424,442`, `test_cross_domain_integration.py:645`,
`test_inference_integration.py:976`, `test_parallel_integration.py:39,50,112,138,248`,
`test_spine_mesh.py:737`, `test_spine_heart_isolation.py:47`). Several carry the
comment *"solo process"* / *"starts a LIVE heart"*. They are **not deselected by
default**, and root `conftest.py` records that torch construction on worker
threads **access-violated on 3.15** (a crash, which no per-test timeout can
catch). So `pytest -n auto` on 3.15t is not merely slower or faster — it is
unsafe with these tests collected. The `slow` marker is registered, but nothing
enforces "these must not be parallelised."

---

## 4. Host-absolute paths and live stores

### 4.1 Live stores: contained at the root, with one deliberate escape hatch

No test file references `memory_store.db` or `AZAZAEL_MEMORY_DIR` directly
(0 hits) — because containment lives in `conftest.py`, not in each test. That is
the right design: root `conftest.py` sets `AZAZAEL_GENERATED_DIR`,
`AZAZAEL_ENTRENCHMENT_PATH`, `AZAZAEL_MEMORY_DIR` and `AZAZAEL_NO_HEART` **at
import time**, before any test module imports the modules that read them
(`CORE.local_memory` computes `DB_PATH` at import).

**The escape hatch, named on purpose:** each override is
`if not os.environ.get(...)`. An operator who exports `AZAZAEL_MEMORY_DIR` to the
live store gets exactly the 408-row contamination the file was written to
prevent, with the suite green. Worth an explicit refusal (compare the resolved
path against the live store and fail closed) rather than a silent honour.

### 4.2 Absolute paths: 31 hits, and one is a genuine portability defect

Most hits are **deliberate** and I am not calling them defects:

- `test_shell_path_escaping.py:95-110,195-203` — asserts on how bash mangles
  `C:\Users\clint\x.txt`. Platform-specific **by design**, and it is itself
  guarded by `requires_bash = pytest.mark.skipif(...)` at line 74.
- `test_operator_scoring.py:57,105,115,267-269` — decoy paths, i.e. the negative
  control for a path classifier.
- `test_tmp_divergence.py:11-12`, `test_git_tools.py:569-570` — expectations and
  recorded measurements, not live dependencies.
- Six files carry `/c/Azazael/.venvs/py315t/Scripts/python.exe` **in docstrings
  only**, as the recommended run command. No runtime effect.

**The real defect:** `test_agent_orders_sync.py:172,175` asserts
`"/mnt/c/Users/clint" in text` and `"python3 /mnt/c/Users/clint/_board.py"`.
This hard-codes both the Windows username and the WSL mount layout into an
assertion. It will fail for any other user, and it is the one host-identity
assertion in the suite that is not a declared fixture. For a tree being prepared
for publication this should be parameterised on the resolved home, or marked
`env`.

---

## 5. Skips that can hide a defect

17 skip/xfail sites. They are not equivalent, and two shapes matter.

### 5.1 Anti-skip monkeypatches (5 sites) — deliberate, and worth keeping

`test_config_and_breaker.py:21`, `test_clusterworms_unit.py:37`,
`test_worm_execute_all_integration.py:41`, `test_worm_governance_integration.py:42`,
`test_worm_registry_integration.py:37` all assign
`pytest.mark.skip = lambda *a, **kw: lambda f: f`.

That **neutralises `skip()` inside those modules**, turning a skip into a run.
Note the limit: it patches only `skip`, not `skipif` — so a `skipif` in those
files still skips silently. Worth knowing before trusting a green run there.

### 5.2 `skipif(<module> is None, reason="not importable")` — the defect-hiding shape

- `test_exmachina_operators.py:24`
- `test_provider_failover.py:112`

If the module fails to import because of a **real regression**, the file skips
**green**. Nothing distinguishes "not installed" from "imports are broken", which
is the exact failure class the project's own 0B-D rule names. Recommendation:
turn these into failures when the module is expected present, and gate the
environmental case on the **registered `env` marker** so it is countable
(`pytest -m env`), rather than on an import that can rot.

Other environment skips — `test_era_windows.py:10` (whole file),
`test_git_tools.py:74,77`, `test_mesh_html_view.py:57,62`,
`test_onnx_export_refuses_to_fabricate.py:64,87,106`,
`test_pipeline_provenance_capsule.py:49`, `test_shell_path_escaping.py:74` — are
declared with reasons and are the defensible shape.

### 5.3 A registered marker that is not enforced

`pytest.ini` registers `slow`, `nuitka_incompatible`, `env`, `order` — good — but
does **not** enable `--strict-markers`, and says so: enabling it today "turns
every unregistered mark in the existing suite into a collection error." The file
also records that `test_parallel_integration.py:450` and
`test_inference_integration.py:1054` inspect `obj.__pytestmark__` **by the string
name** `"slow"`. So a typo'd mark does not error — those two checks silently stop
excluding slow tests, and the run stays green. This is a latent defect the
project has already written down; it is unchanged.

---

## 6. Negative controls

`tests/test_prose_forensics.py` is the exemplar and it is a **real** control, not
a shape:

- a hand-counted fixture the instrument must reproduce **exactly** (arithmetic
  checkable by eye);
- a bad control — `--start-after` with an absent marker must return **3**
  (refuse), not measure the whole page (`test_missing_trim_marker_is_refused_not_ignored`);
- an explicit "the marker must exist or the control proves nothing" guard at
  line 51, which is the check most negative controls omit.

**Coverage across the rest of `tests/`: NOT ENUMERATED.** The sweep needed
("negative control", "known-healthy", "must not fire") is exactly the alternation
pattern this environment zeroes, and only 0 matches came back while the phrase is
provably present in a file I read.

The structural mitigation already exists and should be used instead of a sweep:
the `env` marker separates "fails without an environment" from "fails on
regression", which is the property a negative control is meant to give.

---

## 7. Summary

| Class | State | Evidence |
|---|---|---|
| Timeouts | **Bounded, deliberately** — 120 s per test, stack-dumping method, plugin-free fallback; no overrides found | `pytest.ini` |
| `slow` tests under `-n auto` | **Unsafe on 3.15t** — live-heart/torch tests can AV, which no timeout catches | 12 marks, `conftest.py` torch note |
| Count assertions | **Brittle** — exemplar failing now and **not explained by the code as read** | §2, `test_prose_forensics.py` |
| Live-store containment | **Correct at rootdir**, with a silent env escape hatch | root `conftest.py` |
| Host paths | Mostly fixtures; **1 real portability defect** | `test_agent_orders_sync.py:172` |
| Skips | 5 anti-skip patches (fine); **2 `skipif(import)` sites hide regressions** | §5 |
| Marker enforcement | **Not strict**; documented silent-marker risk unchanged | `pytest.ini` |
| `src/tests/` | **Contained but excluded** from the default run — 14 modules | `conftest.py:1-50` |

**Three actions, in order:**
1. Print the actual `split_sentences` output for the failing fixture **before**
   touching either the test or the splitter, and never relax `== 5` to `== 6`.
2. Convert `test_exmachina_operators.py:24` and `test_provider_failover.py:112`
   from "skip if not importable" to an `env`-marked failure.
3. Decide whether `src/tests/` runs anywhere. If not, say so in `pytest.ini`;
   a silent exclusion reads as coverage.

*Nothing was executed. No test here is reported as passing.*
