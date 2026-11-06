#!/usr/bin/env python3
"""bake_append.py: the only sanctioned writer for bake harvest lanes.

Doctrine (user mandate 2026-11-06): every error must evolve the harness.
Concretely: rows failing schema are REJECTED HERE, at write time, instead
of dying as BAD_KIND drops at merge time (which is how 3 forge rows were
nearly lost on 2026-11-06: kind "fact" is not in the merge tool's KINDS).

Usage:
  python tools/bake_append.py --lane state/xxx.jsonl --kind lesson \\
      --id my-row --title "T" --body "text >= 40 chars..."
  python tools/bake_append.py --lane state/xxx.jsonl --kind lesson \\
      --id my-row --title "T" --body-file /tmp/body.txt
Exit 0 appended (prints new line count); exit 2 rejected (reason on stdout).
"""
import argparse
import json
import os
import sys

KINDS = {"error_fix", "lesson", "mandate",
         "sop_rule", "violation", "anti_pattern"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--kind", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--source", default="freebuff-harness")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--body")
    g.add_argument("--body-file")
    a = ap.parse_args()
    if a.kind not in KINDS:
        print("REJECTED BAD_KIND %r (valid: %s)"
              % (a.kind, sorted(KINDS)))
        return 2
    body = a.body
    if a.body_file:
        with open(a.body_file, encoding="utf-8") as f:
            body = f.read()
    if len(body or "") < 40:
        print("REJECTED BODY-TOO-SHORT (%d chars, need >= 40)"
              % len(body or ""))
        return 2
    row = {"source": a.source, "item_id": a.id,
           "title": a.title, "body": body, "kind": a.kind}
    line = json.dumps(row)
    json.loads(line)  # must be one clean JSON line
    lane = a.lane
    if not os.path.exists(lane):
        print("REJECTED NO-SUCH-LANE %s" % lane)
        return 2
    with open(lane, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    n = sum(1 for _ in open(lane, encoding="utf-8"))
    print("appended %s as line %d" % (a.id, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
