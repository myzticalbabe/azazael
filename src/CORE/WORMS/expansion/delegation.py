# coding: utf-8
"""
ECOSYSTEM EXPANSION — ask_owner mid-flight clarification channel.

A worm executing on a pool worker thread sometimes cannot proceed without
input from its owner (ambiguous target, missing credential, destructive
action needing confirmation). Before this module the only options were to
fail or guess — both recorded as ordinary failures, indistinguishable from
real defects.

The channel is deliberately narrow:

* Worm code raises ``NeedsClarification(question)`` or calls ``ask_owner()``
  directly. Both park the worker on a ``threading.Event`` with a deadline —
  never on stdin/UI, never unbounded (the pool watchdog kills hung waits).
* The owner (or an owner-side automation) answers via ``answer_question()``.
* The rendezvous is an in-process registry keyed by ``decision_id``. The
  ``MemoryBus`` is used as an observability tap only (``worm.question.>`` /
  ``worm.answer.>`` announcements, best-effort): question delivery never
  depends on bus subscription timing, so the channel works in tests and in
  processes without a bus.
* The executor boundary (``CLUSTERWORMS.WormExecutor._execute_direct``)
  normalises both outcomes to the standard result shape with
  ``needs_input`` set, so telemetry, breaker accounting and aggregation
  keep working. A clarification is NOT a transient failure: it must not
  trigger breaker retry, and it records at ``info``-adjacent severity
  discipline (success=False, error names the question, not a crash).

Fail-closed: timeout (default 30s, must stay below the pool watchdog) and
a missing bus both produce a ``needs_input`` outcome naming the question,
never a hang and never a guessed answer.
"""

from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Callable, Dict, Optional, Tuple, List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

#: Upper bound for a parked wait. Must stay below the pool watchdog /
#: ``as_completed`` timeouts that supervise worker threads, or the park
#: becomes the hang it exists to prevent.
DEFAULT_TIMEOUT_S = 30.0

#: Longest question text carried. Bounded like the telemetry error cap: a
#: question is a signature for the owner, not a transcript dump.
MAX_QUESTION_CHARS = 800

QUESTION_TOPIC = "worm.question"
ANSWER_TOPIC = "worm.answer"


class NeedsClarification(Exception):
    """Raised by worm code that needs owner input to proceed.

    Carries everything the executor needs to normalise the outcome without
    importing this module's internals.
    """

    def __init__(self, question: str, *,
                 decision_id: Optional[str] = None,
                 worm: Optional[str] = None,
                 timeout_s: float = DEFAULT_TIMEOUT_S):
        super().__init__(str(question)[:MAX_QUESTION_CHARS])
        self.question = str(question)[:MAX_QUESTION_CHARS]
        self.decision_id = decision_id
        self.worm = worm
        self.timeout_s = float(timeout_s)


class ClarificationTimeout(Exception):
    """No answer arrived before the deadline. Fail-closed, never a guess."""

    def __init__(self, question: str, *,
                 decision_id: Optional[str] = None,
                 worm: Optional[str] = None,
                 waited_s: float = 0.0):
        super().__init__("clarification timed out: %s"
                         % str(question)[:MAX_QUESTION_CHARS])
        self.question = str(question)[:MAX_QUESTION_CHARS]
        self.decision_id = decision_id
        self.worm = worm
        self.waited_s = float(waited_s)


_lock = threading.Lock()
#: decision_id -> [threading.Event, answer slot]. In-process only: the wait
#: must not depend on bus delivery timing (tests, bus-less processes).
_waiters: Dict[str, list] = {}


def _new_decision_id() -> str:
    try:
        from CORE.WORMS.expansion.spawn_credit import new_decision_id
        return str(new_decision_id())
    except Exception:
        note_failure("delegation:L97", None)
        try:
            from CORE.uuid7 import uuid7
            return "d-local-%s" % uuid7().hex[:12]
        except Exception:
            note_failure("delegation:L101", None)
            return "d-local-%s" % uuid.uuid4().hex[:12]


