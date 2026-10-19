# coding: utf-8
"""Controls for tools/heredoc_pipe_lint.py -- the advisory `.githooks/pre-commit`
stanza runs this over staged shell files and reads its EXIT CODE.

Why this file exists. The hook treats a non-zero exit as the signal
(`echo "$staged_sh" | xargs ... heredoc_pipe_lint.py`, then `if [ $? -ne 0 ]`),
so the contract under test is two-part: the detector must find the unsafe shape,
and the CLI must actually say so in its exit status. A linter that is correct but
always exits 0 makes the hook a dead check, and a linter that flags every heredoc
gets switched off -- each of those is a clause below.

The rule the tool realises (from its own docstring, measured 2026-10-15): the
PREDICTOR IS PAYLOAD LENGTH, not triple quotes. A ~170-line heredoc lost its
payload; a ~20-line one applied first try. Triple quotes only change how the
failure looks (SyntaxError instead of a silent no-op), so they are context on a
finding, never a rule -- pinned separately here so a later edit cannot promote
them back into a trigger.

Four clauses:
  1. an over-long payload and an unterminated heredoc are both REPORTED;
  2. a short payload is NOT reported, with or without triple quotes;
  3. the CLI contract the hook depends on: exit 0 clean / 1 findings / 2 usage,
     including xargs' many-files-at-once invocation and the mixed case;
  4. the detector is load-bearing: stubbing `scan_command` silences the unsafe
     fixture, so clause 1 cannot be passing on the fixture alone.

Not covered, deliberately: whether a payload would be mangled by a *particular*
shell. This lints command text; the shell that receives it is out of scope.
"""

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

import heredoc_pipe_lint as lint  # noqa: E402 - after sys.path

# -- fixtures ---------------------------------------------------------------
# A payload longer than the limit, a payload comfortably under it, and one whose
# terminator line is missing. Built as whole command texts so the tests exercise
# the same text a shell file would contain.

LONG_PAYLOAD = "python - <<'PY'\n" + "x = 1\n" * (lint.MAX_PAYLOAD_LINES + 5) + "PY\n"

SHORT_PAYLOAD = "python - <<'PY'\n" + "x = 1\n" * 20 + "PY\n"

# Same length, but the payload carries triple quotes. Under the limit this is
# still the safe form -- the measurement says triple quotes alone never broke a
# heredoc, so this must stay silent.
SHORT_WITH_TRIPLE = (
    "python - <<'PY'\n"
    'doc = """a short docstring"""\n'
    "x = 1\n"
    "PY\n"
)

UNTERMINATED = "python - <<'PY'\nx = 1\ny = 2\n"

CLEAN_SHELL = "#!/bin/sh\nset -eu\nprintf '%s\\n' ok\n"


def _write(tmp_path, name, text):
    path = Path(tmp_path) / name
    path.write_text(text, encoding="utf-8")
    return path


# -- clause 1: the defect is reported ---------------------------------------

def test_an_over_long_payload_is_reported(tmp_path):
    """The measured failure: a big payload through a heredoc loses its body."""
    findings = lint.scan_command(LONG_PAYLOAD, source="big.sh")
    assert [f["kind"] for f in findings] == ["heredoc_too_long"], findings
    assert findings[0]["tag"] == "PY", findings[0]
    assert findings[0]["payload_lines"] > lint.MAX_PAYLOAD_LINES, findings[0]
    # The line must point at the heredoc's opening line, which is what a reader
    # edits; the payload length is the finding's own field.
    assert findings[0]["line"] == 1, findings[0]


def test_a_missing_terminator_is_reported(tmp_path):
    """Bash says 'delimited by end-of-file'; this says it before the command."""
    findings = lint.scan_command(UNTERMINATED, source="cut.sh")
    assert [f["kind"] for f in findings] == ["heredoc_unterminated"], findings
    assert findings[0]["tag"] == "PY", findings[0]
    assert "delimited by end-of-file" in findings[0]["detail"], findings[0]


