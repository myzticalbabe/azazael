"""Memory retrieval/utilization diagnostic (2026-09-29, pure, stdlib only).

ICLR'26 finding: retrieval method drives 14–23 pts, write strategy 3–8.
So the first question on any memory miss is retrieval-vs-utilization,
not "store more". Two pure helpers, no store access, no model calls:

* ``fit_budget`` — token-budget trim (not top-k): pack items until the
  budget is spent so retrieved context fits the downstream window.
* ``classify_failure`` — retrieval failure (nothing relevant surfaced)
  vs utilization failure (relevant retrieved, answer still wrong) vs
  hallucination (answered without retrieval).
"""
from __future__ import annotations


def fit_budget(items: list[dict], budget: int,
               size_of=None) -> list[dict]:
    """Pack items in order until ``budget`` is spent. Never raises."""
    try:
        budget = max(0, int(budget))
    except (TypeError, ValueError):
        return list(items or [])
    if size_of is None:
        def size_of(it):
            try:
                return len(str(it.get("text", it)))
            except Exception:
                return 0
    out = []
    spent = 0
    for it in items or []:
        try:
            cost = int(size_of(it))
        except Exception:
            cost = 0
        if spent + cost > budget and out:
            break
        out.append(it)
        spent += cost
    return out


def classify_failure(retrieved_relevant: bool, answered: bool,
                     answer_correct: bool) -> str:
    """One of retrieval_failure / utilization_failure / hallucination / ok.

    * no relevant retrieved → retrieval_failure (fix retrieval, not writes)
    * relevant retrieved + wrong/missing answer → utilization_failure
    * answered with nothing retrieved → hallucination risk path
    * otherwise ok.
    """
    if not retrieved_relevant:
        return "retrieval_failure" if not answer_correct else "hallucination"
    if answered and not answer_correct:
        return "utilization_failure"
    if not answered:
        return "utilization_failure"
    return "ok"
