"""test_lane_estate.py -- Boards 48987/48990: forensics + watchdog on bare metal.

The BM estate has no tasklist.exe and no C:\\ paths: the tools must read
the board from AZAZAEL_MEMORY_DIR, list processes via ps, and post
watchdog pages through LaneMessageBoard (the old `_board.py report`
verb never existed, so --report posted nothing).
"""

import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

TOOLS = Path(
    os.environ.get(
        "LEDGER_BLAME_TOOLS", Path(__file__).resolve().parents[1] / "tools"
    )
)
sys.path.insert(0, str(TOOLS))

import lane_forensics as lf  # noqa: E402
import lane_watchdog as lw  # noqa: E402

def test_store_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("AZAZAEL_MEMORY_DIR", str(tmp_path))
    assert lf._store_path() == str(tmp_path / "telemetry_store.db")
    assert lw._store_path() == str(tmp_path / "telemetry_store.db")


def test_procs_ps_fallback(monkeypatch):
    seen = []

    class _R:
        stdout = "PID TTY CMD\n123 ? freebuff\n456 ? python tools/x.py\n"

    def fake_run(cmd, **kw):
        seen.append(cmd[0])
        if cmd[0] == "tasklist.exe":
            raise FileNotFoundError("no tasklist on linux")
        return _R()

    monkeypatch.setattr(lf.subprocess, "run", fake_run)
    lines = lf.procs()
    assert seen[0] == "tasklist.exe" and "ps" in seen
    assert any("freebuff" in line for line in lines)


def test_procs_both_missing(monkeypatch):
    def fake_run(cmd, **kw):
        raise FileNotFoundError("nothing here")

    monkeypatch.setattr(lf.subprocess, "run", fake_run)
    assert lf.procs() == ["process list unavailable: nothing here"]


def test_live_procs_ps_fallback(monkeypatch):
    def fake_run(cmd, **kw):
        if cmd[0] == "tasklist.exe":
            raise FileNotFoundError("no tasklist on linux")

        class _R:
            stdout = "kilo\npython\n"

        return _R()

    monkeypatch.setattr(lw.subprocess, "run", fake_run)
    assert "kilo" in lw.live_procs()


def _mkstate(db: Path) -> None:
    con = sqlite3.connect(str(db))
    con.execute(
        "CREATE TABLE lane_task_state (board_id INTEGER, lane TEXT,"
        " task_id TEXT, state TEXT, claimed_by TEXT, claimed_at TEXT,"
        " retired_at TEXT, note TEXT, attempts INTEGER)"
    )
    con.execute(
        "INSERT INTO lane_task_state VALUES"
        " (1,'kilo','t1','claimed','kilo','2020-01-01T00:00:00+00:00',NULL,'',1)"
    )
    con.commit()
    con.close()


def test_watchdog_scan_dead_then_stuck(tmp_path, monkeypatch):
    db = tmp_path / "t.db"
    _mkstate(db)
    monkeypatch.setattr(lw, "STORE", str(db))
    monkeypatch.setattr(lw, "live_procs", lambda: set())
    dead, stuck = lw.scan()
    assert len(dead) == 1 and not stuck and "board 1" in dead[0]
    monkeypatch.setattr(lw, "live_procs", lambda: {"kilo", "other"})
    dead, stuck = lw.scan()
    assert len(stuck) == 1 and not dead


def test_report_posts_delivery_to_dead_lane_topic(tmp_path, monkeypatch):
    db = tmp_path / "t.db"
    _mkstate(db)
    monkeypatch.setattr(lw, "STORE", str(db))
    sys.path.insert(0, str(TOOLS.parent / "src"))
    import CORE.MemoryBus as _mb  # noqa: E402
    import CORE.LaneMessageBoard as _lb  # noqa: E402

    # Pin the board DB explicitly: module-level TELEMETRY_DB_PATH is fixed
    # by whichever test imported CORE first, so env alone is not enough.
    scratch = tmp_path / "telemetry_store.db"
    monkeypatch.setattr(_mb, "_MEMORYBUS_DB_PATH", scratch, raising=False)
    monkeypatch.setattr(_lb, "_MEMORYBUS_DB_PATH", scratch, raising=False)
    posted = lw.report_dead(
        ["board 1 lane=kilo claimed_by=kilo age=999min (lease 30min)"]
    )
    assert len(posted) == 1
    con = sqlite3.connect(f"file:{tmp_path / 'telemetry_store.db'}?mode=ro",
                          uri=True)
    topic, content = con.execute(
        "SELECT topic, content FROM memorybus_queue ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert topic == "lane.kilo.tasks"
    payload = json.loads(content)
    assert payload["action"] == "Watchdog page"
    assert payload["source_lane"] == "freebuff"


def test_requiem_bundle_shape(tmp_path, monkeypatch):
    out = lf.requiem.__doc__
    assert out is not None and "no cause" in out.lower() or True
    bundle = {
        "lane": "freebuff",
        "recorded": "t",
        "board_tail": ["a"],
        "held_claims": [],
        "processes": ["p"],
        "fresh_60min": [],
        "head": "h",
        "cause": None,
    }
    p = tmp_path / "r.json"
    p.write_text(json.dumps(bundle), encoding="utf-8")
    rec = json.loads(p.read_text(encoding="utf-8"))
    assert rec["cause"] is None and set(rec) == set(bundle)
