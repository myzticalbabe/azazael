# Deep-dive audit — multi-lane orchestration, before any push

**Date:** 2026-11-02
**Subject:** the lane board as deployed (`src/CORE/LaneMessageBoard.py` + the operator CLI + the canon
that teaches it), and the publish state of the documents written today.
**Verdict:** the method works and the store is far healthier than its headline number suggests, but
**two defects make the queue report work that no lane is doing**, and the repository still cannot be
pushed for reasons that predate this session (no licence, two blobs over GitHub's limit, a remote
that is a local directory).

Every finding below is either read from a file (cited by line) or measured by a command run today.
Nothing is inferred from how the system usually behaves. Where a earlier document in this tree states
a figure, it is re-measured here rather than quoted.

---

## 1. Method and coverage, stated before any conclusion

Executed today:

| what | command | result |
|---|---|---|
| queue state, all lanes | `_board.py stats <lane>` for kilo/freebuff/opencode/agy/crush | table in §3 |
| raw state distribution | `SELECT state, COUNT(*) FROM lane_task_state GROUP BY state` | archived 738, done 129, blocked 18, available 10, claimed 10 |
| churn | live rows by `attempts` | 20 at ≥3, **max 12** |
| lease arithmetic | `strftime('%s', claimed_at)` on the 10 claimed rows | all `1793622823` = 12:33:43Z, lease expired at 13:03:43Z, audit clock 17:27:18Z |
| topic census | `SELECT topic, COUNT(*) FROM memorybus_queue GROUP BY topic` | 44,994 rows; 40,079 `cluster.execute.start` (89.1%); 905 lane rows |
| lane set | `LaneMessageBoard.py:125`; `_board.py claim agy` | tuple of 3; refusal exits 1 |
| gate registry | `tools/preflight_all.py --self-test` | 32 gates, 0 failures, 5 no-control |
| gate controls | `preflight_all.py --self-test --run-controls` | all declared controls executed, exit 0 |
| release semantics | `release_task` at `:1054-1082` | preserves `attempts` (already fixed) |
| second board | `state/agent_board.jsonl` | 3 rows, last 2026-10-18, 2 `claimed` |
| publish arithmetic | `git count-objects -vH`; `git cat-file --batch-all-objects` | 954.92 MiB pack; blobs of 272.3 MB and 228.8 MB |
| working tree | `git status --porcelain \| wc -l`; `git rev-parse --abbrev-ref HEAD` | 51 changed; branch `deepseek-engram-813`, 1,269 commits |

**Not executed:** any claim/retire against the live store (this audit added no rows and moved none);
the Kali lane's store (not reachable from here); the MCP cold-start path; and the five gates that
declare no control, whose behaviour is therefore *unknown* rather than good.

---

## 2. Findings, by severity

### A1 — P1 — No attempt cap: the queue offers work no lane can finish

**Measured.** 20 live rows carry `attempts >= 3`; the maximum is 12. Ten rows on `lane.kilo.tasks`
were all leased at 12:33:43Z with attempts 3–8 — the same ten rows, handed out and abandoned each
time the 30-minute lease expired.

**Why it matters.** `stats` reports these as available work, so the first claim of every hour goes to
rows that have never succeeded. The queue's headline is an upper bound, not a plan, and the retry
counter climbs without ever producing a decision.

**Remedy.** When `attempts + 1 > cap`, write `blocked` with the reason and stop offering the row:

```python
if attempts > self.MAX_ATTEMPTS:
    UPDATE lane_task_state SET state='blocked', claimed_at=NULL,
           note='attempt cap reached (N) -- needs a human decision' WHERE board_id=?
```

`docs/scripts/lane_kit.py:claim` implements exactly this and `tests/test_lane_kit.py` pins it
(`-k attempt_cap`). **Open in production.** The cap value should be per lane (a bulk re-index lane
needs a higher cap than a reasoning lane) — that argues for the lane record of A5, not for a hard
constant.

### A2 — P1 — `claimed` counts expired leases, so a dead lane reads as busy

