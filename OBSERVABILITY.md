# Azazael Observability

All-in-one observability for Azazael: health checks, metrics, drift alerts, scheduled training, workflow engine, Prometheus metrics, web dashboard, Slack notifications, and report export.

---

## Quick Start

```bash
# Full dashboard (one-time view)
python cli_observability.py dashboard

# Live-repeating dashboard with all servers
python cli_observability.py dashboard --all-servers --watch

# Start health + Prometheus servers in background + dashboard
python cli_observability.py all --prometheus-port 18421

# Run one training pipeline
python cli_observability.py train

# Query health endpoint
python cli_observability.py health --check

# Web dashboard (open http://localhost:18422 in browser)
python cli_observability.py web

# Export report to JSON
python cli_observability.py export report.json

# Export report to HTML
python cli_observability.py export --html report.html
```

---

## CLI Reference: `cli_observability.py`

### Global Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Host for health/Prometheus servers |
| `--health-port` | `18420` | Health endpoint port |
| `--timeout` | `5` | Connection timeout (seconds) |

### `dashboard` — Observability Dashboard

Display system health, metrics, drift alerts, session info, MetaCluster status, workflow engine, and scheduled training.

| Flag | Description |
|------|-------------|
| `--health` | Health check only |
| `--metrics` | Metrics only |
| `--drift` | Drift alerts only |
| `--since` | Time filter: `"24h"`, `"30m"`, `"3600s"`, or ISO date |
| `--watch` | Live-repeating view (default interval 5s) |
| `--interval` | Refresh interval in seconds (default `5`) |
| `--json` | Output full report as JSON |
| `--all-servers` | Start health server (18420) + Prometheus endpoint (18421) in background |

### `health` — Health Endpoint Server

| Flag | Description |
|------|-------------|
| `--check` | One-shot check (connect to server, print response, exit) |

### `web` — Web Dashboard (HTTP)

Serves a modern HTML dashboard in the browser.

| Flag | Default | Description |
|------|---------|-------------|
| `--watch` | `False` | Auto-refresh mode |
| `--interval` | `5` | Refresh interval (seconds) |
| `--port` | `18422` | HTTP port |
| `--export` | `None` | Export HTML to file and exit (e.g., `--export report.html`) |
| `--since` | `None` | Time filter for exported report |

**Endpoints:**
- `http://localhost:18422/` — HTML dashboard
- `http://localhost:18422/health` — JSON health report
- `http://localhost:18422/prometheus` — Prometheus metrics

### `notify` — Alert Notifier (Slack)

Periodically checks health, drift, and circuit breakers and sends Slack webhook alerts.

| Flag | Default | Description |
|------|---------|-------------|
| `--watch` | `False` | Periodic watcher mode |
| `--check` | `False` | One-shot check and exit |
| `--interval` | `60` | Check interval (seconds) |
| `--webhook` | `None` | Slack webhook URL (or set `SLACK_WEBHOOK_URL` env var) |
| `--web-dashboard` | `False` | Also start web dashboard (port 18422) |
| `--prometheus` | `False` | Also start Prometheus endpoint (port 18421) |

**Configuration via environment variables:**
- `SLACK_WEBHOOK_URL` — Slack Incoming Webhook URL

```bash
# One-shot check
python cli_observability.py notify --check

# Watcher with Slack alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/... python cli_observability.py notify --watch

# Watcher + web dashboard + Prometheus
SLACK_WEBHOOK_URL=https://hooks.slack.com/... python cli_observability.py notify --watch --web-dashboard --prometheus
```

### `train` — Training Pipeline

| Flag | Default | Description |
|------|---------|-------------|
| `--episodes` | `50` | RL episodes |
| `--limit` | `200` | Records to extract |
| `--source` | `None` | Source filter (e.g., `"SystemZ"`) |

### `export` — Report Export

Export the full observability report to a file.

