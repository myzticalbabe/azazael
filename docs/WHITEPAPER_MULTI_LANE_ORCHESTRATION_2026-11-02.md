# Multi-lane agent orchestration

**A method for running several AI agents on one body of work without them colliding, duplicating, or
quietly stopping — written from a deployment that has done all three.**

| | |
|---|---|
| **Date** | 2026-11-02 |
| **Status** | Method and measurements. Every figure below was read from a live store or a executed command on this date, and the command is named beside it. |
| **Audience** | Anyone who has more than one agent, or more than one terminal, working on one repository. No prior knowledge of this codebase is assumed. |
| **Companion** | `docs/TUTORIAL_MULTI_LANE_ORCHESTRATION_2026-11-02.md` (build it in 20 minutes), `docs/scripts/lane_kit.py` (the runnable minimum), `docs/AUDIT_ORCHESTRATION_2026-11-02.md` (what is still broken here) |
| **What this is not** | Not a product, not a framework recommendation, and not a claim that the deployment described is finished. It is not a substitute for the gate layer of the project it came from. |

---

## 1. The problem, stated without the vocabulary

You have one body of work and two agents. Immediately:

1. **They take the same task.** Both read "fix the README", both fix it, one overwrites the other.
   Nothing errors.
2. **A task is assigned to an agent that has stopped.** It never says so. The task is neither done
   nor available, and the queue looks busy.
3. **The same task is posted repeatedly.** A retry, a re-run, a second session — each copy is
   offered as fresh work, and the backlog grows faster than it drains.
4. **An agent reports "done" for work it never held**, because nothing in the interface required it
   to prove a claim.
5. **Neither agent can see the other's progress**, so both re-derive the same conclusion, and the
   cost of coordination exceeds the work.

None of these raise an exception. Each one makes an answer wrong or a day disappear. That is the
whole reason this method exists: **the failure mode of multi-agent work is not a crash, it is a
plausible wrong state.**

A file-based todo list fails at (1) and (3). A chat channel fails at (2) and (4). A single agent
loop fails at (5) by construction. What follows is the smallest set of objects that closes all five.

---

## 2. Five objects, and nothing else

```
   post ─────────────▶ ┌──────────────────────────────────────────┐
                       │  WORK ITEMS   (one row each, durable)    │
                       │  47187  README line 12                   │
                       │  47206  meshscene --verify replays       │
                       │  47249  board needs a `post` verb        │
                       └───────┬──────────────────┬───────────────┘
                     claim (CAS)                  │ claim
                               ▼                  ▼
                       ┌──────────────┐   ┌──────────────┐
                       │   freebuff   │   │   opencode   │     ← LANES
                       │  holds 1,2   │   │  holds 3     │
                       └──────┬───────┘   └──────┬───────┘
                       retire │                  │ retire
                              ▼                  ▼
                       done / blocked      done / blocked         ← terminal, never re-offered
                              │
                              ▼
                       GATE runs the named control and returns an exit code
```

### 2.1 Lane

A lane is a **role with a claim on a topic**, not a person and not a process. In this deployment
there are three (`opencode`, `kilo`, `freebuff`), and the set is a Python tuple — measured at
`src/CORE/LaneMessageBoard.py:125`, so **adding a lane is a code change**, not a config edit. A
fourth lane name is refused with `ValueError: lane must be one of ('opencode', 'kilo', 'freebuff')`
and exit 1 (measured on `claim agy`).

Lanes earn their existence by **different tools**, not different enthusiasm. A lane that can only do
what another lane can do is a second queue with the same bottleneck. The production dispatch rule is
therefore: *if the task is mechanical — a re-render, a re-index, a bulk verification — push it to the
lane that owns that kind of work; keep only the reasoning here.*

### 2.2 Work item

A row with an identity, a destination lane, an action, and a detail string. Identity is the triple
`(task_id, action, detail)` — **not the row id**, which is transport. This distinction is load
bearing: when a smoke-test entry point was run 72 times it posted 75 copies of the same task, and a
queue keyed on row id treated all 75 as work. A queue keyed on the triple treats copies 2–75 as
duplicates of copy 1 and retires them with a pointer.

