# AZAZAEL — Self-Replicating AI Worm Ecosystem

**Version:** 1.0.0 | **Python:** ≥3.14t (free-threaded) | **Platform:** Windows 64-bit | **Status:** Beta

Azazael is an autonomous system administration framework built on a **worm ecosystem** — self-contained, self-registering modules that discover, monitor, analyze, and heal computing environments. Designed exclusively for Python 3.14t free-threading, Azazael achieves true parallel execution across CPU, GPU, and NPU devices without the Global Interpreter Lock.

---

## Architecture

```
azazael/
├── src/
│   ├── CORE/                  # Foundation layer
│   │   ├── worm_registry.py   # Central registry + auto-discovery + spawn engine
│   │   ├── Agent.py           # FreeThreadedAgent base class
│   │   ├── freethreading.py   # Free-threaded primitives (pools, queues, counters)
│   │   ├── config.py          # Hierarchical configuration
│   │   ├── MemoryBus.py       # Inter-agent message bus
│   │   ├── PamsRecorder.py    # Persistent AI memory recording
│   │   ├── local_memory.py    # SQLite-backed local persistent store
│   │   ├── circuit_breaker.py # Circuit breaker + dead-letter queue
│   │   ├── compliance_auditor.py # Governance and compliance
│   │   ├── worm_governance.py # Naming, dedup, lifecycle management
│   │   ├── secrets_manager.py # Thread-safe secret rotation
│   │   ├── threading_utils.py # Atomic counters, snapshot dicts
│   │   ├── metrics.py         # Metrics collection + health checks
│   │   ├── workflow.py        # Workflow engine with conditional routing
│   │   ├── web_dashboard.py   # Real-time web monitoring dashboard
│   │   ├── health_server.py   # Prometheus + health endpoint server
│   │   ├── dashboard.py       # CLI dashboard
│   │   ├── NeuralPipeline.py  # ML/NLP analysis pipeline
│   │   ├── sb3_agent.py       # Stable-Baselines3 reinforcement learning agent
│   │   ├── AgentPool.py       # Pool of FreeThreadedAgent workers
│   │   ├── error_triage.py    # Error categorization and triage system
│   │   ├── direct_memory.py   # Direct session memory (JSON)
│   │   ├── notifier.py        # Webhook-based notifications
│   │   ├── enforcement_harness.py # Compliance enforcement
│   │   ├── STRUCTURE.py       # Module structure definitions
│   │   ├── STRESS_TEST.py     # System stress testing
│   │   ├── PYTHON_MANAGER.py  # Python version/environment manager
│   │   ├── NODE.py            # Node-level orchestrator
│   │   ├── FREETHREAD_UPGRADE.py # Legacy free-thread utilities
│   │   ├── FreeThreadedAgent.py # Legacy agent base (alias)
│   │   └── WORMS/             # ~80+ worm modules (auto-discovered)
│   ├── ORCHESTRATION/         # System orchestration layer
│   │   ├── HYDRA.py           # Multi-headed orchestration
│   │   ├── HYDRA_ANALYZER.py  # Orchestration analysis
│   │   ├── TARBABY.py         # File system discovery and migration
│   │   ├── HORUS.py           # System monitoring
│   │   ├── ECOSYSTEM_CRAWLER_LAUNCHER.py  # Ecosystem discovery
│   │   ├── ECOSYSTEM_OPTIMIZER.py         # Ecosystem optimization
│   │   └── ml_platforms/      # ML platform integrations (OpenVINO, LM Studio, etc.)
│   ├── INTERPRETERS/          # Cross-language runners (Go, Rust)
│   ├── SHORTCUTS/             # Batch file launchers
│   ├── SCRIPTS/               # Environment setup, LSP, sentinel gate
│   ├── TOOLS/                 # Utility tools
│   ├── UTILITIES/
│   │   ├── TARBABY/           # File migration tools
│   │   ├── TERENCE/           # Code analysis
│   │   ├── KLINK/             # Cross-platform wrappers
│   │   ├── PERSEPHONE/        # WSL sync manager
│   │   └── POINDEXTER/        # Codebase indexing
│   ├── META/                  # Meta-worm spawning and reporting
│   └── tests/                 # 45+ test files
├── docs/                      # Architecture, specs, conversion plans
├── config/                    # YAML/JSON configuration
├── data/                      # Runtime data, PAMS events, fleet dashboards
├── templates/                 # HTML, Mermaid, video templates
└── tests/                     # Integration and unit tests
```

### Key Concepts

**Worms** are self-registering Python classes that each perform a specific system administration task. They auto-discover via `@register_worm` decorator or directory scanning, and are coordinated by the `SpawnDiversityEngine` for balanced, non-overlapping execution.

**Agents** are `FreeThreadedAgent` subclasses that run tasks in parallel using free-threaded thread pools. They feature automatic PAMS memory recording, inter-agent messaging via `MemoryBus`, and hierarchical sub-agent spawning.

