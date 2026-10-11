#!/usr/bin/env python3
"""
gosp_learner_train.py -- Train GOSP's RecursiveLearner over the root corpus docs

Feeds real corpus documents through GossamerOxfordParser.parse(learn=True) so the
RecursiveLearner converges the 8 native-intelligence dimension weights. Captures
pre/post learner state + per-epoch accuracy for evidence.

Run inside WSL2 Ubuntu (gossamer lives there), python 3.14:
    python3 /mnt/c/Users/clint/azazael/scripts/gosp_learner_train.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "/root/gossamer-oxford-parser")
from semantical_main import GossamerOxfordParser  # noqa: E402

OUT = "/mnt/c/Users/clint/GOSP_LEARNER_TRAIN_evidence.json"
CORPUS = Path("/mnt/c/Users/clint")


def corpus_texts(limit: int = 25) -> list:
    texts = []
    for p in sorted(CORPUS.glob("*.html")):
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        t = re.sub(r"<[^>]+>", " ", raw)
        t = re.sub(r"\s+", " ", t).strip()
        if 300 < len(t) < 8000:
            texts.append({"file": p.name, "text": t})
        if len(texts) >= limit:
            break
    for p in sorted(CORPUS.glob("*.md")):
        try:
            t = re.sub(r"\s+", " ", p.read_text(encoding="utf-8", errors="replace")).strip()
        except Exception:  # noqa: BLE001
            continue
        if 300 < len(t) < 8000:
            texts.append({"file": p.name, "text": t})
        if len(texts) >= limit:
            break
    return texts


def main() -> int:
    t0 = time.time()
    parser = GossamerOxfordParser(max_workers=4)
    docs = corpus_texts()
    before = parser.learner.get_state()
    weights_before = dict(parser.native_intel.get_dimension_weights())
    epochs = []
    for i, d in enumerate(docs):
        snippet = d["text"][:900]
        try:
            res = parser.parse(snippet, depth="full", learn=True)
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}] {d['file']} ERROR {e}")
            continue
        state = parser.learner.get_state()
        epochs.append(
            {
                "doc": d["file"],
                "accuracy": round(res.get("accuracy_score", 0.0), 4),
                "iterations": state.get("iterations", 0),
            }
        )
        if i % 5 == 0:
            print(f"  [{i}] {d['file']} acc={epochs[-1]['accuracy']}")

    after = parser.learner.get_state()
    weights_after = dict(parser.native_intel.get_dimension_weights())
    out = {
        "test": "GOSP RecursiveLearner training over real corpus docs",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "docs_fed": len(epochs),
        "elapsed_s": round(time.time() - t0, 2),
        "learner_state_before": before,
        "learner_state_after": after,
        "native_intel_weights_before": weights_before,
        "native_intel_weights_after": weights_after,
        "per_doc": epochs,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)

    print("=== GOSP learner training evidence ===")
    print(f"Docs fed: {len(epochs)} in {out['elapsed_s']}s")
    print(f"Learner: iterations={after.get('iteration')} converged={after.get('converged')} "
          f"acc={after.get('current_accuracy')}")
    print(f"Parses learned from: {after.get('total_parses_learned_from')}")
    print("Dimension weights (before -> after):")
    for k in weights_before:
        print(f"  {k}: {weights_before[k]:.4f} -> {weights_after.get(k, 0):.4f}")
    print(f"Evidence: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
