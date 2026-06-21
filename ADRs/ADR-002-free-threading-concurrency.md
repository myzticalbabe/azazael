# ADR-002: Free-Threading Concurrency Model

**Status:** Implemented (Python 3.14t, June 2026)

## Context

Python 3.14t (free-threading build) removes the GIL, allowing true parallel
execution of Python threads. All Azazael components must be thread-safe.

## Decision

- **SQLite**: WAL mode with `check_same_thread=False`. Each thread opens its
  own connection. Busy timeout of 5s prevents deadlocks. PRAGMA
  `wal_autocheckpoint=1000` keeps WAL file bounded.
- **DirectMemory**: Uses `threading.Lock()` per instance for insert serialization.
  Static methods open separate connections (no lock needed for reads).
- **AuditTrail**: Uses `threading.RLock()` for reentrant safety.
- **FreeThreadPool**: Custom thread pool with work-stealing for parallel inference.
- **Connection Pool**: Thread-local connections (`threading.local()`) avoid
  connection churn while maintaining thread safety.

## Consequences

- Truly parallel inference dispatch on Intel Arc 140T GPU (up to 8 concurrent).
- No GIL contention for DM writes under high concurrency (200 threads verified).
- Thread-local connection pool reduces overhead of open/close per query.
