---
name: azazael-parallel
description: Azazael 3.14t parallel execution — FreeThreadPool, work-stealing, batch collection, GIL-free optimization. Load when optimizing CLUSTERWORMS/CONCURRENCY parallel performance.
metadata:
  category: architecture
  project: azazael
---
# Azazael Parallel Execution — 3.14t Optimization

## Current State

### CLUSTERWORMS.py (`execute_all`, parallel path)
```python
# Current: one thread per worm, lock per result append
threads = []
results_lock = threading.Lock()
cancel_event = threading.Event()
for config in enabled_configs:
    t = threading.Thread(target=execute_and_collect, daemon=True)
    threads.append((t, config.name))
    t.start()
for t, name in threads:
    t.join(timeout=self.timeout)
```

**Issues with current approach:**
- One thread per worm = up to 77 threads on full ecosystem scan
- `results_lock` contended on every result append (hot path)
- No work-stealing — unbalanced workloads leave threads idle
- Daemon threads can leak if timeout is short
- No thread pool reuse — threads created/destroyed on every call

### CONCURRENCY.py (already migrated)
```python
# Already uses FreeThreadPool (3.14t-aware)
with FreeThreadPool(max_workers=self.config.max_workers) as executor:
    futures = {executor.submit(...): name for task in tasks}
    for future in as_completed(futures):
        results.append(future.result())
```

CONCURRENCY.py is the reference implementation. CLUSTERWORMS.py should follow this pattern.

## 3.14t Free-Threading Impact

### What Changes Under 3.14t
| Aspect | 3.12 (GIL) | 3.14t (Free-Threaded) |
|--------|-----------|----------------------|
| Thread parallelism | Serialized by GIL | True parallelism |
| Lock contention | Rare (GIL serializes) | Real — fix hot paths |
| Thread creation cost | Low | Low (unchanged) |
| Queue.put() | Locked | Lock-free in common case |
| list.append() | Safe (GIL) | MUST use lock or Queue |
| dict operations | Safe (GIL) | MUST use lock |

### Detection
```python
# From CORE/freethreading.py
from CORE.freethreading import is_free_threaded, FreeThreadPool

if is_free_threaded():
    # Use FreeThreadPool (3.14t optimized)
    executor = FreeThreadPool(max_workers=min(len(tasks), os.cpu_count() or 8))
else:
    # Use standard ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=min(len(tasks), 8))
```

## Migration: CLUSTERWORMS.execute_all() → FreeThreadPool

### Before (Current)
```python
# Raw threads, per-result locking
if self.parallel:
    threads = []
    results_lock = threading.Lock()
    cancel_event = threading.Event()
    for config in enabled_configs:
        executor = WormExecutor(config.name, config, self.state)
        t = threading.Thread(
            target=execute_and_collect,
            args=(executor, config.name, max(0, config.retry - 1)),
            daemon=True,
        )
        threads.append((t, config.name))
        t.start()
    for t, name in threads:
        t.join(timeout=self.timeout)
```

### After (Recommended)
```python
# FreeThreadPool, batch result collection, cancellation via future.cancel()
from concurrent.futures import as_completed
from CORE.freethreading import FreeThreadPool, is_free_threaded

if self.parallel:
    max_workers = min(len(enabled_configs), os.cpu_count() or 8)
    pool_cls = FreeThreadPool if is_free_threaded() else ThreadPoolExecutor
    
    with pool_cls(max_workers=max_workers) as pool:
        futures = {}
        for config in enabled_configs:
            future = pool.submit(
                self._execute_single_worm, config
            )
            futures[future] = config.name
        
        for future in as_completed(futures, timeout=self.timeout):
            try:
                result = future.result(timeout=self.timeout)
                results.append(result)  # Single-threaded here — no lock needed
            except TimeoutError:
                future.cancel()
                results.append({"success": False, "error": "timeout"})
            except Exception as e:
                results.append({"success": False, "error": str(e)})

def _execute_single_worm(self, config: WormConfig) -> Dict[str, Any]:
    """Executed in worker thread — no shared state access needed."""
    executor = WormExecutor(config.name, config, self.state)
    result = executor.execute(timeout=self.timeout)
    # Retry logic
    for attempt in range(max(0, config.retry - 1)):
        if result.get("success"):
            break
        time.sleep(0.1)
        result = executor.execute(timeout=self.timeout)
    mark_spawned(config.name)
    return result
```

