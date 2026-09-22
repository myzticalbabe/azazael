# coding: utf-8
"""Global test configuration — Python 3.14t free-threading environment constraints.

Loads BEFORE any test module imports. Sets thread-limiting env vars to prevent
C-extension race conditions (OpenBLAS MemoryError, chardet import crashes, etc.)
that occur under Python 3.14 free-threading builds.

See: Error #156, Lesson #82, azazael-fix-python-314t skill.
"""

import os
import pathlib
import sys
import tempfile
import threading

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

# ── Entrenchment snapshot (colour queens, 2026-09-17) ───────────────
# `GrayQueenWorm.detect()` persists its census snapshot so the NEXT session can
# report a delta instead of a total. `SpineCycleWorm._governance_stage()` calls
# it on every cycle, so without a redirect a test run would write
# `NEURAL_MESH_ENTRENCHMENT.json` into the repository it is testing — and would
# also overwrite the operator's real baseline, destroying the diff it exists to
# produce. Same redirect, same reason as the containment pen above.
_ENTRENCHMENT_OVERRIDE = None
if not os.environ.get("AZAZAEL_ENTRENCHMENT_PATH"):
    _ENTRENCHMENT_OVERRIDE = pathlib.Path(
        tempfile.mkdtemp(prefix="azazael_entrenchment_")) / "entrenchment.json"
    os.environ["AZAZAEL_ENTRENCHMENT_PATH"] = str(_ENTRENCHMENT_OVERRIDE)

# ── Memory store isolation (audit 2026-09-21) ───────────────────────
# The SAME hole the spine-state fixture below was written for, still open for
# the memory store. `_record_cluster_worm_telemetry` calls
# `get_memory_store()`, so `tests/test_clusterworms_unit.py` and
# `tests/test_parallel_integration.py` — which execute worms literally named
# `NONEXISTENT` and `NONEXISTENT_RETRY` — wrote their failures into the
# DEVELOPER'S live `~/.azazael/memory_store.db` as if they were real fleet
# telemetry. Measured 2026-09-21: 45 such rows (36 + 9, all failing) sitting in
# the production outcome tap, plus a `TAPTEST` row, where any learner reading
# per-worm reliability would grade them as genuine executions.
#
# Must be set BEFORE `CORE.local_memory` is imported, because that module
# computes `DB_PATH` from this env var at import time — the same
# set-at-collection-reason as the two redirects above. Global rather than
# opt-in, for the reason already stated there: "remember to patch this" is not
# a mechanism.
_MEMORY_DIR_OVERRIDE = None
if not os.environ.get("AZAZAEL_MEMORY_DIR"):
    _MEMORY_DIR_OVERRIDE = tempfile.mkdtemp(prefix="azazael_memory_")
    os.environ["AZAZAEL_MEMORY_DIR"] = _MEMORY_DIR_OVERRIDE


# ── Memory DB path restore (audit 2026-09-22) ───────────────────────
# The override above pins `AZAZAEL_MEMORY_DIR` for the session, but every module
# that derives a DB path from it computes that path ONCE, at import, into a
# module global (`CORE/direct_memory.py:73  DB_PATH = _get_db_path()`, same shape
# in `local_memory`, `record_session`, `MemoryBus`). Legacy unittest-style suites
# redirect themselves by mutating BOTH:
#
#     os.environ["AZAZAEL_MEMORY_DIR"] = str(tmpdir)      # setUp
#     direct_memory.DB_PATH = direct_memory._get_db_path()
#     ...
#     shutil.rmtree(str(tmpdir))                          # tearDown
#
# ...and restore only the env var. The global is left pointing INTO THE DELETED
# temp dir, so every later `DirectMemory()` in the process dies:
#
#   RuntimeError: Failed to initialize database at
#   C:\Users\clint\AppData\Local\Temp\tmp_1cocc4t\memory_store.db:
#   unable to open database file
#
# Measured 2026-09-22 on the aggregate suite (52 failed / 3,628 passed): four
# files leak this way (`test_cli`, `test_doctor`, `test_concurrency_200`,
# `test_perf*`) while the failures land in a DIFFERENT file
# (`test_cross_domain_integration::test_cd1_record_event`,
# `test_worm_smoke::test_every_worm_instantiable` -> ParallelInferenceWorm).
# Reproduced in 18s with:
#
#   pytest tests/test_cli.py tests/test_doctor.py \
#          tests/test_cross_domain_integration.py::test_cd1_record_event
#
# Every one of those files passes when run alone, which is why per-file suites
# and per-file CI never saw it. Restoring after EVERY test — autouse, not
# opt-in — is the same mechanism as the other isolation blocks in this file, for
# the same reason: "remember to patch this" is not a mechanism.
_MEMORY_DIR_BASELINE = os.environ.get("AZAZAEL_MEMORY_DIR", "")

