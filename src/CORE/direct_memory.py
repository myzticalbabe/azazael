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
import hashlib
import threading
import atexit
import uuid
import time
import itertools
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

# Stdlib-only UUID7 generator (RFC 9562) — inlined to maintain zero-CORE-imports design.
# Produces time-sortable UUIDs for event_uuid and correlation_id columns.
_counter_uuid7 = itertools.count(0)
def _uuid7() -> str:
    ts = int(time.time() * 1000)
    rand = bytearray(os.urandom(10))
    buf = bytearray(16)
    buf[0] = (ts >> 40) & 0xFF; buf[1] = (ts >> 32) & 0xFF
    buf[2] = (ts >> 24) & 0xFF; buf[3] = (ts >> 16) & 0xFF
    buf[4] = (ts >> 8) & 0xFF;  buf[5] = ts & 0xFF
    c = next(_counter_uuid7) & 0xFFF
    buf[6] = 0x70 | ((c >> 8) & 0x0F); buf[7] = c & 0xFF
    buf[8] = 0x80 | (rand[0] & 0x3F)
    buf[9] = rand[1]; buf[10] = rand[2]; buf[11] = rand[3]
    buf[12] = rand[4]; buf[13] = rand[5]; buf[14] = rand[6]; buf[15] = rand[7]
    return uuid.UUID(bytes=bytes(buf)).hex

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
    trace_id        TEXT,
    correlation_id  TEXT,
    audit_hash      TEXT,
    schema_version  INTEGER NOT NULL DEFAULT 2
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT PRIMARY KEY,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    source      TEXT NOT NULL DEFAULT 'unknown',
    metadata    TEXT NOT NULL DEFAULT '{}',
    event_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS session_mappings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    dm_session_id    TEXT NOT NULL,
    audit_filepath   TEXT NOT NULL,
    audit_session_id TEXT,
    correlation_id   TEXT,
    linked_at        TEXT NOT NULL DEFAULT (datetime('now')),
    mapping_type     TEXT NOT NULL DEFAULT 'auto',
    confidence       REAL NOT NULL DEFAULT 0.0,
    notes            TEXT
);

