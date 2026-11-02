# AUDIT — Project FLAME (standalone-publish readiness)

**Date:** 2026-11-02
**Auditor:** 3 of 18, FULL AUDIT fan-out
**Target:** `C:/Azazael/azazael/Project_FLAME`
**Mode:** READ-ONLY. No file in the target was modified. This report is the only file written.

**Verdicts**
- **STANDALONE: YES** — no import escapes the directory; every import is stdlib.
- **RUNNABLE AS PUBLISHED: NO, not yet** — the entry command documented in the file is
  monorepo-relative, so a fresh clone following its own instructions fails; and the tree
  ships with **zero tests** because its test file lives outside it.

---

## 1. How a user actually runs it (read from code, not the README)

**The entry point exists and is real.** `tools/flame_engine.py` is a self-contained CLI:

| Evidence | What it establishes |
|---|---|
| `flame_engine.py:465` `def main(argv: Optional[List[str]] = None) -> int` | a callable entry point |
| `flame_engine.py:466-476` | `argparse.ArgumentParser` with `--verify`, `--demo`, `--selftest`, `--seconds`, `--rates`, `--accel`, `--json` |
| `flame_engine.py:478-529` | dispatch: `--selftest` → `selftest()`; `--demo` → one readable run, `return 0`; otherwise `verify()` at `:495` |
| `flame_engine.py:528` `if __name__ == "__main__": sys.exit(main())` | runnable as a script |

**Canonical invocation for the standalone repo:**

```
python tools/flame_engine.py --verify      # invariance matrix + negative control
python tools/flame_engine.py --selftest    # clock and machine controls
python tools/flame_engine.py --demo        # one human-readable run
```

Bare invocation (no flags) also verifies: the `--demo` and `--selftest` branches return
early (`:478`, `:487`), so control falls through to `verify()` at `:495`.

**Exit codes:** `0` verified, `1` a matrix failure or missed control (`:497`, `:527`),
`2` unusable arguments — but note the `2` is **argparse's own** behaviour on a parse error,
not a custom path; the module docstring at `:55` claims `2` as part of its contract, so the
claim is true only by inheritance.

### DEFECT D1 — the documented command is wrong for the published repo

`flame_engine.py:51-53` documents:

```
python Project_FLAME/tools/flame_engine.py --verify
python Project_FLAME/tools/flame_engine.py --demo
python Project_FLAME/tools/flame_engine.py --selftest
```

`Project_FLAME/` is a prefix that exists **only inside the monorepo**. In a standalone repo
whose root is the project itself, that path does not resolve. A new user's first command
fails. This is the single highest-value fix in this slice — three lines.

---

## 2. The contract it publishes

`flame_engine.py:80-85`:

```python
class Machine(Protocol):
    """What the engine needs from a game. Deliberately four methods wide."""
    def reset(self) -> None: ...
    def step(self, input_mask: int) -> None: ...
    def state_hash(self) -> str: ...
    def snapshot(self) -> Dict[str, object]: ...
```

This is the published interface, and it is the whole seam. `README.md:19-26` repeats it.
A `StandInMachine` (`:90`) and a `Session` implement/consume it. Any game plugs in by
implementing four methods — no import of FLAME internals is required, which is what makes
the FLAME / FLAMING SWORD split real rather than nominal.

Two consequences worth stating, because they are what the project actually claims:
`state_hash()` is the instrument that decides whether a presentation change left the sim
alone, and `step(input_mask)` takes an integer bitmask, so the contract cannot express a
analog input without a breaking change. That is a design position, not a defect — but it
is the constraint a third party will hit first.

---

## 3. Tests: absent from the tree, present only in the monorepo

**There is no `tests/` directory in `Project_FLAME`.** Directory listing is LICENSE,
NOTICE, README.md, `tools/`. `tools/` holds exactly one file, `flame_engine.py`.

The tests do exist — at `C:/Azazael/azazael/tests/test_flame_engine.py`, outside the
project. `README.md:53` cites them (`tests/test_flame_engine.py` gives 7 passes), and
`README.md:37` cites `--selftest` output (`9 clock controls, 3 machine controls, 4 schedule
controls`). So the verification layer is real but **is not in the artifact that would be
published**.

**What a standalone repo would ship untested** (i.e. what `test_flame_engine.py` must be
copied in to cover):

1. the closed-form tick formula `tick(n) = floor(n * hz_num * accel_num / (rate * hz_den * accel_den))` (`:40-43`) — that the same tick is reached regardless of frame count;
2. slicing invariance — one hash across 60/120/144/240 fps;
3. acceleration equivalence — one hash at 1x/2x/8x;
4. the **negative control** — a deliberately 60 Hz-assuming clock must be reported `CAUGHT`, never `MISSED` (`:522-525`);
5. tick monotonicity and the no-skip / no-double-serve count (`steps == final tick index`);
6. `--json` output shape and the exit-code contract (`:497` returns 1 only when `result["failures"]` is non-empty);
7. the `Machine` protocol conformance of `StandInMachine`.

