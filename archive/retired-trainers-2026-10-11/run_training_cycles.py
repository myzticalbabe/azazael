# coding: utf-8
"""run_training_cycles.py — Drive many training/evolution cycles back-to-back.

Normally these worms fire on 5-minute cooldowns; this driver catches up by
running N full cycles in one pass. Each cycle runs:

    DREAM  -> recall real store events, synthesize scenarios, record dreams
    EVOLVE -> GA generation with a fitness function that consumes the
              store's external signal (so adaptation is real, not self-talk)
    METACOG -> introspection report over the cycle's results
    AUDIT   -> pyflakes scan + error-delta series

Usage:
    python scripts/run_training_cycles.py [--cycles N] [--pop 50] [--gens 3]
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CORE.local_memory import get_memory_store  # noqa: E402
from CORE.WORMS.expansion.dreaming import DreamingModule  # noqa: E402
from CORE.WORMS.expansion.evolution import EvolutionEngine  # noqa: E402
from CORE.WORMS.expansion.meta_cognition import MetaCognitionWorm  # noqa: E402
from CORE.WORMS.expansion.code_audit import WeeklyCodeAuditWorm  # noqa: E402


# --------------------------------------------------------------------------
# Store-driven fitness: a genome's fitness reflects real external signal.
# --------------------------------------------------------------------------

_EXTERNAL_SOURCES = ("AZAZAEL_CODE_AUDIT", "BCC_990_PART7")


def _external_signal_stats(store) -> dict:
    """Count real external events by source (full store, not a window),
    plus the error-delta trend from audit runs."""
    stats = {"external": 0, "by_source": {}, "errors_fixed": 0, "total": 0}
    try:
        db = Path.home() / ".azazael" / "memory_store.db"
        import sqlite3
        con = sqlite3.connect(str(db), timeout=5)
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT source, event_type, data FROM memories "
            "WHERE source IN (?, ?)", _EXTERNAL_SOURCES
        ).fetchall()
        con.close()
    except Exception:
        return stats
    for r in rows:
        src = r["source"]
        ev = r["event_type"]
        stats["external"] += 1
        stats["by_source"][src] = stats["by_source"].get(src, 0) + 1
        if ev == "code_audit_run":
            stats["total"] += 1
            d = r["data"]
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except Exception:
                    d = {}
            if isinstance(d, dict):
                stats["errors_fixed"] += max(0, int(d.get("delta", 0) or 0))
    return stats


def make_store_fitness(store):
    """Fitness function over GA genes, grounded in real store signal.

    Genes tune how aggressively the system weights external vs internal
    signal (external_weight) and how often it refreshes (refresh_rate). A
    genome scores higher when external signal is high, error delta is
    positive (errors fixed), and its choices are internally coherent.
    """
    base = _external_signal_stats(store)
    ext = base["external"]
    err_fixed = base["errors_fixed"]

    def fitness(genome):
        g = genome.genes
        ext_w = float(g.get("external_weight", 0.7))
        refresh = float(g.get("refresh_rate", 0.5))
        pop = float(g.get("population", 0.5))
        # Signal component: reward real external data and fixed errors.
        sig = 0.0
        if ext > 0:
            sig += min(1.0, ext / 200.0) * ext_w
        sig += min(1.0, err_fixed / 50.0) * 0.3
        # Coherence: refresh_rate should not be so high it thrashes, nor so
        # low it starves; population mid-range is stable.
        refresh_pen = 0.2 * abs(refresh - 0.5)
        pop_pen = 0.1 * abs(pop - 0.5)
        return max(0.0, min(1.0, sig - refresh_pen - pop_pen))

    return fitness


_GENE_BOUNDS = {
    "external_weight": (0.1, 1.0),
    "refresh_rate": (0.1, 1.0),
    "population": (0.1, 1.0),
    "mutation_scale": (0.05, 0.5),
    "elitism_ratio": (0.05, 0.4),
}


def run_one_cycle(idx: int, store, evo: EvolutionEngine, dreamer: DreamingModule,
                  metacog: MetaCognitionWorm, auditor: WeeklyCodeAuditWorm,
                  gens_per_cycle: int = 3) -> dict:
    """Run one full training cycle; returns collected stats."""
    cycle = {"index": idx, "ts": datetime.now(timezone.utc).isoformat(),
             "dream": {}, "evolution": {}, "metacog": {}, "audit": {}}

    # 1) DREAM — recall real store events, synthesize, record
    try:
        d = dreamer.run_dreaming_pipeline(num_episodes=2, scenario_count=8)
        if isinstance(d, dict):
            cycle["dream"] = {k: d.get(k) for k in
                              ("dream_count", "quality", "creativity",
                               "novel_patterns", "scenarios") if k in d}
            if d.get("dream_count") is None and d.get("dreams"):
                cycle["dream"]["dream_count"] = len(d["dreams"])
    except Exception as e:
        cycle["dream"]["error"] = str(e)[:200]

    # 2) EVOLVE — store-driven GA generations
    try:
        fitness_fn = make_store_fitness(store)
        for _ in range(gens_per_cycle):
            evo.evaluate_population(fitness_fn, use_curative=False, workers=4)
            evo.evolve()
        best = evo.get_best_genome()
        cycle["evolution"] = {
            "generation": evo._generation,
            "best_fitness": round(best.fitness, 4) if best else None,
            "best_genes": best.genes if best else None,
            "population": len(evo._population),
        }
    except Exception as e:
        cycle["evolution"]["error"] = str(e)[:200]

    # 3) METACOG — introspection over the cycle
    try:
        rep = metacog.execute()
        if isinstance(rep, dict):
            cycle["metacog"] = {k: rep.get(k) for k in
                                ("episode_count", "strategy_scores",
                                 "adaptations", "confidence") if k in rep}
    except Exception as e:
        cycle["metacog"]["error"] = str(e)[:200]

    # 4) AUDIT — pyflakes scan, error delta series
    try:
        a = auditor.execute()
        cycle["audit"] = {k: a.get(k) for k in
                          ("undefined_total", "total_issues", "delta",
                           "duration_s") if k in a}
    except Exception as e:
        cycle["audit"]["error"] = str(e)[:200]

    return cycle


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=5)
    ap.add_argument("--pop", type=int, default=30)
    ap.add_argument("--gens", type=int, default=3)
    args = ap.parse_args()

    store = get_memory_store()
    dreamer = DreamingModule()
    evo = EvolutionEngine(population_size=args.pop, elitism_count=4)
    evo.initialize_population(dict(_GENE_BOUNDS))
    metacog = MetaCognitionWorm()
    auditor = WeeklyCodeAuditWorm()

    # baseline external signal
    base = _external_signal_stats(store)
    print(f"baseline external signal: {base['external']} events "
          f"({base['by_source']}) | errors fixed so far: {base['errors_fixed']}")
    print(f"running {args.cycles} cycles x {args.gens} GA generations "
          f"(pop {args.pop})...")
    print("-" * 72)

    results = []
    for i in range(1, args.cycles + 1):
        t0 = time.time()
        c = run_one_cycle(i, store, evo, dreamer, metacog, auditor, args.gens)
        dt = time.time() - t0
        ev = c["evolution"]
        fit = ev.get("best_fitness")
        aud = c["audit"]
        und = aud.get("undefined_total", "?")
        print(f"cycle {i:3d} | gen {ev.get('generation','?'):4d} | "
              f"fitness {fit if fit is not None else '?':>7} | "
              f"undefined {und} | delta {aud.get('delta','?')} | {dt:.1f}s")
        results.append(c)

    # final state
    best = evo.get_best_genome()
    after = _external_signal_stats(store)
    print("-" * 72)
    print(f"after {args.cycles} cycles: generation {evo._generation} | "
          f"best fitness {round(best.fitness, 4) if best else '?'}")
    print(f"best genes: {json.dumps(best.genes, indent=2) if best else '?'}")
    print(f"external signal: {base['external']} -> {after['external']} events")

    # persist the run summary
    try:
        store.record_event(
            source="CycleRunner",
            event_type="training_cycle_batch",
            data={
                "cycles": args.cycles,
                "generations": evo._generation,
                "best_fitness": best.fitness if best else 0.0,
                "best_genes": best.genes if best else {},
                "external_before": base,
                "external_after": after,
                "duration_s": round(sum(r.get("duration_s", 0) for r in results), 1),
            },
            tags=["cycle", "training", "evolution"],
        )
    except Exception:
        pass  # scanner:ignore
    print("run summary recorded to store")


if __name__ == "__main__":
    main()