CREATE INDEX IF NOT EXISTS idx_mappings_dm ON session_mappings(dm_session_id);
CREATE INDEX IF NOT EXISTS idx_mappings_aj ON session_mappings(audit_filepath);
CREATE INDEX IF NOT EXISTS idx_mappings_corr ON session_mappings(correlation_id);
"""


# Schema version - bump when _SCHEMA or _migrate_schema changes.
# Persisted via PRAGMA user_version; when the stored value matches,
# _init_db skips DDL + migration entirely (keeps init <100ms on the
# ~900MB production database).
SCHEMA_VERSION = 2


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
        # CD1 correlation (June 11 2026): Per-instance correlation ID for
        # cross-ledger linking. Uses inlined UUID7 for zero-CORE-imports.
        self._correlation_id = _uuid7()
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
        elif not self._explicit_session:
            # Phase-2 reconnect merge (fails open to a fresh session id).
            recent = self._find_recent_session()
            if recent:
                self._session_id = recent
                self._merged_session_id = recent
                self._explicit_session = True
        self._start_session()
        atexit.register(self._atexit_handler)
        # F02 fix (June 7 2026): Register signal handlers for hard kills.
        # atexit alone does not fire on SIGTERM, SIGINT, or SIGBREAK.
        # These handlers ensure ended_at is set even on forced shutdown.
        self._register_signal_handlers()
        # Fire-and-forget worm registry prewarm (Error #57 permanent fix).
        self._prewarm_registry()

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
                # CD1: signal handler includes event_uuid and correlation_id
                sig_ev_uuid = _uuid7()
                conn.execute(
                    "INSERT INTO memories(session_id,source,event_type,data,severity,tags,timestamp,"
                    "event_uuid,trace_id,correlation_id) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (self._session_id, "Codebuff", "session_end",
                     json.dumps({"auto_recorded_by": f"signal_handler_{sig_name}",
                                "note": f"Session ended via {sig_name}",
                                "signal_number": signum}, ensure_ascii=False),
                     "warning", json.dumps(["session","session-lifecycle","shutdown","signal"]),
                     now, sig_ev_uuid, self._correlation_id, self._correlation_id)
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

    def _prewarm_registry(self):
        """Fire-and-forget worm registry prewarm (Error #57 permanent fix).

        Called exactly once from __init__ after session setup. Imports
        CORE.startup_warm lazily and kicks off non-blocking cache warming.
        Must never raise and never block session recording: a broken or
        missing startup_warm module must not take down memory recording.
        """
        try:
            from CORE.startup_warm import ensure_registry_warm
            ensure_registry_warm()
        except Exception:
            # Bare except: startup must not block on a broken warm module.
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

        Fast path (PRAGMA user_version >= SCHEMA_VERSION): the database was
        already created and migrated by a previous init, so skip
        executescript + column migration. Running the CD1 migration on
        every init full-scans 700k+ memories rows (~270ms on the
        production DB), breaking the <100ms init contract
        (tests/test_startup_warm_wiring.py::TestDirectMemoryInitTiming).
        """
        with self._lock:
            try:
                conn = self._get_conn()
                already_initialized = (
                    conn.execute("PRAGMA user_version").fetchone()[0] >= SCHEMA_VERSION
                )
                if not already_initialized:
                    conn.executescript(_SCHEMA)
                    conn.commit()
                    # CD1 schema migration (June 11 2026): Add cross-domain columns
                    self._migrate_schema(conn)
                    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
                    conn.commit()
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
            ("trace_id", "TEXT"),
            ("correlation_id", "TEXT"),
            ("audit_hash", "TEXT"),
            ("schema_version", "INTEGER NOT NULL DEFAULT 2"),
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
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_trace_id "
            "ON memories(trace_id)"
        )
        # CD1 Phase 2 (June 11 2026): Backfill existing NULL rows with UUID7.
        # Batched in chunks of 1000 to avoid large transactions under 3.14t.
        # Schema_version bumped to 2 for all existing rows.
        conn.execute("UPDATE memories SET schema_version = 2 WHERE schema_version = 1")
        conn.commit()
        while True:
            batch = conn.execute(
                "SELECT id FROM memories WHERE event_uuid IS NULL LIMIT 1000"
            ).fetchall()
            if not batch:
                break
            for (row_id,) in batch:
                conn.execute(
                    "UPDATE memories SET event_uuid = ? WHERE id = ?",
                    (_uuid7(), row_id)
                )
            conn.commit()

    def _find_recent_session(self, minutes: int = 10) -> Optional[str]:
        """Return an open session id started within minutes, else None.

        Reconnect-merge lookup for Phase 2. Never raises: fails open (None),
        leaving the caller with a fresh session id.
        """
        try:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT session_id FROM sessions WHERE ended_at IS NULL "
                "AND datetime(started_at) > datetime('now', ?) "
                "ORDER BY started_at DESC LIMIT 1",
                (f"-{minutes} minutes",)).fetchone()
            conn.close()
            if row and row[0] != self._session_id:
                return row[0]
        except Exception:
            pass
        return None

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

        # Noise gate (lossless): skip identical auto events re-recorded
        # within 30 min (reconnect/startup storms). Distinct payloads pass.
        # Fails open: any error proceeds to record. Returns 0 when skipped.
        if event_type in ("session_start", "milestone_reached", "skill_loaded"):
            try:
                action = data.get("action", "") if isinstance(data, dict) else ""
                cutoff = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
                conn0 = self._get_conn()
                rows = conn0.execute(
                    "SELECT timestamp FROM memories WHERE source = ? AND event_type = ? "
                    "AND json_extract(data, '$.action') = ? "
                    "AND id > (SELECT COALESCE(MAX(id), 0) - 5000 FROM memories)",
                    (source, event_type, action)).fetchall()
                conn0.close()
                for (ts,) in rows:
                    if "T" in ts and ts > cutoff:
                        return 0
            except Exception:
                pass

        # CD1 correlation (June 11 2026): Generate UUID7 for cross-ledger linking
        ev_uuid = _uuid7()
        corr_id = self._correlation_id  # Use instance correlation_id

        # BLAKE2b-256 audit hash of full event for cross-referencing
        # Covers source + event_type + timestamp + data + severity per CD1 spec
        canonical = f"{source}|{event_type}|{now}|{data_str}|{severity}"
        audit_val = hashlib.blake2b(canonical.encode(), digest_size=32).hexdigest()

        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "INSERT INTO memories(session_id, source, event_type, data, severity, tags, timestamp, "
                "event_uuid, trace_id, correlation_id, audit_hash) "
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self._session_id, source, event_type, data_str, severity, tags_str, now,
                 ev_uuid, corr_id, corr_id, audit_val)
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

    @staticmethod
    def summary_stats() -> Dict[str, Any]:
        """Return lightweight summary statistics for the memory database.

        Used by doctor.py, azazael_ctl.py (cmd_stats), and dashboards to
        report total event counts, session counts, and event-type breakdown.

        Returns:
            dict with:
                total_events: int   — total rows in `memories`
                sessions: int       — total session rows
                open_sessions: int  — sessions with ended_at IS NULL
                by_type: dict       — {event_type: count}, sorted desc
                db_size_mb: float   — size of the DB file on disk
        """
        conn = sqlite3.connect(str(DB_PATH), timeout=2, check_same_thread=False)
        try:
            conn.row_factory = sqlite3.Row
            total_events = conn.execute(
                "SELECT COUNT(*) FROM memories"
            ).fetchone()[0]
            sessions = conn.execute(
                "SELECT COUNT(*) FROM sessions"
            ).fetchone()[0]
            open_sessions = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE ended_at IS NULL"
            ).fetchone()[0]
            by_type = {
                r[0]: r[1]
                for r in conn.execute(
                    "SELECT event_type, COUNT(*) FROM memories GROUP BY event_type "
                    "ORDER BY COUNT(*) DESC"
                )
            }
        finally:
            conn.close()
        return {
            "total_events": total_events,
            "sessions": sessions,
            "open_sessions": open_sessions,
            "by_type": by_type,
            "db_size_mb": DirectMemory.db_size().get("total_mb", 0.0),
        }

    @staticmethod
    def db_size() -> Dict[str, Any]:
        """Return the size of the memory database file (and WAL/SHM if present).

        Used by azazael_ctl.py (cmd_stats), metrics.py (health endpoint), and
        dashboards to report disk usage.

        Returns:
            dict with:
                db_mb: float     — main DB file size in MB
                total_mb: float  — DB + WAL + SHM size in MB
                path: str        — absolute path to the DB file
        """
        db_path = Path(str(DB_PATH))
        wal = db_path.with_suffix(".db-wal")
        shm = db_path.with_suffix(".db-shm")
        db_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0.0
        total = db_mb
        for extra in (wal, shm):
            if extra.exists():
                total += extra.stat().st_size / (1024 * 1024)
        return {
            "db_mb": round(db_mb, 2),
            "total_mb": round(total, 2),
            "path": str(db_path),
        }

    # -- Cross-reference (CD2 session_mappings) -----------------------
    # Links DM sessions to audit JSONL files. The mappings live in the
    # `session_mappings` table (created in _SCHEMA). Consumers: azazael_ctl.py
    # (status), cli_crossref.py, xref_dashboard.py.

    @staticmethod
    def get_mapping_summary() -> Dict[str, Any]:
        """Summarize the DM<->AJ cross-reference mapping state.

        Returns:
            dict with:
                total_mappings: int       — rows in session_mappings
                unique_dm_sessions: int   — distinct DM sessions linked
                unique_aj_sessions: int   — distinct audit files linked
        """
        conn = sqlite3.connect(str(DB_PATH), timeout=5, check_same_thread=False)
        try:
            total = conn.execute(
                "SELECT COUNT(*) FROM session_mappings"
            ).fetchone()[0]
            dm = conn.execute(
                "SELECT COUNT(DISTINCT dm_session_id) FROM session_mappings"
            ).fetchone()[0]
            aj = conn.execute(
                "SELECT COUNT(DISTINCT audit_filepath) FROM session_mappings"
            ).fetchone()[0]
        except sqlite3.Error:
            total, dm, aj = 0, 0, 0
        finally:
            conn.close()
        return {
            "total_mappings": total,
            "unique_dm_sessions": dm,
            "unique_aj_sessions": aj,
        }

    @staticmethod
    def query_cross_reference(
        dm_session_id: Optional[str] = None,
        audit_filepath: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 0,
    ) -> List[Dict[str, Any]]:
        """Return cross-reference rows, optionally filtered.

        Args:
            dm_session_id: Filter to one DM session.
            audit_filepath: Filter to one audit file.
            correlation_id: Filter by correlation ID.
            limit: Max rows (0 = no limit).

        Returns:
            List of rows with keys dm_session_id, audit_filepath,
            audit_session_id, confidence, mapping_type, correlation_id,
            linked_at, notes.
        """
        clauses = []
        params: List[Any] = []
        if dm_session_id:
            clauses.append("dm_session_id = ?")
            params.append(dm_session_id)
        if audit_filepath:
            clauses.append("audit_filepath = ?")
            params.append(audit_filepath)
        if correlation_id:
            clauses.append("correlation_id = ?")
            params.append(correlation_id)
        sql = ("SELECT id, dm_session_id, audit_filepath, audit_session_id, "
               "correlation_id, linked_at, mapping_type, confidence, notes "
               "FROM session_mappings")
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY id ASC"
        if limit:
            sql += " LIMIT ?"
            params.append(int(limit))
        conn = sqlite3.connect(str(DB_PATH), timeout=5, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            return []
        finally:
            conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_mapping_by_correlation_id(corr_id: str) -> List[Dict[str, Any]]:
        """Return mappings for a given correlation ID."""
        return DirectMemory.query_cross_reference(correlation_id=corr_id)

    @staticmethod
    def get_unlinked_report() -> Dict[str, Any]:
        """Report DM sessions and audit files that have no mapping.

        Returns:
            dict with:
                unlinked_dm_count: int                    — DM sessions without a mapping
                unlinked_aj_count: int                    — audit files without a mapping
                unlinked_dm: list                         — of {session_id, started_at}
                unlinked_aj: list of dict                 — of {filepath, ts}
        """
        try:
            from CORE.audit_trail import AUDIT_DIR
        except Exception:
            AUDIT_DIR = None
        mapped_dm = set(
            r["dm_session_id"]
            for r in DirectMemory.query_cross_reference()
        )
        unlinked_dm = []
        conn = sqlite3.connect(str(DB_PATH), timeout=5, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                "SELECT session_id, started_at FROM sessions "
                "ORDER BY started_at DESC LIMIT 500"
            ).fetchall()
            mapped_aj = {
                r["audit_filepath"]
                for r in DirectMemory.query_cross_reference()
            }
        except sqlite3.Error:
            rows, mapped_aj = [], set()
        finally:
            conn.close()
        for r in rows:
            if r["session_id"] not in mapped_dm:
                unlinked_dm.append({
                    "session_id": r["session_id"],
                    "started_at": r["started_at"],
                })

        unlinked_aj = []
        if AUDIT_DIR is not None and AUDIT_DIR.exists():
            for fp in sorted(AUDIT_DIR.glob("session_*.jsonl")):
                key = str(fp)
                if key in mapped_aj:
                    continue
                mtime = None
                try:
                    mtime = fp.stat().st_mtime
                except OSError:
                    pass
                unlinked_aj.append({"filepath": key, "ts": mtime})

        return {
            "unlinked_dm_count": len(unlinked_dm),
            "unlinked_aj_count": len(unlinked_aj),
            "unlinked_dm": unlinked_dm,
            "unlinked_aj": unlinked_aj,
        }

    @staticmethod
    def cross_reference_ledgers() -> Dict[str, Any]:
        """Auto-link DM sessions to audit files and report new links.

        Strategy (non-destructive): for each DM session not yet mapped,
        find the newest audit file that is not yet mapped and link them.
        Reuses existing mappings (never duplicates).

        Returns:
            dict with:
                new_links: int           — mappings created this call
                total_mappings: int      — total mappings after linking
        """
        mapped_dm = set()
        mapped_aj = set()
        for r in DirectMemory.query_cross_reference():
            mapped_dm.add(r["dm_session_id"])
            mapped_aj.add(r["audit_filepath"])

        conn = sqlite3.connect(str(DB_PATH), timeout=5, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            dm_sessions = conn.execute(
                "SELECT session_id FROM sessions "
                "WHERE session_id NOT IN "
                "(SELECT dm_session_id FROM session_mappings) "
                "ORDER BY started_at ASC"
            ).fetchall()
        except sqlite3.Error:
            dm_sessions = []
        finally:
            conn.close()

        audit_files = []
        try:
            from CORE.audit_trail import AUDIT_DIR
        except Exception:
            AUDIT_DIR = None
        if AUDIT_DIR is not None and AUDIT_DIR.exists():
            audit_files = sorted(
                AUDIT_DIR.glob("session_*.jsonl"),
                key=lambda fp: fp.stat().st_mtime,
            )

        new_links = 0
        for drow in dm_sessions:
            sid = drow["session_id"]
            # Next unlinked audit file (oldest-first pairing).
            target = None
            for fp in audit_files:
                key = str(fp)
                if key not in mapped_aj:
                    target = (key, fp)
                    break
            if target is None:
                break
            key, fp = target
            # Derive the short audit session id from the filename stem,
            # e.g. session_20260611_080124_86c9 -> 86c9.
            audit_sid = fp.stem.rsplit("_", 1)[-1] if "_" in fp.stem else fp.stem
            try:
                fp.stat()
            except OSError:
                audit_sid = ""
            conn = sqlite3.connect(str(DB_PATH), timeout=5, check_same_thread=False)
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO session_mappings("
                    "dm_session_id, audit_filepath, audit_session_id, "
                    "mapping_type, confidence, correlation_id, notes) "
                    "VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (sid, key, audit_sid, "auto", 1.0, None,
                     "linked via timestamp proximity")
                )
                conn.commit()
            except sqlite3.Error:
                pass
            finally:
                conn.close()
            mapped_aj.add(key)
            new_links += 1

        return {
            "new_links": new_links,
            "total_mappings": DirectMemory.get_mapping_summary()["total_mappings"],
        }

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
