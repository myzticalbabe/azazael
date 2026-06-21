---
name: azazael-production
description: Azazael production readiness — critical gaps (testing, error recovery, config), high-priority items (performance, docs, observability), effort estimates, roadmap.
metadata:
  category: planning
  project: azazael
---
# Azazael Production — Roadmap & Gaps

## Priority Summary

| Priority | Items | Effort |
|----------|-------|--------|
| 🔴 Critical (blocking prod) | Testing, Error Recovery, Config | 2-3 weeks |
| 🟡 High | Performance, Docs, Observability | 1-2 weeks |
| 🟢 Medium | Registry enhancements, Workflows, CODEX | 2-4 weeks |
| 🔵 Low | Code hygiene, UI/UX, Deployment | 1-3 weeks |

## 🔴 Critical — Blocking Production

### 1. Test Coverage
- [ ] Unit tests for CLUSTERWORMS.py dynamic resolution (3 strategies)
- [ ] Unit tests for NATURE_CLUSTERS.py category discovery
- [ ] Unit tests for METACLUSTER.py routing engine
- [ ] Integration tests for parallel execution
- [ ] Integration tests for cross-nature orchestration
- [ ] Mock tests for PAMS/MemoryBus

### 2. Error Recovery
- [ ] Timeout handling: daemon threads still run after timeout
- [ ] Partial failure handling: should cluster continue or abort?
- [ ] Circuit breaker: stop if error rate exceeds threshold
- [ ] Retry with exponential backoff (currently fixed 0.1s)
- [ ] Dead letter queue for failed executions

### 3. Configuration
- [ ] Centralized config file (YAML/TOML) for clusters
- [ ] Environment variable validation in paths.py
- [ ] Per-nature config overrides

## 🟡 High Priority

### 4. Performance
- [ ] Profile parallel execution bottleneck
- [ ] Consider ThreadPoolExecutor instead of raw threads
- [ ] Cache worm registry lookups
- [ ] Lazy-load worm modules
- [ ] Cache Mermaid graph output
- [ ] Batch PAMS events

### 5. Documentation
- [ ] Module-level docstrings for all new files
- [ ] Architecture diagram in root README
- [ ] API reference for ClusterWORMZ, MetaCluster
- [ ] Usage examples
- [ ] Troubleshooting guide

### 6. Observability
- [ ] Structured logging (JSON) for cluster operations
- [ ] Metrics: execution count, duration, success rate
- [ ] Health check endpoint
- [ ] Alert on worm registration drift

## 🟢 Medium Priority

### 7. Registry Enhancements
- [ ] Validate registry at startup
- [ ] Registry versioning
- [ ] Worm dependency graph
- [ ] Worm health scoring

### 8. Cross-Nature Workflows
- [ ] Standard workflow templates
- [ ] Workflow DSL
- [ ] Conditional routing
- [ ] Workflow history and replay

### 9. CODEX Video Pipeline
- [ ] Install ffmpeg
- [ ] Test full HTML → mp4 generation
- [ ] Progress bar for video generation
- [ ] Multiple output formats (mp4, webm, gif)
- [ ] Batch generation

## 🔵 Low Priority

### 10. Code Hygiene
- [ ] Remove unused PurePosixPath from TRIMZ.py
- [ ] Standardize error handling (bare except)
- [ ] Consolidate _LOCAL_TARGETS config into paths.py
- [ ] Add `__all__` to all module exports

### 11. UI/UX
- [ ] Web dashboard for cluster status
- [ ] Real-time Mermaid rendering
- [ ] CLI `azazael cluster status`
- [ ] CLI `azazael cluster run --nature security`

### 12. Deployment
- [ ] Single-entry `azazael` CLI
- [ ] Docker container
- [ ] Scheduled cluster runs
- [ ] Git hook integration

## Related Skills
- `azazael-deploy` — Docker, CLI packaging, scheduled runs
- `azazael-environment` — Python version, dependencies, path setup
- `azazael-git` — Commit conventions, branching

## Current State
- **256** syntax-clean files
- **77** worms registered
- **0** test files
- **0** configuration files
- **0** deployment artifacts
