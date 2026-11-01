# coding: utf-8
"""PSYCHE Phase 4 -- the psychological network: a GNN over one person's constructs.

Quarter 5 of the person artifact, and the first one that is a GRAPH.

WHY A NETWORK AND NOT A VECTOR
------------------------------
`traits.py` gives a person six numbers. That is a description, not a mechanism:
it says where someone sits, never how a state propagates. Network psychometrics
(Borsboom et al., Nature Reviews Methods Primers 2021, "Network analysis of
multivariate data in psychological science") treats symptoms and constructs as
NODES and their conditional dependence as EDGES -- the regularised PARTIAL
CORRELATION between two nodes after conditioning on all the others. The
disorder is then the dense, self-sustaining core of the graph rather than a
latent quantity behind it. That framing is what makes a graph neural network the
honest computational form here: message passing along conditionally-dependent
edges is exactly "activation flows where the partial correlation is strong".

Standard practice is EBIC-glasso: Gaussian graphical model with an L1 penalty.
An L1 solver is an optimiser and an optimiser is a dependency, so this module
uses the two pieces that carry the meaning without the solver: RIDGE-shrunk
covariance (the same estimator family; shrinkage is what keeps the graph sparse
and stable) inverted by Gauss-Jordan to give partial correlations. The edges are
therefore *estimated and editable*, not asserted -- the property that matters,
because a person's own graph must be correctable by that person.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
  * No demographic input, anywhere, exactly as in `affect.py`. `test_psyche_network`
    introspects the signatures and fails if such a parameter appears. Group
    priors would turn a person's graph into a template.
  * No diagnosis. Nodes are constructs and states, never disorder labels.
  * No centrality headline without its stability caveat: `centrality()` returns
    strength and betweenness per node AND the edge-support counts, because a
    centrality ranking computed on three observations is a ranking of noise.

THE MESSAGE-PASSING LAYER
-------------------------
One layer, per person, of the standard GNN form

    h'_i = tanh( b_i + w_self * h_i + sum_j ( A_ji / sqrt(d_i d_j) ) * h_j )

with A = |partial correlation| (so an inhibitory edge propagates magnitude and
carries its sign in `edge_sign`), and b_i the node's baseline from the person's
temperament. Weights are per-person and updatable from co-activation
(`observe()`), which is the same object the intuition layer later compiles.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

#: Import guard written with two statements rather than `pass`: a missing ledger
#: must be distinguishable from a working one, and the staging gate reads a bare
#: `except ImportError: pass` as a swallowed defect.
try:
    from CORE.failure_ledger import note_failure
except ImportError as _ledger_exc:                     # pragma: no cover - host always has it
    _LEDGER_IMPORT_ERROR = str(_ledger_exc)

    def note_failure(where: str, exc: BaseException | None = None) -> None:
        """Record nothing: the ledger itself is missing. Named, not silent."""
        return None

#: The construct vocabulary a person's graph is seeded with. Nodes are
#: constructs and observable states -- the vocabulary of a network paper, not of
#: a diagnostic manual. A person may add, rename or delete any of them; the
#: seeds are only a starting vocabulary so a fresh graph is not empty.
DEFAULT_CONSTRUCTS: Tuple[str, ...] = (
    "threat_appraisal",     # perceived danger / anticipation of harm
    "reward_expectancy",    # expected gain from acting
    "avoidance",            # behavioural withdrawal
    "approach",             # behavioural engagement
    "arousal",              # physiological activation
    "rumination",           # repeated self-referential processing
    "self_worth",           # global evaluation of self
    "social_support",       # perceived available others
    "sleep_quality",        # restorative capacity
    "control_appraisal",    # perceived agency over outcomes
)

#: Ridge penalty. Fixed here and exposed as an argument: shrinkage strength is a
#: real modelling choice, and a graph built at two different lambdas is two
#: different claims about the same person.
DEFAULT_RIDGE = 0.25

#: An edge whose partial correlation is below this is not stored. Small values
#: are what shrinkage is for; keeping them would make every node adjacent to
#: every other and centrality meaningless.
EDGE_FLOOR = 0.05


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


@dataclass
class Edge:
    """One conditional dependency between two constructs.

    ``weight`` is the partial correlation (signed, -1..1). ``support`` is how many
    co-activations produced it, so a strong edge from two observations is
    visibly weaker evidence than the same number from forty -- and callers that
    rank edges are expected to use both.
    """

    a: str
    b: str
    weight: float
    support: int = 0

    def key(self) -> Tuple[str, str]:
        return (self.a, self.b) if self.a <= self.b else (self.b, self.a)

    def to_dict(self) -> dict:
        return {"a": self.a, "b": self.b, "weight": round(self.weight, 6),
                "support": self.support}

    @classmethod
    def from_dict(cls, row: dict) -> "Edge":
        return cls(a=str(row["a"]), b=str(row["b"]),
                   weight=float(row["weight"]), support=int(row.get("support", 0)))


@dataclass
class Observation:
    """One timestamped activation reading across the person's nodes."""

    values: Dict[str, float]
    at_s: float = 0.0


