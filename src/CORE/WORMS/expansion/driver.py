# coding: utf-8
"""
GOAL/CURIOSITY DRIVER — Category: ORCHESTRATION (1 worm)
Gives the mesh a "want": goal proposals + curiosity-ranked trials, driven
by local gemma-4-E2B (llama-server on :8089) with heuristic fallbacks.

Why gemma-E2B can drive: 3.19GB Q4 fits beside the 5.5GB-free budget,
~20s per short judgment is fine at hourly cadence, and every model call
has a deterministic fallback so a dead server degrades to heuristics,
never to a stall.

GemmaDriverWorm: propose_goal(), rank_trials(), judge_dream(),
compute_fitness(). Pure-python fitness needs no model.
"""

import json
import threading
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any

try:
    from CORE.worm_registry import register_worm
except ImportError:
    def register_worm(**kw):
        return lambda cls: cls

BASE = "http://127.0.0.1:8089/v1/chat/completions"


def compute_fitness(hist: list) -> dict[str, Any]:
    """Scalar fitness from fitness.jsonl rows. Higher = healthier learning.

    Components: coverage growth (new ledger keys implied by sample growth),
    fail-band health (5-25% failure = learning zone), Q movement (spread
    changing = adapting, frozen = stagnant), proposal yield.
    """
    if not hist:
        return {"fitness": 0.0, "components": {}}
    first, last = hist[0], hist[-1]
    growth = max(0.0, (last.get("samples", 0) - first.get("samples", 0)) / 50.0)
    growth = min(1.0, growth)
    fails = last.get("fails", 0)
    samples = max(1, last.get("samples", 0))
    fr = fails / samples
    band = 1.0 - min(1.0, abs(fr - 0.12) / 0.12) if fr > 0 else 0.2
    spreads = [h.get("q_spread", 0.0) for h in hist[-6:]]
    move = 0.0
    if len(spreads) > 1:
        move = min(1.0, abs(spreads[-1] - spreads[0]) * 4.0 + 0.1)
    fit = round(0.4 * growth + 0.3 * band + 0.2 * move + 0.1 * 1.0, 3)
    return {"fitness": fit, "components": {"growth": round(growth, 3),
                                           "fail_band": round(band, 3),
                                           "q_move": round(move, 3),
                                           "fail_rate": round(fr, 4)}}


@register_worm(category="orchestration", priority=7, cooldown_seconds=300.0,
    description="Gemma-E2B goal/curiosity driver with heuristic fallbacks")
class GemmaDriverWorm:
    """Local-model driver. Slow (~20s/call) -> use per-cycle max, cache goals."""

    VERSION = "1.0.0"

    def __init__(self, timeout: float = 120.0):
        self._timeout = timeout
        self._lock = threading.Lock()
        self._calls = 0
        self._fallbacks = 0

    def _chat(self, prompt: str, max_tokens: int = 96) -> str | None:
        body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                           "max_tokens": max_tokens, "temperature": 0.2}).encode()
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(BASE, data=body,
                                       headers={"Content-Type": "application/json"}),
                timeout=self._timeout)
            with self._lock:
                self._calls += 1
            msg = json.loads(r.read())["choices"][0]["message"]
            # reasoning-model builds park output in reasoning_content with
            # empty content (seen live on gemma-4-E2B); fall back to it.
            text = (msg.get("content") or "").strip()
            if not text:
                text = (msg.get("reasoning_content") or "").strip()
            self._log_call(prompt, text)
            return text
        except Exception:
            with self._lock:
                self._fallbacks += 1
            return None

    def propose_goal(self, fitness_hist: list) -> dict[str, Any]:
        """One objective for the next stretch. Model first, heuristic fallback."""
        fit = compute_fitness(fitness_hist)
        prompt = ("You steer a self-improving computer monitor. Recent fitness: "
                  f"{json.dumps(fit)}. Pick the lowest component among "
                  "growth, fail_band, q_move and reply ONLY JSON like "
                  '{"objective":"raise q_move via chaos drills",'
                  '"target_metric":"q_move","target_value":0.5}. '
                  "target_metric MUST be one of growth, fail_band, q_move.")
        txt = self._chat(prompt)
        if txt:
            try:
                start = txt.find("{")
                goal = json.loads(txt[start:txt.rfind("}") + 1])
                return {"success": True, "src": "gemma-e2b", "fitness": fit,
                        "goal": goal}
            except Exception:
                pass
        # fallback: aim at the weakest improvable component (fail_rate is a
        # raw input, not a maximand — never target it directly).
        comps = {k: v for k, v in fit.get("components", {}).items()
                 if k != "fail_rate"} or {"growth": 0.0}
        weak = min(comps, key=lambda k: comps[k])
        return {"success": True, "src": "heuristic", "fitness": fit,
                "goal": {"objective": f"raise {weak} next stretch",
                         "target_metric": weak, "target_value": 0.8}}

    def rank_trials(self, candidates: list, context: str = "",
                    stats: dict | None = None) -> dict[str, Any]:
        """Curiosity order: least-sampled first (model may rerank).

        Pass stats={env: {ok_rate, median_ms, samples}} to ground the model
        in measured history — ungrounded rankings tested near-random.
        """
        stat_txt = ""
        if stats:
            stat_txt = " Measured history: " + "; ".join(
                f"{e}: ok={v.get('ok_rate')} med={v.get('median_ms')}ms "
                f"n={v.get('samples')}" for e, v in stats.items()) + "."
        prompt = ("Rank these probe targets by reliability (proven low latency "
                  "and high success first) for a self-learning monitor. "
                  f"Context: {context[:200]}.{stat_txt} "
                  f"Targets: {', '.join(candidates)}. Reply ONLY a comma "
                  "list in best-first order.")
        txt = self._chat(prompt, max_tokens=48)
        if txt:
            ranked = [c.strip() for c in txt.replace("\n", ",").split(",")]
            ordered = [c for c in ranked if c in candidates]
            ordered += [c for c in candidates if c not in ordered]
            return {"success": True, "src": "gemma-e2b", "order": ordered}
        return {"success": True, "src": "heuristic", "order": list(candidates)}

    def judge_dream(self, dream: str) -> dict[str, Any]:
        """Keep/reject a synthetic dream. Model judge, heuristic fallback."""
        txt = self._chat("Is this a coherent system-dream worth remembering? "
                         f"Reply ONLY yes or no. Dream: {dream[:300]}",
                         max_tokens=8)
        if txt:
            return {"success": True, "src": "gemma-e2b",
                    "keep": txt.lower().startswith("y")}
        ok = len(dream.strip()) >= 40 and " " in dream.strip()
        return {"success": True, "src": "heuristic", "keep": ok}

    def stats(self) -> dict:
        with self._lock:
            return {"calls": self._calls, "fallbacks": self._fallbacks}

    MISTAKE_LOG = "G:/source-of-truth/azazael_models/gemma_mistakes.jsonl"

    def _log_call(self, prompt: str, reply: str) -> None:
        """Every driver call becomes future training data (mistake mining)."""
        import os as _os
        try:
            parsed_ok = False
            try:
                start = reply.find("{")
                json.loads(reply[start:reply.rfind("}") + 1])
                parsed_ok = True
            except Exception:
                pass
            rec = {"at": datetime.now(timezone.utc).isoformat(),
                   "prompt": prompt[:500], "reply": reply[:800],
                   "parsed_ok": parsed_ok, "empty": not bool(reply)}
            _os.makedirs(_os.path.dirname(self.MISTAKE_LOG), exist_ok=True)
            with open(self.MISTAKE_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
        except Exception:
            pass

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.stats()}
