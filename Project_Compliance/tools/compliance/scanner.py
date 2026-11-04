"""DEPRECATED -- use ``CORE.compliance.scanner`` instead.

This file is a backward-compatibility shim, not an implementation.

Why it exists
-------------
``Project_Compliance/tools/compliance/scanner.py`` was an untracked, orphaned
snapshot of the scanner: 2,185 lines against the canonical module's 2,241, an
identical ``--help``, and a rule table of **20** where the canonical module
carries **21**. Nothing imported it -- ``orchestrator.py`` already imports
``CORE.compliance.scanner`` and ``dashboard_api.py`` imports
``CORE.compliance.scanner_db`` -- and no script or document referenced the path
(only a generated ``graphify-out`` artifact mentioned it). Measured 2026-11-04.

Leaving it in place was the defect: anyone running
``python Project_Compliance/tools/compliance/scanner.py`` got a scanner that was
silently missing a rule, with no signal that a newer one existed.

What it does now
----------------
``import`` re-exports the canonical public names below, and running the path as
a script delegates to the canonical CLI, so an old command line keeps working
and reports the canonical rule set.

Use instead::

    from CORE.compliance.scanner import ASTAntiPatternScanner
"""

from __future__ import annotations

import runpy
import sys
import warnings
from pathlib import Path

#: The repo root's ``src``, resolved from this file rather than assumed from
#: PYTHONPATH: `Project_Compliance/tools/compliance/scanner.py` -> parents[3].
_SRC = Path(__file__).resolve().parents[3] / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

warnings.warn(
    "Project_Compliance/tools/compliance/scanner.py is deprecated. "
    "Use 'from CORE.compliance.scanner import ASTAntiPatternScanner' instead; "
    "this path now re-exports the canonical 21-rule scanner.",
    FutureWarning,
    stacklevel=2,
)

from CORE.compliance.scanner import (  # noqa: E402  (after sys.path setup)
    DEFAULT_EXCLUDES,
    FINDING_EXPLANATIONS,
    FINDING_SEVERITIES,
    FIX_SUGGESTIONS,
    AntiPatternResult,
    ASTAntiPatternScanner,
    reset_scanner,
    run_cli,
    scan_file,
)

__all__ = [
    "DEFAULT_EXCLUDES",
    "FINDING_EXPLANATIONS",
    "FINDING_SEVERITIES",
    "FIX_SUGGESTIONS",
    "AntiPatternResult",
    "ASTAntiPatternScanner",
    "reset_scanner",
    "run_cli",
    "scan_file",
]


if __name__ == "__main__":
    # The path used to be runnable, so it stays runnable -- against the
    # canonical module, which owns the argument parser.
    runpy.run_module("CORE.compliance.scanner", run_name="__main__", alter_sys=True)