### 2.3 Claim, and the lease that makes a claim safe

A claim is a **compare-and-set inside one transaction**: pick the oldest claimable rows for this
lane and flip their state to `claimed` with a timestamp and a claimant, atomically. Two lanes polling
at the same instant cannot receive the same row, because the second one's `BEGIN IMMEDIATE` waits and
then sees the state it was going to read.

A claim **expires**. Without expiry, an agent that dies mid-task strands its rows forever and the
queue reports itself as busy while making no progress — which is the most expensive failure in the
list because it looks like work. The production lease is 1800 s
(`CLAIM_LEASE_SECONDS`, `LaneMessageBoard.py:871`); an expired claim is re-offered with
`attempts + 1`.

A lease is not a lock. It is a **bet that a claim will be retired within a window**, and the bet is
checked by the attempt counter. That is why the counter is not decoration — see §4.2.

### 2.4 Retirement

`done` or `blocked`, with a note, and **only from a live claim**. Hold this rule exactly: a row
nobody holds cannot be retired, and the operation returns `False` rather than pretending. This is the
difference between "I completed it" (a memory) and "the store moved a row out of someone's hand"
(a measurement). Every claim of completion in this deployment is supposed to name the command and
its output; the store is the receipt.

`blocked` is not a failure state. It is the queue's way of saying **this row needs a decision, not
another attempt** — and it is the state the reference implementation was missing (§4.2).

### 2.5 Gate

A rule that can refuse, with a **named control** that proves it can refuse. Measured on this tree
today: 32 registered gates, 0 failures, 5 with no declared control, and every declared control
executed (`python tools/preflight_all.py --self-test --run-controls`, exit 0). The gate layer is what
turns "we agreed to check" into "the commit did not land".

The single most useful gate property is the one most often skipped: **a gate is unvalidated until a
known-bad input makes it fail.** An instrument that has only ever returned zero is indistinguishable
from one that is disconnected. Five gates in this deployment are honestly reported as having no
governed control, which is better than five that would have been reported green.

---

## 3. The loop, verb by verb

The reference CLI implements thirteen verbs. They are worth reading as a sentence:

```
max · tasks · status · announces · announce · report · post · claim · release · done · block · stats · store
 └── read ─────────────────────────────────────────┘ └──── work ────────────────────┘ └── audit ─┘
```

The loop is three verbs wide:

```bash
# 1. take work — atomically, oldest first, with a lease
python board.py claim freebuff 10
# 2. do the work, and record what settled it
python board.py done 47187 "docs/README.md:12 edited; pre-commit pass"
# 3. report the unit, then take more
python board.py report freebuff ok "3 rows retired; 2 pushed to kilo"
```

and it terminates when `claim` says `NO OPEN TASKS` — a state that is only reachable because retired
rows leave the query. **A loop that does not retire gets slower every iteration**; a loop that
retires gets faster. That is the entire performance story of this method, and it is a property of the
queue's query, not of the agents.

Three verbs carry subtleties that cost a day each when missed:

| verb | the trap | the fix |
|---|---|---|
| `tasks` | it is a **reader**. It marks nothing, so a drain loop built on it re-reads the same rows forever, and it looked like "work" until 2026-10-31 when retired rows were filtered out of it. | Read only to see what is available. Work only through `claim`. |
| `store` | prints the resolved database path, whether it is a symlink, its size and its row count. On a second machine this file was a real 32 KB file with **0 rows** where the documentation described a symlink, so every post from that lane went into a void and `stats` printed `{'open': 0}` — which reads as "no work", not as "wrong file". | Run `store` before trusting an empty queue. A lane on the wrong store makes every other part of the method silently useless. |
| `report` | status rows must go to `lane.<this-lane>.status`. Before the verb existed, the only way to post one wrote it to the constructing process's lane — a freebuff status landed on `lane.opencode.status` (row 47382), and a freebuff reader saw nothing (the correct write is row 47383). | Post the status through a board constructed for the lane. Then read the row back; a post the writer cannot see did not land. |

---

## 4. Eleven ways this goes wrong, with the evidence

Each entry is a failure this deployment actually had. "Measured" means a command was run on
2026-11-02 and the figure came out of it.

