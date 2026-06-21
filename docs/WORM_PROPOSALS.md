# WORM PROPOSALS — New Worms for Python 3.14t Free-Threading

**Proposed:** June 4, 2026 | **Python 3.14t** | **Priority: P0-P3**

---

## Proposal 1: RaceConditionDetector 🔴 P0

**Purpose**: Automated detection of race conditions across worm operations in 3.14t free-threaded mode.

**Rationale**: With 3.14t's GIL removal, worms execute truly concurrently. The audit found 16 worms with partial/no thread safety. A dedicated race detection worm would catch these before they cause silent corruption.

**Architecture**:
- Wraps `threading` lock acquisition with tracing
- Monitors shared mutable state access patterns
- Flags concurrent writes to unguarded attributes
- Integrates with MetaCognitionWorm for anomaly pattern learning

**Methods**:
- `instrument_worm(worm_instance)` — Wraps a worm with lock tracing
- `detect_data_races()` — Analyzes access logs for concurrent write conflicts
- `generate_safety_report()` — Per-worm thread safety recommendations

**Standalone .exe**: `azazael-race-detector.exe` — Run against any Python 3.14t project.

---

## Proposal 2: ErrorRecoveryOrchestrator 🔴 P0

**Purpose**: Centralized error recovery for all 38 worms with retry, fallback, and circuit-breaking.

**Rationale**: Only 15 worms have full error recovery. The remaining 23 either have partial recovery or none at all. A centralized recovery orchestrator would:
- Retry failed worm executions with exponential backoff
- Fallback to degraded mode when dependencies fail
- Circuit-break worms that consistently fail
- Record recovery patterns for MetaCognitionWorm learning

**Architecture**:
- Wraps `worm.execute()` calls with retry logic
- Tracks failure counts per worm → triggers circuit breaker
- Fallback strategy: degrade gracefully (e.g., skip non-critical worms)

**Methods**:
- `execute_with_recovery(worm_type, worm_instance)` — Retry wrapper
- `get_circuit_breaker_status()` — Which worms are currently broken
- `reset_circuit(worm_type)` — Manual reset after fix

**Standalone .exe**: `azazael-recovery-orchestrator.exe`

---

## Proposal 3: SubAgentPoolManager 🟠 P1

**Purpose**: Dynamic sub-agent pool management for parallel 3.14t execution.

**Rationale**: Only 8 of 38 worms spawn sub-agents. The remaining 30 execute sequentially. With 3.14t free-threading, all worms could benefit from parallel sub-agent execution.

**Architecture**:
- Pluggable pool manager that any worm can use
- Work-stealing queue for load balancing
- Automatic thread count adjustment based on system load
- Integration with CurativePool for governance

**Methods**:
- `spawn_sub_agent(worm_type, task)` — Create a sub-agent from any worm
- `execute_parallel(tasks)` — Run multiple worm tasks in parallel
- `get_pool_stats()` — Active/queued/completed counts

**Standalone .exe**: `azazael-subagent-pool.exe`

---

## Proposal 4: SessionStateManager 🟠 P1

**Purpose**: Automatic session persistence for all 38 worms — save/restore state across runs.

**Rationale**: Before June 4 fixes, zero worms persisted state. After fixes, only 3 of 38 have auto-save. A state manager would:
- Snapshot all worm states on shutdown
- Restore on startup
- Version worm state schemas
- Handle migration when worm APIs change

**Architecture**:
- Pluggable `save_state()` / `load_state()` interface
- Each worm registers its state schema
- Persists to LocalMemoryStore with versioning
- Auto-migrates state when worm version changes

**Methods**:
- `register_worm_state(worm_type, get_state_fn, set_state_fn)`
- `snapshot_all()` — Save all registered worm states
- `restore_all()` — Load all registered worm states
- `migrate_state(worm_type, from_version, to_version)`

**Standalone .exe**: `azazael-session-state.exe`

---

## Proposal 5: CrossWormOptimizer 🟡 P2

**Purpose**: Multi-objective optimization across worm parameter spaces, using Pareto-front evolution.

**Rationale**: The EvolutionEngine already supports NSGA-II multi-objective optimization. A cross-worm optimizer would optimize across worm boundaries — e.g., balance SYSTEMZ scan frequency vs NETWORXZ poll interval vs memory usage.

**Architecture**:
- Builds on EvolutionEngine.optimize_multi_objective()
- Defines cross-worm objective functions (throughput, latency, memory)
- Discovers Pareto-optimal worm configurations
- Integrates with HydraBridge for pipeline-level optimization

**Methods**:
- `optimize_cross_worm(worm_configs, objective_fns)` — Multi-worm multi-objective
- `get_pareto_front()` — Non-dominated configurations
- `apply_optimal_config(config)` — Deploy optimal config to live worms

**Standalone .exe**: `azazael-cross-worm-optimizer.exe`

---

## Proposal 6: WormCompiler 🟡 P2

**Purpose**: Compile individual worm functions to standalone .exe via Nuitka/Python 3.14t.

**Rationale**: The Azazael Standalone Suite (39 .exe files) needs automation. Rather than hand-building each .exe, a compiler worm would:
- Analyze worm dependency graph
- Generate minimal import set per worm
- Invoke Nuitka with correct flags for 3.14t free-threading
- Test the resulting .exe

**Methods**:
- `analyze_dependencies(worm_type)` — Find minimum imports
- `compile_to_exe(worm_type, output_dir)` — Build standalone .exe
- `test_exe(exe_path)` — Smoke test the compiled executable
- `compile_suite(worm_types)` — Build all requested .exe files

**Standalone .exe**: `azazael-compiler.exe` — Bootstraps itself

---

## Proposal 7: DockerOrchestrator 🟢 P3

**Purpose**: Containerize individual worms as microservices with Docker Compose orchestration.

**Rationale**: The expansion/container.py worm provides basic Docker support. A full orchestrator would:
- Generate Dockerfiles per worm type
- Create docker-compose.yml for worm networks
- Manage container lifecycle (start/stop/restart/healthcheck)
- Expose worm APIs via HTTP endpoints

**Methods**:
- `containerize_worm(worm_type)` — Generate Dockerfile
- `compose_cluster(worm_types)` — Generate docker-compose.yml
- `deploy_cluster()` — Docker compose up
- `health_check()` — Verify all containers healthy

**Standalone .exe**: `azazael-docker-orchestrator.exe`

---

## Priority Summary

| Priority | Worms | Effort | Impact |
|----------|-------|--------|--------|
| 🔴 P0 | RaceConditionDetector, ErrorRecoveryOrchestrator | 3-5 days each | Prevents silent data corruption |
| 🟠 P1 | SubAgentPoolManager, SessionStateManager | 2-4 days each | Unlocks full 3.14t parallelism |
| 🟡 P2 | CrossWormOptimizer, WormCompiler | 3-5 days each | Multi-worm optimization + auto-builds |
| 🟢 P3 | DockerOrchestrator | 2-3 days | Microservice deployment |
