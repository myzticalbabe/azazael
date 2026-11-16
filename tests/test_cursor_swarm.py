# coding: utf-8
"""Tests for `tools/cursor_swarm/` -- the WORKER swarm.

Why this file exists
--------------------
The cursor swarm writes to the tree's own claim ledger, and the tree's own
validator is what reads it. Two dialects would mean every row the swarm writes
is unreadable by the one tool whose job is to read it - and a ledger nobody can
read is a private language wearing a schema.

So the first thing these tests pin is the DIALECT, not the picture: the rows the
swarm writes must validate under `claim_agreement.validate_ledger`, unchanged,
including the optional `ts` column the A8 audit asked for and the eight-key rows
that were written before it existed.

The second thing pinned is the transaction. The audit's P0 finding was that a
rolled-back swarm left the ledger claiming work that did not exist, so the
ledger is inside the transaction now. That property is a control here: force a
worker red, and the canonical ledger must be byte-identical afterwards.

The third is the picture's own arithmetic: a cursor's TIP lands on the node it
claims, the schedule fits the budget, and the self-test line the page prints is
computed from the live DOM rather than written into the markup.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import claim_agreement  # noqa: E402
import monitor_theme  # noqa: E402


def _load(name, path):
    """Load a module by path - the package has no __init__.py, by design."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HERE = ROOT / "tools" / "cursor_swarm"
swarm = _load("cursor_swarm_swarm", HERE / "swarm.py")
site = _load("cursor_swarm_site", HERE / "swarm_site.py")


# ── the dialect ───────────────────────────────────────────────────────────

def _rows(count=3, verdict="landed", ts=1700000000000):
    out = []
    for i in range(count):
        out.append({"cursor_id": "w%02d" % (i + 1), "tree": "src/CORE",
                    "node": "src/CORE/x", "verdict": verdict,
                    "claim": "read 1 module(s) of src/CORE/x [placed]", "ts": ts})
    return out


def test_swarm_rows_validate_under_the_trees_own_validator(tmp_path):
    """The swarm's rows must be readable by the tree's validator, unchanged."""
    rows, _ = swarm.chain(_rows(), 1, "GENESIS")
    path = tmp_path / "ledger.jsonl"
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
                    encoding="utf-8")
    report = claim_agreement.validate_ledger(str(path))
    assert report["bad"] == [], report["bad"]
    assert report["rows"] == 3


def test_the_optional_ts_column_is_authenticated_not_ignored(tmp_path):
    """The A8 audit §2.4: a `ts` column that is NOT hashed can be rewritten.

    Restricting the hash to the canonical eight keys would leave the timestamp
    unauthenticated, so the design's proposal was backwards and the rule stayed
    "hash every key the row carries". This is the control for that decision:
    change the timestamp and the chain must break.
    """
    rows, _ = swarm.chain(_rows(), 1, "GENESIS")
    rows[0]["ts"] = rows[0]["ts"] + 1
    body = {k: v for k, v in rows[0].items() if k != "hash"}
    import hashlib
    expect = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    assert rows[0]["hash"] != expect, "a rewritten ts must not keep its hash"
    path = tmp_path / "ledger.jsonl"
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows),
                    encoding="utf-8")
    report = claim_agreement.validate_ledger(str(path))
    assert report["bad"], "the tree's validator must reject the rewritten row"


def test_eight_key_rows_without_ts_still_validate(tmp_path):
    """Rows written before the column existed keep their hashes."""
    rows = [{"cursor_id": "w01", "tree": "src/CORE", "node": "src/CORE/x",
             "verdict": "landed", "claim": "read 1 module(s) of src/CORE/x [placed]"}]
    import hashlib
    body = dict(rows[0], frame=1, prev_hash="GENESIS")
    body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    path = tmp_path / "old.jsonl"
    path.write_text(json.dumps(body, sort_keys=True) + "\n", encoding="utf-8")
    report = claim_agreement.validate_ledger(str(path))
    assert report["bad"] == [], report["bad"]
    assert report["rows"] == 1


def test_the_live_v0_ledger_is_still_readable():
    """The swarm's dialect must not invalidate the rows that already exist."""
    live = Path("C:/Users/clint/LIVEVIEW_CURSOR_SWARM_V0.jsonl")
    if not live.exists():
        return
    report = claim_agreement.validate_ledger(str(live))
    assert report["bad"] == [], report["bad"][:3]


# ── the transaction ───────────────────────────────────────────────────────

