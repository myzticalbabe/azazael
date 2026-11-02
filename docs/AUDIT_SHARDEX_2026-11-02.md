# AUDIT — Project_SHARDEX standalone publish readiness (2026-11-02)

Read-only audit. **Nothing was executed** (this auditor had no terminal), so every
statement below is a reading of source, not a test result. Test *status* is therefore
UNKNOWN; what is asserted is what each test *requires*, which is checkable by reading.

Target: `C:/Azazael/azazael/Project_SHARDEX`
Tree contents: `LICENSE`, `NOTICE`, `SHARDEX.md`, `shardex.py`, `transubstantiate.py`,
`meshscene.py`, `ops.py`, `tests/{test_shardex,test_transubstantiate,test_mesh_live}.py`
There is **no `pyproject.toml`**, no `README.md`, no `.github/`, no `CITATION.cff`.

## Verdict

**COUPLED — NOT YET RUNNABLE as a standalone repo.** The core ladder (L0–L3) is
stdlib-only and will run, but three things outside the tree are referenced, and one of
them is an executable read from the parent repo (`shardex.py:753`). One test file cannot
pass in a fresh clone because its fixture lives in `docs/` at the monorepo root.

Rung-level verdict:

| rung | standalone today | evidence |
| --- | --- | --- |
| L0 MIRROR | **works** | pure stdlib, `shardex.py`; `test_shardex.py:53-62` synthesises its own toy game, so no external game is needed |
| L1 SHATTER | **works** | same file, same fixture |
| L2 FORGE | **works** (browser agreement optional) | `shardex.py:765-772` treats a browser as optional and says so; `test_shardex.py:211` skips the browser test when none is found |
| L3 TUNE / `--verify` | **works** | pure Python; no external read |
| `--doctor` | **fails** | `shardex.py:753` reads `../docs/METTHEW/shard.schema.json`, absent in a standalone clone → `NOT READY` at `shardex.py:775` |
| image → field → mesh (live mutation) | **not runnable** | needs `tools/sample_image.js` and `tools/capture_transubstantiation.js`, both outside the tree, plus puppeteer |
| `transubstantiate.py --extract/--forge/--verify` | code works; **its test cannot pass** | test fixture is `ROOT/docs/YGGDRASIL_CLEAVE.html` (`test_transubstantiate.py:17,19`) |

## 1. Executable reads that reach outside the tree

| file:line | what it reads | present today? | effect in a fresh clone |
| --- | --- | --- | --- |
| `shardex.py:753` | `parents[1]/docs/METTHEW/shard.schema.json` | **yes** (`docs/METTHEW/shard.schema.json`) | `--doctor` prints `MISSING: shards cannot be checked against the project's own contract` and returns `REFUSED` |
| `test_transubstantiate.py:17,19` | `parents[2]/docs/YGGDRASIL_CLEAVE.html` | **yes** (`docs/YGGDRASIL_CLEAVE.html`) | that test errors on a missing file |
| `test_shardex.py:25` | `parents[1]` = `Project_SHARDEX` itself | n/a | fine |

Note the severity of `shardex.py:753` precisely: the schema is read **only** inside
`doctor()` (it is the sole occurrence of `shard.schema.json` in the tree — a scoped search
returned that one line). Mirror, shatter, forge and verify do not consult it. So it does
not break the pipeline; it breaks the health check, which is worse for a public repo than
it sounds, because a clean checkout's first command will be `--doctor` and it will say
`NOT READY`.

## 2. External assets the documented pipeline needs, and where they live today

Both harness scripts exist — but in the **monorepo's** `tools/`, not in `Project_SHARDEX`:

| asset | documented invocation | actual location today |
| --- | --- | --- |
| `sample_image.js` | `meshscene.py:28`, `SHARDEX.md:185` | `C:/Azazael/azazael/tools/sample_image.js` (117 lines, confirmed by read) |
| `capture_transubstantiation.js` | `meshscene.py:31`, `SHARDEX.md:145,187` | `C:/Azazael/azazael/tools/capture_transubstantiation.js` (132 lines, confirmed by read) |
| puppeteer | `NODE_PATH=C:/Users/clint/node_modules` (`sample_image.js:13`, `capture_transubstantiation.js:14`, `meshscene.py:28,31`, `SHARDEX.md:145,185-187`) | `require('puppeteer')` at `sample_image.js:14` and `capture_transubstantiation.js:15`; `node_modules` exists at `C:/Users/clint/node_modules` |
| reference shard `highend_duel` | `SHARDEX.md:63` | `docs/METTHEW/reference-shards/highend_duel` and `highend_ladder` — both present, both outside the tree |
| animation fixture `YGGDRASIL_CLEAVE.html` | `transubstantiate.py:41`, `SHARDEX.md:166` | `docs/YGGDRASIL_CLEAVE.html` — present, outside the tree |

