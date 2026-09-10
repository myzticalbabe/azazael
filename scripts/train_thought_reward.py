"""train_thought_reward.py — gradient consumer for the thought corpus.

The loop's first learned weights over reasoning: TF-IDF-ish hashed
unigram features from (task + reasoning) text, logistic regression by
hand-rolled SGD (stdlib only, no sklearn dependency to rot). Labels are
the traces' own success flags. Artifact: state/thought_reward_model.json
{weights, bias, trained_at, n_pos, n_neg, loo_accuracy}.

Honest limits: ~35 traces, heavily success-skewed — class-balanced
sample weights compensate, and leave-one-out accuracy is reported, not
hidden. This scores reasoning patterns; it does not fine-tune any LLM.

Usage:
    python scripts/train_thought_reward.py            # train + report
    python scripts/train_thought_reward.py --score "some reasoning text"
"""
import sys
import json
import math
import re
import time
from hashlib import md5
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

DIM = 4096
EPOCHS = 300
LR = 0.1
MODEL_PATH = (Path(__file__).resolve().parent.parent / "state"
              / "thought_reward_model.json")

_TOKEN = re.compile(r"[a-z]{3,}")


def featurize(task: str, reasoning: str) -> dict:
    counts: dict = {}
    for tok in _TOKEN.findall(("%s %s" % (task, reasoning)).lower()):
        counts[int(md5(tok.encode()).hexdigest()[:8], 16) % DIM] = \
            counts.get(int(md5(tok.encode()).hexdigest()[:8], 16) % DIM, 0) + 1
    norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
    return {k: v / norm for k, v in counts.items()}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, x))))


def load_corpus():
    from CORE.local_memory import get_memory_store
    rows = get_memory_store().query_memories(event_type="thought_process",
                                             limit=2000)
    data = []
    for r in rows:
        d = r.get("data", {})
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                continue
        if not isinstance(d, dict) or "success" not in d:
            continue
        txt_task = str(d.get("task", ""))
        txt_reas = str(d.get("reasoning", ""))
        if not (txt_task or txt_reas):
            continue
        data.append((txt_task, txt_reas, bool(d.get("success"))))
    return data


def train(data, epochs: int = EPOCHS, lr: float = LR):
    n_pos = sum(1 for _, _, y in data if y)
    n_neg = len(data) - n_pos
    w_pos = len(data) / (2.0 * max(n_pos, 1))
    w_neg = len(data) / (2.0 * max(n_neg, 1))
    feats = [(featurize(t, r), y) for t, r, y in data]
    w = [0.0] * DIM
    b = 0.0
    for _ in range(epochs):
        for x, y in feats:
            p = _sigmoid(sum(w[k] * v for k, v in x.items()) + b)
            err = (p - (1.0 if y else 0.0)) * (w_pos if y else w_neg)
            for k, v in x.items():
                w[k] -= lr * err * v
            b -= lr * err
    return w, b


def loo_accuracy(data) -> float:
    if len(data) < 4:
        return 0.0
    hits = 0
    for i in range(len(data)):
        rest = data[:i] + data[i + 1:]
        w, b = train(rest, epochs=150)
        t, r, y = data[i]
        p = _sigmoid(sum(w[k] * v for k, v in featurize(t, r).items()) + b)
        if (p >= 0.5) == y:
            hits += 1
    return round(hits / len(data), 3)


def score_text(text: str, model: dict) -> float:
    w, b = model["weights"], model["bias"]
    x = featurize("", text)
    return round(_sigmoid(sum(w[k] * v for k, v in x.items()) + b), 4)


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--score":
        model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
        print(score_text(" ".join(sys.argv[2:]), model))
        return 0
    data = load_corpus()
    print("corpus: %d traces (%d ok / %d fail)" % (
        len(data), sum(1 for _, _, y in data if y),
        sum(1 for _, _, y in data if not y)))
    if len(data) < 6:
        print("too few traces to train")
        return 1
    t0 = time.time()
    w, b = train(data)
    loo = loo_accuracy(data)
    pos = [t for t, _, y in data if y][:2]
    _ = pos
    model = {"weights": [round(v, 6) for v in w], "bias": round(b, 6),
             "dim": DIM, "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
             "n_pos": sum(1 for _, _, y in data if y),
             "n_neg": sum(1 for _, _, y in data if not y),
             "loo_accuracy": loo,
             "train_seconds": round(time.time() - t0, 1)}
    tmp = MODEL_PATH.with_suffix(".json.tmp")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(model), encoding="utf-8")
    tmp.replace(MODEL_PATH)
    print("loo_accuracy=%.3f baseline=%.3f" % (
        loo, max(model["n_pos"], model["n_neg"]) / len(data)))
    print("wrote %s (%d weights)" % (MODEL_PATH, DIM))
    # Sanity: known fail traces should score below known successes.
    fails = [(t, r) for t, r, y in data if not y]
    oks = [(t, r) for t, r, y in data if y]
    if fails and oks:
        import statistics as _st
        fs = [score_text(t + " " + r, model) for t, r in fails]
        os_ = [score_text(t + " " + r, model) for t, r in oks]
        print("fail-mean=%.3f ok-mean=%.3f" % (_st.mean(fs), _st.mean(os_)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
