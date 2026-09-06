# coding: utf-8
"""Unit tests for worm registry importability validation (startup check).

Covers:
  - validate_registry_importable(): all-pass on healthy registry
  - _resolve_worm_import_module(): package-qualified, bare WORMS, bare src-root,
    worms.* package, and empty info
  - validate_registry_importable() with a broken entry (unimportable module,
    missing class) → flagged in `broken` and `valid=False`
  - startup_warm wiring: _run_registry_validation stores a result;
    get_registry_validation() returns it; cache_status() surfaces it
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from CORE.worm_registry import (
    WORM_REGISTRY,
    _registry_lock,
    _resolve_worm_import_module,
    register_worm,
    repair_registry,
    reset_registry,
    validate_registry_importable,
)


# ── _resolve_worm_import_module ─────────────────────────────────────

def test_resolve_package_qualified_passthrough():
    """CORE.WORMS.X and worms.* module refs pass through unchanged."""
    assert _resolve_worm_import_module({"module": "CORE.WORMS.SYSTEMZ"}) == "CORE.WORMS.SYSTEMZ"
    assert _resolve_worm_import_module({"module": "worms.nmap_scanner"}) == "worms.nmap_scanner"


def test_resolve_bare_worms_module():
    """Bare module name + CORE/WORMS source file → CORE.WORMS.<name>."""
    info = {
        "module": "CLUSTERWORMS",
        "source_file": "C:/Users/clint/azazael/src/CORE/WORMS/CLUSTERWORMS.py",
    }
    assert _resolve_worm_import_module(info) == "CORE.WORMS.CLUSTERWORMS"


def test_resolve_bare_core_module():
    """Bare module name + CORE/ source file → CORE.<name>."""
    info = {
        "module": "SOMEWORM",
        "source_file": "C:/Users/clint/azazael/src/CORE/SOMEWORM.py",
    }
    assert _resolve_worm_import_module(info) == "CORE.SOMEWORM"


def test_resolve_bare_src_root_module():
    """src-root module (TRIMZ.py) stays bare — imports from src root."""
    assert _resolve_worm_import_module({"module": "TRIMZ"}) == "TRIMZ"


def test_resolve_empty_info():
    """No module and no source_file → empty string (validation will flag it)."""
    assert _resolve_worm_import_module({}) == ""


def test_resolve_bare_with_source_stem():
    """Bare module with only a source file infers the module name from the stem."""
    info = {"module": "", "source_file": "C:/Users/clint/azazael/src/CORE/WORMS/HEALTHZ.py"}
    assert _resolve_worm_import_module(info) == "CORE.WORMS.HEALTHZ"


# ── validate_registry_importable ────────────────────────────────────

# Module-level probe worms so the standalone runner (module == "__main__")
# can resolve them via getattr() — function-local classes would not be
# attributes of the test module and would be flagged as broken.


@register_worm(category="diagnostic", priority=5, cooldown_seconds=30)
class _ProbeWormA:
    VERSION = "1.0.0"


@register_worm(category="monitor", priority=6, cooldown_seconds=30)
class _ProbeWormB:
    VERSION = "1.0.0"


def _fresh_registry():
    """Reset the registry and re-register the module-level probe worms."""
    reset_registry()
    register_worm(category="diagnostic", priority=5, cooldown_seconds=30)(_ProbeWormA)
    register_worm(category="monitor", priority=6, cooldown_seconds=30)(_ProbeWormB)


def test_validate_all_pass():
    """Healthy registry → valid=True, checked == total, no broken entries."""
    _fresh_registry()
    result = validate_registry_importable()
    assert result["valid"] is True
    assert result["total"] == 2
    assert result["checked"] == 2
    assert result["broken"] == []
    assert "validated_at" in result


def test_validate_flags_broken_module():
    """Entry whose module cannot be imported is reported as broken."""
    _fresh_registry()
    with _registry_lock:
        WORM_REGISTRY["_GhostWorm"] = {
            "class": object,  # not a real registered worm
            "module": "no_such_module_xyz",
            "category": "utility",
            "priority": 5,
            "cooldown_seconds": 30,
            "source_file": "",
        }
    try:
        result = validate_registry_importable()
        assert result["valid"] is False
        assert result["total"] == 3
        assert result["checked"] == 2
        names = [b["name"] for b in result["broken"]]
        assert "_GhostWorm" in names
        b = next(x for x in result["broken"] if x["name"] == "_GhostWorm")
        assert "no_such_module_xyz" in b["module"]
        assert b["error"]
    finally:
        reset_registry()


def test_validate_flags_missing_class():
    """Entry whose module imports but lacks the registered class is broken."""
    _fresh_registry()
    with _registry_lock:
        WORM_REGISTRY["_NotThere"] = {
            "class": object,
            "module": "CORE.worm_registry",  # imports fine, class absent
            "category": "utility",
            "priority": 5,
            "cooldown_seconds": 30,
            "source_file": "",
        }
    try:
        result = validate_registry_importable()
        assert result["valid"] is False
        b = next(x for x in result["broken"] if x["name"] == "_NotThere")
        assert "not found" in b["error"].lower()
    finally:
        reset_registry()


# ── repair_registry (auto-repair) ──────────────────────────────────

def test_repair_registry_noop_when_valid():
    """Healthy registry → repair is a no-op (attempt=False, nothing repaired)."""
    _fresh_registry()
    try:
        result = repair_registry()
        assert result["attempt"] is False
        assert result["repaired"] == 0
        assert result["valid"] is True
        assert result["still_broken"] == []
    finally:
        reset_registry()


def test_repair_registry_runs_and_revalidates():
    """Broken entries trigger a re-discovery repair attempt (never raises)."""
    _fresh_registry()
    with _registry_lock:
        WORM_REGISTRY["_GhostWorm"] = {
            "class": object,
            "module": "no_such_module_xyz",
            "category": "utility",
            "priority": 5,
            "cooldown_seconds": 30,
            "source_file": "",
        }
    try:
        before = validate_registry_importable()
        assert before["valid"] is False  # pre-condition
        result = repair_registry()
        assert result["attempt"] is True
        assert "repaired_at" in result
        # Report shape: still_broken is a list, total present, no raise.
        assert isinstance(result["still_broken"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["checked"], int)
    finally:
        reset_registry()


# ── startup_warm wiring ─────────────────────────────────────────────

def test_run_registry_validation_stores_result():
    """_run_registry_validation() populates the module-level result."""
    import CORE.startup_warm as sw

    # Force a re-run against the live registry (safe: worms already importable)
    sw._run_registry_validation()
    result = sw.get_registry_validation()
    assert result is not None
    assert "valid" in result
    assert "total" in result
    assert "broken" in result


def test_cache_status_surfaces_validation():
    """cache_status() includes registry_valid + registry_validation keys."""
    import CORE.startup_warm as sw

    sw._run_registry_validation()
    status = sw.cache_status()
    assert "registry_valid" in status
    assert "registry_validation" in status


# ── per-category importability breakdown ────────────────────────────

def test_breakdown_healthy():
    """Healthy registry → each category has checked == total, broken == 0."""
    import CORE.startup_warm as sw

    _fresh_registry()  # resets registry and registers _ProbeWormA (diagnostic) + _ProbeWormB (monitor)
    try:
        validation = validate_registry_importable()
        bd = sw.registry_importability_by_category(validation)
        assert "diagnostic" in bd
        assert "monitor" in bd
        for cat, row in bd.items():
            assert row["total"] == row["checked"]
            assert row["broken"] == 0
        # roll-up matches the validation totals
        assert sum(r["total"] for r in bd.values()) == validation["total"]
    finally:
        reset_registry()


def test_breakdown_counts_broken_by_category():
    """A broken worm is attributed to its category with broken >= 1."""
    import CORE.startup_warm as sw

    _fresh_registry()
    with _registry_lock:
        WORM_REGISTRY["_GhostWorm"] = {
            "class": object,
            "module": "no_such_module_xyz",
            "category": "diagnostic",
            "priority": 5,
            "cooldown_seconds": 30,
            "source_file": "",
        }
    try:
        validation = validate_registry_importable()
        bd = sw.registry_importability_by_category(validation)
        assert bd["diagnostic"]["broken"] >= 1
        assert bd["diagnostic"]["checked"] == bd["diagnostic"]["total"] - 1
        # total broken across categories == validation broken count
        assert sum(r["broken"] for r in bd.values()) == len(validation["broken"])
    finally:
        reset_registry()


def test_breakdown_empty_registry():
    """Empty/unavailable registry → empty-safe {} (no raise)."""
    import CORE.startup_warm as sw

    reset_registry()
    try:
        assert sw.registry_importability_by_category(None) == {}
        assert sw.registry_importability_by_category({}) == {}
    finally:
        reset_registry()


def test_cache_status_includes_breakdown():
    """cache_status() exposes registry_by_category even on an empty registry."""
    import CORE.startup_warm as sw

    reset_registry()
    try:
        status = sw.cache_status()
        assert "registry_by_category" in status
        assert status["registry_by_category"] == {}
    finally:
        reset_registry()


# ── standalone runner (pytest segfaults on 3.14t — Error #48) ───────

if __name__ == "__main__":
    failures = 0
    tests = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            tests += 1
            try:
                fn()
                print(f"  PASS {name}")
            except Exception as e:
                failures += 1
                print(f"  FAIL {name}: {e}")
    print(f"\n{tests - failures}/{tests} tests passed")
    sys.exit(1 if failures > 0 else 0)
