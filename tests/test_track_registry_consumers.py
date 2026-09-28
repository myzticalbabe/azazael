"""Consumer integrity tests for the single-source training registry."""
from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import live_monitor  # noqa: E402
import run_training_orchestrator  # noqa: E402
import track_registry  # noqa: E402
# run_full_pass deleted 2026-09-28 (forensic: phantom coverage, self-
# collision, stale architecture). Its assertions below were removed with
# it; the registry remains the single rotation authority.


class TestRegistryConsumers(unittest.TestCase):
    def test_registry_is_the_rotation_authority(self):
        self.assertEqual(tuple(track_registry.ROTATION), tuple(live_monitor.TRAIN_ALGOS))
        self.assertEqual(tuple(track_registry.ROTATION), tuple(run_training_orchestrator.ROTATION))

    def test_live_monitor_event_surface_covers_every_reward_track(self):
        expected = {event[0] for event in track_registry.REWARD_EVENTS.values()}
        self.assertTrue(expected.issubset(set(live_monitor.TRAIN_EVENT_TYPES)))
        self.assertIn("sb3_training_orchestrated", live_monitor.TRAIN_EVENT_TYPES)

    def test_no_invented_rotation_track(self):
        self.assertNotIn("GRPOTUNE", live_monitor.TRAIN_ALGOS)
        self.assertNotIn("GRPOTUNE", run_training_orchestrator.ROTATION)

    def test_every_registered_track_has_a_dispatch_shape(self):
        for name, spec in track_registry.TRACKS.items():
            self.assertIn(spec["kind"], {"sb3", "cycle", "neural"}, name)
            if spec["kind"] != "sb3":
                self.assertIn(name, track_registry.RUNNERS, name)
                self.assertEqual(track_registry.RUNNERS[name], spec["runner"])


if __name__ == "__main__":
    unittest.main()