**Measured.** At 17:27:18Z, `stats kilo` returns `claimed: 10, available: 10, open_incl_claimed: 20`.
The ten "claimed" rows were leased at 12:33:43Z — **four hours and fifty-four minutes earlier** — and
their lease expired at 13:03:43Z. All 378 kilo rows are `archived 313 / done 55 / claimed 10`: there
are **zero** rows in `state='available'`, so the `available: 10` *is* the expired set. Live claims on
the kilo lane: **0**.

**Cause, read from the code.** `task_stats` (`LaneMessageBoard.py:1181-1230`) computes `available`
with an expiry-aware query — correct — but sets `counts["claimed"]` from a raw `GROUP BY state` that
has no time predicate. `open_incl_claimed` then adds the two, so the same ten rows are counted twice.

**Why it matters.** This is the failure mode the whole method exists to prevent, in the reporting
layer: a lane that has been dead for five hours is described as holding ten pieces of work. A
supervisor reading `claimed: 10` concludes the lane is saturated, when in fact the lane has no live
claim at all.

**Remedy.** Split the number, do not smooth it: `claimed_live` (lease unexpired) and
`claimed_expired`, and define `open_incl_claimed = available + claimed_live` where `available` already
includes the expired rows. Board row **47208** asks for exactly these two fields and is still open;
its own quoted figure ("24 rows at claimed") is stale and must be re-measured, not carried forward.
**Open.**

### A3 — P2 — A second board that nothing drains

**Measured.** `state/agent_board.jsonl`: 3 rows, last written 2026-10-18, two of them `claimed`. The
live queue is `lane_task_state` + `memorybus_queue` in SQLite. Nothing reads the file.

**Why it matters.** Split brain is silent: work posted to the dead board is invisible to every lane,
and a reader that finds the file concludes the project has three tasks and two agents working. The
file also contradicts the canon's "the board is the delivery plane" in a way only a dated mtime
reveals.

**Remedy.** Delete it, or move it under `archive/` with a one-line `SUPERSEDED-BY` header naming the
table. Do not leave a file called `agent_board` in a tree where "the board" means something else.
**Open** (deliberately not deleted by this audit: deleting another lane's artefact is their change to
make, and the file is evidence for this finding).

### A4 — P1 — The canon teaches a CLI that has three more verbs than it documents, and one fixed bug it still warns about

**Measured.** `docs/agent_orders/03_lane_queue.md` documents `claim`, `stats`, `done`, `block`,
`store`. The CLI implements thirteen verbs including **`post`**, **`report`** and **`release`**.
Separately, the canon states that `release` "**deletes** the claim row … the delete also erases
`attempts`, so a row claimed and released four times still reads `attempts=1`" — but `release_task`
(`:1076-1082`) now preserves `attempts` and appends a note. The canon describes a defect that no
longer exists.

**Why it matters, twice over.** `report` is the **only correct way** to satisfy the canon's own rule
that every work unit ends with a `lane.<lane>.status` row; a lane following the documented verbs
cannot execute the documented protocol. And a warning about a fixed bug teaches a reader to code
around a hazard that is gone — the inverse of a stale claim, and just as misleading.

**Remedy.** Add the three verbs to the canon with one line each (the CLI's own comments are already
the text), and replace the release paragraph with the current behaviour and its date. Because the
canon is generated into **nine** instruction files by `tools/agent_orders_sync.py`, the change is one
edit plus `--fix`, and the hook blocks on drift (`[AgentOrders] BLOCKED`). **Open** — not done here,
because it changes what every lane is told, which is a decision rather than a correction.

### A5 — P2 — A lane is a value in the source

**Measured.** `VALID_LANES = ("opencode", "kilo", "freebuff")` at `LaneMessageBoard.py:125`. `claim
agy` refuses with exit 1. `stats agy` prints zeros rather than refusing, so a mistyped lane reads as
an empty queue.

**Why it matters.** This is the one architectural promise the whitepaper does not keep: the fourth
lane costs a code change and a redeploy of every importer. It also makes A1's per-lane cap awkward,
since there is nowhere to put it.

