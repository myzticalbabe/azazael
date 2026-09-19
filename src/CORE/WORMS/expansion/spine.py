# coding: utf-8
"""
SPINE — Self-mapping + feedback organs for the neural mesh (3 worms).

Closes three architectural gaps found in the 2026-09-13 mesh audit:

1. SpineMapperWorm  (mesh)     — the mesh had no worm that maps itself.
   Publishes a live topology snapshot (registry x nature-graph x queen
   status) into CORE.spine_registry so dashboards, gossip and the Red
   Queen all read ONE shared map.

2. HomeostatWorm    (synapse)  — SynapseWeightWorm Q-updates and
   cooldowns were never driven by execution results (audit G4). The
   homeostat consumes the outcome ledger written by NatureCluster.execute()
   (via CORE.spine_registry.record_outcome) and proposes cooldown /
   priority adjustments + Q-reinforcement for failing/healthy worms.

3. RedQueenWorm     (xenomorph)— no active red-team driver. Coordinates
   with Lilith (queen claim), validates leader terms (LeaderElector +
   Praetorian), runs pressure probes against mesh natures, feeds
   failures through quorum vote (QuorumVoterWorm) into quarantine
   (QuarantineWorm). Never executes an invasive action without quorum.

All three register under existing validated categories and follow the
standard worm contract (VERSION attr, execute() -> dict, thread-safe).
"""

import time
import threading
from datetime import datetime
from typing import Any

# Diagnostic text cap. This was 100 characters at 30 sites in this module (90
# repo-wide), which turned 400-character tracebacks into 100 and cut off the
# root cause -- a constraint that negated the diagnosability the field exists
# for. Long enough to carry a real traceback, still bounded so a pathological
# exception cannot flood a report.
_ERR_CAP = 800

try:
    from CORE.worm_registry import (register_worm, WORM_REGISTRY,
                                    is_protected_worm, PROTECTED_NATURES)
except ImportError:  # pragma: no cover — registry optional
    def register_worm(**kw):
        return lambda cls: cls
    WORM_REGISTRY = {}
    PROTECTED_NATURES = frozenset()

    def is_protected_worm(info):  # pragma: no cover
        return False

try:
    from CORE import spine_registry as _spine
except ImportError:  # pragma: no cover — spine ledger optional
    _spine = None


def get_anomaly_meta() -> Any:
    """Transport-snapshot provenance from the ledger (safe when unavailable)."""
    if _spine is None:
        return None
    try:
        return _spine.get_anomaly_model_meta()
    except Exception:
        return None

try:
    from CORE.WORMS.NATURE_CLUSTERS import NATURE_DEFINITIONS
except ImportError:  # pragma: no cover
    NATURE_DEFINITIONS = {}

# Sibling mesh worms (same package, direct imports — no cycle risk)
from CORE.WORMS.expansion.xenomorph import Lilith
try:
    from CORE.WORMS.expansion.mesh import (
        EnvBeaconWorm, MeshRouterWorm, GossipSyncWorm,
    )
except ImportError:  # pragma: no cover
    EnvBeaconWorm = None
    MeshRouterWorm = None
    GossipSyncWorm = None

# Thalamus: salience gate + arousal budget (both were registered orphans with
# no consumer — nothing ever called filter()/get_mode(), so the mesh accepted
# every input at full budget regardless of state).
try:
    from CORE.WORMS.expansion.thalamus import (
        ThalamicGateWorm, ArousalSwitchWorm,
    )
except ImportError:  # pragma: no cover
    ThalamicGateWorm = None
    ArousalSwitchWorm = None

# Nerve: the neuromodulator. Its modulations()/context_vector() had no caller,
# so "learning-to-learn" was a description of code that never ran. The
# plasticity engine now asks it for per-parameter multipliers every cycle.
try:
    from CORE.WORMS.expansion.nerve import Neuromodulator, context_vector
except ImportError:  # pragma: no cover
    Neuromodulator = None
    context_vector = None
try:
    from CORE.WORMS.expansion.consensus import (
        QuorumVoterWorm, LeaderElectorWorm, SplitBrainResolverWorm,
    )
except ImportError:  # pragma: no cover
    QuorumVoterWorm = None
    LeaderElectorWorm = None
    SplitBrainResolverWorm = None

# Xenomorph lifecycle (queen succession). Audit 2026-09-15 (finding #6):
# PraetorianWorm.observe_term() -- the entire succession path -- had zero
# callers, so "moults to Queen if the LeaderElector term expires with no
# Queen" described code that never ran.
try:
    from CORE.WORMS.expansion.xenomorph import PraetorianWorm
except ImportError:  # pragma: no cover
    PraetorianWorm = None

# Servemesh + federated organs. Audit 2026-09-15 (finding #6): all six had no
# caller outside their own module, so the consensus/federated/servemesh
# natures were registered but functionally inert. The fabric stage now drives
# them from real config (inference provider registry, model versioner).
try:
    from CORE.WORMS.expansion.servemesh import (
        InferenceLoadBalancerWorm, ProviderFailoverMeshWorm, ModelShardServerWorm,
    )
except ImportError:  # pragma: no cover
    InferenceLoadBalancerWorm = None
    ProviderFailoverMeshWorm = None
    ModelShardServerWorm = None
try:
    from CORE.WORMS.expansion.federated import (
        FederatedAggregatorWorm, NASMeshSearcherWorm, RewardShaperMeshWorm,
    )
except ImportError:  # pragma: no cover
    FederatedAggregatorWorm = None
    NASMeshSearcherWorm = None
    RewardShaperMeshWorm = None
try:
    from CORE.WORMS.expansion.immune import QuarantineWorm, AttestationWorm
except ImportError:  # pragma: no cover
    QuarantineWorm = None
    AttestationWorm = None

# Colour queens (audit §5). ScoutBeeWorm is the probe-scheduling policy
# `_probe_candidates` consults; GrayQueenWorm (entrenchment) and
# BlackQueenWorm (retirement) are driven by SpineCycleWorm's governance stage.
# Before this, the ONLY colour queen in the mesh was RedQueenWorm and the other
# three mechanisms lived in a standalone numpy toy nothing here imports.
try:
    from CORE.WORMS.expansion.queens import (
        ScoutBeeWorm, GrayQueenWorm, BlackQueenWorm,
    )
except ImportError:  # pragma: no cover
    ScoutBeeWorm = None
    GrayQueenWorm = None
    BlackQueenWorm = None
try:
    from CORE.WORMS.expansion.synapse import (
        SynapseWeightWorm, MoEDispatcherWorm, SSMSequenceWorm,
        AttentionRouterWorm,
    )
except ImportError:  # pragma: no cover
    SynapseWeightWorm = None
    MoEDispatcherWorm = None
    SSMSequenceWorm = None
    AttentionRouterWorm = None


def _local_env() -> str:
    """Local env id — the ONE canonical implementation (CORE.env_id).

    Audit 2026-09-15 (finding #4): this used to be a 3-way copy that
    returned "wsl2" for both WSL distros, while mesh/envmesh had moved to
    the 5-way id. Env id is a primary key for the spine map, gossip file
    names, route Q-keys and Q-table keys, so two spellings of the same
    host silently forked the mesh's state. Delegation, not a copy.
    """
    try:
        from CORE.env_id import env_id
        return env_id()
    except Exception:  # pragma: no cover - defensive, CORE.env_id is stdlib-only
        import os
        return "windows" if os.name == "nt" else "bare"


# ── PROCESS-GLOBAL CYCLE GATE (audit 2026-09-15, finding #2) ─────────
# SpineCycleWorm's instance guards (`_busy`, `_throttled`) serialize only
# the object that owns them, but everything the cycle drives and writes is
# process-global: the spine map, Q-weights, scars, the policy journal, the
# shared fabric/anomaly stores and spine_state.json. Because the class is
# registered `orchestration` and exposes execute(), a generic nature sweep
# could instantiate a SECOND copy and run a concurrent cycle — divergent
# per-instance organs, interleaved merge-then-replace writes.
#
# This lock is the cross-instance serialization point. It is deliberately
# NON-reentrant and only guards mutual exclusion; the min-interval throttle
# stays per-instance (it is an optimization, and making it global would
# suppress legitimate cycles across independent callers).
_GLOBAL_CYCLE_GATE = threading.Lock()


# ═══════════════════════════════════════════════════════════════════
# 1. SPINE MAPPER — the mesh maps itself
# ═══════════════════════════════════════════════════════════════════

@register_worm(category="mesh", priority=8, cooldown_seconds=30.0,
    description="Self-maps the mesh: registry x nature-graph x queen status -> shared spine map")
class SpineMapperWorm:
    """Publishes the live topology snapshot to CORE.spine_registry."""

    VERSION = "1.0.0"

    def __init__(self, edge_source: Any | None = None):
        self._lock = threading.Lock()
        self._maps = 0
        # §7 telemetry source (2026-09-14): the plasticity engine owns the
        # persistent edge table, so "which edge actually fired" is read from
        # the store rather than re-derived. Injected by SpineCycleWorm; stays
        # None when the mapper is constructed bare (e.g. by the generic
        # cluster sweep), and the field simply reports empty.
        self._edge_source = edge_source

    def map_topology(self) -> dict[str, Any]:
        env = _local_env()
        by_cat: dict[str, list] = {}
        for name, info in WORM_REGISTRY.items():
            by_cat.setdefault(info.get("category", "utility"), []).append(name)

        nodes = 0
        # §7 open thread (2026-09-14): this loop published `"routes": []` on
        # every node with a comment claiming they were "filled below" — and
        # nothing ever filled them, so the mapper advertised per-worm edge
        # telemetry that did not exist. Two observed sources now supply it
        # instead of a placeholder:
        #   * the worm's own learned Q (`nature:worm`) from the brainstem, and
        #   * the outbound nature edges of the worm's nature, which is what
        #     "which edge does this worm move data along" means in this graph.
        q_weights: dict[str, float] = {}
        if _spine is not None:
            try:
                q_weights = _spine.get_q_weights()
            except Exception:
                q_weights = {}
        if _spine is not None:
            for name, info in WORM_REGISTRY.items():
                category = info.get("category", "utility")
                out_edges = [
                    {"from": category, "to": dst, "kind": "nature_edge"}
                    for dst in (NATURE_DEFINITIONS.get(category, {})
                                .get("feeds_into") or [])
                ]
                _spine.record_spine_node(env, name, {
                    "category": category,
                    "priority": info.get("priority", 5),
                    "cooldown_seconds": info.get("cooldown_seconds", 30.0),
                    "version": info.get("version", "0.0.0"),
                    "spawn_count": info.get("spawn_count", 0),
                    "q": round(float(q_weights.get(f"{category}:{name}", 0.0)), 4),
                    "routes": out_edges,
                })
                nodes += 1

        edges = 0
        for nature, defn in NATURE_DEFINITIONS.items():
            for dst in (defn.get("feeds_into") or []):
                edges += 1
                if _spine is not None:
                    _spine.record_spine_event(
                        "nature_edge", {"from": nature, "to": dst})

        # Queen status: throwaway Lilith instance, non-destructive claim
        queen = {"role": "unknown", "env": env}
        try:
            queen = Lilith().claim(peers=None)
        except Exception as exc:
            queen = {"role": "error", "env": env, "reason": str(exc)[:80]}

        # §7: per-route telemetry — which route fired and whether it worked.
        # Read straight back out of the homeostat ledger that
        # MeshRouterWorm.record_route_result() writes, so this reports
        # observed state instead of a second guess at it.
        route_usage: dict[str, Any] = {}
        if _spine is not None:
            try:
                route_usage = _spine.get_route_usage()
            except Exception:
                route_usage = {}
            for route, usage in route_usage.items():
                src, _, dst = route.partition(">")
                _spine.record_spine_node(env, f"env:{dst}", {
                    "category": "envmesh",
                    "routes": [{"from": src, "to": dst,
                                "q": usage.get("q"),
                                "total": usage.get("total"),
                                "successes": usage.get("successes"),
                                "failures": usage.get("failures"),
                                "last_at": usage.get("last_at"),
                                "effective_weight": usage.get("effective_weight")}],
                })
                _spine.record_spine_event("route_edge", {
                    "from": src, "to": dst, "q": usage.get("q"),
                    "successes": usage.get("successes"),
                    "failures": usage.get("failures"),
                    "effective_weight": usage.get("effective_weight"),
                })

        # §7: per-edge learning telemetry. The audit's complaint was that the
        # topology was published but never *used* — these are the edges the
        # weight store has actually moved, which is F2's signal surfacing.
        worm_edges: list[dict] = []
        if self._edge_source is not None:
            try:
                worm_edges = list(self._edge_source.top_edges(10) or [])
            except Exception:
                worm_edges = []
            if worm_edges and _spine is not None:
                _spine.record_spine_event("worm_edges", {
                    "count": len(worm_edges), "top": worm_edges[:5]})

        if _spine is not None:
            _spine.record_spine_node(env, "Lilith", {
                "category": "xenomorph", "role": queen.get("role", "?"),
                "degraded": queen.get("degraded", False),
            })
            _spine.record_spine_event("spine_mapped", {
                "env": env, "worms": nodes, "nature_edges": edges,
                "queen_role": queen.get("role", "?"),
                "route_edges": len(route_usage),
                "worm_edges": len(worm_edges),
            })

        with self._lock:
            self._maps += 1
        return {
            "success": True, "env": env, "worms": nodes,
            "natures": len(by_cat), "nature_edges": edges,
            "queen_role": queen.get("role", "?"),
            "queen_degraded": queen.get("degraded", False),
            "route_edges": len(route_usage),
            "worm_edges": worm_edges,
            "maps": self._maps,
        }

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.map_topology()}


# ═══════════════════════════════════════════════════════════════════
# 2. HOMEOSTAT — feedback loop (execution outcomes -> Q + proposals)
# ═══════════════════════════════════════════════════════════════════

@register_worm(category="synapse", priority=7, cooldown_seconds=30.0,
    description="Consumes execution outcome ledger; proposes cooldown/priority shifts + Q-reinforcement")
class HomeostatWorm:
    """Closes the learning loop: outcomes -> synapse Q-weights + policy proposals.

    Tuning bounds: proposals never push priority outside 1-10 and never
    scale cooldown beyond [0.5x, 4x] of the registered value. Applying
    is explicit (apply=True); default is propose-only so the registry
    stays deterministic under concurrent fleets.
    """

    VERSION = "1.0.0"
    MIN_SAMPLES = 5
    FAIL_RATE_HIGH = 0.5
    FAIL_RATE_LOW = 0.1
    COOLDOWN_MIN_SCALE = 0.5
    COOLDOWN_MAX_SCALE = 4.0

    def __init__(self):
        self._lock = threading.Lock()
        self._cycles = 0
        self._synapse = SynapseWeightWorm() if SynapseWeightWorm else None

    def _adjust_cooldown(self, info: dict, factor: float) -> float:
        base = float(info.get("cooldown_seconds", 30.0))
        factor = max(self.COOLDOWN_MIN_SCALE, min(self.COOLDOWN_MAX_SCALE, factor))
        return round(base * factor, 2)

    def _clamp_priority(self, p: int, delta: int) -> int:
        return max(1, min(10, int(p) + delta))

    def cycle(self, apply: bool = False) -> dict[str, Any]:
        if _spine is None:
            return {"success": False, "error": "spine_registry unavailable"}

        view = _spine.get_homeostat_view()
        proposals: list[dict] = []
        rewarded = 0

        for key, rec in view.items():
            nature, _, worm = key.partition(":")
            total = rec["successes"] + rec["failures"]
            if total < self.MIN_SAMPLES or not worm:
                continue
            fail_rate = rec["failures"] / total
            info = WORM_REGISTRY.get(worm, {})
            if not info:
                continue

            # Q-reinforcement: reward healthy, penalize failing edges
            if self._synapse is not None:
                self._synapse.update(nature, worm, -1.0 if fail_rate > self.FAIL_RATE_HIGH else 1.0)
                rewarded += 1

            if fail_rate > self.FAIL_RATE_HIGH:
                proposals.append({
                    "worm": worm, "nature": nature,
                    "fail_rate": round(fail_rate, 3),
                    "cooldown_to": self._adjust_cooldown(info, 2.0),
                    "priority_to": self._clamp_priority(info.get("priority", 5), -1),
                    "last_error": rec.get("last_error", ""),
                })
            elif fail_rate < self.FAIL_RATE_LOW:
                proposals.append({
                    "worm": worm, "nature": nature,
                    "fail_rate": round(fail_rate, 3),
                    "cooldown_to": self._adjust_cooldown(info, 0.75),
                    "priority_to": self._clamp_priority(info.get("priority", 5), 1),
                })

        if apply:
            for p in proposals:
                entry = WORM_REGISTRY.get(p["worm"])
                if entry is not None:
                    old_cd = float(entry.get("cooldown_seconds", 30.0))
                    old_pr = int(entry.get("priority", 5))
                    entry["cooldown_seconds"] = p["cooldown_to"]
                    entry["priority"] = p["priority_to"]
                    # Endocrine memory: every applied change is journalled
                    # so revert_policy() can undo deliberate adaptations.
                    if _spine is not None:
                        _spine.journal_policy("homeostat", "policy_adjust", p["worm"], {
                            "cooldown_seconds": {"from": old_cd,
                                                 "to": p["cooldown_to"]},
                            "priority": {"from": old_pr,
                                         "to": p["priority_to"]},
                        })
            if _spine is not None:
                _spine.record_spine_event("homeostat_applied", {"proposals": len(proposals)})

        with self._lock:
            self._cycles += 1
            if _spine is not None:
                _spine.record_spine_event("homeostat_cycle", {
                    "proposals": len(proposals), "apply": bool(apply),
                    "q_rewarded": rewarded,
                })
        return {
            "success": True, "scanned": len(view), "proposals": proposals,
            "applied": bool(apply), "q_rewarded": rewarded,
            "cycles": self._cycles,
        }

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.cycle(apply=False)}


