# Compliance Rate — measured, 2026-10-03

Answers: *are PMB suggestions being implemented, what is the compliance rate, and
how do we improve suggestion quality for compliance?* Every number below was
measured this session, not estimated.

---

## 1. Are PMB suggestions being implemented?

**Before this session: no, because the loop could not run.** `lesson_impact`
returned `n_outcome_turns: 0` on every window — not "no useful lessons", but
*structurally no data*. Root cause:

- `lesson_impact` joins surfaced lessons to turn outcomes via the `agent_actions`
  table.
- That table is written only by PMB's `PostToolUse` `track-action` hook.
- PMB installs that hook for **claude-code**; this host is **Codebuff**, which is
  absent from `pmb.cli.hooks._AGENT_CAP` → **no hook ever fires**.
- The table did not exist; every read is wrapped in `except` → the metric
  reported a clean zero forever.
- PMB's designed fallback, `pmb ambient-watch`, observes **git file changes
  only** — it can never produce a test/build *outcome* signal.

**Now: yes, and it is measured.** `tools/pmb_session_observe.py` writes the same
rows through PMB's own `insert_agent_action`, wired at the two triggers
guaranteed to fire — `pytest_sessionfinish` (`conftest.py`) and the pre-commit
hook. Verified end-to-end:

| Metric | Before | After |
|---|---:|---:|
| `n_outcome_turns` | 0 | 2 |
| `agent_actions` rows | 0 (no table) | 5 |
| `baseline_success_rate` | null | 1.0 |
| e2e checks | — | **11/11 pass** |

Follow-through signals were also fed: 8 surfaced lessons marked
(`surface_id` 322–328) — 5 followed, 3 not-applicable.

## 2. What is the compliance rate?

There are two distinct rates; conflating them hides which one is broken.

### Gate compliance — 4 of 5 enforced gates pass

| Gate | Status | Measured |
|---|---|---|
| Bulk-diff focus (`scripts/commit_gate.py`) | ✅ | every session commit passed |
| Anti-pattern ratchet (`tools/anti_pattern_gate.py`) | ✅ | 2,224 findings = baseline, 0 regression |
| Canon drift (`tools/canon_drift_check.py`) | ✅ | 1,238 identical, 0 drift |
| Test suite | ✅ | 62 passed / 1 skipped (new files); full suite 3,575 pass |
| Type gate (`tools/type_check_gate.py`) | ❌ **unrunnable** | `basedpyright` not installed anywhere on this host |

**Gate compliance = 4/5 = 80%**, and the one failure is an environment gap, not a
code defect — the gate correctly refuses to report a clean tree when it cannot
run.

### Work compliance — 6/6 session commits landed green

`7e0b6c72` → `9902fed6` → `a3895162` → `9480d9c9` → `47585ab4` → `36552752`.
Every one passed the 4-check hook; the hook **blocked my own first commit**
(bulk gate) — proof it is live, not decorative. A = B = `36552752`.

### Backlog compliance — the real debt number

- 2,224 findings across 657 files ≈ **3.4 findings/file**.
- Composition: `unicode_emoji` 1,260 · `import_inside_function` 950 ·
  `hardcoded_win_path` 14.
- Three of seven categories are already at **zero** (`t_string`, `os_system`,
  `cls_new_cls_factory`).
- The ratchet makes this a *ratchet*, not a *fix*: it can only go down. The
  backlog is being paid down, not closed.

## 3. How do we improve suggestion quality for compliance?

Ordered by leverage.

1. **Feed the loop before trusting it.** `lesson_impact` now has 2 outcome turns;
   the tool itself says it needs **≥20** for "thin" and **≥50** for "ok", plus a
   real no-lesson baseline. Until then every per-lesson verdict is
   `insufficient`. **Do not rank or prune lessons on this data yet** — acting on
   n=2 is exactly the failure the tool's own caveat warns about.
2. **Fix the adherence denominator.** `followcheck` needs `surface_ids` on each
   action to infer follow-through without self-report. That wiring now exists;
   the next test run and commit will populate it. Until then, adherence is
   measured only from the 328 historical `lesson_surfaces` rows.
3. **Record lessons that are *checkable*, not *memorable*.** The lessons that
   pulled weight this session were mechanical ("capture output before `| tail`",
   "a `.gitignore` rule does not untrack"). Those convert into gates. Prose
   lessons ("remember to be careful") have no outcome signal and will always
   read `insufficient`.
4. **Pair every lesson with a gate.** The enforcement ladder (already a PMB
   lesson, `surface_id` 322) says: clock/gate first, prose last. A lesson whose
   compliance can be asserted by a hook produces an `agent_actions` row; a
   lesson that lives only in canon produces none. **Gate-able lessons are the
   only ones the loop can ever score.**
5. **Install `basedpyright`** to bring the type gate back to 5/5. It is the one
   measurable gate that is dark.
6. **Give Codebuff a capability entry in PMB.** The root cause of the dead loop
   is a missing row in `_AGENT_CAP`. A `codebuff` entry pointing at the
   `project-observer` mechanism (which now exists) prevents the next agent from
   re-deriving this whole investigation.

---

## Bottom line

| Question | Answer |
|---|---|
| Implementing PMB suggestions? | **Yes now** (was impossible: loop structurally dead). 8 follow signals fed; observer verified 11/11. |
| Compliance rate? | **Gates 4/5 (80%)** — type gate dark. **Commits 6/6.** **Backlog 2,224 findings**, ratcheted. |
| Improve suggestions? | Make them **checkable** and **paired with a gate**; wait for n≥20 outcomes before ranking; fix the missing `codebuff` capability row and install `basedpyright`. |
