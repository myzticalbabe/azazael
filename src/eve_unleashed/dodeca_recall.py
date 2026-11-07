"""Shape-parametric recall: a matrix is rectangular, so we do not use one.

The recall layer maps memory onto a regular solid. The default solid is
the dodecahedron -- 20 vertices, degree 3, diameter 5, girth 5, 12
pentagonal faces (G(10,2)). Recall walks outward from the query's home
vertex: exact hits live ON the home vertex (distance 0 -- the key IS the
address), context surfaces nearest-first, full coverage costs at most the
diameter. That bound is the recall guarantee; ordering, not wall-time, is
what "instantaneous" honestly means at this size.

MORPH-SPACE (hyper-optimization goal): the solid is a parameter, not a
constant. `SHAPES` registers every solid behind one interface; Eve morphs
by naming a shape, and Lillith can later tune the shape itself:

  dodecahedron  20 slots / deg 3 / diam 5  -- balanced default
  petersen      10 slots / deg 3 / diam 2  -- few hot hosts, 2-hop cover
  hypercube-32  32 slots / deg 5 / diam 5  -- larger, same cover as dodeca
  g40           40 slots / deg 3 / diam 7  -- largest, 7-hop cover
  complete-20   20 slots / deg 19 / diam 1  -- broadcast: no order possible
  cycle-20      20 slots / deg 2 / diam 10  -- cheapest edges, slowest cover
  icosahedron   12 slots / deg 5 / diam 3  -- hub shape (NEXT to land)

Rule: few hot keys -> small diameter (petersen); many keys where order
matters -> dodecahedron; broadcast with no nearest-first -> complete.
Measured in tests/test_dodeca_recall.py::test_morph_space_diameters.
"""

from __future__ import annotations

import hashlib
from collections import deque
from typing import Any, Callable, Dict, List, Tuple

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

_DN = 10  # dodecahedron ring size (G(10,2))
_PN = 5  # petersen ring size (G(5,2))
N_VERTICES = 20  # slots on the default solid (kept for callers)


def dodeca_neighbors(v: int) -> List[int]:
    """G(10,2): outer 10-ring + spokes + inner star steps of 2."""
    if not 0 <= v < 20:
        raise ValueError(f"vertex {v!r} not on the dodecahedron")
    if v < _DN:
        i = v
        return sorted([(i - 1) % _DN, (i + 1) % _DN, _DN + i])
    i = v - _DN
    return sorted([i, _DN + (i - 2) % _DN, _DN + (i + 2) % _DN])


def petersen_neighbors(v: int) -> List[int]:
    """G(5,2): outer 5-ring + spokes + inner pentagram steps of 2."""
    if not 0 <= v < 10:
        raise ValueError(f"vertex {v!r} not on the petersen")
    if v < _PN:
        i = v
        return sorted([(i - 1) % _PN, (i + 1) % _PN, _PN + i])
    i = v - _PN
    return sorted([i, _PN + (i - 2) % _PN, _PN + (i + 2) % _PN])


def cycle_neighbors(n: int) -> Callable[[int], List[int]]:
    """C_n: the rectangular extreme -- degree 2, diameter n//2."""
    def _nbr(v: int) -> List[int]:
        if not 0 <= v < n:
            raise ValueError(f"vertex {v!r} not on the cycle")
        return sorted([(v - 1) % n, (v + 1) % n])
    return _nbr


def complete_neighbors(n: int) -> Callable[[int], List[int]]:
    """K_n: the broadcast extreme -- diameter 1, no ordering possible."""
    def _nbr(v: int) -> List[int]:
        if not 0 <= v < n:
            raise ValueError(f"vertex {v!r} not on the complete graph")
        return [w for w in range(n) if w != v]
    return _nbr


def generalized_petersen(n: int) -> Callable[[int], List[int]]:
    """G(n,2): outer n-ring + spokes + inner star steps of 2.

    G(5,2) is the Petersen, G(10,2) the dodecahedron; larger n grows
    the solid (more slots, longer cover). Measured: G(20,2) = 40 slots,
    degree 3, diameter 7.
    """
    def _nbr(x: int) -> List[int]:
        if not 0 <= x < 2 * n:
            raise ValueError(f"vertex {x!r} not on G({n},2)")
        if x < n:
            i = x
            return sorted([(i - 1) % n, (i + 1) % n, n + i])
        i = x - n
        return sorted([i, n + (i - 2) % n, n + (i + 2) % n])
    return _nbr


def hypercube(d: int) -> Callable[[int], List[int]]:
    """Q_d: 2^d vertices, degree d, diameter d. Bit-flip edges."""
    n = 2 ** d

    def _nbr(v: int) -> List[int]:
        if not 0 <= v < n:
            raise ValueError(f"vertex {v!r} not on Q_{d}")
        return sorted([v ^ (1 << b) for b in range(d)])
    return _nbr


