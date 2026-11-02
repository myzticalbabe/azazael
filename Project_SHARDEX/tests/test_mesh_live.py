#!/usr/bin/env python
# coding: utf-8
"""Tests for the live-mutation path: operators, the chain, and the flat-field refusal.

Nothing here renders. What it pins down is the part a reviewer cannot eyeball: that an op is a
pure function of (mesh, op), that the chain changes when any op changes, and that a field with
no structure is refused rather than extruded into noise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Project_SHARDEX"))
sys.path.insert(0, str(ROOT / "Project_SHARDEX" / "tests"))

import ops as OPS        # noqa: E402
import meshscene as M    # noqa: E402


def field(edge_value: int = 40, w: int = 12, h: int = 8) -> dict:
    cells = w * h
    return {"shape": M.FIELD_SHAPE,
            "source": {"path": "x.png", "sha256": "a" * 64, "w": w, "h": h},
            "grid": {"w": w, "h": h},
            "luma": [((i * 37) % 256) for i in range(cells)],
            "hue": [(i * 11) % 360 for i in range(cells)],
            "edge": [edge_value] * cells,
            "variance": 50.0,
            "palette": [{"h": 30, "w": 1.0}],
            "sine_q15": OPS.sine_table()}


def test_a_flat_field_is_refused(tmp_path):
    flat = field(edge_value=0)
    path = tmp_path / "flat.json"
    path.write_text(json.dumps(flat), encoding="utf-8")
    rc, info = M.forge(path, tmp_path / "out")
    assert rc == M.REFUSED
    assert info["state"] == "FLAT-FIELD"


def test_mesh_build_is_deterministic(tmp_path):
    a = M.build_mesh(field())
    b = M.build_mesh(field())
    assert OPS.mesh_digest(a) == OPS.mesh_digest(b)
    assert a["counts"]["neurons"] > 0


def test_operators_are_pure(tmp_path):
    mesh = M.build_mesh(field())
    before = OPS.mesh_digest(mesh)
    table = OPS.sine_table()
    OPS.apply_op(mesh, {"kind": "warp", "amp": 2.0, "freq": 1.0, "phase": 10}, table)
    assert OPS.mesh_digest(mesh) == before, "apply_op mutated its input mesh"


def test_sprout_and_prune_move_the_topology():
    mesh = M.build_mesh(field())
    table = OPS.sine_table()
    base = len(mesh["synapses"])
    sprouted = OPS.apply_op(mesh, {"kind": "sprout", "n": 5, "min_gap": 1}, table)
    assert len(sprouted["synapses"]) > base
    pruned = OPS.apply_op(sprouted, {"kind": "prune", "threshold": 0.5}, table)
    assert len(pruned["synapses"]) < len(sprouted["synapses"])


def test_unknown_op_field_is_refused():
    mesh = M.build_mesh(field())
    with pytest.raises(OPS.OpError):
        OPS.apply_op(mesh, {"kind": "warp", "amp": 1, "freq": 1, "phase": 0, "spin": 2},
                     OPS.sine_table())
    with pytest.raises(OPS.OpError):
        OPS.apply_op(mesh, {"kind": "transmogrify"}, OPS.sine_table())


def test_chain_hash_changes_with_any_op():
    a = [{"kind": "warp", "amp": 1, "freq": 1, "phase": 0}]
    b = [{"kind": "warp", "amp": 2, "freq": 1, "phase": 0}]
    assert OPS.chain_hash(a) != OPS.chain_hash(b)
    two = a + [{"kind": "extrude", "gain": 2}]
    assert OPS.chain_hash(two) != OPS.chain_hash(a)


def test_replay_reproduces_every_intermediate_digest():
    mesh = M.build_mesh(field())
    table = OPS.sine_table()
    ops = [{"kind": "warp", "amp": 1.5, "freq": 1.0, "phase": 3},
           {"kind": "palette", "shift": 90},
           {"kind": "extrude", "gain": 2.0}]
    _final, digests = OPS.replay(mesh, ops, table)
    # replaying the same log from the same base must land on the same digests
    _again, digests2 = OPS.replay(mesh, ops, table)
    assert digests == digests2
    assert len(digests) == len(ops)


def test_touch_moves_only_the_picked_neighbourhood():
    mesh = M.build_mesh(field())
    table = OPS.sine_table()
    index = len(mesh["neurons"]) // 2
    node = mesh["neurons"][index]
    # radius 2 on a 12x8 field: neighbours sit one cell away, and the falloff at exactly the
    # rim is zero, so a radius of 1 would be a legal op that moved nothing.
    touched = OPS.apply_op(mesh, {"kind": "touch", "neuron": index, "radius": 2.0,
                                 "gain": 0.5}, table)
    # the pick itself is the centre of the falloff and therefore cannot move
    assert touched["neurons"][index][:2] == node[:2]
    moved = [i for i, n in enumerate(touched["neurons"]) if n[:2] != mesh["neurons"][i][:2]]
    assert moved, "touch displaced nothing -- the radius was too small for this mesh"
    assert index not in moved
    assert len(moved) < len(mesh["neurons"]), "touch behaved like a global warp"


def test_touch_refuses_a_neuron_that_is_not_there():
    mesh = M.build_mesh(field())
    with pytest.raises(OPS.OpError):
        OPS.apply_op(mesh, {"kind": "touch", "neuron": len(mesh["neurons"]), "radius": 1,
                            "gain": 0.5}, OPS.sine_table())
    with pytest.raises(OPS.OpError):
        OPS.apply_op(mesh, {"kind": "touch", "neuron": 0, "radius": 0, "gain": 0.5},
                     OPS.sine_table())


def test_verify_refuses_a_touch_op_with_no_pick_record(tmp_path):
    """A hand-typed index replays perfectly. Only picked.json can tell it from a click."""
    path = tmp_path / "field.json"
    path.write_text(json.dumps(field()), encoding="utf-8")
    out = tmp_path / "out"
    rc, _info = M.forge(path, out)
    assert rc == M.OK
    base = json.loads((out / "mesh.json").read_text(encoding="utf-8"))
    table = OPS.sine_table()
    op = {"kind": "touch", "neuron": 3, "radius": 0.5, "gain": 0.4}
    after = OPS.apply_op(base, op, table)
    record = {"seq": 0, "op": op, "digest": OPS.mesh_digest(after),
              "neurons": len(after["neurons"]), "synapses": len(after["synapses"])}
    (out / "applied_ops.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    rc, info = M.verify(out)
    assert rc == M.REFUSED
    assert info["state"] == "PICK-UNPROVENANCED"


def test_verify_refuses_a_log_that_does_not_replay(tmp_path):
    fld = field()
    path = tmp_path / "field.json"
    path.write_text(json.dumps(fld), encoding="utf-8")
    out = tmp_path / "out"
    rc, _info = M.forge(path, out)
    assert rc == M.OK
    mesh = json.loads((out / "mesh.json").read_text(encoding="utf-8"))
    # a log whose digest was never produced by this base mesh
    forged = {"seq": 0, "op": {"kind": "palette", "shift": 40}, "digest": "deadbeefdeadbeef",
              "neurons": 1, "synapses": 1}
    (out / "applied_ops.jsonl").write_text(json.dumps(forged) + "\n", encoding="utf-8")
    rc, info = M.verify(out)
    assert rc == M.REFUSED
    assert info["state"] == "DIGEST-DIVERGENCE"
    assert mesh["field_sha256"] == fld["source"]["sha256"]
