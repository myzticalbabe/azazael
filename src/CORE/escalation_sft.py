# coding: utf-8
"""escalation_sft.py — consume the cascade ledger into SFT pairs.

Reads cascade_corrections.jsonl rows {task, triage_answer, big_answer},
emits instruction/response pairs + quality stats. The trainer (overnight
LoRA) consumes pairs.jsonl; this module is the verified daytime half.
"""
import json


def consume(ledger_path: str, out_path: str = "") -> dict:
    pairs, skipped = [], 0
    try:
        lines = open(ledger_path, encoding="utf-8").read().splitlines()
    except Exception:
        return {"pairs": 0, "skipped": 0, "error": "ledger-unreadable"}
    for line in lines:
        try:
            r = json.loads(line)
        except Exception:
            skipped += 1
            continue
        task, big = (r.get("task") or "").strip(), (r.get("big_answer") or "").strip()
        if not task or not big or big == (r.get("triage_answer") or "").strip():
            skipped += 1
            continue
        pairs.append({"instruction": task[:1000], "response": big[:2000],
                      "confidence": r.get("confidence", 0.0)})
    if out_path and pairs:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(pairs, fh, indent=1)
    lens = [len(p["instruction"]) + len(p["response"]) for p in pairs]
    return {"pairs": len(pairs), "skipped": skipped,
            "mean_len": round(sum(lens) / max(1, len(lens)), 1),
            "out": out_path if out_path and pairs else ""}
