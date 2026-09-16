# coding: utf-8
"""The panels must not assert a state the rest of the board contradicts.

Why this file exists
--------------------
The monitors are the part of this system most likely to be believed without
checking, and four separate defects of the same shape were found in them:

* **Lilith** derived "hive live" from the whole `xenomorph` *nature* (8 worms,
  including RedQueenWorm), so one unrelated worm running made the verdict say
  OK while the seven lifecycle worms the section displays were all idle.
* **Lilith** labelled a spawn count `reg=`, which reads as "registered": all
  seven are registered, and `reg=0` looked like a fleet registration failure.
* **Azazael** counted arms via `dir(arms)`, which only sees what
  `arms/__init__` re-exports. `KaliArm` is defined, registered and running, yet
  was reported as an *unexported* file while the AOA board listed 9 arms.
* **Azazael** printed an unconditional "Training is live" verdict on the same
  screen as its own "STALE ... check Task Scheduler" line, with every cycle
  ~21h old.

Each is a claim that does not follow from the data underneath it. These tests
pin the fixed behaviour so the ambiguity cannot silently return.
"""
import json
import os
import sys
import tempfile
import time
import unittest

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_project_root, os.path.join(_project_root, "scripts"),
           os.path.join(_project_root, "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import live_monitor as lm   # noqa: E402


def _freshness(label, ok):
    return {"label": label, "ts": "2026-09-14T00:00:00", "age": 5.0 if ok else 1294.0,
            "ok": ok}


def _data(freshness, training=None):
    """Minimal `data` mapping shaped like collect()'s return value."""
    return {
        "evo": [{"best": 20.415}],
        "strategy": {"value": "defensive"},
        "activity": {"dreams": 11, "quality": 0.665},
        "freshness": freshness,
        "training": training or {},
    }


class TestVerdictFollowsTheData(unittest.TestCase):
    """`bottom_line` may not claim liveness the freshness rows deny."""

    def test_all_stale_is_reported_as_stalled(self):
        data = _data([_freshness("evolution", False),
                      _freshness("metacog/steer", False),
                      _freshness("dreaming", False),
                      _freshness("training", False)])
        verdict = lm.bottom_line(data)
        self.assertIn("stalled", verdict.lower())
        self.assertNotIn("Training is live", verdict)

    def test_stale_training_loop_alone_blocks_the_live_claim(self):
        """Evolution and training are the liveness-defining loops."""
        data = _data([_freshness("evolution", False),
                      _freshness("metacog/steer", True),
                      _freshness("dreaming", True),
                      _freshness("training", True)])
        verdict = lm.bottom_line(data)
        self.assertNotIn("Training is live", verdict)
        self.assertIn("stalled", verdict.lower())

    def test_partial_staleness_is_stated_not_hidden(self):
        data = _data([_freshness("evolution", True),
                      _freshness("metacog/steer", False),
                      _freshness("dreaming", True),
                      _freshness("training", True)])
        verdict = lm.bottom_line(data)
        self.assertIn("partially stale", verdict.lower())
        self.assertIn("1 loop(s) stale", verdict)

    def test_everything_fresh_still_says_live(self):
        data = _data([_freshness("evolution", True),
                      _freshness("metacog/steer", True),
                      _freshness("dreaming", True),
                      _freshness("training", True)])
        self.assertTrue(lm.bottom_line(data).startswith("Training is live"))

    def test_the_live_claim_is_the_minority_case(self):
        """Guard the defect shape directly: a stale board must never open with
        the word 'live'."""
        for evo_ok, train_ok in ((False, False), (False, True), (True, False)):
            data = _data([_freshness("evolution", evo_ok),
                          _freshness("training", train_ok),
                          _freshness("dreaming", True)])
            self.assertNotIn("Training is live", lm.bottom_line(data))


def _real_reexported_names():
    """Names the real `arms/__init__.py` re-exports, read statically.

    Derived rather than hardcoded. These tests previously pinned the literal
    8, so they went red the moment a legitimate arm was added (KaliArm,
    2026-09-14) -- a real honesty check turning into noise. Deriving the
expected value keeps the assertion about *behaviour* (the monitor reports
what is actually on disk) instead of about a snapshot of the tree.
    """
    path = os.path.join(_project_root, "src", "AOA", "arms", "__init__.py")
    names = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            code = raw.split("#", 1)[0].strip()
            if not code.startswith("from .") or " import " not in code:
                continue
            for part in code.split(" import ", 1)[1].split(","):
                part = part.strip().strip("()")
                if part.endswith("Arm"):
                    names.append(part)
    return names


class TestArmCountIsHonest(unittest.TestCase):
    """`arm_classes defined` != `re-exported by arms/__init__`, and a file that
    defines an Arm class is not 'unexported'."""

    def setUp(self):
        self._saved_dir = lm.AOA_DIR
        self._saved_import = dict(lm._AOA_IMPORT)
        self.tmp = tempfile.TemporaryDirectory()
        arms = os.path.join(self.tmp.name, "arms")
        os.makedirs(arms)
        with open(os.path.join(arms, "__init__.py"), "w", encoding="utf-8") as fh:
            # Deliberately re-export only one of the two classes.
            fh.write("from .alpha_arm import AlphaArm\n__all__ = ['AlphaArm']\n")
        with open(os.path.join(arms, "alpha_arm.py"), "w", encoding="utf-8") as fh:
            fh.write("class AlphaArm:\n    pass\n")
        with open(os.path.join(arms, "beta_arm.py"), "w", encoding="utf-8") as fh:
            fh.write("class BetaArm:\n    pass\n")
        with open(os.path.join(arms, "empty_arm.py"), "w", encoding="utf-8") as fh:
            fh.write("# no arm class here\nVALUE = 1\n")
        lm.AOA_DIR = self.tmp.name
        lm._AOA_IMPORT.clear()

    def tearDown(self):
        lm.AOA_DIR = self._saved_dir
        lm._AOA_IMPORT.clear()
        lm._AOA_IMPORT.update(self._saved_import)
        self.tmp.cleanup()

    def test_defined_counts_classes_not_reexports(self):
        out = lm.aoa_status()
        self.assertEqual(out["arm_classes"], 2,
                         "should count AlphaArm and BetaArm defined on disk")

    def test_a_defined_but_unreexported_arm_is_not_called_unexported(self):
        out = lm.aoa_status()
        self.assertNotIn("beta_arm", out["unexported"],
                         "beta_arm defines BetaArm; it is not unexported")
        self.assertIn("beta_arm", out["not_reexported"],
                      "beta_arm is defined but absent from arms/__init__")

    def test_a_file_with_no_class_is_the_real_unexported_case(self):
        out = lm.aoa_status()
        self.assertIn("empty_arm", out["unexported"])

    def test_reexported_is_reported_separately(self):
        out = lm.aoa_status()
        self.assertIn("reexported", out)
        self.assertIn("arm_classes", out)

    def test_the_import_cache_re_resolves_for_a_new_dir(self):
        """The cache is keyed on the directory it resolved against.

        `if not _AOA_IMPORT` latched whatever the first call saw, so a call
        against a different AOA_DIR (or a transient ImportError) fixed the
        reported count for the rest of the process.
        """
        first = lm.aoa_status()["reexported"]
        lm.AOA_DIR = self._saved_dir            # the real tree
        try:
            second = lm.aoa_status()["reexported"]
        finally:
            lm.AOA_DIR = self.tmp.name
        expected = len(_real_reexported_names())
        self.assertEqual(second, expected,
                         "the monitor must report the real re-export count")
        self.assertGreater(expected, 0, "fixture expects a populated arms/__init__")
        self.assertNotEqual(first, second,
                            "the count must be re-derived, not cached across dirs")


class TestAmbiguousLabelsStayFixed(unittest.TestCase):
    """Source-level guards for the two misread labels."""

    def _source(self, rel):
        return open(os.path.join(_project_root, rel), encoding="utf-8").read()

    def test_lilith_does_not_label_spawns_as_registration(self):
        src = self._source(os.path.join("scripts", "lilith_live_monitor.py"))
        for line in src.splitlines():
            if line.strip().startswith("#"):
                continue
            self.assertNotIn('reg=%s', line,
                             "spawn count relabelled as 'reg=' again: %s"
                             % line.strip())
        self.assertIn("spawns=%s", src)
        # An explicit legend, so the column cannot be misread.
        self.assertIn("NOT registration", src)

    def test_azazael_board_does_not_call_the_ga_leaderboard_worm_health(self):
        src = self._source(os.path.join("scripts", "live_monitor.py"))
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            self.assertNotIn('"WORMS  "', line,
                             "WORMGA leaderboard relabelled as live worm "
                             "health again: %s" % stripped)

    def test_azazael_labels_the_wormga_board_and_its_age(self):
        src = self._source(os.path.join("scripts", "live_monitor.py"))
        self.assertIn("WBOARD", src)
        self.assertIn("WORMGA eval", src)


class TestAoaLineReconcilesWithTheBoard(unittest.TestCase):
    """The Azazael board and the AOA board read the same registry and must not
    disagree about the same subsystem.

    `aoa_status()` used to glob only `arms/*_arm.py` and then skip
    `support_arms.py`, so it reported *5* arm classes while the AOA board
    listed 9 registered arms. The four it dropped (PamsArm,
    PerformanceMonitorArm, LlamaServerArm, AgentSelectorArm) are all
    registered and running.
    """

    def _classes_on_disk(self):
        import ast
        import glob
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        total = 0
        for path in glob.glob(os.path.join(root, "src", "AOA", "arms", "*.py")):
            if os.path.basename(path) == "__init__.py":
                continue
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            total += sum(1 for n in tree.body
                         if isinstance(n, ast.ClassDef) and n.name.endswith("Arm"))
        return total

    def test_arm_class_count_matches_the_source_tree(self):
        on_disk = self._classes_on_disk()
        self.assertGreater(on_disk, 5, "fixture expects support_arms to contribute")
        self.assertEqual(lm.aoa_status()["arm_classes"], on_disk,
                         "arm class count must count every arm file on disk")

    def test_the_four_support_arms_are_not_dropped(self):
        src = open(os.path.join(_project_root, "scripts", "live_monitor.py"),
                   encoding="utf-8").read()
        for line in src.splitlines():
            code = line.split("#", 1)[0]
            self.assertNotIn('"support_arms", "__init__"', code,
                             "support_arms must not be skipped: %s" % line.strip())

    def test_registry_arm_count_is_at_least_the_definitions(self):
        """Every defined arm must be re-exported; a gap is a real finding.

        This is the assertion that would have caught the KaliArm omission:
        `not_reexported` is empty only when every arm class defined on disk is
        reachable through `arms/__init__.py`, which is the precondition for
        `@register_arm` having run at all.
        """
        out = lm.aoa_status()
        self.assertEqual(out["reexported"], len(_real_reexported_names()))
        self.assertEqual(out["not_reexported"], [],
                         "every defined arm class must be re-exported")
        self.assertGreaterEqual(out["reexported"], out["arm_classes"],
                                "cannot re-export fewer arms than are defined")


class TestAgesComeFromContentNotMtime(unittest.TestCase):
    """Both AOA artifacts now have a producer that rewrites them, so file mtime
    is the refresh time. Reporting mtime as the artifact's age announced
    "0d ago" for milestones written 76 days earlier and for a baseline taken
    18 days earlier.
    """

    def test_milestone_age_is_the_newest_milestone(self):
        import datetime
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(root, "src", "AOA", "AOA_MILESTONE.json"),
                  encoding="utf-8") as fh:
            doc = json.load(fh)
        stamps = [m.get("timestamp")
                  for m in (doc.get("session") or {}).get("milestones") or []
                  if m.get("timestamp")]
        if not stamps:
            self.skipTest("no recorded milestones to age")
        expected = (time.time()
                    - datetime.datetime.fromisoformat(max(stamps)).timestamp()) / 86400.0
        got = lm.aoa_status()["ms_age_d"]
        self.assertAlmostEqual(got, expected, delta=0.1,
                               msg="milestone age must come from the milestone rows")

    def test_bench_age_is_the_baseline_date(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(os.path.join(root, "src", "AOA", "benchmark_data.json"),
                  encoding="utf-8") as fh:
            bd = json.load(fh)
        base = ((bd.get("_meta") or {}).get("baseline_date")
                or (bd.get("eve") or {}).get("benchmark_date"))
        if not base:
            self.skipTest("no baseline date recorded")
        import datetime
        expected = (time.time()
                    - datetime.datetime.fromisoformat(base).timestamp()) / 86400.0
        self.assertAlmostEqual(lm.aoa_status()["bench_age_d"], expected, delta=0.1)

    def test_mtime_is_not_used_as_the_history_age(self):
        st = lm.aoa_status()
        if st.get("ms_mtime_d") is None:
            self.skipTest("milestone file unreadable")
        # A rewrite moves mtime to ~0 while the history stays months old; the
        # two must not be the same number here or the distinction is gone.
        self.assertNotAlmostEqual(st["ms_mtime_d"], st["ms_age_d"], delta=0.5)


class TestMeshPanelIsTruthful(unittest.TestCase):
    """The console board must show the fleet cycle, and date it honestly.

    Why this class exists: the mesh is the architecture the rest of the system
    now runs on, and this wallboard had *zero* mesh references -- no fabric
    row, no cycle age, no staleness. A fleet cycle that had been dead for 46 h
    therefore read as a healthy board, which is exactly the class of claim
    the rest of this file pins. These tests cover the reader (real artifact
    shapes, optional fields) and the two places the age has to surface: the
    MESH line and the staleness verdict.
    """

    def setUp(self):
        import tempfile
        self._tmp = tempfile.mkdtemp(prefix="mesh_panel_")
        self._old = (lm.MESH_STATE, lm.MESH_TELEMETRY)
        lm.MESH_STATE = os.path.join(self._tmp, "mesh_cycle.json")
        lm.MESH_TELEMETRY = os.path.join(self._tmp, "cycle_telemetry.jsonl")

    def tearDown(self):
        import shutil
        lm.MESH_STATE, lm.MESH_TELEMETRY = self._old
        shutil.rmtree(self._tmp, ignore_errors=True)

    @staticmethod
    def _iso(hours_ago):
        import datetime
        t = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
        return t.strftime("%Y-%m-%dT%H:%M:%S")

    def _write_cycle(self, hours_ago=0.0, natures=None, ok=4, fail=0, cpu=12.0):
        natures = natures if natures is not None else {
            "mesh": {"worms": 4, "ok": 4, "fail": 0, "ms": 37.1},
            "analysis": {"worms": 17, "ok": 17, "fail": 0, "ms": 3942.4},
        }
        with open(lm.MESH_STATE, "w", encoding="utf-8") as f:
            json.dump({"at": self._iso(hours_ago), "ok": ok, "fail": fail,
                       "complete": True, "duration_s": 28.3,
                       "natures": natures, "retried": {"retried": 0},
                       "discovered": {"natures": len(natures), "worms": ok + fail},
                       "telemetry": {"cpu": cpu, "mem": 80.0, "db_mb": 449.9,
                                     "at": self._iso(hours_ago)}}, f)

    def test_reader_reports_natures_and_names_the_failing_one(self):
        self._write_cycle(natures={
            "mesh": {"worms": 4, "ok": 4, "fail": 0, "ms": 37.1},
            "analysis": {"worms": 17, "ok": 14, "fail": 3, "ms": 3942.4},
        }, ok=18, fail=3)
        st = lm.mesh_status()
        self.assertEqual(st["natures"], 2)
        self.assertEqual(st["failed"], ["analysis"])
        self.assertEqual(st["ok"], 18)
        self.assertEqual(st["fail"], 3)
        self.assertEqual(st["slowest"][0], "analysis")

    def test_optional_fields_never_become_invented_numbers(self):
        """A partial artifact yields None, not a plausible 0/0."""
        with open(lm.MESH_STATE, "w", encoding="utf-8") as f:
            json.dump({"at": self._iso(0.0)}, f)
        st = lm.mesh_status()
        self.assertIsNone(st["ok"])
        self.assertIsNone(st["fail"])
        self.assertIsNone(st["natures"])
        self.assertEqual(st["failed"], [])
        self.assertEqual(st["cpu_trend"], [])

    def test_absent_artifact_renders_as_unknown_not_zero(self):
        st = lm.mesh_status()
        self.assertIsNone(st["at"])
        self.assertIsNone(st["ok"])
        self.assertEqual(st["samples"], 0)

    def test_telemetry_tail_supplies_the_cpu_trend(self):
        self._write_cycle(cpu=10.0)
        with open(lm.MESH_TELEMETRY, "w", encoding="utf-8") as f:
            for c in (22.6, 17.5, 14.2, 10.0):
                f.write(json.dumps({"cpu": c, "mem": 80.0, "db_mb": 449.9,
                                    "at": self._iso(0.0)}) + "\n")
        st = lm.mesh_status()
        self.assertEqual(st["samples"], 4)
        self.assertEqual(st["cpu_trend"], [22.6, 17.5, 14.2, 10.0])

    def test_age_comes_from_the_artifact_not_the_file_mtime(self):
        """A freshly rewritten cycle that records an old run must read old.

        The board ages the mesh by the `at` inside it; using mtime would let a
        producer's touch reset the age and hide a dead cycle.
        """
        self._write_cycle(hours_ago=40.0)
        st = lm.mesh_status()
        self.assertIsNotNone(st["age"])
        self.assertGreater(st["age"], 39 * 60)
        self.assertLess(st["age"], 41 * 60)

    def test_collect_wires_the_mesh_into_freshness(self):
        """`collect()` must add a mesh row, or the age reaches nothing."""
        import sqlite3
        self._write_cycle(hours_ago=40.0)
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY, timestamp TEXT, "
                    "event_type TEXT, source TEXT, data TEXT, severity TEXT)")
        data = lm.collect(con)
        con.close()
        self.assertIn("mesh", data)
        mesh_rows = [f for f in data["freshness"] if f["label"] == "mesh"]
        self.assertEqual(len(mesh_rows), 1)
        self.assertFalse(mesh_rows[0]["ok"], "a 40h-old fleet cycle is not fresh")
        # and it must reach the verdict, not just the panel
        self.assertIn("stalled", lm.bottom_line(data).lower())

    def test_a_fresh_fleet_cycle_does_not_claim_staleness(self):
        import sqlite3
        self._write_cycle(hours_ago=0.05)   # ~3 min: one cycle interval
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY, timestamp TEXT, "
                    "event_type TEXT, source TEXT, data TEXT, severity TEXT)")
        data = lm.collect(con)
        con.close()
        mesh_rows = [f for f in data["freshness"] if f["label"] == "mesh"]
        self.assertTrue(mesh_rows[0]["ok"])

    def test_render_shows_the_mesh_line(self):
        """render() draws the fleet cycle (the panel is not collector-only)."""
        import datetime
        import sqlite3
        self._write_cycle(natures={
            "mesh": {"worms": 4, "ok": 4, "fail": 0, "ms": 37.1},
            "analysis": {"worms": 17, "ok": 14, "fail": 3, "ms": 3942.4},
        }, ok=18, fail=3)
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY, timestamp TEXT, "
                    "event_type TEXT, source TEXT, data TEXT, severity TEXT)")
        data = lm.collect(con)          # the real frame, so no key is invented
        con.close()
        lines = lm.render(data, datetime.datetime.now()).split("\n")
        mesh_lines = [ln for ln in lines if ln.startswith("MESH")]
        self.assertEqual(len(mesh_lines), 1)
        self.assertIn("18/21 ok", mesh_lines[0])
        self.assertIn("FAIL: analysis", mesh_lines[0])
        # the LOOPS row must carry the mesh too (that is what the verdict reads)
        self.assertIn("mesh", [ln for ln in lines if ln.startswith("LOOPS")][0])


if __name__ == "__main__":
    unittest.main()
