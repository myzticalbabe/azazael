# Tutorial: build a two-lane work board in twenty minutes

**Companion to** `docs/WHITEPAPER_MULTI_LANE_ORCHESTRATION_2026-11-02.md`. The whitepaper is *why*;
this is *do*. Every command below was run in this repository on 2026-11-02 and the output shown is
the output it printed.

---

## Part 0 — before you start

| you need | why |
|---|---|
| Python 3.8 or newer (`python --version`) | the kit is stdlib only: `sqlite3`, `json`, `hashlib`, `argparse` |
| one folder you can write to | the kit creates a single `.db` file there |
| 20 minutes, and no network | nothing here downloads or calls a model |

You do **not** need: an account, an API key, an agent, this repository's dependencies, or a database
server. The whole board is one file — `docs/scripts/lane_kit.py` — and one table pair.

All commands are run **from the repository root**, so they look like this:

```bash
python docs/scripts/lane_kit.py --demo
```

If you are reading this outside the repository, copy `lane_kit.py` anywhere and replace
`docs/scripts/lane_kit.py` with its path. Nothing else is required.

---

## Part 1 — watch the loop once, before touching it

```bash
python docs/scripts/lane_kit.py --demo
```

Output (abridged where marked `…`; the demo is deterministic, so the numbers are stable):

```
== 1. two lanes, three pieces of work ==
   posted rows [1, 2, 3]; stats freebuff={'available': 2, 'claimed': 0, 'done': 0, 'blocked': 0, 'expired_claim': 0, 'open': 2}

== 2. a lane claims what is oldest, and only its own lane ==
   claimed [(1, 'doc-fix', 'attempt 1'), (2, 'test-gap', 'attempt 1')]
   kilo still holds: {'available': 1, 'claimed': 0, 'done': 0, 'blocked': 0, 'expired_claim': 0, 'open': 1}

== 3. a second worker cannot take work already in a hand ==
   second claim returned 0 row(s) (0 expected) -- no live row is handed out twice

== 4. the lane dies mid-batch; the lease expires and the work returns ==
   stats at t+1801s: {'available': 2, 'claimed': 0, 'done': 0, 'blocked': 0, 'expired_claim': 2, 'open': 2}
   reclaimed [(1, 'attempt 2'), (2, 'attempt 2')] -- attempt counter now proves it was abandoned once

== 5. a duplicate post is not new work ==
   re-posted the same task as row 4; state=done / duplicate: task_row=1 is already claimed
   stats freebuff={'available': 0, 'claimed': 2, 'done': 1, 'blocked': 0, 'expired_claim': 0, 'open': 2}

== 6. retirement must be earned ==
   retiring a row nobody holds (row 999): False
   retiring the row in hand (1): True

== 7. the retry storm, and the cap that ends it ==
   kilo cleared: {'available': 0, 'claimed': 0, 'done': 1, 'blocked': 0, 'expired_claim': 0, 'open': 0}
   round 1 at t+30m: claimed=[5]
   round 2 at t+60m: claimed=[5]
   round 3 at t+90m: claimed=[5]
   [lane_kit] blocked 1 row(s) at the attempt cap: [5]
   round 4 at t+120m: claimed=[]
   stats kilo={'available': 0, 'claimed': 0, 'done': 1, 'blocked': 1, 'expired_claim': 0, 'open': 0}
   row 5 note: blocked / attempt cap reached (3) -- needs a human decision

== 8. totals ==
   {'available': 1, 'claimed': 0, 'done': 3, 'blocked': 1, 'expired_claim': 1, 'open': 1}
```

Read the transcript in order and you have the method:

- **§2** work is lane-scoped and oldest-first.
- **§3** a live claim is not offered again. This is the line that stops two agents overwriting
  each other.
- **§4** a dead lane does not strand work: at `t+1801s` the two claims are *expired*, so they count
  as available again, and the counter reads `attempt 2`.
- **§5** the duplicate is retired on arrival with a pointer to the row already in hand — not worked,
  not lost.