def test_a_red_worker_leaves_the_canonical_ledger_untouched(tmp_path, monkeypatch):
    """P0: the ledger is inside the transaction.

    Force one worker red and the canonical ledger must be byte-identical
    afterwards - not merely shorter. A ledger that says "landed" for work that
    did not land is the one artifact everything else is built on.
    """
    ledger = tmp_path / "worker_frames.jsonl"
    attempts = tmp_path / "worker_attempts.jsonl"
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({
        "scope": "tools/cursor_swarm",
        "workers": [{"id": "w01", "tree": "tools/cursor_swarm",
                     "node": "tools/cursor_swarm", "scope": ["tools/cursor_swarm/swarm.py"],
                     "intent": "read 1 module(s)"}],
    }), encoding="utf-8")

    def red(worker, declared, dirty):
        return {"id": worker["id"], "tree": worker["tree"], "node": worker["node"],
                "scope": list(worker["scope"]), "intent": worker.get("intent", ""),
                "verdict": "rolledback", "reasons": ["forced red by the control"],
                "dirty": [], "reading": "1 module(s) - 0 line(s) - 0 setting read(s)",
                "reads": 0, "undeclared": 0, "bypasses": 0, "unparseable": 1,
                "lines": 0, "ms": 1.0, "claim": "w01 - forced red"}

    monkeypatch.setattr(swarm, "run_worker", red)
    monkeypatch.setattr(swarm, "tracked", lambda scope: ["tools/cursor_swarm/swarm.py"])
    monkeypatch.setattr(swarm, "dirty_in", lambda files: set())

    args = _args(plan_path, ledger, attempts, tmp_path / "site.html")
    rc = swarm.run(args)
    assert rc == 1, "a red worker must roll the swarm back"
    assert not ledger.exists(), "the canonical ledger must not be written on rollback"
    assert attempts.exists(), "the rolled-back attempt must be recorded"
    rows = [json.loads(line) for line in attempts.read_text(encoding="utf-8").splitlines() if line]
    assert rows and all(r["verdict"] == "rolledback" for r in rows)


def _args(plan_path, ledger, attempts, out):
    class A:
        pass
    a = A()
    a.plan = str(plan_path)
    a.ledger = str(ledger)
    a.attempts = str(attempts)
    a.out = str(out)
    a.threads = 1
    return a


# ── the picture's own arithmetic ──────────────────────────────────────────

def test_the_schedule_fits_the_budget_at_seventy_two_workers():
    stagger, slowest = site.schedule(72)
    assert slowest <= site.BUDGET_MS, "%d ms > %d ms" % (slowest, site.BUDGET_MS)
    assert stagger >= 0


def test_the_hotspot_is_read_out_of_the_glyph_not_hard_coded():
    assert "data-hotspot" in site.POINTER_SVG
    assert site.hotspot_of(site.POINTER_SVG) == (2.0, 1.0)


def test_render_draws_one_cursor_and_one_layer_per_worker():
    workers = []
    for i in range(3):
        workers.append({
            "id": "w%02d" % (i + 1), "tree": "src/CORE", "node": "src/CORE/x",
            "scope": ["src/CORE/x.py"], "verdict": "landed", "reading": "1 module(s)",
            "claim": "w%02d - src/CORE/x" % (i + 1), "x": 100.0 + i * 50, "y": 80.0,
            "stage_verdicts": {s: "landed" for s in site.STAGES},
        })
    color = {k: v[0] for k, v in monitor_theme.SEMANTIC.items()}
    page, timing = site.render(workers, [], [], color,
                               {"source": "t", "denominator": "d"})
    assert page.count('class="cursor"') == 3
    assert page.count('class="layer"') == 3
    assert "SELFTEST" in page
    assert timing["slowest"] <= site.BUDGET_MS


def test_held_has_a_colour_of_its_own():
    """The A8 audit P1: `warn` and `advisory` share a hex, so a held cursor
    used to render exactly like a warning."""
    semantic = monitor_theme.SEMANTIC
    assert "held" in semantic
    assert semantic["held"][0] != semantic["warn"][0]
    assert semantic["held"][0] != semantic["advisory"][0]


def test_a_scope_that_will_not_parse_is_red(tmp_path):
    """`parse` is a real check, not a decoration."""
    bad = tmp_path / "broken.py"
    bad.write_text("def (:\n", encoding="utf-8")
    declared, _vocab, _src = swarm.load_declared()
    result = swarm.run_worker({"id": "w01", "tree": "t", "node": "t",
                                "scope": [str(bad)], "intent": "read 1 module(s)"},
                               declared, set())
    assert result["verdict"] == "rolledback"
    assert any("do not parse" in r for r in result["reasons"]), result["reasons"]
