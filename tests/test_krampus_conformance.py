"""Tests for tools/krampus_conformance.py.

The tool's job is to prove three lane configs reach the KRAMPUS surface, so its
failure modes are all silent ones: an entry that reads fine but will not spawn, a
disabled entry counted as present, a probe that returns a count nobody can check.
Each of those has a test here that makes the checker FAIL.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import krampus_conformance as kc  # noqa: E402

FAKE_SERVER = '''
import json, sys
TOOLS = %(tools)r
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    if msg.get("method") == "initialize":
        print(json.dumps({"jsonrpc": "2.0", "id": msg.get("id"),
                          "result": {"protocolVersion": "2025-06-18",
                                     "capabilities": {},
                                     "serverInfo": {"name": "krampus"}}}), flush=True)
    elif msg.get("method") == "tools/list":
        print(json.dumps({"jsonrpc": "2.0", "id": msg.get("id"),
                          "result": {"tools": [{"name": t} for t in TOOLS]}}), flush=True)
'''

WANTED = ["krampus_members", "gamora_lilith"]


def _script(tmp_path: Path, tools) -> Path:
    path = tmp_path / "fake_krampus.py"
    path.write_text(FAKE_SERVER % {"tools": tools}, encoding="utf-8")
    return path


def _config(tmp_path: Path, entry: dict, name: str = "lane.jsonc") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps({"mcpServers": {"krampus": entry}}), encoding="utf-8")
    return path


def test_clean_lane_with_full_tools_is_ok(tmp_path):
    script = _script(tmp_path, WANTED)
    cfg = _config(tmp_path, {"type": "stdio",
                             "command": sys.executable, "args": [str(script)]})
    row = kc.check_lane(cfg, WANTED, probe=True)
    assert row["state"] == kc.OK, row
    assert row["tools"] == sorted(WANTED)


def test_missing_entry_is_a_gap_not_a_pass(tmp_path):
    cfg = tmp_path / "lane.jsonc"
    cfg.write_text(json.dumps({"mcpServers": {"other": {"command": sys.executable}}}),
                   encoding="utf-8")
    row = kc.check_lane(cfg, WANTED, probe=False)
    assert row["state"] == kc.MISSING


def test_disabled_entry_is_not_counted_as_present(tmp_path):
    cfg = _config(tmp_path, {"command": sys.executable, "args": ["x.py"],
                             "disabled": True})
    row = kc.check_lane(cfg, WANTED, probe=False)
    assert row["state"] == kc.DISABLED


def test_unspawnable_command_is_broken(tmp_path):
    cfg = _config(tmp_path, {"type": "stdio",
                             "command": str(tmp_path / "does_not_exist.exe"),
                             "args": []})
    row = kc.check_lane(cfg, WANTED, probe=True)
    assert row["state"] == kc.BROKEN, row
    assert "could not start" in row["detail"] or "initialize" in row["detail"]


def test_incomplete_tool_set_is_partial_and_names_the_gap(tmp_path):
    script = _script(tmp_path, ["krampus_members"])
    cfg = _config(tmp_path, {"type": "stdio",
                             "command": sys.executable, "args": [str(script)]})
    row = kc.check_lane(cfg, WANTED, probe=True)
    assert row["state"] == kc.PARTIAL
    assert "gamora_lilith" in row["detail"]


def test_unreadable_config_is_missing_with_the_reason(tmp_path):
    cfg = tmp_path / "lane.jsonc"
    cfg.write_text("{not json", encoding="utf-8")
    row = kc.check_lane(cfg, WANTED, probe=False)
    assert row["state"] == kc.MISSING
    assert "invalid JSON" in row["detail"]


def test_required_tools_covers_every_selector():
    selectors = ["lilith", "eve"]
    tools = kc.required_tools(selectors)
    assert {"gamora_lilith", "gamora_eve", "krampus_select",
            "providers_list", "provider_best"} <= set(tools)
    assert len(tools) == 6 + len(selectors)


@pytest.mark.parametrize("lane_state,expected_exit", [(kc.OK, 0), (kc.MISSING, 1)])
def test_exit_code_follows_the_gap(monkeypatch, tmp_path, lane_state, expected_exit):
    """A gate that reports 0 over a missing lane has reported a lie."""
    monkeypatch.setattr(kc, "_surface",
                        lambda: ([{"name": "madi"}], ["lilith"], ["groq"]))
    cfg = tmp_path / "lane.jsonc"
    cfg.write_text(json.dumps({"mcpServers": {}}), encoding="utf-8")
    monkeypatch.setattr(kc, "LANES", {"probe-lane": cfg})
    monkeypatch.setattr(kc, "check_lane",
                        lambda path, wanted, probe: {"config": str(path),
                                                     "state": lane_state,
                                                     "detail": "stub", "tools": []})
    assert kc.main([]) == expected_exit


def test_blind_surface_is_exit_two_not_a_pass(monkeypatch):
    def boom():
        raise RuntimeError("krampus not importable")

    monkeypatch.setattr(kc, "_surface", boom)
    assert kc.main(["--json"]) == 2


def test_probe_carries_tool_names_not_only_a_count(tmp_path):
    """A count alone cannot answer 'is the surface covered' (HED-9)."""
    import mcp_eight_verify as eight

    script = _script(tmp_path, ["alpha", "beta"])
    result = eight.probe_stdio([sys.executable, str(script)], cwd=str(tmp_path))
    assert result.ok, result.detail
    assert result.tools == 2
    assert sorted(result.tool_names) == ["alpha", "beta"]
