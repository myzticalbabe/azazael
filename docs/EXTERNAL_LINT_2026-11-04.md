# External lint + mutation probe — measured 2026-11-04

Two instruments added because every gate in this tree was written by this tree.
A family of instruments that agrees with itself has proved only that it is
consistent: `ast_audit` counting 5,488 parsed files says nothing about whether
the scanner would notice a bare `except: pass` in any of them.

| file | what it is | status |
| --- | --- | --- |
| `tools/external_lint.py` | ruff + pyflakes over a path list; report only | new |
| `tools/mutation_probe.py` | plants 14 defect classes, scores 3 detectors | new |
| `tests/test_mutation_probe.py` | control, rule-level catches, verdict logic | new, 7 tests |

Provenance for every number below:

```
C:/Azazael/.venvs/py315t/Scripts/python.exe  (3.15.0rc3, sys._is_gil_enabled() = False)
ruff 0.17.3        pyflakes 4.1.0        HEAD 67a6d912, branch deepseek-engram-813
python tools/external_lint.py --paths src --json state/external_lint.json   -> exit 0
python tools/mutation_probe.py --json state/mutation_probe.json             -> exit 0
python -u -m pytest tests/test_mutation_probe.py -q --timeout=120           -> 7 passed in 0.47s
```

Neither tool is wired into the commit hook. A new blocking gate needs a registry
row and a recorded baseline, and the point of this pass is to look at the debt
before ratcheting it.

## Reading 1 — ruff + pyflakes over `src` (789 files)

```
ruff      13,280 findings      pyflakes  1,216 findings
UP006 3580  BLE001 2183  UP035 1042  UP045 1030  UP031 929
F401   854  I001    802  UP009  411  PLW1510 275  UP017 190  N999 176  UP037 176
F821     3  (undefined name -- the interesting column, see below)

pyflakes: unused_import 876 · unused_variable 116 · redefinition 91 · other 72
          fstring_no_placeholder 49 · star_import 9 · undefined_name 3
```

The bulk is modernization noise (`UP*` typing syntax, `I001` import order,
`BLE001` broad except). It is debt, not breakage, and it is not this pass's job.

### A mislabel in the new file, found and fixed the same day

The first run reported `undefined_name = 9`. Reading those nine lines showed
every one was a `from X import *` note ("unable to detect undefined names"),
while the **3 genuine undefined names were hiding in `other`**: the star-import
needle contains the substring `undefined name`, and it was checked first.

Fixed by giving star imports their own label and letting the narrower needle win
(`tools/external_lint.py`, `_pyflakes_bucket`). The arithmetic is the proof that
only labels moved and no finding was created or lost:

```
before:  undefined_name 9   other 75      total 1,216
after:   undefined_name 3   star_import 9   other 72    total 1,216
```

A count that names the wrong family is HED-3's defect in the reading, not a
cosmetic label.

## Three live defects the oracle found (not fixed here)

`ruff` and `pyflakes` are independent implementations and they agree on all
three, which is why they are worth more than either alone. Each was read at the
cited line before being accepted.

1. **`src/CODEX/comprehensive/GENERATE_ALL_11.py:416`** — `Path` is undefined
   inside the `except ImportError:` fallback. If the primary
   `from CORE.paths import get_desktop_dir` ever fails, the recovery path raises
   `NameError` instead of recovering.
2. **`src/CODEX/comprehensive/GENERATE_RICH_HTML.py:496`** — identical shape,
   identical consequence.
3. **`src/ORCHESTRATION/scripts/generate_docstrings.py:110`** — `directory` is
   undefined. `def process_directory(directory)` keeps only its docstring as a
   body (`results = {...}` and the `rglob` loop dedented out to the enclosing
   scope), so the function returns `None` and the loop below it runs where
   `directory` does not exist. This one is a broken function, not a broken
   fallback.

They are recorded rather than repaired because they sit outside this lane's turf
(`CODEX/`, `ORCHESTRATION/`) in a worktree carrying 152 foreign dirty paths, and
a half-verified repair inside another lane's files is worse than a named defect.
The queued rows are the right owner's work.

