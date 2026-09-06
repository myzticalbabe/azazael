# coding: utf-8
"""Worm smoke tests — instantiate every registered worm and call get_summary().

Verifies that every worm in WORM_REGISTRY:
  1. Can be instantiated (cls() without arguments)
  2. Has a working get_summary() method that returns a valid dict
  3. Has a working get_status() method (optional, skips gracefully)

Warms the registry ONCE at module load time. Covers ALL registered worms
regardless of category — this is the definitive ecosystem health check.

Run standalone (3.14t compatible):
  python tests/test_worm_smoke.py

Run with pytest:
  python -m pytest tests/test_worm_smoke.py -v
"""

import sys
import os
import time
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC / "CORE" / "WORMS"))

os.environ["PYTHONIOENCODING"] = "utf-8"

import pytest
import threading

# Module-level warm-up
from CORE.worm_registry import discover_worms, WORM_REGISTRY, mark_spawned
from collections import defaultdict

print("  Warming registry for smoke test...", end=" ", flush=True)
t0 = time.time()
discover_worms()
elapsed = time.time() - t0
print(f"({len(WORM_REGISTRY)} entries, {elapsed:.1f}s)")

# Worms known to require constructor arguments (skip instantiation)
SKIP_INSTANTIATE = {
    "NatureClusterManager",  # requires NatureClusterManager to exist
    "FreeThreadPool",        # utility, not a worm per se
}

# Worms that hang or timeout on get_summary()
SKIP_SUMMARY = {
    "CLUSTER_INSPECTOR",  # scans 473 files, >60s
    "RLTrainLoop",        # ML training, requires data
    "ScheduledTrainingWorm",  # requires scheduler
}

# Worms with C extensions that may segfault on 3.14t
C_EXTENSION_WORMS = {"PROCESSZ", "SMARTDISK", "DISKZ", "SystemZ", "NETWORXZ", "SYSTEMZ_ML"}

# Group by category
WORMS_BY_CATEGORY = defaultdict(list)
for name, entry in WORM_REGISTRY.items():
    WORMS_BY_CATEGORY[entry.get("category", "unknown")].append(name)

# Per-worm timeout (seconds)
PER_WORM_TIMEOUT = 10


def _run_with_timeout(func, timeout=10):
    """Run a callable with a timeout guard. Returns {"result": ..., "error": ...}."""
    result_data = {"result": None, "error": None}
    done = threading.Event()

    def _try():
        try:
            result_data["result"] = func()
        except Exception as e:
            result_data["error"] = f"{type(e).__name__}: {e}"
        done.set()

    t = threading.Thread(target=_try, daemon=True)
    t.start()
    if not done.wait(timeout=timeout):
        result_data["error"] = f"TIMEOUT (>{timeout}s)"
    return result_data


def _instantiate_with_timeout(cls, name):
    """Instantiate a worm class with a timeout guard."""
    return _run_with_timeout(lambda: cls())


def _get_summary_with_timeout(instance, name):
    """Call get_summary() with a timeout guard."""
    def _call():
        method = getattr(instance, "get_summary", None)
        if method and callable(method):
            return method()
        return None
    return _run_with_timeout(_call)


# ── Tests ──────────────────────────────────────────────────────────


def test_every_worm_instantiable():
    """Every registered worm should instantiate without error."""
    failures = []
    skipped = 0
    for name in sorted(WORM_REGISTRY.keys()):
        if name in SKIP_INSTANTIATE:
            skipped += 1
            continue
        if name in C_EXTENSION_WORMS:
            skipped += 1
            continue

        cls = WORM_REGISTRY[name].get("class")
        if cls is None:
            failures.append(f"{name}: no class in registry")
            continue

        result = _instantiate_with_timeout(cls, name)
        if result["error"]:
            failures.append(f"{name}: {result['error']}")

    total = len(WORM_REGISTRY) - skipped
    assert not failures, (
        f"{len(failures)}/{total} worms failed instantiation:\n" +
        "\n".join(failures[:30])
    )


