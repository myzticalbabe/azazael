"""Tests for tools/soul_fleet_scorecard.py -- no network, ever.

The scorecard binary is absent on this box, so the honest paths are:
absent binary -> skipped exit 0; non-http origin -> not-applicable;
canned payloads -> threshold math. A fake binary script covers the
runner contract without touching the network.
"""

import json
import subprocess

from tools.soul_fleet_scorecard import (
    find_binary,
    low_checks,
    main,
    origin_url,
    run_scorecard,
)

PAYLOAD = {
    "score": 6.5,
    "checks": [
        {"name": "Branch-Protection", "score": 8, "reason": "ok"},
        {"name": "Pinned-Dependencies", "score": 2, "reason": "unpinned"},
        {"name": "Token-Permissions", "score": 0, "reason": "broad"},
        {"name": "Maintained", "score": "n/a", "reason": "skipped-check"},
        {"check": "Legacy-Key", "score": 1, "reason": "old schema"},
    ],
}


def test_low_checks_threshold_math():
    lows = low_checks(PAYLOAD, 5)
    assert len(lows) == 3  # 2 name-keyed + 1 legacy check-keyed
    assert any("Pinned-Dependencies" in f for f in lows)
    assert any("Token-Permissions" in f for f in lows)
    assert any("Legacy-Key" in f for f in lows)
    assert low_checks(PAYLOAD, 0) == []
    assert low_checks({}, 5) == []


def test_absent_binary_skips_exit_0(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))  # empty dir: no binary
    assert find_binary() is None
    assert main(["--root", str(tmp_path)]) == 0


def test_non_http_origin_not_applicable(tmp_path):
    d = tmp_path / "fleet" / "d"
    d.mkdir(parents=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=d, capture_output=True,
                   timeout=60)
    assert origin_url(d) == ""  # no origin at all


def test_runner_reports_missing_binary(tmp_path):
    ok, payload = run_scorecard(str(tmp_path / "nope-xyz"), "http://x")
    assert ok is False and "error" in payload


def test_runner_reports_unparseable_output(tmp_path, monkeypatch):
    import subprocess as _sp

    class _Proc:
        returncode = 0
        stdout = "not json {"
        stderr = "boom"

    monkeypatch.setattr(_sp, "run", lambda *a, **k: _Proc())
    ok, payload = run_scorecard("scorecard", "http://x")
    assert ok is False and "unparseable" in payload["error"]


def test_bad_root_exit_2(tmp_path):
    assert main(["--root", str(tmp_path / "nope"),
                 "--binary", str(tmp_path / "nope")]) == 2
