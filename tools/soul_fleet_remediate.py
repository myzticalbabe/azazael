"""soul_fleet_remediate: the corrective half of the daily loop.

Sight reports; this repairs -- but only what the ownership policy names,
only findings old enough to have had their warning period, and only after
a snapshot tag is taken. Anything else is listed for a human and left
untouched.

Safety rules (measured failures behind each):
- DRY-RUN DEFAULT: without --apply nothing mutates; the plan prints.
- SNAPSHOT FIRST: with --apply, `git tag <prefix>-<utc-ts>` lands before
  any other mutation, so every auto-fix is reversible by tag.
- AGE GATE: a finding acts only when first-seen + min_age_days <= today.
  Today's surprise is never today's deletion.
- POLICY ALLOWLIST: only actions named in the policy file run. Unknown
  finding classes are human work, never auto work.
- STASH BAN: uncommitted work is NEVER stashed/reset/gc-aggressive-cleaned
  (a hook in this fleet refuses refs/stash; stash-then-reset scripts eat
  the work they protect). DIRTY findings always stay human-side.

Safe auto actions (v1): FETCH-PRUNE (drops dead remote-tracking refs),
WORKTREE-PRUNE (clears metadata for worktrees deleted outside git).
Branch deletion belongs to the reaper, not here.

Usage:
  python tools/soul_fleet_remediate.py --report <sight.json>
      --state <first_seen.json> [--policy <policy.json>] [--apply]
      [--json <out.json>]

Exit: 0 every DUE finding was policy-covered (or none due),
      1 human-side work remains, 2 bad inputs.
"""

from __future__ import annotations

import argparse
import calendar
import json
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def parse_day(s: object) -> date | None:
    """Strict YYYY-MM-DD parse that cannot raise.
    The staged scanner blocks try/except-as-validation (a swallowed
    ValueError is how a stamp silently becomes absent), so shape and
    range are checked first and date() only sees a valid triple."""
    if not isinstance(s, str):
        return None
    hit = _DATE_RE.match(s)
    if hit is None:
        return None
    y, m, d = int(hit.group(1)), int(hit.group(2)), int(hit.group(3))
    if not 1 <= m <= 12:
        return None
    if not 1 <= d <= calendar.monthrange(y, m)[1]:
        return None
    return date(y, m, d)


