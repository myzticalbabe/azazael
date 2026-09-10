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
    "LOG_ROTATE_KEEP",
    "LOG_ROTATE_MB",
    "SESSION_ROTATION_HOURS",
    "TYPE_CAPS",
    "VACUUM_THRESHOLD_PCT",
    "archive_old_audit_files",
    "check_db_size_quota",
    "cmd_maintain",
    "enforce_event_ttl",
    "enforce_type_caps",
    "newest_backup",
    "rotate_old_sessions",
    "rotate_logs",
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
LOG_ROTATE_MB = 2            # Rotate logs/*.log past this size
LOG_ROTATE_KEEP = 5          # Keep this many generations (.1 .. .5)

# Per-type keep-last-N caps (2026-09-08): high-volume regenerable
# bookkeeping rows. SAFETY: only rolling-window data is capped here —
# evolution pools read the most-recent <=2000 rows, well within every
# cap below. NEVER add evolution_result / evolution_promotion (the
# selection history) or severity-filtered rows (alert evidence).
TYPE_CAPS = {
    "training_complete": 20000,
    "q_table_persisted": 20000,
    "model_registered": 20000,
    "db_health_snapshot": 2000,
    "db_health_alert": 5000,
    "generation_complete": 5000,
}


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


def enforce_type_caps(caps: dict = None) -> dict:
    """Keep-last-N trim per high-volume bookkeeping event_type.

    Deletes rows older than the newest N of each capped type. Runs in one
    DELETE per type (indexed on event_type); the nightly slot owns the
    lock window and cycles fail soft on contention. Returns per-type
    deleted counts. Dry-run: pass caps={} (no-op) or compute counts with
    the SELECT in cmd_maintain before enabling.
    """
    caps = caps if caps is not None else TYPE_CAPS
    conn = sqlite3.connect(_get_db_path(), timeout=30)
    deleted: dict = {}
    try:
        for event_type, keep in caps.items():
            cur = conn.execute(
                "DELETE FROM memories WHERE event_type = ? AND id NOT IN "
                "(SELECT id FROM memories WHERE event_type = ? "
                "ORDER BY id DESC LIMIT ?)",
                (event_type, event_type, keep),
            )
            deleted[event_type] = cur.rowcount
        conn.commit()
        return {"deleted": deleted, "total": sum(deleted.values())}
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


def _logs_dir() -> Path:
    return Path(_get_db_path()).resolve().parent.parent / "azazael" / "logs"


def _state_dir() -> Path:
    return Path(_get_db_path()).resolve().parent.parent / "azazael" / "state"


def _backup_dir() -> Path:
    d = Path(_get_db_path()).resolve().parent.parent / "azazael" / "backup" / "db"
    d.mkdir(parents=True, exist_ok=True)
    return d


def newest_backup() -> dict:
    """Newest local backup + age (for the monitor STORE line)."""
    try:
        cands = sorted(_backup_dir().glob("memory_store.*.db.gz"))
        if not cands:
            return {"exists": False}
        latest = cands[-1]
        import time as _time
        return {"exists": True, "name": latest.name,
                "mb": round(latest.stat().st_size / 1e6, 1),
                "age_h": round((_time.time() - latest.stat().st_mtime) / 3600.0, 1)}
    except Exception as e:
        return {"exists": False, "error": str(e)[:100]}


