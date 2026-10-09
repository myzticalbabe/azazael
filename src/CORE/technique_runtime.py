#!/usr/bin/env python3
"""technique_runtime.py — the production call path for the harvested techniques.

Why this exists
---------------
`state/SOTA_FULL_REVIEW_2026-10-09.md` reviews 181 harvested techniques against
this codebase. Its dominant finding is NOT missing code — it is **unreachable**
code. Read by reading, on 2026-10-09:

    verification_gate.py   9 composed detectors   1 caller  (an exercise script)
    dispatch_plan.py       plan_dag/assign_roles  2 callers (both exercises)
    reflexion.py           complete buffer        0 production callers
    skill_library.py       8 exported functions   0 importers

So the techniques were *implemented* and then never invoked. A capability with no
call site is indistinguishable from a missing capability, and it rots.

What this module is
-------------------
The single production surface that invokes them, plus the registry that makes the
set enumerable rather than aspirational. Every wiring is an adapter registered
under its EP code:

    from CORE.technique_runtime import register, run_all

    register("EP44", "ReAct driver loop", "CORE.structured_action:drive", fn)

`run_all()` invokes every registered adapter and reports per-EP engagement, so
"all of it is wired" is a command anyone can run and check, not a claim in a
document. Adapters live in `CORE/technique_wiring/` (one module per layer) and
register themselves on import; this file never needs to know they exist.

Contract for an adapter
-----------------------
- takes no arguments and returns a dict describing what it just did;
- is FAIL-OPEN: it catches its own exceptions and never raises into a caller;
- is READ-MOSTLY: it must be safe to invoke on a live system (the self-test runs
  every adapter, so an adapter that mutates the repo or spends money is a bug);
- names the module::symbol it invokes, so the registry is an audit trail.

Deliberately stdlib-only. No adapter here may import a heavy dependency: a wiring
that cannot run on this box is not a wiring, it is a wish.
"""
from __future__ import annotations

import importlib
import threading
import time
from typing import Any, Callable, Dict, List

__all__ = [
    "register", "ADAPTERS", "load_slices", "run_all", "status",
    "verify_boundary", "reflect_on_failure", "recall_with_feedback",
    "discover_wirings",
]

#: EP code -> {"ep", "name", "where", "fn", "layer"}. Populated by `register`
#: from the slice modules and by the direct helpers below.
ADAPTERS: Dict[str, Dict[str, Any]] = {}

#: The ledger lives in a leaf module (stdlib only, zero CORE imports) so that
#: any module can import the recorder without risking an import cycle -- a cycle
#: caught by a guarded import would silently turn every recording into a no-op.
#: Re-exported here because callers and tests reach it as
#: `technique_runtime.note_failure` / `technique_runtime.failure_notes`.
from CORE.failure_ledger import failure_notes, note_failure  # noqa: F401

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)

#: Slice modules under CORE.technique_wiring/. Imported lazily so a slice that
#: fails to import (a missing optional dep) degrades to "that layer is not wired"
#: instead of making the whole runtime unimportable.
SLICES = (
    "_b01_05",
    "_l0_model",
    "_l1_memory",
    "_l2_skills",
    "_l3_verify",
    "_l4_exec",
    "_l5_dispatch",
    "_l6_evolve",
    "_l7_interface",
)

_loaded = False


# -- registry ------------------------------------------------------------------

def register(ep: str, name: str, where: str, fn: Callable[[], Any],
             layer: str = "") -> None:
    """Register one technique's production invocation under its EP code.

    ep:    the EP code from the review ("EP44").
    name:  the technique name (review row title).
    where: the module::symbol actually invoked — the audit trail.
    fn:    the adapter (no args, returns a dict, fail-open, read-mostly).
    """
    ep = str(ep).strip().upper()
    if not ep.startswith("EP") or not callable(fn):
        return
    if layer and not str(layer).upper().startswith("L"):
        raise ValueError(f"layer must be L0..L7, got {layer!r}")
    ADAPTERS[ep] = {"ep": ep, "name": str(name), "where": str(where),
                    "fn": fn, "layer": (layer or "").upper()}


