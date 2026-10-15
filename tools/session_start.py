#!/usr/bin/env python
# coding: utf-8
"""Session start: pull memory context into this session (one command).

Usage: python tools/session_start.py ["what I am about to do"] [--strict]

Prints PMB context (via the .pmb-venv client) and Engram context (via the
engram binary), so the single pushed session-start instruction delivers
both memory stores instead of PMB alone. It then prints ONE summary line
stating how many characters each store actually delivered.
Runs under ANY interpreter. Exit 0 by default -- context is best-effort and a
session must never be blocked by a memory daemon. `--strict` is the opt-in
gate: it exits 1 when any store delivered nothing.

Why this file no longer just "continues without context" -- measured 2026-10-14
-----------------------------------------------------------------------------
It reported `PMB unreachable` and `engram unreachable` and exited 0 while BOTH
stores had in fact answered. stdout is cp1252 on this host; PMB's payload
carried a raw byte that decoded to U+FFFD and engram's carried U+2192, so the
`print()` raised UnicodeEncodeError INSIDE the per-store `except Exception`,
which then relabelled an OUTPUT failure as a CONNECTION failure. No context was
delivered and rc was 0 -- a false green on the mandated step 1 of the memory
protocol (recorded as engram #706).

So two things that used to be fused are now kept apart:

  * the payload is written through `_emit()`, which degrades a character the
    console cannot encode instead of losing the store's whole payload;
  * each store returns the number of characters it delivered, and `main()`
    prints one summary line naming every store's status. A store that
    delivered nothing is reported as such, with its reason -- never as a pass.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Force UTF-8 and degrade unencodable characters: the default Windows console is
# cp1252 and cannot encode either store's payload. Estate convention -- the same
# block sits in tools/verify_hashes.py and scripts/env_drift_alarm.py.
_RECONFIGURE_ERROR = None
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError) as exc:
        # Not fatal: `_emit()` sanitizes against whatever encoding survives.
        # Recorded rather than discarded so the degraded case stays visible.
        _RECONFIGURE_ERROR = "%s: %s" % (type(exc).__name__, exc)

HERE = Path(__file__).resolve().parent
PMB_PY = Path.home() / ".pmb-venv" / "Scripts" / "python.exe"
CLIENT = HERE / "pmb_client.py"
ENGRAM_PROJECT = os.environ.get("ENGRAM_PROJECT", "azazael")
ENGRAM_BIN = os.environ.get("ENGRAM_BIN") or shutil.which("engram") or str(
    Path.home() / "go" / "bin" / "engram.exe"
)


def _emit(text: str) -> int:
    """Write `text`, degrading characters the console cannot encode.

    Returns the number of characters delivered. Degrading one character is
    strictly better than losing a store's entire payload, and returning the
    count is what lets `main()` report delivered-vs-failed instead of guessing.

    The fallback re-encodes through the console's OWN codec: a UTF-8 round-trip
    would preserve the unprintable character and fail again (the trap
    tools/technique_evidence.py documents). Nothing here is allowed to raise,
    because an output failure raised here would be caught by a store's call
    handler and reported as that store being unreachable -- the defect below.
    """
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    safe = text
    try:
        text.encode(enc)
    except UnicodeEncodeError:
        safe = text.encode(enc, "replace").decode(enc, "replace")
    except (LookupError, ValueError):
        safe = text.encode("utf-8", "replace").decode("utf-8", "replace")
    print(safe)
    return len(safe)


def pmb_context(topic: str) -> "tuple[int, str]":
    """Deliver the PMB context. Returns (chars_delivered, status)."""
    if not PMB_PY.exists() or not CLIENT.exists():
        unavailable = (0, "client unavailable (%s)" % CLIENT)
        return unavailable
    try:
        r = subprocess.run(
            [str(PMB_PY), str(CLIENT), "prepare", topic],
            timeout=90, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(HERE.parent))
    except Exception as exc:  # noqa: BLE001 -- any call failure is a result here
        failure = (0, "call failed (%s: %s)" % (type(exc).__name__, exc))
        return failure
    body = (r.stdout or "").strip()
    if not body:
        empty = (0, "no context returned (rc=%s)" % r.returncode)
        return empty
    # Emitted OUTSIDE the call's try: an output failure is not an unreachable
    # store, and only this separation keeps the two from being confused again.
    return _emit(body[-3000:]), "ok"


def engram_context() -> "tuple[int, str]":
    """Deliver the engram context. Returns (chars_delivered, status)."""
    if not (Path(ENGRAM_BIN).exists() or shutil.which(ENGRAM_BIN)):
        missing = (0, "binary not found (%s)" % ENGRAM_BIN)
        return missing
    try:
        r = subprocess.run(
            [ENGRAM_BIN, "context", ENGRAM_PROJECT],
            timeout=60, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(HERE.parent))
    except Exception as exc:  # noqa: BLE001 -- any call failure is a result here
        failure = (0, "call failed (%s: %s)" % (type(exc).__name__, exc))
        return failure
    out = (r.stdout or "").strip()
    if not out:
        empty = (0, "no context returned (rc=%s)" % r.returncode)
        return empty
    # Head, not tail: engram lists newest-first, so the tail is the
    # oldest/least-relevant material. Cap only if it grows large.
    if len(out) > 12000:
        text = out[:12000] + "\n... [engram context truncated]"
    else:
        text = out
    # Emitted OUTSIDE the call's try, for the same reason as pmb_context().
    return _emit(text), "ok"


def mcp_guard() -> str:
    """Ensure the engram MCP config is loadable, and report the restart verdict.

    Runs at session start so the config is guaranteed HEALTHY before the next
    client start - MCP servers resolve at process start, so nothing done here
    can affect the current session. Full detail (including every error) is
    appended to azazael/state/engram_mcp_restart_log.jsonl.

    Returns a short status string for the summary line; never returns None, so
    "the guard did not run" cannot look like "the guard ran and passed".
    """
    guard = HERE / "verify_engram_mcp.py"
    if not guard.exists():
        return "guard-missing"
    try:
        r = subprocess.run(
            [sys.executable, str(guard)],
            timeout=180, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(HERE.parent))
    except Exception as exc:  # noqa: BLE001 -- report, do not lose the session
        status = "unrunnable (%s)" % type(exc).__name__
        _emit("session_start: MCP guard could not run (%s: %s)"
              % (type(exc).__name__, exc))
        return status

    out = (r.stdout or "").strip()
    warn = [l.strip() for l in out.splitlines() if l.strip().startswith("!!")]
    tail = out.split("RESULT")[-1] if "RESULT" in out else out[-600:]
    _emit("engram MCP guard: exit=%s (0=loaded, 1=needs client restart, 2=errors)"
          % r.returncode)
    for w in warn:
        _emit("  " + w)
    for l in tail.splitlines():
        s = l.strip()
        if s and "====" not in s:
            _emit("  " + s)
    return "exit=%s" % r.returncode


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    topic = args[0] if args else "general Azazael work"

    if _RECONFIGURE_ERROR is not None:
        _emit("session_start: stdout left un-reconfigured (%s); payloads now "
              "degrade to the console codec instead of failing" % _RECONFIGURE_ERROR)

    _emit("=== PMB ===")
    pmb_chars, pmb_status = pmb_context(topic)
    _emit("")
    _emit("=== ENGRAM (%s) ===" % ENGRAM_PROJECT)
    eng_chars, eng_status = engram_context()
    _emit("")
    _emit("=== ENGRAM MCP (restart guard) ===")
    guard_status = mcp_guard()
    _emit("")

    # The whole point of the summary line: a reader can tell "delivered
    # everything" from "delivered nothing" without parsing the payload.
    _emit("session_start: delivered PMB=%dch (%s) engram=%dch (%s) mcp_guard=%s"
          % (pmb_chars, pmb_status, eng_chars, eng_status, guard_status))

    absent = [name for name, chars in (("PMB", pmb_chars), ("engram", eng_chars))
              if chars == 0]
    if absent:
        _emit("session_start: NO CONTEXT from %s -- do not treat this session as "
              "memory-loaded" % ", ".join(absent))
    if strict and absent:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
