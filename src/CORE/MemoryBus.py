# coding: utf-8
"""
MemoryBus — PAMS-backed inter-agent pub/sub communication bus.

Provides a publish/subscribe messaging layer for the AZAZAEL multi-agent
ecosystem, backed by the PAMS memory server (port 21434 by default).

Features:
- publish(topic, message, metadata) -> stores to PAMS as a classified memory
- subscribe(topic, callback, pattern) -> polls PAMS for new topic messages
- poll(topic, since_id) -> query PAMS for messages since last check
- Wildcard topic matching (e.g., "agent.*.error")
- Thread-safe subscription registry
- Graceful degradation if PAMS is unreachable
- Optional local fallback queue for offline operation

CANONICAL SOURCE — import from here project-wide:
    from azazael.src.CORE.MemoryBus import MemoryBus

Usage:
    bus = MemoryBus()
    bus.publish("agent.status", {"agent_id": "agent-1", "status": "running"})
    bus.subscribe("agent.*", lambda msg: print(f"Got: {msg}"))
    messages = bus.poll("agent.status", since_id=0)
"""

import sys
import os
import threading
import json
import re
import sqlite3
import itertools
from CORE.uuid7 import uuid7
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Dict, List, Tuple
from collections import defaultdict

# -- Import CORE utilities ----------------------------------------------------
_azazael_src = str(Path(__file__).resolve().parent.parent)
if _azazael_src not in sys.path:
    sys.path.insert(0, _azazael_src)

try:
    from CORE.freethreading import is_free_threaded, ThreadSafeDict, ThreadSafeList
    HAS_FREETHREADING = True
except ImportError:
    HAS_FREETHREADING = False
    ThreadSafeDict: Any = dict  # type: ignore[no-redef]
    ThreadSafeList: Any = list  # type: ignore[no-redef]
    def is_free_threaded() -> bool:
        return hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled()

IS_FREE_THREADED = is_free_threaded()

# -- HTTP client for PAMS (requests preferred, urllib fallback) ---------------
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error

PAMS_URL = os.environ.get("PAMS_URL", "http://127.0.0.1:21434")
PAMS_TIMEOUT = float(os.environ.get("PAMS_TIMEOUT", "2.0"))

# -- F07 fix (June 7 2026): Persistent SQLite fallback queue --------
# When PAMS is unreachable, messages are persisted to memory_store.db
# instead of an ephemeral in-memory list. This prevents absolute data
# loss on process exit during PAMS downtime.
def _get_memorybus_db_path() -> Path:
    """Get the memory store DB path for persistent fallback queue."""
    env_dir = os.environ.get("AZAZAEL_MEMORY_DIR", "")
    if env_dir:
        base = Path(env_dir)
    else:
        base = Path.home() / ".azazael"
    base.mkdir(parents=True, exist_ok=True)
    return base / "memory_store.db"

_MEMORYBUS_DB_PATH = _get_memorybus_db_path()

_MEMORYBUS_QUEUE_SCHEMA = """
CREATE TABLE IF NOT EXISTS memorybus_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic       TEXT NOT NULL,
    content     TEXT NOT NULL,
    metadata    TEXT NOT NULL DEFAULT '{}',
    source      TEXT NOT NULL DEFAULT 'memorybus',
    session_id  TEXT NOT NULL,
    timestamp   TEXT NOT NULL,
    flushed     INTEGER NOT NULL DEFAULT 0,
    -- CD1 schema migration (June 11 2026): Cross-domain correlation fields
    -- See azazael/research/CROSS_DOMAIN.md §CD1 for unified event schema
    event_uuid      TEXT,
    trace_id        TEXT,
    correlation_id  TEXT
);
CREATE INDEX IF NOT EXISTS idx_mbqueue_flushed ON memorybus_queue(flushed, id);
-- idx_mbqueue_correlation created in _migrate_queue_schema() after ALTER TABLE
"""


@dataclass
class BusMessage:
    """A message published on the MemoryBus."""
    message_id: int = 0
    topic: str = ""
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    session_id: str = ""
    source: str = "memorybus"

    def to_dict(self) -> dict:
        return {
            'message_id': self.message_id,
            'topic': self.topic,
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'session_id': self.session_id,
            'source': self.source,
        }


