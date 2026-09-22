# coding: utf-8
"""The no-LLM graph refresh must resolve a graphify install it can actually use.

Why this is a test and not a comment
------------------------------------
`scripts/graph_refresh_no_llm.py` hard-coded its interpreter to the pip install
in the system Python 3.14. That was the right instinct about the venv (the 3.14t
venv has no graphify, so `sys.executable -m graphify` reaches nothing) and the
wrong conclusion about the target. Measured 2026-09-22:

    ~/.local/bin/graphify.exe          0.9.50  exporters/html.py present, PATCHED
    Python314 site-packages (pip)      0.8.8   no exporters package at all
    ~/.claude/skills/graphify (skill)  0.9.55

The hard-coded value was the middle row -- the *only* install whose layout
cannot carry `scripts/graphify_node_limit_patch.py`, because that patch rewrites
`exporters/html.py` and 0.8.8 is a flat package with no `exporters/` at all. And
`graphify_huge_mode.py` is read FROM that file. So the repo's documented refresh
path ran an engine its own renderer does not target, and the huge-mode renderer
was unreachable from it.

What it catches:

* the resolver returning an install without `exporters/html.py` -- the defect
  itself, and the one that produces a wrong artifact rather than an error;
* a silent fallback when nothing qualifies: refusing is the point, because the
  alternative is writing a 688k-node page through the small-graph code path;
* a candidate walk that reports success while finding nothing;
* a patched install losing to an unpatched one (the patch is the reason to
  prefer one install over another; version alone is not).

The instruments here are stubbed rather than probed, so these are unit tests of
the resolution ORDER and the refusal, not of the host's disk. One test does read
the real host, to prove the walk is not vacuous where it runs.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _p in (_ROOT / "scripts", _ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import graph_refresh_no_llm as g  # noqa: E402


def _fake_install(tmp_path: Path, name: str, *, patched: bool) -> Path:
    """A graphify install directory shaped like a real 0.9.x one."""
    install = tmp_path / name / "graphify"
    (install / "exporters").mkdir(parents=True)
    body = "def to_html():\n    return 1\n"
    if patched:
        body = "%s = 5000\n%s" % (g.HUGEMODE_MARKER, body)
    (install / "exporters" / "html.py").write_text(body, encoding="utf-8")
    (install / "cli.py").write_text("# cli\n", encoding="utf-8")
    return install


def _fake_python(tmp_path: Path, name: str) -> Path:
    py = tmp_path / ("%s-python.exe" % name)
    py.write_text("", encoding="utf-8")
    return py


def _stub(monkeypatch, installs: dict[Path, tuple[Path, str]]) -> None:
    """Make the resolver see `installs` as the whole world."""
    monkeypatch.setattr(g, "graphify_python_candidates",
                        lambda: list(installs))
    monkeypatch.setattr(g, "_graphify_install_dir",
                        lambda py: installs.get(py, (None, "?"))[0])
    monkeypatch.setattr(g, "_graphify_version",
                        lambda py: installs.get(py, (None, "?"))[1])


def test_an_install_without_the_exporters_package_is_never_selected(tmp_path, monkeypatch):
    """The 0.8.8 shape: flat package, no `exporters/`. Must be skipped."""
    flat = tmp_path / "flat"
    flat.mkdir()
    (flat / "cli.py").write_text("# flat layout only\n", encoding="utf-8")
    good = _fake_install(tmp_path, "good", patched=True)
    py_bad = _fake_python(tmp_path, "bad")
    py_good = _fake_python(tmp_path, "good")
    _stub(monkeypatch, {py_bad: (flat, "0.8.8"), py_good: (good, "0.9.50")})

    notes: list[str] = []
    chosen = g.resolve_graphify_python(report=notes.append)

    assert chosen == py_good, "the un-patchable install was selected"
    assert any("no exporters" in n for n in notes), notes


def test_it_refuses_instead_of_falling_back_when_nothing_qualifies(tmp_path, monkeypatch):
    """No capable install means None. A fallback would write the wrong artifact."""
    flat = tmp_path / "flat"
    flat.mkdir()
    (flat / "cli.py").write_text("# flat\n", encoding="utf-8")
    py = _fake_python(tmp_path, "only")
    _stub(monkeypatch, {py: (flat, "0.8.8")})

    assert g.resolve_graphify_python(report=lambda _m: None) is None


def test_a_patched_install_beats_a_newer_unpatched_one(tmp_path, monkeypatch):
    """Preference is capability, not version: the patch is what huge mode needs."""
    patched = _fake_install(tmp_path, "patched", patched=True)
    unpatched = _fake_install(tmp_path, "unpatched", patched=False)
    py_patched = _fake_python(tmp_path, "patched")
    py_new = _fake_python(tmp_path, "new")
    # The unpatched one is NEWER, and must still lose.
    _stub(monkeypatch, {py_patched: (patched, "0.9.50"),
                        py_new: (unpatched, "0.9.65")})

    notes: list[str] = []
    chosen = g.resolve_graphify_python(report=notes.append)

    assert chosen == py_patched, (chosen, notes)
    assert any("patched" in n for n in notes), notes


def test_an_unpatched_only_world_warns_instead_of_proceeding_quietly(tmp_path, monkeypatch):
    """Capable-but-unpatched is usable and must say so, by name."""
    install = _fake_install(tmp_path, "unpatched", patched=False)
    py = _fake_python(tmp_path, "u")
    _stub(monkeypatch, {py: (install, "0.9.50")})

    notes: list[str] = []
    assert g.resolve_graphify_python(report=notes.append) == py
    joined = " ".join(notes)
    assert "UNPATCHED" in joined and g.HUGEMODE_MARKER in joined, notes


def test_the_version_skew_is_reported_with_the_remedy(tmp_path, monkeypatch):
    """A skill/package skew is named, with the command that ends it."""
    install = _fake_install(tmp_path, "good", patched=True)
    py = _fake_python(tmp_path, "good")
    _stub(monkeypatch, {py: (install, "0.9.50")})
    skill = tmp_path / ".graphify_version"
    skill.write_text("0.9.55\n", encoding="utf-8")
    monkeypatch.setattr(g, "SKILL_VERSION_FILE", skill)

    notes: list[str] = []
    g.resolve_graphify_python(report=notes.append)

    joined = " ".join(notes)
    assert "skew" in joined, notes
    assert "graphifyy==0.9.55" in joined, notes
    assert "graphify_node_limit_patch.py" in joined, notes


def test_the_skill_and_the_package_can_agree_and_say_nothing(tmp_path, monkeypatch):
    """The negative control: agreement must not produce a warning."""
    install = _fake_install(tmp_path, "good", patched=True)
    py = _fake_python(tmp_path, "good")
    _stub(monkeypatch, {py: (install, "0.9.55")})
    skill = tmp_path / ".graphify_version"
    skill.write_text("0.9.55\n", encoding="utf-8")
    monkeypatch.setattr(g, "SKILL_VERSION_FILE", skill)

    notes: list[str] = []
    g.resolve_graphify_python(report=notes.append)

    assert not any("skew" in n or "WARNING" in n for n in notes), notes


def test_the_candidate_walk_is_not_vacuous_on_this_host():
    """The stubs above prove the order; this proves the walk has something to walk.

    A resolver whose candidate list is empty returns None for everything and
    reads exactly like "no capable install on this box" -- the same silent
    instrument this session has already been bitten by twice. So the real list
    is measured, and if a capable install exists here it must be found.
    """
    cands = g.graphify_python_candidates()
    assert cands, "no candidates; the resolution below would be vacuous"
    assert any(p.exists() for p in cands), cands
    chosen = g.resolve_graphify_python(report=lambda _m: None)
    if chosen is None:
        pytest.skip("no capable graphify install on this host")
    install = g._graphify_install_dir(chosen)
    assert install is not None
    for part in g.REQUIRED_INSTALL_PARTS:
        assert (install / part).exists(), (chosen, part)
