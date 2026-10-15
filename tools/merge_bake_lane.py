"""merge_bake_lane.py — validate + dedupe a lane file into the bake loop input.

Lane files (e.g. state/bake_deepseek_712.jsonl from Engram #714) arrive
from concurrent workers. This tool is the coordinator-side merge gate:
  1. validates every line (JSON + required keys source/item_id/title/body/kind
     + kind in schema + body >= 40 chars). Invalid rows go to the report,
     never to the merged set (a late hallucinated row dies here, per #714).
  2. dedupes row titles against bake_corpus.jsonl + bake_harvest_*.jsonl
     (normalized) and intra-file. Dupes go to the report with reasons.
  3. writes state/bake_merged.jsonl = corpus + harvest + accepted lane rows,
     the single file the demo-expansion step reads.

Usage: python tools/merge_bake_lane.py --lane state/bake_deepseek_712.jsonl [--apply]
  default = dry run (counts only). --apply writes state/bake_merged.jsonl
  + state/bake_merge_report.txt. --lane is repeatable.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MERGED = ROOT / "state" / "bake_merged.jsonl"
OUT_REPORT = ROOT / "state" / "bake_merge_report.txt"
REQUIRED = ("source", "item_id", "title", "body", "kind")
KINDS = {"error_fix", "lesson", "mandate", "sop_rule", "violation", "anti_pattern"}


def norm_title(t):
    return re.sub(r"\s+", " ", str(t).strip().lower())


def load_jsonl(fp):
    rows = []
    for line in Path(fp).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def base_rows():
    rows = []
    corpus = ROOT / "state" / "bake_corpus.jsonl"
    if corpus.exists():
        rows.extend(load_jsonl(corpus))
    for fp in sorted((ROOT / "state").glob("bake_harvest_*.jsonl")):
        rows.extend(load_jsonl(fp))
    return rows


def merge(lanes):
    base = base_rows()
    seen = set(norm_title(r.get("title", "")) for r in base)
    merged = list(base)
    dropped = []
    accepted = 0
    for lane in lanes:
        try:
            rows = load_jsonl(lane)
        except OSError as e:
            dropped.append((str(lane), "UNREADABLE", str(e)[:80]))
            continue
        except ValueError as e:
            dropped.append((str(lane), "BAD_JSON", str(e)[:80]))
            continue
        lane_seen = set()
        for i, r in enumerate(rows):
            where = "%s:%d" % (Path(lane).name, i + 1)
            if not isinstance(r, dict) or any(k not in r for k in REQUIRED):
                dropped.append((where, "BAD_SCHEMA", "missing keys"))
                continue
            if r.get("kind") not in KINDS:
                dropped.append((where, "BAD_KIND", str(r.get("kind"))[:40]))
                continue
            if len(str(r.get("body", ""))) < 40:
                dropped.append((where, "too-short", str(r.get("title", ""))[:60]))
                continue
            key = norm_title(r.get("title", ""))
            if not key:
                dropped.append((where, "empty-title", ""))
                continue
            if key in seen or key in lane_seen:
                dropped.append((where, "dup", str(r.get("title", ""))[:60]))
                continue
            lane_seen.add(key)
            seen.add(key)
            merged.append({"source": str(r["source"])[:80], "item_id": str(r["item_id"])[:80],
                           "title": str(r["title"])[:120], "body": str(r["body"])[:4000],
                           "kind": r["kind"]})
            accepted += 1
    return merged, dropped, accepted, len(base)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", action="append", default=[])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    lanes = args.lane or [str(ROOT / "state" / "bake_deepseek_712.jsonl")]

    merged, dropped, accepted, base_n = merge(lanes)
    print("BASE=%d ACCEPTED=%d MERGED=%d DROPPED=%d" % (base_n, accepted, len(merged), len(dropped)))
    why = {}
    for _, _, w in dropped:
        why[w] = why.get(w, 0) + 1
    print("DROP_REASONS=%s" % json.dumps(why))
    for f, i, w in dropped[:25]:
        print("  drop %s %s (%s)" % (f, i, w))
    if args.apply:
        sys.path.insert(0, str(ROOT / "src"))
        from CORE.sentinel_enforcer import permit_here
        with permit_here("bake merge output"):
            with open(OUT_MERGED, "w", encoding="utf-8") as fh:
                for r in merged:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            with open(OUT_REPORT, "w", encoding="utf-8") as fh:
                for f, i, w in dropped:
                    fh.write("%s\t%s\t%s\n" % (f, i, w))
        print("WROTE %s + %s" % (OUT_MERGED.name, OUT_REPORT.name))


if __name__ == "__main__":
    main()
