# coding: utf-8
"""dream_policy_bridge.py — Close the dream->policy loop.

Applies dream suggestions through MetaCognitionWorm.adapt_strategy (the
designed policy channel: confidence-weighted recommendations persisted as
strategy_adaptation rows), one suggestion at a time.

Safety:
- CurativePool governance per suggestion; blocked items are skipped.
- Minimum confidence gate (default 0.05, calibrated to the creative
  branch band 0.07-0.45; CurativePool remains the real safety).
- Fail-closed: governance/import errors skip items, never raise.
- Audit row per run (best effort).

This module is the `policy_fn` that dreaming.integrate_best() accepts but
no production caller currently passes.
"""

from typing import Any, Dict, List, Optional

MIN_CONFIDENCE = 0.05


def _governance_blocked(suggestion: Dict[str, Any]) -> bool:
    """True when CurativePool explicitly blocks. Fail-closed on errors."""
    try:
        from META.MetaWormSpawner import CurativePool
        pool = CurativePool()
        result = pool.evaluate_action(
            {"context": "dream_policy_bridge",
             "params": {"suggestion": str(suggestion)[:300]}},
            {"action_type": "execute", "output_size": 100,
             "feature": "dream_policy"},
            [{"role": "user", "content": "apply dream policy suggestion"}],
            [{"id": "dream_policy", "archetype": "The Artist"}],
        )
        return result.get("decision") == "blocked"
    except Exception:
        return True


def apply_dream_policy(suggestions: Optional[List[Dict[str, Any]]],
                       patterns: Optional[List[Dict[str, Any]]] = None,
                       min_confidence: float = MIN_CONFIDENCE) -> Dict[str, Any]:
    """Apply dream suggestions to live strategy policy. Returns report dict."""
    applied: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    try:
        from CORE.WORMS.expansion.meta_cognition import MetaCognitionWorm
        mc = MetaCognitionWorm()
    except Exception as e:
        return {"applied": applied,
                "skipped": [{"reason": f"mc-unavailable: {e}"}],
                "governed": False}

    for s in suggestions or []:
        try:
            if not isinstance(s, dict) or s.get("confidence", 0) < min_confidence:
                skipped.append({"reason": "low-confidence"})
                continue
            if _governance_blocked(s):
                skipped.append({"reason": "governance-blocked"})
                continue
            worm = str(s.get("source") or "global")
            actions = [a for a in (s.get("strategies") or
                                   [s.get("recovery_action")]) if a]
            if not actions:
                skipped.append({"reason": "no-actionable-strategy"})
                continue
            res = mc.adapt_strategy(worm, "default", actions)
            applied.append({"worm": worm, "actions": actions,
                            "recommended": res.get("recommended_strategy"),
                            "should_adapt": res.get("should_adapt")})
        except Exception as e:
            skipped.append({"reason": f"error: {e}"})

    try:
        from CORE.direct_memory import DirectMemory
        DirectMemory().record("policy_applied", {
            "action": "dream policy bridge run",
            "applied": len(applied), "skipped": len(skipped),
        }, tags=["policy", "dream", "bridge"])
    except Exception:
        pass
    return {"applied": applied, "skipped": skipped}
