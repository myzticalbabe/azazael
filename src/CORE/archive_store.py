# coding: utf-8
"""archive_store.py — Query across hot DB + monthly G: archives.

Read-only. SELECT statements only (anything else raises ValueError).
Returns per-database result sets so callers see which tier answered.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

HOT_DB = Path.home() / ".azazael" / "memory_store.db"
ARCHIVE_DIR = Path("G:/AZAZAEL_SOURCE_OF_TRUTH/memory_archive")


def list_archives(archive_dir: (Path | None) = None) -> List[Path]:
    """Monthly archive files, oldest first."""
    d = Path(archive_dir) if archive_dir else ARCHIVE_DIR
    if not d.exists():
        return []
    return sorted(d.glob("memory_*.db"))


def query_all(sql: str, params: tuple = (),
              archive_dir: (Path | None) = None) -> Dict[str, Any]:
    """Run a SELECT on hot + every archive. Returns {hot: [...], archives: {month: [...]}}."""
    if not sql.strip().lower().startswith("select"):
        raise ValueError("archive_store only runs SELECT queries")
    out: Dict[str, Any] = {"hot": [], "archives": {}}
    if HOT_DB.exists():
        conn = sqlite3.connect(str(HOT_DB))
        try:
            out["hot"] = conn.execute(sql, params).fetchall()
        finally:
            conn.close()
    for arch in list_archives(archive_dir):
        month = arch.stem.replace("memory_", "")
        try:
            conn = sqlite3.connect(str(arch))
            try:
                out["archives"][month] = conn.execute(sql, params).fetchall()
            finally:
                conn.close()
        except Exception as e:
            out["archives"][month] = [{"error": str(e)[:120]}]
    return out


def archive_summary(archive_dir: (Path | None) = None) -> List[Dict[str, Any]]:
    """Row counts per archive from the hot manifest (no file opens)."""
    if not HOT_DB.exists():
        return []
    conn = sqlite3.connect(str(HOT_DB))
    try:
        rows = conn.execute(
            "SELECT month, db_path, memories_moved, sessions_moved, moved_at "
            "FROM archive_manifest ORDER BY month").fetchall()
    except Exception:
        return []
    finally:
        conn.close()
    return [{"month": r[0], "db_path": r[1], "memories": r[2],
             "sessions": r[3], "moved_at": r[4]} for r in rows]