# name -> (vertex count, neighbor function)
SHAPES: Dict[str, Tuple[int, Callable[[int], List[int]]]] = {
    "dodecahedron": (20, dodeca_neighbors),
    "petersen": (10, petersen_neighbors),
    "cycle-20": (20, cycle_neighbors(20)),
    "complete-20": (20, complete_neighbors(20)),
    "hypercube-32": (32, hypercube(5)),
    "g40": (40, generalized_petersen(20)),
}


def bfs_distances(home: int, n: int,
                  nbr: Callable[[int], List[int]]) -> Dict[int, int]:
    """Shortest-path distance from home to every vertex."""
    dist = {home: 0}
    queue = deque([home])
    while queue:
        x = queue.popleft()
        for y in nbr(x):
            if y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


def diameter(n: int, nbr: Callable[[int], List[int]]) -> int:
    """Worst-case hops to cover the solid: the morph-space coordinate."""
    return max(max(bfs_distances(v, n, nbr).values()) for v in range(n))


def home_of(key: str, n: int) -> int:
    """Stable home vertex for a key (md5, never salted-hash)."""
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % n


class ShapeStore:
    """N slots, one per vertex of the named solid. Morph by naming a shape."""

    def __init__(self, shape: str = "dodecahedron") -> None:
        if shape not in SHAPES:
            raise ValueError(f"unknown shape {shape!r}; SHAPES={sorted(SHAPES)}")
        self.shape = shape
        self.n, self.nbr = SHAPES[shape]
        self.slots: Dict[int, List[Tuple[str, Any]]] = {
            v: [] for v in range(self.n)}

    def put(self, key: str, value: Any) -> int:
        """Store value under key. Returns the home vertex."""
        home = home_of(key, self.n)
        self.slots[home].append((key, value))
        return home

    def recall(self, key: str, radius: int = None) -> Dict[str, Any]:
        """Walk outward from key's home vertex; collect nearest-first.

        `exact`: entries under key (home vertex, distance 0). `context`:
        everything else within radius, distance-ordered. Default radius
        covers the whole solid: at most `diameter` hops, the guarantee.
        """
        if radius is None:
            radius = diameter(self.n, self.nbr)
        home = home_of(key, self.n)
        dist = bfs_distances(home, self.n, self.nbr)
        order = sorted(range(self.n), key=lambda v: (dist[v], v))
        exact: List[Tuple[int, str, Any]] = []
        context: List[Tuple[int, str, Any]] = []
        visited = 0
        hops = 0
        for v in order:
            d = dist[v]
            if d > radius:
                break
            visited += 1
            hops = max(hops, d)
            for k, val in self.slots[v]:
                (exact if k == key else context).append((d, k, val))
        return {"exact": exact, "context": context, "hops": hops,
                "visited": visited, "home": home, "shape": self.shape}

    def matrix_scan(self, key: str) -> Dict[str, Any]:
        """Rectangular baseline: row-major scan, scan order, full visit."""
        home = home_of(key, self.n)
        dist = bfs_distances(home, self.n, self.nbr)
        exact: List[Tuple[int, str, Any]] = []
        context: List[Tuple[int, str, Any]] = []
        for v in range(self.n):  # slot order, not distance order
            for k, val in self.slots[v]:
                (exact if k == key else context).append((dist[v], k, val))
        return {"exact": exact, "context": context, "visited": self.n}


def morph_store(store: ShapeStore, shape: str) -> ShapeStore:
    """Morph every entry onto a new solid. Entries survive; addresses change.

    This is the hyper-optimization move: when the workload outgrows the
    solid (too many keys colliding per vertex, or cover hops dominating),
    re-index onto a larger or smaller shape. Returns the new store.
    """
    new = ShapeStore(shape)
    for v in range(store.n):
        for k, val in store.slots[v]:
            new.put(k, val)
    return new


class DodecaStore(ShapeStore):
    """The default solid. Kept by name: the canon was written for it."""

    def __init__(self) -> None:
        super().__init__("dodecahedron")


# backwards-compatible module-level helpers (dodecahedron default)
def neighbors(v: int) -> List[int]:
    return dodeca_neighbors(v)


def bfs_order(home: int) -> List[int]:
    dist = bfs_distances(home, 20, dodeca_neighbors)
    return sorted(range(20), key=lambda v: (dist[v], v))


def index_live_log(log_path: str, store: ShapeStore = None) -> ShapeStore:
    """Map a live-log's fetch answers onto vertices, keyed by host."""
    import json as _json
    from urllib.parse import urlparse as _parse
    store = store or DodecaStore()
    with open(log_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = _json.loads(line)
            except ValueError as e:
                note_failure("dodeca:index:bad-line", e)
                continue
            if ev.get("phase") != "fetch" or ev.get("event") != "answer":
                continue
            url = ev.get("url", "")
            host = _parse(url).netloc or url
            store.put(host, {"rung": ev.get("rung"),
                             "state": ev.get("state"),
                             "kind": ev.get("kind")})
    return store


def recall_host(store: ShapeStore, host: str) -> Dict[str, Any]:
    """What do we know about this host, nearest memory first."""
    return store.recall(host)
