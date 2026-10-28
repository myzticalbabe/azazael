# coding: utf-8
"""
LaneMessageBoard — cross-lane agent message board and push hook.

Builds on MemoryBus (PAMS-backed pub/sub bus) to provide a durable,
lane-addressable message board for the three-lane agent system:
  opencode ↔ kilo ↔ freebuff

Topics:
  lane.<lane>.tasks      — tasks addressed to a specific lane
  lane.<lane>.status     — status updates from a lane
  lane.all.announce      — announcements broadcast to all lanes
  lane.push.<src>-><dst> — push hook: task pushed from src lane to dst lane

Usage:
    board = LaneMessageBoard()
    board.post_task("kilo", {"id": 1039, "action": "continue", "detail": "run long test"})
    board.push_hook("opencode", "freebuff", {"action": "mcp_config_fix"})
    msgs = board.poll_tasks("kilo")

All messages are durably stored in PAMS (with SQLite fallback), so they
survive session restarts — unlike message-history.json which is ephemeral chat log.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from CORE.MemoryBus import MemoryBus, BusMessage


@dataclass
class LaneTask:
    """A task addressed to a specific lane."""
    lane: str
    task_id: Optional[str] = None
    action: str = ""
    detail: str = ""
    source_lane: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: str = "pending"  # pending | in_progress | completed | blocked
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lane": self.lane,
            "task_id": self.task_id,
            "action": self.action,
            "detail": self.detail,
            "source_lane": self.source_lane,
            "created_at": self.created_at,
            "status": self.status,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LaneTask":
        return cls(
            lane=d.get("lane", ""),
            task_id=d.get("task_id"),
            action=d.get("action", ""),
            detail=d.get("detail", ""),
            source_lane=d.get("source_lane", ""),
            created_at=d.get("created_at", ""),
            status=d.get("status", "pending"),
            metadata=d.get("metadata", {}),
        )


class LaneMessageBoard:
    """
    Cross-lane message board backed by MemoryBus (PAMS durable store).

    Provides task posting, lane subscriptions, push hooks, and polling
    for opencode / kilo / freebuff lanes.
    """

    VALID_LANES = ("opencode", "kilo", "freebuff")

    def __init__(
        self,
        session_id: Optional[str] = None,
        pams_url: Optional[str] = None,
        lane: str = "opencode",
    ):
        if lane not in self.VALID_LANES:
            raise ValueError(f"lane must be one of {self.VALID_LANES}, got {lane!r}")
        self.lane = lane
        self._bus = MemoryBus(pams_url=pams_url, session_id=session_id)
        self._lock = threading.Lock()
        self._callbacks: Dict[str, List[Callable[[LaneTask], None]]] = {
            lane: [] for lane in self.VALID_LANES
        }
        self._callbacks["all"] = []

    # -- topic helpers -------------------------------------------------------

    def _task_topic(self, lane: str) -> str:
        return f"lane.{lane}.tasks"

    def _status_topic(self, lane: str) -> str:
        return f"lane.{lane}.status"

    def _announce_topic(self) -> str:
        return "lane.all.announce"

    def _push_topic(self, src: str, dst: str) -> str:
        return f"lane.push.{src}->{dst}"

    # -- public API: post ---------------------------------------------------

    def post_task(
        self,
        lane: str,
        action: str,
        detail: str = "",
        task_id: Optional[str] = None,
        source_lane: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Post a task to a lane's task queue.

        Returns the message ID from the bus (PAMS or local fallback).
        """
        if lane not in self.VALID_LANES:
            raise ValueError(f"lane must be one of {self.VALID_LANES}, got {lane!r}")
        task = LaneTask(
            lane=lane,
            task_id=task_id,
            action=action,
            detail=detail,
            source_lane=source_lane or self.lane,
            metadata=metadata or {},
        )
        return self._bus.publish(
            self._task_topic(lane),
            task.to_dict(),
            metadata={"type": "lane_task", "lane": lane, "source": self.lane},
            source=self.lane,
        )

    def post_announcement(
        self,
        announcement: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Broadcast an announcement to all lanes."""
        return self._bus.publish(
            self._announce_topic(),
            {
                "announcement": announcement,
                "source_lane": self.lane,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            metadata={"type": "announcement", "source": self.lane},
            source=self.lane,
        )

    def post_status(
        self,
        status: str,
        detail: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Post a status update from this lane."""
        return self._bus.publish(
            self._status_topic(self.lane),
            {
                "lane": self.lane,
                "status": status,
                "detail": detail,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            metadata={"type": "lane_status", "lane": self.lane, "source": self.lane},
            source=self.lane,
        )

    def push_hook(
        self,
        dst_lane: str,
        action: str,
        detail: str = "",
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Push a task from this lane to another lane via the push hook.

        Equivalent to post_task but recorded on a push-specific topic
        so push-hook traffic can be filtered/audited separately.
        """
        if dst_lane not in self.VALID_LANES:
            raise ValueError(
                f"dst_lane must be one of {self.VALID_LANES}, got {dst_lane!r}"
            )
        # Audit record on the push-specific topic (separate from delivery).
        try:
            self._bus.publish(
                self._push_topic(self.lane, dst_lane),
                {
                    "src_lane": self.lane,
                    "dst_lane": dst_lane,
                    "task_id": task_id,
                    "action": action,
                    "detail": detail,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                metadata={"type": "lane_push", "src": self.lane, "dst": dst_lane},
                source=self.lane,
            )
        except Exception:
            pass
        # Delivery record on the destination lane's task queue.
        return self.post_task(
            lane=dst_lane,
            action=action,
            detail=detail,
            task_id=task_id,
            source_lane=self.lane,
            metadata=metadata or {},
        )

    # -- public API: subscribe ----------------------------------------------

    def subscribe_to_tasks(
        self,
        lane: str,
        callback: Callable[[LaneTask], None],
    ) -> int:
        """
        Subscribe to tasks addressed to a lane.

        Returns the number of active subscriptions for that lane's topic.
        """
        if lane not in self.VALID_LANES:
            raise ValueError(f"lane must be one of {self.VALID_LANES}, got {lane!r}")

        def _adapter(msg: BusMessage) -> None:
            try:
                task = LaneTask.from_dict(msg.content if isinstance(msg.content, dict)
                                          else json.loads(msg.content))
            except Exception:
                return  # malformed message; skip
            callback(task)

        with self._lock:
            self._callbacks[lane].append(callback)
        return self._bus.subscribe(self._task_topic(lane), _adapter)

    def subscribe_to_all_tasks(
        self,
        callback: Callable[[LaneTask], None],
    ) -> None:
        """Subscribe to tasks for all lanes (for monitoring/audit)."""
        for lane in self.VALID_LANES:
            self.subscribe_to_tasks(lane, callback)

    def subscribe_to_announcements(
        self,
        callback: Callable[[Dict[str, Any]], None],
    ) -> int:
        """Subscribe to all-lane announcements."""
        return self._bus.subscribe(self._announce_topic(), callback)

    # -- public API: poll ---------------------------------------------------

    def _poll_persistent_queue(
        self,
        topic: str,
        since_id: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Read messages directly from the shared persistent SQLite queue.

        This enables cross-instance (cross-process) communication even when
        PAMS is unavailable: both lanes read from the same SQLite database.

        FIX 2026-10-26 (board-blindness): with since_id=0 the old
        ORDER BY id ASC LIMIT took the OLDEST N rows, so any queue longer
        than `limit` hid every new task from polling lanes. Now takes the
        NEWEST N (DESC) and re-sorts ASC, so a poll always sees live orders.
        """
        import sqlite3

        from CORE.MemoryBus import _MEMORYBUS_DB_PATH

        results: List[Dict[str, Any]] = []
        try:
            conn = sqlite3.connect(str(_MEMORYBUS_DB_PATH), timeout=2)
            conn.row_factory = sqlite3.Row
            if since_id:
                rows = conn.execute(
                    "SELECT id, topic, content, metadata, source, session_id, timestamp "
                    "FROM memorybus_queue "
                    "WHERE topic LIKE ? AND id > ? "
                    "ORDER BY id ASC LIMIT ?",
                    (topic, since_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, topic, content, metadata, source, session_id, timestamp "
                    "FROM memorybus_queue "
                    "WHERE topic LIKE ? "
                    "ORDER BY id DESC LIMIT ?",
                    (topic, limit),
                ).fetchall()
                rows = rows[::-1]
            conn.close()
            for row in rows:
                try:
                    content = row["content"]
                    if isinstance(content, str):
                        content = json.loads(content)
                    metadata = row["metadata"]
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                    results.append({
                        "id": row["id"],
                        "topic": row["topic"],
                        "content": content,
                        "metadata": metadata,
                        "source": row["source"],
                        "session_id": row["session_id"],
                        "timestamp": row["timestamp"],
                    })
                except Exception:
                    continue
        except Exception:
            pass
        return results

    def poll_tasks(
        self,
        lane: str,
        since_id: int = 0,
        limit: int = 50,
    ) -> List[LaneTask]:
        """
        Poll for tasks addressed to a lane.

        Reads from both the MemoryBus (PAMS or local in-memory queue) and the
        shared persistent SQLite queue, enabling cross-instance communication
        even when PAMS is unavailable.

        Returns tasks with message ID > since_id.
        """
        if lane not in self.VALID_LANES:
            raise ValueError(f"lane must be one of {self.VALID_LANES}, got {lane!r}")

        # Read from MemoryBus (PAMS or in-memory local queue)
        msgs = self._bus.poll(topic=self._task_topic(lane), since_id=since_id, limit=limit)

        # Also read from the shared persistent SQLite queue for cross-instance msgs
        persistent = self._poll_persistent_queue(self._task_topic(lane), since_id, limit)

        # Merge, deduplicating by id
        seen: set = set()
        tasks: List[LaneTask] = []

        for m in msgs:
            mid = m.message_id
            if mid in seen:
                continue
            seen.add(mid)
            try:
                tasks.append(LaneTask.from_dict(
                    m.content if isinstance(m.content, dict) else json.loads(m.content)
                ))
            except Exception:
                continue

        for p in persistent:
            mid = p["id"]
            if mid in seen:
                continue
            seen.add(mid)
            try:
                task = LaneTask.from_dict(p["content"])
                # Expose the durable queue row id: pollers cite Board-<id>,
                # and ordering below keys on it instead of the string task_id
                # (mixed numeric/string ids sort meaninglessly as strings).
                if isinstance(task.metadata, dict):
                    task.metadata.setdefault("_row_id", mid)
                tasks.append(task)
            except Exception:
                continue

        # Newest-first when uncursored (see _poll_persistent_queue fix);
        # key on durable row id, fallback to legacy string task_id sort.
        def _order(t: LaneTask):
            try:
                rid = (t.metadata or {}).get("_row_id")
                if rid is not None:
                    return (0, int(rid))
            except Exception:
                pass
            try:
                if t.task_id and t.task_id.isdigit():
                    return (1, int(t.task_id))
            except Exception:
                pass
            return (2, 0)

        tasks.sort(key=_order)
        return tasks[:limit]

    def poll_announcements(
        self,
        since_id: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Poll for all-lane announcements."""
        msgs = self._bus.poll(topic=self._announce_topic(), since_id=since_id, limit=limit)

        # Also read from persistent queue
        persistent = self._poll_persistent_queue(self._announce_topic(), since_id, limit)

        out: List[Dict[str, Any]] = []
        seen: set = set()
        for m in msgs:
            mid = m.message_id
            if mid in seen:
                continue
            seen.add(mid)
            try:
                out.append(m.content if isinstance(m.content, dict) else json.loads(m.content))
            except Exception:
                continue

        for p in persistent:
            mid = p["id"]
            if mid in seen:
                continue
            seen.add(mid)
            try:
                out.append(p["content"])
            except Exception:
                continue

        return out[:limit]


    def poll_and_deliver(self) -> int:
        """Poll all lanes' task topics and deliver to subscribers.

        Returns the number of messages delivered.
        """
        delivered = 0
        for lane in self.VALID_LANES:
            delivered += self._bus.poll_and_deliver(topic=self._task_topic(lane))
        delivered += self._bus.poll_and_deliver(topic=self._announce_topic())
        return delivered

    def get_stats(self) -> Dict[str, int]:
        """Return bus statistics."""
        return dict(self._bus.get_stats())

    # -- legacy chat-log migration ------------------------------------------

    def import_from_chat_log(self, chat_log_path: str) -> int:
        """
        Import task-looking entries from message-history.json into the board.

        Parses the JSON array and tracks context across entries: when an enggram
        number appears in one entry and a lane name appears in a nearby entry,
        a pending task is created for that lane. Returns the number of tasks imported.
        """
        import json
        import os
        import re

        if not os.path.isfile(chat_log_path):
            return 0

        engram_re = re.compile(r"engram\s*(?:#)?(\d+)", re.IGNORECASE)
        lane_re = re.compile(r"\b(kilo|freebuff|opencode)\b", re.IGNORECASE)

        count = 0
        pending_engram: Optional[str] = None
        pending_detail: str = ""

        try:
            with open(chat_log_path, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
        except Exception:
            return 0

        if not isinstance(data, list):
            return 0

        for entry in data:
            if not isinstance(entry, str):
                continue
            text = entry.strip()
            if not text:
                continue

            em = engram_re.search(text)
            lm = lane_re.search(text)

            if em:
                pending_engram = em.group(1)
                pending_detail = text[:500]

            if lm:
                lane = lm.group(1).lower()
                if lane in self.VALID_LANES and pending_engram:
                    self.post_task(
                        lane=lane,
                        action="imported_from_chat_log",
                        detail=pending_detail,
                        task_id=pending_engram,
                        source_lane="migration",
                        metadata={"source": "message-history.json"},
                    )
                    count += 1
                    pending_engram = None
                    pending_detail = ""

        return count


def main() -> int:
    """CLI smoke test: post a task to each lane and poll kilo's queue."""
    board = LaneMessageBoard(lane="opencode")

    board.post_task("kilo", "continue", "enggram #1039 — continue needed tasks concurrently", task_id="1039")
    board.post_task("freebuff", "mcp_config_fix", "string command → argv ARRAY", task_id="mcp-001")
    board.post_announcement("LaneMessageBoard initialized — cross-lane task board live")

    tasks = board.poll_tasks("kilo")
    print(f"Kilo tasks: {len(tasks)}")
    for t in tasks:
        print(f"  #{t.task_id} {t.action}: {t.detail[:60]}")

    stats = board.get_stats()
    print(f"Bus stats: {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
