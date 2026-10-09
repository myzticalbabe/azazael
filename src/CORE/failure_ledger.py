#!/usr/bin/env python3
"""failure_ledger.py — one process-wide ledger of swallowed failures.

WHY A LEAF MODULE. Every fail-open handler in this tree is supposed to RECORD its
swallow, because an unrecorded swallow is indistinguishable from success. That
only works if the recorder is importable from anywhere: a module that imports the
technique runtime to get it can hit an import cycle, and a guarded
``except ImportError`` would then silently downgrade every recording to a no-op --
the recorder itself swallowed. This module therefore imports nothing but the
standard library, and everything else imports it.

READ SIDE. ``failure_notes()`` returns {where:ExcType: count}. Empty means
nothing recorded a degradation in this process. This is the same object the
technique runtime re-exports as ``technique_runtime.note_failure``.
"""

from __future__ import annotations

import threading
from typing import Dict, Optional

#: Swallowed failures, by "where:ExcType". Populated by every fail-open handler.
_FAILURE_NOTES: Dict[str, int] = {}
_FAILURE_LOCK = threading.Lock()

#: Times the recorder itself could not record. Non-zero means the real count is
#: higher than `failure_notes()` reports -- never silently zero.
_LOST_NOTES = [0]


def note_failure(where: str, exc: Optional[BaseException] = None) -> None:
    """Record a swallowed failure. Cheap, bounded, thread-safe, never raises."""
    try:
        key = "%s:%s" % (where, type(exc).__name__ if exc is not None else "unknown")
        with _FAILURE_LOCK:
            _FAILURE_NOTES[key] = _FAILURE_NOTES.get(key, 0) + 1
    except Exception:                             # never raise from the recorder
        note_failure("failure_ledger:L37", None)
        _LOST_NOTES[0] += 1


def failure_notes() -> Dict[str, int]:
    """A snapshot of recorded swallowed failures (empty = nothing degraded).

    The reserved key ``__lost__:recorder`` is present only when the recorder
    itself failed, i.e. the real count exceeds the reported one.
    """
    with _FAILURE_LOCK:
        out = dict(_FAILURE_NOTES)
    if _LOST_NOTES[0]:
        out["__lost__:recorder"] = _LOST_NOTES[0]
    return out


def reset_notes() -> None:
    """Clear the ledger (tests only -- production never clears evidence)."""
    with _FAILURE_LOCK:
        _FAILURE_NOTES.clear()
    _LOST_NOTES[0] = 0
