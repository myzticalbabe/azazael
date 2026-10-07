#!/usr/bin/env python
# coding: utf-8
"""Session start: pull PMB context into this session (one command).

Usage: python tools/session_start.py ["what I am about to do"]
Runs under ANY interpreter: delegates to the .pmb-venv client.
Exit 0 always (context is best-effort, never blocking).
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PMB_PY = Path.home() / ".pmb-venv" / "Scripts" / "python.exe"
CLIENT = HERE / "pmb_client.py"


def main() -> int:
    topic = sys.argv[1] if len(sys.argv) > 1 else "general Azazael work"
    if not PMB_PY.exists() or not CLIENT.exists():
        print("session_start: PMB client unavailable, continuing without context")
        return 0
    try:
        r = subprocess.run(
            [str(PMB_PY), str(CLIENT), "prepare", topic],
            timeout=90, capture_output=True, text=True, errors="replace",
            cwd=str(HERE.parent))
        print(r.stdout[-3000:] if r.stdout else "(no context returned)")
    except Exception as e:
        print(f"session_start: PMB unreachable ({e}), continuing without context")
    return 0


if __name__ == "__main__":
    sys.exit(main())
