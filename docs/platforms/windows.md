# Windows

Status: **the reference OS.** Everything in the tree was first run here, so this
page is about not breaking a working install rather than about making one.

## The two interpreters, and why both exist

| interpreter | version | GIL | use |
|---|---|---|---|
| `C:/Azazael/.venvs/py315t/Scripts/python.exe` | 3.15.0rc3 | **off** (free-threaded) | production and the full test suite |
| `python` on PATH | 3.14.7 | on | ordinary scripts, anything whose wheels have no 3.15t build |

```bash
C:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest tests/ -q
```

Run the suite with the 3.15t interpreter. A "hang" or a segfault measured under
3.14 is not evidence about production, and this tree has already spent a session
on that confusion.

## Shell

Every command in this repository is written for **bash**, which on Windows means
Git Bash. `cd /c/Azazael/azazael`, forward slashes, `rm`/`mv` — never
`dir`/`move`/`del`. Two consequences that have cost real time:

- Backslashes in a bash path are escapes: `C:\Users\me` arrives as `C:Usersme`.
- `> nul` creates a **file named `nul`** that is painful to delete. Use
  `/dev/null`.

PowerShell is available but must be invoked as a program, with its own quoting
rules (`-NoProfile -Command '...'`), and never for file operations that bash
handles.

## What to install

1. **Git for Windows** (provides Git Bash). Then, from the tree root:

   ```bash
   git config core.hooksPath .githooks    # enables the commit gates
   ```

   Without this the pre-commit gate silently does not run: `.git/hooks/pre-commit`
   is a forwarder to the tracked `.githooks/pre-commit`, and a clone that never
   runs the config line has no gate at all.

2. **CPython 3.15t** and a venv at `.venvs/py315t` (see the section above).
3. **Node** — only needed for the Puppeteer capture path (`src/CODEX/capture_*.js`)
   and for `npx skills` if you install community skills.
4. **Chrome** — Puppeteer capture launches it; a headless-only Chromium is not a
   substitute for the renderer as configured.

## Delta table

| constant | reference value | on Windows, keep it unless measured otherwise |
|---|---|---|
| paths | `C:/Azazael/azazael` | forward slashes in bash, `Path` in Python (never string-concatenate) |
| venv | `.venvs/py315t` | one venv per interpreter, both on disk |
| hooks | `core.hooksPath .githooks` | per-clone setting; it is not in the repo |
| line endings | `newline="\n"` on writes | tools that rewrite files set it explicitly; `git` is configured not to convert |
| console encoding | UTF-8 assumed | the profile and gate output contains `—` and `→`; `PYTHONIOENCODING=utf-8` if a console mangles it |

## Known Windows-specific failure modes

- **`OSError: [WinError 10048]`** — port already bound. Windows
  `SO_REUSEADDR` lets a *second* process bind a live port with no error, which
  is how six proxies ended up double-bound on `:8766`. Check the process table,
  not just the socket.
- **A background process started in a sync command does not survive tool
  cleanup.** Long jobs belong in a persisted terminal (BACKGROUND) and must be
  verified still running afterwards, with its log read.
- **`robocopy`** on large trees can outlive a short timeout and look like a
  hang. Bound it, and prefer `shutil`/`cp -a` for small sets.
- **Antivirus locks on freshly written `.pyd`/`.exe`** produce a
  `PermissionError` on rename; retry once, then report it rather than falling
  back to a different build.

## GPU on Windows

Windows is where the accelerator question is worst, because the same physical
adapter can be reachable through three mutually exclusive stacks:

| adapter | route | doc |
|---|---|---|
| Intel Arc (integrated) | XPU torch wheel, Cycles on `ONEAPI` | [`intel-ultra-9-evo.md`](intel-ultra-9-evo.md) |
| NVIDIA | `cu12x` wheels, Cycles on `CUDA` | [`cuda.md`](cuda.md) |
| neither / unknown | CPU; say so | this page, and `box_profile.py` |

Do not infer the adapter from the laptop's marketing name. `box_profile.py`
reports what torch can actually reach, in three states, and `unknown` means the
library is missing rather than the hardware.

## Verification

```bash
python tools/box_profile.py --write box_profile.json
C:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest tests/ -q
python tools/commgate.py                  # or: git commit; the gate runs there
```

A Windows install is done when the suite passes on the 3.15t interpreter and the
commit gate prints its 15-gate table — not when `pip install` exited 0.