### 4.1 Two boards, one of them dead

**Measured:** `state/agent_board.jsonl` holds 3 rows, the last written 2026-10-18, two of them stuck
in `claimed`. The live queue is a SQLite table (`memorybus_queue` + `lane_task_state`).

A second board is not redundancy, it is a **split brain**: work posted to the dead one is invisible
to every lane, and work in the live one is invisible to anything still reading the file. The failure
is silent because both are "the board" in prose.

**Rule:** exactly one store. If a second one exists, retire it in the same change that names its
replacement — or delete it, and say so.

### 4.2 Retry inflation: the queue offers work that can never finish

**Measured:** 20 live rows (`claimed` or `available`) carry `attempts >= 3`; the maximum is **12**.
Ten rows on `lane.kilo.tasks` were all leased at 12:33:43 today with attempts 3–8, meaning the same
rows are handed out, abandoned, and handed out again every half hour.

Nothing in the reference implementation caps attempts. So `stats` reports them as available work
forever, and a lane that polls will spend its first claim of every hour on rows no lane can finish.
**The queue's headline number is therefore an upper bound, not a plan.**

**Remedy, and it is small:** a cap. When `attempts` would exceed the cap, move the row to `blocked`
with the reason `attempt cap reached (n) — needs a human decision`. The runnable minimum in
`docs/scripts/lane_kit.py` implements it; here is the property it buys, from its own demo:

```
   round 1 at t+30m: claimed=[5]
   round 2 at t+60m: claimed=[5]
   round 3 at t+90m: claimed=[5]
   [lane_kit] blocked 1 row(s) at the attempt cap: [5]
   round 4 at t+120m: claimed=[]
```

Three offers and a decision beats three hundred offers and no decision.

### 4.3 Duplicate posting

**Measured history:** `mcp_config_fix` was posted 75 times; a module's `__main__` smoke test posted
a kilo task, a freebuff task and an announcement on **every run**, and it was run 72 times. Every
copy was claimable.

Two fixes, both necessary: (a) identity is the `(task_id, action, detail)` triple, so copies collapse
instead of multiplying; (b) **never run a module's `__main__` as an operational tool** if that
`__main__` is a smoke test. The CLI exists so the smoke test never has to be the interface.

Note the corollary the triple creates: a *revised* task (same id, new detail) is genuinely different
work. Deduping on `task_id` alone retired a revision as a duplicate and the revision was lost.

### 4.4 Release that erases the evidence

**Measured 2026-10-31:** `release` **deleted** the state row. Consequences, both real: a row claimed
and released four times still read `attempts=1`, so inflation was invisible; and the release itself
left no record, so the queue could be filled and emptied all day with nothing to review.

**Rule:** a state change nulls the claim and keeps the history. Current code preserves `attempts` and
appends `[released <ts>]` to the note (`lane_kit.py:release`).

### 4.5 A "done" that nothing checked

Retirement returns `False` when no live claim moved. The trap is the caller that ignores it and
prints completion, which is how a batch of ten gets reported as ten when two were never claimed.
**Report the exit status, not the intention.** In this deployment that rule is enforced by a receipt
guard on subagent completions (command, `exit_code`, stdout digest), because "done" without a
receipt is indistinguishable from a hallucination.

### 4.6 Status written to the wrong place

Covered in §3: the verb existed for one lane only. The general lesson is that **a status channel
constructed at import time has an owner**, and that owner is not whoever calls it next.

### 4.7 Two stores on two machines

Covered in §3 (`store`). The Kali lane's file was real, writable, and empty. A lane cannot detect
this by posting successfully — writes succeed. It can only detect it by **reading back** and by
comparing the resolved path to the one the other machine sees.

### 4.8 A reader mistaken for a queue

`tasks` returned every row ever posted until retired rows were filtered in SQL. A reader that returns
history cannot drive a drain loop without an external cursor, and cursors drift. The fix is in the
query: claimable-only by default, `--all` and `--claimed` as explicit audit views.

### 4.9 The lease window fighting the batch

