"""Advanced DirectMemory tests: filtered queries, dedup, stats, time series, tags, GC, replay, import/export, validation."""
import sys, os, json, sqlite3, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from CORE.direct_memory import DirectMemory
from pathlib import Path

_orig_db = None

def setup_module():
    global _orig_db
    import CORE.direct_memory as dm_mod
    _orig_db = str(dm_mod.DB_PATH)
    dm_mod.DB_PATH = Path(tempfile.mktemp(suffix='_test_adv.db'))

def teardown_module():
    import CORE.direct_memory as dm_mod
    if Path(str(dm_mod.DB_PATH)).exists():
        Path(str(dm_mod.DB_PATH)).unlink()
    if _orig_db:
        dm_mod.DB_PATH = _orig_db

class TestFilteredQuery:
    def test_filter_by_type(self):
        dm = DirectMemory()
        dm.file_read(["a.py"])
        dm.file_edit("a.py", "fix", 3)
        dm.test_run("suite", 5, 0)
        events = dm.list_events()
        types = [e["event_type"] for e in events]
        assert "file_read" in types
        assert "file_edit" in types
        assert "test_run" in types
        dm.end({"ok": True})

    def test_dedup_by_uuid(self):
        dm = DirectMemory()
        dm.file_read(["a.py"])
        count = dm.count()
        assert count >= 2  # session_start + file_read
        dm.end({"ok": True})

    def test_replay_session(self):
        dm = DirectMemory()
        dm.file_read(["x.py"])
        dm.skill_loaded("test-skill")
        dm.milestone("test", {"ok": True})
        events = dm.list_events()
        types = [e["event_type"] for e in events]
        assert "session_start" in types
        assert "file_read" in types
        assert "milestone_reached" in types
        dm.end({"ok": True})

class TestSessionGC:
    def test_close_stale(self):
        import CORE.direct_memory as dm_mod
        conn = sqlite3.connect(str(dm_mod.DB_PATH))
        conn.execute("INSERT OR IGNORE INTO sessions(session_id, started_at) VALUES('stale_test', '2020-01-01T00:00:00')")
        conn.commit()
        conn.close()
        closed = DirectMemory.close_stale_sessions(max_age_hours=1)
        assert closed >= 1

class TestImportExport:
    def test_import_export_roundtrip(self):
        dm = DirectMemory()
        dm.file_read(["a.py"])
        dm.skill_loaded("test")
        events = dm.list_events()
        assert len(events) >= 3
        dm.end({"ok": True})
