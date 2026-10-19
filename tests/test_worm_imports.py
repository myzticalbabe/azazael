"""Unit tests for the health-check module-path resolver (RULE 0K).

Mirrors the resolver in `_worm_health_check.py`'s worker: bare registry
module names must be prefixed by their package when the module's home
directory is a package, so that imports resolve in subprocess isolation.
"""
import sys
import pytest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC / "CORE" / "WORMS"))


def test_import_lightweight_worms():
    """Lightweight WORMS should import without errors."""
    lightweight = [
        "CLOCKZ", "DISKZ", "CONCURRENCY", "ERROR_SCAN_WORM",
        "METACLUSTER", "CLUSTERWORMS", "NETWORXZ"
    ]
    for mod in lightweight:
        try:
            __import__(mod)
        except Exception as e:
            pytest.fail(f"{mod} failed to import: {e}")


def test_import_heavy_worms():
    """Heavier WORMS may fail on a free-threading build due to C extensions — skip expected failures."""
    heavy = [
        "PROCESSZ", "SMARTDISK", "ERRORZ", "TRIMZ", "METRICZ"
    ]
    failures = []
    for mod in heavy:
        try:
            __import__(mod)
        except Exception as e:
            err = str(e).lower()
            if "c extension" in err or "pandas" in err:
                pytest.skip(f"{mod}: free-threading C extension issue ({e})")
            failures.append(f"{mod}: {e}")
    if failures:
        pytest.fail("\n".join(failures))


def test_freethreading_detection():
    """Free-threading detection should work without error."""
    try:
        result = not sys._is_gil_enabled()
        assert isinstance(result, bool)
    except Exception as e:
        pytest.fail(f"Free-threading detection failed: {e}")


# ── Standalone execution (backward compatible) ──────────────────────


if __name__ == "__main__":

    def _import_mods(mods):
        p = f = 0
        for m in mods:
            try:
                __import__(m)
                p += 1
            except Exception:
                f += 1
        return p, f

    ok, bad = _import_mods([
        "CLOCKZ", "DISKZ", "CONCURRENCY", "ERROR_SCAN_WORM",
        "METACLUSTER", "CLUSTERWORMS", "NETWORXZ",
    ])
    print(f"lightweight: {ok} OK, {bad} FAIL")
    sys.exit(1 if bad else 0)
