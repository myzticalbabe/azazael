# Graph-Assisted Audit — 2026-09-29

Three audit tools built to answer questions the call graph could not, and
what each one cost to get honest.

Supersedes nothing. Complements `NEURAL_MESH_AUDIT_2026-09-29.md`.

---

## What the graph can and cannot answer

Measured against `graphify-out/graph.json` (3,122 files, 47,411 nodes,
13,289 call edges):

| question | graph answer |
|---|---|
| where did this file move to | **yes** — instant, by basename |
| is this function called | partly — 7 of 7 call sites found for one probe, 1 of 7 for another |
| what breaks if I change this | **no** — `affected` missed a call on a line I could read |
| does this dict key ever get set | **no** — it indexes zero string literals |

The last row is the important one. `model_values`, `violations`,
`total_checks` and `summary` are all absent from the node labels, and there
is no string-literal node kind at all. That is correct scoping for a call
graph, and it means an entire defect class is outside its reach — the class
in which `cd2_verifier._z3_verify` built a model, threw it away, and
returned `{}` while appearing perfectly healthy in every graph query.

---

## Tool 1 — `tools/dead_function_check.py`

Functions in `src/` that nothing in the repository calls.

**Result: 161 functions** — 134 whose name appears nowhere at all, 27 whose
only mentions are string literals (dispatch tables). Plus 589 methods with
no static call edge, reported separately because "no caller" and "not an
entry point" are different claims.

### Six false-positive classes, each found by checking rather than trusting

1. **References were never recorded at all.** `real_references` was handed
   the empty `sites` dict as its *lookup table*, so every
   `candidates.get(name)` missed. Every candidate was reported dead no
   matter how often it was used. This is the bug that produced 789.

2. **Only `src/` was scanned for references.** `src/` is 745 of 1,273
   Python files; the other 528 are tests, tools and scripts, and they call
   into `src/` constantly. Any function exercised only by a test looked
   dead.

3. **A package `__init__.py` re-export counted as nothing.**
   `src/CORE/__init__.py` does `from .audit_trail import audit_gate_passed`
   — that publishes the name. The re-export set is now collected repo-wide,
   because the publishing module is not the defining module.

4. **`__all__` read only in its bare form.** `__all__: list[str] = [...]`
   is as common here as `__all__ = [...]`. Missing the annotated form
   flagged exported functions as dead, contradicting the module's own
   contract.

5. **The `Class.` prefix defeated every exclusion.** A method's graph label
   is `Arm.execute`; comparing that whole string against `FRAMEWORK_HOOKS`
   and `TOO_COMMON` never matches. Every `execute`, `health` and `run`
   method bypassed both filters. This was most of why the method list ran
   to 2,817.

6. **pytest hooks and conftest have no caller by construction.**
   `pytest_configure` is called by pytest, not by code.

A trap worth recording: `src/CORE/STRUCTURE.py` looks like it declares
`__all__` at line 6, and grep confirms `create_structure` there. It does
not — the `__all__` is **100 lines up inside a 102-line module docstring**.
The AST was right and the grep was wrong. Same shape as an earlier
`__all__` false positive in this session.

### Independent verification

