"""The admissibility ISA -- twelve ops, one per measurement this tree paid for.

Each op is a *predicate over a reading*, not a rule in prose. A reading is a flat
mapping; an op reads only the keys it declares and returns ``(state, reason)``
where state is one of:

``PASS``       the op's question was answered in the affirmative
``LEAD``       the reading is real but cannot carry a verdict (queue it)
``CUT``        the reading is hostile to admissibility and must not be used
``BLIND``      the instrument could not answer -- not the same as a zero
``NO_QUORUM``  the finders split below quorum -- the absence of a verdict
``SKIP``       the op does not apply to this reading (and says why)

Every op also carries ``legacy``: what the pre-RC code did. That column is the
backward-compatibility contract -- ``evaluate(..., legacy=True)`` reproduces the
old behaviour exactly, so a caller can be migrated by *proving the difference on
real rows* instead of trusting a changelog. Two of the twelve legacy behaviours
are defective on purpose (``0x05`` coerces a split into PARTIAL, ``0x0C`` treats a
disabled gate as a pass); they are kept because replaying them is how the defect is
demonstrated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

__all__ = ["ISA", "LADDER", "Op", "evaluate", "isa_table", "quorum_state", "rung"]

PASS = "PASS"
LEAD = "LEAD"
CUT = "CUT"
BLIND = "BLIND"
NO_QUORUM = "NO_QUORUM"
SKIP = "SKIP"

#: the verdict ladder: exclusive rungs, most severe first. A reading sits on one.
LADDER: Tuple[str, ...] = ("CUT", "BLIND", "NO_QUORUM", "LEAD", "PARTIAL", "VERIFIED")


@dataclass(frozen=True)
class Op:
    code: str
    name: str
    question: str
    keys: Tuple[str, ...]
    legacy: str
    fn: Callable[[Mapping[str, Any], Mapping[str, Any]], Tuple[str, str]]


def _present(record: Mapping[str, Any], key: str) -> bool:
    value = record.get(key)
    return value is not None and value != ""


def _tier(record, ctx):
    tier = str(record.get("tier") or "").upper()
    if tier in ("A", "B"):
        return PASS, "tier %s" % tier
    if tier == "C":
        return LEAD, "tier C corroborates an A or B; it cannot carry a fact alone"
    if tier == "D":
        return LEAD, "tier D is a pointer: queue it, never cite it"
    return CUT, "no tier declared: an untiered source cannot be weighed"


def _ground(record, ctx):
    if "quote_grounded" not in record:
        return SKIP, "no quotation exhibited"
    if record.get("quote_grounded") is True:
        return PASS, "quotation found in its cited capture"
    return CUT, "quotation not found in its source: no evidence, not weak evidence"


def _denom(record, ctx):
    if not record.get("population_claim"):
        return SKIP, "not a population claim"
    n, m = record.get("n"), record.get("m")
    if isinstance(n, int) and isinstance(m, int) and m > 0:
        return PASS, "%d/%d carry a denominator" % (n, m)
    return CUT, "population verdict with no usable denominator"


def _universe(record, ctx):
    if not record.get("negative"):
        return SKIP, "not a negative"
    universe = record.get("universe")
    if isinstance(universe, (list, tuple)) and len(universe) > 0:
        return PASS, "negative over %d named source(s)" % len(universe)
    return CUT, "universe-free negative: this is 'we did not search', not 'none exists'"


def quorum_state(share: float, quorum: float, legacy: bool = False) -> Tuple[str, str]:
    """The 0x05 decision, isolated so the engine and the judge share one rule.

    The precondition lives in the shared rule, not only in the engine's band: at a
    quorum of exactly 0.50 a 3-2-1 split's top share meets the threshold, so the
    split obtains a verdict. Refusing the quorum here means no caller can reach
    the comparison with a threshold that cannot exclude a split.
    """
    if float(quorum) <= 0.5:
        raise ValueError("quorum %.4f cannot exclude a 0.50 split; it must be > 0.50"
                         % float(quorum))
    if share >= quorum:
        return PASS, "share %.2f >= quorum %.2f" % (share, quorum)
    if legacy:
        # pre-RC: any PARTIAL in the tally was reported as a PARTIAL grade, with
        # the words "no quorum" printed beside it. A reader keeps the grade.
        return PASS, "legacy: split reported as PARTIAL (no quorum, %.2f)" % share
    return NO_QUORUM, "share %.2f < quorum %.2f: no verdict was obtained" % (share, quorum)


def _quorum(record, ctx):
    share = record.get("share")
    if share is None:
        return SKIP, "single finder, no share to aggregate"
    return quorum_state(float(share), float(ctx["quorum"]), bool(ctx["legacy"]))


def _blind(record, ctx):
    if record.get("instrument_answered") is False:
        return BLIND, "the instrument could not answer"
    return PASS, "instrument answered"


def _trunc(record, ctx):
    klass = str(record.get("truncation_class") or "").lower()
    if not klass:
        return SKIP, "no truncation reported on this path"
    if klass == "silent" and record.get("verdict_adjacent"):
        if ctx["legacy"]:
            return PASS, "legacy: silent cut in a verdict path went unclassified"
        return CUT, "silent cut feeding a verdict: the verdict is contaminated"
    return PASS, "%s cut is admissible on this path" % klass


def _provenance(record, ctx):
    command, digest = record.get("command"), record.get("digest")
    if command and digest:
        return PASS, "command + digest present"
    if ctx["legacy"]:
        return PASS, "legacy: a claim without a command was accepted"
    return CUT, "claim with no command/digest: indistinguishable from a recollection"


def _stale(record, ctx):
    age = record.get("age_days")
    if age is None:
        return SKIP, "no age declared"
    limit = float(ctx.get("max_age_days") or 0)
    if limit <= 0:
        return PASS, "staleness gate off (0): recorded, not enforced"
    if float(age) <= limit:
        return PASS, "%.1f day(s) old, limit %.1f" % (float(age), limit)
    return CUT, "artifact is %.1f day(s) old; it answers for a tree it no longer describes" % float(age)


def _repro(record, ctx):
    draws = record.get("draws")
    if not draws:
        return SKIP, "no re-draw recorded"
    if record.get("reproduced") is True:
        return PASS, "grade reproduced across %d draw(s)" % int(draws)
    return LEAD, "grade did not reproduce: quote the draws, not a verdict"


def _knob(record, ctx):
    knob = record.get("knob")
    if not knob:
        return SKIP, "no setting involved"
    readers = record.get("knob_readers")
    if isinstance(readers, int) and readers > 0:
        return PASS, "%s read by %d consumer(s)" % (knob, readers)
    return CUT, "%s is an orphan knob: declared, read by nothing" % knob


def _disabled(record, ctx):
    if "enabled" not in record:
        return SKIP, "not a gate state"
    if record.get("enabled") is True:
        return PASS, "gate enabled"
    if ctx["legacy"]:
        return PASS, "legacy: a disabled gate reported success"
    return BLIND, "gate disabled by config: exit 2, never a pass"


ISA: Tuple[Op, ...] = (
    Op("0x01", "TIER", "what weight can this source bear?", ("tier",),
       "any source was weighed the same", _tier),
    Op("0x02", "GROUND", "is the exhibited quotation in its source?", ("quote_grounded",),
       "a quotation was trusted if it looked plausible", _ground),
    Op("0x03", "DENOM", "does a population verdict carry N of M?", ("population_claim", "n", "m"),
       "a verdict was accepted with no count", _denom),
    Op("0x04", "UNIVERSE", "does a negative name what it searched?", ("negative", "universe"),
       "'not found' meant 'not found anywhere'", _universe),
    Op("0x05", "QUORUM", "did the finders reach the quorum?", ("share",),
       "a split was reported as PARTIAL with 'no quorum' beside it", _quorum),
    Op("0x06", "BLIND", "could the instrument answer at all?", ("instrument_answered",),
       "a blocked provider was reported as 0 results", _blind),
    Op("0x07", "TRUNC", "was a value silently cut on a verdict path?", ("truncation_class",),
       "every truncation looked like formatting", _trunc),
    Op("0x08", "PROVENANCE", "does the claim carry its command and digest?",
       ("command", "digest"), "a claim without a command was accepted", _provenance),
    Op("0x09", "STALE", "is the artifact newer than what it describes?", ("age_days",),
       "a stale artifact answered for a tree that had moved", _stale),
    Op("0x0A", "REPRO", "did the grade survive a re-draw?", ("draws", "reproduced"),
       "one draw was quoted as a finding", _repro),
    Op("0x0B", "KNOB", "is the setting read by anything?", ("knob", "knob_readers"),
       "orphan knobs and bypass readers were invisible", _knob),
    Op("0x0C", "DISABLED", "is the gate actually on?", ("enabled",),
       "a disabled gate reported success", _disabled),
)

_ORDER: Tuple[str, ...] = ("0x08", "0x09", "0x02", "0x01", "0x03", "0x04",
                           "0x07", "0x0B", "0x0C", "0x06", "0x0A", "0x05")


def isa_table() -> List[Dict[str, str]]:
    """The ISA as rows: code, name, question, legacy behaviour."""
    return [{"code": op.code, "name": op.name, "question": op.question,
             "legacy": op.legacy} for op in ISA]


def rung(states: Mapping[str, str]) -> str:
    """Collapse op states into exactly one ladder rung."""
    if states.get("0x02") == CUT or states.get("0x03") == CUT or states.get("0x04") == CUT:
        return CUT
    if states.get("0x08") == CUT or states.get("0x09") == CUT:
        return CUT
    if states.get("0x07") == CUT or states.get("0x0B") == CUT:
        return CUT
    if states.get("0x06") == BLIND or states.get("0x0C") == BLIND:
        return BLIND
    if states.get("0x05") == NO_QUORUM:
        return NO_QUORUM
    if states.get("0x01") == LEAD or states.get("0x0A") == LEAD:
        return LEAD
    if any(state == CUT for state in states.values()):
        return CUT
    if any(state == NO_QUORUM for state in states.values()):
        return NO_QUORUM
    if any(state == LEAD for state in states.values()):
        return LEAD
    return "VERIFIED"


def evaluate(record: Mapping[str, Any], quorum: float = 0.66,
             legacy: bool = False, max_age_days: float = 0.0) -> Dict[str, Any]:
    """Run the ISA over one reading and return the rung plus every op's reason.

    ``legacy=True`` reproduces the pre-RC behaviour for every op, including the
    two defective ones -- this is the migration instrument, not a mode to ship.
    """
    ctx: Dict[str, Any] = {"quorum": float(quorum), "legacy": bool(legacy),
                           "max_age_days": float(max_age_days)}
    by_code = {op.code: op for op in ISA}
    states: Dict[str, str] = {}
    reasons: Dict[str, str] = {}
    for code in _ORDER:
        op = by_code[code]
        state, reason = op.fn(record, ctx)
        states[code] = state
        reasons[code] = "%s %s: %s" % (op.code, op.name, reason)
    return {"rung": rung(states), "states": states, "reasons": reasons,
            "quorum": ctx["quorum"], "legacy": ctx["legacy"],
            "isa": "%s-%d" % ("HYPER_EDGE-ISA", len(ISA))}


def summarize(result: Mapping[str, Any]) -> str:
    """One line: the rung and the ops that produced it (non-PASS/SKIP only)."""
    notable = [text for code, text in sorted(result["reasons"].items())
               if result["states"][code] not in (PASS, SKIP)]
    return "%s | %s" % (result["rung"], "; ".join(notable) or "every op passed")


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="print the admissibility ISA")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    import json
    rows = isa_table()
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        for row in rows:
            print("%s %-11s %s" % (row["code"], row["name"], row["question"]))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
