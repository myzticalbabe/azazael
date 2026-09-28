"""Tests for scripts/commit_gate.py -- pure bulk-detection logic only.

No git, no DB, no network: evaluate()/is_generated() are pure functions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import commit_gate as cg


def test_small_changeset_passes():
    rows = [(5, 2, "src/a.py"), (10, 0, "src/b.py")]
    assert cg.evaluate(rows, 150, 8) == []


def test_big_file_blocked():
    rows = [(200, 60, "src/CORE/local_memory.py")]
    problems = cg.evaluate(rows, 150, 8)
    assert len(problems) == 1
    assert "local_memory.py" in problems[0]


def test_too_many_files_blocked():
    rows = [(1, 1, "f%d.py" % i) for i in range(9)]
    problems = cg.evaluate(rows, 150, 8)
    assert any("9 staged files" in p for p in problems)


def test_binary_counted_not_measured():
    rows = [(-1, -1, "asset.ppm")]
    assert cg.evaluate(rows, 150, 8) == []


def test_new_files_exempt_from_line_cap():
    rows = [(400, 0, "research/NEW_DESIGN.md")]
    # Untracked-origin unknown: flagged (created set not consulted).
    assert cg.evaluate(rows, 150, 8) != []
    assert cg.evaluate(rows, 150, 8, created=set()) != []
    assert cg.evaluate(rows, 150, 8,
                       created={"research/NEW_DESIGN.md"}) == []


def test_new_files_still_count_toward_file_tally():
    rows = [(-1, -1, "n%d.bin" % i) for i in range(9)]
    assert any("9 staged files" in p for p in cg.evaluate(rows, 150, 8))


def test_generated_classification():
    assert cg.is_generated("output/matrix_frames/frame_1.ppm")
    assert cg.is_generated("graphify-out/2026-09-28/graph.json")
    assert cg.is_generated("dashboard/monitor_x.html")
    assert not cg.is_generated("scripts/chain_controller.py")
    assert not cg.is_generated("src/CORE/local_memory.py")
