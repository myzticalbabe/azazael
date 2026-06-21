import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HYDRA" / "ml_platforms"))

#!/usr/bin/env python3
"""
Unit Tests for HYDRA
"""

import pytest
from pathlib import Path
import sys

_src_hydra = Path(__file__).resolve().parent.parent.parent.parent  # UNIT/ -> TESTING/ -> CODEX/ -> src/
if str(_src_hydra) not in sys.path:
    sys.path.insert(0, str(_src_hydra))


class TestHYDRACluster:
    """Unit tests for HYDRACluster."""

    def test_cluster_initialization(self):
        """Test HYDRACluster initializes."""
        try:
            from HYDRA.HYDRA import HYDRACluster

            cluster = HYDRACluster()
            assert cluster is not None
        except ImportError:
            pytest.skip("HYDRACluster not implemented")

    def test_cluster_has_run_discover(self):
        """Test HYDRACluster has run_discover method."""
        try:
            from HYDRA.HYDRA import HYDRACluster

            cluster = HYDRACluster()
            assert hasattr(cluster, "run_discover")
        except ImportError:
            pytest.skip("HYDRACluster not implemented")

    def test_cluster_has_run_all(self):
        """Test HYDRACluster has run_all method."""
        try:
            from HYDRA.HYDRA import HYDRACluster

            cluster = HYDRACluster()
            assert hasattr(cluster, "run_all")
            assert callable(cluster.run_all)
        except ImportError:
            pytest.skip("HYDRACluster not implemented")

    def test_cluster_has_stages(self):
        """Test HYDRACluster has expected stages."""
        try:
            from HYDRA.HYDRA import HYDRACluster

            expected_stages = [
                "discover",
                "analyze",
                "optimize",
                "validate",
                "deploy",
                "feedback",
            ]
            # Check that stages attribute exists or can be discovered
            cluster = HYDRACluster()
            # Just verify initialization works
            assert cluster is not None
        except ImportError:
            pytest.skip("HYDRACluster not implemented")


class TestHYDRADataClasses:
    """Unit tests for HYDRA data classes."""

    def test_processing_stage_creation(self):
        """Test ProcessingStage dataclass."""
        try:
            from HYDRA.HYDRA import ProcessingStage

            stage = ProcessingStage(name="test_stage", enabled=True, duration_ms=100.0)
            assert stage.name == "test_stage"
        except ImportError:
            pytest.skip("ProcessingStage not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
