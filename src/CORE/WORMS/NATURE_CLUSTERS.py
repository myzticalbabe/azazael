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

#: Load the root module FROM ITS FILE, under its true name ``NATURE_CLUSTERS``.
#: Two problems meet here. Worm discovery puts ``src/CORE/WORMS`` at
#: ``sys.path[0]`` and imports top-level modules by bare name, so
#: ``import NATURE_CLUSTERS`` resolves to THIS shim (the file executing) and
#: dies on a circular import (measured 2026-10-02: ``cannot import name
#: 'NATURE_DEFINITIONS' from partially initialized module 'NATURE_CLUSTERS'``);
#: that left NatureClusterManager unregistered and ``execute_all`` reported
#: ``Unknown module``. And the registry stores each class's ``__module__`` as
#: its import name, so loading under a synthetic name makes the registry entry
#: unimportable for the smoke tests.
#:
#: Loading by file under the real name solves both: the module object is built
#: from the root file (no name lookup), and its classes report
#: ``__module__ == "NATURE_CLUSTERS"``, which IS importable once this shim has
#: installed it in ``sys.modules``. The guard reuses it only when the cached
#: module really is the root file -- if a caller imported this shim bare, the
#: cached entry is the shim and must be replaced.
_ROOT_NAME = "NATURE_CLUSTERS"

def _is_root_module(module: object) -> bool:
    path = getattr(module, "__file__", None)
    return bool(path) and Path(path).resolve() == _ROOT_FILE

if _is_root_module(sys.modules.get(_ROOT_NAME)):
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