A separate brute-force AST scan (`/tmp/verify_dead.py`, not sharing the
tool's resolution logic) disagreed on 27 of 161 candidates. All 27 are
string-literal mentions, which the tool already classifies separately, and
all are explained: `cmd_worms` and friends are dispatched by name from
`klink.py`'s dispatch table; `tchebycheff` has a docstring admitting *"no
production caller and no test"*; `_reload_paths` appears in a conftest
comment. Two are Windows case-folding artifacts of the verifier
(`KLINK` vs `klink`), not tool errors.

---

## Tool 2 — `tools/manifest_reconcile.py`

Reconciles `BUILD_TARGETS` in `scripts/build_all_concurrent.py` against
disk and the graph, distinguishing three outcomes rather than pass/fail:

- **ok** — the path exists
- **moved** — it does not, and the graph found where it went
- **missing** — it does not, and nothing shares the basename
- **ambiguous** — several files share it, and no evidence distinguishes them

**Result: 32 entries, all resolve.** The 9 stale entries were fixed in
`d6c3203c` (2 paths corrected, 7 never-implemented targets commented out).

Reporting *ambiguous* rather than picking one is deliberate: a guess in a
build manifest is worse than no report, because it is indistinguishable
from a fact once written down.

### The vacuous-truth failure

The first version printed **`OK: every declared manifest entry resolves`
having extracted zero entries**, because it read `X = {...}` while the
manifest is `X: Dict[str, Dict] = {...}`. "Every entry resolves" is
trivially true of an empty set.

Fixed, plus an explicit guard: zero entries is now `INCONCLUSIVE` (rc 2),
not `OK` (rc 0). All four mutations of this tool bite.

---

## Tool 3 — `tools/dict_key_contract.py`

Reports dict keys read but never written within a function, and vice versa.
This is the class the graph structurally cannot see.

**Result: 3,464 candidates across 532 modules.** These are *questions*,
not defects, and the tool says so on every run.

### Getting from 23,027 to 3,464

- 23,027 → count keys only on dicts the module **constructs**. A subscript
  on a name from elsewhere is a dict whose keys this module cannot see.
- 13,634 → census per **(function, dict)** rather than per module. A dict
  built in one method and read in another is the normal shape here;
  `worm_result` alone crosses four methods in `NATURE_CLUSTERS.py`.
- 8,790 → exclude dict **parameters**. Their keys are the caller's
  business.
- 7,345 → exclude **returned literals**, which callers read by
  definition. That alone was 7,119 of 13,634 — over half the report, all
  of it structurally meaningless.

### What it cannot do, stated plainly

A docstring promise is not code. The `get_summary()["total_checks"]` bug —
a key the docstring advertises that no path sets — is **not** detectable
by a key census, and a test asserts that the tool does not claim it.

The real `model_values` bug is symmetric-but-empty: the key is written on
the happy path and read by the caller, so both sides agree. Only
reachability analysis would catch it, and this tool does not do that.

---

## Finding: stale unlinked duplicates at the repo root

**21 tracked `.py` files sit at the repository root. 8 shadow a same-named
file elsewhere, and all 8 differ in content.**

```
NATURE_CLUSTERS.py      vs  src/CORE/WORMS/NATURE_CLUSTERS.py       DIFFERS
health_server.py        vs  src/CORE/health_server.py               DIFFERS
PamsRecorder.py         vs  src/CORE/PamsRecorder.py                DIFFERS
METACLUSTER.py          vs  packages/.../clusters/METACLUSTER.py    DIFFERS
_worm_execution_matrix.py, _worm_health_check.py, metrics.py, run_tests.py
```

The root copies were last touched **2026-09-06**; the `src/` copies
**2026-09-28**. Nothing in `src/`, `tests/`, `tools/` or `scripts/` imports
any of them (0 top-level imports each).

This is not cosmetic. It is why `dict_key_contract` initially reported
`NATURE_CLUSTERS.py:706` when the reader would have
`src/CORE/WORMS/NATURE_CLUSTERS.py` open — **the line numbers pointed at
the wrong file**. All three tools now scope to `src/ tests/ tools/
scripts/` explicitly and print their scope on every run.

**Not fixed here.** Deleting tracked files is not mine to do unprompted,
and `archive/` and `archived*/` legitimately hold historical copies. The
eight root-level ones are candidates for removal on the next pass.

---

## Verification

33 tests in `tests/test_graph_tools.py`. **8 mutations, all 8 bite** —
reintroducing each shipped bug fails at least one test:

| | mutation | result |
|---|---|---|
| M1 | attribute references never recorded | bites |
| M2 | reference scan limited to `src/` | bites |
| M3 | framework hooks no longer excluded | bites |
| M4 | annotated assignment no longer read | bites (2) |
| M5 | empty-result guard removed | bites |
| M6 | ambiguity reported as a guess | bites (2) |
| M7 | `dict_key` empty-result guard removed | bites |
| M8 | parameter dicts no longer excluded | bites (2) |

Two of the 33 tests assert capabilities the tools **do not** have — a
docstring promise is not a key, and a parameter dict is out of scope. A
suite that only checks working cases would have passed against all three
broken tools.

### Timeline cost

Each of these tools shipped with a false PASS and was caught by checking
its output against the filesystem rather than by its own tests. That is the
same failure mode as `test_cross_domain_integration.py`, whose `check()`
helper printed `[FAIL]` and incremented a counter nothing asserted on: a
tool that reports success without a test that can observe its failure.
