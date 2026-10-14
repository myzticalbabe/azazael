#!/usr/bin/env python3.14t
"""
sync_all.py - Bidirectional sync across all Azazael environments.

Environments:
  1. Windows 11   : <this tree>                         (primary dev, derived)
  2. WSL2         : /root/azazael                  (Linux build target)
  3. Desktop      : C:/Azazael/desktop/AZAZAEL_Standalone (release)
  4. G: source    : G:/source-of-truth/azazael      (canonical archive)
  5. G: AZAZAEL   : G:/AZAZAEL/AZAZAEL_ROOT          (primary archive)
  6. Kali WSL2    : E:/Kali/azazael                 (Kali Linux security distro)

Usage:
    python3.14t sync_all.py --status          Show sync status
    python3.14t sync_all.py --sync-all        Sync all environments
    python3.14t sync_all.py --sync-to wsl2    Sync Windows to WSL2
    python3.14t sync_all.py --sync-to kali    Sync WSL2 to Kali
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

#: This file lives at <root>/scripts/sync_all.py, so the Windows hub root is
#: derived, never literal (U3/move-day: the tree moved C:/Users/clint/azazael
#: -> C:/Azazael/azazael; a literal would have pinned the old Ort).
_WINDOWS_ROOT = Path(__file__).resolve().parent.parent

ENVIRONMENTS: Dict[str, Dict] = {
    "windows": {
        "label": "Windows 11 (primary dev)",
        "root": _WINDOWS_ROOT,
        "src": _WINDOWS_ROOT / "src",
        "docs": _WINDOWS_ROOT / "docs",
        "tests": _WINDOWS_ROOT / "tests",
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
        "root": Path("C:/Azazael/desktop/AZAZAEL_Standalone"),
        "src": None,
        "docs": Path("C:/Azazael/desktop/AZAZAEL_Standalone/docs"),
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
    "kali": {
        "label": "Kali Linux (WSL2)",
        # The tree lives inside the distro. `E:/Kali/azazael` was never a real
        # path — E:\Kali holds only the distro's ext4.vhdx and an icon — so the
        # environment reported as missing while it was running with a full tree.
        "root": Path("/root/azazael"),
        "src": Path("/root/azazael/src"),
        "docs": Path("/root/azazael/docs"),
        "tests": Path("/root/azazael/tests"),
        "type": "wsl",
        "wsl_distro": "kali-linux",
        "wsl_root_user": True,
    },
}

SYNC_CODE_PATTERNS = [
    "src/CORE/WORMS/expansion/*.py",
    "src/CORE/WORMS/CLUSTERWORMS.py",
    "src/CORE/WORMS/METACLUSTER.py",
    "src/CORE/WORMS/NETWORK_DIAG.py",
    "src/CORE/WORMS/CODEX_TOOLS.py",
    "src/ORCHESTRATION/hydra_bridge.py",
    "tests/*.py",
]

SYNC_DOC_PATTERNS = [
    "docs/*.md",
    "docs/scripts/*.py",
    "LESSONS_*.md",
    "MEMORIES*.md",
    "MASTER_TASKS.md",
    "SYSTEM_INSTRUCTIONS.md",
    "HAT_TAXONOMY.md",
]

SYNC_SCRIPT_PATTERNS = [
    "scripts/*.py",
]

SYNC_SKILL_PATTERNS = [
    "skills/*.md",
]

# WSL environment detection
IS_WSL = Path("/root/azazael").exists()


def _resolve_path(p: Path, env_type: str) -> Path:
    """Resolve a path for the current runtime. Converts C:/G:/ -> /mnt/ on WSL."""
    if IS_WSL and env_type != "wsl":
        return Path(wsl_path(p))
    return p


def run_wsl(cmd: str, timeout: int = 60) -> Tuple[int, str, str]:
    """Run a command inside WSL2 (Ubuntu-26.04).
    
    Execs wsl.exe directly rather than through a shell. `shell=True` on Windows
    means cmd.exe, which does not treat single quotes as quoting and reads
    `2>/dev/null` as a redirection to a file named /dev/null, so every probe came
    back rc=255 "The system cannot find the path specified." and the
    cross-environment verdict was decided by a shell parse error rather than by
    the files. wsl.exe is an ordinary PE binary and execs fine without a shell.
    """
    try:
        result = subprocess.run(
            ["wsl.exe", "-d", "Ubuntu-26.04", "-e", "bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace"
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
    if s.startswith("E:"):
        return "/mnt/e" + s[2:]
    return s


# ═══════════════════════════════════════════════════════════════════════
# Sync Operations
# ═══════════════════════════════════════════════════════════════════════

def _copy_to_wsl(src_file: Path, dest_wsl: str) -> tuple:
    """Copy a file into WSL2 via the \\\\wsl$ UNC path (no shell quoting).

    Falls back to `cp` over wsl.exe when the UNC path is unavailable.
    Returns (ok, error_message).
    """
    unc = "\\\\wsl$\\Ubuntu-26.04" + dest_wsl.replace("/", "\\")
    try:
        Path(unc).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, unc)
        return True, ""
    except OSError as e:
        cmd = f"mkdir -p $(dirname {dest_wsl}) && cp {wsl_path(src_file)} {dest_wsl}"
        rc, _out, err = run_wsl(cmd)
        return (rc == 0), err.strip()


def sync_windows_to_wsl2(dry_run: bool = False) -> Dict[str, Any]:
    """Sync Windows 11 -> WSL2 (code + docs + tests + scripts).
    
    Source: Windows files accessed via /mnt/c/... from WSL2
    Destination: WSL2 native filesystem at /root/azazael/...
    """
    windows_root = ENVIRONMENTS["windows"]["root"]
    all_patterns = SYNC_CODE_PATTERNS + SYNC_DOC_PATTERNS + SYNC_SCRIPT_PATTERNS + SYNC_SKILL_PATTERNS
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

            ok, err_msg = _copy_to_wsl(src_file, dest_wsl)

            if ok:
                synced.append(str(rel_path))
            else:
                errors.append(f"{rel_path}: {err_msg}")

    return {"synced": synced, "errors": errors, "count": len(synced),
            "target": "wsl2"}


def sync_wsl_to_windows(dry_run: bool = False) -> Dict[str, Any]:
    """Sync WSL2 -> Windows 11 (code + docs + skills + scripts).
    
    Source: WSL2 native filesystem at /root/azazael/...
    Destination: Windows files via /mnt/c/Users/clint/azazael/...
    Runs from WSL2 directly — no wsl.exe needed.
    """
    wsl_root = Path("/root/azazael")
    windows_root = Path("/mnt/c/Users/clint/azazael")
    
    if not wsl_root.exists():
        return {"synced": [], "errors": ["WSL root /root/azazael not found"], "count": 0, "target": "windows"}
    if not windows_root.exists():
        return {"synced": [], "errors": ["Windows root /mnt/c/Users/clint/azazael not found"], "count": 0, "target": "windows"}
    
    all_patterns = SYNC_CODE_PATTERNS + SYNC_DOC_PATTERNS + SYNC_SCRIPT_PATTERNS + SYNC_SKILL_PATTERNS
    synced = []
    errors = []
    
    for pattern in all_patterns:
        for src_file in sorted(wsl_root.glob(pattern)):
            rel_path = src_file.relative_to(wsl_root)
            dest = windows_root / rel_path
            
            if dry_run:
                synced.append(str(rel_path))
                continue
            
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src_file, dest)
                synced.append(str(rel_path))
            except OSError as e:
                errors.append(f"{rel_path}: {e}")
    
    return {"synced": synced, "errors": errors, "count": len(synced), "target": "windows"}


def _is_mounted_windows_drive(p: Path) -> bool:
    """True when `p` sits on a mounted Windows drive rather than on the distro's
    own root filesystem.

    `/mnt/g` existed only as an ordinary directory on the WSL root device —
    `/proc/mounts` had /mnt/c and /mnt/e but no /mnt/g. `sync_wsl_to_g` therefore
    copied its whole file set into the distro and reported success, while the
    real G: archives stayed months out of date and nothing failed. Comparing the
    device id is what distinguishes an actual drvfs mount from that trap.
    """
    try:
        return p.stat().st_dev != Path("/").stat().st_dev
    except OSError:
        return False


def sync_wsl_to_g(dry_run: bool = False) -> Dict[str, Any]:
    """Sync WSL2 -> G: archives (both source-of-truth and AZAZAEL_SOURCE_OF_TRUTH).
    
    Runs from WSL2 directly — copies to /mnt/g/ paths.
    """
    wsl_root = Path("/root/azazael")
    g_targets = [
        Path("/mnt/g/source-of-truth/azazael"),
        Path("/mnt/g/AZAZAEL_SOURCE_OF_TRUTH"),
    ]
    
    all_patterns = SYNC_CODE_PATTERNS + SYNC_DOC_PATTERNS + SYNC_SCRIPT_PATTERNS + SYNC_SKILL_PATTERNS
    total_synced = []
    total_errors = []
    
    for g_root in g_targets:
        if not g_root.exists():
            total_errors.append(f"G: target {g_root} not found")
            continue
        if not _is_mounted_windows_drive(g_root):
            total_errors.append(
                f"G: target {g_root} is not a mounted Windows drive (same device "
                f"as /) — refusing to write the archive into the distro's own "
                f"filesystem; mount it with: mount -t drvfs G: /mnt/g"
            )
            continue
        
        for pattern in all_patterns:
            for src_file in sorted(wsl_root.glob(pattern)):
                rel_path = src_file.relative_to(wsl_root)
                dest = g_root / rel_path
                
                if dry_run:
                    total_synced.append(f"{g_root.name}:{rel_path}")
                    continue
                
                dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src_file, dest)
                    total_synced.append(f"{g_root.name}:{rel_path}")
                except OSError as e:
                    total_errors.append(f"{g_root.name}:{rel_path}: {e}")
    
    return {"synced": total_synced, "errors": total_errors, "count": len(total_synced), "target": "g"}


def sync_wsl_to_kali(dry_run: bool = False) -> Dict[str, Any]:
    """Sync WSL2 Ubuntu -> Kali WSL2 via E: drive bridge.
    
    Strategy (batched for performance):
    1. Copy all files from /root/azazael to /mnt/e/kali_sync_temp/ (Windows filesystem bridge)
    2. Run single wsl.exe command to rsync the bridge into Kali's /root/azazael/
    3. Clean up bridge temp files
    """
    wsl_root = Path("/root/azazael")
    e_bridge = Path("/mnt/e/kali_sync_temp")
    kali_root = "/root/azazael"
    
    if not wsl_root.exists():
        return {"synced": [], "errors": ["WSL root /root/azazael not found"], "count": 0, "target": "kali"}
    
    all_patterns = SYNC_CODE_PATTERNS + SYNC_DOC_PATTERNS + SYNC_SCRIPT_PATTERNS + SYNC_SKILL_PATTERNS
    
    # Stage 1: Batch copy all files to E: bridge
    staged = []
    errors = []
    for pattern in all_patterns:
        for src_file in sorted(wsl_root.glob(pattern)):
            rel_path = src_file.relative_to(wsl_root)
            bridge_dest = e_bridge / rel_path
            
            if dry_run:
                staged.append(rel_path)
                continue
            
            bridge_dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src_file, bridge_dest)
                staged.append(rel_path)
            except OSError as e:
                errors.append(f"bridge:{rel_path}: {e}")
    
    if dry_run:
        return {"synced": [str(r) for r in staged], "errors": errors, "count": len(staged), "target": "kali"}
    
    # Stage 2: Single batch copy from E: bridge into Kali
    rc, stdout, stderr = run_wsl_kali(
        f"mkdir -p {kali_root} && cp -r /mnt/e/kali_sync_temp/* {kali_root}/"
    )
    
    if rc != 0:
        errors.append(f"kali batch copy failed: {stderr.strip()}")
        errors.append("Files staged at /mnt/e/kali_sync_temp/ — run manually in Kali:")
        errors.append(f"  cp -r /mnt/e/kali_sync_temp/* {kali_root}/")
        # Don't clean up bridge on failure — user may need the files
        return {"synced": [str(r) for r in staged], "errors": errors, "count": len(staged), "target": "kali"}
    
    # Stage 3: Clean up bridge temp files (only on success)
    try:
        shutil.rmtree(e_bridge, ignore_errors=True)
    except OSError:
        pass
    
    return {"synced": [str(r) for r in staged], "errors": errors, "count": len(staged), "target": "kali"}


def run_wsl_kali(cmd: str, timeout: int = 60) -> Tuple[int, str, str]:
    """Run a command inside Kali WSL2 distro.
    
    Execs wsl.exe directly rather than through a shell, for the same reason as
    `run_wsl`: cmd.exe mangles the quoting and the `2>/dev/null` redirect, so a
    shell-routed probe reports rc=255 while looking like a filesystem problem.
    """
    try:
        result = subprocess.run(
            ["wsl.exe", "-d", "kali-linux", "-u", "root", "-e", "bash", "-c", cmd],
            capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace"
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -1, "", "WSL/kali-linux not available"


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
    """Get status of an environment — works from both Windows and WSL."""
    env_type = env_info["type"]
    
    # A WSL2 distro keeps its tree inside the distro, so a host-side stat() of the
    # root always fails and the generic branch below would report a running
    # distro as unavailable purely because of where the script was launched.
    # Probe through wsl.exe instead, from Windows as well as from WSL.
    if env_type == "wsl" and not IS_WSL:
        runner = run_wsl_kali if env_info.get("wsl_distro") == "kali-linux" else run_wsl
        tree = str(env_info["root"]).replace("\\", "/")
        status: dict[str, Any] = {
            "name": env_name,
            "label": env_info["label"],
            "type": env_type,
        }
        rc, _, _ = runner(f"test -d {tree}")
        status["available"] = (rc == 0)
        if not status["available"]:
            status["warning"] = f"{tree} not accessible via wsl.exe"
            return status
        # Count via wsl.exe
        rc_py, out_py, _ = runner(f"find {tree}/src -name '*.py' 2>/dev/null | wc -l")
        status["py_files"] = int(out_py.strip()) if rc_py == 0 and out_py.strip().isdigit() else 0
        rc_docs, out_docs, _ = runner(f"ls {tree}/docs/*.md 2>/dev/null | wc -l")
        status["docs"] = int(out_docs.strip()) if rc_docs == 0 and out_docs.strip().isdigit() else 0
        return status
    
    root = _resolve_path(env_info["root"], env_type)

    status = {
        "name": env_name,
        "label": env_info["label"],
        "type": env_type,
        "available": root.exists(),
    }
    if not status["available"]:
        status["warning"] = "Environment root not accessible"
        return status

    # Count .py files
    src = env_info.get("src")
    if src:
        src_path = _resolve_path(src, env_type)
        if src_path.exists():
            status["py_files"] = len(list(src_path.rglob("*.py")))
        else:
            status["py_files"] = 0
    else:
        status["py_files"] = 0

    # Count .md docs
    docs = env_info.get("docs")
    if docs:
        docs_path = _resolve_path(docs, env_type)
        if docs_path.exists():
            status["docs"] = len(list(docs_path.glob("*.md")))
        else:
            status["docs"] = 0
    else:
        status["docs"] = 0

    if env_info.get("exe_only"):
        status["exe_files"] = len(list(root.glob("*.exe")))
    return status


def verify_integrity() -> Dict[str, bool]:
    """Verify file integrity across environments — works from both Windows and WSL."""
    results: dict[str, bool] = {}

    # Resolve environment roots for current runtime
    win_type = ENVIRONMENTS["windows"]["type"]
    g_source_type = ENVIRONMENTS["g_source"]["type"]
    win_root = _resolve_path(ENVIRONMENTS["windows"]["root"], win_type)
    g_source = _resolve_path(ENVIRONMENTS["g_source"]["root"], g_source_type)
    wsl_root = Path("/root/azazael") if IS_WSL else None

    # Helper: get filenames from a WSL distro. Ubuntu-26.04 and Kali both keep
    # their tree at /root/azazael, so the *distro* — not the path — is what must
    # select the runner. Keying on the path alone made the two distros
    # indistinguishable and let Kali diverge unseen (D-2).
    def wsl_files(subpath: str, ext: str = "*.py", distro: str = "ubuntu") -> set[str]:
        if IS_WSL and wsl_root and distro == "ubuntu":
            p = wsl_root / subpath
            return set(f.name for f in p.glob(ext)) if p.exists() else set()
        runner = run_wsl_kali if distro == "kali" else run_wsl
        rc, stdout, _ = runner(f"ls /root/azazael/{subpath}/{ext} 2>/dev/null")
        if rc != 0 or not stdout.strip():
            return set()
        return set(Path(f).name for f in stdout.strip().split("\n") if f)

    # 1. Code: expansion/ parity, Windows vs each distro. Ubuntu and Kali are
    #    probed separately — a shared "/root/azazael" must not merge verdicts.
    win_exp_path = win_root / "src/CORE/WORMS/expansion"
    win_exp = set(f.name for f in win_exp_path.glob("*.py")) if win_exp_path.exists() else set()
    results["expansion"] = win_exp == wsl_files("src/CORE/WORMS/expansion")
    results["expansion_kali"] = win_exp == wsl_files("src/CORE/WORMS/expansion", distro="kali")

    # 2. Docs: Windows vs G: source-of-truth. Fail closed: an unmounted G: is an
    #    *unknown* archive, not a passing one (D-3). `if g_docs else True` turned
    #    a missing drive into a green result.
    win_docs_path = win_root / "docs"
    win_docs = set(f.name for f in win_docs_path.glob("*.md")) if win_docs_path.exists() else set()
    g_docs_path = g_source / "docs"
    g_docs = set(f.name for f in g_docs_path.glob("*.md")) if g_docs_path.exists() else set()
    results["docs_g"] = bool(g_docs) and win_docs.issubset(g_docs)

    # 3. Tests: Windows vs each distro (subset check)
    win_tests_path = win_root / "tests"
    win_tests = set(f.name for f in win_tests_path.glob("*.py")) if win_tests_path.exists() else set()
    wsl_tests = wsl_files("tests")
    results["tests"] = win_tests.issubset(wsl_tests) if wsl_tests else False
    kali_tests = wsl_files("tests", distro="kali")
    results["tests_kali"] = win_tests.issubset(kali_tests) if kali_tests else False

    # 4. Scripts: Windows vs each distro (subset check)
    win_scripts_path = win_root / "scripts"
    win_scripts = set(f.name for f in win_scripts_path.glob("*.py")) if win_scripts_path.exists() else set()
    wsl_scripts = wsl_files("scripts")
    results["scripts"] = win_scripts.issubset(wsl_scripts) if wsl_scripts else False
    kali_scripts = wsl_files("scripts", distro="kali")
    results["scripts_kali"] = win_scripts.issubset(kali_scripts) if kali_scripts else False

    # 5. Desktop release (D-1): the standalone folder is a build artifact
    #    tree, not a mirror, so parity is the wrong check — presence of the
    #    release markers is. Without this, verify could report ALL SYNCED
    #    while the release folder was deleted out from under it.
    desk = ENVIRONMENTS.get("desktop", {}).get("root")
    if desk is not None:
        desk = _resolve_path(desk, ENVIRONMENTS["desktop"].get("type"))
        results["desktop"] = bool(
            desk and desk.is_dir()
            and (desk / "docs").is_dir() and (desk / "skills").is_dir())
    else:
        results["desktop"] = False

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
    parser.add_argument("--sync-to", choices=["wsl2", "windows", "g", "desktop", "kali"])
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
        # Skip Windows→WSL direction when already on WSL
        if Path("/root/azazael").exists():
            print("Skipping Windows -> WSL2 (already on WSL)")
        else:
            print("Syncing Windows -> WSL2...")
            r = sync_windows_to_wsl2(dry_run=args.dry_run)
            print(f"  {r['count']} files synced")
            for e in r.get("errors", []):
                print(f"  ERROR: {e}")

    if args.sync_to == "windows" or args.sync_all:
        print("Syncing WSL2 -> Windows 11...")
        r = sync_wsl_to_windows(dry_run=args.dry_run)
        print(f"  {r['count']} files synced")
        for e in r.get("errors", []):
            print(f"  ERROR: {e}")

    if args.sync_to == "g" or args.sync_all:
        # Try G: via /mnt/g/ (WSL2) first, then fall back to Windows paths
        g_wsl = Path("/mnt/g/source-of-truth/azazael")
        if g_wsl.exists() or Path("/mnt/g/AZAZAEL_SOURCE_OF_TRUTH").exists():
            print("Syncing WSL2 -> G: archives...")
            r = sync_wsl_to_g(dry_run=args.dry_run)
            print(f"  {r['count']} files synced")
            for e in r.get("errors", []):
                print(f"  ERROR: {e}")
        else:
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

    if args.sync_to == "kali" or args.sync_all:
        print("Syncing WSL2 -> Kali Linux via E: bridge...")
        r = sync_wsl_to_kali(dry_run=args.dry_run)
        print(f"  {r['count']} files synced")
        for e in r.get("errors", []):
            print(f"  ERROR: {e}")

    if args.sync_all:
        print(f"\nFull sync complete - {ts}")


if __name__ == "__main__":
    main()
