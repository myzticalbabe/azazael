#!/usr/bin/env python3
"""
azazael-observability — Unified CLI for Azazael observability.

Combines health endpoint server, observability dashboard, and training pipeline
into a single command with sub-commands.

Usage:
    python cli_observability.py dashboard          # Run the dashboard
    python cli_observability.py dashboard --watch  # Live-repeating dashboard
    python cli_observability.py health             # Start health endpoint server
    python cli_observability.py health --check     # One-shot health check
    python cli_observability.py train              # Run one training pipeline
    python cli_observability.py all                # Start health server + dashboard
    python cli_observability.py all --watch        # Health server + live dashboard
"""
import os
import sys
import json
import time
import socket
import argparse

# Ensure src is on path
_src = os.path.join(os.path.dirname(__file__), "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


def cmd_dashboard(args):
    """Run the observability dashboard."""
    from CORE.dashboard import run_dashboard as _run
    # Forward all dashboard args
    _run(args)


def cmd_health(args):
    """Start or check the health endpoint server."""
    from CORE.health_server import HealthServer, main as hs_main

    if args.check:
        # One-shot check
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(args.timeout)
            s.connect((args.host, args.health_port))
            data = s.recv(65535)
            print(data.decode("utf-8"))
            s.close()
        except ConnectionRefusedError:
            print(json.dumps({"error": f"No health server on {args.host}:{args.health_port}"}))
            sys.exit(1)
    else:
        # Start server
        server = HealthServer(host=args.host, port=args.health_port)
        print(f"Health server listening on {args.host}:{args.health_port}")
        print("Press Ctrl+C to stop.")
        try:
            server.start()
        except KeyboardInterrupt:
            print("\nShutting down...")
            server.stop()


def cmd_train(args):
    """Run one training pipeline and print results."""
    print("Running training pipeline...")
    try:
        from CORE.WORMS.expansion.scheduling import ScheduledTrainingWorm, ScheduleConfig
        config = ScheduleConfig(
            n_episodes=args.episodes,
            data_limit=args.limit,
            source_filter=args.source,
        )
        trainer = ScheduledTrainingWorm(config=config)
        run = trainer.execute()
        if run.success:
            print(f"  [OK] Run {run.run_id}")
            print(f"       reward={run.avg_reward:.2f}  records={run.records_extracted}")
            print(f"       episodes={run.n_episodes}  duration={run.duration_ms:.0f}ms")
            print(f"       model_version={run.model_version}  q_table_size={run.q_table_size}")
        else:
            print(f"  [FAIL] {run.error}")
    except Exception as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)


