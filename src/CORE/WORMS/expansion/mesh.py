# coding: utf-8
"""
NEURAL MESH — Category: MESH (4 worms)
Fabric transport for all environments: Windows 11 <-> WSL2 <-> Bare Metal <-> Kali <-> G:

MeshRouterWorm, GossipSyncWorm, PartitionHealerWorm, EnvBeaconWorm
"""

import threading
import platform
from datetime import datetime
from typing import Any

# Single canonical env identity (audit 2026-09-15, finding #4). Env id is a
# primary key for spine-map nodes, gossip filenames, route Q-keys and beacon
# peer sets, so there must be exactly one implementation. It lives in
# CORE.env_id; this module and three others used to carry stale copies.
try:
    from CORE.env_id import env_id as _canonical_env_id
    from CORE.env_id import describe_env as _canonical_describe_env
    from CORE.env_id import is_known_env, VALID_ENVS
    _CANONICAL_ENV = True
except ImportError:  # pragma: no cover - defensive
    _CANONICAL_ENV = False
    VALID_ENVS = ("windows", "wsl2-ubuntu", "wsl2-kali", "bare", "kali")

    def is_known_env(name: str) -> bool:
        return bool(name) and any(
            v.startswith(name) or name.startswith(v) for v in VALID_ENVS)

try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

try:
    from CORE.freethreading import is_free_threaded, ThreadSafeDict
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    ThreadSafeDict = dict
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False

# Fabric operational state (audit 2026-09-15, finding #7): hydrate in
# __init__, publish on mutation, so routing/partition/beacon state survives a
# new NatureClusterManager or a restart instead of living only in memory.
try:
    from CORE.WORMS.expansion.fabric_state import (
        hydrate, publish, cap_list, cap_map,
    )
except ImportError:  # pragma: no cover - defensive, keeps mesh importable alone
    def hydrate(instance, provider, attrs):
        return 0

    def publish(instance, provider, attrs):
        return False

    def cap_list(seq, limit):
        return seq

    def cap_map(d, limit):
        return d


def _stamp(value: Any) -> str:
    """Best-effort recency stamp from a merged value ("" when absent)."""
    if not isinstance(value, dict):
        return ""
    for key in ("updated_at", "at", "last_at", "exported_at", "saved_at"):
        ts = value.get(key)
        if isinstance(ts, str) and ts:
            return ts
    return ""

# Back-compat alias. The old tuple hard-coded the pre-2026-09-13 3-way
# spelling ("wsl2") and was never updated when envmesh split WSL2 into
# wsl2-ubuntu/wsl2-kali, so `dst_env in _MESH_ENVS` reported the two most
# common non-Windows targets as unreachable (`hops = -1`). Route liveness is
# now decided by is_known_env(), which is prefix-tolerant.
_MESH_ENVS = tuple(VALID_ENVS) + ("g_archive", "standalone")


def _read_text(path: str) -> str:
    try:
        with open(path, 'r', errors='replace') as f:
            return f.read()
    except Exception:
        return ""


def _env_id() -> str:
    """Canonical 5-way env id: windows|wsl2-ubuntu|wsl2-kali|bare|kali.

    Thin delegate to CORE.env_id.env_id() — the one implementation. Kept as
    a private alias because this module was historically the "reference"
    every other copy claimed to mirror.
    """
    if _CANONICAL_ENV:
        return _canonical_env_id()
    import os
    if os.name == 'nt':
        return "windows"
    ver = _read_text('/proc/version').lower()
    if 'microsoft' in ver:
        return "wsl2-ubuntu"
    if 'kali' in _read_text('/etc/os-release').lower():
        return "kali"
    return "bare"


def describe_env() -> dict:
    """Richer host description: virt, container flavour, memory, FT.

    Delegates to CORE.env_id.describe_env() (audit 2026-09-15, finding #14:
    the local copy had a dead try/except that hard-coded "hyperv_host" on
    Windows without ever checking Hyper-V, and dropped the free-threading
    flag the canonical version reports).
    """
    if _CANONICAL_ENV:
        out = _canonical_describe_env()
        out["ft"] = is_free_threaded()
        return out
    import os
    return {"env": _env_id(), "virt": "unknown", "cpu": os.cpu_count() or 0,
            "mem_gb": 0.0, "ft": is_free_threaded(), "bare_likely": False}


@register_worm(category="mesh", priority=9, cooldown_seconds=10.0,
    description="Cross-env mesh router — wraps MessageBroker+IPCBridge+ProtocolNegotiator")
