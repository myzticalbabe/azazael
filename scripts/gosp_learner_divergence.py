#!/usr/bin/env python3
"""
gosp_learner_divergence.py -- Force the 8 native-intel dimension weights to diverge

Feeds deliberately error-rich sentences, one set per analysis dimension
(scope ambiguities, presupposition violations, implicature triggers, thematic
role ambiguities, discourse shifts, focus/topic, modality), through
GossamerOxfordParser.parse(learn=True). Captures pre/post weights, measures
divergence (std across the 8 weights + biggest movers), then feeds real corpus
docs and reports final learner accuracy.

Run in WSL2 Ubuntu (gossamer lives there), python 3.14:
    python3 /mnt/c/Users/clint/azazael/scripts/gosp_learner_divergence.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, "/root/gossamer-oxford-parser")
from semantical_main import GossamerOxfordParser  # noqa: E402

OUT = "/mnt/c/Users/clint/GOSP_LEARNER_DIVERGENCE_evidence.json"
CORPUS = Path("/mnt/c/Users/clint")

# Error-rich sentences per dimension: each stresses a failure mode of that dimension
STIMULI = {
    "presupposition": [
        "The treasurer stopped misreporting the reserve fund.",
        "John realized the board had never approved the bonus.",
        "Why did the CFO continue hiding the deficit?",
    ],
    "implicature": [
        "Some of the officers attended the meeting.",
        "The CEO managed to avoid the audit committee.",
        "Either the chair or the treasurer signed the filing.",
    ],
    "scope_ambiguity": [
        "Every board member approved a compensation plan.",
        "The company did not file every required return.",
        "Each auditor reviewed some transactions twice.",
    ],
    "lexical_semantics": [
        "The custodian executed the reallocation order.",
        "The advisor liquidated the client's entire portfolio.",
        "The trustee transferred the donation to the reserve.",
    ],
    "thematic_roles": [
        "The fund was transferred by the custodian to the client.",
        "The client was charged excessive fees by the advisor.",
        "The donation benefited the executive's foundation.",
    ],
    "discourse_structure": [
        "First the filing was rejected. Then the appeal was withdrawn. The deadline passed.",
        "The board resigned. The agency intervened. Ultimately the grant was suspended.",
        "After the audit failed, the insurer denied the claim, and the clinic closed.",
    ],
    "focus_and_topic": [
        "It was the CFO who signed the disclosure.",
        "The compensation committee, not the full board, set the bonuses.",
        "What the regulator questioned was the investment income.",
    ],
    "modality_and_mood": [
        "The officer must have known about the transfer.",
        "The board should have approved the expenditure.",
        "If the custodian had reported the loss, the auditor would have acted.",
    ],
}


def corpus_acc(parser, limit: int = 8) -> list:
    accs = []
    n = 0
    for p in sorted(CORPUS.glob("*.html")):
        try:
            t = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace"))
            t = re.sub(r"\s+", " ", t).strip()
        except Exception:  # noqa: BLE001
            continue
        if 400 < len(t) < 6000:
            accs.append(parser.parse(t[:900], learn=True).get("accuracy_score", 0.0))
            n += 1
        if n >= limit:
            break
    return accs


def main() -> int:
    t0 = time.time()
    parser = GossamerOxfordParser(max_workers=4)
    w0 = dict(parser.native_intel.get_dimension_weights())
    per_dim = {}
    for dim, sents in STIMULI.items():
        parser.native_intel.reset_weights() if hasattr(parser.native_intel, "reset_weights") else None
        before = dict(parser.native_intel.get_dimension_weights())
        accs = []
        for s in sents:
            accs.append(parser.parse(s, learn=True).get("accuracy_score", 0.0))
        after = dict(parser.native_intel.get_dimension_weights())
        moved = {k: round(after[k] - before[k], 4) for k in before if after[k] != before[k]}
        per_dim[dim] = {
            "stimuli_acc": accs,
            "weights_before": before,
            "weights_after": after,
            "movers": moved,
        }

    w_end = dict(parser.native_intel.get_dimension_weights())
    import statistics

    # Feed the full stimulus set again plus corpus docs to see final state
    corpus_accs = corpus_acc(parser)
    learner = parser.learner.get_state()

    out = {
        "test": "GOSP learner divergence forcing",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "weights_uniform_start": w0,
        "per_dimension": per_dim,
        "weights_final": w_end,
        "weight_std_start": round(statistics.pstdev(list(w0.values())), 4),
        "weight_std_final": round(statistics.pstdev(list(w_end.values())), 4),
        "corpus_accuracy_after": [round(a, 4) for a in corpus_accs],
        "learner_final": learner,
        "elapsed_s": round(time.time() - t0, 2),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)

    print("=== GOSP weight divergence forcing ===")
    std0 = out["weight_std_start"]
    stdf = out["weight_std_final"]
    print(f"Weight std: {std0} -> {stdf}")
    movers = {}
    for dim, d in per_dim.items():
        for k, v in d["movers"].items():
            movers[k] = movers.get(k, 0.0) + v
    if movers:
        print("Cumulative movers:")
        for k, v in sorted(movers.items(), key=lambda kv: -abs(kv[1])):
            print(f"  {k}: {v:+.4f}")
    else:
        print("No dimension weights moved (learner converged before reweighting)")
    print(f"Learner: iter={learner.get('iteration')} acc={learner.get('current_accuracy')}")
    print(f"Evidence: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
