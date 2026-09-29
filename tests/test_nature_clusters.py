"""Tests for CORE/WORMS/NATURE_CLUSTERS.py."""
import sys, os, unittest, threading
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from CORE.WORMS.NATURE_CLUSTERS import (
    NatureCluster, NatureClusterManager, NatureResult,
    NATURE_DEFINITIONS, CrossNatureRoute,
)


class TestNatureDefinitions(unittest.TestCase):
    def test_all_natures_have_required_fields(self):
        for nature, defn in NATURE_DEFINITIONS.items():
            self.assertIn("purpose", defn, f"{nature} missing purpose")
            self.assertIn("triggers", defn, f"{nature} missing triggers")
            self.assertIn("feeds_into", defn, f"{nature} missing feeds_into")
            self.assertIsInstance(defn["feeds_into"], list, f"{nature} feeds_into not a list")

    def test_known_natures(self):
        for name in ["monitor", "security", "defense", "orchestration", "telemetry", "analysis"]:
            self.assertIn(name, NATURE_DEFINITIONS)

    def test_at_least_15_natures(self):
        # Floor tracks live NATURE_DEFINITIONS (26, 2026-09-29) with headroom.
        self.assertGreaterEqual(len(NATURE_DEFINITIONS), 20)


class TestNatureResult(unittest.TestCase):
    def test_defaults(self):
        r = NatureResult(nature="test")
        self.assertEqual(r.nature, "test")
        self.assertEqual(r.success_count, 0)
        self.assertEqual(r.failure_count, 0)
        self.assertEqual(r.duration_ms, 0.0)
        self.assertEqual(r.worm_results, {})
        self.assertEqual(r.errors, [])


class TestCrossNatureRoute(unittest.TestCase):
    def test_creation(self):
        route = CrossNatureRoute(from_nature="monitor", to_nature="defense")
        self.assertEqual(route.from_nature, "monitor")
        self.assertEqual(route.to_nature, "defense")
        self.assertEqual(route.data_mapping, {})

    def test_with_data_mapping(self):
        route = CrossNatureRoute(
            from_nature="security", to_nature="repair",
            data_mapping={"vulns": "fix_targets"},
            description="Security feeds repair",
        )
        self.assertEqual(route.data_mapping["vulns"], "fix_targets")


class TestNatureCluster(unittest.TestCase):
    def test_init(self):
        cluster = NatureCluster("security")
        self.assertEqual(cluster.nature, "security")
        self.assertIn("nature_security_", cluster.cluster_id)
        self.assertIsInstance(cluster.worms, dict)
        self.assertEqual(cluster._parallel, False)
        self.assertEqual(cluster._timeout, 60)

    def test_definition_loaded(self):
        cluster = NatureCluster("security")
        self.assertIn("purpose", cluster.definition)
        self.assertIn("Vulnerability", cluster.definition["purpose"])

    def test_unknown_nature(self):
        cluster = NatureCluster("nonexistent_xyz")
        self.assertEqual(cluster.definition, {})

    def test_add_worm_manual(self):
        cluster = NatureCluster("test")
        cluster.add_worm_manual("TestWorm", type("TestWorm", (), {}))
        self.assertIn("TestWorm", cluster.worms)

    def test_set_parallel(self):
        cluster = NatureCluster("security")
        cluster.set_parallel(True)
        self.assertTrue(cluster._parallel)

    def test_set_timeout(self):
        cluster = NatureCluster("security")
        cluster.set_timeout(120)
        self.assertEqual(cluster._timeout, 120)

    def test_discover_worms(self):
        cluster = NatureCluster("orchestration")
        count = cluster.discover_worms()
        self.assertGreater(count, 0)
        self.assertGreater(len(cluster.worms), 0)

    def test_get_status(self):
        cluster = NatureCluster("orchestration")
        cluster.discover_worms()
        status = cluster.get_status()
        self.assertIn("nature", status)
        self.assertIn("worm_count", status)
        self.assertIn("version", status)
        self.assertIn("free_threaded", status)
        self.assertEqual(status["nature"], "orchestration")

    def test_get_worm_info(self):
        cluster = NatureCluster("orchestration")
        cluster.discover_worms()
        info = cluster.get_worm_info()
        self.assertGreater(len(info), 0)
        for item in info:
            self.assertIn("name", item)
            self.assertIn("priority", item)

    def test_to_mermaid(self):
        cluster = NatureCluster("security")
        cluster.discover_worms()
        mermaid = cluster.to_mermaid()
        self.assertIn("subgraph security", mermaid)

    def test_repr(self):
        cluster = NatureCluster("security")
        r = repr(cluster)
        self.assertIn("NatureCluster", r)
        self.assertIn("security", r)

    def test_version(self):
        self.assertEqual(NatureCluster.VERSION, "1.0.0")


class TestNatureClusterManager(unittest.TestCase):
    def test_init(self):
        ncm = NatureClusterManager()
        self.assertEqual(ncm.clusters, {})
        self.assertEqual(len(ncm._execution_history), 0)

    def test_discover_all_natures(self):
        ncm = NatureClusterManager()
        counts = ncm.discover_all_natures()
        self.assertGreater(len(counts), 0)
        self.assertGreater(sum(counts.values()), 0)
        self.assertGreater(len(ncm.clusters), 0)

    def test_get_cluster(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        cluster = ncm.get_cluster("security")
        if cluster is not None:
            self.assertEqual(cluster.nature, "security")

    def test_get_cluster_creates_new(self):
        ncm = NatureClusterManager()
        cluster = ncm.get_cluster("orchestration")
        self.assertIsNotNone(cluster)
        self.assertEqual(cluster.nature, "orchestration")

    def test_execute_nature(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        result = ncm.execute_nature("orchestration")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, NatureResult)
        self.assertEqual(result.nature, "orchestration")

    def test_execute_nonexistent_nature(self):
        ncm = NatureClusterManager()
        result = ncm.execute_nature("nonexistent_xyz")
        self.assertIsNone(result)

    def test_get_status(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        status = ncm.get_status()
        self.assertIn("natures", status)
        self.assertIn("total_worms", status)
        self.assertIn("free_threaded", status)
        self.assertGreater(status["natures"], 0)

    def test_list_all_worms(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        worms = ncm.list_all_worms()
        self.assertGreater(len(worms), 0)
        for nature, worm_list in worms.items():
            self.assertIsInstance(worm_list, list)

    def test_get_cross_nature_routes(self):
        ncm = NatureClusterManager()
        routes = ncm.get_cross_nature_routes()
        self.assertGreater(len(routes), 0)
        for route in routes:
            self.assertIsInstance(route, CrossNatureRoute)
            self.assertIn(route.from_nature, NATURE_DEFINITIONS)
            self.assertIn(route.to_nature, NATURE_DEFINITIONS)

    def test_to_mermaid(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        mermaid = ncm.to_mermaid()
        self.assertIn("graph TB", mermaid)

    def test_repr(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        r = repr(ncm)
        self.assertIn("NatureClusterManager", r)

    def test_version(self):
        self.assertEqual(NatureClusterManager.VERSION, "1.0.0")

    def test_score_natures(self):
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        scores = ncm._score_natures()
        self.assertGreater(len(scores), 0)
        for nature, score in scores.items():
            self.assertIsInstance(score, float)


if __name__ == "__main__":
    unittest.main()
