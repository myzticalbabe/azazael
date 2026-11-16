"""Tests for the Q3 game-tree arena consumer of Q1R1 rulesets."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from maat import arena, rules


def _ruleset() -> dict:
    """Facts chosen so every kernel is present: render (mirror), mesh (shatter),
    arena (pulse/nest/drift). The arena log must show each in its place."""
    return rules.extract("mirror then shatter then pulse then nest then drift",
                         ref="t", version="2026-11-03")


class ArenaStateTests(unittest.TestCase):
    def test_new_arena_is_conformant(self):
        self.assertEqual(arena.validate_arena(arena.new_arena("s", version="2026-11-03")), [])

    def test_new_arena_deterministic(self):
        self.assertEqual(arena.new_arena("s", version="2026-11-03"),
                         arena.new_arena("s", version="2026-11-03"))

    def test_bad_parent_rejected(self):
        st = arena.new_arena("s", version="2026-11-03")
        st["branches"][0]["parent"] = "ghost"
        self.assertTrue(any("parent" in e for e in arena.validate_arena(st)))

    def test_foreign_token_rejected(self):
        st = arena.new_arena("s", version="2026-11-03")
        st["branches"][0]["tokens"] = ["nonfact"]
        self.assertTrue(any("vocabulary" in e for e in arena.validate_arena(st)))


class ApplyTests(unittest.TestCase):
    def test_non_arena_rules_are_deferred(self):
        out = arena.apply(_ruleset(), arena.new_arena("s", version="2026-11-03"), frames=self.CYCLE)
        applied = [e for e in out["log"] if not e["deltas"][0].startswith("deferred")]
        self.assertTrue(applied)
        self.assertTrue(all(e["effect"] in ("spawn", "promote", "retire", "forbid")
                            for e in applied))
        self.assertTrue(any(e["effect"] == "shatter"  # mesh rule: Q2's turn
                            and e["deltas"][0].startswith("deferred") for e in out["log"]))
        self.assertTrue(any(e["effect"] == "overlay"  # render rule: deferred too
                            and e["deltas"][0].startswith("deferred") for e in out["log"]))

    # one full cycle of the fact vocabulary, so every mapped kernel fires
    CYCLE = len(rules.FACTS)

    def test_promote_gives_score_to_live_branches(self):
        out = arena.apply(_ruleset(), arena.new_arena("s", version="2026-11-03"), frames=self.CYCLE)
        scores = [b["score"] for b in out["arena"]["branches"]]
        self.assertTrue(max(scores) > 0.0)
        self.assertEqual(out["ranking"][0]["id"], max(out["ranking"], key=lambda r: r["score"])["id"])

    def test_input_arena_is_not_mutated_in_place(self):
        st = arena.new_arena("s", version="2026-11-03")
        before = json.dumps(st, sort_keys=True)
        arena.apply(_ruleset(), st)
        self.assertEqual(json.dumps(st, sort_keys=True), before)

    def test_bad_arena_state_rejected_loudly(self):
        st = arena.new_arena("s", version="2026-11-03")
        st["seed_sha256"] = "zz"
        with self.assertRaises(ValueError):
            arena.apply(_ruleset(), st)


class DeterminismTests(unittest.TestCase):
    def test_same_inputs_same_outputs(self):
        a = arena.apply(_ruleset(), arena.new_arena("s", version="2026-11-03"), frames=arena.FRAMES)
        b = arena.apply(_ruleset(), arena.new_arena("s", version="2026-11-03"), frames=arena.FRAMES)
        self.assertEqual(a, b)
        self.assertEqual(a["ranking"], b["ranking"])

    def test_ranking_shape(self):
        out = arena.apply(_ruleset(), arena.new_arena("s", version="2026-11-03"))
        for row in out["ranking"]:
            self.assertIn("id", row)
            self.assertIn("score", row)
            self.assertIn("depth", row)


class CliTests(unittest.TestCase):
    def _run(self, *argv):
        root = pathlib.Path(__file__).resolve().parents[1]
        env = dict(os.environ, PYTHONPATH=str(root / "src")) if sys.platform == "win32" else None
        return subprocess.run(
            [sys.executable, "-m", "maat", *argv],
            capture_output=True, text=True, cwd=root, timeout=30, env=env,
        )

    def test_cli_arena_end_to_end(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            rj = pathlib.Path(d) / "rs.json"
            rj.write_text(json.dumps(_ruleset()), encoding="utf-8")
            proc = self._run("arena", "--rules", str(rj), "--seed", "cli-seed",
                             "--frames", str(len(rules.FACTS)))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = json.loads(proc.stdout)
            self.assertEqual(out["arena"]["arena_format"], arena.ARENA_FORMAT)
            self.assertTrue(out["log"])
            self.assertTrue(out["ranking"])

    def test_cli_rejects_bad_ruleset_with_status_1(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            rj = pathlib.Path(d) / "bad.json"
            bad = _ruleset()
            bad["rules"][0]["id"] = "XX"
            rj.write_text(json.dumps(bad), encoding="utf-8")
            proc = self._run("arena", "--rules", str(rj))
            self.assertEqual(proc.returncode, 1)
            self.assertIn("rule id", proc.stderr)


if __name__ == "__main__":
    unittest.main()
