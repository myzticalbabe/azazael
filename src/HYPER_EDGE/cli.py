"""HYPER_EDGE command line: isa | evolve | selftest.

``selftest`` is the point of the package. An instrument that has never been made
to fail is a hypothesis, so every one of the twelve ops is exercised with a
reading it MUST refuse, and the legacy/RC difference is proved on a split vote
rather than described in a changelog. Exit codes: 0 every check ran and passed,
1 a check failed, 2 a check could not be performed (which is not a pass).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

from HYPER_EDGE import microcode
from HYPER_EDGE.compat import capabilities, parallel_map, report as compat_report
from HYPER_EDGE import evolution

__all__ = ["main", "selftest"]

GOOD: Dict[str, Any] = {
    "tier": "A",
    "quote_grounded": True,
    "population_claim": True,
    "n": 33,
    "m": 66,
    "negative": True,
    "universe": ["UJS", "IRS"],
    "share": 0.90,
    "instrument_answered": True,
    "truncation_class": "labelled",
    "verdict_adjacent": True,
    "command": "tools/foo.py --check",
    "digest": "EXIT=0 OK",
    "age_days": 0.5,
    "draws": 2,
    "reproduced": True,
    "knob": "arena.quorum",
    "knob_readers": 1,
    "enabled": True,
}


def _reading(**overrides: Any) -> Dict[str, Any]:
    record = dict(GOOD)
    record.update(overrides)
    return record


#: one negative control per op: (code, overrides, state the op must return, context)
CONTROLS: Tuple[Tuple[str, Dict[str, Any], str, Dict[str, Any]], ...] = (
    ("0x01", {"tier": "D"}, microcode.LEAD, {}),
    ("0x02", {"quote_grounded": False}, microcode.CUT, {}),
    ("0x03", {"n": None}, microcode.CUT, {}),
    ("0x04", {"universe": []}, microcode.CUT, {}),
    ("0x05", {"share": 0.50}, microcode.NO_QUORUM, {}),
    ("0x06", {"instrument_answered": False}, microcode.BLIND, {}),
    ("0x07", {"truncation_class": "silent", "verdict_adjacent": True}, microcode.CUT, {}),
    ("0x08", {"command": ""}, microcode.CUT, {}),
    # the staleness op is off at limit 0 by design (recorded, not enforced), so its
    # control must supply a live limit -- otherwise the control tests nothing.
    ("0x09", {"age_days": 9.0}, microcode.CUT, {"max_age_days": 1.0}),
    ("0x0A", {"reproduced": False}, microcode.LEAD, {}),
    ("0x0B", {"knob_readers": 0}, microcode.CUT, {}),
    ("0x0C", {"enabled": False}, microcode.BLIND, {}),
)


class Checks:
    def __init__(self) -> None:
        self.rows: List[Tuple[str, str, str]] = []

    def check(self, name: str, ok: Optional[bool], detail: str) -> None:
        state = "SKIPPED" if ok is None else ("PASS" if ok else "FAIL")
        self.rows.append((state, name, detail))
        print("  [%-7s] %-34s %s" % (state, name, detail))

    def failed(self) -> int:
        return sum(1 for state, _, _ in self.rows if state == "FAIL")

    def skipped(self) -> int:
        return sum(1 for state, _, _ in self.rows if state == "SKIPPED")


def selftest(evidence: str = "", recheck: str = "") -> int:
    checks = Checks()
    print(compat_report())
    caps = capabilities()
    checks.check("compat probes", caps["probe_faults"] == 0,
                 "%s, %d probe fault(s)" % (caps["threading_mode"], caps["probe_faults"]))

    codes = [op.code for op in microcode.ISA]
    checks.check("isa has 12 unique ops", len(codes) == 12 and len(set(codes)) == 12,
                 "%d ops, %d unique" % (len(codes), len(set(codes))))
    table = microcode.isa_table()
    checks.check("every op carries its legacy behaviour",
                 all(row["legacy"] for row in table),
                 "%d/%d documented" % (sum(1 for r in table if r["legacy"]), len(table)))

    base = microcode.evaluate(_reading(quorum=0.66))
    checks.check("a complete reading reaches VERIFIED", base["rung"] == "VERIFIED",
                 "rung=%s" % base["rung"])

    by_code = {op.code: op for op in microcode.ISA}
    for code, overrides, expected, ctx in CONTROLS:
        result = microcode.evaluate(_reading(**overrides), **ctx)
        op = by_code[code]
        got = result["states"][code]
        checks.check("%s %s refuses" % (code, op.name), got == expected,
                     "%s on the control, rung=%s" % (got, result["rung"]))

    split = _reading(share=0.50)
    rc = microcode.evaluate(split)
    legacy = microcode.evaluate(split, legacy=True)
    checks.check("RC refuses a 0.50 split", rc["rung"] == "NO_QUORUM",
                 "rung=%s" % rc["rung"])
    # The precondition lives in the shared rule, so a caller cannot reach the
    # comparison with a threshold that a 3-2-1 split would meet.
    refused = "accepted"
    try:
        microcode.quorum_state(0.50, 0.50)
    except ValueError as fault:
        refused = "refused: %s" % fault
    checks.check("a quorum of 0.50 is refused at the rule", refused.startswith("refused"),
                 refused)
    checks.check("legacy mode reproduces the old coercion", legacy["rung"] == "VERIFIED",
                 "legacy rung=%s (the defect being migrated away from)" % legacy["rung"])

    serial = [len(text) for text in ("a", "bb", "ccc", "dddd", "eeeee", "ffffff")]
    pooled = parallel_map(lambda text: len(text), ("a", "bb", "ccc", "dddd", "eeeee", "ffffff"))
    checks.check("parallel_map preserves order", pooled == serial,
                 "%s workers=%d" % (pooled == serial, evolution.default_workers(caps)))

    path = evidence or "ARC/cain/arena_llm_judgments_r8.json"
    repath = recheck or "ARC/cain/arena_llm_judgments_r8_c4_recheck.json"
    try:
        ev = evolution.load_evidence(path)
        rc_ev = evolution.load_evidence(repath)
    except (FileNotFoundError, ValueError) as fault:
        checks.check("determinism on recorded evidence", None,
                     "cannot run: %s" % fault)
        ev = rc_ev = None
    if ev is not None and rc_ev is not None:
        first = evolution.evolve(ev, rc_ev, generations=3, population=8, seed=7)
        second = evolution.evolve(ev, rc_ev, generations=3, population=8, seed=7)
        checks.check("evolve is deterministic for a seed",
                     first["chosen"] == second["chosen"],
                     "chosen %s" % (first["chosen"] or {}).get("quorum"))
        shares = evolution.pin_shares(ev)
        band = first["band"]
        probe = evolution.score({"quorum": band["must_not_pass"],
                                 "max_age_days": 0.0, "truncation_strict": 0.0},
                                shares, evolution.pin_shares(rc_ev))
        checks.check("a quorum at the split edge is refused",
                     probe["admissible"] is False,
                     "q=%.3f verdicts=%d %s" % (probe["quorum"], probe["verdicts"],
                                                "; ".join(probe["inadmissible_reasons"])))
        checks.check("chosen genome is admissible",
                     bool(first["chosen"] and first["chosen"]["admissible"]),
                     "chosen q=%s" % (first["chosen"] or {}).get("quorum"))
        # Native adoption, proved rather than asserted: the engine's share must be
        # the judge's share, because both now resolve to the same rule.
        agree = evolution.crosscheck(ev, shares)
        checks.check("tally agrees with arena_llm_judge",
                     None if not agree["available"] else not agree["mismatches"],
                     ("%d pin(s), %d mismatch(es)%s" % (
                         agree["checked"], len(agree["mismatches"]),
                         (": " + "; ".join(agree["mismatches"])) if agree["mismatches"] else "")) if agree["available"] else "arena_llm_judge not importable")

    failed, skipped = checks.failed(), checks.skipped()
    print("selftest: %d check(s), %d failed, %d skipped" %
          (len(checks.rows), failed, skipped))
    if failed:
        return 1
    return 2 if skipped else 0


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="HYPER_EDGE", description=(
        "HYPER_EDGE rc1 -- admissibility microcode + meta-evolution over recorded rows"))
    ap.add_argument("--version", action="version", version="HYPER_EDGE 0.1.0rc1")
    sub = ap.add_subparsers(dest="command")

    isa = sub.add_parser("isa", help="print the twelve admissibility ops")
    isa.add_argument("--json", action="store_true")

    st = sub.add_parser("selftest", help="exercise every op with a reading it must refuse")
    st.add_argument("--evidence", default="")
    st.add_argument("--recheck", default="")

    ev = sub.add_parser("evolve", help="evolve admissibility parameters on recorded rows")
    ev.add_argument("--evidence", required=True)
    ev.add_argument("--recheck", default="")
    ev.add_argument("--out", default="")
    ev.add_argument("--generations", type=int, default=8)
    ev.add_argument("--population", type=int, default=24)
    ev.add_argument("--seed", type=int, default=20261105)
    ev.add_argument("--shipped-quorum", type=float, default=None,
                    help="default: read arena.quorum from the settings surface")
    ev.add_argument("--apply", default="", metavar="ENV",
                    help="write the chosen overlay to config/defaults.<ENV>.json")

    args = ap.parse_args(argv)
    if args.command == "isa":
        rows = microcode.isa_table()
        if args.json:
            print(json.dumps(rows, indent=1))
        else:
            for row in rows:
                print("%s %-11s %s" % (row["code"], row["name"], row["question"]))
        return 0
    if args.command == "selftest":
        return selftest(args.evidence, args.recheck)
    if args.command == "evolve":
        return evolution.main([
            "--evidence", args.evidence, "--recheck", args.recheck,
            "--out", args.out, "--generations", str(args.generations),
            "--population", str(args.population), "--seed", str(args.seed),
        ] + (["--shipped-quorum", str(args.shipped_quorum)]
             if args.shipped_quorum is not None else [])
          + (["--apply", args.apply] if args.apply else []))
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
