# coding: utf-8
"""Tests for tools/soul_licence_check.py (pre-commit Check 2b / push Check 8b).

The contract these tests lock (owner mandate, permanent 2026-11-23):

  * a clean tree (Soul Forge LICENSE + manifest) MUST pass (exit 0),
  * a live foreign project-licence claim (CDDL/MIT/Apache) MUST fail (exit 1),
  * a banishment line ("SOUL LICENCE ONLY ... CDDL ... forbidden") MUST pass --
    naming a banished licence to forbid it is not claiming it,
  * a historical record that names Soul Forge as the outcome MUST pass.
"""
import sys
from pathlib import Path

import tools.soul_licence_check as gate


SOUL_LICENSE = (
    "Soul Forge License v1.0\n"
    "Source: https://github.com/myzticalbabe/fixture-repo\n"
)


def _repo(tmp_path, files):
    root = tmp_path / "fixture-repo"
    root.mkdir()
    (root / ".git").mkdir()
    for name, text in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def _run(monkeypatch, capsys, root):
    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, "argv", ["soul_licence_check"])
    return gate.main()


def test_clean_tree_passes(monkeypatch, capsys, tmp_path):
    root = _repo(tmp_path, {
        "LICENSE": SOUL_LICENSE,
        "PUBLIC_MANIFEST.json": '{"license": "LicenseRef-SoulForge-1.0"}',
    })
    assert _run(monkeypatch, capsys, root) == 0
    assert "SOUL LICENCE ONLY" in capsys.readouterr().out


def test_live_cddl_claim_fails(monkeypatch, capsys, tmp_path):
    """The actual job: a live foreign project-licence claim must fail."""
    root = _repo(tmp_path, {
        "LICENSE": SOUL_LICENSE,
        "CITATION.cff": 'license: "CDDL-1.1"\n',
    })
    assert _run(monkeypatch, capsys, root) == 1
    assert "CDDL" in capsys.readouterr().out


def test_banishment_line_does_not_fail(monkeypatch, capsys, tmp_path):
    """Naming a banished licence to forbid it is not claiming it."""
    root = _repo(tmp_path, {
        "LICENSE": SOUL_LICENSE,
        "NOTICE": ("Project licence: Soul Forge v1.0 -- SOUL LICENCE ONLY, "
                   "not CDDL, not MIT.\n"),
    })
    assert _run(monkeypatch, capsys, root) == 0


def test_historical_record_with_outcome_passes(monkeypatch, capsys, tmp_path):
    root = _repo(tmp_path, {
        "LICENSE": SOUL_LICENSE,
        "notes.md": ("Licence update: now Soul Forge License v1.0 "
                     "(LicenseRef-SoulForge-1.0). "
                     "CDDL-1.1 references below are superseded history.\n"),
    })
    assert _run(monkeypatch, capsys, root) == 0


def test_missing_license_fails(monkeypatch, capsys, tmp_path):
    root = _repo(tmp_path, {})
    assert _run(monkeypatch, capsys, root) == 1
