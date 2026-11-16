"""ledger_blame.py -- annotate evidence-tier failures with owning commit+lane.

A blocked push dies on rows nobody owns on sight: the pusher runs a full
triage pass over gate output to find whose row broke the tier (servemesh
wire row -> opencode 5514c7da; worktree_snapshot finding -> origin's own
ce64a668). This tool removes that pass. It parses failure text, extracts
repo paths per failing line, resolves (owning_commit, owning_lane) for
each, groups rows by lane, and either prints the routable block (default)
or posts one delivery row per owning lane to the board (--route).

Reads failure text from --file or stdin. Writes annotated rows to
state/ledger_blame_<UTCdate>.jsonl. Reuses tools/attr_push_block.py for
the TURF table and `git log` touchers, so the two can never disagree
about who owns a path.

Board posts use CORE.LaneMessageBoard.post_task with a deterministic
task_id (identical re-post collapses, never duplicates). --route needs
the board DB: on Windows it resolves to the home .azazael dir; on other
estates set AZAZAEL_MEMORY_DIR to the .azazael directory first.

Exit 0 = rows annotated. Exit 2 = no attributable paths found.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import attr_push_block  # noqa: E402  (TURF table + git touchers)

STATE_DIR = REPO / "state"

#: Repo-rooted path prefixes worth attributing. Bare well-known files
#: (NEURAL_MESH_WIRE_OR_CUT.json, GAMORA_*) are covered too: the TURF
#: table matches them by substring, and git log takes any tracked path.
PATH_RE = re.compile(
    r"(?P<p>(?:tools|src|docs|tests|state|Project_ELIZA|CORE|\.githooks)"
    r"/[A-Za-z0-9_.\-/]+(?:\.[A-Za-z0-9]+)?)"
)
GATE_RE = re.compile(r"^\[(?P<gate>[A-Za-z0-9 _/\-]{1,40})\]")
#: Bare well-known files with no directory prefix (NEURAL_MESH_WIRE_OR_CUT.json
#: is the canonical one: attr_push_block.py documents it as the push that
#: cost a triage pass). The TURF table matches these by substring.
BARE_RE = re.compile(
    r"(?<![/\w])(?P<b>[A-Z][A-Za-z0-9_]{2,}\.(?:json|md|py|txt|yml|yaml|sh))"
)
TRAIL_RE = re.compile(r"[:'\",;]+$")
LINECOL_RE = re.compile(r":\d+(?::\d+)?$")


def extract_paths(line: str) -> list[str]:
    """Repo-relative paths mentioned in a failure line, order-kept."""
    found: list[str] = []
    for m in PATH_RE.finditer(line):
        p = TRAIL_RE.sub("", m.group("p"))
        p = LINECOL_RE.sub("", p)
        if p and p not in found:
            found.append(p)
    for m in BARE_RE.finditer(line):
        p = m.group("b")
        if p not in found:
            found.append(p)
    return found


def annotate(path: str) -> tuple[str, str]:
    """(owning_lane, owning_commit) for one repo path."""
    owner = attr_push_block.turf_owner(path)
    try:
        touchers = attr_push_block.newest_touchers(path, 1)
    except Exception:
        touchers = []
    commit = touchers[0] if touchers else "unknown (untracked or git unavailable)"
    return owner, commit


def parse(text: str) -> list[dict]:
    """Failure text -> annotated rows (one per path mentioned)."""
    rows: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        gate_m = GATE_RE.match(line)
        gate = gate_m.group("gate") if gate_m else "nogate"
        for path in extract_paths(line):
            owner, commit = annotate(path)
            rows.append(
                {
                    "gate": gate,
                    "line": line[:300],
                    "path": path,
                    "owning_lane": owner,
                    "owning_commit": commit,
                }
            )
    return rows


def group_by_lane(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["owning_lane"], []).append(r)
    return groups


def render_block(groups: dict[str, list[dict]]) -> str:
    out = ["[LedgerBlame] blocked push routes itself:"]
    for lane in sorted(groups):
        rows = groups[lane]
        if lane == "UNKNOWN":
            out.append(f"  lane UNKNOWN ({len(rows)} rows): newest toucher adjudicates")
        else:
            out.append(f"  route: post delivery to lane.{lane} quoting this block")
        for r in rows:
            out.append(f"    [{r['gate']}] {r['path']}")
            out.append(f"      touched: {r['owning_commit']}")
    return "\n".join(out)


def write_ledger(rows: list[dict], path: Path | None = None) -> Path:
    stamp = datetime.now(timezone.utc)
    if path is None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        path = STATE_DIR / ("ledger_blame_%s.jsonl" % stamp.strftime("%Y-%m-%d"))
    try:
        head = os.popen("git -C %s rev-parse --short HEAD 2>/dev/null" % REPO).read().strip()
    except Exception:
        head = "unknown"
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            rec = dict(r)
            rec["annotated_at"] = stamp.isoformat(timespec="seconds")
            rec["head"] = head or "unknown"
            f.write(json.dumps(rec) + "\n")
    return path


def post_deliveries(
    groups: dict[str, list[dict]], board: object, source_lane: str = "freebuff"
) -> list[int]:
    """One delivery row per known owning lane. Returns board ids posted."""
    block = render_block(groups)
    digest = hashlib.sha1(block.encode("utf-8")).hexdigest()[:8]
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    posted: list[int] = []
    for lane in sorted(groups):
        if lane == "UNKNOWN":
            continue
        detail = (
            "Push-block attribution %s (ledger blame, no triage pass):\n%s"
            % (date, block)
        )
        bid = board.post_task(
            lane=lane,
            action="Push-block attribution",
            detail=detail,
            task_id="ledger-blame-%s-%s-%s" % (date, lane, digest),
            source_lane=source_lane,
            metadata={"kind": "delivery", "tool": "ledger_blame.py"},
        )
        posted.append(int(bid))
    return posted


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Attribute gate failures to owning lanes.")
    ap.add_argument("--file", default=None, help="failure text file (default: stdin)")
    ap.add_argument("--route", action="store_true",
                    help="post one delivery row per owning lane to the board")
    ap.add_argument("--ledger", default=None, help="ledger jsonl path override")
    ap.add_argument("--lane", default="freebuff", help="source lane for --route posts")
    args = ap.parse_args(argv)

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        ap.error("no input: pass --file or pipe failure text on stdin")
        return 2

    rows = parse(text)
    if not rows:
        print("[LedgerBlame] no attributable repo paths in input; nothing to route.")
        return 2
    ledger = write_ledger(rows, Path(args.ledger) if args.ledger else None)
    print("[LedgerBlame] %d rows -> %s" % (len(rows), ledger))
    groups = group_by_lane(rows)
    print(render_block(groups))
    if args.route:
        sys.path.insert(0, str(REPO / "src"))
        from CORE.LaneMessageBoard import LaneMessageBoard

        board = LaneMessageBoard(lane=args.lane)
        posted = post_deliveries(groups, board, source_lane=args.lane)
        print("[LedgerBlame] posted deliveries: %s" % (posted or "none (all UNKNOWN)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