class MemoryBus:
    """
    PAMS-backed publish/subscribe bus for inter-agent communication.

    Uses the PAMS REST API to store published messages as classified memories
    (category="memorybus", tags=[topic]) and polls for new messages by topic.

    Subscriptions use glob-style wildcard patterns:
        "agent.*.error" matches "agent.runtime.error", "agent.network.error"
        "*.status" matches "agent.status", "pool.status"
        "agent.>" matches "agent.status", "agent.error.detail" (prefix wildcard)
    """

    VERSION = "1.1.0"

    def __init__(self, pams_url: Optional[str] = None, session_id: Optional[str] = None,
                 poll_interval_sec: float = 1.0, use_local_fallback: bool = True):
        self.pams_url = (pams_url or PAMS_URL).rstrip('/')
        self.session_id = session_id or uuid7().hex[:8]
        self.poll_interval_sec = poll_interval_sec
        self.use_local_fallback = use_local_fallback

        # -- Subscription registry (thread-safe) --------------------------
        # {pattern: [(callback, compiled_regex), ...]}
        self._subscriptions: Dict[str, List[Tuple[Callable, re.Pattern]]] = defaultdict(list)
        self._sub_lock = threading.Lock()

        # -- Poll state (per-topic last seen ID) ---------------------------
        self._last_seen: Dict[str, int] = ThreadSafeDict()
        self._poll_lock = threading.Lock()

        # -- Local fallback queue (when PAMS is down) ----------------------
        # F07 fix (June 7 2026): In-memory queue is now backed by persistent
        # SQLite storage. Messages are written to memory_store.db when PAMS
        # is unreachable, preventing absolute data loss on process exit.
        self._local_queue: List[BusMessage] = []
        self._local_queue_lock = threading.Lock()
        self._persisted_ids: set = set()  # Track which messages were already persisted
        self._persistent_queue_initialized = False
        # P0 fix (June 11 2026): Atomic message_id counter using itertools.count
        self._message_counter = itertools.count(1)
        # CD1 correlation (June 11 2026): Cross-domain correlation ID
        self._correlation_id = uuid7().hex
        self._init_persistent_queue()

        # -- Stats (thread-safe: backing dict + dedicated lock) ----------
        self._stats_data: Dict[str, int] = {
            'published': 0,
            'delivered': 0,
            'polls': 0,
            'pams_errors': 0,
            'local_fallback_used': 0,
            'persistent_fallback_used': 0,
            'persistent_flushed': 0,
            'subscriptions': 0,
        }
        self._stats = ThreadSafeDict()  # Maintain backward compat for dynamic keys
        self._stats_lock = threading.Lock()

        # -- Check PAMS connectivity --------------------------------------
        self._pams_available = self._check_pams()

    def _init_persistent_queue(self):
        """Initialize the persistent SQLite queue for message durability."""
        if self._persistent_queue_initialized:
            return
        try:
            conn = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript(_MEMORYBUS_QUEUE_SCHEMA)
            conn.commit()
            # CD1 schema migration (June 11 2026): Add cross-domain columns
            self._migrate_queue_schema(conn)
            conn.close()
            self._persistent_queue_initialized = True
        except Exception:
            pass

    def _migrate_queue_schema(self, conn: sqlite3.Connection):
        """Run additive schema migrations for existing queue tables.

        CD1 (June 11 2026): Adds event_uuid and correlation_id columns
        to memorybus_queue if they don't exist.
        """
        existing_cols = set(
            r[1] for r in conn.execute("PRAGMA table_info('memorybus_queue')").fetchall()
        )
        migrations = [
            ("event_uuid", "TEXT"),
            ("trace_id", "TEXT"),
            ("correlation_id", "TEXT"),
        ]
        for col_name, col_type in migrations:
            if col_name not in existing_cols:
                conn.execute(
                    f"ALTER TABLE memorybus_queue ADD COLUMN {col_name} {col_type}"
                )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_mbqueue_correlation "
            "ON memorybus_queue(correlation_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_mbqueue_trace_id "
            "ON memorybus_queue(trace_id)"
        )
        # CD1 Phase 2 (June 11 2026): Backfill existing NULL rows with UUID7.
        # Batched in chunks of 1000 to avoid large transactions under 3.14t.
        while True:
            batch = conn.execute(
                "SELECT id FROM memorybus_queue WHERE event_uuid IS NULL LIMIT 1000"
            ).fetchall()
            if not batch:
                break
            for (row_id,) in batch:
                conn.execute(
                    "UPDATE memorybus_queue SET event_uuid = ? WHERE id = ?",
                    (uuid7().hex, row_id)
                )
            conn.commit()

    def _persist_to_queue(self, topic: str, content: Any, metadata: Dict,
                          source: str, event_uuid: str = "") -> int:
        """Persist a message to the SQLite fallback queue. Returns row ID."""
        if not self._persistent_queue_initialized:
            return 0
        try:
            conn = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
            conn.execute("PRAGMA journal_mode=WAL")
            corr_id = self._correlation_id
            cursor = conn.execute(
                "INSERT INTO memorybus_queue(topic,content,metadata,source,session_id,timestamp,"
                "event_uuid,trace_id,correlation_id) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (topic, json.dumps(content, default=str),
                 json.dumps(metadata, default=str), source,
                 self.session_id, datetime.now().isoformat(),
                 event_uuid or uuid7().hex, corr_id, corr_id)
            )
            row_id = cursor.lastrowid or 0
            conn.commit()
            conn.close()
            return row_id
        except Exception:
            self._increment('pams_errors')
            return 0

    # -- Public API ------------------------------------------------------------

    def publish(self, topic: str, content: Any, metadata: Optional[Dict[str, Any]] = None,
                source: str = "memorybus") -> Optional[int]:
        """
        Publish a message to a topic.

        Args:
            topic: The topic string (e.g., "agent.status", "pool.task.complete").
            content: The message payload (dict, string, or any JSON-serializable).
            metadata: Optional additional metadata.
            source: Identifier for the publishing component.

        Returns:
            Message ID from PAMS if successful, None if fallback-only.
        """
        metadata = metadata or {}
        metadata['topic'] = topic
        metadata['source'] = source

        # Serialize content
        if isinstance(content, (dict, list, str, int, float, bool)):
            payload = content
        else:
            payload = str(content)

        self._increment('published')

        if self._pams_available:
            try:
                msg_id = self._post_to_pams(topic, payload, metadata, source)
                if msg_id is not None:
                    with self._poll_lock:
                        self._last_seen[topic] = max(
                            self._last_seen.get(topic, 0), msg_id
                        )
                    return msg_id
            except Exception:
                self._increment('pams_errors')

        # -- Fallback: store locally + persist to SQLite -----------------
        if self.use_local_fallback:
            self._increment('local_fallback_used')
            # CD1 correlation (June 11 2026): UUID7 for cross-ledger linking
            ev_uuid = uuid7().hex
            msg = BusMessage(
                message_id=next(self._message_counter),
                topic=topic,
                content=payload,
                metadata=metadata,
                timestamp=datetime.now().isoformat(),
                session_id=self.session_id,
                source=source,
            )
            with self._local_queue_lock:
                self._local_queue.append(msg)
                if len(self._local_queue) > 1000:
                    self._local_queue = self._local_queue[-1000:]
            # F07 fix: Persist to SQLite for durability
            pid = self._persist_to_queue(topic, payload, metadata, source, ev_uuid)
            if pid:
                self._increment('persistent_fallback_used')
                self._persisted_ids.add(msg.message_id)
            return msg.message_id

        return None

    def subscribe(self, pattern: str, callback: Callable[[BusMessage], None]) -> int:
        """
        Subscribe to messages matching a topic pattern.

        Patterns use glob-style wildcards:
            "*" matches a single topic segment
            ">" matches one or more trailing segments (prefix wildcard)

        Examples:
            "agent.status" — exact match
            "agent.*.error" — single wildcard
            "pool.>" — prefix wildcard (matches pool.task, pool.status, etc.)

        Args:
            pattern: Topic pattern with wildcards.
            callback: Called with BusMessage when a matching message is published.

        Returns:
            Number of active subscriptions for this pattern.
        """
        compiled = self._compile_pattern(pattern)

        with self._sub_lock:
            self._subscriptions[pattern].append((callback, compiled))
            count = len(self._subscriptions[pattern])

        self._stats['subscriptions'] = sum(
            len(subs) for subs in self._subscriptions.values()
        )
        return count

    def unsubscribe(self, pattern: str, callback: Optional[Callable] = None) -> int:
        """
        Unsubscribe from a pattern.

        Args:
            pattern: The subscription pattern.
            callback: If provided, only remove this specific callback.
                      If None, remove all callbacks for this pattern.

        Returns:
            Number of remaining subscriptions for this pattern.
        """
        with self._sub_lock:
            if pattern not in self._subscriptions:
                return 0

            if callback is None:
                del self._subscriptions[pattern]
                count = 0
            else:
                self._subscriptions[pattern] = [
                    (cb, regex) for cb, regex in self._subscriptions[pattern]
                    if cb is not callback
                ]
                count = len(self._subscriptions[pattern])
                if count == 0:
                    del self._subscriptions[pattern]

        self._stats['subscriptions'] = sum(
            len(subs) for subs in self._subscriptions.values()
        )
        return count

    def poll(self, topic: Optional[str] = None, since_id: int = 0,
             limit: int = 20) -> List[BusMessage]:
        """
        Poll PAMS for messages since a given ID, optionally filtered by topic.

        Args:
            topic: Optional topic filter.
            since_id: Only return messages with ID > since_id.
            limit: Max messages to return.

        Returns:
            List of BusMessage objects.
        """
        self._increment('polls')

        messages = []

        # -- Check local fallback queue first -----------------------------
        if self.use_local_fallback:
            with self._local_queue_lock:
                local_msgs = [
                    m for m in self._local_queue
                    if m.message_id > since_id
                    and (topic is None or self._matches_topic(topic, m.topic))
                ]
                messages.extend(local_msgs)

        # -- Query PAMS ---------------------------------------------------
        if self._pams_available:
            try:
                pams_msgs = self._query_pams(topic=topic, since_id=since_id, limit=limit)
                if pams_msgs:
                    messages.extend(pams_msgs)
            except Exception:
                self._increment('pams_errors')

        # Deduplicate by message_id
        seen = set()
        unique = []
        for m in sorted(messages, key=lambda x: x.message_id):
            if m.message_id not in seen:
                seen.add(m.message_id)
                unique.append(m)

        # Update last_seen
        if unique:
            with self._poll_lock:
                for m in unique:
                    self._last_seen[m.topic] = max(
                        self._last_seen.get(m.topic, 0), m.message_id
                    )

        return unique

    def poll_and_deliver(self, topic: Optional[str] = None) -> int:
        """
        Poll for new messages and deliver to matching subscribers.

        Args:
            topic: Optional topic filter (if None, polls all topics).

        Returns:
            Number of messages delivered to subscribers.
        """
        # Determine since_id per topic
        with self._poll_lock:
            if topic and topic in self._last_seen:
                since_id = self._last_seen[topic]
            else:
                since_id = 0

        messages = self.poll(topic=topic, since_id=since_id)

        delivered = 0
        for msg in messages:
            count = self._deliver_to_subscribers(msg)
            delivered += count

        return delivered

    def get_last_seen(self, topic: str) -> int:
        """Get the last seen message ID for a topic."""
        return self._last_seen.get(topic, 0)

    def get_stats(self) -> dict:
        """Get bus statistics. Thread-safe atomic snapshot."""
        pq_size = 0
        try:
            if self._persistent_queue_initialized:
                conn = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
                pq_size = conn.execute("SELECT COUNT(*) FROM memorybus_queue WHERE flushed=0").fetchone()[0]
                conn.close()
        except Exception:
            pass

        with self._stats_lock:
            stats_snapshot = dict(self._stats_data)

        with self._local_queue_lock:
            lq_size = len(self._local_queue)

        with self._poll_lock:
            topics_count = len(self._last_seen)

        return {
            'version': self.VERSION,
            'session_id': self.session_id,
            'pams_url': self.pams_url,
            'pams_available': self._pams_available,
            'free_threaded': IS_FREE_THREADED,
            'subscriptions': stats_snapshot.get('subscriptions', 0),
            'published': stats_snapshot.get('published', 0),
            'delivered': stats_snapshot.get('delivered', 0),
            'polls': stats_snapshot.get('polls', 0),
            'pams_errors': stats_snapshot.get('pams_errors', 0),
            'local_fallback_used': stats_snapshot.get('local_fallback_used', 0),
            'persistent_fallback_used': stats_snapshot.get('persistent_fallback_used', 0),
            'persistent_flushed': stats_snapshot.get('persistent_flushed', 0),
            'local_queue_size': lq_size,
            'persistent_queue_size': pq_size,
            'topics_tracked': topics_count,
        }

    def flush_local_queue(self) -> int:
        """
        Attempt to flush the local + persistent fallback queues to PAMS.

        F07 fix: Also flushes persisted SQLite messages.

        Returns:
            Number of messages successfully flushed.
        """
        if not self._pams_available:
            return 0

        flushed = 0
        # Flush in-memory queue first
        with self._local_queue_lock:
            remaining = []
            for msg in self._local_queue:
                try:
                    mid = self._post_to_pams(
                        msg.topic, msg.content, msg.metadata, msg.source
                    )
                    if mid is not None:
                        flushed += 1
                    else:
                        remaining.append(msg)
                except Exception:
                    remaining.append(msg)
            self._local_queue = remaining

        # Flush persistent SQLite queue (batched updates for efficiency)
        if self._persistent_queue_initialized:
            try:
                conn = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
                rows = conn.execute(
                    "SELECT id, topic, content, metadata, source FROM memorybus_queue WHERE flushed=0 ORDER BY id"
                ).fetchall()
                conn.close()
                flushed_ids = []
                for row in rows:
                    try:
                        row_content = json.loads(row[2]) if isinstance(row[2], str) else row[2]
                        row_metadata = json.loads(row[3]) if isinstance(row[3], str) else row[3]
                        mid = self._post_to_pams(row[1], row_content, row_metadata, row[4])
                        if mid is not None:
                            flushed_ids.append(row[0])
                            flushed += 1
                            self._increment('persistent_flushed')
                    except Exception:
                        pass
                # Batch update all flushed messages in one query
                if flushed_ids:
                    conn2 = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
                    placeholders = ','.join('?' * len(flushed_ids))
                    conn2.execute(
                        f"UPDATE memorybus_queue SET flushed=1 WHERE id IN ({placeholders})",
                        flushed_ids
                    )
                    conn2.commit()
                    conn2.close()
            except Exception:
                pass

        return flushed

    # -- Internal --------------------------------------------------------------

    def _check_pams(self) -> bool:
        """Check if PAMS server is reachable."""
        try:
            if HAS_REQUESTS:
                resp = requests.get(f"{self.pams_url}/health", timeout=PAMS_TIMEOUT)
                return resp.status_code == 200
            else:
                req = urllib.request.Request(f"{self.pams_url}/health")
                with urllib.request.urlopen(req, timeout=PAMS_TIMEOUT) as resp:
                    return resp.status == 200
        except Exception:
            return False

    def _post_to_pams(self, topic: str, content: Any,
                      metadata: Dict[str, Any], source: str) -> Optional[int]:
        """Post a message to PAMS as a memory. Returns message ID or None."""
        memory_data = {
            "session_id": self.session_id,
            "category": "memorybus",
            "content": json.dumps({
                "topic": topic,
                "content": content,
                "metadata": metadata,
                "source": source,
                "timestamp": datetime.now().isoformat(),
            }),
            "confidence": 1.0,
            "source": source,
            "tags": [topic] + self._topic_segments(topic),
        }

        if HAS_REQUESTS:
            resp = requests.post(
                f"{self.pams_url}/memories",
                json=memory_data,
                timeout=PAMS_TIMEOUT,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get('id')
        else:
            data_bytes = json.dumps(memory_data).encode('utf-8')
            req = urllib.request.Request(
                f"{self.pams_url}/memories",
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
            )
            with urllib.request.urlopen(req, timeout=PAMS_TIMEOUT) as resp:
                data = json.loads(resp.read())
                return data.get('id')

        return None

    def _query_pams(self, topic: Optional[str] = None, since_id: int = 0,
                    limit: int = 20) -> List[BusMessage]:
        """Query PAMS for memorybus memories. Returns list of BusMessage."""
        params = f"?limit={limit}"
        if topic:
            params += f"&category=memorybus"
        else:
            params += "&category=memorybus"

        if HAS_REQUESTS:
            resp = requests.get(
                f"{self.pams_url}/memories{params}",
                timeout=PAMS_TIMEOUT,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            memories = data.get('memories', [])
        else:
            req = urllib.request.Request(f"{self.pams_url}/memories{params}")
            with urllib.request.urlopen(req, timeout=PAMS_TIMEOUT) as resp:
                data = json.loads(resp.read())
                memories = data.get('memories', [])

        messages = []
        for mem in memories:
            mem_id = mem.get('id', 0)
            if mem_id <= since_id:
                continue

            # Parse stored JSON content
            try:
                content_str = mem.get('content', '{}')
                inner = json.loads(content_str) if isinstance(content_str, str) else content_str
            except (json.JSONDecodeError, TypeError):
                inner = {'content': content_str}

            msg_topic = inner.get('topic', mem.get('category', 'unknown'))
            if topic and not self._matches_topic(topic, msg_topic):
                continue

            messages.append(BusMessage(
                message_id=mem_id,
                topic=msg_topic,
                content=inner.get('content', mem.get('content')),
                metadata=inner.get('metadata', {}),
                timestamp=mem.get('timestamp', ''),
                session_id=mem.get('session_id', ''),
                source=inner.get('source', 'memorybus'),
            ))

        return messages

    def _deliver_to_subscribers(self, msg: BusMessage) -> int:
        """Deliver a message to all matching subscribers. Returns delivery count."""
        count = 0
        with self._sub_lock:
            # Snapshot subscriptions to avoid holding lock during callbacks
            all_subs = [
                (cb, regex) for subs in self._subscriptions.values()
                for cb, regex in subs
            ]

        for callback, regex in all_subs:
            try:
                if regex.search(msg.topic):
                    callback(msg)
                    count += 1
                    self._increment('delivered')
            except Exception:
                # Don't let one bad callback crash the bus
                pass

        return count

    def close(self) -> None:
        """Flush local + persistent queues and clean up resources.

        F07 fix: In-memory messages are persisted to SQLite before clearing,
        preventing absolute data loss on process exit.
        """
        # Persist any remaining UNPERSISTED in-memory messages to SQLite
        if self._local_queue and self._persistent_queue_initialized:
            with self._local_queue_lock:
                for msg in self._local_queue:
                    if msg.message_id not in self._persisted_ids:
                        self._persist_to_queue(msg.topic, msg.content, msg.metadata, msg.source)

        if self._local_queue:
            self.flush_local_queue()
        self._local_queue.clear()
        self._subscriptions.clear()

        # WAL checkpoint on the persistent queue DB
        if self._persistent_queue_initialized:
            try:
                conn = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                conn.close()
            except Exception:
                pass

    @staticmethod
    def _matches_topic(pattern: str, topic: str) -> bool:
        """Check if a topic string matches a pattern."""
        regex = MemoryBus._compile_pattern(pattern)
        return bool(regex.search(topic))

    @staticmethod
    def _compile_pattern(pattern: str) -> re.Pattern:
        """
        Compile a glob-style topic pattern to a regex.

        Rules:
            * matches exactly one segment (between dots or at ends)
            > matches one or more trailing segments
            literal text matches exactly
        """
        # Escape regex special chars except * and >
        # Note: re.escape does NOT escape > (it's not a regex metachar),
        # so we must replace the literal '>' before it gets escaped.
        # Strategy: replace wildcards first, then escape the rest.
        
        # Replace > with a sentinel BEFORE escaping (since re.escape won't touch >)
        SENTINEL = '\x00WILDCARD_GT\x00'
        pattern = pattern.replace('>', SENTINEL)
        
        escaped = re.escape(pattern)
        
        # Restore sentinel to regex wildcard
        escaped = escaped.replace(SENTINEL, r'.+')
        
        # Replace escaped * (re.escape turns * into \*) with single-segment wildcard
        escaped = escaped.replace(r'\*', r'[^.]+')

        return re.compile(f'^{escaped}$')

    @staticmethod
    def _topic_segments(topic: str) -> List[str]:
        """Split a dotted topic into meaningful prefix segments as PAMS tags.
        
        Skips single-segment tags (too broad) and adds 'bus.' namespace prefix.
        Example: 'agent.status.error' -> ['bus.agent.status', 'bus.agent.status.error']
        """
        parts = topic.split('.')
        segments = []
        for i in range(2, len(parts) + 1):  # Start from 2+ segments to avoid single-segment
            segments.append('bus.' + '.'.join(parts[:i]))
        return segments

    def _increment(self, key: str, delta: int = 1) -> None:
        """Thread-safe stat increment.

        Uses dedicated _stats_lock to protect compound read-modify-write.
        Under 3.14t free-threading, ThreadSafeDict alone is insufficient
        because get() and __setitem__ are separate operations.
        """
        with self._stats_lock:
            current = self._stats_data.get(key, 0)
            self._stats_data[key] = current + delta

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (f"MemoryBus(session={self.session_id}, "
                f"pams={'UP' if self._pams_available else 'DOWN'}, "
                f"subs={stats['subscriptions']}, "
                f"pub={stats['published']}, "
                f"del={stats['delivered']})")


# -- Self-test -----------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 65)
    print("  MemoryBus - Self-test")
    print("=" * 65)
    print(f"  Free-threaded: {IS_FREE_THREADED}")
    print(f"  PAMS URL: {PAMS_URL}")

    bus = MemoryBus()
    print(f"  PAMS available: {bus._pams_available}")

    # -- Test 1: Pattern compilation --------------------------------------
    print("\n  [1] Pattern matching:")
    patterns = {
        "agent.status": ["agent.status", "agent.status.detail", "pool.status"],
        "agent.*.error": ["agent.runtime.error", "agent.network.error", "agent.error"],
        "pool.>": ["pool.task", "pool.task.complete", "pool", "agent.task"],
        "*.status": ["agent.status", "pool.status", "agent.status.detail"],
    }
    for pattern, test_topics in patterns.items():
        matches = [t for t in test_topics if bus._matches_topic(pattern, t)]
        print(f"      '{pattern}' matches: {matches}")

    # -- Test 2: Publish (local fallback) ---------------------------------
    print("\n  [2] Publishing messages (local fallback)...")
    mid1 = bus.publish("agent.status", {"status": "running", "agent_id": "test-1"})
    mid2 = bus.publish("agent.error", {"error": "test error", "agent_id": "test-1"})
    mid3 = bus.publish("pool.task", {"task_id": "task-42", "action": "infer"})
    print(f"      Published 3 messages: IDs = {mid1}, {mid2}, {mid3}")

    # -- Test 3: Subscribe and deliver ------------------------------------
    print("\n  [3] Testing subscriptions...")
    received: Any = ThreadSafeList() if HAS_FREETHREADING else []

    def agent_handler(msg: BusMessage) -> None:
        if HAS_FREETHREADING:
            received.append(msg.to_dict())
        else:
            received.append(msg.to_dict())
        print(f"      [SUBSCRIBER] Received: {msg.topic} -> {str(msg.content)[:80]}")

    bus.subscribe("agent.*", agent_handler)
    bus.subscribe("pool.>", agent_handler)
    print(f"      Subscriptions: {bus.get_stats()['subscriptions']}")

    delivered = bus.poll_and_deliver()
    print(f"      Delivered: {delivered} messages to subscribers")

    # -- Test 4: Poll without delivery ------------------------------------
    print("\n  [4] Polling for agent messages...")
    msgs = bus.poll(topic="agent.status", since_id=0)
    print(f"      Found {len(msgs)} agent.status messages")
    for m in msgs[:3]:
        print(f"        [{m.message_id}] {m.topic}: {str(m.content)[:60]}")

    # -- Test 5: Stats ----------------------------------------------------
    print("\n  [5] Bus stats:")
    stats = bus.get_stats()
    for k, v in stats.items():
        print(f"      {k}: {v}")

    # -- Test 6: Unsubscribe ----------------------------------------------
    print("\n  [6] Unsubscribing...")
    remaining = bus.unsubscribe("agent.*", agent_handler)
    print(f"      agent.* remaining subs: {remaining}")
    stats = bus.get_stats()
    print(f"      Total subscriptions: {stats['subscriptions']}")

    print("\n" + "=" * 65)
    print("  MemoryBus self-test complete.")
    print("=" * 65)