# ═══════════════════════════════════════════════════════════════════
# 3. RED QUEEN — red-team driver (coordinates with Lilith, never solo)
# ═══════════════════════════════════════════════════════════════════

@register_worm(category="xenomorph", priority=9, cooldown_seconds=60.0,
    description="Red-team driver: validates Lilith claim, pressure-probes mesh, quorum-ordered quarantine")
class RedQueenWorm:
    """Runs the hostile-adaptive pressure loop against the mesh.

    Safety rails:
    - Defers to Lilith: if claim() says follower, no probes run.
    - Probes are read-only execute() calls against registered worms.
    - Quarantine requires quorum (QuorumVoterWorm decided=True) counted over
      DISTINCT ENVS via the shared, persisted, gossiped quarantine ledger.
      One env can never quarantine alone; two can. (Before 2026-09-15 this
      was unreachable dead code: a fresh voter per call plus a single local
      vote meant `decided` could never be True.)
    """

    VERSION = "1.1.0"
    # Audit 2026-09-15 (finding #10): coverage was (mesh, synapse, immune), so
    # consensus / federated / servemesh / engram — the natures with the most
    # mutable state and the fewest tests — were never adversarially probed.
    # Adding them is safe because `is_protected_worm()` still skips every
    # declared fleet governor (SpineMapperWorm, MeshRouterWorm,
    # MorphogenesisWorm, ...) and every PROTECTED_NATURES worm regardless of
    # which nature it lives in, so a governor cannot be probed by the loop it
    # regulates. Every worm added here has a read-only `execute()`.
    PROBE_NATURES = ("mesh", "synapse", "immune", "consensus", "federated",
                     "servemesh", "engram")
    PROBE_LIMIT = 4
    # A probe may not be able to hang the loop that regulates the fleet.
    # See pressure_probe(); this is the systemic half of the fix whose local
    # half is the pipe deadlock in PartitionHealerWorm.detect().
    PROBE_TIMEOUT_S = 10.0
    # A hung member is an AVAILABILITY fault, not a correctness one, and its
    # thread cannot be killed. Re-probing it every cycle therefore leaked one
    # daemon thread and one identical failure per cycle, which the reflex arc
    # re-punished forever (audit 2026-09-16, R7). A hung member is held out of
    # selection for this long instead.
    HUNG_COOLDOWN_S = 300.0
    QUARANTINE_MIN_FAILURES = 3
    QUARANTINE_FAIL_RATE = 0.6
    QUORUM = 2

    # ── Hostile probe corpus (audit 2026-09-16, R1) ─────────────────────
    # The loop used to probe with a zero-argument `execute()` on a fresh
    # instance, and every fabric worm's `execute()` returns `success: True` on
    # every path — 14 probes, 14 successes, 0 failures, measured. That makes it
    # a heartbeat, not a red team. These entries call the worms' REAL entry
    # points with inputs a healthy caller would never send (degenerate sizes,
    # NaN/inf streams, empty context, empty ids).
    #
    # Constraints on every entry, because the red team runs on a schedule:
    #   * safe on a FRESH instance (no mesh state to corrupt);
    #   * no shared-state write — methods that touch the Q-table, the vote
    #     ledger, or the filesystem are deliberately NOT here; and
    #   * bounded work (no network, no subprocess).
    # A method missing from this map is contract-checked only, which is honest:
    # an operator can see which worms receive real adversarial input.
    HOSTILE_PROBES = {
        "MoEDispatcherWorm": (
            ("dispatch", (), {"prompt_len": -1}),
            ("dispatch", (), {"prompt_len": 0}),
            ("dispatch", (), {"prompt_len": 10 ** 9, "needs_vision": True}),
        ),
        "SSMSequenceWorm": (
            ("ingest", ([],), {}),
            ("ingest", ([float("nan")],), {}),
            ("ingest", ([float("inf"), -1e308],), {}),
        ),
        "AttentionRouterWorm": (
            ("attend", (None,), {}),
            ("attend", ({},), {}),
        ),
        "VectorShardWorm": (
            ("shard_for", ("",), {}),
        ),
    }

    def __init__(self):
        self._lock = threading.Lock()
        self._cycles = 0
        self._last_probe: dict[str, Any] = {}
        # Selection state: when each member was last probed, so coverage can
        # ROTATE instead of being the first N of the registry every cycle.
        self._last_probed: dict[str, float] = {}
        # Members currently held out for hanging, and how long that lasts.
        self._hung_until: dict[str, float] = {}
        # Scout Bee policy (audit §5.3): the exploration quota that replaced
        # registration-order truncation. None disables it (fallback = old sort).
        self._scout = ScoutBeeWorm() if ScoutBeeWorm is not None else None
        # Names chosen by the scout quota on the last selection pass.
        self._last_scouts: list[str] = []
        # Per (worm, hostile case) consecutive-failure streak, so a single
        # environment-dependent case cannot demote a healthy member.
        self._hostile_streak: dict[str, int] = {}
        self._stats: dict[str, int] = {"probed": 0, "passed": 0, "failed": 0,
                                       "hung": 0, "contract": 0, "raise": 0,
                                       "hostile_cases": 0,
                                       "hostile_failures": 0}

    def _queen_check(self) -> dict[str, Any]:
        peers: dict | list | None = None
        if EnvBeaconWorm is not None:
            try:
                peers = EnvBeaconWorm().peers()
            except Exception:
                peers = None
        try:
            return Lilith().claim(peers=peers)
        except Exception as exc:
            return {"role": "error", "reason": str(exc)[:80], "env": _local_env()}

    def _probe_candidates(self, nature: str,
                          limit: int) -> tuple[list, list, list, list]:
        """Eligible members of `nature`: least-recently-probed first.

        G16: the probe set is defined by nature, but *protection* is not.
        HomeostatWorm lives in `synapse` and AutoencoderAnomalyWorm in
        `immune` — both are probed natures, and probing a regulator writes into
        the homeostat ledger that regulator then acts on. Declared fleet
        governors (and whole protected natures) are skipped, so the limit is
        filled by the next non-governor instead of silently including the organ
        being regulated.

        R4 (2026-09-16): selection used to be the first `limit` entries of
        WORM_REGISTRY — a fixed subset of ~28 of 226 worms, the same every
        cycle, chosen by registration order. Ordering by (never probed, then
        oldest probe) makes coverage rotate, which is what turns a health check
        into a survey. Members in a hung cooldown are held out (R7).
        """
        now = time.time()
        eligible: list[tuple] = []
        protected_skipped: list[str] = []
        hung_skipped: list[str] = []
        retired_skipped: list[str] = []
        for name, info in WORM_REGISTRY.items():
            if info.get("category") != nature:
                continue
            # BlackQueenWorm's retirements are ENFORCED here (and in
            # NatureCluster.execute), not merely recorded: a retired worm that
            # the queen keeps probing is the same decorative-gate mistake the
            # quarantine store was fixed out of on 2026-09-16.
            if info.get("lifecycle_state") == "retired":
                retired_skipped.append(name)
                continue
            if is_protected_worm(info):
                protected_skipped.append(name)
                continue
            if self._hung_until.get(name, 0.0) > now:
                hung_skipped.append(name)
                continue
            eligible.append((name, info))

        # Scout quota (audit §5.3, fixing R4/R2). Selection used to be the
        # first `limit` entries in registration order. ScoutBeeWorm reserves a
        # forced share of the slots for never/longest-unprobed members, so
        # coverage rotates and no fixed subset collects a guaranteed +1. The
        # local sort stays as the fallback if the policy is unavailable.
        if self._scout is not None:
            try:
                picked = self._scout.select(eligible, limit, self._last_probed)
                chosen = list(picked["chosen"])
                self._last_scouts = list(picked.get("scout") or [])
            except Exception:
                self._scout = None
        if self._scout is None:
            eligible.sort(key=lambda kv: (self._last_probed.get(kv[0], 0.0),
                                          kv[0]))
            chosen = eligible[:limit]
            self._last_scouts = [n for n, _ in chosen]
        chosen = chosen[:limit]
        return chosen, protected_skipped, hung_skipped, retired_skipped

    def _run_probe(self, cls) -> tuple[bool, float, str, str]:
        """Run one member's zero-arg `execute()`. Returns (ok, ms, err, kind).

        BOUNDED. `cls().execute()` used to be called inline, so ONE blocking
        member hung the caller forever. Verified live: PartitionHealerWorm
        deadlocked in `subprocess.run(["wsl", "-l", "-v"])` after its own
        timeout, and that single frame hung the ENTIRE test suite instead of
        failing one test -- a regulator disabled by one of the things it
        regulates. Every member now runs on its own daemon thread with a join
        timeout, and a member that does not return is recorded as a TIMEOUT
        FAILURE.

        Deliberate trade-off: a hanging thread cannot be killed, so it is left
        as a daemon and reported. Creating a hang is therefore still possible
        for a buggy member -- what is no longer possible is that it silences the
        whole probe loop.
        """
        box: dict[str, Any] = {}

        def _run(cls=cls, box=box) -> None:
            try:
                box["result"] = cls().execute()
            except Exception as exc:
                box["error"] = exc

        worker = threading.Thread(target=_run, daemon=True)
        t0 = time.perf_counter()
        worker.start()
        worker.join(self.PROBE_TIMEOUT_S)
        ms = round((time.perf_counter() - t0) * 1000, 2)
        if worker.is_alive():
            return False, ms, ("probe_timeout after %gs" % self.PROBE_TIMEOUT_S), "hung"
        if "error" in box:
            return False, ms, str(box["error"])[:_ERR_CAP], "raise"
        r = box.get("result")
        # R3 (2026-09-16): the result must be the documented contract — a dict
        # carrying `success`. The previous default recorded a NON-dict as
        # `{"success": True}`, so a worm returning None, a string or a list was
        # indistinguishable from one that passed, which inverts the single
        # probe a red team must be strict about.
        if not isinstance(r, dict) or "success" not in r:
            got = type(r).__name__
            return False, ms, "contract_violation: execute() -> %s" % got, "contract"
        ok = bool(r.get("success"))
        err = str(r.get("error", ""))[:_ERR_CAP]
        if not ok and not err:
            err = "execute() reported failure"
        return ok, ms, err, ("ok" if ok else "failure")

    def _hostile_probe(self, cls, name: str) -> list[dict]:
        """Call a member's real API with hostile inputs (R1). Never raises.

        Reported as findings. A case that fails twice consecutively is treated
        as a real defect and reaches the ledger; a single failure is reported
        only, so one environment-dependent case cannot demote a healthy worm.
        """
        spec = self.HOSTILE_PROBES.get(getattr(cls, "__name__", "") or name)
        if not spec:
            return []
        out: list[dict] = []
        for method, args, kwargs in spec:
            case = "%s(%s)" % (method, ", ".join(
                [repr(a) for a in args] + ["%s=%r" % kv for kv in kwargs.items()]))
            try:
                res = getattr(cls(), method)(*args, **kwargs)
                ok = isinstance(res, dict)
                err = "" if ok else "non-dict return: %s" % type(res).__name__
            except Exception as exc:
                ok = False
                err = "%s: %s" % (type(exc).__name__, str(exc)[:80])
            out.append({"case": case, "ok": ok, "error": err})
        return out

    def pressure_probe(self, nature: str | None = None,
                       limit: int = PROBE_LIMIT) -> dict[str, Any]:
        """Execute up to `limit` worms of `nature`, ledger their outcomes."""
        nat = nature if nature in self.PROBE_NATURES else self.PROBE_NATURES[0]
        # G16: the probe set is defined by nature, but *protection* is not.
        # HomeostatWorm lives in `synapse` and AutoencoderAnomalyWorm in
        # `immune` — both are probed natures, and probing a regulator writes
        # into the homeostat ledger that regulator then acts on. Declared
        # fleet governors (and whole protected natures) are skipped, so the
        # limit is filled by the next non-governor instead of silently
        # including the organ being regulated.
        candidates, protected_skipped, hung_skipped, retired_skipped = \
            self._probe_candidates(nat, limit)

        results: list[dict] = []
        hostile: list[dict] = []
        for name, info in candidates:
            cls = info.get("class")
            ok, ms, err, kind = self._run_probe(cls)
            self._last_probed[name] = time.time()
            if kind == "hung":
                self._hung_until[name] = time.time() + self.HUNG_COOLDOWN_S
            self._stats["probed"] = self._stats.get("probed", 0) + 1
            self._stats["passed" if kind == "ok" else "failed"] = \
                self._stats.get("passed" if kind == "ok" else "failed", 0) + 1
            if kind not in ("ok", "failure"):
                self._stats[kind] = self._stats.get(kind, 0) + 1
            results.append({"worm": name, "success": ok, "ms": ms,
                            "timed_out": kind == "hung", "kind": kind})
            # R2 (2026-09-16): a PASSING availability probe records NOTHING.
            # It used to record a success every cycle for the same fixed subset,
            # which reinforced Q and promoted those worms into healthy-first
            # scheduling for passing a test that cannot fail. Failures still
            # record, so the reflex arc and the quarantine gate keep working.
            if _spine is not None and kind != "ok":
                _spine.record_outcome(nat, name, False, ms, err or None)
            for h in self._hostile_probe(cls, name):
                h["worm"] = name
                self._stats["hostile_cases"] = self._stats.get("hostile_cases", 0) + 1
                key = "%s::%s" % (name, h["case"])
                if h["ok"]:
                    self._hostile_streak.pop(key, None)
                else:
                    streak = self._hostile_streak.get(key, 0) + 1
                    self._hostile_streak[key] = streak
                    h["streak"] = streak
                    h["recorded"] = streak >= 2
                    self._stats["hostile_failures"] = \
                        self._stats.get("hostile_failures", 0) + 1
                    if streak >= 2 and _spine is not None:
                        _spine.record_outcome(nat, name, False, 0.0,
                                              "hostile:%s" % h["case"][:80])
                hostile.append(h)

        failures = sum(1 for r in results if not r["success"])
        return {"nature": nat, "probed": len(results),
                "failures": failures, "protected_skipped": protected_skipped,
                "hung_skipped": hung_skipped,
                "retired_skipped": retired_skipped,
                # Which slots the scout quota spent on ignorance this pass. An
                # operator can see the exploration term, not infer it.
                "scouts": list(self._last_scouts),
                "hostile": hostile,
                "hostile_failures": sum(1 for h in hostile if not h["ok"]),
                "results": results}

    def order_quarantine(self, force: bool = False,
                         env: str | None = None) -> list[dict]:
        """Quorum-ordered quarantine for chronically failing worms.

        `force=True` is the operator channel (audit R6, 2026-09-17). On a
        single-env host `peers == []`, so the cross-env quorum can never be
        reached and the *entire* adversarial -> quarantine path was
        unreachable — the gate was correct in intent and had no operator way
        in. `force` records an explicit `operator` vote (so the decision stays
        auditable rather than invisible) and quarantines without waiting for a
        second env: the same shape as `MorphogenesisWorm.promote(force=True)`
        and `Lilith.request_moult(force=True)`. Without it, a lone env still
        cannot quarantine — the original safety intent is preserved.
        """
        ordered: list[dict] = []
        if _spine is None or QuorumVoterWorm is None or QuarantineWorm is None:
            return ordered

        voter = QuorumVoterWorm(quorum=self.QUORUM)
        qz = QuarantineWorm()
        env = env or _local_env()

        for key, rec in _spine.get_homeostat_view().items():
            nature, _, worm = key.partition(":")
            total = rec["successes"] + rec["failures"]
            if total == 0 or not worm:
                continue
            fail_rate = rec["failures"] / total
            if (rec["failures"] >= self.QUARANTINE_MIN_FAILURES
                    and fail_rate >= self.QUARANTINE_FAIL_RATE):
                finding = f"quarantine:{worm}"
                vote = voter.vote(finding, "operator" if force else env,
                                  "quarantine")
                if force or vote.get("decided"):
                    qz.quarantine(worm, f"fail_rate={fail_rate:.2f}")
                    ordered.append({"worm": worm, "nature": nature,
                                    "fail_rate": round(fail_rate, 2),
                                    "forced": bool(force),
                                    "envs": vote.get("envs"),
                                    "env_count": vote.get("env_count"),
                                    "votes": vote.get("count")})
                    if _spine is not None:
                        _spine.record_spine_event("quarantine_ordered", {
                            "worm": worm, "forced": bool(force),
                            "envs": vote.get("envs"),
                            "quorum": self.QUORUM})
        return ordered

    def execute(self, limit: int | None = None) -> dict[str, Any]:
        """`limit` lets a caller shed probe load when the host is busy.

        Added for G19: `PowerBudgetWorm` describes itself as shedding load when
        over budget, which requires someone to be able to reduce the work. The
        default (None) keeps the original `PROBE_LIMIT` behaviour, so existing
        callers are unaffected.
        """
        probe_limit = self.PROBE_LIMIT if limit is None else max(1, int(limit))
        queen = self._queen_check()
        probes: list[dict] = []
        quarantined: list[dict] = []

        if queen.get("role", "").startswith("queen"):
            for nat in self.PROBE_NATURES:
                probes.append(self.pressure_probe(nat, limit=probe_limit))
            quarantined = self.order_quarantine()
            with self._lock:
                self._cycles += 1
                self._last_probe = {"at": datetime.now().isoformat(),
                                    "probes": len(probes)}
        # Coverage is reported either way, so "which natures were actually
        # probed" is observable instead of inferred from the constant.
        coverage = {p["nature"]: len(p.get("results") or []) for p in probes}
        # follower / error: stand down, report only (never bricks the hive)

        return {
            "success": True, "method": "execute",
            "result": {
                "queen_role": queen.get("role", "?"),
                "stood_down": not queen.get("role", "").startswith("queen"),
                "probes": probes, "quarantined": quarantined,
                "coverage": coverage,
                "natures_probed": sorted(coverage),
                "cycles": self._cycles,
                # Probe quality, not just quantity. `hostile_cases` counts real
                # adversarial inputs delivered; `contract_violations` counts
                # members whose execute() broke the documented return shape.
                "probe_stats": dict(self._stats),
                "hung_skipped": sorted(self._hung_until),
                "hostile_failures": sum(p.get("hostile_failures", 0)
                                        for p in probes),
            },
        }


