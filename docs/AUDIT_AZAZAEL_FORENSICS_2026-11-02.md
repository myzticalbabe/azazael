# AUDIT — azazael-forensics (auditor 15 of 18, FULL AUDIT 2026-11-02)

**Target:** `C:/Azazael/azazael-forensics` — standalone tree, own `.git`, landed 2026-10-28
as "Yggdrasil Cleave #11".
**Method:** read-only. Files read in full: `README.md`, `CAPABILITIES.md`, `forensics/portable.py`,
`forensics/home.py`, `pyproject.toml`, `.gitignore`, `tests/test_smoke.py`, `tests/test_home.py`.
Nothing executed — no terminal was used for this audit.

**Verdicts up front:**

| Question | Answer |
|---|---|
| Publishes as a standalone repo? | **YES mechanically, NO as advertised.** |
| Is it "the forensic investigation suite"? | **NO.** It is an engineering defect-detector layer for the azazael tree. |

Both verdicts are argued below rather than asserted.

---

## 1. Detectors and the exit-code contract

Four modules are native to the tree (`forensics/`): `goal_liveness.py`, `marker_audit.py`,
`count_derivation.py`, `board_stale.py`. Their subjects, per `README.md`:

| Module | Hunts |
|---|---|
| `goal_liveness` | stale open items at 0% progress, duplicate titles, settled-but-open |
| `marker_audit` | false-OK marks (recall/fanout, ok-without-write) |
| `count_derivation` | prose numbers vs artifact JSON/markdown counts |
| `board_stale` | duplicate keys, completed-vs-open contradictions |

The contract is `0` clean · `1` findings · `2` ENVIRONMENT. **The `2` is real, not decorative** —
`tests/test_smoke.py::test_fail_closed_missing_store` launches each of the four as a subprocess
against a non-existent store and asserts `returncode == 2`. That is the correct shape of a
control: it proves the detector refuses rather than reporting a clean tree it never read.

**Limitation of that contract, stated plainly:** `2` protects against *false green on an absent
store*. It does not protect against *false green on a present store*. There is no fixture in
`tests/` that a detector is known to FIRE on. So the suite proves the oracles cannot be blinded
by absence, and proves nothing about whether they can see. That is half of RULE 0B-C.

## 2. The portability contract — the module contradicts its own docstring

`forensics/portable.py:6` states:

> "There are NO machine-default paths in this tree."

That is **false for one of the two locators.**

- `locate_pmb_db` (`:23-39`) is clean. Precedence: explicit arg → `PMB_WORKSPACE_DIR` → raise
  `Environment`. It fails closed with a message that says why. No default path anywhere.
- `locate_board_db` (`:42-...`) **smuggles two things the claim excludes:**
  - `:55` — `Path.home() / ".azazael" / "telemetry_store.db"`. That is a machine-default path:
    it is the azazael install convention, resolved from the home directory. On a machine where
    azazael was never installed it silently does not match, but on one where a *different*
    user's or a *stale* azazael store exists it matches without being asked.
  - `:64` — `from CORE.MemoryBus import _MEMORYBUS_DB_PATH as mbp`, inside a
    `try/except Exception: pass` (`:67-68`). A `CORE` import in the module whose entire job is
    to be free of `CORE`, wrapped in a bare swallow so it can never be observed failing.

It does ultimately fail closed, so no false green results. But the tree's headline claim is
about *the absence of coupling*, and the claim does not hold for the board path. Worse, the
swallowed import is the exact silent-failure pattern this project's own canon treats as a
recurring defect class — a `try/except` that converts "the monorepo is missing" into "nothing
happened".

**Remedy is small:** delete `:51-68` and let the precedence be explicit arg → `FORENSICS_BOARD_DB`
→ `AZAZAEL_MEMORY_DIR` → raise. The sibling-import branch buys nothing that the environment
variable does not already buy, and costs the portability claim its truth.

## 3. `home.py` — the adapter is honestly coupled, but the headline overstates it

`home.py` does not secretly import the monorepo; it *launches* it as subprocesses with `cwd=home`
and passes exit codes through. That is a bridge, not a dependency, and when the home checkout is
absent `locate_home` raises and the tool exits `2`. Correct behaviour.

The problem is the framing, in three places that disagree:

- `home.py:5` docstring: "inventories all **49** named forensic tools".
- `README.md`: "azazael's **49**-tool forensic set".
- `home.py` `TOOLS` registry: **52** entries (4 native + 33 portable + 15 coupled), and
  `tests/test_home.py::test_registry_counts` asserts exactly `52`.

So the documented figure is stale by three and the test enforces the true one. A reader of the
published README is told 49, and the number they get from `inventory` is 52.

