# coding: utf-8
"""Global test configuration — Python 3.14t free-threading environment constraints.

Loads BEFORE any test module imports. Sets thread-limiting env vars to prevent
C-extension race conditions (OpenBLAS MemoryError, chardet import crashes, etc.)
that occur under Python 3.14 free-threading builds.

See: Error #156, Lesson #82, azazael-fix-python-314t skill.
"""

import os
import sys

import pytest

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

# ── Morphogenesis containment pen (audit 2026-09-15, finding #3) ────
# `SpineCycleWorm.run_cycle(apply=True)` can stage generated specialist
# source into `CORE/WORMS/expansion/generated/`. Tests must never write
# source into the tree they are testing, so the pen is redirected to a
# session temp dir. This is the same override an installed deployment uses
# when the package directory is read-only.
_GENERATED_DIR_OVERRIDE = None
if not os.environ.get("AZAZAEL_GENERATED_DIR"):
    import tempfile

    _GENERATED_DIR_OVERRIDE = tempfile.mkdtemp(prefix="azazael_generated_")
    os.environ["AZAZAEL_GENERATED_DIR"] = _GENERATED_DIR_OVERRIDE


def pytest_unconfigure(config):
    """Remove the session's redirected containment pen."""
    import shutil

    if _GENERATED_DIR_OVERRIDE:
        shutil.rmtree(_GENERATED_DIR_OVERRIDE, ignore_errors=True)


# ── Spine state isolation (audit 2026-09-15) ────────────────────────
# `spine_registry._STATE_FILE` defaults to the DEVELOPER'S live store at
# `~/.azazael/spine_state.json`. Isolation was opt-in per test file, so any
# test that recorded an outcome and then called `save_spine_state()` wrote the
# real store. Verified for real: running `tests/test_spine_mesh.py` against a
# live 76-record homeostat replaced it with synthetic fixtures (`mesh:W0`,
# `learning:W1`) — hours of accumulated learning, gone, with no error.
#
# The redirect is global rather than opt-in for the same reason the
# containment pen above is: a test must not be able to damage the machine it
# is testing, and "remember to patch this" is not a mechanism.
#
# Note this patches the module attributes, so a test that opens the real path
# by string (e.g. `test_aoa_routing_telemetry`'s read-only provenance check)
# still reads the real file, as intended.
@pytest.fixture(autouse=True)
def _isolate_spine_state(tmp_path_factory, monkeypatch):
    """Redirect the spine's durable store to a per-test temp dir."""
    try:
        from CORE import spine_registry as _sr
    except Exception:  # spine not importable in this environment
        yield
        return
    base = tmp_path_factory.mktemp("spine_state")
    monkeypatch.setattr(_sr, "_STATE_FILE", base / "spine_state.json")
    monkeypatch.setattr(_sr, "_GOSSIP_DIR", base / "gossip")
    yield


@pytest.fixture(autouse=True)
def _isolate_hlc_clock(monkeypatch):
    """Give every test a pristine hybrid logical clock.

    `CORE/hlc.py` is a process-wide singleton, and it *adopts* a peer's physical
    time whenever that peer is within `MAX_DRIFT_MS` — which is correct HLC
    behaviour, not a bug. The consequence for a test session is that the clock
    advances and then *stays* advanced: once a test observes a stamp ~200s ahead
    (the clock-trust tests do exactly that, on purpose), the singleton's
    `_physical` sits ~200s ahead of wall clock, so a later test that publishes an
    incumbent and then offers a stamp "2 seconds in the future" is offering one
    that is genuinely *older* than the incumbent. It then loses the merge, and
    the failure is order-dependent:

        test_mesh_fabric_gaps.py::test_fabric_state_merges_by_recency  ->  passes
          alone, fails when the clock-trust tests run first in the session.

    `reset_remote_view()` cannot fix this: it deliberately clears only the
    observability fields, because un-monotoning the logical clock is the exact
    failure mode the module exists to prevent. Installing a fresh instance is the
    honest isolation — the assertion holds on a clock that has seen nothing.

    Global rather than opt-in for the same reason as the fixtures above.
    """
    try:
        from CORE import hlc as _H
    except Exception:  # hlc not importable in this environment
        yield
        return
    monkeypatch.setattr(_H, "_HLC", _H.HybridLogicalClock(), raising=False)
    yield


# ── Sentinel write-guard isolation (audit 2026-09-16) ───────────────
# `CORE/sentinel_enforcer.py` installs a *process-global* `sys.addaudithook` at
# import time that raises PermissionError on any write whose mode contains
# w/a/+/x unless a thread-local token is set. `CORE/compliance/orchestrator.py`
# imports it in order to arm the hook, so the first suite that builds a
# ComplianceOrchestrator arms the guard for the remainder of the session and
# every later test that writes a temp file dies. Verified for real:
#
#   pytest tests/test_compliance_step45_init.py tests/test_compliance_auditor.py
#     -> test_halt_flag_file: PermissionError: CRITICAL: Unauthorized write
#
# The same failure reproduces against the pre-change copy of that suite, so it
# is an isolation defect rather than a regression. The guard exists to gate the
# assistant's tool writes; a test writing a temp file is not what it guards.
# Nothing under tests/ asserts that the hook blocks, so holding the token open
# cannot mask a real check. The previous value is restored afterwards, so a test
# that wants to assert blocking can switch it off and still see the guard.
#
# Deliberately lazy: it only engages once the hook has actually been armed, so a
# suite that never touches compliance code keeps running exactly as before.
@pytest.fixture(autouse=True)
def _permit_sentinel_test_writes():
    """Hold the sentinel write token open for the duration of each test."""
    module = sys.modules.get("CORE.sentinel_enforcer")
    token = getattr(module, "_GATED_CALL", None) if module is not None else None
    if token is None:
        yield
        return
    previous = getattr(token, "is_active", False)
    token.is_active = True
    try:
        yield
    finally:
        token.is_active = previous

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