- **§6** `False` for the row nobody holds.
- **§7** three offers, then a block. Something must decide what that task is; retrying is not a
  decision.

**Now answer three questions before continuing** (they are the lesson, not a quiz):

1. Row 5 was offered three times. Why did the queue stop, and what has to happen next?
2. Row 4 was never worked. Was it lost?
3. What does `expired_claim` count, and why is it separate from `claimed`?

---

## Part 2 — do it by hand with four commands

A real board in a real file. `--db` names the file; `:memory:` (the demo's choice) disappears on exit.

```bash
python docs/scripts/lane_kit.py --db k.db post freebuff fix_typo "README:12"
```
```
1
```
The verb prints the **row id**. That id is transport — see Part 3.1 for why that distinction matters.

```bash
python docs/scripts/lane_kit.py --db k.db claim freebuff
```
```
CLAIMED row=1 attempts=1 action=fix_typo  README:12
```

```bash
python docs/scripts/lane_kit.py --db k.db rows
```
```
row=1 lane=freebuff action=fix_typo state=claimed attempts=1 note=
```

```bash
python docs/scripts/lane_kit.py --db k.db done 1 "edited line 12; test pass"
```
```
DONE 1: moved
```
Exit code `0`. **`moved` is the receipt**: the store moved a row out of your hand. If you ever see
`NOT moved`, the row was not yours to retire, and the exit code is `1` so a script can tell.

```bash
python docs/scripts/lane_kit.py --db k.db stats freebuff
```
```
{'available': 0, 'claimed': 0, 'done': 1, 'blocked': 0, 'expired_claim': 0, 'open': 0}
```

That is the entire loop: **post → claim → do → done → stats**. Everything else is a guard on one of
those five.

---

## Part 3 — break it on purpose (four experiments)

Deliberate breakage is how you learn which guard is load-bearing. Each experiment names what you
should see; if you see something else, the guard is missing in your build.

### 3.1 Post the same task twice

```bash
python docs/scripts/lane_kit.py --db k.db post freebuff fix_typo "README:12"
python docs/scripts/lane_kit.py --db k.db rows
```
```
row=1 lane=freebuff action=fix_typo state=done attempts=1 note=edited line 12; test pass
row=2 lane=freebuff action=fix_typo state=done attempts=0 note=duplicate of task_row=1
```

Row 2 exists (the post was not lost) and is **already retired** with a pointer. Identity here is
`(task_id, action, detail)`, not the row id — which is why re-posting is cheap and why changing the
detail of a task makes it genuinely new work.

### 3.2 Retire a row nobody holds

```bash
python docs/scripts/lane_kit.py --db k.db post freebuff new_thing "detail"
python docs/scripts/lane_kit.py --db k.db done 3 "I think I did this"
```
```
DONE 3: NOT moved (no live claim)
```
Exit code `1`. **This is the whole difference between a status report and a measurement.** A caller
that prints "done" without reading this exit code is reporting a memory.

### 3.3 Abandon a claim and take the work back

The lease is 30 real minutes, which is too long to sit through. Two honest ways to see it:

```bash
python -m pytest tests/test_lane_kit.py -q -k expired
```
```
1 passed
```
or run the demo's §4 again, which injects the clock:

```bash
python docs/scripts/lane_kit.py --demo
```

What the test asserts: a claim made at `t0`, then `t0 + 1801`, is claimable again **and** the attempt
counter reads 2. Change `LEASE_SECONDS` to `60` in a copy of the file and the same experiment takes
a minute by hand — that is the parameter to tune first, and the whitepaper's §4.9 says how (it must
exceed the p95 duration of one claim in that lane).

### 3.4 Watch the queue refuse to retry forever

```bash
python -m pytest tests/test_lane_kit.py -q -k attempt_cap
```
```
1 passed
```

The test sets `max_attempts=2`, abandons the same row twice, and asserts the third offer comes back
**empty** with the row in `blocked` and a note naming the cap. Without this cap the production board
measured 20 live rows at `attempts >= 3` and a maximum of **12** — a queue advertising work that no
lane could finish.

