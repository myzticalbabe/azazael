import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "HYDRA" / "ml_platforms"))

#!/usr/bin/env python3
"""
PERSEPHONE CLI - Command Line Interface

Cross-platform development utilities.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.path_manager import PathManager
from lib.sync_manager import SyncManager
from lib.environment import EnvironmentManager


def print_help():
    """Print help message."""
    print("""
PERSEPHONE CLI v1.0.0

Commands:
    paths          - List all registered paths
    sync           - Sync Azazael to PERSEPHONE
    env            - Show environment configuration
    detect         - Detect paths and their status
    setup          - Generate environment setup scripts
    help           - Show this help message

Usage:
    persephone <command>

Examples:
    persephone paths
    persephone sync --dry-run
    persephone setup bash
""")


def cmd_paths():
    """List all registered paths."""
    pm = PathManager()
    for info in pm.list_all():
        status = "[OK]" if info.exists else "[MISSING]"
        print(f"  {info.name:15} {status} {info.windows}")


def cmd_sync(dry_run: bool = True):
    """Sync Azazael to PERSEPHONE."""
    sm = SyncManager()
    result = sm.sync_azazael_to_persephone(dry_run)
    print(f"Source: {result.source}")
    print(f"Target: {result.target}")
    print(f"Status: {'Would sync' if result.success else 'Failed'}")
    if result.errors:
        for error in result.errors:
            print(f"Error: {error}")


def cmd_env():
    """Show environment configuration."""
    em = EnvironmentManager()
    print("Environment Variables:")
    for name, var in em.variables.items():
        print(f"  {name}={var.value}")


def cmd_detect():
    """Detect paths and their status."""
    pm = PathManager()
    results = pm.sync_paths()
    print("Path Detection:")
    for name, exists in results.items():
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {name:15} {status}")


def cmd_setup(shell: str = "bash"):
    """Generate environment setup script."""
    em = EnvironmentManager()
    if shell == "bash":
        print(em.get_bashrc_snippet())
    elif shell == "powershell":
        print(em.get_powershell_snippet())
    else:
        print(f"Unknown shell: {shell}")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] == "help":
        print_help()
        return

    command = args[0].lower()

    if command == "paths":
        cmd_paths()
    elif command == "sync":
        dry_run = "--dry-run" in args or "-n" in args
        cmd_sync(dry_run)
    elif command == "env":
        cmd_env()
    elif command == "detect":
        cmd_detect()
    elif command == "setup":
        shell = args[1] if len(args) > 1 else "bash"
        cmd_setup(shell)
    else:
        print(f"Unknown command: {command}")
        print("Use 'persephone help' for available commands")


if __name__ == "__main__":
    main()
