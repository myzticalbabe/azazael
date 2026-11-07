"""Lillith (the tuner) unit tests + trainer config/resume logic.

Live I/O is never exercised here; the live proof is `eve train --gens 1`.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed.self_modifying_worms import (
    GeneticAlgorithm,
    WormDNA,
    splice_hunches,
)
from eve_unleashed.trainer import (
    LillithTuner,
    TrainConfig,
    dream_seed_hunches,
    effective_confidence,
    load_or_seed,
    load_pop,
    save_pop,
    teacher_bias,
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


def test_splice_takes_head_of_a_tail_of_b():
    out = splice_hunches(["r1", "r2", "r3", "r4"], ["s1", "s2", "s3"])
    assert out == ["r1", "r2", "s2", "s3"]


def test_splice_dedups_drops_empty_and_caps():
    out = splice_hunches(["r1", "r1", None, ""], ["r1", "s9"], cap=3)
    assert out == ["r1", "s9"] and len(out) <= 3


def test_crossover_splices_parent_hunches():
    rng = random.Random(11)
    a = WormDNA(worm_id="a", worm_type="fetcher",
                hunches=["r1", "r2", "r3", "r4"])
    b = WormDNA(worm_id="b", worm_type="fetcher", hunches=["s1", "s2"])
    child = WormDNA.crossover(a, b, rng=rng)
    assert child.hunches == ["r1", "r2", "s2"]
    assert child.parent_ids == ["a", "b"]


def test_teacher_bias_pulls_quarter_gap_and_skips_teacher():
    ga = GeneticAlgorithm(population_size=3, rng=random.Random(2))
    t = WormDNA(worm_id="t", worm_type="fetcher", aggressiveness=1.0,
                min_confidence=0.9)
    w = WormDNA(worm_id="w", worm_type="fetcher", aggressiveness=0.2,
                min_confidence=0.6)
    ga.seed([t, w, WormDNA(worm_id="x", worm_type="fetcher",
                           aggressiveness=0.2, min_confidence=0.6)])
    assert teacher_bias(ga, t, strength=0.25) == 2
    assert abs(w.aggressiveness - 0.4) < 1e-9  # 0.2 + .25 * (1.0-0.2)
    assert abs(w.min_confidence - 0.675) < 1e-9
    assert t.aggressiveness == 1.0  # the teacher is never moved


def test_teacher_bias_respects_clamps():
    ga = GeneticAlgorithm(population_size=2, rng=random.Random(3))
    t = WormDNA(worm_id="t", worm_type="fetcher", min_confidence=0.99)
    w = WormDNA(worm_id="w", worm_type="fetcher", min_confidence=0.5)
    ga.seed([t, w])
    teacher_bias(ga, t, strength=1.0)
    assert w.min_confidence == 0.99  # full pull lands exactly on teacher


def test_effective_confidence_boosts_only_ancestral_rungs():
    assert effective_confidence(0.7, "archive", ["archive"]) == 0.75
    assert effective_confidence(0.7, "render", ["archive"]) == 0.7
    assert effective_confidence(0.97, "archive", ["archive"]) == 0.99
    assert effective_confidence(0.7, None, ["archive"]) == 0.7


def _dream_log(tmp_path, wins=2):
    import json as _j
    lines = []
    ts = 1000.0
    for i in range(wins):
        ts += 1
        lines.append({"ts": ts, "phase": "fetch", "event": "intuition",
                      "url": "https://w.example/%d" % i,
                      "predicted": "archive"})
        lines.append({"ts": ts + 0.5, "phase": "fetch", "event": "answer",
                      "url": "https://w.example/%d" % i,
                      "rung": "archive", "state": "ok"})
    lines.append({"ts": ts + 1, "phase": "fetch", "event": "intuition",
                  "url": "https://l.example/", "predicted": "render"})
    lines.append({"ts": ts + 1.5, "phase": "fetch", "event": "answer",
                  "url": "https://l.example/", "rung": "render",
                  "state": "blocked"})
    p = tmp_path / "dream.jsonl"
    p.write_text("\n".join(_j.dumps(r) for r in lines) + "\n",
                 encoding="utf-8")
    return str(p)


def test_dream_seed_hunches_takes_winners_only(tmp_path):
    log = _dream_log(tmp_path, wins=2)
    assert dream_seed_hunches(log) == ["archive"]  # render lost, excluded


def test_dream_seed_hunches_empty_log_seeds_nothing(tmp_path):
    assert dream_seed_hunches(str(tmp_path / "missing.jsonl")) == []


def test_load_or_seed_fresh_carries_dream_seeds(tmp_path):
    log = _dream_log(tmp_path, wins=3)
    cfg = TrainConfig(pop=2, fresh=True, pop_path=str(tmp_path / "p.json"),
                      log_path=log)
    ga = GeneticAlgorithm(population_size=2, rng=random.Random(9))
    load_or_seed(ga, cfg, random.Random(9))
    assert all(d.hunches == ["archive"] for d in ga.population)


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
