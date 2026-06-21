#!/usr/bin/env python3
"""
cProfile harness: 100-worm parallel execution through FreeThreadPool.

Measures:
  1. FreeThreadPool creation/scheduling overhead
  2. Worker execution time distribution (varying latencies)
  3. as_completed() result collection overhead
  4. Lock contention hotspots under free-threading
  5. Throughput at concurrency levels [2, 4, 8, 16, 32, 64, 100]

Output: _profile_100worm.prof (binary) + analysis to stdout
"""

import cProfile
import pstats
import io
import os
import sys
import time
import threading
import random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from CORE.freethreading import (
    FreeThreadPool, is_free_threaded, get_thread_info,
    ThreadSafeCounter, CancellationToken,
)
from concurrent.futures import as_completed, TimeoutError


# ── Synthetic Worm Config (mimics real WormConfig without full import) ──

@dataclass
class SynthWormConfig:
    name: str
    priority: int = 5
    cooldown_seconds: float = 30.0
    retry: int = 1
    latency_ms: int = 50       # Simulated execution time
    fail_rate: float = 0.0     # 0.0 - 1.0 probability of failure
    enabled: bool = True


def synth_execute_worm(config: SynthWormConfig) -> Dict[str, Any]:
    """Simulate worm execution with configurable latency and failure rate."""
    start = time.perf_counter()

    # Simulate CPU-bound work
    _ = sum(i * i for i in range(config.latency_ms * 10))

    # Simulate I/O wait
    time.sleep(config.latency_ms / 1000.0)

    # Simulate failure
    if random.random() < config.fail_rate:
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "name": config.name,
            "success": False,
            "duration_ms": elapsed,
            "result": {"error": f"Simulated failure (rate={config.fail_rate})"},
            "error": f"Simulated failure (rate={config.fail_rate})",
        }

    elapsed = (time.perf_counter() - start) * 1000
    return {
        "name": config.name,
        "success": True,
        "duration_ms": elapsed,
        "result": {
            "status": "ok",
            "tokens": config.latency_ms,
            "cooldown_remaining": max(0, config.cooldown_seconds - elapsed / 1000),
        },
    }


# ── Profile: Thread Pool Creation & Scheduling Overhead ──

def profile_pool_overhead():
    """Measure FreeThreadPool creation time vs task scheduling time."""
    print("=" * 70)
    print("PHASE 1: FreeThreadPool Creation & Scheduling Overhead")
    print("=" * 70)

    for num_workers in [4, 8, 16, 32, 64]:
        # Measure pool creation
        t0 = time.perf_counter()
        pool = FreeThreadPool(max_workers=num_workers, thread_name_prefix="prof-create")
        creation_time = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        with pool as p:
            enter_time = (time.perf_counter() - t1) * 1000

            # Submit N empty tasks
            t2 = time.perf_counter()
            futures = [p.submit(lambda: None) for _ in range(num_workers)]
            submit_time = (time.perf_counter() - t2) * 1000

            # Collect results
            t3 = time.perf_counter()
            for f in as_completed(futures, timeout=10):
                f.result()
            collect_time = (time.perf_counter() - t3) * 1000

        total = creation_time + enter_time + submit_time + collect_time
        print(f"  Workers={num_workers:>3}: create={creation_time:.2f}ms, "
              f"enter={enter_time:.2f}ms, submit={submit_time:.2f}ms, "
              f"collect={collect_time:.2f}ms, total={total:.2f}ms")


# ── Profile: 100-Worm Parallel Execution ──

