"""Native azazael ML package.

Owns the eight classical estimator families behind one uniform interface.
Stateless factories only (no module-level mutable state) so the package is
safe under Python 3.14t free-threading: every call builds a fresh estimator.
"""

from ML.estimators import (
    ESTIMATOR_FAMILIES,
    EstimatorSpec,
    fit_score,
    make_estimator,
)

__all__ = [
    "ESTIMATOR_FAMILIES",
    "EstimatorSpec",
    "fit_score",
    "make_estimator",
]