| Flag | Description |
|------|-------------|
| `--json` | Force JSON output |
| `--html` | Force HTML output |
| `--since` | Time filter: `"24h"`, `"30m"`, `"3600s"`, or ISO date |

Format is auto-detected from file extension (`.json` or `.html`).

```bash
# Auto-detect from extension
python cli_observability.py export report.json
python cli_observability.py export report.html

# Force HTML for non-standard extension
python cli_observability.py export --html report.out
```

### `all` — Combined Server + Dashboard

| Flag | Description |
|------|-------------|
| `--health` | Health check only |
| `--metrics` | Metrics only |
| `--drift` | Drift alerts only |
| `--since` | Time filter |
| `--watch` | Live-repeating view |
| `--interval` | Refresh interval (s) |
| `--json` | JSON output |
| `--prometheus-port` | Start Prometheus endpoint on this port |
| `--all-servers` | Start health server + Prometheus endpoint + dashboard |

---

## Web Dashboard: `python -m CORE.web_dashboard`

Serves a modern, responsive HTML dashboard at `http://localhost:18422` with dark theme, cards for each observability section, and auto-refresh support.

```bash
# Serve once
python -m CORE.web_dashboard

# Auto-refresh every 10 seconds
python -m CORE.web_dashboard --watch --interval 10

# Custom port
python -m CORE.web_dashboard --port 18080

# Export to HTML and exit
python -m CORE.web_dashboard --export dashboard.html
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Host to bind to |
| `--port` | `18422` | HTTP port |
| `--watch` | `False` | Auto-refresh mode |
| `--interval` | `5` | Refresh interval (seconds) |
| `--export` | `None` | Export HTML to file and exit |
| `--since` | `None` | Time filter for export |

### HTTP Endpoints

| Path | Content-Type | Description |
|------|-------------|-------------|
| `/` | `text/html` | HTML dashboard with health, metrics, drift, scheduling, MetaCluster, workflows, dead letters, config |
| `/health` | `application/json` | Full JSON health report (same as TCP health endpoint) |
| `/prometheus` | `text/plain` | Prometheus exposition format metrics |

---

## Notifier: `python -m CORE.notifier`

Slack webhook integration for proactive alerting. Checks system health, drift alerts, and circuit breaker dead letters on a configurable interval and sends notifications when issues are detected.

```bash
# One-shot check (console output)
python -m CORE.notifier

# Start watcher
python -m CORE.notifier --watch --interval 300

# With Slack webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... python -m CORE.notifier --watch

# With web dashboard + Prometheus endpoint
SLACK_WEBHOOK_URL=... python -m CORE.notifier --watch --web-dashboard --prometheus
```

### Alert Types

| Component | Trigger | Alert Title |
|-----------|---------|-------------|
| **Health** | Status changes to `down` or `degraded` | `Health Degraded to DOWN` / `DEGRADED` |
| **Health** | Recovery from degraded state | `Health Restored` |
| **Drift** | Critical severity alerts | `Drift Alert` |
| **Drift** | Warning severity alerts | `Drift Warning` |
| **Circuit Breaker** | Dead letters accumulated | `Dead Letter Alert` |

State change detection prevents repeated alerts — only notifies on transitions (ok -> down, degraded -> ok, etc.).

---

## Dashboard: `python -m CORE.dashboard`

| Flag | Description |
|------|-------------|
| `--health` | Health check only |
| `--metrics` | Metrics only |
| `--drift` | Drift alerts only |
| `--json` | JSON output mode |
| `--since` | Time filter e.g. `"24h"`, `"30m"` |
| `--watch` | Live-repeating view |
| `--interval` | Refresh interval (default 5s) |
| `--health-server` | Start health endpoint in background |
| `--health-server-port` | Health server port (default `18420`) |
| `--prometheus-server` | Start Prometheus endpoint in background |
| `--prometheus-server-port` | Prometheus port (default `18421`) |
| `--all-servers` | Start both health + Prometheus |
| `--output` | Write JSON report to file (e.g., `report.json`) |
| `--export-html` | Export standalone HTML report to file (e.g., `report.html`) |

---

## Health Endpoint

TCP server on port **18420** that responds with a JSON health report.

```bash
# Query via CLI
python -m CORE.health_server --check

