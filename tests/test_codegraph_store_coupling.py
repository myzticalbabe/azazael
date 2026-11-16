# coding: utf-8
"""The graph store the gate certifies must be the store the remedy writes.

Why this exists (2026-11-15)
---------------------------
``mcp_startup_gate.py`` read ``<repo>/src/graphify-out/graph.json`` and FAILED
the ``codegraph-staleness`` leg, printing this remedy:

    rebuild: scripts/graphify_bin.sh update C:/Azazael/azazael

That command writes ``<repo>/graphify-out/graph.json`` -- a file no lane
passes as ``--graph``. Executed literally, the operator gets a rebuild, an
exit 0, and a gate that is still red, with a fresh orphan on disk. The guard
in ``tools/graphify_scope_guard.py`` refuses it (exit 3), which is the only
reason the failure was visible at all rather than silent.

The defect class is NOT "a typo in one string". It is two files owning the
same fact separately: the gate names a read path, the guard names a write
path, and nothing compared them. So this file compares them, and it executes
the remedy text against the guard, so a future edit to either side that
re-introduces the split fails here instead of in front of an operator.

Run:
    python tests/test_codegraph_store_coupling.py
"""

import os
import re
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.env  # type: ignore[import-not-found]

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

GATE_SRC = REPO_ROOT / "tools" / "mcp_startup_gate.py"


def _gate():
    from tools import mcp_startup_gate

    return mcp_startup_gate


def _guard():
    from tools import graphify_scope_guard

    return graphify_scope_guard


# ── the two constants must name one store ──────────────────────────


def test_gate_store_is_src_graphify_out():
    """The gate certifies <repo>/src/graphify-out/graph.json, not the repo root."""
    store = Path(_gate().CODEGRAPH_STORE).resolve()
    assert store == (REPO_ROOT / "src" / "graphify-out" / "graph.json").resolve()


def test_guard_canonical_dir_is_the_gate_store():
    """The guard's allowed write dir and the gate's read file are one path."""
    guard = _guard()
    written = REPO_ROOT.joinpath(*guard.CANONICAL_PARTS) / "graph.json"
    assert written.resolve() == Path(_gate().CODEGRAPH_STORE).resolve()


# ── the remedy text must be a command the guard allows ─────────────


def test_every_printed_remedy_targets_src():
    """No advisory may say `graphify_bin.sh update <something other than src>`."""
    text = GATE_SRC.read_text(encoding="utf-8", errors="replace")
    mentions = re.findall(r"graphify_bin\.sh update ([^\s\"']+)", text)
    assert mentions, "gate no longer prints a rebuild remedy; update this test"
    wrong = [target for target in mentions if target.rstrip(",);") != "src"]
    assert not wrong, (
        "remedy targets that the scope guard refuses (an orphan store): %s" % wrong
    )


def test_remedy_argv_passes_the_guard(monkeypatch, capsys):
    """Run the remedy's own argv through the guard: allowed, and the old form refused.

    The negative control matters as much as the positive one. If this test only
    asserted "src is allowed" it would still pass on a guard that allowed
    everything, so the repo-root form is required to be REFUSED in the same run.
    """
    guard = _guard()
    for name in ("GRAPHIFY_OUT", "GRAPHIFY_REPO_ROOT", guard.ESCALATION_VAR):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(REPO_ROOT)

    allowed = guard.main(["--repo-root", str(REPO_ROOT), "--", "update", "src"])
    refused = guard.main(["--repo-root", str(REPO_ROOT), "--", "update", str(REPO_ROOT)])

    assert allowed == guard.EXIT_OK, capsys.readouterr().err
    assert refused == guard.EXIT_DRIFT, capsys.readouterr().err


if __name__ == "__main__":
    # Standalone runner: pytest is not dependable on the free-threaded builds.
    class _MP:
        def __init__(self):
            self._env = {}

        def delenv(self, name, raising=False):
            self._env[name] = os.environ.pop(name, None)

        def chdir(self, path):
            os.chdir(str(path))

    sys.path.insert(0, str(REPO_ROOT))
    failures = 0
    for fn in (
        test_gate_store_is_src_graphify_out,
        test_guard_canonical_dir_is_the_gate_store,
        test_every_printed_remedy_targets_src,
        test_remedy_argv_passes_the_guard,
    ):
        try:
            if fn.__name__ == "test_remedy_argv_passes_the_guard":
                fn(_MP(), None)
            else:
                fn()
        except AssertionError as exc:
            failures += 1
            print("FAIL %s: %s" % (fn.__name__, exc))
        else:
            print("ok   %s" % fn.__name__)
    print("%d failure(s)" % failures)
    sys.exit(1 if failures else 0)
