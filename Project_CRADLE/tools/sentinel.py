# coding: utf-8
"""sentinel -- THE REAPER. The pre-action check that runs before a framed change is acted on.

WHY THE NAME
------------
A sentinel stands and watches. This does something less polite: when a frame's own claims
do not resolve, it TAKES the frame out of play and names the claim that failed. That is
reaping, so the launcher calls it the REAPER and this file keeps the name `sentinel.py`,
because five gates and three documents quote that path.

WHY IT SHIPS WITH THE DEFENDER
------------------------------
The defender writes the frame; the reaper refuses to let a frame be ACTED ON when the
frame's own claims do not resolve. That distinction is the whole point: a prompter can
produce a beautiful frame about a file that does not exist, defended tests that were
never written, and an evidence command nobody has. The frame reads as rigour; the check
would have caught all three in 3 ms.

So this is deliberately mechanical and deliberately narrow. Every assertion resolves
something against the disk or a closed vocabulary -- there is no assertion here that can
be satisfied by better prose:

  S1 intent-scoped     the intent opens with an act from a closed list
  S2 target-resolves   the target exists, or is declared new as `new:<path>`
  S3 break-resolves    every must_not_break entry names a path that EXISTS
  S4 defence-named     something is named as surviving the change
  S5 landing-stated    the frame says what blocks the landing
  S6 no-wishes         acceptance language, refused as in the defender
  S7 posture-intact    preservation work carries a valid posture (bytes == 0)

S3 is the one that earns its keep: "do not break the tests" is unfalsifiable, while
"tests/test_defender.py must still pass" is a path the sentinel can stat. A sentinel that
cannot stat is a poem.

USAGE
-----
    python tools/sentinel.py --intent "refuse a bad shard" --target tools/sword.py \\
        --break tests/test_defender.py --evidence "pytest -q" --json
    python tools/sentinel.py --selftest

Exit 0 when the action is allowed, 1 when it is BLOCKED (one line per reason), 2 when the
sentinel itself could not run -- and 2 is never reported as OK.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

#: The true name of this part. The file is `sentinel.py` and stays that way; the role is
#: to reap a frame whose claims do not resolve, not to watch it.
NAME = "REAPER"

#: The closed act vocabulary. An intent that opens with none of these is a topic, not a
#: task, and the difference is the whole reason this file exists.
ACTS = ("add", "build", "convert", "delete", "demand", "extract", "fix", "frame",
        "guard", "land", "measure", "migrate", "record", "refuse", "rename",
        "replace", "restore", "ship", "split", "stop", "verify", "write")

#: Refused in any field that must assert (never in a field whose job is to name the bad
#: shape -- that is the control's job, and scanning it refuses the honest control).
_WISHES = ("good enough", "looks right", "looks good", "should work", "should be fine",
           "seems fine", "works as expected", "tested manually", "obviously",
           "clearly correct", "no issues", "trust me")

_PATHISH = re.compile(r"([\w./\\-]+\.(?:py|sh|bat|md|json|jsonl|yml|yaml|js|ts|toml|db))")
_NEW = "new:"


class SentinelError(Exception):
    """The sentinel could not run. Never a pass, never a fail -- an absence."""


def _load_defender():
    """The posture rules live in one place; a second copy would be a second answer."""
    import importlib.util

    path = HERE / "defender.py"
    spec = importlib.util.spec_from_file_location("flaming_sword_defender_sentinel",
                                                  path)
    if spec is None or spec.loader is None:
        raise SentinelError("defender.py not loadable from %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check(intent: str, target: str, must_not_break: Sequence[str], defends: Sequence[str],
          refusal: str, acceptance: str = "", evidence: str = "", preserve: bool = False,
          posture: Optional[Dict[str, Any]] = None,
          root: Optional[Path] = None) -> Dict[str, Any]:
    """Return {verdict, problems, resolved}. Never raises for a bad frame."""
    root = Path(root) if root is not None else ROOT
    problems: List[str] = []
    resolved: List[str] = []

    def note(path: str) -> None:
        # Deduped: the target and the break list routinely name the same file, and a
        # resolved list that says the same thing twice reads as two checks.
        if path not in resolved:
            resolved.append(path)

    # S1 -- a topic is not a task
    first = (intent or "").strip().lower().split(" ")[0] if intent else ""
    if not first:
        problems.append("S1 intent-scoped: no intent")
    elif first not in ACTS:
        problems.append("S1 intent-scoped: %r does not open with an act from %s -- a "
                        "topic is not a task" % (first, ", ".join(ACTS[:6]) + ", ..."))

    # S2 -- the target must resolve, or be honestly declared new
    target = (target or "").strip()
    if not target:
        problems.append("S2 target-resolves: no target")
    elif target.startswith(_NEW):
        declared = target[len(_NEW):].strip()
        if not declared:
            problems.append("S2 target-resolves: %r declares nothing" % target)
        elif (root / declared).exists():
            problems.append("S2 target-resolves: %r is declared new but already exists"
                            % declared)
        else:
            note("%s (declared new)" % declared)
    else:
        candidate = root / target
        if candidate.exists():
            note(target)
        else:
            problems.append("S2 target-resolves: %r does not exist and is not declared "
                            "new as %s%s" % (target, _NEW, target))

    # S3 -- a break list that cannot be stat'ed decides nothing
    if not must_not_break:
        problems.append("S3 break-resolves: no must_not_break entry")
    for item in must_not_break or []:
        paths = _PATHISH.findall(str(item))
        if not paths:
            problems.append("S3 break-resolves: %r names no path, so nothing can be "
                            "verified as still passing" % (item,))
            continue
        for path in paths:
            if (root / path).exists():
                note(path)
            else:
                problems.append("S3 break-resolves: %r does not exist -- a break list "
                                "entry naming a missing file is a wish" % path)

    # S4 / S5 / S6 -- the frame's own assertions
    named = [str(d).strip() for d in defends or [] if str(d).strip()]
    if not named:
        problems.append("S4 defence-named: nothing is named as surviving this change")
    for item in named:
        # A placeholder is the shape a model writes when it has not decided yet: it is
        # long enough to pass a length check and says nothing, so it is refused.
        if ("<" in item and ">" in item) or item.lower().startswith("todo"):
            problems.append("S4 defence-named: %r is a placeholder, not a defence -- "
                            "name the test, claim or gate that survives" % (item,))
    if not (refusal or "").strip():
        problems.append("S5 landing-stated: the frame does not say what blocks the "
                        "landing")
    blob = " ".join([intent or "", refusal or "", acceptance or "", evidence or ""]).lower()
    for wish in _WISHES:
        if wish in blob:
            problems.append("S6 no-wishes: %r decides nothing" % (wish,))

    # S7 -- posture, delegated so there is one answer to "what is a valid posture"
    if preserve:
        defender = _load_defender()
        problems.extend("S7 posture-intact: " + p.replace("D9 posture-declared: ", "")
                        for p in defender.posture_problems(posture or {}))

    return {
        "verdict": "SENTINEL OK" if not problems else "SENTINEL BLOCKED",
        "problems": problems,
        "resolved": resolved,
        "preserve": bool(preserve),
        "root": str(root),
    }


# --------------------------------------------------------------------------- #
# Controls
# --------------------------------------------------------------------------- #

def _healthy(root: Optional[Path] = None) -> Dict[str, Any]:
    return check(
        intent="refuse a shard whose golden run does not reproduce",
        target="tools/sword.py",
        must_not_break=["tests/test_defender.py"],
        defends=["the golden run's state_sha256 token"],
        refusal="BLOCK when the acceptance command exits non-zero",
        acceptance="pytest exits 0 and prints 30 passed",
        evidence="tests/test_defender.py",
        root=root,
    )


def _mutations() -> List[Tuple[str, Any, str]]:
    def topic_intent(kwargs: Dict[str, Any]) -> None:
        kwargs["intent"] = "the shard validator situation"

    def missing_target(kwargs: Dict[str, Any]) -> None:
        kwargs["target"] = "tools/does_not_exist.py"

    def new_but_present(kwargs: Dict[str, Any]) -> None:
        kwargs["target"] = "new:tools/sword.py"

    def break_list_is_prose(kwargs: Dict[str, Any]) -> None:
        kwargs["must_not_break"] = ["don't break anything important"]

    def break_list_names_ghost(kwargs: Dict[str, Any]) -> None:
        kwargs["must_not_break"] = ["tests/test_ghost.py"]

    def no_defence(kwargs: Dict[str, Any]) -> None:
        kwargs["defends"] = []

    def placeholder_defence(kwargs: Dict[str, Any]) -> None:
        kwargs["defends"] = ["<name what survives: a test, a claim, a gate>"]

    def no_refusal(kwargs: Dict[str, Any]) -> None:
        kwargs["refusal"] = ""

    def wish(kwargs: Dict[str, Any]) -> None:
        kwargs["acceptance"] = "the suite looks right afterwards"

    def empty_posture(kwargs: Dict[str, Any]) -> None:
        kwargs["preserve"] = True
        kwargs["posture"] = {}

    return [
        ("intent is a topic", topic_intent, "S1 intent-scoped"),
        ("target does not exist", missing_target, "S2 target-resolves"),
        ("new target already exists", new_but_present, "S2 target-resolves"),
        ("break list is prose", break_list_is_prose, "S3 break-resolves"),
        ("break list names a ghost", break_list_names_ghost, "S3 break-resolves"),
        ("nothing defended", no_defence, "S4 defence-named"),
        ("placeholder defended", placeholder_defence, "S4 defence-named"),
        ("no landing condition", no_refusal, "S5 landing-stated"),
        ("a wish", wish, "S6 no-wishes"),
        ("preservation with no posture", empty_posture, "S7 posture-intact"),
    ]


def selftest(root: Optional[Path] = None) -> Tuple[int, List[str]]:
    lines: List[str] = []
    failures = 0
    base = _healthy(root)
    if base["problems"]:
        failures += 1
        lines.append("FAIL healthy control: a correct action was BLOCKED: %s"
                     % base["problems"][:3])
    else:
        lines.append("PASS healthy control: a correct action is allowed (%d path(s) "
                     "resolved)" % len(base["resolved"]))

    for name, mutate, expected in _mutations():
        kwargs = dict(
            intent="refuse a shard whose golden run does not reproduce",
            target="tools/sword.py",
            must_not_break=["tests/test_defender.py"],
            defends=["the golden run's state_sha256 token"],
            refusal="BLOCK when the acceptance command exits non-zero",
            acceptance="pytest exits 0 and prints 30 passed",
            evidence="tests/test_defender.py",
        )
        try:
            mutate(kwargs)
        except (KeyError, TypeError) as exc:
            failures += 1
            lines.append("FAIL %s: mutation could not be applied (%s)" % (name, exc))
            continue
        verdict = check(root=root, **kwargs)
        if [p for p in verdict["problems"] if p.startswith(expected)]:
            lines.append("PASS %s -> %s" % (name, expected))
        else:
            failures += 1
            lines.append("FAIL %s: expected %r, got %s"
                         % (name, expected, verdict["problems"][:2] or "SENTINEL OK"))

    # A sentinel that cannot read its own inputs must say so, not pass.
    try:
        _load_defender()
        lines.append("PASS defender.py loads (S7 has one source of posture truth)")
    except SentinelError as exc:
        failures += 1
        lines.append("FAIL %s" % exc)
    return failures, lines


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pre-action check: does this framed change resolve?")
    parser.add_argument("--intent", default="")
    parser.add_argument("--target", default="")
    parser.add_argument("--break", dest="must_not_break", action="append", default=[])
    parser.add_argument("--defends", action="append", default=[])
    parser.add_argument("--refusal", default="")
    parser.add_argument("--acceptance", default="")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--preserve", action="store_true")
    parser.add_argument("--root", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        failures, lines = selftest(Path(args.root) if args.root else None)
        if args.json:
            print(json.dumps({"failures": failures, "lines": lines}, indent=1))
        else:
            for line in lines:
                print(line)
            print("")
            print("SELFTEST %s (%d control(s), %d failure(s))"
                  % ("OK" if not failures else "FAILED", len(lines), failures))
        return 0 if not failures else 1

    if not args.intent:
        parser.error("--intent is required (or --selftest)")

    posture = None
    if args.preserve:
        posture = _load_defender().default_posture()
    verdict = check(intent=args.intent, target=args.target,
                    must_not_break=args.must_not_break, defends=args.defends,
                    refusal=args.refusal, acceptance=args.acceptance,
                    evidence=args.evidence, preserve=args.preserve, posture=posture,
                    root=Path(args.root) if args.root else None)
    if args.json:
        print(json.dumps(verdict, indent=1, sort_keys=True))
    else:
        print(verdict["verdict"])
        for problem in verdict["problems"]:
            print("     %s" % problem)
        if verdict["resolved"]:
            print("  resolved: %s" % ", ".join(verdict["resolved"][:6]))
        if verdict["problems"]:
            print("")
            print("  the action is BLOCKED: no claim above can be satisfied by better "
                  "prose, only by a path that exists")
    return 0 if not verdict["problems"] else 1


if __name__ == "__main__":
    sys.exit(main())