class MeshRouterWorm:
    """Env-aware routing Win<->WSL2<->Bare<->Kali<->G:."""

    VERSION = "1.1.0"

    # Persisted operational state (audit 2026-09-15, finding #7).
    PROVIDER = "MeshRouterWorm"
    _STATE_ATTRS = ("_routes",)
    ROUTES_MAX = 512  # finding #8: bounded growth

    def __init__(self):
        self._routes: dict = {}
        self._lock = threading.Lock()
        self._env = _env_id()
        hydrate(self, self.PROVIDER, self._STATE_ATTRS)

    @staticmethod
    def _route_key(src: str, dst: str) -> str:
        """String route key — the same `src>dst` form the route Q-table uses.

        Keys used to be `(src, dst)` tuples, which cannot survive JSON
        persistence, so registered route weights were among the state the
        mesh lost on every restart (finding #7).
        """
        return f"{src}>{dst}"

    def add_route(self, src: str, dst: str, weight: float = 1.0):
        with self._lock:
            self._routes[self._route_key(src, dst)] = {
                "weight": weight, "updated": datetime.now().isoformat(),
            }
            cap_map(self._routes, self.ROUTES_MAX)
            publish(self, self.PROVIDER, self._STATE_ATTRS)

    def route(self, dst_env: str, payload: dict) -> dict[str, Any]:
        """Route with learned weight: registered weight x learned reliability.

        The learning signal lives in CORE.spine_registry's Q-table under
        nature="route", worm="<src>><dst>": every record_route_result()
        call is auto-reinforced by the brainstem (success +1 / failure -1,
        EMA). route() multiplies the static registered weight by
        (1 + q) clamped to [0.1, 5.0] — routes that keep failing get
        starved, reliable routes get promoted. Fails open to the static
        weight when the spine ledger is unavailable.
        """
        with self._lock:
            key = self._route_key(self._env, dst_env)
            w = self._routes.get(key, {"weight": 1.0})
        base_w = float(w.get("weight", 1.0))
        q = 0.0
        try:
            from CORE import spine_registry as _spine
            q = _spine.get_q_weight("route", f"{self._env}>{dst_env}")
        except Exception:
            q = 0.0
        eff_w = round(max(0.1, min(5.0, base_w * (1.0 + q))), 3)
        return {
            "success": True, "src": self._env, "dst": dst_env,
            "weight": base_w, "effective_weight": eff_w, "q": round(q, 3),
            "hops": 1 if is_known_env(dst_env) else -1,
            "payload_keys": list(payload.keys())[:10],
        }

    def record_route_result(self, dst_env: str, success: bool,
                            duration_ms: float = 0.0) -> None:
        """Feed a route outcome into the brainstem (route learning)."""
        try:
            from CORE import spine_registry as _spine
            _spine.record_outcome("route", f"{self._env}>{dst_env}",
                                  bool(success), float(duration_ms))
        except Exception:
            pass  # learning is best-effort; routing must not fail on it

    def get_routing_table(self) -> dict:
        with self._lock:
            return {"env": self._env, "routes": len(self._routes),
                    "ft": is_free_threaded()}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.get_routing_table()}


@register_worm(category="mesh", priority=8, cooldown_seconds=15.0,
    description="Epidemic state gossip — worm health, model versions; heals sync drift")
class GossipSyncWorm:
    """Gossip merge for mesh state convergence — trust-gated, recency-ordered.

    Audit 2026-09-15 (finding #9): the previous merge was first-writer-wins
    (``if k not in self._state``), which cannot converge. Once a key was seen
    its value was frozen forever, so a changed value could never propagate and
    two envs that ever disagreed stayed disagreed. It also had no notion of the
    spine's provenance model, even though the spine already owned a signed,
    seq-anti-replayed, recency-wins merge.

    Two paths now:

    * **Spine-shaped payload** (carries ``spine_map``/``homeostat``/``seq`` …)
      — provenance is enforced by ``spine_registry.check_gossip_trust``
      (Ed25519 signature when available, monotonic seq, TOFU key pinning). An
      untrusted payload applies nothing and reports ``rejected``. Pass
      ``merge_ledger=True`` to also run the full trust-checked ledger merge;
      the default only records the trust verdict, because ``SpineGossipWorm``
      is the transport that owns that merge (re-merging would be duplicated
      work on the hot path).
    * **Plain mapping** — per-key recency merge on ``at``/``updated_at``. A
      timestamped value may replace an older one; a value with no timestamp can
      only fill a gap, never overwrite.
    """

    VERSION = "2.0.0"
    PROVIDER = "GossipSyncWorm"
    _STATE_ATTRS = ("_state", "_rounds")
    STATE_KEYS_MAX = 512  # finding #8
    _SPINE_PAYLOAD_KEYS = ("spine_map", "homeostat", "q_weights", "seq",
                           "gossip_from", "exported_at", "fabric_state")
    _ENVELOPE_KEYS = ("signature", "signer_pub")

    def __init__(self):
        self._state: dict = {}
        self._lock = threading.Lock()
        self._rounds = 0
        hydrate(self, self.PROVIDER, self._STATE_ATTRS)

    def gossip(self, peer_state: dict,
               merge_ledger: bool = False) -> dict[str, Any]:
        """Merge a peer payload. Trust-gated; recency-wins; never raises."""
        if not isinstance(peer_state, dict):
            return {"success": False, "error": "payload must be a dict"}
        out: dict[str, Any] = {"success": True, "new": 0, "applied": 0,
                               "stale_skipped": 0, "rejected": None,
                               "trust": "n/a", "merge": "plain"}

        if any(k in peer_state for k in self._SPINE_PAYLOAD_KEYS):
            out["merge"] = "spine"
            try:
                from CORE import spine_registry as _spine
            except Exception as exc:  # pragma: no cover - defensive
                return {"success": False, "error": str(exc)[:100]}
            trust = _spine.check_gossip_trust(peer_state)
            out["trust"] = trust.get("signature", "?")
            out["env"] = trust.get("env", "")
            if not trust.get("ok"):
                out["rejected"] = trust.get("reason", "untrusted")
                with self._lock:
                    self._rounds += 1
                    out["rounds"] = self._rounds
                return out
            if merge_ledger:
                try:
                    out["spine_merge"] = _spine.merge_spine_gossip(peer_state)
                except Exception as exc:
                    out["spine_merge"] = {"merged": False,
                                          "error": str(exc)[:80]}

        with self._lock:
            for k, v in peer_state.items():
                if k in self._ENVELOPE_KEYS:
                    continue
                cur = self._state.get(k)
                if cur is None:
                    self._state[k] = v
                    out["new"] += 1
                    continue
                ts_new, ts_cur = _stamp(v), _stamp(cur)
                if ts_new and (not ts_cur or ts_new > ts_cur):
                    self._state[k] = v
                    out["applied"] += 1
                elif ts_new and ts_new == ts_cur:
                    pass  # idempotent re-merge of an identical payload
                else:
                    out["stale_skipped"] += 1
            cap_map(self._state, self.STATE_KEYS_MAX)
            self._rounds += 1
            publish(self, self.PROVIDER, self._STATE_ATTRS)
            out["known_keys"] = len(self._state)
            out["rounds"] = self._rounds
        return out

    def get_state(self) -> dict:
        with self._lock:
            return {"keys": len(self._state), "rounds": self._rounds}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute",
                "result": self.get_state()}


