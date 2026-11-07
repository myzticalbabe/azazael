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


def transmogrify(name: str, n: int,
                 nbr: Callable[[int], List[int]]) -> str:
    """Register ANY neighbor-function as a new solid. Validated, or refused.

    Refuses: vertex out of range, self-loop, disconnected graph. Returns
    the name on success -- this is 'any form wanted', with a bouncer."""
    if n < 4:
        raise ValueError(f"a solid needs >= 4 vertices, got {n}")
    for v in range(n):
        for w in nbr(v):
            if not 0 <= w < n:
                raise ValueError(f"vertex {v} reaches off-solid {w}")
            if w == v:
                raise ValueError(f"vertex {v} loops to itself")
    if len(bfs_distances(0, n, nbr)) != n:
        raise ValueError(f"{name}: graph is disconnected")
    SHAPES[name] = (n, nbr)
    return name


def mutate_shape(name: str, swaps: int = 3,
                 rng: "random.Random | None" = None,
                 prefix: str = "mut") -> Tuple[str, int]:
    """Rewire a registered solid's edges; register the variant; report it.

    Edge-swaps preserve the degree sequence (swap (a,b),(c,d) for
    (a,d),(c,b)); rejects swaps that duplicate an edge or self-loop, and
    refuses a disconnected result. Returns (new_name, measured_diameter)."""
    import random as _random
    rng = rng or _random.Random()
    if name not in SHAPES:
        raise ValueError(f"unknown shape {name!r}; SHAPES={sorted(SHAPES)}")
    n, nbr = SHAPES[name]
    adj: Dict[int, set] = {v: set(nbr(v)) for v in range(n)}
    edges = sorted({tuple(sorted((v, w))) for v in range(n) for w in adj[v]})
    have = {tuple(sorted(e)) for e in edges}
    done = 0
    tries = 0
    while done < swaps and tries < swaps * 50:
        tries += 1
        (a, b), (c, d) = rng.sample(edges, 2)
        if len({a, b, c, d}) < 4:
            continue
        e1, e2 = tuple(sorted((a, d))), tuple(sorted((c, b)))
        if e1 in have or e2 in have:
            continue
        for x, y in ((a, b), (c, d)):
            adj[x].discard(y)
            adj[y].discard(x)
        for x, y in ((a, d), (c, b)):
            adj[x].add(y)
            adj[y].add(x)
        edges = sorted({tuple(sorted((v, w)))
                        for v in range(n) for w in adj[v]})
        have = {tuple(sorted(e)) for e in edges}
        done += 1
    frozen = {v: sorted(ws) for v, ws in adj.items()}

    def _mut(v: int) -> List[int]:
        return list(frozen[v])
    if len(bfs_distances(0, n, _mut)) != n:
        raise ValueError(f"mutation of {name} disconnected the solid")
    new_name = f"{prefix}-{name}-{done}sw"
    SHAPES[new_name] = (n, _mut)
    return new_name, diameter(n, _mut)


def transsubstantiate(store: ShapeStore,
                      key_fn: Callable[[str, Any], str],
                      shape: str = None) -> ShapeStore:
    """Change what the vertices HOLD: re-home every entry under new keys.

    Same graph (or a named new one); new addressing substance. Entries
    survive; addresses change. The deepest morph: accidents kept, substance
    swapped."""
    new = ShapeStore(shape or store.shape)
    for v in range(store.n):
        for k, val in store.slots[v]:
            new.put(key_fn(k, val), val)
    return new


