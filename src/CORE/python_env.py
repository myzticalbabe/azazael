# coding: utf-8
"""interpreter roles for this tree (Engram #1430-half: ci_two_interpreter_gate seam).

Production is the free-threaded 3.15t venv; the GIL sidecar is the SAME
3.15.0rc3 build with the GIL on, so a suite comparison isolates threading
rather than version drift. Both roles are verified live on this host
(2026-10-18): primary reports gil False, sidecar gil True, both carry
pytest 9.x. A missing sidecar file drops the role (returns None) instead
of raising, per the gate's contract.

probe() encodes the child-env rule shared with
scripts/ci_two_interpreter_gate.py: a GIL build aborts when PYTHON_GIL=0
is exported, so it is popped for child processes.
"""
from __future__ import annotations

import os
from pathlib import Path

PRIMARY = Path("C:/Azazael/.venvs/py315t/Scripts/python.exe")
GIL_SIDECAR = Path("C:/Azazael/.venvs/py315/Scripts/python.exe")


def primary_python() -> Path:
    """Free-threaded production interpreter (3.15t, GIL off)."""
    return PRIMARY


def gil_python() -> Path | None:
    """Same-version GIL sidecar, or None when its file is absent."""
    return GIL_SIDECAR if GIL_SIDECAR.exists() else None


def probe(env: dict | None = None) -> dict:
    """Child-process env: PYTHON_GIL popped so GIL builds don't abort."""
    clean = dict(os.environ if env is None else env)
    clean.pop("PYTHON_GIL", None)
    return clean
