# coding: utf-8
"""Unit tests for cluster worm modules (3.14t compatible) — pytest style."""

import sys
import pytest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC / "CORE" / "WORMS"))

TEST_MODULES = {
    "CLUSTERWORMS": "CORE/WORMS/CLUSTERWORMS.py",
    "METACLUSTER": "CORE/WORMS/METACLUSTER.py",
    "CONCURRENCY": "CORE/WORMS/CONCURRENCY.py",
    "SMARTDISK": "CORE/WORMS/SMARTDISK.py",
}


@pytest.mark.parametrize("mod_name,rel_path", [
    (name, path) for name, path in TEST_MODULES.items()
])
def test_module_imports(mod_name, rel_path):
    """Each cluster module should import with public attributes."""
    src_path = SRC / rel_path
    assert src_path.exists(), f"Source not found: {src_path}"
    try:
        mod = __import__(mod_name)
        attrs = [a for a in dir(mod) if not a.startswith('_')]
        assert len(attrs) > 0, f"{mod_name} has no public attributes"
    except Exception as e:
        # Known 3.14t C extension incompatibility — skip, don't fail
        err = str(e).lower()
        if "pandas" in err or "c extension" in err:
            pytest.skip(f"3.14t C extension issue: {e}")
        raise


# ── Standalone execution (backward compatible) ──────────────────────


def _run_standalone():
    """Run tests standalone when invoked directly (pytest compatibility shim)."""
    passed = 0
    failed = 0
    errors = []

    for mod_name, rel_path in TEST_MODULES.items():
        src_path = SRC / rel_path
        if not src_path.exists():
            print(f"SKIP {mod_name}: source not found at {src_path}")
            continue
        try:
            mod = __import__(mod_name)
            attrs = [a for a in dir(mod) if not a.startswith('_')]
            print(f"PASS {mod_name}: {len(attrs)} public attrs")
            passed += 1
        except Exception as e:
            err = str(e)
            if "pandas" in err.lower() or "C extension" in err:
                print(f"SKIP {mod_name}: 3.14t C ext issue ({err[:60]})")
            else:
                print(f"FAIL {mod_name}: {err[:80]}")
                failed += 1
                errors.append(err)

    print(f"\nResults: {passed} passed, {failed} failed")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  {e}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_standalone())
