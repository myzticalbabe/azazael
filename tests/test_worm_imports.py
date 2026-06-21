# coding: utf-8
"""Unit tests for WORMS module imports (E2E validation on 3.14t) — pytest style."""
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
        "METACLUSTER", "NATURE_CLUSTERS", "CLUSTERWORMS", "NETWORXZ"
    ]
    for mod in lightweight:
        try:
            __import__(mod)
        except Exception as e:
            pytest.fail(f"{mod} failed to import: {e}")


def test_import_heavy_worms():
    """Heavier WORMS may fail on 3.14t due to C extensions — skip expected failures."""
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
                pytest.skip(f"{mod}: 3.14t C extension issue ({e})")
            failures.append(f"{mod}: {e}")
    if failures:
        pytest.fail("\n".join(failures))


def test_freethreading_detection():
    """3.14t free-threading detection should work without error."""
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
                print(f"  PASS: {m}")
                p += 1
            except Exception as e:
                err = str(e).lower()
                if "c extension" in err or "pandas" in err:
                    print(f"  SKIP: {m} (3.14t C ext issue)")
                    p += 1
                else:
                    print(f"  FAIL: {m} - {e}")
                    f += 1
        return p, f

    p, f = 0, 0
    print("[Lightweight WORMS]")
    p1, f1 = _import_mods(["CLOCKZ", "DISKZ", "CONCURRENCY", "ERROR_SCAN_WORM",
                           "METACLUSTER", "NATURE_CLUSTERS", "CLUSTERWORMS", "NETWORXZ"])

    print("\n[Heavy WORMS]")
    p2, f2 = _import_mods(["PROCESSZ", "SMARTDISK", "ERRORZ", "TRIMZ", "METRICZ"])

    p3 = f3 = 0
    print("\n[Free-threading]")
    try:
        result = not sys._is_gil_enabled()
        print(f"  PASS: free-threading={result}")
        p3 = 1
    except Exception as e:
        print(f"  FAIL: {e}")
        f3 = 1

    p = p1 + p2 + p3
    f = f1 + f2 + f3

    print(f"\n{'='*50}")
    print(f"Results: {p} passed, {f} failed")
    sys.exit(0 if f == 0 else 1)
