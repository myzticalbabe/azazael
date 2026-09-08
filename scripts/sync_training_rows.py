# coding: utf-8
"""sync_training_rows.py - Copy new memory rows from the WSL training DB back
to the Windows live DB, deduped by event_uuid.

The full-fleet training ran on ubuntu1 (WSL Ubuntu-26.04) against a copy of
the Windows memory_store.db. This script merges the rows the training added
(model_registered, q_table_persisted, training_complete, worm_training, etc.)
back into the Windows DB. Idempotent: rows whose event_uuid already exists
are skipped.

Usage:
    python scripts/sync_training_rows.py <src_db> <dst_db>
"""
import sqlite3
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: sync_training_rows.py <src_db> <dst_db>")
        return 2
    src_db, dst_db = sys.argv[1], sys.argv[2]

    src = sqlite3.connect(src_db)
    src.row_factory = sqlite3.Row
    dst = sqlite3.connect(dst_db, timeout=60)
    dst.execute("PRAGMA busy_timeout = 60000")

    have = set(
        r[0] for r in dst.execute(
            "SELECT event_uuid FROM memories WHERE event_uuid IS NOT NULL AND event_uuid != ''"
        ).fetchall()
    )
    print("dst uuids:", len(have))

    cols = [r[1] for r in dst.execute("PRAGMA table_info(memories)").fetchall()]
    rows = src.execute("SELECT * FROM memories").fetchall()
    new_rows = [dict(r) for r in rows if r["event_uuid"] not in have]
    print("src rows:", len(rows), "new to sync:", len(new_rows))

    if new_rows:
        # Exclude the primary key: the src DB is a copy of the dst, so
        # ids overlap and INSERTing them collides with existing PKs.
        # Let autoincrement assign fresh ids; dedup stays on event_uuid.
        col_list = [c for c in cols if c != "id"]
        data = [tuple(r.get(c) for c in col_list) for r in new_rows]
        placeholders = ",".join("?" * len(col_list))
        sql = f"INSERT OR IGNORE INTO memories({','.join(col_list)}) VALUES({placeholders})"
        dst.executemany(sql, data)
        dst.commit()
        print("inserted:", len(new_rows))

    n = dst.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    mx = dst.execute("SELECT MAX(created_at) FROM memories").fetchone()[0]
    print("dst db now:", n, "rows, newest:", mx)
    return 0


if __name__ == "__main__":
    sys.exit(main())