**Remedy.** A `lanes` table (name, topic, lease, max_attempts) and a check that a lane exists. The
write is a migration plus the tuple's three uses; the test is the one the whitepaper names — **add a
fourth lane without editing the other three**. **Open.** Also fix the `stats` asymmetry so an unknown
lane refuses as loudly as `claim` does.

### A6 — P2 — The protocol's CLI lives outside the tree

**Measured.** The canon's commands name an absolute path beside the home directory; the file is not
in the repository, so a clone cannot reproduce the protocol, and the path carries a username into
every lane's instruction file (publish blocker B8 in `docs/PUBLISH_READINESS_2026-11-02.md`).

**Remedy.** Move the CLI into `tools/` and keep a thin shim at the old path for one session. The
tutorial added today deliberately uses **only repo-relative commands** so it is reproducible from a
clone; that is the pattern the canon should follow.

### A7 — P3 — The queue shares a table with a telemetry firehose

**Measured.** `memorybus_queue`: 44,994 rows. Lane work: 905 (398 + 378 + 129). The largest topics are
`cluster.execute.start` (40,079, **89.1%**), `monitor.berks` (363), `cluster.nature.built` (344),
`monitor.threat` (268), `t.limit` (200). The claim query filters by topic and is correct; the *table*
is not a queue.

**Remedy.** Either a separate `lane_queue` table, or treat every question as topic-scoped (the SQL
already is) and stop quoting table-level counts. A `COUNT(*)` on this table answers "how busy is the
system", never "how much work is queued".

### A8 — P3 — Blocked rows are only visible in the audit view

**Measured.** 18 blocked rows, **17 of them on freebuff**; the CLI has no verb that lists them, so
they appear only under `tasks --all` among 738 archived rows. `stats` counts them and nothing surfaces
their notes.

**Why it matters.** Blocked is where decisions queue. A decision that is counted but never listed is
a decision nobody makes, and the concentration in one lane means one lane is absorbing the ambiguity
of the whole board.

**Remedy.** A `blocked [lane]` verb printing id, lane, note and age — three lines of CLI, and it makes
the queue's most important state readable.

### A9 — Closed since the last audit, with receipts

Worth recording so the fixes are not re-litigated:

- `release` no longer deletes state; attempts survive (`:1076`).
- `post` exists, and routes through `push_hook` so the `lane.push.<src>-><dst>` audit row carries
  `delivery_row` (`_board.py`, verb `post`).
- `report <lane> <status>` posts a status for the named lane and **reads the row back**, exiting 1 on
  `NOT READ BACK` — the 47382/47383 wrong-lane defect.
- `store` detects a split-brain file (the Kali 32 KB / 0-row failure).
- `tasks` is claimable-only by default, with `--all`/`--claimed` as explicit audit views.
- The gate registry's declared controls were **executed**, not merely listed:
  `preflight_all.py --self-test --run-controls` exits 0 with every declared control demonstrated.

### A10 — P1 — One lane's dirty file blocks every lane's commit, with no scoped override

**Measured while landing this session's work.** `git commit` failed at the Bible gate:

```
harvest: Project_ELIZA/README.md moved since the harvest
FAILED
[Bible] BLOCKED: the corpus contradicts itself (see above).
```

`git status --porcelain Project_ELIZA/README.md` → ` M` — an **uncommitted** 84-line edit by another
lane. The stanza (`.githooks/pre-commit:205-218`) exits 1 with no environment override, so **no lane
can commit anything** until `docs/bible/harvest.json` is refreshed.

**Why the obvious repair is wrong.** `python tools/bible_harvest.py --write` records the hash of the
file **as it sits in the working tree**. Committing that ledger alongside documents that do not
include the README produces a commit whose ledger describes content that is not in the commit — a
clean checkout then fails its own gate. The correct sequence is: the owning lane commits the README
and re-runs `--write` in the same commit.

**Remedy (two, either is enough).** (a) Compare the harvest against the committed blob —
`git show HEAD:<path>` — so a dirty working tree cannot block an unrelated commit; or (b) a declared,
scoped override `BIBLE_HARVEST_ALLOW=<path>` that prints the bypassed surface, in the style of
`ALLOW_PREFLIGHT`. Either keeps the gate's meaning ("the ledger describes what is committed") while
stopping one lane's in-flight edit from being a repo-wide stop.