# Query via socket
python -c "import socket; s=socket.socket(); s.connect(('localhost',18420)); print(s.recv(65535).decode()); s.close()"

# Query via cli_observability
python cli_observability.py health --check
```

### JSON Response Sections

| Section | Description |
|---------|-------------|
| `timestamp` | ISO datetime of report |
| `since` | Present if `--since` was used |
| `health` | Health check report (overall status, component details) |
| `metrics` | Metrics snapshot (count, avg, min, max, p50, p95, p99) |
| `drift` | Drift alert issues (type, severity, message) |
| `dead_letters` | Circuit breaker dead letter summary |
| `config` | System configuration (version, PAMS, circuit breaker, clusters) |
| `session` | LocalMemoryStore stats (total memories, sessions, top sources/events) |
| `metacluster` | MetaCluster status (natures, worms, routing paths, orchestration history) |
| `workflows` | Workflow engine status (templates, execution count, last execution) |
| `scheduling` | Scheduled training runs (recent runs, total count) |
| `breakers` | Circuit breaker stats (only on health endpoint) |

---

## Prometheus Metrics

TCP server on port **18421** that responds with Prometheus exposition format (text/plain).

```bash
# Start with health server
python -m CORE.health_server --prometheus-port 18421

# Query
python -m CORE.health_server --prometheus-check
python -m CORE.health_server --prometheus-check --prometheus-port 18421

# Raw query
python -c "import socket; s=socket.socket(); s.connect(('localhost',18421)); print(s.recv(65535).decode()); s.close()"
```

### Available Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `azazael_health_ok` | gauge | — | Overall health (1=ok, 0=down) |
| `azazael_components_total` | gauge | `status` | Component count by status (ok, degraded, down) |
| `azazael_metric_count` | gauge | `name` | Data points per metric |
| `azazael_metric_avg` | gauge | `name` | Average value per metric |
| `azazael_total_memories` | gauge | — | Total events in LocalMemoryStore |
| `azazael_total_sessions` | gauge | — | Total sessions in LocalMemoryStore |
| `azazael_training_runs_total` | counter | — | Total training pipeline runs |
| `azazael_training_reward_avg` | gauge | — | Average reward from last training run |
| `azazael_worms_total` | gauge | — | Total registered worms across all natures |
| `azazael_orchestration_runs_total` | counter | — | Total MetaCluster orchestration runs |

Metrics are scrapable by standard Prometheus agents. Example `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'azazael'
    static_configs:
      - targets: ['localhost:18421']
```

Prometheus metrics are also available via the web dashboard at `http://localhost:18422/prometheus`.

---

## Training Pipeline

The `ScheduledTrainingWorm` runs the full ML pipeline:

```
DataPipelineWorm -> FeatureEngineer -> RLTrainLoop -> ModelVersioner
```

Results are persisted to LocalMemoryStore for dashboard and health endpoint visibility.

```bash
# Basic run
python cli_observability.py train

# Custom run
python cli_observability.py train --episodes 100 --limit 500 --source SystemZ

# Via worm directly
python -c "
from CORE.WORDS.expansion.scheduling import ScheduledTrainingWorm
t = ScheduledTrainingWorm()
r = t.execute()
print(f'OK' if r.success else f'FAIL: {r.error}')
"
```

---

## Scheduled Scheduler

The scheduler runs the training pipeline on a configurable interval:

```python
from CORE.WORDS.expansion.scheduling import ScheduledTrainingWorm, ScheduleConfig

# Run every 24 hours
trainer = ScheduledTrainingWorm()
trainer.start_scheduler()

# Run every hour
trainer2 = ScheduledTrainingWorm(ScheduleConfig(interval_hours=1.0))
trainer2.start_scheduler()

# Stop
trainer.stop_scheduler()
```

