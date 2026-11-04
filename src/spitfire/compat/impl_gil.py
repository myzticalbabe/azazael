#!/usr/bin/env python3
# coding: utf-8
"""GIL implementation for legacy Windows (7, 8.1).

Runs under Python 3.8/3.12 with the GIL. Uses ThreadPoolExecutor
with processes=False for compatibility.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]


def sh(*args: str) -> tuple[int, str, str]:
    try:
        out = subprocess.run(
            args,
            capture_output=True,
            cwd=str(REPO),
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
    except subprocess.TimeoutExpired as exc:
        return (124, "", f"timeout after 600s: {type(exc).__name__}")
    return (out.returncode, out.stdout or "", out.stderr or "")


def dirty_paths() -> list[tuple[str, str]]:
    code, out, _ = sh("git", "status", "--porcelain", "-z")
    if code != 0:
        raise SystemExit(f"git status failed: exit {code}")
    rows: list[tuple[str, str]] = []
    for entry in out.split("\0"):
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        st = status.strip()
        if path.startswith("-> "):
            continue
        if st == "??":
            kind = "untracked"
        elif "D" in st:
            kind = "deleted"
        else:
            kind = "modified"
        rows.append((path, kind))
    return rows


def classify(path: str, status: str) -> dict:
    import os as _os
    import time as _time

    low = path.lower()
    name = _os.path.basename(low)
    stat = _os.stat(_os.path.join(REPO, path)) if status != "deleted" else _os.stat(REPO)

    if name.endswith((".pyc", ".pyo", ".pyd", ".DS_Store", ".tmp", ".bak")):
        cat = "build-artifact"
    elif name.endswith((".jsonl", ".log")) or low.startswith(
        ("state/", "out/", "logs/", "tmp/")
    ):
        cat = "data-or-log"
    elif status == "untracked" and "/archived/" in low:
        cat = "archived-tree"
    elif name.endswith((".py", ".rs", ".go", ".ts", ".md", ".toml", ".yaml", ".yml")):
        cat = "source-or-doc"
    elif name.endswith(".json"):
        cat = (
            "data-or-log"
            if ("state/" in low or "out/" in low or "/logs/" in low)
            else "source-or-doc"
        )
    else:
        cat = "unknown"

    added = removed = -1
    if status == "modified":
        code, out, _ = sh("git", "diff", "--numstat", "HEAD", "--", path)
        first = out.splitlines()[0] if out.strip() else ""
        parts = first.split("\t")
        if len(parts) >= 2 and parts[0].isdigit():
            added, removed = int(parts[0]), int(parts[1])

    return {
        "path": path,
        "status": status,
        "bytes": stat.st_size,
        "mtime": _time.strftime("%Y-%m-%d %H:%M", _time.localtime(stat.st_mtime)),
        "added": added,
        "removed": removed,
        "category": cat,
    }


def census(args: argparse.Namespace) -> int:
    rows = dirty_paths()
    t0 = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        verdicts = list(
            ex.map(lambda v: classify(v[0], v[1]), rows)
        )

    dt = time.perf_counter() - t0
    cats: dict[str, int] = {}
    for v in verdicts:
        cats[v["category"]] = cats.get(v["category"], 0) + 1

    save_path = args.save or REPO / "state" / "spitfire_census.jsonl"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8", newline="\n") as f:
        for v in verdicts:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **v}) + "\n")

    print(
        f"spitfire census: {len(verdicts)} paths, {args.max_workers} workers (GIL), "
        f"{dt:.2f}s -> {save_path}"
    )
    for c in sorted(cats, key=cats.get, reverse=True):
        print(f"  {cats[c]:4d}  {c}")
    return 0


def fix(args: argparse.Namespace) -> int:
    print("[spitfire fix] GIL implementation - stub", file=sys.stderr)
    return 0


def run(args: argparse.Namespace, target) -> int:
    if args.cmd == "census":
        return census(args)
    if args.cmd == "fix":
        return fix(args)
    if args.cmd == "all":
        rc = census(args)
        if rc != 0:
            return rc
        return fix(args)
    return 2