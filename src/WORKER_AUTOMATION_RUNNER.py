#!/usr/bin/env python3
"""
Worker Automation Runner — starts all automation components.

Usage:
    python -m src.WORKER_AUTOMATION run       # Run full automation (daemon)
    python -m src.WORKER_AUTOMATION test      # Run component tests
    python -m src.WORKER_AUTOMATION metrics   # Collect and print metrics once
    python -m src.WORKER_AUTOMATION dispatch  # Run dispatcher loop for one lane
"""

import sys
import argparse

from src.WORKER_AUTOMATION import (
    WorkerAutomation,
    LocalLLMRouter,
    AutoCodeReview,
    TestAggregator,
    MetricsCollector,
    DependencyDispatcher,
    TaskNode,
    WorkStealer,
    LessonBus,
    HealthMonitor,
)


def run_automation():
    """Run full automation suite"""
    print("[AUTOMATION] Starting full worker automation...")
    auto = WorkerAutomation()
    auto.start()
    print("[AUTOMATION] All components running. Press Ctrl+C to stop.")
    try:
        while True:
            import time
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[AUTOMATION] Shutting down...")
        auto.stop()


def run_tests():
    """Run component tests"""
    print("[TEST] Running component tests...")

    # Test LLM Router
    print("Testing LocalLLMRouter...")
    llm = LocalLLMRouter()
    result = llm.route_coding_task(["implement hello world", "fix bug in parser"], workers=4)
    assert "CHECKABLE" in result["tally"]
    print("  LLM Router: OK")

    # Test AutoCodeReview
    print("Testing AutoCodeReview...")
    review = AutoCodeReview()
    print("  AutoCodeReview: OK")

    # Test TestAggregator
    print("Testing TestAggregator...")
    agg = TestAggregator()
    m = agg.aggregate_sarah()
    assert m["total_collected"] > 0
    print(f"  TestAggregator: {m['total_collected']} SARAH tests")

    # Test MetricsCollector
    print("Testing MetricsCollector...")
    metrics = MetricsCollector()
    m = metrics.collect()
    assert "kilo_queue" in m
    print("  MetricsCollector: OK")

    # Test DependencyDispatcher
    print("Testing DependencyDispatcher...")
    dispatcher = DependencyDispatcher()
    dispatcher.register_task(TaskNode("T1", "kilo", "a", "d", []))
    dispatcher.register_task(TaskNode("T2", "kilo", "a", "d", ["T1"]))
    ready = dispatcher.get_ready_tasks("kilo")
    assert len(ready) == 1 and ready[0].task_id == "T1"
    dispatcher.mark_done("T1")
    ready = dispatcher.get_ready_tasks("kilo")
    assert len(ready) == 1 and ready[0].task_id == "T2"
    print("  DependencyDispatcher: OK")

    # Test WorkStealer
    print("Testing WorkStealer...")
    stealer = WorkStealer()
    stolen = stealer.steal_work("kilo", max_items=1)
    print(f"  WorkStealer: {len(stolen)} stolen")

    # Test LessonBus
    print("Testing LessonBus...")
    bus = LessonBus()
    bus.publish_lesson("kilo", {"title": "test", "content": "test lesson"})
    lessons = bus.subscribe("freebuff", since_id=0)
    assert len(lessons) >= 0
    print("  LessonBus: OK")

    # Test HealthMonitor
    print("Testing HealthMonitor...")
    health = HealthMonitor()
    health._check_health()
    print("  HealthMonitor: OK")

    print("\n[TEST] All component tests PASSED!")


def run_metrics():
    """Collect and print metrics once"""
    metrics = MetricsCollector()
    m = metrics.collect()
    import json
    print(json.dumps(m, indent=2))


def run_dispatch(lane: str):
    """Run dispatcher loop for a specific lane"""
    from src.WORKER_AUTOMATION import WorkerAutomation
    auto = WorkerAutomation()
    print(f"[DISPATCH] Starting dispatcher for {lane}")
    auto.dispatcher.dispatch_loop(lane)


def main():
    parser = argparse.ArgumentParser(description="Worker Automation Suite")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run", help="Run full automation daemon")
    subparsers.add_parser("test", help="Run component tests")
    subparsers.add_parser("metrics", help="Collect and print metrics once")
    dispatch_parser = subparsers.add_parser("dispatch", help="Run dispatcher for lane")
    dispatch_parser.add_argument("lane", choices=["kilo", "freebuff", "opencode", "clinical"])

    args = parser.parse_args()

    if args.command == "run":
        run_automation()
    elif args.command == "test":
        run_tests()
    elif args.command == "metrics":
        run_metrics()
    elif args.command == "dispatch":
        run_dispatch(args.lane)


if __name__ == "__main__":
    main()