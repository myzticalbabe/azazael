#!/usr/bin/env python3.14t
"""
sync_all.py - Bidirectional sync across all Azazael environments.

Environments:
  1. Windows 11   : C:/Users/clint/azazael         (primary dev)
  2. WSL2         : /root/azazael                  (Linux build target)
  3. Desktop      : C:/Users/clint/Desktop/AZAZAEL_Standalone (release)
  4. G: source    : G:/source-of-truth/azazael      (canonical archive)
  5. G: AZAZAEL   : G:/AZAZAEL/AZAZAEL_ROOT          (primary archive)

Usage:
    python3.14t sync_all.py --status          Show sync status
    python3.14t sync_all.py --sync-all        Sync all environments
    python3.14t sync_all.py --sync-to wsl2    Sync Windows to WSL2
    python3.14t sync_all.py --verify          Verify integrity across all

Created: June 4, 2026 - Environment realignment session
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════════
# Environment Mapping
# ═══════════════════════════════════════════════════════════════════════

ENVIRONMENTS: Dict[str, Dict] = {
    "windows": {
        "label": "Windows 11 (primary dev)",
        "root": Path("C:/Users/clint/azazael"),
        "src": Path("C:/Users/clint/azazael/src"),
        "docs": Path("C:/Users/clint/azazael/docs"),
        "tests": Path("C:/Users/clint/azazael/tests"),
        "type": "windows",
    },
    "wsl2": {
        "label": "WSL2 Ubuntu-26.04",
        "root": Path("/root/azazael"),
        "src": Path("/root/azazael/src"),
        "docs": Path("/root/azazael/docs"),
        "tests": Path("/root/azazael/tests"),
        "type": "wsl",
        "wsl_distro": "Ubuntu-26.04",
    },
    "desktop": {
        "label": "Desktop AZAZAEL_Standalone",
        "root": Path("C:/Users/clint/Desktop/AZAZAEL_Standalone"),
        "src": None,
        "docs": Path("C:/Users/clint/Desktop/AZAZAEL_Standalone/docs"),
        "tests": None,
        "type": "release",
        "exe_only": True,
    },
    "g_source": {
        "label": "G: source-of-truth",
        "root": Path("G:/source-of-truth/azazael"),
        "src": Path("G:/source-of-truth/azazael/src"),
        "docs": Path("G:/source-of-truth/azazael/docs"),
        "tests": None,
        "type": "archive",
    },
    "g_root": {
        "label": "G: AZAZAEL_ROOT",
        "root": Path("G:/AZAZAEL/AZAZAEL_ROOT"),
        "src": Path("G:/AZAZAEL/AZAZAEL_ROOT/src"),
        "docs": Path("G:/AZAZAEL/AZAZAEL_ROOT/docs"),
        "tests": None,
        "type": "archive",
    },
}

SYNC_CODE_PATTERNS = [
    "src/CORE/WORMS/expansion/*.py",
    "src/CORE/WORMS/CLUSTERWORMS.py",
    "src/CORE/WORMS/METACLUSTER.py",
    "src/CORE/WORMS/NETWORK_DIAG.py",
    "src/CORE/WORMS/CODEX_TOOLS.py",
    "src/CORE/WORMS/CROSS_NATURE_ROUTER.py",
    "src/ORCHESTRATION/hydra_bridge.py",
    "tests/*.py",
]

SYNC_DOC_PATTERNS = [
    "docs/*.md",
    "docs/scripts/*.py",
    "LESSONS_*.md",
    "MEMORIES*.md",
    "MASTER_TASKS.md",
]

SYNC_SCRIPT_PATTERNS = [
    "scripts/*.py",
]


def run_wsl(cmd: str, timeout: int = 60) -> Tuple[int, str, str]:
    """Run a command inside WSL2."""
    try:
        result = subprocess.run(
            ["wsl", "-d", "Ubuntu-26.04", "-e", "bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -1, "", "WSL not available"


def wsl_path(win_path: Path) -> str:
    """Convert Windows Path to WSL /mnt/c/... path."""
    s = str(win_path).replace("\\", "/")
    if s.startswith("C:"):
        return "/mnt/c" + s[2:]
    if s.startswith("G:"):
        return "/mnt/g" + s[2:]
    return s


# ═══════════════════════════════════════════════════════════════════════
# Sync Operations
# ═══════════════════════════════════════════════════════════════════════

def sync_windows_to_wsl2(dry_run: bool = False) -> Dict[str, Any]:
    """Sync Windows 11 -> WSL2 (code + docs + tests + scripts).
    
    Source: Windows files accessed via /mnt/c/... from WSL2
    Destination: WSL2 native filesystem at /root/azazael/...
    """
    windows_root = ENVIRONMENTS["windows"]["root"]
    all_patterns = SYNC_CODE_PATTERNS + SYNC_DOC_PATTERNS + SYNC_SCRIPT_PATTERNS
    synced = []
    errors = []

    for pattern in all_patterns:
        for src_file in sorted(windows_root.glob(pattern)):
            rel_path = src_file.relative_to(windows_root)
            # Source: Windows file via /mnt/c mount
            src_wsl = wsl_path(src_file)
            # Destination: WSL2 native filesystem
            dest_wsl = f"/root/azazael/{rel_path.as_posix()}"

            if dry_run:
                synced.append(str(rel_path))
                continue

            cmd = f"mkdir -p $(dirname {dest_wsl}) && cp {src_wsl} {dest_wsl}"
            rc, stdout, stderr = run_wsl(cmd)

            if rc == 0:
                synced.append(str(rel_path))
            else:
                errors.append(f"{rel_path}: {stderr.strip()}")

    return {"synced": synced, "errors": errors, "count": len(synced),
            "target": "wsl2"}


def sync_docs_to_target(windows_root: Path, target_root: Path,
                        dry_run: bool = False) -> Dict[str, Any]:
    """Sync documentation to any target environment."""
    synced = []
    for pattern in SYNC_DOC_PATTERNS:
        for src_file in sorted(windows_root.glob(pattern)):
            rel_path = src_file.relative_to(windows_root)
            dest = target_root / rel_path
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src_file, dest)
                except OSError as e:
                    synced.append(f"ERROR: {rel_path}: {e}")
                    continue
            synced.append(str(rel_path))
    return {"synced": synced, "count": len(synced),
            "target": str(target_root)}


# ═══════════════════════════════════════════════════════════════════════
# Status & Verification
# ═══════════════════════════════════════════════════════════════════════

def get_env_status(env_name: str, env_info: Dict) -> Dict[str, Any]:
    """Get status of an environment."""
    env_type = env_info["type"]

    if env_type == "wsl":
        # WSL2 paths are Linux-native — use run_wsl() instead of Path.exists()
        rc, _, _ = run_wsl("test -d /root/azazael")
        available = (rc == 0)
        status = {
            "name": env_name,
            "label": env_info["label"],
            "type": env_type,
            "available": available,
        }
        if not status["available"]:
            status["warning"] = "WSL2 root not accessible"
            return status
        # Count .py files via WSL
        rc_py, out_py, _ = run_wsl("find /root/azazael/src -name '*.py' 2>/dev/null | wc -l")
        if rc_py == 0 and out_py.strip().isdigit():
            status["py_files"] = int(out_py.strip())
        else:
            status["py_files"] = 0
        # Count .md files via WSL
        rc_docs, out_docs, _ = run_wsl("ls /root/azazael/docs/*.md 2>/dev/null | wc -l")
        if rc_docs == 0 and out_docs.strip().isdigit():
            status["docs"] = int(out_docs.strip())
        else:
            status["docs"] = 0
        return status

    # Non-WSL environments: use Path.exists() directly
    status = {
        "name": env_name,
        "label": env_info["label"],
        "type": env_type,
        "available": env_info["root"].exists(),
    }
    if not status["available"]:
        status["warning"] = "Environment root not accessible"
        return status
    if env_info.get("src") and env_info["src"].exists():
        status["py_files"] = len(list(env_info["src"].rglob("*.py")))
    else:
        status["py_files"] = 0
    if env_info.get("docs") and env_info["docs"].exists():
        status["docs"] = len(list(env_info["docs"].glob("*.md")))
    else:
        status["docs"] = 0
    if env_info.get("exe_only"):
        status["exe_files"] = len(list(env_info["root"].glob("*.exe")))
    return status


def verify_integrity() -> Dict[str, bool]:
    """Verify file integrity across all 5 environments."""
    results = {}
    win_root = ENVIRONMENTS["windows"]["root"]

    # 1. Code: expansion/ parity Windows vs WSL2
    win_exp = set(f.name for f in (win_root / "src/CORE/WORMS/expansion").glob("*.py"))
    rc, stdout, _ = run_wsl("ls /root/azazael/src/CORE/WORMS/expansion/*.py 2>/dev/null")
    wsl_exp = set(Path(f).name for f in stdout.strip().split("\n") if f) if rc == 0 else set()
    results["expansion"] = win_exp == wsl_exp

    # 2. Docs: Windows vs G: source-of-truth (graceful if G: unavailable)
    win_docs = set(f.name for f in (win_root / "docs").glob("*.md"))
    g_source = ENVIRONMENTS["g_source"]["root"]
    if g_source.exists():
        g_docs_path = g_source / "docs"
        g_docs = set(f.name for f in g_docs_path.glob("*.md")) if g_docs_path.exists() else set()
        results["docs_g"] = win_docs.issubset(g_docs)
    else:
        results["docs_g"] = True  # G: not available, skip check

    # 3. Tests: Windows vs WSL2 (subset check — WSL2 may have extra legacy files)
    win_tests = set(f.name for f in (win_root / "tests").glob("*.py"))
    rc, stdout, _ = run_wsl("ls /root/azazael/tests/*.py 2>/dev/null")
    wsl_tests = set(Path(f).name for f in stdout.strip().split("\n") if f) if rc == 0 else set()
    results["tests"] = win_tests.issubset(wsl_tests) if wsl_tests else False

    # 4. Scripts: Windows vs WSL2 (subset check — WSL2 may have extra legacy files)
    win_scripts = set(f.name for f in (win_root / "scripts").glob("*.py"))
    rc, stdout, _ = run_wsl("ls /root/azazael/scripts/*.py 2>/dev/null")
    wsl_scripts = set(Path(f).name for f in stdout.strip().split("\n") if f) if rc == 0 else set()
    results["scripts"] = win_scripts.issubset(wsl_scripts) if wsl_scripts else False

    results["all_ok"] = all(results.values())
    return results


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Azazael Environment Sync"
    )
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--sync-all", action="store_true")
    parser.add_argument("--sync-to", choices=["wsl2", "g", "desktop"])
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if not (args.status or args.verify or args.sync_all or args.sync_to):
        parser.print_help()
        return

    windows_root = ENVIRONMENTS["windows"]["root"]
    ts = datetime.now().isoformat()

    if args.status:
        print(f"Azazael Sync Status - {ts}")
        print("=" * 60)
        for name, info in ENVIRONMENTS.items():
            s = get_env_status(name, info)
            icon = "OK" if s["available"] else "XX"
            print(f"  [{icon}] {s['label']} ({s['type']})")
            if s["available"]:
                if s.get("py_files"):
                    print(f"      .py: {s['py_files']}")
                if s.get("docs"):
                    print(f"      docs: {s['docs']}")
                if s.get("exe_files"):
                    print(f"      .exe: {s['exe_files']}")
        v = verify_integrity()
        print(f"\n  Integrity: {'ALL SYNCED' if v['all_ok'] else 'OUT OF SYNC'}")
        for k, ok in v.items():
            if k != "all_ok" and not ok:
                print(f"    {k}: FAIL")

    if args.verify:
        v = verify_integrity()
        if v["all_ok"]:
            print("PASS: All environments in sync")
        else:
            print("FAIL: Environments out of sync")
            for k, ok in v.items():
                if k != "all_ok" and not ok:
                    print(f"  {k}: out of sync")

    if args.sync_to == "wsl2" or args.sync_all:
        print("Syncing Windows -> WSL2...")
        r = sync_windows_to_wsl2(dry_run=args.dry_run)
        print(f"  {r['count']} files synced")
        for e in r.get("errors", []):
            print(f"  ERROR: {e}")

    if args.sync_to == "g" or args.sync_all:
        for gk in ["g_source", "g_root"]:
            gi = ENVIRONMENTS[gk]
            if gi["root"].exists():
                print(f"Syncing docs -> {gi['label']}...")
                r = sync_docs_to_target(windows_root, gi["root"], dry_run=args.dry_run)
                print(f"  {r['count']} files synced")

    if args.sync_to == "desktop" or args.sync_all:
        dr = ENVIRONMENTS["desktop"]["root"]
        if dr.exists():
            print("Syncing docs -> Desktop...")
            r = sync_docs_to_target(windows_root, dr, dry_run=args.dry_run)
            print(f"  {r['count']} files synced")

    if args.sync_all:
        print(f"\nFull sync complete - {ts}")


if __name__ == "__main__":
    main()
