#!/usr/bin/env python3
# coding: utf-8
"""The proprioception gate must be LOUD when it refuses, at the source.

Why this file exists. `scripts/spine_cycle_apply.py` already maps a refusal to a
non-zero exit (tests/test_spine_cycle_visibility.py pins that). But it is only
one caller. `night_shift.py`, `train_today.py` and any future caller read the
report dict and would each have to remember to special-case `skipped` -- and two
of them did not, so a refused write read there as "proposals=0": success-shaped.

The fix is at the gate. `SpineCycleWorm.run_cycle` now emits a WARNING through
`logging` on the refusal path, so every caller surfaces it whether or not it
inspects the returned dict. These tests pin that the warning is emitted, names
the skip and the reason, and does NOT fire on the observation-only path (the
gate is only supposed to hold back WRITES).
"""
from __future__ import annotations

import logging
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, os.path.join(_ROOT, "src"), os.path.join(_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from CORE.WORMS.expansion.spine import SpineCycleWorm  # noqa: E402

_LOGGER = logging.getLogger("CORE.WORMS.expansion.spine")
_REASON = "stale artifacts: graphify-out/graph.json"


class TestGateRefusalIsLoud(unittest.TestCase):

    def _worm_refusing(self) -> SpineCycleWorm:
        w = SpineCycleWorm(min_interval_seconds=0)
        # Shadow the probe so the refusal is deterministic and offline: the test
        # is about the warning, not about reproducing a stale tree.
        w._self_image_stale = lambda: _REASON  # type: ignore[method-assign]
        return w

    def test_refusal_emits_a_warning_naming_skip_and_reason(self):
        w = self._worm_refusing()
        with self.assertLogs(_LOGGER, level="WARNING") as cm:
            rep = w.run_cycle(apply=True)
        self.assertEqual(rep.get("skipped"), "stale_self_image")
        self.assertFalse(rep.get("success"), "a refusal is not a success")
        blob = "\n".join(cm.output)
        self.assertIn("REFUSED", blob)
        self.assertIn("stale_self_image", blob)
        self.assertIn("graphify-out/graph.json", blob,
                      "the reason must reach the log, not be dropped")

    def test_observation_only_cycle_does_not_refuse(self):
        """Looking cannot harm: the gate must not hold back an apply=False cycle."""
        w = SpineCycleWorm(min_interval_seconds=0)
        w._self_image_stale = lambda: _REASON  # type: ignore[method-assign]
        logger = logging.getLogger("CORE.WORMS.expansion.spine")
        records: list[str] = []
        handler = logging.Handler()
        handler.emit = lambda r: records.append(r.getMessage())  # type: ignore[method-assign]
        logger.addHandler(handler)
        try:
            rep = w.run_cycle(apply=False)
        finally:
            logger.removeHandler(handler)
        self.assertIsNone(rep.get("skipped"),
                          "an observation-only cycle must not be refused")
        self.assertFalse(any("REFUSED" in m for m in records),
                         "no refusal warning on the observation path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
