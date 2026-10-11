"""Guard: no module may fall back to `Path.home() / "azazael"` for its project root.

MEASURED 2026-10-11 (action registry followups, item [1]). Twenty-two code sites
across ~20 modules defaulted their project root to `Path.home() / "azazael"`. On this
host that names a DIFFERENT, stale checkout from the tree the modules ship in
(`C:/Azazael/azazael`), so with `AZAZAEL_ROOT` unset they put the wrong tree on
`sys.path` and read and wrote the wrong tree's output and data directories.

Every site is repaired. This test is the part that was MISSING: nothing stopped the
next module from reintroducing the same fallback -- which is how it reached 22 sites
in the first place. It is AST-based on purpose, so a COMMENT that quotes the old value
for the record (most repaired modules carry one) is not a violation while real code is.

The needle is checked in both quote styles, because the two `src/AOA` test modules
used single quotes and a double-quote-only sweep silently missed them.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"

#: The stale value, in the shapes the tree actually used: `"azazael"` and `'azazael'`.
_STALE_NAMES = {"azazael"}


def _is_path_home_call(node: ast.AST) -> bool:
    """True only if this node IS the `Path.home()` call itself.

    Deliberately NOT "mentions `Path.home()` somewhere in its subtree". That looser
    needle flagged `Path.home() / ".cache" / "azazael" / "uv"` -- a legitimate cache
    directory -- because the `/ "azazael"` division has `Path.home()` somewhere in its
    left subtree. MEASURED 2026-10-11: it produced exactly two such false positives
    (`src/UVZ.py:60`, `src/META/UVZ.py:60`), which is how a guard gets disabled. The
    defect shape is `Path.home()` divided DIRECTLY by the name, so the sibling operand
    must BE the call, not merely contain it.
    """
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "home"
    )


def stale_root_lines(tree: ast.AST) -> list[int]:
    """Line numbers of `Path.home() / "azazael"` divisions that are in CODE.

    Matches the innermost division of a chained form, so
    `Path.home() / "azazael" / "src"` is caught by its inner BinOp regardless of
    what is appended after it.
    """
    hits: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            for a, b in ((node.left, node.right), (node.right, node.left)):
                if (isinstance(a, ast.Constant) and a.value in _STALE_NAMES
                        and _is_path_home_call(b)):
                    hits.append(node.lineno)
    return sorted(set(hits))


def test_no_module_falls_back_to_a_home_relative_azazael_root() -> None:
    """The whole point of this file: keep the count at zero."""
    offenders: list[str] = []
    scanned = 0
    for path in sorted(SRC.rglob("*.py")):
        # Backup litter is not importable code; it is tracked separately (registry D-3).
        if ".pre_gate_backup" in path.name:
            continue
        scanned += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            # A file that cannot be parsed cannot contribute an importable fallback.
            continue
        for lineno in stale_root_lines(tree):
            offenders.append("%s:%d" % (path.relative_to(SRC.parent), lineno))

    assert scanned > 100, (
        "scan found only %d files under %s -- the guard is not looking where it "
        "thinks it is" % (scanned, SRC)
    )
    assert not offenders, (
        "stale home-relative project-root fallback reintroduced at: %s\n"
        "Use `CORE.paths.get_project_root_safe()` (honours AZAZAEL_ROOT, never "
        "raises), or in a bootstrap module that cannot import CORE yet, "
        "`Path(__file__).resolve().parents[N]`." % ", ".join(offenders)
    )


def test_the_needle_check_actually_catches_the_needle() -> None:
    """A negative control: the guard must FAIL on the very shape it forbids.

    Without this, a refactor that made `stale_root_lines` return [] for every input
    would leave the guard passing while catching nothing -- a gate that can never
    fail, which is the defect class this sweep exists to remove.
    """
    caught = stale_root_lines(ast.parse('ROOT = str(Path.home() / "azazael")\n'))
    assert caught == [1]

    caught_chained = stale_root_lines(
        ast.parse('sys.path.insert(0, str(Path.home() / "azazael" / "src"))\n'))
    assert caught_chained == [1]

    caught_single = stale_root_lines(
        ast.parse("sys.path.insert(0, str(Path.home() / 'azazael' / 'src'))\n"))
    assert caught_single == [1]

    # And it must NOT fire on the legitimate neighbours, or it will be disabled.
    assert stale_root_lines(ast.parse('D = str(Path.home() / "Desktop")\n')) == []
    assert stale_root_lines(ast.parse('P = str(Path.home() / ".azazael")\n')) == []
    assert stale_root_lines(ast.parse('B = Path(os.environ.get("X", str(Path.home() / "azazael_backup")))\n')) == []

    # The false positives that forced the needle to be tightened from "mentions
    # Path.home()" to "IS Path.home()": a cache dir under home is not a root.
    assert stale_root_lines(
        ast.parse('C = Path.home() / ".cache" / "azazael" / "uv"\n')) == []
    assert stale_root_lines(
        ast.parse('C = str(Path.home() / ".cache" / "azazael" / "uv")\n')) == []


def test_canonical_resolver_exists_and_points_at_this_tree() -> None:
    from CORE.paths import get_project_root_safe

    root = get_project_root_safe()
    assert isinstance(root, Path)
    assert (root / "src" / "CORE").is_dir(), (
        "get_project_root_safe() resolved to %s, which is not a tree containing "
        "src/CORE" % root
    )


def test_canonical_resolver_honours_the_env_override(tmp_path, monkeypatch) -> None:
    """AZAZAEL_ROOT must win -- the repair must not have dropped the override."""
    from CORE.paths import clear_cache, get_project_root_safe

    fake = tmp_path / "fakeroot"
    (fake / "src" / "CORE").mkdir(parents=True)
    monkeypatch.setenv("AZAZAEL_ROOT", str(fake))
    clear_cache()
    try:
        assert get_project_root_safe() == fake
    finally:
        clear_cache()


def test_canonical_resolver_never_raises_on_a_sentinel_failure(monkeypatch) -> None:
    """The fail-open contract: a monitor must not die for a bad root.

    A path that is neither a tree nor an existing directory forces the
    location-derived branch, which is the one that used to be `~/azazael`.
    """
    from CORE.paths import clear_cache, get_project_root_safe

    monkeypatch.delenv("AZAZAEL_ROOT", raising=False)
    clear_cache()
    try:
        root = get_project_root_safe()
    finally:
        clear_cache()
    assert (root / "src" / "CORE").is_dir(), (
        "the fallback branch must return the tree it ships in, not a home-relative "
        "guess; got %s" % root
    )
    assert os.path.basename(str(root)) == "azazael" or str(root).endswith("azazael"), (
        "fallback root %s does not look like this repo" % root
    )
