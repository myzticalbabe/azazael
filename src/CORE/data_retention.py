"""data_retention.py — Data lifecycle management for Azazael.

Covers followups: #17 (event TTL), #18 (session rotation), #19 (DB size quota),
#20 (audit archival), #21 (scheduled GC), #24 (DB vacuum scheduler).

Usage:
    from CORE.data_retention import enforce_event_ttl, rotate_old_sessions, \
        check_db_size_quota, archive_old_audit_files, run_maintenance
"""


__all__ = [
    "AUDIT_ARCHIVE_DAYS",
    "DB_SIZE_QUOTA_MB",
    "EVENT_TTL_DAYS",
    "SESSION_ROTATION_HOURS",
    "VACUUM_THRESHOLD_PCT",
    "archive_old_audit_files",
    "check_db_size_quota",
    "cmd_maintain",
    "enforce_event_ttl",
    "rotate_old_sessions",
    "run_maintenance",
    "vacuum_if_needed",
    "wal_checkpoint",
]


import json
import sqlite3
import gzip
from pathlib import Path
from datetime import datetime, timezone, timedelta


# Default thresholds
EVENT_TTL_DAYS = 90          # Auto-delete events older than this
SESSION_ROTATION_HOURS = 24  # Auto-close sessions older than this
DB_SIZE_QUOTA_MB = 500       # Warn when DB exceeds this
AUDIT_ARCHIVE_DAYS = 30      # Archive .audit/ files older than this
VACUUM_THRESHOLD_PCT = 20    # Auto-vacuum when free pages exceed this %


def _get_db_path() -> str:
    from CORE.direct_memory import DB_PATH
    return str(DB_PATH)


def enforce_event_ttl(ttl_days: int = EVENT_TTL_DAYS) -> dict:
    """Delete events older than ttl_days. Returns count deleted."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ttl_days)).isoformat()
    conn = sqlite3.connect(_get_db_path(), timeout=5)
    try:
        cursor = conn.execute(
            "DELETE FROM memories WHERE timestamp < ?", (cutoff,)
        )
        deleted = cursor.rowcount
        conn.commit()
        # Also delete orphaned sessions
        conn.execute(
            "DELETE FROM sessions WHERE session_id NOT IN "
            "(SELECT DISTINCT session_id FROM memories)"
        )
        conn.commit()
        return {"events_deleted": deleted, "cutoff": cutoff}
    finally:
        conn.close()


def rotate_old_sessions(max_age_hours: int = SESSION_ROTATION_HOURS) -> int:
    """Auto-close sessions older than max_age_hours. Returns count closed."""
    from CORE.direct_memory import DirectMemory
    return DirectMemory.close_stale_sessions(max_age_hours=max_age_hours)


def check_db_size_quota(quota_mb: int = DB_SIZE_QUOTA_MB) -> dict:
    """Check DB size against quota. Returns warning if exceeded."""
    from CORE.doctor import get_db_size
    size = get_db_size()
    total_mb = size.get("total_mb", 0)
    return {
        "size_mb": total_mb,
        "quota_mb": quota_mb,
        "exceeded": total_mb > quota_mb,
        "pct": round(total_mb / quota_mb * 100, 1) if quota_mb > 0 else 0,
    }


def archive_old_audit_files(max_age_days: int = AUDIT_ARCHIVE_DAYS) -> list:
    """Gzip-compress .audit/ files older than max_age_days.
    
    Returns list of (filepath, archive_path) for archived files.
    Renames original to .jsonl.gz after archiving.
    """
    from CORE.audit_trail import AUDIT_DIR
    archived = []
    if not AUDIT_DIR.exists():
        return archived

    cutoff = datetime.now() - timedelta(days=max_age_days)
    for fp in sorted(AUDIT_DIR.glob("session_*.jsonl")):
        try:
            mtime = datetime.fromtimestamp(fp.stat().st_mtime)
            if mtime < cutoff:
                # Read and compress
                data = fp.read_bytes()
                gz_path = fp.with_suffix(".jsonl.gz")
                with gzip.open(gz_path, "wb", compresslevel=6) as gz:
                    gz.write(data)
                # Remove original
                fp.unlink()
                archived.append((fp.name, gz_path.name))
        except Exception:
            continue
    return archived


def vacuum_if_needed() -> dict:
    """Run VACUUM if fragmentation exceeds threshold."""
    conn = sqlite3.connect(_get_db_path(), timeout=10)
    try:
        # Check free pages
        freelist = conn.execute("PRAGMA freelist_count").fetchone()[0]
        page_count = conn.execute("PRAGMA page_count").fetchone()[0]
        if page_count > 0:
            free_pct = freelist / page_count * 100
            if free_pct > VACUUM_THRESHOLD_PCT:
                conn.execute("VACUUM")
                return {"vacuumed": True, "free_pct_before": round(free_pct, 1)}
        return {"vacuumed": False, "free_pct": round(freelist / max(page_count, 1) * 100, 1) if page_count > 0 else 0}
    finally:
        conn.close()


def wal_checkpoint() -> dict:
    """Run WAL checkpoint to keep WAL file bounded."""
    conn = sqlite3.connect(_get_db_path(), timeout=5)
    try:
        before = Path(_get_db_path()).with_suffix(".db-wal").stat().st_size if Path(_get_db_path()).with_suffix(".db-wal").exists() else 0
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        after = Path(_get_db_path()).with_suffix(".db-wal").stat().st_size if Path(_get_db_path()).with_suffix(".db-wal").exists() else 0
        return {"before_bytes": before, "after_bytes": after, "freed_bytes": before - after}
    finally:
        conn.close()


def run_maintenance() -> dict:
    """Run all maintenance tasks in sequence.
    
    Returns dict with results of each task.
    """
    results = {}
    try:
        results["event_ttl"] = enforce_event_ttl()
    except Exception as e:
        results["event_ttl"] = {"error": str(e)}
    try:
        results["session_rotation"] = {"closed": rotate_old_sessions()}
    except Exception as e:
        results["session_rotation"] = {"error": str(e)}
    try:
        results["db_quota"] = check_db_size_quota()
    except Exception as e:
        results["db_quota"] = {"error": str(e)}
    try:
        results["audit_archive"] = {"archived": archive_old_audit_files()}
    except Exception as e:
        results["audit_archive"] = {"error": str(e)}
    try:
        results["vacuum"] = vacuum_if_needed()
    except Exception as e:
        results["vacuum"] = {"error": str(e)}
    try:
        results["wal_checkpoint"] = wal_checkpoint()
    except Exception as e:
        results["wal_checkpoint"] = {"error": str(e)}
    return results


def cmd_maintain():
    """CLI command: run all maintenance tasks and print results."""
    results = run_maintenance()
    print("=== Maintenance Run ===")
    for task, result in results.items():
        status = "[OK]" if "error" not in result else "[FAIL]"
        print(f"  {status} {task}: {json.dumps(result, default=str)}")
    print("  Done.")


if __name__ == "__main__":
    cmd_maintain()
