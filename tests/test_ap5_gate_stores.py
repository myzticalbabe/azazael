"""The AP-5 transcript gate must distinguish 'nothing scanned' from 'clean'.

Both fixtures below transcribe the manicode schema observed on this host
(2026-10-19, ``%USERPROFILE%\\.config\\manicode\\projects\\azazael\\chats\\
<session>\\chat-messages.json``):

    [{"id": "...", "variant": "ai" | "user", "content": "",
      "blocks": [{"type": "text", "content": "...",
                  "textType": "text" | "reasoning"}],
      "timestamp": "..."}]

The field names are copied from a real session file, not invented, so a test
that passes here is evidence about the real store rather than about a fixture
that happened to agree with the parser.

The load-bearing test is ``test_absent_store_is_not_clean`` and its sibling
``test_no_assistant_prose_is_not_clean``: they FAIL if the gate ever collapses
'missing store' or 'empty store' back into a zero-finding success, which is the
defect this change exists to close -- the gate previously reported clean for a
client whose prose it had never opened.
"""

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

import transcript_ap5_gate as gate  # noqa: E402 - after sys.path

#: Unquoted on purpose: permission_seeking_guard blanks quoted spans, so a
#: violation inside quotes is correctly NOT a finding. This one is prose.
VIOLATION = "Want me to land the fix now?"
CLEAN_PROSE = "The gate was wired and the check passed."


def _ai(message_id, *blocks):
    """One assistant message, mirroring the observed record shape."""
    return {
        "id": message_id,
        "variant": "ai",
        "content": "",
        "blocks": list(blocks),
        "timestamp": "11:17 PM",
    }


def _user(message_id, content):
    """One operator message: observed with content and NO blocks key."""
    return {
        "id": message_id,
        "variant": "user",
        "content": content,
        "timestamp": "11:17 PM",
    }


def _text(content, text_type="text"):
    return {"type": "text", "content": content, "textType": text_type}


def _write_session(root, session_id, messages, project="azazael"):
    """Write a real-shaped chat-messages.json under the projects root."""
    session_dir = Path(root) / project / "chats" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    path = session_dir / "chat-messages.json"
    path.write_text(json.dumps(messages), encoding="utf-8")
    return path


def _scan(tmp_path, limit=500):
    return gate.scan_manicode_store(
        root=str(tmp_path), session=None, limit=limit,
        max_bytes=gate.DEFAULT_MAX_STORE_BYTES,
    )


# ─── positive path: prose found, rule shared with the opencode leg ───────


def test_manicode_finds_planted_violation_in_prose(tmp_path):
    _write_session(
        tmp_path,
        "2026-10-19T03-17-04.170Z",
        [_user("m1", "continue"), _ai("m2", _text(VIOLATION))],
    )
    result = _scan(tmp_path)

    assert result.status == gate.SCANNED
    assert result.scanned_parts == 1
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.rule == "want_me_to"
    assert finding.source == "manicode"
    assert finding.message_id == "m2"
    assert finding.session_id == "2026-10-19T03-17-04.170Z"


def test_reasoning_blocks_are_counted_not_scanned(tmp_path):
    _write_session(
        tmp_path,
        "2026-10-19T03-17-04.170Z",
        [
            _ai(
                "m2",
                _text(VIOLATION, text_type="reasoning"),
                _text(CLEAN_PROSE),
            )
        ],
    )
    result = _scan(tmp_path)

    assert result.status == gate.SCANNED
    assert result.scanned_parts == 1
    assert result.skipped_reasoning == 1
    assert result.findings == []


def test_quoted_anti_pattern_is_not_a_finding(tmp_path):
    """The rulebook is reused, not forked: quoting the pattern stays clean."""
    _write_session(
        tmp_path,
        "2026-10-19T03-17-04.170Z",
        [_ai("m2", _text('The docs quote "%s" as the counter-example.' % VIOLATION))],
    )
    result = _scan(tmp_path)

    assert result.status == gate.SCANNED
    assert result.findings == []


# ─── the controls: absence must never read as a pass ────────────────────


def test_absent_store_is_not_clean(tmp_path, capsys):
    missing = tmp_path / "no-such-root"
    code = gate.main(["--source", "manicode", "--manicode-root", str(missing)])
    out = capsys.readouterr().out

    assert code == 2, "an absent store must not exit 0"
    assert "AP-5: clean" not in out
    assert "STORE ABSENT" in out
    assert "NOT SCANNED" in out


