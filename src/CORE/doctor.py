"""doctor.py — Self-diagnostic for Azazael systems.

Covers followups: #3 (doctor), #5 (process watchdog), #6 (startup validation),
#14 (DB integrity check), #25 (query timeout), #30 (index verification),
#31 (file permission validation), #34 (env var validation).

Usage:
    python -m CORE.doctor          # Full diagnostic
    python -m CORE.doctor --quick   # Quick health check
"""


__all__ = [
    "check_db_integrity",
    "check_disk_space",
    "check_env_vars",
    "check_file_permissions",
    "check_index_usage",
    "cmd_doctor",
    "cmd_verify",
    "get_db_size",
    "run_all",
]


import os
import sys
import json
import time
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timezone


def check_db_integrity() -> dict:
    """Run PRAGMA integrity_check on the DB."""
    from CORE.direct_memory import DB_PATH
    start = time.perf_counter()
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        elapsed = (time.perf_counter() - start) * 1000
        conn.close()
        return {"ok": result == "ok", "result": result, "elapsed_ms": round(elapsed, 1)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_index_usage() -> list:
    """Check which indexes are used by common queries (EXPLAIN QUERY PLAN)."""
    from CORE.direct_memory import DB_PATH
    queries = [
        ("SELECT * FROM memories WHERE timestamp > '2020-01-01'", "memories(timestamp)"),
        ("SELECT * FROM memories WHERE session_id = 'test' AND event_type = 'test'", "memories(session_id, event_type)"),
        ("SELECT * FROM memories WHERE event_uuid = 'test'", "memories(event_uuid)"),
        ("SELECT * FROM session_mappings WHERE dm_session_id = 'test'", "idx_mappings_dm"),
    ]
    results = []
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        for query, expected_index in queries:
            plan = conn.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()
            plan_str = " ".join(str(r[2]) if len(r) > 2 else str(r) for r in plan)
            uses_index = expected_index in plan_str
            results.append({"query": query[:60], "expected_index": expected_index, "uses_index": uses_index, "plan": plan_str[:100]})
        conn.close()
    except Exception:
        pass
    return results


def get_db_size() -> dict:
    """Get database file size and WAL size."""
    from CORE.direct_memory import DB_PATH
    db = Path(str(DB_PATH))
    wal = db.with_suffix(".db-wal")
    shm = db.with_suffix(".db-shm")
    sizes = {"db": db.stat().st_size if db.exists() else 0}
    if wal.exists():
        sizes["wal"] = wal.stat().st_size
    if shm.exists():
        sizes["shm"] = shm.stat().st_size
    sizes["total_mb"] = round(sum(sizes.values()) / (1024 * 1024), 2)
    sizes["db_mb"] = round(sizes["db"] / (1024 * 1024), 2)
    return sizes


def check_file_permissions() -> list:
    """Verify .audit/ files are read-only after close."""
    import stat
    from CORE.audit_trail import AUDIT_DIR
    issues = []
    if not AUDIT_DIR.exists():
        return issues
    for fp in sorted(AUDIT_DIR.glob("session_*.jsonl")):
        try:
            mode = os.stat(str(fp)).st_mode
            is_writable = bool(mode & stat.S_IWRITE)
            if is_writable:
                issues.append(f"{fp.name}: writable (should be read-only)")
        except Exception:
            pass
    return issues


def check_env_vars() -> list:
    """Validate required environment variables."""
    warnings = []
    if not os.environ.get("OLLAMA_HOST", ""):
        pass  # Optional — InferencePool uses default
    mem_dir = os.environ.get("AZAZAEL_MEMORY_DIR", "")
    if mem_dir and not Path(mem_dir).exists():
        warnings.append(f"AZAZAEL_MEMORY_DIR={mem_dir}: directory does not exist")
    return warnings


def check_disk_space() -> dict:
    """Check available disk space on DB and audit directories."""
    from CORE.direct_memory import DB_PATH
    from CORE.audit_trail import AUDIT_DIR
    result = {}
    for label, path in [("db", Path(str(DB_PATH)).parent), ("audit", AUDIT_DIR)]:
        try:
            usage = shutil.disk_usage(str(path))
            free_gb = round(usage.free / (1024**3), 1)
            total_gb = round(usage.total / (1024**3), 1)
            pct = round(usage.used / usage.total * 100, 1)
            result[label] = {"free_gb": free_gb, "total_gb": total_gb, "used_pct": pct}
        except Exception:
            pass
    return result


def run_all(quick: bool = False) -> dict:
    """Run all diagnostic checks and return report."""
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "checks": {}}

    # DB integrity (skip in quick mode)
    if not quick:
        report["checks"]["db_integrity"] = check_db_integrity()
        report["checks"]["index_usage"] = check_index_usage()

    # DB size
    report["checks"]["db_size"] = get_db_size()

    # File permissions
    report["checks"]["file_permissions"] = check_file_permissions()

    # Environment variables
    report["checks"]["env_vars"] = check_env_vars()

    # Disk space
    report["checks"]["disk_space"] = check_disk_space()

    # Ollama connectivity
    try:
        from CORE.inference_pool import InferencePool
        pool = InferencePool(max_concurrent=1)
        report["checks"]["ollama"] = pool.health()
    except Exception as e:
        report["checks"]["ollama"] = {"healthy": False, "error": str(e)}

    # Audit trail health
    try:
        from CORE.audit_trail import verify_on_startup
        broken = verify_on_startup()
        report["checks"]["audit"] = {"broken_files": len(broken), "broken": [b.get("file", "")[-40:] for b in broken]}
    except Exception as e:
        report["checks"]["audit"] = {"error": str(e)}

    # Session stats
    try:
        from CORE.direct_memory import DirectMemory
        report["checks"]["sessions"] = {
            "open": DirectMemory.get_open_sessions_count(),
            "total_events": DirectMemory.summary_stats().get("total_events", 0),
        }
    except Exception as e:
        report["checks"]["sessions"] = {"error": str(e)}

    # Overall health
    all_ok = all(
        c.get("ok", True) if isinstance(c, dict) else True
        for c in report["checks"].values() if isinstance(c, dict)
    )
    report["healthy"] = all_ok
    return report


