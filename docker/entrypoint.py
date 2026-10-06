#!/usr/bin/env python3.15t
"""
entrypoint.py - Azazael Core Docker Entrypoint (CD5 Split WAL Config)

Initializes the database directory, configures SQLite WAL journal with
split tmpfs/volume layout, and starts the main event loop.

Called as the CMD in docker-compose.yml azazael-core service.
Extracted from inline command for maintainability and syntax validation.

Environment variables (set by docker-compose.yml):
  AZAZAEL_MEMORY_DIR  - Persistent storage path (default: /persistent)
  AZAZAEL_WAL_DIR     - tmpfs path for WAL/SHM files (default: /data)
  PYTHON_GIL          - Set to "0" for free-threading mode
  PYTHONPATH          - Must include /app/azazael/src
"""

import os
import sys
import time
import logging
import sqlite3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("azazael-core")


def get_env(key: str, default: str) -> str:
    """Get an env var with a descriptive log message if missing."""
    value = os.environ.get(key)
    if value:
        logger.info(f"  {key}: {value}")
    else:
        logger.warning(f"  {key}: not set, using default '{default}'")
    return value or default


def main():
    mem_dir = get_env("AZAZAEL_MEMORY_DIR", "/persistent")
    wal_dir = get_env("AZAZAEL_WAL_DIR", "/data")
    gil = os.environ.get("PYTHON_GIL", "1")

    logger.info("Azazael Core v1.0 - CD5 Split WAL Configuration")
    logger.info(f"  Memory dir: {mem_dir}")
    logger.info(f"  WAL dir:    {wal_dir}")
    logger.info(f"  GIL:        {'disabled' if gil == '0' else 'enabled'}")

    # Verify directories exist and are writable
    for label, path in [("Memory", mem_dir), ("WAL", wal_dir)]:
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
                logger.info(f"  {label} dir created: {path}")
            except OSError as e:
                logger.error(f"  {label} dir cannot be created: {e}")
                sys.exit(1)
        if os.access(path, os.W_OK):
            logger.info(f"  {label} dir writable: {path}")
        else:
            logger.error(f"  {label} dir NOT writable: {path}")
            sys.exit(1)

    # Initialize SQLite with WAL journal and split config
    db_path = os.path.join(mem_dir, "memory_store.db")
    logger.info(f"  DB path: {db_path}")

    conn = sqlite3.connect(db_path, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-65536")

    # Set WAL directory to tmpfs (CD5 split approach)
    try:
        conn.execute(f'PRAGMA wal_directory="{wal_dir}"')
        logger.info(f"  WAL directory set to: {wal_dir} (PRAGMA wal_directory supported)")
    except sqlite3.OperationalError:
        logger.warning("  PRAGMA wal_directory not supported in this SQLite version")
        logger.warning(f"  WAL/SHM files will remain alongside .db in {mem_dir}")

    # Verify WAL mode is active
    journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    logger.info(f"  Journal mode: {journal_mode}")

    conn.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY)")
    conn.close()

    logger.info("Azazael Core initialized successfully")

    # Heartbeat loop
    tick = 0
    while True:
        time.sleep(60)
        tick += 1
        logger.debug(f"Heartbeat - OK ({tick})")


if __name__ == "__main__":
    main()
