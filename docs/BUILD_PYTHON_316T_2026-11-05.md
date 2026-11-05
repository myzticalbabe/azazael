# Build Python 3.16t — instructions for the opencode lane

**Issued by:** freebuff lane, 2026-11-05. **Target:** a free-threaded CPython **3.16**
(no-GIL) interpreter at `C:/Azazael/.venvs/py316t`, plus a same-version GIL sidecar
at `C:/Azazael/.venvs/py316` for packages that ship no `cp316t` wheel.

**Series statement.** 3.16 is the next series, not a 3.15 point release. Nothing in
this build may be validated by a `sys.version_info` test alone; a build only counts
as 3.16t when the **capability probe** below prints `free-threaded` **and** the
version line says `3.16`.

**Honesty clause.** No 3.16 interpreter exists on this machine as of
2026-11-05; every number this tree has measured is 3.15.0rc3
(`.venvs/py315t`). Nothing here is a claim that 3.16t works — it is the procedure
that produces the first reading, and it names the two points where 3.16 may differ
from 3.15 so the executor records the difference instead of assuming.

---

## 0. Preconditions — check, do not assume

```bash
df -h /c | tail -1                      # measured 2026-11-05: 756G size, 7.6G avail, 100% used
git --version; cl.exe 2>/dev/null || echo "no MSVC on PATH"   # Windows: VS Build Tools 2022 + Python workload
```

- **Disk.** An out-of-tree 3.16 build (source ~700 MB + Release build ~1.6 GB +
  venv ~400 MB) needs **≥ 4 GB** free. At 7.6 GB free the build fits *if* nothing
  else lands during it; if `df` shows < 6 GB, stop and report — a build that dies
  at 99% leaves a half-linked `python.exe` that fails in ways that look like source
  defects.
- **Windows toolchain.** Visual Studio 2022 Build Tools with the *Desktop development
  with C++* workload. `PCbuild\build.bat` finds it through `vswhere`; a missing
  workload reports `Cannot find vcvarsall.bat`.
- **Do not build inside the repo.** Build in `C:/Azazael/.build/cpython-316`
  (already gitignored via `.build/`) so `git status` stays clean and a failed build
  cannot be committed.

## 1. Fetch the series

```bash
mkdir -p C:/Azazael/.build && cd C:/Azazael/.build
git clone --depth 1 --branch 3.16 https://github.com/python/cpython cpython-316
cd cpython-316 && git log -1 --format='%H %cd %s' --date=iso
```

- The branch name **may not exist yet**. Resolution order, and record which one you
  used in the build record: `3.16` → `main` (then note that `main` is the 3.17
  development branch the day 3.16 forks) → the newest `v3.16.0a*` tag
  (`git ls-remote --tags origin 'v3.16*'`).
- A shallow clone of `main` is acceptable; a shallow clone **cannot** be used to
  claim a tagged release. If you build from `main`, the record says `main@<sha>`.

## 2. Configure free-threading — confirm the flag's name in THIS version

The no-GIL configure switch has been renamed across series. Do not paste 3.15's flag
and assume:

```bash
./configure --help | grep -iE "gil|free.?thread"        # record the exact line
```

- If `--disable-gil` is offered, use it (3.13–3.15 spelling).
- If the help offers a different spelling (`--enable-free-threading`,
  `--with-free-threading`, …), use that spelling and **record the line verbatim**
  in the build record. A build configured with an unrecognised flag silently
  produces a GIL build — `configure` warns, and the warning scrolls past.
- **Windows** (`PCbuild\build.bat`): `PCbuild\build.bat -p x64 -c Release --disable-gil`
  (or the 3.16 spelling from `PCbuild\build.bat -h`).

```bash
# UNIX, out-of-tree, prefix owned by this tree
mkdir -p /c/Azazael/.build/py316t-build && cd /c/Azazael/.build/py316t-build
../cpython-316/configure --disable-gil --prefix=/c/Azazael/.venvs/py316t --with-ensurepip=install
make -j16 && make install
```

`-j16` matches this box's 16 cores (measured: `cpu=16` in the compat report). A
serial `make` on a 16-core machine is a process violation, not caution.

## 3. The gate — this is the acceptance test, not a sanity check

```bash
PY=C:/Azazael/.venvs/py316t/python.exe
$PY -c "import sys, sysconfig; print(sys.version); print('gil_enabled', getattr(sys,'_is_gil_enabled',lambda:'absent')()); print('Py_GIL_DISABLED', sysconfig.get_config_var('Py_GIL_DISABLED'))"
```

