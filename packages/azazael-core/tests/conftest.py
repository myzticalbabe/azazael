"""Shared test fixtures and configuration for azazael-core tests."""

import os
import sys
import subprocess
from pathlib import Path

import pytest


# Ensure the package is importable from the src directory
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = _PACKAGE_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


@pytest.fixture(scope="session")
def cli_module() -> str:
    """Return the CLI module name."""
    return "azazael_core.cli"


@pytest.fixture(scope="session")
def python_exe() -> str:
    """Return the Python executable path."""
    return sys.executable


@pytest.fixture
def run_cli(python_exe: str, cli_module: str):
    """Factory fixture that returns a function to run CLI commands."""

    def _run(command: str, timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
        return subprocess.run(
            [python_exe, "-m", cli_module, command],
            capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
            **kwargs,
        )

    return _run


@pytest.fixture
def worm_registry():
    """Provide access to the worm registry (already populated by package init)."""
    from azazael_core.worm_registry import WORM_REGISTRY
    return WORM_REGISTRY


@pytest.fixture
def cluster_registry():
    """Provide access to the cluster registry."""
    from azazael_core.worms.clusters import CLUSTER_REGISTRY
    return CLUSTER_REGISTRY


@pytest.fixture
def nature_definitions():
    """Provide access to Nature definitions."""
    from azazael_core.worms.clusters import NATURE_DEFINITIONS
    return NATURE_DEFINITIONS