class SwarmStore:
    """Swarm the recall: keys sharded across stores, recall fans out.

    Each shard is a full solid (default hypercube-32). put lands on one
    shard; recall asks every shard and merges context by (distance, shard)
    while exact hits stay exact. The swarm is the shape, multiplied."""

    def __init__(self, shape: str = "hypercube-32", shards: int = 4) -> None:
        if shards < 1:
            raise ValueError(f"a swarm needs >= 1 shard, got {shards}")
        self.shape = shape
        self.stores = [ShapeStore(shape) for _ in range(shards)]

    def _shard(self, key: str) -> int:
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) \
            % len(self.stores)

    def put(self, key: str, value: Any) -> Tuple[int, int]:
        """Store value; returns (shard, home vertex)."""
        s = self._shard(key)
        return s, self.stores[s].put(key, value)

    def recall(self, key: str, radius: int = None) -> Dict[str, Any]:
        """Fan out to every shard; merge. Exact stays exact."""
        exact: List[Tuple[int, str, Any]] = []
        context: List[Tuple[int, int, str, Any]] = []
        hops = visited = 0
        for i, st in enumerate(self.stores):
            res = st.recall(key, radius=radius)
            exact.extend(res["exact"])
            context.extend((d, i, k, v)
                           for d, k, v in res["context"])
            hops = max(hops, res["hops"])
            visited += res["visited"]
        context.sort(key=lambda m: (m[0], m[1]))
        return {"exact": exact, "context": context, "hops": hops,
                "visited": visited, "shards": len(self.stores),
                "shape": self.shape}

    def count(self) -> int:
        """Total entries across all shards."""
        return sum(len(sl) for st in self.stores for sl in st.slots.values())

    def _all_entries(self) -> List[Tuple[str, Any]]:
        return [(k, v) for st in self.stores for sl in st.slots.values()
                for k, v in sl]

    def rebalance(self, shards: int) -> int:
        """Rebuild the swarm at a new shard count; every entry re-homed.

        The shard function changes with the count, so all entries move.
        Returns the new shard count."""
        if shards < 1:
            raise ValueError(f"a swarm needs >= 1 shard, got {shards}")
        entries = self._all_entries()
        self.stores = [ShapeStore(self.shape) for _ in range(shards)]
        for k, v in entries:
            self.put(k, v)
        return len(self.stores)

    def grow(self, n: int = 1) -> int:
        """MULTIPLY: add shards and rebalance. Returns the new count."""
        return self.rebalance(len(self.stores) + n)

    def shrink(self, n: int = 1) -> int:
        """Divide the swarm down, never below one. Returns the new count."""
        return self.rebalance(len(self.stores) - n)


def cast_projection(store: ShapeStore, genome: Dict[str, Any],
                    provenance: Dict[str, Any] = None) -> Dict[str, Any]:
    """PROJECTION: cast the finished stone -- in ALL forms, not one.

    Gold comes in all forms, so the artifact is three: JSON (portable,
    inspectable, reloads entries anywhere), a frozen .py module (importable
    gold: rebuilds the store with no trainer), and a .md chronicle (the
    lineage record: who, what solid, what was learned). Returns the three
    texts plus the payload dict.

    Constraint, stated not hidden: the .py form embeds values as literals,
    so values must be repr-literals. The JSON form carries anything
    json-serializable (default=str beyond that)."""
    import datetime as _dt
    import json as _json
    entries = [(k, v) for v in range(store.n) for k, v in store.slots[v]]
    prov = dict(provenance or {})
    prov.setdefault("cast_utc",
                    _dt.datetime.now(_dt.timezone.utc).isoformat())
    payload = {"shape": store.shape, "slots": store.n,
               "diameter": diameter(store.n, store.nbr),
               "genome": dict(genome),
               "hunches": list(genome.get("hunches") or []),
               "entries": entries, "provenance": prov}
    gid = genome.get("worm_id", "?")
    json_text = _json.dumps(payload, indent=2, default=str)
    py_text = (
        '"""Cast stone: {shape} + genome {gid}. Frozen; needs no trainer."""\n'
        "from eve_unleashed.dodeca_recall import ShapeStore\n\n"
        "SHAPE = {shape!r}\nGENOME = {genome!r}\n"
        "HUNCHES = {hunches!r}\nENTRIES = {entries!r}\n\n"
        "def load():\n"
        "    st = ShapeStore(SHAPE)\n"
        "    for k, v in ENTRIES:\n"
        "        st.put(k, v)\n"
        "    return st\n"
    ).format(shape=store.shape, gid=gid, genome=dict(genome),
             hunches=list(genome.get("hunches") or []), entries=entries)
    md_lines = [f"# Cast stone: `{gid}`", "",
                f"- solid: **{store.shape}** "
                f"({store.n} slots, diameter "
                f"{diameter(store.n, store.nbr)})",
                f"- lineage: gen {genome.get('generation', '?')}, "
                f"parents {genome.get('parent_ids', [])}",
                f"- hunches: {list(genome.get('hunches') or [])}",
                f"- entries: {len(entries)}",
                f"- cast: {prov['cast_utc']}", "",
                "## genes", ""]
    for gene in ("aggressiveness", "min_confidence", "cooldown_s",
                 "scan_interval_s", "resource_budget_mb",
                 "mutation_rate"):
        md_lines.append(f"- {gene}: {genome.get(gene, '?')}")
    md_lines += ["", "## provenance", ""]
    for k, v in prov.items():
        if k != "cast_utc":
            md_lines.append(f"- {k}: {v}")
    return {"json": json_text, "py": py_text,
            "md": "\n".join(md_lines) + "\n", "payload": payload}


