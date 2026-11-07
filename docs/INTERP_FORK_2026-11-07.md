# Individualized interpreter — fork declaration (2026-11-07)

**Owner:** freebuff lane. **Status:** DECLARED. **Engine:** `C:/Azazael/.venvs/py316t`
(CPython v3.16.0a1 @ `22d79d98`, `--disable-gil`, MSVC native, free-threaded).

## What "fork" means here

Not a source fork: the CPython tree at `C:/Azazael/.build/cpython-316` carries
**zero source edits** (dirty verdict BENIGN — `Programs/test_frozenmain.h` M,
`Include/pyconfig.h` + `libs/` untracked, all build-generated). The fork is a
**maintenance fork**: this tree pins one upstream commit, owns its build recipe,
its acceptance gates, and its merge discipline, and never tracks upstream by
default. Upstream may vanish; the engine keeps running this repo.

## Pinned base

| item | value |
| --- | --- |
| upstream | python/cpython tag v3.16.0a1 |
| sha | `22d79d9840a275ed6ed36cd590dc74edc61765fb` |
| flags | `PCbuild/build.bat -p x64 -c Release --disable-gil` |
| sidecar | `C:/Azazael/.venvs/py316` (same series, GIL on) |
| record | `state/py316t_build.json` (dirty BENIGN, 2026-11-07) |
| canonical | `state/canonical_interp.json` (written by `promote`) |

## Permanence

`C:/Azazael/.build/cpython-316` is a **permanent artifact**. Both venvs resolve
their stdlib from it (`pyvenv.cfg` home lines). Deleting or cleaning it kills
the interpreter. `interp_cycle guard` fails if it vanishes while needed.

## Merge discipline

1. `watch` weekly (or on demand). A `core C fix: YES` is a rebuild *candidate*,
   never an order.
2. Security fixes are **hand-ported** onto the pinned tree by an agent, then a
   full rebuild + `verify` (7 probes, property-based) + `promote`.
3. No rebase to a newer upstream ref without: verify PASS, evolve parity
   (q within noise of shipped), full record refresh via `verify --apply`.
4. Custom patches (a future 0x0D opcode, a ceval change) land as documented
   diffs against the pinned sha, recorded in the build record — never silent.
5. Rebuilds take the build lock first (`interp_cycle lock --take <lane>`);
   `promote` refuses under a live lock.

## What this does NOT change

The repo evolve loop still tunes repo knobs. The engine still only runs code.
The fork declaration changes *who maintains the engine* (us, deliberately) —
not what the engine can do.