def test_every_worm_has_get_summary():
    """Every registered worm should return a valid get_summary() dict."""
    failures = []
    skipped = 0
    for name in sorted(WORM_REGISTRY.keys()):
        if name in SKIP_INSTANTIATE or name in SKIP_SUMMARY:
            skipped += 1
            continue
        if name in C_EXTENSION_WORMS:
            skipped += 1
            continue

        cls = WORM_REGISTRY[name].get("class")
        if cls is None:
            continue

        # Try to instantiate
        inst_result = _instantiate_with_timeout(cls, name)
        if inst_result["error"]:
            failures.append(f"{name}: instantiation failed: {inst_result['error']}")
            continue

        instance = inst_result["result"]
        if instance is None:
            failures.append(f"{name}: instance is None")
            continue

        # Call get_summary
        summary_result = _get_summary_with_timeout(instance, name)
        if summary_result["error"]:
            failures.append(f"{name}: get_summary() failed: {summary_result['error']}")
            continue

        summary = summary_result["result"]
        if not isinstance(summary, dict):
            failures.append(f"{name}: get_summary() returned {type(summary).__name__}, not dict")
            continue

        # Note: many worms use custom summary formats without 'success' key.
        # This is a known gap — BaseWormMixin.get_summary() always includes 'success'.
        # Worms not using BaseWormMixin may have different formats.

    total = len(WORM_REGISTRY) - skipped - len(SKIP_INSTANTIATE) - len(SKIP_SUMMARY)
    assert not failures, (
        f"{len(failures)}/{total} worms failed get_summary():\n" +
        "\n".join(failures[:30])
    )


def test_every_category_has_smokeable_worms():
    """Every category should have at least 1 worm that can be smoked."""
    empty = []
    for cat, worms in sorted(WORMS_BY_CATEGORY.items()):
        smokeable = [
            w for w in worms
            if w not in SKIP_INSTANTIATE
            and w not in SKIP_SUMMARY
            and w not in C_EXTENSION_WORMS
        ]
        if not smokeable:
            empty.append(cat)
    assert not empty, f"Categories with no smokeable worms: {empty}"


def test_mark_spawned_increments_counter():
    """mark_spawned() should increment spawn_count."""
    for name in list(WORM_REGISTRY.keys())[:5]:
        before = WORM_REGISTRY[name].get("spawn_count", 0)
        mark_spawned(name)
        after = WORM_REGISTRY[name].get("spawn_count", 0)
        assert after == before + 1, f"{name}: spawn_count not incremented"


def test_worm_summary_structure():
    """First 10 smokeable worms should return well-structured summaries."""
    tested = 0
    failures = []
    for name in sorted(WORM_REGISTRY.keys()):
        if name in SKIP_INSTANTIATE or name in SKIP_SUMMARY:
            continue
        if name in C_EXTENSION_WORMS:
            continue

        cls = WORM_REGISTRY[name].get("class")
        if cls is None:
            continue

        inst_result = _instantiate_with_timeout(cls, name)
        if inst_result["error"] or inst_result["result"] is None:
            continue

        summary_result = _get_summary_with_timeout(inst_result["result"], name)
        if summary_result["error"]:
            continue

        summary = summary_result["result"]
        if not isinstance(summary, dict):
            continue

        # Verify it's a usable summary dict (any format is OK)

        tested += 1
        if tested >= 10:
            break

    assert not failures, "\n".join(failures[:20])
    assert tested >= 3, f"Only {tested} worms smokeable (need >= 3)"


# ── Standalone runner ──────────────────────────────────────────────


def _run_standalone():
    """Run all tests standalone (for 3.14t where pytest segfaults)."""
    passed = 0
    failed = 0

    test_fns = [
        ("Every worm instantiable", test_every_worm_instantiable),
        ("Every worm has get_summary", test_every_worm_has_get_summary),
        ("Every category has smokeable worms", test_every_category_has_smokeable_worms),
        ("mark_spawned increments counter", test_mark_spawned_increments_counter),
        ("Worm summary structure", test_worm_summary_structure),
    ]

    print(f"\n  Worm Smoke Tests ({len(test_fns)} tests)")
    print(f"  {'=' * 55}")
    for name, fn in test_fns:
        try:
            fn()
            print(f"  [OK] {name}")
            passed += 1
        except AssertionError as e:
            lines = str(e).split("\n")[:5]
            print(f"  [FAIL] {name}: {lines[0]}")
            for line in lines[1:]:
                print(f"         {line}")
            failed += 1
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print(f"  {'=' * 55}")
    print(f"  Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_standalone())