**Cost today:** this session's three documents are written, tested and staged, and **cannot be
committed** until that README lands or the gate is scoped. It is recorded here rather than worked
around, because the workaround is the defect.

### A11 — P3 — Five gates have no declared control, and the hook runs on two interpreters

**Measured.** `preflight_all --self-test`: 32 gates, 0 failures, **5 with no declared control**
(`testing-paradigm-advisory`, `supervisor-verdict`, `pmb-outcome-observer`, `anchor-runtime`,
`type-check`), each with a stated reason. The tool also warns that gates run on two interpreters
resolved **by name** (3.15t free-threaded and the pmb venv), so a gate can behave differently
depending on which one it lands on.

**Assessment.** Labelling an uncontrolled gate is the correct behaviour and is better than a green
row; `anchor-runtime` demonstrates its own negative controls on every run. The two-interpreter note
is a real risk that has not produced a failure yet — it belongs in a slow CI job, not the commit hook.

---

## 3. The state as measured, and what it implies

| lane | available | claimed (raw) | live claims | done | blocked | archived | retired |
|---|---:|---:|---:|---:|---:|---:|---:|
| kilo | 10 | 10 | **0** | 55 | 0 | 313 | 368 |
| freebuff | 10 | 0 | 0 | 49 | 17 | 322 | 388 |
| opencode | 0 | 0 | 0 | 25 | 1 | 103 | 129 |
| **total** | **20** | **10** | **0** | **129** | **18** | **738** | **885** |

Three readings, each earned:

1. **There is no live work anywhere on this board.** Zero live claims at 17:27Z. The board is idle and
   healthy; `claimed: 10` is A2's artefact.
2. **885 of 905 rows are retired (97.8%).** The 20 "open" rows are 10 real (the churning kilo set) plus
   10 freebuff rows, one of which is the corpus work landed today.
3. **The blocked pile is one lane's.** 17 of 18 blocked rows are freebuff's; that lane is the board's
   decision queue, and nothing reads it (A8).

---

## 4. What today's documents claim, and whether the tree supports it

| claim in the new docs | supported by | check |
|---|---|---|
| the kit's invariants hold | `tests/test_lane_kit.py` | `pytest tests/test_lane_kit.py -q` → **14 passed** |
| the demo transcript is real | `python docs/scripts/lane_kit.py --demo` | deterministic; three runs, one digest (`464f91ec…`) |
| the kit refuses an unknown lane cleanly | `claim agy` | `REFUSED: lane must be one of (...)` , exit 1 |
| production figures (20/10/18/738/129) | §1 measurements | re-measured at 17:27Z; must not be quoted later without re-running `stats` |
| 32 gates, 0 failures, 5 uncontrolled | `preflight_all --self-test` | exit 0 |
| "the fourth lane is a code change" | `LaneMessageBoard.py:125` + `claim agy` | reproduced |
| no attempt cap in production | `claim_tasks` (`:879-1035`) | no `MAX_ATTEMPTS` symbol in the file |

**One correction made during the audit:** the first draft of the kit's `stats` subtracted a global
expiry count from a lane-scoped count, which printed `claimed: -1` for one lane. Fixed, and the fix
is pinned by `test_expiry_is_charged_to_its_own_lane`. The kit's `post` also originally ignored live
claims when deduping, so a duplicate posted while its original was in hand became new work — fixed,
pinned by `test_repost_while_claimed_is_a_duplicate`. Both are the same class as A2/A1 in the
production code, found in the small implementation because the tests were written first.

---

## 5. Publish state — re-measured, unchanged

These are not this session's regressions; they are the standing blockers, re-measured so nobody
plans a push on last week's arithmetic.

