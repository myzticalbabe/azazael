#!/usr/bin/env python
# coding: utf-8
"""Tests for transubstantiate.py: the extraction contract, the refusal, and the golden.

The negative control is the point. An extractor that "succeeds" on a source with no
deterministic clock manufactures a translation out of a guess, and nothing downstream can
tell. So the suite asserts the refusal as hard as it asserts the extraction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Project_SHARDEX"))

import transubstantiate as T  # noqa: E402

ANIMATION = ROOT / "docs" / "YGGDRASIL_CLEAVE.html"

NO_CLOCK = """<script>
const GROW=10000;
function frame(){ requestAnimationFrame(frame); }
requestAnimationFrame(frame);
</script>
"""

COMPLETE = """<script>
window.__step=function(ms){draw(ms);};
const LIMBS=[["a",-1,.34,"#7df9ff","A"],["b",1,.30,"#00ffa3","B"]];
const GROW=30000,LABEL=8000,HOLD=7000;
function mulberry32(a){return function(){a|=0;return 0.5}}
const R=mulberry32(20261028);
function branch(x,y,ang,len,w,depth,hue){
  if(depth<=0){for(let i=0;i<3;i++){}return;}
  branch(x,y,ang,len*(.68+R()*.12),w*.66,depth-1,hue);
}
branch(960,1080,-Math.PI/2,150,26,4,"#8a6b3d");
ctx.arc(0,0,3.2,0,7);
</script>
"""


def test_prng_matches_the_js_implementation():
    """The port was wrong once (476 segments vs the browser's 489). This vector is the
    first six draws of the browser's mulberry32 at seed 20261028, measured in node."""
    rnd = T.mulberry32(20261028)
    got = [round(rnd(), 6) for _ in range(6)]
    assert got == [0.064762, 0.821390, 0.421255, 0.051588, 0.205913, 0.544268]


@pytest.mark.skipif(not ANIMATION.exists(), reason="the 2D animation is not in this tree")
def test_extracts_the_real_animation_with_line_evidence():
    rules = T.extract(ANIMATION)
    assert rules["shape"] == T.RULES_SHAPE
    assert rules["clock"]["hook"] == "window.__step"
    assert rules["clock"]["line"] > 0
    assert rules["seed"]["value"] == 20261028
    assert rules["phases"]["GROW"] == 30000
    assert rules["phases"]["TOTAL"] == 45000
    assert len(rules["limbs"]) == 10
    # every limb carries the hue it was given, not a generated one
    assert all(limb["hue"].startswith("#") for limb in rules["limbs"])
    assert rules["fractal"]["root_depth"] == 4


def test_refuses_a_source_without_a_clock(tmp_path):
    source = tmp_path / "no_clock.html"
    source.write_text(NO_CLOCK, encoding="utf-8")
    with pytest.raises(T.ExtractError) as failure:
        T.extract(source)
    assert any("clock" in reason for reason in failure.value.missing)
    # the refusal names every missing rule, not just the first one
    assert len(failure.value.missing) == 7


def test_forge_then_verify_round_trip(tmp_path):
    source = tmp_path / "anim.html"
    source.write_text(COMPLETE, encoding="utf-8")
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps(T.extract(source)), encoding="utf-8")
    rc, info = T.forge(rules_path, tmp_path / "scene")
    assert rc == T.OK, info
    assert info["segments"] > 0 and info["leaves"] > 0
    rc, verified = T.verify(tmp_path / "scene")
    assert rc == T.OK
    assert verified["state"] == "VERIFIED"
    # the browser probe is absent here, so the cross-language leg must say NOT-RUN rather
    # than claim a match it never made
    assert verified["browser"]["state"] == "NOT-RUN"


def test_verify_refuses_a_hand_edited_rule(tmp_path):
    source = tmp_path / "anim.html"
    source.write_text(COMPLETE, encoding="utf-8")
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps(T.extract(source)), encoding="utf-8")
    rc, _info = T.forge(rules_path, tmp_path / "scene")
    assert rc == T.OK
    mutated = json.loads((tmp_path / "scene" / "rules.json").read_text(encoding="utf-8"))
    mutated["fractal"]["len_shrink_base"] = 0.99
    (tmp_path / "scene" / "rules.json").write_text(json.dumps(mutated), encoding="utf-8")
    rc, refused = T.verify(tmp_path / "scene")
    assert rc == T.REFUSED
    assert refused["state"] == "TAMPERED"


def test_bind_shard_refuses_a_shard_that_does_not_hold_the_source(tmp_path):
    source = tmp_path / "anim.html"
    source.write_text(COMPLETE, encoding="utf-8")
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps(T.extract(source)), encoding="utf-8")
    shard = tmp_path / "shard.json"
    shard.write_text(json.dumps({"genre": "doc-only", "entrypoint": "",
                                 "files": [{"path": "other.html", "sha256": "0" * 64}]}),
                     encoding="utf-8")
    rc, refused = T.bind_shard(rules_path, shard)
    assert rc == T.REFUSED
    assert refused["state"] == "SOURCE-NOT-IN-SHARD"
    # and nothing was written into the shard
    assert "transubstantiation" not in json.loads(shard.read_text(encoding="utf-8"))


def test_bind_shard_records_the_link_when_the_source_is_present(tmp_path):
    source = tmp_path / "anim.html"
    source.write_text(COMPLETE, encoding="utf-8")
    rules = T.extract(source)
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps(rules), encoding="utf-8")
    shard = tmp_path / "shard.json"
    shard.write_text(json.dumps({"genre": "doc-only", "entrypoint": "",
                                 "files": [{"path": "anim.html",
                                            "sha256": rules["source"]["sha256"]}]}),
                     encoding="utf-8")
    rc, info = T.bind_shard(rules_path, shard)
    assert rc == T.OK, info
    doc = json.loads(shard.read_text(encoding="utf-8"))
    assert doc["transubstantiation"]["source_sha256"] == rules["source"]["sha256"]
    assert doc["transubstantiation"]["geometry_sha256"] == info["geometry_sha256"]
    # a shard that carries a transubstantiable animation is no longer doc-only
    assert doc["genre"] == "canvas-animation"
    assert doc["entrypoint"] == "anim.html"


def test_selftest_reports_pass():
    rc, lines = T.selftest()
    assert rc == 0, "\n".join(lines)
    assert any("negative control refused" in line for line in lines)