#: (module, that module's own zero-arg resolver, the global it fills).
_MEMORY_DB_RESOLVERS = (
    ("CORE.direct_memory", "_get_db_path", "DB_PATH"),
    ("CORE.local_memory", "_get_store_path", "DB_PATH"),
    ("CORE.record_session", "_get_db_path", "DB_PATH"),
    ("CORE.MemoryBus", "_get_memorybus_db_path", "_MEMORYBUS_DB_PATH"),
)

#: Modules that cache MORE than one value from the env dir, so one resolver
#: cannot express the restore: they own a reloader that recomputes all of them.
_MEMORY_DB_RELOADERS = (
    ("CORE.backup", "_reload_paths"),
    ("CORE.cd3_exporter", "_reload_paths"),
)

#: Modules that cache a path read from `AZAZAEL_MEMORY_DIR` at import time.
#: `tests/test_memory_dir_caching.py` rediscovers this set by AST and FAILS when
#: a module is missing here, so the list cannot silently rot.
MEMORY_DIR_CACHING_MODULES = tuple(
    [entry[0] for entry in _MEMORY_DB_RESOLVERS]
    + [entry[0] for entry in _MEMORY_DB_RELOADERS]
)


@pytest.fixture(autouse=True)
def _restore_memory_db_globals():
    """Put the memory dir and every derived DB-path global back after a test.

    Only touches modules that are already imported, so a suite that never
    reaches memory code pays nothing. The env var is restored FIRST, because each
    resolver recomputes from it.
    """
    yield
    if _MEMORY_DIR_BASELINE:
        os.environ["AZAZAEL_MEMORY_DIR"] = _MEMORY_DIR_BASELINE
    else:
        os.environ.pop("AZAZAEL_MEMORY_DIR", None)
    for _mod_name, _resolver, _attr in _MEMORY_DB_RESOLVERS:
        _module = sys.modules.get(_mod_name)
        if _module is None:
            continue
        _fn = getattr(_module, _resolver, None)
        if _fn is not None:
            setattr(_module, _attr, _fn())
    for _mod_name, _reloader in _MEMORY_DB_RELOADERS:
        _module = sys.modules.get(_mod_name)
        if _module is None:
            continue
        _fn = getattr(_module, _reloader, None)
        if _fn is not None:
            _fn()


def pytest_unconfigure(config):
    """Remove the session's redirected containment pen, snapshot, and store."""
    import shutil

    if _GENERATED_DIR_OVERRIDE:
        shutil.rmtree(_GENERATED_DIR_OVERRIDE, ignore_errors=True)
    if _ENTRENCHMENT_OVERRIDE:
        shutil.rmtree(str(_ENTRENCHMENT_OVERRIDE.parent), ignore_errors=True)
    if _MEMORY_DIR_OVERRIDE:
        shutil.rmtree(_MEMORY_DIR_OVERRIDE, ignore_errors=True)


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
class _SharedWriteToken:
    """Process-wide stand-in for `sentinel_enforcer._GATED_CALL`.

    The real token is `threading.local()` (`sentinel_enforcer.py:40`) and the
    audit hook reads it per thread (`:53`). This one is deliberately SHARED, so a
    permit granted on the main thread also covers threads the code under test
    starts. A test that wants to observe blocking still can: it sets
    `_GATED_CALL.is_active = False` on this same object.
    """

    is_active = True


#: `AZAZAEL_TEST_SHARED_PERMIT=0` keeps the REAL `threading.local()` token, so
#: the production permit-carrying is what makes worker writes pass.
_SHARED_PERMIT_ENABLED = os.environ.get(
    "AZAZAEL_TEST_SHARED_PERMIT", "1").strip().lower() not in ("0", "false", "no")


