# coding: utf-8
"""
AOA delegation spec — the 4-tuple subagent contract (AOrchestra, 2026-02).

A routing decision used to dissolve at the executor boundary: the router
chose ``arm_id`` for ``capability`` with a ``reason``, then called
``arm.execute(capability, payload)`` with a bare payload. The choice's
context (why this arm, what evidence, which model) never reached the arm,
and the result carried no record of the delegation that caused it — so
orchestration quality could not be learned from experience.

``DelegationSpec`` is the contract that crosses that boundary, after
AOrchestra's ``(Instruction, Context, Tools, Model)`` tuple:

* Instruction — what to do: capability + selection reason.
* Context    — what it may know: caller payload + evidence snapshot.
* Tools      — what it may touch: arm_id + capability (the tool address).
* Model      — what it runs as: optional model/provider hint; arms own
  their execution, so None means "arm default" and is always valid.

Wire-compatible by construction: ``to_payload()`` returns the original
payload plus a ``_delegation`` envelope arms ignore if they do not read
it, and ``attach()`` adds provenance keys to the routed result without
changing its shape. Nothing in ``BaseArm.execute`` changes signature.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here

#: Envelope key. Underscore-prefixed by the convention that caller payload
#: keys are domain words; a collision with a real arm payload key would
#: silently change what the arm computes.
ENVELOPE_KEY = "_delegation"


@dataclass(frozen=True)
class DelegationSpec:
    """One routed delegation. Immutable: the decision as made."""

    instruction: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    model: Optional[str] = None
    reason: str = ""
    degraded: bool = False

    def to_payload(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Caller payload plus the envelope. Arms that ignore it behave
        exactly as before; arms that read it get the full contract."""
        base = dict(payload or {})
        base[ENVELOPE_KEY] = {
            "instruction": self.instruction,
            "tools": list(self.tools),
            "model": self.model,
            "reason": self.reason,
            "degraded": bool(self.degraded),
        }
        return base

    def attach(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Stamp provenance onto a routed result dict, in place."""
        if isinstance(result, dict):
            result["delegation"] = {
                "instruction": self.instruction,
                "tools": list(self.tools),
                "model": self.model,
                "reason": self.reason,
                "degraded": bool(self.degraded),
            }
        return result

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def from_route(capability: str,
               payload: Optional[Dict[str, Any]],
               decision: Optional[Dict[str, Any]],
               arm_id: str,
               model: Optional[str] = None) -> DelegationSpec:
    """Build the spec a routing decision implies.

    Never raises: a damaged decision degrades to an honest minimal spec
    (empty reason, degraded=True) rather than stopping the route — the
    router's contract is that routing never fails on bookkeeping.
    """
    try:
        dec = decision if isinstance(decision, dict) else {}
        reason = str(dec.get("reason") or "")
        degraded = bool(dec.get("degraded", False))
        evidence = dec.get("evidence")
        ctx = dict(payload) if isinstance(payload, dict) else {}
        if isinstance(evidence, dict):
            ctx["_routing_evidence"] = {
                k: {"q": (v or {}).get("q"), "pulls": (v or {}).get("pulls")}
                for k, v in evidence.items()
                if isinstance(v, dict)
            }
        instruction = str(capability or "")
        if reason:
            instruction = "%s [%s]" % (instruction, reason)
        return DelegationSpec(
            instruction=instruction,
            context=ctx,
            tools=[str(arm_id)] if arm_id else [],
            model=model,
            reason=reason,
            degraded=degraded,
        )
    except Exception:
        note_failure("delegation_spec:L112", None)
        safe_ctx = dict(payload) if isinstance(payload, dict) else {}
        return DelegationSpec(
            instruction=str(capability or ""),
            context=safe_ctx,
            tools=[str(arm_id)] if arm_id else [],
            model=model,
            reason="",
            degraded=True,
        )
