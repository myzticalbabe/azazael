#!/usr/bin/env python3
"""
KLINK - Azazael Ecosystem Unified Command Launcher

Cross-platform CLI for all Azazael ecosystem commands.
Supports: Windows (CMD/PowerShell), Linux, Debian, macOS, WSL

Usage:
    python klink.py --help
    python klink.py status
    python klink.py worms
    python klink.py hydra all
    python klink.py optimize

Installation:
    chmod +x klink.py
    sudo cp klink.py /usr/local/bin/klink
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Configuration
DEFAULT_Azazael_ROOT = "C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION"
LINUX_Azazael_ROOT = os.path.expanduser("~/Desktop/Azazael")

# Detect platform and set root
if sys.platform == "win32":
    Azazael_ROOT = os.environ.get("Azazael_ROOT", DEFAULT_Azazael_ROOT)
else:
    Azazael_ROOT = os.environ.get("Azazael_ROOT", LINUX_Azazael_ROOT)

# Command mappings
COMMANDS = {
    # Core
    "status": {"func": "cmd_status", "help": "Show ecosystem status"},
    "version": {"func": "cmd_version", "help": "Show version info"},
    "list": {"func": "cmd_list", "help": "List all commands"},
    # WORMZ
    "worms": {"func": "cmd_worms", "help": "Run all WORMZ worms"},
    "systemz": {"func": "cmd_systemz", "help": "System information worm"},
    "processz": {"func": "cmd_processz", "help": "Process management worm"},
    "diskz": {"func": "cmd_diskz", "help": "Disk analysis worm"},
    "networkz": {"func": "cmd_networkz", "help": "Network analysis worm"},
    "clockz": {"func": "cmd_clockz", "help": "Time synchronization worm"},
    # METAWORMS
    "metaworms": {"func": "cmd_metaworms", "help": "Run all METAWORMS"},
    "errorz": {"func": "cmd_errorz", "help": "Error tracking metaworm"},
    "trimz": {"func": "cmd_trimz", "help": "Optimization metaworm"},
    "healthz": {"func": "cmd_healthz", "help": "Health monitoring metaworm"},
    "hydrometa": {"func": "cmd_hydrometa", "help": "HYDRA metaworm"},
    # HYDRA
    "hydra": {"func": "cmd_hydra", "help": "Run HYDRA cluster", "has_args": True},
    # Ecosystem
    "terence": {"func": "cmd_terence", "help": "TERENCE error resolver"},
    "horus": {"func": "cmd_horus", "help": "HORUS output formatter"},
    "tarbaby": {"func": "cmd_tarbaby", "help": "Binary builder"},
    "poindexter": {"func": "cmd_poindexter", "help": "Mathematical indexer"},
    "persephone": {"func": "cmd_persephone", "help": "Cross-platform utilities"},
    # Optimization
    "optimize": {"func": "cmd_optimize", "help": "Run ecosystem optimizer"},
    "monitor": {"func": "cmd_monitor", "help": "Launch live monitoring popup"},
    "analyze": {"func": "cmd_analyze", "help": "Analyze batch files"},
    # Full runs
    "all": {"func": "cmd_all", "help": "Run full ecosystem"},
    "full": {"func": "cmd_all", "help": "Run full ecosystem"},
}


def log(msg, level="INFO"):
    """Print colored log message."""
    colors = {
        "INFO": "\033[94m",  # Blue
        "OK": "\033[92m",  # Green
        "WARN": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "NC": "\033[0m",  # No Color
    }
    if sys.platform == "win32":
        colors = {k: "" for k in colors}

    print(f"{colors.get(level, colors['INFO'])}[{level}] {msg}{colors['NC']}")


def run_python(script_path, args=None):
    """Run a Python script."""
    full_path = Path(Azazael_ROOT) / script_path
    if not full_path.exists():
        return False, f"Script not found: {full_path}"

    cmd = [sys.executable, str(full_path)] + (args or [])
    result = os.system(" ".join(f'"{c}"' for c in cmd))
    return result == 0, "Success" if result == 0 else "Failed"


def cmd_status():
    """Show ecosystem status."""
    print("\n" + "=" * 60)
    print("  Azazael ECOSYSTEM STATUS")
    print("=" * 60)
    print(f"\nPlatform: {sys.platform}")
    print(f"Azazael_ROOT: {Azazael_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Commands available: {len(COMMANDS)}")
    print("\nComponents:")
    for folder in [
        "WORMZ",
        "METAWORMS",
        "HYDRA",
        "TERENCE",
        "HORUS",
        "TARBABY",
        "POINDEXTER",
        "PERSEPHONE",
    ]:
        path = Path(Azazael_ROOT) / folder
        exists = "âœ“" if path.exists() else "âœ—"
        print(f"  [{exists}] {folder}")
    print("=" * 60)


def cmd_version():
    """Show version."""
    print("Azazael Ecosystem v5.0.0")
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version.split()[0]}")


def cmd_list():
    """List all commands."""
    print("\nAvailable Commands:")
    print("-" * 40)
    for cmd, info in COMMANDS.items():
        print(f"  {cmd:<15} - {info['help']}")
    print("-" * 40)


# WORMZ Commands
def cmd_worms():
    run_python("WORMZ/CONCURRENCY.py", ["--scan"])


def cmd_systemz():
    run_python("WORMZ/SYSTEMZ.py", ["--status"])


def cmd_processz():
    run_python("WORMZ/PROCESSZ.py", ["--status"])


def cmd_diskz():
    run_python("WORMZ/DISKZ.py", ["--status"])


def cmd_networkz():
    run_python("WORMZ/NETWORXZ.py", ["--status"])


def cmd_clockz():
    run_python("WORMZ/CLOCKZ.py", ["--status"])


# METAWORMS Commands
def cmd_metaworms():
    run_python("METAWORMS/HYDRAMETA.py", ["--all"])


def cmd_errorz():
    run_python("METAWORMS/ERRORZ.py", ["--all"])


def cmd_trimz():
    run_python("METAWORMS/TRIMZ.py", ["--all"])


def cmd_healthz():
    run_python("METAWORMS/HEALTHZ.py", ["--all"])


def cmd_hydrometa():
    run_python("METAWORMS/HYDRAMETA.py", ["--all"])


# HYDRA Command
def cmd_hydra(args):
    if not args or args[0] in ["all", None]:
        run_python("HYDRA/HYDRA.py", ["--all"])
    else:
        stage = args[0]
        valid_stages = [
            "discovery",
            "analysis",
            "optimization",
            "validation",
            "deployment",
            "feedback",
        ]
        if stage in valid_stages:
            run_python("HYDRA/HYDRA.py", ["--stage", stage])
        else:
            log(f"Invalid stage: {stage}", "ERROR")
            print(f"Valid stages: {', '.join(valid_stages)}")


# Ecosystem Commands
def cmd_terence():
    run_python("TERENCE/TERENCE.py", ["--scan"])


def cmd_horus():
    run_python("HORUS/HORUS.py")


def cmd_tarbaby():
    run_python("TARBABY/TARBABY.py", ["--test"])


def cmd_poindexter():
    run_python("POINDEXTER/POINDEXTER.py")


def cmd_persephone():
    run_python("PERSEPHONE/persephone.py")


# Optimization Commands
def cmd_optimize():
    run_python("ECOSYSTEM_OPTIMIZER.py", ["-o"])


def cmd_monitor():
    """Launch live monitoring popup."""
    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(full_path)] + (args or []),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            log("Live monitor launched", "OK")
        else:
            log(f"Monitor launch issue: {result.stderr[:100]}", "WARN")
    except Exception as e:
        log(f"Could not launch monitor: {e}", "ERROR")


def cmd_analyze():
    run_python("BAT_OPTIMIZATION_ANALYSIS.py")


# Full Ecosystem
def cmd_all():
    run_python("Azazael_INTEGRATION.py")


def main():
    parser = argparse.ArgumentParser(
        description="KLINK - Azazael Ecosystem Unified Command Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  klink.py status              Show ecosystem status
  klink.py worms               Run all WORMZ worms
  klink.py hydra all           Run full HYDRA cycle
  klink.py hydra discovery     Run HYDRA discovery stage
  klink.py optimize            Run ecosystem optimizer
  klink.py all                 Run full ecosystem

Platforms: Windows, Linux, Debian, macOS, WSL
        """,
    )
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for command")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--version", action="store_true", help="Show version")

    args = parser.parse_args()

    if args.version:
        cmd_version()
        return

    if not args.command or args.command in ["help", "--help", "-h"]:
        cmd_list()
        print("\nUse 'klink.py --help' for full usage")
        return

    cmd_name = args.command.lower()

    if cmd_name not in COMMANDS:
        log(f"Unknown command: {cmd_name}", "ERROR")
        print(f"\nAvailable commands: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    cmd_info = COMMANDS[cmd_name]
    func_name = cmd_info["func"]

    if args.json:
        result = {
            "command": cmd_name,
            "timestamp": datetime.now().isoformat(),
            "status": "running",
        }
        print(json.dumps(result, indent=2))

    # Call the appropriate function
    func = globals().get(func_name)
    if func:
        if cmd_info.get("has_args"):
            func(args.args)
        else:
            func()
    else:
        log(f"Function not found: {func_name}", "ERROR")


if __name__ == "__main__":
    main()
