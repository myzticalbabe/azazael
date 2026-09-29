"""Reflexion verbal buffer (2026-09-29, stdlib only, fail-open).

Verbal reinforcement without weight updates (Reflexion, 2303.11366):
after a failed trajectory the agent writes one paragraph — what went
wrong, what to try differently — stored as episodic memory and prepended
to the next attempt. Actor / Evaluator / Self-Reflection split is the
caller's job; this module is only the buffer: append + recall.

Free-Jev: local tap only, no model calls. Recording must never break a
caller: every entry point returns a bool / list, never raises.
"""
from __future__ import annotations

from typing import Any

EVENT_TYPE = "reflexion_note"
MAX_TEXT_CHARS = 2000


def record_reflection(question: str, what_failed: str, what_next: str,
                      *, store: Any = None,
                      decision_id: str | None = None) -> bool:
    """Append one verbal reflection. Returns True if written."""
    text_failed = str(what_failed or "")[:MAX_TEXT_CHARS]
    text_next = str(what_next or "")[:MAX_TEXT_CHARS]
    if not text_failed and not text_next:
        return False
    try:
        if store is None:
            from CORE.local_memory import get_memory_store
            store = get_memory_store()
        data: dict[str, Any] = {
            "question": str(question or "")[:500],
            "what_failed": text_failed,
            "what_next": text_next,
        }
        if decision_id:
            data["decision_id"] = str(decision_id)
        store.record_event(
            source="reflexion",
            event_type=EVENT_TYPE,
            data=data,
            severity="info",
            tags=["reflexion", "verbal-rl"],
            correlation_id=str(decision_id) if decision_id else None,
        )
        return True
    except Exception:
        return False


def reflections_for(question: str, *, store: Any = None,
                    limit: int = 5) -> list[dict[str, Any]]:
    """Recall up to ``limit`` reflections for a question (newest first)."""
    try:
        if store is None:
            from CORE.local_memory import get_memory_store
            store = get_memory_store()
        # `store` is injectable (this module is used with test doubles), so
        # prefer the paged reader when the store has one and fall back to the
        # plain read otherwise. fetch_all_memories is required on a real store:
        # query_memories clamps at MAX_QUERY_LIMIT (500), which would make
        # recall silently ignore every reflection older than the newest 500.
        fetch = getattr(store, "fetch_all_memories", None)
        if callable(fetch):
            rows = fetch(event_type=EVENT_TYPE, limit=500) or []
        else:
            rows = store.query_memories(event_type=EVENT_TYPE, limit=500) or []
    except Exception:
        return []
    q = " ".join(str(question or "").lower().split())
    hits = []
    for row in rows:
        d = (row or {}).get("data") or {}
        if isinstance(d, str):
            try:
                import json as _json
                d = _json.loads(d)
            except Exception:
                continue
        if not isinstance(d, dict):
            continue
        if q and q not in str(d.get("question", "")).lower():
            continue
        hits.append({"question": d.get("question"),
                     "what_failed": d.get("what_failed"),
                     "what_next": d.get("what_next"),
                     "decision_id": d.get("decision_id")})
        if len(hits) >= max(1, int(limit)):
            break
    return hits