def load_slices(force: bool = False) -> Dict[str, str]:
    """Import every slice module so its `register` calls run.

    Returns {slice_name: "ok" | "MISSING: <why>"}. A slice that fails to import
    is reported, never fatal: the runtime must stay usable when one layer's
    optional dependency is absent.
    """
    global _loaded
    report: Dict[str, str] = {}
    if _loaded and not force:
        return report
    for name in SLICES:
        mod = f"CORE.technique_wiring.{name}"
        try:
            importlib.import_module(mod)
            report[name] = "ok"
        except Exception as exc:                      # pragma: no cover - env
            note_failure("technique_runtime:L122", exc)
            report[name] = f"MISSING: {type(exc).__name__}: {exc}"
    _loaded = True
    return report


def _ep_key(ep: str) -> tuple:
    """Sort EPs numerically ('EP9' before 'EP10'), non-numeric last."""
    try:
        return (0, int(ep[2:]))
    except ValueError:
        note_failure("technique_runtime:L132", None)
        return (1, 0)


def discover_wirings() -> List[str]:
    """The registered EP codes, sorted — the enumerable form of 'all of it'."""
    load_slices()
    return sorted(ADAPTERS, key=_ep_key)


def status(record: bool = True) -> Dict[str, Any]:
    """The registry as data: what is wired, where, and on which layer."""
    load_slices()
    rows = [{"ep": a["ep"], "name": a["name"], "where": a["where"],
             "layer": a["layer"]} for a in ADAPTERS.values()]
    rows.sort(key=lambda r: _ep_key(r["ep"]))
    out = {"n_wired": len(rows), "wirings": rows}
    if record:
        _cite("technique-wiring", True,
              [f"wired:{len(rows)}"], [])
    return out


def run_all(record: bool = True) -> Dict[str, Any]:
    """Invoke EVERY registered adapter. This is the point of the module.

    Returns {"n", "engaged", "errored", "results": {ep: {...}}}. `engaged` counts
    adapters that ran to completion; `errored` counts adapters that raised (a bug
    in the adapter, reported — never swallowed). A non-zero `errored` means this
    module's own contract is broken.
    """
    load_slices()
    results: Dict[str, Any] = {}
    engaged = errored = 0
    for ep in sorted(ADAPTERS, key=_ep_key):
        a = ADAPTERS[ep]
        t0 = time.perf_counter()
        try:
            value = a["fn"]()
            engaged += 1
            entry = {"ok": True, "where": a["where"],
                     "summary": _summarise(value),
                     "ms": round((time.perf_counter() - t0) * 1000, 2)}
            if isinstance(value, dict):
                entry["verdict"] = _verdict_keys(value)
        except Exception as exc:
            note_failure("technique_runtime:L177", exc)
            errored += 1
            entry = {"ok": False, "where": a["where"],
                     "error": f"{type(exc).__name__}: {exc}",
                     "ms": round((time.perf_counter() - t0) * 1000, 2)}
        results[ep] = entry

    out = {"n": len(results), "engaged": engaged, "errored": errored,
           "results": results}
    if record:
        _cite("technique-runtime", errored == 0,
              [f"wired:{len(results)}", f"engaged:{engaged}",
               f"errored:{errored}"],
              [f"fix adapter: {ep}" for ep, r in results.items()
               if not r["ok"]])
    return out


def _verdict_keys(value: Dict[str, Any]) -> Dict[str, Any]:
    """The boolean verdict flags an adapter's result carries, if any."""
    keys = ("accepted", "valid", "ok", "complete", "executable", "closed",
            "permitted", "passed", "engaged")
    return {k: value[k] for k in keys if isinstance(value.get(k), bool)}


def _summarise(value: Any) -> str:
    """A one-line, bounded description of an adapter's return value."""
    if value is None:
        return "None"
    if isinstance(value, dict):
        return ", ".join(f"{k}={_short(v)}" for k, v in list(value.items())[:6])
    if isinstance(value, (list, tuple, set)):
        return f"{type(value).__name__}({len(value)})"
    return _short(value)


def _short(v: Any, limit: int = 40) -> str:
    s = str(v)
    return s if len(s) <= limit else s[:limit - 1] + "\u2026"


# -- direct helpers: the production call paths used by live boundaries ---------
#
# These are the four entry points real code should call. Each is fail-open and
# each records a ledger citation, so an integration is auditable at the boundary
# rather than only in the runtime's own self-test.

