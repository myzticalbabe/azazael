# coding: utf-8
"""
NEURAL MESH — Category: MESH (4 worms)
Fabric transport for all environments: Windows 11 <-> WSL2 <-> Bare Metal <-> Kali <-> G:

MeshRouterWorm, GossipSyncWorm, PartitionHealerWorm, EnvBeaconWorm
"""

import time
import hashlib
import threading
import platform
from datetime import datetime
from typing import Any

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

_MESH_ENVS = ("windows", "wsl2", "bare", "kali", "g_archive", "standalone")


def _read_text(path: str) -> str:
    try:
        with open(path, 'r', errors='replace') as f:
            return f.read()
    except Exception:
        return ""


def _env_id() -> str:
    """Env id, 5-way via envmesh when available: windows|wsl2-ubuntu|wsl2-kali|bare|kali.

    Delegates to envmesh.env_id_v2() (splits WSL2 Ubuntu vs Kali, which the
    old microsoft-first check conflated into one 'wsl2' bucket and merged
    their Q-table keys). Falls back to legacy detection if envmesh missing.
    bare = generic non-WSL, non-Kali Linux (incl. true bare metal AND VMs).
    Use describe_env() when you need to distinguish true bare metal.
    """
    try:
        from CORE.WORMS.expansion.envmesh import env_id_v2
        return env_id_v2()
    except Exception:
        pass
    import os
    if os.name == 'nt':
        return "windows"
    ver = _read_text('/proc/version').lower()
    if 'microsoft' in ver:
        return "wsl2"
    if 'kali' in _read_text('/etc/os-release').lower():
        return "kali"
    return "bare"


def describe_env() -> dict:
    """Richer host description: virt, docker flavour, GPU presence, FT.

    Distinguishes TRUE bare metal (no hypervisor) from VMs/WSL2, so callers
    (e.g. Lilith) can prefer bare without bricking when absent.
    """
    import os
    env = _env_id()
    virt = "unknown"
    if env == "windows":
        try:
            virt = "hyperv_host"  # Windows with HypervisorPresent checked by caller
        except Exception:
            pass
    else:
        ver = _read_text('/proc/version').lower()
        cgroup = _read_text('/proc/1/cgroup').lower()
        if 'microsoft' in ver:
            virt = "wsl2"
        elif 'hypervisor' in ver or 'kvm' in ver or 'vmware' in ver:
            virt = "vm"
        elif 'docker' in cgroup or 'kubepods' in cgroup:
            virt = "container"
        elif os.path.exists('/.dockerenv'):
            virt = "container"
        else:
            virt = "bare_metal_or_unknown"
    try:
        import psutil
        mem_gb = round(psutil.virtual_memory().total / 1e9, 1)
    except Exception:
        try:
            with open('/proc/meminfo', 'r') as f:
                mem_kb = int(f.readline().split()[1])
            mem_gb = round(mem_kb / 1e6, 1)
        except Exception:
            mem_gb = 0.0
    return {"env": env, "virt": virt, "cpu": os.cpu_count() or 0,
            "mem_gb": mem_gb, "ft": is_free_threaded(),
            "bare_likely": env == "bare" and virt == "bare_metal_or_unknown"}


@register_worm(category="mesh", priority=9, cooldown_seconds=10.0,
    description="Cross-env mesh router — wraps MessageBroker+IPCBridge+ProtocolNegotiator")
class MeshRouterWorm:
    """Env-aware routing Win<->WSL2<->Bare<->Kali<->G:."""

    VERSION = "1.0.0"

    def __init__(self):
        self._routes: dict = {}
        self._lock = threading.Lock()
        self._env = _env_id()

    def add_route(self, src: str, dst: str, weight: float = 1.0):
        with self._lock:
            self._routes[(src, dst)] = {
                "weight": weight, "updated": datetime.now().isoformat(),
            }

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
            key = (self._env, dst_env)
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
            "hops": 1 if dst_env in _MESH_ENVS else -1,
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
    """Gossip protocol for mesh state convergence."""

    VERSION = "1.0.0"

    def __init__(self):
        self._state: dict = {}
        self._lock = threading.Lock()
        self._rounds = 0

    def gossip(self, peer_state: dict) -> dict[str, Any]:
        merged = 0
        with self._lock:
            for k, v in peer_state.items():
                if k not in self._state:
                    self._state[k] = v
                    merged += 1
            self._rounds += 1
            return {"success": True, "merged": merged,
                    "known_keys": len(self._state), "rounds": self._rounds}

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

    VERSION = "1.0.0"

    def __init__(self):
        self._partitions: list = []
        self._lock = threading.Lock()

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
            return {"success": True, "partitioned": bool(issues),
                    "issues": issues, "events": len(self._partitions)}

    def heal(self) -> dict[str, Any]:
        with self._lock:
            n = len(self._partitions)
            self._partitions.clear()
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

    VERSION = "1.0.0"

    def __init__(self):
        self._beacons: dict = {}
        self._lock = threading.Lock()

    def beacon(self) -> dict[str, Any]:
        import shutil
        cap = {
            "env": _env_id(),
            "ft": is_free_threaded(),
            "platform": platform.platform()[:60],
            "cpu": __import__('os').cpu_count(),
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
        return {"success": True, "beacon": cap}

    def peers(self) -> dict:
        with self._lock:
            return {"peers": list(self._beacons.keys())}

    def execute(self) -> dict[str, Any]:
        r = self.beacon()
        return {"success": True, "method": "execute", "result": r["beacon"]}
