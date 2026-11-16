"""test_ledger_blame.py -- Board-48985: push-range attribution, no triage pass.

Proves tools/ledger_blame.py annotates each failing row with owning
commit+lane and routes the block per lane. Git-dependent tests build a
throwaway repo; the board test posts to a scratch DB only (never the
live board).
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(
    os.environ.get(
        "LEDGER_BLAME_TOOLS", Path(__file__).resolve().parents[1] / "tools"
    )
)
sys.path.insert(0, str(TOOLS))

import attr_push_block  # noqa: E402
import ledger_blame  # noqa: E402


def test_extract_paths_basic():
    line = "[Ratchet] tools/mesh_function_preflight.py --check failed, see src/CORE/WORMS/x.py"
    assert ledger_blame.extract_paths(line) == [
        "tools/mesh_function_preflight.py",
        "src/CORE/WORMS/x.py",
    ]


def test_extract_paths_strips_linecol_and_quotes():
    line = "ERROR 'tools/foo.py:123:4', also \"docs/bar.md:7\", trailing:"
    assert ledger_blame.extract_paths(line) == ["tools/foo.py", "docs/bar.md"]


def test_extract_paths_dedupes_and_ignores_plain_text():
    line = "tools/a.py failed; tools/a.py failed again; nothing else here"
    assert ledger_blame.extract_paths(line) == ["tools/a.py"]


def test_extract_paths_catches_bare_wire_filename():
    line = "[Wire] NEURAL_MESH_WIRE_OR_CUT.json drift"
    assert ledger_blame.extract_paths(line) == ["NEURAL_MESH_WIRE_OR_CUT.json"]


def test_turf_owner_known_and_unknown():
    assert attr_push_block.turf_owner("tools/lane_forensics.py") == "freebuff"
    assert (
        attr_push_block.turf_owner("src/CORE/WORMS/expansion/servemesh/q.py")
        == "opencode"
    )
    assert attr_push_block.turf_owner("tools/something_new.py") == "UNKNOWN"


def _init_repo(path: Path) -> None:
    env = dict(
        os.environ,
        GIT_CONFIG_NOSYSTEM="1",
        HOME=str(path),
        GIT_AUTHOR_NAME="t",
        GIT_AUTHOR_EMAIL="t@t",
        GIT_COMMITTER_NAME="t",
        GIT_COMMITTER_EMAIL="t@t",
    )
    subprocess.run(["git", "init", "-q"], cwd=path, check=True, env=env, timeout=30)
    (path / "tools").mkdir()
    (path / "tools" / "lane_forensics.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True, env=env, timeout=30)
    subprocess.run(["git", "commit", "-qm", "lane commit subject"],
                   cwd=path, check=True, env=env, timeout=30)


def test_annotate_against_throwaway_repo(tmp_path, monkeypatch):
    if shutil.which("git") is None:
        pytest.skip("no git binary")
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    monkeypatch.setattr(attr_push_block, "REPO", str(repo))
    owner, commit = ledger_blame.annotate("tools/lane_forensics.py")
    assert owner == "freebuff"
    assert "lane commit subject" in commit


def test_parse_groups_and_renders():
    text = (
        "[Ratchet] tools/lane_forensics.py failed\n"
        "[Refs] src/CORE/WORMS/expansion/servemesh/q.py missing\n"
        "a context line with no path at all\n"
    )
    rows = ledger_blame.parse(text)
    assert len(rows) == 2
    assert rows[0]["gate"] == "Ratchet"
    assert rows[1]["gate"] == "Refs"
    groups = ledger_blame.group_by_lane(rows)
    assert set(groups) == {"freebuff", "opencode"}
    block = ledger_blame.render_block(groups)
    assert "lane.freebuff" in block and "lane.opencode" in block
    assert "tools/lane_forensics.py" in block


def test_render_unknown_names_toucher_not_lane():
    rows = [
        {"gate": "g", "line": "l", "path": "tools/brand_new.py",
         "owning_lane": "UNKNOWN", "owning_commit": "abc1234 2026-11-01 new"},
    ]
    block = ledger_blame.render_block(ledger_blame.group_by_lane(rows))
    assert "UNKNOWN" in block and "lane.UNKNOWN" not in block


def test_write_ledger(tmp_path):
    rows = [
        {"gate": "g", "line": "l", "path": "tools/x.py",
         "owning_lane": "freebuff", "owning_commit": "abc"},
    ]
    out = ledger_blame.write_ledger(rows, tmp_path / "lb.jsonl")
    rec = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert rec["path"] == "tools/x.py"
    assert "annotated_at" in rec and "head" in rec


def test_main_no_paths_exit_2(tmp_path):
    f = tmp_path / "nofail.txt"
    f.write_text("[Gate] all green, no paths here\n")
    rc = ledger_blame.main(
        ["--file", str(f), "--ledger", str(tmp_path / "lb.jsonl")])
    assert rc == 2


def test_main_happy_path_writes_ledger(tmp_path):
    f = tmp_path / "fail.txt"
    f.write_text("[Ratchet] tools/lane_forensics.py failed\n")
    rc = ledger_blame.main(
        ["--file", str(f), "--ledger", str(tmp_path / "lb.jsonl")])
    assert rc == 0
    rec = json.loads((tmp_path / "lb.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert rec["owning_lane"] == "freebuff"
    assert rec["path"] == "tools/lane_forensics.py"


def test_route_posts_to_scratch_board_only(tmp_path, monkeypatch):
    sys.path.insert(0, str(TOOLS.parent / "src"))
    import CORE.MemoryBus as _mb
    import CORE.LaneMessageBoard as _lb
    from CORE.LaneMessageBoard import LaneMessageBoard

    # Pin the board DB explicitly: module-level TELEMETRY_DB_PATH is fixed
    # by whichever test imported CORE first, so env alone is not enough.
    scratch = tmp_path / "telemetry_store.db"
    monkeypatch.setattr(_mb, "_MEMORYBUS_DB_PATH", scratch, raising=False)
    monkeypatch.setattr(_lb, "_MEMORYBUS_DB_PATH", scratch, raising=False)

    board = LaneMessageBoard(lane="freebuff")
    groups = {
        "opencode": [
            {"gate": "g", "line": "l tools/q.py", "path": "tools/q.py",
             "owning_lane": "opencode", "owning_commit": "c1"},
        ],
        "UNKNOWN": [
            {"gate": "g", "line": "l tools/zzz.py", "path": "tools/zzz.py",
             "owning_lane": "UNKNOWN", "owning_commit": "c2"},
        ],
    }
    posted = ledger_blame.post_deliveries(groups, board, source_lane="freebuff")
    assert len(posted) == 1  # UNKNOWN never posts
    con = sqlite3.connect(f"file:{tmp_path / 'telemetry_store.db'}?mode=ro", uri=True)
    topic, content = con.execute(
        "SELECT topic, content FROM memorybus_queue ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert topic == "lane.opencode.tasks"
    payload = json.loads(content)
    assert payload["task_id"].startswith("ledger-blame-")
    assert payload["source_lane"] == "freebuff"
    assert "tools/q.py" in payload["detail"]
