#!/usr/bin/env python3
"""generated_audit.py -- G2: an excused path must be provably generator-owned.

`scripts/commit_gate.py` exempts five paths from the bulk caps because a machine
writes them. That exemption is a claim about ownership, and until now nothing
proved it: the table said "generated", and every later session believed it. A
path that is excused but no longer reproduced by its generator is a hole in the
gate in the one direction that matters -- hand edits to a machine-shaped file
pass as machine bytes.

So this reads the exemption table from its single owner (an import, never a copy)
and asks each entry for proof:

  check-bytes      the generator has `--check` and returns 0 against the disk
  render-compare   no `--check`, so render to a temp file and compare bytes
  no-verifier      the file records a MEASUREMENT, not a rendering; registered
                   as such, with its reason, and counted separately

Verdicts, all distinct because the repairs differ:

  PROVED            proof obtained, bytes identical
  DRIFTED           proof obtained, bytes differ (the file is stale or hand-edited)
  NO-VERIFIER       registered exemption: this file cannot be byte-checked
  GENERATOR-MISSING the named generator is not on disk
  ERROR             the verifier ran and could not answer

Exit: 0 when the audit ran (advisory -- HED-2's debt model), 1 only under
--strict when a path is DRIFTED, GENERATOR-MISSING or ERROR, 2 when the
exemption table itself could not be read. A run that could not perform the
audit is never a pass.

Usage:
    python tools/generated_audit.py
    python tools/generated_audit.py --strict
    python tools/generated_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# How each excused path is proved. The generator column is deliberately NOT
# repeated here: it is read from GENERATED_PATHS so the two cannot disagree.
# Only the METHOD lives here, because the method is knowledge about the tool.
VERIFIERS: dict[str, dict[str, object]] = {
    "docs/INDEX.md": {
        "kind": "render-compare",
        "args": ["--out", "{tmp}"],
        "why": "docs_index.py has no --check; it renders the whole index to --out",
    },
    "Project_ELIZA/shards/SHARD_INDEX.json": {
        "kind": "check-bytes",
        "args": ["--check"],
        "why": "shard_intake.py rewrites the index top to bottom and can compare",
    },
    "ARC/esquire/pins.json": {
        "kind": "check-bytes",
        "args": ["--check"],
        "why": "arc_ledger.py renders the registry and reproduces HEAD's blob",
    },
    "logs/basedpyright_report.json": {
        "kind": "no-verifier",
        "args": [],
        "why": "records the output of one type-check RUN; there is no render to "
               "compare it against, so it is exempt as a measurement artifact",
    },
    "logs/basedpyright_baseline.json": {
        "kind": "no-verifier",
        "args": [],
        "why": "rewritten only by `type_check_gate.py --baseline`, i.e. a paid-down "
               "debt list; byte-comparison would only restate the run",
    },
}

FAILING = {"DRIFTED", "GENERATOR-MISSING", "ERROR"}


def _exemptions() -> dict[str, str]:
    """The exemption table from its owner, not a copy (HED-5)."""
    scripts = ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from commit_gate import GENERATED_PATHS  # noqa: PLC0415

    return dict(GENERATED_PATHS)


def _run_full(cmd: list[str]) -> tuple[int, str, str]:
    """Run a generator; return (returncode, last stdout line, all stdout)."""
    try:
        proc = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 99, "could not run: %s" % type(exc).__name__, ""
    stdout = proc.stdout or ""
    tail = [ln for ln in stdout.splitlines() if ln.strip()]
    return proc.returncode, (tail[-1] if tail else ""), stdout


def _run(cmd: list[str]) -> tuple[int, str]:
    """Back-compatible pair form of _run_full."""
    rc, tail, _stdout = _run_full(cmd)
    return rc, tail


def _render_compare(gen: Path, args: list[str], target: Path) -> tuple[str, str]:
    """Render to a temp path and compare bytes with what is on disk."""
    if not target.is_file():
        return "ERROR", "target not on disk"
    tmpdir = tempfile.mkdtemp(prefix="generated-audit-")
    out = Path(tmpdir) / target.name
    cmd = [sys.executable, str(gen)]
    for a in args:
        cmd.append(a.replace("{tmp}", str(out)))
    rc, tail = _run(cmd)
    if rc != 0:
        return "ERROR", "generator rc=%d %s" % (rc, tail[:80])
    if not out.is_file():
        return "ERROR", "generator wrote no output"
    disk = target.read_bytes()
    rendered = out.read_bytes()
    if disk == rendered:
        return "PROVED", "disk %d bytes identical to render" % len(disk)
    return "DRIFTED", "disk %d bytes, render %d bytes, identical=False" % (
        len(disk), len(rendered))


# A line that actually asserts agreement. Quoting the generator's LAST stdout
# line instead (while it prints prose) dresses unrelated text as proof -- the
# same class of defect as a pass verdict with no denominator.
PROOF_LINE = re.compile(
    r"(?i)(identical|canonical|up[ -]to[ -]date|matches|in sync|\bOK\b)")


def _proof_line(stdout: str, rc: int) -> str:
    """The strongest agreement line the generator printed, else the exit fact."""
    for line in stdout.splitlines():
        if line.strip() and PROOF_LINE.search(line):
            return line.strip()[:120]
    return "generator --check rc=%d (no agreement line printed)" % rc


def _check_bytes(gen: Path, args: list[str], target: Path) -> tuple[str, str]:
    cmd = [sys.executable, str(gen)] + list(args)
    rc, _tail, stdout = _run_full(cmd)
    if rc == 0:
        return "PROVED", _proof_line(stdout, rc)
    if rc == 1:
        return "DRIFTED", _proof_line(stdout, rc)
    return "ERROR", "generator --check rc=%d" % rc


def audit() -> tuple[list[dict[str, str]], dict[str, int]]:
    """One row per excused path plus a per-verdict count."""
    try:
        table = _exemptions()
    except Exception as exc:  # noqa: BLE001 -- reported, never swallowed
        print("generated_audit: cannot read GENERATED_PATHS: %s: %s"
              % (type(exc).__name__, exc))
        print("generated_audit: nothing audited, which is not a pass")
        raise SystemExit(2)

    rows: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    for rel, generator in sorted(table.items()):
        rule = VERIFIERS.get(rel)
        target = ROOT / rel
        gen = ROOT / generator
        if rule is None:
            verdict, detail = "ERROR", "no verifier registered for this excused path"
        elif rule["kind"] == "no-verifier":
            verdict, detail = "NO-VERIFIER", str(rule.get("why", ""))
        elif not gen.is_file():
            verdict, detail = "GENERATOR-MISSING", "no %s on disk" % generator
        elif rule["kind"] == "render-compare":
            verdict, detail = _render_compare(
                gen, list(rule["args"]), target)  # type: ignore[arg-type]
        else:
            verdict, detail = _check_bytes(
                gen, list(rule["args"]), target)  # type: ignore[arg-type]
        rows.append({"path": rel, "generator": generator,
                     "kind": str(rule["kind"]) if rule else "none",
                     "verdict": verdict, "detail": detail})
        counts[verdict] = counts.get(verdict, 0) + 1
    return rows, counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when any excused path is drifted or unprovable")
    ap.add_argument("--json", action="store_true", help="machine-readable rows")
    args = ap.parse_args(argv)

    rows, counts = audit()
    if args.json:
        print(json.dumps({"rows": rows, "counts": counts,
                          "excused": len(rows)}, indent=2))
    else:
        for r in rows:
            print("%-14s %-46s %s" % (r["verdict"], r["path"], r["detail"]))
        print("generated_audit: %d/%d excused paths accounted for (%s)"
              % (len(rows), len(rows),
                 ", ".join("%s=%d" % kv for kv in sorted(counts.items()))))

    failing = sum(counts.get(k, 0) for k in FAILING)
    if args.strict and failing:
        print("generated_audit: STRICT FAIL -- %d path(s) not provably owned"
              % failing)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