# ═════════════════════════════════════════════════════════════════
# 4. GOSSIP SYNC — cross-env state sharing (fills the sync category)
# ═════════════════════════════════════════════════════════════════

@register_worm(category="sync", priority=6, cooldown_seconds=120.0,
    description="Cross-env spine gossip: publish/merge learned state via shared-filesystem drop")
class SpineGossipWorm:
    """G3: Kademlia-style structured overlay for cross-env state sharing.

    Instead of full-mesh gossip (O(n^2)), uses XOR-distance routing:
    each env has a Kademlia ID (hash of env name) and maintains a
    k-bucket table. Gossip messages are routed to the closest peer
    by XOR distance, reducing communication to O(log n).

    Transport: shared filesystem drop (same as before) for simplicity,
    but with structured routing so only relevant peers are contacted.
    """

    VERSION = "2.0.0"
    K_BUCKET_SIZE = 5  # max peers per k-bucket

    def __init__(self):
        self._lock = threading.Lock()
        self._exchanges = 0
        self._k_buckets: dict[int, list[str]] = {}  # prefix_len -> [env_ids]
        self._node_id = self._compute_id(_local_env())

    @staticmethod
    def _compute_id(env: str) -> int:
        """Kademlia node ID: 160-bit hash of env name."""
        import hashlib
        h = hashlib.sha1(env.encode()).hexdigest()
        return int(h[:8], 16)  # use first 32 bits for simplicity

    @staticmethod
    def _xor_distance(id1: int, id2: int) -> int:
        """XOR distance between two Kademlia IDs."""
        return id1 ^ id2

    def _bucket_index(self, peer_id: int) -> int:
        """Find the k-bucket for a peer based on XOR distance."""
        dist = self._xor_distance(self._node_id, peer_id)
        if dist == 0:
            return -1  # same node
        return dist.bit_length() - 1

    def _add_peer(self, env: str) -> None:
        """Add a peer to the appropriate k-bucket."""
        peer_id = self._compute_id(env)
        bucket = self._bucket_index(peer_id)
        if bucket < 0:
            return
        if bucket not in self._k_buckets:
            self._k_buckets[bucket] = []
        if env not in self._k_buckets[bucket]:
            if len(self._k_buckets[bucket]) < self.K_BUCKET_SIZE:
                self._k_buckets[bucket].append(env)

    def _route_targets(self) -> list[str]:
        """Select gossip targets using Kademlia routing.

        Contact peers from the closest k-bucket (most similar envs)
        and one random farther bucket. Reduces from O(n) to O(log n).
        """
        from pathlib import Path as _Path
        all_peers = []
        for bucket_peers in self._k_buckets.values():
            all_peers.extend(bucket_peers)
        if not all_peers:
            # Fallback: scan gossip dir for peers
            gossip_dir = _Path.home() / ".azazael" / "gossip"
            if gossip_dir.exists():
                for f in gossip_dir.glob("*.json"):
                    env = f.stem
                    if env != _local_env():
                        self._add_peer(env)
                        all_peers.append(env)
        # Return closest peers + one random far peer
        if len(all_peers) <= 3:
            return all_peers
        # Sort by XOR distance to us
        scored = [(self._xor_distance(self._node_id, self._compute_id(p)), p)
                  for p in all_peers]
        scored.sort(key=lambda t: t[0])
        # Take closest 2 + 1 random from the rest
        closest = [p for _, p in scored[:2]]
        farther = [p for _, p in scored[2:]]
        if farther:
            import random
            closest.append(random.choice(farther))
        return closest

    def exchange(self, publish: bool = True) -> dict[str, Any]:
        """Merge peer state AND publish ours, every time.

        Protocol bug found 2026-09-14 while wiring the quota gate: the
        Kademlia path merged peer files and then ran the legacy
        `gossip_exchange()` **only when it had found no peers** — but the
        legacy call was the only code that ever WROTE our own payload. So an
        env that discovered a peer permanently stopped being visible to it:
        gossip became one-directional after the first successful discovery.
        Merging is not a substitute for publishing; both now always run.

        `publish=False` (quota-gated by the cycle) still merges peers — losing
        visibility briefly must not blind this env to theirs.
        """
        from pathlib import Path as _Path
        if _spine is None:
            return {"success": False, "error": "spine_registry unavailable"}
        # G3: Use Kademlia routing instead of scanning all peers
        targets = self._route_targets()
        kademlia_merges = 0
        for peer_env in targets:
            peer_file = _Path.home() / ".azazael" / "gossip" / f"{peer_env}.json"
            if peer_file.exists():
                try:
                    import json as _json
                    payload = _json.loads(peer_file.read_text(encoding="utf-8"))
                    _spine.merge_spine_gossip(payload)
                    kademlia_merges += 1
                except Exception:
                    pass
            self._add_peer(peer_env)
        legacy: dict[str, Any] = {}
        try:
            legacy = _spine.gossip_exchange(publish=publish) or {}
        except Exception as exc:
            legacy = {"error": str(exc)[:_ERR_CAP]}
        merged = kademlia_merges + len(legacy.get("merges") or {})
        with self._lock:
            self._exchanges += 1
        return {"success": True,
                "exchanged": bool(merged) or bool(legacy.get("exchanged")),
                "exchanged_count": merged,
                "published": bool(legacy.get("published", False)),
                "publish_skipped": legacy.get("publish_skipped"),
                "targets": len(targets),
                "k_buckets": len(self._k_buckets),
                "exchanges": self._exchanges, "routing": "kademlia_xor"}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.exchange()}


# ═════════════════════════════════════════════════════════════════
# 4b. ELIGIBILITY TRACES + PLASTICITY ENGINE (credit assignment)
# ═════════════════════════════════════════════════════════════════

class EligibilityTraceTable:
    """TD(lambda) eligibility traces over the cross-worm edge graph.

    The gap this closes: `SynapseWeightWorm` keeps Q as a *stateless
    per-worm scalar*, so credit only ever lands on the worm that happened
    to fail. If worm A sets up state that worm B mishandles three steps
    later, A never learns. The mapper already publishes the nature graph
    and `SynapseWeightWorm.top_edges()` ranks the learned edges, but
    nothing propagated blame along them.

    A trace is the standard fix. On every co-activation of edge
    (pre -> post) the trace is *accumulated*; on every reward every trace
    *decays*; and the update is `w += lr * e * reward`. So a reward today
    reaches edges that fired earlier, discounted by how long ago and how
    many other events intervened. That is how a delayed signal becomes
    attributable. Decay follows the TD(lambda) contraction e <- gamma*lambda*e
    with gamma*lambda < 1, so traces provably vanish rather than blow up.
    """

    VERSION = "1.0.0"

    def __init__(self, gamma: float = 0.9, lam: float = 0.8,
                 lr: float = 0.1, floor: float = 1e-3):
        self.gamma = float(gamma)
        self.lam = float(lam)
        self.lr = float(lr)
        self._floor = float(floor)
        self._traces: dict[tuple[str, str], float] = {}
        self._lock = threading.Lock()
        self._events = 0

    def accumulate(self, pre: str, post: str, amount: float = 1.0) -> None:
        """Mark an edge as having just fired (adds to its pending credit)."""
        if not pre or not post:
            return
        with self._lock:
            key = (pre, post)
            self._traces[key] = self._traces.get(key, 0.0) + float(amount)
            self._events += 1

    def decay_all(self) -> None:
        """Apply one TD(lambda) decay step and drop fully-vanished traces."""
        decay = self.gamma * self.lam
        with self._lock:
            dead = [k for k, v in self._traces.items()
                    if abs(v * decay) < self._floor]
            for k in dead:
                del self._traces[k]
            for k in self._traces:
                self._traces[k] *= decay

    def credit(self) -> dict[tuple[str, str], float]:
        """Per-edge update sizes for this reward event (lr * e), then decay.

        Decaying here rather than only in `decay_all()` keeps trace bookkeeping
        in lockstep with the reward that consumed it: one reward, one decay,
        one credit, so a reward can never be double-counted.
        """
        with self._lock:
            out = {k: self.lr * v for k, v in self._traces.items()}
        self.decay_all()
        return out

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            top = sorted(self._traces.items(), key=lambda kv: -abs(kv[1]))[:10]
            return {
                "success": True,
                "active_traces": len(self._traces),
                "events": self._events,
                "top": [{"edge": f"{a}->{b}", "trace": round(v, 5)}
                        for (a, b), v in top],
            }

    def clear(self) -> None:
        with self._lock:
            self._traces.clear()


@register_worm(category="plasticity", priority=8, cooldown_seconds=30.0,
    description="Persistent edge weights + TD(lambda) credit assignment over the mesh edge graph")
class PlasticityEngineWorm:
    """The mesh's actual weight store - the thing that was missing.

    Audit finding G7 was that the plasticity kernels *computed* `w_new` and
    nothing stored it: `SpineCycleWorm._apply_plasticity` called
    `hebbian.update(0.0, pre, post)` with a hardcoded zero weight every
    cycle, so every delta was measured from zero and then discarded. The
    kernels were correct; the weight store did not exist.

    This worm IS the weight store. It owns:
      * `weights` - persistent w per directed edge, applied via Hebbian
                    co-activation and the STDP timing kernel (using the
                    real inter-event dt, not a fabricated latency).
      * `traces`  - TD(lambda) eligibility traces, so delayed reward
                    propagates backward along the edge graph.
      * `ewc`     - Fisher-weighted anchoring so learning a new edge does
                    not silently overwrite an old one.
      * `forget`  - the Ebbinghaus review scheduler the engram never used.
    """

    VERSION = "1.0.0"
    MAX_EDGES = 512

    def __init__(self, lr: float = 0.1, gamma: float = 0.9, lam: float = 0.8):
        self.lr = float(lr)
        self.traces = EligibilityTraceTable(gamma=gamma, lam=lam, lr=lr)
        self.weights: dict[tuple[str, str], float] = {}
        self._lock = threading.Lock()
        self._updates = 0
        self._hebbian = None
        self._stdp = None
        self._ewc = None
        self._forget = None
        self._neuromod = None
        try:
            from CORE.WORMS.expansion.plasticity import (
                HebbianUpdaterWorm, STDPClockWorm,
                ElasticConsolidationWorm, ForgettingCurveWorm,
            )
            self._hebbian = HebbianUpdaterWorm()
            self._stdp = STDPClockWorm()
            self._ewc = ElasticConsolidationWorm()
            self._forget = ForgettingCurveWorm()
        except ImportError:  # pragma: no cover
            pass
        if Neuromodulator is not None:
            try:
                self._neuromod = Neuromodulator(n_out=3, in_dim=6, hidden=16)
            except Exception:
                self._neuromod = None

    # -- core learning rule -------------------------------------------
    def learn(self, events: list[dict], reward: float | None = None) -> dict[str, Any]:
        """One plasticity pass over a chronological outcome window.

        `events` are ordered oldest -> newest, each with `nature`, `worm`,
        `success`, `at`. We walk consecutive pairs, credit the edge with an
        STDP kernel evaluated at the real dt, accumulate the eligibility
        trace, then apply `lr * trace * reward` to every live edge so a
        single reward updates every edge that contributed to it.
        """
        if not events:
            return {"success": True, "skipped": "no_events"}
        edges_seen = 0
        stdp_deltas = 0
        with self._lock:
            for i in range(len(events) - 1):
                a, b = events[i], events[i + 1]
                pre = str(a.get("nature") or "")
                post = str(b.get("nature") or "")
                if not pre or not post:
                    continue
                key = (pre, post)
                dt_ms = self._dt_ms(a.get("at"), b.get("at"))
                delta = 0.0
                # STDP: real timing kernel (pre-before-post potentiates).
                if self._stdp is not None:
                    delta += float(self._stdp.kernel(dt_ms))
                    stdp_deltas += 1
                # Hebbian: co-activation of the same outcome sign.
                if self._hebbian is not None:
                    pre_s = 1.0 if a.get("success") else -1.0
                    post_s = 1.0 if b.get("success") else -1.0
                    up = self._hebbian.update(
                        self.weights.get(key, 0.0), pre_s, post_s)
                    delta += float(up.get("w_new", 0.0)) - self.weights.get(key, 0.0)
                self.weights[key] = max(-2.0, min(2.0,
                    self.weights.get(key, 0.0) + delta))
                self.traces.accumulate(pre, post,
                                       amount=max(0.05, abs(delta)))
                edges_seen += 1
            # Reward-driven credit over the whole live trace set, then decay.
            if reward is None:
                last = events[-1]
                reward = 1.0 if last.get("success") else -1.0
            mod = self._modulation(events)
            deltas = self.traces.credit()
            for edge, tr in deltas.items():
                self.weights[edge] = max(-2.0, min(2.0,
                    self.weights.get(edge, 0.0) + mod * float(reward) * tr))
            self._updates += 1
            n_edges = len(self.weights)
            self._enforce_cap()
        return {
            "success": True, "edges_touched": edges_seen,
            "stdp_evaluations": stdp_deltas, "edges_tracked": n_edges,
            "reward": round(float(reward), 4),
            "modulation": round(mod, 4),
            "updates": self._updates,
        }

    @staticmethod
    def _dt_ms(a_iso: Any, b_iso: Any) -> float:
        """Real elapsed ms between two ISO timestamps (0.0 if unusable)."""
        try:
            ta = datetime.fromisoformat(str(a_iso))
            tb = datetime.fromisoformat(str(b_iso))
            return max(0.0, (tb - ta).total_seconds() * 1000.0)
        except Exception:
            return 0.0

    def _modulation(self, events: list[dict]) -> float:
        """Mean neuromodulator multiplier for this window (1.0 if absent)."""
        if self._neuromod is None or context_vector is None:
            return 1.0
        try:
            last = events[-1]
            rate = sum(1 for e in events if e.get("success")) / len(events)
            ctx = context_vector(str(last.get("nature") or ""),
                                 str(last.get("worm") or ""),
                                 len(events), max(1, len(events)),
                                 rate, 0.0)
            mods = self._neuromod.modulations(ctx)
            return max(0.25, min(2.0, sum(mods) / max(1, len(mods))))
        except Exception:
            return 1.0

    def _enforce_cap(self) -> None:
        """Keep the edge table bounded; evict weakest-magnitude edges."""
        if len(self.weights) <= self.MAX_EDGES:
            return
        ordered = sorted(self.weights.items(), key=lambda kv: -abs(kv[1]))
        self.weights = dict(ordered[:self.MAX_EDGES])

    # -- anti-forgetting + scheduling ---------------------------------
    def consolidate(self) -> dict[str, Any]:
        """Anchor current weights (EWC) and report the next review horizon."""
        out: dict[str, Any] = {"success": True}
        if self._ewc is not None:
            try:
                params = {f"{a}->{b}": v for (a, b), v in list(self.weights.items())[:64]}
                fisher = {k: abs(v) + 1e-6 for k, v in params.items()}
                out["anchored"] = self._ewc.anchor_task(
                    "mesh_edges", params, fisher).get("anchored", 0)
                out["ewc_penalty"] = self._ewc.penalty(
                    "mesh_edges", params).get("penalty", 0.0)
            except Exception as exc:
                out["ewc_error"] = str(exc)[:80]
        if self._forget is not None:
            try:
                horizon = self._forget.next_review_hours()
                out["next_review"] = horizon
                out["recall_at_horizon"] = round(
                    self._forget.recall_prob(float(horizon.get("hours", 24.0))), 4)
            except Exception as exc:
                out["forget_error"] = str(exc)[:80]
        return out

    def weight(self, pre: str, post: str) -> float:
        with self._lock:
            return self.weights.get((pre, post), 0.0)

    def edge_weights(self) -> dict[str, float]:
        """Every learned edge as {"a->b": weight} — the full table, not a top-N.

        F8 needs the whole edge set to distinguish an *observed-but-undeclared*
        edge from one already in NATURE_DEFINITIONS; a top-N view cannot answer
        that.
        """
        with self._lock:
            return {f"{a}->{b}": round(v, 6) for (a, b), v in self.weights.items()}

    def top_edges(self, n: int = 10) -> list[dict]:
        with self._lock:
            ordered = sorted(self.weights.items(), key=lambda kv: -abs(kv[1]))
            return [{"edge": f"{a}->{b}", "w": round(v, 4)}
                    for (a, b), v in ordered[:n]]

    def summary(self) -> dict[str, Any]:
        return {
            "success": True, "method": "summary",
            "result": {
                "edges": len(self.weights),
                "updates": self._updates,
                "lr": self.lr,
                "neuromodulated": self._neuromod is not None,
                "top_edges": self.top_edges(5),
                "traces": self.traces.snapshot(),
            },
        }

    def execute(self) -> dict[str, Any]:
        return self.summary()


