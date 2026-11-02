#!/usr/bin/env python3
# coding: utf-8
"""Gate: the evidence ledger must extract, not invent.

Every test here is a way the harvest could look complete while recording the
wrong thing, which is worse than recording nothing because a verse then cites it:

* an error entry whose remedy sits on the lines after its label (the common
  shape) must not be harvested with an empty remedy;
* a table of contents is a map of a document and not a finding;
* a package README is evidence only where it says what does not work;
* `__init__.py` must survive cleaning, because a ledger that renames a module
  corrupts every path a reader would follow;
* an observation with no *Learned* section is undiagnosed, and copying its body
  into the cause field would claim a diagnosis it never made.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import bible_harvest as H


ERROR_DOC = """# Log

## TABLE OF CONTENTS

### By Tag

| tag | count |
| --- | --- |
| threading | 7 |

## Error #12 — Duplicate module broke the patch

**Cause:** the module was imported under two paths.

**Prevention:**
1. assert identity, not equality of names.
2. give every module one import path.

**File(s):** `src/CORE/paths/__init__.py`
"""


def _write(tmp_path: Path, relative: str, text: str) -> Path:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_remedy_after_its_label_is_harvested(tmp_path):
    path = _write(tmp_path, "ERROR_LOG.md", ERROR_DOC)
    records = H._records_for(path, "error", "numbered")
    assert len(records) == 1
    record = records[0]
    assert record["title"] == "Duplicate module broke the patch"
    assert record["cause"].startswith("the module was imported under two paths")
    assert "assert identity" in record["remedy"]
    assert "one import path" in record["remedy"]


def test_table_of_contents_is_not_a_finding(tmp_path):
    path = _write(tmp_path, "ERROR_LOG.md", ERROR_DOC)
    titles = [record["title"] for record in H._records_for(path, "error", "numbered")]
    assert "By Tag" not in titles
    assert all("tag" not in title.lower() for title in titles)


def test_dunder_paths_survive_cleaning(tmp_path):
    path = _write(tmp_path, "ERROR_LOG.md", ERROR_DOC)
    record = H._records_for(path, "error", "numbered")[0]
    assert "__init__.py" in record["files"]


def test_readme_keeps_only_limitation_sections(tmp_path):
    _write(tmp_path, "Project_X/README.md",
           "# X\n\n## What this is\n\nA package.\n\n"
           "## Limitations\n\nIt refuses to fit.\n")
    records = H._records_for(tmp_path / "Project_X" / "README.md", "limitation",
                             "limitation")
    assert [record["title"] for record in records] == ["Limitations"]
    assert records[0]["kind"] == "limitation"


def test_harvest_is_deterministic(tmp_path, monkeypatch):
    _write(tmp_path, "ERROR_LOG.md", ERROR_DOC)
    monkeypatch.setattr(H, "SURFACES", (("ERROR_LOG.md", "error", "numbered"),))
    monkeypatch.setattr(H, "README_GLOB", "no_such_glob_*")
    first = H.harvest(tmp_path, db=tmp_path / "absent.db")
    second = H.harvest(tmp_path, db=tmp_path / "absent.db")
    assert H.render(first) == H.render(second)
    assert first["totals"]["records"] == 1


def test_a_moved_surface_is_stale(tmp_path, monkeypatch):
    _write(tmp_path, "ERROR_LOG.md", ERROR_DOC)
    monkeypatch.setattr(H, "SURFACES", (("ERROR_LOG.md", "error", "numbered"),))
    monkeypatch.setattr(H, "README_GLOB", "no_such_glob_*")
    ledger = tmp_path / "harvest.json"
    ledger.write_text(H.render(H.harvest(tmp_path, db=tmp_path / "absent.db")),
                      encoding="utf-8")
    assert H.stale(tmp_path, ledger)[0] == []
    _write(tmp_path, "ERROR_LOG.md", ERROR_DOC + "\n## Error #13 — Another\n\n**Cause:** x.\n")
    problems, _newer = H.stale(tmp_path, ledger)
    assert any("moved since the harvest" in problem for problem in problems)


def test_engram_observation_without_learned_has_no_cause(tmp_path, monkeypatch):
    import sqlite3
    db = tmp_path / "engram.db"
    connection = sqlite3.connect(db, timeout=5)
    connection.execute("CREATE TABLE observations (id INTEGER PRIMARY KEY, "
                       "project TEXT, type TEXT, title TEXT, content TEXT, "
                       "created_at TEXT, deleted_at TEXT)")
    connection.execute("INSERT INTO observations VALUES (1, 'azazael', 'bugfix', 't', "
                       "'**What**: something happened', '2026-11-01', NULL)")
    connection.commit()
    connection.close()
    records, newest = H.engram_records(db)
    assert newest == 1
    assert records[0]["symptom"].startswith("something happened")
    assert records[0]["cause"] == ""
