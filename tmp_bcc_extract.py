"""Resumable Gemini semantic extraction for the BCC corpus (graphify Step 3, Part B).

Calls graphify.llm.extract_corpus_parallel with per-chunk persistence: the
on_chunk_done callback writes each chunk result to disk the moment it lands, so
a process kill (terminal timeout) loses at most one in-flight chunk.

Idempotent: pass --resume to skip files that already have extraction output in
an existing chunk file (matched by source_file). Writes the final merged
.graphify_semantic.json when all files are covered.
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path("BCC_GRAPH_INPUT")
OUT = Path("graphify-out")
CHUNK_DIR = OUT / "chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

resume = "--resume" in sys.argv

detect = json.loads((OUT / ".graphify_detect.json").read_text(encoding="utf-8"))
all_files = [f for cat in ("document", "paper", "image") for f in detect["files"].get(cat, [])]
print(f"Corpus files for semantic extraction: {len(all_files)}", flush=True)

# Collect already-extracted source files from existing chunk files
done_sources = set()
existing_chunks = []
if resume:
    for cf in sorted(CHUNK_DIR.glob("chunk_*.json")):
        try:
            d = json.loads(cf.read_text(encoding="utf-8"))
        except Exception:
            print(f"WARNING: unreadable chunk file {cf.name}, ignoring", flush=True)
            continue
        existing_chunks.append(d)
        for n in d.get("nodes", []):
            sf = n.get("source_file")
            if sf:
                done_sources.add(str(sf))
        for e in d.get("edges", []):
            sf = e.get("source_file")
            if sf:
                done_sources.add(str(sf))
    remaining = [f for f in all_files if str(f) not in done_sources]
    print(f"Resume: {len(done_sources)} sources already extracted, {len(remaining)} remaining", flush=True)
else:
    remaining = list(all_files)

if not remaining:
    print("Nothing to extract - all files already covered.", flush=True)
else:
    from graphify.llm import extract_corpus_parallel

    file_paths = [Path(f) for f in remaining]
    n_chunks = max(1, (len(file_paths) + 19) // 20)
    print(f"Semantic extraction: {len(file_paths)} files -> ~{n_chunks} chunks via Gemini (serialized for free-tier quota)", flush=True)

    # Free tier allows ~5 requests/min on gemini-3-flash: serialize chunks and
    # retry failed passes after a quota-reset sleep.
    for attempt in range(1, 4):
        t0 = time.time()
        state = {"done": 0}

        def on_chunk_done(idx, total, chunk_result):
            state["done"] += 1
            fn = CHUNK_DIR / f"chunk_{idx:03d}.json"
            fn.write_text(json.dumps(chunk_result, ensure_ascii=False, indent=1), encoding="utf-8")
            nn = len(chunk_result.get("nodes", []))
            ne = len(chunk_result.get("edges", []))
            print(f"  chunk {idx}/{total} saved: {nn} nodes, {ne} edges ({time.time()-t0:.0f}s elapsed)", flush=True)

        result = extract_corpus_parallel(
            files=file_paths,
            backend="gemini",
            root=ROOT,
            on_chunk_done=on_chunk_done,
            max_concurrency=1,
        )
        # Count files this pass actually produced output for
        produced = set()
        for n in result.get("nodes", []):
            sf = n.get("source_file")
            if sf:
                produced.add(str(sf))
        still_missing = [f for f in file_paths if str(f) not in produced]
        print(f"Pass {attempt}: {len(produced)} files produced output, {len(still_missing)} still missing", flush=True)
        if not still_missing:
            break
        if attempt < 3:
            print(f"Quota-reset sleep 55s before retry pass...", flush=True)
            time.sleep(55)
            file_paths = [Path(f) for f in still_missing]
    # extract_corpus_parallel merges chunks; persist its return too (may include token counts)
    (OUT / ".graphify_semantic_new.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"Parallel run complete: {len(result.get('nodes', []))} nodes, "
          f"{len(result.get('edges', []))} edges, "
          f"tokens in={result.get('input_tokens', 0):,} out={result.get('output_tokens', 0):,}", flush=True)

# Merge: chunk files take precedence (they are the canonical per-chunk outputs);
# if no chunk files exist, fall back to the parallel-run merged output.
merged_nodes, merged_edges, merged_hyper = [], [], []
chunk_count = 0
for cf in sorted(CHUNK_DIR.glob("chunk_*.json")):
    d = json.loads(cf.read_text(encoding="utf-8"))
    merged_nodes += d.get("nodes", [])
    merged_edges += d.get("edges", [])
    merged_hyper += d.get("hyperedges", [])
    chunk_count += 1

if chunk_count == 0:
    alt = OUT / ".graphify_semantic_new.json"
    if alt.exists():
        d = json.loads(alt.read_text(encoding="utf-8"))
        merged_nodes = d.get("nodes", [])
        merged_edges = d.get("edges", [])
        merged_hyper = d.get("hyperedges", [])

# Dedupe nodes by id (first wins)
seen = set()
deduped = []
for n in merged_nodes:
    if n.get("id") not in seen:
        seen.add(n.get("id"))
        deduped.append(n)

sem = {
    "nodes": deduped,
    "edges": merged_edges,
    "hyperedges": merged_hyper,
    "input_tokens": 0,
    "output_tokens": 0,
}
(OUT / ".graphify_semantic.json").write_text(json.dumps(sem, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"MERGED .graphify_semantic.json: {len(deduped)} nodes, {len(merged_edges)} edges, "
      f"{len(merged_hyper)} hyperedges (from {chunk_count} chunk files)", flush=True)
