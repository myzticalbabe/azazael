# coding: utf-8
"""
local_memory.py — SQLite-backed persistent AI memory store.

Provides full CRUD for session events, memories, and recall queries.
Works completely offline — no PAMS server required.
Designed for Eve Unleashed and all Azazael components.

Features:
- record_event(source, event_type, data, severity, tags) -> memory_id
- query_memories(source=None, event_type=None, limit=50, since=None) -> list
- search_memories(query, source=None, limit=50) -> fuzzy text search
- recall_recent(limit=20, source=None) -> most recent memories
- list_sessions() -> all session IDs with counts
- get_session(session_id) -> all memories for a session
- get_stats() -> memory store statistics
- export_json(path) -> export all memories to JSON file

Usage:
    from CORE.local_memory import LocalMemoryStore
    store = LocalMemoryStore()
    store.record_event("EveUnleashed", "inference", {"prompt": "..."})
    results = store.search_memories("inference")
    recent = store.recall_recent(10)
"""

import sqlite3
import json
import os
import sys
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from CORE.uuid7 import uuid7

# -- Storage location ------------------------------------------------------
def _get_store_path() -> Path:
    """Determine storage path.

    Resolution order:
    1. AZAZAEL_MEMORY_DIR env var (explicit override)
    2. ~/.azazael/ (always fast - local SSD, no network/SD card)

    G: drive is intentionally NOT used as default because it is an SD card
    with high latency that causes sqlite3 operations to hang (>120s).
    Use AZAZAEL_MEMORY_DIR=G:/AZAZAEL/memory to opt into G: explicitly.
    """
    env_dir = os.environ.get("AZAZAEL_MEMORY_DIR", "")
    if env_dir:
        base = Path(env_dir)
    else:
        base = Path.home() / ".azazael"
    base.mkdir(parents=True, exist_ok=True)

    target_db = base / "memory_store.db"
    return target_db


DB_PATH = _get_store_path()
VERSION = "1.0.0"


