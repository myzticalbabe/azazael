# coding: utf-8
"""MUTAGEN — the 17th organ: did the genome GROW, or was it given away?

Why this test exists
--------------------
Phase E (Morph) appends one row per cycle to `state/proteus_morph.jsonl` with the
gene it trialled and the fitness delta it measured. That ledger is the record of
whether adding a gene helped, and until MUTAGEN existed no organ read it.

What the ledger showed on 2026-09-12 is the failure this organ encodes: 76% of
the structural trials ran with the trialled gene resolved to its OFF state, and
every one of them was retained. A gene that is switched off in the trial arm
cannot have produced the gain, so the delta was measuring the comparison rather
than the gene.

Two things are therefore locked here:

* the organ's classification of "provably inert", and the rule that an absent
  ledger yields NO signal rather than a calm zero;
* the mirror of the producer's boolean threshold (`proteus_hooks._as_bool`,
  which crosses at 0.5). The tier is deliberately loadable as a bare directory,
  so it cannot always import the producer; the mirror is pinned so the two
  cannot drift apart in silence.
"""
import os
import sys
import unittest

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_project_root, os.path.join(_project_root, "src"),
           os.path.join(_project_root, "src", "CORE", "WORMS", "expansion")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exmachina as ex                                    # noqa: E402
from CORE.WORMS.expansion import proteus_hooks as ph      # noqa: E402

_LEDGER = os.path.join(_project_root, "state", "proteus_morph.jsonl")


def _row(gene="use_schema_features", value=False, delta=1.0, dim=5, cycle=0):
    """One morph-ledger row, shaped exactly as `proteus_hooks.morph_record`."""
    return {"cycle_index": cycle, "gene": gene, "dimension": dim,
            "fitness": 20.0 + float(delta), "baseline_fitness": 20.0,
            "extra": {gene: value}}


def _inert_ledger(n=6, delta=1.0):
    return [_row(value=False, delta=delta, cycle=i) for i in range(n)]


class TestMirrorOfTheProducerThreshold(unittest.TestCase):
    """The tier mirrors `_as_bool`'s threshold; lock it to the producer."""

    def test_mirror_threshold_matches_the_producer(self):
        self.assertEqual(ex._MORPH_SWITCH_AT, 0.5)
        # If the producer ever moves its crossing point, these flip and this
        # test fails -- which is the point: a silent divergence would make the
        # organ count inert trials against a rule nobody else uses.
        self.assertIs(ph._as_bool(0.5), True)
        self.assertIs(ph._as_bool(0.4999), False)
        self.assertIs(ph._as_bool(True), True)
        self.assertIs(ph._as_bool(False), False)

    def test_observed_ledger_values_resolve_as_the_producer_resolves_them(self):
        # values that actually occur in the ledger
        cases = [0.05632200445147071, 0.06856321716945209, 0.5141935498649961,
                 True, False]
        for v in cases:
            self.assertIs(ph._as_bool(v),
                          v if isinstance(v, bool) else (float(v) >= ex._MORPH_SWITCH_AT),
                          "mirror disagrees with the producer on %r" % (v,))

    def test_resolver_reports_which_path_it_took(self):
        _resolve, how = ex._switch_resolver()
        self.assertIn(how, ("producer", "threshold:0.5"))


class TestProvablyInertTrials(unittest.TestCase):

    def test_gene_off_in_every_trial_is_never_enabled(self):
        m = ex.mutagenesis(_inert_ledger(6))
        self.assertEqual(m["trials"], 6)
        self.assertEqual(m["inert_trials"], 6)
        self.assertEqual(m["inert_share"], 1.0)
        self.assertEqual(m["never_enabled"], ["use_schema_features"])
        # a gene that never went on has no observable value effect
        self.assertIsNone(m["genes"][0]["value_effect"])
        self.assertTrue(m["genes"][0]["never_enabled"])

    def test_free_growth_reports_the_retention_of_unattributable_trials(self):
        m = ex.mutagenesis(_inert_ledger(6))
        self.assertEqual(m["verdict"], "free growth")
        # 6/6 is significant (p = 1/64) but the discount is real on purpose:
        # with so few trials the share is not yet trustworthy on its own.
        self.assertGreater(m["free_growth"], 0.5)
        self.assertLessEqual(m["free_growth"], 1.0)
        self.assertEqual(m["inert_positive"], 6)

    def test_more_evidence_moves_free_growth_toward_the_inert_share(self):
        small = ex.mutagenesis(_inert_ledger(6))["free_growth"]
        big = ex.mutagenesis(_inert_ledger(40))["free_growth"]
        self.assertGreater(big, small)
        self.assertAlmostEqual(big, 1.0, places=3)

    def test_resolvable_trials_with_the_gene_on_are_not_inert(self):
        rows = [_row(value=True, delta=(1.0 if i % 2 == 0 else -1.0), cycle=i)
                for i in range(8)]
        m = ex.mutagenesis(rows)
        self.assertEqual(m["inert_trials"], 0)
        self.assertEqual(m["inert_share"], 0.0)
        self.assertEqual(m["free_growth"], 0.0)
        self.assertEqual(m["verdict"], "selection active")

    def test_weak_evidence_discounts_free_growth(self):
        # half the inert trials lost: retention is not distinguishable from noise
        rows = [_row(value=False, delta=(1.0 if i % 2 == 0 else -1.0), cycle=i)
                for i in range(8)]
        m = ex.mutagenesis(rows)
        self.assertEqual(m["inert_trials"], 8)
        self.assertLess(m["free_growth"], 0.15,
                        "free growth must be discounted when the trials did not all win")
        self.assertEqual(m["verdict"], "selection active")

    def test_value_effect_is_the_on_minus_off_differential(self):
        rows = ([_row(value=True, delta=2.0, cycle=i) for i in range(3)]
                + [_row(value=False, delta=0.5, cycle=i) for i in range(3)])
        m = ex.mutagenesis(rows)
        self.assertEqual(m["inert_trials"], 3)
        self.assertAlmostEqual(m["genes"][0]["value_effect"], 1.5, places=4)


