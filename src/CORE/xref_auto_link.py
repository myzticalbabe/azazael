#!/usr/bin/env python3
"""xref_auto_link.py — utility functions (auto_link_at_creation)""",
"""Auto-link DM sessions with AJ sessions at creation time."""


__all__ = [
    "auto_link_at_creation",
]

import json
from datetime import datetime
from CORE.direct_memory import DirectMemory
from CORE.audit_trail import AUDIT_DIR

def auto_link_at_creation(dm_session_id: str) -> bool:
    """Find a matching AJ session by timestamp proximity and link it."""
    # Get the DM session's start time
    import sqlite3
    from CORE.direct_memory import DB_PATH
    conn = sqlite3.connect(str(DB_PATH), timeout=3)
    row = conn.execute("SELECT started_at FROM sessions WHERE session_id = ?",
                       (dm_session_id,)).fetchone()
    conn.close()
    if not row:
        return False
    try:
        dm_dt = datetime.fromisoformat(row[0])
    except (ValueError, TypeError):
        return False

    # Find closest AJ session within 5 seconds
    for fp in sorted(AUDIT_DIR.glob("session_*.jsonl")):
        try:
            with fp.open("r", encoding="utf-8") as f:
                first = f.readline()
                d = json.loads(first)
                if d.get("type") == "session_start":
                    aj_ts = d.get("ts", "")
                    if aj_ts:
                        aj_dt = datetime.fromisoformat(aj_ts)
                        delta = abs((dm_dt - aj_dt).total_seconds())
                        if delta <= 5.0:
                            dm = DirectMemory(session_id=dm_session_id)
                            return dm.link_audit_session(
                                str(fp), audit_session_id=d.get("session_uuid", ""),
                                mapping_type="auto", confidence=1.0,
                                notes="auto-linked at creation")
        except Exception:
            continue
    return False

if __name__ == "__main__":
    import sys
    sid = sys.argv[1] if len(sys.argv) > 1 else input("DM session ID: ")
    result = auto_link_at_creation(sid)
    print(f"Auto-link: {'success' if result else 'no match found'}")
