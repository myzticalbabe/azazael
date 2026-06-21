#!/usr/bin/env python3
"""Azazael Unified CLI — One tool to run all azazael commands.

Usage:
    python3 unified_cli.py hydra --status
    python3 unified_cli.py health
    python3 unified_cli.py import-test
    python3 unified_cli.py benchmark
    python3 unified_cli.py scan
    python3 unified_cli.py backup
"""

import sys
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path.home() / "Desktop"
PROJECT_DIR = SCRIPTS_DIR / "azazael-project-e"

COMMANDS = {
    "hydra": f"cd {PROJECT_DIR} && python3 HYDRA.py",
    "health": f"KERAS_BACKEND=torch python3 {SCRIPTS_DIR}/health_check_azazael.py",
    "import-test": f"KERAS_BACKEND=torch python3 {SCRIPTS_DIR}/test_azazael_imports.py",
    "benchmark": f"KERAS_BACKEND=torch python3 {SCRIPTS_DIR}/benchmark_frameworks.py",
    "ner": f"python3 {SCRIPTS_DIR}/visualize_ner.py",
    "scan": f"python3 {SCRIPTS_DIR}/compare_scans.py",
    "memory": f"KERAS_BACKEND=torch python3 {SCRIPTS_DIR}/memory_profile.py",
    "backup": f"python3 {SCRIPTS_DIR}/backup_to_g.py",
    "api": f"cd {SCRIPTS_DIR} && python3 -m uvicorn hydra_api:app --reload --port 8000",
    "dashboard": f"cd {SCRIPTS_DIR} && python3 flask_dashboard.py",
    "test": f"cd {SCRIPTS_DIR} && KERAS_BACKEND=torch python3 -m pytest hydra_test.py hydra_integration_test.py -v",
    "graph": f"cd {PROJECT_DIR} && python3 {SCRIPTS_DIR}/hydra_graph.py",
    "qlearn": f"KERAS_BACKEND=torch python3 {SCRIPTS_DIR}/qlearning_env.py --episodes 100",
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Azazael Unified CLI")
        print()
        print("Usage:  python3 unified_cli.py <command> [args...]")
        print()
        print("Commands:")
        for cmd, run in sorted(COMMANDS.items()):
            print(f"  {cmd:<15s}  {run[:60]}...")
        print()
        print("Examples:")
        print("  python3 unified_cli.py hydra --status")
        print("  python3 unified_cli.py health")
        print("  python3 unified_cli.py import-test")
        return

    cmd = sys.argv[1]
    extra_args = " ".join(sys.argv[2:])

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(sorted(COMMANDS.keys()))}")
        sys.exit(1)

    full_cmd = f"{COMMANDS[cmd]} {extra_args}"
    print(f"▶ {full_cmd}\n")
    subprocess.run(full_cmd, shell=True)


if __name__ == "__main__":
    main()