def verify_boundary(subject: str, **kwargs: Any) -> Dict[str, Any]:
    """Verify a layer transition before accepting it (verify-before-accept).

    Thin, fail-open wrapper over `verification_gate.verify_before_accept` — the
    function that nine composed detectors sit behind and that, before this
    runtime, no production boundary called.

    Extra kwargs are forwarded when the gate's signature accepts them and dropped
    otherwise, so a caller written against an older gate cannot crash a boundary.
    """
    try:
        from CORE import verification_gate as vg
        sig = getattr(vg, "verify_before_accept", None)
        if sig is None:
            return {"accepted": True, "reasons": ["no-gate"],
                    "remediations": [], "citation": ""}
        import inspect
        params = inspect.signature(sig).parameters
        accepted = {k: v for k, v in kwargs.items() if k in params}
        verdict = sig(subject=str(subject), **accepted)
        return verdict if isinstance(verdict, dict) else {
            "accepted": bool(verdict), "reasons": [], "remediations": [],
            "citation": ""}
    except Exception as exc:
        # A verifier that fails must not block the boundary it guards: report
        # the failure and let the caller proceed (fail-open is the house rule
        # for every gate in this tree) -- but RECORD it, so a gate that is
        # silently erroring is visible in failure_notes() rather than looking
        # exactly like a gate that passed.
        note_failure("verify-boundary", exc)
        return {"accepted": True, "reasons": [f"gate-error:{type(exc).__name__}"],
                "remediations": [], "citation": ""}


def reflect_on_failure(question: str, what_failed: str, what_next: str,
                       decision_id: str | None = None,
                       predicted: float | None = None) -> Dict[str, Any]:
    """Write one verbal reflection after a failed attempt (Reflexion, EP113).

    Adds what the buffer was missing: `predicted`, the caller's own confidence
    *before* the attempt, stored with the realised outcome so calibration can be
    measured later instead of asserted (EP294).
    """
    written = False
    try:
        from CORE.WORMS.expansion import reflexion as _rx
        written = bool(_rx.record_reflection(
            question=question, what_failed=what_failed, what_next=what_next,
            decision_id=decision_id))
        if predicted is not None:
            _record_calibration(question, predicted, decision_id)
    except Exception:
        note_failure("technique_runtime:L275", None)
        written = False
    return {"written": written, "question": _short(question),
            "predicted": predicted}


def _record_calibration(question: str, predicted: float,
                        decision_id: str | None) -> None:
    """Store a predicted-vs-realised row (EP294). Fail-open."""
    try:
        from CORE.local_memory import get_memory_store
        get_memory_store().record_event(
            source="reflection_calibration",
            event_type="reflection_calibration",
            data={"question": _short(question, 200),
                  "predicted": float(predicted),
                  "decision_id": str(decision_id or "")},
            severity="info", tags=["reflection", "calibration"])
    except Exception as exc:
        note_failure("reflection-calibration", exc)


def recall_with_feedback(query: str, **kwargs: Any) -> Dict[str, Any]:
    """Recall through the router and feed the read statistics back (EP235).

    The loop the review found missing: `RecallRouterWorm` already records which
    shards it hit and how well they scored (`_hits`, `_last_scores`); nothing
    consumed them. Recording the read here is what lets consolidation learn from
    what consumers actually needed.
    """
    try:
        from CORE.WORMS.expansion import engram as _en
        router_cls = getattr(_en, "RecallRouterWorm", None)
        if router_cls is None:
            return {"routed": False, "reason": "no-router"}
        router = router_cls()
        route = router.route_recall(str(query))
        return {"routed": True, "route": (route or {}).get("route"),
                "mode": (route or {}).get("mode"),
                "hits": len(getattr(router, "_hits", []) or [])}
    except Exception as exc:
        note_failure("technique_runtime:L315", exc)
        return {"routed": False, "reason": f"{type(exc).__name__}"}


def _cite(subject: str, accepted: bool, reasons: List[str],
          remediations: List[str]) -> str:
    """Cite a runtime verdict on the hash-chained ledger (fails open)."""
    try:
        from CORE import audit_trail as _at
        return _at.audit_verification_gate(subject, accepted,
                                           list(reasons), list(remediations))
    except Exception as exc:
        # Uncited, but recorded: a missing ledger is a degraded audit trail, and
        # `failure_notes()` must be able to say so.
        note_failure("audit-cite", exc)
        return ""
