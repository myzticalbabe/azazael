#!/usr/bin/env python3
"""


__all__ = [
    "cmd_backup",
    "cmd_config",
    "cmd_inference",
    "cmd_stats",
    "cmd_status",
    "cmd_status_json",
    "main",
]

azazael_ctl.py — Unified Azazael CLI (crossref, audit, memory, inference).

Usage:
    azazael-ctl crossref <subcommand> [args]
    azazael-ctl audit <subcommand> [args]
    azazael-ctl memory <subcommand> [args]
    azazael-ctl inference <subcommand> [args]
    azazael-ctl status
    azazael-ctl help
"""

import sys
import os
import json
import time
import shutil
from pathlib import Path

# Lock file — prevent concurrent writes
_LOCK_FILE = Path.home() / ".azazael" / "ctl.lock"

# Color support (disabled if not a TTY)
_COLORS = sys.stdout.isatty()


def _acquire_lock():
    """Acquire a lock file to prevent concurrent azazael-ctl processes."""
    _LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        import fcntl
        _lock_fd = os.open(str(_LOCK_FILE), os.O_CREAT | os.O_RDWR)
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except (ImportError, IOError, OSError):
        # Windows or lock contention
        if _LOCK_FILE.exists():
            age = time.time() - _LOCK_FILE.stat().st_mtime
            if age < 30:  # Lock is fresh (<30s old)
                print(_color("Another azazael-ctl process may be running. Use --force to override.", "red"))
                return False
            # Stale lock — override
        _LOCK_FILE.touch()
        return True


def _release_lock():
    """Release the lock file."""
    try:
        if _LOCK_FILE.exists():
            _LOCK_FILE.unlink()
    except Exception:
        pass

def _color(text: str, code: str) -> str:
    if not _COLORS:
        return text
    codes = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
        "bold": "\033[1m", "dim": "\033[2m", "reset": "\033[0m",
    }
    return f"{codes.get(code, '')}{text}{codes.get('reset', '')}"


def _progress_bar(current: int, total: int, label: str = "") -> str:
    """Simple progress bar for CLI."""
    if not _COLORS:
        return f"{label} {current}/{total}"
    width = min(40, shutil.get_terminal_size().columns - 30)
    filled = int(width * current / max(total, 1))
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * current / max(total, 1))
    return f"{label} [{bar}] {pct}% ({current}/{total})"


def cmd_status(json_output: bool = False):
    cols, _ = shutil.get_terminal_size()
    header = _color("  AZAZAEL System Status", "bold")
    print("=" * cols)
    print(header)
    print("=" * cols)
    from CORE.direct_memory import DirectMemory
    from CORE.audit_trail import verify_on_startup
    try:
        s = DirectMemory.get_mapping_summary()
        print(f"\n  {_color('Cross-Reference:', 'cyan')}")
        print(f"    Total mappings:   {_color(str(s.get('total_mappings', '?')), 'green')}")
        print(f"    Linked DM:        {s.get('unique_dm_sessions', '?')}")
        print(f"    Linked AJ:        {s.get('unique_aj_sessions', '?')}")
    except Exception as e:
        print(f"  DM error: {e}")

    try:
        broken = verify_on_startup()
        print(f"\n  {_color('Audit Trail:', 'magenta')}")
        broken_count = len(broken)
        clr = "red" if broken_count > 0 else "green"
        print(f"    Broken files:     {_color(str(broken_count), clr)}")
        for b in broken:
            print(f"      {b.get('file', '?')[-40:]}")
    except Exception as e:
        print(f"  Audit error: {e}")

    print(f"\n  {_color('Inference Pool:', 'yellow')}")
    try:
        from CORE.inference_pool import InferencePool
        pool = InferencePool(max_concurrent=1)
        health = pool.health()
        status_text = _color("Online", "green") if health.get("healthy") else _color("Offline", "red")
        print(f"    Status:           {status_text}")
        print(f"    Max concurrent:   {pool.stats['max_concurrent']}")
        print(f"    VRAM:             {pool.stats['vram_gb']}GB")
    except Exception as e:
        print(f"    Not available: {e}")

    from CORE.freethreading import print_thread_info
    print(f"\n  {_color('Python:', 'blue')}")
    print_thread_info()
    open_cnt = DirectMemory.get_open_sessions_count()
    open_clr = "yellow" if open_cnt > 0 else "green"
    print(f"  Open sessions:    {_color(str(open_cnt), open_clr)}")


def cmd_status_json():
    """JSON status output for programmatic consumption."""
    from CORE.direct_memory import DirectMemory
    from CORE.audit_trail import verify_on_startup
    s = DirectMemory.get_mapping_summary()
    broken = verify_on_startup()
    report = {
        "crossref": {"total": s.get("total_mappings",0), "dm": s.get("unique_dm_sessions",0), "aj": s.get("unique_aj_sessions",0)},
        "audit": {"broken": len(broken), "files": [b.get("file","") for b in broken]},
        "sessions": {"open": DirectMemory.get_open_sessions_count()},
    }
    print(json.dumps(report, indent=2))


