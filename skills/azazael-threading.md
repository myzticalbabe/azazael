---
name: azazael-threading
description: Azazael threading patterns — Python 3.14t free-threading design, threading.Lock, threading.Event, ThreadPoolExecutor, lock-free queues, parallel execution safety.
metadata:
  category: conventions
  project: azazael
  auto_load: true
---
# Azazael Threading — 3.14t Free-Threading Patterns

## Python 3.14t — No-GIL Mode

Python 3.14 introduces free-threading (`python3.14t`). Threads achieve true parallelism. This changes everything for CLUSTERWORMS parallel execution.

### Detection
```python
import sys
is_free_threaded = hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled()
```

## Thread Safety Primitives

### threading.Lock — Mutex
```python
import threading

class WormExecutor:
    def __init__(self):
        self._results_lock = threading.Lock()
        self._results = []
    
    def execute_parallel(self, configs):
        def worker(config):
            result = self._execute_one(config)
            with self._results_lock:  # Critical section
                self._results.append(result)
        # ...
```

**3.14t impact:** Lock contention is real. Keep critical sections minimal. Consider `RLock` only for reentrant needs.

### threading.Event — Cancellation
```python
class ClusterWORMZ:
    def __init__(self):
        self._cancel = threading.Event()
    
    def execute_parallel(self, configs):
        def worker(config):
            if self._cancel.is_set():  # Check cancellation
                return {"success": False, "error": "cancelled"}
            return self._execute_one(config)
        # ...
    
    def cancel(self):
        self._cancel.set()
```

### ThreadPoolExecutor — Preferred Over Raw Threads
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_with_pool(configs, max_workers=8):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(execute_worm, cfg): cfg for cfg in configs}
        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)
                results.append(result)
            except TimeoutError:
                results.append({"success": False, "error": "timeout"})
    return results
```

## 3.14t Optimizations

### Lock-Free Queue (Hot Path)
```python
from queue import Queue  # Thread-safe by design, minimal locking in 3.14t

_result_queue = Queue()

def worker(config):
    result = execute_worm(config)
    _result_queue.put(result)  # Lock-free in 3.14t for common case
```

### Atomic Counter Pattern
```python
import threading

class AtomicCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value
    
    @property
    def value(self) -> int:
        with self._lock:
            return self._value
```

### Batch Results Collection
Instead of locking per-result, batch collect:
```python
def worker_batch(configs_slice):
    """Each thread processes a batch and returns all results at once."""
    local_results = []
    for cfg in configs_slice:
        local_results.append(execute_worm(cfg))
    return local_results  # Single lock per batch, not per worm

# Main thread merges without locking
all_results = []
for batch in thread_results:
    all_results.extend(batch)
```

## Current CLUSTERWORMS Threading Design

### What's Implemented
- `threading.Lock` for `results` list protection
- `threading.Event` for cancellation
- Retry logic in sequential path
- Daemon threads with timeout

### 3.14t Upgrade Path (from azazael-parallel skill)
- Replace raw threads with `ThreadPoolExecutor`
- Add `Queue` for result collection (lock-free)
- Add batch processing per thread
- Add work-stealing for unbalanced workloads

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| `list.append()` without lock (3.14t) | Use lock or Queue |
| `time.sleep()` for synchronization | Use Event or Condition |
| Raw threads for parallel execution | ThreadPoolExecutor |
| Lock held during I/O | Release lock before blocking |
| `cls.__new__()` in threaded factory | `cls()` with proper init |
