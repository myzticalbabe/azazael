"""net_genome: evolving the network itself, scored on the iGPU."""
import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed.net_genome import (
    NetFitness,
    NetGA,
    NetGenome,
    evaluate,
    run,
)
from eve_unleashed.self_modifying_worms import GeneticAlgorithm


def test_genome_clamps_to_documented_bounds():
    g = NetGenome(hidden=3, lr=9.0, steps=1, init_seed=0, mutation_rate=9.0)
    assert g.hidden == 8
    assert g.lr == pytest.approx(5e-2)
    assert g.steps == 10
    assert g.init_seed == 1
    assert g.mutation_rate == pytest.approx(0.6)


def test_mutate_mints_a_new_id_and_keeps_bounds():
    rng = random.Random(7)
    parent = NetGenome(hidden=32, lr=0.01, steps=40)
    child = parent.mutate(rng=rng)
    assert child.worm_id != parent.worm_id
    assert child.generation == parent.generation + 1
    assert child.parent_ids == [parent.worm_id]
    for _ in range(200):
        child = child.mutate(rng=rng)
        assert 8 <= child.hidden <= 256
        assert 1e-3 <= child.lr <= 5e-2
        assert 10 <= child.steps <= 240


def test_crossover_takes_genes_from_both_parents():
    rng = random.Random(3)
    a = NetGenome(hidden=8, lr=0.001, steps=10)
    b = NetGenome(hidden=256, lr=0.05, steps=240)
    seen_hidden, seen_lr = set(), set()
    for _ in range(200):
        c = NetGenome.crossover(a, b, rng=rng, fitter=a)
        seen_hidden.add(c.hidden)
        seen_lr.add(c.lr)
    assert seen_hidden == {8, 256}
    assert sorted(seen_lr) == [pytest.approx(0.001), pytest.approx(0.05)]


def test_netga_reuses_the_inherited_selection():
    assert issubclass(NetGA, GeneticAlgorithm)
    ga = NetGA(population_size=4, elite_keep=1, rng=random.Random(1))
    ga.seed_networks([NetGenome()])
    assert len(ga.population) == 4
    assert callable(ga._select)


def test_fitness_score_penalizes_slow_runs_at_equal_loss():
    fast = NetFitness(worm_id="a", loss=0.2, ms=100.0, backend="opencl")
    slow = NetFitness(worm_id="b", loss=0.2, ms=4000.0, backend="opencl")
    assert fast.score() > slow.score()
    assert fast.to_dict()["score"] == pytest.approx(fast.score())


@pytest.mark.parametrize("hidden", [8, 128])
def test_evaluate_reduces_loss_below_untrained(hidden):
    """Mean-gradient normalization: 256-sample batches must not go nan."""
    g = NetGenome(hidden=hidden, lr=0.01, steps=40, init_seed=3)
    fit = evaluate(g, use_gpu=None)
    assert not math.isnan(fit.loss), "batch gradient diverged to nan"
    assert fit.loss < 0.5, f"untrained-scale loss, got {fit.loss}"
    assert fit.backend in ("opencl", "cpu")


def test_run_improves_and_reports_its_denominator():
    res = run(generations=2, population=4, elite_keep=1, seed=5,
              verbose=False)
    assert res["generations"] == 2
    assert len(res["history"]) == 2
    for row in res["history"]:
        assert row["backend"] in ("opencl", "cpu")
        assert "ms" in row and "loss" in row
    assert res["best_genome"] is not None
    assert res["best_loss"] <= res["first_loss"]
