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
                      decision_id: str | None = None,
                      outcome: str | None = None,
                      predicted: float | None = None,
                      realised: float | None = None) -> bool:
    """Append one verbal reflection. Returns True if written.

    `outcome` / `predicted` / `realised` are optional and purely additive
    (EP294, RefGRPO reflection calibration). A reflection that carries the
    caller's own confidence BEFORE the attempt (`predicted`) next to what
    actually happened (`realised`) can be scored against reality later, which
    is the difference between a verbal buffer and a calibrated one. Every one
    of them defaults to None, so a caller passing only the original three
    arguments gets byte-identical behaviour.
    """
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
        # Additive calibration fields: only written when actually supplied, so
        # a pre-existing row and a new row stay distinguishable.
        for _key, _value in (("outcome", outcome), ("predicted", predicted),
                             ("realised", realised)):
            if _value is not None:
                data[_key] = _value
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
    """Recall up to ``limit`` reflections for a question (utility-weighted).

    Newest-first within each rank. Reflections that carry a `realised` outcome
    are promoted ahead of ones that do not (EP294): a reflection that was
    scored against reality is better evidence for the next attempt than one
    that was never checked. Rows without an outcome are still returned - they
    are simply ranked below - so this is a re-ordering, never a filter.
    """
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
                     "decision_id": d.get("decision_id"),
                     "outcome": d.get("outcome"),
                     "predicted": d.get("predicted"),
                     "realised": d.get("realised")})

    # `rows` arrives newest-first, and Python's sort is stable, so ranking only
    # on "has a realised outcome" preserves recency order inside each rank.
    hits.sort(key=lambda h: 0 if h.get("realised") is not None else 1)
    return hits[:max(1, int(limit))]
