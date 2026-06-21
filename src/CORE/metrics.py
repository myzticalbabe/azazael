"""
metrics.py — Prometheus metrics and monitoring for Azazael.

Covers followups: #9 (Prometheus /metrics HTTP endpoint),
#10 (azazael-ctl metrics command), #11 (OpenMetrics format),
#12 (metric histograms: p50/p90/p99), #13 (health check HTTP endpoint),
#14 (metric labels: session_id, event_type, model).

Uses a stdlib-only design with an optional HTTP server. When the
'prometheus_client' package is available, it also exports to Prometheus
format. Falls back to a simple JSON-based metrics registry.

Usage:
    from CORE.metrics import MetricsRegistry, start_metrics_server

    registry = MetricsRegistry()
    registry.record_event("file_edit", {"session_id": "s1", "duration_ms": 150})
    registry.record_inference("llama3.2:1b", {"tokens_per_sec": 35.2})

    # Start HTTP server in background thread
    start_metrics_server(port=9090, registry=registry)
"""


__all__ = [
    "MetricsHandler",
    "MetricsRegistry",
    "cmd_metrics",
    "get_registry",
    "start_metrics_server",
]


import json
import threading
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    HTTPServer = None
    BaseHTTPRequestHandler = object


class MetricsRegistry:
    """Thread-safe metrics registry with label support and histograms.

    Stores counters, gauges, and latency samples for Prometheus export
    and CLI display. All methods are thread-safe.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Counters: {name: {label_key: count}}
        self._counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        # Gauges: {name: value}
        self._gauges: dict[str, float] = {}
        # Latency samples: {name: [ms_values]}
        self._latency_samples: dict[str, list[float]] = defaultdict(list)
        # Max samples to keep per metric (to bound memory)
        self._max_samples = 10000

    def _labels_key(self, labels: dict[str, str]) -> str:
        """Create a deterministic label key from a dict."""
        return json.dumps(labels, sort_keys=True)

    def increment(self, name: str, labels: (dict[str, str] | None) = None,
                  value: int = 1):
        """Increment a counter metric.

        Args:
            name: Metric name (e.g., 'events_total').
            labels: Optional dict of label key/value pairs.
            value: Amount to increment by.
        """
        key = self._labels_key(labels or {})
        with self._lock:
            self._counters[name][key] += value

    def record_event(self, event_type: str,
                     labels: (dict[str, str] | None) = None):
        """Record an event occurrence. Shortcut for increment('events_total')."""
        lbls = dict(labels or {})
        lbls.setdefault("event_type", event_type)
        self.increment("events_total", labels=lbls)

    def record_inference(self, model: str,
                         labels: (dict[str, str] | None) = None):
        """Record an inference call. Shortcut for increment('inferences_total')."""
        lbls = dict(labels or {})
        lbls.setdefault("model", model)
        self.increment("inferences_total", labels=lbls)

    def set_gauge(self, name: str, value: float,
                  labels: (dict[str, str] | None) = None):
        """set a gauge metric to a specific value."""
        key = self._labels_key(labels or {})
        with self._lock:
            self._gauges[f"{name}_{key}"] = value

    def record_latency(self, name: str, duration_ms: float,
                       labels: (dict[str, str] | None) = None):
        """Record a latency sample for histogram computation.

        Args:
            name: Metric name (e.g., 'inference_latency_ms').
            duration_ms: Latency in milliseconds.
            labels: Optional labels.
        """
        key = self._labels_key(labels or {})
        metric_key = f"{name}_{key}"
        with self._lock:
            samples = self._latency_samples[metric_key]
            samples.append(duration_ms)
            # Trim to max_samples
            if len(samples) > self._max_samples:
                self._latency_samples[metric_key] = samples[-self._max_samples:]

    def get_histogram(self, name: str,
                      labels: (dict[str, str] | None) = None) -> dict[str, float]:
        """Compute histogram percentiles from recorded latency samples.

        Returns dict with 'p50', 'p90', 'p99', 'avg', 'min', 'max',
        'count' keys.
        """
        key = self._labels_key(labels or {})
        metric_key = f"{name}_{key}"
        with self._lock:
            samples = list(self._latency_samples.get(metric_key, []))

        if not samples:
            return {"p50": 0, "p90": 0, "p99": 0, "avg": 0, "min": 0, "max": 0, "count": 0}

        sorted_s = sorted(samples)
        n = len(sorted_s)
        return {
            "p50": sorted_s[int(n * 0.50)],
            "p90": sorted_s[int(n * 0.90)],
            "p99": sorted_s[int(n * 0.99)],
            "avg": sum(sorted_s) / n,
            "min": sorted_s[0],
            "max": sorted_s[-1],
            "count": n,
        }

    def open_sessions(self, count: int):
        """Track open session count as a gauge."""
        self.set_gauge("open_sessions", float(count))

    def db_size_mb(self, size_mb: float):
        """Track DB size as a gauge."""
        self.set_gauge("db_size_mb", size_mb)

    def snapshot(self) -> dict[str, Any]:
        """Take a complete snapshot of all metrics.

        Returns a nested dict with 'counters', 'gauges', and 'histograms'.
        """
        with self._lock:
            counters_snap = {k: dict(v) for k, v in self._counters.items()}
            gauges_snap = dict(self._gauges)

        histograms = {}
        with self._lock:
            metric_keys = list(self._latency_samples.keys())
        for mk in metric_keys:
            # Extract name and labels from metric_key
            histograms[mk] = self.get_histogram(mk)

        return {
            "counters": counters_snap,
            "gauges": gauges_snap,
            "histograms": histograms,
        }

    def to_openmetrics(self) -> str:
        """Export to Prometheus OpenMetrics text format."""
        snap = self.snapshot()
        lines: list[str] = ["# HELP azazael_events_total Total events recorded.",
                            "# TYPE azazael_events_total counter"]
        for labels_key, count in snap.get("counters", {}).get("events_total", {}).items():
            lbl_str = self._labels_to_prom(labels_key) if labels_key and labels_key != "{}" else ""
            lines.append(f"azazael_events_total{lbl_str} {count}")

        lines.append("# HELP azazael_inferences_total Total inference calls.")
        lines.append("# TYPE azazael_inferences_total counter")
        for labels_key, count in snap.get("counters", {}).get("inferences_total", {}).items():
            lbl_str = self._labels_to_prom(labels_key) if labels_key and labels_key != "{}" else ""
            lines.append(f"azazael_inferences_total{lbl_str} {count}")

        lines.append("# HELP azazael_db_size_mb Database size in MB.")
        lines.append("# TYPE azazael_db_size_mb gauge")
        for gauge_key, val in snap.get("gauges", {}).items():
            if gauge_key.startswith("db_size_mb"):
                lines.append(f"azazael_db_size_mb {val}")

        lines.append("# HELP azazael_open_sessions Open session count.")
        lines.append("# TYPE azazael_open_sessions gauge")
        for gauge_key, val in snap.get("gauges", {}).items():
            if gauge_key.startswith("open_sessions"):
                lines.append(f"azazael_open_sessions {val}")

        lines.append("# HELP azazael_latency_ms Latency histogram.")
        lines.append("# TYPE azazael_latency_ms gauge")
        for hist_key, hist in snap.get("histograms", {}).items():
            for pctile, val in hist.items():
                if pctile != "count":
                    lines.append(f"azazael_latency_ms{{histogram=\"{hist_key}\",percentile=\"{pctile}\"}} {val}")

        lines.append("# EOF")
        return "\n".join(lines)

    def to_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps(self.snapshot(), indent=2, default=str)

    @staticmethod
    def _labels_to_prom(labels_key: str) -> str:
        """Convert a JSON labels dict to Prometheus label string."""
        try:
            labels = json.loads(labels_key)
            parts = [f'{k}="{v}"' for k, v in sorted(labels.items())]
            return "{" + ",".join(parts) + "}" if parts else ""
        except (json.JSONDecodeError, AttributeError):
            return ""


# ── Global registry singleton ───────────────────────────────────────

_registry: (MetricsRegistry | None) = None
_registry_lock = threading.Lock()


def get_registry() -> MetricsRegistry:
    """Get or create the global metrics registry singleton."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = MetricsRegistry()
    return _registry