class TestAbsenceIsNotCalm(unittest.TestCase):

    def test_no_ledger_yields_no_signal(self):
        m = ex.mutagenesis(None)
        self.assertEqual(m["verdict"], "unavailable")
        self.assertIsNone(m["free_growth"], "an absent ledger must not score 0.0")
        self.assertNotIn("mutagenesis", ex.epistemic_report([])["signals"])

    def test_too_few_rows_is_unavailable_not_active(self):
        m = ex.mutagenesis(_inert_ledger(3))
        self.assertEqual(m["verdict"], "unavailable")
        self.assertIsNone(m["free_growth"])

    def test_signal_appears_only_when_the_ledger_is_supplied(self):
        rep = ex.epistemic_report([], morph_rows=_inert_ledger(6))
        self.assertIn("mutagenesis", rep["signals"])
        self.assertGreater(rep["signals"]["mutagenesis"], 0.5)

    def test_never_raises_on_garbage(self):
        for junk in (None, [], [None], [{}], [{"fitness": "x"}], "nonsense", 42,
                     [{"fitness": 1.0, "baseline_fitness": None}], object()):
            try:
                ex.mutagenesis(junk)
            except Exception as exc:                        # noqa: BLE001
                self.fail("mutagenesis(%r) raised %s: %s"
                          % (junk, type(exc).__name__, exc))


class TestLoadAndSuiteEvidence(unittest.TestCase):

    def test_genetic_load_and_the_wilson_bound(self):
        genome = {"usefulness_floor": 0.15,
                  "genes": [{"name": "a", "usefulness": 0.30},
                            {"name": "b", "usefulness": 0.05}]}
        mutation = {"at": "2026-01-01T00:00:00", "mutants": 30, "killed": 30,
                    "target": "x.py"}
        m = ex.mutagenesis(_inert_ledger(6), genome=genome, mutation=mutation)
        self.assertEqual(m["load"]["below_floor"], ["b"])
        self.assertEqual(m["load"]["share"], 0.5)
        self.assertEqual(m["tests"]["score"], 1.0)
        # 30/30 is NOT "score 1.0" -- with n=30 the honest statement is a bound,
        # and the difference between those two claims is the whole point.
        self.assertEqual(m["tests"]["lower"], 0.8865)

    def test_missing_artifacts_leave_load_and_tests_unset(self):
        m = ex.mutagenesis(_inert_ledger(6))
        self.assertIsNone(m["load"])
        self.assertIsNone(m["tests"])


class TestRegistry(unittest.TestCase):

    def test_mutagen_is_registered_in_the_organ_table(self):
        keys = [o["key"] for o in ex.ORGANS]
        self.assertIn("mutagen", keys)
        self.assertEqual(len(ex.ORGANS), 17,
                         "the organ table gained or lost an entry")
        names = {o["name"] for o in ex.ORGANS}
        self.assertIn("MUTAGEN", names)

    def test_mutagenesis_is_a_weighted_severity_signal(self):
        self.assertIn("mutagenesis", ex.SEVERITY_WEIGHTS)
        weight, _why = ex.SEVERITY_WEIGHTS["mutagenesis"]
        self.assertGreater(weight, 0.0)
        self.assertIn("mutagenesis", ex.__all__)

    def test_panel_declares_the_mutagen_organ(self):
        import exmachina_live_monitor as mon
        names = {n for n, _t, _d in mon.EX_ORGANS}
        self.assertIn("MUTAGEN", names)
        self.assertIn("mutagen", mon._GLYPH_TIERS["ascii"])
        self.assertIn("mutagen", mon._GLYPH_TIERS["unicode"])


class TestRealLedger(unittest.TestCase):
    """Structural checks against the committed artifact (not brittle numbers)."""

    def setUp(self):
        if not os.path.exists(_LEDGER):
            self.skipTest("no morph ledger on this checkout")
        import json
        with open(_LEDGER, encoding="utf-8") as f:
            self.rows = [json.loads(l) for l in f if l.strip()]

    def test_real_ledger_produces_a_verdict(self):
        m = ex.mutagenesis(self.rows)
        self.assertEqual(m["trials"], len(self.rows))
        self.assertIn(m["verdict"], ("free growth", "drift", "selection active"))
        self.assertIsNotNone(m["free_growth"])
        self.assertGreaterEqual(m["free_growth"], 0.0)
        self.assertLessEqual(m["free_growth"], 1.0)

    def test_real_ledger_retention_is_not_a_selection_signal(self):
        m = ex.mutagenesis(self.rows)
        # The point of the organ: near-total retention, which no genuinely
        # selective operator produces.
        self.assertGreater(m["retention"], 0.9)


if __name__ == "__main__":
    unittest.main()
