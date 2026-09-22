#!/usr/bin/env python3
"""Closed-loop evolution: route-preference genomes, LIVE probe fitness.

EvolutionEngine.evolve() is single-step with no fitness of its own — prior
runs either errored (no init) or spun empty generations. This closes it:
each generation is scored by real measurements, best genome persisted.
"""
import json
import subprocess
import sys
import time

from log_hygiene import quiet_noisy_loggers

quiet_noisy_loggers()
sys.path.insert(0, "C:/Users/clint/azazael/src")

ENVS = ["wsl2-ubuntu", "wsl2-kali", "g_archive", "windows"]
DISTRO = {"wsl2-ubuntu": "Ubuntu-26.04", "wsl2-kali": "kali-linux"}


def probe(env):
    t0 = time.perf_counter()
    try:
        if env in DISTRO:
            ok = subprocess.run(["wsl", "-d", DISTRO[env], "--", "echo", "ok"],
                                capture_output=True, timeout=45).returncode == 0
        elif env == "g_archive":
            open("G:/source-of-truth/azazael_models/probe.tmp", "w").write("x" * 4096)
            import os
            os.remove("G:/source-of-truth/azazael_models/probe.tmp")
            ok = True
        else:
            import socket
            socket.gethostbyname("localhost")
            ok = True
    except Exception:
        ok = False
    return ok, (time.perf_counter() - t0) * 1000.0


def fitness_fn(genome):
    """Lower latency on preferred envs + success = higher fitness."""
    genes = genome.genes if hasattr(genome, "genes") else genome
    score, det = 0.0, {}
    tot = sum(max(0.01, float(genes.get("w_" + e.replace("-", "_"), 1.0))) for e in ENVS)
    for env in ENVS:
        ok, ms = probe(env)
        # normalize: genome expresses RELATIVE preference (sums to 1), so
        # evolution must discriminate between envs, not max all weights.
        w = max(0.01, float(genes.get("w_" + env.replace("-", "_"), 1.0))) / tot
        det[env] = {"ok": ok, "ms": round(ms, 1)}
        score += (1.0 if ok else -2.0) * w - min(2.0, ms / 1000.0) * 0.1
    return round(score, 3)


def main(gens=6, pop=10):
    from CORE.WORMS.expansion.evolution import EvolutionEngine
    from CORE import spine_registry as sp
    e = EvolutionEngine(population_size=pop, early_stop_patience=99)
    e.set_gene_specs({f"w_{env.replace('-', '_')}": {"lo": 0.1, "hi": 5.0}
                      for env in ENVS})
    e.initialize_population()
    for g in range(gens):
        ev = e.evaluate_population(fitness_fn, use_curative=False, workers=1)
        r = e.evolve()
        print(f"gen {r.get('generation')}: {json.dumps(ev)[:200]}", flush=True)
    best = e.get_best_genome()
    if hasattr(best, "genes"):
        best = {"genes": best.genes, "fitness": getattr(best, "fitness", None),
                "generation": getattr(best, "generation", None),
                "id": getattr(best, "id", None)}
    doc = {"best": best, "at": __import__("datetime").datetime.now().isoformat()}
    open("G:/source-of-truth/azazael_models/evo_best.json", "w").write(json.dumps(doc, indent=1))
    try:
        sp.record_outcome("learning", "EvolutionEngine", True, 0.0)
        sp.save_spine_state()
    except Exception:
        pass
    print("best saved")


if __name__ == "__main__":
    main()
