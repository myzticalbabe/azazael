"""
test_freethreading.py — Comprehensive test suite for freethread_utils.py.

Tests all major components: detection, thread-safe data structures,
FreeThreadPool, DeviceParallelConfig, benchmarks, and OpenVINO async runner.

Targets Python 3.14t free-threaded (no-GIL) exclusively.
"""

import sys, os, time, threading, unittest, json
from pathlib import Path

# Add llama-server/unified to path for import
sys.path.insert(0, str(Path(__file__).parent / 'llama-server' / 'unified'))

from freethread_utils import (
    is_free_threaded, get_thread_info, print_thread_info,
    ThreadSafeCounter, ThreadSafeDict, ThreadSafeList,
    FreeThreadPool, DeviceParallelConfig,
    OpenVINOAsyncRunner, benchmark_parallel, print_benchmark_table,
    ConcurrentTaskRunner,
)


class TestFreeThreadingDetection(unittest.TestCase):
    """Test free-threading detection and diagnostics."""

    def test_is_free_threaded_returns_bool(self):
        self.assertIsInstance(is_free_threaded(), bool)

    def test_get_thread_info_keys(self):
        info = get_thread_info()
        required_keys = [
            'free_threaded', 'python_version', 'python_executable',
            'cpu_count', 'threading_active_count', 'gil_status',
            'effective_parallelism',
        ]
        for key in required_keys:
            self.assertIn(key, info, f"Missing key: {key}")

    def test_effective_parallelism_consistency(self):
        info = get_thread_info()
        self.assertTrue(info['free_threaded'])
        self.assertEqual(info['effective_parallelism'], os.cpu_count())
        self.assertEqual(info['gil_status'], 'disabled')

    def test_print_thread_info_no_crash(self):
        """print_thread_info() should not raise any exception."""
        print_thread_info()  # Just verify it runs

    def test_is_free_threaded_always_true(self):
        """Verify is_free_threaded() always returns True on 3.14t."""
        self.assertTrue(is_free_threaded(),
            "is_free_threaded() should always return True on Python 3.14t")


class TestThreadSafeCounter(unittest.TestCase):
    """Test ThreadSafeCounter operations with real threads."""

    def test_basic_increment(self):
        c = ThreadSafeCounter()
        self.assertEqual(c.value, 0)
        c.increment()
        self.assertEqual(c.value, 1)
        c.increment(5)
        self.assertEqual(c.value, 6)

    def test_basic_decrement(self):
        c = ThreadSafeCounter(10)
        c.decrement(3)
        self.assertEqual(c.value, 7)

    def test_concurrent_increments(self):
        """50 threads each incrementing 100 times should give exactly 5000."""
        c = ThreadSafeCounter()
        num_threads = 50
        increments_per_thread = 100

        def worker():
            for _ in range(increments_per_thread):
                c.increment()

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(c.value, num_threads * increments_per_thread)

    def test_reset(self):
        c = ThreadSafeCounter(42)
        c.reset()
        self.assertEqual(c.value, 0)

    def test_repr(self):
        c = ThreadSafeCounter(7)
        self.assertIn('7', repr(c))


class TestThreadSafeDict(unittest.TestCase):
    """Test ThreadSafeDict operations."""

    def test_basic_operations(self):
        d = ThreadSafeDict()
        d['key'] = 'value'
        self.assertEqual(d['key'], 'value')

    def test_get_and_update(self):
        d = ThreadSafeDict(counter=0)
        def increment(val):
            return val + 1
        result = d.get_and_update('counter', 0, increment)
        self.assertEqual(result, 0)
        self.assertEqual(d['counter'], 1)

    def test_safe_get(self):
        d = ThreadSafeDict({'a': 1, 'b': 2})
        self.assertEqual(d.safe_get('a'), 1)
        self.assertIsNone(d.safe_get('missing'))
        self.assertEqual(d.safe_get('missing', 'default'), 'default')

    def test_keys_safe(self):
        d = ThreadSafeDict({'x': 1, 'y': 2})
        self.assertEqual(sorted(d.keys_safe()), ['x', 'y'])

    def test_values_safe(self):
        d = ThreadSafeDict({'x': 1, 'y': 2})
        self.assertEqual(sorted(d.values_safe()), [1, 2])

    def test_concurrent_writes(self):
        """Multiple threads writing to different keys should be consistent."""
        d = ThreadSafeDict()
        num_threads = 20

        def worker(idx):
            d[f'key_{idx}'] = idx * 100

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(d.keys_safe()), num_threads)
        for i in range(num_threads):
            self.assertEqual(d[f'key_{i}'], i * 100)


