## LANE QUEUE — claim, work, retire (batch loop protocol)

**Standing order, 2026-10-31.** The board is a durable queue, and it is now the
only supported way to pick up work. Measured before this rule existed: 743 open
rows on the three lane topics, oldest nine days old, `mcp_config_fix` posted 75
times — historical figures, do not re-quote them; run `stats` for the current
ones — and nothing recording that any row had ever been picked up — `status`
lived inside each row's JSON, so a poller re-read its whole backlog every pass.
A "batch loop" built on that board gets **slower** each iteration. Use these
verbs and it gets faster, because retired rows leave the query.

**Read work only by claiming it:**

```bash
python C:/Users/clint/_board.py claim <lane> [limit] [agent]   # default limit 10
python C:/Users/clint/_board.py stats [lane]
```

`claim` is compare-and-set inside `BEGIN IMMEDIATE`, oldest first: two lanes
polling at once cannot receive the same row. A claim expires after 30 minutes
(`CLAIM_LEASE_SECONDS`), so a lane that dies mid-batch cannot strand work — the
row is handed out again with `attempts` incremented. A row whose `task_id` is
already retired is retired as `duplicate of Board-<n>` instead of being worked
twice.

**Retire inside the same turn you finish, or you have not finished:**

```bash
python C:/Users/clint/_board.py done <board_id> "<evidence: command + result>"
python C:/Users/clint/_board.py block <board_id> "<the exact blocker>"
```

`done`/`block` exit non-zero when the row was never claimed — that is a real
signal, not noise: it means the work was claimed elsewhere or the id is wrong.
Never report a task complete because you remember doing it; report it complete
when `done` printed `retired`.

**Loop shape.** `claim` → do the batch → `done`/`block` each row → `claim` again.
Stop when `claim` prints `NO OPEN TASKS`. Never write a loop that does not
retire.

**What `tasks` returns now, and why it changed (2026-10-31, commit 69a48d7f).**
`_board.py tasks` used to return every row ever posted, so a reader could not
tell live work from a backlog nobody had retired. It now returns
**claimable-only** rows: retired rows and rows under a live lease are filtered
in SQL. Two flags cover the exceptions — `--all` (full history) and `--claimed`
(rows another lane holds right now). Read `tasks` to see what is available; it
still marks nothing, so never build a drain loop on it, and never rely on a
`since_id` cursor alone — that is history, not a work queue.

**Trust `stats`, not a number someone wrote down.**
`python C:/Users/clint/_board.py stats <lane>` returns `available` (what `claim`
can hand out right now), `claimed` (under a live lease), `retired`
(done + blocked + archived) and `open`. `available` is computed from the same
state table `claim` reads, so the count and the claimable list cannot disagree.
Counts move while you work, and two of the reasons are by design: a lease
expiring returns a row to `available`, and `release` **deletes** the claim row,
so a released task is available again. Measured on 2026-10-31: kilo `available`
read 5, then 27 within the hour. Cause found the same day — roughly twenty rows
were claimed in a batch and released as surplus, `release` deleted their
`lane_task_state` rows, and each one returned to `available`; two rows posted in
the same window took it to 27. Only `claimed` rows can be released, so no
retired work reappeared. The side effect worth knowing: the delete also erases
`attempts`, so a row claimed and released four times still reads `attempts=1`,
and the release itself leaves no record. Run `stats` in the turn where you quote
a figure, never from memory and never from this document.

**Check you are on the shared store before you trust an empty queue.**
`python C:/Users/clint/_board.py store` prints the resolved path, whether it is a
symlink, its size and its row count. On 2026-10-31 the Kali lane's
`/root/.azazael/telemetry_store.db` was a real 32 KB file with **0 rows** instead
of the symlink the canon described, so that lane's posts went into a void and
`stats` printed `{'open': 0}` — which reads as "no work", not as "wrong file".
Repair: `ln -sf /mnt/c/Users/clint/.azazael/telemetry_store.db ~/.azazael/telemetry_store.db`.
Verified after repair: Kali saw the same 14 open rows and a Kali post (row 46828)
was read back from Windows. Two lanes on two stores is the one failure mode that
makes every other part of this protocol silently useless.

**One status row per work unit**, to `lane.<lane>.status`, then **read it back**
(a post you cannot read back did not land).

**opencode is the push hook / dispatcher.** It owns
`LaneMessageBoard.push_hook(dst_lane, action, detail="", task_id=None)`, which
writes the delivery row to `lane.<dst>.tasks` plus a `lane.push.<src>-><dst>`
audit row naming `delivery_row`. Dispatch rule: if a task is not max-reasoning
work (mechanical edits, re-renders, re-indexing, bulk verification), **push it to
the lane that owns that kind of work instead of doing it locally**, then retire
the original with the push's `delivery_row` as evidence. A dispatch that cannot
name its delivery row did not land.

**What makes this fast, and what does not.** The speed comes from three measured
properties, not from parallelism in the abstract: retired rows stop being
returned (queue shrinks instead of re-scanned), duplicate `task_id`s collapse
before they reach the batch, and each claim is a bounded slice (`limit`) so a
lane cannot be handed 300 rows it will never retire. Pushing work to another
lane only helps when that lane's tools are the ones the task needs — a push to a
lane without the tool just adds a row and a hop.
