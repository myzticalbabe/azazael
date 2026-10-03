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
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

# src/CORE/WORMS/NATURE_CLUSTERS.py -> parents[3] is the repository root.
_ROOT_FILE = Path(__file__).resolve().parents[3] / "NATURE_CLUSTERS.py"

#: Load the root module by FILE, not by the name ``NATURE_CLUSTERS``. Worm
#: discovery puts ``src/CORE/WORMS`` at ``sys.path[0]``, so a bare
#: ``import NATURE_CLUSTERS`` from inside this shim resolves to the shim itself
#: -- the file that is executing -- and dies on a circular import (measured
#: 2026-10-02: ``cannot import name 'NATURE_DEFINITIONS' from partially
#: initialized module 'NATURE_CLUSTERS'``). That left NatureClusterManager
#: unregistered, so ``execute_all`` reported ``Unknown module``. Loading the
#: file under a private name is immune to whichever directory wins the name
#: lookup, and the ``sys.modules`` guard keeps the root module single.
_ROOT_NAME = "_azazael_root_nature_clusters"
if _ROOT_NAME in sys.modules:
    _root = sys.modules[_ROOT_NAME]
else:
    _spec = spec_from_file_location(_ROOT_NAME, _ROOT_FILE)
    if _spec is None or _spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load NATURE_CLUSTERS from {_ROOT_FILE}")
    _root = module_from_spec(_spec)
    sys.modules[_ROOT_NAME] = _root
    _spec.loader.exec_module(_root)

NATURE_DEFINITIONS = _root.NATURE_DEFINITIONS
CrossNatureRoute = _root.CrossNatureRoute
NatureCluster = _root.NatureCluster
NatureClusterManager = _root.NatureClusterManager
NatureResult = _root.NatureResult

__all__ = [
    "NATURE_DEFINITIONS",
    "CrossNatureRoute",
    "NatureCluster",
    "NatureClusterManager",
    "NatureResult",
]