The substantive point: **48 of the 52 tools live in the monorepo and are unreachable without it.**
`python -m forensics.home inventory` prints `ENVIRONMENT: azazael home not located` and exits 2
on a clean machine. So a published `azazael-forensics` repo delivers **4 working detectors**, and
the other 48 become available only if the user separately clones azazael. That is a legitimate
design (one source of truth, no drift — the docstring argues it well) but it must be the first
thing the README says, not a footnote, or the repo over-promises on install.

## 4. Test coverage

Two files, six tests:

- `test_smoke.py` — `test_imports`, `test_help` (all four `--help` exit 0), `test_fail_closed_missing_store` (all four exit 2 on absent store).
- `test_home.py` — registry classes, registry counts (52), no-orphan-references.

Coverage is honest but thin, and self-contained: `test_smoke` uses `tmp_path` and subprocesses,
`test_home` imports the registry only. **No test requires the monorepo**, which is exactly right
for a portable tree.

Missing, in order of value:
1. **A known-bad fixture per detector** — one row the detector must flag, asserting exit `1`
   and the finding text. Without it, "exit 2 on nothing" is the only proven behaviour.
2. **`count_derivation`'s positive path** — it takes a file plus `--root`, the only detector with
   a non-database input, and the only one where a wrong-but-present input could silently produce
   zero findings.
3. **`locate_board_db` precedence test** — the branch containing the two defects in §2 has no
   test at all, which is why they survived.

## 5. Packaging and license

`pyproject.toml` is present and sane: `name = "azazael-forensics"`, `version = "0.1.0"`,
`requires-python = ">=3.10"`, `dependencies = []` (true — stdlib only), and four console scripts
(`forensics-goal-liveness`, `forensics-count-derivation`, `forensics-marker-audit`,
`forensics-board-stale`). `.gitignore` is correct.

Two blocking gaps for a public repo:

- **No `LICENSE` file anywhere in the tree**, and **no `license` field** in `pyproject.toml`.
  Publishing without one makes the code legally non-reusable (all rights reserved), which
  contradicts the purpose of open-sourcing it. For consistency with the sibling projects, use
  Apache-2.0 — `Project_Nurse_Ratchet/LICENSE` in the monorepo is the canonical copy already in
  this repo's ecosystem.
- **No `NOTICE`**, so any future third-party material has no declared place to be attributed.

Also absent: `forensics.home` has no console-script entry, so the adapter is reachable only by
`python -m forensics.home` while the four detectors get scripts. Minor inconsistency.

## 6. Verdict

**Publishes standalone: YES mechanically, NO as advertised.**

Mechanically it is the healthiest publish candidate found in this audit: stdlib-only, declared
dependencies, a real `pyproject.toml`, a real fail-closed control, self-contained tests, and no
machine path in the PMB branch. It would install and run.

It does not publish *as described* until three things are done:
1. Fix `portable.py` — remove the `~/.azazael` default and the swallowed `CORE.MemoryBus` import
   (§2), so the "no machine-default paths" sentence becomes true.
2. Correct the count — 52, not 49, in `home.py:5` and `README.md` (§3).
3. Add `LICENSE` (Apache-2.0) + `NOTICE`, and state up front that 48 of 52 tools need a separate
   `azazael` checkout (§3, §5).

**Is it "the forensic investigation suite"? NO.**

This is the most important distinction in this report, because the owner's phrase has been
attached to several artifacts in this session. What this tree contains is a set of
**engineering defect detectors** for a software repository: it asks whether *the azazael tree*
is lying to itself — stale goals, false-OK marks, prose numbers that do not match artifacts,
a board whose rows contradict each other.

A forensic investigation suite asks different questions: it ingests evidence from an external
subject, preserves chain of custody, grades source tiers, extracts entities and relationships,
and produces findings traceable to a raw document and a hash. **None of that machinery is here**
— no evidence intake, no tier grading, no entity extraction, no provenance ledger. `README.md`
is candid that the tree "checks outputs" while "the home does work", which is the right
description of what it is and the wrong description of a forensic investigation suite.

So: this tree is not ELIZA's subject matter, and folding it into `Project_ELIZA` to satisfy the
name would repeat the error this session already spent effort correcting.

## 7. What I did not check

Stated so absence is not read as a pass:

- **The four detector bodies were not read.** Their subjects and exit contracts in §1 come from
  `README.md`, `CAPABILITIES.md`, and the subprocess assertions in `test_smoke.py` — not from
  reading `goal_liveness.py`, `marker_audit.py`, `count_derivation.py`, `board_stale.py`.
- **`manifests/kali_canon_118.json` was not read.** Unknown whether it is input data, a
  measurement record, or required at runtime. It is a single file in an otherwise empty directory
  and nothing in the four modules I read references it.
- **Nothing was executed** — no test run, no `inventory` run, no import of the package. Every
  claim about behaviour rests on source and on the assertions the existing tests encode.
- **Git history of this tree was not examined** (3 commits are visible in the monorepo's records:
  `edd8d12`, `490503b`, `892c7f4`) — whether anything was removed or renamed before publication
  is open.