class TestThreadSafeList(unittest.TestCase):
    """Test ThreadSafeList operations."""

    def test_append_and_len(self):
        lst = ThreadSafeList()
        lst.append(1)
        lst.append(2)
        self.assertEqual(len(lst), 2)

    def test_extend(self):
        lst = ThreadSafeList([1, 2])
        lst.extend([3, 4, 5])
        self.assertEqual(len(lst), 5)

    def test_get_all(self):
        lst = ThreadSafeList([1, 2, 3])
        self.assertEqual(lst.get_all(), [1, 2, 3])

    def test_concurrent_appends(self):
        """100 threads each appending 10 items should give 1000 items."""
        lst = ThreadSafeList()
        num_threads = 100
        items_per_thread = 10

        def worker(offset):
            for i in range(items_per_thread):
                lst.append(offset * 1000 + i)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(lst), num_threads * items_per_thread)
        self.assertEqual(len(lst.get_all()), num_threads * items_per_thread)

    def test_repr(self):
        lst = ThreadSafeList([1, 2])
        self.assertIn('2', repr(lst))


class TestFreeThreadPool(unittest.TestCase):
    """Test FreeThreadPool functionality."""

    def test_auto_sizing(self):
        pool = FreeThreadPool()
        self.assertGreater(pool.max_workers, 0)
        self.assertLessEqual(pool.max_workers, max(8, os.cpu_count() or 8))

    def test_context_manager(self):
        results = []
        with FreeThreadPool(max_workers=4) as pool:
            f1 = pool.submit(lambda: 42)
            f2 = pool.submit(lambda: 84)
            results.append(f1.result())
            results.append(f2.result())
        self.assertEqual(results, [42, 84])

    def test_map_operation(self):
        with FreeThreadPool(max_workers=4) as pool:
            squared = list(pool.map(lambda x: x * x, range(10)))
        self.assertEqual(squared, [0, 1, 4, 9, 16, 25, 36, 49, 64, 81])

    def test_parallel_execution(self):
        """Verify threads run in parallel by timing."""
        def sleep_work():
            time.sleep(0.1)
            return True

        start = time.perf_counter()
        with FreeThreadPool(max_workers=8) as pool:
            futures = [pool.submit(sleep_work) for _ in range(8)]
            results = [f.result() for f in futures]
        elapsed = time.perf_counter() - start

        self.assertTrue(all(results))
        # Under FT, 8 threads sleeping 0.1s should finish in ~0.1s
        self.assertLess(elapsed, 0.5, f"Parallel execution too slow: {elapsed:.2f}s")

    def test_info_keys(self):
        info = FreeThreadPool.info()
        for key in ['free_threaded', 'cpu_count', 'recommended_workers',
                     'max_workers_for_io', 'max_workers_for_cpu', 'max_workers_for_gpu']:
            self.assertIn(key, info, f"Missing info key: {key}")

    def test_exit_cleans_up(self):
        pool = FreeThreadPool(max_workers=2)
        with pool:
            self.assertIsNotNone(pool._executor)
        # After exit, executor should be None (but _executor is private)
        with self.assertRaises(RuntimeError):
            pool.submit(lambda: 1)


class TestDeviceParallelConfig(unittest.TestCase):
    """Test device-aware parallelism configuration."""

    def test_cpu_config(self):
        cfg = DeviceParallelConfig.for_cpu()
        self.assertEqual(cfg.device_name, "CPU")
        self.assertGreater(cfg.optimal_workers, 0)

    def test_gpu_config(self):
        cfg = DeviceParallelConfig.for_gpu()
        self.assertEqual(cfg.device_name, "GPU")

    def test_npu_config(self):
        cfg = DeviceParallelConfig.for_npu()
        self.assertEqual(cfg.device_name, "NPU")

    def test_for_device_string(self):
        for dev in ["CPU", "GPU", "NPU", "cpu", "intel_gpu", "AI_BOOST"]:
            cfg = DeviceParallelConfig.for_device(dev)
            self.assertIsNotNone(cfg)
            self.assertGreater(cfg.optimal_workers, 0)

    def test_unknown_device_falls_back_to_cpu(self):
        cfg = DeviceParallelConfig.for_device("quantum_computer")
        self.assertEqual(cfg.device_name, "CPU")

    def test_summary_string(self):
        cfg = DeviceParallelConfig.for_cpu()
        summary = cfg.summary()
        self.assertIn("CPU", summary)
        self.assertIn("workers", summary)

    def test_gil_limited_flag(self):
        cpu_cfg = DeviceParallelConfig.for_cpu()
        ft = is_free_threaded()
        self.assertEqual(cpu_cfg.gil_limited, not ft)

    def test_npu_not_gil_limited(self):
        """NPU is always async (hardware queue), so not GIL-limited."""
        npu_cfg = DeviceParallelConfig.for_npu()
        self.assertFalse(npu_cfg.gil_limited)


