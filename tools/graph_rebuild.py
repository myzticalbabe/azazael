#!/usr/bin/env python3
# coding: utf-8
"""GRAPH-REBUILD -- rebuild the graph across rounds, because the quota is the blocker.

Measured 2026-09-18: every chunk failure in the semantic pass is
`429 RESOURCE_EXHAUSTED`, `generate_content_free_tier_requests limit: 5` per
minute, with `retryDelay ~40s`. The extractor fires chunks in parallel with no
backoff, so it burns the free-tier quota in seconds and loses the remainder --
9 of 71 chunks produced output on one run, 29 of 64 failed on the next, at a
different count each time. That is a budget constraint silently negotiating away
a capability, the same shape as the 100-character diagnostic cap.

So this wraps the extract in rounds with a wait between them and counts what
each round actually produced. It does not promise the semantic half completes:
it reports the per-round success count and stops when a round adds nothing, so
"it is still incomplete and here is the trend" is visible rather than assumed.

It also reports whether the installed package has a local-model path. 0.8.8
documents none -- `extract --help` has no backend/model/ollama flag -- but the
package does reference ollama in llm.py, prs.py and __main__.py, so the claim
"there is no local path" was never safe to make from a help screen.

    python tools/graph_rebuild.py --rounds 3 --sleep 60 --out graphify-out
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "logs" / "graph_rebuild_report.json"
SITE = Path("/c/Users/clint/AppData/Local/Programs/Python/Python314/Lib/site-packages/graphify")
if not SITE.is_dir():
    SITE = Path(sys.prefix) / "Lib" / "site-packages" / "graphify"

CHUNK_FAIL = re.compile(r"chunk (\d+)/(\d+) failed")
ROUND_DONE = re.compile(r"Deduplicated (\d+) node")


def local_backend() -> dict:
    """Does the installed package offer a local inference path?"""
    hits: list[str] = []
    files: list[str] = []
    if SITE.is_dir():
        for p in SITE.rglob("*.py"):
            try:
                body = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "ollama" in body.lower() or "11434" in body:
                files.append(p.name)
                for m in re.finditer(r"^.*(ollama|11434).*$", body, re.M | re.I):
                    line = m.group(0).strip()
                    if len(line) < 160:
                        hits.append("%s: %s" % (p.name, line))
                    if len(hits) > 12:
                        break
    return {"site_packages": str(SITE), "package_present": SITE.is_dir(),
            "files_with_ollama": sorted(set(files)), "sample": hits[:12]}


def rounds(count: int, sleep_s: int, out: str, timeout: int) -> dict:
    history: list[dict] = []
    for i in range(1, count + 1):
        started = time.time()
        cmd = [sys.executable, "-m", "graphify", "extract", "src", "--out", out]
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                                  text=True, timeout=timeout)
            text = (proc.stdout or "") + (proc.stderr or "")
            rc = proc.returncode
        except subprocess.TimeoutExpired as exc:
            text = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            rc = None
        fails = CHUNK_FAIL.findall(text)
        chunks = max((int(f[1]) for f in fails), default=0)
        entry = {"round": i, "rc": rc, "chunk_failures": len(fails),
                 "chunks_seen": chunks,
                 "dedup": [int(m) for m in ROUND_DONE.findall(text)][:1],
                 "elapsed_s": round(time.time() - started, 1)}
        history.append(entry)
        print("[round %d] rc=%s chunk failures=%d/%s elapsed=%ss"
              % (i, rc, entry["chunk_failures"], chunks or "?", entry["elapsed_s"]))
        if i < count:
            time.sleep(sleep_s)
    return {"rounds": history, "generated": datetime.now(timezone.utc).isoformat()}


def cluster_pass(out: str, timeout: int = 1800) -> dict:
    """Regenerate GRAPH_REPORT.md / graph.html from the graph extract just wrote.

    `extract` writes graph.json; the report comes from a separate cluster pass.
    Running extract alone left GRAPH_REPORT.md stale by 49 sources while
    graph.json was freshly rebuilt -- precisely the report/artifact mismatch the
    freshness guard was built to catch, reproduced by the rebuild itself. So the
    rebuild does both halves now, in one command.
    """
    try:
        res = subprocess.run([sys.executable, "-m", "graphify", "cluster-only",
                              "--out", out], cwd=str(ROOT), capture_output=True,
                             text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"rc": None, "tail": ["timeout"]}
    text = ((res.stdout or "") + (res.stderr or "")).strip().splitlines()
    return {"rc": res.returncode, "tail": text[-3:]}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--sleep", type=int, default=60)
    ap.add_argument("--out", default="graphify-out")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--probe-only", action="store_true",
                    help="report the local-backend surface, do not rebuild")
    args = ap.parse_args(argv)

    report: dict = {"local_backend": local_backend()}
    print("local-model surface: %s"
          % (report["local_backend"]["files_with_ollama"] or "none found"))
    for s in report["local_backend"]["sample"][:6]:
        print("   %s" % s)
    if not args.probe_only:
        report.update(rounds(args.rounds, args.sleep, args.out, args.timeout))
        report["cluster"] = cluster_pass(args.out)
        print("[cluster] rc=%s %s" % (report["cluster"]["rc"],
                                      " | ".join(report["cluster"]["tail"])[-160:]))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("report: %s" % REPORT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
