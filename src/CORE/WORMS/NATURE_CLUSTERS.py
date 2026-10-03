# coding: utf-8
"""Compatibility shim: NATURE_CLUSTERS now lives at the repository root.

The canonical module is ``NATURE_CLUSTERS.py`` at the repo root (it grew there
during the src flattening; the file under ``src/CORE/WORMS/`` was removed from
the index). This import path stayed live, though, in four places:

    METACLUSTER.py                          (CORE.WORMS.NATURE_CLUSTERS)
    _worm_execution_matrix.py               (CORE.WORMS.NATURE_CLUSTERS)
    tools/nature_integration_map.py         (CORE.WORMS.NATURE_CLUSTERS)
    tools/gephi_mesh_pipeline.py            (CORE.WORMS.NATURE_CLUSTERS)

Every one of them wrapped the import in ``try/except ImportError``, so the
break was SILENT: the generator printed ``natures declared : 0`` and produced a
plan with an empty contract-coverage block, and the two executors degraded to
"No natures declared" instead of failing. That is the failure mode this shim
removes -- it re-exports the root module so the existing callers keep working.

New code should import the root module directly::

    from NATURE_CLUSTERS import NATURE_DEFINITIONS
"""

from __future__ import annotations

import sys
from pathlib import Path

# src/CORE/WORMS/NATURE_CLUSTERS.py -> parents[3] is the repository root.
_ROOT = str(Path(__file__).resolve().parents[3])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from NATURE_CLUSTERS import (  # noqa: E402,F401
    NATURE_DEFINITIONS,
    CrossNatureRoute,
    NatureCluster,
    NatureClusterManager,
    NatureResult,
)

__all__ = [
    "NATURE_DEFINITIONS",
    "CrossNatureRoute",
    "NatureCluster",
    "NatureClusterManager",
    "NatureResult",
]
