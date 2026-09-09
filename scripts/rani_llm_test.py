#!/usr/bin/env python3
"""rani_llm_test.py -- Test Eve Unleashed RANI against a live local LLM.

Same AdversarialEngine battery as the GOSP integration, but the inference
backend is a real model (OmniCoder via the Rust gateway :18080) instead of
the deterministic parser — this exercises Eve Unleashed end to end and
records WHICH model answered every round (backend field).

Run on Windows (gateway + llama-server must be up):
    python scripts\\rani_llm_test.py [--model omnicoder] [--rounds 3] [--max-tokens 60]
"""
import argparse
import importlib.util
import json
import sys
import time
import urllib.request
from pathlib import Path

RANI_ENGINE = Path(r"C:\Users\clint\Desktop\EveUnleashed_Selector\agents\adversarial\engine.py")
OUT = Path.home() / "RANI_LLM_evidence.json"
GATEWAY = "http://127.0.0.1:18080/v1/chat/completions"


def llm_infer(prompt: str, model: str, max_tokens: int) -> str:
    """Local-LLM inference via the Rust gateway: prompt -> response text."""
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(
        GATEWAY, data=body, headers={"Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    msg = data["choices"][0].get("message") or {}
    think = (msg.get("reasoning_content") or "").strip()
    text = (msg.get("content") or "").strip()
    if think and not text:
        text = "[thinking-only] " + think[:300]
    return text or "[empty response]"


def main() -> int:
    ap = argparse.ArgumentParser(description="RANI battery vs live local LLM")
    ap.add_argument("--model", default="omnicoder")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=60)
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location("rani_engine", RANI_ENGINE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    t0 = time.time()
    engine = mod.AdversarialEngine(
        mod.AdversarialConfig(adversarial_rounds=args.rounds, recursion_depth=1))
    backend = f"{args.model}-via-gateway"
    engine.register_inference(
        lambda p: llm_infer(p, args.model, args.max_tokens), name=backend)

    probe = "Explain why the sky is blue in one sentence."
    rounds = engine.run_adversarial_battery(probe, num_rounds=args.rounds)
    sm = engine.get_summary()
    report = {
        "test": "RANI x live LLM",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "backend": backend,
        "model": args.model,
        "elapsed_s": round(time.time() - t0, 2),
        "engine_summary": {
            "total_rounds": sm.get("total_rounds"),
            "adversarial_detected": sm.get("adversarial_detected"),
            "avg_latency_ms": round(sm.get("avg_latency_ms", 0), 1),
            "avg_score": round(sm.get("avg_score", 0), 4),
        },
        "rounds": [{
            "round_id": r.round_id,
            "backend": r.backend,
            "prompt": r.prompt[:100],
            "score": round(r.score, 3),
            "critique": (r.critique or "")[:80],
            "adversarial_flag": r.adversarial_flag,
            "latency_ms": round(r.latency_ms, 1),
            "response_prefix": (r.response or "")[:200],
        } for r in rounds],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    print("=== RANI x live LLM ===")
    print(f"backend: {backend}  rounds: {len(rounds)}  "
          f"adv={sm.get('adversarial_detected')} avg_score={sm.get('avg_score', 0):.3f}")
    for r in report["rounds"]:
        print(f"  R{r['round_id']} backend={r['backend']} score={r['score']:.2f} "
              f"flag={r['adversarial_flag']} lat={r['latency_ms']:.0f}ms")
        print(f"      resp: {r['response_prefix'][:120]}")
    print(f"Evidence: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
