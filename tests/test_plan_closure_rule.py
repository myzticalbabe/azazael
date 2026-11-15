# coding: utf-8
"""A closure record must be closeable by the relation that names it.

`_superseded_task_ids` closes a task by the NUMBER its closure title carries:
an edge to "DONE #593" closes task 593. A closure record written as its own
task -- "TRIAGE-007 DONE #593", observation 1902 -- carries 593 and IS 1902, so
no edge could ever close 1902. Measured 2026-11-15: 11 such records (the whole
TRIAGE-006/007 batch) sat in `triage_plan` as ordinary open work, and every new
closure statement added one more permanent open item.

The fix adds a second, narrower closure path: an edge whose endpoint IS the
record's own title closes it. Title-prefix matching was rejected once before
(`_superseded_task_ids` docstring: "prefix matching broke on the first real
use") because a closure title is a DIFFERENT sentence that merely mentions the
task. That reasoning does not apply here -- the endpoint is the record's own
title, truncated -- and this file pins both halves of that distinction.

`RELATIONS` is transcribed from a real `engram conflicts list` run on this host
2026-11-15, including the ~60-char truncation and its "..." tail, because the
truncation is what the prefix rule has to survive.
"""

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

from engram_supervise import (  # noqa: E402 - after sys.path
    _closed_by_own_title, _superseded_endpoint_titles, _superseded_task_ids,
    _title_claims_finished,
)

RELATIONS = """
Conflicts List (project: azazael)
  Total:  3602
  Showing: 500

  id:             4910
  sync_id:        rel-99ab6068e842727a
  relation:       supersedes
  judgment_status: judged
  source:         obs-108c5ac1af52d9b7 \u2014 TRIAGE-008: 11 done-in-title closure records consolidated an...
  target:         obs-a5fbc985dfe49a53 \u2014 TRIAGE-006 DONE #578: phantom: no engram record for #578 exi...
  created_at:     2026-11-15 11:42:28

  id:             4909
  sync_id:        rel-5ec90158a8a1d14f
  relation:       supersedes
  judgment_status: judged
  source:         obs-108c5ac1af52d9b7 \u2014 TRIAGE-008: 11 done-in-title closure records consolidated an...
  target:         obs-9f2f0b4b1d6e8a01 \u2014 DEEPSEEK LANE: transport sweep + skill_library/structured_actio...
  created_at:     2026-11-15 11:42:28

  id:             4896
  sync_id:        rel-pending0000000000
  relation:       supersedes
  judgment_status: pending
  source:         obs-108c5ac1af52d9b7 \u2014 TRIAGE-008: 11 done-in-title closure records consolidated an...
  target:         obs-0000000000000000 \u2014 TRIAGE-006 DONE #549
  created_at:     2026-11-15 11:42:05
"""

#: The real title of observation 1868, before truncation.
TITLE_1868 = ("TRIAGE-006 DONE #578: phantom: no engram record for #578 exists "
              "(task_detail empty); triage union matches")


def test_number_closure_still_works():
    """The original path is untouched: the number in a closure title closes it."""
    ids = _superseded_task_ids(RELATIONS)
    assert ids is not None, "transcribed output must be recognized"
    assert "578" in ids


def test_pending_relation_is_not_a_verdict():
    """An unjudged pair closes nothing -- it is owed, not decided."""
    assert "549" not in _superseded_task_ids(RELATIONS)


def test_own_title_endpoint_is_collected_despite_truncation():
    eps = _superseded_endpoint_titles(RELATIONS)
    assert any(e.startswith("TRIAGE-006 DONE #578") for e in eps)
    assert not any(e.endswith("...") for e in eps), "truncation tail must be gone"
    assert len(eps) == 2, "the pending pair must not contribute an endpoint"


def test_closure_record_closes_itself_by_own_title():
    """The defect: 1868 is 'TRIAGE-006 DONE #578' and can now be retired."""
    eps = _superseded_endpoint_titles(RELATIONS)
    assert _title_claims_finished(TITLE_1868)
    assert _closed_by_own_title(TITLE_1868, eps)


def test_an_ordinary_task_is_not_retired_by_a_mention():
    """#594 claims done-and-uncommitted, which counts as a claim to settle."""
    eps = _superseded_endpoint_titles(RELATIONS)
    plain = "OPENCODE LANE: 124 PARTIAL + 392 orphans + test-file landing"
    assert not _title_claims_finished(plain)
    assert not _closed_by_own_title(plain, eps)


def test_a_short_stub_matches_nothing():
    """Below 12 chars an endpoint cannot identify a record, so it closes none."""
    assert not _closed_by_own_title("TRIAGE-006 DONE #578", ["TRIAGE-006"])
