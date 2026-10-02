# coding: utf-8
"""Rootdir test configuration — applies to EVERY test directory in the repo.

WHY THIS EXISTS (audit 2026-09-21, second occurrence of the same class)
-----------------------------------------------------------------------
`tests/conftest.py` redirects `AZAZAEL_MEMORY_DIR`, `AZAZAEL_GENERATED_DIR`
and `AZAZAEL_ENTRENCHMENT_PATH` so a test cannot write into the live stores
it is testing. But a conftest only applies to its OWN directory subtree, and
this repository has a SECOND test directory:

    pytest.ini:  testpaths = tests

`pytest.ini` confines the normal run to `tests/`, so `src/tests/` is reached
only by IDE test discovery or a direct `pytest src/tests/...` — exactly the
runs nobody watches. `src/tests/` has `__init__.py` and 14 test modules and
had NO conftest, so every redirect written for `tests/` was absent there.

Measured consequence (this file's justification, not a hypothesis):
`src/tests/test_worm_registry.py` defines fixture worm classes named
`FleetOrch`, `NetDiag`, `DivWorm`, `SysMonitor`, `ClockSync`, `BinAnalysis`,
`BatchWorm2/4`, `ShortCooldown`, `MonWorm`, `DiagWorm`, `OnlyWorm` and calls
`SpawnDiversityEngine.record_spawn(...)`, which writes a REAL
`spawn_selected` row via `get_memory_store()`. The live choice tap held:

    608 spawn_selected rows total
      408 written by those fixtures (12 names, NONE of them registered worms)
      200 written by the only real component ever chosen (MetaCluster)

So two thirds of the production "which worm did we choose" record was unit
test fixtures. Anything reading that tap to score a component - including
`CORE.WORMS.expansion.spawn_credit.chosen_but_never_run()` and the
morphogenesis opportunity trigger built on it - would score twelve worms
that do not exist and conclude the fleet is 12 organs short. The previous
scrub of the OUTCOME tap fixed the symptom on one tap; this is the same hole
on the CHOICE tap, and the hole is "a test directory outside tests/".

The fix is placed at the rootdir, not added to `src/tests/`, because the
defect is not "src/tests is special" - it is "a test directory anywhere is
unprotected". A third test directory added later is covered by construction
rather than by remembering.

The env vars are read at IMPORT time by the modules that own them
(`CORE.local_memory` computes `DB_PATH` at import), so they must be set at
collection, before any test module imports. That is why this is module-level
code and not a fixture.

`tests/conftest.py` is unchanged and still works: its redirects are guarded
by `if not os.environ.get(...)`, so with this file setting the vars first
they become deliberate no-ops and its `pytest_unconfigure` correctly skips
removing directories it did not create (it tracks its own override handles).
"""

from __future__ import annotations

import os
import pathlib
import tempfile

# ── Containment pen: generated specialist source ────────────────────
_GENERATED_DIR_OVERRIDE = None
if not os.environ.get("AZAZAEL_GENERATED_DIR"):
    _GENERATED_DIR_OVERRIDE = tempfile.mkdtemp(prefix="azazael_generated_")
    os.environ["AZAZAEL_GENERATED_DIR"] = _GENERATED_DIR_OVERRIDE

# ── Entrenchment snapshot (GrayQueen census baseline) ───────────────
_ENTRENCHMENT_OVERRIDE = None
if not os.environ.get("AZAZAEL_ENTRENCHMENT_PATH"):
    _ENTRENCHMENT_OVERRIDE = pathlib.Path(
        tempfile.mkdtemp(prefix="azazael_entrenchment_")) / "entrenchment.json"
    os.environ["AZAZAEL_ENTRENCHMENT_PATH"] = str(_ENTRENCHMENT_OVERRIDE)

# ── Memory store: the outcome AND choice telemetry taps ─────────────
_MEMORY_DIR_OVERRIDE = None
if not os.environ.get("AZAZAEL_MEMORY_DIR"):
    _MEMORY_DIR_OVERRIDE = tempfile.mkdtemp(prefix="azazael_memory_")
    os.environ["AZAZAEL_MEMORY_DIR"] = _MEMORY_DIR_OVERRIDE


def pytest_unconfigure(config):
    """Remove the session's redirected pen, snapshot and store."""
    import shutil

    if _GENERATED_DIR_OVERRIDE:
        shutil.rmtree(_GENERATED_DIR_OVERRIDE, ignore_errors=True)
    if _ENTRENCHMENT_OVERRIDE:
        shutil.rmtree(str(_ENTRENCHMENT_OVERRIDE.parent), ignore_errors=True)
    if _MEMORY_DIR_OVERRIDE:
        shutil.rmtree(_MEMORY_DIR_OVERRIDE, ignore_errors=True)
