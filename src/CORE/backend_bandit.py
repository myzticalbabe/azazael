# coding: utf-8
"""backend_bandit.py — Thompson routing over inference backends per model.

Arms: wrapper-cpu, wrapper-sycl, ollama. Seeded from bench_results.jsonl
tok/s; updated with measured rewards. The 9B tie and Eve-Ollama facts
live here as data, not doctrine.
"""
import json
import math
import random
from pathlib import Path

BACKENDS = ("cpu", "sycl", "ollama")
BENCH = Path(r"C:\Users\clint\AppData\Local\Temp\opencode\bench_results.jsonl")


class BackendBandit:
    VERSION = "1.0.0"

    def __init__(self, seed: float = 1.0):
        self._rng = random.Random(0)
        # (model, backend) -> [successes, failures, tok_sum, n]
        self._stats: dict[tuple, list] = {}
        self._seed = float(seed)
        self._hydrate_from_bench()

    def _hydrate_from_bench(self):
        """Seed priors from measured tok/s rows (backend-compare + GO rows)."""
        try:
            lines = BENCH.read_text().splitlines()
        except Exception:
            return
        for line in lines:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("type") == "backend-compare":
                m = r.get("model", "?")
                for b, k in (("sycl", "sycl_tps"), ("cpu", "cpu_tps")):
                    t = float(r.get(k) or 0)
                    if t > 0:
                        s = self._stats.setdefault((m, b), [0.0, 0.0, 0.0, 0])
                        s[0] += t  # pseudo-successs proportional to tok/s
                        s[2] += t
                        s[3] += 1
            elif r.get("status") == "GO" and r.get("tps"):
                key = (r.get("file", "?")[:30], "cpu")
                s = self._stats.setdefault(key, [0.0, 0.0, 0.0, 0])
                s[0] += float(r["tps"])
                s[2] += float(r["tps"])
                s[3] += 1
            elif r.get("status") == "GO-VIA-OLLAMA":
                key = (r.get("file", "?")[:30], "ollama")
                s = self._stats.setdefault(key, [0.0, 0.0, 0.0, 0])
                s[0] += 1.0
                s[3] += 1

    def pick(self, model: str, path: str = "") -> str:
        """Thompson draw over backends for this model (substring match).

        Census veto (Eve-class): if path fingerprints as unloadable
        natively, ollama is forced — no exploration draw against physics.
        """
        if path:
            try:
                from CORE.gguf_census import fingerprint
                fp = fingerprint(path)
                if fp.get("magic_ok") and fp.get("loadable") is False:
                    return "ollama"
            except Exception:
                pass
        cands = {}
        for (m, b), (s, f, _t, _n) in self._stats.items():
            if m in model or model in m:
                cands.setdefault(b, [0.0, 0.0])
                cands[b][0] += s + self._seed
                cands[b][1] += f + self._seed
        if not cands:
            return "cpu"  # doctrine default: CPU wins ties on this box
        draws = {b: self._rng.betavariate(max(1.0, s), max(1.0, f))
                 for b, (s, f) in cands.items()}
        # unseen backends get a small exploration draw
        for b in BACKENDS:
            draws.setdefault(b, self._rng.betavariate(1.0, 3.0))
        return max(draws, key=lambda b: draws[b])

    def update(self, model: str, backend: str, ok: bool, tps: float = 0.0):
        s = self._stats.setdefault((model[:30], backend), [0.0, 0.0, 0.0, 0])
        if ok:
            s[0] += 1.0 + min(5.0, tps / 10.0)
        else:
            s[1] += 1.0
        s[2] += tps
        s[3] += 1

    def table(self, model: str) -> dict:
        out = {}
        for (m, b), (s, f, t, n) in self._stats.items():
            if m in model or model in m:
                out[b] = {"w": round(s / (s + f + 1e-9), 3), "n": n,
                          "mean_tps": round(t / max(1, n), 2)}
        return out
