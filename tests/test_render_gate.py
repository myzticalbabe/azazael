# coding: utf-8
"""Tests for `tools/render_gate.py` -- the gate the five savers did not have.

Why this file exists
--------------------
Every check this tool performs was done by hand, five times, on 2026-11-16: the
frame count, the rate, the duration, and whether a decoded frame was the saver's
colour or a black canvas. Two hand-checks found real defects. A hand-check that
found a defect once is not a control until something fails when the defect
returns.

The controls here are the two defect classes that actually happened:

* A saver whose resize handler assigns `canvas.width` without the same-box guard
  renders 300 black frames. `test_missing_guard_fails_the_contract` is that bug
  as a fixture, and it must FAIL -- a contract check that passes everything is
  the class of instrument this tree keeps paying for.
* A clip that is 300 frames of black passed every count-based check ever run on
  it. `test_black_frame_fails_even_when_counts_are_right` pins counts correct
  and colour black, so only the colour check can fail.

Nothing here needs ffmpeg, node or a browser: the measured faces take their
readings as dicts, which is what makes them testable at all.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import render_gate as rg  # noqa: E402

GOOD_SAVER = """<!doctype html>
<script>
(function () {
  let lastMs = null;
  function resize() {
    const bw = Math.floor(window.innerWidth);
    if (bw === cv.width) return;
    cv.width = bw;
  }
  const captureMode = !!window.__capture;
  window.__TOTAL = 10000;
  window.__step = function (ms) {
    lastMs = ms;
    return new Promise(function (resolve) { resolve(ms); });
  };
  window.addEventListener('resize', function () {
    resize();
    if (captureMode && lastMs !== null) frame(lastMs);
  });
})();
</script>
"""

# The real defect: assignment with no comparison first. Every captured frame was
# wiped a millisecond before it was read.
NO_GUARD_SAVER = GOOD_SAVER.replace(
    "    const bw = Math.floor(window.innerWidth);\n    if (bw === cv.width) return;\n",
    "    const bw = Math.floor(window.innerWidth);\n")

EXPECT = {"frames": 300, "fps": 30.0, "seconds": 10.0,
          "size": "1920x1080", "min_luma": 8.0, "palette": None, "tol": 45}


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


# --------------------------------------------------------------------------- #
# contract
# --------------------------------------------------------------------------- #
def test_contract_passes_a_complete_saver():
    checks = rg.check_contract(GOOD_SAVER)
    assert [c["name"] for c in checks if not c["ok"]] == []
    assert all(c["line"] for c in checks)


def test_missing_guard_fails_the_contract():
    checks = {c["name"]: c for c in rg.check_contract(NO_GUARD_SAVER)}
    assert checks["same-box resize guard"]["ok"] is False
    # and the other four points still pass, so the finding names one thing
    others = [n for n, c in checks.items() if n != "same-box resize guard"]
    assert all(checks[n]["ok"] for n in others)


def test_contract_cli_exit_codes(tmp_path):
    good = _write(tmp_path, "good.html", GOOD_SAVER)
    bad = _write(tmp_path, "bad.html", NO_GUARD_SAVER)
    assert rg.main(["contract", str(good)]) == rg.EXIT_OK
    assert rg.main(["contract", str(bad)]) == rg.EXIT_FINDING
    assert rg.main(["contract", str(tmp_path / "absent.html")]) == rg.EXIT_CANNOT


# --------------------------------------------------------------------------- #
# readings
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("raw,want", [
    ("30/1", 30.0), ("30000/1001", 30000 / 1001), ("25", 25.0),
    ("0/0", None), ("", None), ("abc", None), ("30/", None),
])
def test_parse_rate(raw, want):
    got = rg.parse_rate(raw)
    if want is None:
        assert got is None
    else:
        assert got == pytest.approx(want)


def test_black_frame_fails_even_when_counts_are_right():
    readings = {"frames": 300, "fps": 30.0, "seconds": 10.0,
                "size": "1920x1080", "rgb": (2, 0, 2)}
    checks = {c["name"]: c["ok"] for c in rg.evaluate(readings, EXPECT)}
    assert checks["frames"] and checks["fps"] and checks["seconds"]
    assert checks["not black"] is False


def test_good_frame_passes_and_palette_tolerance_is_enforced():
    good = {"frames": 300, "fps": 30.0, "seconds": 10.0,
            "size": "1920x1080", "rgb": (140, 38, 16)}
    expect = dict(EXPECT, palette=(136, 34, 14), tol=10)
    assert all(c["ok"] for c in rg.evaluate(good, expect))

    # 3 counts off is inside tol; 40 off is not
    near = dict(good, rgb=(139, 41, 19))
    assert all(c["ok"] for c in rg.evaluate(near, expect))
    far = dict(good, rgb=(90, 38, 16))
    assert not all(c["ok"] for c in rg.evaluate(far, expect))


def test_wrong_frame_count_is_named():
    readings = {"frames": 150, "fps": 30.0, "seconds": 5.0,
                "size": "1920x1080", "rgb": (140, 38, 16)}
    failed = [c["name"] for c in rg.evaluate(readings, EXPECT) if not c["ok"]]
    assert set(failed) == {"frames", "seconds"}


def test_verify_cannot_run_without_the_clip(tmp_path):
    assert rg.main(["verify", str(tmp_path / "nope.mp4")]) == rg.EXIT_CANNOT


# --------------------------------------------------------------------------- #
# pilot
# --------------------------------------------------------------------------- #
PILOT = {"html": "x.html", "total_timeline_ms": 10000, "fps": 30,
         "planned_frames": 300, "ms_per_frame": 39175.0, "projected_s": 11752.5,
         "contract": {"total": True, "step": True, "draw": False}}


def test_pilot_flags_a_multihour_render_before_it_starts():
    checks = {c["name"]: c for c in rg.judge_pilot(PILOT, 1800, 8.0, (17, 5, 30))}
    assert checks["projected <= budget"]["ok"] is False
    assert checks["step hook (live)"]["ok"] is True
    assert checks["first frame has pixels"]["ok"] is True


def test_pilot_flags_a_black_first_frame():
    checks = {c["name"]: c for c in rg.judge_pilot(PILOT, None, 8.0, (2, 0, 2))}
    assert checks["first frame has pixels"]["ok"] is False
    assert "projected <= budget" not in checks


def test_pilot_without_a_measured_sample_is_not_a_pass():
    checks = {c["name"]: c for c in rg.judge_pilot(PILOT, 1800, 8.0, None)}
    assert checks["first frame has pixels"]["ok"] is False


def test_pilot_reports_missing_step_hook():
    payload = dict(PILOT, contract={"total": True, "step": False, "draw": True})
    checks = {c["name"]: c for c in rg.judge_pilot(payload, None, 8.0, (17, 5, 30))}
    assert checks["step hook (live)"]["ok"] is False


# The 2026-11-16 defect: the driver never asked for a GPU, so headless Chrome
# rasterized on SwiftShader and every projection was 31.5x the real job. A
# projection measured on the wrong renderer must not read as a passing budget.
def test_pilot_fails_a_projection_measured_on_software_raster():
    payload = dict(PILOT, projected_s=300.0, software_raster=True,
                   renderer="ANGLE (Google, Vulkan ... SwiftShader Device)")
    checks = {c["name"]: c for c in rg.judge_pilot(payload, 1800, 8.0, (17, 5, 30))}
    assert checks["projected <= budget"]["ok"] is True
    assert checks["hardware raster"]["ok"] is False, "a software projection is not this job"
    assert "SwiftShader" in str(checks["hardware raster"]["got"])


def test_pilot_hardware_raster_is_recorded_and_passes():
    payload = dict(PILOT, projected_s=112.8, software_raster=False,
                   renderer="ANGLE (Intel, Intel(R) Arc(TM) 140T GPU Direct3D11)")
    checks = {c["name"]: c for c in rg.judge_pilot(payload, 1800, 8.0, (17, 5, 30))}
    assert checks["hardware raster"]["ok"] is True
    assert "Intel" in str(checks["hardware raster"]["got"])


def test_pilot_software_raster_can_be_waived_explicitly():
    payload = dict(PILOT, projected_s=300.0, software_raster=True, renderer="SwiftShader")
    checks = {c["name"]: c for c in rg.judge_pilot(
        payload, 1800, 8.0, (17, 5, 30), allow_software_raster=True)}
    assert checks["hardware raster"]["ok"] is True
    assert "waived" in str(checks["hardware raster"]["want"])


def test_a_payload_without_a_renderer_is_not_flagged_as_software():
    # Absence of the field is not evidence of software: driver versions that do
    # not report it must not fail the gate on a fact they never measured.
    checks = {c["name"]: c for c in rg.judge_pilot(PILOT, 1800, 8.0, (17, 5, 30))}
    assert "hardware raster" not in checks


# --------------------------------------------------------------------------- #
# ratchet
# --------------------------------------------------------------------------- #
def _reading(**over):
    base = {"frames": 300, "fps": 30.0, "seconds": 10.0, "size": "1920x1080",
            "rgb": [140, 38, 16]}
    base.update(over)
    return base


def test_ratchet_is_silent_when_nothing_moved():
    assert rg.compare_baseline({"a.mp4": _reading()}, {"a.mp4": _reading()}) == []


def test_ratchet_names_a_regenerated_clip():
    findings = rg.compare_baseline({"a.mp4": _reading()},
                                   {"a.mp4": _reading(frames=299)})
    assert [f["name"] for f in findings] == ["frames"]
    assert findings[0]["got"] == 299 and findings[0]["want"] == 300


def test_ratchet_names_a_colour_regression():
    findings = rg.compare_baseline({"a.mp4": _reading()},
                                   {"a.mp4": _reading(rgb=[2, 0, 2])})
    assert [f["name"] for f in findings] == ["colour"]
    assert findings[0]["ok"] is False


def test_ratchet_names_a_clip_it_has_never_seen():
    findings = rg.compare_baseline({}, {"fresh.mp4": _reading()})
    assert findings[0]["name"] == "new clip"


def test_ratchet_refuses_to_run_with_no_clip():
    assert rg.main(["ratchet"]) == rg.EXIT_CANNOT
