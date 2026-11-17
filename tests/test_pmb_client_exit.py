#!/usr/bin/env python3
"""The PMB CLI must not exit 0 on a rejected call.

Why this file exists: on 2026-11-16 the MCP transport answered every `call`
with `{"code": -32600, "message": "Session not found"}`, `tools/pmb_client.py`
printed it as an ordinary payload and returned 0. A caller reading the exit
status -- a shell `&&` chain, a lane script, an agent -- saw a successful recall
that had retrieved nothing. The SDK's `CallToolResult.isError` is carried
SIDEWAYS from the content, so joining `result.content` and discarding the flag
is what turned a refusal into a report.

The tests are written against `has_error()` and `main()`'s exit code, not
against any one error string: the shapes below are transcribed from what the
daemon and the SDK actually produced, and a new envelope shape that is neither
an answer nor recognised as a refusal fails `test_answer_shapes_are_not_errors`
by being misread, not by being absent.
"""
from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pmb_client  # noqa: E402


def test_marker_set_by_call_tool_is_an_error():
    assert pmb_client.has_error({"_pmb_error": True, "text": "nope"})


def test_mcp_iserror_echo_is_an_error():
    assert pmb_client.has_error({"isError": True, "content": []})


def test_jsonrpc_error_object_is_an_error():
    # Transcribed from the live transport failure, 2026-11-16.
    assert pmb_client.has_error({"code": -32600, "message": "Session not found"})


def test_plain_error_key_is_an_error():
    assert pmb_client.has_error({"error": "tool not found"})


def test_text_refusal_is_an_error():
    # Transcribed from the live daemon, 2026-11-16: unknown tool answered with
    # this sentence as ordinary content and `isError` unset.
    assert pmb_client.has_error("Unknown tool: 'no_such_tool_xyz'")
    assert pmb_client.has_error("Error: session expired")


def test_answer_shapes_are_not_errors():
    assert not pmb_client.has_error({"lessons": [], "decisions": []})
    assert not pmb_client.has_error({"results": [{"content": "x"}]})
    assert not pmb_client.has_error({"code": 0, "message": "ok", "result": {}})
    assert not pmb_client.has_error("a plain text answer")
    assert not pmb_client.has_error(["a", "list"])


def test_main_exits_one_when_the_daemon_refuses(monkeypatch, capsys):
    monkeypatch.setattr(pmb_client, "call_tool",
                        lambda name, args: {"_pmb_error": True,
                                            "text": "Session not found"})
    rc = pmb_client.main(["recall", "anything"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "rejected" in out and "Session not found" in out


def test_main_exits_zero_on_a_real_answer(monkeypatch, capsys):
    monkeypatch.setattr(pmb_client, "call_tool",
                        lambda name, args: {"results": [{"content": "ok"}]})
    rc = pmb_client.main(["recall", "anything"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ok" in out


def test_main_exits_one_on_a_text_refusal(monkeypatch, capsys):
    monkeypatch.setattr(pmb_client, "call_tool",
                        lambda name, args: "Unknown tool: 'nope'")
    rc = pmb_client.main(["call", "nope", "{}"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "Unknown tool" in out


def test_json_mode_still_prints_the_refusal(monkeypatch, capsys):
    # A --json caller must get the daemon's own words back even on failure,
    # otherwise the machine-readable path is the one that goes silent.
    monkeypatch.setattr(pmb_client, "call_tool",
                        lambda name, args: {"_pmb_error": True,
                                            "text": "Session not found"})
    rc = pmb_client.main(["call", "stats", "{}", "--json"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "_pmb_error" in out
