"""Dodecahedron recall: topology invariants + recall behavior.

Topology pins the implementation to G(10,2) -- 20 vertices, 30 edges,
3-regular, connected, diameter 5, girth 5, exactly 12 five-cycles (the
faces). Measured independently before baking in.
"""

import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed import dodeca_recall as D
from eve_unleashed import live_log as L


def _all_edges():
    seen = set()
    for v in range(D.N_VERTICES):
        for w in D.neighbors(v):
            seen.add((min(v, w), max(v, w)))
    return seen


def test_morph_space_diameters():
    assert D.diameter(10, D.petersen_neighbors) == 2
    assert D.diameter(20, D.dodeca_neighbors) == 5
    assert D.diameter(20, D.cycle_neighbors(20)) == 10
    assert D.diameter(20, D.complete_neighbors(20)) == 1
    assert D.diameter(32, D.hypercube(5)) == 5
    assert D.diameter(40, D.generalized_petersen(20)) == 7


def test_larger_solids_are_sound():
    n32, h32 = D.SHAPES["hypercube-32"]
    assert n32 == 32 and all(len(h32(v)) == 5 for v in range(32))
    assert len(D.bfs_distances(0, 32, h32)) == 32
    n40, g40 = D.SHAPES["g40"]
    assert n40 == 40 and all(len(g40(v)) == 3 for v in range(40))
    assert len(D.bfs_distances(0, 40, g40)) == 40


def _prism(v: int) -> list:
    """Triangular prism: 6 vertices, degree 3, diameter 2."""
    if not 0 <= v < 6:
        raise ValueError(v)
    if v < 3:
        return sorted([(v - 1) % 3, (v + 1) % 3, v + 3])
    i = v - 3
    return sorted([i, 3 + (i - 1) % 3, 3 + (i + 1) % 3])


def test_transmogrify_registers_any_valid_form():
    D.transmogrify("prism-6", 6, _prism)
    st = D.ShapeStore("prism-6")
    assert st.n == 6
    st.put("k", "v")
    assert st.recall("k")["exact"][0][0] == 0
    assert D.diameter(6, _prism) == 2


def test_transmogrify_refuses_broken_forms():
    import pytest as _p
    with _p.raises(ValueError):
        D.transmogrify("tiny", 3, lambda v: [])
    with _p.raises(ValueError):
        D.transmogrify("loopy", 6, lambda v: [v])
    with _p.raises(ValueError):
        D.transmogrify("split", 6,
                       lambda v: [u for u in _prism(v) if (u < 3) == (v < 3)])


def test_mutate_rewires_but_keeps_degree_and_cover():
    import random as _r
    new_name, diam = D.mutate_shape("dodecahedron", swaps=3,
                                    rng=_r.Random(316))
    n, nbr = D.SHAPES[new_name]
    assert n == 20 and all(len(nbr(v)) == 3 for v in range(20))
    assert len(D.bfs_distances(0, 20, nbr)) == 20
    st = D.ShapeStore(new_name)
    st.put("mk", "mv")
    assert [m[1] for m in st.recall("mk")["exact"]] == ["mk"]


def test_transsubstantiate_rehomes_every_entry():
    src = D.DodecaStore()
    src.put("a.example", {"rung": "archive"})
    src.put("b.example", {"rung": "render"})
    new = D.transsubstantiate(src, lambda k, v: v["rung"])
    assert new.shape == "dodecahedron"
    got = new.recall("archive")["exact"]
    assert [m[1] for m in got] == ["archive"]  # re-homed under rung
    assert got[0][2] == {"rung": "archive"}  # substance (value) survives
    assert [m[1] for m in new.recall("render")["exact"]] == ["render"]
    assert new.recall("a.example")["exact"] == []  # old keys are gone


def test_swarm_hypercubes_fan_out_and_merge():
    sw = D.SwarmStore("hypercube-32", shards=4)
    keys = ["h%d.example" % i for i in range(40)]
    homes = {k: sw.put(k, k + "-val") for k in keys}
    assert len({s for s, _ in homes.values()}) > 1  # spread happened
    for k in keys:
        res = sw.recall(k)
        assert [m[1] for m in res["exact"]] == [k]
        assert res["exact"][0][0] == 0
        dists = [(m[0], m[1]) for m in res["context"]]
        assert dists == sorted(dists)  # merged nearest-first
    assert sw.recall("never-seen")["exact"] == []


