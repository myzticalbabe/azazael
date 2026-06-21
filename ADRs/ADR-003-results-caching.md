# ADR-003: Query Result Caching Strategy

**Status:** Implemented (CD3, June 2026)

## Context

Frequently-queried aggregates like `summary_stats()` and `get_mapping_summary()`
recalculate from scratch on every call, causing unnecessary DB scans.

## Decision

Use a simple in-memory TTL-based cache:
- **Cache key**: Arbitrary string (e.g., `"summary_stats"`).
- **Cache value**: Serialized dict (directly returned).
- **TTL**: Configurable per entry (default 30s).
- **Invalidation**: `_cache_invalidate(pattern)` clears matching keys.
  `_cache_invalidate()` with no pattern clears all.
- **Thread safety**: `threading.Lock()` around dict operations.

No external caching library (Redis, memcached) — this is an offline CLI tool.

## Consequences

- `summary_stats()` is ~100x faster when cached (0.1ms vs 10ms).
- Cache is automatically invalidated on writes via `_cache_invalidate("summary")`.
- No external dependency required.
