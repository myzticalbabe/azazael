# coding: utf-8
"""
direct_memory.py — DirectMemory persistent session recording.

Stdlib-only. Zero CORE imports. Always works in <0.1s.
Writes directly to the same SQLite database as LocalMemoryStore
for cross-session queryability.

This is the CANONICAL memory system for all Codebuff/Azazael sessions.
Replaces 660-line CodebuffTracker with a lean, focused API.

Usage (from any Codebuff session):
    import sys; sys.path.insert(0, 'azazael/src')
    from CORE.direct_memory import DirectMemory

    dm = DirectMemory()
    dm.file_read(["MEMORIES.md", "ERROR_LOG.md"])
    dm.skill_loaded("azazael-startup")
    dm.file_edit("file.py", "Fix bug", lines_changed=3)
    dm.milestone("Phase complete", {"count": 5})
    dm.end({"tasks_complete": 5, "summary": "All done"})

Or use the module-level convenience:
    from CORE.direct_memory import record, end
    record("event_type", {"key": "value"})
    end({"summary": "ok"})
"""

import sqlite3
import json
import os
import signal
import threading
import atexit
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

__version__ = "1.0.0"

# -- Database path (same as LocalMemoryStore) ----------------------
def _get_db_path() -> Path:
    env_dir = os.environ.get("AZAZAEL_MEMORY_DIR", "")
    if env_dir:
        base = Path(env_dir)
    else:
        base = Path.home() / ".azazael"
    base.mkdir(parents=True, exist_ok=True)
    return base / "memory_store.db"

DB_PATH = _get_db_path()

# -- Schema (same as LocalMemoryStore) -----------------------------
_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    source      TEXT NOT NULL,
    event_type  TEXT NOT NULL,
    data        TEXT NOT NULL DEFAULT '{}',
    severity    TEXT NOT NULL DEFAULT 'info',
    tags        TEXT NOT NULL DEFAULT '[]',
    timestamp   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    -- CD1 schema migration (June 11 2026): Cross-domain correlation fields
    -- See azazael/research/CROSS_DOMAIN.md §CD1 for unified event schema
    event_uuid      TEXT,
    correlation_id  TEXT,
    audit_hash      TEXT,
    schema_version  INTEGER NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_memories_event_uuid ON memories(event_uuid);
CREATE INDEX IF NOT EXISTS idx_memories_correlation ON memories(correlation_id);

CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT PRIMARY KEY,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    source      TEXT NOT NULL DEFAULT 'unknown',
    metadata    TEXT NOT NULL DEFAULT '{}',
    event_count INTEGER NOT NULL DEFAULT 0
);
"""


class DirectMemory:
    """Persistent memory that auto-initializes every session. Stdlib-only, <0.1s.

    MANDATORY: Every Codebuff session MUST initialize DirectMemory at startup
    and call .end() at session completion. The atexit handler provides safety
    for unexpected exits but explicit .end() is preferred for summary data.

    This is the canonical memory system for Azazael. CodebuffTracker is
    deprecated — use DirectMemory instead.
    """

    def __init__(self, session_id: Optional[str] = None,
                 merged_session_id: Optional[str] = None):
        """Initialize DirectMemory.

        Args:
            session_id: Custom session ID. Auto-generated if not provided.
            merged_session_id: If provided, reuse this existing session instead
                of creating a new one. Events will be recorded under this session.
                Use this to group multiple Codebuff messages into one session.
        """
        self._db_path = str(DB_PATH)
        self._lock = threading.Lock()
        self._session_id = session_id or datetime.now().strftime("codebuff_%Y%m%d_%H%M%S")
        self._explicit_session = bool(session_id)  # True if user provided session_id
        self._merged_session_id = merged_session_id
        self._event_count = 0
        self._files_changed: List[str] = []
        self._ended = False
        # Validate session_id before proceeding
        if not self._session_id or not isinstance(self._session_id, str):
            self._session_id = datetime.now().strftime("codebuff_%Y%m%d_%H%M%S")
        if merged_session_id:
            if not merged_session_id or not isinstance(merged_session_id, str):
                merged_session_id = None
        self._init_db()

        if merged_session_id:
            # Reuse existing session — don't create a new one
            self._session_id = merged_session_id
            self._explicit_session = True
        self._start_session()
        atexit.register(self._atexit_handler)
        # F02 fix (June 7 2026): Register signal handlers for hard kills.
        # atexit alone does not fire on SIGTERM, SIGINT, or SIGBREAK.
        # These handlers ensure ended_at is set even on forced shutdown.
        self._register_signal_handlers()

    def _register_signal_handlers(self):
        """Register signal handlers to catch hard-kill signals.

        F02 fix: atexit handlers don't fire on SIGTERM/SIGINT/SIGBREAK.
        These handlers call .end() before the process terminates,
        preventing orphaned sessions with ended_at=NULL.

        Uses a separate flag (_signal_ending) and try/finally to avoid
        deadlock if the signal arrives while self._lock is held.
        """
        self._signal_ending = False

        def _handle_signal(signum, frame):
            if self._ended or self._signal_ending:
                return
            self._signal_ending = True
            try:
                sig_name = signal.Signals(signum).name
            except (ValueError, AttributeError):
                sig_name = f"signal_{signum}"
            try:
                # Direct DB write to avoid lock contention in signal context
                now = datetime.now(timezone.utc).isoformat()
                conn = sqlite3.connect(self._db_path, timeout=1)
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute(
                    "UPDATE sessions SET ended_at=? WHERE session_id=? AND ended_at IS NULL",
                    (now, self._session_id)
                )
                conn.execute(
                    "INSERT INTO memories(session_id,source,event_type,data,severity,tags,timestamp) "
                    "VALUES(?,?,?,?,?,?,?)",
                    (self._session_id, "Codebuff", "session_end",
                     json.dumps({"auto_recorded_by": f"signal_handler_{sig_name}",
                                "note": f"Session ended via {sig_name}",
                                "signal_number": signum}, ensure_ascii=False),
                     "warning", json.dumps(["session","session-lifecycle","shutdown","signal"]),
                     now)
                )
                conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                conn.commit()
                conn.close()
            except Exception:
                pass
            finally:
                self._ended = True
            os._exit(128 + signum)

        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                signal.signal(sig, _handle_signal)
            except (ValueError, OSError):
                pass
        if hasattr(signal, 'SIGBREAK'):
            try:
                signal.signal(signal.SIGBREAK, _handle_signal)
            except (ValueError, OSError):
                pass

    def _atexit_handler(self):
        """Auto-end session on unexpected process exit."""
        if not self._ended:
            try:
                self.end({"auto_recorded_by": "atexit_handler",
                          "note": "Session ended via atexit (unexpected exit)"})
            except Exception:
                pass

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA wal_autocheckpoint=1000")
        return conn

    def _init_db(self):
        """Initialize the database schema and run migrations.

        Creates tables if they don't exist. Handles concurrent access
        safely by wrapping in the instance lock.
        """
        with self._lock:
            try:
                conn = self._get_conn()
                conn.executescript(_SCHEMA)
                conn.commit()
                # CD1 schema migration (June 11 2026): Add cross-domain columns
                self._migrate_schema(conn)
                conn.close()
            except sqlite3.Error as e:
                raise RuntimeError(f"Failed to initialize database at {self._db_path}: {e}") from e

    def _migrate_schema(self, conn: sqlite3.Connection):
        """Run additive schema migrations for existing databases.

        CD1 (June 11 2026): Adds event_uuid, correlation_id, audit_hash,
        and schema_version columns to the memories table if they don't exist.
        """
        existing_cols = set(
            r[1] for r in conn.execute("PRAGMA table_info('memories')").fetchall()
        )
        migrations = [
            ("event_uuid", "TEXT"),
            ("correlation_id", "TEXT"),
            ("audit_hash", "TEXT"),
            ("schema_version", "INTEGER NOT NULL DEFAULT 1"),
        ]
        for col_name, col_type in migrations:
            if col_name not in existing_cols:
                conn.execute(
                    f"ALTER TABLE memories ADD COLUMN {col_name} {col_type}"
                )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_memories_event_uuid "
            "ON memories(event_uuid)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_correlation "
            "ON memories(correlation_id)"
        )
        conn.commit()

    def _start_session(self):
        """Insert or verify session record.

        For merged sessions, preserves the original started_at.
        For new sessions, inserts with current timestamp.

        Thread-safe: uses INSERT OR IGNORE + separate SELECT to avoid
        the SELECT-then-INSERT race on 3.14t free-threading.
        """
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            try:
                conn = self._get_conn()
                # Atomic INSERT OR IGNORE — avoids SELECT/INSERT race
                conn.execute(
                    "INSERT OR IGNORE INTO sessions(session_id, started_at, source, metadata) "
                    "VALUES(?, ?, ?, ?)",
                    (self._session_id, now, "Codebuff",
                     json.dumps({"recorder": f"DirectMemory v{__version__}"}))
                )
                conn.commit()
                conn.close()
            except sqlite3.Error:
                pass

        if not self._merged_session_id:
            self.record("session_start", {
                "action": "session_start",
                "direct_memory_version": __version__,
            }, tags=["session", "session-lifecycle", "startup"])
        else:
            self.record("message_start", {
                "action": "message_start (merged session)",
                "merged_into": self._merged_session_id,
            }, tags=["session", "session-lifecycle", "message"])

    @property
    def session_id(self) -> str:
        return self._session_id

    # -- Validation ------------------------------------------------

    VALID_SEVERITIES = {"info", "warning", "error", "critical"}
    MAX_SOURCE_LENGTH = 128
    MAX_EVENT_TYPE_LENGTH = 128

    def _validate(self, event_type: str, severity: str, source: str):
        """Lightweight validation — raises ValueError on invalid input."""
        if not source or not isinstance(source, str):
            raise ValueError(f"source must be a non-empty string, got: {source!r}")
        if len(source) > self.MAX_SOURCE_LENGTH:
            raise ValueError(f"source too long ({len(source)} > {self.MAX_SOURCE_LENGTH})")
        if not event_type or not isinstance(event_type, str):
            raise ValueError(f"event_type must be a non-empty string, got: {event_type!r}")
        if len(event_type) > self.MAX_EVENT_TYPE_LENGTH:
            raise ValueError(f"event_type too long ({len(event_type)} > {self.MAX_EVENT_TYPE_LENGTH})")
        sev = severity.lower() if isinstance(severity, str) else ""
        if sev not in self.VALID_SEVERITIES:
            raise ValueError(
                f"severity must be one of {sorted(self.VALID_SEVERITIES)}, got: {severity!r}"
            )
        return sev

    # -- Core recording ---------------------------------------------

    def record(self, event_type: str, data: Optional[Dict[str, Any]] = None,
               severity: str = "info", tags: Optional[List[str]] = None,
               source: str = "Codebuff") -> int:
        """Record a single event. Returns the row ID."""
        severity = self._validate(event_type, severity, source)
        now = datetime.now(timezone.utc).isoformat()
        data_str = json.dumps(data if data is not None else {}, ensure_ascii=False, default=str)
        all_tags = list(tags or [])
        if "session-recording" not in all_tags:
            all_tags.append("session-recording")
        tags_str = json.dumps(all_tags, ensure_ascii=False, default=str)

        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "INSERT INTO memories(session_id, source, event_type, data, severity, tags, timestamp) "
                "VALUES(?, ?, ?, ?, ?, ?, ?)",
                (self._session_id, source, event_type, data_str, severity, tags_str, now)
            )
            mem_id = cursor.lastrowid or 0
            conn.execute(
                "UPDATE sessions SET event_count = event_count + 1 WHERE session_id = ?",
                (self._session_id,)
            )
            conn.commit()
            conn.close()
            self._event_count += 1
        return mem_id

    # -- Convenience methods ----------------------------------------

    def file_read(self, filepaths: List[str], description: str = ""):
        return self.record("file_read", {
            "action": f"read: {description or ', '.join(Path(p).name for p in filepaths[:5])}",
            "files": filepaths,
            "count": len(filepaths),
        }, tags=["file", "file-read"])

    def file_edit(self, filepath: str, description: str, lines_changed: int = 0):
        with self._lock:
            if filepath and filepath not in self._files_changed:
                self._files_changed.append(filepath)
        return self.record("file_edit", {
            "action": f"edit: {description}",
            "filepath": filepath,
            "filename": Path(filepath).name if filepath else "unknown",
            "description": description,
            "lines_changed": lines_changed,
        }, tags=["file", "file-edit", "code"])

    def file_create(self, filepath: str, description: str, file_size_bytes: int = 0):
        with self._lock:
            if filepath and filepath not in self._files_changed:
                self._files_changed.append(filepath)
        return self.record("file_create", {
            "action": f"create: {description}",
            "filepath": filepath,
            "filename": Path(filepath).name if filepath else "unknown",
            "description": description,
            "size_bytes": file_size_bytes,
        }, tags=["file", "file-create", "code"])

    def file_delete(self, filepath: str, description: str):
        return self.record("file_delete", {
            "action": f"delete: {description}",
            "filepath": filepath,
            "filename": Path(filepath).name if filepath else "unknown",
            "description": description,
        }, severity="warning", tags=["file", "file-delete", "code"])

    def skill_loaded(self, skill_name: str):
        return self.record("skill_loaded", {
            "action": f"skill: {skill_name}",
            "skill": skill_name,
        }, tags=["skill", "startup"])

    def code_review(self, subject: str, issues_found: int = 0, issues_fixed: int = 0,
                    summary: str = ""):
        severity = "warning" if issues_found > 0 else "info"
        return self.record("code_review", {
            "action": f"review: {subject}",
            "subject": subject,
            "issues_found": issues_found,
            "issues_fixed": issues_fixed,
            "summary": summary[:500] if summary else "",
        }, severity=severity, tags=["review", "code-review", "quality"])

    def test_run(self, test_suite: str, passed: int, failed: int = 0,
                 skipped: int = 0, duration_ms: float = 0):
        severity = "error" if failed > 0 else "info"
        extra_tags = ["test-failure"] if failed > 0 else ["test-pass"]
        return self.record("test_run", {
            "action": f"test: {test_suite} ({passed}p/{failed}f/{skipped}s)",
            "test_suite": test_suite,
            "passed": passed, "failed": failed, "skipped": skipped,
            "duration_ms": round(duration_ms, 1),
        }, severity=severity, tags=["test", "test-run", "ci", "quality"] + extra_tags)

    def milestone(self, title: str, details: Optional[Dict] = None):
        return self.record("milestone_reached", {
            "action": f"milestone: {title}",
            "title": title,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, tags=["milestone", "progress"])

    def tooling_verify(self, tools_found: int, tools_missing: int,
                       details: Optional[Dict] = None):
        severity = "warning" if tools_missing > 0 else "info"
        return self.record("tooling_verify", {
            "action": f"tooling: {tools_found} found, {tools_missing} missing",
            "tools_found": tools_found,
            "tools_missing": tools_missing,
            "details": details or {},
        }, severity=severity, tags=["tooling", "startup", "environment"])

    def error_occurrence(self, error_id: int, title: str, file_path: str,
                         severity: str = "error", details: Optional[Dict] = None):
        return self.record("error_occurrence", {
            "action": f"error #{error_id}: {title}",
            "error_id": error_id,
            "title": title,
            "file_path": file_path,
            "error_log_ref": f"ERROR_LOG.md#error-{error_id}",
            "details": details or {},
        }, severity=severity, tags=["error", "error-log", "error-occurrence"])

    # -- Session lifecycle ------------------------------------------

    def end(self, summary: Optional[Dict] = None):
        """End the session with summary data. MANDATORY at session end.

        When using merged_session_id, the session is NOT closed — only
        the current sub-session recording stops. The merged session
        remains open for future messages.
        """
        if self._ended:
            return
        self._ended = True
        try:
            atexit.unregister(self._atexit_handler)
        except Exception:
            pass

        summary = summary or {}
        summary.update({
            "event_count": self._event_count,
            "files_changed_count": len(self._files_changed),
            "files_changed": self._files_changed[:50],
        })

        self.record("session_end", {
            "action": "session_end",
            "summary": summary,
        }, tags=["session", "session-lifecycle", "shutdown"])

        if self._explicit_session:
            # Explicitly named session — don't close (may be reused)
            if self._merged_session_id:
                self.record("message_end", {
                    "action": "message_end (merged session)",
                    "summary": summary,
                }, tags=["session", "session-lifecycle", "message"])
            else:
                self.record("session_end", {
                    "action": "session_end (explicit session, stays open)",
                    "summary": summary,
                }, tags=["session", "session-lifecycle", "shutdown"])
            return

        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self._get_conn()
            # WAL checkpoint before closing
            conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
            conn.execute(
                "UPDATE sessions SET ended_at = ? WHERE session_id = ?",
                (now, self._session_id)
            )
            conn.commit()
            conn.close()

    # -- Session maintenance ----------------------------------------

    @staticmethod
    def close_stale_sessions(max_age_hours: int = 1) -> int:
        """Close all sessions with ended_at=NULL older than max_age_hours.

        Call this at session start to clean up orphaned sessions from
        previous Codebuff messages that exited without calling .end().

        Args:
            max_age_hours: Close sessions older than this (default: 1 hour).

        Returns:
            Number of sessions closed.
        """
        conn = sqlite3.connect(str(DB_PATH), timeout=2, check_same_thread=False)
        try:
            cursor = conn.execute(
                "UPDATE sessions SET ended_at = ? "
                "WHERE ended_at IS NULL "
                "AND started_at < datetime('now', ?)",
                (datetime.now(timezone.utc).isoformat(), f"-{max_age_hours} hours")
            )
            closed = cursor.rowcount
            conn.commit()
        finally:
            conn.close()
        return closed

    @staticmethod
    def get_open_sessions_count() -> int:
        """Return the number of currently open (un-ended) sessions."""
        conn = sqlite3.connect(str(DB_PATH), timeout=2, check_same_thread=False)
        try:
            n = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE ended_at IS NULL"
            ).fetchone()[0]
        finally:
            conn.close()
        return n

    # -- Query helpers ----------------------------------------------

    def count(self) -> int:
        conn = self._get_conn()
        n = conn.execute(
            "SELECT COUNT(*) FROM memories WHERE session_id = ?",
            (self._session_id,)
        ).fetchone()[0]
        conn.close()
        return n

    def list_events(self, limit: int = 50) -> List[Dict]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM memories WHERE session_id = ? ORDER BY id ASC LIMIT ?",
            (self._session_id, limit)
        ).fetchall()
        conn.close()
        results = []
        for r in rows:
            d = dict(r)
            for field in ("data", "tags"):
                try:
                    d[field] = json.loads(d[field]) if isinstance(d[field], str) else d[field]
                except (json.JSONDecodeError, TypeError):
                    pass
            results.append(d)
        return results

    def recall_recent(self, limit: int = 20) -> List[Dict]:
        with self._lock:
            conn = self._get_conn()
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM memories WHERE source='Codebuff' ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            conn.close()
        results = []
        for r in rows:
            d = dict(r)
            for field in ("data", "tags"):
                try:
                    d[field] = json.loads(d[field]) if isinstance(d[field], str) else d[field]
                except (json.JSONDecodeError, TypeError):
                    pass
            results.append(d)
        return results


# -- Module-level convenience ---------------------------------------

_default_dm: Optional[DirectMemory] = None
_dm_lock = threading.Lock()


def get_dm(session_id: Optional[str] = None,
           merged_session_id: Optional[str] = None) -> DirectMemory:
    """Get or create the default DirectMemory singleton for this process.

    Args:
        session_id: Custom session ID (auto-generated if None).
        merged_session_id: Reuse an existing session for multi-message grouping.
    """
    global _default_dm
    if _default_dm is None:
        with _dm_lock:
            if _default_dm is None:
                _default_dm = DirectMemory(
                    session_id=session_id,
                    merged_session_id=merged_session_id,
                )
    return _default_dm


def record(event_type: str, data: Optional[Dict] = None,
           severity: str = "info", tags: Optional[List[str]] = None) -> int:
    """Quick record using the default DirectMemory instance."""
    return get_dm().record(event_type, data, severity=severity, tags=tags)


def end(summary: Optional[Dict] = None):
    """End the default session."""
    get_dm().end(summary)


# -- Self-test ------------------------------------------------------
if __name__ == "__main__":
    print(f"DirectMemory v{__version__} — Self-test")
    print(f"  DB: {DB_PATH}")

    dm = DirectMemory()
    print(f"  Session: {dm.session_id}")

    dm.file_read(["/fake/MEMORIES.md", "/fake/ERROR_LOG.md"], "canonical files")
    dm.skill_loaded("azazael-startup")
    dm.skill_loaded("azazael-error-prevention")
    dm.file_create("/fake/new_module.py", "Test creation")
    dm.file_edit("/fake/module.py", "Fix bug", lines_changed=5)
    dm.code_review("Test review", issues_found=1, issues_fixed=1)
    dm.test_run("test_suite", passed=5, failed=0)
    dm.milestone("Self-test complete", {"events": 7})
    dm.end({"status": "ok"})

    count = dm.count()
    print(f"  Events recorded: {count}")
    assert count >= 9, f"Expected >=9 events, got {count}"

    events = dm.list_events()
    for e in events:
        et = e['event_type']
        data = e.get('data', {})
        action = data.get('action', '?') if isinstance(data, dict) else '?'
        print(f"    [{e['id']}] {et}: {action}")

    # Verify cross-session recall
    recent = dm.recall_recent(3)
    print(f"  Recent Codebuff events: {len(recent)}")
    for r in recent:
        print(f"    [{r['id']}] {r['event_type']}")

    print("  DirectMemory self-test PASSED")
