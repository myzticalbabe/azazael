# coding: utf-8
"""
Azazael Local Development Package
Provides local AI development tools and integrations
"""

import os
import sys
from pathlib import Path

__version__ = "1.0.0"
__author__ = "Azazael"

# Core modules
from . import bootstrap
from . import NODE
from .CORE import PYTHON_MANAGER
from .CORE import STRESS_TEST
from .CORE.WORMS import (
    OMNI_WORM,
    ERROR_SCAN_WORM,
    MORPHING_WORM_V2,
    WORM_FLEET,
    CLUSTER_INSPECTOR,
)

# Local LLM support
try:
    from .ORCHESTRATION.ml_platforms import lm_studio_client

    LM_STUDIO_AVAILABLE = True
except ImportError:
    LM_STUDIO_AVAILABLE = False

# Open Interpreter support
try:
    import interpreter

    OPEN_INTERPRETER_AVAILABLE = True
except ImportError:
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
    print(f"  bootstrap: OK")
    print(f"  NODE: OK")
    print(f"  PYTHON_MANAGER: OK")
    print(f"  STRESS_TEST: OK")
    print(f"  Worms: OK")
    print(f"  LM Studio: {'OK' if LM_STUDIO_AVAILABLE else 'NOT AVAILABLE'}")
    print(
        f"  Open Interpreter: {'OK' if OPEN_INTERPRETER_AVAILABLE else 'NOT AVAILABLE'}"
    )
    print()
    return True
