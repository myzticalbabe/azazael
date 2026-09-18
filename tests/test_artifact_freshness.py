# coding: utf-8
"""Tests for tools/artifact_freshness.py.

The guard exists because a stale map gets acted on. So it is tested in both
directions: it must FLAG an artifact older than its source, and it must NOT
flag one that is current -- a guard that always fails is as useless as one that
never does, and only the flagging direction is easy to get right by accident.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import artifact_freshness as af  # noqa: E402


def _touch(path: Path, when: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    os.utime(path, (when, when))


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    _touch(root / "src" / "a.py", time.time() - 1000)
    return root


REG = (("out.json", ("src",), ("*.py",)),)


def test_missing_artifact_is_reported(tmp_path):
    root = _repo(tmp_path)
    rows = af.audit(root, REG)
    assert rows[0]["exists"] is False
    assert rows[0]["stale"] is True
    assert rows[0]["reason"] == "missing"


def test_fresh_artifact_is_not_flagged(tmp_path):
    """The direction a guard can pass vacuously if it only ever checks 'exists'."""
    root = _repo(tmp_path)
    _touch(root / "out.json", time.time())
    rows = af.audit(root, REG)
    assert rows[0]["stale"] is False, rows
    assert rows[0]["newer_count"] == 0


def test_artifact_older_than_source_is_flagged_with_evidence(tmp_path):
    root = _repo(tmp_path)
    _touch(root / "out.json", time.time() - 500)
    _touch(root / "src" / "b.py", time.time() - 10)  # source changed after build
    rows = af.audit(root, REG)
    assert rows[0]["stale"] is True
    assert rows[0]["newer_count"] == 1
    assert rows[0]["newer"] == ["src/b.py"], rows[0]


def test_graph_report_mismatch_detected(tmp_path):
    """A fresh report describing a re-derived graph is not a freshness problem.

    graphify's shrink guard can refuse the graph.json write while the report is
    regenerated from the re-derived graph, leaving both files new and
    disagreeing. mtime checks cannot see it; this is why the guard reads content.
    """
    root = _repo(tmp_path)
    g = root / "graphify-out" / "graph.json"
    g.parent.mkdir(parents=True, exist_ok=True)
    g.write_text(json.dumps({"nodes": [{"id": "a"}], "edges": []}), encoding="utf-8")
    os.utime(g, (time.time() - 10, time.time() - 10))
    _touch(root / "graphify-out" / "GRAPH_REPORT.md", time.time())
    out = af.graph_report_mismatch(root)
    assert out["checked"] is True
    assert out["clustered"] is False
    assert out["mismatch"] is True
    assert "no communities" in out["reason"]


def test_graph_report_consistent_when_clustered(tmp_path):
    root = _repo(tmp_path)
    g = root / "graphify-out" / "graph.json"
    g.parent.mkdir(parents=True, exist_ok=True)
    g.write_text(json.dumps({"nodes": [{"id": "a", "community": 0}], "edges": []}),
                 encoding="utf-8")
    os.utime(g, (time.time() - 10, time.time() - 10))
    _touch(root / "graphify-out" / "GRAPH_REPORT.md", time.time())
    out = af.graph_report_mismatch(root)
    assert out["clustered"] is True
    assert out["mismatch"] is False


def test_main_exit_codes(tmp_path, capsys):
    """Both directions, against the substituted registry.

    The real REGISTRY is not used: in a fixture repo none of its artifacts
    exist, so every row is legitimately stale and the exit code would be 1 for
    a reason unrelated to what this test is checking.
    """
    root = _repo(tmp_path)
    _touch(root / "out.json", time.time() - 500)
    _touch(root / "src" / "b.py", time.time() - 10)
    assert af.main(["--json", "--root", str(root)], REG) == 1
    _touch(root / "out.json", time.time())
    assert af.main(["--json", "--root", str(root)], REG) == 0


def test_missing_real_artifact_is_stale_by_default(tmp_path):
    """The default registry: a repo with no artifacts at all must FAIL.

    This is the direction that matters operationally -- an absent census is
    not 'fresh', and a guard that treated 'missing' as 'nothing to report'
    would pass on a checkout that had never been audited.
    """
    root = _repo(tmp_path)
    assert af.main(["--json", "--root", str(root)]) == 1
    rows = af.audit(root)
    assert rows and all(r["stale"] for r in rows), rows
