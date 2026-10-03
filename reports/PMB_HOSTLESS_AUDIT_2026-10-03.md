# PMB hookless-features audit — Codebuff, 2026-10-03

PMB wires **seven** lifecycle hooks, and it wires them for **claude-code**
(`pmb.cli.hooks._claude_hook_specs`). This host is **Codebuff**, which has no host
hook surface. This audits every hook PMB installs and names the equivalent that
now exists here — or records that none does.

| # | PMB hook (claude-code) | What it does | Codebuff equivalent | Status |
|---|---|---|---|---|
| 1 | `UserPromptSubmit` → `prepare-context` | auto-recall: inject matching lessons before the model thinks | **`prepare()` / `recall()` called explicitly** (MCP tools) | ✅ manual |
| 2 | `SessionStart` → `session-restore` | rebuild "where you left off" after compaction | **`session_brief()`** MCP tool | ✅ manual |
| 3 | `PreToolUse` → `pretool` | fire a matching rule at tool-call time (advisory) | **none** — needs a pre-tool hook | ❌ no equivalent |
| 4 | `PostToolUse` → `track-action` | write the `agent_actions` row (the outcome-loop input) | **`tools/pmb_session_observe.py`** at the test + commit triggers | ✅ fixed |
| 5 | `Stop` → `lesson-followcheck` | infer which surfaced lessons were followed | **`run_followcheck()`** via the engine, wired into the observer | ✅ fixed |
| 6 | `Stop` → `autowrite` | journal the turn if the agent didn't | **`pmb ambient-watch .`** (project observer) | ✅ available |
| 7 | `Stop` → `capture-exploration` | auto-memoize an exploration from the transcript | **`tools/pmb_observe_transcript.py`** + `record_exploration()` | ✅ manual |

## What was actually broken, and why

Only **#4** was *silently* broken, and it took **#5** down with it: both read the
`agent_actions` table, which nothing on this host wrote. `lesson_impact` therefore
reported `n_outcome_turns: 0` forever, and the adherence pass had no actions to
match against. Everything else degraded to "manual" rather than "dead" — the tool
still worked if called.

The distinguishing symptom was not an error but **a number that never moved**. A
metric that reads a table nothing writes is dead code wearing a zero.

## The three classes of hook dependency

1. **Injected context** (#1, #2, #7) — degrades to *manual*. The agent must call
   the tool. Safe, because a missed call loses convenience, not data.
2. **Observed actions** (#4, #5, #6) — degrades to *dead*, because a metric or a
   loop reads the table and gets nothing. This is the dangerous class.
3. **In-tool guardrails** (#3) — degrades to *absent*. No equivalent exists on a
   host without a pre-tool hook; the lesson simply cannot fire at tool-call time.

## Guard against recurrence

- `tools/pmb_e2e_check.py` asserts `agent_actions` is populated and has
  `surface_ids`, and that `lesson_impact` has a non-zero outcome signal.
- `tests/test_pmb_loop_liveness.py` asserts the wiring itself (observer present,
  conftest hook, pre-commit hook, status mapping the classifier counts), so
  deleting any of them fails a test rather than going quiet.
- `codebuff` is now registered in `pmb.cli.hooks._AGENT_CAP` as `mcp-only`, so the
  next agent gets `install_hook("codebuff")` guidance instead of re-deriving this.

## Residual gaps (accepted)

- **#3 PreToolUse** — no host hook, so no just-in-time rule firing. The mitigation
  is class 1: call `prepare()`/`find_lessons()` before acting.
- **#6 autowrite** — `ambient-watch` observes **git file changes only**, so it
  cannot produce a test/build *outcome*. That is precisely why the outcome
  observer (#4) is not redundant with it.
- **#7 capture-exploration** — `pmb_observe_transcript.py` extracts command
  outcomes, not exploration conclusions; those still need `record_exploration()`.