def test_morph_preserves_every_entry():
    small = D.ShapeStore("dodecahedron")
    keys = [f"host-{i}.example" for i in range(25)]  # more keys than slots
    for k in keys:
        small.put(k, k + "-val")
    big = D.morph_store(small, "g40")
    assert big.shape == "g40" and big.n == 40
    for k in keys:
        res = big.recall(k)
        assert [m[1] for m in res["exact"]] == [k]
        assert res["exact"][0][0] == 0
    down = D.morph_store(big, "petersen")
    for k in keys:
        assert [m[1] for m in down.recall(k)["exact"]] == [k]
    assert len(_all_edges()) == 30
    assert all(len(D.neighbors(v)) == 3 for v in range(20))
    for v in range(20):
        assert len(D.bfs_distances(v, 20, D.dodeca_neighbors)) == 20  # connected


def test_diameter_is_five():
    diam = max(max(D.bfs_distances(v, 20, D.dodeca_neighbors).values())
               for v in range(20))
    assert diam == 5


def test_girth_is_five():
    def girth_at(s):
        depth = {s: 0}
        parent = {s: None}
        q = deque([s])
        best = None
        while q:
            x = q.popleft()
            for y in D.neighbors(x):
                if y == parent[x]:
                    continue
                if y in depth:
                    c = depth[x] + depth[y] + 1
                    if best is None or c < best:
                        best = c
                else:
                    parent[y] = x
                    depth[y] = depth[x] + 1
                    q.append(y)
        return best
    assert min(girth_at(v) for v in range(20)) == 5


def test_twelve_pentagonal_faces():
    found = set()
    def dfs(path):
        if len(path) == 5:
            if path[0] in D.neighbors(path[-1]):
                rots = [tuple(path[i:] + path[:i]) for i in range(5)]
                rev = tuple(reversed(path))
                rots += [tuple(rev[i:] + rev[:i]) for i in range(5)]
                found.add(min(rots))
            return
        for y in D.neighbors(path[-1]):
            if y not in path:
                dfs(path + [y])
    for v in range(20):
        dfs([v])
    assert len(found) == 12


def test_recall_finds_seeded_item_within_five_hops():
    store = D.DodecaStore()
    store.put("alpha", {"rung": "example", "state": "ok"})
    res = store.recall("alpha")
    assert len(res["exact"]) == 1
    assert res["exact"][0][1:] == ("alpha", {"rung": "example", "state": "ok"})
    assert res["exact"][0][0] == 0  # the key IS the address: instantaneous
    assert res["hops"] <= 5 and res["visited"] <= 20


def test_recall_reaches_antipode():
    store = D.DodecaStore()
    # plant a foreign entry at max distance from far-key's home vertex
    home = D.home_of("far-key", 20)
    dist = D.bfs_distances(home, 20, D.dodeca_neighbors)
    anti = max(dist, key=lambda v: dist[v])
    assert dist[anti] == 5
    store.slots[anti].append(("pole-marker", "x"))  # planted at far pole
    res = store.recall("far-key")
    far = [c for c in res["context"] if c[1] == "pole-marker"]
    assert len(far) == 1 and far[0][0] == 5
    assert res["hops"] == 5  # full coverage costs the diameter, no more


def test_recall_is_distance_ordered_and_matches_matrix_set():
    store = D.DodecaStore()
    for k in ["k1", "k2", "k3", "k1", "k2"]:
        store.put(k, k + "-val")
    for key in ["k1", "k2", "k3"]:
        walk = store.recall(key)
        scan = store.matrix_scan(key)
        assert [m[1:] for m in walk["exact"]] == [m[1:] for m in scan["exact"]]
        assert {m[1:] for m in walk["context"]} == {m[1:] for m in scan["context"]}
        dists = [m[0] for m in walk["context"]]
        assert dists == sorted(dists)  # nearest context first, always
        assert walk["visited"] <= scan["visited"]


def test_recall_unknown_key_is_empty_not_an_error():
    res = D.DodecaStore().recall("never-seen")
    assert res["exact"] == [] and res["context"] == []


def test_live_log_index_and_host_recall(tmp_path):
    log = str(tmp_path / "t.jsonl")
    L.emit("fetch", "intuition", path=log, url="https://example.com",
           guess="guess", confidence=0.9, predicted="example")
    L.emit("fetch", "answer", path=log, url="https://example.com",
           rung="example", state="ok", kind="live")
    L.emit("fetch", "answer", path=log, url="http://unseen-train.invalid/",
           rung="commoncrawl", state="blocked", kind="wall")
    store = D.index_live_log(log)
    res = D.recall_host(store, "example.com")
    assert len(res["exact"]) == 1
    assert res["exact"][0][2]["rung"] == "example"
    assert res["exact"][0][0] == 0  # own home vertex: instantaneous
    assert D.recall_host(store, "no-such-host")["exact"] == []
