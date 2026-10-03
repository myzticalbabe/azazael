# coding: utf-8
"""
NEURAL MESH — Category: ENGRAM (4 worms)
Distributed memory coherence: Win, WSL2, G:.

VectorShardWorm, RecallRouterWorm, CoherenceValidatorWorm, DreamConsolidatorWorm

2026-09-14 audit fix (F1): this nature used to "shard embeddings" with
`sha256(mem_id) % len(ENVS)` and "recall" by dict lookup — no vectors, no
similarity, no index — while `CORE.embedding_backend` (real 768/1024/4096-dim
vectors, disk-cached, with a self-tuning dimension optimizer) and `faiss` +
`numpy` were installed and unused by the fabric.

Now:
- `VectorShardWorm` holds real vectors and a real ANN index, with a fail-open
  backend chain  faiss -> numpy brute force -> stdlib cosine. Placement stays
  deterministic (consistent hash of the id) so shard OWNERSHIP is stable
  across runs and envs, while RETRIEVAL is semantic.
- `RecallRouterWorm` routes a query to the shard owning the best semantic hit,
  and keeps the old id -> owner lookup as an explicit fast path.
- `CoherenceValidatorWorm` keeps the exact-hash fast path and adds cosine
  DRIFT detection, so near-duplicate replicas (the unicode-dash corruption
  class that hash equality cannot see) are classified instead of missed.

Everything stays fail-open: no embedder, no faiss and no numpy still works.
"""

import time
import threading
import hashlib
import math
from datetime import datetime
from typing import Any, Optional

try:
    from CORE.worm_registry import register_worm
except ImportError:
    def register_worm(**kw):
        return lambda cls: cls


