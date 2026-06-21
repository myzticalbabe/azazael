import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))

#!/usr/bin/env python3
"""
Unit Tests for METAWORMS
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

sys.path.insert(0, "C:/Users/clint/Desktop/Azazael_UNIFIED")


class TestMetaWormResult:
    """Unit tests for MLEntry dataclass."""

    def test_worm_result_creation(self):
        """Test MLEntry can be created."""
        from CORE.WORMS.WORMZ_ML import MLEntry

        entry = MLEntry(
            term="test_term",
            category="test",
            confidence=0.95,
            occurrences=5,
            files=["file1.py", "file2.py"],
            last_found="2026-02-12",
            pattern_score=0.8,
        )
        assert entry.term == "test_term"
        assert entry.category == "test"
        assert entry.confidence == 0.95


class TestMetaWormConfig:
    """Unit tests for WORMZ_MLConfig."""

    def test_config_defaults(self):
        """Test WORMZ_MLConfig has expected defaults."""
        from CORE.WORMS.WORMZ_ML import WORMZ_MLConfig

        config = WORMZ_MLConfig()
        assert (
            "C:/Users/clint/Desktop/Azazael_UNIFIED/ORCHESTRATION"
            in config.TARGET_FOLDERS
        )
        assert "__pycache__" in config.SKIP_PATTERNS


class TestHYDRAMETA:
    """Unit tests for HYDRAMETA genetic algorithm."""

    def test_hydrometa_initialization(self):
        """Test HYDRAMETA initializes with defaults."""
        try:
            from CORE.WORMS.WORMZ_ML import HYDRAMETA

            optimizer = HYDRAMETA()
            assert optimizer.population_size == 50
            assert optimizer.generations == 100
        except ImportError:
            pytest.skip("HYDRAMETA not implemented")

    def test_hydrometa_has_optimize_method(self):
        """Test HYDRAMETA has optimize method."""
        try:
            from CORE.WORMS.WORMZ_ML import HYDRAMETA

            optimizer = HYDRAMETA()
            assert hasattr(optimizer, "optimize")
            assert callable(optimizer.optimize)
        except ImportError:
            pytest.skip("HYDRAMETA not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