1800 s is right for a 5-minute task and wrong for a 40-minute one: the work is reclaimed **while it
is still being done**, and the second claimant redoes it. There is no universally correct value;
there is a correct *relationship*: **the lease must exceed the p95 duration of a claim in that
lane**, and the batch `limit` must be small enough that a lane retires its batch inside one lease.

### 4.10 A work queue inside a firehose table

**Measured:** `memorybus_queue` holds **44,994 rows**. Of these, **40,079 (89.1%) are
`cluster.execute.start` telemetry**; the three lane topics are 398 + 378 + 129 = **905 rows**. The
claim query filters by topic, so it is correct — but the table it reads is 98% not-work, and every
`COUNT(*)` on it is a census of a different thing than the one being asked about.

**Rule:** a queue and a telemetry stream are different tables, or the queue must be indexed on
`(topic, id)` and every question must name its topic. "How many rows are open" is a question about a
topic, never about a table.

### 4.11 The lane that cannot be woken

Nothing outside a chat session can *wake* a chat session. A push lands as a row; a row is not an
interrupt. The deployment's answer is a **spool plus a drain at the first turn**: work is appended to
a durable file, and `board_watch --drain` prints and acknowledges it when the session next runs.
Spooled work is *queued, not received* — and a claim held by a session that has gone quiet is what
the lease is for.

---

## 5. What this deployment actually looks like today

Measured with the board CLI's `stats` per lane and a direct read of `lane_task_state`.

| lane | available | claimed (raw) | live claims | done | blocked | archived | retired |
|---|---:|---:|---:|---:|---:|---:|---:|
| kilo | 10 | 10 | **0** | 55 | 0 | 313 | 368 |
| freebuff | 10 | 0 | 0 | 49 | 17 | 322 | 388 |
| opencode | 0 | 0 | 0 | 25 | 1 | 103 | 129 |
| **total** | **20** | **10** | **0** | **129** | **18** | **738** | **885** |

Read this honestly:

- **There is no live work on this board right now.** The ten kilo rows reported as `claimed` were
  leased at 12:33Z and their lease expired at 13:03Z; at the audit clock of 17:27Z the raw `claimed`
  counter still said 10. **A stale claim counter is how a dead lane reads as busy** — the exact
  failure mode this method exists to prevent, in the reporting layer. Split the number
  (`claimed_live` / `claimed_expired`); the audit records it as A2.
- **885 of 905 rows ever tracked are retired.** The queue is not a growing backlog; the 738 archived
  rows are mostly the pre-2026-10-31 cutover backlog that was retired in bulk. Its headline
  "available 20" is 10 freebuff rows plus the 10 churning kilo rows of §4.2.
- **`freebuff` carries 17 blocked rows and `kilo` carries none.** Blocked is where decisions pile
  up. A lane with zero blocked rows is not necessarily healthy — it can also be a lane that has not
  yet been asked to decide anything.
- **The numbers move while you read them.** Two lanes polling, a lease expiring and a release
  returning a row all change `available` within the hour (measured on 2026-10-31: 5 → 27 in one
  hour, caused by ~20 rows claimed in a batch and released as surplus). Quote `stats` from the turn
  in which you quote it, never from a document.

Gate state, same date: **32 gates, 0 failures, 5 without a declared control, controls executed and
passing.** Publish state is separately bad and is not this document's claim — see
`docs/AUDIT_ORCHESTRATION_2026-11-02.md` §5.

---

## 6. Parallelism: what pays, what only looks like speed

Three lanes do not make work three times faster. Measured, the gains come from exactly three
properties:

1. **Retired rows stop being returned.** The queue shrinks instead of being re-scanned.
2. **Duplicates collapse before they reach a batch.** 75 copies of one task become one claim.
3. **Each claim is bounded.** A lane cannot be handed 300 rows it will never retire.

The gains do **not** come from concurrency in the abstract. Two lanes editing the same file collide;
two lanes reasoning about the same question duplicate the reasoning. Dispatch helps when the
destination lane has **different tools** for the job, and it is a net loss otherwise — a push to a
lane that cannot do the work adds a row, a hop, and a false sense of throughput.

The rule that follows is unfashionable and correct: **serialise by file, parallelise by kind of
work.** A lane owns files and topics; when ownership is unclear, do not spawn a lane, write the
boundary down.

