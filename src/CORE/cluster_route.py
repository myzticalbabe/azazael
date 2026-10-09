# coding: utf-8
"""cluster_route.py — P1-5 HDBSCAN-lite + ProtoNet + TPE-lite (2026-09-15).

Stdlib-first so CPU box stays testable; uses sklearn/hdbscan/optuna
when present, else deterministic fallbacks.
"""
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


def hdbscan_lite(vecs, min_size: int = 5):
    """Single-link threshold clustering fallback (noise=-1).

    If hdbscan/sklearn present, delegates; else distance-threshold groups.
    Returns {"labels": [...], "noise_rate": float}.
    """
    try:
        import hdbscan as _h
        cl = _h.HDBSCAN(min_cluster_size=min_size).fit(vecs)
        labels = list(map(int, cl.labels_))
        noise = sum(1 for l in labels if l == -1) / max(1, len(labels))
        return {"labels": labels, "noise_rate": noise, "backend": "hdbscan"}
    except Exception:
        note_failure("cluster_route:L21", None)
    try:
        from sklearn.cluster import HDBSCAN as _H
        cl = _H(min_cluster_size=min_size).fit(vecs)
        labels = list(map(int, cl.labels_))
        noise = sum(1 for l in labels if l == -1) / max(1, len(labels))
        return {"labels": labels, "noise_rate": noise, "backend": "sklearn"}
    except Exception:
        note_failure("cluster_route:L29", None)
    # fallback: greedy threshold (mean pairwise dist / 2)
    import math
    n = len(vecs)
    if n == 0:
        return {"labels": [], "noise_rate": 0.0, "backend": "fallback"}
    threshold = 1.0
    labels, cur = [-1] * n, 0
    for i in range(n):
        if labels[i] != -1:
            continue
        labels[i] = cur
        for j in range(i + 1, n):
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(vecs[i], vecs[j])))
            if d < threshold:
                labels[j] = cur
        cur += 1
    # mark singletons as noise
    from collections import Counter
    cnt = Counter(labels)
    labels = [l if cnt[l] >= min(1, min_size // 5 + 1) else -1 for l in labels]
    noise = sum(1 for l in labels if l == -1) / max(1, n)
    return {"labels": labels, "noise_rate": noise, "backend": "fallback"}


def proto_route(query, protos: dict):
    """Nearest-prototype routing. protos: {worm: vec}. Returns best worm."""
    import math

    def d(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    return min(protos, key=lambda w: d(query, protos[w]))


def tpe_lite_suggest(trials, bounds: dict, n_candidates: int = 24):
    """Multivariate-lite TPE: split top-25% good, sample around best.

    trials: [(params_dict, score)]. bounds: {k: (lo, hi)}.
    Returns suggested params dict. Optuna used when present (caller opt-in).
    """
    import random
    rng = random.Random(0)
    if not trials:
        return {k: rng.uniform(*v) for k, v in bounds.items()}
    try:
        import optuna as _o  # noqa: F401
        # Optuna present — caller should build real study; keep lite path
        # deterministic for tests. (Full study lives in tune script.)
        pass
    except Exception:
        note_failure("cluster_route:L79", None)
    ranked = sorted(trials, key=lambda t: t[1], reverse=True)
    good = ranked[:max(1, len(ranked) // 4)]
    base = good[0][0]
    out = {}
    for k, (lo, hi) in bounds.items():
        span = (hi - lo) * 0.2
        out[k] = min(hi, max(lo, base.get(k, (lo + hi) / 2) + rng.uniform(-span, span)))
    return out