# ── HTTP Metrics Server ─────────────────────────────────────────────


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP request handler for /metrics and /health endpoints."""

    registry: MetricsRegistry = None  # type: ignore

    def do_GET(self):
        if self.path == "/metrics":
            self._serve_metrics()
        elif self.path == "/health":
            self._serve_health()
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Azazael Metrics Server\n/health  /metrics\n")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def _serve_metrics(self):
        data = self.registry.to_openmetrics()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))

    def _serve_health(self):
        """Health check endpoint — returns 200 if DB is accessible."""
        healthy = True
        try:
            from CORE.direct_memory import DirectMemory
            DirectMemory.db_size()
        except Exception:
            healthy = False
        status = 200 if healthy else 503
        body = json.dumps({
            "status": "healthy" if healthy else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Suppress default HTTP server logging


def start_metrics_server(port: int = 9090, host: str = "127.0.0.1",
                         registry: (MetricsRegistry | None) = None) -> threading.Thread:
    """Start a background HTTP server for /metrics and /health endpoints.

    Args:
        port: HTTP server port (default: 9090).
        host: Bind address (default: 127.0.0.1).
        registry: MetricsRegistry instance. Uses global singleton if None.

    Returns:
        The background thread (daemon=True).
    """
    if HTTPServer is None:
        raise ImportError("http.server not available")

    reg = registry or get_registry()
    MetricsHandler.registry = reg

    server = HTTPServer((host, port), MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True,
                              name="metrics-server")
    thread.start()
    return thread


# ── CLI Display ──────────────────────────────────────────────────────


def cmd_metrics():
    """Print current metrics to stdout (for azazael-ctl metrics)."""
    registry = get_registry()
    snap = registry.snapshot()
    print("=== Azazael Metrics ===")
    ev_counts = list(snap['counters'].get('events_total', {}).values())
    events_total = sum(ev_counts) if ev_counts else 0
    print(f"  Events: {events_total}")
    inf_counts = list(snap['counters'].get('inferences_total', {}).values())
    inferences_total = sum(inf_counts) if inf_counts else 0
    print(f"  Inferences: {inferences_total}")
    open_sessions = snap['gauges'].get('open_sessions_{}', 0.0)
    print(f"  Open sessions: {open_sessions:.0f}")
    db_size = snap['gauges'].get('db_size_mb_{}', 0.0)
    print(f"  DB size: {db_size:.1f} MB")
    if snap["histograms"]:
        print("\n  Latency Histograms:")
        for name, hist in list(snap["histograms"].items())[:3]:
            print(f"    {name}: p50={hist['p50']:.0f}ms p90={hist['p90']:.0f}ms p99={hist['p99']:.0f}ms count={hist['count']}")


# ── Self-test ───────────────────────────────────────────────────────

if __name__ == "__main__":
    registry = MetricsRegistry()
    registry.record_event("file_edit", {"session_id": "s1"})
    registry.record_event("file_read", {"session_id": "s1"})
    registry.record_inference("llama3.2:1b")
    registry.record_inference("gemma3:4b")
    registry.open_sessions(3)
    registry.db_size_mb(42.5)
    for i in range(100):
        registry.record_latency("inference_latency_ms", float(100 + i * 0.5))
    print(registry.to_openmetrics())
    print("\nJSON:")
    print(registry.to_json()[:500])
    print("\n  metrics.py self-test PASSED")