---

## Workflow Engine

Run multi-step workflows with dependency resolution and conditional routing.

```python
from CORE.workflow import WorkflowEngine, Workflow, WorkflowStep

engine = WorkflowEngine()

# Create a workflow from a template
wf = engine.create_from_template("daily_training", {"n_episodes": 100})

# Execute it
result = engine.execute(wf)
print(f"Success: {result.success}")
print(f"Steps: {result.success_count} ok, {result.failure_count} fail")
```

Built-in templates:
- `daily_training` — ML pipeline: extract -> engineer -> train -> register
- `system_health_check` — Monitor -> diagnose -> report
- `security_audit` — Security scan -> analyze

Custom DSL workflows:
```python
wf = engine.parse_dsl({
    "name": "custom_pipeline",
    "params": {"threshold": 10},
    "steps": [
        {"id": "step1", "action": "sleep", "params": {"seconds": 1}},
        {"id": "step2", "action": "log", "params": {"message": "Done"},
         "depends_on": ["step1"]},
    ],
})
result = engine.execute(wf)
```

---

## Report Export

Export the full observability report as JSON or standalone HTML.

```bash
# JSON export (via dashboard)
python -m CORE.dashboard --output report.json

# HTML export (via dashboard)
python -m CORE.dashboard --export-html report.html

# JSON export (via CLI)
python cli_observability.py export report.json

# HTML export (via CLI)
python cli_observability.py export --html report.html

# With time filter
python cli_observability.py export report.json --since 24h

# Via web dashboard module
python -m CORE.web_dashboard --export dashboard.html
```

Exported HTML reports are self-contained — they include all CSS inline and can be opened offline in any browser.

---

## Running Tests

```bash
# All observability tests (fast)
python tests/test_observability.py

# Include slow integration tests (TCP servers)
python tests/test_observability.py --slow

# List test files
python tests/test_observability.py --list

# Via run_tests.py
python run_tests.py --observability

# Individual test files
python tests/test_dashboard_filters.py
python tests/test_health_server.py
python tests/test_server_integration.py
python tests/test_scheduling.py
python tests/test_workflow.py
python tests/test_cli_observability.py
python tests/test_web_dashboard.py
```

---

## Architecture

```
+------------------------------------------------+
|              cli_observability.py                |
|  +--------+ +--------+ +-------+ +--------+   |
|  |dashboard| | health | | train | |  all   |   |
|  +--------+ +--------+ +-------+ +--------+   |
|  +--------+ +--------+ +--------+             |
|  |  web   | | notify | | export |             |
|  +--------+ +--------+ +--------+             |
+--------+---------+-----------+---------+-------+
         |         |           |         |
    +----v----+ +--v--+ +-----v-----+ +--v--+
    |dashboard| | web_ | |health_   | |notif|
    |  .py    | |dash  | |server.py | |.py  |
    +----+----+ | .py  | +----+-----+ +--+--+
         |      +------+      |           |
    +----v----+          +----v-----+ +---v---+
    |get_     |          |Health    | |Slack  |
    |report() |          |Server    | |Webhook|
    +---------+          +----------+ +-------+
```

Data flows:
1. **Dashboard** reads from `HealthCheck`, `MetricsCollector`, `DriftAlert`, `BreakerRegistry`, `LocalMemoryStore`, `MetaCluster`, `WorkflowEngine`
2. **Health endpoint** delegates to `get_report()` from dashboard + adds breaker stats
3. **Prometheus endpoint** reads from the same sources but formats as text/plain
4. **Web dashboard** reads from `get_report()` and renders HTML with dark-theme cards
5. **Notifier** periodically checks health/drift/breakers and sends Slack webhook alerts
6. **Export** writes `get_report()` as JSON or renders HTML via `web_dashboard.export_html()`
7. **ScheduledTrainingWorm** persists results to `LocalMemoryStore` for dashboard visibility
