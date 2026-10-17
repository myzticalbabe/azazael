"""Smoke tests for azazael-core CLI commands."""

import sys
import subprocess
from pathlib import Path

import pytest

# Path to the CLI module
CLI_MODULE = "azazael_core.cli"


def run_cli(command: str) -> subprocess.CompletedProcess:
    """Run a CLI command and return the result."""
    return subprocess.run(
        [sys.executable, "-m", CLI_MODULE, command],
        capture_output=True,
        text=True, encoding="utf-8", errors="replace",
        timeout=30,
    )


class TestVersion:
    """Test the version command."""

    def test_version_output(self):
        result = run_cli("version")
        assert result.returncode == 0
        assert "azazael-core v3.1.0" in result.stdout
        assert "Python" in result.stdout

    def test_version_no_stderr(self):
        result = run_cli("version")
        assert result.stderr == "" or "warning" in result.stderr.lower()


class TestPaths:
    """Test the paths command."""

    def test_paths_output(self):
        result = run_cli("paths")
        assert result.returncode == 0
        assert "Dynamic Paths" in result.stdout
        assert "Project Root" in result.stdout
        assert "Src Dir" in result.stdout

    def test_paths_has_all_sections(self):
        result = run_cli("paths")
        for section in ["Project Root", "Src Dir", "Output Dir", "Desktop Dir",
                         "G: Drive", "CORE Dir", "WORMS Dir"]:
            assert section in result.stdout, f"Missing section: {section}"


class TestRegistry:
    """Test the registry command."""

    def test_registry_output(self):
        result = run_cli("registry")
        assert result.returncode == 0
        assert "Worm Registry" in result.stdout
        assert "Total:" in result.stdout

    def test_registry_has_worms(self):
        """After bundling expansion worms, registry should show > 0 worms."""
        result = run_cli("registry")
        # Extract total worm count
        for line in result.stdout.split("\n"):
            if "Total:" in line and "worms" in line:
                # Parse e.g. "Total: 50 worms across 10 categories"
                parts = line.strip().split()
                count = int(parts[1])
                assert count > 0, f"Expected > 0 worms, got {count}"
                return
        pytest.fail("Could not find worm count in registry output")


class TestClusters:
    """Test the clusters command."""

    def test_clusters_output(self):
        result = run_cli("clusters")
        assert result.returncode == 0
        assert "Cluster System" in result.stdout

    def test_clusters_shows_import_status(self):
        result = run_cli("clusters")
        for module in ["CLUSTERWORMS", "NATURE_CLUSTERS", "METACLUSTER"]:
            assert module in result.stdout, f"Missing module: {module}"

    def test_clusters_shows_predefined(self):
        result = run_cli("clusters")
        assert "system" in result.stdout.lower() or "Predefined Clusters" in result.stdout

    def test_clusters_shows_natures(self):
        result = run_cli("clusters")
        assert "Nature Categories" in result.stdout
        assert "security" in result.stdout.lower()


class TestConfig:
    """Test the config command."""

    def test_config_output(self):
        result = run_cli("config")
        assert result.returncode == 0
        assert "Configuration" in result.stdout
        assert "AZAZAEL_ROOT" in result.stdout


class TestHelp:
    """Test the help command."""

    def test_help_no_args(self):
        result = subprocess.run(
            [sys.executable, "-m", CLI_MODULE],
            capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        assert result.returncode == 0
        assert "Usage" in result.stdout or "Commands" in result.stdout

    def test_help_flag(self):
        result = run_cli("help")
        assert result.returncode == 0
        assert "Usage" in result.stdout or "Commands" in result.stdout

    def test_help_lists_clusters(self):
        result = run_cli("help")
        assert "clusters" in result.stdout.lower()

    def test_unknown_command(self):
        result = run_cli("nonexistent")
        assert result.returncode != 0
        assert "Unknown" in result.stderr


class TestClustersImport:
    """Test that cluster modules can be imported."""

    def test_clusters_module_imports(self):
        from azazael_core.worms.clusters import (
            _CLUSTERWORMS_OK,
            _NATURE_OK,
            _META_OK,
            CLUSTER_REGISTRY,
            NATURE_DEFINITIONS,
        )
        assert _CLUSTERWORMS_OK, "CLUSTERWORMS should be importable"
        assert _NATURE_OK, "NATURE_CLUSTERS should be importable"
        assert _META_OK, "METACLUSTER should be importable"
        assert len(CLUSTER_REGISTRY) > 0, "Should have predefined clusters"
        assert len(NATURE_DEFINITIONS) > 0, "Should have Nature definitions"

    def test_clusterwormz_class(self):
        from azazael_core.worms.clusters import ClusterWORMZ
        cluster = ClusterWORMZ("system")
        status = cluster.get_status()
        assert "cluster_id" in status
        assert status["cluster_type"] == "system"
        assert status["worm_count"] > 0
        assert "version" in status

    def test_nature_cluster_manager(self):
        from azazael_core.worms.clusters import NatureClusterManager
        ncm = NatureClusterManager()
        assert hasattr(ncm, "discover_all_natures")
        status = ncm.get_status()
        assert "version" in status

    def test_meta_cluster(self):
        from azazael_core.worms.clusters import MetaCluster
        mc = MetaCluster()
        status = mc.get_status()
        assert "version" in status
        assert "routing_paths" in status

    def test_clusterwormz_mermaid(self):
        from azazael_core.worms.clusters import ClusterWORMZ
        cluster = ClusterWORMZ("system")
        mermaid = cluster.to_mermaid()
        assert "graph TB" in mermaid
        assert "CLUSTER" in mermaid

    def test_nature_cluster_manager_mermaid(self):
        from azazael_core.worms.clusters import NatureClusterManager
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        mermaid = ncm.to_mermaid()
        assert "graph TB" in mermaid
        # Should have at least the expansion-packed natures
        assert "security" in mermaid.lower()

    def test_meta_cluster_mermaid(self):
        from azazael_core.worms.clusters import MetaCluster
        mc = MetaCluster()
        mc.discover_all()
        mermaid = mc.to_mermaid()
        assert "graph TB" in mermaid

    def test_cluster_registry_types(self):
        from azazael_core.worms.clusters import CLUSTER_REGISTRY
        expected_types = ["system", "network", "security", "full", "health"]
        for ct in expected_types:
            assert ct in CLUSTER_REGISTRY, f"Missing cluster type: {ct}"