Item 4 is the load-bearing one: without it a green matrix is indistinguishable from an
instrument that cannot fail. Publishing the engine without its control is the exact defect
this repository records elsewhere as "a broken instrument reported OK".

---

## 4. Packaging state

| Item | State |
|---|---|
| `LICENSE` | **present** — Apache-2.0, added this session |
| `NOTICE` | **present**, added this session; makes no dependency claim (correct — none verified) |
| `README.md` | present and unusually good: states what the project *refuses* to claim (`:57-71`) |
| `pyproject.toml` | **ABSENT** — no packaging metadata, no declared entry point, no Python floor |
| `tests/` | **ABSENT** (see §3) |
| `.gitignore` | **ABSENT** |
| CI | **ABSENT** — no `.github/`; contrast `Project_Nurse_Ratchet/.github/workflows/ci.yml` |

Dependencies are undeclared but harmless **today** because there are none: `:59-64` imports
`argparse, hashlib, json, sys, fractions, typing` — all stdlib. `typing.Protocol` requires
Python 3.8+; `from __future__ import annotations` (`:57`) means the annotations are strings,
so the real floor is 3.8 unless `Dict[str, object]` at runtime is required anywhere.

### DEFECT D2 — one machine-absolute path in a published file

`README.md:39`:

```
Verified 2026-11-01 on `C:/Azazael/.venvs/py315t/Scripts/python.exe` (3.15.0rc3 free-threading):
```

This is the **only** absolute path anywhere in the tree (the code is clean — no `C:/`, no
`C:/Users/clint`, no `.venvs` reference in `flame_engine.py`). It is a provenance record and
should stay quoted as measurement, but it names a path no reader has. Recommend keeping the
interpreter *version* and dropping or genericising the path.

### Documented (not imported) external dependency

`README.md:78-80` states `tools/sword_2600.py` — the cartridge front-end — still lives in
the monorepo's `tools/` because the intake documents cite it there, and calls adoption a
follow-up. That is an honest disclosure of an unfinished seam, **not** an import coupling;
nothing in `flame_engine.py` references it. It does mean FLAME's *cartridge intake* story
is incomplete in a standalone clone, while its *scheduler* story is complete.

### Provenance note — the rename

Git history shows `tools/sword_engine.py` was renamed to
`Project_FLAME/tools/flame_engine.py` at 96% similarity. Nothing in this audit depends on
that; recorded so the lineage is not mistaken for a lost file.

---

## 5. Verdicts, with the reason

**STANDALONE — YES.**
Every import in `flame_engine.py` is stdlib (`:59-64`). There is no `from CORE`, no
`src.` import, no sibling-project import, and no absolute path in code. The FLAMING SWORD
relationship is a **Protocol**, not an import, so FLAME genuinely runs with the rest of the
monorepo absent. This is the cleanest of the trees audited.

**RUNNABLE AS PUBLISHED — NO, not yet.** Three concrete reasons, all cheap:
1. **D1**: the only documented entry commands (`:51-53`) carry the `Project_FLAME/` prefix
   and therefore fail in a standalone clone. Fix: three lines, in place.
2. **Zero tests ship** — `test_flame_engine.py` is outside the tree; the negative control
   that makes the instrument falsifiable would not travel with the code.
3. No `pyproject.toml`, so there is no declared entry point and no declared Python floor;
   the reader must infer both from the README.

**Blocking order to publish:** D1 (3 lines) → copy `tests/test_flame_engine.py` into
`Project_FLAME/tests/` and confirm it imports the engine by relative path rather than by
monorepo path → add a minimal `pyproject.toml` with `requires-python` and a console script →
genericise `README.md:39`. D2 is cosmetic; D1 and the test copy are not.

---

## 6. Not established by this audit

- **Nothing was executed.** No run of `--verify`, `--selftest` or `--demo`. The 7-pass and
  9/3/4 control counts are quoted from `README.md:53` and were **not** re-measured here.
  A fresh-clone run is still owed and is the acceptance gate for this project.
- Whether `tests/test_flame_engine.py` imports `flame_engine` by a path that survives being
  moved into the project — not read.
- `__pycache__/` exists under `tools/`; whether it is tracked was not checked.
- No assessment of whether the `Machine` four-method contract is sufficient for the M-34
  2600 sim, which is an architecture question outside this slice.
