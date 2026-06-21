# coding: utf-8
"""
CODEX/CORE/matrix_animation.py — DEPRECATION SHIM

This file was an exact byte-for-byte duplicate of the root matrix_animation.py.
It now re-exports from the canonical source: azazael/src/matrix_animation.py

Update your imports from:
    from CODEX.CORE.matrix_animation import ...
to:
    from matrix_animation import ...

This shim will be removed in a future release.
"""

import sys
import warnings
from pathlib import Path

warnings.warn(
    "CODEX.CORE.matrix_animation is deprecated. "
    "Use 'from matrix_animation import ...' instead. "
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

from matrix_animation import *  # noqa: E402, F401
