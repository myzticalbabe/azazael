"""Tests for the Q1 rules-as-data format and its skeleton extractor."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from maat import rules


def _valid_ruleset() -> dict:
    return rules.ruleset("2026-11-03", {
        "media": "2d", "ref": "test-src", "content_sha256": "a" * 64,
        "measured_on": "2026-11-03",
    }, [
        {"id": "R1", "when": ["mirror"], "then": {"kernel": "render", "effect": "overlay", "args": {}}, "weight": 0.5},
    ])


class FormatTests(unittest.TestCase):
    def test_format_version_is_first_checked(self):
        rs = _valid_ruleset()
        rs["rule_format"] = "WRONG"
        errs = rules.validate(rs)
        self.assertTrue(any("rule_format" in e for e in errs))

    def test_conformant_ruleset_validates_clean(self):
        self.assertEqual(rules.validate(_valid_ruleset()), [])

    def test_unknown_fact_is_not_freeform(self):
        rs = _valid_ruleset()
        rs["rules"][0]["when"] = ["nonsense"]
        errs = rules.validate(rs)
        self.assertTrue(any("unknown fact" in e for e in errs))

    def test_unknown_effect_rejected(self):
        rs = _valid_ruleset()
        rs["rules"][0]["then"] = {"kernel": "arena", "effect": "explode", "args": {}}
        self.assertTrue(any("unknown effect" in e for e in rules.validate(rs)))

    def test_bad_source_hash_rejected(self):
        rs = _valid_ruleset()
        rs["source"]["content_sha256"] = "zz"
        self.assertTrue(any("content_sha256" in e for e in rules.validate(rs)))

    def test_bad_rule_id_rejected(self):
        rs = _valid_ruleset()
        rs["rules"][0]["id"] = "X9"
        self.assertTrue(any("rule id" in e for e in rules.validate(rs)))


class ExtractTests(unittest.TestCase):
    def test_deterministic_same_text_same_source_hash(self):
        a = rules.extract("mirror then shatter then forge", ref="x")
        b = rules.extract("mirror then shatter then forge", ref="x")
        self.assertEqual(a["source"]["content_sha256"], b["source"]["content_sha256"])
        self.assertEqual(a, b)

    def test_hits_match_declared_vocabulary(self):
        rs = rules.extract("mirror and shatter and forge and weave", ref="x")
        facts = [r["when"][0] for r in rs["rules"]]
        self.assertEqual(facts, ["mirror", "shatter", "forge", "weave"])
        self.assertEqual(rules.validate(rs), [])

    def test_no_hits_yields_empty_ruleset(self):
        rs = rules.extract("nothing relevant here", ref="x")
        self.assertEqual(rs["rules"], [])
        self.assertEqual(rules.validate(rs), [])

    def test_synonyms_map_to_canonical_fact(self):
        rs = rules.extract("reflect fracture anvil", ref="x")
        self.assertEqual([r["when"][0] for r in rs["rules"]], ["mirror", "shatter", "forge"])

    def test_shatter_effect_carries_kernel_declared_name(self):
        rs = rules.extract("shatter", ref="x")
        self.assertEqual(rs["rules"][0]["then"],
                         {"kernel": "mesh", "effect": "shatter", "args": {"fact": "shatter"}})


class LoadCliTests(unittest.TestCase):
    def test_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "rs.json"
            p.write_text(json.dumps(rules.extract("forge and veil", ref="f")), encoding="utf-8")
            rs = rules.load(p)
            self.assertEqual(rs["rule_format"], "Q1R1")

    def test_legacy_synonym_mapping_exists(self):
        self.assertIn("reflect", rules._TOKEN_FACTS)

    def test_cli_rules_emits_conformant_json(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        proc = subprocess.run(
            [sys.executable, "-m", "maat", "rules",
             "--text", "mirror then shatter", "--ref", "cli-test", "--version", "2026-11-03"],             capture_output=True, text=True, cwd=root, timeout=30,
            env=None if sys.platform != "win32" else {"PYTHONPATH": str(root / "src")},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rs = json.loads(proc.stdout)
        self.assertEqual(rs["rule_format"], "Q1R1")
        self.assertEqual(rules.validate(rs), [])


if __name__ == "__main__":
    unittest.main()
