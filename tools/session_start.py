#!/usr/bin/env python
# coding: utf-8
"""Session start: pull memory context into this session (one command).

Usage: python tools/session_start.py ["what I am about to do"]
Prints PMB context (via the .pmb-venv client) and Engram context (via the
engram binary), so the single pushed session-start instruction delivers
both memory stores instead of PMB alone.
Runs under ANY interpreter. Exit 0 always (context is best-effort, never
blocking).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PMB_PY = Path.home() / ".pmb-venv" / "Scripts" / "python.exe"
CLIENT = HERE / "pmb_client.py"
ENGRAM_PROJECT = os.environ.get("ENGRAM_PROJECT", "azazael")
ENGRAM_BIN = os.environ.get("ENGRAM_BIN") or shutil.which("engram") or str(
    Path.home() / "go" / "bin" / "engram.exe"
)


def pmb_context(topic: str) -> None:
    if not PMB_PY.exists() or not CLIENT.exists():
        print("session_start: PMB client unavailable, continuing without context")
        return
    try:
        r = subprocess.run(
            [str(PMB_PY), str(CLIENT), "prepare", topic],
            timeout=90, capture_output=True, text=True, errors="replace",
            cwd=str(HERE.parent))
        print(r.stdout[-3000:] if r.stdout else "(no context returned)")
    except Exception as e:
        print(f"session_start: PMB unreachable ({e}), continuing without context")


def engram_context() -> None:
    if not (Path(ENGRAM_BIN).exists() or shutil.which(ENGRAM_BIN)):
        print("session_start: engram binary not found, continuing without engram context")
        return
    try:
        r = subprocess.run(
            [ENGRAM_BIN, "context", ENGRAM_PROJECT],
            timeout=60, capture_output=True, text=True, errors="replace",
            cwd=str(HERE.parent))
        out = (r.stdout or "").strip()
        # Head, not tail: engram lists newest-first, so the tail is the
        # oldest/least-relevant material. Cap only if it grows large.
        if not out:
            print("(no engram context returned)")
        elif len(out) > 12000:
            print(out[:12000] + "\n... [engram context truncated]")
        else:
            print(out)
    except Exception as e:
        print(f"session_start: engram unreachable ({e}), continuing without engram context")


def mcp_guard() -> None:
    """Ensure the engram MCP config is loadable, and report the restart verdict.

    Runs at session start so the config is guaranteed HEALTHY before the next
    client start - MCP servers resolve at process start, so nothing done here
    can affect the current session. Full detail (including every error) is
    appended to azazael/state/engram_mcp_restart_log.jsonl.
    """
    guard = HERE / "verify_engram_mcp.py"
    if not guard.exists():
        print("session_start: MCP guard not found, skipping")
        return
    try:
        r = subprocess.run(
            [sys.executable, str(guard)],
            timeout=180, capture_output=True, text=True, errors="replace",
            cwd=str(HERE.parent))
    except Exception as e:
        print(f"session_start: MCP guard could not run ({e})")
        return

    out = (r.stdout or "").strip()
    warn = [l.strip() for l in out.splitlines() if l.strip().startswith("!!")]
    tail = out.split("RESULT")[-1] if "RESULT" in out else out[-600:]
    print(f"engram MCP guard: exit={r.returncode} "
          "(0=loaded, 1=needs client restart, 2=errors)")
    for w in warn:
        print("  " + w)
    for l in tail.splitlines():
        s = l.strip()
        if s and "====" not in s:
            print("  " + s)


def main() -> int:
    topic = sys.argv[1] if len(sys.argv) > 1 else "general Azazael work"
    print("=== PMB ===")
    pmb_context(topic)
    print()
    print(f"=== ENGRAM ({ENGRAM_PROJECT}) ===")
    engram_context()
    print()
    print("=== ENGRAM MCP (restart guard) ===")
    mcp_guard()
    return 0


if __name__ == "__main__":
    sys.exit(main())