def _h(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8', errors='replace')).hexdigest()[:16]


def _embed(text: str) -> list:
    """Semantic embedding via CORE.embedding_backend; [] when unavailable."""
    try:
        from CORE.embedding_backend import embed_text
        return list(embed_text(text) or [])
    except Exception:
        return []


def _cosine(a: list, b: list) -> float:
    """Cosine similarity; dimension-agnostic, 0.0 on empty/mismatched input."""
    try:
        from CORE.embedding_backend import cosine as _be_cosine
        return float(_be_cosine(a, b))
    except Exception:
        pass
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _l2_normalize(vec: list) -> list:
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else list(vec)


class _VectorIndex:
    """ANN index over L2-normalised embeddings with a fail-open backend chain.

    Backend selection is lazy and honest — `stats()` reports which one is in
    use, so an environment running the pure-stdlib fallback is visible rather
    than silently slower:

      faiss   — IndexFlatIP for small corpora (exact), IndexHNSWFlat above
                HNSW_THRESHOLD (approximate, still cosine via normalisation)
      numpy   — one normalised matrix, full inner-product scan
      stdlib  — per-vector cosine loop

    Vectors are expected to be semantically comparable; `add()` rejects a
    vector whose dimension disagrees with the index instead of corrupting it.
    """

    HNSW_THRESHOLD = 512

    def __init__(self):
        self._lock = threading.RLock()
        self._ids: list[str] = []
        self._vecs: list[list[float]] = []
        self._pos: dict[str, int] = {}
        self._dim = 0
        self._backend = "empty"
        self._dirty = True
        self._faiss = None
        self._np = None
        self._faiss_index = None
        self._matrix = None

    # ── writers ──────────────────────────────────────────────────────
    def add(self, mem_id: str, vec: list) -> dict:
        """Add or replace one vector. Returns {added, dim, backend}."""
        if not vec:
            return {"added": False, "reason": "empty_vector"}
        v = _l2_normalize([float(x) for x in vec])
        with self._lock:
            if self._dim and len(v) != self._dim:
                return {"added": False, "reason": "dim_mismatch",
                        "expected": self._dim, "got": len(v)}
            if not self._dim:
                self._dim = len(v)
            idx = self._pos.get(mem_id)
            if idx is None:
                self._pos[mem_id] = len(self._ids)
                self._ids.append(mem_id)
                self._vecs.append(v)
            else:
                self._vecs[idx] = v
            self._dirty = True
            return {"added": True, "dim": self._dim, "size": len(self._ids)}

    def __len__(self) -> int:
        with self._lock:
            return len(self._ids)

    # ── backend resolution ───────────────────────────────────────────
    def _ensure_backend(self) -> str:
        """Pick the best available backend once; never raises."""
        if self._backend != "empty" and not self._dirty:
            return self._backend
        # numpy (cheap, no native build needed)
        if self._np is None:
            try:
                import numpy as _n
                self._np = _n
            except Exception:
                self._np = False
        # faiss (preferred when present) -- but its wheel on this host is
        # GIL-ABI: importing it under a free-threaded build faults at C level
        # (an access violation, not an ImportError), which no try/except can
        # catch. So decide by the RUNTIME, not by the import -- the docstring's
        # "fail-open" promise is only true if the fault is never attempted.
        if self._faiss is None:
            try:
                from CORE.native_guard import import_ok as _import_ok

                _ok = _import_ok("faiss")
            except Exception:
                _ok = False
            if _ok:
                try:
                    import faiss as _f

                    self._faiss = _f
                except Exception:
                    self._faiss = False
            else:
                self._faiss = False
        if self._faiss:
            self._backend = "faiss"
        elif self._np:
            self._backend = "numpy"
        else:
            self._backend = "stdlib"
        self._rebuild()
        return self._backend

    def _rebuild(self) -> None:
        """Rebuild the materialised index from the raw vector list."""
        with self._lock:
            if not self._dirty:
                return
            n = len(self._ids)
            if self._backend == "faiss" and n:
                try:
                    d = self._dim
                    if n > self.HNSW_THRESHOLD:
                        idx = self._faiss.IndexHNSWFlat(d, 32)
                    else:
                        idx = self._faiss.IndexFlatIP(d)
                    mat = self._np.asarray(self._vecs, dtype="float32")
                    idx.add(mat)
                    self._faiss_index = idx
                    self._matrix = None
                    self._dirty = False
                    return
                except Exception:
                    self._backend = "numpy" if self._np else "stdlib"
            if self._backend == "numpy" and n:
                try:
                    self._matrix = self._np.asarray(self._vecs, dtype="float64")
                    self._faiss_index = None
                    self._dirty = False
                    return
                except Exception:
                    self._backend = "stdlib"
            self._faiss_index = None
            self._matrix = None
            self._dirty = False

    # ── readers ──────────────────────────────────────────────────────
    def search(self, vec: list, top_k: int = 5) -> list:
        """Top-k semantic hits as [(mem_id, score), ...] (score = cosine)."""
        if not vec:
            return []
        with self._lock:
            if not self._ids:
                return []
            backend = self._ensure_backend()
            q = _l2_normalize([float(x) for x in vec])
            if len(q) != self._dim:
                return []
            k = max(1, min(int(top_k), len(self._ids)))
            if backend == "faiss" and self._faiss_index is not None:
                qm = self._np.asarray([q], dtype="float32")
                scores, idxs = self._faiss_index.search(qm, k)
                return [(self._ids[int(i)], float(s))
                        for s, i in zip(scores[0], idxs[0]) if int(i) >= 0]
            if backend == "numpy" and self._matrix is not None:
                sims = self._matrix @ self._np.asarray(q, dtype="float64")
                order = self._np.argsort(-sims)[:k]
                return [(self._ids[int(i)], float(sims[int(i)])) for i in order]
            scored = [(self._ids[i], _cosine(q, self._vecs[i]))
                      for i in range(len(self._ids))]
            scored.sort(key=lambda t: -t[1])
            return scored[:k]

    def vector(self, mem_id: str) -> list:
        with self._lock:
            i = self._pos.get(mem_id)
            return list(self._vecs[i]) if i is not None else []

    def has(self, mem_id: str) -> bool:
        with self._lock:
            return mem_id in self._pos

    def stats(self) -> dict:
        with self._lock:
            backend = self._backend
            if backend == "empty" and self._ids:
                backend = "pending"  # added but not yet materialised
            return {"size": len(self._ids), "dim": self._dim,
                    "backend": backend,
                    "faiss": bool(self._faiss),
                    "numpy": bool(self._np)}


@register_worm(category="engram", priority=7, cooldown_seconds=60.0,
    description="Semantic shard store: real embeddings + ANN index; shard map on G:")
class VectorShardWorm:
    """Vector store with deterministic shard ownership and semantic search.

    Shard PLACEMENT (which env owns a memory) stays a stable hash of the id,
    because ownership must not move when the corpus grows. RETRIEVAL is now a
    real nearest-neighbour search over embeddings, not a dict lookup.
    """

    VERSION = "2.0.0"
    ENVS = ("windows", "wsl2", "g_archive")

    def __init__(self, shards: int = 3, top_k: int = 5):
        self._shards = max(1, int(shards))
        self._top_k = max(1, int(top_k))
        self._map: dict[str, str] = {}
        self._counts: dict[str, int] = {e: 0 for e in self.ENVS}
        self._index = _VectorIndex()
        self._lock = threading.Lock()

    def shard_for(self, mem_id: str) -> str:
        """Deterministic shard owner for an id (placement, not retrieval)."""
        idx = int(_h(mem_id), 16) % len(self.ENVS)
        env = self.ENVS[idx]
        with self._lock:
            self._map[mem_id] = env
            self._counts[env] += 1
        return env

    def add(self, mem_id: str, text: Optional[str] = None,
            vec: Optional[list] = None) -> dict:
        """Store a memory: embed `text` (or take `vec`) and index it."""
        v = list(vec) if vec else (_embed(text) if text else [])
        shard = self.shard_for(mem_id)
        res = self._index.add(mem_id, v) if v else {"added": False,
                                                   "reason": "no_vector"}
        return {"success": True, "mem": mem_id, "shard": shard,
                "dim": len(v), **res}

    def search(self, query: str = "", vec: Optional[list] = None,
               top_k: Optional[int] = None) -> dict:
        """Semantic search; each hit reports its owning shard."""
        q = list(vec) if vec else (_embed(query) if query else [])
        if not q:
            return {"success": True, "hits": [], "backend": "unavailable",
                    "reason": "no_query_vector"}
        hits = self._index.search(q, top_k or self._top_k)
        out = []
        with self._lock:
            for mem_id, score in hits:
                out.append({"mem": mem_id, "score": round(score, 4),
                            "shard": self._map.get(mem_id, "unknown")})
        return {"success": True, "hits": out,
                "backend": self._index.stats()["backend"],
                "indexed": len(self._index)}

    def stats(self) -> dict:
        with self._lock:
            return {"mapped": len(self._map), "counts": dict(self._counts),
                    "shards": self._shards, "index": self._index.stats()}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.stats()}


