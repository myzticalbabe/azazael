"""BCC semantic extraction via the Azazael 12-provider free inference chain.

Bridges graphify's canonical extraction spec (_EXTRACTION_SYSTEM, token-budget
chunk packing, JSON parsing) onto azazael CORE.inference.providers, per RULE 0D:
on any provider failure, fall through to the next provider immediately — no
waiting, no blocking. Chunks are persisted the moment they land, so re-runs
resume without losing work and without re-billing quota.

Provider order: Groq -> OpenRouter -> Mistral -> Cerebras -> GitHub ->
HuggingFace -> Cloudflare -> SiliconFlow -> Zhipu -> Cohere (nvidia skipped: no
key; gemini skipped: free-tier quota exhausted).
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

from graphify.llm import (  # noqa: E402
    _EXTRACTION_SYSTEM,
    _pack_chunks_by_tokens,
    _parse_llm_json,
    _read_files,
)
from CORE.inference.providers import OpenAIProvider  # noqa: E402

ROOT = Path("BCC_GRAPH_INPUT").resolve()
OUT = Path("graphify-out")
CHUNK_DIR = OUT / "chunks"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)
AZ_PREFIX = f"chunk_az{int(time.time())}_"  # run-unique: never overwrite a prior run's chunks
TOKEN_BUDGET = 12_000  # cloudflare llama-3.3-70b-fp8-fast has a small context window
MAX_TOKENS = 8192
BISECT_DEPTH = 3

# RULE 0D failover order (minus nvidia: no key). gemini re-added per user
# request — its free-tier per-minute quota resets quickly and the probe will
# drop it automatically if it's still exhausted.
BASE_ORDER = [
    "groq", "openrouter", "mistral", "cerebras", "github",
    "huggingface", "cloudflare", "siliconflow", "zhipu", "cohere", "gemini",
]
PER_CALL_TIMEOUT_S = 90


def _call_provider_timeout(p, user_message, timeout_s):
    """chat() with a hard wall-clock cap via a daemon thread (never blocks exit)."""
    holder = {}

    def _run():
        try:
            holder["r"] = p.chat(
                user_message,
                system_prompt=_EXTRACTION_SYSTEM,
                temperature=0,
                max_tokens=MAX_TOKENS,
            )
        except Exception as exc:
            holder["r"] = {"error": f"{type(exc).__name__}: {str(exc)[:140]}"}

    th = threading.Thread(target=_run, daemon=True)
    th.start()
    th.join(timeout_s)
    if th.is_alive():
        return {"error": f"TIMEOUT after {timeout_s}s (daemon abandoned)"}
    return holder.get("r") or {"error": "empty response"}


# --- Probe phase: rank providers by real latency, drop dead ones fast ---
def _probe():
    print("Probing providers (5s cap each)...", flush=True)
    ranked = []
    for name in BASE_ORDER:
        try:
            p = OpenAIProvider(name)
            if not p.has_valid_key():
                print(f"  {name}: no key", flush=True)
                continue
            t0 = time.time()
            r = _call_provider_timeout(p, "Reply with the single word: ok", 5)
            dt = time.time() - t0
            if "error" in r:
                print(f"  {name}: DEAD ({str(r['error'])[:60]})", flush=True)
                continue
            print(f"  {name}: live ({dt:.1f}s)", flush=True)
            ranked.append((dt, name))
        except Exception as exc:
            print(f"  {name}: ERR {type(exc).__name__}", flush=True)
    ranked.sort()
    order = [n for _, n in ranked]
    print(f"Provider order: {order}", flush=True)
    return order


PROVIDER_ORDER = _probe()

failover_log = []  # (chunk_tag, provider, error)
token_totals = {"input": 0, "output": 0}


def call_with_failover(user_message: str, chunk_tag: str):
    """Try each provider in RULE 0D order until one returns parseable JSON."""
    errors = []
    for name in PROVIDER_ORDER:
        try:
            p = OpenAIProvider(name)
            if not p.has_valid_key():
                errors.append(f"{name}: no key")
                continue
            resp = _call_provider_timeout(p, user_message, PER_CALL_TIMEOUT_S)
        except Exception as exc:  # transport-level failure
            errors.append(f"{name}: {type(exc).__name__}: {str(exc)[:120]}")
            continue
        if "error" in resp:
            errors.append(f"{name}: {str(resp['error'])[:160]}")
            failover_log.append((chunk_tag, name, str(resp["error"])[:160]))
            continue
        usage = resp.get("usage") or {}
        token_totals["input"] += int(usage.get("prompt_tokens") or 0)
        token_totals["output"] += int(usage.get("completion_tokens") or 0)
        content = resp.get("content") or ""
        finish = resp.get("finish_reason")
        parsed = _parse_llm_json(content)
        if parsed.get("nodes") or parsed.get("edges"):
            if finish == "length":
                print(f"    [{chunk_tag}] {name}: OK but TRUNCATED (finish=length) -> bisection", flush=True)
                return parsed, name, "length"
            return parsed, name, finish
        if len(content) > 4000:
            # Long unparseable output is almost always a mid-string cut -> bisect now
            print(f"    [{chunk_tag}] {name}: {len(content)} chars unparseable -> truncation bisection", flush=True)
            errors.append(f"{name}: truncated/unparseable ({len(content)} chars)")
            return None, errors, "length"
        errors.append(f"{name}: hollow response ({len(content)} chars)")
    # If everything failed with a context-window overflow, signal the caller to bisect
    joined = " ".join(errors)
    if "exceeded this model context window" in joined or "context_length_exceeded" in joined or "too many tokens" in joined.lower():
        return None, errors, "context_overflow"
    return None, errors, None


def process_chunk(files, chunk_tag, depth=0):
    """Extract one chunk with failover; bisect once on truncation."""
    user_message = _read_files(files, ROOT)
    parsed, who, finish = call_with_failover(user_message, chunk_tag)
    need_bisect = (
        (finish == "length" or (parsed is None and finish == "context_overflow"))
        and len(files) > 1 and depth < BISECT_DEPTH
    )
    if need_bisect:
        mid = len(files) // 2
        reason = "TRUNCATION" if finish == "length" else "CONTEXT OVERFLOW"
        print(f"    [{chunk_tag}] {reason} -> bisecting {len(files)} files", flush=True)
        merged = {"nodes": [], "edges": [], "hyperedges": []}
        for part in (files[:mid], files[mid:]):
            g = process_chunk(part, chunk_tag + "x", depth + 1)
            if g:
                merged["nodes"] += g.get("nodes", [])
                merged["edges"] += g.get("edges", [])
                merged["hyperedges"] += g.get("hyperedges", [])
        return merged
    if parsed is not None:
        fn = CHUNK_DIR / f"{AZ_PREFIX}{chunk_tag}.json"
        fn.write_text(json.dumps(parsed, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  [{chunk_tag}] saved via {who}: {len(parsed.get('nodes', []))} nodes, "
              f"{len(parsed.get('edges', []))} edges", flush=True)
        return parsed
    if finish == "context_overflow":
        print(f"  [{chunk_tag}] CONTEXT OVERFLOW unresolvable ({len(files)} file(s))", flush=True)
    print(f"  [{chunk_tag}] ALL PROVIDERS FAILED: {who}", flush=True)
    failover_log.append((chunk_tag, "ALL", "; ".join(who)[:400]))
    return None


detect = json.loads((OUT / ".graphify_detect.json").read_text(encoding="utf-8"))
all_files = [Path(f) for cat in ("document", "paper", "image") for f in detect["files"].get(cat, [])]
all_files = [f.resolve() for f in all_files]

# Resume: skip files already covered by any existing chunk (gemini-era + az)
done_sources = set()
for cf in CHUNK_DIR.glob("chunk_*.json"):
    try:
        d = json.loads(cf.read_text(encoding="utf-8"))
    except Exception:
        continue
    for n in d.get("nodes", []):
        if n.get("source_file"):
            done_sources.add(str(n["source_file"]))
    for e in d.get("edges", []):
        if e.get("source_file"):
            done_sources.add(str(e["source_file"]))
def _keys_for(f):
    """All plausible string keys a chunk might use for this file."""
    try:
        rel = str(f.relative_to(ROOT))
    except ValueError:
        rel = str(f)
    return {str(f), rel, f.name}

remaining = [f for f in all_files if not (_keys_for(f) & done_sources)]
print(f"Files total: {len(all_files)}, already extracted: {len(all_files) - len(remaining)}, remaining: {len(remaining)}", flush=True)

if remaining:
    chunks = _pack_chunks_by_tokens(remaining, TOKEN_BUDGET)
    print(f"Azazael failover extraction: {len(chunks)} chunks (budget {TOKEN_BUDGET} tokens each)", flush=True)
    t0 = time.time()
    for i, chunk in enumerate(chunks):
        tag = f"{i:03d}"
        names = ", ".join(f.name for f in chunk[:3])
        print(f"chunk {tag}: {len(chunk)} files [{names}...]", flush=True)
        process_chunk(chunk, tag)
        time.sleep(0.5)  # be gentle with free tiers
    print(f"Elapsed: {time.time()-t0:.0f}s", flush=True)

# ---- Merge ALL chunks (gemini-era chunk_*.json + az chunks) ----
merged_nodes, merged_edges, merged_hyper = [], [], []
seen = set()
for cf in sorted(CHUNK_DIR.glob("chunk_*.json")):
    try:
        d = json.loads(cf.read_text(encoding="utf-8"))
    except Exception:
        print(f"WARNING: unreadable chunk {cf.name}", flush=True)
        continue
    merged_nodes += d.get("nodes", [])
    merged_edges += d.get("edges", [])
    merged_hyper += d.get("hyperedges", [])
for n in merged_nodes:
    pass
deduped = []
for n in merged_nodes:
    if n.get("id") not in seen:
        seen.add(n.get("id"))
        deduped.append(n)
sem = {
    "nodes": deduped,
    "edges": merged_edges,
    "hyperedges": merged_hyper,
    "input_tokens": token_totals["input"],
    "output_tokens": token_totals["output"],
}
(OUT / ".graphify_semantic.json").write_text(json.dumps(sem, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"MERGED .graphify_semantic.json: {len(deduped)} nodes, {len(merged_edges)} edges, "
      f"{len(merged_hyper)} hyperedges; tokens in={token_totals['input']:,} out={token_totals['output']:,}", flush=True)
if failover_log:
    print(f"Failover events: {len(failover_log)}", flush=True)
    for tag, prov, err in failover_log[:10]:
        print(f"  {tag} | {prov} | {err[:100]}", flush=True)

# RULE 0D: record the session's provider health to DirectMemory
try:
    from CORE.direct_memory import record
    record("graphify_extraction_failover", {
        "corpus": "BCC_GRAPH_INPUT",
        "providers_tried": PROVIDER_ORDER,
        "failover_events": len(failover_log),
        "merged_nodes": len(deduped),
        "merged_edges": len(merged_edges),
        "tokens": token_totals,
    })
except Exception as exc:
    print(f"(DirectMemory record skipped: {type(exc).__name__}: {exc})", flush=True)