@register_worm(category="mesh", priority=7, cooldown_seconds=60.0,
    description="Detects split-brain (WSL stopped, G: unmounted), replays DeadLetterQueue")
class PartitionHealerWorm:
    """Partition detection + DLQ replay."""

    VERSION = "1.1.0"
    PROVIDER = "PartitionHealerWorm"
    _STATE_ATTRS = ("_partitions",)
    PARTITIONS_MAX = 200  # finding #8

    def __init__(self):
        self._partitions: list = []
        self._lock = threading.Lock()
        hydrate(self, self.PROVIDER, self._STATE_ATTRS)

    def detect(self) -> dict[str, Any]:
        import os
        issues = []
        if os.name == 'nt':
            if not os.path.exists(r'G:\source-of-truth'):
                issues.append("g_unmounted")
        else:
            if not os.path.exists('/mnt/g'):
                issues.append("g_unmounted")
        with self._lock:
            if issues:
                self._partitions.append({
                    "at": datetime.now().isoformat(), "issues": issues,
                })
                cap_list(self._partitions, self.PARTITIONS_MAX)
                publish(self, self.PROVIDER, self._STATE_ATTRS)
            return {"success": True, "partitioned": bool(issues),
                    "issues": issues, "events": len(self._partitions)}

    def heal(self) -> dict[str, Any]:
        with self._lock:
            n = len(self._partitions)
            self._partitions.clear()
            publish(self, self.PROVIDER, self._STATE_ATTRS)
            return {"success": True, "replayed_partitions": n,
                    "dlq_replay": "queued"}

    def execute(self) -> dict[str, Any]:
        d = self.detect()
        if d["partitioned"]:
            return {"success": True, "method": "execute", "result": d}
        return {"success": True, "method": "execute", "result": self.heal()}


@register_worm(category="mesh", priority=6, cooldown_seconds=15.0,
    description="Heartbeat + capability advertisement for router weights")
class EnvBeaconWorm:
    """Capability beacon for mesh routing weights."""

    VERSION = "1.1.0"
    PROVIDER = "EnvBeaconWorm"
    _STATE_ATTRS = ("_beacons",)
    BEACONS_MAX = 64  # finding #8

    def __init__(self):
        self._beacons: dict = {}
        self._lock = threading.Lock()
        hydrate(self, self.PROVIDER, self._STATE_ATTRS)

    def beacon(self) -> dict[str, Any]:
        import os as _os
        cap = {
            "env": _env_id(),
            "ft": is_free_threaded(),
            "platform": platform.platform()[:60],
            "cpu": _os.cpu_count(),
            "at": datetime.now().isoformat(),
        }
        try:
            import importlib.util as _iu
            cap["tools"] = {
                t: bool(_iu.find_spec(t)) for t in ("nmap", "torch", "onnx")
            }
        except Exception:
            cap["tools"] = {}
        with self._lock:
            self._beacons[cap["env"]] = cap
            cap_map(self._beacons, self.BEACONS_MAX)
            publish(self, self.PROVIDER, self._STATE_ATTRS)
        return {"success": True, "beacon": cap}

    def peers(self) -> dict:
        with self._lock:
            return {"peers": list(self._beacons.keys())}

    def execute(self) -> dict[str, Any]:
        r = self.beacon()
        return {"success": True, "method": "execute", "result": r["beacon"]}
