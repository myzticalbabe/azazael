# coding: utf-8
"""Canonical reward co-tabulation (memory unity: one converged scale).

Every trainer/loop/gate in this tree measures something else: success rates
[0,1], unbounded fitness sums, millisecond durations, boolean vetoes,
z-scored advantages, losses (lower-better), margins, counts. Averaging across
spaces without a common scale lets one space's units swamp the rest — a single
fitness point outweighs a whole [0,1] rate, and an unbounded -ms/10000 tail
vetoes a reliable worm.

This module is the meeting point, not another normalizer:
- SCALES: registry of named scales (units, range, higher_better).
- canonical_reward(...): validated record {value, scale_id, provenance}.
- to_common_scale(record, baseline): z-space mapping that REFUSES (None)
  without a measured baseline instead of inventing one.
- emit_canonical(store, ...): one canonical row (source reward-ledger).
- scale_distributions(store, ...): measured {mean, std, ...} per scale_id —
  the baselines future calibration consumes.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here


SCALES: Dict[str, Dict[str, Any]] = {
    "rate_01": {"units": "fraction", "range": (0.0, 1.0), "higher_better": True,
                "notes": "success rates, accuracies, Wilson means, LLM scores, rubric scores"},
    "boolean": {"units": "flag", "range": (0, 1), "higher_better": True,
                "notes": "accept/deny, valid/invalid, pass/fail"},
    "count": {"units": "items", "range": (0, None), "higher_better": None,
              "notes": "extensive: support counts, savings slots, pulls; direction is contextual"},
    "millis": {"units": "milliseconds", "range": (0.0, None), "higher_better": False,
               "notes": "durations; never average against rates (documented harm)"},
    "fitness_points": {"units": "avg_reward sums", "range": (None, None), "higher_better": True,
                       "notes": "evolution totals; unbounded, pool-relative only"},
    "zscore": {"units": "std from group mean", "range": (None, None), "higher_better": True,
               "notes": "GRPO/DAPO advantages; comparable only within their group"},
    "loss": {"units": "nats", "range": (0.0, None), "higher_better": False,
             "notes": "DPO-style losses; lower is better — negate before ranking with rewards"},
    "margin": {"units": "native", "range": (None, None), "higher_better": True,
               "notes": "raw margins; prefer bounded_margin form for cross-use"},
    "probability": {"units": "probability", "range": (0.0, 1.0), "higher_better": True,
                    "notes": "calibrated beliefs; rank recall prefers scored rows"},
    "severity_payoff": {"units": "table units", "range": (-1.4, 1.4), "higher_better": True,
                        "notes": "RL per-step table values; action-indexed, not cross-action comparable"},
}


def describe_scale(scale_id: str) -> Dict[str, Any]:
    """Return the registry entry for a scale, or {} when unknown."""
    entry = SCALES.get(str(scale_id))
    return dict(entry) if isinstance(entry, dict) else {}


def canonical_reward(value: Any, scale_id: str,
                     provenance: str = "") -> Dict[str, Any]:
    """Build a validated canonical reward record.

    Never raises and never drops data: unknown scales, non-numeric and
    non-finite values are kept with ok=False and a reason, so a bad
    producer is visible instead of silently absent.
    """
    rec: Dict[str, Any] = {
        "value": value, "scale_id": str(scale_id),
        "provenance": str(provenance or ""), "ok": True, "reason": "",
    }
    if str(scale_id) not in SCALES:
        rec.update(ok=False, reason="unknown-scale")
        return rec
    if isinstance(value, bool):
        if str(scale_id) != "boolean":
            rec.update(ok=False, reason="non-numeric")
            return rec
        rec["value"] = int(value)
        return rec
    if not isinstance(value, (int, float)):
        rec.update(ok=False, reason="non-numeric")
        return rec
    if value != value or value in (float("inf"), float("-inf")):
        rec.update(value=None, ok=False, reason="non-finite")
        return rec
    lo, hi = SCALES[str(scale_id)]["range"]
    if (lo is not None and value < lo) or (hi is not None and value > hi):
        rec["reason"] = "out-of-range (kept)"
    return rec


def to_common_scale(record: Dict[str, Any],
                    baseline: Optional[Dict[str, Any]]) -> Optional[float]:
    """Map a canonical record into z-space against a MEASURED baseline.

    baseline is {mean, std} from scale_distributions(). REFUSES (None) when
    the baseline is missing, non-numeric, or zero-variance: rescaling against
    an invented distribution is how one space silently swamps another.
    """
    z: Optional[float] = None
    try:
        value = (record or {}).get("value")
        mean = (baseline or {}).get("mean")
        std = (baseline or {}).get("std")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if isinstance(mean, bool) or not isinstance(mean, (int, float)):
            return None
        if isinstance(std, bool) or not isinstance(std, (int, float)):
            return None
        if std <= 0:
            return None
        z = (float(value) - float(mean)) / float(std)
    except Exception as exc:
        note_failure("reward-scales:to-common-scale", exc)
        z = None
    return z


def emit_canonical(store: Any, value: Any, scale_id: str, provenance: str,
                   worm: Any = None, context_key: Any = None) -> bool:
    """Write one canonical reward row. Fail-open: never raises."""
    rec = canonical_reward(value, scale_id, provenance)
    data: Dict[str, Any] = {
        "scale_id": rec["scale_id"], "value": rec["value"],
        "ok": rec["ok"], "reason": rec["reason"],
        "provenance": rec["provenance"],
    }
    if worm is not None:
        data["worm"] = str(worm)
    if context_key is not None:
        data["context_key"] = str(context_key)
    kept = False
    try:
        kept = bool(store.record_event(
            "reward-ledger", "reward-term", data,
            severity="info", tags=["reward-ledger", str(scale_id)]))
    except Exception as exc:
        note_failure("reward-scales:emit", exc)
    return kept


def scale_distributions(store: Any, limit: int = 5000) -> Dict[str, Any]:
    """Measured {n, mean, std, min, max} per scale_id over canonical rows.

    Only ok=True numeric rows count. Empty store -> {} (callers must treat
    missing baselines as refusal input to to_common_scale, not as zeros).
    """
    out: Dict[str, Any] = {}
    rows: list = []
    try:
        rows = store.query_memories(
            source="reward-ledger", limit=int(limit)) or []
    except Exception as exc:
        note_failure("reward-scales:distributions-read", exc)
        rows = []
    buckets: Dict[str, list] = {}
    for r in rows:
        data = r.get("data") if isinstance(r.get("data"), dict) else {}
        if data.get("ok") is not True:
            continue
        v = data.get("value")
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        buckets.setdefault(str(data.get("scale_id", "unknown")), []).append(
            float(v))
    for sid, vals in buckets.items():
        n = len(vals)
        mean = sum(vals) / n
        var = sum((v - mean) ** 2 for v in vals) / n
        out[sid] = {"n": n, "mean": mean, "std": var ** 0.5,
                    "min": min(vals), "max": max(vals)}
    return out


def calibration_snapshot(store: Any, limit: int = 5000) -> Dict[str, Any]:
    """z-scores of the latest row per scale against measured baselines.

    The first real CONSUMER of the co-tabulated ledger: for every scale
    with a measured baseline (std > 0), map its latest ok=True numeric row
    into z-space. Scales without baselines are reported refused, never
    invented. Writes one summary row (source reward-ledger, event
    reward-calibration, no value field so scale_distributions skips it).
    Fail-open: never raises.
    """
    out: Dict[str, Any] = {"scales": {}, "refused": [], "kept": False}
    try:
        dists = scale_distributions(store, limit=limit)
        rows = store.query_memories(source="reward-ledger",
                                    limit=int(limit)) or []
    except Exception as exc:
        note_failure("reward-scales:calibration-read", exc)
        return out
    latest: Dict[str, Dict[str, Any]] = {}
    for r in rows if isinstance(rows, list) else []:
        if not isinstance(r, dict):
            continue
        data = r.get("data") if isinstance(r.get("data"), dict) else {}
        if data.get("ok") is not True:
            continue
        v = data.get("value")
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        sid = str(data.get("scale_id", "unknown"))
        rid = r.get("id", 0)
        try:
            rid = int(rid)
        except Exception:
            rid = 0
        if sid not in latest or rid > latest[sid].get("_id", -1):
            latest[sid] = {"value": float(v), "_id": rid}
    for sid, info in latest.items():
        base = dists.get(sid) or {}
        z = to_common_scale({"value": info["value"]}, base)
        if z is None:
            out["refused"].append(sid)
        else:
            out["scales"][sid] = {"z": z, "value": info["value"],
                                  "n": base.get("n")}
    try:
        out["kept"] = bool(store.record_event(
            "reward-ledger", "reward-calibration",
            {"scales": {k: {"z": v["z"], "value": v["value"]}
                        for k, v in out["scales"].items()},
             "refused": list(out["refused"])},
            severity="info", tags=["reward-ledger", "calibration"]))
    except Exception as exc:
        note_failure("reward-scales:calibration-write", exc)
    return out
