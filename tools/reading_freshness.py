#!/usr/bin/env python3
"""Reading freshness -- a verdict older than its tree is stale, not a pass.

The class this catches, measured 2026-11-14: ``logs/deep_dive.json`` reported
``ok  golden_arrow_status  588 file(s), 572 passed, 16 failed (run
2026-11-09T10:01:05Z)`` -- a five-day-old suite result counted as one of today's
legs, while ``src/`` and ``tools/`` had changed under it. The leg's own docstring
says "no report means no reading, not a pass"; the sibling defect is a report
that exists and is *older than the inputs it describes*, which no existing leg
checked. ``tools/artifact_freshness.py`` answers a different question (a
REGISTRY of derived artifacts against their declared sources); this one asks
whether any logged reading in ``logs/`` and ``state/`` was taken before the code
it is quoted against.

The clock is the newest **commit** touching ``src/`` or ``tools/``, not the
newest mtime. Measured 2026-11-14: with mtime as the clock, editing one tool
declared 18 artifacts stale by "0.0 day(s)" -- the instrument fires on the
session, not on the tree, and a check that always fires is a check that gets
ignored. A commit is a durable statement about the tree; an mtime is a statement
about this checkout's filesystem. When git cannot be asked, the tool falls back
to mtime and *says so in the reading* -- which clock produced a verdict is part
of the verdict.

An artifact with no parseable timestamp is UNDATABLE -- reported, never counted
as fresh, because a verdict that cannot say when it was taken cannot say what it
is a verdict about.

Exit: 0 reported (advisory), 1 under --strict when any reading is stale, 2 when
no artifact could be read at all (which is not a pass).
"""
from __future__ import annotations

import argparse
import calendar
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: This file's own path, excluded from the input scan in the mtime fallback.
#: Measured 2026-11-14: the auditor's own mtime became "newest input", so every
#: artifact edited before it was reported STALE by 0.0 days -- an instrument
#: declaring each verdict invalid because the instrument was written later. Its
#: own bytes are not an input to any artifact, so it is not a clock here.
SELF = Path(__file__).resolve()

#: Wall bound the deep-dive leg reads off this module. Measured 2026-11-14: the
#: scan is a git call plus ~180 file reads, under 2 s; 120 s is the shape of a
#: hung stat on a network path, not of a slow read.
BUDGET_S = 120

#: Directories whose edits invalidate a verdict about this tree.
INPUTS = ("src", "tools")

