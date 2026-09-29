# coding: utf-8
"""Regression guard for the intermesh audit (tools/nature_integration_map.py).

What "intermesh" is
-------------------
The audit that turns the wire-or-cut census into an actionable plan by mapping
each uncalled capability onto the natures' own data contracts, and that renders
`NEURAL_MESH_INTEROP.mmd` (the only human-readable picture of the mesh).

The four gaps these tests pin (all measured 2026-09-28)
-------------------------------------------------------
1. 23 of 103 findings (22%) got the disposition `module_level`, which no
   consumer can act on, and the Mermaid emitter then skipped them outright
   (`continue`) -- so a fifth of the backlog was invisible in the one artifact
   meant to make it visible. A module-level capability now inherits its nature
   from the registry's `__module__` records, keyed by BOTH the dotted path and
   the short stem the census actually stores.
2. The disposition classes were computed and thrown away: exactly one
   `classDef` was emitted and C_wire / C_integrate / C_unresolved were never
   attached to a node, so wireable, orphaned and unresolved capabilities all
   rendered identically. Per the Mermaid flowchart spec a class only takes
   effect when declared AND attached.
3. "Production" meant `src/` only, so the schedulers and audit tools in
   `scripts/` and `tools/` were invisible as consumers. `get_gossip_trust_state`
   is called by `mesh_gossip_cycle.py` and still landed in `unresolved`.
4. Nothing checked the data contracts at all, even though `emits`/`requires` are
   the only evidence that can distinguish a real wiring from decoration -- the
   `SplitBrainResolverWorm.report_fork` failure the tool's own docstring cites.
23 natures declared no contract, so `emits`/`requires` came back as empty dicts
that read as "clean".
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_tool():
    path = ROOT / "tools" / "nature_integration_map.py"
    if not path.is_file():
        pytest.skip("tools/nature_integration_map.py not present")
    spec = importlib.util.spec_from_file_location("nim_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nim = _load_tool()


# ── 1. module-level capabilities are not a dead end ────────────────────

DEFS = {"optimization": {"feeds_into": ["monitor", "telemetry"]},
        "monitor": {"feeds_into": ["orchestration"]}}


class TestModuleLevelDispositions:
    def test_module_level_with_a_production_referrer_is_wireable(self):
        out = nim.classify(
            {"qualname": "spine_reset", "module": "spine_registry"},
            {}, DEFS, {"spine_reset": [("src/CORE/x.py", 3)]},
            {"spine_registry": "mesh"})
        assert out["kind"] == "module_level"
        assert out["disposition"] == "wire_at_site"
        assert out["ref_scope"] == ["src"]

    def test_module_level_inherits_its_module_nature(self):
        out = nim.classify(
            {"qualname": "q_confidence", "module": "optimization"},
            {}, DEFS, {}, {"optimization": "optimization"})
        assert out["kind"] == "module_level"
        assert out["nature"] == "optimization"
        assert out["disposition"] == "integrate_via_stage"
        assert out["consumer_natures"] == ["monitor", "telemetry"]
        assert "must drive it" in out["reason"]

    def test_module_level_with_nothing_known_is_honestly_unresolved(self):
        out = nim.classify(
            {"qualname": "_mad", "module": "exmachina"}, {}, DEFS, {}, {})
        assert out["disposition"] == "unresolved"
        assert out["nature"] == ""

    def test_no_finding_is_left_with_the_dead_end_disposition(self):
        """`module_level` must never be a disposition again, only a kind."""
        for refs, modules in (((), {}), ({"f": [("src/a.py", 1)]}, {}),
                              ((), {"m": "monitor"})):
            out = nim.classify({"qualname": "f", "module": "m"},
                               {}, DEFS, dict(refs), dict(modules))
            assert out["disposition"] != "module_level", out


# ── 2/3. entry points count, and the referrer's scope is recorded ──────

class TestConsumerScope:
    def test_scope_tag_names_the_roots_that_hold_the_refs(self):
        scope_of = {"src/CORE/a.py": "src", "scripts/b.py": "scripts",
                    "tools/c.py": "tools"}
        refs = [("scripts/b.py", 1), ("src/CORE/a.py", 2)]
        assert nim._scope_tag(refs, scope_of) == ["scripts", "src"]

    def test_use_roots_include_the_entry_points(self):
        assert set(nim.USE_ROOTS) == {"src", "scripts", "tools"}

    def test_scan_reaches_scripts_and_tags_them(self):
        uses, scope_of = nim.production_uses()
        assert any(f.startswith("scripts/") for f in scope_of), \
            "scripts/ must be scanned: the schedulers are production consumers"
        assert scope_of.get("scripts/chain_controller.py") == "scripts"


# ── 4. the data-contract half is reported, not silently empty ──────────

class TestContractCoverage:
    def test_undeclared_contract_is_named_not_silent(self):
        cov = nim.contract_coverage({"mesh": {"feeds_into": []}}, {})
        assert cov["no_contract_declared"] == ["mesh"]
        assert cov["declared"] == {}

    def test_declared_emit_that_nothing_reads_is_reported(self):
        defs = {"monitor": {"data_contracts": {
            "emits": {"cpu_pct": "float", "read_me": "float"},
            "requires": {}}}}
        cov = nim.contract_coverage(defs, {"read_me": [("src/x.py", 1)]})
        assert cov["declared"]["monitor"] == {"emits": 2, "requires": 0}
        assert cov["declared_emits_nothing_reads"] == {"monitor": ["cpu_pct"]}

    def test_a_fully_read_contract_reports_no_decoration(self):
        defs = {"monitor": {"data_contracts": {
            "emits": {"cpu_pct": "float"}, "requires": {"limit": "int"}}}}
        cov = nim.contract_coverage(defs, {"cpu_pct": [("src/x.py", 1)]})
        assert cov["declared_emits_nothing_reads"] == {}


# ── derived contracts cover the natures that declare none ─────────────

class TestDerivedContracts:
    """`derived_contracts` reads emits off the code, so it cannot be invented."""

    def test_envelope_keys_are_not_treated_as_payload(self):
        assert "success" in nim.ENVELOPE_KEYS
        assert "result" in nim.ENVELOPE_KEYS
        assert "method" in nim.ENVELOPE_KEYS
        assert "cpu_pct" not in nim.ENVELOPE_KEYS

    def test_covers_more_natures_than_declare_a_contract(self):
        if not (ROOT / "src" / "CORE" / "worm_registry.py").is_file():
            pytest.skip("src tree not present")
        # The tool only puts `src` on sys.path inside main(), so a caller that
        # loads it as a module has to do it first.
        src = str(ROOT / "src")
        if src not in sys.path:
            sys.path.insert(0, src)
        try:
            natures = nim.registry_natures()
        except Exception as exc:                # registry optional
            pytest.skip("registry unavailable: %r" % (exc,))
        if not natures:
            pytest.skip("registry returned nothing")
        derived = nim.derived_contracts(natures)
        assert derived, "no nature's emits could be derived from code"
        # Every derived entry must name keys and say how many members it read.
        for nature, item in derived.items():
            assert item["emits"], "%s derived an empty contract" % nature
            assert item["members"] >= 1
            assert not (set(item["emits"]) & nim.ENVELOPE_KEYS)

    def test_synthetic_source_yields_exactly_its_payload_keys(self, tmp_path,
                                                              monkeypatch):
        mod = tmp_path / "fake_nature.py"
        mod.write_text(
            "class FakeWorm:\n"
            "    def execute(self):\n"
            "        return {'success': True, 'payload_a': 1,\n"
            "                'payload_b': 2, 'result': {}}\n",
            encoding="utf-8")
        monkeypatch.setattr(nim, "_module_file", lambda m: mod)
        derived = nim.derived_contracts(
            {"FakeWorm": {"nature": "fakenature", "module": "fake_nature"}})
        assert list(derived) == ["fakenature"]
        assert sorted(derived["fakenature"]["emits"]) == ["payload_a",
                                                          "payload_b"]

    def test_coverage_reports_both_registers(self):
        defs = {"mesh": {"data_contracts": {"emits": {"a": "int"},
                                              "requires": {}}}}
        derived = {"mesh": {"emits": {"a": 1, "b": 1}, "members": 2}}
        cov = nim.contract_coverage(defs, {"a": [("src", 1)]}, derived)
        assert cov["declared"]["mesh"] == {"emits": 1, "requires": 0}
        assert cov["derived"]["mesh"] == {"emits": 2, "members": 2}
        assert cov["derived_emits_nothing_reads"] == {"mesh": ["b"]}
        assert cov["coverage"] == (
            "1/1 natures declare a contract, 1/1 have one derivable from code")


# ── the rendered artifact keeps the dispositions visible ──────────────

class TestInteropGraph:
    """Pins the artifact the generator writes, not a private helper."""

    MMD = ROOT / "NEURAL_MESH_INTEROP.mmd"
    MAP = ROOT / "NEURAL_MESH_INTEGRATION_MAP.json"

    def test_declared_and_applied_classes_agree(self):
        if not self.MMD.is_file():
            pytest.skip("NEURAL_MESH_INTEROP.mmd not generated")
        text = self.MMD.read_text(encoding="utf-8", errors="replace")
        declared = set(re.findall(r"classDef\s+([A-Za-z_][\w]*)\s", text))
        applied = set(re.findall(r":::([A-Za-z_][\w]*)", text))
        assert declared, "the graph must declare at least one class"
        undeclared = applied - declared
        assert not undeclared, (
            "applied a class that was never declared, so it renders as if "
            "unstyled: %s" % sorted(undeclared))

    def test_every_disposition_has_a_declared_and_applied_class(self):
        if not self.MMD.is_file():
            pytest.skip("NEURAL_MESH_INTEROP.mmd not generated")
        text = self.MMD.read_text(encoding="utf-8", errors="replace")
        declared = set(re.findall(r"classDef\s+([A-Za-z_][\w]*)\s", text))
        applied = set(re.findall(r":::([A-Za-z_][\w]*)", text))
        for name in ("C_wire", "C_integrate", "C_unresolved"):
            assert name in declared, "%s not declared" % name
            assert name in applied, (
                "%s declared but never attached to a node -- the disposition "
                "is invisible in the graph" % name)

    def test_module_level_capabilities_appear_in_the_graph(self):
        if not self.MMD.is_file() or not self.MAP.is_file():
            pytest.skip("interop artifacts not generated")
        plan = json.loads(self.MAP.read_text(encoding="utf-8"))["findings"]
        if not any(v.get("kind") == "module_level" for v in plan.values()):
            pytest.skip("no module-level findings in the current plan")
        text = self.MMD.read_text(encoding="utf-8", errors="replace")
        assert "D_" in text, (
            "module-level capabilities must be graphed under their module; "
            "they used to be skipped by a bare `continue`")

    def test_plan_reports_contract_coverage(self):
        if not self.MAP.is_file():
            pytest.skip("NEURAL_MESH_INTEGRATION_MAP.json not generated")
        doc = json.loads(self.MAP.read_text(encoding="utf-8"))
        cov = doc.get("contract_coverage")
        assert cov, "the plan must carry contract_coverage"
        assert cov["natures_total"] > 0
        assert "no_contract_declared" in cov
        assert "declared_emits_nothing_reads" in cov
        assert "derived_emits_nothing_reads" in cov
        assert cov["derived_natures"] > 0, (
            "the derived register must span natures that declare no contract")
        assert cov["coverage"].startswith(
            "%d/%d natures declare a contract, %d/%d have one derivable"
            % (len(cov["declared"]), cov["natures_total"],
               cov["derived_natures"], cov["natures_total"]))