def profile_100worm_execution():
    """Profile 100 synthetic worms through FreeThreadPool with cProfile."""
    print()
    print("=" * 70)
    print("PHASE 2: 100-Worm Parallel Execution — cProfile Analysis")
    print("=" * 70)

    # Generate 100 synthetic worm configs with distributed latencies:
    # - 20 fast worms (10-30ms)
    # - 30 medium worms (30-80ms)
    # - 30 medium-slow worms (80-150ms)
    # - 20 slow worms (150-300ms)
    random.seed(42)  # Reproducible
    configs = []
    for i in range(20):
        configs.append(SynthWormConfig(
            name=f"worm_fast_{i:02d}", priority=9,
            latency_ms=random.randint(10, 30), fail_rate=0.02))
    for i in range(30):
        configs.append(SynthWormConfig(
            name=f"worm_med_{i:02d}", priority=7,
            latency_ms=random.randint(30, 80), fail_rate=0.05))
    for i in range(30):
        configs.append(SynthWormConfig(
            name=f"worm_slow_{i:02d}", priority=5,
            latency_ms=random.randint(80, 150), fail_rate=0.08))
    for i in range(20):
        configs.append(SynthWormConfig(
            name=f"worm_heavy_{i:02d}", priority=3,
            latency_ms=random.randint(150, 300), fail_rate=0.10))

    configs.sort(key=lambda c: c.priority, reverse=True)

    print(f"  Total configs: {len(configs)}")
    print(f"  Fast (10-30ms): 20, Med (30-80ms): 30, Slow (80-150ms): 30, Heavy (150-300ms): 20")
    print(f"  Free-threaded: {is_free_threaded()}")
    print()

    # ── Run with cProfile ──
    max_workers = min(len(configs), os.cpu_count() or 8)
    print(f"  max_workers: {max_workers}")
    print()

    profiler = cProfile.Profile()
    profiler.enable()

    # --- Main execution (same pattern as CLUSTERWORMS.execute_all) ---
    t0_wall = time.perf_counter()
    results = []
    timed_out = []

    with FreeThreadPool(max_workers=max_workers, thread_name_prefix="worm-prof") as pool:
        # Submit all worms
        futures = {}
        for config in configs:
            future = pool.submit(synth_execute_worm, config)
            futures[future] = config.name

        # Collect results via as_completed
        timeout = 30.0
        try:
            for future in as_completed(futures, timeout=timeout):
                name = futures[future]
                try:
                    result = future.result(timeout=1.0)
                    results.append(result)
                except TimeoutError:
                    timed_out.append(name)
                    results.append({
                        "name": name, "success": False,
                        "duration_ms": timeout * 1000,
                        "error": f"Timed out after {timeout}s",
                        "timed_out": True,
                    })
                except Exception as e:
                    results.append({
                        "name": name, "success": False,
                        "duration_ms": 0,
                        "error": str(e),
                    })
        except TimeoutError:
            for future, name in futures.items():
                if name not in [r.get("name") for r in results]:
                    timed_out.append(name)
                    results.append({
                        "name": name, "success": False,
                        "error": "Pool-level timeout",
                        "timed_out": True,
                    })

    wall_elapsed = (time.perf_counter() - t0_wall) * 1000
    profiler.disable()
    # --- End main execution ---

    # ── Analyze Results ──
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count
    durations = [r.get("duration_ms", 0) for r in results]

    print(f"  Results: {success_count}/{len(results)} succeeded, "
          f"{fail_count} failed, {len(timed_out)} timed out")
    print(f"  Wall-clock: {wall_elapsed:.0f}ms")
    if durations:
        sorted_dur = sorted(durations)
        print(f"  Min duration: {sorted_dur[0]:.0f}ms")
        print(f"  Max duration: {sorted_dur[-1]:.0f}ms")
        print(f"  P50: {sorted_dur[len(sorted_dur)//2]:.0f}ms")
        print(f"  P95: {sorted_dur[int(len(sorted_dur)*0.95)]:.0f}ms")
        print(f"  P99: {sorted_dur[int(len(sorted_dur)*0.99)]:.0f}ms")
        total_cpu = sum(durations)
        print(f"  Total CPU time: {total_cpu:.0f}ms")
        efficiency = (total_cpu / (wall_elapsed * max_workers)) * 100 if wall_elapsed > 0 and max_workers > 0 else 0
        print(f"  Parallel efficiency: {efficiency:.1f}%")

    # ── cProfile Stats ──
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumtime")
    print(f"\n  --- Top 20 by cumulative time ---")
    ps.print_stats(20)

    # Sort by tottime (self time) to find CPU hotspots
    s2 = io.StringIO()
    ps2 = pstats.Stats(profiler, stream=s2).sort_stats("tottime")
    print(f"\n  --- Top 20 by self time (CPU hotspots) ---")
    ps2.print_stats(20)

    # Sort by call count to find hot-path functions
    s3 = io.StringIO()
    ps3 = pstats.Stats(profiler, stream=s3).sort_stats("ncalls")
    print(f"\n  --- Top 20 by call count ---")
    ps3.print_stats(20)

    return results, profiler


