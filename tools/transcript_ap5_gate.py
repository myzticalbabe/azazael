"""Transcript gate: enforce prose rules over persisted assistant messages.

WHY THIS EXISTS
---------------
The opencode plugin API exposes hooks for tool execution, system-prompt
transform, and inbound messages -- but none receives assistant OUTPUT. So a
rule governing what the agent SAYS (AP-5, SYSTEM_INSTRUCTIONS.md:2046) can be
injected as advice but can never be gated pre-send. Injection != enforcement.

Assistant prose is persisted in the session store, so it CAN be gated
downstream. This is the same shape as claim_guard.py at commit time: scan a
durable artifact after the fact.

    python tools/transcript_ap5_gate.py --limit 500
    python tools/transcript_ap5_gate.py --session ses_abc --json

Exit codes:
    0  clean (no permission-seeking language in scanned assistant prose)
    1  findings present
    2  store unreadable / unusable schema

The store is opened read-only (mode=ro). This gate NEVER writes.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from permission_seeking_guard import scan as scan_text  # noqa: E402

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

DEFAULT_DB = os.path.expandvars(
    r"%USERPROFILE%\.local\share\opencode\opencode.db"
)


@dataclass
class Finding:
    session_id: str
    message_id: str
    part_id: str
    rule: str
    line: int
    match: str
    excerpt: str


@dataclass
class Report:
    db: str
    scanned_parts: int = 0
    scanned_sessions: set = field(default_factory=set)
    findings: list = field(default_factory=list)
    schema_ok: bool = True
    note: str = ""


def _role_of(message_data: Any) -> str:
    """Extract role from a message.data JSON blob (no role column exists)."""
    if isinstance(message_data, str):
        try:
            message_data = json.loads(message_data)
        except (ValueError, TypeError) as exc:
            # Unparseable role blob -> treat as not-assistant, which is the
            # conservative direction (we skip rather than scan someone else's
            # prose). Record it anyway: a role we cannot read is a schema
            # change, and silently dropping rows would shrink the scan without
            # saying so.
            note_failure("transcript_ap5_gate:_role_of", exc)
            return ""
    if isinstance(message_data, dict):
        role = message_data.get("role")
        if isinstance(role, str):
            return role
    return ""


def _text_of(part_data: Any) -> str:
    """Extract assistant prose from a part.data JSON blob.

    Falls back to the raw string when the shape is unknown: an unparseable
    blob is still text a human would have read, so skipping it would be a
    silent hole rather than a reported limitation.
    """
    if isinstance(part_data, str):
        try:
            part_data = json.loads(part_data)
        except (ValueError, TypeError) as exc:
            # Record, then fall back. The raw blob is still text a human would
            # have read, so returning it beats dropping it -- but an unparseable
            # blob is a schema change and must be visible, not swallowed.
            note_failure("transcript_ap5_gate:_text_of", exc)
            return part_data
    if isinstance(part_data, dict):
        if part_data.get("type") not in (None, "text"):
            return ""
        text = part_data.get("text")
        return text if isinstance(text, str) else ""
    return ""


def _excerpt(around: str, width: int = 90) -> str:
    flat = " ".join(around.split())
    return flat if len(flat) <= width else flat[: width - 1] + "\u2026"


def scan_store(
    db: str,
    session: str | None = None,
    limit: int = 500,
) -> Report:
    report = Report(db=db)
    uri = "file:%s?mode=ro" % db.replace("\\", "/")
    try:
        con = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        report.schema_ok = False
        report.note = "cannot open store: %s" % exc
        return report

    try:
        q = (
            "SELECT p.session_id, p.message_id, p.id, p.data, m.data "
            "FROM part p LEFT JOIN message m ON m.id = p.message_id "
        )
        args: list[Any] = []
        if session:
            q += "WHERE p.session_id = ? "
            args.append(session)
        q += "ORDER BY p.time_created DESC LIMIT ?"
        args.append(limit)

        try:
            rows = con.execute(q, args).fetchall()
        except sqlite3.Error as exc:
            report.schema_ok = False
            report.note = "query failed: %s" % exc
            return report

        for sess_id, msg_id, part_id, part_data, msg_data in rows:
            if _role_of(msg_data) != "assistant":
                continue
            text = _text_of(part_data)
            if not text:
                continue
            report.scanned_parts += 1
            report.scanned_sessions.add(sess_id or "?")
            for f in scan_text(text):
                lines = text.splitlines()
                lo = max(0, f.line - 1)
                context = lines[lo] if lo < len(lines) else ""
                report.findings.append(
                    Finding(
                        session_id=sess_id or "?",
                        message_id=msg_id or "?",
                        part_id=part_id or "?",
                        rule=f.name,
                        line=f.line,
                        match=f.match,
                        excerpt=_excerpt(context),
                    )
                )
        return report
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=DEFAULT_DB, help="session store path")
    ap.add_argument("--session", help="restrict to one session id")
    ap.add_argument("--limit", type=int, default=500, help="parts to scan")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not os.path.exists(args.db):
        print("transcript gate: no session store at %s" % args.db, file=sys.stderr)
        return 2

    report = scan_store(args.db, args.session, args.limit)

    if not report.schema_ok:
        print("transcript gate: %s" % report.note, file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "db": report.db,
                    "scanned_parts": report.scanned_parts,
                    "scanned_sessions": sorted(report.scanned_sessions),
                    "findings": [asdict(f) for f in report.findings],
                },
                indent=2,
            )
        )
        return 1 if report.findings else 0

    print("transcript gate -- assistant prose (post-hoc)")
    print("  store:    %s" % report.db)
    print("  scanned:  %d assistant part(s) across %d session(s)"
          % (report.scanned_parts, len(report.scanned_sessions)))

    if not report.findings:
        print("  AP-5: clean")
        return 0

    print("  AP-5: %d finding(s)" % len(report.findings))
    for f in report.findings:
        print("  [%s] %s msg=%s line=%d %r" % (
            f.rule, f.session_id[:12], f.message_id[:12], f.line, f.match))
        if f.excerpt:
            print("      \u2026 %s" % f.excerpt)
    print(
        "\nMandated actions are NOT requests (SYSTEM_INSTRUCTIONS.md:2046).\n"
        "This gate runs AFTER emission: it cannot prevent a violation, only\n"
        "make it visible. Prevention is not available -- no assistant-output\n"
        "hook exists in the plugin API."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())