#: Keys artifacts in this tree actually use for "when was this taken".
#: Measured 2026-11-14 over 181 artifacts in logs/ and state/: 156 were undatable
#: with the first vocabulary, and the three shapes it missed were not exotic --
#: `at` (20 files, ISO), `when` (1, ISO) and `time` (7, epoch MILLIseconds as a
#: string). A reading vocabulary that omits the key a sub-tree actually writes
#: reports its dates as absent, which is the stronger and wrong claim.
# A stamp shape is recognised by what it LOOKS like, before strptime is asked.
DATE_SHAPES = (
    (re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"), "%Y-%m-%dT%H:%M:%S"),
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"), "%Y-%m-%d %H:%M:%S"),
    (re.compile(r"^\d{4}-\d{2}-\d{2}"), "%Y-%m-%d"),
)

TIME_KEYS = ("generated", "generated_at", "ran_at", "built_at", "timestamp",
             "ts", "date", "updated", "updated_at", "collected_at",
             "at", "when", "time")

#: Plausible epoch range (2001-09-09 .. 2100-01-01): an epoch-looking string is
#: only a timestamp inside it, so a `time` field holding a duration or a counter
#: is refused rather than reported as a 1970-era reading.
EPOCH_MIN, EPOCH_MAX = 1_000_000_000, 4_102_444_800

SEARCH = ("logs/*.json", "state/*.json")


def newest_commit() -> tuple[float, str]:
    """Newest commit epoch touching INPUTS, with a human description.

    Returns ``(0.0, "")`` when git cannot answer, so the caller can fall back
    and name the fallback rather than inventing a clock.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%ct %h %ad", "--date=short",
             "--", *INPUTS],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return 0.0, "git unavailable (%s)" % type(exc).__name__
    out = (proc.stdout or "").strip()
    if proc.returncode != 0 or not out:
        return 0.0, "git could not name a commit touching %s" % (INPUTS,)
    parts = out.split(None, 2)
    try:
        epoch = float(parts[0])
    except (IndexError, ValueError):
        return 0.0, "git output unparsable (%r)" % out[:60]
    return epoch, "commit %s %s" % (parts[1], parts[2] if len(parts) > 2 else "")


def newest_input_mtime(skipped: list[str]) -> tuple[float, str]:
    """Fallback clock: newest file mtime under INPUTS, SELF excluded.

    A path that cannot be stat'ed is appended to ``skipped`` rather than
    dropped: the clock is then the newest of the readable files, and the
    reading says how many it could not see.
    """
    newest, where = 0.0, ""
    for name in INPUTS:
        base = ROOT / name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.resolve() == SELF:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError as exc:
                skipped.append("%s (%s)" % (path.name, type(exc).__name__))
                continue
            if mtime > newest:
                newest, where = mtime, path.relative_to(ROOT).as_posix()
    return newest, "mtime %s" % (where or "none")


def clock(skipped: list[str]) -> tuple[float, str]:
    """The tree's timestamp and the name of the clock that produced it."""
    epoch, how = newest_commit()
    if epoch > 0:
        return epoch, how
    epoch, how = newest_input_mtime(skipped)
    return epoch, how


def artifact_time(data, unparsed: list[str] | None = None) -> float | None:
    """Best timestamp the artifact can offer, as epoch seconds (UTC-correct).

    A value that is present but unreadable is appended to ``unparsed`` so the
    caller can report it; a silently skipped key looks exactly like an absent
    one, and "no timestamp" is a stronger claim than "one I could not parse".
    """
    if unparsed is None:
        unparsed = []
    if not isinstance(data, dict):
        return None
    for key in TIME_KEYS:
        if key not in data:
            continue
        value = data[key]
        if isinstance(value, (int, float)) and value > 1_000_000_000:
            return float(value)
        if isinstance(value, str) and value.strip():
            # Measured 2026-11-14: 12 artifacts store the stamp as a quoted
            # string (``"generated": "'2026-10-17'"``), so the quote is part of
            # the value and strptime refuses it. Normalise before parsing.
            text = value.strip().strip("'\"")
            # Epoch seconds (10 digits) or milliseconds (13) stored as a string.
            # Measured 2026-11-14: 7 artifacts carry `time: '1793683625085'`, and
            # reading that as a date string made a written stamp look absent.
            if text.isdigit() and len(text) in (10, 13):
                seconds = int(text) / (1000.0 if len(text) == 13 else 1.0)
                if EPOCH_MIN <= seconds <= EPOCH_MAX:
                    return seconds
            # ``Z`` is UTC; mktime() would read it as local time and skew every
            # comparison by the zone offset (measured: -0500 here).
            utc = text.endswith("Z")
            text = text[:-1] if utc else text
            # Date-only is a real timestamp in this tree (measured: 12 artifacts
            # carry ``generated: 2026-10-17``); refusing it would report a date
            # as an absent one, which is the stronger and wrong claim.
            #
            # The failure is recorded ONLY when every shape failed. Measured
            # 2026-11-14: appending inside the loop counted a date-only stamp as
            # two unparsable values before the 10-character shape matched, so the
            # reading reported 18 unparsable stamps that had all parsed -- a
            # count inflated by the order the shapes are tried is a wrong number,
            # not a conservative one.
            # A regex decides WHICH shape applies, so strptime is only called on
            # a string that already matches it and cannot raise. Measured
            # 2026-11-14: probing shapes with try/except and `continue` added a
            # silent_except_continue the staged scanner blocks -- and the
            # blocker was right, because a swallowed ValueError is how a stamp
            # silently becomes "absent". The shape test is a match, not an
            # exception.
            parsed = None
            for pattern, shape in DATE_SHAPES:
                hit = pattern.match(text)
                if hit is not None:
                    parsed = time.strptime(hit.group(0), shape)
                    break
            if parsed is None:
                unparsed.append("%s=%r" % (key, text[:24]))
                continue
            return float(calendar.timegm(parsed) if utc
                         else time.mktime(parsed))
    return None


def run(strict: bool = False) -> tuple[int, list[dict], dict]:
    skipped: list[str] = []
    unparsed: list[str] = []
    tree_time, clock_name = clock(skipped)
    rows: list[dict] = []
    for pattern in SEARCH:
        for path in sorted(ROOT.glob(pattern)):
            rel = path.relative_to(ROOT).as_posix()
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                rows.append({"artifact": rel, "state": "UNREADABLE",
                             "detail": str(exc)[:120]})
                continue
            taken = artifact_time(data, unparsed)
            if taken is None:
                rows.append({"artifact": rel, "state": "UNDATABLE",
                             "detail": "no timestamp key among %s"
                                       % (TIME_KEYS,)})
                continue
            if taken < tree_time:
                days = (tree_time - taken) / 86400.0
                rows.append({"artifact": rel, "state": "STALE",
                             "detail": "%.1f day(s) older than %s"
                                       % (days, clock_name)})
            else:
                rows.append({"artifact": rel, "state": "FRESH", "detail": ""})
    if not rows:
        print("reading_freshness: no artifact under %s -- nothing read"
              % (SEARCH,))
        return 2, [], {"artifacts": 0}
    stale = [r for r in rows if r["state"] == "STALE"]
    undatable = [r for r in rows if r["state"] == "UNDATABLE"]
    unreadable = [r for r in rows if r["state"] == "UNREADABLE"]
    # Summary first: the deep-dive leg parses the FIRST line as the reading, and
    # a first line naming one stale artifact carries no denominator (HED-9).
    print("reading_freshness: %d artifact(s), %d stale, %d undatable, %d"
          " unreadable | clock %s (tree %.1f day(s) old) | unreadable inputs %d,"
          " unparsable stamp(s) %d"
          % (len(rows), len(stale), len(undatable), len(unreadable), clock_name,
             max(0.0, (time.time() - tree_time) / 86400.0), len(skipped),
             len(unparsed)))
    for note in skipped:
        print("  INPUT-UNREAD " + note)
    for note in unparsed:
        print("  STAMP-UNPARSED " + note)
    for r in stale:
        print("  STALE      %s  (%s)" % (r["artifact"], r["detail"]))
    for r in undatable:
        print("  UNDATABLE  %s  (%s)" % (r["artifact"], r["detail"]))
    for r in unreadable:
        print("  UNREADABLE %s  (%s)" % (r["artifact"], r["detail"]))
    stats = {"artifacts": len(rows), "stale": len(stale),
             "undatable": len(undatable), "unreadable": len(unreadable),
             "clock": clock_name, "inputs_unread": len(skipped),
             "stamps_unreadable": len(unparsed)}
    if strict and (stale or unreadable):
        return 1, rows, stats
    return 0, rows, stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any reading is stale or unreadable")
    ap.add_argument("--json", default="", help="write rows to this path")
    args = ap.parse_args(argv)
    code, rows, stats = run(strict=args.strict)
    if args.json:
        Path(args.json).write_text(json.dumps({"stats": stats, "rows": rows},
                                              indent=2), encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
