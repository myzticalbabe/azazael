# coding: utf-8
"""
CODEX/CORE/QL_FILE_OPTIMIZER.py — DEPRECATION SHIM

This file was an exact byte-for-byte duplicate of the root QL_FILE_OPTIMIZER.py.
It now re-exports from the canonical source: azazael/src/QL_FILE_OPTIMIZER.py

Update your imports from:
    from CODEX.CORE.QL_FILE_OPTIMIZER import ...
to:
    from QL_FILE_OPTIMIZER import ...

This shim will be removed in a future release.
"""

import sys
import warnings
from pathlib import Path

warnings.warn(
    "CODEX.CORE.QL_FILE_OPTIMIZER is deprecated. "
    "Use 'from QL_FILE_OPTIMIZER import ...' instead. "
    "This shim will be removed in a future release.",
    UserWarning,
    stacklevel=2,
)

_src_dir = Path(__file__).resolve().parent.parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
# Remove CORE directory from path to prevent circular self-import
_own_dir = str(Path(__file__).resolve().parent)
if _own_dir in sys.path:
    sys.path.remove(_own_dir)

from QL_FILE_OPTIMIZER import *  # noqa: E402, F401
