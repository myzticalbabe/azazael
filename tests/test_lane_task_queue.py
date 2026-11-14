# coding: utf-8
"""Queue semantics for LaneMessageBoard.task claim/retire (2026-10-31).

Each test here pins a rule the batch-loop protocol in
`docs/agent_orders/03_lane_queue.md` depends on. The failure each one prevents
is named, because a test whose purpose is only "coverage" gets deleted the
first time it is inconvenient.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import CORE.LaneMessageBoard as lmb_mod  # noqa: E402
from CORE.LaneMessageBoard import LaneMessageBoard  # noqa: E402


@pytest.fixture()
def board(tmp_path, monkeypatch):
    """A board pointed at a throwaway store, seeded with real queue rows.

    The board's lane is `freebuff` because that is the lane these tests
    claim and retire work on. It matters: `complete_task` and
    `release_task` now require the acting lane to match the row's lane, so a
    board scoped to one lane cannot retire another lane's claimed work.
    """
    db = tmp_path / "telemetry_store.db"
    con = sqlite3.connect(str(db), timeout=5)
    con.execute(
        "CREATE TABLE memorybus_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "topic TEXT, content TEXT, metadata TEXT, source TEXT, session_id TEXT, "
        "timestamp TEXT, flushed INTEGER, event_uuid TEXT, trace_id TEXT, "
        "correlation_id TEXT, audit_hash TEXT, schema_version INTEGER)"
    )
    con.commit()
    con.close()
    monkeypatch.setattr(lmb_mod, "_MEMORYBUS_DB_PATH", db, raising=False)
    return LaneMessageBoard(lane="freebuff"), db


def _post(db, lane, task_id, action="do", detail="x", created="2026-10-31T00:00:00+00:00"):
    body = {"lane": lane, "task_id": task_id, "action": action, "detail": detail,
            "source_lane": "opencode", "created_at": created, "status": "pending"}
    con = sqlite3.connect(str(db), timeout=5)
    cur = con.execute(
        "INSERT INTO memorybus_queue (topic, content, timestamp) VALUES (?, ?, ?)",
        (f"lane.{lane}.tasks", json.dumps(body), created),
    )
    con.commit()
    rid = cur.lastrowid
    con.close()
    return rid


def test_claim_is_bounded_and_exclusive(board):
    """Two lanes polling at once must not both receive the same row."""
    b, db = board
    for i in range(5):
        _post(db, "freebuff", f"T{i}")
    first = b.claim_tasks("freebuff", limit=2, agent="laneA")
    second = b.claim_tasks("freebuff", limit=2, agent="laneB")
    assert len(first) == 2
    assert len(second) == 2
    assert {r["board_id"] for r in first}.isdisjoint({r["board_id"] for r in second})


def test_completed_rows_are_not_handed_out_again(board):
    """The whole point of the change: retired work leaves the query."""
    b, db = board
    rid = _post(db, "freebuff", "ONCE")
    [claimed] = b.claim_tasks("freebuff", limit=10, agent="laneA")
    assert claimed["board_id"] == rid
    assert b.complete_task(rid, state="done", note="evidence") is True
    assert b.claim_tasks("freebuff", limit=10, agent="laneA") == []


def test_a_reposted_task_id_is_retired_as_a_duplicate(board):
    """mcp_config_fix was posted 75 times; each copy must not become work."""
    b, db = board
    first = _post(db, "freebuff", "SAME")
    duplicate = _post(db, "freebuff", "SAME")
    [claimed] = b.claim_tasks("freebuff", limit=10, agent="laneA")
    assert claimed["board_id"] == first
    b.complete_task(first, state="done", note="done once")
    # The duplicate is retired during the next claim, not handed to the batch.
    assert b.claim_tasks("freebuff", limit=10, agent="laneA") == []
    con = sqlite3.connect(str(db), timeout=5)
    state, note = con.execute(
        "SELECT state, note FROM lane_task_state WHERE board_id=?", (duplicate,)
    ).fetchone()
    con.close()
    assert state == "done"
    assert f"duplicate of Board-{first}" == note


def test_an_abandoned_claim_is_reclaimed_after_the_lease(board):
    """A lane that dies mid-batch must not strand work forever."""
    b, db = board
    rid = _post(db, "freebuff", "ORPHAN")
    assert len(b.claim_tasks("freebuff", limit=10, agent="deadlane")) == 1
    # A live claim is not handed out again...
    assert b.claim_tasks("freebuff", limit=10, agent="other") == []
    # ...until the lease expires.
    reclaimed = b.claim_tasks("freebuff", limit=10, agent="other", lease_seconds=-1)
    assert [r["board_id"] for r in reclaimed] == [rid]


def test_release_returns_work_without_retiring_it(board):
    b, db = board
    rid = _post(db, "freebuff", "HAND-BACK")
    b.claim_tasks("freebuff", limit=10, agent="laneA")
    assert b.release_task(rid) is True
    [again] = b.claim_tasks("freebuff", limit=10, agent="laneB")
    assert again["board_id"] == rid


def test_release_refuses_a_retired_row(board):
    """Release must never resurrect completed work."""
    b, db = board
    rid = _post(db, "freebuff", "CLOSED")
    b.claim_tasks("freebuff", limit=10, agent="laneA")
    b.complete_task(rid, state="done", note="closed")
    assert b.release_task(rid) is False


def test_complete_task_reports_when_nothing_moved(board):
    """Silent success is the defect this guards: an id that was never claimed."""
    b, db = board
    rid = _post(db, "freebuff", "NEVER-CLAIMED")
    assert b.complete_task(rid, state="done", note="") is False


def test_archive_backlog_dry_run_changes_nothing_and_dumps(board, tmp_path):
    b, db = board
    old = _post(db, "freebuff", "OLD", created="2026-10-20T00:00:00+00:00")
    new = _post(db, "freebuff", "NEW", created="2026-10-31T05:00:00+00:00")
    dump = tmp_path / "dump.tsv"
    res = b.archive_backlog("2026-10-31", lane="freebuff", dry_run=True,
                            dump_path=str(dump))
    assert res["matched"] == 1 and res["retired"] == 0
    assert dump.exists() and "OLD" in dump.read_text(encoding="utf-8")
    # Both rows are still claimable: a dry run retired nothing.
    ids = {r["board_id"] for r in b.claim_tasks("freebuff", limit=10, agent="a")}
    assert ids == {old, new}


def test_archive_backlog_apply_retires_only_pre_cutover_rows(board, tmp_path):
    b, db = board
    old = _post(db, "freebuff", "OLD", created="2026-10-20T00:00:00+00:00")
    new = _post(db, "freebuff", "NEW", created="2026-10-31T05:00:00+00:00")
    res = b.archive_backlog("2026-10-31", lane="freebuff", dry_run=False,
                            dump_path=str(tmp_path / "d.tsv"))
    assert res["retired"] == 1
    ids = {r["board_id"] for r in b.claim_tasks("freebuff", limit=10, agent="a")}
    assert ids == {new}, old


def test_a_dict_detail_does_not_crash_the_claim(board):
    """Legacy rows carry detail as a dict; slicing one raised KeyError: slice."""
    b, db = board
    body = {"task_id": "DICT-DETAIL", "action": "legacy",
            "detail": {"note": "was an object"}, "created_at": "2026-10-31T01:00:00+00:00"}
    con = sqlite3.connect(str(db), timeout=5)
    con.execute("INSERT INTO memorybus_queue (topic, content) VALUES (?, ?)",
                ("lane.freebuff.tasks", json.dumps(body)))
    con.commit()
    con.close()
    [row] = b.claim_tasks("freebuff", limit=10, agent="a")
    assert "was an object" in row["detail"]


def test_stats_counts_open_claimed_and_retired(board):
    b, db = board
    a = _post(db, "freebuff", "A")
    _post(db, "freebuff", "B")
    b.claim_tasks("freebuff", limit=1, agent="laneA")
    b.complete_task(a, state="done", note="n")
    stats = b.task_stats("freebuff")
    assert stats["done"] == 1
    assert stats["open"] == 1


def _fake_bus(db_path):
    """A bus whose publish lands in THIS test's store.

    `post_task` publishes through MemoryBus and then reads the row back from
    `_MEMORYBUS_DB_PATH`. The fixture only redirects the latter, so the real
    bus wrote somewhere the readback could not see and every post_task test
    died with "published but no durable queue row could be read back". This
    stub writes into the same tmp store, which is what the real bus does when
    it is pointed at it.
    """
    def publish(topic, content, metadata=None, source=""):
        con = sqlite3.connect(str(db_path), timeout=5)
        try:
            con.execute(
                "INSERT INTO memorybus_queue (topic, content, metadata, source, "
                "timestamp, flushed) VALUES (?, ?, ?, ?, ?, 0)",
                (topic, json.dumps(content), json.dumps(metadata or {}), source,
                 "2026-10-31T00:00:00+00:00"),
            )
            con.commit()
        finally:
            con.close()
        return 1
    return publish


def test_post_task_collapses_an_identical_repost(board):
    """Prevention, where the claim path only cleans up afterwards.

    `claim_tasks` retires a duplicate when it finds one, so the board stayed
    correct -- but the ROWS stayed too: measured 2026-10-31, 764 task rows for
    370 task_ids, `1039` posted 75 times by an opencode poster firing every
    ~130 s for six days. Cleanup at claim time leaves the queue mostly copies
    and every reader pays for them. post_task now refuses to make the duplicate.
    """
    b, db = board
    b._bus.publish = _fake_bus(db)
    first = b.post_task(lane="freebuff", action="do", task_id="SAME", detail="x")
    again = b.post_task(lane="freebuff", action="do", task_id="SAME", detail="x")

    assert again == first, "an identical re-post created a second row"
    con = sqlite3.connect(str(db), timeout=5)
    n = con.execute("SELECT count(*) FROM memorybus_queue").fetchone()[0]
    con.close()
    assert n == 1, "a duplicate row reached the store anyway"


def test_post_task_still_posts_a_changed_instruction(board):
    """The guard must not swallow an update.

    Collapsing on task_id alone would drop a genuinely revised task and leave
    the lane working the old brief -- a worse failure than the duplicate.
    """
    b, db = board
    b._bus.publish = _fake_bus(db)
    first = b.post_task(lane="freebuff", action="do", task_id="SAME", detail="v1")
    changed = b.post_task(lane="freebuff", action="do", task_id="SAME", detail="v2")

    assert changed != first, "a changed detail was collapsed into the old row"


def test_post_task_posts_again_after_the_row_is_retired(board):
    """A retired row must not block the same task_id forever."""
    b, db = board
    b._bus.publish = _fake_bus(db)
    first = b.post_task(lane="freebuff", action="do", task_id="REUSE", detail="x")
    [claimed] = b.claim_tasks("freebuff", limit=10, agent="laneA")
    b.complete_task(claimed["board_id"], state="done", note="done")

    fresh = b.post_task(lane="freebuff", action="do", task_id="REUSE", detail="x")
    assert fresh != first, "a retired row blocked the legitimate re-post"


def test_a_revised_task_is_not_retired_as_a_duplicate(board):
    """A changed detail and the old one are not the same work.

    Measured 2026-10-31: post_task was taught to allow a revision (same
    task_id, new detail), and then claim_tasks retired that revision as
    "duplicate of Board-46849" -- because it keyed the duplicate check on
    task_id alone. The update was silently dropped and the lane would have
    worked the superseded brief. Both paths now key on
    (task_id, action, detail).
    """
    b, db = board
    b._bus.publish = _fake_bus(db)
    old = b.post_task(lane="freebuff", action="do", task_id="REV", detail="v1")
    new = b.post_task(lane="freebuff", action="do", task_id="REV", detail="v2")
    assert new != old

    claimed = b.claim_tasks("freebuff", limit=10, agent="laneA")
    ids = {c["board_id"] for c in claimed}
    assert new in ids, "the revised task was retired as a duplicate"
    assert old in ids, "the original was dropped from the same batch"

    con = sqlite3.connect(str(db), timeout=5)
    states = dict(con.execute("SELECT board_id, note FROM lane_task_state").fetchall())
    con.close()
    assert not any("duplicate" in (n or "") for n in states.values()), states


def test_poll_tasks_excludes_retired_rows(board):
    """The reader must ask the same question the writer does.

    Until 2026-10-31 poll_tasks did not join lane_task_state at all, so the
    command every lane instruction file names showed retired work as live:
    measured on the real board, kilo 340 rows for 25 actionable (313 of them
    'archived pre-cutover backlog'), freebuff 330 for 7, opencode 99 for 2.
    """
    b, db = board
    live = _post(db, "freebuff", "LIVE")
    done = _post(db, "freebuff", "DONE")
    gone = _post(db, "freebuff", "GONE")
    b.claim_tasks("freebuff", limit=10, agent="laneA")
    b.complete_task(done, state="done", note="finished")
    b.complete_task(gone, state="blocked", note="cannot proceed")
    # Hand the live row back: a row under a live lease is work in somebody's
    # hands, and the default poll drops those too -- so without this release the
    # test would be asserting on a lease, not on retirement.
    assert b.release_task(live) is True

    ids = {(t.metadata or {}).get("_row_id") for t in b.poll_tasks("freebuff", limit=50)}
    assert ids == {live}, "a retired row was presented as live work"

    audit = {(t.metadata or {}).get("_row_id")
             for t in b.poll_tasks("freebuff", limit=50, include_retired=True)}
    assert audit == {live, done, gone}, "the audit view lost rows"


def test_poll_tasks_excludes_live_claims_unless_asked(board):
    """A live lease is work in somebody's hands, not work on offer.

    Measured 2026-10-31 after the retirement filter landed: freebuff polled 12
    rows against 5 claimable, because a claimed row is not retired. The poll
    number has to equal what `claim` will return or the lane plans work it
    cannot get.
    """
    b, db = board
    rid = _post(db, "freebuff", "HELD")
    b.claim_tasks("freebuff", limit=10, agent="laneA")

    assert b.poll_tasks("freebuff", limit=50) == []
    held = b.poll_tasks("freebuff", limit=50, include_claimed=True)
    assert [t.metadata.get("_row_id") for t in held] == [rid]
    # The audit view must show every row, leases included. Measured 2026-10-31:
    # `--all` returned 328 of freebuff's 335 rows because the 7 live claims were
    # filtered out even with include_retired set.
    everything = b.poll_tasks("freebuff", limit=50, include_retired=True)
    assert [t.metadata.get("_row_id") for t in everything] == [rid]
    # And the number a lane reads agrees with what it would get.
    assert b.task_stats("freebuff")["available"] == 0
    assert b.task_stats("freebuff")["claimed"] == 1


def test_archived_is_its_own_state_not_blocked(board, tmp_path):
    """archive_backlog reused 'blocked', the documented cannot-proceed value.

    So stats reported kilo blocked=313 and the number could not be read without
    knowing which producer wrote it.
    """
    b, db = board
    _post(db, "freebuff", "OLD", created="2026-10-20T00:00:00+00:00")
    b.archive_backlog("2026-10-31", lane="freebuff", dry_run=False,
                      dump_path=str(tmp_path / "d.tsv"))
    stats = b.task_stats("freebuff")
    assert stats["archived"] == 1
    assert stats["blocked"] == 0, "archive wrote the cannot-proceed state"
    assert stats["available"] == 0
    # An archived row is not claimable and not 'blocked' to an auditor either.
    assert b.claim_tasks("freebuff", limit=10, agent="a") == []


def test_stats_separates_available_from_claimed(board):
    """open used to mean available+claimed, so a lane planned work it could not get.

    Measured on the real board: freebuff open=11 with claimed=7 while
    claim_tasks yielded 4.
    """
    b, db = board
    _post(db, "freebuff", "A")
    _post(db, "freebuff", "B")
    b.claim_tasks("freebuff", limit=1, agent="laneA")

    stats = b.task_stats("freebuff")
    assert stats["available"] == 1, "claimed work counted as available"
    assert stats["claimed"] == 1
    assert stats["open"] == 1, "open must mean claimable"
    assert stats["open_incl_claimed"] == 2
    assert len(b.claim_tasks("freebuff", limit=10, agent="laneB")) == 1


def test_post_status_returns_the_durable_row_id(board):
    """post_status returned the per-process bus counter (1), not the row id.

    Measured 2026-10-31: the status row landed at id 46858 while the call
    returned 1. post_task had already been fixed for this; its two sibling
    posters had not.
    """
    b, db = board
    b._bus.publish = _fake_bus(db)
    b.post_task(lane="freebuff", action="do", task_id="FIRST", detail="x")

    row = b.post_status("WORKING", "second write")
    con = sqlite3.connect(str(db), timeout=5)
    top = con.execute("SELECT MAX(id) FROM memorybus_queue "
                      "WHERE topic='lane.freebuff.status'").fetchone()[0]
    con.close()

    assert row == top, "post_status did not return its own durable row id"
    assert row != 1, "post_status still returns the per-process bus counter"


def test_post_status_raises_when_the_row_cannot_be_read_back(board, monkeypatch):
    """A post you cannot read back did not land: say so, do not return a number."""
    b, db = board
    monkeypatch.setattr(b._bus, "publish", lambda *a, **k: 1)
    with pytest.raises(RuntimeError, match="NOT delivered"):
        b.post_status("LOST", "nothing was written")


def test_a_lapsed_lease_is_not_counted_as_claimed_and_available(board):
    """A lapsed lease was in both numbers, so `open_incl_claimed` added it twice.

    `claimed` was a raw `state='claimed'` count while `available` already
    returned lapsed leases to the pool (that is why a dead lane's work comes
    back). Measured on the real board 2026-11-02: freebuff claimed=9 of which
    7 had lapsed, and available already included them.
    """
    b, db = board
    rid = _post(db, "freebuff", "STALE")
    b.claim_tasks("freebuff", limit=1, agent="deadLane")
    # Backdate the lease past CLAIM_LEASE_SECONDS without waiting 30 minutes.
    con = sqlite3.connect(str(db), timeout=5)
    con.execute(
        "UPDATE lane_task_state SET claimed_at = ? WHERE board_id = ?",
        ("2026-10-01T00:00:00+00:00", rid),
    )
    con.commit()
    con.close()

    stats = b.task_stats("freebuff")
    assert stats["claimed_live"] == 0, "a lapsed lease was reported as held"
    assert stats["claimed"] == 0, "`claimed` still means the raw state count"
    assert stats["claimed_expired"] == 1, "the lapsed lease vanished instead of being named"
    assert stats["claimed_all"] == 1
    assert stats["available"] == 1, "claim_tasks would hand this out; stats denied it"
    assert stats["open_incl_claimed"] == 1, "the lapsed lease was counted twice"
    # And the number agrees with behaviour: the row really is claimable again.
    assert [t["task_id"] for t in b.claim_tasks("freebuff", limit=5, agent="liveLane")] == ["STALE"]


def test_churned_names_rows_handed_out_three_times_and_never_retired(board):
    """`available` grows forever when the same rows keep coming back.

    A row at attempts>=3 is not waiting on a lane, it is waiting on a decision.
    Counting it inside `available` makes a stuck queue look like a full one.
    """
    b, db = board
    rid = _post(db, "freebuff", "ANCHOR")
    for _ in range(3):
        b.claim_tasks("freebuff", limit=1, agent="laneA")
        b.release_task(rid)

    stats = b.task_stats("freebuff")
    assert stats["churned"] == 1, "a thrice-released row was not named as churn"
    assert stats["available"] == 1
    # Retiring it clears the count: churn is about unretired work.
    b.claim_tasks("freebuff", limit=1, agent="laneA")
    b.complete_task(rid, "done", "retired")
    assert b.task_stats("freebuff")["churned"] == 0


def test_a_wall_of_stale_duplicates_does_not_hide_real_work(board):
    """The claim window is taken BEFORE duplicate detection.

    Measured on the real opencode board 2026-11-14: 31 stale re-posts stood
    in front of 6 real tasks. The claim walked its 10-row window, retired
    every row in it as a duplicate, returned NOTHING, and the CLI printed
    "NO OPEN TASKS" while `task_stats` counted 47 available. The lane could
    not get work it was entitled to.
    """
    b, db = board
    anchor = _post(db, "freebuff", "STALE", action="old")
    b.claim_tasks("freebuff", limit=1, agent="laneA")
    b.complete_task(anchor, state="done", note="done")
    for _ in range(30):
        _post(db, "freebuff", "STALE", action="old")
    real = _post(db, "freebuff", "REAL", action="real")

    claimed = b.claim_tasks("freebuff", limit=10, agent="laneA")
    ids = {r["board_id"] for r in claimed}
    assert real in ids, "the duplicate wall hid the real task"
    assert b.last_claim_stats["duplicates_retired"] == 30
    assert b.last_claim_stats["claimed"] == 1


def test_claim_reports_what_it_did_including_the_duplicates_it_retired(board):
    """A claim that retired 10 copies and found no work must not read as
    "NO OPEN TASKS" with no reason attached."""
    b, db = board
    anchor = _post(db, "freebuff", "SAME")
    b.claim_tasks("freebuff", limit=10, agent="laneA")
    b.complete_task(anchor, state="done", note="done")
    _post(db, "freebuff", "SAME")

    claimed = b.claim_tasks("freebuff", limit=10, agent="laneA")
    assert claimed == []
    stats = b.last_claim_stats
    assert stats["duplicates_retired"] == 1
    assert stats["claimed"] == 0
    assert stats["scanned"] >= 1


def test_stats_available_is_the_work_a_claim_would_hand_out(board):
    """`available` counted every row on offer, including stale copies.

    The canon says `available` is "what claim_tasks can hand out right now",
    and it was not: 37 rows on offer, 31 of them copies of retired work, 6
    pieces of real work. The number has to agree with the claim or a lane
    plans work it cannot get.
    """
    b, db = board
    anchor = _post(db, "freebuff", "STALE", action="old")
    b.claim_tasks("freebuff", limit=1, agent="laneA")
    b.complete_task(anchor, state="done", note="done")
    for _ in range(5):
        _post(db, "freebuff", "STALE", action="old")
    _post(db, "freebuff", "REAL", action="real")

    stats = b.task_stats("freebuff")
    assert stats["available"] == 1, "stale copies were counted as work"
    assert stats["stale_duplicates"] == 5, "the removed count was hidden"
    assert stats["open"] == 1
    # And the number agrees with behaviour.
    assert len(b.claim_tasks("freebuff", limit=10, agent="laneA")) == 1


def test_a_revised_task_is_not_counted_as_a_stale_duplicate(board):
    """Same task_id, different detail: a revision, not a copy.

    Keyed on the full signature (task_id + action + detail), never on
    task_id alone -- the 2026-10-31 bug that retired a revision as a
    duplicate of the brief it superseded.
    """
    b, db = board
    old = _post(db, "freebuff", "REV", action="do", detail="v1")
    b.claim_tasks("freebuff", limit=10, agent="laneA")
    b.complete_task(old, state="done", note="done")
    _post(db, "freebuff", "REV", action="do", detail="v2")

    stats = b.task_stats("freebuff")
    assert stats["available"] == 1, "a revision was counted as a stale copy"
    assert stats["stale_duplicates"] == 0
    assert [r["task_id"] for r in b.claim_tasks("freebuff", limit=10, agent="a")] == ["REV"]


def test_a_copy_of_work_another_lane_holds_live_is_not_offered_as_work(board):
    """The third duplicate rule: another agent holds this work right now.

    `claim_tasks` retires such a copy with the note "duplicate: same
    task_id is already claimed" and never hands it out, so `available` must
    not count it either.
    """
    b, db = board
    _post(db, "freebuff", "HELD")
    b.claim_tasks("freebuff", limit=1, agent="laneA")   # live lease
    copy = _post(db, "freebuff", "HELD")

    stats = b.task_stats("freebuff")
    assert stats["available"] == 0, "a copy of live-held work was offered"
    assert stats["stale_duplicates"] == 1
    # The claim does not hand it out either, and retires the copy.
    claimed = b.claim_tasks("freebuff", limit=10, agent="laneB")
    assert copy not in {r["board_id"] for r in claimed}
    con = sqlite3.connect(str(db), timeout=5)
    state, note = con.execute(
        "SELECT state, note FROM lane_task_state WHERE board_id=?", (copy,)
    ).fetchone()
    con.close()
    assert state == "done"
    assert "already claimed" in note


def test_a_lane_cannot_retire_another_lanes_claimed_work(board):
    """`complete_task` had no lane predicate, so any lane's `done` could
    retire another lane's claimed row.

    That work then vanished: it was never finished, only marked finished,
    and the lane that owned it would never see it again.
    """
    b, db = board
    rid = _post(db, "freebuff", "OTHER-LANE")
    b.claim_tasks("freebuff", limit=1, agent="freebuff")

    other = LaneMessageBoard(lane="opencode")   # a different lane, same store
    assert other.complete_task(rid, state="done", note="not mine") is False, \
        "one lane retired another lane's claimed work"
    # The row is still claimed, so its owner can still retire it.
    assert b.complete_task(rid, state="done", note="mine") is True
    con = sqlite3.connect(str(db), timeout=5)
    state = con.execute("SELECT state FROM lane_task_state WHERE board_id=?",
                         (rid,)).fetchone()[0]
    con.close()
    assert state == "done"


def test_a_lane_cannot_release_another_lanes_claimed_work(board):
    """The same hole in `release_task`: handing back work you do not hold
    takes it out of the queue the owning lane is relying on."""
    b, db = board
    rid = _post(db, "freebuff", "HELD-BY-THEM")
    b.claim_tasks("freebuff", limit=1, agent="freebuff")

    other = LaneMessageBoard(lane="opencode")
    assert other.release_task(rid) is False, \
        "one lane released another lane's claim"
    assert b.release_task(rid) is True


def test_a_malformed_row_does_not_abort_the_claim(board):
    """One unreadable row must not take the whole lane's batch with it.

    `claim_tasks` read `payload.get("task_id")` outside its parse guard, so a
    row whose content is a JSON list raised AttributeError and rolled the
    whole claim back.
    """
    b, db = board
    con = sqlite3.connect(str(db), timeout=5)
    con.execute("INSERT INTO memorybus_queue (topic, content) VALUES (?, ?)",
                ("lane.freebuff.tasks", json.dumps([1, 2, 3])))
    con.commit()
    con.close()
    good = _post(db, "freebuff", "GOOD")

    claimed = b.claim_tasks("freebuff", limit=10, agent="laneA")
    assert good in {r["board_id"] for r in claimed}


def test_poll_tasks_shows_the_work_a_claim_would_hand_out(board):
    """The reader and the writer must ask the same question.

    The canon at LaneMessageBoard.poll_tasks claims the poll number equals
    what `claim` hands out. Retired rows and live leases were already
    filtered; stale copies were not, so the reader showed 37 rows for 6
    pieces of work.
    """
    b, db = board
    anchor = _post(db, "freebuff", "STALE", action="old")
    b.claim_tasks("freebuff", limit=1, agent="laneA")
    b.complete_task(anchor, state="done", note="done")
    for _ in range(4):
        _post(db, "freebuff", "STALE", action="old")
    real = _post(db, "freebuff", "REAL", action="real")

    ids = {(t.metadata or {}).get("_row_id") for t in b.poll_tasks("freebuff", limit=50)}
    assert ids == {real}, "the reader showed copies as work"
    # The audit view still shows everything.
    audit = {(t.metadata or {}).get("_row_id")
             for t in b.poll_tasks("freebuff", limit=50, include_retired=True)}
    assert len(audit) == 6