Expected shape (values, not exact text):

```
3.16.0a1 (…, …) […]
gil_enabled False
Py_GIL_DISABLED 1
```

Then the tree's own probe, which is the only reading that decides adoption:

```bash
cd C:/Azazael/azazael
PYTHONPATH=src C:/Azazael/.venvs/py316t/python.exe -m HYPER_EDGE.cli capabilities
PYTHONPATH=src C:/Azazael/.venvs/py316t/python.exe -m HYPER_EDGE.cli selftest
```

- `capabilities` must print `python 3.16… free-threaded`, `pool=CORE.freethreading.FreeThreadPool`,
  and `probe_faults=0`. A non-zero `probe_faults` is a finding, not noise.
- `selftest` must print `24 check(s), 0 failed, 0 skipped`. If a check fails on 3.16
  **the check is the deliverable** — record the failing check name and its reason
  line, do not relax the assertion.
- If `is_free_threaded()` disagrees with `sys._is_gil_enabled()`, the native detector
  is wrong for this series: fix `CORE/freethreading.is_free_threaded` to read
  `sysconfig Py_GIL_DISABLED` as a second source, and say so in the record.

## 4. The GIL sidecar — a second venv, same version

Free-threaded wheels carry the `cp316t` ABI tag; a package that publishes only
`cp316` cannot install into 3.16t. This is the same shape as the 3.15t sidecar
(`skill azazael-gil-sidecar`), and it is a **second interpreter of the same series**,
never a downgrade to 3.15:

```bash
# build once more, GIL enabled, same source tree, separate prefix
mkdir -p /c/Azazael/.build/py316-build && cd /c/Azazael/.build/py316-build
../cpython-316/configure --prefix=/c/Azazael/.venvs/py316 --with-ensurepip=install
make -j16 && make install
```

Record which packages need the sidecar by attempting the 3.16t install first and
listing what pip refuses. Never install a `cp316` wheel into `py316t` by force.

## 5. Verification that must be run, and its limits

```bash
PY=C:/Azazael/.venvs/py316t/python.exe
$PY -m pytest tests/test_hyper_edge.py -q -p no:xdist            # expect: 11 passed
PYTHONPATH=src $PY -m HYPER_EDGE.cli evolve --generations 6 --population 24 --seed 7
PYTHONPATH=src $PY -m HYPER_EDGE.cli selftest
```

Write `state/py316t_build.json` with: branch/tag + sha, configure line copied from
`--help`, `sys.version`, `Py_GIL_DISABLED`, `gil_enabled`, the `capabilities` line,
the `selftest` line, the pytest count, and the packages refused by each venv.

**Limits to state in the record, not to paper over:** wide-suite behaviour on 3.16
is unmeasured until the full `tests/` run is performed there; a wheel set that
installs is not a wheel set that works; and a green `selftest` on 3.16t proves the
ISA's own properties, not the tree's 6,000-odd other tests.

## 6. Acceptance (commands, not assertions)

| # | command | must print |
|---|---|---|
| 1 | `.../py316t/python.exe -c "import sys;print(sys.version)"` | a line starting `3.16` |
| 2 | same + `sys._is_gil_enabled()` | `False` |
| 3 | `PYTHONPATH=src .../py316t/python.exe -m HYPER_EDGE.cli capabilities` | `3.16…free-threaded`, `pool=CORE.freethreading.FreeThreadPool`, `probe_faults=0` |
| 4 | `PYTHONPATH=src .../py316t/python.exe -m HYPER_EDGE.cli selftest` | `24 check(s), 0 failed, 0 skipped` |
| 5 | `.../py316t/python.exe -m pytest tests/test_hyper_edge.py -q` | `11 passed` |
| 6 | `cat state/py316t_build.json` | every field above present, with the branch and sha |

DONE = all six pasted into the record **with their exit codes**, plus the two
failing/refused items named (there will be at least one: expect wheel refusals).
A build that cannot be performed is reported as `BLOCKED` with the failing command,
never as a pass.

## 7. ERROR CAPTURE (mandatory, #714/#716)

Record every error, near-miss and falsification at ENCOUNTER TIME into
`state/bake_harvest_opencode_<date>.jsonl` with schema
`{source, item_id, title, body, kind}`; body >= 40 chars; kinds:
`error_fix | lesson | mandate | sop_rule | violation | anti_pattern`.
Do not defer to session end — reconstruction loses detail and over-weights what is
still salient. Validate: `tools/merge_bake_lane.py --lane <file> --apply`.