def _permit_sentinel_writes() -> bool:
    """Latch the sentinel write token open if the guard is armed.

    Returns True when the guard was found (so the caller can distinguish
    "permitted" from "not armed yet"). The latch is deliberately not restored:
    see `pytest_runtest_setup` below.
    """
    module = sys.modules.get("CORE.sentinel_enforcer")
    token = getattr(module, "_GATED_CALL", None) if module is not None else None
    if token is None:
        return False
    token.is_active = True
    # The latch above only covers the THREAD that ran it. Any worker thread the
    # code under test starts arrives with `is_active` unset and is blocked.
    # Measured 2026-09-22: `fs_probe.bounded_subprocess_output` runs its child on
    # a `bounded-subprocess` thread and opens `tempfile.TemporaryFile()` there:
    #
    #   {"ok": false, "out": "", "timeout": false,
    #    "error": "CRITICAL: Unauthorized write to
    #              C:\\Users\\clint\\AppData\\Local\\Temp. All edits MUST route..."}
    #
    # so every delegated probe answered `_UNANSWERED` and returned None. That is
    # the whole of `test_fs_probe_backend`'s 10 aggregate failures, reproduced in
    # 4 seconds with `pytest tests/test_compliance_step45_init.py
    # tests/test_fs_probe_backend.py` (10 failed / 28 passed) while every one of
    # those tests passes alone. Swapping the thread-local for a shared token makes
    # the session permit hold for every thread. It is a test-environment change;
    # the guard's own semantics are untouched, and the production consequence of
    # the thread-locality is recorded separately (Error #197).
    # Belt-and-braces, and now provably redundant for the probe path:
    # `fs_probe._carried_permit` carries the starter's permit onto the worker
    # (production fix, guarded by `tests/test_sentinel_thread_permit.py`), so the
    # delegated probes answer without this swap. Set
    # `AZAZAEL_TEST_SHARED_PERMIT=0` to run the suite against the real
    # thread-local token and prove it. The swap stays ON by default until a full
    # run with it off is green, because other legacy suites write from worker
    # threads through paths this fix does not cover.
    if _SHARED_PERMIT_ENABLED and isinstance(token, threading.local):
        module._GATED_CALL = _SharedWriteToken()
    return True


# ── Sentinel write-guard: armed BEFORE any fixture of any scope ─────
# The block above fixes the guard leaking into per-test temp writes, but its
# fixture is FUNCTION-scoped, and pytest sets up module/class-scoped fixtures
# FIRST. So a module-scoped fixture that imports a script which opens its log
# file at import time (e.g. `scripts/evolution_cycle.py:48`) is blocked before
# the function-scoped permit ever runs. Measured 2026-09-22 on a full-suite run:
# 207 `PermissionError: CRITICAL: Unauthorized write` — 69 collection errors in
# `test_evolution_gates.py` (61) and `test_import_map.py` (8) and a share of the
# 72 failures, while every one of those files passed when run alone.
#
# `pytest_runtest_setup` is called before fixture setup of ANY scope, which is
# the earliest hook a conftest gets, and the latch is left ON for the session:
# the guard exists to gate the assistant's tool writes, not a test process's
# temp/log files, and nothing under `tests/` asserts that it blocks. A test that
# wants to observe blocking can still set `_GATED_CALL.is_active = False` itself.
def pytest_runtest_setup(item):  # noqa: ARG001 - pytest hook signature
    _permit_sentinel_writes()


@pytest.fixture(autouse=True)
def _permit_sentinel_test_writes():
    """Hold the sentinel write token open for the duration of each test."""
    _permit_sentinel_writes()
    yield

# ── Standalone-script runner (audit 2026-09-21) ─────────────────────
# Seven files under `tests/` are named `test_*.py` and are STANDALONE SCRIPTS:
# every assertion in them sits under `if __name__ == "__main__"`, with `PASS`/
# `FAIL` counters and `sys.exit(1)` on failure. pytest therefore collected ZERO
# tests from them and reported `rc=5`, "no tests collected" -- measured
# 2026-09-21, `test_algorithm_coverage`, `test_cloud_tab_error_handling`,
# `test_full_integration`, `test_observability`, `test_provider_failover`,
# `test_secrets_manager_thread_safety` and `test_calc`.
#
# The consequence is worth stating plainly: **none of those checks has ever run
# in CI**, and the files look green because they fail to collect rather than
# because they pass. Rewriting each script body into test functions would be six
# separate refactors of working code; running the script the way its author
# intended, and asserting its exit code, makes the existing assertions execute
# today and does not touch the logic.
@pytest.fixture
def run_standalone_script():
    """Run a `tests/test_*.py` script and return its CompletedProcess."""
    import subprocess

    def _run(path: str, timeout: float = 300.0):
        return subprocess.run(
            [sys.executable, str(path)],
            capture_output=True, text=True, timeout=timeout, cwd=str(pathlib.Path(__file__).parent.parent),
        )

    return _run


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
