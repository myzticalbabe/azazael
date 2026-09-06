"""RULE 0Z-F Telemetry Counter Tests"""
import sys
sys.path.insert(0, "src")

try:
    from CORE.compliance.pre_action_gate import PreActionGate, reset_telemetry_state
    GATE_AVAILABLE = True
except ImportError:
    GATE_AVAILABLE = False


def fresh_gate():
    """Return a gate with reset persisted+in-memory counters (isolation)."""
    reset_telemetry_state()
    return PreActionGate()


if __name__ == "__main__":
    print("=" * 60)
    print("  RULE 0Z-F TELEMETRY TESTS")
    print("=" * 60)

    if not GATE_AVAILABLE:
        print("SKIP: PreActionGate not available")
        sys.exit(0)

    passed = 0
    total = 4

    # Test 1: Counters start at 0 (after reset)
    gate = fresh_gate()
    if gate.parallel_batch_count == 0 and gate.sequential_spawn_count == 0:
        print("  [PASS] Counters start at 0")
        passed += 1
    else:
        print(f"  [FAIL] Counters start at 0: batch={gate.parallel_batch_count}, seq={gate.sequential_spawn_count}")

    # Test 2: record_parallel_batch increments
    gate2 = fresh_gate()
    gate2.record_parallel_batch()
    gate2.record_parallel_batch()
    gate2.record_parallel_batch()
    if gate2.parallel_batch_count == 3:
        print("  [PASS] record_parallel_batch increments to 3")
        passed += 1
    else:
        print(f"  [FAIL] record_parallel_batch: expected 3, got {gate2.parallel_batch_count}")

    # Test 3: record_sequential_violation increments
    gate3 = fresh_gate()
    gate3.record_sequential_violation()
    if gate3.sequential_spawn_count == 1:
        print("  [PASS] record_sequential_violation increments to 1")
        passed += 1
    else:
        print(f"  [FAIL] record_sequential_violation: expected 1, got {gate3.sequential_spawn_count}")

    # Test 4: Independent counters
    gate4 = fresh_gate()
    gate4.record_parallel_batch()
    gate4.record_sequential_violation()
    gate4.record_sequential_violation()
    if gate4.parallel_batch_count == 1 and gate4.sequential_spawn_count == 2:
        print("  [PASS] Independent parallel=1 sequential=2")
        passed += 1
    else:
        print(f"  [FAIL] Independent: parallel={gate4.parallel_batch_count}, seq={gate4.sequential_spawn_count}")

    # Test 5: Counters persist across processes (fresh gate reloads saved state)
    gate5a = fresh_gate()
    gate5a.record_parallel_batch()
    gate5a.record_parallel_batch()
    gate5b = PreActionGate()
    if gate5b.parallel_batch_count == 2:
        print("  [PASS] Counters persist across processes (loaded 2)")
        passed += 1
    else:
        print(f"  [FAIL] Persistence: expected 2, got {gate5b.parallel_batch_count}")
    total = 5

    # Cleanup so CI/other suites start from a clean slate
    reset_telemetry_state()

    print(f"\n{passed}/{total} TELEMETRY TESTS PASSED")
    sys.exit(0 if passed == total else 1)
