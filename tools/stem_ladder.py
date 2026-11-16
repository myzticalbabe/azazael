"""Ladder viewer for the STEM wing.

Reads ``ARC/stem/ladder.json`` and ``ARC/stem/pins.json`` and prints the ladder as
one table, or one rung in full.

This tool does not grade.  ``tools/stem_pins.py`` is the wing's checker: it opens
the cited document, proves each quoted standard sentence is verbatim there, and
returns the verdict ``tools/arc_check.py`` folds into the container's.  Printing a
second verdict here would give one wing two instruments that can disagree, which
is exactly the state ``arc_check.grade_wing`` calls BLIND.  So ``--check``
delegates by running that checker and returning *its* exit code unchanged.

Usage:
    python tools/stem_ladder.py                  # every rung, one line each
    python tools/stem_ladder.py --rung E5         # one rung, every declared field
    python tools/stem_ladder.py --json logs/stem_ladder.json
    python tools/stem_ladder.py --check           # delegate to stem_pins.py
    python tools/stem_ladder.py --check --strict  # ... and fail on declared gaps

Exit codes:
    0  the ladder printed, and every rung joined exactly one pin
    1  the ladder and the ledger do not join: a rung is unpinned, or a pin names
       a rung that is not in the ladder
    2  the ladder or the ledger cannot be read

    ``--check`` does not use the codes above.  It returns stem_pins.py's own:
    0 READY, 1 GAPS, 2 BLIND.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LADDER = ROOT / "ARC" / "stem" / "ladder.json"
DEFAULT_LEDGER = ROOT / "ARC" / "stem" / "pins.json"
CHECKER = ROOT / "tools" / "stem_pins.py"
CHECKER_TIMEOUT = 300  # seconds; the checker only reads two JSON files and a doc

EXIT_OK = 0
EXIT_JOIN = 1
EXIT_BLIND = 2


class Unreadable(Exception):
    """The ladder or the ledger could not be read as JSON."""


def load_json(path: Path, label: str) -> Dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Unreadable("%s could not be read at %s: %s" % (label, path, exc))
    try:
        loaded = json.loads(text)
    except ValueError as exc:
        raise Unreadable("%s is not valid JSON at %s: %s" % (label, path, exc))
    if not isinstance(loaded, dict):
        raise Unreadable("%s at %s holds %s, not an object" % (label, path, type(loaded).__name__))
    return loaded


def join(ladder: Dict[str, Any], ledger: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Pair each rung with its pin.  Returns (rows, join_defects).

    The join is by rung id, on both sides, so an orphaned pin is reported rather
    than silently dropped: a pin nobody reads still claims to back something.
    """
    rungs = [r for r in ladder.get("rungs") or [] if isinstance(r, dict)]
    pins = [p for p in ledger.get("pins") or [] if isinstance(p, dict)]

    by_rung: Dict[str, List[Dict[str, Any]]] = {}
    for pin in pins:
        by_rung.setdefault(str(pin.get("rung")), []).append(pin)

    rows: List[Dict[str, Any]] = []
    defects: List[str] = []
    ladder_rungs = set()

    for rung in rungs:
        rid = str(rung.get("rung"))
        ladder_rungs.add(rid)
        matched = by_rung.get(rid) or []
        if not matched:
            defects.append("%s is in the ladder and has no pin" % rid)
        elif len(matched) > 1:
            defects.append(
                "%s has %d pins (%s); a rung backs one claim"
                % (rid, len(matched), ", ".join(str(p.get("id")) for p in matched))
            )
        rows.append({"rung": rung, "pin": matched[0] if matched else None})

    for rung_id in sorted(by_rung):
        if rung_id not in ladder_rungs:
            defects.append(
                "pin %s names rung %s, which is not in the ladder"
                % (", ".join(str(p.get("id")) for p in by_rung[rung_id]), rung_id)
            )

    return rows, defects


def print_table(rows: List[Dict[str, Any]], ladder: Dict[str, Any]) -> None:
    document = ladder.get("document") or "(no document declared)"
    print("ladder: %s  (%d rungs, document %s)" % (ladder.get("version"), len(rows), document))
    print(
        "  %-4s %-28s %-6s %-8s %-22s %-10s %s"
        % ("rung", "who", "tier", "floor", "instrument", "status", "pin")
    )
    for row in rows:
        rung = row["rung"]
        pin = row["pin"]
        print(
            "  %-4s %-28s %-6s %-8s %-22s %-10s %s"
            % (
                rung.get("rung"),
                str(rung.get("who"))[:28],
                (pin or {}).get("tier", "-"),
                rung.get("min_tier", "-"),
                str(rung.get("instrument"))[:22],
                rung.get("instrument_status", "-"),
                (pin or {}).get("id", "[unpinned]"),
            )
        )
    gaps = ladder.get("declared_gaps") or []
    if gaps:
        print("declared gaps: %d (none of them is a defect; `--rung` shows the detail)" % len(gaps))