| # | state today | evidence | owner |
|---|---|---|---|
| B1 | **2 blobs over GitHub's 100 MB hard limit** — 272.3 MB and 228.8 MB; pack 954.92 MiB | `git cat-file --batch-all-objects --batch-check`; `git count-objects -vH` | decision: rewrite history or publish a snapshot |
| B2 | `origin` is `C:\Users\clint\azazael` — a **local directory**, not a host | `git remote -v` | decision |
| B4 | **no `LICENSE`** — default is all rights reserved | `ls LICENSE*` → none | owner decision; without it "for the public" is not a legal statement |
| B6 | 51 changed files; branch `deepseek-engram-813`; 1,269 commits | `git status --porcelain`, `git rev-parse` | hygiene before push |
| B8 | the username is embedded in canon and tool names | `docs/agent_orders/03_lane_queue.md:15` | sanitise, or accept knowingly |

**What is safe to publish *from today's work*, as individual documents rather than a `docs/` copy**
(the standing rule from `docs/AUDIT_DOCS_2026-11-02.md` is that `docs/` must never ship as a directory):

**A contamination warning found while measuring A10.** The pending (uncommitted) edit to
`Project_ELIZA/README.md` adds a section titled *"BCC RE-INVESTIGATION MACHINERY — PUBLIC, FULLY
EXECUTABLE"* to a project README that `docs/AUDIT_ELIZA_2026-11-02.md` treats as a standalone publish
candidate. Whether or not that content is appropriate, a publishable project README is the wrong
place to announce an investigation's machinery, and it must be decided **before** that file is
committed or anything is pushed. Not reverted here: it is another lane's in-flight work.

| artefact | ships? | why |
|---|---|---|
| `docs/WHITEPAPER_MULTI_LANE_ORCHESTRATION_2026-11-02.md` | **yes** | method + measured figures; no home paths, no username (`grep -c clint` → 0), no investigation content, no live-defect secrets |
| `docs/TUTORIAL_MULTI_LANE_ORCHESTRATION_2026-11-02.md` | **yes** | repo-relative commands only; runs with stdlib Python; `grep -c clint` → 0 |
| `docs/scripts/lane_kit.py` | **yes** | stdlib only, one file, no imports from this tree; path reference made neutral during the audit |
| `tests/test_lane_kit.py` | **yes** | imports only the kit |
| this audit | **no** | names live defects and unpatched weaknesses, the same class `AUDIT_DOCS` excludes |

---

## 6. Ordered plan before a push

0. **Unblock committing** (A10): land the ELIZA README and refresh the harvest in one commit, or scope
   the harvest check to the committed blob. Nothing downstream can land until this is done.
1. **Fix A2** (split `claimed_live`/`claimed_expired`) — it is the number every reader trusts, and it
   is currently wrong in the direction that hides a dead lane. One function, one test.
2. **Fix A1** (attempt cap, per lane) — needs A5's lane record to be done well, so do A5 first or
   accept a constant for one session.
3. **Update the canon** (A4) with the three verbs and the corrected release paragraph, then
   `agent_orders_sync --fix`; the hook proves the drift is gone.
4. **Retire the second board** (A3) with a `SUPERSEDED-BY` header or a move to `archive/`.
5. **Owner decisions** — licence (B4) and the B1 route (rewrite vs snapshot). Nothing public happens
   before these two, and neither is an engineering task.
6. **Push by absolute path**, `git -C C:/Azazael/azazael push`, with `remote -v` printed before and
   after; never from a shell whose cwd is a different repository.

---

## 7. What this audit does not establish

- It did not run the Kali lane, the MCP cold-start path, or the five uncontrolled gates. Their state
  is **unknown**, not green.
- It did not claim or retire live rows, so it has not exercised the queue's write path under
  contention; the concurrency argument rests on reading `BEGIN IMMEDIATE` and on the kit's tests, not
  on two real lanes racing here.
- It did not sweep `docs/` again for publish suitability; it relied on
  `docs/AUDIT_DOCS_2026-11-02.md` and checked only the artefacts added today.
- Figures in §3 are a snapshot at 17:27Z. Two lanes polling, a lease expiring or a release changes
  them within the hour; re-run `stats` before quoting any of them.
- It proposes remedies for A1–A8 and implements none of them in the production board. The only code
  changed today is the runnable minimum (`docs/scripts/lane_kit.py`) and its tests, and the defects
  fixed there were its own.