| Concept | Description |
|---------|-------------|
| **Worm Registry** | Central `WORM_REGISTRY` dict with auto-discovery, pickle caching for sub-second startup |
| **SpawnDiversityEngine** | Category rotation, cooldown enforcement, time-based patterns, fleet-aware selection |
| **FreeThreadPool** | Auto-sized `ThreadPoolExecutor` for no-GIL parallelism |
| **WorkStealingPool** | Load-balanced thread pool with work-stealing across per-worker queues |
| **MemoryBus** | Topic-based pub/sub messaging between agents (optional PAMS persistence) |
| **PAMS Recorder** | Persistent AI Memory System — records events to SQLite/HTTP |
| **Circuit Breaker** | Failure isolation with dead-letter queue, configurable thresholds |
| **Compliance Auditor** | Governance enforcement with structured compliance checking |

---

## Installation

### Requirements
- **Python 3.14t** (free-threaded build) — *required, no other Python version supported*
- Windows 10/11 64-bit
- `psutil` (auto-installed)

```bash
# 1. Verify Python 3.14t free-threading
python --version                    # Must be 3.14.x
python -c "import sys; print('Free-threaded:', hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled())"
# Must print: Free-threaded: True

# 2. Clone and install
git clone <repo-url>
cd azazael
pip install -e .

# 3. Verify installation
python -c "from CORE.worm_registry import discover_worms; print(f'Discovered: {discover_worms()} worms')"
```

### Optional Dependencies
| Package | Purpose |
|---------|---------|
| `openvino` | GPU/NPU accelerated inference |
| `torch` (CPU) | ML/AI worm training |
| `stable-baselines3` | Reinforcement learning agents |
| `lm-studio` / `ollama` | Local LLM integration |

---

## Quick Start

### Launch the System
```bash
# Option 1: Run the observability dashboard (monitoring UI)
azazael-observability --port 18420
# Opens: http://localhost:18420

# Option 2: Run the full orchestrator
python -c "
from CORE.NODE import AzazaelNode
node = AzazaelNode()
node.run()
"

# Option 3: Discover and spawn worms interactively
python -c "
from CORE.worm_registry import discover_worms, SpawnDiversityEngine
count = discover_worms()
engine = SpawnDiversityEngine()
pick = engine.pick_next_spawn()
print(f'Ready: {count} worms | Next spawn: {pick}')
"
```

### Discover and Run Worms
```python
from CORE.worm_registry import discover_worms, WORM_REGISTRY, SpawnDiversityEngine

# Auto-discover all worm modules (first run: ~40s cold, then <0.2s with cache)
count = discover_worms()
print(f"Found {count} worms in {len(WORM_REGISTRY)} total")

# Use the spawn engine to pick the best worm to run
engine = SpawnDiversityEngine()
next_worm = engine.pick_next_spawn()
print(f"Recommended: {next_worm['type']} ({next_worm['reason']})")
```

### Create a Custom Agent
```python
from CORE.Agent import FreeThreadedAgent, AgentConfig, FreeThreadPool

class MyAnalyzer(FreeThreadedAgent):
    def _run(self, task, pool):
        data = task.get("data")
        # Your analysis logic here
        return {"analyzed": True, "input": data}

agent = MyAnalyzer(AgentConfig(agent_name="my-analyzer"))
result = agent.execute({"data": "hello"})
print(result.result)  # {"analyzed": True, "input": "hello"}
```

### Batch Parallel Execution
```python
tasks = [{"n": i} for i in range(100)]
results = agent.execute_many(tasks, task_type="batch", max_workers=16)
print(f"Completed: {sum(1 for r in results if r.success)}/{len(results)}")
```

---

## Configuration

Azazael uses hierarchical YAML/JSON configuration (`config/config.yaml`, `config/production.yaml`). Key configuration domains:

| Domain | File(s) | Description |
|--------|---------|-------------|
| Paths | `config.yaml` → `PathsConfig` | Project root, G: drive, output directories |
| PAMS | `config.yaml` → `PamsConfig` | Memory recording endpoint, timeouts |
| MemoryBus | `config.yaml` → `MemoryBusConfig` | Pub/sub broker, session management |
| Clusters | `config.yaml` → `ClustersConfig` | Worm cluster definitions |
| Nature | `config.yaml` → `NatureConfig` | Nature cluster discovery |
| Free-threading | `config.yaml` → `FreeThreadingConfig` | Pool sizing, work-stealing |
| Security | `config.yaml` → `SecurityConfig` | Secret rotation, audit |
| Circuit Breaker | `config.yaml` → `CircuitBreakerConfig` | Failure thresholds, backoff |

---

## Project Structure

### Worm Categories (24 categories)
```
monitor       diagnostic    analysis      defense
optimization  orchestration sync          repair
utility       learning      ml            data
visualization container     communication migration
security      config        backup        profiling
telemetry     expansion     network       system
```

### Test Suite (45+ test files)
```bash
# Run all tests (standalone runner — pytest segfaults on 3.14t)
python run_tests.py

# Run specific test
python tests/test_worm_registry.py
python tests/test_clusterworms_unit.py

# Run integration tests (slow)
python run_tests.py --skip-slow
```

