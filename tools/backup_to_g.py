"""Incremental Backup Script — Syncs azazael-project-e changes to G: archive."""

import subprocess
import shutil
from pathlib import Path
from datetime import datetime

SRC = Path.home() / "Desktop" / "azazael-project-e"
DST = Path("/mnt/windows/g/AZAZAEL/azazael-project-e_backup")
LOG = Path.home() / ".azazael_backup.log"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def sync():
    if not SRC.exists():
        log(f"❌ Source {SRC} not found")
        return False

    DST.mkdir(parents=True, exist_ok=True)
    log(f"Syncing {SRC} → {DST}")

    # Count files before
    src_count = sum(1 for _ in SRC.rglob("*") if _.is_file() and "__pycache__" not in str(_))
    dst_count = sum(1 for _ in DST.rglob("*") if _.is_file() and "__pycache__" not in str(_))

    log(f"Source: {src_count} files | Destination: {dst_count} files")

    # Use rsync for efficient sync
    cmd = [
        "rsync", "-avh", "--delete",
        "--exclude=__pycache__",
        "--exclude=.appdata",
        "--exclude=*.pyc",
        str(SRC) + "/",
        str(DST) + "/",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        # Count new total
        new_dst = sum(1 for _ in DST.rglob("*") if _.is_file() and "__pycache__" not in str(_))
        log(f"✅ Sync complete: {new_dst} files on destination")
        return True
    else:
        log(f"❌ Sync failed: {result.stderr[:200]}")
        return False


def verify():
    """Verify integrity by comparing file counts."""
    src_count = sum(1 for _ in SRC.rglob("*") if _.is_file() and "__pycache__" not in str(_))
    dst_count = sum(1 for _ in DST.rglob("*") if _.is_file() and "__pycache__" not in str(_))
    match = src_count == dst_count
    log(f"Verification: {src_count} src vs {dst_count} dst — {'✅ MATCH' if match else '❌ MISMATCH'}")
    return match


if __name__ == "__main__":
    log("=" * 50)
    log("Starting incremental backup")
    if sync():
        verify()
    log("Backup complete")
    log("=" * 50)
