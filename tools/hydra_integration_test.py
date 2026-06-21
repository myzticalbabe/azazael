"""Integration Tests — Full HYDRA discover → run → adapt → status chain.

Run:  KERAS_BACKEND=torch pytest hydra_integration_test.py -v
"""

import sys
import os
sys.path.insert(0, os.path.expanduser("~/Desktop/azazael-project-e"))

import pytest
from HYDRA import HYDRACluster


@pytest.fixture
def cluster(tmp_path):
    return HYDRACluster(base_path=str(tmp_path / "hydra_test"))


class TestFullChain:
    def test_discover_empty_no_crash(self, cluster):
        """Discover with no ml_platforms available should handle gracefully."""
        # Should not crash even without real ml_platforms
        groups = cluster.auto_discover_ml_groups()
        assert isinstance(groups, dict)

    def test_run_empty_sequence(self, cluster):
        """Run pipeline with no nodes should complete all 6 stages."""
        cluster.build_sequence()
        results = cluster.run_sequential()
        assert len(results["stages"]) == 6
        assert results["start_time"] is not None
        assert results["end_time"] is not None

    def test_register_and_run(self, cluster):
        """Register a node, run pipeline, verify it gets processed."""
        from HYDRA import ClusterNode
        cluster.register_node(ClusterNode(name="test_core", group="Core", priority=5))
        cluster.build_sequence()
        results = cluster.run_sequential()
        assert len(results["stages"]) > 0

    def test_status_reflects_nodes(self, cluster):
        """Status should show registered nodes."""
        from HYDRA import ClusterNode
        for i in range(3):
            cluster.register_node(ClusterNode(name=f"n{i}", group="Core"))
        s = cluster.get_cluster_status()
        assert s["total_nodes"] == 3

    def test_adapt_no_failures(self, cluster):
        """Adapt with no failures should produce 0 adaptations."""
        from HYDRA import ClusterNode
        cluster.register_node(ClusterNode(name="healthy", group="Core"))
        count = len(cluster.adaptive_learn())
        assert count == 0  # No failures → no adaptations needed

    def test_save_and_load(self, cluster):
        """Nodes should persist across cluster instances."""
        from HYDRA import ClusterNode
        cluster.register_node(ClusterNode(name="persistent", group="Analysis"))
        c2 = HYDRACluster(base_path=str(cluster.base_path))
        c2.load_nodes()
        assert "persistent" in c2.nodes

    def test_full_chain_no_crash(self, cluster):
        """Full discover → register → run → adapt → status chain."""
        cluster.auto_discover_ml_groups()
        cluster.build_sequence()
        cluster.run_sequential()
        cluster.adaptive_learn()
        s = cluster.get_cluster_status()
        assert "total_nodes" in s