def cmd_backup(output_dir: str = None):
    """Backup memory_store.db and .audit/ to a directory."""
    import shutil
    from datetime import datetime
    from pathlib import Path
    from CORE.direct_memory import DB_PATH
    out = Path(output_dir or f"azazael_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    out.mkdir(parents=True, exist_ok=True)
    # Copy DB
    db_path = Path(str(DB_PATH))
    items = []
    if db_path.exists():
        items.append(db_path)
    from CORE.audit_trail import AUDIT_DIR
    if AUDIT_DIR.exists():
        items.extend(sorted(AUDIT_DIR.glob("*.jsonl")))
    total = len(items)
    for idx, src in enumerate(items, 1):
        dest = out / src.name
        shutil.copy2(str(src), str(dest))
        print(f"\r{_progress_bar(idx, total, 'Backup:')}")
        if _COLORS:
            print(f"  {src.name} -> {dest.name}", end="\033[K\n")
        else:
            print(f"  {src.name} -> {dest.name}")
    print()
    print(f"\n  {_color('Backup saved to:', 'green')} {out.resolve()}")


def cmd_config():
    """Print current configuration."""
    from CORE.direct_memory import DB_PATH
    from CORE.audit_trail import AUDIT_DIR
    from CORE.inference_pool import OLLAMA_BASE
    print("=== Azazael Configuration ===")
    print(f"  DB path:          {DB_PATH}")
    print(f"  Audit dir:        {AUDIT_DIR.resolve()}")
    print(f"  Ollama base:      {OLLAMA_BASE}")
    print(f"  Python:           {sys.version.split()[0]}")
    import platform
    print(f"  Platform:         {platform.system()} {platform.release()}")
    print(f"  Free-threading:   {'yes' if __import__('CORE.freethreading', fromlist=['is_free_threaded']).is_free_threaded() else 'no'}")
    print(f"  AZAZAEL_MEMORY_DIR: {os.environ.get('AZAZAEL_MEMORY_DIR', '(not set)')}")


def cmd_stats():
    """Print system statistics."""
    from CORE.direct_memory import DirectMemory
    print("=== Azazael Statistics ===")
    s = DirectMemory.summary_stats()
    print(f"  Total events:     {s.get('total_events', '?')}")
    print(f"  Sessions:         {s.get('sessions', '?')}")
    print(f"  Event types:      {len(s.get('by_type', {}))}")
    print(f"  Open sessions:    {DirectMemory.get_open_sessions_count()}")
    print(f"  DB size:          {DirectMemory.db_size().get('total_mb', '?')} MB")
    by_type = s.get('by_type', {})
    print("\n  Top event types:")
    for et, cnt in sorted(by_type.items(), key=lambda x: -x[1])[:10]:
        print(f"    {et:30s} {cnt}")


def cmd_inference(args: list):
    """InferencePool subcommands."""
    from CORE.inference_pool import InferencePool
    pool = InferencePool()
    if not args or args[0] == "benchmark":
        model = args[1] if len(args) > 1 else "llama3.2:1b"
        iterations = int(args[2]) if len(args) > 2 and args[2].isdigit() else 5
        result = pool.benchmark(model=model, iterations=iterations)
        for k, v in result.items():
            print(f"  {k}: {v}")
    elif args[0] == "models":
        models = pool.list_models()
        if models:
            for m in models:
                print(f"  {m.get('name', '?')}")
        else:
            print("  No models found (Ollama not running?)")
    elif args[0] == "classify":
        text = " ".join(args[1:])
        result = pool.infer(f"Classify: {text}")
        print(result.get("response", result.get("error", "?")))
    elif args[0] == "stats":
        for k, v in pool.stats.items():
            print(f"  {k}: {v}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    # Handle --json flag (must be before section)
    json_output = "--json" in args
    if json_output:
        args.remove("--json")

    section = args[0]
    rest_args = args[1:]

    if section == "doctor":
        from CORE.doctor import cmd_doctor
        cmd_doctor()
    elif section == "verify":
        from CORE.doctor import cmd_verify
        report = cmd_verify()
        sys.exit(0 if report.get("healthy") else 1)
    elif section == "config":
        cmd_config()
    elif section == "stats":
        cmd_stats()
    elif section == "maintain":
        dry_run = "--dry-run" in rest_args
        if dry_run:
            print("  DRY RUN — no changes will be made")
        else:
            from CORE.data_retention import cmd_maintain
            cmd_maintain()
    elif section == "backup":
        cmd_backup(rest_args[0] if rest_args else None)
    elif section == "dashboard":
        from CORE.xref_dashboard import generate_html
        result = generate_html()
        print(f"  Dashboard: {result}")
    elif section == "status":
        if "--watch" in rest_args:
            # Watch mode: poll periodically
            interval = 2
            try:
                idx = rest_args.index("--interval")
                if idx + 1 < len(rest_args):
                    interval = int(rest_args[idx + 1])
            except (ValueError, IndexError):
                pass
            try:
                while True:
                    print("\033[2J\033[H", end="")
                    if json_output:
                        cmd_status_json()
                    else:
                        cmd_status()
                    print(f"\n{_color('Watching... Ctrl+C to stop', 'dim')} (every {interval}s)")
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopped.")
        elif json_output:
            cmd_status_json()
        else:
            cmd_status()
    elif section == "crossref":
        from CORE.cli_crossref import main as xref_main
        sys.argv = [sys.argv[0]] + rest_args + (["--json"] if json_output else [])
        xref_main()
    elif section == "audit":
        from CORE.cli_audit import main as audit_main
        sys.argv = [sys.argv[0]] + rest_args
        audit_main()
    elif section == "memory":
        from CORE.cli_memory import main as mem_main
        sys.argv = [sys.argv[0]] + rest_args
        mem_main()
    elif section == "inference":
        cmd_inference(rest_args)
    elif section in ("help", "--help", "-h"):
        print(__doc__)
    else:
        print(f"Unknown section: {section}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    try:
        locked = _acquire_lock()
        if locked:
            main()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    finally:
        _release_lock()
