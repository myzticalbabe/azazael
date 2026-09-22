"""Tests for the L1 wiring cycle: the gate, the canary, and the effector.

WHY THIS FILE EXISTS (2026-09-21)
---------------------------------
`wiring_genome.py` (rung L1) had a genotype and a fitness but no cycle and no
consumer, which is the defect this project already found once at the
hyperparameter layer: memory -> hyperparameters -> training -> memory, never
conditioned on what was learned, so the loop closed inside the trainer and the
system's behaviour never changed.

The wiring genome closes it because `worm_registry.decide_execution_order` READS
the promoted genome. So the tests below are ordered by what they defend:

1. **The effector** -- that a promoted genome actually changes dispatch order.
   Without this the whole rung is a report, so it is tested first.
2. **The gate** -- that it accumulates evidence instead of crowning one lucky
   draw, and refuses to promote on evidence too thin to carry a verdict.
3. **The canary** -- that a promotion which does not hold is reverted.
4. **Operator observability** -- the defect the first live run found: two of
   three mutation operators produced children scoring IDENTICALLY to their
   parent (delta exactly 0.0), i.e. search dimensions that did not exist.

Run:
    /c/Users/clint/venv-314t/Scripts/python.exe -m pytest tests/test_wiring_cycle.py -q
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from CORE.WORMS.expansion import wiring_genome as wg  # noqa: E402


def _load_wiring_cycle(tmp_path, monkeypatch):
    """Import `scripts/wiring_cycle.py` against a throwaway state dir.

    The module computes its state paths at import time, so the env var must be
    set BEFORE the import — the same set-at-collection-time reason `conftest.py`
    gives for the memory store. Reimported per test so no test can leak a
    promotion into another, or into the developer's real `state/`.
    """
    monkeypatch.setenv("AZAZAEL_WIRING_STATE_DIR", str(tmp_path))
    monkeypatch.delenv("AZAZAEL_WIRING_PROMOTED", raising=False)
    monkeypatch.setenv("AZAZAEL_WIRING_DISCOVER", "0")  # ~38s cold start
    spec = importlib.util.spec_from_file_location(
        "wiring_cycle_under_test", _ROOT / "scripts" / "wiring_cycle.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


REGISTRY = {
    "Alpha": {"priority": 5, "category": "monitor"},
    "Beta": {"priority": 5, "category": "monitor"},
    "Gamma": {"priority": 5, "category": "monitor"},
    "Delta": {"priority": 5, "category": "monitor"},
    "SpineCycleWorm": {"priority": 5, "category": "mesh"},   # infra: not evolvable
}

CREDIT = {"Alpha": 0.9, "Beta": 0.8, "Gamma": 0.2, "Delta": 0.7}
ELIGIBLE = ["Alpha", "Beta", "Gamma", "Delta"]


@pytest.fixture
def wc(tmp_path, monkeypatch):
    mod = _load_wiring_cycle(tmp_path, monkeypatch)
    monkeypatch.setattr(mod, "load_registry", lambda: dict(REGISTRY))
    monkeypatch.setattr(mod, "eligible_organs", lambda r: list(ELIGIBLE))

    def fake_credit():
        return SimpleCredit(CREDIT)

    monkeypatch.setattr(mod, "load_credit", fake_credit)
    return mod


class SimpleCredit:
    """Stand-in carrying only what `credit_snapshot` reads."""

    def __init__(self, rewards):
        self._rewards = dict(rewards)
        self.outcomes = {w: SimpleOutcome(w, 12) for w in rewards}
        self.n_outcome_rows = len(rewards) * 12
        self.n_choice_rows = len(rewards)
        self.attribution_mode = "per-worm-type (statistical)"

    @property
    def rewards(self):
        return dict(self._rewards)


class SimpleOutcome:
    def __init__(self, worm_type, n):
        self.worm_type = worm_type
        self.n = n


# --------------------------------------------------------------------------
# 1. The effector -- without this the rung is a report
# --------------------------------------------------------------------------

def test_a_promoted_genome_changes_dispatch_order(tmp_path, monkeypatch):
    """THE test for this rung: state written here must alter behaviour there.

    A learner whose output nothing consumes is the defect this project already
    paid for once. So this pins the actual causal link:
    `state/wiring_promoted.json` -> `decide_execution_order` ordering.
    """
    from CORE import worm_registry as wr

    promoted = tmp_path / "wiring_promoted.json"
    monkeypatch.setattr(wr, "WIRING_PROMOTED_PATH", str(promoted))
    monkeypatch.setattr(wr, "_wiring_cache", None)
    monkeypatch.setattr(wr, "_wiring_cache_stamp", None)
    monkeypatch.setattr(wr, "WORM_REGISTRY", {
        "Alpha": {"priority": 5}, "Beta": {"priority": 5},
        "Gamma": {"priority": 5}, "SpineCycleWorm": {"priority": 5},
    })

    engine = wr.SpawnDiversityEngine()
    monkeypatch.setattr(engine, "_record_pams", lambda et, data: None)
    monkeypatch.setattr(engine, "record_spawn", lambda *a, **k: None)

    # No promotion file: ranking falls back to registry priority then name.
    baseline, _ = engine.decide_execution_order("monitor", ["Alpha", "Beta", "Gamma"])
    assert baseline == ["Alpha", "Beta", "Gamma"]

    # A promoted genome that promotes Gamma and DEMOTES Alpha.
    promoted.write_text(json.dumps({
        "active": ["Beta", "Gamma"],
        "priority": {"Gamma": 10, "Beta": 9},
    }), encoding="utf-8")

    ordered, decision_id = engine.decide_execution_order(
        "monitor", ["Alpha", "Beta", "Gamma"])

    assert decision_id, "the decision must still be recorded joinably"
    assert ordered == ["Gamma", "Beta", "Alpha"], ordered

    # THE INVARIANT: ordering only. A demoted organ still runs.
    assert set(ordered) == {"Alpha", "Beta", "Gamma"}


def test_the_effector_is_inert_without_a_promotion(tmp_path, monkeypatch):
    """No promotion must mean no behaviour change, not a crash or a default."""
    from CORE import worm_registry as wr

    monkeypatch.setattr(wr, "WIRING_PROMOTED_PATH",
                        str(tmp_path / "does-not-exist.json"))
    monkeypatch.setattr(wr, "_wiring_cache", None)
    monkeypatch.setattr(wr, "_wiring_cache_stamp", None)

    assert wr._load_promoted_wiring() is None
    engine = wr.SpawnDiversityEngine()
    monkeypatch.setattr(engine, "_record_pams", lambda et, data: None)
    monkeypatch.setattr(engine, "record_spawn", lambda *a, **k: None)
    monkeypatch.setattr(wr, "WORM_REGISTRY", {"Beta": {"priority": 9},
                                              "Alpha": {"priority": 1}})

    ordered, _ = engine.decide_execution_order("monitor", ["Alpha", "Beta"])
    assert ordered == ["Beta", "Alpha"], "registry priority must still decide"


def test_the_effector_survives_a_corrupt_promotion_file(tmp_path, monkeypatch):
    """Dispatch must never be blocked by state."""
    from CORE import worm_registry as wr

    bad = tmp_path / "wiring_promoted.json"
    bad.write_text("{not json at all", encoding="utf-8")
    monkeypatch.setattr(wr, "WIRING_PROMOTED_PATH", str(bad))
    monkeypatch.setattr(wr, "_wiring_cache", None)
    monkeypatch.setattr(wr, "_wiring_cache_stamp", None)

    assert wr._load_promoted_wiring() is None


def test_the_effector_notices_a_new_promotion_without_a_restart(tmp_path,
                                                               monkeypatch):
    """Cache is keyed on mtime, not a TTL.

    A TTL would either serve a stale genome right after a promotion or re-read
    the file on every hot dispatch call.
    """
    from CORE import worm_registry as wr

    path = tmp_path / "wiring_promoted.json"
    monkeypatch.setattr(wr, "WIRING_PROMOTED_PATH", str(path))
    monkeypatch.setattr(wr, "_wiring_cache", None)
    monkeypatch.setattr(wr, "_wiring_cache_stamp", None)

    assert wr._load_promoted_wiring() is None
    path.write_text(json.dumps({"active": ["Alpha"]}), encoding="utf-8")
    assert wr._load_promoted_wiring() is not None

    # Rewrite with different content and a distinct mtime.
    import os
    import time
    time.sleep(0.01)
    path.write_text(json.dumps({"active": ["Beta"]}), encoding="utf-8")
    os.utime(path, (time.time() + 5, time.time() + 5))
    assert wr._load_promoted_wiring()["active"] == ["Beta"]


# --------------------------------------------------------------------------
# 2. The gate
# --------------------------------------------------------------------------

def _cycle_wg(mod):
    """The `wiring_genome` object the cycle under test ACTUALLY calls.

    Patching the module imported at the top of this file is not the same thing:
    `worm_registry._purge_worm_modules()` deletes every `CORE.WORMS.*` entry from
    `sys.modules` (so re-discovery can re-fire the `@register_worm` decorators),
    and the re-import installs a SECOND module object under the same name. After
    any `reset_registry()` in the session, this file's `wg` and the cycle's `wg`
    are different objects — measured 2026-09-22: a forced winner was ignored, the
    gate reported `no candidate beat the incumbent`, and eight gate tests failed
    in-suite while passing alone. The cycle is what runs, so the cycle's module is
    what gets patched.
    """
    return getattr(mod, "wg", wg)


def _force_winner(mod, monkeypatch, genome=None, delta=0.5):
    """Make every cycle score one fixed candidate at a fixed delta.

    Patches `OBSERVABLE_MUTATIONS`, because the cycle calls the OPERATORS
    directly, not the `mutate` helper. The first version patched `wg.mutate`,
    which the cycle never calls — so those gate tests were passing by the
    accident that a fixed RNG seed produces the same child each cycle, rather
    than because the streak logic worked. A test that passes for a reason other
    than the one it names is worse than no test.
    """
    # NOTE the composition: three organs, not the full four. A forced winner
    # identical to the seed genome has the SAME fingerprint, because
    # `fingerprint()` is over composition only (generation/parent/origin are
    # excluded so lineage cannot masquerade as novelty). A fixture that happened
    # to equal the seed made the canary's revert assertion unfalsifiable.
    target = _cycle_wg(mod)
    winner = genome if genome is not None else target.WiringGenome(
        active=frozenset({"Alpha", "Beta", "Delta"}), origin="forced")
    monkeypatch.setattr(target, "OBSERVABLE_MUTATIONS",
                        (lambda g, e, r: winner,))
    monkeypatch.setattr(target, "paired_compare", lambda c, i, r, e, margin=0.0: {
        "ok": True, "delta": delta, "accept": delta > margin,
        "candidate": {"observed": 4, "coverage": 1.0,
                      "evidence_ratio": 1.0, "n_active": 4},
        "incumbent": {},
        "candidate_fingerprint": c.fingerprint(),
        "incumbent_fingerprint": i.fingerprint(),
    })
    return winner


def test_one_winning_draw_does_not_promote(wc, monkeypatch):
    """The measured defect: 159/400 rows (39.8%) cleared a single gate."""
    # `L1_MIN_WINS` is read from the hyper-optimizer and only FALLS BACK to the
    # shipped literal, so the count is asserted against the live threshold rather
    # than against 3. Hardcoding the literal made these tests fail the moment a
    # tuned value landed (measured 2026-09-22: ``_hyp`` returned min_wins=2 while
    # the tests still expected 3).
    assert wc.L1_MIN_WINS > 1, "a single win must never be enough to promote"
    _force_winner(wc, monkeypatch)
    report = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)

    assert report["ok"] is True
    assert report["promoted"] is False
    assert report["accepted"] == 1, "the candidate must actually be accepted"
    assert report["streak"]["wins"] == 1
    assert ("awaiting %d consecutive wins" % wc.L1_MIN_WINS) in report["reason"]


def test_the_same_candidate_must_win_consecutively(wc, monkeypatch):
    _force_winner(wc, monkeypatch)
    for expected in range(1, wc.L1_MIN_WINS):
        report = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
        assert report["streak"]["wins"] == expected
        assert report["promoted"] is False

    report = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert report["streak"]["wins"] == wc.L1_MIN_WINS
    assert report["promoted"] is True
    # The streak resets after a promotion, so the next one must earn it again.
    assert wc._streak_state()["wins"] == 0

    promoted = json.loads(Path(wc.PROMOTED_JSON).read_text(encoding="utf-8"))
    assert promoted["fingerprint"]
    assert promoted["promoted_by"] == "wiring_cycle"


def _other_winner():
    # Three organs, so it still clears the evidence floor: a 1-organ candidate
    # would be rejected as thin evidence before the streak is ever consulted.
    return wg.WiringGenome(active=frozenset({"Alpha", "Beta", "Gamma"}),
                           origin="forced-other")


def test_a_noise_level_improvement_cannot_be_promoted(wc, monkeypatch):
    """The measured defect: promotions won by 0.09% of the signal's spread.

    Live, 2026-09-21, with the gate's margin at 0.0: three genomes were promoted
    on paired deltas of +0.000555, +0.000272 and +0.000111, while the credit
    signal they were scored on had a population spread of 0.1228. A streak does
    not filter that, because the search offers twelve fresh children per cycle;
    a handful of near-ties sitting just above the incumbent assembles the streak
    out of noise. This pins the floor: a sub-margin improvement must never
    promote, however many cycles it is offered.
    """
    assert wc.L1_MARGIN > 0.0, "a zero margin is the bug this test guards"
    _force_winner(wc, monkeypatch, delta=wc.L1_MARGIN / 4.0)
    reports = [wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
               for _ in range(wc.L1_MIN_WINS + 2)]
    assert not any(r.get("promoted") for r in reports), \
        "a sub-margin improvement was promoted"


def test_an_improvement_above_the_margin_still_promotes(wc, monkeypatch):
    """The floor must not make the gate unreachable."""
    _force_winner(wc, monkeypatch, delta=max(0.5, wc.L1_MARGIN * 10))
    reports = [wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
               for _ in range(wc.L1_MIN_WINS)]
    assert reports[-1].get("promoted") is True


def test_carrying_the_elite_is_what_makes_the_gate_reachable(wc, monkeypatch):
    """THE fix for an unreachable gate.

    Live measurement 2026-09-21: two wins on one fingerprint, never a third, in
    hours of running -- because every cycle generated fresh random children and
    discarded them, so the same winner had to be re-invented by chance three
    times in a row. Carrying the winner forward makes the third win a matter of
    the candidate still being good, and `best.label` is asserted to be the
    carried elite rather than a lucky newcomer.
    """
    _force_winner(wc, monkeypatch)
    assert wc.L1_MIN_WINS >= 2, "carrying an elite only matters when >1 win is needed"

    r1 = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert r1["streak"]["wins"] == 1 and r1["promoted"] is False
    assert r1["elite_carried"] is False, "nothing exists to carry on the first cycle"

    r2 = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert r2["elite_carried"] is True, \
        "the winner was not carried into the next cycle"

    final = r2
    for _ in range(wc.L1_MIN_WINS + 1):
        if final["promoted"]:
            break
        final = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert final["promoted"] is True, "the gate never reached its threshold"
    assert final["best"]["label"] == "elite_carried", \
        "the streak accumulated on a fresh child, not on the carried elite"


def test_a_BETTER_winner_takes_over_and_restarts_the_streak(wc, monkeypatch):
    """The streak must still not accumulate across DIFFERENT candidates.

    The delta is a function of who is being scored, not a constant: the carried
    elite stays at 0.5 while the newcomer scores 0.9, i.e. a real improvement
    rather than a tie. (`_force_winner` cannot express this -- it patches
    `paired_compare` to one value for every candidate, including the elite it is
    meant to be displacing, so both arms of the comparison move together.)
    """
    _force_winner(wc, monkeypatch)
    assert wc.L1_MIN_WINS >= 2, "the streak must need more than one win"
    for _ in range(wc.L1_MIN_WINS - 1):
        wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    elite_fp = wc._streak_state()["fingerprint"]
    assert elite_fp and wc._streak_state()["wins"] == wc.L1_MIN_WINS - 1

    other = _other_winner()
    assert other.fingerprint() != elite_fp, "fixture must differ from the elite"

    # The newcomer must clear the LIVE elite-replace floor (`elite_delta *
    # (1 + L1_ELITE_REPLACE_RATIO)`), not the shipped fallback: the ratio is
    # hyper-optimized (measured 2026-09-22: 0.8625, i.e. a floor of 0.93125), so
    # a hardcoded 0.9 failed to displace a 0.5 elite.
    better = 0.5 * (1.0 + wc.L1_ELITE_REPLACE_RATIO) + 0.01

    def _by_fingerprint(c, i, r, e, margin=0.0):
        d = better if c.fingerprint() == other.fingerprint() else 0.5
        return {"ok": True, "delta": d, "accept": d > margin,
                "candidate": {"observed": 4, "coverage": 1.0,
                              "evidence_ratio": 1.0, "n_active": 4},
                "incumbent": {"value": 0.5}}

    target = _cycle_wg(wc)
    monkeypatch.setattr(target, "OBSERVABLE_MUTATIONS", (lambda g, e, r: other,))
    monkeypatch.setattr(target, "paired_compare", _by_fingerprint)
    rep = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)

    assert rep["best"]["fingerprint"] == other.fingerprint(), \
        "a genuinely better candidate failed to displace the carried elite"
    assert rep["streak"]["wins"] == 1, "a different winner must restart the count"
    assert rep["streak"]["fingerprint"] == other.fingerprint()


def test_thin_evidence_is_reported_but_never_promoted(wc, monkeypatch):
    """The `alert`-pool defect: oracle EQUALLED the best constant, and it promoted anyway.

    Two organs carry observations and the candidate touches both, so it covers
    100% of the available evidence — and that is still not a verdict, because a
    cover ratio is not a sample size. This is the distinction the earlier
    pipeline missed when it promoted on a per-state oracle that equalled the
    best constant.
    """
    _force_winner(wc, monkeypatch)
    monkeypatch.setattr(wc, "load_credit",
                        lambda: SimpleCredit({"Alpha": 0.9, "Beta": 0.8}))
    for _ in range(5):
        report = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert report["promoted"] is False
    assert "evidence too thin" in report["reason"], report["reason"]
    assert report["best_evidence_ratio"] == pytest.approx(1.0)
    assert report["best_observed"] == 2
    assert report["streak"]["wins"] == 0


def test_the_gate_still_gates_after_a_registry_reset(tmp_path, monkeypatch):
    """Regression for the in-suite failure that was invisible when run alone.

    `worm_registry.reset_registry()` deletes every `CORE.WORMS.*` module from
    `sys.modules` so the `@register_worm` decorators can re-fire, which also
    re-imports the HELPER modules (measured 2026-09-22: `wiring_genome` comes back
    as a different object — the purge's docstring only warns about worm CLASS
    identity). So after any earlier module reset, this file's `wg` and the
    cycle's are different objects, and a test that patches this file's `wg`
    patches something the cycle never calls: the forced winner was ignored, the
    gate reported `no candidate beat the incumbent`, and eight gate tests failed
    in-suite while passing alone.

    Here the cycle is loaded AFTER the reset, which is the in-suite order.
    """
    import importlib

    from CORE import worm_registry as wr

    mod_name = "CORE.WORMS.expansion.wiring_genome"
    before = importlib.import_module(mod_name)
    wr.reset_registry()
    after = importlib.import_module(mod_name)
    assert after is not before, \
        "fixture precondition: a reset must re-import the helper module"

    post_reset = _load_wiring_cycle(tmp_path, monkeypatch)
    monkeypatch.setattr(post_reset, "load_registry", lambda: dict(REGISTRY))
    monkeypatch.setattr(post_reset, "eligible_organs", lambda r: list(ELIGIBLE))
    monkeypatch.setattr(post_reset, "load_credit",
                        lambda: SimpleCredit(CREDIT))
    assert _cycle_wg(post_reset) is not wg, \
        "the cycle must hold the re-imported module, not this file's"

    _force_winner(post_reset, monkeypatch)
    report = post_reset.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert report["accepted"] == 1, report.get("reason")
    assert report["streak"]["wins"] == 1


def test_apply_switch_blocks_a_promotion_the_gate_approved(wc, monkeypatch):
    """AZAZAEL_WIRING_L1_APPLY=0 stops writes while still recording trials."""
    _force_winner(wc, monkeypatch)
    monkeypatch.setattr(wc, "L1_APPLY", False)
    for _ in range(3):
        report = wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert report["promoted"] is False
    assert "L1_APPLY=0" in report["reason"]
    assert not Path(wc.PROMOTED_JSON).exists()


def test_without_apply_the_cycle_still_scores_and_records(wc, monkeypatch):
    """Shadow mode must still produce the evidence a review needs."""
    _force_winner(wc, monkeypatch)
    for _ in range(3):
        report = wc.run_cycle(apply_promotion=False, candidates=2, seed=1)
    assert report["promoted"] is False
    assert "--apply not given" in report["reason"]
    assert wc._lineage_size() > 0


# --------------------------------------------------------------------------
# 3. The canary
# --------------------------------------------------------------------------

def test_canary_reverts_a_promotion_that_does_not_hold(wc, monkeypatch):
    _force_winner(wc, monkeypatch)
    for _ in range(3):
        wc.run_cycle(apply_promotion=True, candidates=1, seed=1)
    assert Path(wc.PROMOTED_JSON).exists()
    assert Path(wc.PREV_JSON).exists(), "rollback must be one file restore"

    # The promoted genome decays: its realised score collapses.
    genome = wg.WiringGenome.from_dict(
        json.loads(Path(wc.PROMOTED_JSON).read_text(encoding="utf-8")))
    status = _decayed_canary(wc, genome, CREDIT, ELIGIBLE, {})

    assert status["status"] == "reverted"
    # The revert restored the pre-promotion genome, not merely reported a problem.
    restored = json.loads(Path(wc.PROMOTED_JSON).read_text(encoding="utf-8"))
    assert restored["fingerprint"] != genome.fingerprint()

    rows = Path(wc.LINEAGE_JSONL).read_text(encoding="utf-8").splitlines()
    assert any("canary-revert" in r for r in rows), \
        "a revert with no lineage row is indistinguishable from no revert"


def _decayed_canary(wc, genome, rewards, eligible, counts):
    """`canary_check` against a collapsed fitness, without patching globals."""
    target = _cycle_wg(wc)
    real_fitness = target.fitness
    try:
        target.fitness = lambda g, c, e=None: {"ok": True, "value": -1.0,
                                               "observed": 4, "coverage": 1.0}
        return wc.canary_check(genome, rewards, eligible, counts)
    finally:
        target.fitness = real_fitness


def test_canary_ignores_a_genome_that_was_not_promoted(wc):
    """The canary only judges the genome it promoted."""
    state = {"fingerprint": "wg-x", "baseline": 0.5}
    Path(wc.CANARY_JSON).write_text(json.dumps(state), encoding="utf-8")
    genome = wg.WiringGenome(active=frozenset({"Alpha", "Beta", "Gamma", "Delta"}))
    # fingerprint mismatch -> not the promoted genome at all
    assert wc.canary_check(genome, CREDIT, ELIGIBLE, {})["status"] == "not-promoted"


# --------------------------------------------------------------------------
# 4. Operator observability -- the defect the first live run found
# --------------------------------------------------------------------------

def test_inert_operators_are_excluded_from_the_cycle(wc, monkeypatch):
    """40 live mutations produced 0 accepted candidates with all three operators.

    Cause: `fitness` read only `active` and the effector read only `priority`, so
    a cooldown mutation returned a child scoring IDENTICALLY to its parent.
    A search dimension nothing can observe is not a dimension.
    """
    report = wc.run_cycle(apply_promotion=False, candidates=4, seed=1)

    assert report["operators"] == ["mutate_flip_active", "mutate_bump_priority"]
    assert report["operators_excluded"] == ["mutate_adjust_cooldown"]
    assert set(report["operators"]) == {
        op.__name__ for op in wg.OBSERVABLE_MUTATIONS}


def test_every_used_operator_can_actually_move_the_score(wc, monkeypatch):
    """The invariant behind the exclusion: a used operator must not be a no-op.

    Measured per operator on a credit table where every organ is observed, so a
    null result is the operator's fault rather than the observation gap's.
    """
    incumbent = wg.seed_genome(REGISTRY)
    for op in wg.OBSERVABLE_MUTATIONS:
        import random
        moved = 0
        for i in range(60):
            child = op(incumbent, ELIGIBLE, random.Random(i))
            if wg.paired_compare(child, incumbent, CREDIT, ELIGIBLE)["delta"] != 0.0:
                moved += 1
        assert moved > 0, f"{op.__name__} cannot move the objective at all"


def test_priority_is_in_the_objective(wc):
    """Without this, the effector's ordering dimension was unselectable."""
    g = wg.WiringGenome(active=frozenset(ELIGIBLE))
    low = wg.WiringGenome(active=frozenset(ELIGIBLE), priority={"Gamma": 1})
    high = wg.WiringGenome(active=frozenset(ELIGIBLE), priority={"Gamma": 10})

    # Priority is a WEIGHT, and Gamma is the worst organ (0.2): the objective must
    # reward putting it LAST, which is exactly what the effector's ordering does.
    assert (wg.fitness(low, CREDIT, ELIGIBLE)["value"]
            > wg.fitness(high, CREDIT, ELIGIBLE)["value"])
    # And it must prefer the opposite for the best organ (Alpha, 0.9).
    best_high = wg.WiringGenome(active=frozenset(ELIGIBLE), priority={"Alpha": 10})
    best_low = wg.WiringGenome(active=frozenset(ELIGIBLE), priority={"Alpha": 1})
    assert (wg.fitness(best_high, CREDIT, ELIGIBLE)["value"]
            > wg.fitness(best_low, CREDIT, ELIGIBLE)["value"])
    # With uniform weights it reduces to the plain mean, so no baseline shifts.
    base = wg.fitness(g, CREDIT, ELIGIBLE)
    assert base["ranked_credit"] == pytest.approx(base["mean_credit"])
    assert base["ranked_credit"] == pytest.approx(0.65)


def test_search_resolution_is_reported_not_implied(wc, monkeypatch):
    """The binding constraint is observation coverage, so the cycle says so."""
    monkeypatch.setattr(wc, "load_credit", lambda: SimpleCredit({"Alpha": 0.9}))
    report = wc.run_cycle(apply_promotion=False, candidates=2, seed=1)

    assert report["visible_organs"] == 1
    assert report["search_resolution"] == pytest.approx(0.25)
