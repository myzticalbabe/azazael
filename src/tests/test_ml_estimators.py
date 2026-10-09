# coding: utf-8
"""
Unit tests for ML.estimators - native azazael wrappers for the eight
classical estimator families.
"""

import sys
import unittest
import warnings
from pathlib import Path

# Ensure azazael/src is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ML.estimators import (
    ESTIMATOR_FAMILIES,
    describe,
    fit_score,
    make_estimator,
)
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


def _blobs():
    from sklearn.datasets import make_classification, make_regression

    Xc, yc = make_classification(n_samples=200, n_features=10, random_state=0)
    Xr, yr = make_regression(n_samples=200, n_features=10, random_state=0)
    return (Xc, yc), (Xr, yr)


class TestRegistry(unittest.TestCase):
    def test_eight_families(self):
        self.assertEqual(len(ESTIMATOR_FAMILIES), 8)
        for name in (
            "linear_regression",
            "logistic_regression",
            "knn",
            "svm",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "neural_network",
        ):
            self.assertIn(name, ESTIMATOR_FAMILIES)

    def test_unknown_family_raises(self):
        with self.assertRaises(KeyError):
            make_estimator("nope")
        with self.assertRaises(KeyError):
            describe("nope")

    def test_overrides_applied(self):
        est = make_estimator("knn", n_neighbors=3)
        self.assertEqual(est.n_neighbors, 3)

    def test_fresh_instances_independent(self):
        self.assertIsNot(make_estimator("svm"), make_estimator("svm"))


class TestFunctional(unittest.TestCase):
    def test_all_families_warning_free(self):
        (Xc, yc), (Xr, yr) = _blobs()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            for family in ESTIMATOR_FAMILIES:
                X, y = (Xr, yr) if family == "linear_regression" else (Xc, yc)
                est, score = fit_score(family, X, y)
                self.assertGreaterEqual(score, 0.9, family)
                self.assertEqual(len(est.predict(X[:5])), 5)

    def test_neural_network_converges(self):
        (Xc, yc), _ = _blobs()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _, score = fit_score("neural_network", Xc, yc)
        self.assertEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