# ── Profile: Scaling Analysis ──

def profile_scaling():
    """Test throughput at various concurrency levels with 100 worms."""
    print()
    print("=" * 70)
    print("PHASE 3: Scaling Analysis — Concurrency Levels vs Throughput")
    print("=" * 70)

    # Generate stable workload: 100 worms, each 30ms
    random.seed(42)
    configs = [
        SynthWormConfig(
            name=f"worm_scale_{i:03d}",
            latency_ms=30,
            priority=5,
            fail_rate=0.0,
        )
        for i in range(100)
    ]

    for workers in [2, 4, 8, 16, 32, 50, 64, 100]:
        t0 = time.perf_counter()
        results = []

        with FreeThreadPool(max_workers=workers, thread_name_prefix="scale-prof") as pool:
            futures = {pool.submit(synth_execute_worm, c): c.name for c in configs}
            for future in as_completed(futures, timeout=120):
                try:
                    results.append(future.result(timeout=1.0))
                except TimeoutError:
                    results.append({"success": False, "error": "timeout"})

        wall = (time.perf_counter() - t0) * 1000
        throughput = len(results) / (wall / 1000) if wall > 0 else 0
        success = sum(1 for r in results if r.get("success"))
        print(f"  Workers={workers:>3}: wall={wall:>7.0f}ms, "
              f"throughput={throughput:>6.0f} worms/s, "
              f"success={success}/{len(results)}")

    # Also test with WorkStealingPool for comparison
    print(f"\n  --- WorkStealingPool comparison ---")
    from CORE.freethreading import WorkStealingPool
    for workers in [4, 8, 16, 32]:
        t0 = time.perf_counter()
        wsd_configs = list(configs)  # copy
        tasks = [(synth_execute_worm, (c,), {}) for c in wsd_configs]

        with WorkStealingPool(num_workers=workers, thread_name_prefix="ws-prof") as pool:
            pool.submit_all(tasks)
            pool.wait_all(timeout=120)
            results = pool.results()

        wall = (time.perf_counter() - t0) * 1000
        s = pool.stats
        throughput = len(results) / (wall / 1000) if wall > 0 else 0
        print(f"  WS Workers={workers:>3}: wall={wall:>7.0f}ms, "
              f"throughput={throughput:>6.0f} worms/s, "
              f"steals={s['steals_succeeded']}/{s['steals_failed']}, "
              f"imbalance={s['load_imbalance']}")


# ── Profile: Lock Contention Under Free-Threading ──

