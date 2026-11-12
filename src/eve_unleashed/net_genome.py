"""net_genome -- evolve the NETWORK itself, scored on the iGPU.

Until now the evolved unit was a worm CONFIG genome (WormDNA: fetch
policy) and MCML networks were hand-built. This module makes the network
the genome: each NetGenome decodes to a Dense-tanh-Dense network, weights
are fit by gradient descent inside the episode, and the fitness is the
validation loss that network achieves -- so evolution searches topology
and optimizer genes while backprop does the weight search it is good at.

Reuse, not a fork (E2R-9): NetGA subclasses GeneticAlgorithm and calls
its inherited `_select` for fitness-proportionate selection. Only the two
type-specific hooks GeneticAlgorithm hardcodes (WormDNA.crossover and
WormDNA.mutate) are swapped for the NetGenome equivalents.

Scoring engine: mcml_gpu.FusedPair (tiled SGEMM, device-resident batch
pass). With no OpenCL device the same genomes are scored on the pure
CPU Dense path and the report says which backend produced the numbers --
a reading never silently changes meaning.

Fitness is the network's own validation loss on a fixed task, not a
simulation of the fetch world: nothing here claims to predict a live wall.
"""
from __future__ import annotations

import math
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .self_modifying_worms import GeneticAlgorithm

# -- the task: a fixed, deterministic regression both backends score alike --
IN_DIM = 8
OUT_DIM = 4


def _task(seed: int, n: int) -> Tuple[List[List[float]], List[List[float]]]:
    """Fixed nonlinear target with high-frequency and multiplicative terms.

    Chosen by measurement, not taste: on an easier tanh-only target every
    width scored 0.072-0.088 with no monotonic trend, so selection had no
    gradient. Here capacity pays (256 train samples, mean gradient, 40
    steps lr 0.01): hidden 8 -> 0.4226, 32 -> 0.4466, 128 -> 0.2998,
    256 -> 0.2280, and 256/120 steps -> 0.1964.
    """
    rng = random.Random(seed)
    X, T = [], []
    for _ in range(n):
        x = [rng.uniform(-1.0, 1.0) for _ in range(IN_DIM)]
        a = math.sin(5 * x[0]) * math.cos(4 * x[1])
        b = math.tanh(3 * x[2] * x[3] * x[4])
        c = math.tanh(sum(math.sin(3 * v) for v in x) / IN_DIM)
        d = math.cos(6 * x[5]) * math.tanh(x[6] * x[7] + x[0])
        T.append([a, b, c, d])
        X.append(x)
    return X, T


TRAIN_X, TRAIN_T = _task(11, 256)
VAL_X, VAL_T = _task(29, 64)


