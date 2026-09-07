---
name: azazael-work-stealing
description: WorkStealingPool and WorkStealingQueue — dynamic load balancing across threads for Python 3.14t free-threading.
metadata:
  category: parallel
  project: azazael
  priority: high
  auto_load: false
---

# azazael-work-stealing
**Category:** Domain Knowledge
**Priority:** HIGH
**Dependencies:** azazael-parallel, azazael-threading
**Created:** June 7, 2026

## Purpose
Documents the WorkStealingPool and WorkStealingQueue: dynamic load balancing across threads for Python 3.14t free-threading.

## Key File
`CORE/freethreading.py` — WorkStealingPool, WorkStealingQueue (added to existing FreeThreadPool module)

## Design
- Each worker has its own `WorkStealingQueue` (LIFO push/pop for cache locality)
- Idle workers steal from the front (FIFO) of other workers' queues
- Random victim selection minimizes lock contention
- Steal success rate tracked for performance monitoring
- Suitable for heterogeneous workloads where some tasks take longer than others

## When to Use WorkStealingPool vs FreeThreadPool
- **WorkStealingPool**: Heterogeneous workloads, variable task duration, many small tasks
- **FreeThreadPool**: Homogeneous workloads, fixed task duration, I/O-bound tasks

## Usage
```python
from CORE.freethreading import WorkStealingPool

with WorkStealingPool(num_workers=8) as pool:
    for arg in args:
        pool.submit(heavy_fn, arg)
    pool.wait_all(timeout=60)
    results = pool.results()
    print(pool.stats)  # Steal success rate, load imbalance
```

## Stats
- `steals_succeeded` / `steals_failed` — work-stealing efficiency
- `load_imbalance` — max queue size minus min queue size
- `steal_success_rate` — percentage of steal attempts that found work
