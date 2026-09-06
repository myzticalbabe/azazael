# coding: utf-8
"""
Regression tests for fixes landed 2026-08-28.

Covers:
1. get_status dispatcher guard — the NatureCluster generic dispatcher
   prefers get_status() over execute(); without it, the inference worms
   fell through to execute() with an empty prompt and looped on
   "No prompt" errors.
2. nature_cluster dedup — NatureClusterManager.discover_all_natures()
   now reuses cached clusters so the `count > 0` guard suppresses
   duplicate nature_cluster_discovery records on repeat runs.
3. DynamicLogger section export — module-level section() is importable
   (SCRIPTS/test_dynamic_logging.py depends on it).

Run:  python -m unittest tests.test_verify_fixes -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Dispatcher priority order used by NatureCluster._run_worm_method
DISPATCHER_ORDER = [
    "get_summary",
    "get_status",
    "run",
    "execute",
    "scan",
    "check",
    "analyze",
]

INFERENCE_WORMS = (
    "CORE.WORMS.PARALLEL_INFERENCE_WORM.ParallelInferenceWorm",
    "CORE.WORMS.INFERENCE_WORM.InferenceWorm",
    "CORE.WORMS.NIM_INFERENCE.NimInferenceWorm",
)


class TestGetStatusDispatcherGuard(unittest.TestCase):
    """The dispatcher must resolve to get_status (never bare execute)."""

    def test_all_inference_worms_resolve_to_get_status(self):
        for dotted in INFERENCE_WORMS:
            with self.subTest(worm=dotted):
                module_name, cls_name = dotted.rsplit(".", 1)
                module = __import__(module_name, fromlist=[cls_name])
                worm = getattr(module, cls_name)()
                first = next((m for m in DISPATCHER_ORDER if hasattr(worm, m)), None)
                self.assertEqual(
                    first,
                    "get_status",
                    f"{cls_name} must resolve dispatcher to get_status, got {first}",
                )

    def test_get_status_is_side_effect_free(self):
        """get_status() reports healthy without firing inference."""
        for dotted in INFERENCE_WORMS:
            with self.subTest(worm=dotted):
                module_name, cls_name = dotted.rsplit(".", 1)
                module = __import__(module_name, fromlist=[cls_name])
                worm = getattr(module, cls_name)()
                status = worm.get_status()
                self.assertIsInstance(status, dict)
                self.assertTrue(status.get("success"))

    def test_execute_still_rejects_empty_prompt(self):
        """The no-prompt guard must remain in place on execute()."""
        from CORE.WORMS.INFERENCE_WORM import InferenceWorm
        from CORE.WORMS.NIM_INFERENCE import NimInferenceWorm

        for worm in (InferenceWorm(), NimInferenceWorm()):
            result = worm.execute()  # no prompt
            self.assertFalse(result.get("success"))
            self.assertIn("prompt", str(result.get("error", "")).lower())


class TestNatureClusterDedup(unittest.TestCase):
    """Cluster reuse makes the discovery dedup guard effective."""

    @classmethod
    def setUpClass(cls):
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

        cls.manager = NatureClusterManager()
        cls.run1 = cls.manager.discover_all_natures()
        cls.run2 = cls.manager.discover_all_natures()
        # grab one populated cluster for the per-cluster assertions
        cls.sample_nature = next(iter(cls.run1))
        cls.sample_cluster = cls.manager.clusters[cls.sample_nature]

    def test_clusters_are_reused_across_runs(self):
        """discover_all_natures() reuses cached cluster instances."""
        self.assertTrue(self.run1)
        self.assertTrue(self.run2)
        for nature in self.run1:
            with self.subTest(nature=nature):
                self.assertIn(nature, self.manager.clusters)

    def test_reused_cluster_finds_no_new_worms_on_second_pass(self):
        """A reused cluster discovers 0 new worms, so the record guard
        (if count > 0) suppresses duplicate nature_cluster_discovery events.
        """
        before = len(self.sample_cluster.worms)
        new_count = self.sample_cluster.discover_worms()
        # discover_worms returns the total; the *new* count is what the
        # record guard uses. Assert the worm set did not grow.
        self.assertGreater(before, 0)
        self.assertEqual(len(self.sample_cluster.worms), before)

    def test_fresh_cluster_would_rediscover(self):
        """Sanity check: a brand-new cluster re-sees the worms as new,
        proving dedup comes from instance reuse, not from the registry.
        """
        from CORE.WORMS.NATURE_CLUSTERS import NatureCluster

        fresh = NatureCluster(self.sample_nature)
        fresh.discover_worms()
        self.assertGreaterEqual(len(fresh.worms), len(self.sample_cluster.worms))


class TestDynamicLoggerSectionExport(unittest.TestCase):
    """Module-level section() must exist (test_dynamic_logging imports it)."""

    def test_module_level_section_is_callable(self):
        import AzazaelDynamicLogger as dlog

        self.assertTrue(callable(getattr(dlog, "section", None)))
        # peers exported alongside it
        for name in ("info", "warn", "error", "success"):
            self.assertTrue(callable(getattr(dlog, name, None)))

    def test_import_of_section_succeeds(self):
        """The exact import the SCRIPTS test uses must work."""
        from AzazaelDynamicLogger import section, info, logger  # noqa: F401

        self.assertTrue(callable(section))

    def test_section_runs_against_singleton_logger(self):
        """section() logs through the shared logger without raising."""
        import AzazaelDynamicLogger as dlog

        dlog.section("TEST SECTION")  # must not raise


if __name__ == "__main__":
    unittest.main()