def write_projection(store: ShapeStore, genome: Dict[str, Any],
                     base_path: str,
                     provenance: Dict[str, Any] = None) -> List[str]:
    """Write all three forms to <base>.json / <base>.py / <base>.md."""
    cast = cast_projection(store, genome, provenance)
    paths = []
    for ext in ("json", "py", "md"):
        p = f"{base_path}.{ext}"
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(cast[ext])
        paths.append(p)
    return paths


#: The shipped solids. Custom registrations may dissolve; these may not.
BUILTIN_SHAPES = frozenset(["dodecahedron", "petersen", "cycle-20",
                            "complete-20", "hypercube-32", "g40"])


def conjoin(a: ShapeStore, b: ShapeStore, shape: str = None) -> ShapeStore:
    """CONJOIN: marry two stores onto one solid. Every entry survives.

    Defaults to the larger solid; same key in both yields both entries
    (recall exact shows the full marriage, no silent winner)."""
    shape = shape or (a.shape if a.n >= b.n else b.shape)
    new = ShapeStore(shape)
    for st in (a, b):
        for v in range(st.n):
            for k, val in st.slots[v]:
                new.put(k, val)
    return new


def separate(store: ShapeStore, pred: Callable[[str, Any], bool],
             shape: str = None) -> Tuple[ShapeStore, ShapeStore]:
    """SEPARATE: divide one store by predicate. (match, rest).

    Disjoint and complete: every entry lands in exactly one child."""
    shape = shape or store.shape
    match, rest = ShapeStore(shape), ShapeStore(shape)
    for v in range(store.n):
        for k, val in store.slots[v]:
            (match if pred(k, val) else rest).put(k, val)
    return match, rest


def dissolve_key(store: ShapeStore, key: str) -> int:
    """DISSOLVE (entry): remove every entry under key. Returns the count."""
    sl = store.slots[home_of(key, store.n)]
    before = len(sl)
    sl[:] = [(k, v) for k, v in sl if k != key]
    return before - len(sl)


def unregister_shape(name: str) -> str:
    """DISSOLVE (solid): burn a custom registration back to nothing.

    Builtins refuse -- the shipped solids are load-bearing. Existing
    stores hold their own function reference and keep working."""
    if name in BUILTIN_SHAPES:
        raise ValueError(f"{name}: builtin solids do not dissolve")
    if name not in SHAPES:
        raise ValueError(f"unknown shape {name!r}; SHAPES={sorted(SHAPES)}")
    del SHAPES[name]
    return name


def ferment(store: ShapeStore, salience: Any, threshold: float = 1.0) -> list:
    """FERMENT: rot entries whose salience falls below threshold, in place.

    salience is a dict (key -> weight) or a callable ((key, value) ->
    weight); dream() per-host salience plugs straight in. Returns the
    removed entries. What the lineage stopped caring about, the solid
    stops holding."""
    if callable(salience):
        weight = salience
    else:
        weight = lambda k, v: salience.get(k, 0.0)
    removed = []
    for v in range(store.n):
        kept = []
        for k, val in store.slots[v]:
            (kept if weight(k, val) >= threshold else removed).append((k, val))
        store.slots[v] = kept
    return removed


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
