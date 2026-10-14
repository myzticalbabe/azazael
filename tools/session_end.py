#!/usr/bin/env python
# coding: utf-8
"""Session end: improve pass + record prompt (one command).

Usage: python tools/session_end.py
Prints the azazael-improve checklist with this session's evidence sources
and the exact record command. The agent executes the pass; this script
makes it one step instead of a remembered discipline.
Exit 0 always.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    print("=== SESSION END: improve pass ===")
    print("1. Evidence: state/converge_315.json, PMB outbox, session tool outputs.")
    print("2. Write [IMP-N] items (Observation file:line, Suggestion, Grounded).")
    print("3. Fix trivial now; file the rest as a PMB goal.")
    print("4. Record outcomes now (facts, lessons, goal updates):")
    print()
    print("   C:/Users/clint/.pmb-venv/Scripts/python.exe tools/pmb_capture.py \\")
    print('       --lesson "..." --fact "..." --project azazael')
    print()
    try:
        r = subprocess.run(
            [sys.executable, "-c",
             "import json; m=json.load(open('state/converge_315.json')); "
             "print('converge:', m.get('iteration'), 'live:', m.get('total_live'))"],
            timeout=30, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(HERE.parent))
        print((r.stdout or "").strip() or "(no converge manifest yet)")
    except Exception:
        print("(no converge manifest yet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