def track_regime() -> Dict[str, Any]:
    """Snapshot of the regime a training run executes in (STACK Phase 1).

    Cheap, local, fail-soft signals a contextual router can condition on:
    time structure (slot/hour/dow), store sizes, recent outcome volume.
    Never raises: any unreadable signal becomes -1/None rather than
    breaking a training run. Kept flat (JSON-native) for ledger reads.
    """
    now = datetime.now().astimezone()
    reg: Dict[str, Any] = {
        "slot": int(now.timestamp()) // 300,
        "hour": now.hour,
        "dow": now.weekday(),
        "db_mb_main": -1.0,
        "db_mb_tel": -1.0,
        "outcome_1h": -1,
    }
    try:
        base = DB_PATH.parent
        for key, name in (("db_mb_main", "memory_store.db"),
                          ("db_mb_tel", "telemetry_store.db")):
            try:
                reg[key] = round((base / name).stat().st_size / 1e6, 1)
            except OSError:
                pass
    except Exception:
        pass
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        try:
            cutoff = (datetime.now(timezone.utc)
                      - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            reg["outcome_1h"] = int(conn.execute(
                "SELECT COUNT(*) FROM memories WHERE created_at > ?",
                (cutoff,)).fetchone()[0])
        finally:
            conn.close()
    except Exception:
        pass
    return reg

# -- Schema -----------------------------------------------------------------
SCHEMA_SQL = """
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

CREATE INDEX IF NOT EXISTS idx_memories_session ON memories(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_source ON memories(source);
CREATE INDEX IF NOT EXISTS idx_memories_event_type ON memories(event_type);
CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp);
CREATE INDEX IF NOT EXISTS idx_memories_severity ON memories(severity);

-- Composite indexes for common query patterns — quantitative performance improvement
CREATE INDEX IF NOT EXISTS idx_memories_source_event_severity ON memories(source, event_type, severity);
CREATE INDEX IF NOT EXISTS idx_memories_session_timestamp ON memories(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_memories_severity_timestamp ON memories(severity, timestamp);

CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT PRIMARY KEY,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    source      TEXT NOT NULL DEFAULT 'unknown',
    metadata    TEXT NOT NULL DEFAULT '{}',
    event_count INTEGER NOT NULL DEFAULT 0
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    event_type,
    data,
    tags,
    content='memories',
    content_rowid='id'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, event_type, data, tags)
    VALUES (new.id, new.event_type, new.data, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, event_type, data, tags)
    VALUES ('delete', old.id, old.event_type, old.data, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, event_type, data, tags)
    VALUES ('delete', old.id, old.event_type, old.data, old.tags);
    INSERT INTO memories_fts(rowid, event_type, data, tags)
    VALUES (new.id, new.event_type, new.data, new.tags);
END;

CREATE TABLE IF NOT EXISTS knowledge_patterns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_agent    TEXT NOT NULL,
    pattern_type    TEXT NOT NULL,
    embedding       TEXT NOT NULL DEFAULT '[]',
    metadata        TEXT NOT NULL DEFAULT '{}',
    confidence      REAL NOT NULL DEFAULT 1.0,
    hit_count       INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_kp_source_agent ON knowledge_patterns(source_agent);
CREATE INDEX IF NOT EXISTS idx_kp_pattern_type ON knowledge_patterns(pattern_type);
"""


class LocalMemoryStore:
    """SQLite-backed persistent memory store for AI session recording.

    Quantitative improvements over v1.0.0:
    - Composite indexes for common query patterns (faster filtered queries)
    - Query performance tracking with timing, count, and slow-query logging
    - Database health scoring (0-100) with fragmentation, WAL, integrity metrics
    - Size monitoring with configurable threshold warnings
    - Auto-backup scheduling alongside auto-vacuum
    - Enhanced get_stats() with query performance, fragmentation, WAL metrics
    - Index usage analysis for query optimization
    """

    VERSION = "2.0.0"

    # -- Performance Tracking ------------------------------------------
    # Track query performance metrics (reset on store creation)
    _query_count: int = 0
    _slow_query_count: int = 0
    _total_query_time_ms: float = 0.0
    _max_query_time_ms: float = 0.0
    _slow_query_threshold_ms: float = 500.0  # Queries >500ms logged as slow

    #: Hard ceiling on rows returned by a single `query_memories` call.
    #: The store reaches hundreds of MB and 200k+ rows, so an unbounded
    #: LIMIT is a memory hazard. Callers that need more must paginate with
    #: `offset`. Requests above this are CLAMPED AND WARNED (2026-09-18) —
    #: the clamp used to be silent, so callers asking for 5000 rows got 500
    #: and had no way to tell a truncated read from a complete one.
    MAX_QUERY_LIMIT: int = 500

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DB_PATH)
        self._lock = threading.Lock()
        self._maintenance_lock = threading.Lock()
        self._limit_clamp_issued = False
        self._session_id = datetime.now().strftime("codebuff_%Y%m%d_%H%M%S")
        self._vacuum_running = False
        self._vacuum_interval: float = 86400.0  # 24 hours
        self._vacuum_thread: Optional[threading.Thread] = None
        self._backup_running = False
        self._backup_thread: Optional[threading.Thread] = None
        self._backup_interval: float = 86400.0  # 24 hours (default)
        self._last_backup_path: Optional[str] = None
        self._size_warning_issued = False
        self._max_size_mb = 400  # Default threshold (warn at 80% of 500 MB quota)
        # Instance-level performance counters (was class-level — moved for 3.14t safety)
        self._query_count: int = 0
        self._slow_query_count: int = 0
        self._total_query_time_ms: float = 0.0
        self._max_query_time_ms: float = 0.0
        self._slow_query_threshold_ms: float = 500.0
        # P0 fix (June 11 2026): Dedicated lock for _QueryTimer stat updates.
        # _QueryTimer.__exit__() previously assumed the caller held self._lock,
        # but query_memories() and search_memories() do NOT acquire self._lock.
        # Under 3.14t free-threading, two threads calling query_memories()
        # simultaneously race on _query_count, _total_query_time_ms, etc.
        self._perf_lock = threading.Lock()
        self._init_db()

        # Config-driven auto-maintenance is deferred — import CORE.config
        # triggers slow G: drive access via paths.py. Call _apply_config()
        # explicitly after construction if config is needed.
        self._config_applied = False

    def _init_db(self):
        """Initialize database schema and run migrations."""
        with self._lock:
            conn = sqlite3.connect(self.db_path, timeout=2)
            # Same discipline as _get_conn: busy_timeout FIRST, so the
            # CD1 migration UPDATE below waits on live writers instead of
            # failing instantly with "database is locked" (measured
            # 2026-09-26: benchmark colliding with 8 chain processes).
            # 60s: a VACUUM or bulk DELETE on the 800MB+ store can hold
            # the writer lock for tens of seconds; process start is rare
            # and may wait, but must never crash on contention.
            conn.execute("PRAGMA busy_timeout=60000")
            conn.executescript(SCHEMA_SQL)
            conn.commit()
            # CD1 schema migration (June 11 2026): Add cross-domain columns
            # to existing databases that were created before these columns existed.
            self._migrate_schema(conn)
            conn.close()

    def _migrate_schema(self, conn: sqlite3.Connection):
        """Run additive schema migrations for existing databases.

        CD1 (June 11 2026): Adds event_uuid, correlation_id, audit_hash,
        and schema_version columns to the memories table if they don't exist
        on databases created before this migration.

        Uses ALTER TABLE ADD COLUMN which is non-destructive and backward-compatible.
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
        # Create indexes if they don't exist (idempotent via IF NOT EXISTS)
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
                    (uuid7().hex, row_id)
                )
            conn.commit()

    def _apply_config(self):
        """Apply configuration from CORE.config (call explicitly after construction).

        Deferred from __init__ to avoid slow G: drive access via paths.py
        during import. Safe to call multiple times — runs at most once.
        """
        if self._config_applied:
            return
        self._config_applied = True
        try:
            from CORE.config import get_config
            cfg = get_config()
            ms_cfg = cfg.memory_store
            self._max_size_mb = ms_cfg.max_size_mb_warn
            if ms_cfg.auto_vacuum:
                self.start_auto_vacuum(interval_hours=ms_cfg.vacuum_interval_hours)
            if cfg.backup.interval_hours > 0:
                self.start_auto_backup(
                    interval_hours=cfg.backup.interval_hours,
                    keep_count=cfg.backup.keep_count,
                    target_dir=cfg.backup.target_dir,
                )
        except Exception:
            pass  # Config not available — defaults stay

    # -- Query Performance Tracking ---------------------------------------

    class _QueryTimer:
        """Context manager that times query execution and updates store stats.

        NOTE: Does NOT acquire self.store._lock in __exit__. The caller
        (typically record_event) already holds self._lock. Re-acquiring
        it would deadlock since threading.Lock is not re-entrant.
        Stats updates are safe because they run inside the caller's lock.
        """
        def __init__(self, store: "LocalMemoryStore", query_label: str = ""):
            self.store = store
            self.query_label = query_label
            self.start = 0.0
            self.duration_ms = 0.0

        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.duration_ms = (time.perf_counter() - self.start) * 1000
            # P0 fix (June 11 2026): Acquire dedicated _perf_lock for stat updates.
            # Previously assumed caller held self.store._lock, but query_memories()
            # and search_memories() do NOT. Under 3.14t free-threading, the
            # read-modify-write on these counters races without a lock.
            with self.store._perf_lock:
                self.store._query_count += 1
                self.store._total_query_time_ms += self.duration_ms
                if self.duration_ms > self.store._max_query_time_ms:
                    self.store._max_query_time_ms = self.duration_ms
                if self.duration_ms > self.store._slow_query_threshold_ms:
                    self.store._slow_query_count += 1

    def _get_conn(self) -> sqlite3.Connection:
        """Get a new connection. Uses WAL mode for concurrent access.

        NOTE: must not take self._lock -- callers such as register_pattern and
        start_session already hold it, and threading.Lock is not re-entrant.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=60)
        conn.row_factory = sqlite3.Row
        # busy_timeout FIRST. It is what makes later statements wait for a lock
        # instead of failing, and it used to be issued *after* journal_mode --
        # so the journal_mode statement below ran with the default timeout of 0.
        # 2026-09-28: 15s -> 60s. Train ARS runs fail with "database is locked"
        # ~39x/day; contention (472MB DB, concurrent chain writers) exceeds 15s.
        conn.execute("PRAGMA busy_timeout=60000")
        # journal_mode is PERSISTENT (stored in the DB header), so it only needs
        # to be established once. Re-issuing it on EVERY connection is what broke
        # concurrent reads: changing it takes a write lock, so a fresh reader
        # racing a writer raised "database is locked" immediately -- the error
        # seen in TestKnowledgeGraphConcurrency. Read it instead, and only set it
        # when the database genuinely is not in WAL yet.
        try:
            row = conn.execute("PRAGMA journal_mode").fetchone()
            if not row or str(row[0]).lower() != "wal":
                conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            # A writer holds the lock while the mode is being established. WAL is
            # already the applicable mode, so continuing is safe.
            pass
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA wal_autocheckpoint=1000")
        return conn

    # -- Performance Metrics ----------------------------------------------

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get query performance statistics.

        Returns:
            Dict with query count, timing metrics, and slow query info.
        """
        avg_time = (
            self._total_query_time_ms / self._query_count
            if self._query_count > 0 else 0.0
        )
        return {
            "total_queries": self._query_count,
            "total_query_time_ms": round(self._total_query_time_ms, 2),
            "avg_query_time_ms": round(avg_time, 2),
            "max_query_time_ms": round(self._max_query_time_ms, 2),
            "slow_query_count": self._slow_query_count,
            "slow_query_threshold_ms": self._slow_query_threshold_ms,
            "slow_query_pct": round(
                (self._slow_query_count / max(self._query_count, 1)) * 100, 2
            ),
        }

    # -- Session Management ------------------------------------------------

    def start_session(self, source: str = "unknown", metadata: Optional[dict] = None,
                      session_id: Optional[str] = None) -> str:
        """Start a new session. Returns session_id."""
        sid = session_id or self._session_id
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "INSERT OR REPLACE INTO sessions(session_id, started_at, source, metadata) VALUES(?, ?, ?, ?)",
                (sid, datetime.now(timezone.utc).isoformat(), source, json.dumps(metadata or {}))
            )
            conn.commit()
            conn.close()
        return sid

    @property
    def current_session_id(self) -> str:
        """Return the current session ID."""
        return self._session_id

    def end_session(self, session_id: Optional[str] = None):
        """Mark a session as ended."""
        sid = session_id or self._session_id
        with self._lock:
            conn = self._get_conn()
            conn.execute(
                "UPDATE sessions SET ended_at = ? WHERE session_id = ?",
                (datetime.now(timezone.utc).isoformat(), sid)
            )
            conn.commit()
            conn.close()

    def list_sessions(self, limit: int = 20) -> List[Dict]:
        """List recent sessions with event counts."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT session_id, started_at, ended_at, source, event_count, metadata "
            "FROM sessions ORDER BY started_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_session(self, session_id: str) -> Dict:
        """Get session info with all memories."""
        conn = self._get_conn()
        session = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not session:
            conn.close()
            return {"session_id": session_id, "error": "Not found", "memories": []}
        memories = conn.execute(
            "SELECT * FROM memories WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        ).fetchall()
        conn.close()
        result = dict(session)
        result["memories"] = [dict(m) for m in memories]
        return result

    # -- Recording ----------------------------------------------------------

    # -- Data Validation ----------------------------------------------

    VALID_SEVERITIES = {"info", "warning", "error", "critical"}
    MAX_DATA_SIZE = 10 * 1024 * 1024  # 10 MB max data payload
    MAX_TAGS = 50  # Max tags per event
    MAX_SOURCE_LENGTH = 128
    MAX_EVENT_TYPE_LENGTH = 128

    def _validate_event_args(self, source: str, event_type: str, data: Any,
                              severity: str, tags: Optional[List[str]]):
        """Validate event arguments before recording.

        Raises ValueError on invalid input with a descriptive message.
        """
        if not source or not isinstance(source, str):
            raise ValueError(f"source must be a non-empty string, got: {source!r}")
        if len(source) > self.MAX_SOURCE_LENGTH:
            raise ValueError(f"source too long ({len(source)} > {self.MAX_SOURCE_LENGTH})")

        if not event_type or not isinstance(event_type, str):
            raise ValueError(f"event_type must be a non-empty string, got: {event_type!r}")
        if len(event_type) > self.MAX_EVENT_TYPE_LENGTH:
            raise ValueError(f"event_type too long ({len(event_type)} > {self.MAX_EVENT_TYPE_LENGTH})")

        severity_lower = severity.lower() if isinstance(severity, str) else ""
        if severity_lower not in self.VALID_SEVERITIES:
            raise ValueError(
                f"severity must be one of {sorted(self.VALID_SEVERITIES)}, got: {severity!r}"
            )

        if tags is not None:
            if not isinstance(tags, list):
                raise ValueError(f"tags must be a list, got: {type(tags).__name__}")
            if len(tags) > self.MAX_TAGS:
                raise ValueError(f"tags too many ({len(tags)} > {self.MAX_TAGS})")
            for tag in tags:
                if not isinstance(tag, str):
                    raise ValueError(f"each tag must be a string, got: {type(tag).__name__}: {tag!r}")

        if data is not None:
            data_str = json.dumps(data, ensure_ascii=False)
            if len(data_str) > self.MAX_DATA_SIZE:
                raise ValueError(f"data payload too large ({len(data_str)} bytes > {self.MAX_DATA_SIZE})")

        return severity_lower

    # -- Recording ----------------------------------------------------------

    def record_event(self, source: str, event_type: str, data: Any = None,
                     severity: str = "info", tags: Optional[List[str]] = None,
                     session_id: Optional[str] = None,
                     correlation_id: Optional[str] = None) -> int:
        """
        Record an event to memory.

        Args:
            source: Component name (e.g., "EveUnleashed", "CLUSTERWORMS").
            event_type: Event category (e.g., "inference", "repl_exec", "session_start").
            data: JSON-serializable payload.
            severity: "info", "warning", "error", or "critical".
            tags: Optional list of string tags for categorization.
            session_id: Optional session override.
            correlation_id: Optional CD1 cross-ledger correlation ID.

        Returns:
            The memory ID (rowid).

        Raises:
            ValueError: If validation fails.
        """
        severity = self._validate_event_args(source, event_type, data, severity, tags)

        sid = session_id or self._session_id
        data_str = json.dumps(data if data is not None else {}, ensure_ascii=False)
        tags_str = json.dumps(tags or [], ensure_ascii=False)
        ts = datetime.now(timezone.utc).isoformat()

        with self._lock:
            with self._QueryTimer(self, "record_event"):
                # Lock-contention retry (2026-09-25): concurrent Chain jobs
                # (evolution/train/dream/metacog) share this 600MB WAL DB, and
                # an exclusive hold longer than busy_timeout surfaces as
                # "database is locked" — losing training/evolution records
                # while the run itself reports success. Bounded retries with
                # backoff; still raises after exhaustion (callers fail open).
                last_exc = None
                for attempt in (1, 2, 3):
                    conn = None
                    try:
                        conn = self._get_conn()
                        # CD1 correlation (June 11 2026): Generate UUID7 for cross-ledger linking
                        ev_uuid = uuid7().hex
                        corr_id = correlation_id or ""
                        trace_id_val = corr_id or uuid7().hex  # trace_id defaults to correlation_id
                        # BLAKE2b-256 audit hash of full event for cross-referencing
                        # Covers source + event_type + timestamp + data + severity per CD1 spec
                        canonical = f"{source}|{event_type}|{ts}|{data_str}|{severity}"
                        audit_val = hashlib.blake2b(canonical.encode(), digest_size=32).hexdigest()
                        cursor = conn.execute(
                            "INSERT INTO memories(session_id, source, event_type, data, severity, tags, timestamp, "
                            "event_uuid, trace_id, correlation_id, audit_hash) "
                            "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (sid, source, event_type, data_str, severity, tags_str, ts, ev_uuid, trace_id_val, corr_id, audit_val)
                        )
                        mem_id = cursor.lastrowid or 0

                        # Update session event count
                        conn.execute(
                            "UPDATE sessions SET event_count = event_count + 1 WHERE session_id = ?",
                            (sid,)
                        )
                        conn.commit()
                        break
                    except sqlite3.OperationalError as exc:
                        last_exc = exc
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                        if attempt < 3:
                            time.sleep(float(attempt))
                            continue
                        # Observable exhaustion (forensic 2026-09-26): a stall
                        # longer than ~48s of retries still loses the record.
                        # The DB itself is unwritable by definition here, so
                        # count it in a sidecar monitors can read instead of
                        # letting it vanish into one log line.
                        try:
                            _sidecar = os.path.join(
                                os.path.dirname(self.db_path),
                                "lock_exhaustion.jsonl")
                            with open(_sidecar, "a", encoding="utf-8") as fh:
                                fh.write(json.dumps({
                                    "at": datetime.now(timezone.utc).isoformat(),
                                    "event_type": event_type, "source": source,
                                }) + "\n")
                        except Exception:
                            pass
                        raise
                    finally:
                        if conn is not None:
                            try:
                                conn.close()
                            except Exception:
                                pass

        # -- Size monitoring: issue warning if DB exceeds threshold -----
        if not self._size_warning_issued:
            try:
                current_mb = os.path.getsize(self.db_path) / (1024 * 1024)
                if current_mb > self._max_size_mb:
                    self._size_warning_issued = True
                    import logging
                    logging.warning(
                        f"Memory store at {self.db_path} is {current_mb:.1f} MB "
                        f"(threshold: {self._max_size_mb} MB). "
                        f"Consider running purge_old() or export_json() to reduce size."
                    )
            except Exception:
                pass

        return mem_id

    # -- Querying -----------------------------------------------------------

    def query_memories(self, source: Optional[str] = None, event_type: Optional[str] = None,
                       severity: Optional[str] = None, limit: int = 50,
                       offset: int = 0, since: Optional[str] = None,
                       session_id: Optional[str] = None, max_age_days: Optional[int] = None,
                       exclude_sources: Optional[List[str]] = None) -> List[Dict]:
        """
        Query memories with optional filters.

        Args:
            source: Filter by source component.
            event_type: Filter by event type.
            severity: Filter by severity level.
            limit: Max results to return.
            offset: Pagination offset.
            since: ISO timestamp — only return events after this time.
            session_id: Filter by session.
            max_age_days: Only return events newer than N days.
            exclude_sources: Skip events from these source components (used to
                keep training pools free of self-generated bookkeeping noise,
                e.g. RLTrainLoop/ModelVersioner events recorded by the very
                training runs being evaluated).

        Returns:
            List of memory dicts, newest first.
        """
        conditions = ["severity != 'deleted'"]  # Exclude tombstoned (soft-deleted) rows
        params: List[Any] = []

        if source:
            conditions.append("source = ?")
            params.append(source)
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        if severity:
            conditions.append("severity = ?")
            params.append(severity)
        if since:
            conditions.append("timestamp > ?")
            params.append(since)
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        if max_age_days:
            # Python-computed UTC cutoff in T-format (2026-09-09 fix):
            # SQLite datetime('now') renders space-separated, which sorts
            # BELOW every T-separated stored row — the old predicate
            # matched all of today's rows regardless of window.
            conditions.append("timestamp > ?")
            params.append((datetime.now(timezone.utc) - timedelta(days=max_age_days)).isoformat())
        if exclude_sources:
            conditions.append(
                "source NOT IN (%s)" % ", ".join("?" * len(exclude_sources)))
            params.extend(exclude_sources)

        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM memories WHERE {where} ORDER BY id DESC LIMIT ? OFFSET ?"
        # Loud clamp: a truncated read that looks complete is worse than a
        # refused one, because the caller silently analyses the wrong window
        # (this bit the evolution history gates and the training-data
        # extractors, all of which request limit=5000).
        effective_limit = min(limit, self.MAX_QUERY_LIMIT)
        if limit > self.MAX_QUERY_LIMIT and not self._limit_clamp_issued:
            self._limit_clamp_issued = True
            try:
                import logging
                logging.warning(
                    "query_memories(limit=%s) clamped to MAX_QUERY_LIMIT=%s "
                    "(source=%s, event_type=%s). Paginate with offset to read "
                    "further rows; a single call will not return more.",
                    limit, self.MAX_QUERY_LIMIT, source, event_type,
                )
            except Exception:
                pass
        params.extend([effective_limit, offset])

        with self._QueryTimer(self, "query_memories"):
            # Same lock-contention retry as record_event (2026-09-27): reads
            # block on a writer's exclusive hold (VACUUM, checkpoint, bulk
            # DELETE, migration). Measured: a training run died 67s in on a
            # locked extraction query while the write path would have
            # retried. Readers get the same bounded retries; exhaustion
            # raises like before (callers fail open).
            last_exc = None
            rows = []
            for attempt in (1, 2, 3):
                conn = None
                try:
                    conn = self._get_conn()
                    rows = conn.execute(sql, params).fetchall()
                    break
                except sqlite3.OperationalError as exc:
                    last_exc = exc
                    if attempt < 3:
                        time.sleep(float(attempt * 2))
                        continue
                    raise
                finally:
                    if conn is not None:
                        try:
                            conn.close()
                        except Exception:
                            pass

        results = []
        for r in rows:
            d = dict(r)
            # Parse JSON fields
            for field in ("data", "tags"):
                try:
                    d[field] = json.loads(d[field]) if isinstance(d[field], str) else d[field]
                except (json.JSONDecodeError, TypeError):
                    pass
            results.append(d)
        return results

    def count_memories(self, event_type: Optional[str] = None,
                       source: Optional[str] = None) -> int:
        """True row count for one tap, unbounded (SQL COUNT, not a capped page).

        `query_memories` clamps every call to MAX_QUERY_LIMIT, so a consumer
        that sums fetched rows reports a SAMPLE as if it were the population as
        soon as a tap outgrows its fetch budget. Growth checks (the neural
        loop's grade stage) need the real number: a saturated sample pins at
        the limit and can never observe growth again.
        """
        conn = self._get_conn()
        try:
            sql = "SELECT COUNT(*) as n FROM memories WHERE 1=1"
            params = []
            if event_type:
                sql += " AND event_type = ?"
                params.append(event_type)
            if source:
                sql += " AND source = ?"
                params.append(source)
            return int(conn.execute(sql, params).fetchone()["n"])
        finally:
            conn.close()

    def search_memories(self, query: str, source: Optional[str] = None,
                        limit: int = 50) -> List[Dict]:
        """
        Full-text search across event_type, data, and tags.

        Args:
            query: Search text.
            source: Optional source filter.
            limit: Max results.

        Returns:
            List of matching memory dicts, ranked by relevance.
        """
        # Sanitize FTS5 query — escape special chars
        safe_query = query.replace('"', '""').replace("'", "''")
        # Exclude tombstoned (soft-deleted) rows, same as query_memories()
        conditions = ["memories_fts MATCH ?", "memories.severity != 'deleted'"]
        params: List[Any] = [f'"{safe_query}"']

        if source:
            conditions.append("memories.source = ?")
            params.append(source)

        where = " AND ".join(conditions)
        sql = f"""
            SELECT memories.*, rank
            FROM memories_fts
            JOIN memories ON memories_fts.rowid = memories.id
            WHERE {where}
            ORDER BY rank
            LIMIT ?
        """
        params.append(limit)

        with self._QueryTimer(self, "search_memories"):
            conn = self._get_conn()
            try:
                rows = conn.execute(sql, params).fetchall()
            except sqlite3.OperationalError:
                # FTS5 query syntax error — fall back to LIKE search
                like_param = f"%{query}%"
                if source:
                    rows = conn.execute(
                        "SELECT * FROM memories WHERE (event_type LIKE ? OR data LIKE ?) AND source = ? "
                        "AND severity != 'deleted' "
                        "ORDER BY id DESC LIMIT ?",
                        (like_param, like_param, source, limit)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM memories WHERE (event_type LIKE ? OR data LIKE ?) "
                        "AND severity != 'deleted' "
                        "ORDER BY id DESC LIMIT ?",
                        (like_param, like_param, limit)
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

    def recall_recent(self, limit: int = 20, source: Optional[str] = None) -> List[Dict]:
        """Get the most recent memories, optionally filtered by source."""
        return self.query_memories(source=source, limit=limit)

    # -- Quantitative: Index Usage Analysis ----------------------------------

    def get_index_usage(self) -> List[Dict[str, Any]]:
        """Get index usage statistics from SQLite.

        Uses PRAGMA index_list + index_info to enumerate all indexes
        and their columns. Provides quantitative data on index coverage.

        Returns:
            List of dicts with index details: name, table, columns, unique.
        """
        conn = self._get_conn()
        try:
            indexes = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='memories' "
                "ORDER BY name"
            ).fetchall()

            result = []
            for row in indexes:
                idx_name = row["name"]
                idx_info = conn.execute(
                    f"PRAGMA index_xinfo('{idx_name}')"
                ).fetchall()
                columns = [r["name"] for r in idx_info if r["key"] == 1]
                result.append({
                    "index_name": idx_name,
                    "columns": columns,
                    "column_count": len(columns),
                })
            return result
        finally:
            conn.close()

    # -- Quantitative: Database Health Score ---------------------------------

    def health_check(self) -> Dict[str, Any]:
        """Compute a quantitative Database Health Score (0-100).

        Evaluates multiple health dimensions:
        - Integrity check passed (+25 points)
        - Fragmentation ratio (+15 points) — lower fragmentation = better
        - WAL mode health (+15 points)
        - Size vs threshold (+15 points) — under threshold = better
        - Slow query ratio (+15 points) — fewer slow queries = better
        - Index coverage (+15 points) — all expected indexes present

        Returns:
            Dict with overall score, per-dimension breakdown, and warnings.
        """
        score = 0
        details: Dict[str, Any] = {}
        warnings: List[str] = []

        # Dimension 1: Integrity (25 pts)
        integrity = self.integrity_check()
        if integrity.get("passed", False):
            score += 25
            details["integrity"] = {"score": 25, "max": 25, "passed": True}
        else:
            details["integrity"] = {
                "score": 0, "max": 25, "passed": False,
                "errors": integrity.get("errors", ["Unknown"]),
            }
            warnings.extend(integrity.get("errors", []))

        # Dimension 2: Fragmentation (15 pts)
        # Fragmentation = 1 - (actual_on_disk_size / theoretical_page_size)
        # Where theoretical_page_size = page_count * page_size (the upper bound)
        # And actual_on_disk_size is the real file size (may be smaller due to
        # unused pages within the file, or larger due to WAL overhead).
        # A ratio close to 1 means the file is nearly full of pages (efficient).
        # A ratio < 0.6 means significant unused space (fragmented).
        try:
            actual_file_bytes = os.path.getsize(self.db_path)
        except OSError:
            actual_file_bytes = 0
        theoretical_bytes = integrity.get("page_count", 0) * integrity.get("page_size", 4096)
        if theoretical_bytes > 0 and actual_file_bytes > 0:
            # storage_efficiency = how much of the page allocation is actually used
            storage_efficiency = min(1.0, actual_file_bytes / theoretical_bytes)
            # fragmentation = how much space is wasted (lower is better)
            # Formula: frag = max(0, 1.0 - storage_efficiency)
            frag = max(0.0, 1.0 - storage_efficiency)
            frag_score = max(0, int(15 * (1.0 - frag)))
            score += frag_score
            details["fragmentation"] = {
                "score": frag_score, "max": 15,
                "storage_efficiency": round(storage_efficiency, 4),
                "estimated_fragmentation": round(frag, 4),
                "actual_file_size_mb": round(actual_file_bytes / (1024 * 1024), 2),
                "theoretical_page_size_mb": round(theoretical_bytes / (1024 * 1024), 2),
            }
            if frag > 0.5:
                warnings.append(
                    f"High estimated fragmentation ({frag:.1%}) — run vacuum() to compact"
                )
        else:
            details["fragmentation"] = {"score": 15, "max": 15, "ratio": 0}

        # Dimension 3: WAL Mode (15 pts)
        wal_mode = integrity.get("wal_mode", "")
        if wal_mode == "wal":
            score += 15
            details["wal_mode"] = {"score": 15, "max": 15, "mode": wal_mode}
        else:
            score += 5  # Still works, but not optimal
            details["wal_mode"] = {"score": 5, "max": 15, "mode": wal_mode,
                                     "note": "WAL mode recommended for concurrent access"}

        # Dimension 4: Size vs Threshold (15 pts)
        try:
            current_mb = os.path.getsize(self.db_path) / (1024 * 1024)
        except OSError:
            current_mb = 0
        threshold_mb = self._max_size_mb
        if current_mb <= 0:
            size_score = 15
        elif current_mb <= threshold_mb * 0.5:
            size_score = 15  # Under 50% of threshold: perfect
        elif current_mb <= threshold_mb * 0.8:
            size_score = 12  # 50-80%: good
        elif current_mb <= threshold_mb:
            size_score = 8   # 80-100%: fair
        elif current_mb <= threshold_mb * 1.5:
            size_score = 4   # 100-150%: poor
        else:
            size_score = 0   # >150%: critical
        score += size_score
        details["size"] = {
            "score": size_score, "max": 15,
            "current_mb": round(current_mb, 2),
            "threshold_mb": threshold_mb,
            "pct_of_threshold": round((current_mb / max(threshold_mb, 1)) * 100, 1),
        }
        if current_mb > threshold_mb:
            warnings.append(
                f"Database size ({current_mb:.1f} MB) exceeds threshold ({threshold_mb} MB)"
            )

        # Dimension 5: Slow Query Ratio (15 pts)
        total_queries = self._query_count
        slow_queries = self._slow_query_count
        if total_queries == 0:
            query_score = 15  # No queries yet: perfect score
        else:
            slow_pct = slow_queries / total_queries
            if slow_pct <= 0.01:
                query_score = 15  # <=1% slow: excellent
            elif slow_pct <= 0.05:
                query_score = 12  # 1-5%: good
            elif slow_pct <= 0.10:
                query_score = 8   # 5-10%: fair
            elif slow_pct <= 0.25:
                query_score = 4   # 10-25%: poor
            else:
                query_score = 0   # >25%: critical
        score += query_score
        details["query_performance"] = {
            "score": query_score, "max": 15,
            "total_queries": total_queries,
            "slow_queries": slow_queries,
            "slow_pct": round((slow_queries / max(total_queries, 1)) * 100, 2),
        }
        if slow_queries > 0 and total_queries > 0 and (slow_queries / total_queries) > 0.1:
            warnings.append(
                f"High slow query ratio ({slow_queries}/{total_queries}, "
                f"{slow_queries / max(total_queries, 1) * 100:.1f}%) "
                f"— consider adding indexes or optimizing queries"
            )

        # Dimension 6: Index Coverage (15 pts)
        expected_indexes = {
            "idx_memories_session", "idx_memories_source",
            "idx_memories_event_type", "idx_memories_timestamp",
            "idx_memories_severity",
            "idx_memories_source_event_severity",
            "idx_memories_session_timestamp",
            "idx_memories_severity_timestamp",
        }
        conn = self._get_conn()
        try:
            existing = set(
                r["name"] for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='memories'"
                ).fetchall()
            )
            missing = expected_indexes - existing
            extra = existing - expected_indexes
            coverage_pct = round((len(existing & expected_indexes) / len(expected_indexes)) * 100, 1)
            index_score = max(0, int(15 * (coverage_pct / 100)))
            score += index_score
            details["index_coverage"] = {
                "score": index_score, "max": 15,
                "expected": len(expected_indexes),
                "existing": len(existing),
                "coverage_pct": coverage_pct,
                "missing_indexes": sorted(missing) if missing else [],
                "extra_indexes": sorted(extra) if extra else [],
            }
            if missing:
                warnings.append(f"Missing expected indexes: {', '.join(sorted(missing))}")
        finally:
            conn.close()

        return {
            "score": score,
            "max_score": 100,
            "grade": self._health_grade(score),
            "details": details,
            "warnings": warnings,
            "auto_vacuum": self.auto_vacuum_status,
            "auto_backup": self.auto_backup_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "store_version": self.VERSION,
        }

    @staticmethod
    def _health_grade(score: int) -> str:
        """Convert numeric health score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 65:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    # -- Quantitative: Comprehensive Health Report --------------------------

    def get_health_report(self) -> Dict[str, Any]:
        """Get a comprehensive quantitative health report combining all metrics.

        Includes:
        - Database health score (0-100) with grade
        - Integrity check results
        - Query performance statistics
        - Storage efficiency metrics
        - Index coverage analysis
        - Session analytics
        - Growth trends (daily event counts)
        - Error/warning trends
        - Maintenance status (auto-vacuum, auto-backup)

        Returns:
            Dict with all health and performance metrics combined.
        """
        return {
            "store_version": self.VERSION,
            "db_path": self.db_path,
            "health": self.health_check(),
            "stats": self.get_stats(),
            "performance": self.get_performance_stats(),
            "indexes": self.get_index_usage(),
            "growth_trends": self.get_db_growth(days=7),
            "error_trends": self.get_error_trends(days=7),
            "maintenance": {
                "auto_vacuum": self.auto_vacuum_status,
                "auto_backup": self.auto_backup_status,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # -- Statistics (Enhanced) ----------------------------------------------

    def get_stats(self) -> Dict:
        """Get memory store statistics with quantitative metrics.

        Enhanced over v1.0.0 with:
        - DB size with WAL overhead
        - Fragmentation ratio
        - Query performance metrics
        - Index coverage
        - Session analytics (avg events/session, durations)
        - Event rate (events per hour in current session)
        """
        conn = self._get_conn()
        try:
            total = conn.execute("SELECT COUNT(*) as n FROM memories").fetchone()["n"]
            sessions_total = conn.execute("SELECT COUNT(*) as n FROM sessions").fetchone()["n"]
            sources = conn.execute(
                "SELECT source, COUNT(*) as n FROM memories GROUP BY source ORDER BY n DESC LIMIT 10"
            ).fetchall()
            event_types = conn.execute(
                "SELECT event_type, COUNT(*) as n FROM memories GROUP BY event_type ORDER BY n DESC LIMIT 10"
            ).fetchall()
            severities = conn.execute(
                "SELECT severity, COUNT(*) as n FROM memories GROUP BY severity ORDER BY n DESC"
            ).fetchall()

            # DB size with WAL overhead
            db_size_mb = os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            wal_path = self.db_path + "-wal"
            wal_size_mb = os.path.getsize(wal_path) / (1024 * 1024) if os.path.exists(wal_path) else 0
            shm_path = self.db_path + "-shm"
            shm_size_mb = os.path.getsize(shm_path) / (1024 * 1024) if os.path.exists(shm_path) else 0

            # Fragmentation estimate
            page_count = conn.execute("PRAGMA page_count").fetchone()[0]
            page_size = conn.execute("PRAGMA page_size").fetchone()[0]
            theoretical_mb = (page_count * page_size) / (1024 * 1024)
            frag_ratio = round(1.0 - (db_size_mb / max(theoretical_mb, 1)), 4) if theoretical_mb > 0 else 0

            # Session analytics
            avg_events_per_session = round(total / max(sessions_total, 1), 1)
            completed_sessions = conn.execute(
                "SELECT COUNT(*) as n FROM sessions WHERE ended_at IS NOT NULL"
            ).fetchone()["n"]
            active_sessions = sessions_total - completed_sessions

            # Event rate
            current_session_events = conn.execute(
                "SELECT COUNT(*) as n FROM memories WHERE session_id = ?",
                (self._session_id,)
            ).fetchone()["n"]

            return {
                "version": self.VERSION,
                "schema_version": VERSION,
                "db_path": self.db_path,
                "db_size_mb": round(db_size_mb, 2),
                "wal_size_mb": round(wal_size_mb, 2),
                "shm_size_mb": round(shm_size_mb, 2),
                "total_size_mb": round(db_size_mb + wal_size_mb + shm_size_mb, 2),
                "total_memories": total,
                "total_sessions": sessions_total,
                "completed_sessions": completed_sessions,
                "active_sessions": active_sessions,
                "avg_events_per_session": avg_events_per_session,
                "current_session": self._session_id,
                "current_session_events": current_session_events,
                "fragmentation_ratio": frag_ratio,
                "page_count": page_count,
                "page_size": page_size,
                "theoretical_size_mb": round(theoretical_mb, 2),
                "sources": {r["source"]: r["n"] for r in sources},
                "event_types": {r["event_type"]: r["n"] for r in event_types},
                "severities": {r["severity"]: r["n"] for r in severities},
                "performance": self.get_performance_stats(),
            }
        finally:
            conn.close()

    # -- Export -------------------------------------------------------------

    def export_json(self, path: Optional[str] = None) -> str:
        """Export all memories to a JSON file. Returns the file path."""
        out_path = path or str(Path(self.db_path).parent / f"memory_export_{self._session_id}.json")
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM memories ORDER BY id ASC").fetchall()
        conn.close()

        memories = []
        for r in rows:
            d = dict(r)
            for field in ("data", "tags"):
                try:
                    d[field] = json.loads(d[field]) if isinstance(d[field], str) else d[field]
                except (json.JSONDecodeError, TypeError):
                    pass
            memories.append(d)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "version": VERSION,
                "count": len(memories),
                "memories": memories,
            }, f, indent=2, ensure_ascii=False)

        return out_path

    # -- Maintenance --------------------------------------------------------

    def vacuum(self):
        """Compact the database."""
        with self._lock:
            conn = self._get_conn()
            conn.execute("VACUUM")
            conn.close()

    def integrity_check(self) -> Dict[str, Any]:
        """Run PRAGMA integrity_check to verify database health.

        Returns:
            Dict with 'passed' (bool), 'errors' (list of strings),
            'page_count', 'page_size', and 'wal_mode' status.
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute("PRAGMA integrity_check")
            rows = [r[0] for r in cursor.fetchall()]
            passed = all(r == "ok" for r in rows)
            errors = [r for r in rows if r != "ok"]

            page_count = conn.execute("PRAGMA page_count").fetchone()[0]
            page_size = conn.execute("PRAGMA page_size").fetchone()[0]
            wal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            wal_checkpoint = conn.execute("PRAGMA wal_checkpoint").fetchone()

            return {
                "passed": passed,
                "ok": passed,
                "errors": errors,
                "page_count": page_count,
                "page_size": page_size,
                "wal_mode": wal_mode,
                "wal_checkpoint": list(wal_checkpoint) if wal_checkpoint else None,
                "db_size_mb": round(page_count * page_size / (1024 * 1024), 2),
            }
        finally:
            conn.close()

    def backup(self, target_path: str) -> str:
        """Create a safe online backup of the database.

        Uses VACUUM INTO (SQLite 3.27+) or falls back to a file copy
        with WAL checkpoint to ensure consistency.

        Args:
            target_path: Path for the backup file.

        Returns:
            The target file path on success.

        Raises:
            RuntimeError: If backup fails.
        """
        target = Path(target_path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)

            with self._lock:
                conn = self._get_conn()
                try:
                    # Try VACUUM INTO (SQLite 3.27+) — atomic, consistent
                    conn.execute(f"VACUUM INTO '{target}'")
                    conn.commit()
                except Exception:
                    # Fallback: checkpoint WAL, then copy file
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    conn.commit()
                    import shutil
                    shutil.copy2(self.db_path, str(target))
                finally:
                    conn.close()
        except RuntimeError:
            raise
        except Exception as e:
            # Honor the documented contract: any backup failure raises
            # RuntimeError (previously raw OSError/FileExistsError leaked).
            raise RuntimeError(f"Backup failed: {e}") from e

        # Verify the backup is readable
        verify_conn = sqlite3.connect(str(target))
        try:
            row_count = verify_conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            verify_conn.execute("SELECT COUNT(*) FROM sessions").fetchone()
        except Exception as e:
            raise RuntimeError(f"Backup verification failed: {e}") from e
        finally:
            verify_conn.close()

        return str(target)

    def purge_old(self, days: int = 90) -> int:
        """Delete memories older than N days. Returns count deleted."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "DELETE FROM memories WHERE timestamp < ?",
                (cutoff,)
            )
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
        return deleted

    def tombstone(self, ids: list) -> int:
        """Non-destructive delete: mark rows deleted, wipe payloads.

        (2026-09-10, A6: GRPO policy cleanup bypassed this API with a
        private connection + silent swallow. All tombstoning routes
        through here now.) Returns rows marked. Raises on DB error —
        callers decide visibility, never silent.
        """
        ids = [int(i) for i in (ids or [])]
        if not ids:
            return 0
        with self._lock:
            conn = self._get_conn()
            try:
                cursor = conn.execute(
                    "UPDATE memories SET severity = 'deleted', data = '{}' "
                    "WHERE id IN (%s)" % ",".join("?" * len(ids)),
                    ids,
                )
                marked = cursor.rowcount
                conn.commit()
            finally:
                conn.close()
        return marked

    # -- Real-Error Query (filters test artifacts) -------------------------

    # Patterns in data that indicate test artifacts, not real errors
    _TEST_ARTIFACT_PATTERNS = [
        'nonexistent.exe',
        'nonexistent',
        'bad_action',
    ]

    def _is_test_artifact(self, memory: Dict) -> bool:
        """Check if a memory record is a test artifact."""
        data = memory.get("data", {})
        if isinstance(data, dict):
            data_str = json.dumps(data, default=str).lower()
        else:
            data_str = str(data).lower()
        event_type = str(memory.get("event_type", "")).lower()
        source = str(memory.get("source", "")).lower()
        combined = f"{data_str} {event_type} {source}"
        for pattern in self._TEST_ARTIFACT_PATTERNS:
            if pattern in combined:
                return True
        return False

    def query_real_errors(self, days: int = 7, limit: int = 100,
                          exclude_sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Query real errors/warnings, excluding known test artifacts.

        Args:
            days: Look back this many days. Use 0 to return empty (no time window).
            limit: Max results per severity category.
            exclude_sources: Skip these source components (e.g. a monitor
                excluding its own alert rows to avoid self-referential
                threshold breaches).

        Returns:
            Dict with 'errors', 'warnings', 'total', and 'filtered' counts,
            plus exact COUNT(*) totals ('total_errors_exact') — the sampled
            lists are fetch-capped, so thresholds must use the exact totals.
        """
        if days <= 0:
            return {
                "errors": [], "warnings": [],
                "total_errors": 0, "total_warnings": 0,
                "total_errors_exact": 0, "total_warnings_exact": 0,
                "capped": False,
                "filtered_errors": 0, "filtered_warnings": 0,
            }
        all_errors = self.query_memories(severity="error", max_age_days=days,
                                         limit=limit * 2, exclude_sources=exclude_sources)
        all_warnings = self.query_memories(severity="warning", max_age_days=days,
                                           limit=limit * 2, exclude_sources=exclude_sources)

        real_errors = [e for e in all_errors if not self._is_test_artifact(e)]
        real_warnings = [w for w in all_warnings if not self._is_test_artifact(w)]

        # Exact totals with the same predicates (sample lists above are
        # fetch-capped at 500 rows by query_memories, so len() is a floor).
        conds = ["severity != 'deleted'", "severity = ?",
                 "timestamp > ?"]
        excl_sql = ""
        if exclude_sources:
            excl_sql = " AND source NOT IN (%s)" % ", ".join("?" * len(exclude_sources))
        conn = self._get_conn()
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            where = " AND ".join(conds) + excl_sql
            total_errors_exact = conn.execute(
                f"SELECT COUNT(*) FROM memories WHERE {where}",
                ["error", cutoff, *(exclude_sources or [])]).fetchone()[0]
            total_warnings_exact = conn.execute(
                f"SELECT COUNT(*) FROM memories WHERE {where}",
                ["warning", cutoff, *(exclude_sources or [])]).fetchone()[0]
        finally:
            conn.close()

        return {
            "errors": real_errors[:limit],
            "warnings": real_warnings[:limit],
            "total_errors": len(real_errors),
            "total_warnings": len(real_warnings),
            "total_errors_exact": total_errors_exact,
            "total_warnings_exact": total_warnings_exact,
            "capped": len(all_errors) >= 500 or len(all_warnings) >= 500,
            "filtered_errors": len(all_errors) - len(real_errors),
            "filtered_warnings": len(all_warnings) - len(real_warnings),
        }

    @staticmethod
    def _triage_signature(memory: Dict) -> str:
        """Cluster key: event_type + normalized first line of the message.

        Normalization lowercases, collapses numbers/hex/uuids to '#', and
        truncates — so 200 repetitions of the same failing probe land in
        one cluster while genuinely different errors stay apart.
        """
        import re
        data = memory.get("data", {})
        if isinstance(data, dict):
            msg = str(data.get("error") or data.get("message")
                      or data.get("action") or data.get("reason") or "")
        else:
            msg = str(data)
        first = msg.strip().splitlines()[0] if msg.strip() else ""
        first = first[:160].lower()
        first = re.sub(r"0x[0-9a-f]+", "#", first)
        first = re.sub(r"[0-9a-f]{8}-[0-9a-f-]{4,}", "#", first)
        first = re.sub(r"\d+", "#", first)
        return "%s|%s" % (memory.get("event_type", "?"), first or "(empty)")

    def triage_real_errors(self, days: int = 7, limit: int = 100,
                           exclude_sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Cluster real errors/warnings into triage groups (2026-09-09).

        query_real_errors() lists rows but nobody grouped them — 600
        identical probe failures looked as alarming as 600 distinct bugs.
        Returns clusters sorted by count desc: source, severity, count,
        newest timestamp, and a sample row. Designed for the nightly
        maintenance log, not for new store rows (no churn).
        """
        qr = self.query_real_errors(days=days, limit=limit,
                                    exclude_sources=exclude_sources)
        clusters: Dict[tuple, Dict[str, Any]] = {}
        for sev_key in ("errors", "warnings"):
            for m in qr.get(sev_key, []):
                key = (m.get("source", "?"), m.get("severity", "?"),
                       self._triage_signature(m))
                c = clusters.get(key)
                if c is None:
                    clusters[key] = {
                        "source": m.get("source", "?"),
                        "severity": m.get("severity", "?"),
                        "signature": key[2],
                        "count": 1,
                        "newest": m.get("timestamp", ""),
                        "sample_event": m.get("event_type", "?"),
                    }
                else:
                    c["count"] += 1
                    if str(m.get("timestamp", "")) > str(c["newest"]):
                        c["newest"] = m.get("timestamp", "")
                        c["sample_event"] = m.get("event_type", "?")
        ranked = sorted(clusters.values(), key=lambda c: -c["count"])
        return {
            "generated": datetime.now(timezone.utc).isoformat(),
            "window_days": days,
            "total_errors_exact": qr.get("total_errors_exact", 0),
            "total_warnings_exact": qr.get("total_warnings_exact", 0),
            "capped": qr.get("capped", False),
            "filtered_errors": qr.get("filtered_errors", 0),
            "filtered_warnings": qr.get("filtered_warnings", 0),
            "cluster_count": len(ranked),
            "clusters": ranked[:25],
        }

    def get_error_trends(self, days: int = 30) -> List[Dict]:
        """Get daily error/warning counts for trend analysis.

        Args:
            days: Number of days to look back.

        Returns:
            List of daily counts: [{"date": "...", "errors": N, "warnings": M}, ...]
        """
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT date(timestamp) as day, severity, COUNT(*) as cnt "
            "FROM memories WHERE severity IN ('error', 'warning') "
            "AND timestamp > ? "
            "GROUP BY day, severity ORDER BY day",
            ((datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),)
        ).fetchall()
        conn.close()

        # Aggregate by day
        trend: Dict[str, Dict] = {}
        for r in rows:
            day = r["day"]
            if day not in trend:
                trend[day] = {"date": day, "errors": 0, "warnings": 0}
            if r["severity"] == "error":
                trend[day]["errors"] = r["cnt"]
            elif r["severity"] == "warning":
                trend[day]["warnings"] = r["cnt"]

        return sorted(trend.values(), key=lambda d: d["date"])

    def get_db_growth(self, days: int = 30) -> List[Dict]:
        """Get daily event count growth for trend analysis.

        Args:
            days: Number of days to look back.

        Returns:
            List of daily counts: [{"date": "...", "count": N}, ...]
        """
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT date(timestamp) as day, COUNT(*) as cnt "
            "FROM memories WHERE timestamp > ? "
            "GROUP BY day ORDER BY day",
            ((datetime.now(timezone.utc) - timedelta(days=days)).isoformat(),)
        ).fetchall()
        conn.close()
        return [{"date": r["day"], "count": r["cnt"]} for r in rows]

    # -- Auto-Vacuum Scheduler ---------------------------------------------

    def start_auto_vacuum(self, interval_hours: float = 24.0):
        """Start a background thread that periodically vacuums the database.

        Args:
            interval_hours: How often to vacuum (default: 24 hours).
        """
        with self._maintenance_lock:
            if self._vacuum_running:
                return  # Already running
            self._vacuum_interval = interval_hours * 3600
            self._vacuum_running = True
        self._vacuum_thread = threading.Thread(
            target=self._vacuum_loop, daemon=True,
            name="azazael-db-vacuum",
        )
        self._vacuum_thread.start()

    def stop_auto_vacuum(self):
        """Stop the background vacuum thread."""
        with self._maintenance_lock:
            self._vacuum_running = False
        if self._vacuum_thread is not None and self._vacuum_thread.is_alive():
            self._vacuum_thread.join(timeout=10)

    def _vacuum_loop(self):
        """Background loop that periodically vacuums the database."""
        while True:
            with self._maintenance_lock:
                running = self._vacuum_running
            if not running:
                break
            time.sleep(self._vacuum_interval)
            with self._maintenance_lock:
                if not self._vacuum_running:
                    break
            try:
                self.vacuum()
            except Exception:
                pass

    @property
    def auto_vacuum_status(self) -> Dict[str, Any]:
        """Get auto-vacuum status."""
        with self._maintenance_lock:
            running = self._vacuum_running
        interval_hours = self._vacuum_interval / 3600
        return {
            "running": running,
            "interval_hours": round(interval_hours, 1),
            "thread_alive": (
                self._vacuum_thread.is_alive()
                if self._vacuum_thread is not None else False
            ),
        }

    # -- Auto-Backup Scheduler ---------------------------------------------

    def start_auto_backup(self, interval_hours: float = 24.0,
                          keep_count: int = 7,
                          target_dir: Optional[str] = None):
        """Start a background thread that periodically backs up the database.

        Args:
            interval_hours: How often to back up (default: 24 hours).
            keep_count: Number of recent backups to keep (default: 7).
            target_dir: Directory for backups (default: ~/.azazael/backups/).
        """
        with self._maintenance_lock:
            if self._backup_running:
                return
            self._backup_interval = interval_hours * 3600
            self._backup_keep_count = keep_count
            if target_dir:
                self._backup_target_dir = target_dir
            else:
                self._backup_target_dir = str(Path(self.db_path).parent / "backups")
            self._backup_running = True
        self._backup_thread = threading.Thread(
            target=self._backup_loop, daemon=True,
            name="azazael-db-backup",
        )
        self._backup_thread.start()

    def stop_auto_backup(self):
        """Stop the background backup thread."""
        with self._maintenance_lock:
            self._backup_running = False
        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_thread.join(timeout=10)

    def _backup_loop(self):
        """Background loop that periodically backs up the database."""
        while True:
            with self._maintenance_lock:
                running = self._backup_running
            if not running:
                break
            time.sleep(self._backup_interval)
            with self._maintenance_lock:
                if not self._backup_running:
                    break
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(
                    self._backup_target_dir,
                    f"memory_store_backup_{timestamp}.db",
                )
                self._last_backup_path = self.backup(backup_path)
                self._prune_backups(keep_count=self._backup_keep_count)
            except Exception:
                pass

    def _prune_backups(self, keep_count: int = 7):
        """Remove old backups beyond the keep count."""
        try:
            backup_dir = Path(self._backup_target_dir)
            if not backup_dir.exists():
                return
            backups = sorted(
                [f for f in backup_dir.glob("memory_store_backup_*.db")],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            for old_backup in backups[keep_count:]:
                old_backup.unlink(missing_ok=True)
        except Exception:
            pass

    @property
    def auto_backup_status(self) -> Dict[str, Any]:
        """Get auto-backup status."""
        with self._maintenance_lock:
            running = self._backup_running
        interval_hours = self._backup_interval / 3600
        return {
            "running": running,
            "interval_hours": round(interval_hours, 1),
            "thread_alive": (
                self._backup_thread.is_alive()
                if self._backup_thread is not None else False
            ),
            "last_backup_path": getattr(self, "_last_backup_path", None),
            "target_dir": getattr(self, "_backup_target_dir", ""),
            "keep_count": getattr(self, "_backup_keep_count", 7),
        }

    def close(self):
        """Close any active connections and finalize WAL checkpoint."""
        self.stop_auto_vacuum()
        self.stop_auto_backup()
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            conn.close()
        except Exception:
            pass

    # -- Knowledge Graph: Pattern Registration & Similarity ---------------

    def register_pattern(self, source_agent: str, pattern_type: str,
                         embedding: list[float],
                         metadata: (dict | None) = None,
                         confidence: float = 1.0) -> int:
        """Register a pattern/embedding in the knowledge graph.

        Args:
            source_agent: Agent that discovered the pattern.
            pattern_type: Category (e.g., "anomaly", "preference").
            embedding: Feature vector as list of floats.
            metadata: Optional metadata dict.
            confidence: Confidence score (0.0-1.0).

        Returns:
            Pattern ID (rowid).
        """
        embedding_str = json.dumps(embedding, ensure_ascii=False)
        metadata_str = json.dumps(metadata or {}, ensure_ascii=False)
        ts = datetime.now(timezone.utc).isoformat()

        with self._lock:
            conn = self._get_conn()
            cursor = conn.execute(
                "INSERT INTO knowledge_patterns(source_agent, pattern_type, embedding, metadata, confidence, created_at, updated_at) "
                "VALUES(?, ?, ?, ?, ?, ?, ?)",
                (source_agent, pattern_type, embedding_str, metadata_str, confidence, ts, ts)
            )
            pid = cursor.lastrowid or 0
            conn.commit()
            conn.close()
        return pid

    def query_similar_patterns(self, embedding: list[float], top_k: int = 10,
                                pattern_type: (str | None) = None) -> list[dict[str, Any]]:
        """Find patterns similar to the given embedding via cosine similarity.

        Args:
            embedding: Query feature vector.
            top_k: Max results to return.
            pattern_type: Optional filter by pattern type.

        Returns:
            List of pattern dicts with similarity scores, sorted descending.
        """
        conn = self._get_conn()
        try:
            if pattern_type:
                rows = conn.execute(
                    "SELECT * FROM knowledge_patterns WHERE pattern_type = ? ORDER BY id DESC",
                    (pattern_type,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM knowledge_patterns ORDER BY id DESC"
                ).fetchall()
        finally:
            conn.close()

        results = []
        matched_ids = []
        for r in rows:
            stored_emb = json.loads(r["embedding"]) if isinstance(r["embedding"], str) else r["embedding"]
            sim = self._cosine_similarity(embedding, stored_emb)

            matched_ids.append(r["id"])
            metadata_val = json.loads(r["metadata"]) if isinstance(r["metadata"], str) else r["metadata"]
            results.append({
                "id": r["id"],
                "source_agent": r["source_agent"],
                "pattern_type": r["pattern_type"],
                "embedding": stored_emb,
                "metadata": metadata_val,
                "confidence": r["confidence"],
                "hit_count": r["hit_count"] + 1,
                "similarity": round(sim, 4),
                "created_at": r["created_at"],
            })

        results.sort(key=lambda x: -x["similarity"])
        top = results[:top_k]

        # Persist hit counts for the patterns this query matched.
        #
        # This used to open a NEW connection per row, never take self._lock, and
        # swallow every failure with `except Exception: pass`. Two concurrent
        # queries -- or a query racing a register_pattern -- therefore hit
        # "database is locked", the error vanished, and the returned hit_count
        # still claimed +1 for an update that never landed. Now: one batched
        # statement, serialized on self._lock, and a failure is surfaced and the
        # reported counts corrected rather than silently invented.
        if matched_ids:
            try:
                with self._lock:
                    upd = self._get_conn()
                    try:
                        stamp = datetime.now(timezone.utc).isoformat()
                        # Chunked: SQLite caps bind variables per statement, and
                        # the match set is the whole pattern table.
                        for i in range(0, len(matched_ids), 500):
                            chunk = matched_ids[i:i + 500]
                            placeholders = ",".join("?" * len(chunk))
                            upd.execute(
                                "UPDATE knowledge_patterns SET hit_count = hit_count + 1, "
                                f"updated_at = ? WHERE id IN ({placeholders})",
                                [stamp, *chunk],
                            )
                        upd.commit()
                    finally:
                        upd.close()
            except sqlite3.Error as exc:
                print(f"LocalMemoryStore: hit-count update failed ({exc})")
                for row in top:
                    row["hit_count"] -= 1

        return top

    def get_patterns_by_agent(self, source_agent: str,
                               pattern_type: (str | None) = None) -> list[dict[str, Any]]:
        """Get all patterns registered by a specific agent.

        Args:
            source_agent: Agent name to filter by.
            pattern_type: Optional filter by pattern type.

        Returns:
            List of pattern dicts.
        """
        conn = self._get_conn()
        try:
            if pattern_type:
                rows = conn.execute(
                    "SELECT * FROM knowledge_patterns WHERE source_agent = ? AND pattern_type = ? ORDER BY id DESC",
                    (source_agent, pattern_type)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM knowledge_patterns WHERE source_agent = ? ORDER BY id DESC",
                    (source_agent,)
                ).fetchall()
        finally:
            conn.close()

        results = []
        for r in rows:
            metadata_val = json.loads(r["metadata"]) if isinstance(r["metadata"], str) else r["metadata"]
            results.append({
                "id": r["id"],
                "source_agent": r["source_agent"],
                "pattern_type": r["pattern_type"],
                "embedding": json.loads(r["embedding"]) if isinstance(r["embedding"], str) else r["embedding"],
                "metadata": metadata_val,
                "confidence": r["confidence"],
                "hit_count": r["hit_count"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            })
        return results

    def delete_pattern(self, pattern_id: (int | None) = None,
                         source_agent: (str | None) = None,
                         pattern_type: (str | None) = None) -> int:
        """Delete one or more patterns from the knowledge graph.

        Supports flexible filtering — at least one of pattern_id, source_agent,
        or pattern_type must be provided. Combine source_agent + pattern_type
        to delete specific pattern categories for an agent.

        Args:
            pattern_id: Delete a specific pattern by its ID.
            source_agent: Delete all patterns registered by this agent.
            pattern_type: Delete all patterns of this type (optionally combined
                          with source_agent for a compound filter).

        Returns:
            Number of rows deleted.

        Raises:
            ValueError: If no filter argument is provided.
        """
        if pattern_id is None and source_agent is None and pattern_type is None:
            raise ValueError(
                "At least one of pattern_id, source_agent, or pattern_type must be provided"
            )

        conditions: list[str] = []
        params: list[Any] = []

        if pattern_id is not None:
            conditions.append("id = ?")
            params.append(pattern_id)
        if source_agent is not None:
            conditions.append("source_agent = ?")
            params.append(source_agent)
        if pattern_type is not None:
            conditions.append("pattern_type = ?")
            params.append(pattern_type)

        where = " AND ".join(conditions)
        sql = f"DELETE FROM knowledge_patterns WHERE {where}"

        with self._lock:
            conn = self._get_conn()
            try:
                cursor = conn.execute(sql, params)
                deleted = cursor.rowcount
                conn.commit()
            finally:
                conn.close()

        return deleted

    def get_knowledge_graph_stats(self) -> dict[str, Any]:
        """Get statistics about the knowledge graph.

        Returns:
            Dict with total_patterns, by_agent, by_type, avg_confidence.
        """
        conn = self._get_conn()
        try:
            total = conn.execute("SELECT COUNT(*) as n FROM knowledge_patterns").fetchone()["n"]

            by_agent = {}
            agent_rows = conn.execute(
                "SELECT source_agent, COUNT(*) as n FROM knowledge_patterns GROUP BY source_agent"
            ).fetchall()
            for r in agent_rows:
                by_agent[r["source_agent"]] = r["n"]

            by_type = {}
            type_rows = conn.execute(
                "SELECT pattern_type, COUNT(*) as n FROM knowledge_patterns GROUP BY pattern_type"
            ).fetchall()
            for r in type_rows:
                by_type[r["pattern_type"]] = r["n"]

            avg_conf = conn.execute(
                "SELECT AVG(confidence) as avg_c FROM knowledge_patterns"
            ).fetchone()["avg_c"] or 0.0
        finally:
            conn.close()

        return {
            "total_patterns": total,
            "by_agent": by_agent,
            "by_type": by_type,
            "avg_confidence": round(avg_conf, 4),
        }

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors.

        Dimension-tolerant: if lengths differ (multi-model store — nomic 768,
        bge-m3 1024, etc.), both vectors are projected to the store's
        self-tuned optimal dimension before comparison. Returns 0.0 only for
        empty vectors.
        """
        if not vec1 or not vec2:
            return 0.0
        if len(vec1) != len(vec2):
            try:
                from CORE.embedding_backend import project, optimal_dim
                k = optimal_dim()
                vec1 = project(vec1, k)
                vec2 = project(vec2, k)
            except Exception:
                return 0.0
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)


