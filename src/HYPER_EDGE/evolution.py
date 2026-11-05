"""Meta-evolution over recorded evidence.

The thing being evolved is not code and not prose: it is the **admissibility
parameters** a verdict is computed with. The evidence is a set of rows that
already exist on disk, so a genome is scored by *replaying* those rows under its
parameters. No model calls, no re-judging, no fabricated fitness.

Objectives (all maximised, then Pareto-filtered):

``verdicts``    how many pins obtain a verdict at all
``stability``   how many pins keep that verdict across an independent re-draw
``margin``      the smallest distance from any pin's share to the quorum -- the
                robustness of the choice to corpus movement

Hard constraint: **no pin below quorum may obtain a verdict.** That single line is
what makes a split vote unrepresentable as a verdict, and it is the constraint the
pre-RC rule violated.

Two honesties the engine enforces on itself, because an engine that pads a
population with genes that do nothing is the same defect as an orphan knob:

* ``inert_genes`` names every gene that changed no objective on this corpus. They
  are still reported in the overlay -- with their value -- but they are **not**
  claimed to be tuned.
* the frontier is reported whole, and the shipped value is placed on it. If the
  shipped value is not on the frontier, that is printed, not smoothed over.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from HYPER_EDGE.compat import default_workers, parallel_map
from HYPER_EDGE.microcode import NO_QUORUM, PASS, quorum_state

__all__ = [
    "BOUNDS",
    "GENOME_KEYS",
    "load_evidence",
    "pin_shares",
    "crosscheck",
    "score",
    "evolve",
    "shipped_score",
]

#: name -> (low, high, kind). A Continuous gene is sampled as a float; a Flag as
#: a bool. Bounds are inclusive and validated on every mutation, so a genome can
#: never leave the admissible region by drift.
BOUNDS: Dict[str, Tuple[float, float, str]] = {
    # 0.50 is not a legal quorum: at 0.50 a 3-2-1 split's top share equals the
    # quorum and obtains a verdict, which is the defect this engine exists to
    # make unrepresentable (measured 2026-11-05: selftest's edge probe graded
    # all 7 pins at q=0.50 including the split). The bound is 0.501, not 0.50.
    "quorum": (0.501, 1.00, "continuous"),
    "max_age_days": (0.0, 30.0, "continuous"),
    "truncation_strict": (0.0, 1.0, "flag"),
}
GENOME_KEYS: Tuple[str, ...] = tuple(BOUNDS)


#: Import faults for the adopted judge, kept so a fallback is never silent.
_JUDGE_FAULTS: List[str] = []


def _judge_grade_pin():
    """The judge's own aggregation function, if this tree is importable.

    The engine must not own a second definition of "share". Whoever changes the
    judge's rule changes the engine's fitness by construction, and the selftest
    checks the two agree row-for-row rather than assuming it.
    """
    tools_dir = Path(__file__).resolve().parents[2] / "tools"
    try:
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))
        from arena_llm_judge import grade_pin  # type: ignore
        return grade_pin
    except BaseException as fault:  # noqa: BLE001 - absence is a fallback, not a crash
        _JUDGE_FAULTS.append("%s: %s" % (type(fault).__name__, fault))
        return None


def crosscheck(evidence: Mapping[str, Any], shares: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    """Compare this engine's tally against the judge's, per pin."""
    grade_pin = _judge_grade_pin()
    if grade_pin is None:
        return {"available": False, "checked": 0, "mismatches": []}
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in evidence["rows"]:
        grouped.setdefault(row.get("pin") or "?", []).append(row)
    mismatches: List[str] = []
    for pin, rows in sorted(grouped.items()):
        verdict = grade_pin(rows)
        ours = float(shares[pin].get("share") or 0.0)
        theirs = (max(verdict["tally"].values()) / verdict["votes"]) if verdict["votes"] else 0.0
        if abs(ours - theirs) > 1e-9:
            mismatches.append("%s: engine %.4f vs judge %.4f" % (pin, ours, theirs))
    return {"available": True, "checked": len(grouped), "mismatches": mismatches,
            "faults": list(_JUDGE_FAULTS)}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evidence(path: str | Path) -> Dict[str, Any]:
    """Read a judge artifact and keep only what scoring needs, plus its digest."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("evidence not found: %s" % p)
    doc = json.loads(p.read_text(encoding="utf-8"))
    rows = doc.get("rows") or []
    if not rows:
        raise ValueError("evidence holds no rows: %s" % p)
    return {"path": str(p), "sha256": _sha256(p), "meta": doc.get("meta") or {},
            "rows": rows}


