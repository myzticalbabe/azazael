#!/usr/bin/env python3
"""Unified land-and-push orchestration: one command from commits to synced.

Measured failure modes this tool exists to stop paying for (2026-11-23,
_azazael_fix lane, Windows Git Bash host):

1. Stale push base. The pre-push hook judges ``<known-remote-tip>..HEAD``
   but never fetches, so a tracking ref from hours ago inflates the judged
   range with commits that are already on the origin. This tool fetches
   first, then derives the base from the fresh tracking ref.
2. Mangled hook paths. With ``MSYS_NO_PATHCONV=1`` exported (the usual
   interactive setting on this box), hook children receive joined paths
   like ``C:\\\\c\\\\Users\\\\...`` and the disk-floor / evidence gates
   refuse on paths that do not exist. Without it, the same gates pass.
   This tool scrubs the variable from every git child environment and
   says so aloud, instead of inheriting whatever the caller exported.
3. Push-time surprises. The evidence tier takes ~200 s and judges the
   whole range; discovering a failure there wastes a push round-trip.
   This tool runs the same preflight (``preflight_all.py --check
   --base <tip>``) BEFORE pushing, so a red gate stops the run locally.
4. Undeclared escapes. ``ALLOW_SHARD_INTAKE`` (Kali census unavailable on
   a Windows host) and ``ALLOW_BULK_COMMIT`` (landed history whose bulk
   commits predate their declarations and cannot be re-messaged without
   a forbidden history rewrite) are only ever passed with an explicit
   ``--allow-*`` flag plus ``--justify`` text, and both are printed
   aloud in the run log. No silent bypass exists in this tool.

Usage:
    python tools/unified_land.py [--remote origin] [--branch NAME]
                                 [--check-only] [--no-fetch]
                                 [--allow-shard-intake --justify-shard TXT]
                                 [--allow-bulk --justify-bulk TXT]

Exit codes: 0 synced (pushed, or already in sync); 1 a gate failed;
2 the run could not be performed (no git, no remote, no interpreter).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FETCH_TIMEOUT = 180
PREFLIGHT_TIMEOUT = 1200
PUSH_TIMEOUT = 1200


def scrubbed_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Child env for git: MSYS_NO_PATHCONV removed (measured 2026-11-23).

    With it set, hook-spawned interpreters mangle ``/c/...`` args into
    ``C:\\\\c\\\\...`` and gates refuse on nonexistent paths. Without it,
    the identical gates pass. Scrubbing is scoped to children this tool
    spawns; the caller's shell is untouched.
    """
    env = dict(os.environ)
    if env.pop("MSYS_NO_PATHCONV", None) is not None:
        print("unified-land: scrubbed MSYS_NO_PATHCONV for git children "
              "(hook paths mangle with it set; measured 2026-11-23)")
    if extra:
        env.update(extra)
    return env


def run(cmd: list[str], env: dict[str, str], timeout: int,
        cwd: Path = REPO) -> subprocess.CompletedProcess[str]:
    """Run a child with bounded wait and explicit UTF-8 decode."""
    return subprocess.run(
        cmd, cwd=str(cwd), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default=None,
                    help="default: current branch")
    ap.add_argument("--check-only", action="store_true",
                    help="run fetch + preflight, never push")
    ap.add_argument("--no-fetch", action="store_true",
                    help="skip fetch (stale base risk; not recommended)")
    ap.add_argument("--allow-shard-intake", action="store_true")
    ap.add_argument("--justify-shard", default="")
    ap.add_argument("--allow-bulk", action="store_true")
    ap.add_argument("--justify-bulk", default="")
    args = ap.parse_args(argv)

    env = scrubbed_env()
    py = sys.executable

    if args.branch:
        branch = args.branch
    else:
        r = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], env, 60)
        if r.returncode != 0:
            print("unified-land: cannot read current branch", file=sys.stderr)
            print(r.stderr[-2000:], file=sys.stderr)
            return 2
        branch = r.stdout.strip()
    print(f"unified-land: remote={args.remote} branch={branch}")

    if not args.no_fetch:
        r = run(["git", "fetch", args.remote, branch], env, FETCH_TIMEOUT)
        if r.returncode != 0:
            print("unified-land: fetch failed; refusing on a stale base",
                  file=sys.stderr)
            print(r.stderr[-2000:], file=sys.stderr)
            return 2
        print("unified-land: fetch ok (base is fresh, not remembered)")

    r = run(["git", "rev-parse", f"{args.remote}/{branch}"], env, 60)
    if r.returncode != 0:
        print(f"unified-land: no tracking ref {args.remote}/{branch}; "
              "push once manually first", file=sys.stderr)
        return 2
    base = r.stdout.strip()
    r = run(["git", "rev-parse", "HEAD"], env, 60)
    head = r.stdout.strip()
    print(f"unified-land: base={base[:12]} head={head[:12]}")
    if base == head:
        print("unified-land: IN SYNC -- nothing to push (base == HEAD)")
        return 0

    push_env = scrubbed_env()
    if args.allow_shard_intake:
        if not args.justify_shard:
            print("unified-land: --allow-shard-intake needs "
                  "--justify-shard", file=sys.stderr)
            return 2
        push_env["ALLOW_SHARD_INTAKE"] = "1"
        print(f"unified-land: ALLOW_SHARD_INTAKE=1 declared: "
              f"{args.justify_shard}")
    if args.allow_bulk:
        if not args.justify_bulk:
            print("unified-land: --allow-bulk needs --justify-bulk",
                  file=sys.stderr)
            return 2
        push_env["ALLOW_BULK_COMMIT"] = "1"
        print(f"unified-land: ALLOW_BULK_COMMIT=1 declared: "
              f"{args.justify_bulk}")

    print("unified-land: preflight (same gates the push hook runs) ...")
    r = run([py, "tools/preflight_all.py", "--check",
             "--base", base, "--tip", head], push_env, PREFLIGHT_TIMEOUT)
    print(r.stdout[-4000:])
    if r.returncode != 0:
        print("unified-land: PREFLIGHT FAILED -- push not attempted; "
              "fix the named gate or declare its escape aloud",
              file=sys.stderr)
        return 1
    print("unified-land: preflight PASS")

    if args.check_only:
        print("unified-land: --check-only; push skipped by request")
        return 0

    print(f"unified-land: pushing {branch} to {args.remote} ...")
    r = run(["git", "push", args.remote, branch], push_env, PUSH_TIMEOUT)
    print(r.stdout[-2000:])
    print(r.stderr[-2000:], file=sys.stderr)
    if r.returncode != 0:
        print("unified-land: PUSH REFUSED -- the hook names the gate "
              "above; iterate on it, never bypass silently",
              file=sys.stderr)
        return 1

    r = run(["git", "rev-parse", f"{args.remote}/{branch}"], env, 60)
    if r.stdout.strip() == head:
        print(f"unified-land: SYNC PROOF -- {args.remote}/{branch} == "
              f"HEAD ({head[:12]}); the landing happened")
        return 0
    print("unified-land: push exited 0 but tracking ref disagrees; "
          "investigate before claiming sync", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
