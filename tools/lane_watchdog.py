"""lane_watchdog.py -- heartbeat for lanes: page when claims outlive their lease.

A lane agent died 2026-11-07 holding 5 claims while every instrument read
empty: tasklist flags mangled by Git-bash read as 'no processes', the board
CLI hides claim states, and the lease (30 min) expired with nobody watching.
This tool is the watcher.

    python tools/lane_watchdog.py            # scan: leases vs live processes
    python tools/lane_watchdog.py --report   # scan + post dead-lane row(s)

A lane is DEAD when it holds an unretired claim older than the lease AND no
agent process for that lane exists. A live process with old claims is STUCK
(named, not paged). Exit 0 always on a completed scan; exit 2 when the scan
itself could not run (store missing/unreadable) -- that is not a clean bill.

--report posts one page per dead lane through LaneMessageBoard, which lands
it on `lane.<lane>.tasks` and returns the durable row id (read back, as
always). The old `_board.py report` verb never existed, so the previous
--report path printed 'reported' while writing nothing. Read-only without it.
"""
from __future__ import annotations

import argparse
import calendar
import os
import sqlite3
import subprocess
import sys
import time

def _store_path() -> str:
    """Board DB path: AZAZAEL_MEMORY_DIR first, so bare metal needs no C: path."""
    env = os.environ.get("AZAZAEL_MEMORY_DIR")
    if env:
        return os.path.join(env, "telemetry_store.db")
    return r"C:\Users\clint\.azazael\telemetry_store.db"


STORE = _store_path()
LEASE_S = 30 * 60  # CLAIM_LEASE_SECONDS, per the lane-queue canon
LANE_PROC = {"kilo": ("kilo",), "opencode": ("opencode",),
             "freebuff": ("freebuff", "codebuff")}


def _env() -> dict:
    env = dict(os.environ)
    env["MSYS_NO_PATHCONV"] = "1"
    return env


class ProcListBlind(RuntimeError):
    """The process list itself is unavailable (tasklist wedged -- measured
    2026-11-07, 60s timeout on a plain TABLE read). Raised, never returned
    as an empty set: emptiness pages every lane, blindness must shout."""


def live_procs() -> set[str]:
    """Lower-cased process image names alive right now.

    `tasklist.exe` first (Windows), `ps` second (bare metal / WSL). A host
    with no tasklist used to raise ProcListBlind on every pass; blindness is
    still raised, but only after both readers have actually failed.
    """
    errors: list[str] = []
    for cmd in (["tasklist.exe"], ["ps", "-eo", "comm="]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                 timeout=60, env=_env()).stdout.lower()
        except Exception as exc:  # noqa: BLE001 -- becomes BLIND, not empty
            errors.append(str(exc))
            continue
        if cmd[0] == "ps":
            return {line.strip() for line in out.splitlines() if line.strip()}
        return set(out.split())
    raise ProcListBlind(f"process list unavailable: {errors[-1]}")


def held_claims() -> list[tuple]:
    """Unretired claims: (board_id, lane, claimed_by, claimed_at)."""
    db = sqlite3.connect(STORE, timeout=30)
    try:
        return db.execute(
            "SELECT board_id, lane, claimed_by, claimed_at FROM lane_task_state"
            " WHERE retired_at IS NULL AND claimed_by IS NOT NULL").fetchall()
    finally:
        db.close()


def scan(now: float | None = None) -> tuple[list[str], list[str]]:
    """Returns (dead_lines, stuck_lines). Raises RuntimeError if unscannable."""
    if not os.path.exists(STORE):
        raise RuntimeError(f"store missing: {STORE}")
    now = now if now is not None else time.time()
    procs = live_procs()  # raises ProcListBlind (a RuntimeError) when blind
    dead, stuck = [], []
    for bid, lane, by, at in held_claims():
        try:
            # Board stamps are UTC (+00:00); timegm, not mktime (local).
            # mktime here mis-ages every claim by the UTC offset (~5h) and
            # pages every lane -- measured once, never again.
            age = now - calendar.timegm(
                time.strptime(at[:19], "%Y-%m-%dT%H:%M:%S"))
        except Exception:  # noqa: BLE001 -- bad timestamp reads as newborn
            age = 0
        if age < LEASE_S:
            continue
        names = LANE_PROC.get(str(lane).lower(), (str(lane).lower(),))
        alive = any(any(n in p for p in procs) for n in names)
        line = (f"board {bid} lane={lane} claimed_by={by} age={age/60:.0f}min"
                f" (lease {LEASE_S//60}min)")
        (stuck if alive else dead).append(line)
    return dead, stuck


def report_dead(dead: list[str]) -> list[int]:
    """Post one watchdog page per dead lane; return the durable row ids.

    Posts through LaneMessageBoard so the page lands on the dead lane's own
    `lane.<lane>.tasks` topic. Raises if a row cannot be read back -- a page
    that did not land is not a page.
    """
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from CORE.LaneMessageBoard import LaneMessageBoard

    board = LaneMessageBoard(lane="freebuff")
    posted: list[int] = []
    for line in dead:
        lane = line.split("lane=")[1].split()[0]
        detail = ("WATCHDOG page: agent process gone with claim past lease. "
                  + line + ". Re-claim or release, then check waiting work.")
        posted.append(board.post_task(lane=lane, action="Watchdog page",
                                      detail=detail, source_lane="freebuff"))
    return posted


def main() -> int:
    ap = argparse.ArgumentParser(description="Page dead lanes, name stuck ones.")
    ap.add_argument("--report", action="store_true",
                    help="post dead-lane row(s) to lane.<lane>.tasks")
    args = ap.parse_args()
    try:
        dead, stuck = scan()
    except Exception as exc:  # noqa: BLE001 -- exit 2, never a false clean
        print(f"watchdog BLIND: {exc}")
        return 2
    for line in stuck:
        print(f"STUCK (process alive, claim expired): {line}")
    for line in dead:
        print(f"DEAD (no process, claim expired): {line}")
    if not dead and not stuck:
        print("watchdog: all held claims within lease (or none held)")
    if args.report and dead:
        try:
            rows = report_dead(dead)
        except Exception as exc:  # noqa: BLE001 -- an unposted page is a failure
            print(f"report FAILED: {exc}")
            return 3
        print(f"reported: {len(rows)} watchdog page(s), read back as {rows}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