Note the class: **the canonical scanner cannot see any of them.** Its 21 rules
are house anti-patterns — emoji, `os.system`, silent excepts, unbounded waits —
not dead or undefined names. The `NameError` that HED-1 says lived for months was
in exactly this blind spot.

## Reading 2 — mutation probe: what each detector actually catches

14 mutants, each planted in a temporary copy of one clean fixture, plus that
clean fixture as the negative control.

```
[CLEAN   ] control     0 finding(s) across 3 detector(s)
[OK      ] emoji_in_string          scanner(unicode_emoji)
[OK      ] os_system_call           scanner(os_system)
[OK      ] shell_true               scanner(shell_true) ruff(PLW1510)
[OK      ] subprocess_no_timeout    scanner(subprocess_no_timeout)
[OK      ] open_no_encoding         scanner(open_no_encoding)
[OK      ] silent_except_pass       scanner(silent_except_pass)
[OK      ] except_return_default    scanner(except_return_default)
[OK      ] cls_new_factory          scanner(cls_new_factory)
[OK      ] hardcoded_win_path       scanner(hardcoded_win_path)
[KNOWN   ] raw_windows_path         caught by nothing (recorded gap, below)
[OK      ] unused_import            ruff(F401,I001) pyflakes(unused_import)
[OK      ] unused_variable          ruff(F841) pyflakes(unused_variable)
[OK      ] undefined_name           ruff(F821) pyflakes(undefined_name)
[OK      ] fstring_no_placeholder   ruff(F541) pyflakes(fstring_no_placeholder)

scanner 9/14   ruff 5/14   pyflakes 4/14
verdict: COVERED (13/14 caught, 1 known gap, control clean)   exit 0
```

The two columns are complementary, and that is the finding:

- the **scanner** owns all 9 house anti-patterns and is blind to all 4 dead-name
  classes;
- **ruff + pyflakes** own the 4 dead-name classes and catch only 1 of the 9
  house patterns (`shell_true`, incidentally, via `PLW1510`).

Neither is redundant, and the union is what a gate needs.

### The recorded gap

`raw_windows_path` (`RAW_ROOT = r"C:\Users\clint"`) is caught by nothing.
`_PATTERN_WIN_PATH` is `r'[Cc]:\\\\'` — **two** backslashes in the file text — so
it sees the ordinary `"C:\\Users"` spelling and is blind to the raw-string form,
which is the spelling this tree prefers; neither external leg flags a hardcoded
path at all. It is annotated in `MUTANTS` with `known_gap=` so the run stays
green on an accepted gap while an *unexplained* hole still exits 1. A mutant that
starts being caught is reported `CLOSED` and the annotation is removed.

### An instrument found an inconsistency in the scanner

While landing this, the staged scanner gate rejected `tools/mutation_probe.py`
with `cls_new_factory 0 -> 1`: the fixture's source string contained the call in
plain text. Two things follow.

- The probe now assembles that fragment from parts, exactly as it already did for
the emoji, so the instrument never appears as a finding in the gate it measures.
- The scanner is **inconsistent about string bodies**: `os.system(...)` written
inside the same file's string literal was *not* flagged, while
`cls().__new__(...)` was. The `os_system` rule filters string bodies; this one
does not. A rule that fires on prose will fire on documentation and on test
fixtures, so it is queued as a defect rather than silently worked around.

## What this does not prove

- **No finding count here is a quality score.** 13,280 ruff findings over 789
  files measures rule-set strictness against an unfamiliar corpus, not the state
  of the tree.
- **14 mutants are not the defect space.** They cover the classes this tree has
  already paid for. A class nobody has thought of is not in the matrix.
- **A caught mutant is a caught mutant in that one fixture.** It does not prove
  the rule fires in a nested function, behind a decorator, or in a generated
  file.
- The clean control proves the detectors are not flagging everything *in this
  fixture*, not corpus-wide.

## Next

1. Fix the three undefined names (owner's lane), then re-run both tools.
2. Decide whether `external_lint` becomes a ratchet: its F-code families
   (`F401` 854, `F841` 115) are the only part small enough to gate today.
3. Feed the probe a second generation of mutants (`open` without `with`,
   `sqlite3.connect` without `timeout`, `requests` without `timeout`) once the
   first set is stable across a full `golden_arrow` run.
