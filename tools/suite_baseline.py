"""Chunked, resumable full-suite baseline (T-15 companion).

Why this exists: a single `pytest tests/` invocation of this tree exceeds the
600 s command ceiling, so no green baseline could ever be established — the
suite was "4068 tests collect, unverified". This runs the same files in bounded
batches and journals each batch, so a run that dies mid-way RESUMES instead of
restarting, and the per-batch record survives for the audit trail.

It does NOT weaken the suite: no deselects, no `--ignore`, no retries, no
`-x`. Every collected test runs, and the exit status of each batch is recorded
verbatim. A batch that fails stays failed in the journal.

Usage:
    python tools/suite_baseline.py            # resume / run all batches
    python tools/suite_baseline.py --report   # print the journal summary only
    python tools/suite_baseline.py --batch-size 25
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TESTS = REPO / "tests"
JOURNAL = REPO / "state" / "suite_baseline.jsonl"
PY = sys.executable


def test_files() -> list[str]:
    """Every collected test file, sorted for a stable chunk assignment."""
    return sorted(str(p.relative_to(REPO)).replace("\\", "/")
                  for p in TESTS.rglob("test_*.py"))


def chunks(files: list[str], size: int) -> list[list[str]]:
    return [files[i:i + size] for i in range(0, len(files), size)]


def done_batches() -> set[int]:
    """Batch indices already journaled OK -- the resume set."""
    if not JOURNAL.exists():
        return set()
    out: set[int] = set()
    for line in JOURNAL.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("returncode") == 0:
            out.add(int(rec.get("batch", -1)))
    return out


def run_batch(idx: int, batch: list[str], timeout: int = 900) -> dict:
    """Run one batch. A hung batch is recorded as rc=124, never left hanging.

    Without the timeout a single hanging test would stall the whole baseline
    with no record, which is the failure mode this runner exists to remove.
    """
    t0 = time.time()
    timed_out = False
    try:
        proc = subprocess.run(
            [PY, "-m", "pytest", "-q", "--tb=line", "-rf", *batch],
            cwd=str(REPO), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout)
        rc, raw = proc.returncode, (proc.stdout or "")
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc = 124
        raw = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        raw += f"\n[BATCH TIMEOUT after {timeout}s -- rc=124 recorded]"
    tail = raw.splitlines()[-25:]
    rec = {"batch": idx, "n_files": len(batch), "returncode": rc,
           "timed_out": timed_out, "timeout_s": timeout,
           "seconds": round(time.time() - t0, 1), "tail": tail,
           "files": batch}
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def summarise() -> int:
    if not JOURNAL.exists():
        print("no journal yet")
        return 1
    recs = [json.loads(x) for x in
            JOURNAL.read_text(encoding="utf-8", errors="replace").splitlines()
            if x.strip()]
    latest: dict[int, dict] = {}
    for r in recs:
        latest[int(r["batch"])] = r
    bad = [r for r in latest.values() if r.get("returncode") != 0]
    total_s = sum(float(r.get("seconds", 0)) for r in latest.values())
    print(f"batches journaled : {len(latest)}")
    print(f"batches ok        : {len(latest) - len(bad)}")
    print(f"batches FAILED    : {len(bad)}")
    print(f"wall seconds      : {total_s:.0f}")
    for r in sorted(bad, key=lambda x: int(x["batch"])):
        print(f"\n--- batch {r['batch']} rc={r['returncode']} "
              f"({r['n_files']} files) ---")
        for line in r.get("tail", []):
            print("   " + line)
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--timeout", type=int, default=900,
                    help="per-batch seconds; a exceeded batch is rc=124")
    args = ap.parse_args(argv)

    files = test_files()
    if not files:
        print("no test files found")
        return 2
    if args.report:
        return summarise()

    todo = chunks(files, args.batch_size)
    already = done_batches()
    print(f"{len(files)} test files -> {len(todo)} batches "
          f"(size {args.batch_size}); {len(already)} already ok")
    for idx, batch in enumerate(todo):
        if idx in already:
            continue
        rec = run_batch(idx, batch, timeout=args.timeout)
        mark = "OK  " if rec["returncode"] == 0 else (
            "TIME" if rec.get("timed_out") else "FAIL")
        print(f"[{mark}] batch {idx + 1}/{len(todo)} "
              f"{rec['n_files']} files in {rec['seconds']}s "
              f"rc={rec['returncode']}", flush=True)
    return summarise()


if __name__ == "__main__":
    raise SystemExit(main())
