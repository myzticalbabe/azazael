#!/usr/bin/env python3
# coding: utf-8
"""box_trees -- see all trees on this box in one view.

Scans known roots for git repos (dirs containing .git) plus top-level
project dirs, and prints one table: path, kind, branch, HEAD, dirty count.
Writes JSON to ~/yggdrasil_forest/box_trees.json for other tools.

Usage:
  python azazael/tools/box_trees.py                 # human table
  python azazael/tools/box_trees.py --json          # JSON to stdout
  python azazael/tools/box_trees.py --write path    # write JSON elsewhere
  python azazael/tools/box_trees.py --install-startup  # logon VBS in Startup folder
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from CORE.failure_ledger import note_failure
except ImportError:  # never break the host
    def note_failure(where, exc=None):
        pass


OUT_DEFAULT = Path.home() / "yggdrasil_forest" / "box_trees.json"
SCAN_ROOTS = ["C:/Azazael", "C:/Users/clint", str(Path.home())]
MAX_DEPTH = 3
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
        ".pytest_cache", "dist", "build", "target", ".cargo", ".rustup"}


def _run(cmd, cwd=None, timeout=10):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception as exc:
        note_failure("tools/box_trees._run", exc)
        return None


def git_info(path: Path) -> dict:
    info = {"kind": "dir", "branch": None, "head": None, "dirty": None}
    if not (path / ".git").exists():
        return info
    info["kind"] = "git"
    b = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(path))
    h = _run(["git", "rev-parse", "--short", "HEAD"], cwd=str(path))
    st = _run(["git", "status", "--porcelain=v1"], cwd=str(path))
    info["branch"] = b
    info["head"] = h
    info["dirty"] = len(st.splitlines()) if st is not None else None
    return info


def scan_root(root: Path, depth=MAX_DEPTH) -> list[dict]:
    rows = []
    if not root.exists():
        return rows
    # root itself
    g = git_info(root)
    rows.append({"path": str(root), **g})
    stack = [(root, 0)]
    seen = {root.resolve()} if root.exists() else set()
    while stack:
        cur, d = stack.pop()
        if d >= depth:
            continue
        try:
            with os.scandir(cur) as it:
                entries = list(it)
        except OSError as exc:
            note_failure("tools/box_trees.scan_root.scandir", exc)
            continue
        for e in entries:
            if not e.is_dir(follow_symlinks=False):
                continue
            if e.name in SKIP or e.name.startswith(".") and e.name not in (".agents",):
                # still allow .agents but skip other dot-dirs except .git check below
                if e.name != ".git":
                    pass
            p = Path(e.path)
            try:
                rp = p.resolve()
            except OSError as exc:
                note_failure("tools/box_trees.scan_root.resolve", exc)
                continue
            if rp in seen:
                continue
            seen.add(rp)
            if (p / ".git").exists() or (p / ".git").is_file():
                rows.append({"path": str(p), **git_info(p)})
                # do not descend into git repos beyond one level (avoid node_modules etc.)
                continue
            if d + 1 < depth:
                # record top-level dirs only (depth 1) as plain dirs
                if d == 0:
                    rows.append({"path": str(p), "kind": "dir",
                                 "branch": None, "head": None, "dirty": None})
                stack.append((p, d + 1))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", default=None)
    ap.add_argument("--roots", default=None, help="comma-separated roots to scan")
    ap.add_argument("--install-startup", action="store_true",
                    help="install logon VBS in Windows Startup folder")
    args = ap.parse_args(argv)

    if args.install_startup:
        return install_startup()

    roots = [Path(r) for r in (args.roots.split(",") if args.roots else SCAN_ROOTS)]
    # always include this repo root
    repo = Path(__file__).resolve().parent.parent.parent
    if repo not in roots:
        roots.append(repo)
    rows = []
    for r in roots:
        rows.extend(scan_root(r))
    # de-dupe by path
    uniq = {}
    for row in rows:
        uniq[row["path"]] = row
    rows = sorted(uniq.values(), key=lambda r: r["path"].lower())
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(),
               "roots": [str(r) for r in roots],
               "count": len(rows), "trees": rows}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{'PATH':60} {'KIND':5} {'BRANCH':20} {'HEAD':8} DIRTY")
        for t in rows:
            print(f"{t['path'][:60]:60} {t['kind']:5} "
                  f"{str(t['branch'] or '-')[:20]:20} "
                  f"{t['head'] or '-':8} {t['dirty'] if t['dirty'] is not None else '-'}")
        print(f"\n{len(rows)} trees from {len(roots)} roots")
    out = Path(args.write) if args.write else OUT_DEFAULT
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if not args.json:
            print(f"wrote {out}")
    except OSError as exc:
        print(f"write failed: {exc}", file=sys.stderr)
        return 1
    return 0


def install_startup() -> int:
    """Mirror pmb-floor-proxy.vbs: run box_trees scan at logon."""
    startup = Path(os.environ.get("APPDATA", "")) / \
        "Microsoft/Windows/Start Menu/Programs/Startup"
    if not startup.exists():
        print(f"Startup folder not found: {startup}", file=sys.stderr)
        return 2
    py = sys.executable.replace("python.exe", "pythonw.exe")
    tool = Path(__file__).resolve()
    vbs = startup / "box-trees-scan.vbs"
    vbs.write_text(
        "' box_trees logon scan -- runs at logon, exits fast.\n"
        "' Disable by renaming with a .disabled suffix.\n"
        "Set sh = CreateObject(\"WScript.Shell\")\n"
        "sh.Environment(\"PROCESS\")(\"BOX_TREES_ORIGIN\") = \"logon\"\n"
        f"sh.Run \"\"\"{py}\"\" \"\"{tool}\"\"\", 0, False\n",
        encoding="utf-8")
    print(f"installed {vbs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
