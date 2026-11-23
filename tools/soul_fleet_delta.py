"""soul_fleet_delta: new / resolved / aging findings across dated fleet reports.

A single snapshot cannot tell a newborn finding from a month-old one --
both print the same line, and the month-old one has been silently accepted.
This tool diffs two reports (soul_fleet_sight or soul_fleet_sweep JSON) and
says, per repo: NEW (in cur, not prev), RESOLVED (in prev, not cur), AGING
(in both -- with first-seen tracked in a state file so age is measured,
never guessed).

Exit contract (mirrors sight/sweep): 0 ran with no NEW findings,
1 NEW findings present, 2 inputs unreadable.

Usage:
  python tools/soul_fleet_delta.py --prev <older.json> --cur <newer.json>
      [--state <first_seen.json>] [--age-days 14] [--json <out.json>]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


def load_report(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"unreadable report {path}: {exc}") from exc


def findings_map(report: dict) -> dict[str, list[str]]:
    """repo name -> sorted finding strings. Accepts sight or sweep schema."""
    repos = report.get("repos") or report.get("entries") or []
    out: dict[str, list[str]] = {}
    for entry in repos:
        name = entry.get("name") or entry.get("repo") or "?"
        out[name] = sorted(entry.get("findings") or [])
    return out


def diff_reports(
    prev: dict[str, list[str]], cur: dict[str, list[str]]
) -> dict[str, dict[str, list[str]]]:
    """Per repo: new / resolved / persisting finding strings."""
    result: dict[str, dict[str, list[str]]] = {}
    for name in sorted(set(prev) | set(cur)):
        p, c = set(prev.get(name, [])), set(cur.get(name, []))
        entry = {
            "new": sorted(c - p),
            "resolved": sorted(p - c),
            "persisting": sorted(c & p),
        }
        if any(entry.values()) or name not in prev or name not in cur:
            result[name] = entry
    return result


def load_state(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def apply_first_seen(
    diff: dict[str, dict[str, list[str]]],
    state: dict,
    today: str,
    age_days: int,
) -> tuple[dict, dict]:
    """Stamp first-seen dates; mark persisting findings older than age_days DUE.

    Returns (diff_annotated, updated_state). repos vanished from cur are
    dropped from state so it cannot grow without bound.
    """
    new_state: dict = {}
    for name, entry in diff.items():
        repo_state: dict = dict(state.get(name, {}))
        for finding in entry["new"]:
            repo_state.setdefault(finding, today)
        for finding in entry["persisting"]:
            repo_state.setdefault(finding, today)
        annotated = []
        for finding in entry["persisting"]:
            try:
                age = (date.fromisoformat(today)
                       - date.fromisoformat(repo_state[finding])).days
            except ValueError:
                age = 0
            annotated.append({"finding": finding,
                              "first_seen": repo_state[finding],
                              "age_days": age,
                              "due": age >= age_days})
        entry["persisting"] = annotated
        new_state[name] = {f: repo_state[f]
                           for f in list(entry["new"])
                           + [a["finding"] for a in annotated]
                           if f in repo_state}
    return diff, new_state


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Diff two fleet reports.")
    ap.add_argument("--prev", required=True)
    ap.add_argument("--cur", required=True)
    ap.add_argument("--state", default=None)
    ap.add_argument("--age-days", type=int, default=14)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    try:
        prev = findings_map(load_report(Path(args.prev)))
        cur = findings_map(load_report(Path(args.cur)))
    except ValueError as exc:
        print(f"delta: {exc}", file=sys.stderr)
        return 2

    diff = diff_reports(prev, cur)
    state_path = Path(args.state) if args.state else None
    diff, new_state = apply_first_seen(diff, load_state(state_path),
                                       date.today().isoformat(), args.age_days)
    if state_path is not None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(new_state, indent=2),
                              encoding="utf-8")

    n_new = sum(len(e["new"]) for e in diff.values())
    n_res = sum(len(e["resolved"]) for e in diff.values())
    n_due = sum(1 for e in diff.values()
                for a in e["persisting"] if a["due"])
    for name, entry in diff.items():
        tags = []
        if entry["new"]:
            tags.append(f"NEW={len(entry['new'])}")
        if entry["resolved"]:
            tags.append(f"RESOLVED={len(entry['resolved'])}")
        due = [a for a in entry["persisting"] if a["due"]]
        if due:
            tags.append(f"DUE({args.age_days}d+)={len(due)}")
        if tags:
            print(f"{name}: {', '.join(tags)}")
    print(f"{len(diff)} repo(s) with movement, "
          f"{n_new} new, {n_res} resolved, {n_due} due")
    if args.json:
        Path(args.json).write_text(
            json.dumps({"diff": diff,
                        "summary": {"new": n_new, "resolved": n_res,
                                    "due": n_due}}, indent=2),
            encoding="utf-8")
    return 1 if n_new else 0


if __name__ == "__main__":
    raise SystemExit(main())
