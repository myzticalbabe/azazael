# coding: utf-8
"""A registered gate that cannot fail is not a gate.

The registry in `tools/preflight_all.py` proves three things about a gate: that
it is **wired** (its own `--self-test` re-derives the list from the hook text),
that it is **present** (`test_hook_gate_presence.py`), and that it has a
**control** where one exists. None of those is the property a gate is for --
saying no.

That distinction is not academic in this tree. `tools/ast_audit.py` is a
REPORTER: it prints `syntax_err=1` and exits 0. It is a gate only because
`tools/deep_dive.py::leg_ast_audit` reads `syntax_errors` out of the report and
raises. Both halves were proved in-process on 2026-11-14; the point is that the
producer's exit code alone would have read as a pass.

So this test asks the shell-level question of every script the hook runs: **is
there a path that exits non-zero?** Measured 2026-11-14, all 36 distinct
registered scripts answer yes. That reading is the reason for the ratchet --
nothing in the tree would have failed if one of them had answered no.

What this test **cannot** prove: that the failing branch is REACHABLE. A
`return 1` under an impossible condition satisfies it and still never fires.
Reachability needs the gate's own control test, named per row in the registry;
this test only guarantees the gate has not become a pure reporter.

It reads the files as they are on disk, not at HEAD: the question is what the
next commit runs, and a dirty gate file flipping this test is a real signal
about the gate that is about to run, not noise.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import preflight_all as pf  # noqa: E402


def _nonzero(node: ast.expr) -> bool:
    """True when this expression can be a non-zero exit signal."""
    if isinstance(node, ast.Constant):
        return (isinstance(node.value, int) and not isinstance(node.value, bool)
                and node.value != 0)
    if isinstance(node, ast.UnaryOp):
        return True
    # A computed value (`sys.exit(main())`) can be non-zero; refusing it would
    # flag the most common correct shape in this tree.
    return True


def failure_paths(source: str) -> tuple[bool, bool]:
    """(explicit non-zero exit, module raises anywhere)."""
    tree = ast.parse(source)
    explicit = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and node.value is not None \
                and _nonzero(node.value):
            explicit = True
        elif isinstance(node, ast.Call) and node.args:
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name in ("exit", "_exit", "SystemExit") and _nonzero(node.args[0]):
                explicit = True
    raises = any(isinstance(node, ast.Raise) for node in ast.walk(tree))
    return explicit, raises


def registered_scripts() -> list[str]:
    seen: dict[str, None] = {}
    for gate in pf.GATES:
        seen.setdefault(str(gate.argv[0]), None)
    return list(seen)


def test_the_roster_is_not_empty():
    """An empty loop would pass this file and prove nothing."""
    scripts = registered_scripts()
    assert len(scripts) == 36, scripts
    assert len(pf.GATES) > len(scripts)  # one script serves several rows


@pytest.mark.parametrize("script", registered_scripts())
def test_registered_gate_can_exit_non_zero(script: str):
    path = ROOT / script
    assert path.is_file(), script
    explicit, raises = failure_paths(path.read_text(encoding="utf-8"))
    assert explicit, (
        "%s is registered as a gate but has no explicit non-zero exit -- it can "
        "only report. Either give it a verdict, or name the consumer that raises "
        "on its count." % script)


def test_a_reporter_is_visible_to_this_test():
    """Negative control: the check must fail on a reporter, or it proves nothing.

    `ast_audit.py` is the live example: it reports `syntax_err` and exits 0, and
    is a gate only through `deep_dive.leg_ast_audit`. Fed a module that can only
    report, this test's own predicate must say so.
    """
    reporter = "def main():\n    print('5 findings')\n    return 0\n"
    explicit, raises = failure_paths(reporter)
    assert explicit is False and raises is False

    failing = "def main():\n    return 2 if bad() else 0\n"
    assert failure_paths(failing)[0] is True

    exiting = "import sys\nsys.exit(int(sys.argv[1]))\n"
    assert failure_paths(exiting)[0] is True
