# coding: utf-8
"""A receipt clears the staleness leg only while it describes this tree.

Why this exists (2026-11-16)
---------------------------
``graphify update`` compares topology first (watch.py:2081-2103) and, when
nothing structural changed, returns BEFORE writing; ``built_at_commit`` is
written only by ``export.to_json`` (export.py:411). A commit that touches
``src/`` data alone therefore leaves the gate's only evidence frozen at the
older commit, and the gate stays red with a remedy that cannot execute -- while
the git range's changed files contain no code at all.

The fix is an evidence receipt, and evidence is exactly the kind of thing that
gets weakened later by someone in a hurry. So this file pins both directions:

* a receipt minted at HEAD, for this build and these store bytes, PASSES;
* a missing receipt, another HEAD, another build commit, or a store that moved
  since the receipt all FAIL -- the leg must still go red on real drift.

Run:
    python -m pytest tests/test_codegraph_freshness_receipt.py -q
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.env  # type: ignore[import-not-found]

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BUILT = "4b072b40" + "0" * 32
HEAD = "5445cae3" + "0" * 32
OTHER = "3c8ef5c4" + "0" * 32
CHANGED = ["src/PSYCHE/data/female_needs_hyperedges.json"]
NO_CHANGE = "No code-graph topology changes detected; outputs left untouched."


def _freshness():
    from tools import graphify_freshness

    return graphify_freshness


def _gate():
    from tools import mcp_startup_gate

    return mcp_startup_gate


@pytest.fixture()
def store(tmp_path):
    path = tmp_path / "graphify-out" / "graph.json"
    path.parent.mkdir()
    path.write_text(json.dumps({"nodes": [], "built_at_commit": BUILT}), encoding="utf-8")
    return path


def _write_receipt(store, **over):
    doc = {
        "version": 1,
        "head": HEAD,
        "built_at_commit": BUILT,
        "graph_sha256": hashlib.sha256(store.read_bytes()).hexdigest(),
        "evidence": NO_CHANGE,
    }
    doc.update(over)
    (store.parent / "freshness.json").write_text(json.dumps(doc), encoding="utf-8")
    return doc


# ── the judgement itself ───────────────────────────────────────────


def test_receipt_accepts_head_build_and_bytes_that_agree(store):
    _write_receipt(store)
    fresh, why = _freshness().receipt_verdict(store, HEAD, BUILT)
    assert fresh, why


def test_absence_is_reported_as_absence_not_staleness(store):
    fresh, why = _freshness().receipt_verdict(store, HEAD, BUILT)
    assert fresh is False
    assert "no freshness receipt" in why


def test_receipt_for_another_head_is_refused(store):
    _write_receipt(store, head=OTHER)
    fresh, why = _freshness().receipt_verdict(store, HEAD, BUILT)
    assert fresh is False
    assert "HEAD is" in why


def test_receipt_for_another_build_commit_is_refused(store):
    _write_receipt(store, built_at_commit=OTHER)
    fresh, why = _freshness().receipt_verdict(store, HEAD, BUILT)
    assert fresh is False
    assert "store records" in why


def test_store_bytes_moving_after_the_receipt_is_refused(store):
    _write_receipt(store)
    store.write_text(json.dumps({"nodes": [1], "built_at_commit": BUILT}), encoding="utf-8")
    fresh, why = _freshness().receipt_verdict(store, HEAD, BUILT)
    assert fresh is False
    assert "store changed since the receipt" in why


def test_unreadable_receipt_is_not_a_pass(store):
    (store.parent / "freshness.json").write_text("{not json", encoding="utf-8")
    fresh, why = _freshness().receipt_verdict(store, HEAD, BUILT)
    assert fresh is False
    assert "unreadable" in why


# ── the gate's branch ──────────────────────────────────────────────


def _gate_at(monkeypatch, store, tmp_path):
    """Point the staleness leg at a temp store whose HEAD is one commit ahead."""
    gate = _gate()
    conf = tmp_path / "mcp.json"
    conf.write_text(
        json.dumps({"mcpServers": {"codegraph": {
            "command": "codegraph", "args": ["--graph", str(store)]}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "CODEGRAPH_STORE", store)
    monkeypatch.setattr(gate, "KILO_CONF", conf)
    monkeypatch.setattr(gate, "FREEBUFF_CONF", tmp_path / "absent-freebuff.json")
    monkeypatch.setattr(gate, "OPENCODE_CONF", tmp_path / "absent-opencode.json")
    monkeypatch.setattr(gate, "OPENCODE_KILO_CONF", tmp_path / "absent-opencode-kilo.json")
    monkeypatch.setattr(gate, "_graph_built_commit", lambda path: (BUILT, ""))

    def fake_git(root, *args):
        if args[:2] == ("rev-parse", "HEAD"):
            return 0, HEAD
        if args and args[0] == "cat-file":
            return 0, ""
        if args and args[0] == "diff":
            return 0, "\n".join(CHANGED)
        return 1, ""

    monkeypatch.setattr(gate, "_git", fake_git)
    return gate


def test_gate_passes_on_a_receipt_minted_at_head(monkeypatch, store, tmp_path):
    _write_receipt(store)
    gate = _gate_at(monkeypatch, store, tmp_path)
    status, detail, _remedy = gate.check_codegraph_freshness()
    assert status == gate.PASS, detail
    assert "no topology change" in detail


def test_gate_fails_without_a_receipt(monkeypatch, store, tmp_path):
    gate = _gate_at(monkeypatch, store, tmp_path)
    status, detail, remedy = gate.check_codegraph_freshness()
    assert status == gate.FAIL, detail
    assert "no freshness receipt" in detail
    assert "graphify_freshness.py --stamp" in remedy
    assert "graphify_bin.sh update src" in remedy


def test_gate_fails_when_the_receipt_names_another_head(monkeypatch, store, tmp_path):
    _write_receipt(store, head=OTHER)
    gate = _gate_at(monkeypatch, store, tmp_path)
    status, detail, _remedy = gate.check_codegraph_freshness()
    assert status == gate.FAIL, detail
    assert "HEAD is" in detail


def test_gate_fails_when_the_store_moved_since_the_receipt(monkeypatch, store, tmp_path):
    _write_receipt(store)
    store.write_text(json.dumps({"nodes": [1], "built_at_commit": BUILT}), encoding="utf-8")
    gate = _gate_at(monkeypatch, store, tmp_path)
    status, detail, _remedy = gate.check_codegraph_freshness()
    assert status == gate.FAIL, detail
    assert "store changed since the receipt" in detail


# ── the minter refuses to mint on evidence it does not have ────────


def _stamp_env(monkeypatch, head_after=None):
    fresh = _freshness()
    monkeypatch.setattr(fresh, "read_built_commit", lambda path: BUILT)
    monkeypatch.setattr(fresh, "changed_under_src", lambda built, head: list(CHANGED))
    calls = {"n": 0}

    def fake_git(*args):
        calls["n"] += 1
        if calls["n"] == 1:
            return 0, HEAD
        return 0, head_after or HEAD

    monkeypatch.setattr(fresh, "_git", fake_git)
    return fresh


def test_stamp_refuses_when_update_did_not_report_no_change(monkeypatch, store):
    fresh = _stamp_env(monkeypatch)
    monkeypatch.setattr(
        fresh, "run_update",
        lambda timeout=600: (0, "Extracted 120 nodes; wrote graph.json."),
    )
    with pytest.raises(fresh.ProofError):
        fresh.stamp(store)
    assert not (store.parent / "freshness.json").exists()


def test_stamp_refuses_when_update_fails(monkeypatch, store):
    fresh = _stamp_env(monkeypatch)
    monkeypatch.setattr(fresh, "run_update", lambda timeout=600: (1, "ImportError: boom"))
    with pytest.raises(fresh.ProofError) as excinfo:
        fresh.stamp(store)
    assert "exited 1" in str(excinfo.value)
    assert not (store.parent / "freshness.json").exists()


def test_stamp_refuses_when_head_moved_during_the_run(monkeypatch, store):
    fresh = _stamp_env(monkeypatch, head_after=OTHER)
    monkeypatch.setattr(fresh, "run_update", lambda timeout=600: (0, NO_CHANGE))
    with pytest.raises(fresh.ProofError) as excinfo:
        fresh.stamp(store)
    assert "HEAD moved" in str(excinfo.value)
    assert not (store.parent / "freshness.json").exists()


def test_stamp_writes_a_receipt_the_gate_then_accepts(monkeypatch, store):
    fresh = _stamp_env(monkeypatch)
    monkeypatch.setattr(fresh, "run_update", lambda timeout=600: (0, NO_CHANGE))
    doc = fresh.stamp(store)
    assert doc["stamped"] is True, doc
    written = json.loads((store.parent / "freshness.json").read_text(encoding="utf-8"))
    assert written["head"] == HEAD
    assert written["built_at_commit"] == BUILT
    assert written["graph_sha256"] == hashlib.sha256(store.read_bytes()).hexdigest()
    fresh_now, why = fresh.receipt_verdict(store, HEAD, BUILT)
    assert fresh_now, why
