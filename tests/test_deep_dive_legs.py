"""The render-ratchet leg: absence must never read as a pass.

The leg exists so the clip gate cannot be forgotten, and the failure mode it is
most likely to have is the one every neglected gate has -- a host with no clips
reporting `ok` because there was nothing left to disagree with. These four
cases pin that boundary: off, unrecorded, recorded-but-absent, and the negative
control that a tool which could not run is `error`, never clean.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import deep_dive as dd  # noqa: E402


@pytest.fixture()
def tree(tmp_path, monkeypatch):
    """A repository-shaped directory, so nothing here touches the real logs."""
    monkeypatch.setattr(dd, "ROOT", tmp_path)
    (tmp_path / "logs").mkdir()
    return tmp_path


def _settings(monkeypatch, ratchet=True):
    monkeypatch.setattr(dd, "setting",
                        lambda key, fallback: ratchet if key == "render_gate.ratchet"
                        else fallback)


def test_disabled_knob_is_skipped_and_names_itself(tree, monkeypatch):
    _settings(monkeypatch, ratchet=False)
    out = dd.leg_render_ratchet(None)
    assert out["status"] == "skipped"
    assert "render_gate.ratchet=false" in out["detail"]


def test_no_baseline_is_skipped_not_clean(tree, monkeypatch):
    _settings(monkeypatch)
    out = dd.leg_render_ratchet(None)
    assert out["status"] == "skipped"
    assert "nothing recorded" in out["detail"]


def test_recorded_clips_absent_from_this_host_are_skipped(tree, monkeypatch):
    _settings(monkeypatch)
    (tree / "logs" / "render_gate_baseline.json").write_text(
        json.dumps({"C:/nowhere/one.mp4": {"frames": 300}}), encoding="utf-8")
    out = dd.leg_render_ratchet(None)
    assert out["status"] == "skipped"
    assert "1 clip(s) recorded, 0 present" in out["detail"]


def test_a_ratchet_that_could_not_run_is_error_not_ok(tree, monkeypatch):
    """exit 2 means nothing was audited, which is the one answer that is not a pass."""
    _settings(monkeypatch)
    clip = tree / "fake.mp4"
    clip.write_bytes(b"not a video")
    (tree / "logs" / "render_gate_baseline.json").write_text(
        json.dumps({str(clip): {"frames": 300}}), encoding="utf-8")
    (tree / "tools").mkdir()
    (tree / "tools" / "render_gate.py").write_text("import sys\nsys.exit(2)\n",
                                                  encoding="utf-8")
    out = dd.leg_render_ratchet(None)
    assert out["status"] == "error"
    assert "1 of 1 recorded clip(s) present" in out["detail"]
