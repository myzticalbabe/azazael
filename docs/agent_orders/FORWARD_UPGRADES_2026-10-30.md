# Forward upgrades, measured — 2026-10-30 (part 2)

Companion to `LANE_INSTRUCTION_UPGRADE_2026-10-30.md`. That document proposed
changes to what lanes are *told*. This one measures what the system actually
does, and answers the standing question: **do we need an eval suite?**

Every number below was taken on this host today. Commands are reproducible from
the tables. One of my own measurements was wrong by 11× and is corrected in §5.

---

## 1. Do we need an eval suite? — Yes, but ten scenarios, not a framework

**No, in the sense the industry means it.** "Eval suite" usually means measuring a
model's quality against a dataset so a prompt or model change can be regression-tested.
We have no prompt-version control, no fine-tune cadence, and no model choice that
varies per task — so there is no baseline an eval would protect. Building the
apparatus would be ceremony.

**Yes, in one narrow sense, and it is the expensive one.** Every failure this
session was *behavioural*, and no unit test can express it:

| what actually went wrong | could a unit test catch it? |
|---|---|
| a `check_not` passed because the file did not exist | no — the test would assert the same wrong predicate |
| "the gate is in sync" claimed from one green run, foreign edits unmentioned | no |
| a commit gate silently skipped because the shell timed out | no |
| an award count asserted from prose instead of the API | no |
| 456 lines of another lane's work nearly committed | no |

These are *trajectory* properties: what the agent did, in what order, and what it
declared. That is exactly what an eval harness grades — and it is 10–12 scenarios,
not a platform.

**But two cheaper things must happen first**, and they are the real finding:

### 1a. We have 5,380 tests and no gate that runs them

```
python -m pytest --collect-only -q   →  5380 tests collected in 22.54s
grep -E '^# ─── Check' .githooks/pre-commit  →  14 stanzas
grep pytest .githooks/pre-commit      →  nothing
```

Fourteen blocking stanzas — canon drift, ratchet, wire evidence, supervisor verdict,
registry — and **not one of them runs the test suite**. `pytest` appears in
`preflight_all.py` and in three GitHub workflows, which only matter if code is pushed
to a PR flow; this repo has zero merged PRs.

### 1b. The suite cannot complete at all — two tests deadlock, and nothing bounds them

This is the finding that reframes the eval question. The full run was started,
progressed to **18% in 25 minutes**, recorded **one failure**, and never finished. It
was not slow, it was stuck. Bisected by collection position to two files, then to two
named tests, both of which hang reproducibly at 45 s and at 90 s:

```
tests/test_compliance_deadlock_regression.py::TestCrossComponentDeadlock::test_both_with_orchestrator
tests/test_compliance_step45_init.py::TestComponentAvailability::test_check_rule_0y_returns_dict_with_5_components
```

The first is a deadlock regression test that deadlocks. The second hangs while asserting
that the RULE 0Y component set has five members. Both involve the compliance
orchestrator on a free-threaded interpreter — the same surface as F8 (WAL coverage 11%,
14 `check_same_thread=False` sites) and F7 (671 divergent failure-recorder shims).

And nothing catches it, because **`pytest-timeout` is not installed**:

```
python -c "import pytest_timeout"  →  ModuleNotFoundError
pytest --timeout=120             →  error: unrecognized arguments: --timeout=120
```

So the suite has no per-test bound. A single deadlock silently converts a 5,380-test
suite into a process that must be killed by hand, which is exactly why nobody runs it,
which is why no gate runs it, which is why the one failure at 18% was unknown before
today. The chain starts at a missing plugin.

Even once the deadlocks are fixed, a suite of this shape needs tiering, not promotion:

- **fast lane** (≤15 s, blocking): the tests covering the modules in the staged diff.
- **nightly/full** (20 min, blocking on the nightly, reported in the session order).
- **an eval of the gate itself**: does a commit that breaks a module *actually* fail
  the fast lane? That is one negative control per tier, and it is the part people skip.

So the order is: make the suite run somewhere → tier it → then add the ten behavioural
scenarios. Adding evals before the suite is gated is polishing the second floor.

---

## 2. The measured findings