@dataclass
class NetGenome:
    """A network's topology + optimizer genes. `worm_id` keeps the name the
    inherited GeneticAlgorithm code paths look up (`fitness[...]`)."""

    worm_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hidden: int = 32
    lr: float = 0.01
    steps: int = 40
    init_seed: int = 3
    mutation_rate: float = 0.4
    generation: int = 1
    parent_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.hidden = max(8, min(256, (self.hidden // 8) * 8))
        self.lr = max(1e-3, min(5e-2, self.lr))
        self.steps = max(10, min(240, self.steps))
        self.init_seed = max(1, min(9_999, self.init_seed))
        self.mutation_rate = max(0.05, min(0.6, self.mutation_rate))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def mutate(self, rng: Optional[random.Random] = None) -> "NetGenome":
        rng = rng or random.Random()
        d = asdict(self)
        d["worm_id"] = str(uuid.uuid4())
        d["generation"] = self.generation + 1
        d["parent_ids"] = [self.worm_id]
        if rng.random() < self.mutation_rate:
            d["hidden"] = max(8, min(256, self.hidden + rng.choice(
                [-32, -16, -8, 8, 16, 32])))
        if rng.random() < self.mutation_rate:
            d["lr"] = self.lr * math.exp(rng.gauss(0.0, 0.35))
        if rng.random() < self.mutation_rate:
            d["steps"] = self.steps + rng.choice([-20, -10, 10, 20])
        if rng.random() < 0.15:
            d["init_seed"] = rng.randint(1, 9_999)
        return NetGenome(**d)

    @classmethod
    def crossover(cls, a: "NetGenome", b: "NetGenome",
                  rng: Optional[random.Random] = None,
                  fitter: Optional["NetGenome"] = None) -> "NetGenome":
        """Splice genes from both parents; `fitter` breaks ties the way
        WormDNA.crossover does, so a fitter parent leans the blend."""
        rng = rng or random.Random()
        lean = fitter if fitter is not None else a
        d: Dict[str, Any] = {
            "worm_id": str(uuid.uuid4()),
            "hidden": a.hidden if rng.random() < 0.5 else b.hidden,
            "lr": a.lr if rng.random() < 0.5 else b.lr,
            "steps": a.steps if rng.random() < 0.5 else b.steps,
            "init_seed": lean.init_seed if rng.random() < 0.7
            else rng.randint(1, 9_999),
            "mutation_rate": (a.mutation_rate + b.mutation_rate) / 2.0,
            "generation": max(a.generation, b.generation) + 1,
            "parent_ids": [a.worm_id, b.worm_id],
        }
        return NetGenome(**d)


@dataclass
class NetFitness:
    """Loss + wall time for one genome, so a score always prints with the
    numbers that produced it. Not a WormFitness subclass: that dataclass
    requires worm_type/generation, and the GA reads only score()."""

    worm_id: str
    loss: float
    ms: float
    backend: str

    def score(self) -> float:
        # Lower validation loss is better; a run that took visibly longer is
        # penalized so evolution cannot buy loss with unbounded time.
        quality = 1.0 / (1.0 + max(0.0, self.loss))
        time_penalty = 1.0 / (1.0 + self.ms / 5000.0)
        return quality * time_penalty

    def to_dict(self) -> Dict[str, Any]:
        return {"worm_id": self.worm_id, "loss": self.loss,
                "ms": self.ms, "backend": self.backend,
                "score": self.score()}


# -- scoring engines --
def _fit_cpu(g: NetGenome) -> Tuple[float, float]:
    from .mcml import Dense
    d1 = Dense(IN_DIM, g.hidden, seed=g.init_seed)
    d2 = Dense(g.hidden, OUT_DIM, seed=g.init_seed + 1)
    B = len(TRAIN_X)
    t0 = time.perf_counter()
    for _ in range(g.steps):
        for x, t in zip(TRAIN_X, TRAIN_T):
            y1 = [math.tanh(v) for v in d1.forward(x)]
            y2 = d2.forward(y1)
            _, gy2 = _mse(y2, t)
            gy1 = [gv * (1.0 - v * v)
                   for gv, v in zip(d2.backward(y1, gy2), y1)]
            d1.backward(x, gy1)
        # MEAN gradient: backward() accumulates a SUM over the batch, so a
        # raw step makes the effective rate scale with batch size (batch 256
        # diverged to nan at lr 0.01 while batch 32 was stable).
        for d in (d1, d2):
            d.W = [[w - g.lr * gw / B for w, gw in zip(row, grow)]
                   for row, grow in zip(d.W, d.gW)]
            d.b = [v - g.lr * gv / B for v, gv in zip(d.b, d.gb)]
            d.gW = [[0.0] * d.in_dim for _ in range(d.out_dim)]
            d.gb = [0.0] * d.out_dim
    loss = sum(_mse(d2.forward([math.tanh(v) for v in d1.forward(x)]), t)[0]
               for x, t in zip(VAL_X, VAL_T)) / len(VAL_X)
    return loss, (time.perf_counter() - t0) * 1000.0


def _mse(pred: List[float], target: List[float]) -> Tuple[float, List[float]]:
    n = len(pred)
    diff = [p - t for p, t in zip(pred, target)]
    return sum(d * d for d in diff) / n, [2.0 * d / n for d in diff]


def _fit_gpu(g: NetGenome) -> Tuple[float, float]:
    from .mcml_gpu import FusedPair, mse_batch
    pair = FusedPair(IN_DIM, g.hidden, OUT_DIM,
                     seed1=g.init_seed, seed2=g.init_seed + 1)
    t0 = time.perf_counter()
    for _ in range(g.steps):
        # One forward per step: backward_batch reads the buffers forward
        # just wrote, so a second call would overwrite them.
        y = pair.forward_batch(TRAIN_X)
        _, gy = mse_batch(y, TRAIN_T)
        # Divide the output gradient by the batch size: backward_batch
        # accumulates a SUM, and backward is linear in gy, so this turns it
        # into a mean gradient and makes lr independent of batch size.
        B = len(TRAIN_X)
        pair.backward_batch([[v / B for v in row] for row in gy])
        pair.step(g.lr)
        pair.zero_grad()
    val = pair.forward_batch(VAL_X)
    loss = mse_batch(val, VAL_T)[0]
    return loss, (time.perf_counter() - t0) * 1000.0


#: Why the last backend probe failed, so "cpu" is never an unexplained
#: fallback: report() and run() print this when they fall back.
LAST_BACKEND_ERROR: Optional[str] = None


def backend_available() -> bool:
    global LAST_BACKEND_ERROR
    try:
        from .mcml_gpu import FusedPair
        FusedPair(IN_DIM, 8, OUT_DIM)
    except Exception as e:  # noqa: BLE001 - recorded, then reported
        LAST_BACKEND_ERROR = f"{type(e).__name__}: {e}"
        return False
    LAST_BACKEND_ERROR = None
    return True


def evaluate(g: NetGenome, use_gpu: Optional[bool] = None) -> NetFitness:
    """Score one genome. Backend is recorded on the result."""
    if use_gpu is None:
        use_gpu = backend_available()
    if use_gpu:
        loss, ms = _fit_gpu(g)
        backend = "opencl"
    else:
        loss, ms = _fit_cpu(g)
        backend = "cpu"
    return NetFitness(worm_id=g.worm_id, loss=loss, ms=ms, backend=backend)


class NetGA(GeneticAlgorithm):
    """GeneticAlgorithm with the network genome's breeding hooks.

    `_select` is inherited unchanged -- the selection mechanics are the
    developed instrument. Only evolve() is restated, because the parent
    calls WormDNA.crossover/WormDNA.mutate by name.
    """

    def seed_networks(self, genomes: List[NetGenome]) -> None:
        with self._lock:
            self.population = list(genomes[: self.population_size])
            while len(self.population) < self.population_size:
                self.population.append(NetGenome())
            self.generation = 1

    def evolve(self) -> List[NetGenome]:
        with self._lock:
            pop = list(self.population)
            fit = dict(self.fitness)

        scored = [(d, f.score() if (f := fit.get(d.worm_id)) is not None
                   else 0.3) for d in pop]
        scored.sort(key=lambda x: x[1], reverse=True)
        elites = [d for d, _ in scored[: self.elite_keep]]

        new_pop: List[NetGenome] = list(elites)
        while len(new_pop) < self.population_size:
            p1, p2 = self._select(scored), self._select(scored)
            s1 = fit[p1.worm_id].score() if fit.get(p1.worm_id) else 0.3
            s2 = fit[p2.worm_id].score() if fit.get(p2.worm_id) else 0.3
            child = NetGenome.crossover(p1, p2, rng=self.rng,
                                        fitter=p1 if s1 >= s2 else p2)
            if self.rng.random() < 0.7:
                child = child.mutate(rng=self.rng)
            new_pop.append(child)

        self.population = new_pop[: self.population_size]
        self.generation += 1
        return list(self.population)


def run(generations: int = 4, population: int = 8, elite_keep: int = 2,
        seed: int = 20261112, use_gpu: Optional[bool] = None,
        verbose: bool = True) -> Dict[str, Any]:
    """Seed -> score -> breed, reporting the best network per generation."""
    rng = random.Random(seed)
    ga = NetGA(population_size=population, elite_keep=elite_keep, rng=rng)
    start = NetGenome(hidden=32, lr=0.02, steps=60, init_seed=3)
    population_list = [start] + [start.mutate(rng=rng)
                                 for _ in range(population - 1)]
    ga.seed_networks(population_list)

    backend = "opencl" if (use_gpu if use_gpu is not None
                           else backend_available()) else "cpu"
    history = []
    best_ever: Optional[Tuple[float, NetGenome]] = None
    for gen in range(generations):
        for g in ga.population:
            ga.record_fitness(evaluate(g, use_gpu=(backend == "opencl")))
        best = ga.best()
        bf = ga.fitness[best.worm_id]
        if verbose:
            print(f"gen {ga.generation}: best loss={bf.loss:.5f} "
                  f"score={bf.score():.4f} hidden={best.hidden} "
                  f"lr={best.lr:.4f} steps={best.steps} "
                  f"ms={bf.ms:.0f} backend={bf.backend}")
        history.append({"generation": ga.generation, "loss": bf.loss,
                        "score": bf.score(), "hidden": best.hidden,
                        "lr": best.lr, "steps": best.steps,
                        "ms": bf.ms, "backend": bf.backend})
        if best_ever is None or bf.loss < best_ever[0]:
            best_ever = (bf.loss, best)
        ga.evolve()

    first, last = history[0], history[-1]
    result = {
        "backend": backend,
        "generations": generations,
        "first_loss": first["loss"],
        "best_loss": best_ever[0] if best_ever else None,
        "best_genome": best_ever[1].to_dict() if best_ever else None,
        "improved": bool(best_ever and best_ever[0] < first["loss"]),
        "history": history,
    }
    if verbose:
        if backend == "cpu" and LAST_BACKEND_ERROR:
            print(f"backend=cpu (opencl unavailable: {LAST_BACKEND_ERROR})")
        print(f"backend={backend} first_loss={first['loss']:.5f} "
              f"best_loss={result['best_loss']:.5f} "
              f"improved={result['improved']}")
        print(f"VERDICT: {'OK' if result['improved'] else 'FLAT'} "
              f"network evolution over {generations} generations")
    return result


if __name__ == "__main__":
    import sys
    gens = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    res = run(generations=gens)
    sys.exit(0 if res["improved"] else 1)
