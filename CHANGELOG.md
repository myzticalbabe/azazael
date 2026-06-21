# Changelog

## v1.0.0 (2026-06-15)

### Added
- **Structured Logging** (`CORE/logging_config.py`): JSON formatter, rotating file handler, request ID/trace ID propagation, slow query logging (>100ms), structured error logging with error_id, configurable log levels.
- **Prometheus Metrics** (`CORE/metrics.py`): Thread-safe metrics registry with counters, gauges, and latency histograms. HTTP server with `/metrics` (OpenMetrics) and `/health` endpoints. Histogram percentiles (p50/p90/p99) with label support.
- **Deep Data Features** (`direct_memory.py`): 8 new static methods — `explain_query()` (EXPLAIN QUERY PLAN), `schema_diff()` (compare vs expected schema), `event_correlation()` (co-occurring event types), `session_clustering()` (Jaccard similarity grouping), `anomaly_detection()` (unusual session patterns), `trend_analysis()` (7d/30d event rate trends), `session_search()` (full-text across metadata), `data_quality_report()` (nulls, deprecated types, orphans).
- **Audit Trail Depth** (`audit_trail.py`): 3 new functions — `audit_trail_diff()` (UUID-based entry comparison between files), `audit_search_by_content()` (grep-like across all audit fields), `audit_compress_session()` (gzip + metadata sidecar).
- **Backup Enhancements** (`backup.py`): `verify_backup_integrity()` (SHA-256 hash verification against manifest), `restore_backup()` (from manifest with dry_run support).
- **CLI UX** (`azazael_ctl.py`): `--silent` flag, `--color`/`NO_COLOR` support, `--version`, `help <command>` detail, `--format` flag (table/json/csv), `azazael-ctl alias`, `azazael-ctl complete` (completion installer), `--log-level` flag.
- `pyproject.toml`: All CLI entrypoints registered (`azazael-ctl`, `azazael-doctor`, `azazael-maintain`, `azazael-observability`).

### Fixed
- `metrics.py cmd_metrics()`: Fixed f-string syntax that crashed with `AttributeError` on int values and gauge lookups.
- `logging_config.py`: Removed module-level `get_logger("azazael")` that triggered premature logging configuration on import.

## v0.9.0 (2026-06-14)

### Added
- Production gap modules: doctor.py, data_retention.py, rollback.py, backup.py
- Circuit breaker + retry in inference_pool.py
- Event TTL, integrity_check, db_size, batch import in direct_memory.py
- CLI: doctor, config, verify, maintain, stats subcommands + lock file

## v0.8.0 (2026-06-13)

### Added
- Test files: test_property_based.py, test_concurrency_200.py, test_ip_fuzz.py, test_perf_threshold.py, test_validation.py, test_doctor.py
- Test coverage: 78 tests across all modules
- CONTRIBUTING.md with coding standards

### Fixed
- All test files now use temp DB isolation
- cli_memory.py: dynamic DB_PATH resolution
- cli_completion.py: bash script uses case statement

## v0.7.0 (2026-06-12)

### Added
- DirectMemory CD3: purge, merge, tags, search, summary, mermaid, distribution, orphans
- InferencePool CD3: connectivity check, warmup, queue, adaptive concurrency, structured output, token estimation, auto-routing, health
- AuditTrail CD3: sign_existing, keys_rotate, verify_all_anchors, find_duplicates, session_stats, export_json, repair_broken
- CLI CD3: colors, progress bars, --watch mode, dashboard, tab-completion
- ADR-001 (two-ledger system), ADR-002 (free-threading concurrency), ADR-003 (results caching)

## v0.6.0 (2026-06-11)

### Added
- Cross-referencing engine: DM ↔ AJ session linking via correlation_id
- DirectMemory CD1/CD2 schema migrations
- AuditTrail v3.0: Merkle tree, Ed25519 signing, proof-of-omission, anomaly detection
- CrossLedgerDashboard HTML report generation

## v0.5.0 (2026-06-10)

### Added
- DirectMemory persistent session recording
- AuditTrail append-only JSON Lines with SHA-256 hash chaining
- InferencePool parallel LLM dispatch with Ollama
- FreeThreadPool for 3.14t free-threading
- Session cross-referencing infrastructure