def cmd_web(args):
    """Start the web dashboard (HTTP)."""
    from CORE.web_dashboard import WebDashboardServer, export_html

    if args.export:
        path = export_html(args.export, since=args.since)
        print(f"  Exported HTML report to {path}")
        return

    server = WebDashboardServer(
        host=args.host,
        port=args.port,
        watch=args.watch,
        interval=args.interval,
    )
    print(f"Web dashboard starting on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        server.stop()


def cmd_notify(args):
    """Start the alert notifier (Slack webhook)."""
    from CORE.notifier import run_check, start_watcher, get_webhook_url

    webhook_url = args.webhook or get_webhook_url()
    if not webhook_url:
        print("  [NOTIFIER] No Slack webhook URL. Set SLACK_WEBHOOK_URL env var.")
        print("  Alerts will be logged to console only.")

    if args.watch:
        start_watcher(
            webhook_url=webhook_url,
            interval=args.interval,
            web_dashboard=args.web_dashboard,
            prometheus=args.prometheus,
        )
    else:
        run_check(webhook_url)


def cmd_export(args):
    """Export report to file."""
    output = args.output
    since = args.since

    # Determine format from arguments or file extension
    use_html = args.html or output.lower().endswith(".html")
    use_json = args.json_output or output.lower().endswith(".json")

    if use_html:
        from CORE.web_dashboard import export_html
        path = export_html(output, since=since)
        print(f"  HTML report exported to {path}")
    elif use_json:
        from CORE.dashboard import get_report
        import json as _json
        report = get_report(since=since)
        with open(output, "w", encoding="utf-8") as f:
            _json.dump(report, f, indent=2, default=str)
        print(f"  JSON report exported to {os.path.abspath(output)}")
    else:
        print(f"  [ERROR] Unknown output format: {output}. Use .json or .html extension.")
        sys.exit(1)


def cmd_all(args):
    """Start health server + dashboard together."""
    from CORE.health_server import HealthServer, PrometheusServer

    # Start health server in background
    server = HealthServer(host=args.host, port=args.health_port)
    health_t = server.start_background()
    time.sleep(0.5)
    print(f"  Health server started on {args.host}:{args.health_port}")

    # Start Prometheus server in background if requested
    prometheus_server = None
    prometheus_t = None
    if hasattr(args, 'prometheus_port') and args.prometheus_port:
        prometheus_server = PrometheusServer(host=args.host, port=args.prometheus_port)
        prometheus_t = prometheus_server.start_background()
        print(f"  Prometheus endpoint started on {args.host}:{args.prometheus_port}")
        time.sleep(0.3)

    try:
        # Run dashboard (faux args with health-server implied)
        from types import SimpleNamespace
        d_args = SimpleNamespace(
            health=args.health,
            metrics=args.metrics,
            drift=args.drift,
            since=args.since,
            watch=args.watch,
            interval=args.interval,
            health_server=False,  # Already started above
            health_server_port=args.health_port,
            json_output=args.json,
            prometheus_server=False,
            prometheus_server_port=args.prometheus_port or 18421,
        )
        from CORE.dashboard import run_dashboard
        run_dashboard(d_args)
    finally:
        print("  Stopping health server...")
        server.stop()
        if health_t.is_alive():
            health_t.join(timeout=2)
        if prometheus_server:
            print("  Stopping Prometheus endpoint...")
            prometheus_server.stop()
            if prometheus_t and prometheus_t.is_alive():
                prometheus_t.join(timeout=2)


def main():
    parser = argparse.ArgumentParser(
        description="Azazael Observability — health server, dashboard, and training pipeline",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for health server")
    parser.add_argument("--health-port", type=int, default=18420, help="Health server port")
    parser.add_argument("--timeout", type=int, default=5, help="Connection timeout (seconds)")

    sub = parser.add_subparsers(dest="command", help="Command to run")

    # dashboard
    dash = sub.add_parser("dashboard", help="Run observability dashboard")
    dash.add_argument("--health", action="store_true", help="Health check only")
    dash.add_argument("--metrics", action="store_true", help="Metrics only")
    dash.add_argument("--drift", action="store_true", help="Drift alert only")
    dash.add_argument("--since", default=None,
                      help='Time filter: "24h", "30m", "3600s", or ISO date like "2026-01-15"')
    dash.add_argument("--watch", action="store_true", help="Live-repeating view")
    dash.add_argument("--interval", type=int, default=5, help="Refresh interval (s)")
    dash.add_argument("--json", action="store_true", dest="json_output",
                      help="Output JSON instead of formatted view")
    dash.add_argument("--all-servers", action="store_true",
                      help="Start both health server (18420) and Prometheus endpoint (18421) in background")

    # web
    web = sub.add_parser("web", help="Start web dashboard (HTTP)")
    web.add_argument("--watch", action="store_true", help="Auto-refresh mode")
    web.add_argument("--interval", type=int, default=5, help="Refresh interval (s)")
    web.add_argument("--port", type=int, default=18422, help="HTTP port")
    web.add_argument("--export", default=None, help="Export HTML to file and exit")
    web.add_argument("--since", default=None, help='Time filter: "24h", "30m"')

    # notify
    notify = sub.add_parser("notify", help="Alert notifier (Slack webhook)")
    notify.add_argument("--watch", action="store_true", help="Periodic watcher")
    notify.add_argument("--check", action="store_true", help="One-shot check")
    notify.add_argument("--interval", type=int, default=60, help="Check interval (s)")
    notify.add_argument("--webhook", default=None, help="Slack webhook URL")
    notify.add_argument("--web-dashboard", action="store_true", help="Start web dashboard")
    notify.add_argument("--prometheus", action="store_true", help="Start Prometheus endpoint")

    # health
    health = sub.add_parser("health", help="Health endpoint server")
    health.add_argument("--check", action="store_true", help="One-shot check")

    # train
    train = sub.add_parser("train", help="Run one training pipeline")
    train.add_argument("--episodes", type=int, default=50, help="RL episodes")
    train.add_argument("--limit", type=int, default=200, help="Record limit")
    train.add_argument("--source", default=None, help="Source filter")

    # export
    export = sub.add_parser("export", help="Export report to file")
    export.add_argument("--json", action="store_true", dest="json_output",
                        help="Export JSON report (default: auto-detect from extension)")
    export.add_argument("--html", action="store_true", help="Export HTML report")
    export.add_argument("--since", default=None,
                        help='Time filter: "24h", "30m", "3600s", or ISO date')
    export.add_argument("output", help="Output file path (.json or .html)")

    # all
    all_cmd = sub.add_parser("all", help="Health server + dashboard")
    all_cmd.add_argument("--health", action="store_true", help="Health check only")
    all_cmd.add_argument("--metrics", action="store_true", help="Metrics only")
    all_cmd.add_argument("--drift", action="store_true", help="Drift alert only")
    all_cmd.add_argument("--since", default=None,
                      help='Time filter: "24h", "30m", "3600s", or ISO date like "2026-01-15"')
    all_cmd.add_argument("--watch", action="store_true", help="Live-repeating view")
    all_cmd.add_argument("--interval", type=int, default=5, help="Refresh interval (s)")
    all_cmd.add_argument("--json", action="store_true", dest="json_output",
                      help="Output JSON instead of formatted view")
    all_cmd.add_argument("--prometheus-port", type=int, default=None,
                      help="Also start Prometheus metrics endpoint on this port (e.g., 18421)")
    all_cmd.add_argument("--all-servers", action="store_true",
                      help="Start both health server + Prometheus endpoint + dashboard in one command")

    args = parser.parse_args()

    # Handle --all-servers: enable both servers
    if args.command in ("dashboard", "all") and args.all_servers:
        args.health_server = True
        args.prometheus_server = True

    if args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "health":
        cmd_health(args)
    elif args.command == "train":
        cmd_train(args)
    elif args.command == "web":
        cmd_web(args)
    elif args.command == "notify":
        cmd_notify(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "all":
        cmd_all(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
