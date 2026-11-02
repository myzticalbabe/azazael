# AUDIT — Project_FLAMING_SWORD (standalone publish candidate)

**Date:** 2026-11-02 · **Auditor:** worker 2 of 18, FULL AUDIT fan-out
**Target:** `C:/Azazael/azazael/Project_FLAMING_SWORD`
**Method:** read-only. Directory listings, source reads, and scoped `code_search`
(exit 0 when scoped to this directory). **Nothing was executed** — no test run,
no import, no git. Verdicts rest on reading source, not on observing behaviour.
**Verdict:** **STANDALONE** — one blocking item, and it is configuration, not code.

---

## 1. Inventory

| Path | Contents |
|---|---|
| `tools/` | `sword.py`, `defender.py`, `sentinel.py`, `memory_bridge.py`, `chain_server.py`, `housekeep.py`, `disposition.py` |
| `tests/` | `test_sword.py`, `test_defender.py`, `test_sentinel_memory.py`, `test_chain_server.py`, `test_housekeep.py`, `test_disposition.py` |
| `aio/` | `flaming_sword.aio.json` (the instruction object `--brief` prints) |
| root files | `README.md`, `config.example.json`, `LICENSE`, `NOTICE` |

`LICENSE` and `NOTICE` (Apache-2.0) are **new as of today** and were not in the
tree before this audit; they are present now. There is **no `pyproject.toml`,
`setup.py` or `setup.cfg`** — see §4.

---

## 2. Entry points, and what each needs to run

