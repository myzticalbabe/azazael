#!/usr/bin/env python3
"""training_intake.py — Phase-2 training intake over unity rows (Oct-10).

Forensic finding: Phase 1 (memory unity) exists — every production hook call
leaves a `technique-link` join row, queens leave canonical `reward-ledger`
rows "so the learning loop can...", and reflections leave
`reflection_calibration` rows — but NO training module reads any of them.
GRPO scores from execution history; the designed intake was never built.

This module is that intake. All reads, fail-open, stdlib-only:

- gather(): join the three unity streams into one intake summary —
  per-hook ok-rates, per-subject canonical rewards, calibration error stats.
  Consumers: monitor/fitness level only.

REJECTED (prior Phase-2 lesson, obs #382): per-worm GRPO reward shaping
from global link terms — group normalization washes global terms, and
per-worm mapping would be substring-guessing. No shaping wrapper ships
in this module for that reason; shaping stays out until per-worm hook
identity exists.
"""

from __future__ import annotations

from typing import Any, Dict, List

from CORE.local_memory import get_memory_store

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass


def gather(limit: int = 200) -> Dict[str, Any]:
    """Join unity rows into one intake summary. Read-only, fail-open."""
    out: Dict[str, Any] = {"n_link": 0, "link_ok_rate": None,
                           "by_hook": {}, "rewards": {}, "n_rewards": 0,
                           "calibration": {"n": 0, "mean_abs_error": None}}
    try:
        store = get_memory_store()
    except Exception as exc:
        note_failure("training-intake:store", exc)
        out["store_error"] = type(exc).__name__
        return out
    try:
        link_rows = store.query_memories(source="technique-link",
                                         limit=int(limit)) or []
    except Exception as exc:
        note_failure("training-intake:link-read", exc)
        link_rows = []
    try:
        reward_rows = store.query_memories(source="reward-ledger",
                                           limit=int(limit)) or []
    except Exception as exc:
        note_failure("training-intake:reward-read", exc)
        reward_rows = []
    try:
        cal_rows = store.query_memories(source="reflection_calibration",
                                        limit=int(limit)) or []
    except Exception as exc:
        note_failure("training-intake:cal-read", exc)
        cal_rows = []

    ok = 0
    by_hook: Dict[str, List[int]] = {}
    for r in link_rows:
        d = r.get("data") or {}
        hook = str(d.get("hook", d.get("event_type", "?")))
        good = 1 if d.get("ok", False) else 0
        ok += good
        by_hook.setdefault(hook, [0, 0])
        by_hook[hook][0] += good
        by_hook[hook][1] += 1
    out["n_link"] = len(link_rows)
    out["link_ok_rate"] = round(ok / len(link_rows), 4) if link_rows else None
    out["by_hook"] = {h: round(g / max(t, 1), 4) for h, (g, t) in by_hook.items()}

    rewards: Dict[str, float] = {}
    for r in reward_rows:
        d = r.get("data") or {}
        subj = str(d.get("subject", d.get("team", d.get("worm", "?"))))
        try:
            rewards[subj] = float(d.get("value", d.get("reward", 0.0)))
        except (TypeError, ValueError) as exc:
            note_failure("training-intake:86", exc)
            continue
    out["rewards"] = rewards
    out["n_rewards"] = len(rewards)

    errs: List[float] = []
    for r in cal_rows:
        d = r.get("data") or {}
        try:
            if d.get("predicted") is not None and d.get("realised") is not None:
                errs.append(abs(float(d["predicted"]) - float(d["realised"])))
        except (TypeError, ValueError) as exc:
            note_failure("training-intake:97", exc)
            continue
    out["calibration"] = {"n": len(cal_rows),
                          "n_scored": len(errs),
                          "mean_abs_error": (round(sum(errs) / len(errs), 6)
                                             if errs else None)}
    return out