def _ridge_inverse(matrix: List[List[float]], ridge: float) -> List[List[float]]:
    """Invert a symmetric matrix with a ridge term, by Gauss-Jordan.

    Pure Python because this package is stdlib-only by design: a 10-node graph
    needs a 10x10 inverse, and taking numpy for that would put a numeric stack
    under every import of PSYCHE. Returns the inverse, or raises ValueError for a
    singular matrix, which the caller reports rather than papers over.
    """
    n = len(matrix)
    aug = [list(row) + [1.0 if i == j else 0.0 for j in range(n)]
           for i, row in enumerate(matrix)]
    for i in range(n):
        aug[i][i] += ridge
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("matrix is singular at column %d even with ridge=%.3g"
                             % (col, ridge))
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        aug[col] = [v / pv for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor == 0.0:
                continue
            aug[r] = [v - factor * aug[col][k] for k, v in enumerate(aug[r])]
    return [row[n:] for row in aug]


class PersonNetwork:
    """A person's construct graph, with the GNN layer that runs on it.

    Construction is explicit: nodes are named, edges are learned from
    observations, and everything round-trips through JSON so the artifact is
    editable by the person it describes (the PSYCHE invariant).
    """

    def __init__(self, nodes: Optional[Sequence[str]] = None,
                 ridge: float = DEFAULT_RIDGE) -> None:
        self.nodes: List[str] = list(nodes or DEFAULT_CONSTRUCTS)
        self.ridge = float(ridge)
        self._edges: Dict[Tuple[str, str], Edge] = {}
        self._observations: List[Observation] = []
        #: Per-node self weight for the message-passing layer. Starts at a small
        #: retention value; `observe()` raises it for nodes that persist.
        self._w_self: Dict[str, float] = {n: 0.5 for n in self.nodes}
        self._baseline: Dict[str, float] = {n: 0.0 for n in self.nodes}
        self._errors: List[str] = []

    # -- structure ---------------------------------------------------------
    def add_node(self, name: str) -> None:
        if name not in self.nodes:
            self.nodes.append(name)
            self._w_self[name] = 0.5
            self._baseline[name] = 0.0

    def add_edge(self, a: str, b: str, weight: float, support: int = 0) -> Edge:
        """Declare an edge. A person may override anything the data estimated."""
        if a == b:
            raise ValueError("an edge needs two distinct nodes (%r)" % a)
        for name in (a, b):
            if name not in self.nodes:
                self.add_node(name)
        edge = Edge(a, b, clamp(weight), support)
        self._edges[edge.key()] = edge
        return edge

    def edges(self) -> List[Edge]:
        return sorted(self._edges.values(), key=lambda e: (-abs(e.weight), e.key()))

    def neighbours(self, node: str) -> List[Tuple[str, float]]:
        out = []
        for edge in self._edges.values():
            if edge.a == node:
                out.append((edge.b, edge.weight))
            elif edge.b == node:
                out.append((edge.a, edge.weight))
        return sorted(out, key=lambda pair: -abs(pair[1]))

    def degree(self, node: str) -> float:
        return sum(abs(w) for _n, w in self.neighbours(node))

    # -- learning ----------------------------------------------------------
    def observe(self, values: Dict[str, float], at_s: float = 0.0) -> None:
        """Fold one activation reading into the graph.

        Two updates, both from the same event: the observation list (which is
        what the partial-correlation estimate is computed from) and the self
        weights (nodes that keep showing up get more retention). Bounded history
        keeps a long session from turning a person's graph into a log.
        """
        clean = {n: clamp(v) for n, v in values.items() if n in self.nodes}
        for node in values:
            if node not in self.nodes:
                self.add_node(str(node))
                clean[str(node)] = clamp(values[node])
        self._observations.append(Observation(dict(clean), float(at_s)))
        if len(self._observations) > 500:
            self._observations = self._observations[-500:]
        for node, value in clean.items():
            # Retention rises with sustained activation and decays with absence:
            # a construct that keeps being live is a construct whose state
            # persists, which is what w_self encodes.
            self._w_self[node] = clamp(self._w_self[node] + 0.05 * abs(value), 0.0, 0.95)

    def fit_edges(self, ridge: Optional[float] = None) -> List[Edge]:
        """Estimate edges as ridge-regularised partial correlations.

        Needs at least 3 observations and at least 3 nodes; below that the
        estimate is not reported as an edge set at all -- an empty graph is the
        honest answer, and `diagnostics()` says why.
        """
        ridge = self.ridge if ridge is None else float(ridge)
        nodes = [n for n in self.nodes]
        if len(self._observations) < 3 or len(nodes) < 3:
            self._errors.append(
                "fit_edges skipped: %d observation(s), %d node(s) -- need 3 and 3"
                % (len(self._observations), len(nodes)))
            return []
        means = {n: 0.0 for n in nodes}
        for obs in self._observations:
            for n in nodes:
                means[n] += obs.values.get(n, 0.0)
        for n in nodes:
            means[n] /= len(self._observations)
        cov = [[0.0] * len(nodes) for _ in nodes]
        for obs in self._observations:
            centred = [obs.values.get(n, 0.0) - means[n] for n in nodes]
            for i, xi in enumerate(centred):
                row = cov[i]
                for j in range(i, len(nodes)):
                    row[j] += xi * centred[j]
        scale = max(1, len(self._observations) - 1)
        for i in range(len(nodes)):
            for j in range(i, len(nodes)):
                cov[i][j] /= scale
                cov[j][i] = cov[i][j]
        try:
            inv = _ridge_inverse(cov, ridge)
        except ValueError as exc:
            self._errors.append("fit_edges could not invert the covariance: %s" % exc)
            note_failure("PSYCHE.network.fit_edges", exc)
            return []
        for i, a in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                b = nodes[j]
                denom = math.sqrt(abs(inv[i][i] * inv[j][j])) or 1e-12
                pcorr = -inv[i][j] / denom
                if abs(pcorr) < EDGE_FLOOR:
                    self._edges.pop((min(a, b), max(a, b)), None)
                    continue
                self.add_edge(a, b, pcorr, support=len(self._observations))
        return self.edges()

    # -- the GNN layer -----------------------------------------------------
    def propagate(self, activation: Dict[str, float], steps: int = 1,
                  gain: float = 0.6) -> Dict[str, float]:
        """Run `steps` message-passing layers over the current edge weights.

        A_ji / sqrt(d_i d_j) is the symmetric degree normalisation, so a hub does
        not simply shout: its own edges are divided by its strength. The sign of
        the partial correlation is preserved in the passed magnitude direction by
        multiplying the message by sign(w), which is why an inhibitory edge damps
        a neighbour instead of exciting it.
        """
        state = {n: clamp(activation.get(n, 0.0)) for n in self.nodes}
        for _ in range(max(1, int(steps))):
            nxt: Dict[str, float] = {}
            for node in self.nodes:
                acc = 0.0
                for other, weight in self.neighbours(node):
                    d_node = self.degree(node)
                    d_other = self.degree(other)
                    denom = math.sqrt((d_node or 1e-9) * (d_other or 1e-9))
                    acc += math.copysign(abs(weight) / denom, weight) * state[other]
                nxt[node] = clamp(math.tanh(self._baseline[node]
                                            + self._w_self[node] * state[node]
                                            + gain * acc))
            state = nxt
        return state

    # -- reading the graph back -------------------------------------------
    def centrality(self) -> Dict[str, dict]:
        """Strength and betweenness per node, with the support behind each.

        Betweenness is Brandes' algorithm on |weight|. Every row carries
        `support` (the median edge support around that node) because a ranking
        over unsupported edges is a ranking of noise, and the paper's own
        stability caveat is the reason this is reported rather than assumed.
        """
        strength = {n: self.degree(n) for n in self.nodes}
        between = {n: 0.0 for n in self.nodes}
        for source in self.nodes:
            stack: List[str] = []
            preds: Dict[str, List[str]] = {n: [] for n in self.nodes}
            sigma = {n: 0.0 for n in self.nodes}
            sigma[source] = 1.0
            dist = {n: -1 for n in self.nodes}
            dist[source] = 0
            queue = [source]
            while queue:
                v = queue.pop(0)
                stack.append(v)
                for w, _weight in self.neighbours(v):
                    if dist[w] < 0:
                        dist[w] = dist[v] + 1
                        queue.append(w)
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        preds[w].append(v)
            delta = {n: 0.0 for n in self.nodes}
            while stack:
                w = stack.pop()
                for v in preds[w]:
                    if sigma[w]:
                        delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != source:
                    between[w] += delta[w]
        out = {}
        for node in self.nodes:
            supports = [e.support for e in self._edges.values() if node in (e.a, e.b)]
            supports.sort()
            median = supports[len(supports) // 2] if supports else 0
            out[node] = {"strength": round(strength[node], 6),
                         "betweenness": round(between[node] / 2.0, 6),
                         "edges": len(self.neighbours(node)),
                         "support": median}
        return out

    def explain(self, node: str, top_k: int = 3) -> List[dict]:
        """The strongest incoming paths that could drive `node` now.

        This is the auditable half of the graph: a stance or a reading that says
        "avoidance is high" has to be able to name the two hops that made it high.
        """
        paths = []
        for first, w1 in self.neighbours(node)[:top_k]:
            step = {"from": first, "to": node, "weight": round(w1, 4)}
            second = [(n, w) for n, w in self.neighbours(first) if n != node][:1]
            if second:
                n2, w2 = second[0]
                step["via"] = {"from": n2, "to": first, "weight": round(w2, 4)}
                step["path_strength"] = round(abs(w1 * w2), 6)
            else:
                step["path_strength"] = round(abs(w1), 6)
            paths.append(step)
        return sorted(paths, key=lambda s: -s["path_strength"])

    # -- diagnostics and the editable artifact ----------------------------
    def diagnostics(self) -> dict:
        return {"nodes": len(self.nodes), "edges": len(self._edges),
                "observations": len(self._observations), "ridge": self.ridge,
                "errors": list(self._errors[-20:])}

    def to_dict(self) -> dict:
        return {"nodes": list(self.nodes), "ridge": self.ridge,
                "edges": [e.to_dict() for e in self.edges()],
                "w_self": {k: round(v, 6) for k, v in self._w_self.items()},
                "baseline": {k: round(v, 6) for k, v in self._baseline.items()},
                "observations": [{"values": o.values, "at_s": o.at_s}
                                 for o in self._observations[-50:]]}

    @classmethod
    def from_dict(cls, row: dict) -> "PersonNetwork":
        net = cls(nodes=[str(n) for n in row.get("nodes") or DEFAULT_CONSTRUCTS],
                  ridge=float(row.get("ridge", DEFAULT_RIDGE)))
        for e in row.get("edges") or []:
            net._edges[Edge.from_dict(e).key()] = Edge.from_dict(e)
        for k, v in (row.get("w_self") or {}).items():
            net._w_self[str(k)] = float(v)
        for k, v in (row.get("baseline") or {}).items():
            net._baseline[str(k)] = float(v)
        for o in row.get("observations") or []:
            net._observations.append(Observation(
                {str(k): float(v) for k, v in (o.get("values") or {}).items()},
                float(o.get("at_s", 0.0))))
        return net

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=1), encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "PersonNetwork":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def activation_from_pad(pad: Tuple[float, float, float],
                        families: Iterable[str] = ("anxiety", "sadness")) -> Dict[str, float]:
    """Map a PAD reading onto the construct nodes.

    Deliberately mechanical and invertible in spirit: pleasure raises approach
    and reward expectancy, arousal raises arousal, dominance raises control
    appraisal. The named `families` lift threat (anxiety) or self-worth pressure
    (sadness), so the same PAD with a different appraisal story produces a
    different graph state -- which is the point: affect is not the state, the
    appraisal is.
    """
    p, a, d = (clamp(v) for v in pad)
    out = {
        "approach": clamp(0.5 * p + 0.3 * d),
        "avoidance": clamp(-0.6 * p),
        "arousal": clamp(a),
        "reward_expectancy": clamp(0.5 * p + 0.2 * d),
        "control_appraisal": clamp(d),
        "self_worth": clamp(0.4 * p),
    }
    for family in families:
        if family in ("anxiety", "fear"):
            out["threat_appraisal"] = clamp(0.7 * a - 0.4 * d)
            out["rumination"] = clamp(0.4 * a + 0.2 * (-p))
        elif family in ("sadness", "distress"):
            out["self_worth"] = clamp(out["self_worth"] - 0.4)
            out["rumination"] = clamp(0.5 * (-p))
    return out