## Work-Stealing for Unbalanced Workloads

When worms have vastly different cooldowns (5s MetaCluster vs 300s ColdArchivist):

```python
def execute_work_stealing(self, configs: List[WormConfig]) -> List[Dict]:
    """Work-stealing: each worker grabs next task from shared queue."""
    from queue import Queue
    
    task_queue = Queue()
    for config in sorted(configs, key=lambda c: c.cooldown, reverse=True):
        task_queue.put(config)  # Longest cooldowns first
    
    results = []
    
    def worker():
        while True:
            try:
                config = task_queue.get_nowait()
            except:
                return  # No more tasks
            result = self._execute_single_worm(config)
            results.append(result)  # Lock-free — single consumer thread
            task_queue.task_done()
    
    max_workers = min(len(configs), os.cpu_count() or 8)
    threads = [threading.Thread(target=worker) for _ in range(max_workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    return results
```

**When to use work-stealing:**
- Mix of short and long cooldowns (orchestration 5s + backup 300s)
- Unknown worm execution times
- Full ecosystem scans (226 worms with varied costs)

## Batch Result Collection (Lock-Free)

Instead of locking per result, batch inside the worker:

```python
def execute_batched(self, configs: List[WormConfig], batch_size: int = 8) -> List[Dict]:
    """Each worker processes a batch, returns all results at once."""
    batches = [configs[i:i+batch_size] for i in range(0, len(configs), batch_size)]
    
    def process_batch(batch):
        return [self._execute_single_worm(cfg) for cfg in batch]
    
    all_results = []
    with ThreadPoolExecutor(max_workers=len(batches)) as pool:
        for batch_result in pool.map(process_batch, batches):
            all_results.extend(batch_result)  # Single thread — no lock
    
    return all_results
```

## Optimization Priorities

| Priority | Change | Impact | Effort |
|----------|--------|--------|--------|
| P0 | Replace raw threads with FreeThreadPool in execute_all | Eliminates thread leaks, reduces contention | Medium |
| P1 | Move result collection out of lock (batch or Queue) | Eliminates hot-path lock contention | Low |
| P2 | Add work-stealing for full ecosystem scans | Better utilization under unbalanced workloads | Medium |
| P3 | Add adaptive max_workers based on is_free_threaded() | Auto-tunes for GIL vs free-threaded | Low |
| P4 | Profile with GILContentionProbe under 3.14t | Validates optimization effectiveness | Low |

## Testing Parallel Execution

```python
# Write to _test_parallel.py, then execute:
# python _test_parallel.py && rm _test_parallel.py

import sys; sys.path.insert(0, 'src')
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
from CORE.freethreading import is_free_threaded
import time

print(f"Free-threaded: {is_free_threaded()}")

# Sequential baseline
cluster = ClusterWORMZ.build_from_nature("monitor")
t0 = time.time()
results_seq = cluster.execute_sequential()
t_seq = (time.time() - t0) * 1000

# Parallel 
cluster.set_parallel(True)
t0 = time.time()
results_par = cluster.execute_all()
t_par = (time.time() - t0) * 1000

print(f"Sequential: {t_seq:.0f}ms ({len(results_seq)} worms)")
print(f"Parallel:   {t_par:.0f}ms ({len(results_par)} worms)")
print(f"Speedup:    {t_seq/t_par:.1f}x" if t_par > 0 else "N/A")
```

## Related Skills
- `azazael-threading` — Thread safety primitives, Lock/Event/Queue patterns
- `azazael-clusters` — CLUSTERWORMS, CONCURRENCY, MetaCluster APIs
- `azazael-worms-monitor` — GILContentionProbe and profiling worms