def run_git(args: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True,
            timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, f"git failed: {exc}"
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


DEFAULT_POLICY = {
    "min_age_days": 14,
    "snapshot_prefix": "auto-snap",
    "auto_actions": ["FETCH-PRUNE", "WORKTREE-PRUNE"],
}


def load_json(path: Path, what: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable {what} {path}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def due_findings(report: dict, state: dict, min_age: int,
                 today: str) -> tuple[dict[str, list[str]], list[str]]:
    """repo -> DUE finding strings (first-seen + min_age <= today).
    Returns (due, skipped): malformed first-seen dates are recorded in
    skipped, never silently dropped."""
    out: dict[str, list[str]] = {}
    skipped: list[str] = []
    for entry in report.get("repos", []):
        name = entry.get("name", "?")
        repo_state = state.get(name, {})
        due = []
        for finding in entry.get("findings", []):
            first = repo_state.get(finding)
            if first is None:
                continue  # unseen: warning period starts now, not due
            first_day = parse_day(first)
            if first_day is None:
                skipped.append(f"{name}: malformed first-seen "
                               f"{first!r} for {finding!r}")
                continue
            today_day = parse_day(today)
            if today_day is None:  # cannot happen; today is generated
                skipped.append(f"{name}: bad run date {today!r}")
                continue
            if (today_day - first_day).days >= min_age:
                due.append(finding)
        if due:
            out[name] = sorted(due)
    return out, skipped


def plan_for(finding: str, auto_actions: list[str]) -> str | None:
    """Map a DUE finding to a policy action, or None (human-side).
    v1: every finding class stays human-side -- uncommitted work, sync
    state, origins and defaults all need a judgement call. The auto
    pair below runs as repo-level HYGIENE (unconditionally safe: dropped
    refs were already gone server-side; pruned worktree metadata was
    already detached), never as a fix for a specific finding. Branch
    deletion belongs to the reaper, not here."""
    return None


def snapshot(path: Path, prefix: str, dry: bool) -> str:
    tag = (prefix + "-"
           + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if dry:
        return f"would-tag {tag}"
    rc, out = run_git(["tag", tag], path)
    if rc != 0:
        raise RuntimeError(f"snapshot tag failed in {path}: {out}")
    return tag


def apply_action(path: Path, action: str, dry: bool) -> str:
    if action == "FETCH-PRUNE":
        if dry:
            return "would run: git fetch --prune origin"
        rc, out = run_git(["fetch", "--prune", "origin"], path)
        return f"fetch-prune rc={rc} {out[:200]}"
    if action == "WORKTREE-PRUNE":
        if dry:
            return "would run: git worktree prune"
        rc, out = run_git(["worktree", "prune"], path)
        return f"worktree-prune rc={rc} {out[:200]}"
    return f"unknown action {action}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Policy-gated fleet remediation.")
    ap.add_argument("--report", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--root", required=True,
                    help="fleet root holding the repo directories")
    ap.add_argument("--policy", default=None)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    try:
        report = load_json(Path(args.report), "report")
        state = load_json(Path(args.state), "state")
    except ValueError as exc:
        print(f"remediate: {exc}", file=sys.stderr)
        return 2
    policy = dict(DEFAULT_POLICY)
    if args.policy:
        try:
            policy.update(load_json(Path(args.policy), "policy"))
        except ValueError as exc:
            print(f"remediate: {exc}", file=sys.stderr)
            return 2

    root = Path(args.root)
    today = datetime.now(timezone.utc).date().isoformat()
    due, skipped = due_findings(report, state, int(policy["min_age_days"]),
                                  today)
    for line in skipped:
        print(f"SKIPPED-DATE: {line}")
    auto_actions = list(policy["auto_actions"])

    planned: dict[str, list[dict]] = {}
    human: dict[str, list[str]] = {}
    hygiene = [a for a in ("FETCH-PRUNE", "WORKTREE-PRUNE")
               if a in auto_actions]
    for name, findings in due.items():
        human[name] = list(findings)
        if hygiene:
            planned[name] = [{"finding": "(hygiene: dead tracking refs / "
                                          "detached worktree metadata)",
                               "action": a} for a in hygiene]

    results: dict[str, list[str]] = {}
    if args.apply:
        for name, items in planned.items():
            repo = root / name
            if not (repo / ".git").is_dir() and not (repo / "HEAD").is_file():
                results[name] = [f"skip: not a repo dir: {repo}"]
                continue
            try:
                tag = snapshot(repo, str(policy["snapshot_prefix"]),
                               dry=False)
            except RuntimeError as exc:
                results[name] = [str(exc)]
                continue
            lines = [f"snapshot {tag}"]
            for item in items:
                lines.append(f"{item['action']}: "
                             + apply_action(repo, item["action"], dry=False))
            results[name] = lines
    else:
        for name, items in planned.items():
            results[name] = [f"would snapshot, then {i['action']} "
                             f"for: {i['finding']}" for i in items]

    for name in sorted(set(results) | set(planned)):
        print(f"{name}:")
        for line in results.get(name, []):
            print(f"  - {line}")
    n_human = sum(len(v) for v in human.values())
    if human:
        print(f"HUMAN-SIDE ({n_human} finding(s), left untouched):")
        for name, findings in sorted(human.items()):
            for finding in findings:
                print(f"  - {name}: {finding}")
    print(f"{len(due)} repo(s) with DUE findings, "
          f"{'APPLIED' if args.apply else 'PLANNED'}, "
          f"{n_human} human-side, {len(skipped)} skipped-date")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"planned": planned, "human": human, "results": results,
             "applied": bool(args.apply)}, indent=2), encoding="utf-8")
    return 1 if n_human else 0


if __name__ == "__main__":
    raise SystemExit(main())
