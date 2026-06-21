# Forked from src/CORE/config.py on 2026-05-29 for azazael-core standalone package.
# Sync changes from canonical source when updating.
# coding: utf-8
"""Centralized configuration for AZAZAEL production."""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Single source of truth for all AZAZAEL configuration."""
    
    # Paths
    AZAZAEL_ROOT = Path(os.environ.get("AZAZAEL_ROOT", Path.cwd()))
    SRC_DIR = AZAZAEL_ROOT / "src"
    
    # Cluster
    CLUSTER_TIMEOUT = int(os.environ.get("AZAZAEL_CLUSTER_TIMEOUT", "30"))
    CLUSTER_RETRY_COUNT = int(os.environ.get("AZAZAEL_RETRY_COUNT", "3"))
    CLUSTER_PARALLELISM = int(os.environ.get("AZAZAEL_PARALLELISM", "8"))
    
    # Circuit Breaker
    CIRCUIT_FAILURE_THRESHOLD = int(os.environ.get("AZAZAEL_CIRCUIT_THRESHOLD", "5"))
    CIRCUIT_RESET_TIMEOUT = int(os.environ.get("AZAZAEL_CIRCUIT_RESET", "60"))
    
    @classmethod
    def get_python_paths(cls) -> list:
        """Get all Python executable paths for the system."""
        paths = []
        python_base = Path.home() / "AppData" / "Local" / "Programs" / "Python"
        for version in ["313", "314", "312", "311", "310"]:
            candidate = python_base / f"Python{version}" / "python.exe"
            if candidate.exists():
                paths.append(str(candidate))
        paths.append("python")
        return paths