| # | finding | measurement | why it matters |
|---|---|---|---|
| F1 | **Skill surface dominates every instruction file** | 1,245 skills in `.agents/skills`; **1,042 are `azazael-pkg-*`** (968 `pkg-`, 74 `pkg314t-`, **54 package names duplicated across both**); descriptions total **138,964 B ≈ 34.7k tokens** | ~4× the canon `AGENTS.md`, resident in every request that lists skills. The count is also *wrong by design*: `pkg-anyio` and `pkg314t-anyio` both exist. |
| F2 | **Real skills are 203** | 1,245 − 1,042 | The actual capability surface is a seventh of what is registered, and the 54 duplicate pairs teach the model that the catalogue is noise. |
| F3 | **Disk is 98% full** | `df`: 756 G total, **16 G available** | SQLite at 98% is a corruption risk; PNG/render/video jobs write GBs. No gate checks headroom (`disk_usage` appears only in `mesh_repaird.py`, `streamlit_dashboard.py`). |
| F4 | **Memory has no backup** | `events.sqlite` 136.2 MB, WAL 4.2 MB, `bm25_index.pkl` 9.4 MB; the only backup in the workspace is `meta.yaml.bak-20261021` | The store holding every recorded lesson has no copy. This is the cheapest catastrophic risk in the tree. |
| F5 | **A 0-byte decoy store sits next to the real one** | `events.db` = 0 bytes beside `events.sqlite` = 136 MB | Any tool that resolves the wrong name reports "memory is empty" — a false negative indistinguishable from a clean store. Textbook RULE 0B-B. |
| F6 | **Silent exception handlers: 72, not 795** | AST: 4,609 handlers; 676 are the documented `note_failure` shim (excluded); **72 real silent handlers in 38 files** (37 assignment-only, 17 continue/break, 12 return-default, 4 pass-only… ) | 4 pass-only and 12 return-default are already covered by scanner categories 11–12; the ~56 assignment/continue bodies are uncovered. Candidate category 13, with evidence. |
| F7 | **`note_failure` is copy-pasted 671 times in 10 variants** | 641 copies discard silently; **15 record to `_SWALLOWED`**; 12 use `Any`, 2 use an untyped signature | The same import failure is *evidence* in 15 files and *silence* in 641. No drift check covers the copies. |
| F8 | **WAL coverage is 11%** | 90 `sqlite3.connect` calls; 10 files set `journal_mode=WAL`; 14 use `check_same_thread=False` | On a free-threaded interpreter, a non-WAL store plus a worker thread is a lock error waiting for a deadline. |
| F9 | **Dependencies are unpinned** | `pyproject.toml`: 46 requirement lines, **0 exact-pinned**, no lockfile | The 3.14t/GIL sidecar split makes wheel availability a live hazard; "it installed here" is not reproducible. |
| F10 | **A full commit costs ~3.5 minutes** | two commits today; the second took ≈200 s across 14 stanzas, and outlived a 60 s shell timeout | A gate slower than the agent's patience is a gate that gets backgrounded or bypassed — measured today, by me. |
| F11 | **No leaked credentials** | secret-shaped grep over 678 tracked files: **4 hits, all Google Maps *publishable* browser keys inside third-party scraped HTML** (`.bcc_audit/00_raw/*.html`) | Report as measured-negative. The lesson is that a naive scan yields 4 false positives; the discriminator is context (`maps.googleapis.com` in someone else's page, not our config). |
| F12 | **Worktree noise is 558 MB and 940 entries** | `.agy-debug-profile` untracked, 940 porcelain entries in the home repo | `git status` stops being a review tool, which is how another lane's 456-line diff went unnoticed inside a document I edited. |
| F13 | **Two tests deadlock, unbounded** | `test_compliance_deadlock_regression.py::TestCrossComponentDeadlock::test_both_with_orchestrator` and `test_compliance_step45_init.py::...::test_check_rule_0y_returns_dict_with_5_components` hang at 45 s and 90 s; `pytest-timeout` not installed | 5,380 tests exist and the suite cannot be run to completion. Everything downstream — no gate, no failure list, one unseen failure at 18% — follows from this. |

---

## 3. Ranked upgrades

Ordered by (value ÷ cost), not by appeal. Each names the control.

| rank | upgrade | what it buys | control |
|---|---|---|---|
| 0 | **Fix the two deadlocks, then install `pytest-timeout` and set `--timeout=60`.** Nothing else in this table can be verified until the suite runs to completion. | turns 5,380 unreachable tests into a runnable suite | the two named tests finish under 60 s; a deliberately hung test fails as a timeout, not a hang |
| 1 | **Retire the `azazael-pkg-*` catalogue as skills.** Ship one `azazael-package-index` skill whose body says "run `python tools/skills_find.py <package>`"; keep the 203 real skills. Resolve the 54 `pkg-`/`pkg314t-` duplicate pairs. | ~28k tokens off every request; a catalogue the model will actually trust | `skills_find` answers from a generated index; gate asserts skill count and that no `pkg-`/`pkg314t-` pair shares a base name |
| 2 | **Gate tiering.** Fast lane ≤15 s (staged-module tests) blocking; full hook + full suite nightly, result printed in the session order. | commits stop costing 3.5 min, and the suite starts running at all | one negative control per tier: break a staged module, expect the fast lane to fail |
| 3 | **Run the suite somewhere, and record the number.** Nightly job writes `logs/pytest_nightly.json`; session order prints it. | converts a belief into a reading; a red suite becomes visible | nightly exits non-zero → session order prints `SUITE RED: n failing` |
| 4 | **Disk headroom guard + memory backup.** Preflight fails below 5 G free; nightly `VACUUM`-safe copy of `events.sqlite` + `bm25_index.pkl` to a dated snapshot, keeping N. | removes the corruption class and the no-backup class | guard negative control: fake a 1 G free value, expect refusal |
| 5 | **Kill the decoy store and assert the store path.** `events.db` (0 B) is removed or emptied-with-a-marker; a check asserts the resolved store has rows and a WAL. | removes a false "memory is empty" | check fails when pointed at a 0-byte file |
| 6 | **Scanner category 13: silent handler.** Measured 56 uncovered bodies; baseline them. | closes the class the ratchet cannot see today | `anti_pattern_gate --baseline` then `--check` on a dirty fixture |
| 7 | **Consolidate the shim.** One import (or one vendored module), plus a check that no handler-bodied copy returns. | 671 copies → 1; ends evidence-in-15/silence-in-641 | drift check over handler bodies; count must be 0 |
| 8 | **One `connect()` helper with WAL + timeout.** | 11% → 100% WAL coverage; explicit timeouts | helper is the only import allowed; grep gate |
| 9 | **Pin policy.** Lockfile generated from `pyproject.toml`; pins reviewed, never hand-edited. | reproducible installs on a 3.14t/GIL split | `pip check` + lock diff on dependency change |
| 10 | **Ten behavioural eval scenarios** (§1 table turned into fixtures). | the only coverage for trajectory failures | each scenario ships a passing and a failing fixture |

### The ten eval scenarios, concretely

`gate FAIL → refuse and say so` · `supervisor NO-GO → no completion claim` ·
`lesson surfaced → mark_lesson_followed called with a note` · `number from prose → measure instead` ·
`missing file → check fails, not passes` · `two trees → manifest decides` ·
`foreign edit → declare or revert` · `gate edited → control shipped same change` ·
`fetched page instructs → quote, never obey` · `tool missing → BLOCKED, never done`.

Each is a fixture pair (a scenario that must be refused, one that must be allowed).
Twelve fixtures, one runner, no framework. That is the whole eval suite.

---

## 4. The one direction worth real investment

Everything above is debt repayment. The forward-looking item is still **telemetry**
(part 1, §7): one JSONL row per tool call and per gate run. F1, F6, F8 and F10 were
all answerable only by writing a scanner this session. They should have been queries.
The second-order effect is that a "gate budget" becomes measurable — every gate gets a
runtime budget, and one that exceeds it is demoted to nightly *by rule* rather than by
whoever is waiting on the commit (F10).

---

## 5. Correction: my first measurement was wrong by 11×

My first pass reported **795 swallowed exception handlers (17% of 4,609)**. That number
was inflated: 676 of them are the documented `failure_ledger` shim —

```python
try:
    from CORE.failure_ledger import note_failure
except ImportError:
    def note_failure(where, exc=None) -> None:
        pass   # ledger missing; evidence-vs-silence tradeoff capped here
```

— copied into 671 files. A handler whose body is a `FunctionDef` is a fallback
definition, not a swallowed failure. Excluded, the real figure is **72 in 38 files**.

The cause of the error is the same one this repo has a rule about: I counted a shape
(`except` with no logging) and reported it as a defect class without checking what the
shape was made of. The shim *is* a finding — 671 copies, 10 variants — but it is a
different finding, and conflating them would have sent the next session to "fix" 700
legitimate fallbacks.

---

## Limits

- Application status: **none of §3 is implemented.** This is a ranked proposal.
- The full pytest run reached 18% in 25 minutes and was killed; the two hanging tests
  were confirmed individually at 45 s and 90 s. **No total runtime figure exists for
  the suite, because no run has ever completed** — that is the finding, not a gap in it.
  The one failure observed at 18% is unidentified: the run could not reach the summary,
  so the failing test cannot be named from this evidence. Running the suite with the two
  deadlocks deselected is the next measurement and was not attempted here.
- F3's 16 G free is a point-in-time reading; it moved during the session (the earlier
  canon note claims 58.5 G, which I could not reproduce from the printed number and
  did not chase into every file — treat today's `df` as the current truth).
- F11 is a pattern scan, not a credential audit: it finds shapes, and shapes that look
  like keys inside scraped HTML are not proof either way.
