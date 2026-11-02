# coding: utf-8
"""memory_bridge -- the prompter's memory, with its absence stated instead of implied.

WHY A BRIDGE AND NOT AN IMPORT
------------------------------
The defender must stay stdlib-only and portable: it is pointed at repositories it has
never seen, on machines that have no PMB daemon, no Engram store and no Plex. Importing
the estate's memory libraries would make the prompter fail exactly where it is most
useful -- on someone else's tree.

So memory arrives through two declared adapters, and when neither answers the result is
**UNMEMORED**, not "no lessons found". The distinction is the whole file:

  * `no lessons matched your query` is a fact about the world.
  * `the memory backend did not answer` is a fact about this run.

Reporting the second as the first is the estate's most expensive recurring defect: a
recall that returns nothing because the store was unreachable reads as evidence that
nothing was ever learned. Here the state is in the return value, the CLI prints it, and a
frame built on an UNMEMORED lookup carries that word into the prompt.

ADAPTERS
--------
  jsonl     a file of records (one JSON object per line). The prompter's own lesson
            ledger, `.flaming_sword/lessons.jsonl`, is this shape.
  command   any command that prints JSON lines on stdout -- this is how the estate points
            the bridge at PMB, Engram or the board without teaching this file their
            schemas. It is split ARGV-style and never run through a shell, so a pipeline
            must be written as `sh -c '<pipeline>'` at the call site. A command that exits
            non-zero, prints nothing parseable, or times out is UNMEMORED with its reason.

Writes go to `.flaming_sword/frames.jsonl` (append-only, one frame per line), which is
also what M-42's sweep will read to require a frame per queued id.

USAGE
-----
    python tools/memory_bridge.py --probe
    python tools/memory_bridge.py --recall "shard validator" --jsonl .flaming_sword/lessons.jsonl
    python tools/memory_bridge.py --command "python tools/recall.py --jsonl" --recall "x"
    python tools/memory_bridge.py --selftest
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

MEMORY = "MEMORY"
UNMEMORED = "UNMEMORED"

STATE_DAY_DIR = ".flaming_sword"
FRAMES_FILE = "frames.jsonl"
LESSONS_FILE = "lessons.jsonl"
VERIFICATIONS_FILE = "verifications.jsonl"

#: The lessons ledger is THE GRIMOIRE: the book the cradle keeps. One line per thing
#: that failed or was refused, written at the moment it failed, because a reconstruction
#: at session end keeps whatever is still salient and loses the rest. The FILE NAME stays
#: `lessons.jsonl` -- ledgers already on disk are that name, and a book you have to
#: migrate to read is a book you stop reading.
GRIMOIRE = LESSONS_FILE
GRIMOIRE_NAME = "GRIMOIRE"

#: Appending the same lesson twice is how a ledger becomes noise: the reader sees
#: "learned 40 times" and stops believing any of it. Content is hashed and an exact
#: repeat is skipped (the estate's own dedupe rule, and the reason a count means count).
import hashlib  # noqa: E402  (kept beside the constant it serves)

_COMMAND_TIMEOUT = 20


# --------------------------------------------------------------------------- #
# Adapters
# --------------------------------------------------------------------------- #

def _read_jsonl(path: Path) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Return (records, error). A malformed line is an error, not a skipped line."""
    records: List[Dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [], "unreadable: %s" % exc
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except ValueError as exc:
            return records, "line %d is not JSON (%s)" % (number, exc)
        if not isinstance(record, dict):
            return records, "line %d is not an object" % number
        records.append(record)
    return records, None


def _run_command(command: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Run the adapter command as ARGV, never through a shell.

    The first version passed the string to `shell=True`, and the staged scanner refused
    it as a new anti-pattern -- correctly: the command adapter would have been an
    injection surface fed by whatever a caller typed. Splitting argv-style costs pipes
    (an adapter that needs one writes `sh -c '<pipeline>'`, which is explicit at the call
    site) and buys the property that matters: no prompt-derived value can ever become a
    shell fragment.
    """
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return [], "the command is not parseable as argv (%s)" % exc
    if not argv:
        return [], "the command is empty"
    try:
        completed = subprocess.run(argv, capture_output=True, text=True,
                                   timeout=_COMMAND_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        return [], "the command could not run: %s" % exc
    if completed.returncode != 0:
        return [], "the command exited %d (stderr: %s)" % (
            completed.returncode, (completed.stderr or "").strip()[:120])
    records: List[Dict[str, Any]] = []
    for number, line in enumerate((completed.stdout or "").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            return records, "stdout line %d is not JSON; the adapter contract is one " \
                            "object per line" % number
        if not isinstance(record, dict):
            return records, "stdout line %d is not an object" % number
        records.append(record)
    return records, None


def probe(jsonl: Optional[str] = None, command: Optional[str] = None) -> Dict[str, Any]:
    """Answer 'is there a memory behind this run' without pretending either way."""
    if command:
        records, error = _run_command(command)
        if error:
            return {"state": UNMEMORED, "backend": "command", "reason": error,
                    "records": 0}
        return {"state": MEMORY, "backend": "command", "reason": "", "records": len(records)}
    if jsonl:
        path = Path(jsonl)
        if not path.exists():
            return {"state": UNMEMORED, "backend": "jsonl",
                    "reason": "%s does not exist" % path, "records": 0}
        records, error = _read_jsonl(path)
        if error:
            return {"state": UNMEMORED, "backend": "jsonl", "reason": error,
                    "records": len(records)}
        return {"state": MEMORY, "backend": "jsonl", "reason": "", "records": len(records)}
    return {"state": UNMEMORED, "backend": "none",
            "reason": "no memory backend configured (--jsonl or --command); this is not "
                      "the same as no lessons existing",
            "records": 0}


# --------------------------------------------------------------------------- #
# Recall
# --------------------------------------------------------------------------- #

def _haystack(record: Dict[str, Any]) -> str:
    fields = ("content", "lesson", "text", "summary", "title", "claim", "note")
    return " ".join(str(record.get(field) or "") for field in fields).lower()


def recall(query: str, jsonl: Optional[str] = None, command: Optional[str] = None,
           limit: int = 5) -> Dict[str, Any]:
    """Return {state, backend, reason, matches}. Matches carry their backend label."""
    state = probe(jsonl=jsonl, command=command)
    if state["state"] != MEMORY:
        return {**state, "matches": []}
    records, error = (_run_command(command) if command else _read_jsonl(Path(jsonl or "")))
    if error:
        return {"state": UNMEMORED, "backend": state["backend"], "reason": error,
                "matches": []}
    terms = [t for t in str(query or "").lower().split() if len(t) > 2]
    scored: List[Tuple[int, Dict[str, Any]]] = []
    for record in records:
        hay = _haystack(record)
        score = sum(1 for term in terms if term in hay)
        if score:
            scored.append((score, record))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    matches = [{"score": score, "backend": state["backend"],
                "content": str(record.get("content") or record.get("lesson")
                               or record.get("text") or record)[:400]}
               for score, record in scored[:limit]]
    return {"state": MEMORY, "backend": state["backend"], "reason": "",
            "matches": matches, "records": len(records)}


# --------------------------------------------------------------------------- #
# Writing
# --------------------------------------------------------------------------- #

def _append(state_dir: Optional[str], filename: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    directory = Path(state_dir) if state_dir else Path.cwd() / STATE_DAY_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return {"path": str(path), "bytes": path.stat().st_size, "entry": entry}


def record_lesson(content: str, kind: str = "lesson", tags: Optional[Sequence[str]] = None,
                  trigger: str = "", state_dir: Optional[str] = None) -> Dict[str, Any]:
    """Write a lesson to `.flaming_sword/lessons.jsonl`, which recall reads.

    WHY THIS EXISTS: the bridge could read a ledger and nothing ever wrote one, so every
    run reported UNMEMORED and the honesty of that report hid an empty pipe. A memory is
    only a memory when the loop closes -- so the loop closes here, at the moment a
    verification fails or a task lands, not at the end of a session.
    """
    text = (content or "").strip()
    if len(text) < 24:
        raise ValueError("a lesson under 24 characters decides nothing: %r" % text)
    digits = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    directory = Path(state_dir) if state_dir else Path.cwd() / STATE_DAY_DIR
    ledger = directory / LESSONS_FILE
    if ledger.exists():
        records, _error = _read_jsonl(ledger)
        for record in records:
            if record.get("sha") == digits:
                return {"path": str(ledger), "skipped": "duplicate", "sha": digits,
                        "entry": record}
    from datetime import datetime, timezone

    entry = {"sha": digits, "content": text, "kind": kind, "tags": list(tags or []),
             "trigger": trigger,
             "written_at": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
    written = _append(state_dir, LESSONS_FILE, entry)
    written["skipped"] = ""
    return written


def record_verification(frame_id: str, command: str, exit_code: int,
                        observed: str = "", state_dir: Optional[str] = None) -> Dict[str, Any]:
    """Record whether the acceptance command was actually run, and with what result.

    A mismatch is written as a LESSON automatically. That is the authorship campaign in
    one line: the thing that went wrong is stored where the next frame will recall it,
    without a human remembering to write it down.
    """
    verdict = "VERIFIED" if exit_code == 0 else "FAILED"
    entry = {"frame_id": frame_id, "command": command, "exit_code": int(exit_code),
             "observed": (observed or "")[:500], "verdict": verdict}
    written = _append(state_dir, VERIFICATIONS_FILE, entry)
    written["verdict"] = verdict
    if verdict == "FAILED":
        written["lesson"] = record_lesson(
            "the acceptance command for frame %s exited %d: %s" % (frame_id, exit_code,
                                                                  command),
            kind="failed-verification", tags=["verification", "frame"],
            trigger=command, state_dir=state_dir)
    return written


def record(frame: Dict[str, Any], state_dir: Optional[str] = None) -> Dict[str, Any]:
    """Append one frame to `.flaming_sword/frames.jsonl`. Returns where it landed."""
    directory = Path(state_dir) if state_dir else Path.cwd() / STATE_DAY_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / FRAMES_FILE
    entry = {
        "frame_id": frame.get("frame_id"),
        "intent": frame.get("intent"),
        "target": frame.get("target"),
        "defends": frame.get("defends"),
        "must_not_break": frame.get("must_not_break"),
        "acceptance": frame.get("acceptance"),
        "control": frame.get("control"),
        "refusal": frame.get("refusal"),
        "evidence": frame.get("evidence"),
        "shape": frame.get("shape"),
        "draft": bool(frame.get("draft")),
        "preserve": bool(frame.get("preserve")),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return {"path": str(path), "bytes": path.stat().st_size, "entry": entry}


# --------------------------------------------------------------------------- #
# Controls
# --------------------------------------------------------------------------- #

def selftest() -> Tuple[int, List[str]]:
    lines: List[str] = []
    failures = 0

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        lessons = tmp_path / LESSONS_FILE
        lessons.write_text(
            json.dumps({"content": "a shard validator must refuse a stale state_sha256"})
            + "\n" +
            json.dumps({"content": "the defender's posture must state bytes_of_original"})
            + "\n", encoding="utf-8")

        state = probe(jsonl=str(lessons))
        if state["state"] == MEMORY and state["records"] == 2:
            lines.append("PASS jsonl backend reports MEMORY with 2 records")
        else:
            failures += 1
            lines.append("FAIL jsonl backend: %s" % state)

        found = recall("shard validator state_sha256", jsonl=str(lessons))
        if found["state"] == MEMORY and found["matches"] and \
                found["matches"][0]["backend"] == "jsonl":
            lines.append("PASS recall returns a labelled match (%d)" % len(found["matches"]))
        else:
            failures += 1
            lines.append("FAIL recall returned %s" % found)

        # An absent backend must be UNMEMORED, never "no lessons".
        absent = probe(jsonl=str(tmp_path / "missing.jsonl"))
        if absent["state"] == UNMEMORED and "does not exist" in absent["reason"]:
            lines.append("PASS a missing ledger is UNMEMORED with its reason")
        else:
            failures += 1
            lines.append("FAIL a missing ledger reported %s" % absent)

        nothing = probe()
        if nothing["state"] == UNMEMORED and "no memory backend" in nothing["reason"]:
            lines.append("PASS no configured backend is UNMEMORED, not empty")
        else:
            failures += 1
            lines.append("FAIL no configured backend reported %s" % nothing)

        # A failing command is an absence with a reason, not a silent zero.
        broken = probe(command='%s -c "import sys; sys.exit(3)"'
                       % sys.executable.replace("\\", "/"))
        if broken["state"] == UNMEMORED and "exited 3" in broken["reason"]:
            lines.append("PASS a command that exits 3 is UNMEMORED and names the code")
        else:
            failures += 1
            lines.append("FAIL failing command reported %s" % broken)

        # Unparseable output must not be read as an empty store.
        noise = probe(command='%s -c "print(\'not json\')"'
                      % sys.executable.replace("\\", "/"))
        if noise["state"] == UNMEMORED and "not JSON" in noise["reason"]:
            lines.append("PASS unparseable output is UNMEMORED, not zero lessons")
        else:
            failures += 1
            lines.append("FAIL unparseable output reported %s" % noise)

        # A malformed line inside a ledger is an error, not a skipped line.
        bad = tmp_path / "bad.jsonl"
        bad.write_text('{"content": "ok"}\n{oops}\n', encoding="utf-8")
        malformed = probe(jsonl=str(bad))
        if malformed["state"] == UNMEMORED and "line 2" in malformed["reason"]:
            lines.append("PASS a malformed line is UNMEMORED and names the line")
        else:
            failures += 1
            lines.append("FAIL a malformed line reported %s" % malformed)

        # The command adapter, working: two records in, two records out.
        good_cmd = ('%s -c "import json;print(json.dumps({\'content\':\'a lesson\'}))"'
                    % sys.executable.replace("\\", "/"))
        good = probe(command=good_cmd)
        if good["state"] == MEMORY and good["records"] == 1:
            lines.append("PASS the command adapter reads one JSON line")
        else:
            failures += 1
            lines.append("FAIL the command adapter reported %s" % good)

        # Writing: append-only, and readable back through the same reader.
        frame = {"intent": "refuse a stale hash", "target": "x.py", "defends": ["y"],
                 "shape": "defensive-v1"}
        wrote = record(frame, state_dir=str(tmp_path))
        again = record(frame, state_dir=str(tmp_path))
        path = Path(wrote["path"])
        records, error = _read_jsonl(path)
        if error or len(records) != 2:
            failures += 1
            lines.append("FAIL frames did not append (%s, %d records)"
                         % (error, len(records)))
        else:
            lines.append("PASS frames append and read back (%d records, %d bytes)"
                         % (len(records), again["bytes"]))

    return failures, lines


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="The defender's memory bridge, with its absence stated.")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--recall", metavar="QUERY", default=None)
    parser.add_argument("--jsonl", default=None)
    parser.add_argument("--command", dest="recall_command", default=None)
    parser.add_argument("--record", metavar="FRAME_JSON", default=None)
    parser.add_argument("--state-dir", default=None)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        failures, lines = selftest()
        if args.json:
            print(json.dumps({"failures": failures, "lines": lines}, indent=1))
        else:
            for line in lines:
                print(line)
            print("")
            print("SELFTEST %s (%d control(s), %d failure(s))"
                  % ("OK" if not failures else "FAILED", len(lines), failures))
        return 0 if not failures else 1

    if args.probe:
        result = probe(jsonl=args.jsonl, command=args.recall_command)
    elif args.recall is not None:
        result = recall(args.recall, jsonl=args.jsonl, command=args.recall_command)
    elif args.record is not None:
        try:
            frame = json.loads(args.record)
        except ValueError as exc:
            print("REFUSED: --record needs one JSON object (%s)" % exc, file=sys.stderr)
            return 2
        result = record(frame, state_dir=args.state_dir)
    else:
        parser.error("choose --probe, --recall, --record or --selftest")

    if args.json:
        print(json.dumps(result, indent=1, sort_keys=True))
    else:
        print(result.get("state") or result.get("verdict") or result.get("path"))
        for key in ("backend", "reason", "records", "path"):
            if result.get(key):
                print("  %s: %s" % (key, result[key]))
        for match in result.get("matches") or []:
            print("  [%s score=%d] %s" % (match["backend"], match["score"],
                                          match["content"][:160]))
    # UNMEMORED is not a failure of the command, it is a state a caller must see.
    return 0


if __name__ == "__main__":
    sys.exit(main())