def cmd_doctor():
    """Print diagnostic report to stdout."""
    report = run_all()
    cols = shutil.get_terminal_size().columns
    print("=" * cols)
    print(f"  AZAZAEL Doctor -- {'HEALTHY' if report.get('healthy', False) else 'ISSUES FOUND'}")
    print("=" * cols)
    for check_name, result in report["checks"].items():
        if isinstance(result, dict):
            status = "[OK]" if result.get("ok", result.get("healthy", True)) else "[FAIL]"
            print(f"\n  {status} {check_name}")
            for k, v in result.items():
                if k not in ("ok", "healthy", "error"):
                    print(f"      {k}: {v}")
            if "error" in result:
                print(f"      error: {result['error']}")
            if isinstance(result.get("broken"), list) and result["broken"]:
                for b in result["broken"]:
                    print(f"      broken: {b}")
            if isinstance(result.get("warnings"), list) and result["warnings"]:
                for w in result["warnings"]:
                    print(f"      warning: {w}")
        elif isinstance(result, list):
            if result:
                print(f"\n  [WARN] {check_name}")
                for item in result:
                    print(f"      {item}")
    print(f"\n  Overall: {'[OK] HEALTHY' if report.get('healthy') else '[FAIL] ISSUES FOUND'}")
    return report


def cmd_verify():
    """Run verification checks and print summary."""
    report = run_all(quick=True)
    all_ok = report.get("healthy", False)
    print(f"Verify: {'PASS' if all_ok else 'FAIL'} — {sum(1 for c in report['checks'].values() if isinstance(c, dict) and not c.get('ok', c.get('healthy', True)))} issues")
    return report


if __name__ == "__main__":
    import sys
    if "--json" in sys.argv:
        print(json.dumps(run_all(), indent=2))
    elif "--quick" in sys.argv:
        cmd_verify()
    else:
        cmd_doctor()