def test_no_assistant_prose_is_not_clean(tmp_path, capsys):
    """A readable store holding only operator turns is still nothing scanned."""
    _write_session(
        tmp_path, "2026-10-19T03-17-04.170Z", [_user("m1", "continue")]
    )
    code = gate.main(["--source", "manicode", "--manicode-root", str(tmp_path)])
    out = capsys.readouterr().out

    assert code == 2
    assert "AP-5: clean" not in out
    assert "NO ASSISTANT PROSE" in out


def test_statuses_are_distinct(tmp_path):
    """absent / no-prose / scanned must be three different statuses."""
    absent = gate.StoreResult(source="manicode", path="x", status=gate.ABSENT)
    empty = gate.StoreResult(
        source="manicode", path="x", status=gate.NO_ASSISTANT_PROSE
    )
    scanned = gate.StoreResult(source="manicode", path="x", status=gate.SCANNED)

    assert len({absent.status, empty.status, scanned.status}) == 3
    assert gate.SCANNED in gate._STATUS_TEXT
    assert gate.ABSENT in gate._STATUS_TEXT
    assert gate.NO_ASSISTANT_PROSE in gate._STATUS_TEXT
    assert gate.OVERSIZE in gate._STATUS_TEXT


def test_unreadable_store_is_not_clean(tmp_path, capsys):
    bad = Path(tmp_path) / "azazael" / "chats" / "2026-10-19T00-00-00.000Z"
    bad.mkdir(parents=True)
    (bad / "chat-messages.json").write_text("{not json", encoding="utf-8")

    code = gate.main(["--source", "manicode", "--manicode-root", str(tmp_path)])
    out = capsys.readouterr().out

    assert code == 2
    assert "AP-5: clean" not in out
    assert "UNREADABLE" in out


def test_oversize_session_is_reported_not_silently_skipped(tmp_path):
    _write_session(
        tmp_path,
        "2026-10-19T03-17-04.170Z",
        [_ai("m2", _text(VIOLATION))],
    )
    result = gate.scan_manicode_store(
        root=str(tmp_path), session=None, limit=500, max_bytes=10
    )

    assert result.status == gate.OVERSIZE
    assert "oversize" in result.note


# ─── combination behaviour and limits ───────────────────────────────────


def test_source_all_survives_one_absent_store(tmp_path, capsys):
    """One usable store is enough; a missing second store does not fail it."""
    _write_session(
        tmp_path,
        "2026-10-19T03-17-04.170Z",
        [_ai("m2", _text(CLEAN_PROSE))],
    )
    code = gate.main([
        "--source", "all",
        "--db", str(tmp_path / "missing.db"),
        "--manicode-root", str(tmp_path),
    ])
    out = capsys.readouterr().out

    assert code == 0
    assert "AP-5: clean (1 part(s) scanned across 1 store(s))" in out
    assert "STORE ABSENT" in out


def test_opencode_absent_alone_exits_2(tmp_path):
    code = gate.main([
        "--source", "opencode",
        "--db", str(tmp_path / "missing.db"),
    ])
    assert code == 2


def test_findings_exit_1(tmp_path):
    _write_session(
        tmp_path,
        "2026-10-19T03-17-04.170Z",
        [_ai("m2", _text(VIOLATION))],
    )
    code = gate.main(["--source", "manicode", "--manicode-root", str(tmp_path)])
    assert code == 1


def test_limit_is_respected_across_messages(tmp_path):
    messages = [
        _ai("m%d" % i, _text(CLEAN_PROSE)) for i in range(1, 5)
    ]
    _write_session(tmp_path, "2026-10-19T03-17-04.170Z", messages)
    result = _scan(tmp_path, limit=2)

    assert result.status == gate.SCANNED
    assert result.scanned_parts == 2


def test_json_reports_status_and_scanned_flag(tmp_path, capsys):
    code = gate.main([
        "--source", "manicode",
        "--manicode-root", str(tmp_path / "missing"),
        "--json",
    ])
    payload = json.loads(capsys.readouterr().out)

    assert code == 2
    assert payload["stores"][0]["status"] == gate.ABSENT
    assert payload["stores"][0]["scanned"] is False
    assert payload["findings"] == []