def test_the_finding_points_at_its_own_heredoc(tmp_path):
    """Two heredocs, only the second unsafe: the line number must be the second."""
    text = SHORT_PAYLOAD + "\necho between\n" + LONG_PAYLOAD
    findings = lint.scan_command(text, source="two.sh")
    assert len(findings) == 1, findings
    # Derived from the text rather than hardcoded: the long heredoc opens on the
    # line after the separator, so a change to SHORT_PAYLOAD cannot make this
    # assertion quietly wrong.
    expected = text.splitlines().index("echo between") + 2
    assert findings[0]["line"] == expected, findings


# -- clause 2: the negative control -----------------------------------------

def test_a_short_payload_is_not_reported(tmp_path):
    """A linter that flagged every heredoc would pass clause 1 and be useless."""
    assert lint.scan_command(SHORT_PAYLOAD, source="small.sh") == []


def test_triple_quotes_alone_do_not_trigger(tmp_path):
    """The measured discriminator: quotes are context, LENGTH is the rule."""
    assert lint.scan_command(SHORT_WITH_TRIPLE, source="quoted.sh") == []


def test_a_plain_shell_file_is_not_reported(tmp_path):
    assert lint.scan_command(CLEAN_SHELL, source="clean.sh") == []


def test_triple_quotes_are_reported_as_context_on_a_long_payload():
    """On a finding they are worth saying: they change how the loss looks."""
    text = "python - <<'PY'\n" + 'doc = """long"""\n' + "x = 1\n" * 60 + "PY\n"
    findings = lint.scan_command(text, source="long_quoted.sh")
    assert len(findings) == 1, findings
    assert findings[0]["contains_triple_quotes"] is True, findings[0]
    assert "SyntaxError" in findings[0]["detail"], findings[0]


# -- clause 3: the CLI contract the hook depends on -------------------------

def test_cli_exits_zero_on_a_clean_file(tmp_path):
    clean = _write(tmp_path, "clean.sh", CLEAN_SHELL)
    assert lint.main([str(clean)]) == 0


def test_cli_exits_one_on_an_unsafe_file(tmp_path):
    """The hook's only signal. An always-zero linter is a dead check."""
    unsafe = _write(tmp_path, "big.sh", LONG_PAYLOAD)
    assert lint.main([str(unsafe)]) == 1


def test_cli_exits_one_when_only_one_of_many_files_is_unsafe(tmp_path):
    """xargs passes many paths at once; one finding must decide the batch."""
    clean = _write(tmp_path, "clean.sh", CLEAN_SHELL)
    unsafe = _write(tmp_path, "big.sh", LONG_PAYLOAD)
    assert lint.main([str(clean), str(unsafe)]) == 1
    # Order must not matter: same inputs, reversed.
    assert lint.main([str(unsafe), str(clean)]) == 1


def test_cli_json_reports_the_count(tmp_path, capsys):
    unsafe = _write(tmp_path, "big.sh", LONG_PAYLOAD)
    assert lint.main(["--json", str(unsafe)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 1, payload
    assert payload["findings"][0]["kind"] == "heredoc_too_long", payload


def test_cli_usage_errors_exit_two(tmp_path):
    """2 is distinct from 1 on purpose: a usage error is not a finding."""
    missing = Path(tmp_path) / "does_not_exist.sh"
    assert lint.main([]) == 2
    assert lint.main([str(missing)]) == 2


def test_main_is_callable_with_an_explicit_argv(tmp_path):
    """The hook shell needs no argv plumbing, but tests must not read sys.argv."""
    clean = _write(tmp_path, "clean.sh", CLEAN_SHELL)
    assert lint.main([str(clean)]) == 0
    assert lint.main([]) == 2


# -- clause 4: the detector is load-bearing --------------------------------

def test_a_stubbed_detector_silences_the_unsafe_fixture(tmp_path, monkeypatch):
    """Proof that clauses 1-3 read the detector, not the fixture text.

    `lint_file` resolves `scan_command` from module globals at call time, so the
    stub reaches the CLI path. The file is unchanged and still parses; only the
    classifier is gone.
    """
    unsafe = _write(tmp_path, "big.sh", LONG_PAYLOAD)
    monkeypatch.setattr(lint, "scan_command", lambda *a, **k: [])
    assert lint.main([str(unsafe)]) == 0
