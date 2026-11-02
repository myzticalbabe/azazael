# Full review — 2026-11-02, pre-push gate

Every row below comes from a command that ran against a **clean `git clone`** of the
staged repo, not against the source tree. A working tree can hold gitignored files a
stranger never receives, and that difference already produced one false green in this
session.

## Release verdict

| repo | pyproject name | README | NOTICE | install | tests | secrets |
|---|---|---|---|---|---|---|
| flaming_sword | `flaming-sword` | yes | yes | **PASS** | **109 passed** | clean |
| nurse_ratchet | `nurse-ratchet` | yes | yes | **PASS** | **169 passed** | clean |
| shardex | `shardex` | yes | yes | **PASS** | **34 passed, 1 skipped** | clean |
| cradle | `cradle` | yes | yes | **PASS** | **4 passed, 8 skipped** | clean |
| flame | `flame-engine` | yes | yes | **PASS** | **no tests** | clean |
| ELIZA | `eliza` | yes | yes | **FAIL** | 9 errors | clean |

**316 tests pass** across five repos; 9 skip with a stated reason. Total staged size
3.0 MB. Every repo carries Apache-2.0, a NOTICE, and a renderable README.

## Two fixes applied during this review

**1. cradle and shardex had no `README.md`.** Both documented themselves in
`CRADLE.md` / `SHARDEX.md`, which satisfies the packaging `readme` field but means
GitHub renders **no repository page at all**. Added a `README.md` to each that states
what ships, what the external requirements are, and points at the canonical document.
`readme` in both pyprojects still points at the `.md` files that exist.

**2. `cradle doctor` was wrong in both directions, and is now three-state.**

- Before: a standalone install failed 10 checks because `doctor()` asserts that
  FLAMING_SWORD's five files exist beside it. A part that was never going to be in
  this repository is not a defect in this repository.
- Now `doctor()` reports each absent part as **`N/A — not installed: FLAMING_SWORD is
  a separate project`**, and still reports **FAIL** when the sibling tree *is* present
  and a part is missing from it (a real defect).
- Verified both ways: monorepo `12 passed`; clean clone `4 passed, 8 skipped`.

The eight chain tests carry `@needs_chain` (`skipif` the sibling is absent). They are
**skipped, never weakened** — every assertion still runs wherever the chain exists.

An intermediate version of that marker pointed `CHAIN` at
`Project_CRADLE/Project_FLAMING_SWORD/tools`, which silently skipped all eight even
in the monorepo. It was caught by running both contexts and comparing, and corrected.
The wrong path is recorded in the source comment.

## Blocker: ELIZA cannot be reviewed because it cannot build

```
error: package directory 'eliza' does not exist
   tests: 9 errors
```

`pyproject.toml` declares `packages = ["eliza", "eliza.psyche"]`; `.gitignore`
excludes `/eliza/`; the directory does not exist because `tools/publicize.py` was
never run against it. Running it is not the fix: ELIZA's `PUBLIC_MANIFEST.json` copies
`../src/PSYCHE/*` — the **therapeutic** stack — into a repository whose NOTICE says
"forensic investigation suite". Three files describe the wrong project:

| file | says |
|---|---|
| `PUBLIC_MANIFEST.json` summary | "A therapeutic-agent loop, the psychological network it reasons over…" |
| `pyproject.toml` | entry point `eliza-psyche` |
| `README.md` line 3 | "A therapeutic agent that is honest about what it cannot do" |
| `NOTICE` | "Project ELIZA is the forensic investigation suite…" |

The owner's ruling is that ELIZA is the forensic investigation suite and Nurse Ratchet
is the therapeutic agent. The forensic method's real home is
`C:/Users/clint/.bcc_audit/03_tooling/` — `verify_proofs.py` (14,688 bytes) and
`quote_norm.py` (10,177 bytes) both confirmed present — over `00_raw/` (186 MB of
evidence that must never be copied).

**ELIZA is excluded from the push until it builds.** Shipping it as-is would publish a
false description of the code, which is the exact defect this session spent its time
removing from everywhere else.

## Push target

`gh` 2.103.3 is installed at `C:/Azazael/tools_bin/bin/gh.exe` (portable zip — the
winget MSI aborts with `0x80070020`, the file locked by the Git Bash process itself).

```
gh version 2.103.3 (2026-10-26)
You are not logged into any GitHub hosts. To log in, run: gh auth login
```

**Authentication is the last gate.** No credentials exist in this session, and
`gh auth login` is interactive. Once authenticated, each staged repo has one commit and
is push-ready as-is.

## Risk register — carried, not fixed

| risk | status |
|---|---|
| `flame` has **no tests** | installs and its entry point imports; nothing verifies behaviour. "Proven to install" is not "proven to work" |
| No wheel built | `pip install .` from source was proven; `python -m build` and PyPI were not |
| `requires-python = ">=3.10"` | copied from the two pre-existing files, never exercised on 3.10 |
| Two top-level `tools` packages | `flame` and `flaming_sword` both install one; harmless for GitHub, a collision on PyPI |
| `nurse_ratchet` `.gitignore` edit | undone if `tools/publicize.py` is re-run — it writes `.gitignore` itself |
| FLAMING_SWORD `aio/` payload | `aio/flaming_sword.aio.json` is a sibling of `tools/`, so it will not be in the wheel |

## Corrections to this session's own record

Three board diagnoses were made and then disproved by measurement; all three are
corrected here so the record is not left standing:

1. **"pushed rows are born `state='claimed'`"** — false. `post_task` writes **no**
   `lane_task_state` row at all; a pushed row is born `state=NULL` and is immediately
   claimable. The only `'claimed'` INSERT is inside `claim_tasks` (`LaneMessageBoard.py:981`).
2. **"opencode is locked out for 30 minutes"** — false. The stamps at `11:32:07` were
   written by my own `claim opencode 10 freebuff`, which ran twice inside one shell
   pipeline.
3. **"my second claim self-retired the rows"** — false. Those rows carry
   **agent-authored completion notes**; another agent picked the work up and retired it
   within minutes.

What is real, from the DB: the six max-reasoning tasks pushed to opencode were retired
**without the work being done** — dispositions include "do not exist in the repository"
(wrong: the files are in `.bcc_audit/03_tooling/`), "requires web research - not a code
task", and a mis-scoping of `verify-replay` to an unrelated LOWEND verifier. Only
`git-fleet-home-repo-hazard` reached a genuine decision. `jaeger-003` was correctly
deferred: `Project_JAEGER` does not exist.
