# coding: utf-8
"""
NEURAL MESH — Category: CONSENSUS (3 worms)
Agreement across all envs (light on Standalone).

QuorumVoterWorm, LeaderElectorWorm, SplitBrainResolverWorm
"""

import time
import threading
import hashlib
from datetime import datetime
from typing import Any
from collections import Counter

try:
    from CORE.worm_registry import register_worm
except ImportError:
    def register_worm(**kw):
        return lambda cls: cls


@register_worm(category="consensus", priority=9, cooldown_seconds=30.0,
    description="Majority vote on VulnScanner/RaceDetector findings across envs")
class QuorumVoterWorm:
    """Cross-env majority voter."""

    VERSION = "1.0.0"

    def __init__(self, quorum: int = 2):
        self._quorum = quorum
        self._votes: dict[str, list] = {}
        self._lock = threading.Lock()

    def vote(self, finding_id: str, env: str, verdict: str) -> dict[str, Any]:
        with self._lock:
            box = self._votes.setdefault(finding_id, [])
            box.append({"env": env, "verdict": verdict,
                        "at": datetime.now().isoformat()})
            counts = Counter(v["verdict"] for v in box)
            top, n = counts.most_common(1)[0]
            decided = n >= self._quorum
            return {"success": True, "finding": finding_id, "votes": len(box),
                    "top": top, "count": n, "decided": decided,
                    "quorum": self._quorum}

    def tally(self, finding_id: str) -> dict:
        with self._lock:
            box = self._votes.get(finding_id, [])
            counts = dict(Counter(v["verdict"] for v in box))
            return {"finding": finding_id, "votes": len(box), "tally": counts}

    def execute(self) -> dict[str, Any]:
        with self._lock:
            return {"success": True, "method": "execute",
                    "result": {"open_findings": len(self._votes),
                               "quorum": self._quorum}}


@register_worm(category="consensus", priority=8, cooldown_seconds=30.0,
    description="Bully/Raft-lite: elects trainer (Bare) vs server (Win) vs scanner (Kali)")
class LeaderElectorWorm:
    """Lightweight leader election."""

    VERSION = "1.0.0"
    ROLES = ("trainer", "server", "scanner", "archiver")

    def __init__(self):
        self._nodes: dict[str, dict] = {}
        self._leader: dict | None = None
        self._term = 0
        self._lock = threading.Lock()

    def nominate(self, env: str, role: str, priority: int = 5) -> dict[str, Any]:
        with self._lock:
            self._nodes[env] = {"role": role, "priority": priority,
                                "at": datetime.now().isoformat()}
            best = max(self._nodes.items(), key=lambda kv: kv[1]["priority"])
            if self._leader is None or best[0] != self._leader.get("env"):
                self._term += 1
            self._leader = {"env": best[0], **best[1], "term": self._term}
            return {"success": True, "leader": self._leader,
                    "nodes": len(self._nodes)}

    def leader(self) -> dict:
        with self._lock:
            return {"leader": self._leader, "term": self._term,
                    "nodes": list(self._nodes.keys())}

    def apply_placement(self, path: str = "G:/source-of-truth/azazael_models/placement.json") -> dict[str, Any]:
        """Seed nominations from task7 placement.json; remaps bare->wsl2-ubuntu
        when BarePassthroughWorm reports no bare kernel (3-env mesh)."""
        import json as _json
        import os as _os
        try:
            assign = _json.load(open(path, encoding="utf-8"))
        except Exception as exc:
            return {"success": False, "error": f"placement unreadable: {str(exc)[:100]}"}
        remapped = {}
        try:
            from CORE.WORMS.expansion.envmesh import BarePassthroughWorm
            bare_ok = BarePassthroughWorm().probe().get("via", "").startswith("ssh:") or \
                BarePassthroughWorm().probe_local().get("is_bare_kernel", False)
        except Exception:
            bare_ok = _os.environ.get("AZAZAEL_BARE_SSH", "") != ""
        for role, env in assign.items():
            if env == "bare" and not bare_ok:
                remapped[role] = "wsl2-ubuntu"
            else:
                remapped[role] = env
        out = []
        for role, env in remapped.items():
            out.append(self.nominate(env, role, priority=8))
        return {"success": True, "placement": remapped,
                "remapped_bare": [r for r in assign if assign[r] == "bare" and remapped[r] != "bare"],
                "leader": self._leader}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.leader()}


@register_worm(category="consensus", priority=7, cooldown_seconds=120.0,
    description="Resolves ModelVersioner forks after partition (keeps highest reward + hash)")
class SplitBrainResolverWorm:
    """Fork resolver: highest reward wins, hash breaks ties."""

    VERSION = "1.0.0"

    def __init__(self):
        self._forks: dict[str, list] = {}
        self._lock = threading.Lock()

    def report_fork(self, model: str, env: str, reward: float, version_hash: str) -> dict[str, Any]:
        with self._lock:
            box = self._forks.setdefault(model, [])
            box.append({"env": env, "reward": reward, "hash": version_hash,
                        "at": datetime.now().isoformat()})
            return {"success": True, "model": model, "branches": len(box)}

    def resolve(self, model: str) -> dict[str, Any]:
        with self._lock:
            box = self._forks.get(model, [])
            if not box:
                return {"success": True, "model": model, "resolved": False,
                        "reason": "no_forks"}
            winner = sorted(box, key=lambda b: (-b["reward"], b["hash"]))[0]
            self._forks[model] = [winner]
            return {"success": True, "model": model, "resolved": True,
                    "winner": winner, "dropped": len(box) - 1}

    def execute(self) -> dict[str, Any]:
        with self._lock:
            return {"success": True, "method": "execute",
                    "result": {"tracked_models": len(self._forks)}}
