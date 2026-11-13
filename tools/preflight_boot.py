#!/usr/bin/env python3
"""preflight_boot — the state a session needs BEFORE it trusts anything else.

WHY THIS EXISTS
---------------
The 2026-11-12 reboot pre-flight was assembled by hand: disk measured with `df`
(via four drive letters, because plain `du` timed out twice), WSL measured with
`wsl --list --verbose` plus `ls -la` on each vhdx, the stack probed by POSTing an
MCP `initialize` to :8765 and :8766, the repo read with three git commands, and
the board read one lane at a time. Every number in that sweep was correct and
every one of them was gone the moment the session ended.

This tool is that sweep, once, bounded, and written to disk. It is read-only: it
starts nothing, kills nothing, and stages nothing. Its output is one line per
check plus one JSON artifact, so a next session can quote a measurement instead
of re-deriving it — and so "the disk was fine yesterday" stops being a claim
nobody can check.

    python tools/preflight_boot.py            # human lines
    python tools/preflight_boot.py --json     # machine artifact only
    python tools/preflight_boot.py --fast     # skip the supervisor verdict

Exit codes: 0 every check pass, 1 a FAIL, 2 a check could not be performed
(BLIND) — which is neither a pass nor a failure, and is never folded into one.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("USERPROFILE", r"C:\Users\clint"))
REPO = Path(r"C:\Azazael\azazael")
PY = r"C:\Azazael\.venvs\py316t\Scripts\python.exe"
ARTIFACT = HOME / "state" / "preflight_boot.json"

DISK_FLOOR_GB = 10.0
DRIVES = ["C:/", "D:/", "E:/", "G:/"]
MCP_ENDPOINTS = {"daemon": ("127.0.0.1", 8765), "floor-proxy": ("127.0.0.1", 8766)}
LANES = ("freebuff", "kilo", "opencode")


def _run(cmd: list[str], timeout: float, cwd: str | None = None) -> tuple[int, str]:
    """Run a bounded child; never raise. A timeout is a recorded state, not a crash."""
    try:
        done = subprocess.run(cmd, capture_output=True, timeout=timeout,
                              cwd=cwd, check=False)
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {timeout}s"
    except OSError as exc:
        return 127, f"OSError: {exc}"
    out = done.stdout if done.stdout else done.stderr
    return done.returncode, out.decode("utf-8", "replace").replace("\x00", "")


def check_disk() -> dict:
    rows, worst = [], "PASS"
    for drive in DRIVES:
        try:
            usage = shutil.disk_usage(drive)
        except OSError as exc:
            rows.append({"drive": drive, "state": "BLIND", "detail": str(exc)})
            worst = "BLIND" if worst == "PASS" else worst
            continue
        free_gb = usage.free / 1e9
        state = "PASS" if free_gb >= DISK_FLOOR_GB else "FAIL"
        if state == "FAIL":
            worst = "FAIL"
        rows.append({"drive": drive, "free_gb": round(free_gb, 1),
                     "used_pct": round(100 * usage.used / usage.total, 1), "state": state})
    return {"check": "disk", "state": worst, "rows": rows,
            "detail": ", ".join(f"{r['drive']} {r.get('free_gb', '?')}G" for r in rows)}


def check_wsl() -> dict:
    code, out = _run(["wsl.exe", "--list", "--verbose"], timeout=30)
    if code != 0:
        return {"check": "wsl", "state": "BLIND", "detail": out.strip()[:200]}
    distros = []
    for line in out.splitlines()[1:]:
        parts = line.replace("*", " ").split()
        if len(parts) >= 3:
            distros.append({"name": parts[0], "state": parts[1], "version": parts[2]})
    states = {d["state"] for d in distros}
    state = "FAIL" if "Installing" in states else "PASS"
    return {"check": "wsl", "state": state, "distros": distros,
            "detail": ", ".join(f"{d['name']}={d['state']}" for d in distros) or "none registered"}


def check_vhdx() -> dict:
    rows = []
    candidates = [Path(r"C:\wsl\Ubuntu-26.04\ext4.vhdx"), Path(r"E:\Kali\ext4.vhdx")]
    for path in candidates:
        if path.exists():
            rows.append({"path": str(path), "on_disk_gb": round(path.stat().st_size / 1e9, 1)})
    return {"check": "vhdx", "state": "PASS", "rows": rows,
            "detail": ", ".join(f"{Path(r['path']).parent.name} {r['on_disk_gb']}G" for r in rows)
            or "no managed vhdx found"}


def check_repo() -> dict:
    if not (REPO / ".git").exists():
        return {"check": "repo", "state": "BLIND", "detail": f"{REPO} is not a repo"}
    code, head = _run(["git", "-C", str(REPO), "log", "--oneline", "-1"], timeout=30)
    if code != 0:
        return {"check": "repo", "state": "BLIND", "detail": head.strip()[:200]}
    _c, branch = _run(["git", "-C", str(REPO), "rev-parse", "--abbrev-ref", "HEAD"], timeout=30)
    _c, ahead = _run(["git", "-C", str(REPO), "rev-list", "--count", "@{u}..HEAD"], timeout=30)
    _c, dirty = _run(["git", "-C", str(REPO), "status", "--porcelain"], timeout=60)
    dirty_count = len([ln for ln in dirty.splitlines() if ln.strip()])
    ahead_n = int(ahead.strip()) if ahead.strip().isdigit() else -1
    return {"check": "repo", "state": "PASS",
            "head": head.strip(), "branch": branch.strip(), "ahead": ahead_n,
            "dirty": dirty_count,
            "detail": f"{ahead_n} ahead, {dirty_count} dirty path(s)"}


def check_stack() -> dict:
    rows, worst = [], "PASS"
    for label, (host, port) in MCP_ENDPOINTS.items():
        try:
            with socket.create_connection((host, port), timeout=3):
                listening = True
        except OSError as exc:
            rows.append({"endpoint": label, "port": port, "listening": False, "detail": str(exc)})
            worst = "FAIL"
            continue
        payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                              "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                         "clientInfo": {"name": "preflight", "version": "1"}}}).encode()
        request = urllib.request.Request(
            f"http://{host}:{port}/mcp", data=payload,
            headers={"Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream",
                     "Accept-Encoding": "identity"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                rows.append({"endpoint": label, "port": port, "listening": True,
                             "http": response.status, "detail": "initialize answered"})
        except urllib.error.HTTPError as exc:
            # :8765 is designed to answer a bare HTTP client with 401 while still
            # being healthy for the MCP transport, so a status is a reading, not a failure.
            rows.append({"endpoint": label, "port": port, "listening": True,
                         "http": exc.code, "detail": f"HTTP {exc.code} (designed for :8765)"})
            if exc.code >= 500:
                worst = "FAIL"
        except (urllib.error.URLError, TimeoutError) as exc:
            rows.append({"endpoint": label, "port": port, "listening": True,
                         "http": None, "detail": f"listening but silent: {exc}"})
            worst = "FAIL"
    return {"check": "stack", "state": worst, "rows": rows,
            "detail": "; ".join(f"{r['endpoint']} :{r['port']} {r.get('http') or 'no-http'}" for r in rows)}


def check_board() -> dict:
    board = HOME / "_board.py"
    if not board.exists():
        return {"check": "board", "state": "BLIND", "detail": "no _board.py"}
    rows, worst = [], "PASS"
    for lane in LANES:
        code, out = _run([PY, str(board), "stats", lane], timeout=45)
        if code != 0 or "available" not in out:
            rows.append({"lane": lane, "state": "BLIND", "detail": out.strip()[:120]})
            worst = "BLIND" if worst == "PASS" else worst
            continue
        # _board.py prints a Python dict repr (single quotes), not JSON, so the
        # available count is read by pattern rather than by json.loads.
        match = re.search(r"'available':\s*(\d+)", out)
        available = int(match.group(1)) if match else None
        rows.append({"lane": lane, "available": available})
    return {"check": "board", "state": worst, "rows": rows,
            "detail": ", ".join(f"{r['lane']}={r.get('available', '?')}" for r in rows)}


def check_verdict() -> dict:
    supervisor = REPO / "tools" / "supervisor_mcp.py"
    if not supervisor.exists():
        return {"check": "verdict", "state": "BLIND", "detail": "no supervisor_mcp.py"}
    code, out = _run([PY, str(supervisor), "--verdict"], timeout=180)
    verdict = ""
    for line in out.splitlines():
        if "VERDICT" in line.upper():
            verdict = line.strip()
    state = "PASS" if "GO" in verdict.upper() and "NO-GO" not in verdict.upper() else "FAIL"
    if code == 124 or not verdict:
        state = "BLIND"
    return {"check": "verdict", "state": state, "verdict": verdict or "unavailable",
            "detail": verdict or out.strip()[-200:]}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Read-only pre-flight for disk, WSL, repo, stack, board.")
    parser.add_argument("--json", action="store_true", help="print only the JSON artifact")
    parser.add_argument("--fast", action="store_true", help="skip the supervisor verdict")
    args = parser.parse_args(argv)

    started = time.time()
    checks = [check_disk(), check_wsl(), check_vhdx(), check_repo(), check_stack(),
              check_board()]
    if not args.fast:
        checks.append(check_verdict())

    states = {c["state"] for c in checks}
    verdict = "FAIL" if "FAIL" in states else ("BLIND" if "BLIND" in states else "PASS")
    artifact = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict": verdict,
        "seconds": round(time.time() - started, 1),
        "checks": checks,
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(artifact, indent=2))
    else:
        for check in checks:
            print(f"{check['state']:<6}{check['check']:<9}{check.get('detail', '')}")
        print(f"\nverdict: {verdict}  ({artifact['seconds']}s)  -> {ARTIFACT}")
    return {"PASS": 0, "FAIL": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