def _announce(topic: str, payload: Dict[str, Any], bus: Any = None) -> None:
    """Best-effort observability tap. Never raises, never blocks."""
    try:
        if bus is None:
            try:
                from CORE.MemoryBus import MemoryBus
                bus = MemoryBus()
            except Exception:
                note_failure("delegation:L112", None)
                return
        bus.publish(topic, payload, source="delegation")
    except Exception:
        note_failure("delegation:L115", None)
    try:
        from CORE.local_memory import get_memory_store
        store = get_memory_store()
        if store is not None:
            store.record_event(
                source="delegation", event_type="worm_question",
                data={"topic": topic,
                      "question": str(payload.get("question", ""))[:300],
                      "decision_id": payload.get("decision_id"),
                      "worm": payload.get("worm"),
                      "answered": bool(payload.get("answered", False))},
                severity="info", tags=["delegation", "ask-owner"])
    except Exception:
        note_failure("delegation:L129", None)


def ask_owner(question: str, *,
              decision_id: Optional[str] = None,
              worm: Optional[str] = None,
              timeout_s: float = DEFAULT_TIMEOUT_S,
              bus: Any = None) -> Any:
    """Park the calling (worker) thread until the owner answers.

    Returns the answer object. Raises ``ClarificationTimeout`` on deadline.
    Works without a bus (rendezvous is in-process); the bus announcement is
    how owners discover the question.
    """
    q = str(question)[:MAX_QUESTION_CHARS]
    if timeout_s is None or float(timeout_s) <= 0:
        raise ClarificationTimeout(q, decision_id=decision_id, worm=worm,
                                   waited_s=0.0)
    did = decision_id or _new_decision_id()
    ev = threading.Event()
    with _lock:
        _waiters[did] = [ev, None, False]
    _announce("%s.%s" % (QUESTION_TOPIC, worm or "unknown"),
              {"question": q, "decision_id": did, "worm": worm,
               "timeout_s": float(timeout_s)}, bus)
    t0 = time.monotonic()
    got = ev.wait(float(timeout_s))
    with _lock:
        slot = _waiters.pop(did, None)
    waited = time.monotonic() - t0
    if got and slot is not None and slot[2]:
        return slot[1]
    raise ClarificationTimeout(q, decision_id=did, worm=worm, waited_s=waited)


def answer_question(decision_id: str, answer: Any,
                    bus: Any = None) -> bool:
    """Deliver an owner's answer. Returns True if a waiter received it."""
    if not decision_id:
        return False
    with _lock:
        slot = _waiters.get(decision_id)
        if slot is None:
            return False
        slot[1] = answer
        slot[2] = True
        slot[0].set()
    _announce("%s.%s" % (ANSWER_TOPIC, decision_id),
              {"decision_id": decision_id, "answered": True}, bus)
    return True


def pending_count() -> int:
    """Parked workers currently awaiting answers. For monitors/tests."""
    with _lock:
        return len(_waiters)


def on_question(callback: Callable[[Any], None], *,
                bus: Any = None,
                pattern: str = "worm.question.>") -> Optional[int]:
    """Subscribe an owner-side callback to question announcements.

    Returns the subscription id, or None when no bus is available. The
    callback receives the bus message; answering is via ``answer_question``.
    """
    try:
        if bus is None:
            try:
                from CORE.MemoryBus import MemoryBus
                bus = MemoryBus()
            except Exception:
                note_failure("delegation:L201", None)
                return None
        return int(bus.subscribe(pattern, callback))
    except Exception:
        note_failure("delegation:L204", None)
        return None


def clarification_outcome(name: str,
                          exc: Exception,
                          duration_ms: float = 0.0) -> Dict[str, Any]:
    """Normalise a clarification outcome to the executor result shape.

    Matches ``WormExecutor._execute_direct`` output so telemetry, breaker
    accounting and ``aggregate_results`` keep working unchanged. success is
    False (no work completed) but the error names the question — a parked
    wait is not a crash, and must not read as one in the outcome tap.
    """
    timed_out = isinstance(exc, ClarificationTimeout)
    question = getattr(exc, "question", str(exc))[:MAX_QUESTION_CHARS]
    did = getattr(exc, "decision_id", None)
    error = ("clarification timed out, no answer: %s" % question
             if timed_out else "needs owner input: %s" % question)
    return {
        "name": name,
        "success": False,
        "duration_ms": float(duration_ms or 0.0),
        "result": {"needs_input": question,
                   "timed_out": bool(timed_out),
                   "decision_id": did},
        "error": error[:MAX_QUESTION_CHARS],
        "needs_input": question,
        "timed_out": bool(timed_out),
        "decision_id": did,
    }
