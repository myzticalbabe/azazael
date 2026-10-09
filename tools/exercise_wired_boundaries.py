#!/usr/bin/env python3
"""Exercise: the production boundaries actually REACH the technique runtime.

Why this exists
---------------
A grep proves a call site exists; it does not prove the call is ever made. This
repo's recorded failure mode is precisely that gap: `verification_gate.py` had
nine composed detectors and one caller, `reflexion.py` was a complete buffer with
no caller, and a first attempt at this very wiring produced 181 adapters that
only an exercise invoked -- the defect moved up one level instead of dying.

So each check below INSTRUMENTS the runtime entry point (replacing it with a
counter that records the call), drives the real production path, and asserts the
counter moved. A wiring that is only imported, or only present as source text,
fails these checks.

Checks
------
1. sentinel_enforcer  - an enforced edit consults `verify_boundary`.
2. circuit_breaker    - a failed execution writes a reflection via
                        `reflect_on_failure` (and the row really lands).
3. METACLUSTER        - a failed nature writes a reflection.
4. engram             - merely ROUTING a query produces the read-pressure signal
                        the consolidator consumes, with no explicit call.

Exit 0 only when all four hold. The last stdout line is the JSON verdict.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Counter:
    """Stand-in for a runtime entry point that records being called."""

    def __init__(self, real, result=None):
        self.real = real
        self.result = result
        self.calls: list[dict] = []

    def __call__(self, *args, **kwargs):
        self.calls.append({"args": [str(a)[:80] for a in args],
                           "kwargs": {k: str(v)[:80]
                                      for k, v in kwargs.items()}})
        if self.result is not None:
            return self.result
        return self.real(*args, **kwargs)


def check_sentinel() -> dict:
    """An enforced edit must consult the verification gate."""
    from CORE import sentinel_enforcer as se
    from CORE import technique_runtime as tr

    real = tr.verify_boundary
    counter = Counter(real)
    tr.verify_boundary = counter                     # type: ignore[assignment]
    try:
        # Do NOT pre-create the file: the enforcer's global audit hook refuses
        # an unmediated write (correctly), so the probe file is created BY the
        # enforced write under test.
        with tempfile.TemporaryDirectory(dir=str(ROOT / "state")) as td:
            target = Path(td) / "wired_boundary_probe.py"
            se.enforce_write(str(target), "x = 1\n")
        status = se.get_status()
        last_verify = status.get("last_verify") or {}
    finally:
        tr.verify_boundary = real                    # type: ignore[assignment]
    return {"check": "sentinel_enforcer->verify_boundary",
            "calls": len(counter.calls),
            "last_verify": last_verify,
            "pass": bool(counter.calls) and bool(last_verify)}


def check_circuit_breaker() -> dict:
    """A failed execution must write a verbal reflection AND land the row."""
    from CORE import technique_runtime as tr
    from CORE.circuit_breaker import CircuitBreaker

    real = tr.reflect_on_failure
    counter = Counter(real)
    tr.reflect_on_failure = counter                  # type: ignore[assignment]
    try:
        breaker = CircuitBreaker("wired-boundary-probe")
        for _ in range(2):
            try:
                breaker.execute(_boom)
            except Exception as exc:              # expected: the probe provokes a trip
                tr.note_failure("exercise:breaker-provoke", exc)
    finally:
        tr.reflect_on_failure = real                 # type: ignore[assignment]

    # The hook's question is derived from the breaker name + phase, not from the
    # error text, so query on that. Fall back to counting the event type so a
    # row that landed under a different question is still counted (measuring
    # "did a reflection land", not "did my substring match").
    stored = 0
    try:
        from CORE.WORMS.expansion.reflexion import reflections_for
        stored = len(reflections_for("wired-boundary-probe", limit=5))
        if stored == 0:
            from CORE.local_memory import get_memory_store
            rows = get_memory_store().fetch_all_memories(
                event_type="reflexion_note", limit=200) or []
            stored = sum(1 for r in rows
                         if "wired-boundary-probe" in str(r.get("data")))
    except Exception:
        stored = -1
    return {"check": "circuit_breaker->reflect_on_failure",
            "calls": len(counter.calls), "reflections_stored": stored,
            "pass": bool(counter.calls) and stored > 0}


def _boom() -> None:
    raise ValueError("wire-probe: deliberate failure")


def check_metacluster() -> dict:
    """A failed nature must write a reflection (or report it could not run)."""
    from CORE import technique_runtime as tr
    try:
        from CORE.WORMS import METACLUSTER as mc
    except Exception as exc:
        return {"check": "METACLUSTER->reflect_on_failure", "pass": False,
                "error": f"import: {type(exc).__name__}: {exc}"}

    cls = getattr(mc, "MetaCluster", None)
    if cls is None:
        return {"check": "METACLUSTER->reflect_on_failure", "pass": False,
                "error": "no MetaCluster class"}
    try:
        cluster = getattr(mc, "META_CLUSTER", None) or cls()
    except Exception as exc:
        return {"check": "METACLUSTER->reflect_on_failure", "pass": False,
                "error": f"construct: {type(exc).__name__}: {exc}"}

    # A fresh MetaCluster has an empty category map; `discover_all()` is the
    # real discovery path that fills it from the worm registry.
    if not getattr(cluster, "categories", None):
        try:
            cluster.discover_all()
        except Exception as exc:                  # setup best-effort; record why it failed
            tr.note_failure("exercise:discover-all", exc)
    cats = list(getattr(cluster, "categories", {}) or {})
    if not cats:
        # Fall back to two synthetic natures: orchestrate filters by the
        # category map, so injecting it is what makes a failure reachable.
        cats = ["__wire_a__", "__wire_b__"]
        cluster.categories = {n: ["SystemZ"] for n in cats}
    natures = cats[:2]

    # Provoke a GENUINE failure: the closure builds each category's cluster via
    # ClusterWORMZ.build_from_registry, so making that raise drives the real
    # `except Exception` branch rather than simulating one.
    # METACLUSTER imports ClusterWORMZ INSIDE the closure, and
    # `build_from_registry` is a classmethod, so the patch must go on the class
    # in its own module for the closure's import to see it.
    try:
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ as cw
    except Exception as exc:
        return {"check": "METACLUSTER->reflect_on_failure", "pass": False,
                "error": f"import ClusterWORMZ: {type(exc).__name__}"}

    def _boom(_cls, *_a, **_k):
        raise ValueError("wire-probe: deliberate category failure")

    real = tr.reflect_on_failure
    counter = Counter(real)
    real_build = getattr(cw, "build_from_registry", None)
    tr.reflect_on_failure = counter                  # type: ignore[assignment]
    cw.build_from_registry = classmethod(_boom)      # type: ignore[assignment]
    try:
        try:
            cluster.orchestrate(natures=natures)
        except Exception as exc:                  # expected: the probe forces a failure
            tr.note_failure("exercise:orchestrate-provoke", exc)
    finally:
        tr.reflect_on_failure = real                 # type: ignore[assignment]
        if real_build is not None:
            cw.build_from_registry = real_build      # type: ignore[assignment]

    if counter.calls:
        return {"check": "METACLUSTER->reflect_on_failure",
                "calls": len(counter.calls), "natures": natures, "pass": True}
    import inspect
    src = inspect.getsource(type(cluster).orchestrate)
    return {"check": "METACLUSTER->reflect_on_failure", "calls": 0,
            "natures": natures, "call_site_in_source":
                "reflect_on_failure" in src, "pass": False,
            "note": "failure branch not reached even with a raising cluster "
                    "builder"}


def check_engram() -> dict:
    """Merely routing a query must produce the consolidator's read signal."""
    try:
        from CORE.WORMS.expansion.engram import RecallRouterWorm
        router = RecallRouterWorm()
        first = router.route_recall("wire-probe: a query nobody has stored")
        state = router.recall_state()
    except Exception as exc:
        return {"check": "engram->read_pressure", "pass": False,
                "error": f"{type(exc).__name__}: {exc}"}
    reads = int(state.get("reads", 0) or 0)
    signal = state.get("noted_signal")
    return {"check": "engram->read_pressure", "reads": reads,
            "noted_signal": signal, "abstained": first.get("abstained"),
            "pass": reads > 0 and bool(signal)}


def main() -> int:
    checks = [check_sentinel(), check_circuit_breaker(), check_metacluster(),
              check_engram()]
    for c in checks:
        print("%-5s %-42s %s"
              % ("ok" if c["pass"] else "FAIL", c["check"],
                 json.dumps({k: v for k, v in c.items()
                             if k not in ("check", "pass")})[:150]))
    passed = sum(1 for c in checks if c["pass"])
    print(json.dumps({
        "exercise": "wired_boundaries", "n": len(checks), "passed": passed,
        "results": checks, "chain": passed == len(checks),
    }))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
