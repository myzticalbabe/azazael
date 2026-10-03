# coding: utf-8
"""cascade.py — 1.5B triage -> 9B escalation router.

Cheap model answers first with a confidence; escalate only when confidence
is below threshold (tuned by OOF ECE: default 0.65). Tracks savings.
"""


class CascadeRouter:
    """triage_fn(task) -> (answer, confidence). big_fn(task) -> answer.

    ledger_path: every escalation appends {task, triage_answer, confidence,
    big_answer} JSONL — the future SFT corpus. Non-escalations are not
    logged (nothing to learn).
    """

    VERSION = "1.1.0"

    def __init__(self, threshold: float = 0.65, ledger_path: str = ""):
        self.threshold = float(threshold)
        self.ledger_path = ledger_path
        self.n_triage = 0
        self.n_escalated = 0

    def _log_escalation(self, task, triage_ans, conf, big_ans):
        if not self.ledger_path:
            return
        try:
            import json as _json
            import datetime as _dt
            row = {"ts": _dt.datetime.now().isoformat(),
                   "task": str(task)[:2000],
                   "triage_answer": str(triage_ans)[:2000],
                   "confidence": float(conf), "big_answer": str(big_ans)[:2000]}
            with open(self.ledger_path, "a", encoding="utf-8") as fh:
                fh.write(_json.dumps(row) + "\n")
        except Exception:
            pass

    def route(self, task, triage_fn, big_fn) -> dict:
        ans, conf = triage_fn(task)
        self.n_triage += 1
        if conf is None:
            conf = 0.0
        if float(conf) >= self.threshold:
            return {"answer": ans, "via": "triage", "confidence": float(conf),
                    "escalated": False}
        big = big_fn(task)
        self.n_escalated += 1
        self._log_escalation(task, ans, conf, big)
        return {"answer": big, "via": "big", "confidence": float(conf),
                "escalated": True, "triage_answer": ans}

    def stats(self) -> dict:
        tot = max(1, self.n_triage)
        return {"triaged": self.n_triage, "escalated": self.n_escalated,
                "escalation_rate": self.n_escalated / tot,
                "saved_ratio": 1.0 - self.n_escalated / tot}
