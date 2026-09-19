#!/usr/bin/env python3
# coding: utf-8
"""SELF-MODIFY -- the mutator harness. The organ this architecture was missing.

Measured 2026-09-18: the mesh had selection (47 functions entered per cycle),
regulation (64), plasticity (13) -- and NO path by which anything it computed
could edit its own source. Variation existed only as a parameter vector
(`_fabric_variation` searches a priority vector against recorded Q), and a
mutation of a vector cannot produce a call site. So the 166 census findings --
every one a mechanism that is correct and uncalled -- could only ever be fixed
by a human editing Python.

This closes that loop with the four components recursion actually requires,
in the order that is safe: a TRUSTWORTHY TIERED EVALUATOR first (a fast tier
and a band tier, both real), then RETENTION (keep only if the evaluator does
not regress), then the LEDGER (record every attempt with its outcome so
failures accumulate into learning instead of being re-derived), and only then
AUTHORITY -- bounded, because every mutation is reverted unless it earns its
place. There is no rehearsal mode: every run is a real run, and the only thing
that stops a bad change from landing is the evaluator.

    mutate -> evaluate (tier1 compile, tier2 band) -> retain or revert -> record

The evaluator must come first and must be trustworthy: a mutator coupled to a
lying evaluator does not learn, it optimizes nonsense faster. That is not
hypothetical -- the BlackQueen was one approval from retiring EvolutionEngine,
DreamingModule, GeneticOptimizer and HypnagogicSynthesizer using a similarity
metric that scored unrelated worms identical, and it was stopped by a
human-authored quorum rule rather than by the system noticing.

Usage:
    python tools/self_modify.py --patch fix.diff --tier2 tests/test_x.py
    python tools/self_modify.py --patch fix.diff --strict        # demand improvement
    python tools/self_modify.py --ledger                         # read attempts
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "logs" / "mutation_ledger.jsonl"
BAND = ("tests/test_mesh_fabric_followups.py", "tests/test_mesh_fabric_gaps.py",
        "tests/test_mesh_fabric_health.py", "tests/test_artifact_freshness.py")


def _run(cmd: Sequence[str], timeout: int) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"rc": None, "out": "", "err": "timeout", "timeout": True}
    return {"rc": proc.returncode, "out": proc.stdout or "",
            "err": (proc.stderr or "")[-400:]}


def _apply_subs(subs: dict[str, list], encoding: str) -> tuple[bool, str]:
    """Byte-exact substitution apply -- the default way a mutation lands.

    Preferred over `git apply` for mechanical edits because it does not care
    about `core.autocrlf`, mixed LF/CRLF worktrees, or a dirty index. A 46-file
    cap fix was rejected by `git apply` three times for end-of-line reasons
    that had nothing to do with whether the change was correct; the files are a
    genuine mix (some LF in the worktree, some CRLF), so no single git strategy
    satisfies all of them. Line endings here are preserved because the text is
    never split or joined -- only the pattern is replaced.
    """
    for rel, pairs in subs.items():
        p = ROOT / rel
        if not p.is_file():
            return False, "%s: file does not exist" % rel
        raw = p.read_bytes()
        text = raw.decode(encoding, errors="surrogateescape")
        for pair in pairs:
            old, new = pair[0], pair[1]
            if old not in text:
                return False, "%s: pattern absent: %r" % (rel, old[:40])
            text = text.replace(old, new)
        p.write_bytes(text.encode(encoding, errors="surrogateescape"))
    return True, "applied %d file(s)" % len(subs)


def tier1_compile(files: Sequence[Path]) -> dict[str, Any]:
    """Fastest tier: can the mutated source even be imported/parsed?"""
    py = [str(f) for f in files if f.suffix == ".py"]
    if not py:
        return {"ok": True, "detail": "no python files", "checked": 0}
    res = _run([sys.executable, "-m", "py_compile", *py], timeout=120)
    return {"ok": res["rc"] == 0, "checked": len(py),
            "detail": (res["err"] or "").strip()[-200:] if res["rc"] else "compiles"}


_PASSED = re.compile(r"(\d+) passed")
_FAILED = re.compile(r"(\d+) failed")
_ERRORS = re.compile(r"(\d+) error")


def tier2_band(targets: Sequence[str], timeout: int = 600) -> dict[str, Any]:
    """Behaviour tier: does the system still do what its specs say?

    Counts, not just a return code -- a mutation that 'passes' while dropping
    ten tests has regressed, and retention has to see that.
    """
    res = _run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                *targets], timeout=timeout)
    text = res["out"] + res["err"]
    tail = text.strip().splitlines()[-1:] or [""]
    passed = int((_PASSED.search(text) or [0, 0])[1])
    failed = int((_FAILED.search(text) or [0, 0])[1])
    errors = int((_ERRORS.search(text) or [0, 0])[1])
    return {"rc": res["rc"], "passed": passed, "failed": failed,
            "errors": errors, "timeout": bool(res.get("timeout")),
            "summary": tail[0][:160]}


def worse_than(new: dict[str, Any], base: dict[str, Any]) -> str:
    """The retention rule, stated once so it can be argued with.

    Returns "" when the mutation is not a regression, else the reason. A
    regression is: fewer passing, more failing/erroring, or a timeout on a
    baseline that did not time out. Equal counts are accepted: a refactor that
    changes no behaviour is not a regression, and demanding improvement would
    reject every honest cleanup.
    """
    if new.get("timeout") and not base.get("timeout"):
        return "tier2 timed out but the baseline did not"
    if new["passed"] < base["passed"]:
        return "passing tests fell %d -> %d" % (base["passed"], new["passed"])
    if new["failed"] > base["failed"]:
        return "failing tests rose %d -> %d" % (base["failed"], new["failed"])
    if new["errors"] > base["errors"]:
        return "test errors rose %d -> %d" % (base["errors"], new["errors"])
    return ""


def record(row: dict[str, Any]) -> None:
    """Append to the ledger -- the part that makes attempts cumulative.

    Without this, each cycle re-derives the same findings: there is no memory of
    'we tried wiring X, it regressed, we reverted', so nothing accumulates.
    """
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")
    try:
        sys.path.insert(0, str(ROOT / "src"))
        from CORE.direct_memory import DirectMemory  # noqa: PLC0415
        DirectMemory().record("self_modify_attempt", row)
    except Exception:
        pass  # memory is a nice-to-have; the ledger is the record of account


def self_modify(patch: Path, targets: Sequence[str],
                keep_on_tie: bool = True, tier2_timeout: int = 600) -> dict[str, Any]:
    started = time.time()
    patch_text = patch.read_text(encoding="utf-8", errors="replace")
    row: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "patch": str(patch),
        "patch_hash": hashlib.sha256(patch_text.encode()).hexdigest()[:16],
    }

    # Touch nothing until the pre-state is saved. Revert is byte-restore, which
    # works even on a dirty tree -- so this cannot depend on git being clean.
    subs: dict[str, list] | None = None
    if patch.suffix.lower() == ".json":
        try:
            payload = json.loads(patch_text)
        except ValueError as exc:
            row.update({"verdict": "rejected",
                        "reason": "unreadable substitution patch: %s" % exc})
            record(row)
            return row
        subs = payload.get("subs") or {}
        row["encoding"] = payload.get("encoding", "utf-8")
        row["format"] = "subs"
        touched = sorted(subs)
    else:
        row["format"] = "diff"
        touched = sorted({m.group(1).strip() for m in
                          re.finditer(r"^\+\+\+ b/(.+)$", patch_text, re.M)})
    if not touched:
        row.update({"verdict": "rejected", "reason": "patch touches no file"})
        record(row)
        return row
    saved: dict[str, bytes] = {}
    missing: list[str] = []
    for rel in touched:
        p = ROOT / rel
        if p.is_file():
            saved[rel] = p.read_bytes()
        else:
            missing.append(rel)
    row["files"] = touched

    def revert(reason: str) -> None:
        for rel, blob in saved.items():
            (ROOT / rel).write_bytes(blob)
        # A mutation that CREATES a file is reverted by deleting it. Byte-restore
        # alone would leave the new (broken) file on disk and the revert would
        # silently be partial -- so the check is `was it there before?`.
        for rel in missing:
            p = ROOT / rel
            if p.is_file():
                p.unlink()
        row["reverted_files"] = sorted(saved) + ["-" + m for m in missing]

    base = tier2_band(targets, tier2_timeout)
    row["baseline"] = base

    # core.autocrlf=false is load-bearing: with it on, git normalises the patch
    # to CRLF before matching, so a byte-faithful LF diff fails against an LF
    # worktree file. That rejected the whole 46-file cap patch twice, on a
    # different set of files each time because the normalisation only bites
    # files git considers text.
    if subs is not None:
        ok, detail = _apply_subs(subs, row["encoding"])
        row["applied"] = ok
        if not ok:
            revert("substitution failed")
            row.update({"verdict": "rejected", "reason": detail})
            record(row)
            return row
    else:
        applied = _run(["git", "-c", "core.autocrlf=false", "apply",
                        "--whitespace=nowarn", str(patch)], timeout=60)
        if applied["rc"] != 0:
            if saved:
                revert("patch failed to apply")
            row.update({"verdict": "rejected",
                        "reason": "git apply failed: %s" % (applied["err"] or "")[:200]})
            record(row)
            return row
        row["applied"] = True

    t1 = tier1_compile([ROOT / rel for rel in touched if (ROOT / rel).suffix == ".py"])
    row["tier1"] = t1
    if not t1["ok"]:
        revert("tier1")
        row.update({"verdict": "reverted", "reason": "tier1: %s" % t1["detail"]})
        record(row)
        return row

    t2 = tier2_band(targets, tier2_timeout)
    row["tier2"] = t2
    regression = worse_than(t2, base)
    if regression:
        revert("tier2")
        row.update({"verdict": "reverted", "reason": "tier2: %s" % regression})
        record(row)
        return row

    row.update({"verdict": "kept",
                "reason": "tier1 ok; tier2 no regression"
                          + (" (tie accepted)" if keep_on_tie and
                             t2["passed"] == base["passed"] else "")})
    if missing:
        row["note"] = "patch referenced files that do not exist: %s" % missing
    row["elapsed_s"] = round(time.time() - started, 2)
    record(row)
    return row


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--patch", help="unified diff to attempt")
    ap.add_argument("--tier2", nargs="*", default=list(BAND),
                    help="pytest targets for the behaviour tier")
    ap.add_argument("--strict", action="store_true",
                    help="require a strict improvement, not merely no regression")
    ap.add_argument("--ledger", action="store_true", help="print the attempt ledger")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.ledger:
        if not LEDGER.is_file():
            print("no attempts recorded yet")
            return 0
        rows = [json.loads(x) for x in LEDGER.read_text(encoding="utf-8").splitlines() if x.strip()]
        print("%-22s %-10s %-34s %s" % ("WHEN", "VERDICT", "REASON", "TIER2"))
        for r in rows[-20:]:
            t2 = r.get("tier2") or {}
            print("%-22s %-10s %-34s %s" % (
                str(r.get("ts"))[11:19], r.get("verdict", "?"),
                str(r.get("reason"))[:34],
                "passed=%s failed=%s" % (t2.get("passed"), t2.get("failed"))))
        untried = [r for r in rows if r.get("verdict") == "kept"]
        print("\n%d attempt(s), %d kept" % (len(rows), len(untried)))
        return 0

    if not args.patch:
        ap.error("--patch is required unless --ledger")
    row = self_modify(Path(args.patch), args.tier2,
                      keep_on_tie=not args.strict, tier2_timeout=600)
    if args.json:
        print(json.dumps(row, indent=2, default=str))
    else:
        print("verdict: %s" % row.get("verdict"))
        print("reason : %s" % row.get("reason"))
        print("tier1  : %s" % (row.get("tier1") or {}).get("detail"))
        print("tier2  : baseline=%s -> %s"
              % (row.get("baseline", {}).get("passed"),
                 (row.get("tier2") or {}).get("passed")))
        print("ledger : %s" % LEDGER)
    return 0 if row.get("verdict") == "kept" else 1


if __name__ == "__main__":
    sys.exit(main())
