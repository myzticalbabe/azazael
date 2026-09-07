"""Finisher: extract the last uncovered BCC files.

Gemini first with a live model override (the azazael default gemini-2.0-flash
is retired -> 404), then cloudflare/openrouter with a quota-reset sleep between
attempts. Persists chunks and merges all chunk_*.json into .graphify_semantic.json.
"""
import json
import sys
import threading
import time
from pathlib import Path

AZAZAEL_SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(AZAZAEL_SRC))
GRAPHIFY_SP = Path(r"C:/Users/clint/AppData/Local/Programs/Python/Python314/Lib/site-packages")
sys.path.insert(0, str(GRAPHIFY_SP))

from graphify.llm import _EXTRACTION_SYSTEM, _pack_chunks_by_tokens, _parse_llm_json, _read_files
from CORE.inference.providers import OpenAIProvider

ROOT = Path("BCC_GRAPH_INPUT").resolve()
OUT = Path("graphify-out")
CHUNK_DIR = OUT / "chunks"
AZ_PREFIX = f"chunk_fin{int(time.time())}_"
TOKEN_BUDGET = 12_000
MAX_TOKENS = 8192


def call_timeout(p, msg, timeout_s, **kw):
    holder = {}

    def _run():
        try:
            holder["r"] = p.chat(msg, **kw)
        except Exception as exc:
            holder["r"] = {"error": f"{type(exc).__name__}: {str(exc)[:140]}"}

    th = threading.Thread(target=_run, daemon=True)
    th.start()
    th.join(timeout_s)
    if th.is_alive():
        return {"error": f"TIMEOUT after {timeout_s}s"}
    return holder.get("r") or {"error": "empty"}


# Determine remaining files by coverage
detect = json.loads((OUT / ".graphify_detect.json").read_text(encoding="utf-8"))
all_files = [Path(f).resolve() for cat in ("document", "paper", "image") for f in detect["files"].get(cat, [])]
done = set()
for cf in CHUNK_DIR.glob("chunk_*.json"):
    try:
        d = json.loads(cf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for n in d.get("nodes", []):
        if n.get("source_file"):
            done.add(str(n["source_file"]).replace("\\", "/"))
    for e in d.get("edges", []):
        if e.get("source_file"):
            done.add(str(e["source_file"]).replace("\\", "/"))
remaining = []
for f in all_files:
    try:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        rel = str(f)
    if rel not in done and f.name not in done:
        remaining.append(f)
print(f"Remaining files: {len(remaining)} -> {[f.name for f in remaining]}", flush=True)
if not remaining:
    print("Nothing left to extract.", flush=True)
    sys.exit(0)

chunks = _pack_chunks_by_tokens(remaining, TOKEN_BUDGET)
print(f"{len(chunks)} chunks", flush=True)

ATTEMPTS = [
    ("gemini", {"model": "gemini-3-flash-preview"}),
    ("cloudflare", {}),
    ("openrouter", {}),
]

for i, chunk in enumerate(chunks):
    tag = f"{i:03d}"
    files = chunk
    msg = _read_files(files, ROOT)
    saved = False
    for round_no in range(3):
        for name, kw in ATTEMPTS:
            try:
                p = OpenAIProvider(name)
                if not p.has_valid_key():
                    continue
                resp = call_timeout(p, msg, 120, system_prompt=_EXTRACTION_SYSTEM,
                                    temperature=0, max_tokens=MAX_TOKENS, **kw)
            except Exception as exc:
                print(f"  [{tag}] {name}: EXC {type(exc).__name__}", flush=True)
                continue
            if "error" in resp:
                err = str(resp["error"])[:110]
                print(f"  [{tag}] {name}: {err}", flush=True)
                # 429/timeout -> wait out the per-minute window once
                if ("429" in err or "TIMEOUT" in err) and round_no < 2:
                    print("  ... sleeping 65s for quota reset", flush=True)
                    time.sleep(65)
                continue
            content = resp.get("content") or ""
            parsed = _parse_llm_json(content)
            if parsed.get("nodes") or parsed.get("edges"):
                (CHUNK_DIR / f"{AZ_PREFIX}{tag}.json").write_text(
                    json.dumps(parsed, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  [{tag}] saved via {name}: {len(parsed['nodes'])} nodes, "
                      f"{len(parsed['edges'])} edges", flush=True)
                saved = True
                break
            if len(content) > 4000:
                print(f"  [{tag}] {name}: {len(content)} chars unparseable (truncation) - not retrying this provider", flush=True)
        if saved:
            break
        # both providers failed this round; loop sleeps inside on 429
    if not saved:
        print(f"  [{tag}] STILL FAILED after 3 rounds", flush=True)
    time.sleep(2)

# Merge everything
merged_nodes, merged_edges, merged_hyper = [], [], []
for cf in sorted(CHUNK_DIR.glob("chunk_*.json")):
    try:
        d = json.loads(cf.read_text(encoding="utf-8"))
    except Exception:
        continue
    merged_nodes += d.get("nodes", [])
    merged_edges += d.get("edges", [])
    merged_hyper += d.get("hyperedges", [])
seen, deduped = set(), []
for n in merged_nodes:
    if n.get("id") not in seen:
        seen.add(n.get("id"))
        deduped.append(n)
(OUT / ".graphify_semantic.json").write_text(json.dumps({
    "nodes": deduped, "edges": merged_edges, "hyperedges": merged_hyper,
    "input_tokens": 0, "output_tokens": 0,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"MERGED: {len(deduped)} nodes, {len(merged_edges)} edges", flush=True)

try:
    from CORE.direct_memory import record
    record("bcc_extraction_complete", {"nodes": len(deduped), "edges": len(merged_edges),
                                       "remaining_files": [f.name for f in remaining]})
except Exception as exc:
    print(f"(dm record skipped: {exc})", flush=True)
