"""expand_bake_pilot.py — PILOT: 10 error_fix pairs x 1 demo, round-robin live providers.

Mindful mode: skips saturated/dead providers (gemini 503, mistral 429,
empty-balance keys). 3s spacing between calls. Writes state/bake_pilot.jsonl
Usage: python tools/expand_bake_pilot.py [--n 10]
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from CORE.inference.providers import get_provider
from CORE.sentinel_enforcer import permit_here

CORPUS = ROOT / "state" / "bake_corpus.jsonl"
MERGED = ROOT / "state" / "bake_merged.jsonl"
OUT = ROOT / "state" / "bake_pilot.jsonl"
PILOT_PROVIDERS = ["groq", "openrouter", "pollinations", "nvidia_nim", "cohere"]

PROMPT = ("Turn this real incident into ONE training demonstration for a coding agent. "
          "Reply in exactly 3 short lines starting with SITUATION: / CORRECT: / RULE:. "
          "Incident:\n")


def pick_corpus():
    """The pre-merge or the merged corpus, whichever the loop actually has.

    merge_bake_lane.py writes state/bake_merged.jsonl and calls it "the single
    file the demo-expansion step reads"; this pilot used to read bake_corpus
    (505 rows) unconditionally and print DEMOS= with no row count or file name,
    so a run against the smaller input looked identical to one against the
    merged set. Returns None when neither exists -- the caller must not treat
    that as an empty corpus.
    """
    for path in (MERGED, CORPUS):
        if path.is_file():
            return path
    return None


def main():
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10
    corpus = pick_corpus()
    if corpus is None:
        print("SOURCE=- rows=0 -- neither %s nor %s exists; "
              "run tools/merge_bake_lane.py --apply first" % (MERGED.name, CORPUS.name))
        return 2
    rows = [json.loads(l) for l in open(corpus, encoding="utf-8")]
    errs = [r for r in rows if r["kind"] == "error_fix"][:n]
    demos = []
    for i, rec in enumerate(errs):
        pname = PILOT_PROVIDERS[i % len(PILOT_PROVIDERS)]
        try:
            p = get_provider(pname)
            r = p.chat(PROMPT + rec["title"] + "\n" + rec["body"][:1200],
                       max_tokens=256, temperature=0.7)
            if r.get("error"):
                print("pair %d %s NO %s" % (i, pname, str(r["error"])[:90]), flush=True)
                continue
            demos.append({"pair": rec["item_id"], "source": rec["source"],
                          "teacher": pname, "demo": r.get("content", "")[:1500]})
            print("pair %d %s YES %dms" % (i, pname, r.get("elapsed_ms", 0)), flush=True)
        except Exception as e:
            print("pair %d %s EXC %s" % (i, pname, str(e)[:90]), flush=True)
        time.sleep(3)
    with permit_here("bake pilot output"):
        with open(OUT, "w", encoding="utf-8") as fh:
            for d in demos:
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    print("SOURCE=%s rows=%d error_fix=%d DEMOS=%d -> %s" % (
        corpus.name, len(rows), len(errs), len(demos), OUT.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