def profile_lock_contention():
    """Measure lock contention on results append under high concurrency."""
    print()
    print("=" * 70)
    print("PHASE 4: Lock Contention Analysis")
    print("=" * 70)

    if not is_free_threaded():
        print("  SKIP: Not running free-threaded Python (GIL serializes, no contention)")
        return

    # Compare: lock-per-append vs batch-collection vs lock-free queue
    num_tasks = 100
    results_lock = threading.Lock()
    results_list = []

    def worker_with_lock(result: int):
        time.sleep(0.001)  # 1ms work
        with results_lock:
            results_list.append(result)

    def worker_batch(results_batch: list, result: int):
        time.sleep(0.001)
        results_batch.append(result)

    # Test 1: Lock per append
    results_list.clear()
    t0 = time.perf_counter()
    with FreeThreadPool(max_workers=16, thread_name_prefix="lock-prof") as pool:
        futures = [pool.submit(worker_with_lock, i) for i in range(num_tasks)]
        for f in as_completed(futures, timeout=30):
            f.result()
    lock_wall = (time.perf_counter() - t0) * 1000

    # Test 2: Batch collection (no lock — each worker gets its own batch)
    t0 = time.perf_counter()
    batch_size = 10
    batches = [list(range(i, min(i + batch_size, num_tasks)))
               for i in range(0, num_tasks, batch_size)]
    all_results = []
    with FreeThreadPool(max_workers=16, thread_name_prefix="batch-prof") as pool:
        def process_batch(nums):
            local = []
            for n in nums:
                time.sleep(0.001)
                local.append(n)
            return local
        futures = [pool.submit(process_batch, b) for b in batches]
        for f in as_completed(futures, timeout=30):
            all_results.extend(f.result())
    batch_wall = (time.perf_counter() - t0) * 1000

    # Test 3: as_completed() single-threaded append (no lock needed)
    results_list.clear()
    t0 = time.perf_counter()
    with FreeThreadPool(max_workers=16, thread_name_prefix="ac-prof") as pool:
        futures = [pool.submit(lambda i=i: (time.sleep(0.001), i)[1], i)
                   for i in range(num_tasks)]
        for f in as_completed(futures, timeout=30):
            results_list.append(f.result())  # Single-threaded — lock-free
    ac_wall = (time.perf_counter() - t0) * 1000

    print(f"  Lock-per-append:    {lock_wall:.1f}ms")
    print(f"  Batch collection:   {batch_wall:.1f}ms")
    print(f"  as_completed loop:  {ac_wall:.1f}ms (lock-free, single thread)")
    if lock_wall > 0:
        print(f"  Lock overhead:      {lock_wall - ac_wall:.1f}ms "
              f"({((lock_wall/ac_wall)-1)*100:.0f}% of lock-per-append)")


# ── Main ──

def main():
    print("=" * 70)
    print("  100-Worm Parallel Execution — cProfile & Optimization Analysis")
    print("=" * 70)
    info = get_thread_info()
    print(f"  Python: {info['python_version']}")
    print(f"  Free-threaded: {info['free_threaded']}")
    print(f"  CPU cores: {info['cpu_count']}")
    print(f"  Effective parallelism: {info['effective_parallelism']}")
    print()

    # Phase 1: Pool overhead
    profile_pool_overhead()

    # Phase 2: 100-worm cProfile
    results, profiler = profile_100worm_execution()

    # Phase 3: Scaling analysis
    profile_scaling()

    # Phase 4: Lock contention
    profile_lock_contention()

    # ── Summary & Recommendations ──
    print()
    print("=" * 70)
    print("SUMMARY: Bottleneck Analysis & Optimization Recommendations")
    print("=" * 70)

    wall_times = [r.get("duration_ms", 0) for r in results if r.get("success")]
    if wall_times:
        avg = sum(wall_times) / len(wall_times)
        print(f"\n  Worm execution stats:")
        print(f"    Average worm time: {avg:.0f}ms")
        print(f"    Total worms: {len(results)} ({sum(1 for r in results if r.get('success'))} success, "
              f"{sum(1 for r in results if not r.get('success'))} failed)")
        print(f"\n  Key Bottlenecks (check cProfile output above):")
        print(f"    1. Thread pool creation (FreeThreadPool.__enter__)")
        print(f"    2. Pool.submit() per-worm overhead")
        print(f"    3. as_completed() iteration overhead")
        print(f"    4. Lock contention on shared state (if any)")
        print(f"    5. Individual worm execution (latency dominant)")
        print(f"\n  Optimization Priority:")
        print(f"    P0: Eliminate lock contention in result collection (already done — as_completed loop)")
        print(f"    P1: Batch worm submission for large clusters (>50 worms)")
        print(f"    P2: Adaptive max_workers based on workload distribution")
        print(f"    P3: Work-stealing for unbalanced worm latencies (fast vs slow)")

    # Save profile data
    prof_path = Path(__file__).resolve().parent / "_profile_100worm.prof"
    profiler.dump_stats(str(prof_path))
    print(f"\n  cProfile stats saved to: {prof_path}")
    print()


if __name__ == "__main__":
    main()
