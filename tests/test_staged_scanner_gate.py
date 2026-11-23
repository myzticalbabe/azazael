# coding: utf-8
"""Tests for tools/staged_scanner_gate.py.

The gate replaces the old pre-commit check 2, which failed on ANY finding in a
temp snapshot at --severity warning and so blocked every commit touching a
legacy file. The contract these tests lock:

  * a pre-existing finding must NOT block a commit (the old bug),
  * a NEW finding of the same category MUST block (the check's actual job),
  * `--severity error` ignores warning-level findings.
"""
import sys
from pathlib import Path

# Import by file location, the same way the other gate tests do. `import
# tools.staged_scanner_gate` looks identical and is not: `tools/` carries no
# __init__.py on purpose (the per-project trees are separate portions of the
# same namespace), so a regular `tools` package installed in site-packages --
# present on the 3.13 interpreter this gate's control runs under -- wins the
# lookup and this file fails at COLLECTION with ModuleNotFoundError. The
# preflight control reported that as a dead gate, which is what it was.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import staged_scanner_gate as gate  # noqa: E402


_CLEAN = "x = 1\n"
_WITH_SILENT_PASS = "def f():\n    try:\n        x = 1\n    except:\n        pass\n"


def test_counts_detects_a_warning_level_finding():
    counts = gate._counts(_WITH_SILENT_PASS, "x.py", "warning")
    assert counts.get("silent_except_pass", 0) >= 1


def test_severity_error_ignores_warning_level_findings():
    counts = gate._counts(_WITH_SILENT_PASS, "x.py", "error")
    assert counts.get("silent_except_pass", 0) == 0


def _stage(monkeypatch, before, after):
    monkeypatch.setattr(gate, "_staged_py_files", lambda: ["x.py"])
    monkeypatch.setattr(gate, "_show",
                        lambda rev: after if rev == ":0:x.py" else before)
    monkeypatch.setattr(sys, "argv", ["staged_scanner_gate"])


def test_pre_existing_finding_does_not_block(monkeypatch, capsys):
    """The exact bug: an unchanged legacy finding must pass."""
    _stage(monkeypatch, before=_WITH_SILENT_PASS, after=_WITH_SILENT_PASS)
    assert gate.main() == 0
    assert "no new anti-patterns" in capsys.readouterr().out


def test_added_finding_blocks(monkeypatch, capsys):
    """The actual job: adding a warning-level finding must fail."""
    _stage(monkeypatch, before=_CLEAN, after=_WITH_SILENT_PASS)
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "silent_except_pass" in out
    assert "+1" in out


def test_added_warning_ignored_at_error_severity(monkeypatch, capsys):
    _stage(monkeypatch, before=_CLEAN, after=_WITH_SILENT_PASS)
    monkeypatch.setattr(sys, "argv",
                        ["staged_scanner_gate", "--severity", "error"])
    assert gate.main() == 0


def test_new_file_is_compared_against_empty(monkeypatch, capsys):
    """A new file's findings are all new, so a dirty new file must fail."""
    _stage(monkeypatch, before="", after=_WITH_SILENT_PASS)
    assert gate.main() == 1


def test_git_returns_bytes(monkeypatch):
    """`_git` must not decode with the OS locale (regression: cp1252 crash)."""
    out = gate._git("rev-parse", "--is-inside-work-tree")
    assert isinstance(out, bytes)
    assert out.strip() == b"true"


def _stage_commit_mode(monkeypatch, base, before, after):
    """Commit mode: paths come from `base..HEAD`, sides are named blobs."""
    asked: list[str] = []
    monkeypatch.setattr(gate, "_staged_py_files",
                        lambda b=None, t=None: ["x.py"])

    def _show(rev):
        asked.append(rev)
        return before if rev.startswith(f"{base}:") else after

    monkeypatch.setattr(gate, "_show", _show)
    monkeypatch.setattr(sys, "argv",
                        ["staged_scanner_gate", "--base", base])
    return asked


def test_commit_mode_compares_base_to_head_not_the_index(monkeypatch, capsys):
    """The index is another lane's desk drawer at push time -- never read.

    Measured 2026-11-03: a 2-file commit was refused in index mode over 7
    forensic files staged elsewhere. Commit mode must ask git for
    `base:path` and `HEAD:path`, and for `:0:` not at all.
    """
    asked = _stage_commit_mode(monkeypatch, "HEAD~1",
                               before=_CLEAN, after=_CLEAN)
    assert gate.main() == 0
    assert asked == ["HEAD~1:x.py", "HEAD:x.py"]
    assert not any(r.startswith(":0:") for r in asked)
    assert "HEAD~1..HEAD" in capsys.readouterr().out


def test_commit_mode_blocks_a_finding_added_by_the_commit(monkeypatch, capsys):
    """The fix this test was written for: `before` used to stay at HEAD, so
    commit mode compared HEAD against HEAD and could never fire."""
    _stage_commit_mode(monkeypatch, "HEAD~1",
                       before=_CLEAN, after=_WITH_SILENT_PASS)
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "silent_except_pass" in out and "+1" in out


def test_unresolvable_base_refuses_instead_of_passing(monkeypatch, capsys):
    """`git diff NOSUCH HEAD` prints nothing, which reads as 'no changes'."""
    monkeypatch.setattr(sys, "argv",
                        ["staged_scanner_gate", "--base", "nosuchrev"])
    assert gate.main() == 2
    assert "does not resolve" in capsys.readouterr().out

def test_tip_scopes_the_range_to_the_commit_being_pushed(monkeypatch, capsys):
    """A push of an ancestor sends base..sha, so HEAD must not be scanned."""
    asked: list[tuple] = []

    def _files(b=None, t=None):
        asked.append((b, t))
        return ["x.py"]

    # Real revisions: the gate refuses an unresolvable range before it scans, so
    # placeholder refs would exercise the refusal instead of the plumbing.
    base = gate._git("rev-list", "--max-parents=0", "HEAD").decode().split()[0]
    tip = gate._git("rev-parse", "HEAD~1").decode().strip()
    monkeypatch.setattr(gate, "_staged_py_files", _files)
    monkeypatch.setattr(gate, "_show", lambda rev: _CLEAN)
    monkeypatch.setattr(sys, "argv",
                        ["staged_scanner_gate", "--base", base, "--tip", tip])
    assert gate.main() == 0
    assert asked == [(base, tip)]
    assert "%s..%s" % (base, tip) in capsys.readouterr().out


def test_tip_without_base_refuses(monkeypatch, capsys):
    """Without a base the scan would be index-scoped, silently answering a
    different question than the caller asked."""
    monkeypatch.setattr(sys, "argv", ["staged_scanner_gate", "--tip", "HEAD~1"])
    assert gate.main() == 2
    assert "--tip only means something with --base" in capsys.readouterr().out


def test_unimportable_scanner_refuses_instead_of_passing(monkeypatch, capsys):
    """A check whose scanner never loaded certified nothing -- exit 2, not 0.

    This was the last tool-level fail-open on the commit path: the guard printed
    'passing loud' and returned 0, while the `--base` guard eight lines earlier
    returned 2 for exactly the same class of blindness. Two blind conditions,
    two verdicts, one of them a pass.
    """
    # `None` in sys.modules makes `from CORE.compliance.scanner import ...`
    # raise ImportError even though the real module is importable on this box.
    monkeypatch.setitem(sys.modules, "CORE.compliance.scanner", None)
    monkeypatch.setattr(sys, "argv", ["staged_scanner_gate"])
    assert gate.main() == 2
    out = capsys.readouterr().out
    assert "scanner unavailable" in out and "BLIND" in out
