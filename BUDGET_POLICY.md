# Adaptive budgets — investigation and design (2026-09-12)

**Question asked:** the tooling "is not working with limits" — can the limits /
budgets auto-expand as necessary?

**Answer:** they could not, because they were not budgets at all — they were
constants, and hitting one did not fail, warn, or adapt. It silently returned
*less*. That is worse than a hard failure: the artifact still looks complete.

This document records the audit, the fix, and the evidence.

---

## 1. What was actually capped (audit)

| Tool | Cap | Fixed value | Failure mode when hit |
|---|---|---|---|
| `repo_audit.py` | `--max-files` | 2000 | `_files()` returns early; `file_budget_hit: true`, but no re-run ever raised it |
| `repo_audit.py` | `--pattern-cap` | 25 | `shown` truncated per pattern; counts were exact but the locations were lost |
| `repo_audit.py` | `--phase-timeout` | 120 s | phase returns `{}` / partial; `*_timed_out: true`, nothing adapts |
| `repo_audit.py` | `uncovered[:50]` | **hard-coded slice** | **the only record of the backlog**. The real backlog was 262 modules; the summary ever showed 50. This is the concrete instance of "not working with limits". |
| `repo_audit.py` | `bad[:10]` | hard-coded slice | compile errors past the 10th were invisible |
| `mutate.py` | `--max` | 20 | sites sampled; the rest never tested, and the sample was silent |
| `mutate.py` | `--timeout` | 300 s | a timed-out mutant counted in the **denominator** but not as a kill, so a slow suite *silently depressed the score* |
| `live_monitor.py` | freshness | red > 15 min | display only (acceptable) |

Conclusion: none of these expanded. Every new module added to the repo made the
reading quietly worse, which is exactly why the backlog reached 262 while the
summary looked stable at 50.

Two of the caps were also **wrong in kind**, not just small:

* `uncovered[:50]` — a *display* concern encoded as an *inventory* limit.
* mutation timeouts — an *indeterminate* verdict counted as a *decisive* one.

---

## 2. Design (`scripts/budget_policy.py`, stdlib only)

A budget is floor / value / ceiling plus a history, kept in
`state/budget_policy.json`:

```
escalate(name, reason, factor=2, needed=None)  # grow toward the ceiling
settle(name, reason, factor=2)                 # shrink back toward the floor
set_value(name, value, reason)                  # explicit flag wins, still recorded
```

* **Bounded both ways** — auto-expansion cannot run away (ceilings), and one
  busy run cannot inflate budgets permanently (settling).
* **`needed`** — a cap can jump straight to the size the last run wanted
  instead of doubling its way there over many runs (a pattern with 7 242 hits
  against a cap of 25 must not take eight runs to become useful).
* **Recorded** — every change appends `{at, budget, action, from, to, reason}`
  to the ledger's `history`, so an expansion is auditable rather than invisible.
* **Never raises** — a missing or corrupt ledger degrades to the defaults;
  inverted bounds are repaired. A bad budget file must not stop the audit it is
  budgeting.

Registry (floor = the value that was previously hard-coded, so the first run
behaves exactly as before):

| Budget | floor | ceiling |
|---|---|---|
| `audit.max_files` | 2000 | 40000 |
| `audit.pattern_cap` | 25 | 1000 |
| `audit.phase_timeout` | 120 | 3600 |
| `audit.uncovered_shown` | 50 | 2000 |
| `audit.bad_shown` | 10 | 500 |
| `mutate.max_mutants` | 20 | 2000 |
| `mutate.per_test_timeout` | 300 | 3600 |
| `audit.pattern.<name>` | seeded from `audit.pattern_cap` | 1000 |

Per-pattern budgets are registered dynamically (`bp.ensure`) the first time a
pattern is seen, so adding a new risk pattern needs no code change here.

---

## 3. What changed

**`scripts/repo_audit.py`**
* budgets come from the policy; an explicit flag wins *and is recorded*
* after each run: `file_budget_hit` → grow `max_files`; any phase timeout →
  grow `phase_timeout`; each pattern grows **its own** budget when
  `count > cap` (with `needed=<count>`), stays put inside the band, and
  shrinks only with real headroom (`count * 2 <= cap`)
* the `uncovered[:50]` slice is gone: `testmap_uncovered()` is now split out
  and the **full** list is written to `state/test_backlog.json`; the summary
  keeps the exact `uncovered_count` and a slice whose size is itself a budget
* `adaptive` + `budget_policy` snapshot embedded in `state/audit_summary.json`

**`scripts/mutate.py`**
* `--max` / `--timeout` default to the adaptive values; explicit flags recorded
* `score = killed / (killed + survived)` — timeouts are **excluded** and
  reported as `timed_out`; a timeout is not a pass (exit 1)
* `sampled` / `total_sites` recorded; sampling escalates `max_mutants`
* durable `state/mutation_history.json` (per-target, de-duplicated, capped 200)
  so one target's run no longer overwrites the last

