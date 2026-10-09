# coding: utf-8
"""dream_arena.py — dreams-to-arena compiler: kept dreams become test worlds.

Closes the loop the DreamCritic leaves open: coherent synthetic texts are
compiled into Arena Environment descriptors (severity mix from dream
affect-tags, hardness from dream complexity), admitted to the archive iff
novel, and scheduled as the next generation's exams.
"""
import hashlib
import math
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


def compile_world(dream: dict) -> dict:
    """dream: {text, tags:[...], complexity(0..1)} -> Environment config."""
    text = str(dream.get("text", ""))
    tags = list(dream.get("tags") or [])
    cx = max(0.0, min(1.0, float(dream.get("complexity", 0.5))))
    toks = text.split()
    # severity mix from affect tags; hardness from complexity + length
    neg = sum(1 for t in tags if t in ("threat", "harm", "fail", "risk"))
    pos = sum(1 for t in tags if t in ("heal", "fix", "pass", "ok"))
    tot = max(1, neg + pos)
    hard = round(max(0.05, min(0.95, 0.3 + 0.5 * cx + 0.2 * (neg / tot))), 3)
    fp = hashlib.md5(text.encode("utf-8", "replace").replace(b" ", b"")).hexdigest()[:12]
    return {"severity_mix": [round(pos / tot, 3), 0.2, round(neg / tot, 3)],
            "hard_ratio": hard,
            "era_pressure": round(0.5 + 0.5 * cx, 3),
            "n_alerts": max(10, min(1000, len(toks))),
            "fingerprint": fp,
            "source": "dream"}


def admit_worlds(arena, dreams: list[dict], genome=None) -> dict:
    """Compile dreams, populate arena with novel solvable ones.

    Returns {compiled, admitted, skipped}. Never raises.
    """
    compiled, admitted, skipped = 0, 0, 0
    try:
        from CORE.WORMS.expansion.arena import Environment
    except Exception:
        note_failure("dream_arena:L41", None)
        return {"compiled": 0, "admitted": 0, "skipped": len(dreams),
                "error": "arena-unavailable"}
    for d in dreams:
        try:
            cfg = compile_world(d)
            compiled += 1
            env = Environment(cfg["severity_mix"], cfg["hard_ratio"],
                              cfg["era_pressure"], cfg["n_alerts"],
                              seed=int(cfg["fingerprint"][:8], 16))
            if genome is None:
                skipped += 1
                continue
            got = arena.populate(env, genome, n=1)
            if got:
                admitted += 1
            else:
                skipped += 1
        except Exception:
            note_failure("dream_arena:L59", None)
            skipped += 1
    return {"compiled": compiled, "admitted": admitted, "skipped": skipped}