| Entry point | `file:line` | Needs |
|---|---|---|
| `sword.py` — the sweep/loop CLI | `tools/sword.py:1419` | stdlib + `git` (README's claim, consistent with source); a target root |
| `defender.py` — frame builder | `tools/defender.py:818` | stdlib; `--intent`, `--target` |
| `sentinel.py` — claim resolver | `tools/sentinel.py:356` | stdlib; stats paths only |
| `memory_bridge.py` — lesson adapter | `tools/memory_bridge.py:453` | stdlib; one of two adapters (`jsonl` ledger or `command` emitting JSON lines) |
| `chain_server.py` — local HTTP endpoint | `tools/chain_server.py:340` | stdlib `http.server` + `urllib`; `--model-url` for `/ask`, otherwise `/ask` answers **503 NO-MODEL** by design |
| `housekeep.py` — deletion housekeeping | `tools/housekeep.py:413` | stdlib |
| `disposition.py` — ledger library | no `__main__` (library) | imported, not run |

Every runnable tool resolves its siblings **by file path, not by package import**
— `tools/chain_server.py:62` does `sys.path.insert(0, str(HERE))` then
`_sibling()` loads them via `importlib.util.spec_from_file_location`
(`chain_server.py:64-70`). That is the mechanism that makes the tree independent
of any package layout.

**No `CORE` import exists anywhere in this project.** Scoped search for
`from CORE|import CORE|from src` returned only the project's own
`sys.path.insert` lines (`tools/chain_server.py:62`, and the four in `tests/`).
This is the strongest single fact in the audit: the claim that this project does
not need the monorepo's core is **true at import level**.

---

## 3. The blocker: `config.example.json` is broken for a new user

The file is the first thing a reader copies. Two of its lines point at paths that
exist only inside the monorepo:

```
config.example.json:4     "ledger": "docs/platforms/claims.json",
config.example.json:5     "command": ["C:/Azazael/.venvs/py315t/Scripts/python.exe", "tools/platform_claims.py", "--check"]
```

Three separate defects in those two lines:

1. **A machine-absolute interpreter.** `C:/Azazael/.venvs/py315t/Scripts/python.exe`
   is this author's virtualenv. On any other machine it raises
   `FileNotFoundError` / `[WinError 2]` before the detector can report anything.
2. **A monorepo-relative script.** `tools/platform_claims.py` does not exist inside
   `Project_FLAMING_SWORD` — the project's own `tools/` holds only the seven files
   in §1. Copied verbatim, the path is wrong twice: wrong directory *and* wrong tree.
3. **A monorepo-relative ledger.** `docs/platforms/claims.json` likewise lives at the
   monorepo root, not in this project.

There are also two monorepo constants still on the watchlist
(`config.example.json:2`: `PMB_RECALL_MIN_BEST`, `PMB_RECALL_FLOOR`), which mean
nothing in a fresh clone.

**Why this is worse than an omission.** The README is emphatic that
`stale-claims` "requires `claims.command` in the config, and is **UNRUN** without
it" and that `UNRUN is not clean`. A missing key therefore produces the honest
state. A key that is **present but wrong** does not: it either raises inside the
detector or runs a command that cannot succeed, and the first-run user has to
distinguish "this repo has no stale claims" from "I shipped a broken example".
The file's own note (`config.example.json:9`) defends the absoluteness —
"the claims command is absolute because the sweep may run under a different
interpreter than the ledger expects" — which is a reasonable argument for an
operator's real config and does not transfer to an example.

**Remediation (not applied — read-only audit):** ship the `claims` block commented
out or omitted, so the honest `UNRUN` is what a new user sees, and drop the
monorepo watchlist from the example (or leave it with a one-line comment that a
watchlist is per-tree).

---

## 4. Tests, packaging, README

**Tests — self-contained.** All six insert this project's `tools/` onto the path
and nothing else: `tests/test_chain_server.py:27`, `tests/test_defender.py:22`,
`tests/test_sentinel_memory.py:23`. Absolute paths appear in
`tests/test_sword.py:225`, `:226`, `:244` — those are **fixtures for the
`two-interpreters` detector** (two different interpreters, and one deliberately
non-existent path), which is correct design, not leakage.

**Packaging — absent.** No `pyproject.toml`. The README's usage is
`python tools/sword.py ...` run from the project root, which works without a
package. The consequence is that dependencies are undocumented rather than
declared; today that is harmless because they are stdlib only and the README says
so ("Standard library and `git`. No network, no keys, no dependency to install.").
It does mean `tests/` cannot be run as an installed package, only from the root.

**README — unusually strong on refusals, and specific where it matters:**

- states the three loop refusals: no verification command → no landing; no landing
  on red; **no push** (`README.md`, "The loop, and its three refusals");
- states `UNRUN is not clean` as the project's central rule;
- has an explicit **Limits** section (reads documents and Python, does not execute
  the target except through the given command; skips archives/vendored trees;
  only two mechanical fixers exist);
- publishes its own measured number rather than a capability claim: *"149 findings
  across 4 detectors … plus `duplicate-constant` honestly UNRUN"* (`README.md:211`).

That last line is the one place a `C:/Azazael/azazael` path appears in prose
(`README.md:211`) and it is a provenance reference to where the measurement was
taken, not a hard-coded runtime path. Acceptable as-is; worth a one-line "(the
author's tree)" if the repo goes public.

---

## 5. Own vs borrowed

| Item | Ownership |
|---|---|
| all seven `tools/*.py` | **own** — no import from outside the directory |
| all six `tests/*.py` | **own** — path set to local `tools/` |
| `aio/flaming_sword.aio.json` | **own** |
| `README.md`, `LICENSE`, `NOTICE` | **own** |
| `config.example.json:4-5` | **borrowed** — references monorepo `tools/platform_claims.py` and `docs/platforms/claims.json`, neither present here |
| `config.example.json:2` | **borrowed** — monorepo constant names |

Nothing else is borrowed. The project does not read, import or shell out to any
sibling project; the dependency direction runs the other way (CRADLE's
`PARTS` reaches *into* this tree — `Project_CRADLE/cradle.py:73` sets
`SWORD_TOOLS = REPO / "Project_FLAMING_SWORD" / "tools"`), which affects CRADLE's
verdict, not this one.

**Note on `tools/sentinel.py`:** it is present here as the frame-claim resolver.
The coordinator's brief describes it as "THE REAPER" sentinel component of CRADLE.
From this tree's own README, `sentinel.py` is the companion that refuses to let a
frame be acted on when its claims do not resolve — CRADLE consumes it rather than
owning it. This project is therefore the **owner** of that component, which is a
reason it publishes first, not a blocker.

---

## 6. Verdict

**STANDALONE.** No code coupling to `CORE`, `src/` or any sibling project; all
seven tools load each other by path; tests are self-contained; licensing is in
place; the README states what it refuses to claim.

**Blocking item for publish (one):**
`config.example.json:4-5` ships a machine-absolute interpreter
(`C:/Azazael/.venvs/py315t/Scripts/python.exe`) and two monorepo-relative paths
(`tools/platform_claims.py`, `docs/platforms/claims.json`), so the example
config's `stale-claims` detector cannot run on any other machine — and because the
key is present-but-wrong, it does not produce the honest `UNRUN` the README
promises.

**Non-blocking, worth a line before publish:** no `pyproject.toml` (dependencies
undeclared, harmless while stdlib-only); `README.md:211` cites the author's own
tree as the measurement site.

**Not verified here:** nothing was executed. A fresh-clone import-and-run check is
still owed by the coordinator, and `python tools/sword.py --self-test` (README's
seeded-fixture test, both directions) is the command that would prove the loop.
