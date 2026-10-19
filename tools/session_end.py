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


def _zerom_review(root: Path) -> None:
    """RULE 0Z-M defect-class capture review (advisory; the hard block is
    pre-commit: staged_scanner_gate + anti_pattern_gate --check). Names the
    exact worktree files needing a coverage decision so the agent cannot
    claim 'nothing to capture'."""
    print("5. RULE 0Z-M capture review (every fixed class -> gate rule or ledger rejection):")
    ledger = root / "state" / "heuristic_ledger.jsonl"
    try:
        lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        import json as _json
        bad = sum(1 for ln in lines if not _json.loads(ln))
        print(f"   ledger: {len(lines)} entries, {bad} invalid lines ({ledger.name})")
    except FileNotFoundError:
        print("   ledger: MISSING state/heuristic_ledger.jsonl -- create it before finishing")
    except Exception as exc:
        print(f"   ledger: UNREADABLE ({exc}) -- fix before finishing")
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain", "--", "src", "tools", "scripts", "tests"],
            timeout=30, capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=str(root))
        touched = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
        if touched:
            print(f"   worktree code files ({len(touched)}) needing a coverage decision:")
            for ln in touched[:20]:
                print(f"     {ln}")
            if len(touched) > 20:
                print(f"     ... +{len(touched) - 20} more")
            print("   For each fix above: gate rule added + baseline, or ledger rejection. "
                  "Undecided = INCOMPLETE per 0Z-M.")
        else:
            print("   worktree clean: nothing to capture.")
    except Exception as exc:
        print(f"   worktree scan failed ({exc})")


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
    _zerom_review(HERE.parent)
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