### Build System
```bash
# Nuitka standalone executable build (requires patched Nuitka 4.1.2)
python docs/scripts/patch_nuitka_314t.py --apply
# Then use the build scripts in build/standalone/
```

---

## Key Features

- **🔌 Auto-discovery** — Worms register via `@register_worm` decorator; imported modules are auto-discovered with pickle caching for <0.2s cold start
- **🧵 True Parallelism** — Python 3.14t free-threading enables real parallel execution; `WorkStealingPool` provides dynamic load balancing
- **🧠 Persistent Memory** — PAMS Recorder logs every event to SQLite; MemoryBus provides topic-based inter-agent messaging
- **🔁 Spawn Diversity** — Category rotation, cooldown enforcement, time-of-day patterns, fleet-aware prioritization
- **🛡️ Resilience** — Circuit breakers, dead-letter queues, compliance auditor, thread-safe data structures
- **📊 Observability** — Real-time web dashboard with Prometheus metrics, health endpoints, structured logging
- **🤖 ML/AI Integration** — SB3 reinforcement learning agents, OpenVINO async inference, neural pipeline for NLP analysis
- **🔐 Security** — Thread-safe secrets manager, compliance enforcement, input validation on registry parameters

---

## Documentation

| Document | Location |
|----------|----------|
| Architecture Overview | `docs/ARCHITECTURE_DECISION_RECORDS.md` |
| API Reference | `docs/API_REFERENCE.md` |
| Installation Guide | `docs/INSTALL_GUIDE.md` |
| Error Log | `ERROR_LOG.md` (root) |
| Session Startup | `SESSION_STARTUP.md` (root) |
| SOP & Governance | `SOP.md` (root) |
| Conversion Plans | `docs/RUST_CONVERSION_PLAN.md` |
| Video Generation | `docs/VIDEO_GENERATION_PROTOCOL.md` |

---

## Compliance Scanner CLI Reference

The AST Anti-Pattern Scanner (`src/CORE/compliance/scanner.py`) detects 7 anti-pattern categories using AST + regex.

### Basic Usage
```bash
# Scan current directory
python src/CORE/compliance/scanner.py --report

# Scan specific directory with HTML output
python src/CORE/compliance/scanner.py --report --dir src/CORE --format html --open

# CI mode (exit code 1 if findings)
python src/CORE/compliance/scanner.py --report --ci --quiet

# Watch mode (continuous re-scan on file changes)
python src/CORE/compliance/scanner.py --watch --watch-delay 2.0

# Daemon mode (scan every 5 minutes)
python src/CORE/compliance/scanner.py --daemon --daemon-interval 300
```

### All CLI Flags
| Flag | Description |
|------|-------------|
| `--report` | Scan directory and print compliance report |
| `--dir DIR` | Directory to scan (default: current) |
| `--format {text,json,html,junit-xml}` | Output format |
| `--output-dir DIR` | Write findings JSON to directory |
| `--ci` | Exit non-zero if findings exist |
| `--quiet` | Suppress stdout except verdict |
| `--summary-only` | Only print summary counts |
| `--watch` | Watch for file changes and re-scan |
| `--watch-delay N` | Debounce delay (default: 1.0s) |
| `--daemon` | Daemon mode (scan on fixed interval) |
| `--daemon-interval N` | Interval between daemon scans (default: 300s) |
| `--exclude-dirs DIRS` | Comma-separated dirs to exclude |
| `--exclude-files PATT` | Comma-separated glob patterns |
| `--scannerignore PATH` | Path to .scannerignore file |
| `--fail-on CATS` | Categories that cause non-zero exit |
| `--severity {error,warning,info}` | Minimum severity to report |
| `--threshold N` | Only fail if findings > threshold |
| `--max-findings-per-file N` | Cap findings per file |
| `--max-findings-total N` | Cap total findings |
| `--since DATE` | Scan files modified after date |
| `--include-ext EXTS` | File extensions to scan |
| `--ignore-errors` | Skip unreadable files silently |
| `--auto-fix` | Auto-fix emoji and os.system() |
| `--dry-run` | Preview auto-fix changes |
| `--suggest-fix` | Show fix suggestions |
| `--explain` | Show pattern explanations |
| `--compliance-score` | Print 0-100 score with grade |
| `--open` | Open HTML report in browser |
| `--export-dir DIR` | Save to timestamped export dir |
| `--rotate N` | Keep last N exports |
| `--parallel` | Use parallel scanning |
| `--health-check` | Run self-test |
| `--list-rules` | List all anti-pattern rules |
| `--version` | Show version |
| `--init` | Create .scanner-config.yaml |
| `--db-init` | Initialize findings database |
| `--db-history [N]` | Show scan history (N days) |
| `--db-trend [N]` | Show finding trends (N days) |
| `--db-regression [N]` | Show regressions (N days) |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | No findings (or all clean) |
| 1 | Findings detected (CI mode) |
| 2 | Error (invalid args, config issues) |

---

## License

Internal project — Azazael. See `docs/LICENSE_COMPLIANCE_REPORT.md` for third-party license compliance details.