---

## Part 4 — add a lane, and learn what it costs

Open `docs/scripts/lane_kit.py` and change one line:

```python
LANES = ("opencode", "kilo", "freebuff")          # before
LANES = ("opencode", "kilo", "freebuff", "docs")  # after
```

Then:

```bash
python docs/scripts/lane_kit.py --db k.db post docs write_the_glossary "terms A-M"
python docs/scripts/lane_kit.py --db k.db claim docs
python -m pytest tests/test_lane_kit.py -q
```

It works, and **that is the finding**: in this implementation a lane is a value in the source, so the
fourth lane is a code change and a redeploy of everything that imports the tuple. Before you edit,
try claiming a lane that does not exist:

```bash
python docs/scripts/lane_kit.py --db k.db claim agy
```
```
REFUSED: lane must be one of ('opencode', 'kilo', 'freebuff'), got 'agy'
```
Exit `1`, one line, no traceback. A refusal names the acceptable set — that is what a caller needs in
order to recover.

The production system is in the same state (the tuple is at `src/CORE/LaneMessageBoard.py:125`), and
the whitepaper treats it as the one architectural promise it does not yet keep. If you are building
this for real, make lanes **data** — a row in a `lanes` table with a name, a topic, a lease and a
cap — so the fourth lane costs a `INSERT`, not a merge.

---

## Part 5 — add a gate, with a control that proves it can refuse

A rule is not a gate until it can say no. Write the check and the **negative control** in the same
change:

```python
def no_retired_work_reopened(board):
    """A row in done/blocked must never be claimable."""
    row = board.conn.execute(
        "SELECT task_row FROM state WHERE state IN ('done','blocked') LIMIT 1").fetchone()
    if row is None:
        return True                      # nothing retired yet: nothing to violate
    taken = [t["row"] for t in board.claim("freebuff", limit=50)]
    return row[0] not in taken
```

The control is a fixture where it **must** fire — a retired row that something flips back to
`available`. If you cannot construct that fixture, you have a wish, not a gate. This is the rule this
repository enforces with 32 registered gates and an executable control for each; five of them are
honestly labelled "no declared control" rather than counted as green.

For a first gate, prefer the ones whose violation is silent: **duplicate identity**, **retire
without claim**, **claim without expiry**, **a lane other than the destination posting a status**.

---

## Part 6 — four doors, so the on-ramp matches the reader

The same board, four entry points. Pick the door that matches who is reading.

| door | who | what they do | what they should be able to say afterwards |
|---|---|---|---|
| **1. Play** | age ~10–13 | run `--demo`, trace the numbered story, answer Part 1's three questions | "a task nobody can finish gets blocked instead of retried forever" |
| **2. Two lanes** | ~13–17 | Parts 2–3 by hand, then break it four ways | "two workers cannot take the same job, and a dead worker gives its job back" |
| **3. Your own work** | any adult, no code | map a real backlog (email, renovation, grant) onto the seven words in Part 8 | "nothing is in two places and nothing disappears" |
| **4. Build it** | engineer | Part 4–5, then port the five objects to your transport and keep the five invariants | "adding a lane is configuration, and I have a gate that can refuse" |

**Door 3 needs no terminal and is not a lesser door.** The mapping is the whole method:

| concept | your version |
|---|---|
| lane | a person, or a hat you wear |
| work item | a thing with a verb in it ("call the plumber", not "bathroom") |
| claim | written down, with a name and a date |
| lease | "if it is still on my list after a week, it goes back" |
| retire | the row leaves the list, with one line saying what settled it |
| block | a decision that needs a person, and says who |
| gate | the one check that can say no |

---

## Part 7 — ten checks before you trust your board

Run these against any lane board, including this one. Each is a question with an observable answer.

1. **One store.** `--db` / `store` names exactly one file or database. A second file with "board" in
   its name is a split brain. (Here: `state/agent_board.jsonl` was still present, last written
   2026-10-18, two rows stuck `claimed` — see the audit, A2.)
