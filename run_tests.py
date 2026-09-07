#!/usr/bin/env python3
"""
Azazael Test Runner -- runs all standalone-compatible test files on Python 3.14t.

Usage:
    python run_tests.py                          # run all tests
    python run_tests.py -v                       # verbose output
    python run_tests.py --list                   # list test files only
    python run_tests.py test_agent.py            # run specific file
    python run_tests.py --skip-slow              # skip slow tests (test_metacluster_unit)

On Python 3.14t free-threading:
    - 8 test files run standalone (200+ tests, < 6 min total)
    - 1 test file (test_metacluster_unit.py) is very slow (~12-15 min)
      Because: discover_all() imports 76 worm modules (38s), orchestrate_nature() runs
      the full MetaCluster routing graph triggering CLUSTER INSPECTOR (scans 473 files).
      Optimizations applied: progress prints every 100 (was 10), _get_mc() caches discovery
      across test instances (saves 38s per test). Total: ~700-900s for 7 orchestration tests.
    - Use --skip-slow for quick runs, --timeout 1200 for full runs
"""

import os
import sys
import re
import time
import subprocess
import argparse

TESTS_DIR = os.path.join(os.path.dirname(__file__), "tests")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Files that work standalone on 3.14t (fast, <60s each)
STANDALONE_OK = [
    "test_agent.py",                    # 16 tests (2s)
    "test_binary_analysis_parse.py",    # 17 tests (2s)
    "test_binary_analysis_tools.py",    # 28 tests (2s)
    "test_memorybus.py",                # 32 tests (2s)
    "test_pool.py",                     # 19 tests (2s)
    "test_verify_head_hash_normalization.py",  # 3 tests (<1s, anchor path normalization)
    "test_worm_imports.py",             # 14 tests (3s)
    "test_cluster_worms.py",            # 5 tests (3s)
    "test_clusterworms_unit.py",        # 39 tests (30s, worm execution)
    "test_config_and_breaker.py",       # 36 tests (90s, config + breaker integration)
    "test_nature_clusters_unit.py",     # 37 tests (120s, nature cluster execution)
    "test_worm_registry_integration.py", # 10 tests (10s, real worm registry end-to-end, no mocks)
    "test_worm_execute_all_integration.py", # 5 tests (15s, real worms through ClusterWORMZ.execute_all, no mocks)
    "test_worm_governance_integration.py",  # 6 tests (5s, real worm-governance audit path, no mocks)
    "test_ncm_integration.py",          # 8 tests (60s, full NCM discovery workflow)
    "test_logging.py",                  # 12 tests (2s, structured JSON logging)
    "test_metrics.py",                  # 19 tests (2s, metrics, health, drift)
    "test_learning_worms.py",           # 21 tests (3s, DataPipelineWorm, FeatureEngineer)
    "test_metacluster_orchestration.py",  # 20+ tests (30s, MetaCluster orchestration)
    "test_workflow.py",                    # 30+ tests (10s, WorkflowEngine, DependencyGraph, ConditionalRouter, templates)
    "test_health_server.py",              # 16+ tests (5s, health endpoint JSON, server lifecycle)
    "test_cli_observability.py",           # 11 tests (30s, cli_observability subprocess tests)
    "test_dashboard_filters.py",          # 19 tests (2s, _parse_since, since-filtered get_report)
    "test_collectors_roundtrip.py",       # 9 tests (<1s, config/dashboard/sync-manifest round-trips)
    "test_paths_targets.py",              # 18 tests (<1s, get_*_targets canonical-name + cache semantics)
    "test_scheduling.py",                  # 20+ tests (10s, ScheduledTrainingWorm execute, scheduler, config)
    "test_web_dashboard.py",               # 20+ tests (5s, web dashboard, HTML export, notifier, CLI export)
]

# Files that need more time on 3.14t (still pass, just slow)
STANDALONE_SLOW = [
    "test_metacluster_unit.py",         # 20+ tests (~800-900s, full MetaCluster orchestration)
    "test_server_integration.py",       # 21 tests (~10s, health + Prometheus live TCP servers)
]

# Per-file timeouts (seconds) for slow orchestration tests
TIMEOUT_OVERRIDES = {
    "test_metacluster_unit.py": 1200,      # 20 min: discover_all 38s + 7 orchestration tests × ~102s each
    "test_nature_clusters_unit.py": 360,   # 6 min for nature cluster execution
    "test_config_and_breaker.py": 180,     # 3 min for config + breaker tests
    "test_clusterworms_unit.py": 120,      # 2 min for worm execution integration
    "test_worm_registry_integration.py": 120,  # 2 min: cold-cache full real discovery (~45s) or cache-backed (~3s)
    "test_worm_execute_all_integration.py": 180,  # 3 min: real discovery + sequential/parallel execute_all
    "test_worm_governance_integration.py": 120,  # 2 min: cold-cache full real discovery or cache-backed
}


def list_test_files():
    """Return all test files in the tests directory."""
    files = []
    for f in sorted(os.listdir(TESTS_DIR)):
        if f.startswith("test_") and f.endswith(".py"):
            files.append(f)
    return files


def _parse_test_output(output):
    """Parse pass/fail counts from test output."""
    passed = failed = 0
    for line in output.splitlines():
        # pytest format: "3 passed, 1 failed"
        match = re.search(r'(\d+)\s+passed.*?(\d+)\s+failed', line, re.IGNORECASE)
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2))
            break
        # unittest format: "Ran X tests in ..." then "OK" or "FAILED (failures=X)"
        match = re.search(r'Ran (\d+) tests', line)
        if match:
            total = int(match.group(1))
            fail_line = None
            for fl in output.splitlines():
                if 'FAILED' in fl:
                    fail_line = fl
                    break
            if fail_line:
                fm = re.search(r'failures=(\d+)', fail_line)
                if fm:
                    failed = int(fm.group(1))
                else:
                    failed = total
            passed = total - failed
            break
        # Custom format: "Passed: X, Failed: Y"
        match = re.search(r'Passed:\s*(\d+).*?Failed:\s*(\d+)', line)
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2))
            break
    return passed, failed


