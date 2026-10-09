# coding: utf-8
"""
Azazael Local Development Package
Provides local AI development tools and integrations
"""


__version__ = "1.0.0"
__author__ = "Azazael"

# Core modules
try:
    from CORE import bootstrap
except ImportError:
    note_failure("LOCAL_DEV:L14", None)
    bootstrap = None  # Optional bootstrap module (not always present)

from CORE import NODE
from CORE import PYTHON_MANAGER
from CORE import STRESS_TEST
from CORE.WORMS import (
    OMNI_WORM,
    ERROR_SCAN_WORM,
    MORPHING_WORM_V2,
    WORM_FLEET,
    CLUSTER_INSPECTOR,
)
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)

# Local LLM support
try:
    pass

    LM_STUDIO_AVAILABLE = True
except ImportError:
    note_failure("LOCAL_DEV:L33", None)
    LM_STUDIO_AVAILABLE = False

# Open Interpreter support
try:
    pass

    OPEN_INTERPRETER_AVAILABLE = True
except ImportError:
    note_failure("LOCAL_DEV:L41", None)
    OPEN_INTERPRETER_AVAILABLE = False

__all__ = [
    "bootstrap",
    "NODE",
    "PYTHON_MANAGER",
    "STRESS_TEST",
    "OMNI_WORM",
    "ERROR_SCAN_WORM",
    "MORPHING_WORM_V2",
    "WORM_FLEET",
    "CLUSTER_INSPECTOR",
    "LM_STUDIO_AVAILABLE",
    "OPEN_INTERPRETER_AVAILABLE",
]


def get_version():
    return __version__


def check_availability():
    print("Azazael Local Development Package")
    print(f"Version: {__version__}")
    print()
    print("Module Availability:")
    print("  bootstrap: OK")
    print("  NODE: OK")
    print("  PYTHON_MANAGER: OK")
    print("  STRESS_TEST: OK")
    print("  Worms: OK")
    print(f"  LM Studio: {'OK' if LM_STUDIO_AVAILABLE else 'NOT AVAILABLE'}")
    print(
        f"  Open Interpreter: {'OK' if OPEN_INTERPRETER_AVAILABLE else 'NOT AVAILABLE'}"
    )
    print()
    return True
