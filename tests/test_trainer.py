"""Lillith (the tuner) unit tests + trainer config/resume logic.

Live I/O is never exercised here; the live proof is `eve train --gens 1`.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed.self_modifying_worms import GeneticAlgorithm, WormDNA
from eve_unleashed.trainer import (
    LillithTuner,
    TrainConfig,
    load_or_seed,
    load_pop,
    save_pop,
)


def test_lillith_holds_while_warming_up():
    t = LillithTuner()
    d1 = t.observe(0.60)
    assert d1["width"] == 0.15 and "warming" in d1["reason"]
    d2 = t.observe(0.65)
    assert d2["width"] == 0.15


def test_lillith_widens_on_stall():
    t = LillithTuner(width=0.10)
    t.observe(0.70)
    t.observe(0.7004)
    d = t.observe(0.6996)
    assert abs(d["width"] - 0.15) < 1e-9 and d["reason"].startswith("stall")


def test_lillith_narrows_on_climb():
    t = LillithTuner(width=0.20)
    t.observe(0.60)
    t.observe(0.65)
    d = t.observe(0.71)
    assert abs(d["width"] - 0.16) < 1e-9 and d["reason"].startswith("climb")


def test_lillith_clamps():
    t = LillithTuner(width=0.5)
    for _ in range(6):
        t.observe(0.70)
    assert t.width == 0.5
    t2 = LillithTuner(width=0.01)
    t2.observe(0.60)
    t2.observe(0.70)
    t2.observe(0.80)
    assert t2.width == 0.01


def test_lillith_apply_sets_population_width():
    t = LillithTuner(width=0.3)
    ga = GeneticAlgorithm(population_size=3, rng=random.Random(1))
    ga.seed([WormDNA(worm_id=f"w{i}", worm_type="fetcher") for i in range(3)])
    t.apply(ga)
    assert all(abs(d.mutation_rate - 0.3) < 1e-9 for d in ga.population)


def test_load_or_seed_fresh(tmp_path):
    cfg = TrainConfig(pop=3, fresh=True, pop_path=str(tmp_path / "p.json"))
    ga = GeneticAlgorithm(population_size=3, rng=random.Random(7))
    assert load_or_seed(ga, cfg, random.Random(7)) == 1
    assert len(ga.population) == 3


def test_load_or_seed_resumes(tmp_path):
    popf = tmp_path / "p.json"
    dnas = [WormDNA(worm_id=f"r{i}", worm_type="fetcher",
                    aggressiveness=0.28, min_confidence=0.72)
            for i in range(2)]
    popf.write_text(json.dumps([d.to_dict() for d in dnas]))
    cfg = TrainConfig(pop=2, fresh=False, pop_path=str(popf))
    ga = GeneticAlgorithm(population_size=2, rng=random.Random(7))
    start = load_or_seed(ga, cfg, random.Random(7))
    assert start == ga.generation == 1
    assert [d.worm_id for d in ga.population] == ["r0", "r1"]
    assert ga.population[0].aggressiveness == 0.28


def test_load_or_seed_reads_generation(tmp_path):
    popf = tmp_path / "p.json"
    dnas = [WormDNA(worm_id=f"g{i}", worm_type="fetcher") for i in range(2)]
    popf.write_text(json.dumps({"generation": 5,
                               "genomes": [d.to_dict() for d in dnas]}))
    cfg = TrainConfig(pop=2, fresh=False, pop_path=str(popf))
    ga = GeneticAlgorithm(population_size=2, rng=random.Random(7))
    assert load_or_seed(ga, cfg, random.Random(7)) == 5


def test_save_load_pop_roundtrip(tmp_path):
    popf = str(tmp_path / "p.json")
    ga = GeneticAlgorithm(population_size=2, rng=random.Random(3))
    ga.seed([WormDNA(worm_id=f"s{i}", worm_type="fetcher",
                     aggressiveness=0.5) for i in range(2)])
    ga.generation = 7
    save_pop(ga, popf)
    ga2 = GeneticAlgorithm(population_size=2, rng=random.Random(3))
    load_pop(ga2, popf)
    assert ga2.generation == 7
    assert [d.worm_id for d in ga2.population] == ["s0", "s1"]
    assert ga2.population[0].aggressiveness == 0.5
