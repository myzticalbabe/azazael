---
name: azazael-dead-letter-queue
description: Dead Letter Queue — persistent storage for failed worm executions, configurable retry with exponential backoff, analytics, circuit breaker integration.
metadata:
  category: domain
  project: azazael
  priority: high
  auto_load: false
---

# azazael-dead-letter-queue
**Category:** Domain Knowledge
**Priority:** HIGH
**Dependencies:** azazael-worm-analysis, azazael-clusters
**Created:** June 7, 2026

## Purpose
Documents the Dead Letter Queue: persistent storage for failed worm executions, configurable retry with exponential backoff, analytics, circuit breaker integration.

## Key File
`CORE/WORMS/dead_letter_queue.py` — DeadLetterQueue v1.0.0

## Features
- Persistent JSON storage at `~/.azazael/dead_letters.json`
- Thread-safe enqueue/dequeue/replay for Python 3.14t
- Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s... capped at 120s
- `replay_all()` with configurable concurrency
- `analytics()` — top failing worms, error types, retry success rates
- Auto-pruning at 1000 entries (oldest resolved first)
- Atomic file writes (temp → rename)

## Usage
```python
from CORE.WORMS.dead_letter_queue import DeadLetterQueue

dlq = DeadLetterQueue()

# Enqueue a failed worm
dlq.enqueue("SYSTEMZ", {"error": "timeout", "type": "TimeoutError"})

# Replay all pending
results = dlq.replay_all(execute_fn=my_execute_fn)

# Get analytics
stats = dlq.analytics()
print(f"Pending: {stats['pending']}, Success rate: {stats['retry_success_rate']:.0f}%")
```
