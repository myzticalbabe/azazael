<!-- AO:start-here source: docs/agent_orders/01_start_here.md -->

## 0. START HERE — read this before the canon, act before the ceremony

**Every number in these instruction files is a cached reading with a date. If it
disagrees with the tree, the tree wins, and the difference is a defect to record.**
The only numbers you may quote without measuring are in `state/head.json`; if that
file is absent or older than `HEAD`, measure before you speak.

This block is the operating contract. The generated canon below it explains *why*
each rule exists; none of it outranks this block, and none of it needs reading
end-to-end before the first command.

### 0.1 The first four commands, in order, with what "pass" looks like

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix   # PASS: exit 0, every line [PASS]
python C:/Azazael/azazael/tools/session_start.py "<task>"   # PASS: prints PMB + Engram context
#   then the MCP tool supervisor__verdict                     # PASS: GO
python C:/Users/clint/_board.py claim freebuff 10            # PASS: rows, or "NO OPEN TASKS"
```

- `[FAIL]` — repair it before trusting any recall answer.
- `[BLOCKED]` — only a client restart clears it. **Say so in your first sentence**;
  do not spend the session working around a stdio child that is serving old code.
- **If `supervisor__verdict` cannot be called** (tool absent, transport dead): do
  memory work only, print `VERDICT UNAVAILABLE: <error>` as your first line, and
  stop. Do not proceed silently on the assumption that it would have said GO.
- `NO-GO` from the supervisor is not advice. It blocks non-memory work.

### 0.2 The turn contract — a turn is not finished until all seven are done

1. **Claim** the work by id (`_board.py claim <lane>`), never by memory of what
   was pending.
2. **Do** the smallest version that answers the request.
3. **Verify by running.** One command, its exit status, and the line it printed.
   An import is not a test; a green gate is not a filtered recall answer.
4. **Commit** by path (`git add <paths>`), message saying *why*, and read
   `git show --stat HEAD` back — an empty commit is a silent failure.
5. **Retire** the row: `done <id> "<command + result>"` or `block <id> "<blocker>"`.
   A claim you cannot retire did not happen.
6. **Status row**: `_board.py report <lane> <status> <detail>` then read it back.
   The detail MUST include the command, exit code, and output line.
7. **Record** — `pmb_record_batch(items=[...])` with all turn outcomes (activity/decision/lesson/fact/goal).
   One atomic batch per turn; use absolute dates. Encounter-time errors written immediately; outcomes batched at turn end.

Prose is not a deliverable. `done`, `fixed`, `passes`, `verified`, `landed` are
claims; each one carries the command behind it.

### 0.3 Refusals — each of these cost a cycle in a real session

- **Never `git add -A`.** This worktree carries hundreds of pre-existing edits from
  other lanes. A blocked commit can also leave unrelated files staged; `git reset`
  first, then stage by path, and check `git diff --cached --name-only | wc -l`.
- **Never kill a `pams` or `supervisor` process** to "refresh" it. They are your
  client's stdio children; killing one breaks the live session.
- **Never trust a commit that reported success without a stat.** If the intended
  `git add` did not land, `git commit` succeeds empty.
- **Never re-run a gate without staging the fix.** The staged scanner reads the
  **index**: fix → `git add` → re-run, or it re-reports a finding you already fixed.
- **Never rebaseline a scanner finding to get a commit through.** Fix it, or
  declare `ALLOW_BULK_COMMIT=1` in the message for a bulk *operation*.
- **Never hand-edit a generated file** (a lane prompt's `AO:` block, a shard stub,
  `eliza/`, `SHARD_INDEX.json`). Edit the source and regenerate; `--check` is the
  gate, and `--write` may delete what it generated.
- **Never answer acceptance.** `this passes`, `this is done`, `good enough` are the
  user's words, not yours. Describe what you observed.
- **Never write a cause into evidence.** Record what died, where, with what last
  words (`requiem.py`); cause is a judgement made at the worst moment.

### 0.4 Canon is a routing table, not a reading list

`RULE 0K` orders these *when you read them*, never "before everything else".
Read by question, and `grep -n` anything over ~50 KB instead of reading it whole.

| question | document | how |
| --- | --- | --- |
| what is forbidden / mandated | `azazael/MANDATES.md` | grep the rule id |
| this error already happened | `azazael/ERROR_LOG.md` (507 KB) | `grep -n` the symptom, read the window |
| how do I record an error | `azazael/SOP.md` | the ERROR CAPTURE section |
| do not repeat a past mistake | `azazael/MEMORIES.md` | grep the anti-pattern |
| what is true right now | `state/head.json` + `SESSION_STARTUP.md` | read whole (small) |
| why the defaults are like this | `docs/agent_orders/05_hyper_edge_defaults.md` | generated block below |
| what is portable already | `docs/KERNELS_2026-11-02.md` | kernel index |
| last session's open work | newest `docs/*HANDOFF*.md` + the board | read whole (small) |
| a task to hand a fresh model | `docs/ZERO_SHOT_PROMPTS_2026-11-02.md` | paste one brief, whole |

Reading all seven canon documents costs ~1.12 MB (≈280k tokens, measured
2026-11-02) and buys less than one `grep` against the symptom in front of you.

### 0.5 State, handoff, and what a session owes the next one

`python tools/head_state.py --write` writes `state/head.json`: HEAD sha, branch,
date, collected test count, skills count, dirty count, gate verdict. That file —
not prose — is what the next session may quote.

A handoff (`docs/HANDOFF_<date>.md`) carries, in this order and nothing else:

1. HEAD sha and the commit that wrote it (a SHA that does not resolve is a defect)
2. **trusted state**: each claim paired with the command that produced it
3. **attempted and failed** — what you tried that did not work, and why (this is the
   section everyone omits and everyone needs)
4. the queue: board ids, blocking order, one line each
5. first commands for the next session
6. an expiry: the date after which the *numbers* must be re-measured

### 0.6 Stop and ask — the three cases where more work is the wrong answer

- The request can be read two ways and the readings differ in **size or direction**.
- The next step is destructive or hard to undo (history rewrite, deploy, delete of
  untracked work, killing a process you did not start).
- A gate fails for a reason you cannot explain **after one diagnostic pass**. Report
  the failure, the exact command and its output; do not paper over it with a retry.

### 0.7 Automatic ratchet — first error tightens the session (2026-11-09)

- A falsified claim HALTS that line of work until tool-investigated. No
  continuation on the thread, no new claims off it.
- Never present a guess as a conclusion. Unverified, or tool-ran — nothing
  between.
- Never ask the principal to do the investigation. Investigate first; ask
  only when the evidence genuinely forks.
- Never enshrine what one surface showed. Absence claims name their
  surface; one negative never closes the question.
- After one falsification, every further claim that session carries its
  command. The ratchet moves one direction only.