2. **Identity is content.** Post the same task twice; the second must be a duplicate, not work.
3. **Claims are atomic.** Two workers claim at once; the union of their claims is disjoint.
4. **Claims expire.** Set the lease to 5 s, claim, wait, claim again: you should get it back with
   `attempts=2`.
5. **Attempts are capped.** A row nobody can finish reaches `blocked` with a reason, and stops being
   offered.
6. **Retirement returns a boolean, and you check it.** `done` on an unheld row exits non-zero.
7. **Release keeps history.** Claim → release → claim: the attempt count went up, and the note says
   `[released …]`.
8. **Stats separates live from expired.** `claimed` never includes an expired lease, and never reads
   negative.
9. **`tasks` is a reader.** Nothing you can run in a loop is allowed to leave the queue unchanged —
   loops use `claim`.
10. **Every gate has a control.** For each rule, name the input that makes it fail. If you cannot,
    label it "no declared control" rather than green.

Anything you cannot check is not a guarantee, it is a convention.

---

## Part 8 — seven words, defined once

| word | means | is not |
|---|---|---|
| **lane** | a role with a claim on a topic and its own tools | a person, or a process |
| **work item** | a row with identity `(task_id, action, detail)` and a destination lane | a chat message |
| **claim** | an atomic take of the oldest available row, with a timestamp and a claimant | a lock |
| **lease** | the window after which a claim is assumed abandoned | a promise of completion |
| **retire** | `done`/`blocked` from a live claim, with a note, returning a boolean you check | a status update |
| **block** | the queue's way of asking for a decision instead of another attempt | a failure |
| **gate** | a rule that can refuse, plus a control that proves it refuses | a checklist item |

Two more, used but not central: **receipt** (the command and exit code that settle a claim) and
**spool** (a durable file holding work that could not be delivered yet — queued, not received).

---

## Part 9 — the errors you will hit, and what each one means

| symptom | cause | what to do |
|---|---|---|
| `REFUSED: lane must be one of …` | the lane name is not in the set (typo, or a lane you have not added) | use a listed lane, or add it in Part 4 |
| `NOT moved (no live claim)`, exit 1 | you are retiring a row you do not hold, or already retired | `rows` and look at the state; claim first |
| `claim` returns nothing while `rows` shows work | that work is under a **live** claim, or already retired | `rows` shows state; a live claim is somebody's, not yours |
| a row keeps coming back with a higher `attempts` | a lease expires before the work finishes | raise the lease above the p95 duration, or shrink the batch |
| `stats` shows `available` but the lane is idle | those rows are blocked-by-cap in a build without a cap | implement Part 3.4 |
| everything looks empty | you are pointing at a different database | run `store` (production board) or check `--db` |

---

## Part 10 — where this connects to the real system

| file | role |
|---|---|
| `docs/scripts/lane_kit.py` | the board you just used — one file, stdlib, 14 tests |
| `tests/test_lane_kit.py` | the invariants of the whitepaper's §2 as executable assertions |
| `src/CORE/LaneMessageBoard.py` | the production board (SQLite + message bus, no cap yet) |
| `docs/agent_orders/03_lane_queue.md` | the protocol, generated into every lane's instruction file |
| `tools/preflight_all.py` | the gate registry: 32 gates, controls executed |
| `docs/WHITEPAPER_MULTI_LANE_ORCHESTRATION_2026-11-02.md` | why each guard exists, with the measured failures |

**What to read next**, in this order: the whitepaper's §4 (eleven failure modes) → this file's Part 7
(ten checks) → `docs/AUDIT_ORCHESTRATION_2026-11-02.md` (what is still broken, including in this
kit's production ancestor).

---

### One last exercise

Take a real backlog of yours — ten items — and give each one a lane, a verb, and the sentence that
would settle it. Then pick the item you have been avoiding and **stop calling it blocked-in-progress**.
It is one of three things: available, claimed by someone, or blocked on a named decision. Every
backlog item is one of those three, and "in progress" with no claimant is the fourth thing that only
exists in prose.
