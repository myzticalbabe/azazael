import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "ml_platforms"))

# coding: utf-8
"""
Permanent Load

Module for ml_platforms functionality.

Functions:
    - debug_all_errors()
    - excepthook()

Usage:
    >>> import PERMANENT_LOAD
    >>> PERMANENT_LOAD.debug_all_errors()

Author: Auto-generated
Date: 2026-02-10
"""

# coding: utf-8
"""
PERMANENT AUTO-LOAD COMMAND FOR LM STUDIO
Copy-paste this entire block into LM Studio Python interpreter
"""

import sys

# 1. Add ML platforms to path PERMANENTLY
ML_PATH = Path.home() / "Desktop" / "Azazael" / "ml_platforms"
if ML_PATH not in sys.path:
    sys.path.insert(0, ML_PATH)
    # Try to persist via user sitecustomize
    try:
        site_path = os.path.join(os.path.expanduser("~"), "sitecustomize.py")
        with open(site_path, "a") as f:
            f.write(f"\nimport sys\nsys.path.insert(0, r'{ML_PATH}')\n")
        print("[OK] Persisted to user sitecustomize.py")
    except Exception:
        pass

# 2. Import all ML platform tools
try:
    from lm_studio_integration import (
        list_platforms,
    )

    print("[OK] All ML tools imported")
except Exception as e:
    print(f"[WARN] Import error: {e}")


# 3. Create global error debugger
def debug_all_errors():
    """Debug any ML error automatically."""
    import traceback

    def excepthook(type, value, tb):
        print("\n" + "=" * 60)
        print("ML ERROR DETECTED - AUTO DEBUG")
        print("=" * 60)
        print(f"\nError: {type.__name__}: {value}\n")
        print("Traceback:")
        print("-" * 40)
        traceback.print_exception(type, value, tb)
        print("-" * 40)

        # Auto-suggest fixes
        err_msg = str(value).lower()
        fixes = []

        if "cuda" in err_msg and "memory" in err_msg:
            fixes.append("FIX: Reduce batch size or use gradient accumulation")
            fixes.append("FIX: set model.to('cpu') instead of GPU")
        elif "shape mismatch" in err_msg:
            fixes.append("FIX: Use tensor.reshape() or tensor.view()")
            fixes.append("FIX: Check input dimensions")
        elif "dtype" in err_msg:
            fixes.append("FIX: Use .float() or .long() to convert types")
        elif "module not found" in err_msg:
            fixes.append("FIX: pip install the-missing-package")
        elif "nan" in err_msg:
            fixes.append("FIX: Check data normalization")
            fixes.append("FIX: Add gradient clipping")
        elif "onnx" in err_msg:
            fixes.append("FIX: Use symbolic_trace or skip unsupported ops")

        if fixes:
            print("\nAuto-suggested fixes:")
            for f in fixes:
                print(f"  {f}")
        else:
            print("\nNo auto-fix found. Check documentation.")

        print("=" * 60)

    sys.excepthook = excepthook
    print("[OK] Global error debugger installed")


# 4. Run auto-load
print("\n" + "=" * 60)
print("ML PLATFORMS AUTO-LOADED")
print("=" * 60)
list_platforms()
print("\nAvailable commands:")
print("  convert(arr, 'pytorch')  # Convert tensors")
print("  debug('error message')   # Debug errors")
print("  optimize('vmap')         # Get patterns")
print("  track_experiment('name') # Start MLflow")
print("  tensor_info(tensor)      # Show tensor info")
print("=" * 60 + "\n")

# Enable debugging
debug_all_errors()
print("[OK] Ready to debug errors automatically!\n")
