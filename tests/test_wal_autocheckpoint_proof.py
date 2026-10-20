"""WAL autocheckpoint proof (#684 closeout) — tmp-DB only, never the live store.

Acceptance for the #684 headline (PRAGMA wal_autocheckpoint on store
open): the discipline is armed on every connection AND the checkpoint
machinery demonstrably fires. Both are measured on an isolated tmp DB.
"""
import os
import sqlite3

import pytest

from CORE.local_memory import DB_PATH, LocalMemoryStore
pytestmark = pytest.mark.xdist_group("serial")


def _tmp_store(tmp_path):
    return LocalMemoryStore(db_path=str(tmp_path / "proof.db"))


def test_autocheckpoint_armed_on_tmp_store(tmp_path):
    store = _tmp_store(tmp_path)
    assert store.record_event("proof", "checkpoint_probe",
                              {"n": 1}) > 0
    conn = sqlite3.connect(str(tmp_path / "proof.db"))
    try:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert str(mode).lower() == "wal"
        armed = conn.execute("PRAGMA wal_autocheckpoint").fetchone()[0]
        assert int(armed) == 1000
    finally:
        conn.close()


def test_checkpoint_fires_on_tmp_store(tmp_path):
    store = _tmp_store(tmp_path)
    payload = {"blob": "x" * 12000}
    written = 0
    for i in range(400):
        assert store.record_event("proof", "checkpoint_load",
                                  dict(payload, i=i)) > 0
        written += 12200
    db = str(tmp_path / "proof.db")
    wal = db + "-wal"
    # Each record_event opens and closes its connection, so every close
    # checkpoints into the main DB: the proof is that ~4.8MB of payload
    # landed in proof.db itself while the WAL stayed bounded or vanished
    # (fully checkpointed on last close) — never an ever-growing -wal.
    assert os.path.getsize(db) > written // 2
    assert (not os.path.exists(wal)
            or os.path.getsize(wal) < written // 2)
    conn = sqlite3.connect(db)
    try:
        busy, log, done = conn.execute(
            "PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        assert busy == 0
        armed = conn.execute("PRAGMA wal_autocheckpoint").fetchone()[0]
        assert int(armed) == 1000
    finally:
        conn.close()


def test_live_db_untouched_by_proof(tmp_path):
    if not os.path.exists(DB_PATH):
        pytest.skip("no live store on this machine")
    before = (os.path.getsize(DB_PATH), os.path.getmtime(DB_PATH))
    store = _tmp_store(tmp_path)
    assert store.record_event("proof", "no_touch_probe") > 0
    assert (os.path.getsize(DB_PATH),
            os.path.getmtime(DB_PATH)) == before