**Recorded by the system itself:** `state/budget_policy.json` (ledger +
history), `state/test_backlog.json` (262 modules), `state/mutation_history.json`.

---

## 4. Evidence

```
$ python scripts/repo_audit.py
audit: 838 files (budget 2000)
  compile: 838 ok, 0 bad
  testmap: 435 src modules, 262 unnamed in tests
wrote state/test_backlog.json (262 modules)
budgets escalated: audit.pattern_cap->1000

$ python scripts/budget_policy.py
audit.pattern_cap            1000  (floor 25, ceiling 1000)
...

$ python scripts/mutate.py --target src/CORE/WORMS/expansion/exmachina_operators.py \
      --tests tests/test_exmachina_operators.py
mutate: 308 sites in src/CORE/WORMS/expansion/exmachina_operators.py
mutate: 11/20 killed (score 0.55)
  adaptive: escalated mutate.max_mutants -> 40; settled mutate.per_test_timeout
```

* `tests/test_budget_policy.py` — 15 tests: defaults, corrupt ledger,
  inverted bounds, escalation, `needed`, ceiling clamp, settle-to-floor,
  explicit set, snapshot, and that both consumers read the policy (guards
  against a re-hard-coded `[:50]` or `default=20`).
* 476 tests pass across the affected suites; the new modules import and
  escalate/settle correctly under both `python.exe` and
  `.venv-3.14t/Scripts/python3.14t.exe`.

---

## 5. Bugs this investigation surfaced (and fixed)

1. **`src/AOA/cli/aoa_cli.py` did not parse.** The compile phase found it —
   a botched merge had left an orphaned `try:` (no `except`) plus a stray
   duplicate `except`: the `import arms.support_arms` block was missing its
   handler and `import arms.kali_arm` had two. The identical corruption
   appeared **5 times** in the file (copy-pasted `cmd_*` functions). Fixed;
   compile phase now reports `838 ok, 0 bad`.
2. **Mutation timeouts depressed the score** (see above).
3. **`EvolutionEngine.save_checkpoint()` could silently persist nothing.**
   `_get_store()` swallowed a transient SQLite-lock exception and returned
   `None`, so the save no-opped while returning a success-shaped dict, and
   `load_checkpoint()` then returned `False`. Fixed: `_get_store()` retries
   (3 attempts, linear backoff) and `save_checkpoint()` returns an honest
   `persisted: bool`. Regression tests added in `tests/test_nsga2.py`
   (failed-write reported; transient lock recovered).
4. **A brittle float-identity test** — `assertIs(0.1, 0.1)` cannot hold across
   two code objects. Fixed to compare by value (+ type) in
   `tests/test_exmachina_mutagen.py`, and `tests/test_proteus_hooks.py` was
   filtering trainer defaults to `bool` only, so the float knobs
   (`val_ratio`, `test_ratio`) looked like removed kwargs. Both fixed.

---

## 6. Per-pattern budgets (2026-09-12, closes 6.4)

One budget per pattern. Before this, `print_in_src` (7 242 hits) shared a cap
with the risk patterns and dragged it to the ceiling on its own, so
`bare_except`, `todo` and `shell_true` were showing a cap of 1000 they never
needed.

```
audit.pattern.bare_except     25   (2 hits)
audit.pattern.todo            25   (24 hits)
audit.pattern.shell_true      25   (17 hits)
audit.pattern.hardcoded_home 165   (165 hits - exact, no longer 1000)
audit.pattern.print_in_src  1000   (7 242 hits, clamped by its ceiling)
```

Two bugs were found and fixed while landing this:

1. **Polluted seed.** New patterns were seeded from the *current value* of the
   shared `audit.pattern_cap` — which noise had already pushed to 1000 — so
   every pattern started at its ceiling. The seed is now the **floor**
   (`bp.bounds(...)[0]`), and the shared cap is reset to it.
2. **Oscillation.** Settling whenever `count <= cap` made a budget flip:
   165 hits at cap 165 settled to 82, which the next run escalated back to
   165. Settling now requires real headroom (`count * 2 <= cap`), verified
   stable over three consecutive runs.

## 7. Honest caveats

* `print_in_src` still parks at its own ceiling of 1000. That is bounded and
  it no longer taxes the risk patterns, but 7 242 `print(` calls in `src/` is a
  real code-quality signal, not a budget problem.
* `audit.pattern_cap` survives only as the inheritance seed for new patterns.
  It is deliberately no longer the operative cap.
* `local_memory._init_db()` connects with `timeout=2` while `_get_conn()` uses
  `timeout=15` / `busy_timeout=15000`. Left alone deliberately (the short
  timeout keeps startup from blocking on a locked DB); the retry in
  `_get_store()` is what makes the difference non-fatal. Worth revisiting if
  construction-time failures show up again.
* The 262-module backlog is now **visible and complete** but still
  **untriaged** — `state/test_backlog.json` is the input to the test / delete /
  vendor classification, not the result.