---

## 7. From one machine to "the public": the three doors

The question this document was written to answer is how a stranger — of any age, with no context —
gets from "agents seem useful" to "I architect this myself". The obstacle is not code. It is
**vocabulary and the cost of the fourth lane**.

### Door 1 — play with a queue (roughly age 10 and up)

One command, no install, no account:

```bash
python docs/scripts/lane_kit.py --demo
```

It prints a numbered transcript: two lanes, three tasks, a duplicate, a dead lane whose work comes
back, and one task that keeps failing until the queue refuses to retry it. Three questions make it a
lesson rather than a demo:

1. Row 5 was claimed four times. **Why did the queue stop offering it?** (Because a task nobody can
   finish is a decision, not a retry.)
2. Row 4 was never worked, and it is not a mistake. **What was it?** (A duplicate of row 1, recorded
   with a pointer.)
3. What does "retired" mean, and why does it help that finished things stop appearing?

No maths, no jargon: *claim, retire, duplicate, lease, block*.

### Door 2 — two lanes by hand (roughly 13 and up)

Four commands, a real database file, and the instruction to **break it on purpose**:

```bash
python docs/scripts/lane_kit.py --db k.db post freebuff fix_typo "README:12"
python docs/scripts/lane_kit.py --db k.db claim freebuff
python docs/scripts/lane_kit.py --db k.db rows
python docs/scripts/lane_kit.py --db k.db done 1 "edited line 12; test pass"
```

Then the three experiments in the tutorial's Part 3: post the same task twice and watch the second
become a duplicate; claim and never retire, then advance the clock; retire a row nobody holds and
watch it return `False`.

### Door 3 — your own work, no code (any adult)

The method works on a household, a grant application, a renovation, an email backlog. The mapping is
one sentence each:

| concept | your version |
|---|---|
| lane | a person, or a hat you wear |
| work item | a thing with a verb in it ("call the plumber", not "bathroom") |
| claim | written down, with a name and a date |
| lease | "if it is still on my list after a week, it goes back" |
| retire | the row leaves the list, with one line saying what settled it |
| block | a decision, not a delay — it needs a person, and it says who |
| gate | the one check that can say no (the deposit, the signature, the test) |

The value is the same at this scale: **nothing is in two places, and nothing disappears.**

### Door 4 — build your own (engineer)

Port the five objects to your transport — GitHub issues, a Postgres table, Discord threads — and keep
the five invariants:

1. Identity is content, not row id.
2. Claim is compare-and-set in one transaction.
3. Claims expire, and expiry increments a counter.
4. Retirement requires a live claim and returns a boolean you actually check.
5. There is exactly one store, and every reader can name it.

Then add the attempts cap (the reference build is only now getting one) and one gate with a
negative control. Do that before adding a fourth lane: **the test of the architecture is the cost of
the fourth lane**, not the elegance of the first three.

---

## 8. What "hyper-architecting" has to mean to be a promise rather than a word

It cannot mean "more agents". Anyone can start six and get less done. Operationally, it means four
things, each with a test:

| claim | test |
|---|---|
| **Composable** — a new lane is additive | add a fourth lane without editing the other three. If it needs edits in three files, the boundary is in the wrong place. |
| **Auditable** — every claim has a receipt | for any "done", name the command and its exit code. If you cannot, it is not done. |
| **Reversible** — a bad rule can be withdrawn | retired rows are retained; blocking is a state, not a deletion; a release preserves history. |
| **Legible** — a newcomer can read the state | `stats` answers "what is in flight" in one line, and the answer is a measurement, not a summary. |

This deployment meets 2–4 and **fails 1 in one specific, measured way**: the lane set is a tuple in
the source file, so the fourth lane is a code change. That is the honest state, and it is the first
thing a reader should fix in their own build.

---

## 9. What else is needed — the direct answer

Asked whether the whitepaper and tutorial are enough for "the easiest transition possible", the
answer is no, and the gaps are specific. In order of leverage:

1. **A runnable minimum.** Provided here (`docs/scripts/lane_kit.py`, 14 tests). Without it the
   tutorial is a reading exercise, and a reader who cannot run it learns a vocabulary without a
   behaviour.
