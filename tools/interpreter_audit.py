#!/usr/bin/env python3
"""interpreter_audit.py -- G3: measure the interpreter that gates commits.

The commit hook pins an interpreter, and the canon states which one it should
be. Those are two different documents, and until this tool existed nothing
compared them: the hook would keep running whatever it pins while the canon
kept claiming production parity, and every "the suite passes under 3.16t"
sentence would be answering for a tree the hook does not actually check.

This tool is a MEASUREMENT, not a ruling. It:

  1. reads the `PYTHON3=` pin out of `.githooks/pre-commit` (the interpreter
     that really gates a commit),
  2. RUNS that interpreter and records its real version and GIL state,
  3. reads the version the canon claims commit hooks use, from AGENTS.md,
  4. reports MATCH / DRIFTED / UNMEASURABLE, and prints why.

It does not move the pin. Which interpreter gates commits is a policy call with
a cost on both sides (production parity vs. the packages that only build for the
GIL sidecar), so the decision is printed as open and left to the principal.

Verdicts:

  MATCH         hook pin measures the same major.minor as the canon claim
  DRIFTED       hook pin measures a different version than the canon claims
  UNMEASURABLE  the pin is absent, malformed, or the interpreter will not run

Exit: 0 when measured (advisory), 1 under --strict when DRIFTED, 2 when the
audit could not be performed at all.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / ".githooks" / "pre-commit"
CANON = Path("C:/Azazael/AGENTS.md")

PIN_RE = re.compile(r'^\s*PYTHON3="([^"]+)"', re.MULTILINE)
# The canon sentence that makes the claim this tool checks.
CLAIM_RE = re.compile(r"commit hooks?[^\n]{0,80}?3\.(\d+)t", re.IGNORECASE)
PROBE = "import sys, json; print(json.dumps([list(sys.version_info[:3]), "
PROBE += "bool(sys._is_gil_enabled())]))"


def _pin() -> tuple[str | None, str]:
    """The interpreter the hook pins, and a note when it cannot be read."""
    if not HOOK.is_file():
        return None, "no %s on disk" % HOOK.name
    text = HOOK.read_text(encoding="utf-8", errors="replace")
    m = PIN_RE.search(text)
    if not m:
        return None, "no PYTHON3= line in the hook"
    return m.group(1), ""


def _probe(exe: str) -> tuple[tuple[str, bool] | None, str]:
    """Run the pin and return ((version, gil_enabled), note).

    The failure note is part of the return value on purpose. An audit whose
    unmeasurable branch cannot say WHY is indistinguishable from one that
    swallowed an exception, and this tool exists to remove that ambiguity from
    the interpreter question.
    """
    try:
        proc = subprocess.run(
            [exe, "-c", PROBE], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return None, "pinned interpreter will not run: %s" % type(exc).__name__
    if proc.returncode != 0:
        return None, "probe returned rc=%d" % proc.returncode
    try:
        parts = json.loads((proc.stdout or "").strip())
        major, minor, _micro = parts[0]
        gil = bool(parts[1])
    except (ValueError, IndexError, TypeError) as exc:
        return None, "probe output unparseable: %s" % type(exc).__name__
    return ("%d.%d" % (major, minor), gil), ""


def _claim(path: Path) -> tuple[str | None, str]:
    """The major.minor the canon says commit hooks use."""
    if not path.is_file():
        return None, "canon not readable at %s" % path
    text = path.read_text(encoding="utf-8", errors="replace")
    m = CLAIM_RE.search(text)
    if not m:
        return None, "canon states no version for commit hooks"
    return "3.%s" % m.group(1), ""


def audit(canon: Path) -> dict[str, object]:
    exe, pin_note = _pin()
    claimed, claim_note = _claim(canon)
    measured, probe_note = _probe(exe) if exe else (None, "no pin to run")

    if exe is None or measured is None:
        verdict = "UNMEASURABLE"
        detail = pin_note or probe_note or "pinned interpreter gave no reading"
    elif claimed is None:
        verdict = "UNMEASURABLE"
        detail = claim_note
    elif measured[0] == claimed:
        verdict = "MATCH"
        detail = "hook pin measures %s, canon claims %s" % (measured[0], claimed)
    else:
        verdict = "DRIFTED"
        detail = "hook pin measures %s, canon claims %s" % (measured[0], claimed)

    return {
        "verdict": verdict,
        "detail": detail,
        "pin": exe,
        "pin_note": pin_note,
        "measured_version": measured[0] if measured else None,
        "gil_enabled": measured[1] if measured else None,
        "canon_claim": claimed,
        "canon_note": claim_note,
        "decision": "OPEN (G3)",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when the hook pin drifts from the canon claim")
    ap.add_argument("--canon", default=str(CANON),
                    help="instruction file that states the claim")
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    args = ap.parse_args(argv)

    result = audit(Path(args.canon))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Verdict FIRST, then the three readings it rests on. The hyper_edge
        # leg quotes the first line; `pin C:/Azazael/.venvs/py315t/...` as that
        # line states a fact about a file and no verdict at all, so a drifted
        # hook would have read as an ordinary line of configuration.
        print("interpreter_audit: %s -- %s"
              % (result["verdict"], result["detail"]))
        print("interpreter_audit: pin      %s" % (result["pin"] or "<none>"))
        print("interpreter_audit: measured %s  gil_enabled=%s"
              % (result["measured_version"] or "<unmeasurable>",
                 result["gil_enabled"]))
        print("interpreter_audit: canon    %s"
              % (result["canon_claim"] or "<no claim>"))
        print("interpreter_audit: DECISION OPEN (G3) -- which interpreter gates "
              "commits is the principal's call; this tool measures the pin, it "
              "does not move it.")

    if result["verdict"] == "UNMEASURABLE":
        return 2
    if args.strict and result["verdict"] == "DRIFTED":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