def run_test_file(filename, timeout=60):
    """Run a single test file and return results."""
    filepath = os.path.join(TESTS_DIR, filename)
    if not os.path.exists(filepath):
        return {"file": filename, "status": "NOT_FOUND", "output": ""}

    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True, text=True,
            timeout=timeout,
            cwd=PROJECT_ROOT,
        )
        elapsed = round(time.time() - start, 2)
        output = result.stdout + result.stderr
        passed, failed = _parse_test_output(output)

        if result.returncode == 0:
            status = "PASS"
        elif result.returncode in (-11, 139, -1073741819, 3221225477):
            status = "SEGFAULT"
        else:
            status = "FAIL"

        return {
            "file": filename,
            "status": status,
            "passed": passed,
            "failed": failed,
            "duration": elapsed,
            "output": output,
        }
    except subprocess.TimeoutExpired:
        return {
            "file": filename,
            "status": "TIMEOUT",
            "passed": 0,
            "failed": 0,
            "duration": timeout,
            "output": "Timed out after {}s".format(timeout),
        }


def print_summary(results):
    """Print a formatted summary of all test results."""
    total_pass = total_fail = total_tests = 0
    passed_files = segfault_files = timeout_files = fail_files = 0

    print("")
    print("=" * 60)
    print("  Azazael Test Runner -- Python {}".format(sys.version.split()[0]))
    print("=" * 60)

    for r in results:
        icon_map = {"PASS": "OK", "SEGFAULT": "!!", "TIMEOUT": "..", "FAIL": "XX", "NOT_FOUND": "?"}
        icon = icon_map.get(r["status"], "?")
        detail = " ({}/{})".format(r["passed"], r["passed"] + r["failed"]) if r["status"] == "PASS" else " " * 12
        print("  {} {:<35} {:<10}{}  {:.1f}s".format(
            icon, r["file"], r["status"], detail, r.get("duration", 0)
        ))

        if r["status"] == "PASS":
            passed_files += 1
            total_pass += r["passed"]
            total_tests += r["passed"] + r["failed"]
        elif r["status"] == "SEGFAULT":
            segfault_files += 1
        elif r["status"] == "TIMEOUT":
            timeout_files += 1
        elif r["status"] == "FAIL":
            fail_files += 1
            total_fail += r["failed"]
            total_tests += r["passed"] + r["failed"]

    print("=" * 60)
    print("  Files: {} passed, {} segfault, {} timeout, {} fail".format(
        passed_files, segfault_files, timeout_files, fail_files))
    if total_tests > 0:
        print("  Tests: {} passed, {} failed (of {})".format(total_pass, total_fail, total_tests))
    print("=" * 60)
    print("")


# Observability test group — all observability-related test files
OBSERVABILITY_GROUP = [
    "test_cli_observability.py",       # 11 tests — cli_observability subprocess tests
    "test_dashboard_filters.py",       # 19 tests — _parse_since, since-filtered get_report
    "test_health_server.py",           # 16 tests — health endpoint JSON, server lifecycle
    "test_server_integration.py",      # 21 tests — health + Prometheus live TCP endpoints
    "test_scheduling.py",              # 20 tests — ScheduledTrainingWorm
    "test_web_dashboard.py",           # 20+ tests — web dashboard, HTML export, notifier, CLI export
    "test_workflow.py",                # 48 tests — WorkflowEngine, DependencyGraph, templates
]


def main():
    parser = argparse.ArgumentParser(
        description="Azazael Test Runner -- run standalone tests on Python 3.14t",
    )
    parser.add_argument("files", nargs="*", help="Specific test files to run")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--list", action="store_true", help="List test files only")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow tests (test_metacluster_unit)")
    parser.add_argument("--timeout", type=int, default=60, help="Per-test timeout in seconds")
    parser.add_argument("--observability", action="store_true",
                        help="Run only observability-related tests (dashboard, health, scheduling, workflow)")

    args = parser.parse_args()

    if args.list:
        print("\n  Test files:")
        for f in list_test_files():
            suffix = ""
            if f in STANDALONE_OK:
                suffix = "  (standalone OK)"
            elif f in STANDALONE_SLOW:
                suffix = "  (slow, needs ~1200s timeout)"
            else:
                suffix = "  (untested)"
            print("    {}{}".format(f, suffix))
        print()
        return

    # Determine which files to run
    if args.files:
        files_to_run = []
        for f in args.files:
            if f.endswith(".py"):
                files_to_run.append(f)
            else:
                files_to_run.append(f if f.endswith(".py") else f + ".py")
    elif args.observability:
        files_to_run = list(OBSERVABILITY_GROUP)
    elif args.skip_slow:
        files_to_run = list(STANDALONE_OK)
    else:
        files_to_run = list(STANDALONE_OK) + list(STANDALONE_SLOW)

    # Run tests
    results = []
    for filename in files_to_run:
        if args.verbose:
            print("\n  Running {}...".format(filename))
        file_timeout = TIMEOUT_OVERRIDES.get(filename, args.timeout)
        result = run_test_file(filename, timeout=file_timeout)
        results.append(result)

        if args.verbose and result["output"]:
            lines = result["output"].splitlines()
            for line in lines[-10:]:
                print("    {}".format(line))

    # Print summary
    print_summary(results)

    # Return exit code
    passed = all(r["status"] == "PASS" for r in results)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
