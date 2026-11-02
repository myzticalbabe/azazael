# Dispatch — DeepSeek lane, freebuff, after restart (2026-11-02)

Standing orders for the session that picks this up. DeepSeek arrives **in the freebuff lane**; the
work already exists as board rows, so nothing here has to be re-invented, only claimed and retired.

## 0. Start of session, before anything else

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix
python C:/Azazael/azazael/tools/session_start.py "<the task>"
# supervisor__verdict via MCP — NO-GO blocks non-memory work
python C:/Users/clint/_board.py claim freebuff 10
```

`claim` is compare-and-set and hands out oldest-first. **Retire every row in the same turn you finish
it**: `python C:/Users/clint/_board.py done <id> "<command + result>"`. A row that is not retired is
not finished, whatever the transcript says.

## 1. The queue (22 rows, ids are the contract)

Everything is already posted; do not re-post. `claim` returns them in this order.

| batch | board | task_id | why it is in this batch |
| --- | --- | --- | --- |
| 1 | 47192 | `jaeger-000` | the decision that gates jaeger-001..003; nothing else in that family may start first |
| 1 | 47198 | `g2-receipt` | gates the quality of every other receipt you will write |
| 1 | 47208 | `board-lease-report` | measures the queue you are using; do it while you are looking at it |
| 1 | 47210 | `gate-disk-floor` | 5.0 GB free is an active hazard for every later step |
| 1 | 47211 | `docs-index-mockup` | doc-only, touches nothing executable |
| 2 | 47196 | `imp2-verify-inputs` | `meshscene.py` — **serialise with 47206**, same file |
| 2 | 47206 | `verify-replay` | replay is the stronger form of the same fix |
| 3 | 47202 | `aoa-trace-ids` | same package as 47203/47204/47205 — serialise |
| 3 | 47203 | `aoa-bus-sink` | |
| 3 | 47204 | `aoa-contract-promote` | needs 47202/47203 in place to measure anything |
| 3 | 47205 | `aoa-delegation-outcome` | |
| 4 | 47193 | `jaeger-001` | after 47192 |
| 4 | 47194 | `jaeger-002` | after 47193; `_ARM_MODULES` is the trap |
| 4 | 47195 | `jaeger-003` | after 47198 and 47194 |
| any time | 47197 | `g1-claim-trailer` | independent |
| any time | 47199 | `djt-iea-rederive` | evidence gathering, no code |
| any time | 47200 | `prose-splitter` | independent instrument |
| any time | 47201 | `corpus-2015-arm` | network-bound, retry-friendly |
| any time | 47207 | `board-post-verb` | `_board.py` — serialise with 47208 |
| any time | 47212 | `oss-otel-semconv` | drafting only; no PR before 47192 |
| any time | 47213 | `mcp-instructions-repro` | investigation, may conclude "upstream nothing" |
| background | 47187 | `industry_standards_analysis` | needs a post-restart baseline; every cell carries a receipt |

## 2. Using every subagent — and the one rule that outranks fan-out

Fan out **by disjoint file set**, not by task count. Two subagents editing the same file produce a
merge nobody wrote and, worse, a test run that passes against neither version. The batch column
above is the fan-out unit: everything in batch 1 may run concurrently, every row inside batch 3 is
serial because all four touch `src/AOA/`.

Each subagent's brief must contain all five of these, or its work cannot be accepted:

1. the board id and `task_id`;
2. the **exact files** it may modify (and nothing else);
3. the **acceptance command** — the one command whose exit status decides the work;
4. the **receipt** it must return: `command`, `exit_code`, `stdout_sha256` (this is the shape
   `g2-receipt` makes mandatory, so use it before the guard exists);
5. what it must **not** do: claim board rows, commit, post to the board, or touch files outside (2).

Subagents run in parallel; **you re-run the acceptance command yourself**. A subagent's "done" is a
claim; your re-run is the evidence. Where a subagent's receipt and your re-run disagree, the re-run
wins and the discrepancy is recorded — that disagreement is the most valuable thing a fan-out
produces, so never smooth it over.

## 3. Hard constraints, all measured today

- **Never `git add -A`.** The worktree carries 83 modified tracked files and 114 untracked ones from
  other lanes. Stage by path.
- **Commit in the background.** `.githooks/pre-commit` runs claim verification, the mesh wire-or-cut
  ledger, agent-orders sync and preflight: **~3 minutes**, twice today exceeding a 30-second tool
  timeout, which reads as failure while the hook is still running and invites a second commit of the
  same content. Redirect to a log, then poll `git log` for the hash.
- **Disk is at 100%, 5.0 GB free.** Do not run capture or write large artefacts before 47210 lands.
- **Never run `src/CORE/LaneMessageBoard.py` as a script** — its `main()` is a smoke test that posts
  junk rows. Import the class, or use `_board.py` (47207 adds the `post` verb).
- **Baseline to keep green:** `Project_SHARDEX/tests/test_mesh_live.py` 14 pass,
  `tests/test_prose_forensics.py` 6 pass, `meshscene.py --verify .live_pick` VERIFIED chain
  `69da083da4268ec8`. If a change moves any of those, that is the finding, not an inconvenience.
- **Do not re-capture into `.live_pick`/`.live` without `--forge` first** — those pages were
  generated before the `touch` operator existed.

## 4. What "blow through this" must not mean

It must not mean closing rows faster than they are evidenced. The reason this queue exists at all is
that a check which did not fire and an outcome which went badly are different failures, and the first
one is invisible unless someone records that they ran the command. Ten rows retired with receipts
beat twenty retired with summaries; a row retired as `blocked` with the exact blocker named is a
success, and is ranked above a row retired `done` on assertion.