def print_rung(row: Dict[str, Any], document: str) -> None:
    rung = row["rung"]
    pin = row["pin"]
    print("%s -- %s" % (rung.get("rung"), rung.get("who")))
    print("  standard   : %s" % rung.get("standard"))
    print("  artifact   : %s" % rung.get("artifact"))
    print("  re-readable: %s" % rung.get("machine_readable"))
    print("  instrument : %s (%s)" % (rung.get("instrument"), rung.get("instrument_status")))
    if rung.get("instrument_invoke"):
        print("  invoke     : %s" % rung.get("instrument_invoke"))
    if rung.get("instrument_note"):
        print("  note       : %s" % rung.get("instrument_note"))
    print("  min tier   : %s" % rung.get("min_tier"))
    print("  fails as   : %s" % rung.get("characteristic_failure"))
    print("  document   : %s" % document)
    if not pin:
        print("  pin        : [unpinned]")
        return
    print("  pin        : %s (tier %s)" % (pin.get("id"), pin.get("tier")))
    print("  demand     : %s" % pin.get("demand"))
    print("  authority  : %s" % pin.get("authority"))
    print("  cite       : %s" % pin.get("cite"))
    print("  text       : %s" % pin.get("text"))
    print("  verified   : %s" % pin.get("verified"))
    print("  satisfied  : %s" % pin.get("satisfied_by"))
    print("  not proved : %s" % pin.get("does_not_prove"))


def delegate(argv: List[str]) -> int:
    """Run the wing's checker and return its exit code unchanged."""
    if not CHECKER.is_file():
        print("reason: checker missing at %s" % CHECKER.relative_to(ROOT))
        return EXIT_BLIND
    cmd = [sys.executable, str(CHECKER)] + argv
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CHECKER_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        print("reason: checker exceeded %ds at %s" % (CHECKER_TIMEOUT, CHECKER.name))
        return EXIT_BLIND
    return proc.returncode


def main(argv: Optional[List[str]] = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    if "--check" in raw:
        # Everything after the tool name belongs to the checker; --check is its
        # own flag and must survive the hand-off.
        return delegate(raw)

    parser = argparse.ArgumentParser(description="Print the STEM ladder (read-only).")
    parser.add_argument("--rung", metavar="ID", help="print one rung in full, e.g. E5")
    parser.add_argument("--json", metavar="PATH", help="write the joined view as JSON")
    parser.add_argument("--ladder", default=str(DEFAULT_LADDER))
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    args = parser.parse_args(raw)

    try:
        ladder = load_json(Path(args.ladder), "ladder")
        ledger = load_json(Path(args.ledger), "ledger")
    except Unreadable as exc:
        print("reason: %s" % exc)
        return EXIT_BLIND

    rows, defects = join(ladder, ledger)
    document = ladder.get("document") or "(no document declared)"

    if args.json:
        out = Path(args.json)
        payload = {
            "ladder": ladder.get("version"),
            "ledger": ledger.get("version"),
            "document": document,
            "rows": [
                {
                    "rung": row["rung"].get("rung"),
                    "who": row["rung"].get("who"),
                    "min_tier": row["rung"].get("min_tier"),
                    "instrument": row["rung"].get("instrument"),
                    "instrument_status": row["rung"].get("instrument_status"),
                    "pin": (row["pin"] or {}).get("id"),
                    "tier": (row["pin"] or {}).get("tier"),
                }
                for row in rows
            ],
            "declared_gaps": ladder.get("declared_gaps") or [],
            "join_defects": defects,
        }
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print("wrote %s" % out)
        except OSError as exc:
            print("reason: view could not be written to %s: %s" % (out, exc))
            return EXIT_BLIND

    if args.rung:
        wanted = args.rung.strip().upper()
        match = [r for r in rows if str(r["rung"].get("rung")).upper() == wanted]
        if not match:
            print(
                "reason: no rung %s in the ladder (%s)"
                % (wanted, ", ".join(str(r["rung"].get("rung")) for r in rows))
            )
            return EXIT_JOIN
        print_rung(match[0], document)
    else:
        print_table(rows, ladder)

    if defects:
        print("join defects: %d" % len(defects))
        for defect in defects:
            print("  [join] %s" % defect)
        return EXIT_JOIN
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
