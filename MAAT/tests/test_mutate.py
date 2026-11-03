"""Tests for the Q2 mesh-mutation consumer of Q1R1 rulesets."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from maat import mutate, rules


def _ruleset() -> dict:
    return rules.extract("mirror then shatter then forge", ref="t", version="2026-11-03")


class MeshStateTests(unittest.TestCase):
    def test_new_mesh_is_conformant(self):
        mesh = mutate.new_mesh("seed", version="2026-11-03")
        self.assertEqual(mutate.validate_mesh(mesh), [])

    def test_new_mesh_deterministic(self):
        self.assertEqual(mutate.new_mesh("seed", version="2026-11-03"),
                         mutate.new_mesh("seed", version="2026-11-03"))

    def test_bad_color_rejected(self):
        mesh = mutate.new_mesh("seed", version="2026-11-03")
        mesh["primitives"][0]["color"] = [300, 0, 0]
        errs = mutate.validate_mesh(mesh)
        self.assertTrue(any("color" in e for e in errs))

    def test_missing_field_rejected(self):
        mesh = mutate.new_mesh("seed", version="2026-11-03")
        del mesh["primitives"][1]["scale"]
        self.assertTrue(any("scale" in e for e in mutate.validate_mesh(mesh)))


class ApplyTests(unittest.TestCase):
    def test_non_mesh_rules_are_deferred(self):
        out = mutate.apply(_ruleset(), mutate.new_mesh("s", version="2026-11-03"))
        fired_effects = {e["effect"] for e in out["log"]}
        self.assertIn("shatter", fired_effects)
        self.assertIn("displace", fired_effects)
        self.assertNotIn("overlay", fired_effects)  # mirror -> render/overlay stays deferred

    def test_shatter_fractures_and_stamps(self):
        out = mutate.apply(_ruleset(), mutate.new_mesh("s", version="2026-11-03"))
        sh = [e for e in out["log"] if e["effect"] == "shatter"][0]
        p1 = out["mesh"]["primitives"][0]
        self.assertEqual(sh["rule_id"], "R2")
        self.assertFalse(p1["intact"])
        self.assertEqual(p1["fragments"], 2)  # the docstring contract: fragments += 2

    def test_input_mesh_is_not_mutated_in_place(self):
        mesh = mutate.new_mesh("s", version="2026-11-03")
        before = json.dumps(mesh, sort_keys=True)
        mutate.apply(_ruleset(), mesh)
        self.assertEqual(json.dumps(mesh, sort_keys=True), before)

    def test_input_mesh_rejected_loudly(self):
        mesh = mutate.new_mesh("s", version="2026-11-03")
        mesh["seed_sha256"] = "zz"
        with self.assertRaises(ValueError):
            mutate.apply(_ruleset(), mesh)


class DeterminismTests(unittest.TestCase):
    def test_same_inputs_same_outputs(self):
        a = mutate.apply(_ruleset(), mutate.new_mesh("s", version="2026-11-03"))
        b = mutate.apply(_ruleset(), mutate.new_mesh("s", version="2026-11-03"))
        self.assertEqual(a, b)

    def test_log_covers_every_fired_rule(self):
        out = mutate.apply(_ruleset(), mutate.new_mesh("s", version="2026-11-03"))
        for entry in out["log"]:
            self.assertIn("rule_id", entry)
            self.assertIn("deltas", entry)


class CliTests(unittest.TestCase):
    def test_cli_mutate_end_to_end(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            rj = pathlib.Path(d) / "rs.json"
            rj.write_text(json.dumps(_ruleset()), encoding="utf-8")
            env = None
            if sys.platform == "win32":
                env = dict(os.environ, PYTHONPATH=str(root / "src"))
            proc = subprocess.run(
                [sys.executable, "-m", "maat", "mutate", "--rules", str(rj),
                 "--seed", "cli-seed", "--frames", "4"],
                capture_output=True, text=True, cwd=root, timeout=30, env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = json.loads(proc.stdout)
            self.assertEqual(out["mesh"]["mesh_format"], mutate.MESH_FORMAT)
            self.assertTrue(out["log"])

    def test_cli_rejects_bad_ruleset_with_status_1(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            rj = pathlib.Path(d) / "bad.json"
            bad = _ruleset()
            bad["rules"][0]["id"] = "XX"
            rj.write_text(json.dumps(bad), encoding="utf-8")
            env = None
            if sys.platform == "win32":
                env = dict(os.environ, PYTHONPATH=str(root / "src"))
            proc = subprocess.run(
                [sys.executable, "-m", "maat", "mutate", "--rules", str(rj)],
                capture_output=True, text=True, cwd=root, timeout=30, env=env,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("rule id", proc.stderr)


if __name__ == "__main__":
    unittest.main()