_SHARED_SHARDS: Optional[VectorShardWorm] = None
_SHARED_LOCK = threading.Lock()


def shared_shards() -> VectorShardWorm:
    """Process-wide default shard store used by router/validator/consolidator.

    One store per process so a memory added by any organ is findable by any
    other. Callers that need isolation pass an explicit instance instead.
    """
    global _SHARED_SHARDS
    if _SHARED_SHARDS is None:
        with _SHARED_LOCK:
            if _SHARED_SHARDS is None:
                _SHARED_SHARDS = VectorShardWorm()
    return _SHARED_SHARDS


@register_worm(category="engram", priority=8, cooldown_seconds=15.0,
    description="Routes recall to the shard owning the best semantic hit; fallback to G: archive")
class RecallRouterWorm:
    """Shard-aware recall: semantic search first, id lookup as a fast path.

    `route_recall(query, shard_map={...})` keeps the original contract — if the
    query is a known id in `shard_map`, the owner is returned directly with no
    embedding call. Otherwise the query text is embedded and the shard owning
    the best hit is chosen; a miss falls back to `g_archive`.
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._hits: dict[str, int] = {"owner": 0, "semantic": 0, "fallback": 0}
        self._last_scores: list = []
        self._lock = threading.Lock()

    def route_recall(self, query: str, shard_map: Optional[dict] = None,
                     index: Optional[VectorShardWorm] = None,
                     top_k: int = 5) -> dict[str, Any]:
        # Fast path: an exact id with a known owner needs no embedding.
        owner = (shard_map or {}).get(query)
        if owner:
            with self._lock:
                self._hits["owner"] += 1
            return {"success": True, "mem": query, "route": owner,
                    "fallback": False, "mode": "owner_lookup"}

        store = index or shared_shards()
        res = store.search(query=query, top_k=top_k) if query else {"hits": []}
        hits = res.get("hits") or []
        if hits:
            best = hits[0]
            with self._lock:
                self._hits["semantic"] += 1
                self._last_scores = [h["score"] for h in hits]
            return {"success": True, "mem": query, "route": best["shard"],
                    "fallback": False, "mode": "semantic",
                    "score": best["score"],
                    "hits": hits}

        with self._lock:
            self._hits["fallback"] += 1
        return {"success": True, "mem": query, "route": "g_archive",
                "fallback": True, "mode": "fallback"}

    def stats(self) -> dict:
        with self._lock:
            total = sum(self._hits.values())
            return {**self._hits, "total": total,
                    "last_scores": self._last_scores[:5]}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.stats()}


@register_worm(category="engram", priority=6, cooldown_seconds=120.0,
    description="Replica coherence: exact hash equality + cosine drift detection")
class CoherenceValidatorWorm:
    """Detects both outright mismatch and near-duplicate drift between replicas.

    G-F1: hash-set equality alone cannot see the corruption class this mesh
    actually suffers (unicode-dash rewrites, whitespace normalisation) because
    any byte change produces a different hash. When replica *texts* are
    available the validator adds a pairwise cosine floor: replicas at or above
    `threshold` are reported `near_duplicate` (drift inside tolerance), below
    it `divergent`.
    """

    VERSION = "2.0.0"
    DEFAULT_DRIFT_THRESHOLD = 0.995

    def __init__(self, drift_threshold: float = DEFAULT_DRIFT_THRESHOLD):
        self._checked = 0
        self._mismatched: list = []
        self._drifting: list = []
        self._threshold = float(drift_threshold)
        self._lock = threading.Lock()

    def check(self, mem_id: str, replica_hashes: list,
              replica_texts: Optional[list] = None,
              threshold: Optional[float] = None) -> dict[str, Any]:
        thr = self._threshold if threshold is None else float(threshold)
        exact = len(set(replica_hashes)) <= 1
        mode = "exact"
        min_sim = None
        coherent = exact

        if not exact and replica_texts and len(replica_texts) >= 2:
            vecs = [_embed(str(t)) for t in replica_texts[:8]]
            vecs = [v for v in vecs if v]
            if len(vecs) >= 2:
                sims = [_cosine(vecs[0], v) for v in vecs[1:]]
                min_sim = round(min(sims), 4)
                mode = "drift"
                coherent = min_sim >= thr
        elif not exact:
            mode = "hash"

        with self._lock:
            self._checked += 1
            if not exact:
                self._mismatched.append(mem_id)
                if mode == "drift" and coherent:
                    self._drifting.append(mem_id)
        return {"success": True, "mem": mem_id, "coherent": coherent,
                "replicas": len(replica_hashes), "mode": mode,
                "min_similarity": min_sim, "threshold": thr,
                "checked": self._checked}

    def report(self) -> dict:
        with self._lock:
            return {"checked": self._checked,
                    "mismatched": len(self._mismatched),
                    "near_duplicate_drift": len(self._drifting),
                    "divergent": len(self._mismatched) - len(self._drifting),
                    "threshold": self._threshold,
                    "sample": self._mismatched[-5:]}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.report()}


@register_worm(category="engram", priority=5, cooldown_seconds=300.0,
    description="Nightly merge DreamingModule/Hypnagogic output into ModelVersioner + engram index")
class DreamConsolidatorWorm:
    """Dream -> long-term memory consolidation.

    Kept dreams are not just counted: those carrying `text` are embedded and
    indexed into the engram store, so an offline insight becomes recallable
    rather than evaporating when the cycle ends.
    """

    VERSION = "2.0.0"
    SALIENCE_FLOOR = 0.5

    def __init__(self):
        self._merges = 0
        self._last: str | None = None
        self._indexed = 0
        self._lock = threading.Lock()

    def consolidate(self, dream_items: list[dict],
                    index: Optional[VectorShardWorm] = None) -> dict[str, Any]:
        kept = [d for d in dream_items if d.get("salience", 0) >= self.SALIENCE_FLOOR]
        store = index or shared_shards()
        indexed = 0
        for i, d in enumerate(kept):
            text = d.get("text") or d.get("summary") or ""
            if not text:
                continue
            try:
                mem_id = d.get("id") or f"dream:{_h(text)}:{i}"
                if store.add(mem_id, text=text).get("added"):
                    indexed += 1
            except Exception:
                continue
        with self._lock:
            self._merges += 1
            self._indexed += indexed
            self._last = datetime.now().isoformat()
            return {"success": True, "input": len(dream_items),
                    "kept": len(kept), "indexed": indexed,
                    "merges": self._merges, "total_indexed": self._indexed,
                    "at": self._last}

    def stats(self) -> dict:
        with self._lock:
            return {"merges": self._merges, "last": self._last,
                    "total_indexed": self._indexed}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.stats()}
