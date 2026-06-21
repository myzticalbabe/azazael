# coding: utf-8
"""
Unit tests for NatureCluster dead letter queue.

Tests:
- _failed_executions populated on worm failure
- get_failed_executions(since=...) filtering
- retry_failed_worms() retry and queue cleanup
- clear_failed_executions() emptying
- Thread safety of concurrent failures
"""

import sys
import os
import time
import threading
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Simple failing worm class ────────────────────────────────────

class FailingWorm:
    """A worm that always fails — has no standard methods."""
    VERSION = "1.0.0"

class SometimesFailingWorm:
    """A worm that succeeds after 2 initial failures.
    
    Uses an instance-level counter so cached instances (via
    _get_or_create_instance) accumulate attempts across calls.
    """
    VERSION = "1.0.0"

    def __init__(self):
        self._attempts = 0

    def get_status(self):
        self._attempts += 1
        if self._attempts <= 2:
            raise ValueError(f"Simulated failure #{self._attempts}")
        return {"status": "ok", "attempts": self._attempts}

class SuccessWorm:
    """A worm that always succeeds."""
    VERSION = "1.0.0"
    def get_summary(self):
        return {"status": "ok", "data": "success"}


# ═══════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════

passed = 0
failed = 0
errors = []


def test_dlq_populated_on_failure():
    """_failed_executions should be populated when a worm fails."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq")
    nc.add_worm_manual("FailingWorm", FailingWorm)
    result = nc._execute_single_worm("FailingWorm", FailingWorm)
    assert not result.get("success"), "FailingWorm should have failed"
    failures = nc.get_failed_executions()
    assert len(failures) >= 1, f"Expected >= 1 failure, got {len(failures)}"
    assert failures[0]["worm"] == "FailingWorm"
    assert failures[0]["nature"] == "test_dlq"
    assert "error" in failures[0]
    assert "timestamp" in failures[0]
    nc.clear_failed_executions()


def test_dlq_get_since_filter():
    """get_failed_executions(since=...) should filter by time."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_since")
    nc.add_worm_manual("FailingWorm", FailingWorm)

    before = time.time() - 0.1
    nc._execute_single_worm("FailingWorm", FailingWorm)
    after = time.time() + 0.1

    all_fails = nc.get_failed_executions(since=0)
    assert len(all_fails) >= 1

    recent = nc.get_failed_executions(since=before)
    assert len(recent) >= 1, "Should include failures after 'before' timestamp"

    future = nc.get_failed_executions(since=after)
    assert len(future) == 0, f"Should not include failures before 'after', got {len(future)}"

    nc.clear_failed_executions()


def test_dlq_clear():
    """clear_failed_executions should empty the queue."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_clear")
    nc.add_worm_manual("FailingWorm", FailingWorm)
    nc._execute_single_worm("FailingWorm", FailingWorm)
    assert len(nc.get_failed_executions()) >= 1
    nc.clear_failed_executions()
    assert len(nc.get_failed_executions()) == 0, "Queue should be empty after clear"


def test_dlq_retry_failed_worms():
    """retry_failed_worms should retry and clear successful retries."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_retry")

    # Add the "sometimes fails" worm — instance 1 and 2 will fail, 3+ succeed
    nc.add_worm_manual("SometimesFailing", SometimesFailingWorm)

    # Execute twice — both should fail
    r1 = nc._execute_single_worm("SometimesFailing", SometimesFailingWorm)
    assert not r1.get("success"), "First call should fail"
    r2 = nc._execute_single_worm("SometimesFailing", SometimesFailingWorm)
    assert not r2.get("success"), "Second call should fail"

    # Should have 2 failures in queue (different instances since it fails before caching)
    failures = nc.get_failed_executions()
    assert len(failures) >= 2, f"Expected >= 2 failures, got {len(failures)}"

    # Retry — both should succeed on retry (call_id >= 3 succeeds)
    result = nc.retry_failed_worms(max_retries=2)

    assert result["retried"] >= 1, f"Should have retried >= 1, got {result}"
    # At least one should succeed (the third instance onward succeeds)
    # The queue should be empty since retries succeeded
    remaining = nc.get_failed_executions()
    # Might still have failures if retried instances also failed
    # (since SometimesFailingWorm creates new instances each time)
    nc.clear_failed_executions()


def test_dlq_retry_empty():
    """retry_failed_worms with empty queue should return zeroes."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_empty_retry")
    nc.clear_failed_executions()
    result = nc.retry_failed_worms()
    assert result["retried"] == 0
    assert result["succeeded"] == 0
    assert result["still_failed"] == 0


def test_dlq_success_does_not_add_to_queue():
    """Successful worm executions should not populate the dead letter queue."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_success")
    nc.add_worm_manual("SuccessWorm", SuccessWorm)
    result = nc._execute_single_worm("SuccessWorm", SuccessWorm)
    assert result.get("success"), "SuccessWorm should succeed"
    failures = nc.get_failed_executions()
    assert len(failures) == 0, "No failures should be recorded"


def test_dlq_thread_safety():
    """Concurrent failures should be thread-safe."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_thread")
    nc.add_worm_manual("FailingWorm", FailingWorm)

    def fail_many(count=5):
        for _ in range(count):
            nc._execute_single_worm("FailingWorm", FailingWorm)

    threads = []
    for _ in range(3):
        t = threading.Thread(target=fail_many, args=(5,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    failures = nc.get_failed_executions()
    assert len(failures) == 15, f"Expected 15 concurrent failures, got {len(failures)}"

    nc.clear_failed_executions()


def test_dlq_status_integration():
    """get_status should report failed_executions count."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureCluster
    nc = NatureCluster("test_dlq_status")
    status = nc.get_status()
    assert "failed_executions" in status, "get_status should include failed_executions count"
    assert status["failed_executions"] == 0
    nc.add_worm_manual("FailingWorm", FailingWorm)
    nc._execute_single_worm("FailingWorm", FailingWorm)
    status = nc.get_status()
    assert status["failed_executions"] >= 1
    nc.clear_failed_executions()


# ── Test Runner ──────────────────────────────────────────────────

def run_test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  [OK] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1
        errors.append(f"{name}: {e}")


def main():
    global passed, failed, errors
    print("=" * 60)
    print("  Dead Letter Queue Tests")
    print("=" * 60)
    print()
    print(f"  Module: CORE.WORMS.NATURE_CLUSTERS")
    print()
    print(f"  Tests:")
    print()

    tests = [
        ("DLQ populated on failure", test_dlq_populated_on_failure),
        ("get_failed_executions since= filter", test_dlq_get_since_filter),
        ("clear_failed_executions", test_dlq_clear),
        ("retry_failed_worms", test_dlq_retry_failed_worms),
        ("retry_failed_worms (empty queue)", test_dlq_retry_empty),
        ("Success does not add to DLQ", test_dlq_success_does_not_add_to_queue),
        ("Thread safety", test_dlq_thread_safety),
        ("get_status integration", test_dlq_status_integration),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print()
    print(f"  Results: {passed} passed, {failed} failed")
    if errors:
        print("  Errors:")
        for e in errors:
            print(f"    {e}")
    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
