# coding: utf-8
"""interpreter roles for this tree (Engram #1430-half: ci_two_interpreter_gate seam).

Production is the free-threaded 3.15t venv; the GIL sidecar is the SAME
3.15.0rc3 build with the GIL on, so a suite comparison isolates threading
rather than version drift. Both roles are verified live on this host
(2026-10-18): primary reports gil False, sidecar gil True, both carry
pytest 9.x. A missing sidecar file drops the role (returns None) instead
of raising, per the gate's contract.

3.14 RETIREMENT (2026-10-19): the 3.14t free-threaded venv
(``C:/Users/clint/venv-314t``) is RETIRED and archived. It is no longer a
production role and no launcher may pick it. The ONLY sanctioned 3.14
runtime is the 3.14m GIL venv below, for a package that genuinely has no
3.15 build. Anything a 3.15 process needs is installed on 3.15t instead;
resorting to fallback_314() is a deliberate, reported choice, never a
silent ladder rung.

probe() encodes the child-env rule shared with
scripts/ci_two_interpreter_gate.py: a GIL build aborts when PYTHON_GIL=0
is exported, so it is popped for child processes.
"""
from __future__ import annotations

import os
from pathlib import Path

PRIMARY = Path("C:/Azazael/.venvs/py315t/Scripts/python.exe")
GIL_SIDECAR = Path("C:/Azazael/.venvs/py315/Scripts/python.exe")
#: Retired 2026-10-19 — kept as a literal only so a census can name it.
RETIRED_314T = Path("C:/Users/clint/venv-314t/Scripts/python.exe")
#: The one sanctioned 3.14 runtime (GIL, 3.14.5), for what 3.15 cannot load.
FALLBACK_314 = Path("C:/Azazael/.venvs/py314m/Scripts/python.exe")


def primary_python() -> Path:
    """Free-threaded production interpreter (3.15t, GIL off)."""
    return PRIMARY


def gil_python() -> Path | None:
    """Same-version GIL sidecar, or None when its file is absent."""
    return GIL_SIDECAR if GIL_SIDECAR.exists() else None


def fallback_314_python() -> Path | None:
    """Sanctioned 3.14 fallback, or None when its file is absent."""
    return FALLBACK_314 if FALLBACK_314.exists() else None


def roles() -> dict[str, Path]:
    """Resolved roles for callers that must report what they chose."""
    found: dict[str, Path] = {}
    if PRIMARY.exists():
        found["primary"] = PRIMARY
    gil = gil_python()
    if gil is not None:
        found["gil"] = gil
    legacy = fallback_314_python()
    if legacy is not None:
        found["fallback_314"] = legacy
    return found


def probe(env: dict | None = None) -> dict:
    """Child-process env: PYTHON_GIL popped so GIL builds don't abort."""
    clean = dict(os.environ if env is None else env)
    clean.pop("PYTHON_GIL", None)
    return clean