So the L2-live claim in `SHARDEX.md` is real but **not shippable as documented**: a reader
who clones only this directory gets instructions telling them to run `node tools/…` for a
file that is not there.

## 3. The absolute-path problem, stated accurately

The known-fact handed to me was that the absolute path is at `meshscene.py:28,31`. It is —
but it is **inside the module docstring's USAGE block**, not in executable code. A scoped
search for `node_modules|C:/Users|C:/Azazael` over the whole tree returned exactly six
hits, and **all six are prose**:

- `meshscene.py:28,31` — docstring USAGE
- `SHARDEX.md:145,185,187` — documentation
- `shardex.py:82` — `SKIP_DIRS` contains the string `"node_modules"` as a directory to skip
  while mirroring. That is correct usage, not a hardcode.

Plus the two JS files carry the same line in their own `Run:` comments
(`sample_image.js:13`, `capture_transubstantiation.js:14`).

**Executable path literals that do exist**, and are Windows-shaped:

- `shardex.py:765-766` — `C:\Program Files\Google\Chrome\Application\chrome.exe` and the
  x86 variant, each guarded by `Path(...).exists()`, with `shutil.which("chrome")` falling
  through (`shardex.py:767`). Harmless on Linux/macOS but it means the *only* explicitly
  probed install locations are Windows ones.
- `tests/test_shardex.py:29-31` — `CHROME_CANDIDATES` lists the two Windows paths **and**
  `/usr/bin/google-chrome`, `/usr/bin/chromium`, and `_chrome()` (`:48-52`) iterates them
  then falls back to `shutil.which`. Cross-platform; slightly odd that the Windows entries
  precede the Linux ones.

**Publish verdict on this point:** documentation-only, and therefore cheap to fix, but it
is a real blocker for a public repo — the first command in the README contains another
person's home directory. The fix is not to delete the path but to replace it with a
`npm install puppeteer` step plus `NODE_PATH=$(npm root -g)` or a local `node_modules`.

## 4. Tests, and what each requires

| test file | browser? | external fixture? | notes |
| --- | --- | --- | --- |
| `test_shardex.py` (252 lines) | one test only, `:211` `skipif(not _chrome())` | none | builds a toy game in `tmp_path` (`:53-62`); asserts `selftest()` returns 13 lines (`:69-71`) |
| `test_mesh_live.py` (220 lines) | none — "Nothing here renders" (`:3`) | none | constructs its own field dict (`:22-33`); asserts `FLAT-FIELD` refusal at `edge_value=0` (`:36-41`) |
| `test_transubstantiate.py` (151 lines) | none | **yes** — `docs/YGGDRASIL_CLEAVE.html` (`:17,19`) | positive fixture + a `NO_CLOCK` negative control that must be REFUSED (`:24-27`) |

**Status: UNKNOWN.** None were run here. The coordinator must run them; the useful prior is
that `selftest()` is asserted to emit exactly 13 lines, so a change in that count is a
failure, not a cosmetic difference.

## 5. Pre-publish gaps (beyond coupling)

1. **No `pyproject.toml`** — dependencies undeclared. Today that is harmless because the
   Python is stdlib-only, but it is undeclared rather than declared-empty.
2. **No `README.md`** — `SHARDEX.md` is a very good document, and it is not the file a
   visitor looks for. Also no `.github/`, no `CITATION.cff`, whereas the sibling
   therapeutic project ships all three.
3. **`LICENSE` and `NOTICE` were added today by another worker** (not by this audit) —
   present in the tree now; Apache-2.0.
4. **The `tools/*.js` harness must move into the tree** (e.g. `Project_SHARDEX/tools/`) or
   the L2-live section of `SHARDEX.md` must be marked monorepo-only. The first is better:
   it is 249 lines of the verifying half of the claim.

## 6. What this audit could not establish — do not read as a pass

- **Nothing was executed.** No test, no `--selftest`, no `--doctor`, no forge/verify run.
- I did not read all of `shardex.py` (1003 lines) or `transubstantiate.py` (829 lines); the
  coupling claims rest on a scoped search for absolute paths, `parents[N]`, `docs/`,
  `METTHEW` and `require`, plus targeted reads. A coupling that names none of those strings
  would not have been found.
- **Instrument warning, worth passing to the other 17 auditors:** `glob "*.js"` scoped to
  `tools/` returned **0 files**, and a `code_search -l` for symbols those files certainly
  contain (`getImageData|__geo|__mutate|puppeteer`) also returned **0** — yet both files
  exist and were read successfully by absolute path. So a zero from `glob`/`code_search`
  in this tree must be confirmed with `read_files` or `list_directory` before it is
  reported as absence. Two of my own intermediate conclusions were corrected this way.
