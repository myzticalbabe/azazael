# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: COMMUNICATION (5 worms)
MessageBroker, RPCEndpoint, WebhookRelay, IPCBridge, ProtocolNegotiator
"""

import os
import sys
import json
import time
import hashlib
import threading
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

# ── Worm Registry Import ─────────────────────────────────────────────
try:
    from azazael_core.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

# ── Python 3.15t Free-Threading Awareness ────────────────────────────
try:
    from azazael_core.freethreading import is_free_threaded, FreeThreadPool, ThreadSafeDict, ThreadSafeList
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    FreeThreadPool = None
    ThreadSafeDict = dict
    ThreadSafeList = list
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False


@register_worm(category="communication", priority=7, cooldown_seconds=15.0,
    description="Message broker — in-process pub/sub with topic routing and persistence")
class MessageBroker:
    """In-process message broker with topic routing and optional persistence."""

    VERSION = "1.0.0"

    def __init__(self):
        self._topics: Dict[str, List[Callable]] = defaultdict(list)
        self._queue: deque = deque(maxlen=10000)
        self._lock = threading.Lock()

    def subscribe(self, topic: str, handler: Callable[[Dict], None]):
        with self._lock:
            self._topics[topic].append(handler)

    def publish(self, topic: str, payload: Any, persist: bool = False):
        msg = {"topic": topic, "payload": payload, "timestamp": time.time(),
               "id": hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}
        with self._lock:
            if persist:
                self._queue.append(msg)
            handlers = list(self._topics.get(topic, [])) + list(self._topics.get("*", []))
        for h in handlers:
            try:
                h(msg)
            except Exception:
                pass

    def replay(self, topic: str = "", limit: int = 100) -> List[Dict]:
        with self._lock:
            msgs = [m for m in self._queue if not topic or m["topic"] == topic]
            return list(msgs)[-limit:]


@register_worm(category="communication", priority=6, cooldown_seconds=30.0,
    description="RPC endpoint — JSON-RPC 2.0 server for inter-worm remote procedure calls")
class RPCEndpoint:
    """JSON-RPC 2.0 server for inter-worm communication."""

    VERSION = "1.0.0"

    def __init__(self):
        self._methods: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def register_method(self, name: str, func: Callable):
        with self._lock:
            self._methods[name] = func

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC 2.0 request."""
        try:
            method = request.get("method", "")
            params = request.get("params", {})
            req_id = request.get("id")
            func = self._methods.get(method)
            if not func:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found"}}
            result = func(**params) if isinstance(params, dict) else func(*params)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32000, "message": str(e)}}

    def list_methods(self) -> List[str]:
        return list(self._methods.keys())


@register_worm(category="communication", priority=5, cooldown_seconds=30.0,
    description="Webhook relay — dispatch HTTP callbacks with retry and batching")
class WebhookRelay:
    """Dispatches webhook callbacks with retry logic."""

    VERSION = "1.0.0"

    def __init__(self):
        self._hooks: Dict[str, Dict] = {}
        self._delivery_log: List[Dict] = []
        self._lock = threading.Lock()

    def register_webhook(self, name: str, url: str, secret: str = ""):
        with self._lock:
            self._hooks[name] = {"url": url, "secret": secret, "deliveries": 0, "failures": 0}

    def deliver(self, name: str, payload: Dict, max_retries: int = 3) -> Dict[str, Any]:
        """Deliver a webhook payload with retry."""
        hook = self._hooks.get(name)
        if not hook:
            return {"success": False, "error": "Webhook not registered"}
        data = json.dumps(payload).encode()
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(hook["url"], data=data,
                    headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    with self._lock:
                        hook["deliveries"] += 1
                    return {"success": True, "status": resp.status, "attempt": attempt + 1}
            except Exception as e:
                if attempt == max_retries - 1:
                    with self._lock:
                        hook["failures"] += 1
                    return {"success": False, "error": str(e), "attempts": attempt + 1}
                time.sleep(2 ** attempt)


@register_worm(category="communication", priority=5, cooldown_seconds=30.0,
    description="IPC bridge — inter-process communication via pipes, shared memory, or sockets")
class IPCBridge:
    """Inter-process communication bridge for worm-to-worm data transfer."""

    VERSION = "1.0.0"

    def __init__(self):
        self._channels: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def create_channel(self, name: str, channel_type: str = "queue") -> str:
        """Create an IPC channel."""
        ch = {"name": name, "type": channel_type, "messages": deque(maxlen=1000), "created": time.time()}
        with self._lock:
            self._channels[name] = ch
        return name

    def send(self, channel: str, data: Any) -> bool:
        with self._lock:
            ch = self._channels.get(channel)
            if ch:
                ch["messages"].append({"data": data, "timestamp": time.time()})
                return True
        return False

    def receive(self, channel: str, timeout_sec: float = 5.0) -> Optional[Any]:
        """Receive a message from a channel with timeout."""
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            with self._lock:
                ch = self._channels.get(channel)
                if ch and ch["messages"]:
                    return ch["messages"].popleft()["data"]
            time.sleep(0.01)
        return None


@register_worm(category="communication", priority=4, cooldown_seconds=45.0,
    description="Protocol negotiator — auto-detect best protocol between JSON, MessagePack, gRPC")
class ProtocolNegotiator:
    """Auto-negotiates the best serialization protocol between peers."""

    VERSION = "1.0.0"

    def __init__(self):
        self._capabilities: Dict[str, List[str]] = {}
        self._preferred = "json"

    def register_peer(self, peer_id: str, protocols: List[str]):
        self._capabilities[peer_id] = protocols

    def negotiate(self, peer_id: str) -> str:
        """Find the best common protocol with a peer."""
        mine = self._available_protocols()
        theirs = self._capabilities.get(peer_id, ["json"])
        common = [p for p in mine if p in theirs]
        return common[0] if common else "json"

    def _available_protocols(self) -> List[str]:
        protocols = ["json"]
        try:
            import msgpack
            protocols.append("msgpack")
        except ImportError:
            pass
        return protocols

    def serialize(self, data: Any, protocol: str) -> bytes:
        if protocol == "msgpack":
            import msgpack
            return msgpack.dumps(data)
        return json.dumps(data).encode()

    def deserialize(self, data: bytes, protocol: str) -> Any:
        if protocol == "msgpack":
            import msgpack
            return msgpack.loads(data)
        return json.loads(data.decode())