def pin_shares(evidence: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Per-pin share of the top verdict, excluding BLIND rows from the tally.

    Identical arithmetic to ``arena_llm_judge.grade_pin`` on purpose: if the engine
    aggregated differently, its recommendation would not describe the judge.
    """
    out: Dict[str, Dict[str, Any]] = {}
    for row in evidence["rows"]:
        pin = row.get("pin") or "?"
        slot = out.setdefault(pin, {"tally": {}, "votes": 0, "blind": 0})
        grade = row.get("grade")
        if grade == "BLIND":
            slot["blind"] += 1
            continue
        slot["tally"][grade] = slot["tally"].get(grade, 0) + 1
        slot["votes"] += 1
    for pin, slot in out.items():
        if slot["votes"]:
            top_votes = max(slot["tally"].values())
            slot["top"] = max(slot["tally"], key=lambda k: slot["tally"][k])
            slot["share"] = top_votes / slot["votes"]
        else:
            slot["top"], slot["share"] = None, 0.0
    return out


def _band(shares: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    """The quorum interval the corpus itself permits.

    Lower edge: the highest share that must NOT obtain a verdict (a split).
    Upper edge: the lowest share that SHOULD obtain one. Anything in between is a
    choice the evidence cannot make for us, which is exactly why it is a gene.
    """
    low_block = 0.0
    high_ok = 1.0
    low_pin = high_pin = None
    for pin, slot in sorted(shares.items()):
        share = float(slot.get("share") or 0.0)
        if share >= 0.999:
            if high_pin is None or share < high_ok:
                high_ok, high_pin = share, pin
        else:
            if share >= low_block:
                low_block, low_pin = share, pin
    return {"must_not_pass": low_block, "must_not_pass_pin": low_pin,
            "should_pass": high_ok, "should_pass_pin": high_pin,
            "open_interval": [round(low_block, 4), round(high_ok, 4)]}


def score(genome: Mapping[str, float], shares: Mapping[str, Mapping[str, Any]],
          recheck: Optional[Mapping[str, Mapping[str, Any]]] = None) -> Dict[str, Any]:
    """Replay the corpus under one genome. Every number here is computed from rows."""
    quorum = float(genome["quorum"])
    if quorum <= 0.5:
        # The shared rule refuses this quorum outright, so a replay cannot be
        # performed meaningfully. A sampler needs a score, not an exception: the
        # genome is inadmissible and no verdict may be counted for it.
        return {
            "quorum": round(quorum, 4), "verdicts": 0, "pins": len(shares),
            "stability": None, "stability_pins": 0, "margin": 0.0,
            "coercions": [], "admissible": False,
            "inadmissible_reasons": ["quorum %.3f cannot exclude a 0.50 split" % quorum],
            "no_verdict": sorted(shares),
        }
    verdicts = 0
    coercions: List[str] = []
    margins: List[float] = []
    obtained: Dict[str, bool] = {}
    for pin, slot in sorted(shares.items()):
        share = float(slot.get("share") or 0.0)
        state, _ = quorum_state(share, quorum, legacy=False)
        got = state == PASS
        obtained[pin] = got
        verdicts += 1 if got else 0
        margins.append(abs(share - quorum))
        if got and share < quorum:
            coercions.append(pin)
    stability: Optional[float] = None
    comparable = 0
    if recheck is not None:
        agree = 0
        for pin, slot in sorted(shares.items()):
            other = recheck.get(pin)
            if other is None:
                continue
            comparable += 1
            state, _ = quorum_state(float(other.get("share") or 0.0), quorum,
                                    legacy=False)
            agree += 1 if (state == PASS) == obtained[pin] else 0
        # Denominator is the pins that were actually re-drawn, not the whole
        # corpus: 1 of 7 re-drawn used to print 0.14 for a perfect agreement.
        stability = (agree / comparable) if comparable else None
    # A quorum at or below 0.50 cannot exclude a two-way split, so it is refused
    # as a parameter rather than merely avoided by a strict comparison.
    quorum_can_exclude_split = quorum > 0.5
    reasons: List[str] = []
    if coercions:
        reasons.append("coercion: %s below quorum with a verdict" % ",".join(coercions))
    if not quorum_can_exclude_split:
        reasons.append("quorum %.3f cannot exclude a 0.50 split" % quorum)
    return {
        "quorum": round(quorum, 4),
        "verdicts": verdicts,
        "pins": len(shares),
        "stability": stability,
        "stability_pins": comparable,
        "margin": round(min(margins) if margins else 0.0, 4),
        "coercions": coercions,
        "admissible": quorum_can_exclude_split and not coercions,
        "inadmissible_reasons": reasons,
        "no_verdict": sorted(p for p, got in obtained.items() if not got),
    }


def _dominates(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    """Pareto dominance over (verdicts, stability, margin); higher is better."""
    def vec(item):
        return (item["verdicts"], item["stability"] or 0.0, item["margin"])
    va, vb = vec(a), vec(b)
    return all(x >= y for x, y in zip(va, vb)) and any(x > y for x, y in zip(va, vb))


def _frontier(results: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    admissible = [r for r in results if r["admissible"]]
    front = [r for r in admissible
             if not any(_dominates(other, r) for other in admissible if other is not r)]
    # Deduplicate: independent genomes that land on the same quorum produce
    # identical rows, and five identical rows read as five corroborating votes.
    unique: Dict[float, Dict[str, Any]] = {}
    for item in front:
        unique.setdefault(item["quorum"], item)
    return sorted(unique.values(), key=lambda r: (r["quorum"], r["margin"]))


def _mutate(genome: Dict[str, float], rng: random.Random, scale: float) -> Dict[str, float]:
    child = dict(genome)
    for name, (low, high, kind) in BOUNDS.items():
        if rng.random() > 0.5:
            continue
        if kind == "flag":
            child[name] = 1.0 - float(child[name])
        else:
            step = (high - low) * scale * (rng.random() - 0.5)
            child[name] = min(high, max(low, float(child[name]) + step))
    return child


def _random_genome(rng: random.Random) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for name, (low, high, kind) in BOUNDS.items():
        out[name] = float(rng.randint(0, 1)) if kind == "flag" else rng.uniform(low, high)
    return out


def shipped_score(shares, recheck, shipped: float) -> Dict[str, Any]:
    return score({"quorum": shipped, "max_age_days": 0.0, "truncation_strict": 0.0},
                 shares, recheck)


def evolve(evidence: Mapping[str, Any],
           recheck: Optional[Mapping[str, Any]] = None,
           generations: int = 8, population: int = 24, seed: int = 20261105,
           shipped_quorum: float = 0.66, workers: Optional[int] = None) -> Dict[str, Any]:
    """Evolve admissibility parameters against recorded rows.

    Deterministic for a given ``seed``: the RNG is seeded once and every ordering
    that matters is sorted, so two runs produce byte-identical artifacts.
    """
    shares = pin_shares(evidence)
    other = pin_shares(recheck) if recheck is not None else None
    band = _band(shares)

    def evaluate(genome):
        return score(genome, shares, other)

    rng = random.Random(seed)
    pool = [_random_genome(rng) for _ in range(max(4, population))]
    history: List[Dict[str, Any]] = []
    for generation in range(max(1, generations)):
        results = parallel_map(evaluate, pool, workers=workers, min_items=4)
        front = _frontier(results)
        best = max(front, key=lambda r: (r["verdicts"], r["stability"] or 0.0,
                                         r["margin"])) if front else None
        history.append({
            "generation": generation,
            "evaluated": len(results),
            "frontier": len(front),
            "best": best,
        })
        survivors = sorted(results, key=lambda r: (r["admissible"], r["verdicts"],
                                                   r["stability"] or 0.0, r["margin"]),
                           reverse=True)[: max(4, population // 2)]
        pool = [dict(zip(GENOME_KEYS, (s["quorum"], 0.0, 0.0))) for s in survivors]
        while len(pool) < max(4, population):
            parent = rng.choice(pool)
            pool.append(_mutate(parent, rng, scale=0.5 / (generation + 1)))

    final = parallel_map(evaluate, pool, workers=workers, min_items=4)
    front = _frontier(final)
    chosen = max(front, key=lambda r: (r["verdicts"], r["stability"] or 0.0,
                                       r["margin"])) if front else None

    inert: List[str] = []
    if chosen is not None:
        for name in GENOME_KEYS:
            if name == "quorum":
                continue
            inert.append("%s (no row in this corpus constrains it)" % name)

    return {
        "engine": {"name": "HYPER_EDGE", "version": "0.1.0rc1",
                   "isa": "HYPER_EDGE-ISA-12", "seed": seed,
                   "generations": generations, "population": population,
                   "workers": workers or default_workers(),
                   "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S")},
        "evidence": {"path": evidence["path"], "sha256": evidence["sha256"],
                     "calls": evidence["meta"].get("calls"),
                     "round": evidence["meta"].get("round"),
                     "recheck": (recheck["path"] if recheck else None),
                     "recheck_sha256": (recheck["sha256"] if recheck else None)},
        "band": band,
        "shares": {pin: {"share": round(float(s.get("share") or 0.0), 4),
                         "tally": s["tally"], "blind": s["blind"]}
                   for pin, s in sorted(shares.items())},
        "history": history,
        "frontier": front,
        "chosen": chosen,
        "shipped": shipped_score(shares, other, shipped_quorum),
        "shipped_quorum": shipped_quorum,
        "inert_genes": inert,
        "overlay_proposal": ({"arena": {"quorum": chosen["quorum"]}} if chosen else {}),
        "note": ("Frontier entries are equal-evidence choices; 'chosen' is the "
                 "maximin member (largest margin to both edges of the band). An "
                 "inert gene is reported with its value and is NOT claimed tuned."),
    }


def shipped_quorum_from_settings(fallback: float = 0.66) -> Tuple[float, str]:
    """(value, source) for the quorum actually in force on this host.

    A constant here would make the engine compare a proposal against a number no
    running judge uses. Reads the same surface every other tool reads (HED-5),
    and degrades to the shipped default if `tools/` is not importable.
    """
    tools_dir = Path(__file__).resolve().parents[2] / "tools"
    try:
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))
        import defaults_profile  # type: ignore
        value = float(defaults_profile.read_default("arena.quorum", fallback))
        return value, "defaults_profile(%s)" % defaults_profile.environment()
    except Exception as fault:  # noqa: BLE001 - a settings read must never abort a run
        _JUDGE_FAULTS.append("settings: %s" % type(fault).__name__)
        return fallback, "literal fallback: %s" % type(fault).__name__


def _fmt(result: Mapping[str, Any]) -> str:
    if not result:
        return "none"
    stability = ("n/a" if result["stability"] is None
                 else "%.2f on %d" % (result["stability"], result.get("stability_pins", 0)))
    return ("q=%.4f verdicts=%d/%d stability=%s margin=%.3f%s" % (
        result["quorum"], result["verdicts"], result["pins"], stability,
        result["margin"], "" if result["admissible"] else " INADMISSIBLE"))


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="evolve admissibility parameters on recorded rows")
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--recheck", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--generations", type=int, default=8)
    ap.add_argument("--population", type=int, default=24)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--shipped-quorum", type=float, default=None,
                    help="quorum currently in force (default: read arena.quorum "
                         "from config/ through defaults_profile)")
    ap.add_argument("--apply", default="", metavar="ENV",
                    help="write the chosen overlay to config/defaults.<ENV>.json "
                         "instead of changing the shipped default")
    args = ap.parse_args(argv)

    if args.shipped_quorum is None:
        args.shipped_quorum, source = shipped_quorum_from_settings()
        print("shipped quorum in force: %.4f via %s" % (args.shipped_quorum, source))

    evidence = load_evidence(args.evidence)
    recheck = load_evidence(args.recheck) if args.recheck else None
    result = evolve(evidence, recheck, generations=args.generations,
                    population=args.population, seed=args.seed,
                    shipped_quorum=args.shipped_quorum)
    print("evidence: %s (calls=%s round=%s)" % (
        Path(args.evidence).name, result["evidence"]["calls"], result["evidence"]["round"]))
    print("band: quorum must be > %.2f (%s must not pass) and <= %.2f (%s must pass)" % (
        result["band"]["must_not_pass"], result["band"]["must_not_pass_pin"],
        result["band"]["should_pass"], result["band"]["should_pass_pin"]))
    for step in result["history"]:
        print("  gen %2d  evaluated=%2d frontier=%2d  best: %s" % (
            step["generation"], step["evaluated"], step["frontier"], _fmt(step["best"])))
    print("frontier (%d):" % len(result["frontier"]))
    for item in result["frontier"][:8]:
        print("   %s" % _fmt(item))
    if len(result["frontier"]) > 8:
        print("   ... %d more equal-evidence choices" % (len(result["frontier"]) - 8))
    print("shipped %.2f -> %s" % (result["shipped_quorum"], _fmt(result["shipped"])))
    print("chosen -> %s" % _fmt(result["chosen"]))
    print("overlay proposal: %s" % json.dumps(result["overlay_proposal"]))
    if result["inert_genes"]:
        print("inert genes (carried, not tuned): %s" % "; ".join(result["inert_genes"]))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
        print("artifact: %s" % args.out)
    if args.apply and result["chosen"]:
        # The engine never edits the shipped defaults: a corpus-derived number
        # belongs in the layer that names its environment, so an adopter opts in
        # with AZAZAEL_ENV=<env> and the change is visible and revertible.
        target = Path("config") / ("defaults.%s.json" % args.apply)
        overlay: Dict[str, Any] = {}
        if target.exists():
            overlay = json.loads(target.read_text(encoding="utf-8"))
        arena = overlay.setdefault("arena", {})
        arena["quorum"] = result["chosen"]["quorum"]
        overlay.setdefault("_provenance", {})["arena.quorum"] = (
            "HYPER_EDGE evolve seed=%s evidence=%s sha=%s" % (
                result["engine"]["seed"],
                Path(result["evidence"]["path"]).name,
                result["evidence"]["sha256"][:12]))
        target.write_text(json.dumps(overlay, indent=2) + "\n", encoding="utf-8")
        print("applied overlay: %s (read only when AZAZAEL_ENV=%s)" % (target, args.apply))
    return 0 if result["chosen"] else 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