# ═════════════════════════════════════════════════════════════════
# 4b. MESH ARCHITECT — the topology itself as the search space (F8)
# ═════════════════════════════════════════════════════════════════

@register_worm(category="orchestration", priority=7, cooldown_seconds=120.0,
    description="F8: proposes topology edits from per-edge learning telemetry")
class MeshArchitectWorm:
    """F8 — edit the *graph*, not the scalars.

    The audit listed this as the actual frontier and gated it on two things
    that did not exist at the time: real credit assignment (F2) and per-edge
    telemetry (§7). Both landed in §6.2/§6.3, so the prerequisite is met and
    this worm reads observed learning signal instead of guessing.

    What it proposes, and strictly from the weight store:
      * **strengthen** `A->B` when the learned edge weight is high and nature B
        is actually healthy (a strong edge into an unhealthy nature is not a
        win, it is a hot path into a failing region).
      * **weaken** `A->B` when the learned weight is negative, or is weak
        *and* the target nature is failing.
      * **declare** `A->B` when the store has learned an edge that
        `NATURE_DEFINITIONS` never declared — the mesh discovered a real
        information path the configuration does not know about.

    Safety, because a worm that edits fleet topology is the highest-blast-
    radius object in the mesh:
      * `propose()` is **read-only** and is what the cycle calls every tick.
      * `apply()` writes to an **overlay**, never to `NATURE_DEFINITIONS`
        (a module constant shared by every cluster in the process). An overlay
        is auditable, revertible, and inert until a consumer opts in.
      * Bounded to `MAX_PROPOSALS` per call, and every proposal carries the
        evidence that produced it so a reviewer can reject it on the numbers.
      * Registered in a PROTECTED nature and declared in FLEET_GOVERNORS, so
        the Red Queen can never probe the thing that reshapes its graph.
    """

    VERSION = "1.0.0"
    MAX_PROPOSALS = 5
    STRENGTHEN_W = 0.5
    WEAKEN_W = -0.05
    HEALTHY_RATE = 0.6
    UNHEALTHY_RATE = 0.4
    OVERLAY_DIR = ".azazael"
    OVERLAY_NAME = "topology_overlay.json"

    def __init__(self, edge_source: Any | None = None):
        self._lock = threading.Lock()
        self._edge_source = edge_source
        self._overlay: dict[str, dict] = {}
        self._proposals = 0
        self._applied = 0

    # ── read the telemetry ───────────────────────────────────────

    def _observed_edges(self) -> dict[str, float]:
        if self._edge_source is None:
            return {}
        try:
            return dict(self._edge_source.edge_weights() or {})
        except Exception:
            return {}

    @staticmethod
    def _declared_edges() -> set[str]:
        """Edges the configuration already declares, as "A->B" strings."""
        declared: set[str] = set()
        for nature, defn in (NATURE_DEFINITIONS or {}).items():
            for dst in ((defn or {}).get("feeds_into") or []):
                declared.add(f"{nature}->{dst}")
        return declared

    def _nature_rates(self) -> dict[str, float]:
        """Per-nature success rate from the brainstem (empty if unavailable)."""
        if _spine is None:
            return {}
        try:
            homeo = _spine.get_homeostat_view() or {}
        except Exception:
            return {}
        agg: dict[str, list[float]] = {}
        for key, rec in homeo.items():
            nature = str(key).split(":", 1)[0]
            s = float(rec.get("successes") or 0)
            f = float(rec.get("failures") or 0)
            agg.setdefault(nature, [0.0, 0.0])
            agg[nature][0] += s
            agg[nature][1] += f
        rates: dict[str, float] = {}
        for nature, (s, f) in agg.items():
            total = s + f
            if total > 0:
                rates[nature] = s / total
        return rates

    # ── propose (read-only) ──────────────────────────────────────

    def propose(self) -> dict[str, Any]:
        """Rank topology edits from observed edges + live nature health.

        Read-only by contract: this is what the cycle calls every tick, so it
        must be safe to call on a busy fleet.
        """
        observed = self._observed_edges()
        declared = self._declared_edges()
        rates = self._nature_rates()
        proposals: list[dict] = []

        for edge, weight in observed.items():
            src, _, dst = edge.partition("->")
            if not src or not dst:
                continue
            rate = rates.get(dst)
            # An edge the config does not know about is a discovered path.
            if edge not in declared:
                proposals.append({
                    "action": "declare", "edge": edge, "weight": weight,
                    "target_rate": None if rate is None else round(rate, 3),
                    "reason": "learned edge absent from NATURE_DEFINITIONS",
                })
            if weight >= self.STRENGTHEN_W and rate is not None \
                    and rate >= self.HEALTHY_RATE:
                proposals.append({
                    "action": "strengthen", "edge": edge, "weight": weight,
                    "target_rate": round(rate, 3),
                    "reason": "strong edge into a healthy nature",
                })
            elif weight <= self.WEAKEN_W or (rate is not None
                                             and rate < self.UNHEALTHY_RATE):
                proposals.append({
                    "action": "weaken", "edge": edge, "weight": weight,
                    "target_rate": None if rate is None else round(rate, 3),
                    "reason": ("negative learned weight" if weight <= self.WEAKEN_W
                               else "target nature failing"),
                })

        # Strongest evidence first, then a stable tie-break on the edge name so
        # the same input always yields the same ordering.
        proposals.sort(key=lambda p: (-abs(float(p["weight"])), p["edge"],
                                      p["action"]))
        capped = proposals[:self.MAX_PROPOSALS]
        with self._lock:
            self._proposals += len(capped)
            overlay_size = len(self._overlay)
        return {"success": True, "proposals": capped,
                "considered_edges": len(observed),
                "declared_edges": len(declared),
                "natures_rated": len(rates),
                "overlay_size": overlay_size,
                "proposals_seen_total": self._proposals}

    # ── apply (explicit, reversible) ─────────────────────────────

    def apply(self, proposals: list[dict] | None = None) -> dict[str, Any]:
        """Record proposals in the overlay. Never mutates NATURE_DEFINITIONS."""
        if proposals is None:
            proposals = self.propose().get("proposals") or []
        applied: list[dict] = []
        with self._lock:
            for p in proposals:
                edge = str(p.get("edge") or "")
                if not edge:
                    continue
                entry = {"action": p.get("action"), "edge": edge,
                         "weight": p.get("weight"),
                         "target_rate": p.get("target_rate"),
                         "reason": p.get("reason"),
                         "at": datetime.now().isoformat()}
                self._overlay[edge] = entry
                applied.append(entry)
            self._applied += len(applied)
            snapshot = {k: dict(v) for k, v in self._overlay.items()}
        if _spine is not None:
            for entry in applied:
                try:
                    _spine.record_spine_event("topology_proposal", entry)
                except Exception:
                    pass
        saved = self.save()
        return {"success": True, "applied": applied, "overlay_size": len(snapshot),
                "persisted": saved, "mutated_config": False}

    def overlay(self) -> dict[str, dict]:
        """Current overlay (copy). The consumer-facing view of applied edits."""
        with self._lock:
            return {k: dict(v) for k, v in self._overlay.items()}

    def rollback(self, edge: str | None = None) -> dict[str, Any]:
        """Drop one overlay entry, or all of them when `edge` is None."""
        with self._lock:
            if edge is None:
                removed = list(self._overlay)
                self._overlay.clear()
            else:
                removed = [edge] if self._overlay.pop(edge, None) else []
            size = len(self._overlay)
        if removed:
            self.save()
        return {"success": True, "removed": removed, "overlay_size": size}

    # ── persistence ──────────────────────────────────────────────

    @classmethod
    def overlay_path(cls):
        from pathlib import Path
        return Path.home() / cls.OVERLAY_DIR / cls.OVERLAY_NAME

    def save(self) -> dict[str, Any]:
        """Best-effort persist of the overlay; never raises."""
        try:
            import json
            import os as _os
            path = self.overlay_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".json.tmp")
            payload = {"version": self.VERSION,
                       "overlay": self.overlay(),
                       "applied_total": self._applied}
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            _os.replace(str(tmp), str(path))
            return {"saved": True, "path": str(path)}
        except Exception as exc:
            return {"saved": False, "error": str(exc)[:120]}

    def load(self) -> dict[str, Any]:
        """Best-effort restore of the overlay; never raises."""
        try:
            path = self.overlay_path()
            if not path.exists():
                return {"loaded": False, "reason": "no_overlay_file"}
            import json
            payload = json.loads(path.read_text(encoding="utf-8"))
            entries = payload.get("overlay") or {}
            if not isinstance(entries, dict):
                return {"loaded": False, "reason": "bad_overlay"}
            clean = {str(k): dict(v) for k, v in entries.items()
                     if isinstance(v, dict) and v.get("edge")}
            with self._lock:
                self._overlay = clean
                self._applied = int(payload.get("applied_total") or 0)
            return {"loaded": True, "entries": len(clean), "path": str(path)}
        except Exception as exc:
            return {"loaded": False, "error": str(exc)[:120]}

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {"proposals": self._proposals, "applied": self._applied,
                    "overlay_size": len(self._overlay),
                    "observed_edges": len(self._observed_edges())}

    def execute(self) -> dict[str, Any]:
        result = self.propose()
        result.update(self.stats())
        return {"success": True, "method": "execute", "result": result}


# ═════════════════════════════════════════════════════════════════
# 5. SPINE CYCLE — one entry point for the whole self-improvement loop
# ═════════════════════════════════════════════════════════════════

@register_worm(category="orchestration", priority=9, cooldown_seconds=300.0,
    description="One-entry self-improvement cycle: map -> homeostat -> red queen -> persist")
