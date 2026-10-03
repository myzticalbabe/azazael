# coding: utf-8
"""Tests for `tools/anti_pattern_gate.py` — the anti-pattern ratchet.

Why these tests exist
---------------------
`reports/ERROR_LESSON_AUDIT_2026-10-03.md` measured the anti-pattern cluster as
"MECHANIZED BUT NOT ENFORCED": the scanner was built, the hook was written, and
neither was wired to anything that blocks. The failure mode of a quality gate is
never "it crashes" -- it is "it reports OK". So these tests pin the ways this
one could reassure while wrong:

* a count INCREASE must fail,
* a NEW category must fail even if the total is unchanged,
* a count DECREASE must NOT fail (driving a class to zero is the goal),
* a missing or scheme-mismatched baseline must not read as "nothing is wrong",
* and a narrowed run must not silently overwrite the whole-tree baseline.

The scanner is injected rather than invoked: a real run is ~5 s and would make
this file's result depend on the tree it is measuring. One test does run the
real scanner over a temp dir, as the positive/negative control for the injected
ones -- a gate proven only against a fake scanner proves nothing about the real
one.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import anti_pattern_gate as gate  # noqa: E402


# ── helpers ──────────────────────────────────────────────────────────────


def _fake_scan(counts: dict, files: int = 10):
    """Return a replacement for gate.scan yielding fixed counts."""
    def _scan(target: str):
        return Counter(counts), files
    return _scan


def _write_baseline(path: Path, counts: dict, scheme: str = gate.IDENTITY_SCHEME):
    path.write_text(json.dumps({
        "recorded_at": "2026-10-03T00:00:00+00:00",
        "identity_scheme": scheme,
        "category_counts": counts,
    }), encoding="utf-8")


@pytest.fixture
def base_file(tmp_path):
    return tmp_path / "anti_pattern_baseline.json"


# ── the ratchet decision ─────────────────────────────────────────────────


class TestCheck:
    def test_equal_counts_pass(self, base_file, monkeypatch, capsys):
        _write_baseline(base_file, {"unicode_emoji": 5, "os_system": 0})
        monkeypatch.setattr(gate, "scan", _fake_scan({"unicode_emoji": 5}))
        rc = gate.cmd_check("src", base_file)
        assert rc == 0
        assert "OK: no anti-pattern regressions" in capsys.readouterr().out

    def test_increase_fails(self, base_file, monkeypatch, capsys):
        _write_baseline(base_file, {"unicode_emoji": 5})
        monkeypatch.setattr(gate, "scan", _fake_scan({"unicode_emoji": 6}))
        rc = gate.cmd_check("src", base_file)
        assert rc == 1
        out = capsys.readouterr().out
        assert "REGRESSIONS" in out and "5 ->     6" in out

    def test_new_category_fails_even_if_total_equal(self, base_file, monkeypatch,
                                                    capsys):
        """A swap is a regression: one class down, a NEW class appears."""
        _write_baseline(base_file, {"unicode_emoji": 10})
        monkeypatch.setattr(gate, "scan",
                            _fake_scan({"unicode_emoji": 9, "os_system": 1}))
        rc = gate.cmd_check("src", base_file)
        assert rc == 1
        out = capsys.readouterr().out
        assert "NEW category" in out and "os_system" in out

    def test_decrease_does_not_fail(self, base_file, monkeypatch, capsys):
        _write_baseline(base_file, {"unicode_emoji": 10, "os_system": 0})
        monkeypatch.setattr(gate, "scan", _fake_scan({"unicode_emoji": 3}))
        rc = gate.cmd_check("src", base_file)
        assert rc == 0
        out = capsys.readouterr().out
        assert "improved" in out
        assert "cleared" in out and "os_system" in out

    def test_category_at_zero_recorded_and_stays_zero(self, base_file, monkeypatch):
        """The three driven-to-zero categories must not re-appear as NEW."""
        _write_baseline(base_file, {"t_string": 0, "os_system": 0,
                                    "cls_new_factory": 0, "unicode_emoji": 5})
        monkeypatch.setattr(gate, "scan", _fake_scan({"unicode_emoji": 5}))
        assert gate.cmd_check("src", base_file) == 0


# ── the baseline must not be trusted blindly ─────────────────────────────


class TestBaselineIntegrity:
    def test_missing_baseline_is_not_a_pass(self, tmp_path):
        with pytest.raises(SystemExit) as exc:
            gate.cmd_check("src", tmp_path / "does_not_exist.json")
        assert exc.value.code == 2

    def test_scheme_mismatch_is_refused(self, base_file, monkeypatch, capsys):
        """Counts are not comparable across schemes; refuse, do not diff."""
        _write_baseline(base_file, {"unicode_emoji": 5}, scheme="old-scheme-v0")
        monkeypatch.setattr(gate, "scan", _fake_scan({"unicode_emoji": 5}))
        rc = gate.cmd_check("src", base_file)
        assert rc == 2
        assert "identity_scheme" in capsys.readouterr().err

    def test_narrowed_baseline_redirected_to_partial(self, tmp_path):
        """`--baseline --dir src/CORE` must not overwrite the whole-tree file."""
        out = gate._resolve_out(None, narrowed=True, kind="baseline")
        assert out.name == "anti_pattern_baseline.partial.json"
        assert out != gate.BASELINE

    def test_whole_tree_baseline_uses_default_path(self):
        out = gate._resolve_out(None, narrowed=False, kind="baseline")
        assert out == gate.BASELINE

    def test_explicit_path_is_obeyed(self, tmp_path):
        explicit = tmp_path / "custom.json"
        assert gate._resolve_out(str(explicit), narrowed=True,
                                 kind="baseline") == explicit.resolve()


# ── the committed baseline must describe the committed tree ──────────────


class TestCommittedBaseline:
    def test_baseline_exists_and_uses_current_scheme(self):
        assert gate.BASELINE.exists(), (
            "logs/anti_pattern_baseline.json is missing -- the hook's ratchet "
            "cannot run. Record it: python tools/anti_pattern_gate.py --baseline")
        data = json.loads(gate.BASELINE.read_text(encoding="utf-8"))
        assert data["identity_scheme"] == gate.IDENTITY_SCHEME
        assert data["target"] == "src"
        assert data["category_counts"], "baseline recorded no categories"

    def test_baseline_agrees_with_a_live_scan(self):
        """The committed baseline must equal a real scan of the live src/ tree.

        This is the positive/negative control for every injected-scanner test
        above: it proves the instrument the gate wraps actually produces the
        numbers the baseline claims. If this fails, the tree grew or shrank and
        `--baseline` must be re-run deliberately.
        """
        data = json.loads(gate.BASELINE.read_text(encoding="utf-8"))
        live, files = gate.scan("src")
        assert dict(sorted(live.items())) == data["category_counts"], (
            "live anti-pattern counts differ from logs/anti_pattern_baseline.json; "
            "re-run: python tools/anti_pattern_gate.py --baseline")
        assert files == data["files_scanned"]


# ── the scanner itself (positive + negative control) ─────────────────────


class TestRealScanner:
    def test_clean_file_has_no_findings(self, tmp_path):
        """A clean file must scan clean -- the negative control."""
        (tmp_path / "clean.py").write_text("import os\n\n\n"
                                           "def f() -> int:\n    return 1\n",
                                           encoding="utf-8")
        counts, files = gate.scan(str(tmp_path))
        assert files == 1
        assert not counts

    def test_emoji_file_is_detected(self, tmp_path):
        """The positive control: a real emoji must be counted."""
        (tmp_path / "bad.py").write_text('X = "\U0001F600"\n', encoding="utf-8")
        counts, _files = gate.scan(str(tmp_path))
        assert counts.get("unicode_emoji", 0) >= 1
