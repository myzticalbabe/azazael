# Publish proof — 2026-11-02

Every number below was produced by a command that ran. Nothing here is inferred from
metadata. The decisive test is **a clean `git clone` followed by `pip install .` and
`pytest`**, because a working tree can contain gitignored files that a stranger never
receives — that difference already produced one false green in this session and is
recorded below.

## Proof table (clean clone, not working tree)

| repo | commit | files | size | `pip install .` | tests |
|---|---|---|---|---|---|
| flaming_sword | `7cbb976` | 21 | 789K | **PASS** | **109 passed** |
| shardex | `b9ea9f9` | 12 | 542K | **PASS** | **34 passed, 1 skipped** |
| nurse_ratchet | `5af01e3` | 55 | 1.3M | **PASS** | **169 passed** |
| flame | `f3ad75c` | 7 | 210K | **PASS** | no `tests/` directory |

**312 tests pass** (109 + 34 + 169) from clean clones. Staged total across shippable
repos: **3.0 MB**. All six source dirs scanned clean for API-key/token patterns.

## Two repos are held, with evidence

### ELIZA — cannot build

```
error: package directory 'eliza' does not exist
   tests: 9 errors
```

`pyproject.toml` declares `packages = ["eliza", "eliza.psyche"]`, `.gitignore` excludes
`/eliza/`, and the directory does not exist because `tools/publicize.py` was never run against
it. Running it is not the fix: ELIZA's `PUBLIC_MANIFEST.json` copies `../src/PSYCHE/*` — the
therapeutic stack — into a repo whose NOTICE says "forensic investigation suite". Shipping it
would publish a false description of the code, which is the defect this session spent its time
removing.

### cradle — builds, but its own suite fails when shipped alone

```
10 failed
AssertionError: defender is missing at .../Project_FLAMING_SWORD/tools/defender.py
  defender          FAIL   MISSING: tools/defender.py
  REAPER (sentinel) FAIL   MISSING: tools/sentinel.py
  GRIMOIRE (memory) FAIL   MISSING: tools/memory_bridge.py
  server            FAIL   MISSING: tools/chain_server.py
```

`cradle.doctor()` resolves four of its five components through a sibling checkout
(`cradle.py:73`). In the monorepo those exist; in a standalone clone they cannot. The
package installs and its entry point imports, but **its own tests prove it is not
standalone** — so it ships with FLAMING_SWORD or not at all. That is a scope finding, not a
bug to paper over by relaxing the assertions.

## The false green this session produced, and how it was caught

First proof round installed each project **from its source directory** and reported
`nurse_ratchet PASS`. It was wrong: `nurse_ratchet/` is generated and gitignored, so the
working tree contained it while `git ls-files` did not. A clean clone failed with
`package directory 'nurse_ratchet' does not exist`.

Fix applied and re-proven:

1. ran `tools/publicize.py` in `Project_Nurse_Ratchet` — materialised `nurse_ratchet/psyche/*`
   (10 modules), tool self-reported `public tree: OK`;
2. removed the `/nurse_ratchet/` line from `.gitignore` — a standalone repo cannot regenerate
   the package from a monorepo that is not present, so the generated tree must be committed;
3. re-staged (55 files committed), clean-cloned, installed, ran tests: **169 passed**.

Note the tension: `MANIFEST_NOTES.md` argues the generated package should not be committed
because a second copy drifts. That argument holds inside the monorepo and fails for a
standalone public repo, where there is nothing to generate from. For the published artifact,
committing the generated tree is the only honest option.

## Not proven

- **No push target exists.** `gh` is not installed, `gh auth status` is unavailable, and the
  monorepo's only remote is a local path (`C:\Users\clint\azazael`). Repos exist as local
  commits; reaching GitHub needs a remote URL and credentials.
- **flame has no tests.** It installs and its entry point imports, but nothing verifies
  behaviour. "Proven to install" is not "proven to work".
- **No wheel was built** — `pip install .` from source is what was proven, not `python -m build`
  or a PyPI upload.
- `requires-python = ">=3.10"` is copied from the two pre-existing files and was not tested
  under 3.10.
- The `.gitignore` edit for nurse_ratchet will be undone if `tools/publicize.py` is re-run,
  because that tool writes `.gitignore` itself.
