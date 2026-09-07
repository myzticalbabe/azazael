# coding: utf-8
"""DNSWORM — Autonomous DNS reconnaissance worm.

Resolves a safe default target set (local host + public infrastructure names)
using only the standard library. No external binaries, no writes, no side
effects beyond ordinary resolver traffic.

Autonomy contract (see CLUSTERWORMS._STANDARD_METHODS):
- registered via @register_worm -> auto-discovered into WORM_REGISTRY
- no-arg constructor (targets configurable via attribute, not __init__ args)
- NO get_summary/get_status (the cluster calls the first working
  parameterless method — a trivial get_summary would shadow the real work,
  cf. BenchmarkWorm) — scan() is the entry point the cluster will invoke
- scan() is parameterless, bounded (per-query timeout), and returns a dict
"""

import socket

try:
    from CORE.worm_registry import register_worm
except ImportError:
    def register_worm(**kw):
        return lambda cls: cls


@register_worm(category="network", priority=5, cooldown_seconds=300.0, description="Autonomous DNS recon — resolves safe default targets (localhost + public infra) with stdlib only")
class DnsWorm:
    # Safe defaults: this host + public infrastructure. No third-party targets.
    DEFAULT_TARGETS = ["localhost", "example.com", "dns.google"]

    def __init__(self):
        self.targets = list(self.DEFAULT_TARGETS)
        self.timeout_seconds = 8

    def scan(self):
        """Resolve every target. Parameterless so cluster machinery invokes it."""
        results = {}
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self.timeout_seconds)
        try:
            for target in self.targets:
                results[target] = self._resolve_one(target)
        finally:
            socket.setdefaulttimeout(old_timeout)
        ok = sum(1 for r in results.values() if r.get("ok"))
        return {"success": ok > 0, "resolved": ok, "total": len(results),
                "results": results}

    def _resolve_one(self, target):
        try:
            infos = socket.getaddrinfo(target, None)
        except Exception as e:
            return {"ok": False, "error": str(e)[:120]}
        addrs = sorted({i[4][0] for i in infos})
        try:
            reverse = socket.gethostbyaddr(addrs[0])[0]
        except Exception:
            reverse = ""
        return {"ok": True, "addresses": addrs, "reverse": reverse}


if __name__ == "__main__":
    import json
    print(json.dumps(DnsWorm().scan(), indent=2)[:1500])