2. **A licence.** This repository has no `LICENSE` file (measured: `ls LICENSE*` → 0). The default
   is "all rights reserved": nobody may legally copy, modify or redistribute the code, so "the
   public" cannot adopt anything. This is an **owner decision**, not an engineering task, and no
   amount of documentation substitutes for it.
3. **An install path that does not begin in the author's home directory.** The reference CLI and
   several documents name an absolute home path. A stranger cannot follow that, and a public tree
   should not carry it. The tutorial therefore uses only repo-relative commands, and the audit names
   the remaining instances.
4. **One vocabulary, defined once.** `claim`, `lease`, `retire`, `block`, `gate`, `receipt`, `lane`.
   The tutorial's Part 8 is the dictionary; it should be the single source, linked rather than
   restated.
5. **A fourth-lane exercise.** The one thing this architecture cannot yet demonstrate cheaply. Until
   the lane set is configuration, the exercise is "read the tuple, edit it, run the tests" — which
   teaches the right lesson (the boundary is code) but not the promised one (additivity).

What is **not** needed: more prose, a dashboard, a new framework, or another storage engine. Every
failure in §4 is a rule that was missing or a rule that was not enforced, not a missing component.

---

## 10. What this method does not solve

- **Correctness.** Two lanes can both do the wrong thing in perfect order. The board tells you who
  holds what; it does not tell you whether the work was right. That is the gate layer's job, and a
  gate is only as good as its control.
- **Truthfulness.** An agent can retire a row with a false note. The receipt guard raises the cost;
  it does not make lying impossible. Read the receipt, not the summary.
- **Design.** Lanes with no boundary drawn between them will collide no matter what queue they use.
- **Cost.** Parallelism multiplies spend as readily as throughput.
- **A bad task list.** A queue drains whatever you put in it, including work that should not exist.

---

## Appendix A — the measurements, and how to reproduce them

| figure | value | command |
|---|---|---|
| rows in the message table | 44,994 | `SELECT COUNT(*) FROM memorybus_queue` |
| of which telemetry | 40,079 `cluster.execute.start` (89.1%) | `SELECT topic, COUNT(*) ... GROUP BY topic` |
| lane work rows | 398 freebuff + 378 kilo + 129 opencode = 905 | same |
| state distribution | archived 738, done 129, blocked 18, available 10, claimed 10 | `SELECT state, COUNT(*) FROM lane_task_state GROUP BY state` |
| live rows at attempts ≥ 3 | 20 | `... WHERE state IN ('claimed','available') AND attempts>=3` |
| maximum attempts | 12 | `SELECT MAX(attempts) ...` |
| lanes | 3, a Python tuple | `LaneMessageBoard.py:125` |
| lease | 1800 s | `LaneMessageBoard.py:871` |
| registered gates | 32, 0 failures, 5 uncontrolled | `python tools/preflight_all.py --self-test` |
| gate controls executed | all declared, exit 0 | `... --self-test --run-controls` |
| pack size | 954.92 MiB | `git count-objects -vH` |
| blobs over 100 MB | 2 (272.3 MB, 228.8 MB) | `git cat-file --batch-all-objects --batch-check=...` |

The kit's own numbers are reproducible without this repository's data:
`python docs/scripts/lane_kit.py --selftest` prints `lane_kit selftest: OK`, and
`python -m pytest tests/test_lane_kit.py -q` reports **14 passed**.

## Appendix B — file map

| path | what it is |
|---|---|
| `src/CORE/LaneMessageBoard.py` | the reference board: claim, lease, retire, release, post, push |
| `docs/agent_orders/03_lane_queue.md` | the lane protocol, generated into every lane's instruction file |
| `tools/agent_orders_sync.py` | single-source → nine instruction files; the hook blocks on drift |
| `tools/preflight_all.py` | the gate registry and its self-test |
| `docs/scripts/lane_kit.py` | the runnable minimum described in §7 and the tutorial |
| `tests/test_lane_kit.py` | the invariants of §2, as executable assertions |
| `docs/AUDIT_ORCHESTRATION_2026-11-02.md` | what is still wrong, with severities and remedies |