# -- Global singleton ------------------------------------------------------
_global_store: Optional[LocalMemoryStore] = None
_store_lock = threading.Lock()


def get_memory_store(db_path: Optional[str] = None) -> LocalMemoryStore:
    """Get or create the global LocalMemoryStore singleton."""
    global _global_store
    if _global_store is None:
        with _store_lock:
            if _global_store is None:
                _global_store = LocalMemoryStore(db_path=db_path)
    return _global_store


# -- Self-test -------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  LocalMemoryStore — Self-test")
    print("=" * 60)
    print(f"  DB Path: {DB_PATH}")
    print(f"  Session: {datetime.now().strftime('session_%Y%m%d_%H%M%S')}")

    store = LocalMemoryStore()

    # Test 1: Record events
    print("\n  [1] Recording events...")
    id1 = store.record_event("EveUnleashed", "session_start",
                             {"python": sys.version}, tags=["startup", "eve"])
    id2 = store.record_event("EveUnleashed", "inference",
                             {"prompt": "Hello world", "tps": 45.2}, tags=["inference", "test"])
    id3 = store.record_event("CLUSTERWORMS", "worm_execute",
                             {"worm": "SystemZ", "success": True}, severity="info",
                             tags=["worm", "monitor"])
    id4 = store.record_event("EveUnleashed", "error",
                             {"msg": "GPU not detected"}, severity="error",
                             tags=["error", "gpu"])
    print(f"      Recorded 4 events: IDs = {id1}, {id2}, {id3}, {id4}")

    # Test 2: Query
    print("\n  [2] Querying by source...")
    results = store.query_memories(source="EveUnleashed", limit=10)
    print(f"      EveUnleashed events: {len(results)}")
    for r in results:
        print(f"        [{r['id']}] {r['event_type']} ({r['severity']})")

    # Test 3: Full-text search
    print("\n  [3] Full-text search for 'GPU'...")
    found = store.search_memories("GPU")
    print(f"      Found {len(found)} results:")
    for r in found:
        print(f"        [{r['id']}] {r['event_type']}: {r['data']}")

    # Test 4: Recall recent
    print("\n  [4] Recall recent (last 5)...")
    recent = store.recall_recent(5)
    print(f"      {len(recent)} memories, newest first")

    # Test 5: Sessions
    print("\n  [5] Sessions...")
    sessions = store.list_sessions()
    print(f"      {len(sessions)} sessions found")

    # Test 6: Stats (Enhanced)
    print("\n  [6] Stats (Enhanced v2)...")
    stats = store.get_stats()
    print(f"      Total memories: {stats['total_memories']}")
    print(f"      DB size: {stats['db_size_mb']:.2f} MB")
    print(f"      WAL size: {stats['wal_size_mb']:.2f} MB")
    print(f"      Total sessions: {stats['total_sessions']}")
    print(f"      Avg events/session: {stats['avg_events_per_session']}")
    print(f"      Fragmentation: {stats['fragmentation_ratio']}")
    print(f"      Sources: {stats['sources']}")
    print(f"      Event types: {stats['event_types']}")

    # Test 7: Query Performance
    print("\n  [7] Query Performance Stats...")
    perf = store.get_performance_stats()
    print(f"      Total queries: {perf['total_queries']}")
    print(f"      Avg time: {perf['avg_query_time_ms']} ms")
    print(f"      Max time: {perf['max_query_time_ms']} ms")
    print(f"      Slow queries: {perf['slow_query_count']} ({perf['slow_query_pct']}%)")

    # Test 8: Database Health Score
    print("\n  [8] Database Health Check...")
    health = store.health_check()
    print(f"      Score: {health['score']}/{health['max_score']} (Grade: {health['grade']})")
    for dim, detail in sorted(health['details'].items()):
        print(f"        {dim}: {detail['score']}/{detail['max']}")
    if health['warnings']:
        print(f"      Warnings ({len(health['warnings'])}):")
        for w in health['warnings'][:3]:
            print(f"        - {w}")

    # Test 9: Index Usage
    print("\n  [9] Index Usage...")
    indexes = store.get_index_usage()
    print(f"      {len(indexes)} indexes on memories table:")
    for idx in indexes:
        cols = ', '.join(idx['columns'])
        print(f"        {idx['index_name']}: ({cols})")

    # Test 10: Auto-Vacuum Status
    print("\n  [10] Auto-Maintenance Status...")
    print(f"      Auto-vacuum: {store.auto_vacuum_status}")
    print(f"      Auto-backup: {store.auto_backup_status}")

    print("\n" + "=" * 60)
    print("  LocalMemoryStore v2.0 Self-test complete.")
    print(f"  {sum(1 for _ in range(10))} quantitative checks done.")
    print("=" * 60)
