#!/usr/bin/env python3
"""
DEPRECATION SHIM — Re-exports from canonical location.

Canonical source: AZAZAEL_TOOLKIT/azazael_toolkit.py
This shim exists for backward compatibility.
Please update imports to use the canonical path.
"""

import warnings
import sys
from pathlib import Path

# Remove this shim's directory from sys.path to avoid circular import
_own_dir = str(Path(__file__).resolve().parent)
if _own_dir in sys.path:
    sys.path.remove(_own_dir)

# Add the canonical parent directory
_canonical_dir = str(Path(__file__).resolve().parent.parent / "AZAZAEL_TOOLKIT")
if _canonical_dir not in sys.path:
    sys.path.insert(0, _canonical_dir)

warnings.warn(
    "TOOLS/azazael_toolkit.py is deprecated. "
    "Use AZAZAEL_TOOLKIT/azazael_toolkit.py instead.",
    DeprecationWarning,
    stacklevel=2,
)

from azazael_toolkit import main
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

__all__ = ["main"]
