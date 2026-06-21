"""RULE 0Z-F Telemetry Counter Tests"""
import sys
sys.path.insert(0, "src")

try:
    from CORE.compliance.pre_action_gate import PreActionGate
    GATE_AVAILABLE = True
except ImportError:
    GATE_AVAILABLE = False


if __name__ == "__main__":
    print("=" * 60)
    print("  RULE 0Z-F TELEMETRY TESTS")
    print("=" * 60)

    if not GATE_AVAILABLE:
        print("SKIP: PreActionGate not available")
        sys.exit(0)

    passed = 0
    total = 4

    # Test 1: Counters start at 0
    gate = PreActionGate()
    if gate.parallel_batch_count == 0 and gate.sequential_spawn_count == 0:
        print("  [PASS] Counters start at 0")
        passed += 1
    else:
        print(f"  [FAIL] Counters start at 0: batch={gate.parallel_batch_count}, seq={gate.sequential_spawn_count}")

    # Test 2: record_parallel_batch increments
    gate2 = PreActionGate()
    gate2.record_parallel_batch()
    gate2.record_parallel_batch()
    gate2.record_parallel_batch()
    if gate2.parallel_batch_count == 3:
        print("  [PASS] record_parallel_batch increments to 3")
        passed += 1
    else:
        print(f"  [FAIL] record_parallel_batch: expected 3, got {gate2.parallel_batch_count}")

    # Test 3: record_sequential_violation increments
    gate3 = PreActionGate()
    gate3.record_sequential_violation()
    if gate3.sequential_spawn_count == 1:
        print("  [PASS] record_sequential_violation increments to 1")
        passed += 1
    else:
        print(f"  [FAIL] record_sequential_violation: expected 1, got {gate3.sequential_spawn_count}")

    # Test 4: Independent counters
    gate4 = PreActionGate()
    gate4.record_parallel_batch()
    gate4.record_sequential_violation()
    gate4.record_sequential_violation()
    if gate4.parallel_batch_count == 1 and gate4.sequential_spawn_count == 2:
        print("  [PASS] Independent parallel=1 sequential=2")
        passed += 1
    else:
        print(f"  [FAIL] Independent: parallel={gate4.parallel_batch_count}, seq={gate4.sequential_spawn_count}")

    print(f"\n{passed}/{total} TELEMETRY TESTS PASSED")
    sys.exit(0 if passed == total else 1)
