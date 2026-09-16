# coding: utf-8
"""Wire-or-cut contract for the mesh functions nothing reaches (PF16).

Why this is a test and not a to-do list entry
---------------------------------------------
Probe PF16 found 114 mesh functions that nothing in the repository references.
That finding cannot be fixed by editing the function: a function nothing calls
cannot regress visibly, so it can be neither trusted nor repaired by
observation. There are exactly two honest resolutions -- give it a caller, or
delete it -- and choosing between them is a decision, not a patch.

`evolution.py` already encodes this for the v2 engines as `SERVED_ENGINES` /
`UNSERVED_ENGINES`, with a test asserting no UNSERVED name is referenced by the
production driver, and that pattern worked. This test generalises it: every PF16
finding must appear in `NEURAL_MESH_WIRE_OR_CUT.json` with a declared
disposition, and the declaration must agree with reality.

What it catches:

* a NEW unreferenced function -- it fails the undeclared check instead of
  quietly joining a 114-item blind spot;
* a declaration that stopped being true, in both directions: a function
  declared ``wired`` that nothing actually calls, and a function declared
  ``retired`` that something now depends on;
* a declaration for a function that no longer exists, so the table cannot
  accumulate fiction;
* a status typo, which would otherwise silently become a fourth category.

``pending`` is deliberately allowed -- an unreviewed function is not the same as
a decided one, and collapsing those two is how a backlog turns into a lie. The
table is regenerated (decisions preserved) with:

    python tools/mesh_function_preflight.py --verdict
"""

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
for _p in (REPO / "tools", REPO / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import mesh_function_preflight as mfp  # noqa: E402

VERDICT = REPO / "NEURAL_MESH_WIRE_OR_CUT.json"


@pytest.fixture(scope="module")
def table():
    if not VERDICT.exists():
        pytest.skip("no verdict table; run "
                    "python tools/mesh_function_preflight.py --verdict")
    return json.loads(VERDICT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def tree():
    funcs, _counts = mfp.build(None)
    unreferenced = {fn.label for fn in funcs if "PF16" in fn.failures}
    return funcs, unreferenced


def test_the_table_was_generated_by_the_probe_it_claims(table):
    assert table.get("probe") == "PF16"
    assert table.get("rule")


def test_every_unreferenced_function_is_declared(table, tree):
    _funcs, unreferenced = tree
    declared = set(table.get("declared") or {})
    undeclared = sorted(unreferenced - declared)
    assert not undeclared, (
        "%d unreferenced function(s) have no wire-or-cut decision; run "
        "`python tools/mesh_function_preflight.py --verdict` and set a status "
        "for each: %s" % (len(undeclared), undeclared[:10]))


def test_no_declaration_is_stale(table, tree):
    """A declaration for a function that is gone is fiction, not a decision."""
    funcs, _unreferenced = tree
    live = {fn.label for fn in funcs}
    stale = sorted(set(table.get("declared") or {}) - live)
    assert not stale, (
        "%d declaration(s) refer to functions that no longer exist: %s"
        % (len(stale), stale[:10]))


def test_a_wired_declaration_is_actually_wired(table, tree):
    """`wired` means a production caller exists, so PF16 must not fire."""
    _funcs, unreferenced = tree
    declared = table.get("declared") or {}
    lying = sorted(k for k, v in declared.items()
                   if v.get("status") == "wired" and k in unreferenced)
    assert not lying, (
        "declared wired but nothing reaches them: %s" % lying[:10])


def test_a_retired_declaration_is_still_unreferenced_and_states_why(table, tree):
    _funcs, unreferenced = tree
    declared = table.get("declared") or {}
    retired = {k: v for k, v in declared.items()
               if v.get("status") == "retired"}
    resurrected = sorted(k for k in retired if k not in unreferenced)
    assert not resurrected, (
        "declared retired but something now reaches them -- wire them or "
        "delete the declaration: %s" % resurrected[:10])
    silent = sorted(k for k, v in retired.items() if not str(v.get("reason") or "").strip())
    assert not silent, (
        "a retirement without a reason cannot be reviewed: %s" % silent[:10])


def test_statuses_are_known(table):
    known = set(mfp.VERDICT_STATUSES)
    declared = table.get("declared") or {}
    unknown = sorted({str(v.get("status"))
                      for v in declared.values()} - known)
    assert not unknown, "unknown status(es) %s; expected one of %s" % (
        unknown, sorted(known))


def test_counts_agree_with_the_table(table):
    declared = table.get("declared") or {}
    tally = Counter(str(v.get("status")) for v in declared.values())
    for status in mfp.VERDICT_STATUSES:
        assert table["counts"].get(status, 0) == tally.get(status, 0), (
            "count for %r drifted from the table" % status)
    assert table.get("total") == len(declared)


def test_pending_is_visible_rather_than_hidden(table):
    """The backlog must be countable, or it is indistinguishable from zero."""
    declared = table.get("declared") or {}
    pending = [k for k, v in declared.items() if v.get("status") == "pending"]
    assert len(pending) == table["counts"].get("pending", 0)
    # Not an assertion on the SIZE (the backlog is real work), but the number
    # must be reported rather than inferred, so a monitor can trend it.
    assert isinstance(table["counts"].get("pending"), int)
