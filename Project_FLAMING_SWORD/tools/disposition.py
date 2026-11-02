# coding: utf-8
"""Disposition ledger: every error becomes its own task, at the moment it is seen.

The rule this file exists for
------------------------------
Errors are recorded *when they happen*, not when the session ends. Reconstruction
at the end loses the detail (which command, which exit code, which file) and
over-weights whatever is still salient an hour later. So the sweep writes a task
row the instant it meets an error: a detector that raised, a detector that could
not run, a fix that failed, a fix whose own detector still fires, a landing that
was refused, a deletion housekeeping could not make.

One error, one row, one disposition — later.

Why repeats are counted instead of duplicated
---------------------------------------------
"Every error is a separate task" is the rule; taken literally on a scan that runs
every minute, a single UNRUN detector becomes a thousand identical rows and the
ledger stops being readable, which is how a queue dies. So a *distinct* error is
a distinct row (identity = stage + kind + subject), a re-encounter increments
`seen` and moves `last_seen`, and a recurrence **after** a disposition is a NEW
row: the error came back, so it is a new fact about the tree, not a reopened
opinion.

The failure this avoids is the opposite one, and it is worse: an error that is
seen and not written is an error nobody disposes of.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

STATE_DIR = ".flaming_sword"
LEDGER = "tasks.jsonl"
DISPOSITIONS = ("fixed", "wontfix", "duplicate", "deferred", "external")


def ledger_path(root: Path) -> Path:
    return Path(root) / STATE_DIR / LEDGER


def read(root: Path) -> List[Dict]:
    path = ledger_path(root)
    if not path.exists():
        return []
    rows: List[Dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            note_failure("Project_FLAMING_SWORD/tools/disposition.py", exc)
            continue
    return rows


def write(root: Path, rows: List[Dict]) -> None:
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                    encoding="utf-8")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def identity(stage: str, kind: str, subject: str) -> str:
    """What makes two encounters the same error. Not the message: a message with
    a count in it ("3 item(s) failed") changes while the defect does not."""
    raw = "%s|%s|%s" % (stage, kind, subject)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def record(root: Path, stage: str, kind: str, subject: str, what: str,
           evidence: str = "", remedy: str = "") -> Dict:
    """Record one error as one task, now. Returns the row (new or bumped)."""
    rows = read(root)
    ident = identity(stage, kind, subject)
    at = _now()
    for row in rows:
        if row.get("identity") == ident and row.get("status") == "open":
            row["seen"] = int(row.get("seen") or 1) + 1
            row["last_seen"] = at
            row["what"] = what
            if evidence:
                row["evidence"] = evidence
            if remedy:
                row["remedy"] = remedy
            write(root, rows)
            return row
    next_number = 1 + max((int(row["id"].split("-")[1]) for row in rows
                           if row.get("id", "").startswith("t-")), default=0)
    row = {
        "id": "t-%04d" % next_number,
        "identity": ident,
        "stage": stage,
        "kind": kind,
        "subject": subject,
        "what": what,
        "evidence": evidence,
        "remedy": remedy,
        "first_seen": at,
        "last_seen": at,
        "seen": 1,
        "status": "open",
        "disposition": None,
        "note": None,
        "disposed_at": None,
    }
    rows.append(row)
    write(root, rows)
    return row


def tasks(root: Path, include_disposed: bool = False) -> List[Dict]:
    rows = read(root)
    if include_disposed:
        return rows
    return [row for row in rows if row.get("status") == "open"]


def dispose(root: Path, task_id: str, disposition: str,
            note: str = "") -> Optional[Dict]:
    """Close one task with a disposition. The caller decides; the ledger records."""
    if disposition not in DISPOSITIONS:
        raise ValueError("disposition must be one of %s" % ", ".join(DISPOSITIONS))
    rows = read(root)
    for row in rows:
        if row.get("id") == task_id:
            if row.get("status") != "open":
                raise ValueError("%s is already %s" % (task_id, row.get("status")))
            row["status"] = "disposed"
            row["disposition"] = disposition
            row["note"] = note
            row["disposed_at"] = _now()
            write(root, rows)
            return row
    return None



try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where, exc=None):
        pass  # ledger missing; the swallow is still named at the call site

def summary(root: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in read(root):
        key = row.get("status") if row.get("status") == "open" else row.get("disposition")
        counts[key or "unknown"] = counts.get(key or "unknown", 0) + 1
    return counts