def _maybe_full_drill(gz: Path, max_age_days: int = 30) -> dict:
    """Gunzip newest backup to temp + integrity_check, at most monthly."""
    import gzip as _gzip
    import shutil as _shutil
    import tempfile as _tempfile
    import time as _time
    state = _backup_dir() / "last_drill.json"
    try:
        if state.exists():
            last = json.loads(state.read_text(encoding="utf-8"))
            if _time.time() - float(last.get("at", 0)) < max_age_days * 86400:
                return {"status": "deferred", "last": last.get("at_str", "?")}
    except Exception:
        pass
    tmp = Path(_tempfile.mkdtemp(prefix="dbdrill_")) / "drill.db"
    try:
        with _gzip.open(gz, "rb") as f_in, open(tmp, "wb") as f_out:
            _shutil.copyfileobj(f_in, f_out, length=4 * 1024 * 1024)
        vconn = sqlite3.connect(str(tmp), timeout=60)
        try:
            ok = vconn.execute("PRAGMA integrity_check").fetchone()[0]
            n = vconn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        finally:
            vconn.close()
        result = {"status": "pass" if str(ok).lower() == "ok" else "FAIL",
                  "integrity": str(ok)[:60], "rows": n,
                  "at_str": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
        state.write_text(json.dumps(
            {"at": _time.time(), "at_str": result["at_str"],
             "result": result["status"]}), encoding="utf-8")
        return result
    finally:
        try:
            _shutil.rmtree(tmp.parent, ignore_errors=True)
        except Exception:
            pass


def backup_database(keep: int = 3) -> dict:
    """Nightly online backup of the memory store (2026-09-10).

    The single SQLite file underpins all five cycles; until now there
    was no automated restore path. Uses the online backup API (safe
    against concurrent readers/writers), verifies with integrity_check
    on the COPY, gzips it (~5x), and keeps the newest `keep`.

    Source-of-Truth mirror (2026-09-10): a second copy goes to
    G:\\source-of-truth\\azazael\\db-backup\\ — off-disk redundancy.
    Fail-open when G: is absent (undocked laptop must never break
    maintenance). Returns {path, bytes, gz_bytes, integrity, pruned,
    mirror, verified}.
    """
    import gzip as _gzip
    import shutil as _shutil
    src = _get_db_path()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    raw = _backup_dir() / ("memory_store.%s.db" % stamp)
    try:
        sconn = sqlite3.connect(src, timeout=30)
        try:
            dconn = sqlite3.connect(str(raw), timeout=30)
            try:
                sconn.backup(dconn)
            finally:
                dconn.close()
        finally:
            sconn.close()
        vconn = sqlite3.connect(str(raw), timeout=30)
        try:
            integrity = vconn.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            vconn.close()
        if str(integrity).lower() != "ok":
            raw.unlink(missing_ok=True)
            return {"error": "backup integrity check failed: %s" % str(integrity)[:120]}
        gz = raw.with_suffix(".db.gz")
        with open(raw, "rb") as f_in, _gzip.open(gz, "wb") as f_out:
            _shutil.copyfileobj(f_in, f_out, length=4 * 1024 * 1024)
        raw.unlink()
        pruned = []
        existing = sorted(_backup_dir().glob("memory_store.*.db.gz"))
        while len(existing) > keep:
            old = existing.pop(0)
            try:
                old.unlink()
                pruned.append(old.name)
            except OSError:
                break
        out = {"path": str(gz), "gz_bytes": gz.stat().st_size,
               "integrity": "ok", "pruned": pruned}
        # Mirror to Source of Truth (fail-open).
        try:
            _mirror = Path(r"G:\source-of-truth\azazael\db-backup")
            _mirror.mkdir(parents=True, exist_ok=True)
            _dest = _mirror / gz.name
            _shutil.copyfile(str(gz), str(_dest))
            _mexisting = sorted(_mirror.glob("memory_store.*.db.gz"))
            while len(_mexisting) > keep:
                _old = _mexisting.pop(0)
                try:
                    _old.unlink()
                except OSError:
                    break
            out["mirror"] = str(_dest)
        except Exception as e:
            out["mirror"] = "skipped: %s" % str(e)[:100]
        # Restore drill (light): re-read the gz (CRC check) so a
        # bit-rotted archive is caught here, not at 3am during an
        # actual incident.
        try:
            with _gzip.open(gz, "rb") as f:
                _n = 0
                while f.read(4 * 1024 * 1024):
                    _n += 1
            out["verified"] = True
        except Exception as e:
            out["verified"] = "CRC FAIL: %s" % str(e)[:100]
        # Full drill, monthly (2026-09-10): gunzip to temp + real
        # integrity_check proves the archive actually restores, not just
        # CRC-passes. Gated by last-drill state so nightly stays fast.
        try:
            out["full_drill"] = _maybe_full_drill(gz)
        except Exception as e:
            out["full_drill"] = "drill error: %s" % str(e)[:100]
        return out
    except Exception as e:
        try:
            if raw.exists():
                raw.unlink()
        except OSError:
            pass
        return {"error": str(e)[:200]}


def rotate_logs(max_mb: int = LOG_ROTATE_MB, keep: int = LOG_ROTATE_KEEP,
                log_dir: (Path | str | None) = None) -> dict:
    """Rotate logs/*.log past max_mb, keeping .1 .. .keep generations.

    (2026-09-09: evolution_cycle.log was growing unbounded — 0.6 MB and
    climbing 5 KB per cycle with no rotation anywhere. The nightly
    maintenance task runs this, so no log can grow more than ~1 day past
    the cap between runs.)

    Shift-up scheme: .keep is dropped, .N -> .N+1, live .log -> .1.
    A concurrently-written .log is never moved mid-line — writers here
    open append-per-line, and rotation runs from the nightly task when
    cycles aren't mid-write... in practice a torn last line is possible
    and acceptable for logs (never for state/DB, which use tmp+replace).
    Returns {rotated: [...], skipped: [...]}.
    """
    d = Path(log_dir) if log_dir else _logs_dir()
    rotated, skipped = [], []
    if not d.exists():
        return {"rotated": rotated, "skipped": skipped, "log_dir": str(d)}
    cap = max_mb * 1024 * 1024
    for logf in sorted(d.glob("*.log")):
        try:
            if logf.stat().st_size < cap:
                skipped.append(logf.name)
                continue
            oldest = logf.with_name(logf.name + ".%d" % keep)
            if oldest.exists():
                oldest.unlink()
            for n in range(keep - 1, 0, -1):
                src = logf.with_name(logf.name + ".%d" % n)
                if src.exists():
                    src.replace(logf.with_name(logf.name + ".%d" % (n + 1)))
            logf.replace(logf.with_name(logf.name + ".1"))
            rotated.append(logf.name)
        except Exception as e:  # noqa: BLE001 — one bad log never blocks the rest
            skipped.append("%s (%s)" % (logf.name, str(e)[:80]))
    return {"rotated": rotated, "skipped": skipped, "log_dir": str(d)}


def run_maintenance() -> dict:
    """Run all maintenance tasks in sequence.
    
    Returns dict with results of each task.
    """
    results = {}
    # Backup FIRST (2026-09-10): the pre-maintenance snapshot is the
    # true restore point — post-prune state is reproducible, pre-prune
    # deletions are not. Destructive ops (TTL, caps, vacuum) follow.
    try:
        results["db_backup"] = backup_database()
    except Exception as e:
        results["db_backup"] = {"error": str(e)}
    try:
        results["event_ttl"] = enforce_event_ttl()
    except Exception as e:
        results["event_ttl"] = {"error": str(e)}
    try:
        results["session_rotation"] = {"closed": rotate_old_sessions()}
    except Exception as e:
        results["session_rotation"] = {"error": str(e)}
    try:
        results["type_caps"] = enforce_type_caps()
    except Exception as e:
        results["type_caps"] = {"error": str(e)}
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
    try:
        results["log_rotation"] = rotate_logs()
    except Exception as e:
        results["log_rotation"] = {"error": str(e)}
    try:
        # Error triage (2026-09-09): cluster the week's real errors for
        # the maintenance log. Summary only — no new store rows.
        from CORE.local_memory import get_memory_store
        tri = get_memory_store().triage_real_errors(days=7)
        # Persist for the live monitor (atomic; monitor reads + ages it).
        try:
            _td = _state_dir()
            _td.mkdir(parents=True, exist_ok=True)
            _tmp = _td / "error_triage.json.tmp"
            with open(_tmp, "w", encoding="utf-8") as f:
                json.dump(tri, f, ensure_ascii=False, default=str)
            _tmp.replace(_td / "error_triage.json")
        except Exception as e:  # noqa: BLE001 — triage summary still reported
            tri["_persist_error"] = str(e)[:120]
        results["error_triage"] = {
            "errors_exact": tri.get("total_errors_exact", 0),
            "warnings_exact": tri.get("total_warnings_exact", 0),
            "clusters": tri.get("cluster_count", 0),
            "capped": tri.get("capped", False),
            "top": [{"source": c["source"], "severity": c["severity"],
                     "count": c["count"], "newest": c["newest"],
                     "signature": c["signature"][:120]}
                    for c in tri.get("clusters", [])[:5]],
        }
    except Exception as e:
        results["error_triage"] = {"error": str(e)}
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
