# Test backlog: real coverage mapping and triage (2026-09-12)

Closes ROADMAP **4.3** (backlog triage) and the mapping half of **4.2**
(mutation results were being paired with the wrong evidence).

---

## 1. What was wrong with the old testmap

`repo_audit.phase_testmap` asked one question:

```python
uncovered = sorted(m for m in src_mods if m not in blob)
# blob = the concatenated TEXT of every tests/test_*.py
```

Four independent defects:

1. **A mention is not a use.** Any occurrence of the name — a docstring, a
   comment, a variable, an unrelated word — marked the module covered.
   `tests/test_exmachina_mutagen.py` says the words "providers" and "scanner"
   in prose; both modules counted as tested on that basis.
2. **Basenames, not files.** `src_mods` is a `set` of basenames, so
   `src/HYDRA/ml_platforms/harness.py` and
   `src/ORCHESTRATION/ml_platforms/harness.py` collapsed into one entry.
3. **Blind to subprocess use.** `tests/test_scanner.py` runs
   `src/CORE/compliance/scanner.py` as a child process — a real test that never
   appears as an import and (under the old rule) only counted because the word
   happened to appear.
4. **The result was truncated.** Only `uncovered[:50]` was ever stored, so the
   262-module backlog was invisible until the budget fix.

## 2. The replacement: `scripts/import_map.py`

An AST parse of every project `.py` (~840 files, ~1s, cached per process):

* `direct[rel]` — the project modules a file **actually imports**, resolved
  through `src`-relative dotted paths *and* basename aliases (the suites put
  `scripts/` and `tests/` on `sys.path`, so `import budget_policy` is real).
* `path_refs[rel]` — files that name `rel` inside a **run/exec call**
  (`subprocess.run`, `os.system`, `runpy.run_path`, `importlib`, `exec`, …).
* `test_closure()` — everything reachable from a test module, transitively.
* `is_live(rel)` — has an importer, a run-reference, or is a runnable entry
  point.

### A false positive found while building it

The first version counted **every** `.py` string literal as a reference. The
test file for this very module names `src/tmp_verify.py` inside an assertion —
and that was enough to make a dead module look live. That is the *same*
false-positive class as the substring bug being fixed, so the rule was narrowed:
**a literal is a reference only inside a run/exec call.** A mention is not a
load. Guarded by `test_a_bare_mention_is_not_a_reference`.

## 3. Coverage, before and after

| | old (substring) | new (import graph) |
|---|---|---|
| src units | 435 **basenames** | 487 **files** |
| uncovered | 262 names | 312 files |
| evidence | name appears in test text | real import / run-reference |

More uncovered, not fewer — because the old number was measuring the wrong
thing. The honest reading: **175 of 487 src modules (36%) are reached by a
test.**

## 4. Triage result (`state/test_backlog_triage.json`)

Every one of the 312 gets exactly one verdict. **Unknown: 0.**

| verdict | count | meaning |
|---|---|---|
| `test` | 285 | live code no test reaches — the actual work item |
| `vendor` | 21 | not ours to hand-test |
| `delete` | 6 | dead-code candidates, review required |

`vendor` splits further, because they are not the same thing:
**vendored 0, generated 21, of which 8 are live** (`harness.py`, `launcher.py`,
`diagnostics.py`, `tensor_utils.py`, `vectorize_utils.py`,
`run_qanalysis.py`, …). All 21 carry the scaffolded header
`Author: Auto-generated` — this repo's **own** generator output, not
third-party code. That distinction matters: it means the fix is to test the
generator, not 21 generated files. `run_qanalysis.py` and `tensor_utils.py`
being live *and* untested is the one worth acting on.

### The 6 delete candidates

```
src/AOA/build_final.py
src/AOA/rebuild_html.py
src/CODEX/POPUPS/POPUP_SIMPLE.py
src/CODEX/VIDEOS/video_popup.py
src/CORE/LOCAL_DEV.py
src/SCRIPTS/lsp_diagnosis.py
```

Each has no importer, no run-reference, no name mention anywhere in the `.py`
tree, no reference from any `.bat/.ps1/.sh/.yaml`, and no `__main__` block.

**Deletion is not performed by the triage script and should not be automatic.**
A static import graph cannot see dynamic dispatch, and this repo loads modules
by *name* at runtime — the worm registry's `discover_worms()` walks the tree and
imports by string. "No importer" is therefore evidence, not proof. Every
`delete` row carries `requires_review: true` and `test_delete_candidates_are_flagged_for_review`
fails the build if that flag ever disappears.

## 5. Reproduce

```
python scripts/repo_audit.py            # -> state/test_backlog.json   (312 modules)
python scripts/triage_test_backlog.py   # -> state/test_backlog_triage.json (0 unknown)
python scripts/import_map.py            # coverage summary
python scripts/triage_test_backlog.py --show delete
```

Tests: `tests/test_import_map.py` (20 tests — resolution, aliases, duplicate
basenames, the subprocess channel, the bare-mention regression, and the triage
invariants).

## 6. Caveats

* The triage is a **snapshot** of one `test_backlog.json`. Re-run both scripts
  after adding or removing modules; a stale triage is worse than none.
* `test` is not "this module deserves its own test file". Many are reached by
  no test and used only by `scripts/` tooling — the verdict is "no test reaches
  it", which is the honest statement the roadmap asked for.
* The mapping resolves *static* imports. Modules reached only through
  `discover_worms()`, entry-point strings, or a `importlib` call with a
  computed name will read as uncovered — which is a real coverage gap in the
  signal, not a false claim about the tests.
