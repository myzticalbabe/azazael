# coding: utf-8
"""Global test configuration — Python 3.14t free-threading environment constraints.

Loads BEFORE any test module imports. Sets thread-limiting env vars to prevent
C-extension race conditions (OpenBLAS MemoryError, chardet import crashes, etc.)
that occur under Python 3.14 free-threading builds.

See: Error #156, Lesson #82, azazael-fix-python-314t skill.
"""

import os
import sys

# ── Constrain C-extension thread pools ──────────────────────────
# Python 3.14t free-threading removes the GIL, exposing thread-unsafe
# C-libraries that aggressively pre-allocate memory based on CPU count.
# Force single-threaded mode to prevent allocation failures and deadlocks.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("BLIS_NUM_THREADS", "1")

# ── Detect Python 3.14t free-threading ─────────────────────────
try:
    _IS_FREE_THREADED = not sys._is_gil_enabled()
except Exception:
    _IS_FREE_THREADED = "t" in sys.version.lower()


def is_314t() -> bool:
    """Return True if running under Python 3.14 free-threading build."""
    return _IS_FREE_THREADED


# ── CD4: nuitka_incompatible marker registration ────────────────────
def pytest_configure(config):
    """Register custom pytest markers.

    Registers nuitka_incompatible marker per CD4 spec for tests that
    cannot run under Nuitka compiled (.exe or --module) mode.
    Stage 3 of the CD4 pipeline automatically skips these tests via:
        pytest -m "not nuitka_incompatible"
    """
    try:
        from CORE.cd4_pipeline import register_nuitka_marker
        register_nuitka_marker(config)
    except ImportError:
        # Fallback registration if cd4_pipeline module not importable
        config.addinivalue_line(
            "markers",
            "nuitka_incompatible: Mark test as incompatible with Nuitka "
            "compiled execution. Skipped in CD4 pipeline Stage 3.",
        )
