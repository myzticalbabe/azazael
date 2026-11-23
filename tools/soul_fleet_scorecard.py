"""soul_fleet_scorecard: supply-chain posture leg for the fleet.

OpenSSF Scorecard grades what none of our git-truth legs ask: is the
repo GOVERNED (branch protection, pinned deps, token permissions,
signed releases, maintenance)? Each check scores 0-10; anything below
the threshold is a finding. Score deltas week over week (via the delta
tool) catch governance regressions the way sight catches dirt.

Honesty rules (HED-6):
- Binary absent -> whole leg SKIPPED with the reason, exit 0. An
  unavailable reading is not a zero and not a pass; it is skipped.
- Non-http origins (local/file remotes) are NOT-APPLICABLE, not zero.
- A per-repo scorecard failure (rate limit, private repo, network) is
  recorded on that repo and the run continues; one broken repo never
  aborts the leg.
- No token? Scorecard still runs, rate-limited. The missing-token note
  prints so the operator knows the numbers are thin, not wrong.

Usage:
  python tools/soul_fleet_scorecard.py --root <fleet-root>
      [--repos a b] [--min-score 5] [--json <out.json>]
      [--binary <path-to-scorecard>]

Exit: 0 clean or skipped, 1 checks below threshold, 2 bad inputs.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_binary(override: str | None = None) -> str | None:
    if override:
        p = Path(override)
        return str(p) if p.is_file() else None
    return shutil.which("scorecard")


def origin_url(path: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=path,
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        no_remote = ""  # git itself unreachable: no origin to report
        return no_remote
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def run_scorecard(binary: str, url: str, timeout: int = 240,
                  env: dict | None = None) -> tuple[bool, dict]:
    """(ok, payload). ok=False carries {'error': ...}, never raises."""
    try:
        proc = subprocess.run(
            [binary, "--repo", url, "--format", "json"],
            capture_output=True, text=True, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        detail = f"scorecard run failed: {exc}"
        return False, {"error": detail}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        snippet = (proc.stderr or proc.stdout or "")[:200]
        return False, {"error": f"unparseable scorecard output: "
                                  f"{exc} :: {snippet}"}
    # Scorecard can exit non-zero (a check errored internally) while
    # still emitting valid JSON with partial results (measured
    # 2026-11-23: EveUnleashed). The payload is data; the exit code is
    # a note, not a veto.
    if proc.returncode != 0:
        payload["error_note"] = (proc.stderr or "")[:200]
    return True, payload


def low_checks(payload: dict, min_score: int) -> list[str]:
    out = []
    checks = payload.get("checks", [])
    if not isinstance(checks, list):
        return out
    for check in checks:
        if not isinstance(check, dict):
            continue
        score = check.get("score", 10)
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            continue  # scorecard marks unevaluable checks "n/a": data, not 0
        if score < min_score:
            out.append(f"SCORECARD-{check.get('name', check.get('check', '?'))}: "
                       f"{score}/10 ({check.get('reason', '')[:120]})")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scorecard posture leg.")
    ap.add_argument("--root", required=True)
    ap.add_argument("--repos", nargs="*", default=None)
    ap.add_argument("--min-score", type=int, default=5)
    ap.add_argument("--json", default=None)
    ap.add_argument("--binary", default=None)
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"scorecard: no root {root}", file=sys.stderr)
        return 2
    binary = find_binary(args.binary)
    if binary is None:
        print("scorecard: SKIPPED -- no scorecard binary on PATH "
              "(install: go install github.com/ossf/scorecard@latest). "
              "This is skipped, not a pass.")
        return 0

    names = args.repos
    if names is None:
        names = sorted(p.name for p in root.iterdir()
                       if p.is_dir() and not p.name.startswith("."))
    token_note = ("GITHUB_AUTH_TOKEN set" if os.environ.get("GITHUB_AUTH_TOKEN")
                  else "no GITHUB_AUTH_TOKEN: results rate-limited, treat "
                       "gaps as thin data, not failures")
    print(f"scorecard: {token_note}")
    results: list[dict] = []
    for name in names:
        path = root / name
        url = origin_url(path)
        entry: dict = {"repo": name, "url": url, "findings": [],
                       "score": None, "note": ""}
        if not url.startswith("http"):
            entry["note"] = "not-applicable: non-http origin"
            results.append(entry)
            continue
        surl = url[:-4] if url.endswith(".git") else url  # Scorecard
        # resolves owner/repo via the API; a .git suffix 404s (measured
        # 2026-11-23: EveUnleashed unreachable until stripped).
        ok, payload = run_scorecard(binary, surl)
        if not ok:
            entry["note"] = payload.get("error", "unknown error")
            results.append(entry)
            continue
        raw_score = payload.get("score", -1)
        if isinstance(raw_score, (int, float)) and not isinstance(raw_score, bool):
            entry["score"] = float(raw_score)
        else:
            entry["score"] = -1
            entry["note"] = f"unparseable aggregate score {raw_score!r}"
        entry["note"] = payload.pop("error_note", "")
        entry["findings"] = low_checks(payload, args.min_score)
        results.append(entry)

    n_low = sum(len(r["findings"]) for r in results)
    for r in results:
        if r["note"]:
            print(f"{r['repo']}: {r['note']}")
        else:
            print(f"{r['repo']}: score {r['score']} "
                  f"({len(r['findings'])} below {args.min_score})")
            for f in r["findings"]:
                print(f"  - {f}")
    print(f"{len(results)} repo(s), {n_low} check(s) below "
          f"{args.min_score}")
    if args.json:
        Path(args.json).write_text(json.dumps({"results": results}, indent=2),
                                    encoding="utf-8")
    return 1 if n_low else 0


if __name__ == "__main__":
    raise SystemExit(main())
