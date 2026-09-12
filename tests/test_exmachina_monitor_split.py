# coding: utf-8
"""The Ex Machina panel must live in its OWN monitor, not in the Azazael one.

History
-------
The panel was first written by injecting ~700 lines into
`scripts/live_monitor.py`. That was wrong: the Azazael wallboard is a shared
surface, and the epistemic tier is a separate concern with its own viewer
(`scripts/exmachina_live_monitor.py`). The split is easy to undo by accident
(e.g. a later "just add one row" edit), so it is locked here:

* the Azazael monitor must carry no Ex Machina code and must not render the
  panel;
* the standalone monitor must expose the panel and render it within the
  never-wrap width contract.
"""
import os
import re
import sys
import unittest
from datetime import datetime

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_project_root, os.path.join(_project_root, "scripts"),
           os.path.join(_project_root, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import live_monitor as az            # noqa: E402
import exmachina_live_monitor as ex  # noqa: E402
import exmachina_health_alert as alert  # noqa: E402

_SCRIPTS = os.path.join(_project_root, "scripts")
_ANSI = re.compile("\x1b\\[[0-9;]*m")

# Symbols only the Ex Machina panel defines. Their presence in the Azazael
# monitor is the exact shape of the re-injection this test exists to catch.
_PANEL_SYMBOLS = ("exmachina_snapshot", "exmachina_lines", "EX_ORGANS",
                  "_EX_ARTIFACTS", "_EX_STATE", "_GLYPH_TIERS", "set_glyphs",
                  "detect_glyph_tier")
_PANEL_TITLE = "-- EX MACHINA --"


def _src(name):
    with open(os.path.join(_SCRIPTS, name), encoding="utf-8") as f:
        return f.read()


class TestPanelHasItsOwnMonitor(unittest.TestCase):

    def test_azazael_monitor_source_carries_no_panel_code(self):
        src = _src("live_monitor.py")
        for sym in _PANEL_SYMBOLS:
            self.assertNotIn(sym, src,
                             "%s leaked back into scripts/live_monitor.py" % sym)
        self.assertNotIn("EX MACHINA", src.upper(),
                         "the Ex Machina panel was injected into live_monitor.py")

    def test_azazael_module_exposes_no_panel_surface(self):
        for sym in _PANEL_SYMBOLS:
            self.assertFalse(hasattr(az, sym),
                             "live_monitor.%s exists — panel is not split off" % sym)

    def test_standalone_module_exposes_the_panel(self):
        for sym in ("exmachina_snapshot", "exmachina_lines", "set_glyphs"):
            self.assertTrue(hasattr(ex, sym),
                            "exmachina_live_monitor lost %s" % sym)

    def test_standalone_monitor_renders_the_panel_within_width(self):
        cols = 100
        frame = ex.render(size=(cols, 40))
        self.assertIn(_PANEL_TITLE, frame.upper(),
                      "standalone monitor did not render the panel")
        for line in frame.split("\n"):
            # strictly narrower than the window: a line that fills the last
            # cell exactly can wrap and scroll the whole frame, which breaks
            # the in-place refresh
            self.assertLess(
                ex._vis_len(line), cols,
                "line fills or exceeds the window: %r" % _ANSI.sub("", line)[:70])

    def test_standalone_frame_fits_the_launcher_window(self):
        cols, rows = 118, 40          # open_exmachina_live_monitor.bat window
        lines = ex.render(size=(cols, rows)).split("\n")
        self.assertLessEqual(len(lines), rows - 1,
                             "frame needs %d rows of %d" % (len(lines), rows))
        for line in lines:
            self.assertLess(ex._vis_len(line), cols,
                            "line fills the window: %r" % _ANSI.sub("", line)[:70])

    def test_health_check_reports_the_tier(self):
        ok, msg = ex.health_check()
        self.assertIsInstance(ok, bool)
        self.assertTrue(msg, "health_check returned no message")
        # the tier is stdlib-only and committed, so it must load
        self.assertTrue(ok, msg)

    def test_azazael_monitor_does_not_render_the_panel(self):
        con = az.db_connect()
        if con is None:
            self.skipTest("memory store unavailable")
        try:
            data = az.collect(con)
            frame = az.render(data, datetime.now())
        except Exception as exc:                       # noqa: BLE001
            self.skipTest("azazael render unavailable: %s" % exc)
        finally:
            con.close()
        self.assertNotIn("EX MACHINA", frame.upper(),
                         "the Azazael wallboard is rendering the Ex Machina panel")


class TestScheduledHealthAlert(unittest.TestCase):

    def test_degradation_alerts_once_on_the_transition(self):
        import json
        import tempfile
        original = alert.mon.health_check
        alert.mon.health_check = lambda: (False, "tier unavailable")
        try:
            with tempfile.TemporaryDirectory() as d:
                sj = os.path.join(d, "health.json")
                lg = os.path.join(d, "alerts.log")
                alert.run(quiet=True, state_json=sj, alert_log=lg)
                alert.run(quiet=True, state_json=sj, alert_log=lg)  # still down
                with open(sj, encoding="utf-8") as f:
                    self.assertFalse(json.load(f)["ok"])
                with open(lg, encoding="utf-8") as f:
                    lines = [ln for ln in f.read().splitlines() if ln.strip()]
        finally:
            alert.mon.health_check = original
        self.assertEqual(len(lines), 1,
                         "a persistent fault must alert once, not every run")

    def test_healthy_run_writes_state_and_no_alert(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            sj = os.path.join(d, "health.json")
            lg = os.path.join(d, "alerts.log")
            ok, msg = alert.run(quiet=True, state_json=sj, alert_log=lg)
            self.assertTrue(ok, msg)
            with open(sj, encoding="utf-8") as f:
                self.assertTrue(json.load(f)["ok"])
            self.assertFalse(os.path.exists(lg),
                             "a healthy run must not write an alert")


if __name__ == "__main__":
    unittest.main()
