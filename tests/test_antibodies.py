#!/usr/bin/env python3
"""Antibody shards: instance-derived detectors, evidence-gated lifecycle.

Covers routing (error namespace -> antibodies shard), probe execution,
generational recording, and the promotion rules that close the loop:
neutralized needs a passing seek, immune needs a streak, reinfection
reopens, backward skips are refused.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from SHARDS import antibodies
from SHARDS.antibodies import (antibody_status, promote_antibody, record_seek,
                               run_antibody)
from SHARDS.registry import SHARDS, route_shard


def _isolate(tmp_path, monkeypatch):
    store = tmp_path / "antibodies.json"
    monkeypatch.setattr(antibodies, "_STORE_PATH", store)
    return store


def test_registry_routes_error_tasks_to_antibodies():
    assert SHARDS["antibodies"]["langs"] == ["python"]
    assert SHARDS["antibodies"]["canonical"] == "python"
    assert route_shard("antibody seek for immune drift regression") == "antibodies"
    assert route_shard("stale sweep work golden mismatch") == "antibodies"


def test_unknown_antibody_is_structured():
    res = run_antibody("no-such-error")
    assert res["status"] == "unknown-antibody" and not res["ok"]
    assert not promote_antibody("no-such-error", "immune")["ok"]


def test_probes_pass_where_toolchains_exist():
    # Live seek on this box: work tier across toolchains + forced stale.
    # ran >= 1 guards against vacuous passes (python always runs).
    for name in ("seq-range-mismatch", "stale-table-routing"):
        res = run_antibody(name)
        assert res["ok"] and res["ran"] >= 1, res


def test_initial_status_is_seeking(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    st = antibody_status("seq-range-mismatch")
    assert st["ok"] and st["status"] == "seeking" and st["generations"] == []


def test_neutralized_requires_passing_seek(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    refused = promote_antibody("seq-range-mismatch", "neutralized")
    assert not refused["ok"] and "passing seek" in refused["error"]
    record_seek("seq-range-mismatch",
                {"ok": True, "instances": []})
    promoted = promote_antibody("seq-range-mismatch", "neutralized")
    assert promoted["ok"] and promoted["to"] == "neutralized"
    assert antibody_status("seq-range-mismatch")["status"] == "neutralized"


def test_immune_requires_streak_and_order(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    record_seek("stale-table-routing", {"ok": True, "instances": []})
    # Neutralized first: immune direct from seeking is refused.
    assert not promote_antibody("stale-table-routing", "immune")["ok"]
    assert promote_antibody("stale-table-routing", "neutralized")["ok"]
    # One passing seek is not a streak of three.
    assert not promote_antibody("stale-table-routing", "immune")["ok"]
    record_seek("stale-table-routing", {"ok": True, "instances": []})
    record_seek("stale-table-routing", {"ok": True, "instances": []})
    done = promote_antibody("stale-table-routing", "immune")
    assert done["ok"] and done["to"] == "immune"


def test_reinfection_reopens_and_backward_skip_refused(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    for _ in range(3):
        record_seek("stale-table-routing", {"ok": True, "instances": []})
    assert promote_antibody("stale-table-routing", "neutralized")["ok"]
    assert promote_antibody("stale-table-routing", "immune")["ok"]
    # Immune -> neutralized skips backward: refused.
    assert not promote_antibody("stale-table-routing", "neutralized")["ok"]
    # Reinfection reopens: any status -> seeking always allowed.
    record_seek("stale-table-routing",
                {"ok": False, "instances": ["_measured_order"]})
    reopened = promote_antibody("stale-table-routing", "seeking")
    assert reopened["ok"] and reopened["to"] == "seeking"
