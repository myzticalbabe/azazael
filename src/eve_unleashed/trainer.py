"""`eve train`: the developed instrument for test/evolve population cycling.

Ports the proven /tmp harness (gens 1-4: best 0.6793 -> 0.7316, dream
0.375 -> 0.448) into the repo with one addition: the trainer tunes ITSELF.

LILLITH IS THE TUNER. `LillithTuner` watches the best-fitness trajectory and
widens mutation when the lineage stalls, narrows it while it climbs. Her
every decision is logged to the live log as a `tuner` event (width, reason,
history window) so the tuning itself is graded by numbers, never by prose.

Boundary (RULE: who grades the grader): Lillith may tune trainer PARAMETERS
(mutation width). She may not rewrite trainer code or the fitness definition.
Those stay human.
"""

from __future__ import annotations

import json
import os
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .self_modifying_worms import GeneticAlgorithm, WormDNA, WormFitness

DEFAULT_URLS = [
    "https://example.com",
    "https://www.python.org",
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://httpbin.org/status/404",
    "http://unseen-train.invalid/",
    "https://www.ietf.org/rfc/rfc2616.txt",
]
DEFAULT_LOG = "C:/tmp/eve-train.jsonl"
DEFAULT_POP = "C:/tmp/eve-pop.json"
DEFAULT_CAP_S = 40.0  # training-harness bound; the product ladder is untouched


@dataclass
class TrainConfig:
    """Everything `eve train` needs, with the proven defaults baked in."""

    gens: int = 1
    pop: int = 4
    seed: int = 316
    fresh: bool = False
    urls: List[str] = field(default_factory=lambda: list(DEFAULT_URLS))
    log_path: str = DEFAULT_LOG
    pop_path: str = DEFAULT_POP
    cap_s: float = DEFAULT_CAP_S


class LillithTuner:
    """The tuner. Watches best-fitness; tunes mutation width; logs every call.

    Rule (pure, tested):
      - fewer than 3 points     -> hold (not enough evidence)
      - last-3 window flat      -> widen  x1.5 (stall: force exploration)
      - last point climbs       -> narrow x0.8 (climb: protect the lineage)
      - otherwise               -> hold
    Width is clamped to [0.01, 0.5], the same bounds WormDNA enforces.
    """

    STALL_EPS = 1e-3
    WIDEN = 1.5
    NARROW = 0.8
    MIN_W = 0.01
    MAX_W = 0.5

    def __init__(self, width: float = 0.15, window: int = 3) -> None:
        self.width = max(self.MIN_W, min(self.MAX_W, width))
        self.window = max(2, window)
        self.history: List[float] = []

    def observe(self, best: float) -> Dict[str, Any]:
        """Feed one generation's best fitness; returns the tuning decision."""
        self.history.append(float(best))
        w = self.width
        reason = "hold: warming up"
        pts = self.history[-self.window:]
        if len(pts) >= self.window:
            span = max(pts) - min(pts)
            if span < self.STALL_EPS:
                w = min(self.MAX_W, w * self.WIDEN)
                reason = f"stall: span {span:.5f} < eps, widen to {w:.3f}"
            elif pts[-1] > pts[0]:
                w = max(self.MIN_W, w * self.NARROW)
                reason = f"climb: {pts[0]:.4f} -> {pts[-1]:.4f}, narrow to {w:.3f}"
            else:
                reason = f"hold: span {span:.4f}, no climb"
        self.width = w
        return {"width": w, "reason": reason,
                "history": list(self.history[-self.window:])}

    def apply(self, ga: GeneticAlgorithm) -> None:
        """Set the whole population's mutation rate to the tuned width."""
        for d in ga.population:
            d.mutation_rate = max(self.MIN_W, min(self.MAX_W, self.width))


def _capped(fn: Callable, cap_s: float, *a):
    box: Dict[str, Any] = {}
    t = threading.Thread(target=lambda: box.update(r=fn(*a)), daemon=True)
    t.start()
    t.join(timeout=cap_s)
    if "r" in box:
        return box["r"]
    return {"state": "blocked", "rung": "train-cap",
            "kind": "per-fetch cap %ss" % cap_s}


def _memory_rungs(url: str) -> Dict[str, Any]:
    from . import websearch as _w
    body, _snap, aerr = _w._archive_fallback(url)
    if not aerr:
        return {"state": "ok", "rung": "archive", "text": body[:20000]}
    cbody, _cid, cerr = _w._commoncrawl_fetch(url)
    if not cerr:
        return {"state": "ok", "rung": "commoncrawl",
                "text": (cbody or "")[:20000]}
    return {"state": "blocked", "rung": "commoncrawl", "detail": "wall held"}


