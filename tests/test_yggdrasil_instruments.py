# coding: utf-8
"""Unit tests for the 2026-10-31 census instruments.

The census's own `--selftest` proves classification on a fixture. These tests
prove the three STANDALONE instruments behave as gates: the alias table cannot
name a directory that no longer exists, an unused declaration is reported stale,
the unresolved ratchet fails on growth, `--affected` is file-precise and refuses
an ambiguous name, and the boundary policy's own controls stay green.

Nothing here needs a network, a daemon or the real repository: every fixture is
written to a temp dir, because a gate that only runs on one machine's tree is a
gate that stops running on the next one.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"


def _load(name: str):
    """Import a tools/ module by path: tools/ is a script directory, not a package."""
    spec = importlib.util.spec_from_file_location("_t_" + name, TOOLS / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _fixture(root: Path) -> None:
    """A -> B -> C, plus a driver outside src that calls into C."""
    for tree in ("A", "B", "C", "D", "RUN"):
        (root / "src" / tree).mkdir(parents=True, exist_ok=True)
    (root / "src" / "A" / "a.py").write_text("import B.b\n", encoding="utf-8")
    (root / "src" / "B" / "b.py").write_text("from C import c\n", encoding="utf-8")
    (root / "src" / "C" / "c.py").write_text("c = 1\n", encoding="utf-8")
    (root / "src" / "C" / "dup.py").write_text("d = 1\n", encoding="utf-8")
    (root / "src" / "D" / "dup.py").write_text("d = 2\n", encoding="utf-8")
    (root / "src" / "RUN" / "go.bat").write_text("python C\\c.py\r\n", encoding="utf-8")


class AliasTable(unittest.TestCase):
    """The declared alias table is configuration, so it must not outlive it."""

    def test_every_declaration_names_a_real_path(self):
        yc = _load("yggdrasil_census")
        data = json.loads((TOOLS / "resolution_aliases.json").read_text(encoding="utf-8"))
        src = ROOT / "src"
        missing = []
        for prefix, target in (data.get("prefixes") or {}).items():
            if not (src / target).exists():
                missing.append("prefix %s -> %s" % (prefix, target))
        for name, target in (data.get("files") or {}).items():
            if not (src / target).is_file():
                missing.append("file %s -> %s" % (name, target))
        self.assertEqual(missing, [], "alias declaration points at a path that "
                                      "does not exist: %r" % (missing,))
        # ...and the deliberate absences stay documented, so an absent entry is a
        # decision on the record rather than an oversight.
        self.assertIn("deliberately_absent", data)
        self.assertIsInstance(yc.Aliases({}, "empty").stale(), list)

    def test_unused_declaration_is_stale(self):
        yc = _load("yggdrasil_census")
        al = yc.Aliases({"prefixes": {"USED": "CORE", "UNUSED": "CORE"}}, "test")
        al.used["prefix:USED"] += 1
        self.assertEqual(al.stale(), ["prefix:UNUSED"])


class Affected(unittest.TestCase):
    """`--affected` licenses re-verification, so it may not guess."""

    @classmethod
    def setUpClass(cls):
        cls.yc = _load("yggdrasil_census")
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        _fixture(root)
        cls.ledger = cls.yc.census(root / "src", keep_edges=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_file_precise_transitive(self):
        res = self.yc.affected_trees(self.ledger, "C/c.py")
        self.assertEqual(res["granularity"], "file")
        depth = {r["node"]: r["depth"] for r in res["rows"]}
        self.assertEqual(depth.get("B/b.py"), 1)
        self.assertEqual(depth.get("A/a.py"), 2)
        # the driver that calls into C is a *shell* hop and must be reported as one
        self.assertIn("RUN/go.bat", res["affected_files"])

    def test_ambiguous_basename_is_refused(self):
        res = self.yc.affected_trees(self.ledger, "dup.py")
        self.assertTrue(res.get("error"), "ambiguous name was answered, not refused")
        self.assertEqual(res["rows"], [])
        self.assertEqual(sorted(res["candidates"]), ["C/dup.py", "D/dup.py"])

    def test_limb_granularity_is_labelled(self):
        res = self.yc.affected_trees(self.ledger, "C")
        self.assertEqual(res["granularity"], "limb")
        self.assertIn("B", res["affected_limbs"])


class Ratchet(unittest.TestCase):
    """The unresolved count may fall, never rise."""

    def test_growth_fails_and_flat_passes(self):
        rr = _load("unresolved_ratchet")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name) / "baseline.json"
        base.write_text(json.dumps({"counts": {"ambiguous": 2, "outside-root": 1},
                                    "total": 3}), encoding="utf-8")
        rr.BASELINE = base
        now = {"ambiguous": 2, "outside-root": 1, "target-not-found": 0}
        rr.measure = lambda root: {"references": 3, "resolved": 0,
                                  "unresolved": dict(now), "total": sum(now.values())}
        self.assertEqual(rr.main(["--check"]), 0, "unchanged counts must pass")

        now["ambiguous"] = 3
        self.assertEqual(rr.main(["--check"]), 1, "a new unresolved reference must fail")

        now["ambiguous"] = 1        # resolving one must not fail the gate
        self.assertEqual(rr.main(["--check"]), 0)


class BoundaryPolicy(unittest.TestCase):
    """Tier constraints are only worth having if their controls are green."""

    def test_controls_and_policy_shape(self):
        bp = _load("boundary_policy")
        self.assertEqual(bp.selftest(), 0)
        policy = json.loads((TOOLS / "boundary_policy.json").read_text(encoding="utf-8"))
        rules = policy.get("constraints") or []
        self.assertTrue(rules, "policy declares no constraints")
        for rule in rules:
            self.assertTrue(rule.get("name"), "unnamed rule: %r" % (rule,))
            self.assertTrue(rule.get("why"), "rule %r has no reason on record"
                            % (rule.get("name"),))
            self.assertTrue(rule.get("forbid"), "rule %r forbids nothing"
                            % (rule.get("name"),))


if __name__ == "__main__":
    unittest.main()
