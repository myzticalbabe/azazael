# coding: utf-8
"""PSYCHE — requiem: one durable record for a crash, written while it is crashing.

A crash that leaves no record is re-derived later by someone who was not there,
from a memory of it, badly. The in-process failure ledger counts swallowed
failures; it cannot say what died, where, or with what last words, and it dies
with the process it was watching. This module writes one append-only line per
crash and survives the death it describes.

Two properties decide the design.

**It never raises.** A recorder that throws on a crashing process turns one
failure into two and loses the first. Every path here is inside a guard, and a
write that fails is reported in the record (`recorded: False`, `write_error`)
rather than raised.

**It does not name a cause.** Cause is a judgement, and the moment of the crash
is when judgement is least reliable — the state is half-torn-down, the last
frame is usually a library, and the obvious suspect is whatever was on screen.
So a requiem holds the observation only: the unit, where it surfaced, the
exception, a bounded frame chain, and whatever context the caller passed. The
next reader forms the opinion. A field called `cause` would be filled in every
time and be wrong as often as it was easy.

Usage — inside the handler, before the re-raise:

    from PSYCHE.requiem import requiem, epitaph

    try:
        rt_agent.step(turn)
    except BaseException as exc:
        record = requiem(exc, unit="eliza.psyche.rt_agent",
                         where="rt_agent.step", context={"turn": turn})
        log.error(epitaph(record))
        raise

Read them back with `last()`. A requiem that cannot be read back did not land.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "eliza.requiem/1"
#: Overridable so a service, a test and a lane can each keep their own grave.
ENV_PATH = "ELIZA_REQUIEM_PATH"
DEFAULT_PATH = Path.home() / ".eliza" / "requiem.jsonl"
#: Bounded on purpose: a crash inside a deep recursion must not write a log the
#: size of the stack, and the last frames are the ones that carry the location.
MAX_FRAMES = 8
#: Per-value cap for `context`. Enough to identify the state, not to dump it.
MAX_VALUE_CHARS = 500
MAX_CONTEXT_ITEMS = 24


def grave(path: Optional[os.PathLike | str] = None) -> Path:
    """Where requiems are written: explicit, then `ELIZA_REQUIEM_PATH`, then $HOME."""
    if path is not None:
        return Path(path)
    override = os.environ.get(ENV_PATH)
    return Path(override) if override else DEFAULT_PATH


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _jsonable(value: Any, depth: int = 0) -> Any:
    """Coerce one context value to something JSON can hold. Never raises.

    A crash handler that blows up on an unserializable field is the specific
    failure this function exists to prevent, so every branch falls through to a
    repr, and even the repr is truncated.
    """
    try:
        # Scalars first, then the depth gate. Testing depth first turned every
        # int at nesting level three into its repr (['1', '2']), which reads as
        # a string field and is a quiet corruption of the context it records.
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            return _clip(value)
        if depth > 2:
            return _clip(repr(value))
        if isinstance(value, dict):
            return {str(key)[:60]: _jsonable(item, depth + 1)
                    for key, item in list(value.items())[:MAX_CONTEXT_ITEMS]}
        if isinstance(value, (list, tuple, set, frozenset)):
            return [_jsonable(item, depth + 1) for item in list(value)[:MAX_CONTEXT_ITEMS]]
        return _clip(repr(value))
    except Exception as coercion_error:                # never raise from the recorder
        reason = type(coercion_error).__name__
        return "<unrepresentable: %s>" % reason


def _clip(text: str) -> str:
    return text if len(text) <= MAX_VALUE_CHARS else text[:MAX_VALUE_CHARS] + "..."


def _frames(exc: BaseException) -> List[Dict[str, Any]]:
    """The tail of the stack, innermost last. Where it died, not where it started."""
    out: List[Dict[str, Any]] = []
    try:
        extracted = traceback.extract_tb(exc.__traceback__)
        for frame in extracted[-MAX_FRAMES:]:
            out.append({"file": frame.filename, "line": frame.lineno,
                        "func": frame.name})
    except Exception as frames_error:
        # A missing chain is recorded as missing, not swallowed: a requiem whose
        # frames silently vanished would read as a crash with no location.
        out.append({"file": "<unavailable>", "line": 0,
                    "func": type(frames_error).__name__})
    return out


def requiem(exc: BaseException, *, unit: str, where: str,
            context: Optional[Dict[str, Any]] = None,
            path: Optional[os.PathLike | str] = None) -> Dict[str, Any]:
    """Record one crash. Returns the record, whether or not the write landed.

    `exc` is whatever was caught — `BaseException`, so a `SystemExit` or a
    `KeyboardInterrupt` gets a requiem too. The caller keeps the exception and
    should re-raise it: this records the death, it does not preside over it.
    """
    target = grave(path)
    record: Dict[str, Any] = {
        "schema": SCHEMA,
        "at": _now(),
        "unit": str(unit),
        "where": str(where),
        "error": {
            "type": type(exc).__name__,
            "module": type(exc).__module__,
            "message": _clip(str(exc)),
        },
        "frames": _frames(exc),
        "context": _jsonable(context or {}),
        "process": {"pid": os.getpid()},
        "path": str(target),
        "recorded": False,
    }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, sort_keys=True, default=repr)
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")
        record["recorded"] = True
    except Exception as write_error:                   # never raise from the recorder
        record["write_error"] = "%s: %s" % (type(write_error).__name__, write_error)
    return record


def epitaph(record: Dict[str, Any]) -> str:
    """One line for the log: who fell, where, and of what — not why."""
    error = record.get("error") or {}
    fell = "%s at %s" % (record.get("unit", "?"), record.get("where", "?"))
    died_of = "%s: %s" % (error.get("type", "?"), error.get("message", ""))
    if record.get("recorded"):
        return "requiem — %s, of %s [%s]" % (fell, died_of, record.get("path"))
    return ("requiem NOT recorded (%s) — %s, of %s"
            % (record.get("write_error", "unknown"), fell, died_of))


def last(limit: int = 1,
         path: Optional[os.PathLike | str] = None) -> List[Dict[str, Any]]:
    """The most recent requiems, newest last. Empty list = nothing has died here.

    An empty list is a reading about the grave, not about the running code: a
    process that crashed before it could write has left no trace in it. A grave
    that exists but cannot be read raises, because returning `[]` there would
    report "nothing died" about a file whose contents are unknown.
    """
    target = grave(path)
    if not target.is_file():
        return []
    out: List[Dict[str, Any]] = []
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                # A torn line can only be the last one: the file is append-only
                # and a partial write means the process died mid-line. Stop
                # there, so nothing after a tear is read as a whole record.
                break
    return out[-limit:] if limit > 0 else out