def run_url(dna: WormDNA, url: str, log_path: str,
            cap_s: float = DEFAULT_CAP_S):
    """One scored fetch: intuition guesses, policy decides live-vs-memory."""
    from . import intuition as _i
    from . import live_log as _l
    from . import websearch as _w
    g = _i.intuit(url, log_path=log_path)
    _l.emit("fetch", "intuition", path=log_path, url=url,
            guess=g["state"], confidence=g["confidence"],
            predicted=g.get("predicted_rung"))
    skip_live = (g["state"] == "blocked"
                 and g["confidence"] >= dna.min_confidence
                 and dna.aggressiveness < 0.5)
    t0 = time.perf_counter()
    res = (_capped(_memory_rungs, cap_s, url) if skip_live
           else _capped(_w.fetch_visible, cap_s, url))
    if res["state"] != "ok" and dna.aggressiveness >= 0.75 and not skip_live:
        res = _capped(_w.fetch_visible, cap_s, url)
    dt = time.perf_counter() - t0
    _l.emit("fetch", "answer", path=log_path, url=url, rung=res.get("rung"),
            state=res["state"], kind=res.get("kind"))
    actual_ok = res["state"] == "ok"
    hit = ((g["state"] == "guess" and actual_ok)
           or (g["state"] == "blocked" and not actual_ok))
    return actual_ok, hit, dt


def save_pop(ga: GeneticAlgorithm, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"generation": ga.generation,
                   "genomes": [d.to_dict() for d in ga.population]}, fh)


def load_pop(ga: GeneticAlgorithm, path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        saved = json.load(fh)
    if isinstance(saved, dict):  # current format: generation + genomes
        ga.seed([WormDNA.from_dict(d) for d in saved["genomes"]])
        ga.generation = int(saved.get("generation", 1))
    else:  # legacy: bare genome list, generation unknown
        ga.seed([WormDNA.from_dict(d) for d in saved])


def load_or_seed(ga: GeneticAlgorithm, cfg: TrainConfig,
                 rng: random.Random) -> int:
    """Seed a fresh population or resume from the pop file. Returns start gen."""
    if not cfg.fresh and os.path.exists(cfg.pop_path):
        load_pop(ga, cfg.pop_path)
        return ga.generation
    ga.seed([WormDNA(worm_id=f"t1-{i}", worm_type="fetcher",
                     aggressiveness=rng.uniform(0.1, 0.9),
                     min_confidence=rng.uniform(0.5, 0.95),
                     cooldown_s=rng.uniform(0.1, 3.0),
                     mutation_rate=0.15)
             for i in range(ga.population_size)])
    return 1


def one_generation(ga: GeneticAlgorithm, gnum: int, cfg: TrainConfig,
                   tuner: LillithTuner) -> Dict[str, Any]:
    """Score every genome live, tune, evolve. Returns the gen summary."""
    from . import intuition as _i
    from . import live_log as _l
    for d in ga.population:
        ok = hits = wall = 0.0
        for u in cfg.urls:
            o, h, dt = run_url(d, u, cfg.log_path, cfg.cap_s)
            ok += o
            hits += h
            wall += dt
            time.sleep(min(d.cooldown_s, 1.0))
        n = len(cfg.urls)
        ga.record_fitness(WormFitness(
            worm_id=d.worm_id, worm_type=d.worm_type, generation=d.generation,
            resource_usage=min(1.0, wall / (n * 2 * 12.0)),
            insight_quality=hits / n, error_rate=(n - ok) / n,
            uptime_s=wall, actions_taken=n, actions_succeeded=int(ok)))
    scores = {d.worm_id: ga.fitness[d.worm_id].score() for d in ga.population}
    best = max(ga.population, key=lambda d: scores[d.worm_id])
    dr = _i.dream(log_path=cfg.log_path)
    decision = tuner.observe(scores[best.worm_id])
    _l.emit("tuner", "lillith", path=cfg.log_path, gen=gnum,
            width=decision["width"], reason=decision["reason"],
            best=round(scores[best.worm_id], 4))
    summary = {"gen": gnum, "best": round(scores[best.worm_id], 4),
               "mean": round(sum(scores.values()) / len(scores), 4),
               "dream_pairs": dr["pairs"],
               "dream_hit": round(dr["hit_rate"], 3),
               "best_id": best.worm_id[:8],
               "aggr": round(best.aggressiveness, 2),
               "conf": round(best.min_confidence, 2),
               "mutw": round(decision["width"], 3),
               "tune": decision["reason"]}
    print("gen {gen}: best={best:.4f} mean={mean:.4f} "
          "dream_pairs={dream_pairs} dream_hit={dream_hit:.3f} "
          "best={best_id} aggr={aggr:.2f} conf={conf:.2f} "
          "mutw={mutw:.3f} [{tune}]".format(**summary), flush=True)
    ga.evolve()
    tuner.apply(ga)
    return summary


def run(cfg: TrainConfig) -> List[Dict[str, Any]]:
    """Test/evolve cycling: live-score, tune, breed, repeat. Returns summaries."""
    rng = random.Random(cfg.seed)
    ga = GeneticAlgorithm(population_size=cfg.pop, elite_keep=2, rng=rng)
    if cfg.fresh and os.path.exists(cfg.pop_path):
        os.remove(cfg.pop_path)
    start = load_or_seed(ga, cfg, rng)
    tuner = LillithTuner()
    out = []
    for g in range(start, start + cfg.gens):
        out.append(one_generation(ga, g, cfg, tuner))
    save_pop(ga, cfg.pop_path)
    print("DONE gens %d-%d final_gen=%d pop_saved=%s tuner=lillith mutw=%.3f"
          % (start, start + cfg.gens - 1, ga.generation,
             cfg.pop_path, tuner.width), flush=True)
    return out