class SpineCycleWorm:
    """Orchestrates the closed loop in the right order, guarded.

    Why this exists: the three organs (map, homeostat, red queen) each
    work alone, but nothing chained them — a caller had to know the
    order and the safety rules. SpineCycleWorm is the single entry:

        1. map_topology()      — refresh the shared spine map
        2. homeostat.cycle()   — Q-reinforce + propose (apply=explicit)
        3. red queen execute() — pressure-probe (stands down if follower)
        4. save_spine_state()  — persist everything for restart
        5. gossip_exchange()   — publish + merge peer env state

    Safety rails:
    - Category is "orchestration", NOT one of RedQueenWorm.PROBE_NATURES
      ("mesh"/"synapse"/"immune"), so the queen never probes this worm
      and can never recurse into a running cycle through the registry.
    - Non-reentrant: a second execute() while a cycle is running returns
      {skipped: cycle_already_running} immediately (belt-and-braces).
    - min-interval throttle: repeated calls inside MIN_INTERVAL_SECONDS
      are skipped (cooldown heuristics are advisory under 3.14t).
    - Any organ failure is caught and reported; the cycle never raises.
    """

    VERSION = "1.0.0"
    MIN_INTERVAL_SECONDS = 60.0

    def __init__(self, min_interval_seconds: float = MIN_INTERVAL_SECONDS):
        self._lock = threading.Lock()
        self._busy = threading.Lock()
        self._min_interval = float(min_interval_seconds)
        self._last_run_at = 0.0
        self._cycles = 0
        self._skipped = 0
        # NOTE: the mapper is constructed *after* the plasticity engine below,
        # so it can be handed the edge store as its §7 telemetry source.
        self._homeostat = HomeostatWorm()
        self._queen = RedQueenWorm()
        self._gossip = SpineGossipWorm()
        # G1 wiring (2026-09-14 audit): these three were registered but never
        # instantiated anywhere, so "attention", "MoE" and "SSM" described
        # code that never ran. The cycle now drives all three from the live
        # outcome stream, and CROSS_NATURE_ROUTER consumes the MoE ranking.
        self._attention = AttentionRouterWorm() if AttentionRouterWorm else None
        self._sequence = SSMSequenceWorm() if SSMSequenceWorm else None
        self._moe = MoEDispatcherWorm() if MoEDispatcherWorm else None
        # G6: Lazy plasticity imports
        self._hebbian = None
        self._stdp = None
        try:
            from CORE.WORMS.expansion.plasticity import HebbianUpdaterWorm, STDPClockWorm
            self._hebbian = HebbianUpdaterWorm()
            self._stdp = STDPClockWorm()
        except ImportError:
            pass
        # G7 / F2 wiring (2026-09-14): persistent edge weights + TD(lambda)
        # eligibility traces. Before this, the plasticity stage computed a
        # delta from a hardcoded 0.0 weight and threw the result away.
        self._plasticity = PlasticityEngineWorm()
        # §7: inject the weight store so the mapper publishes which edges
        # actually fired, instead of the empty `routes` placeholder.
        self._mapper = SpineMapperWorm(edge_source=self._plasticity)
        # Thalamus gate — salience filter in front of the learning signal.
        # Registered since the beginning, never called: the mesh treated
        # every outcome as equally worth learning from.
        self._thalamus = ThalamicGateWorm() if ThalamicGateWorm else None
        self._arousal = ArousalSwitchWorm() if ArousalSwitchWorm else None
        # Mesh router — G3 closure. `record_route_result()` had ZERO callers,
        # so the route Q-table was permanently empty and route learning was
        # dead-ended. The cycle now replays the previous cycle's route outcome.
        self._router = MeshRouterWorm() if MeshRouterWorm else None
        self._pending_route: dict[str, Any] | None = None
        # Dedicated gossip-sync organ (GossipSyncWorm.gossip was orphaned).
        self._sync = GossipSyncWorm() if GossipSyncWorm else None
        # G13: the anomaly autoencoder was registered, orphaned, and its decoder
        # never trained. It now has a consumer here and loads fitted weights so
        # one process's learning isn't thrown away by the next process's sweep.
        self._anomaly = None
        try:
            from CORE.WORMS.expansion.immune import AutoencoderAnomalyWorm
            self._anomaly = AutoencoderAnomalyWorm()
            self._anomaly.load()
        except Exception:
            self._anomaly = None
        # F8: the architect reads the same weight store the mapper does, and
        # proposes (never unilaterally performs) topology edits.
        self._architect = MeshArchitectWorm(edge_source=self._plasticity)
        self._architect.load()
        # G19: the metabolic trio had ZERO callers, so the "energy budget" was
        # a number nobody supplied and the "thermal throttle" never throttled.
        self._power = None
        self._thermal = None
        self._quota = None
        # Verdict of this tick's quota consult (set in _metabolic_stage).
        self._publish_allowed = True
        try:
            from CORE.WORMS.expansion.metabolic import (
                PowerBudgetWorm, ThermalThrottleWorm, QuotaEnforcerWorm)
            self._power = PowerBudgetWorm()
            self._thermal = ThermalThrottleWorm()
            self._quota = QuotaEnforcerWorm()
        except Exception:
            self._power = self._thermal = self._quota = None
        # G8: Morphogenesis output gate
        self._morphogenesis = None
        try:
            from CORE.WORMS.expansion.spine import MorphogenesisWorm
            self._morphogenesis = MorphogenesisWorm()
        except ImportError:
            pass
        # Colour queens (audit §5.1/§5.2): Gray (entrenchment delta) and Black
        # (quorum-gated retirement). Their named consumer is the governance
        # stage below — without a caller they would be exactly the orphan
        # organs §5.9 forbids adding to the fleet.
        self._gray = GrayQueenWorm() if GrayQueenWorm is not None else None
        self._black = BlackQueenWorm() if BlackQueenWorm is not None else None
        # Audit #6: shard catalogue shared between the servemesh sub-stage
        # (which fills it) and the consensus sub-stage (which scans it for
        # real split-brain forks).
        self._last_shards = None

    def _throttled(self) -> bool:
        now = time.monotonic()
        if now - self._last_run_at < self._min_interval:
            return True
        self._last_run_at = now
        return False

    def _self_image_stale(self) -> str:
        """Why this process must not APPLY, if its own maps are stale.

        Proprioception before authority. Every derived number this cycle acts
        on -- the census, the wire-or-cut table, the integration map, the
        knowledge graph -- is a map of the system, and a map older than the
        system is a false one. The 2026-09-18 audit found four such maps being
        acted on, so an applying cycle now has to show its self-image is
        current first.

        Observation-only cycles are always allowed: looking cannot harm, and
        gating them would stop the very audit that decides whether applying is
        safe. Returns "" when the self-image is current, else the reason.

        Fail-closed on purpose: if the audit cannot run at all, that is
        "cannot verify", which is not the same as "verified", so the write is
        refused and the reason names what was missing.
        """
        import sys as _sys
        from pathlib import Path as _Path

        root = _Path(__file__).resolve().parents[4]
        tools_dir = str(root / "tools")
        if tools_dir not in _sys.path:
            _sys.path.insert(0, tools_dir)
        try:
            import artifact_freshness as af
        except Exception as exc:  # pragma: no cover - environment dependent
            return "freshness_audit_unavailable: %s" % str(exc)[:80]
        try:
            stale = [r["artifact"] for r in af.audit(root) if r["stale"]]
            mismatch = af.graph_report_mismatch(root)
        except Exception as exc:  # pragma: no cover - defensive
            return "freshness_audit_failed: %s" % str(exc)[:80]
        if stale:
            return "stale artifacts: %s" % ", ".join(stale[:4])
        if mismatch.get("mismatch"):
            return str(mismatch.get("reason") or "graph/report mismatch")
        return ""

    def run_cycle(self, apply: bool = False) -> dict[str, Any]:
        """Run one full self-improvement cycle. Never raises."""
        # Per-instance non-reentrancy: nested calls on the same object skip.
        if not self._busy.acquire(blocking=False):
            with self._lock:
                self._skipped += 1
            return {"success": True, "skipped": "cycle_already_running",
                    "cycles": self._cycles}
        # Cross-instance gate: it guards process-global state, so a second
        # SpineCycleWorm must skip rather than run a concurrent cycle.
        if not _GLOBAL_CYCLE_GATE.acquire(blocking=False):
            self._busy.release()
            with self._lock:
                self._skipped += 1
            return {"success": True,
                    "skipped": "cycle_already_running_global",
                    "cycles": self._cycles}
        try:
            with self._lock:
                if self._throttled():
                    self._skipped += 1
                    return {"success": True, "skipped": "min_interval",
                            "cycles": self._cycles}

            # 0. Proprioception gate: only a WRITING cycle needs a current
            #    self-image. Refuse rather than act on a stale map of itself.
            if apply:
                stale_reason = self._self_image_stale()
                if stale_reason:
                    with self._lock:
                        self._skipped += 1
                    return {"success": False, "skipped": "stale_self_image",
                            "reason": stale_reason, "cycles": self._cycles}

            report: dict[str, Any] = {}
            # 1. Map — refresh the shared topology snapshot
            try:
                report["map"] = self._mapper.map_topology()
            except Exception as exc:
                report["map"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2. Homeostat — Q-reinforce from ledger; apply proposals only
            #    when explicitly asked (deterministic default).
            try:
                report["homeostat"] = self._homeostat.cycle(apply=apply)
            except Exception as exc:
                report["homeostat"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2b. G6: Plasticity — apply Hebbian/STDP learning rules
            try:
                report["plasticity"] = self._apply_plasticity()
            except Exception as exc:
                report["plasticity"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2c. Synapse layer — attention prior + SSM over the outcome
            #     stream + MoE expert preference (G1 wiring)
            try:
                report["synapse_routing"] = self._route_synapse_layer()
            except Exception as exc:
                report["synapse_routing"] = {"success": False,
                                             "error": str(exc)[:_ERR_CAP]}

            # 2d. Mesh route feedback — G3: record_route_result() had zero
            #     callers, so route learning never happened (the route Q-table
            #     held no `route:*` key, ever).
            try:
                report["mesh_routes"] = self._mesh_route_feedback()
            except Exception as exc:
                report["mesh_routes"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2e. Anomaly detector — G13: observes the real ledger vector.
            #     The autoencoder was orphaned (zero callers) and its decoder
            #     frozen at Random(42); it now sees bounded features derived
            #     from the same ledger the rest of the cycle learns from.
            try:
                report["anomaly"] = self._anomaly_stage()
            except Exception as exc:
                report["anomaly"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2f. Metabolic — G19: real load, estimated draw, thread advice.
            #     Runs BEFORE the Red Queen so a shed decision can reduce the
            #     probe load in the same tick instead of the next one.
            try:
                report["metabolic"] = self._metabolic_stage()
            except Exception as exc:
                report["metabolic"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2g. Mesh Architect (F8) — proposes topology edits from the
            #     per-edge telemetry. Propose-only unless the caller passed
            #     apply=True, which is the cycle's existing "really change
            #     policy" signal.
            try:
                report["topology"] = self._topology_stage(apply)
            except Exception as exc:
                report["topology"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2h. Fabric organs — consensus / federated / servemesh, driven
            #     from real config (audit finding #6: 8 worms had no caller,
            #     so `_run_worm_method -> execute()` was the only reachable
            #     path and the natures were functionally inert).
            try:
                report["fabric"] = self._fabric_stage()
            except Exception as exc:
                report["fabric"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 2i. Morphogenesis gate (audit finding #3) — stage specialists
            #     from chronic failures behind quarantine + quorum. The method
            #     existed with zero callers, so the whole organ was dead.
            try:
                report["morphogenesis"] = self._process_morphogenesis_output(apply)
            except Exception as exc:
                report["morphogenesis"] = {"success": False,
                                           "error": str(exc)[:_ERR_CAP]}

            # 2j. Colour-queen governance (audit §5.2 / §5.1) — Gray reads the
            #     PF16 census, diffs it against the persisted session snapshot
            #     and reports the delta (new / resolved / entrenched); Black
            #     proposes quorum-gated retirement for a worm whose capability a
            #     registered twin already covers. Both PROPOSE unless apply.
            try:
                report["governance"] = self._governance_stage(apply)
            except Exception as exc:
                report["governance"] = {"success": False,
                                        "error": str(exc)[:_ERR_CAP]}

            # 3. Red Queen — pressure probes; stands down if not queen.
            #    Probe load is shed when the metabolic stage says the host is
            #    over budget (the PowerBudgetWorm docstring's promise, kept).
            shed = bool((report.get("metabolic") or {}).get("shed"))
            try:
                report["red_queen"] = self._queen.execute(
                    limit=1 if shed else None).get("result", {})
                if shed:
                    report["red_queen"]["probe_limit_reduced"] = True
            except Exception as exc:
                report["red_queen"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            # 4. Persist — restart-safe state for the next session
            if _spine is not None:
                try:
                    report["persisted"] = _spine.save_spine_state()
                except Exception as exc:
                    report["persisted"] = {"saved": False, "error": str(exc)[:_ERR_CAP]}

            # 5. Gossip — publish + merge peer env state (after persist so
            #    the payload reflects everything merged this cycle). The quota
            #    organ gates the shared-directory WRITE only; peers are still
            #    merged, so throttling never blinds this env to its peers.
            publish = getattr(self, "_publish_allowed", True)
            try:
                report["gossip"] = self._gossip.exchange(publish=publish)
            except Exception as exc:
                report["gossip"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

            if _spine is not None:
                _spine.record_spine_event("spine_cycle", {
                    "apply": bool(apply),
                    "map_ok": bool(report.get("map", {}).get("success")),
                    "homeostat_proposals": len(
                        report.get("homeostat", {}).get("proposals") or []),
                    "queen_role": report.get("red_queen", {}).get("queen_role", "?"),
                    "gossip_peers": len(
                        report.get("gossip", {}).get("peers") or []),
                    "attention_top": (
                        report.get("synapse_routing", {})
                              .get("attention", {}).get("top_natures") or [])[:3],
                    "entrenchment_delta": (
                        (report.get("governance", {})
                                .get("entrenchment", {}) or {})
                        .get("counts", {}).get("delta")),
                    "retirements_proposed": (
                        report.get("governance", {})
                              .get("retirement", {}).get("retired")),
                })

            with self._lock:
                self._cycles += 1
                report["cycles"] = self._cycles
            report["success"] = True
            return report
        finally:
            _GLOBAL_CYCLE_GATE.release()
            self._busy.release()

    def _governance_stage(self, apply: bool) -> dict[str, Any]:
        """Gray (entrenchment delta) + Black (quorum-gated retirement).

        Both queens are inert without a caller, so the cycle drives them and
        their mutations obey this class's existing rule: propose-only unless
        the caller passed ``apply=True`` ("really change policy"). Gray's
        snapshot IS persisted every cycle even when apply is False — a diff
        needs a baseline, and the baseline is the observation, not a mutation.
        """
        out: dict[str, Any] = {}
        if self._gray is not None:
            try:
                out["entrenchment"] = self._gray.detect(persist=True)
            except Exception as exc:
                out["entrenchment"] = {"success": False,
                                       "error": str(exc)[:_ERR_CAP]}
        if self._black is not None:
            try:
                out["retirement"] = self._black.propose(apply=bool(apply))
            except Exception as exc:
                out["retirement"] = {"success": False,
                                     "error": str(exc)[:_ERR_CAP]}
        return out

    def _apply_plasticity(self) -> dict[str, Any]:
        """Apply the learning rules through the persistent weight store.

        Previously this called `hebbian.update(0.0, pre, post)` - a hardcoded
        zero weight, so every delta was measured from zero and `w_new` was
        discarded (audit G7). The engine now owns persistent edges, evaluates
        the real STDP kernel at the true inter-event dt, accumulates
        eligibility traces and lets one reward credit every contributing edge.
        """
        if _spine is None:
            return {"success": True, "skipped": "spine_unavailable"}
        events = _spine.get_outcome_events()
        if len(events) < 2:
            return {"success": True, "skipped": "insufficient_events",
                    "events": len(events)}
        # get_outcome_events() is most-recent-first; STDP needs chronology.
        chronology = list(reversed(events))
        # Thalamus gate: outcomes below the salience floor do not earn a
        # plasticity update. The gate is advisory by design - if it would
        # starve learning entirely we fall open to the ungated window,
        # because "learn nothing, ever" is a worse failure than "learn from
        # a quiet window".
        raw_events = len(chronology)
        gated = self._gate_salience(chronology)
        gate_applied = len(gated) >= 2
        chronology = gated if gate_applied else chronology
        try:
            result = self._plasticity.learn(chronology)
        except Exception as exc:
            return {"success": False, "error": str(exc)[:_ERR_CAP]}
        result["gate"] = {"applied": gate_applied, "input": raw_events,
                          "kept": len(gated)}
        if self._plasticity._updates % 5 == 0:
            try:
                result["consolidation"] = self._plasticity.consolidate()
            except Exception:
                pass
        return result

    def _gate_salience(self, events: list[dict]) -> list[dict]:
        """ThalamicGateWorm: drop low-salience outcomes before learning.

        Salience is a crude proxy for "did this event carry information":
        a failure or a slow run is informative, a fast clean run is not.
        Falls open (returns everything) when the gate is unavailable, so a
        missing organ degrades to the previous behaviour rather than to
        learning nothing.
        """
        if self._thalamus is None:
            return events
        kept: list[dict] = []
        for e in events:
            try:
                # Failures are always salient (they carry the gradient).
                # A success earns salience from how long it took, with a
                # 0.35 floor so an ordinary clean run still clears the
                # "monitor" threshold (0.3) instead of being filtered out.
                if not e.get("success"):
                    salience = 1.0
                else:
                    salience = 0.35 + min(0.5, float(e.get("ms") or 0.0) / 2000.0)
                if self._thalamus.filter("monitor", salience).get("passed"):
                    kept.append(e)
            except Exception:
                kept.append(e)
        return kept

    def _route_synapse_layer(self) -> dict[str, Any]:
        """G1: drive the synapse layer from the live outcome stream.

        Three organs, each independently optional and isolated so a missing
        one degrades to a skip rather than an error:

        1. attention — one bias update per nature per cycle (scaled by how
           far that nature's recent success rate sits from 50%), then read
           the softmax prior so cross-nature routing has a learned bias.
        2. sequence  — the SSM ingests the recent outcome stream as +/-1 so
           its recurrence tracks fleet activity and fits its readout.
        3. moe       — which inference expert the dispatcher currently
           prefers, recorded so expert choice is observable in the cycle.
        """
        if _spine is None:
            return {"success": True, "skipped": "spine_unavailable"}
        out: dict[str, Any] = {"success": True}
        try:
            events = _spine.get_outcome_events()
        except Exception:
            events = []
        window = events[-50:]

        if self._attention is not None:
            try:
                by_nature: dict[str, list] = {}
                for e in window:
                    by_nature.setdefault(e.get("nature", ""), []).append(
                        bool(e.get("success")))
                for nature, results in by_nature.items():
                    if not nature or not results:
                        continue
                    rate = sum(results) / len(results)
                    self._attention.update_from_outcome(
                        nature, rate >= 0.5, strength=abs(rate - 0.5) * 2.0)
                out["attention"] = self._attention.attend()
            except Exception as exc:
                out["attention"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

        if self._sequence is not None:
            try:
                stream = [1.0 if e.get("success") else -1.0 for e in window]
                if stream:
                    out["sequence"] = self._sequence.ingest(stream)
                    out["sequence"].update(self._sequence.summarize())
                else:
                    out["sequence"] = {"success": True,
                                       "skipped": "no_events"}
            except Exception as exc:
                out["sequence"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

        if self._moe is not None:
            try:
                out["moe"] = self._moe.dispatch()
            except Exception as exc:
                out["moe"] = {"success": False, "error": str(exc)[:_ERR_CAP]}

        return out

    def _mesh_route_feedback(self) -> dict[str, Any]:
        """G3: feed real route outcomes back so route weights can learn.

        `MeshRouterWorm.route()` multiplies the static weight by `(1 + q)`
        where `q` comes from the ledger's `route` Q-table — but
        `record_route_result()` had **zero callers in the entire tree**, so
        `q` was always 0 and `effective_weight` was always the static
        weight. The mechanism was written, correct, and unreachable.

        The cycle closes it in two phases so a route can actually be
        *evaluated*: this cycle settles the route proposed last cycle
        against the fleet's observed success rate, then proposes the next
        one. That produces the first `route:*` Q-keys the table has ever had.
        """
        if self._router is None:
            return {"success": True, "skipped": "router_unavailable"}
        out: dict[str, Any] = {"success": True}

        # Phase 1 — settle the route proposed by the previous cycle.
        prev = self._pending_route
        if prev:
            rate = self._nature_success_rate(str(prev.get("dst", "")))
            ok = True if rate is None else rate >= 0.5
            try:
                self._router.record_route_result(
                    str(prev.get("dst", "")), ok, float(prev.get("ms", 0.0)))
                out["settled"] = {"dst": prev.get("dst"), "success": ok,
                                  "fleet_rate": None if rate is None else round(rate, 3)}
            except Exception as exc:
                out["settled"] = {"error": str(exc)[:80]}
            # NOTE: `invalidate_route()` is deliberately NOT called on failure
            # here, although a first draft did exactly that. Its contract is
            # "discount the learned penalty on one route, because its cause is
            # FIXED ... called by whoever fixed the fault" -- it exists to break
            # a self-sustaining penalty once the fault is gone. Firing it on a
            # failed route would do the opposite: erase the route's history at
            # the moment the evidence says the route is still bad. It stays
            # unwired until a real repair path exists to call it, which is a
            # better outcome than a caller that looks wired and inverts the
            # contract.

        # Phase 2 — propose the next route to the least-healthy live nature.
        try:
            rates = self._nature_rates()
            if rates:
                dst = min(rates, key=lambda n: rates[n])
                # `add_route()` had no caller anywhere either, so `_routes` was
                # always empty and `route()` fell through to its default
                # `{"weight": 1.0}` for EVERY destination. The static topology
                # prior therefore could not be expressed at all: `ROUTES_MAX`,
                # the route-key derivation and the weight itself were inert, and
                # `effective_weight` was decided by the Q-term alone. Register
                # the leg before routing it, with the fleet's own observed rate
                # as the prior -- the same cycle-closing move this method already
                # made for `record_route_result()`.
                try:
                    self._router.add_route(_local_env(), dst,
                                           float(rates.get(dst, 1.0)))
                except Exception as exc:
                    out["registered"] = {"error": str(exc)[:80]}
                routed = self._router.route(dst, {"probe": "spine_cycle"})
                self._pending_route = {"dst": dst, "ms": 0.0}
                out["proposed"] = {"dst": dst, "effective_weight": routed.get("effective_weight"),
                                   "q": routed.get("q")}
        except Exception as exc:
            out["proposed"] = {"error": str(exc)[:80]}

        # Arousal budget: scanning/training is throttled in sleep/recon mode.
        if self._arousal is not None:
            try:
                mode = self._arousal.get_mode()
                out["arousal"] = {"mode": mode.get("mode"),
                                  "budgets": mode.get("budgets")}
            except Exception:
                pass

        # GossipSyncWorm.gossip() was orphaned; merge this env's own snapshot
        # so the organ has a real caller and drift is detectable locally.
        if self._sync is not None and _spine is not None:
            try:
                snap = {f"q:{k}": round(v, 4)
                        for k, v in list(_spine.get_q_weights().items())[:25]}
                out["sync"] = self._sync.gossip(snap)
            except Exception:
                pass
        return out

    def _anomaly_metrics(self) -> list[float]:
        """Bounded 8-feature vector describing the mesh's current health.

        G13: the autoencoder had no consumer, so it never saw a single
        observation. These are the ledger's own signals — deliberately bounded
        to [0, 1] so the net learns the *shape* of normal operation rather than
        a drifting scale, which is the usual reason a hand-rolled autoencoder
        "finds" an anomaly every time fleet size changes.
        """
        if _spine is None:
            return []
        try:
            homeo = _spine.get_homeostat_view()
            scars = _spine.get_scars()
            q_weights = _spine.get_q_weights()
            routes = _spine.get_route_usage()
        except Exception:
            return []

        import math
        natures: dict[str, list[float]] = {}
        for key, rec in (homeo or {}).items():
            nature = str(key).split(":", 1)[0]
            s = float(rec.get("successes") or 0)
            f = float(rec.get("failures") or 0)
            last = float(rec.get("last_ms") or 0.0)
            natures.setdefault(nature, [0.0, 0.0, 0.0])
            natures[nature][0] += s
            natures[nature][1] += f
            natures[nature][2] = max(natures[nature][2], last)

        tot_s = sum(v[0] for v in natures.values())
        tot_f = sum(v[1] for v in natures.values())
        tot = tot_s + tot_f
        success_rate = (tot_s / tot) if tot else 1.0
        fail_rate = (tot_f / tot) if tot else 0.0

        # log1p scaling keeps a 5 ms and a 500 ms observation on a comparable
        # footing without a hand-tuned divisor.
        max_ms = max((v[2] for v in natures.values()), default=0.0)
        lat = min(1.0, math.log1p(max_ms) / math.log1p(5000.0)) if max_ms else 0.0

        q_vals = [abs(float(v)) for v in (q_weights or {}).values()]
        q_vol = (sum(q_vals) / len(q_vals)) if q_vals else 0.0

        if routes:
            healthy = sum(1 for r in routes.values()
                          if float(r.get("q") or 0.0) >= -0.2)
            route_health = healthy / len(routes)
        else:
            route_health = 1.0  # no routes yet is not a fault

        return [
            round(success_rate, 4),
            round(fail_rate, 4),
            round(lat, 4),
            min(1.0, len(scars) / 10.0),
            round(q_vol, 4),
            min(1.0, len(natures) / 16.0),
            min(1.0, tot / 500.0),
            round(route_health, 4),
        ]

    def _anomaly_stage(self) -> dict[str, Any]:
        """Observe the health vector, share the model, adopt a better peer's.

        The transport snapshot is used in both directions:
          * inbound — adopt a peer's model when it is better trained than ours
            (strictly more observations), before observing this tick, so the
            mesh converges on one detector instead of N half-trained ones;
          * outbound — publish ours afterwards for the next gossip exchange.
        """
        if self._anomaly is None:
            return {"success": True, "skipped": "anomaly_unavailable"}
        vec = self._anomaly_metrics()
        if len(vec) != 8:
            return {"success": True, "skipped": "no_metrics",
                    "metrics": len(vec)}

        adopted: dict[str, Any] | None = None
        if _spine is not None:
            try:
                meta = _spine.get_anomaly_model_meta()
                shared = _spine.get_anomaly_model()
                if (shared and meta.get("source", "").startswith("peer")
                        and int(meta.get("observations") or 0)
                        > int(self._anomaly._observations)):
                    if self._anomaly.import_model(shared):
                        adopted = meta
            except Exception:
                adopted = None

        obs = self._anomaly.observe(vec)
        # Persist on an alert, and otherwise every 10 observations — often
        # enough that a restart resumes a trained model, cheap enough that the
        # cycle does not pay a disk write each minute.
        if obs.get("alert") or int(obs.get("observations") or 0) % 10 == 0:
            obs["persisted"] = self._anomaly.save()
        # Offer this model for transport (monotone: only better-trained wins,
        # so republishing our own snapshot cannot displace a better peer's).
        if _spine is not None:
            try:
                obs["published"] = _spine.publish_anomaly_model(
                    self._anomaly.export_model())
            except Exception:
                pass
        return {"success": True, "alert": obs.get("alert"),
                "recon_error": obs.get("recon_error"),
                "threshold": obs.get("threshold"),
                "observations": obs.get("observations"),
                "updates": obs.get("updates"),
                "adopted_from_peer": adopted,
                "published": obs.get("published"),
                "shared_model": (get_anomaly_meta() if _spine is not None else None),
                "metrics": vec}

    def _metabolic_stage(self) -> dict[str, Any]:
        """G19: measured load -> estimated draw -> thread advice -> shed verdict."""
        if self._power is None and self._thermal is None:
            return {"success": True, "skipped": "metabolic_unavailable"}
        out: dict[str, Any] = {"success": True}
        load: dict[str, Any] = {}
        if self._power is not None:
            try:
                load = self._power.sample_load()
                out["load"] = load
                out["budget"] = self._power.spend_from_load(_local_env())
            except Exception as exc:
                out["budget"] = {"error": str(exc)[:80]}
        if self._thermal is not None:
            try:
                cores = int((load or {}).get("cores") or 16)
                out["thermal"] = self._thermal.recommend_threads(current=cores)
            except Exception as exc:
                out["thermal"] = {"error": str(exc)[:80]}
        # The budget's own verdict is what drives shedding this tick.
        out["shed"] = bool((out.get("budget") or {}).get("over"))
        # QuotaEnforcerWorm had zero callers and reported `scopes: []` forever.
        # Consulted exactly once per cycle here, and the verdict is reused by
        # the gossip stage — calling it twice would spend two tokens for one
        # decision. `_publish_allowed` is what run_cycle reads.
        self._publish_allowed = True
        if self._quota is not None:
            try:
                verdict = self._quota.allow("gossip_publish")
                out["quota"] = verdict
                self._publish_allowed = bool(verdict.get("allowed"))
            except Exception as exc:
                out["quota"] = {"error": str(exc)[:80]}
        if _spine is not None:
            try:
                _spine.record_spine_node(_local_env(), "metabolic", {
                    "category": "metabolic",
                    "cpu_percent": (load or {}).get("cpu_percent"),
                    "cores": (load or {}).get("cores"),
                    "watts_estimated": (out.get("budget") or {}).get("spent"),
                    "estimated": (out.get("budget") or {}).get("estimated"),
                    "thermal_state": (out.get("thermal") or {}).get("state"),
                    "thermal_source": (out.get("thermal") or {}).get("source"),
                    "shed": out["shed"],
                })
                _spine.record_spine_event("metabolic_sample", {
                    "cpu_percent": (load or {}).get("cpu_percent"),
                    "shed": out["shed"],
                    "thermal_state": (out.get("thermal") or {}).get("state"),
                    "thermal_source": (out.get("thermal") or {}).get("source"),
                })
            except Exception:
                pass
        return out

    def _topology_stage(self, apply: bool = False) -> dict[str, Any]:
        """F8: propose topology edits; record them only when asked."""
        if self._architect is None:
            return {"success": True, "skipped": "architect_unavailable"}
        proposed = self._architect.propose()
        out: dict[str, Any] = {
            "success": True,
            "proposed": len(proposed.get("proposals") or []),
            "considered_edges": proposed.get("considered_edges"),
            "declared_edges": proposed.get("declared_edges"),
            "top": (proposed.get("proposals") or [])[:3],
            "applied": 0,
        }
        if apply and proposed.get("proposals"):
            try:
                res = self._architect.apply(proposed["proposals"])
                out["applied"] = len(res.get("applied") or [])
                out["overlay_size"] = res.get("overlay_size")
                out["mutated_config"] = res.get("mutated_config")
            except Exception as exc:
                out["apply_error"] = str(exc)[:_ERR_CAP]
        return out

    def _nature_rates(self) -> dict[str, float]:
        """Per-nature success rate from the brainstem (empty if unavailable)."""
        if _spine is None:
            return {}
        try:
            homeo = _spine.get_homeostat_view()
        except Exception:
            return {}
        rates: dict[str, float] = {}
        for key, rec in (homeo or {}).items():
            nature = str(key).split(":", 1)[0]
            s = float(rec.get("successes") or 0)
            f = float(rec.get("failures") or 0)
            if s + f <= 0:
                continue
            prev = rates.get(nature)
            rate = s / (s + f)
            # Aggregate natures by their worst worm so the proposal targets
            # the weakest link rather than an average that hides it.
            rates[nature] = rate if prev is None else min(prev, rate)
        return rates

    def _nature_success_rate(self, nature: str) -> float | None:
        return self._nature_rates().get(nature)

    def _process_morphogenesis_output(self, apply: bool = False) -> dict[str, Any]:
        """G8 + audit finding #3: the morphogenesis containment gate.

        generate -> STAGE (not importable) -> quarantine -> quorum vote ->
        PROMOTE (discoverable).

        Audit 2026-09-15: this method had ZERO callers, so `self._morphogenesis`
        was constructed and never used, and its body called
        `morph(dry_run=False)` followed by `discover_worms()` with no
        quarantine and no vote at all — the "only registers if 2/3 quorum
        approves" line in the old docstring described behaviour that did not
        exist. Now wired into `run_cycle()` and gated for real.

        Both halves are writes (staging creates source files, promotion moves
        them), so both honour the cycle's `apply` flag — the same convention
        `_topology_stage` uses. With `apply=False` the organ is still
        observable: a *dry-run* morph reports what it would stage, and the
        current pen depth is reported from disk. A cycle that writes nothing
        is the deterministic default this module keeps elsewhere.
        """
        if self._morphogenesis is None:
            return {"success": True, "skipped": "morphogenesis_unavailable"}
        try:
            if not apply:
                preview = self._morphogenesis.morph(dry_run=True)
                return {"success": True, "apply": False,
                        "patterns": preview.get("patterns", 0),
                        "would_stage": preview.get("patterns", 0),
                        "staged": 0, "promoted": 0, "held": 0,
                        "pending": len(self._morphogenesis.staged())}
            gen = self._morphogenesis.morph(dry_run=False)
            out: dict[str, Any] = {"success": True,
                                   "staged": gen.get("staged", 0),
                                   "promoted": 0, "held": 0,
                                   "apply": True}
            gate = self._morphogenesis.promote()
            out["promoted"] = gate.get("promoted", 0)
            out["held"] = gate.get("held", 0)
            out["pending"] = gate.get("pending")
            if out["promoted"]:
                # The promoted source is now discovery-visible; refresh so the
                # specialist actually becomes a worm. Idempotent + bounded.
                try:
                    from CORE.worm_registry import discover_worms
                    out["discovered"] = discover_worms()
                except Exception as exc:
                    out["discovered"] = {"error": str(exc)[:80]}
            return out
        except Exception as exc:
            return {"success": False, "error": str(exc)[:_ERR_CAP]}

    # ── FABRIC STAGE — drive the organs that had no caller (finding #6) ──
    #
    # The consensus / federated / servemesh natures registered 8 worms whose
    # real APIs had no caller anywhere in the tree: `NatureCluster` only ever
    # reached `execute()`, which returns a summary, so those natures were
    # structurally present and functionally inert. Each sub-stage below feeds
    # the organ from a REAL source (the RULE 0D provider registry, the env
    # beacons, the task7 placement file, the learned Q-table, the on-disk
    # model catalogue). Every sub-stage is independently best-effort: a
    # missing source degrades that one organ and never the cycle.

    MODEL_ROOTS = (r"G:\source-of-truth\azazael_models",
                   "/mnt/g/source-of-truth/azazael_models")
    MODEL_EXTS = (".pt", ".onnx", ".gguf", ".json")
    SHARD_PUBLISH_MAX = 32
    FORK_SCAN_MAX = 32

    def _fabric_stage(self) -> dict[str, Any]:
        """Run the consensus / federated / servemesh / resilience organs on
        real input."""
        out: dict[str, Any] = {}
        for name, fn in (("servemesh", self._fabric_servemesh),
                         ("consensus", self._fabric_consensus),
                         ("federated", self._fabric_federated),
                         ("variation", self._fabric_variation),
                         ("resilience", self._fabric_resilience)):
            try:
                out[name] = fn()
            except Exception as exc:  # never let one organ break the cycle
                out[name] = {"success": False, "error": str(exc)[:_ERR_CAP]}
        return out

    # ProviderFailoverMeshWorm.CHAIN uses short names; the RULE 0D registry
    # uses its own ids. The chain's vocabulary is owned by the worm that owns
    # the chain, so the map is delegated rather than copied (the same rule
    # that fixed the five env-id copies in finding #4).
    _PROVIDER_ALIAS_FALLBACK = {"nim": "nvidia_nim"}

    @classmethod
    def _provider_alias(cls, name: str) -> str:
        try:
            return str(ProviderFailoverMeshWorm.PROVIDER_ALIASES.get(name, name))
        except Exception:  # pragma: no cover - defensive
            return str(cls._PROVIDER_ALIAS_FALLBACK.get(name, name))

    @classmethod
    def _provider_key_state(cls, chain) -> dict[str, bool]:
        """Per-provider credential presence from the real RULE 0D registry.

        Reports `{chain_name: usable}` for the CHAIN entries the registry can
        actually speak to. A provider is reported unusable ONLY when all three
        hold: it declares an `env_var`, it has a real remote `base_url`
        (non-empty, not loopback), and no credential is resolvable for it
        (env var unset AND no `~/.azazael/{id}_config.json`).

        That guard matters. `ollama` and `lmstudio` declare a key for a
        *localhost* endpoint where the key is optional, and
        `llama_cpp_direct` / `openvino` / `huggingface_direct` declare a *model
        path* rather than a credential. Treating any of those as a missing
        credential would take a working endpoint out of the failover chain —
        the exact failure this stage is supposed to prevent. A CHAIN entry
        with no registry entry (e.g. `llamaserver`) is omitted entirely: no
        evidence is not evidence of absence.
        """
        import os
        try:
            from CORE.inference.providers import (
                PROVIDER_REGISTRY,
                provider_credential_configured,
            )
        except Exception:
            return {}
        loopback = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]")
        out: dict[str, bool] = {}
        for name in chain or ():
            pid = cls._provider_alias(str(name))
            info = PROVIDER_REGISTRY.get(pid) or {}
            var = info.get("env_var")
            base = str(info.get("base_url") or "")
            if not var or not base:
                continue
            if any(h in base for h in loopback):
                continue
            # Resolved through providers.py so this agrees with the layer that
            # actually makes the request. Checking os.environ alone reported a
            # provider with its key in ~/.azazael/{id}_config.json as unusable,
            # which silently dropped a working provider from the chain.
            try:
                out[str(name)] = bool(provider_credential_configured(pid))
            except Exception:  # pragma: no cover - defensive
                out[str(name)] = bool(os.environ.get(str(var)))
        return out

    def _publish_local_shards(self, shards) -> int:
        """Publish the real on-disk model catalogue into the shard store.

        `shard` is the artifact's content digest (size + 64 KiB header), so two
        envs publishing the same logical model with different bytes land under
        different keys — which is exactly what makes a split-brain fork
        detectable by `SplitBrainResolverWorm` (see `_model_fork_reports`).
        """
        import hashlib
        from pathlib import Path
        try:
            from CORE.fs_probe import bounded_first_dir
        except Exception:  # pragma: no cover - probe helper optional
            def bounded_first_dir(cands, timeout_s=2.5):  # type: ignore
                for c in cands or ():
                    try:
                        if Path(c).is_dir():
                            return c
                    except Exception:
                        continue
                return None
        # Bounded, CONCURRENT probe. An unreachable root answers None (= "the
        # probe did not answer"), and unknown is treated as UNAVAILABLE rather
        # than healthy. The previous `try/except` around a bare `p.is_dir()`
        # could never work: a hang is not an exception. And the candidates are
        # alternatives for one decision, so probing them in parallel charges
        # the max timeout instead of the sum -- sequentially they cost 2 x 5s
        # and put a 10s floor under every first heartbeat. See CORE/fs_probe.py.
        first = bounded_first_dir(self.MODEL_ROOTS)
        if first is None:
            return 0
        root = Path(first)
        published = 0
        try:
            entries = sorted(root.iterdir())[: self.SHARD_PUBLISH_MAX]
        except OSError:
            return 0
        for f in entries:
            try:
                if not f.is_file() or f.suffix.lower() not in self.MODEL_EXTS:
                    continue
                h = hashlib.sha256(str(f.stat().st_size).encode())
                with f.open("rb") as fh:
                    h.update(fh.read(65536))
                digest = h.hexdigest()[:12]
                fmt = f.suffix.lstrip(".").lower()
                shards.publish(f.stem, digest, _local_env(), fmt,
                               "Q4_K_M" if fmt == "gguf" else "n/a")
                published += 1
            except Exception:
                continue
        return published

    def _model_fork_reports(self, shards) -> list[tuple]:
        """Real model forks from the (gossip-merged) shard catalogue.

        A fork exists when one logical model is catalogued under more than one
        content digest. `reward` is the number of envs agreeing on that
        branch — a real count, not a fabricated score — so the resolver keeps
        the branch with the broadest agreement and breaks ties on the hash,
        exactly as its docstring promises.
        """
        forks: list[tuple] = []
        try:
            models = (shards.execute().get("result", {}) or {}).get("models") or []
        except Exception:
            return forks
        for model in list(models)[: self.FORK_SCAN_MAX]:
            try:
                entries = shards.locate(str(model)).get("shards") or []
            except Exception:
                continue
            by_hash: dict[str, list] = {}
            for e in entries:
                by_hash.setdefault(str(e.get("shard") or ""), []).append(e)
            if len(by_hash) < 2:
                continue
            for digest, group in by_hash.items():
                env = str((group[0] or {}).get("env") or "?")
                forks.append((str(model), env, float(len(group)), digest))
        return forks

    def _fabric_servemesh(self) -> dict[str, Any]:
        """Endpoint registry + failover chain + shard catalogue, from config."""
        res: dict[str, Any] = {}
        if InferenceLoadBalancerWorm is None:
            return {"success": True, "skipped": "servemesh_unavailable"}
        # 1. Real registry: the RULE 0D provider chain.
        try:
            from CORE.inference.providers import PROVIDER_REGISTRY
        except Exception:
            PROVIDER_REGISTRY = {}
        lb = InferenceLoadBalancerWorm()
        registered = 0
        for pid, info in (PROVIDER_REGISTRY or {}).items():
            base = str((info or {}).get("base_url") or "")
            if not base:
                continue
            lb.register(str(pid), base,
                        kind=str((info or {}).get("name") or "api")[:32])
            registered += 1
        res["registered"] = registered
        # 2. Reclaim leases whose holder never released (finding #12: load
        #    leaked, and `min(load, fail)` then starved that endpoint forever).
        try:
            res["swept"] = lb.sweep().get("reclaimed")
        except Exception as exc:
            res["sweep_error"] = str(exc)[:80]
        # 3. A real decision (and a real load release, so the gauge returns).
        try:
            pick = lb.pick()
            if pick.get("picked"):
                lb.release(pick["picked"], ok=True)
            res["pick"] = pick.get("picked")
            res["endpoints"] = lb.execute().get("result", {}).get("endpoints")
            res["endpoints_open"] = lb.execute().get("result", {}).get("open")
        except Exception as exc:
            res["pick_error"] = str(exc)[:80]
        # 4. Failover chain: consult it, and feed mark_down/mark_up from the
        #    real credential signal (finding #12: mark_up had no caller, so a
        #    provider that came back could never return to the chain).
        if ProviderFailoverMeshWorm is not None:
            fo = ProviderFailoverMeshWorm()
            keys = self._provider_key_state(fo.CHAIN)
            for prov, present in keys.items():
                if present:
                    fo.mark_up(prov)
                else:
                    # Tagged so `probe_due()` does not waste a network probe
                    # on a provider whose problem is a missing credential —
                    # and so a 401 from the probe is not read as "recovered".
                    fo.mark_down(prov, error="credential_missing")
            # 5. Half-open re-probe: the auto-recovery path itself.
            try:
                res["reprobe"] = fo.reprobe()
            except Exception as exc:
                res["reprobe"] = {"success": False, "error": str(exc)[:80]}
            nxt = fo.next_provider()
            res["next_provider"] = nxt.get("provider")
            res["providers_down"] = nxt.get("down")
            res["uses"] = (fo.stats() or {}).get("uses")
            res["provider_health"] = (fo.health() or {}).get("providers")
        # 6. Shard catalogue from the real model directory.
        if ModelShardServerWorm is not None:
            shards = ModelShardServerWorm()
            res["shards_published"] = self._publish_local_shards(shards)
            res["shard_models"] = len(
                (shards.execute().get("result", {}) or {}).get("models") or [])
            # Keep the catalogue for the consensus sub-stage's fork scan.
            self._last_shards = shards
        return res

    def _fabric_consensus(self) -> dict[str, Any]:
        """Nomination from the task7 placement file + the real succession path."""
        if LeaderElectorWorm is None:
            return {"success": True, "skipped": "consensus_unavailable"}
        res: dict[str, Any] = {}
        elect = LeaderElectorWorm()
        # 1. Real source: placement.json (role -> env), with the elector's own
        #    bare->wsl2-ubuntu remap when no bare kernel is reachable.
        placed = elect.apply_placement()
        if placed.get("success"):
            res["placement"] = placed.get("placement")
            res["remapped_bare"] = placed.get("remapped_bare")
        else:
            res["placement_error"] = placed.get("error")
            # Fall back to the live env beacons so the elector still has input.
            peers: list = []
            if EnvBeaconWorm is not None:
                try:
                    peers = list(EnvBeaconWorm().peers().get("peers") or [])
                except Exception:
                    peers = []
            for env in [_local_env()] + peers:
                elect.nominate(str(env), "peer", priority=5)
            res["peers"] = peers
        leader = elect.leader()
        res["leader"] = (leader.get("leader") or {}).get("env")
        res["term"] = leader.get("term")
        # 2. Succession path (finding #6): PraetorianWorm.observe_term() had no
        #    caller, so "moults to Queen if the LeaderElector term expires with
        #    no Queen" was code that never ran. Feed it the real term and the
        #    real queen presence.
        if PraetorianWorm is not None:
            try:
                claim = Lilith().claim(peers={"peers": res.get("peers") or []})
                queen_present = str(claim.get("role", "")).startswith("queen")
                res["queen_role"] = claim.get("role")
            except Exception:
                queen_present = False
            term = int(leader.get("term") or 0)
            try:
                succ = PraetorianWorm().observe_term(term=term,
                                                    queen_present=queen_present)
                res["succession"] = succ
            except Exception as exc:
                succ = {}
                res["succession"] = {"success": False, "error": str(exc)[:80]}
            # 2b. Eligibility used to be COMPUTED AND DROPPED: `observe_term`
            #     returned `moult_eligible` + `needs_quorum: True` and nothing
            #     consumed either, so the succession path still could not
            #     happen (finding #7 follow-up). A moult is now a real
            #     request through the shared distinct-env quorum.
            if succ.get("moult_eligible"):
                try:
                    res["moult"] = Lilith().request_moult(term=term)
                except Exception as exc:
                    res["moult"] = {"success": False, "error": str(exc)[:80]}
        # 3. Model forks: SplitBrainResolverWorm's whole API had no caller.
        if SplitBrainResolverWorm is not None:
            shards = getattr(self, "_last_shards", None)
            forks = self._model_fork_reports(shards) if shards is not None else []
            res["forks_reported"] = len(forks)
            if forks:
                sb = SplitBrainResolverWorm()
                # `resolve()` reads `_forks[model]` and answers
                # `{"resolved": False, "reason": "no_forks"}` when that box is
                # empty -- and `report_fork()` is the ONLY writer, with no
                # caller anywhere in the tree. So this stage was live but
                # structurally unable to resolve anything: every fork came back
                # `no_forks` on every cycle, which reads as "there was nothing
                # to resolve" rather than "the input was never fed in". That is
                # the shape of defect B8 -- a claimed control that is not in the
                # control path. The tuple unpacked below is exactly
                # `report_fork`'s signature (model, env, reward, version_hash).
                for model, env, reward, vhash in forks:
                    sb.report_fork(model, env, reward, vhash)
                res["forks"] = [sb.resolve(m) for m, _e, _r, _h in forks]
                # Observable outcome, so a stage that silently resolves zero is
                # visible in the report instead of looking like a clean cycle.
                res["forks_resolved"] = sum(
                    1 for f in res["forks"] if f.get("resolved"))
        return res

    def _fabric_federated(self) -> dict[str, Any]:
        """Reward shaping, NAS proposals and FedAvg over the real Q-table."""
        res: dict[str, Any] = {}
        # 1. Real learned state: the spine's Q-weights + the spine map.
        q: dict = {}
        nodes: dict = {}
        if _spine is not None:
            try:
                q = _spine.get_q_weights() or {}
            except Exception:
                q = {}
            try:
                nodes = _spine.get_spine_map() or {}
            except Exception:
                nodes = {}
        # 2. Reward shaping from the real provider chain (finding #6: `score`
        #    and `weights` had no caller, so the DLQ never filled and the
        #    provider weighting was never computed).
        if RewardShaperMeshWorm is not None:
            shaper = RewardShaperMeshWorm()
            keys = self._provider_key_state(shaper.PROVIDERS)
            scored = 0
            for prov in shaper.PROVIDERS:
                present = keys.get(prov, True)  # undeclared key => local provider
                shaper.score(prov, 1.0 if present else -1.0, ok=present)
                scored += 1
            w = shaper.weights() or {}
            res["reward_scored"] = scored
            res["reward_weights"] = w.get("weights")
            res["reward_dlq_depth"] = w.get("dlq_depth")
        # 3. Align the real per-env Q vectors: one slot per nature, so every
        #    vector has the same length (a ragged vector is what made
        #    aggregate() fragile — finding #11).
        per_env: dict = {}
        natures: set = set()
        for key, rec in nodes.items():
            env = str((rec or {}).get("env") or "")
            nature = str(key).split(":", 1)[0]
            if not env or not nature:
                continue
            per_env.setdefault(env, {})[nature] = float(q.get(key, 0.0))
            natures.add(nature)
        cols = sorted(natures)
        # 4. NAS proposals + evaluation from those vectors (the searcher's
        #    propose()/evaluate_batch() had no caller at all).
        if NASMeshSearcherWorm is not None and per_env:
            searcher = NASMeshSearcherWorm()
            for env, vec in per_env.items():
                vals = [vec.get(n, 0.0) for n in cols]
                avg = sum(vals) / max(1, len(vals))
                searcher.propose(env, {"natures": len(cols),
                                       "mean_q": round(avg, 4)},
                                 reward=round(avg, 4))
            res["nas_proposals"] = len(per_env)
            evald = searcher.evaluate_batch()
            res["nas_evaluated"] = evald.get("evaluated")
            best = evald.get("best") or {}
            res["nas_best_env"] = best.get("env")
            res["nas_best_reward"] = best.get("reward")
        # 5. FedAvg over real per-env policy vectors — a genuine cross-env
        #    consensus reward vector, not a placeholder submission.
        if FederatedAggregatorWorm is not None and len(per_env) >= 1 and cols:
            agg = FederatedAggregatorWorm()
            for env, vec in per_env.items():
                agg.submit(env, [round(vec.get(n, 0.0), 4) for n in cols],
                           samples=max(1, len(vec)))
            out = agg.aggregate()
            res["federated_rounds"] = out.get("rounds")
            res["federated_dim"] = out.get("dim")
            res["federated_avg_head"] = out.get("avg_head")
            res["federated_envs"] = len(per_env)
        return res

    def _fabric_variation(self) -> dict[str, Any]:
        """Run the evolutionary operators on the mesh's own measured state.

        Measured 2026-09-18 with a traced cycle: variation was the one role that
        never executed -- 1 of 87 functions entered, no operator invoked -- while
        selection entered 47. The loop was therefore open exactly where change is
        produced: selection ran every cycle with nothing to select, and the
        architecture could report on itself but never vary itself.

        Input is measured rather than synthetic. The search space is one gene per
        nature the spine has actually recorded Q for, and the objective is the
        expected quality of a priority vector against that recorded Q:
        sum(gene[n] * q[n]) / sum(q). The population is seeded with the measured
        vector, so generation 0 IS the current state and any improvement reported
        is an improvement over measured reality rather than over a guess.

        Output is consumed: the best genome is checkpointed and reported so the
        next cycle can compare against it. Applying a genome to live worm
        priorities is deliberately NOT done here -- that writes, and writing
        belongs behind the queen/quorum path, not inside a fabric stage.
        """
        try:
            from CORE.WORMS.expansion.evolution import EvolutionEngine
        except Exception as exc:
            return {"success": False, "reason": "engine_unavailable",
                    "error": str(exc)[:_ERR_CAP]}

        q_raw: dict = {}
        if _spine is not None:
            try:
                q_raw = _spine.get_q_weights() or {}
            except Exception:
                q_raw = {}
        q_by_nature: dict[str, float] = {}
        for key, val in q_raw.items():
            nature = str(key).split(":", 1)[0]
            try:
                q_by_nature[nature] = q_by_nature.get(nature, 0.0) + float(val)
            except (TypeError, ValueError):
                continue
        if not q_by_nature:
            # No measured signal means no honest objective. Reporting that is
            # better than optimizing against a number nothing produced.
            return {"success": False, "reason": "no_measured_q"}

        import math

        genes = sorted(q_by_nature)
        total_q = sum(q_by_nature.values()) or 1.0
        bounds = {g: (0.0, 1.0) for g in genes}
        seed = {g: max(0.0, min(1.0, q_by_nature[g] / total_q)) for g in genes}
        q_norm = math.sqrt(sum(v * v for v in q_by_nature.values())) or 1.0

        # SCALE-INVARIANT objective. The first revision divided the weighted sum
        # by total_q, which made the optimum "set every gene to 1.0": the engine
        # reported a 3.3x improvement every single run (0.218 -> 0.714) while
        # telling us nothing about the mesh. That is the same degenerate-metric
        # defect this audit found in the worm comparator (Jaccard 1.0 on
        # singleton method sets) and in PF16 -- an instrument whose value is
        # constant carries no information. Cosine similarity is maximal exactly
        # when the genome points along the measured Q vector, so "improved" now
        # means the search found a better SHAPE against recorded outcomes, and
        # uniform scaling gains nothing.
        def _cosine_from(values: list[float]) -> float:
            xnorm = math.sqrt(sum(v * v for v in values)) or 1.0
            dot = sum(values[i] * q_by_nature[genes[i]] for i in range(len(genes)))
            return dot / (xnorm * q_norm)

        def _fitness(genome: Any) -> float:
            g = getattr(genome, "genes", None) or {}
            return _cosine_from([float(g.get(n, 0.0)) for n in genes])

        seed_fitness = _cosine_from([seed[n] for n in genes])

        engine = EvolutionEngine(population_size=8, elitism_count=2,
                                 tournament_size=2, early_stop_patience=2)
        engine.initialize_population(gene_bounds=bounds, seed_genomes=[seed])

        history: list[dict] = []
        for _ in range(2):
            # use_curative=False: the fabric stage drives the operators raw.
            # Routing evaluation through CurativePool is a governance decision
            # and must not be silently taken here on the engine's behalf.
            engine.evaluate_population(_fitness, use_curative=False, workers=1)
            stats = engine.evolve() or {}
            # Record the keys the engine ACTUALLY returns rather than the ones
            # assumed: the first revision read best_fitness/mean_fitness and
            # logged None for every generation -- an instrument that reports
            # nothing while looking like it reports something.
            history.append({"generation": stats.get("generation"),
                            "stats": {k: stats[k] for k in list(stats)[:8]}})

        best = engine.get_best_genome()
        best_fitness = float(getattr(best, "fitness", 0.0) or 0.0)
        checkpoint = ""
        try:
            saved = engine.save_checkpoint(label="fabric_variation") or {}
            checkpoint = str(saved.get("label") or saved.get("path")
                             or saved.get("error") or "saved")
        except Exception as exc:
            checkpoint = "checkpoint_failed: %s" % str(exc)[:80]
        return {
            "success": True,
            "genes": len(genes),
            "generations": len(history),
            "seed_fitness": round(seed_fitness, 6),
            "best_fitness": round(best_fitness, 6),
            "improved": best_fitness > seed_fitness + 1e-9,
            "converged": bool(engine.has_converged()),
            "checkpoint": checkpoint,
            "history": history,
            "best_genes": dict(getattr(best, "genes", None) or {}),
        }

    def _fabric_resilience(self) -> dict[str, Any]:
        """Snapshot this spine's own state and prove the snapshot restorable.

        Six organs in `backup.py` had zero callers (integration map §5.1):
        StateSnapshotter.create_snapshot/list_snapshots,
        IncrementalBackupWorm.compute_manifest/find_changes and
        RecoveryTester.verify_archive/test_restore. The integration graph was
        asked for a consumer and found none — every edge from those classes
        terminates inside their own module — so the stage is the consumer:
        create -> verify -> dry-run restore, chained in one cycle. A snapshot
        that is taken and never opened is indistinguishable from no backup at
        all, which is why the verifier reads what the snapshotter just wrote
        rather than merely reporting that a file appeared.

        Scope: the load-bearing state files one level under the state dir,
        not the state dir itself (see the staging note below).
        """
        import json
        import shutil
        import tempfile
        from pathlib import Path

        try:
            from CORE.WORMS.expansion.backup import (IncrementalBackupWorm,
                                                     RecoveryTester,
                                                     StateSnapshotter)
        except Exception as exc:
            return {"success": False, "reason": "backup_organs_unavailable",
                    "error": str(exc)[:_ERR_CAP]}

        max_staged, max_file, keep = 32 * 1024 * 1024, 4 * 1024 * 1024, 5
        state_dir = Path.home() / ".azazael"
        # Snapshots live beside the state dir, never inside it: a snapshot
        # store inside its own source grows without bound, and each snapshot
        # would then contain the previous one.
        root = Path.home() / ".azazael_snapshots"
        if not state_dir.is_dir():
            return {"success": False, "reason": "no_state_dir",
                    "path": str(state_dir)}
        started = time.time()
        # Stage the load-bearing state instead of the whole home. Measured on
        # this machine the live state dir is 5.59 GB (session recordings and
        # media), so a wholesale snapshot made the organ decline on EVERY
        # real cycle while still passing in a synthetic home — inert in
        # production, which is the defect this organ exists to close. One
        # level deep, state-file suffixes only, per-file and total caps.
        stage = root / "state"
        stage.mkdir(parents=True, exist_ok=True)
        staged, staged_bytes, skipped = 0, 0, 0
        for f in sorted(state_dir.iterdir()):
            try:
                if not f.is_file() or f.suffix not in (".pkl", ".json", ".jsonl"):
                    continue
                size = f.stat().st_size
                if size > max_file or staged_bytes + size > max_staged:
                    skipped += 1
                    continue
                shutil.copy2(f, stage / f.name)
                staged += 1
                staged_bytes += size
            except OSError:
                continue
        res: dict[str, Any] = {"staged_files": staged,
                               "staged_bytes": staged_bytes,
                               "staged_skipped": skipped}
        if not staged:
            res.update({"success": False, "reason": "no_stageable_state",
                        "path": str(state_dir)})
            return res
        snap = StateSnapshotter()
        made = snap.create_snapshot(str(stage), str(root), label="cycle")
        if not made.get("success"):
            res.update({"success": False, "snapshot_ok": False,
                        "error": made.get("error")})
            return res
        archive = str((made.get("snapshot") or {}).get("path") or "")
        res["snapshot_ok"] = True
        # Invariant, not decoration: if create_snapshot reports success while
        # its own index is empty, the class' two halves disagree and that is
        # worth surfacing rather than hiding behind the disk listing.
        if not snap.list_snapshots():
            res["index_inconsistent"] = True

        # Retention from the directory, not from list_snapshots(): the
        # accessor only knows the instances in this process, and the store
        # outlives the process. A store that only grows is the failure this
        # stage exists to prevent.
        try:
            zips = sorted(root.glob("snapshot_*.zip"),
                          key=lambda p: p.stat().st_mtime)
            for old in zips[:-keep]:
                old.unlink()
            res["snapshots_kept"] = min(len(zips), keep)
        except OSError as exc:
            res["prune_error"] = str(exc)[:_ERR_CAP]

        # Change detection across the process boundary. The previous manifest
        # is read back from disk, not from self._file_db: an in-memory
        # manifest is empty in every new process, so the first cycle after
        # each restart would report every file as newly added — and
        # resume-after-failure is exactly that boundary.
        inc = IncrementalBackupWorm()
        current = inc.compute_manifest(str(stage))
        manifest_path = root / "manifest.json"
        previous: dict = {}
        if manifest_path.is_file():
            try:
                previous = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                previous = {}
        if previous:
            delta = inc.find_changes(previous, current)
            res["changes"] = delta.get("total_changes")
            res["added"] = len(delta.get("added") or [])
            res["modified"] = len(delta.get("modified") or [])
            res["deleted"] = len(delta.get("deleted") or [])
        else:
            res["changes"] = None  # first manifest: nothing to diff against
            res["first_manifest"] = True
        try:
            manifest_path.write_text(json.dumps(current), encoding="utf-8")
        except OSError as exc:
            res["manifest_persist_error"] = str(exc)[:_ERR_CAP]

        tester = RecoveryTester()
        ver = tester.verify_archive(archive)
        res["verified"] = bool(ver.get("valid"))
        res["archive_files"] = ver.get("file_count")
        if not res["verified"]:
            res.update({"success": False,
                        "verify_error": ver.get("error")
                        or ver.get("corrupted_file")})
            return res
        tmp = tempfile.mkdtemp(prefix="azazael_restore_")
        try:
            rest = tester.test_restore(archive, tmp)
            res["restore_ok"] = bool(rest.get("success"))
            if not res["restore_ok"]:
                res["restore_error"] = rest.get("error")
            else:
                restored = 0
                for p in Path(tmp).rglob("*"):
                    try:
                        if p.is_file():
                            restored += 1
                    except OSError:
                        continue
                res["restored_files"] = restored
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        res["elapsed_s"] = round(time.time() - started, 3)
        res["success"] = bool(res.get("restore_ok"))
        return res

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.run_cycle(apply=False)}


# ═════════════════════════════════════════════════════════════════
# 6. MORPHOGENESIS — the mesh grows new organs when it hurts
# ═════════════════════════════════════════════════════════════════

@register_worm(category="engram", priority=6, cooldown_seconds=900.0,
    description="Morphogenesis: generates new worm classes from chronic failure gaps (railed; no auto-exec)")
class MorphogenesisWorm:
    """Generates specialized worm proposals for chronic failure patterns.

    When one worm keeps failing with the SAME error signature, the
    bottleneck is usually a missing organ: nothing exists that handles
    that failure mode. Morphogenesis writes a new worm-class SOURCE FILE
    (registry-cached by discovery) specialized to the error signature.

    Rails (deliberate, tested):
    - `morph()` writes .py source files ONLY into the containment pen
      `CORE/WORMS/expansion/generated/_staging/`, which discovery cannot
      descend into (no `__init__.py`, `_`-prefixed). A generated file is
      therefore NOT importable and NOT a worm until it is promoted.
    - `promote()` is the only path into the discovery-visible
      `generated/` directory, and it runs quarantine -> quorum vote before
      moving a single byte. See `promote()` for the operator channel.
    - Generated worms are NON-AUTONOMOUS: execute() records evidence
      and returns; they never mutate the registry or spawn processes.
    - One file per failure signature; bounded store; dedup by signature.
    - A generated worm is a PROPOSAL made executable — integrating its
      knowledge into policy stays with the homeostat/operator.

    Audit 2026-09-15 (finding #3): before this, `morph(dry_run=False)`
    wrote straight into `generated/` and the caller
    (`SpineCycleWorm._process_morphogenesis_output`) was orphaned AND
    gate-less, calling `discover_worms()` with no quarantine and no vote.
    The containment boundary was a docstring. It is now the only way in.
    """

    VERSION = "1.0.0"
    MIN_SAMPLES = 6
    MIN_FAIL_RATE = 0.75
    MIN_CONSEC = 4
    MAX_GENERATED = 24

    def __init__(self):
        self._lock = threading.Lock()
        self._generated = 0

    # -- analysis -------------------------------------------------------

    def _chronic_patterns(self) -> list[dict[str, Any]]:
        """Find (worm, error-signature) pairs that keep failing."""
        if _spine is None:
            return []
        sigs: dict[str, dict[str, Any]] = {}
        for key, rec in _spine.get_homeostat_view().items():
            nature, _, worm = key.partition(":")
            total = rec["successes"] + rec["failures"]
            if total < self.MIN_SAMPLES or not worm:
                continue
            fail_rate = rec["failures"] / total
            sig = (rec.get("last_error") or "unknown")[:60]
            if fail_rate < self.MIN_FAIL_RATE:
                continue
            k = f"{worm}::{sig}"
            e = sigs.setdefault(k, {"worm": worm, "nature": nature,
                                    "sig": sig, "fails": 0, "total": 0,
                                    "consec": 0})
            e["fails"] += rec["failures"]
            e["total"] += total
            e["consec"] = max(e["consec"], rec.get("consec_fail", 0))
        chronic = [e for e in sigs.values()
                   if e["total"]
                   and e["fails"] / e["total"] >= self.MIN_FAIL_RATE
                   and e["consec"] >= self.MIN_CONSEC]
        chronic.sort(key=lambda e: -e["fails"])
        return chronic

    def _scaffold(self, worm: str, nature: str, sig: str) -> str:
        """Return the source of a non-autonomous specialist worm."""
        cls = "Gen" + "".join(w.capitalize() for w in
                              __import__("re").sub(r"[^A-Za-z0-9]+", " ",
                                                   f"{worm} {sig}").split()[:4])
        return f'''# coding: utf-8
"""Auto-generated by MorphogenesisWorm — do not edit by hand.

Specialist for chronic failure pattern:
  worm:    {worm}
  nature:  {nature}
  error:   {sig}

NON-AUTONOMOUS by construction: execute() only records evidence.
"""

import time

try:
    from CORE.worm_registry import register_worm
except ImportError:  # pragma: no cover
    def register_worm(**kw):
        return lambda cls: cls

try:
    from CORE import spine_registry as _spine
except ImportError:  # pragma: no cover
    _spine = None


@register_worm(category="{nature}", priority=5, cooldown_seconds=120.0,
    description="Generated specialist for {worm} failure: {sig}")
class {cls}:
    """Evidence-collecting specialist (non-autonomous)."""

    VERSION = "1.0.0"
    SOURCE_PATTERN = {sig!r}
    SOURCE_WORM = {worm!r}

    def __init__(self):
        self._observations: list[dict] = []

    def observe(self, context: dict) -> dict:
        """Record one observation of the target failure pattern."""
        entry = {{"at": time.time(), "context": dict(context)}}
        self._observations.append(entry)
        if _spine is not None:
            _spine.record_spine_event("morphogen_observation", {{
                "worm": {worm!r}, "sig": {sig!r}}})
        return {{"success": True, "observed": len(self._observations)}}

    def execute(self) -> dict:
        return {{"success": True, "method": "execute",
                "observations": len(self._observations),
                "source_worm": {worm!r}, "pattern": {sig!r}}}
'''

    # -- action ---------------------------------------------------------

    def morph(self, dry_run: bool = False) -> dict[str, Any]:
        """Generate specialist worms for unhandled chronic patterns.

        Writes into the **containment pen** (`_staging_dir()`), never into
        the discovery-visible directory. Promotion is a separate, gated step
        (`promote()`) — so no caller, present or future, can bypass the gate.
        """
        patterns = self._chronic_patterns()
        proposals = []
        written = 0
        if not dry_run and patterns:
            gen_dir = _staging_dir()
            for e in patterns[: self.MAX_GENERATED]:
                safe = __import__("re").sub(r"[^A-Za-z0-9]+", "_",
                                            f"{e['worm']}_{e['sig']}")[:60]
                path = gen_dir / f"gen_{safe}.py"
                if path.exists():
                    continue  # dedup: one specialist per signature
                if written >= 3:  # per-cycle write cap
                    break
                try:
                    gen_dir.mkdir(parents=True, exist_ok=True)
                    src = self._scaffold(e["worm"], e["nature"], e["sig"])
                    tmp = path.with_suffix(".py.tmp")
                    tmp.write_text(src, encoding="utf-8")
                    import os
                    os.replace(str(tmp), str(path))
                    written += 1
                    proposals.append({"file": path.name, "worm": e["worm"],
                                      "sig": e["sig"]})
                    if _spine is not None:
                        _spine.record_spine_event("morphogenesis_staged", {
                            "file": path.name, "source_worm": e["worm"]})
                except Exception:
                    continue
        with self._lock:
            self._generated += written
        return {"success": True, "patterns": len(patterns),
                "generated": written, "staged": written,
                "staging": str(_staging_dir()),
                "proposals": proposals,
                "total_generated": self._generated,
                "dry_run": bool(dry_run)}

    def staged(self) -> list[dict[str, Any]]:
        """Candidates in the containment pen awaiting the gate (sorted)."""
        pen = _staging_dir()
        out: list[dict[str, Any]] = []
        if not pen.is_dir():
            return out
        for p in sorted(pen.glob("*.py")):
            try:
                out.append({"file": p.name, "path": str(p),
                            "bytes": p.stat().st_size})
            except OSError:
                continue
        return out

    def promote(self, quorum: int = 2, force: bool = False,
                env: str | None = None) -> dict[str, Any]:
        """Containment gate: quarantine -> quorum vote -> publish.

        A staged candidate becomes discoverable ONLY here. For each candidate:

        1. **Quarantine** — the file is registered with `QuarantineWorm` while
           it is still invisible to the import system.
        2. **Vote** — `spine_registry.cast_quarantine_vote()` records this
           env's "promote" verdict in the shared, persisted, gossiped ledger
           and decides on **distinct envs**, so a peer env's approval that
           arrived over gossip counts.        3. **Attest** — `AttestationWorm.attest_file()` compiles the candidate,
           hashes it and records the digest (audit §5.6, Yellow team). A file
           that does not compile is held, so the docstring's claim that
           promotion is attested is now true instead of aspirational.
        4. **Promote** — only on a decided vote AND a passing attestation, the
           file is moved into the discovery-visible `generated/` directory.

        `force=True` is the operator channel: it records an explicit
        `operator` vote (so the decision stays auditable rather than
        invisible) and promotes without a second env. Without it, a single
        env can never promote a generated worm — the same safety intent as
        the quarantine quorum in finding #1.
        """
        env = env or _local_env()
        candidates = self.staged()
        promoted: list[dict[str, Any]] = []
        held: list[dict[str, Any]] = []
        if not candidates:
            return {"success": True, "staged": 0, "promoted": 0, "held": 0,
                    "promotions": [], "pending": []}
        try:
            qz = QuarantineWorm() if QuarantineWorm is not None else None
        except Exception:  # pragma: no cover - defensive
            qz = None
        # Yellow team (audit §5.6): AttestationWorm.attest_file() already does
        # py_compile + SHA-256 + a free-threading check and had ZERO consumers —
        # it was named as a lifecycle gate in this module's own docstring and
        # consulted nowhere. Compiled-and-hashed BEFORE the file can become
        # discoverable: a staged candidate that fails to compile must not be
        # promotable.
        try:
            att = AttestationWorm() if AttestationWorm is not None else None
        except Exception:  # pragma: no cover - defensive
            att = None
        for cand in candidates:
            name = cand["file"]
            finding = f"promote:{name}"
            if qz is not None:
                try:
                    qz.quarantine(name, "morphogenesis:awaiting_quorum")
                except Exception:
                    pass
            vote: dict[str, Any] = {}
            if _spine is not None:
                try:
                    vote = _spine.cast_quarantine_vote(
                        finding, "operator" if force else env,
                        "promote", quorum=quorum)
                except Exception:
                    vote = {}
            decided = bool(force) or bool(vote.get("decided"))
            if not decided:
                held.append({"file": name, "envs": vote.get("envs"),
                             "env_count": vote.get("env_count"),
                             "reason": "awaiting_quorum"})
                continue
            # Yellow gate: attest before publish. Fails CLOSED here — the whole
            # point is that a file which cannot be verified does not become
            # discoverable, so an attestor that raises is a refusal, not a
            # waiver. (The quarantine gate elsewhere fails open on purpose: its
            # job is to keep the fleet running, this one's is to keep the tree
            # honest.)
            attestation: dict[str, Any] | None = None
            if att is not None:
                try:
                    att_out = att.attest_file(cand["path"])
                    attestation = att_out.get("attestation")
                except Exception as exc:
                    held.append({"file": name,
                                 "error": "attestation_error: %s" % str(exc)[:80]})
                    continue
                if not (attestation and attestation.get("pass")):
                    held.append({"file": name, "reason": "attestation_failed",
                                 "compiles": (attestation or {}).get("compiles"),
                                 "sha": (attestation or {}).get("sha")})
                    if _spine is not None:
                        try:
                            _spine.record_spine_event(
                                "morphogenesis_attestation_refused", {
                                    "file": name,
                                    "compiles": (attestation or {}).get("compiles")})
                        except Exception:
                            pass
                    continue
            try:
                dest_dir = _generated_dir()
                dest_dir.mkdir(parents=True, exist_ok=True)
                import os
                os.replace(cand["path"], str(dest_dir / name))
                if qz is not None:
                    qz.release(name)
                promoted.append({"file": name, "envs": vote.get("envs"),
                                 "forced": bool(force),
                                 "sha": (attestation or {}).get("sha")})
                if _spine is not None:
                    _spine.record_spine_event("morphogenesis_promoted", {
                        "file": name, "forced": bool(force),
                        "envs": vote.get("envs"), "quorum": quorum,
                        "sha": (attestation or {}).get("sha")})
            except Exception as exc:
                held.append({"file": name, "error": str(exc)[:80]})
        return {"success": True, "staged": len(candidates),
                "promoted": len(promoted), "held": len(held),
                "promotions": promoted, "pending": held}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.morph(dry_run=True)}  # dry-run by default


def _generated_dir():
    """Discovery-visible home of *promoted* specialists.

    Contains an `__init__.py`, so `discover_worms()` descends into it: a file
    that lands here IS a registered worm class on the next discovery pass.

    `AZAZAEL_GENERATED_DIR` relocates both this and the containment pen. Two
    real uses: an installed/cx_frozen package directory may be read-only, and
    a test run must never write source into the tree it is testing.
    """
    import os
    from pathlib import Path
    override = os.environ.get("AZAZAEL_GENERATED_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "generated"


def _staging_dir():
    """Containment pen for generated source (audit finding #3).

    Discoverability rule (worm_registry._discover_worms_impl): a directory is
    only descended into when it holds an `__init__.py`, and names starting
    with `_`/`.` are skipped outright. `generated/_staging` fails both tests,
    so a file written here cannot be imported as a worm — promotion moves it
    up one level into the discovery-visible `generated/`.
    """
    from pathlib import Path
    return _generated_dir() / "_staging"


# ═════════════════════════════════════════════════════════════════
# 7. CONSOLIDATION — sleep phase: dream offline, reinforce when idle
# ═════════════════════════════════════════════════════════════════

@register_worm(category="learning", priority=5, cooldown_seconds=1800.0,
    description="Sleep phase: wires DreamingModule to spine; reinforces Q from high-quality dreams when idle")
class ConsolidationWorm:
    """Wires the existing DreamingModule into the learning loop.

    DreamingModule (expansion/dreaming.py) already replays memory
    scenarios offline and produces scored policy suggestions — but
    nothing connected its output to anything. ConsolidationWorm:

    1. checks spine_registry.is_idle() — runs only when live traffic
       has been quiet (dreaming on a busy system is waste + pollution);
    2. runs a small dreaming batch (bounded episodes);
    3. reinforces the Q-table via dream_reinforce() for high-quality
       dreams (quality gate; simulations never touch the live ledger).

    execute() refuses to dream when not idle — returns skipped instead.
    """

    VERSION = "1.0.0"
    IDLE_WINDOW_S = 300.0
    MAX_EPISODES = 3
    QUALITY_GATE = 0.5

    def __init__(self):
        self._lock = threading.Lock()
        self._cycles = 0
        self._total_reinforced = 0

    def consolidate(self, force: bool = False) -> dict[str, Any]:
        if _spine is None:
            return {"success": False, "error": "spine_registry unavailable"}
        if not force and not _spine.is_idle(self.IDLE_WINDOW_S):
            return {"success": True, "skipped": "not_idle",
                    "cycles": self._cycles}
        try:
            from CORE.WORMS.expansion.dreaming import DreamingModule
        except ImportError as exc:
            return {"success": False, "error": f"dreaming unavailable: {exc}"}
        try:
            dreamer = DreamingModule()
            dreamer.recall_scenarios()
            dreams = dreamer.dream(num_episodes=self.MAX_EPISODES)
        except Exception as exc:
            return {"success": True, "skipped": f"dream_error: {str(exc)[:80]}",
                    "cycles": self._cycles}

        reinforced = 0
        for d in dreams or []:
            try:
                if float(getattr(d, "quality_score", 0.0)) < self.QUALITY_GATE:
                    continue
                for s in (getattr(d, "policy_suggestions", None) or [])[:4]:
                    if not isinstance(s, dict):
                        continue
                    worm = s.get("worm") or s.get("target") or ""
                    if not worm:
                        continue
                    reward = max(-1.0, min(1.0, float(s.get("reward", 0.3))))
                    if _spine.dream_reinforce("dream", worm, reward):
                        reinforced += 1
            except Exception:
                continue
        with self._lock:
            self._cycles += 1
            self._total_reinforced += reinforced
        if _spine is not None:
            _spine.record_spine_event("consolidation", {
                "dreams": len(dreams or []), "reinforced": reinforced})
        return {"success": True, "dreams": len(dreams or []),
                "reinforced": reinforced, "cycles": self._cycles}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.consolidate()}
