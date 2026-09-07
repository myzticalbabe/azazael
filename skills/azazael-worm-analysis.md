---
name: azazael-worm-analysis
description: Worm analysis patterns — CLUSTERWORMS dynamic resolution, dead letter queue, work-stealing, circuit breaker integration.
metadata:
  category: domain
  project: azazael
  priority: high
  auto_load: false
---

# azazael-worm-analysis
**Category:** Domain Knowledge
**Priority:** HIGH
**Dependencies:** azazael-worms, azazael-clusters, azazael-parallel
**Created:** June 7, 2026

## Purpose
Documents the worm analysis patterns: CLUSTERWORMS dynamic resolution, dead letter queue, work-stealing, circuit breaker integration.

## Key Files
- `CORE/WORMS/CLUSTERWORMS.py` — Coordinated worm collectives, PAMS, MemoryBus, Mermaid
- `CORE/WORMS/dead_letter_queue.py` — Failed worm persistence, retry with backoff, analytics
- `CORE/freethreading.py` — WorkStealingPool, WorkStealingQueue, FreeThreadPool
- `CORE/circuit_breaker.py` — BreakerRegistry for production-grade execution
- `CORE/worm_registry.py` — @register_worm, WORM_REGISTRY, discover_worms()

## Analysis Pipeline
1. ClusterWORMZ.execute_all() — parallel with FreeThreadPool
2. Failed worms → DeadLetterQueue.enqueue_result()
3. DeadLetterQueue.replay_all() — retry with backoff
4. DeadLetterQueue.analytics() — failure patterns

## Thread Safety
All worm execution is thread-safe for Python 3.14t free-threading. WorkStealingPool provides dynamic load balancing across threads.
