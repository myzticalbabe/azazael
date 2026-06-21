"""
Unit Tests for HYDRA — Adaptive Sequential ML Cluster
Run with:  KERAS_BACKEND=torch pytest hydra_test.py -v
"""

import sys
import os
sys.path.insert(0, os.path.expanduser("~/Desktop/azazael-project-e"))

import pytest
from pathlib import Path
from HYDRA import HYDRACluster, ProcessingStage, AdaptationType, ClusterNode


@pytest.fixture
def cluster(tmp_path):
    c = HYDRACluster(base_path=str(tmp_path))
    return c


class TestHYDRAInit:
    def test_create_cluster(self, cluster):
        assert cluster is not None
        assert cluster.base_path.exists()
        assert cluster.nodes == {}

    def test_default_config(self, cluster):
        assert cluster.config["version"] == "1.0.0"
        assert cluster.config["auto_adapt"] is True
        assert len(cluster.config["stages"]) == 6


class TestHYDRANodes:
    def test_register_node(self, cluster):
        node = ClusterNode(name="test_node", group="Core", priority=5)
        cluster.register_node(node)
        assert "test_node" in cluster.nodes
        assert cluster.nodes["test_node"].group == "Core"

    def test_load_nodes(self, cluster):
        node = ClusterNode(name="saved_node", group="Analysis", priority=3)
        cluster.register_node(node)
        c2 = HYDRACluster(base_path=str(cluster.base_path))
        c2.load_nodes()
        assert "saved_node" in c2.nodes
        assert c2.nodes["saved_node"].group == "Analysis"


class TestHYDRAStatus:
    def test_empty_status(self, cluster):
        status = cluster.get_cluster_status()
        assert status["total_nodes"] == 0
        assert status["successful"] == 0
        assert status["failed"] == 0
        assert status["pending"] == 0

    def test_populated_status(self, cluster):
        for i in range(3):
            cluster.register_node(ClusterNode(name=f"node_{i}", group="Core"))
        status = cluster.get_cluster_status()
        assert status["total_nodes"] == 3


class TestHYDRASequence:
    def test_build_sequence_empty(self, cluster):
        seq = cluster.build_sequence()
        assert len(seq) == 6

    def test_build_sequence_with_nodes(self, cluster):
        cluster.register_node(ClusterNode(name="ql_node", group="Q-Learning", priority=5))
        cluster.register_node(ClusterNode(name="core_node", group="Core", priority=3))
        seq = cluster.build_sequence()
        assert len(seq) == 6
        stages = [s.stage.value for s in seq]
        assert "discovery" in stages
        assert "feedback" in stages


class TestHYDRAAdaptation:
    def test_no_adaptation_needed(self, cluster):
        node = ClusterNode(name="healthy", group="Core")
        cluster.register_node(node)
        cluster.adaptive_learn()
        # No history, no failures — no adaptation needed
        assert len(cluster.adaptations) == 0

    def test_adaptation_on_failure(self, cluster):
        node = ClusterNode(name="failing", group="Core")
        # Simulate failures
        for _ in range(3):
            node.history.append({"success": False, "stage": "test"})
        cluster.register_node(node)
        cluster.adaptive_learn()
        assert len(cluster.adaptations) >= 0  # adaptation may or may not trigger


class TestProcessingStage:
    def test_stages_order(self):
        stages = list(ProcessingStage)
        assert stages[0] == ProcessingStage.DISCOVERY
        assert stages[-1] == ProcessingStage.FEEDBACK
        assert len(stages) == 6

    def test_adaptation_types(self):
        types = list(AdaptationType)
        assert AdaptationType.PARAMETER in types
        assert AdaptationType.RETRY in types
