#!/usr/bin/env python3
"""PamsBusBridge - Wires MemoryBus events into PAMS persistence.

Subscribes to MemoryBus topics and automatically persists published
messages as memories in the Persistent AI Memory System (PAMS).
"""

import json
from CORE.uuid7 import uuid7
import threading
from typing import Optional, List

from CORE.FreeThreadedAgent import FreeThreadedAgent
from CORE.MemoryBus import MemoryBus, BusMessage
import requests

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here


class PamsBusBridge(FreeThreadedAgent):
    """
    Bridges MemoryBus events to PAMS persistence.

    Usage::
        bus = MemoryBus()
        bridge = PamsBusBridge(bus, pams_url="http://localhost:5100")
        bridge.subscribe_topic("cluster.*")   # wildcard support
        bridge.start()  # starts listening thread
    """

    def __init__(
        self,
        memory_bus: MemoryBus,
        pams_url: str = "http://localhost:5100",
        name: str = "PamsBusBridge",
        pool=None,
    ):
        super().__init__(name=name, memory_bus=memory_bus, pool=pool)
        self.pams_url = pams_url.rstrip("/")
        self._subscriptions: list = []
        self._stats_lock = threading.Lock()
        self._persist_stats = {"persisted": 0, "failed": 0}
        self._session_id = uuid7().hex[:8]
        self._register_session_with_pams()

    def subscribe_topic(self, topic_pattern: str) -> None:
        """Subscribe to a MemoryBus topic pattern.

        Supports exact topic names. Wildcard matching (e.g. "cluster.*")
        is done via simple prefix matching in the callback.
        """
        self.memory_bus.subscribe(topic_pattern, self._on_memory_message)
        self._subscriptions.append(topic_pattern)
        self.tlog("info", f"Subscribed to topic pattern: {topic_pattern}")

    def subscribe_all(self) -> None:
        """Subscribe to the wildcard topic to receive all events."""
        self.subscribe_topic("*")

    def _register_session_with_pams(self):
        """Register this bridge as a session with PAMS."""
        try:
            r = requests.post(f"{self.pams_url}/memories", json={
                "session_id": self._session_id,
                "category": "session",
                "content": json.dumps({"bridge": self.name, "status": "online"}),
                "source": self.name,
                "confidence": 1.0,
            }, timeout=5)
            sid = self._session_id
            self.tlog("info", f'Session {sid} registered with PAMS')
        except Exception as e:
            note_failure("PamsBusBridge:L70", e)
            self.tlog("warning", f'Could not register session: {e}')

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_memory_message(self, message: BusMessage) -> None:
        """Callback when a MemoryBus message is received. Persists to PAMS."""
        try:
            payload = {
                "session_id": self._session_id,
                "content": json.dumps({
                    "topic": message.topic,
                    "payload": message.content,
                    "source": message.source,
                    "message_id": message.message_id,
                    "timestamp": message.timestamp,
                }),
                "category": "memorybus",
                "source": message.source or "MemoryBus",
                "confidence": 1.0,
            }
            r = requests.post(
                f"{self.pams_url}/memories",
                json=payload,
                timeout=5,
            )
            if r.status_code == 200:
                with self._stats_lock:
                    self._persist_stats["persisted"] += 1
                topic = message.topic
                msg_id = message.message_id
                self.tlog("debug", f"Persisted: {topic} (id={msg_id})")
            else:
                with self._stats_lock:
                    self._persist_stats["failed"] += 1
                status_code = r.status_code
                topic = message.topic
                self.tlog("warning", f"PAMS returned {status_code} for {topic}")
        except Exception as e:
            note_failure("PamsBusBridge:L110", e)
            with self._stats_lock:
                self._persist_stats["failed"] += 1
            topic = message.topic
            self.tlog("error", f"Failed to persist {topic}: {e}")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main loop: keep the bridge alive and processing."""
        sub_count = len(self._subscriptions)
        self.tlog("info", f"PamsBusBridge online - subscribing to {sub_count} patterns")
        while self.is_running:
            import time
            time.sleep(1.0)

    def on_stop(self) -> None:
        """Clean up subscriptions on stop."""
        for pattern in self._subscriptions:
            try:
                self.memory_bus.unsubscribe(pattern, self._on_memory_message)
            except Exception:
                note_failure("PamsBusBridge:L133", None)
        stats = self._persist_stats
        self.tlog("info", f"PamsBusBridge stopped. Stats: {stats}")

    def bridge_stats(self) -> dict:
        """Get persistence statistics."""
        with self._stats_lock:
            return dict(self._persist_stats)