class TestBenchmark(unittest.TestCase):
    """Test benchmark_parallel functionality."""

    def test_benchmark_basic(self):
        def trivial_work():
            return sum(range(100))

        results = benchmark_parallel(trivial_work, max_workers=4,
                                     total_iterations=100, device="CPU")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIsInstance(r.num_workers, int)
            self.assertGreater(r.throughput_per_sec, 0)
            self.assertIsInstance(r.speedup_vs_baseline, float)

    def test_baseline_speedup_is_1(self):
        def work():
            time.sleep(0.001)
            return 1

        results = benchmark_parallel(work, max_workers=2, total_iterations=10,
                                     device="CPU")
        # baseline (workers=1) should have speedup ~1.0
        self.assertAlmostEqual(results[0].speedup_vs_baseline, 1.0, delta=0.1)

    def test_print_benchmark_table_no_crash(self):
        def work():
            return 1

        results = benchmark_parallel(work, max_workers=2, total_iterations=10)
        print_benchmark_table(results)  # Just verify it runs


class TestConcurrentTaskRunner(unittest.TestCase):
    """Test ConcurrentTaskRunner for multi-device orchestration."""

    def test_empty_tasks(self):
        runner = ConcurrentTaskRunner()
        report = runner.run_all()
        self.assertEqual(report['results'], {})

    def test_single_task(self):
        runner = ConcurrentTaskRunner()

        def cpu_work():
            return sum(range(1000))

        runner.set_task("CPU", cpu_work)
        report = runner.run_all()

        self.assertIn('CPU_result', report['results'])
        self.assertIn('CPU_elapsed_sec', report['results'])
        self.assertEqual(report['results']['CPU_result'], sum(range(1000)))
        self.assertEqual(report['errors'], [])

    def test_multiple_devices_parallel(self):
        runner = ConcurrentTaskRunner()

        def work(device):
            time.sleep(0.05)
            return f"done_{device}"

        runner.set_task("CPU", lambda: work("cpu"))
        runner.set_task("GPU", lambda: work("gpu"))
        runner.set_task("NPU", lambda: work("npu"))

        report = runner.run_all()

        for dev in ["CPU", "GPU", "NPU"]:
            self.assertIn(f'{dev}_result', report['results'])
            self.assertIn(f'{dev}_elapsed_sec', report['results'])

        # Under free-threading, multi-device should be fast
        total_time = report.get('total_duration_sec', 999)
        self.assertLess(total_time, 2.0)  # Should be ~0.05s, allow generous margin

    def test_task_error_handling(self):
        runner = ConcurrentTaskRunner()

        def failing_work():
            raise ValueError("Test error")

        runner.set_task("CPU", failing_work)
        report = runner.run_all()

        self.assertGreater(len(report['errors']), 0)
        self.assertEqual(report['errors'][0]['device'], 'CPU')


class TestThreadAffinity(unittest.TestCase):
    """Test thread affinity (Windows-only, non-destructive)."""

    def test_set_current_thread_affinity_no_error(self):
        """Should not raise exception, even if it fails on restricted systems."""
        from freethread_utils import set_current_thread_affinity
        try:
            result = set_current_thread_affinity(0)  # Mask 0 (no cores) — should fail
            # Either True or False is acceptable — just no crash
            self.assertIsInstance(result, bool)
        except Exception as e:
            if sys.platform == 'win32':
                self.fail(f"set_current_thread_affinity raised exception: {e}")
            else:
                self.skipTest("Not on Windows")

    def test_set_current_thread_affinity_single_core(self):
        """Pin to core 0 — should succeed on Windows with sufficient privileges."""
        if sys.platform != 'win32':
            self.skipTest("Not on Windows")
        from freethread_utils import set_current_thread_affinity
        # core 0 mask = 1
        result = set_current_thread_affinity([0])
        # Just verify no exception; result may be False if restricted
        self.assertIsInstance(result, bool)


class TestDiagnosticOutput(unittest.TestCase):
    """Test that diagnostic functions run without crashing."""

    def test_detect_devices(self):
        from freethread_utils import detect_devices
        configs = detect_devices()
        self.assertGreater(len(configs), 0)
        self.assertEqual(configs[0].device_name, "CPU")

    def test_print_benchmark_table_empty(self):
        from freethread_utils import print_benchmark_table
        print_benchmark_table([])  # Should handle empty list gracefully

    def test_print_benchmark_table_empty(self):
        from freethread_utils import print_benchmark_table
        print_benchmark_table([])  # Should handle empty list gracefully


# ── Run All Tests ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f"\n{'='*70}")
    print(f"  Free-Threading Test Suite (Python 3.14t)")
    print(f"  {'='*70}")
    print(f"  Free-threaded: True (no GIL)")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  CPU cores: {os.cpu_count()}")
    print(f"  {'='*70}\n")

    # Run with high verbosity
    unittest.main(verbosity=2)
