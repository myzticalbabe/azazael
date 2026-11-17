#!/usr/bin/env python3
"""Tests for the three audit instruments added by the 2026-11-16 gap repair.

Each tool exists to make one previously-unfalsifiable claim measurable:

  generated_audit    an excused path is provably generator-owned (G2)
  interpreter_audit  the hook's interpreter matches what canon claims (G3)
  disclosure_audit   the untracked credential population has a denominator (s3)

So the tests are written against the VERDICT BRANCHES, not against today's tree.
A test that asserted "docs/INDEX.md is DRIFTED" would pass this week, fail once
somebody regenerates it, and never notice the branch that broke. Every fixture
here is built in tmp_path.

The one test that matters most is `test_no_secret_value_reaches_output`: a
scanner that finds a secret by printing it has created a second copy of the
leak in the transcript, in the CI log, and in whatever reads the report.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import disclosure_audit  # noqa: E402
import generated_audit  # noqa: E402
import interpreter_audit  # noqa: E402

GEN_SRC = textwrap.dedent(
    """
    import sys

    args = sys.argv[1:]
    if "--check" in args:
        print("identical: yes" if STATUS == "match" else "identical: no")
        raise SystemExit(0 if STATUS == "match" else 1)
    out = args[args.index("--out") + 1]
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(PAYLOAD)
    """
)


def _generator(root: Path, status: str, payload: str = "rendered") -> Path:
    """A stand-in generator with the same exit contract as the real ones."""
    gen = root / "tools" / "gen.py"
    gen.parent.mkdir(parents=True, exist_ok=True)
    gen.write_text(
        "STATUS = %r\nPAYLOAD = %r\n" % (status, payload) + GEN_SRC,
        encoding="utf-8",
    )
    return gen


# --------------------------------------------------------------------------
# generated_audit
# --------------------------------------------------------------------------

def _wire(monkeypatch, root: Path, table: dict[str, str],
          verifiers: dict[str, dict[str, object]]) -> None:
    monkeypatch.setattr(generated_audit, "ROOT", root)
    monkeypatch.setattr(generated_audit, "_exemptions", lambda: dict(table))
    monkeypatch.setattr(generated_audit, "VERIFIERS", verifiers)


def test_check_bytes_proved(tmp_path, monkeypatch):
    _generator(tmp_path, "match")
    (tmp_path / "target.json").write_text("x", encoding="utf-8")
    _wire(monkeypatch, tmp_path, {"target.json": "tools/gen.py"},
          {"target.json": {"kind": "check-bytes", "args": ["--check"]}})

    rows, counts = generated_audit.audit()

    assert rows[0]["verdict"] == "PROVED"
    assert "identical" in rows[0]["detail"]
    assert counts == {"PROVED": 1}


def test_check_bytes_drifted(tmp_path, monkeypatch):
    _generator(tmp_path, "differ")
    (tmp_path / "target.json").write_text("x", encoding="utf-8")
    _wire(monkeypatch, tmp_path, {"target.json": "tools/gen.py"},
          {"target.json": {"kind": "check-bytes", "args": ["--check"]}})

    rows, _counts = generated_audit.audit()

    assert rows[0]["verdict"] == "DRIFTED"


def test_render_compare_proved(tmp_path, monkeypatch):
    _generator(tmp_path, "match", payload="rendered")
    (tmp_path / "target.md").write_text("rendered", encoding="utf-8")
    _wire(monkeypatch, tmp_path, {"target.md": "tools/gen.py"},
          {"target.md": {"kind": "render-compare", "args": ["--out", "{tmp}"]}})

    rows, _counts = generated_audit.audit()

    assert rows[0]["verdict"] == "PROVED"
    assert "identical" in rows[0]["detail"]


def test_render_compare_drifted_names_both_sizes(tmp_path, monkeypatch):
    payload = "a much longer render"
    _generator(tmp_path, "match", payload=payload)
    (tmp_path / "target.md").write_text("short", encoding="utf-8")
    _wire(monkeypatch, tmp_path, {"target.md": "tools/gen.py"},
          {"target.md": {"kind": "render-compare", "args": ["--out", "{tmp}"]}})

    rows, _counts = generated_audit.audit()

    assert rows[0]["verdict"] == "DRIFTED"
    # HED-9: the reading carries both denominators, not just "different".
    # The lengths are MEASURED, not remembered -- a hardcoded byte count is a
    # claim that silently rots the moment the fixture changes.
    assert "disk %d bytes" % len("short") in rows[0]["detail"]
    assert "render %d bytes" % len(payload) in rows[0]["detail"]


def test_generator_missing_is_a_failure_not_a_skip(tmp_path, monkeypatch):
    _wire(monkeypatch, tmp_path, {"target.json": "tools/absent.py"},
          {"target.json": {"kind": "check-bytes", "args": ["--check"]}})

    rows, _counts = generated_audit.audit()

    assert rows[0]["verdict"] == "GENERATOR-MISSING"
    assert "absent" in rows[0]["detail"]


def test_unregistered_excused_path_is_an_error(tmp_path, monkeypatch):
    _wire(monkeypatch, tmp_path, {"target.json": "tools/gen.py"}, {})

    rows, _counts = generated_audit.audit()

    assert rows[0]["verdict"] == "ERROR"
    assert "no verifier" in rows[0]["detail"]


def test_no_verifier_is_reported_but_not_failing(tmp_path, monkeypatch, capsys):
    _wire(monkeypatch, tmp_path, {"logs/report.json": "tools/gen.py"},
          {"logs/report.json": {"kind": "no-verifier", "args": [],
                                "why": "records a measurement"}})

    rc = generated_audit.main(["--strict"])
    out = capsys.readouterr().out

    assert rc == 0, "a registered exemption must not fail --strict"
    assert "NO-VERIFIER" in out
    assert "records a measurement" in out


def test_strict_fails_only_on_unprovable_paths(tmp_path, monkeypatch, capsys):
    _generator(tmp_path, "differ")
    (tmp_path / "target.json").write_text("x", encoding="utf-8")
    _wire(monkeypatch, tmp_path,
          {"target.json": "tools/gen.py", "other.json": "tools/gen.py"},
          {"target.json": {"kind": "check-bytes", "args": ["--check"]},
           "other.json": {"kind": "no-verifier", "args": [], "why": "run output"}})

    rc = generated_audit.main(["--strict"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "STRICT FAIL -- 1 path(s)" in out


def test_advisory_exit_is_zero_even_when_drifted(tmp_path, monkeypatch):
    _generator(tmp_path, "differ")
    (tmp_path / "target.json").write_text("x", encoding="utf-8")
    _wire(monkeypatch, tmp_path, {"target.json": "tools/gen.py"},
          {"target.json": {"kind": "check-bytes", "args": ["--check"]}})

    assert generated_audit.main([]) == 0


def test_unreadable_exemption_table_exits_two_and_says_so(monkeypatch, capsys):
    def _boom():
        raise ImportError("no commit_gate")

    monkeypatch.setattr(generated_audit, "_exemptions", _boom)

    with pytest.raises(SystemExit) as exc:
        generated_audit.audit()

    assert exc.value.code == 2
    assert "nothing audited, which is not a pass" in capsys.readouterr().out


def test_denominator_is_printed(tmp_path, monkeypatch, capsys):
    _wire(monkeypatch, tmp_path,
          {"a.json": "tools/gen.py", "b.json": "tools/gen.py"},
          {"a.json": {"kind": "no-verifier", "args": [], "why": "x"},
           "b.json": {"kind": "no-verifier", "args": [], "why": "y"}})

    generated_audit.main([])
    out = capsys.readouterr().out

    assert "2/2 excused paths accounted for" in out


# --------------------------------------------------------------------------
# interpreter_audit
# --------------------------------------------------------------------------

def _canon(tmp_path: Path, sentence: str) -> Path:
    path = tmp_path / "AGENTS.md"
    path.write_text(sentence + "\n", encoding="utf-8")
    return path


def test_match_when_hook_and_canon_agree(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(interpreter_audit, "_pin", lambda: ("py.exe", ""))
    monkeypatch.setattr(interpreter_audit, "_probe",
                        lambda _e: (("3.16", False), ""))
    canon = _canon(tmp_path, "Session startup, test suite, commit hooks, and "
                             "all gates use 3.16t: measured 2026-11-09.")

    rc = interpreter_audit.main(["--canon", str(canon)])
    out = capsys.readouterr().out

    assert rc == 0
    assert "MATCH" in out


def test_drifted_when_hook_pins_an_older_interpreter(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(interpreter_audit, "_pin", lambda: ("py.exe", ""))
    monkeypatch.setattr(interpreter_audit, "_probe",
                        lambda _e: (("3.15", False), ""))
    canon = _canon(tmp_path, "commit hooks and all gates use 3.16t")

    rc = interpreter_audit.main(["--canon", str(canon), "--strict"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "DRIFTED" in out
    assert "measures 3.15" in out and "claims 3.16" in out


def test_decision_is_printed_open(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(interpreter_audit, "_pin", lambda: ("py.exe", ""))
    monkeypatch.setattr(interpreter_audit, "_probe",
                        lambda _e: (("3.15", False), ""))
    canon = _canon(tmp_path, "commit hooks use 3.16t")

    interpreter_audit.main(["--canon", str(canon)])
    out = capsys.readouterr().out

    # The tool measures; it must not claim the policy call.
    assert "DECISION OPEN (G3)" in out
    assert "does not move it" in out


def test_unmeasurable_when_the_pin_will_not_run(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(interpreter_audit, "_pin", lambda: ("missing.exe", ""))
    monkeypatch.setattr(interpreter_audit, "_probe",
                        lambda _e: (None, "pinned interpreter will not run: OSError"))
    canon = _canon(tmp_path, "commit hooks use 3.16t")

    rc = interpreter_audit.main(["--canon", str(canon)])
    out = capsys.readouterr().out

    assert rc == 2, "a run that could not measure is never a pass"
    assert "UNMEASURABLE" in out
    # The reason must survive to the report, not be defaulted away.
    assert "will not run" in out


def test_pin_regex_reads_the_real_hook_shape(tmp_path, monkeypatch):
    hook = tmp_path / "pre-commit"
    hook.write_text('#!/bin/bash\nPYTHON3="C:/x/py.exe"\necho hi\n',
                    encoding="utf-8")
    monkeypatch.setattr(interpreter_audit, "HOOK", hook)

    exe, note = interpreter_audit._pin()

    assert exe == "C:/x/py.exe"
    assert note == ""


def test_pin_absent_is_named_not_guessed(tmp_path, monkeypatch):
    hook = tmp_path / "pre-commit"
    hook.write_text("#!/bin/bash\necho hi\n", encoding="utf-8")
    monkeypatch.setattr(interpreter_audit, "HOOK", hook)

    exe, note = interpreter_audit._pin()

    assert exe is None
    assert "no PYTHON3=" in note


# --------------------------------------------------------------------------
# disclosure_audit
# --------------------------------------------------------------------------

def _wire_disclosure(monkeypatch, root: Path, names: list[str]) -> None:
    monkeypatch.setattr(disclosure_audit, "ROOT", root)
    monkeypatch.setattr(disclosure_audit, "_untracked", lambda: list(names))


def test_name_detector_flags_credential_file(tmp_path, monkeypatch):
    (tmp_path / "credentials_real.json").write_text("{}", encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, ["credentials_real.json"])

    findings, _stats = disclosure_audit.audit(200_000)

    assert [f["detector"] for f in findings] == ["credentials-file"]
    assert findings[0]["kind"] == "name"


def test_env_template_is_not_a_leak_but_env_is(tmp_path, monkeypatch):
    (tmp_path / ".env.example").write_text("KEY=\n", encoding="utf-8")
    (tmp_path / ".env").write_text("KEY=\n", encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, [".env.example", ".env"])

    findings, _stats = disclosure_audit.audit(200_000)

    assert [f["path"] for f in findings] == [".env"]


def test_template_flagged_but_excluded_from_strict(tmp_path, monkeypatch, capsys):
    (tmp_path / "credentials_template.json").write_text("{}", encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, ["credentials_template.json"])

    rc = disclosure_audit.main(["--strict"])
    out = capsys.readouterr().out

    assert rc == 0, "a template is printed, not failed, by default"
    assert "template" in out


def test_screenshot_labelled_and_excluded_from_strict(tmp_path, monkeypatch, capsys):
    (tmp_path / "20260101_github_token_settings.png").write_bytes(b"\x89PNG\r\n")
    _wire_disclosure(monkeypatch, tmp_path, ["20260101_github_token_settings.png"])

    rc = disclosure_audit.main(["--strict"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "screenshot" in out


def test_content_detector_finds_private_key_block(tmp_path, monkeypatch):
    body = "header\n-----BEGIN RSA PRIVATE KEY-----\nabc\n"
    (tmp_path / "notes.txt").write_text(body, encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, ["notes.txt"])

    findings, _stats = disclosure_audit.audit(200_000)

    assert findings[0]["detector"] == "private-key-block"
    assert findings[0]["kind"] == "content"
    assert findings[0]["line"] == 2


def test_no_secret_value_reaches_output(tmp_path, monkeypatch, capsys):
    sentinel = "S3NT1NELvalue-UNIQUE-9f3a"
    body = 'password = "%s"\n' % sentinel
    (tmp_path / "creds.json").write_text(body, encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, ["creds.json"])

    disclosure_audit.main([])
    disclosure_audit.main(["--json"])
    out = capsys.readouterr().out

    assert "secret-assignment" in out, "the detector must still report"
    assert sentinel not in out, "a scanner that prints the secret copies it"


def test_json_reports_that_values_were_not_printed(tmp_path, monkeypatch, capsys):
    (tmp_path / "credentials_real.json").write_text("{}", encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, ["credentials_real.json"])

    disclosure_audit.main(["--json"])

    assert '"values_printed": false' in capsys.readouterr().out


def test_population_and_denominator_are_printed(tmp_path, monkeypatch, capsys):
    (tmp_path / "a.txt").write_text("plain\n", encoding="utf-8")
    _wire_disclosure(monkeypatch, tmp_path, ["a.txt"])

    disclosure_audit.main([])
    out = capsys.readouterr().out

    assert "population=untracked" in out
    assert "listed=1 scanned=1" in out


def test_unreadable_population_exits_two(monkeypatch, capsys):
    def _boom():
        raise RuntimeError("git ls-files rc=128")

    monkeypatch.setattr(disclosure_audit, "_untracked", _boom)

    with pytest.raises(SystemExit) as exc:
        disclosure_audit.audit(200_000)

    assert exc.value.code == 2
    assert "nothing audited, which is not a pass" in capsys.readouterr().out
