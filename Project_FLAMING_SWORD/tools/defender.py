# coding: utf-8
"""defender -- write the defensive frame BEFORE a change, and refuse a frame that is not one.

WHY THIS EXISTS
---------------
Two failures kept landing in the same shape. A change described as "fix X" arrives
with no statement of what X was defending, so nothing can tell a repair from a
removal: the test that proved the old behaviour is deleted as "dead code", the gate
that refused the bad state is "simplified" away, and the run goes green. And a
preservation task described as "extract the game" arrives with no statement of whose
copy is being used or what may not be carried, so the fastest satisfying answer is a
copy of bytes that must never be copied.

Both are the same defect: the frame is missing, so the cheapest output wins. This
module is the frame. It is a PROMPTER, not a prose generator: it emits the claims a
task must carry -- what is defended, what must not break, the command that decides,
the mutation that must be refused, and (for preservation work) the posture that keeps
the act lawful -- and it refuses to emit a frame that is missing any of them.

WHAT IT EMITS, AND WHY EACH FIELD IS LOAD-BEARING
-------------------------------------------------
  defends         the artefact that survives because of this change; a change that
                  defends nothing is a deletion in a costume
  must_not_break  each entry names a test or a check, so "don't break anything" is
                  not an answer
  acceptance      a command plus an observable outcome -- the finish line
  control         a mutation that MUST be refused (RULE 0B-C); without it the
                  acceptance command proves only that something ran
  refusal         the condition that blocks the landing
  evidence        a path or a command, never "TBD"
  posture         for `--preserve`: whose copy, how many bytes of the original,
                  the lawful route, and the authority it rests on -- absent posture
                  is refused rather than filled in with a guess

The rendered `prompt` is what a model is handed. It puts the frame FIRST, before the
task, because a frame added afterwards is a rationalisation of work already done.

USAGE
-----
    python tools/defender.py --intent "delete the dead detector" \\
        --target tools/x.py --evidence "pytest tests/test_x.py -q"
    python tools/defender.py --intent "convert the cartridge to ticks" --preserve --json
    python tools/defender.py --selftest

Nothing here decides whether the work is lawful. It refuses to frame work that has
not said whose copy it is, which is the part a prompter can actually enforce.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

MIN_PROSE = 40

#: Phrases that decide nothing. Refused structurally, not discouraged.
_WISHES = ("good enough", "looks right", "looks good", "should work", "should be fine",
           "seems fine", "works as expected", "tested manually", "obviously",
           "clearly correct", "no issues", "trust me")

_COMMAND_RE = re.compile(
    r"(python3?\s|pytest\s|git\s|tools/[\w/]+\.py|scripts/[\w/]+\.py|`[^`]+`|"
    r"--check|--selftest|--self-test|exit\s*\d|\brc\b)", re.I)
_OUTCOME_RE = re.compile(r"(\b\d+\b|PASS|FAIL|BLOCK|refus|exit\s*(code|status)?\s*\d?|"
                         r"zero|exactly)", re.I)
_REFUSAL_RE = re.compile(r"(refus|reject|fail|block|must not|error|exit 1)", re.I)

#: The preservation posture. Each field exists because its absence was, in this
#: estate's history, filled in with an assumption.
POSTURE_FIELDS = ("whose_copy", "bytes_of_original", "lawful_route", "authority",
                  "what_must_not_be_carried")

#: Claims that may stand as posture authority. A posture citing something else is not
#: refused for being wrong -- it is refused for being unverifiable, which is worse.
AUTHORITIES = {
    "sony-v-connectix": "Sony Computer Entertainment v. Connectix (9th Cir. 2000) "
                        "-- intermediate copying for a new, non-infringing product "
                        "was fair use",
    "sega-v-accolade": "Sega v. Accolade (9th Cir. 1992) -- disassembly for "
                       "compatibility is fair use",
    "owner-holds-copy": "the operator holds the physical copy and the machine is "
                        "what failed, so the act is repair of their own property",
    "eu-declined-to-legislate": "the EU declined to legislate a preservation "
                                "exemption (2026); no statutory route is claimed",
    "us-exemption-declined": "the US declined a preservation exemption (2024); no "
                             "statutory route is claimed",
    "no-authority-claimed": "no legal authority is claimed: the work stays inside "
                            "rules-only extraction and states that plainly",
}


# --------------------------------------------------------------------------- #
# The frame
# --------------------------------------------------------------------------- #

def frame(intent: str, target: str, evidence: str, defends: Sequence[str],
          must_not_break: Sequence[str], acceptance: str, control: str,
          refusal: Optional[str] = None, preserve: bool = False,
          posture: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Assemble the frame. Refuses to emit one that cannot bear weight."""
    frame_obj: Dict[str, Any] = {
        "shape": "defensive-v1",
        "intent": intent,
        "target": target,
        "defends": list(defends),
        "must_not_break": list(must_not_break),
        "acceptance": acceptance,
        "control": control,
        "refusal": refusal or default_refusal(acceptance),
        "evidence": evidence,
        "preserve": bool(preserve),
    }
    if preserve:
        frame_obj["posture"] = posture or {}
    # `problems` is always present, empty on success: a caller that has to test for the
    # key's existence eventually indexes it, and a KeyError is not a frame.
    frame_obj["problems"] = problems_in(frame_obj)
    if frame_obj["problems"]:
        frame_obj["prompt"] = ""
        return frame_obj
    frame_obj["prompt"] = render(frame_obj)
    return frame_obj


def default_refusal(acceptance: str) -> str:
    return ("BLOCK the landing when %r does not run, exits non-zero, or its outcome "
            "differs from the one stated" % (acceptance.strip() or "the acceptance "
                                             "command"))


def problems_in(frame_obj: Dict[str, Any]) -> List[str]:
    problems: List[str] = []

    intent = str(frame_obj.get("intent") or "").strip()
    if len(intent) < 12:
        problems.append("D1 intent-named: no intent, so the frame defends nothing in "
                        "particular")
    target = str(frame_obj.get("target") or "").strip()
    if not target:
        problems.append("D1 intent-named: no target named")

    defends = [d for d in frame_obj.get("defends") or [] if str(d).strip()]
    if not defends:
        problems.append("D2 defends-something: nothing is named as surviving this "
                        "change; a change that defends nothing is a deletion in costume")
    for item in defends:
        if len(str(item).strip()) < 12:
            problems.append("D2 defends-something: %r is too thin to be an artefact "
                            "-- name the test, claim or gate" % (item,))

    breaks = [b for b in frame_obj.get("must_not_break") or [] if str(b).strip()]
    if not breaks:
        problems.append("D3 break-list: no must_not_break entry; 'don't break "
                        "anything' decides nothing")
    for item in breaks:
        text = str(item)
        if not (_COMMAND_RE.search(text) or "/" in text or "\\" in text):
            problems.append("D3 break-list: %r names no test or path" % (item,))

    acceptance = str(frame_obj.get("acceptance") or "")
    if not _COMMAND_RE.search(acceptance):
        problems.append("D4 acceptance-runnable: the acceptance names no command")
    if not _OUTCOME_RE.search(acceptance):
        problems.append("D4 acceptance-runnable: the acceptance names no observable "
                        "outcome (count, verdict, exit status)")

    control = str(frame_obj.get("control") or "")
    if not _REFUSAL_RE.search(control):
        problems.append("D5 control-refuses: the control describes nothing that must "
                        "be refused, so it is a second happy path")

    evidence = str(frame_obj.get("evidence") or "")
    if not (_COMMAND_RE.search(evidence) or "/" in evidence or "\\" in evidence):
        problems.append("D6 evidence-lands: evidence names neither a command nor a path")

    blob = " ".join([acceptance, control, evidence, str(frame_obj.get("refusal") or "")]).lower()
    for wish in _WISHES:
        if wish in blob:
            problems.append("D7 no-wishes: %r decides nothing; only a measurement "
                            "closes a task" % (wish,))

    refusal = str(frame_obj.get("refusal") or "")
    if not _REFUSAL_RE.search(refusal):
        problems.append("D8 refusal-stated: nothing is stated as blocking the landing")

    if frame_obj.get("preserve"):
        problems.extend(posture_problems(frame_obj.get("posture") or {}))
    return problems


def posture_problems(posture: Dict[str, Any]) -> List[str]:
    problems: List[str] = []
    if not isinstance(posture, dict) or not posture:
        return ["D9 posture-declared: preservation work with no posture, so whose copy "
                "it is and what may not be carried are left to assumption"]
    for field in POSTURE_FIELDS:
        value = posture.get(field)
        if field == "bytes_of_original":
            if not isinstance(value, int):
                problems.append("D9 posture-declared: bytes_of_original must be an "
                                "integer measurement, not %r" % (value,))
            elif value != 0:
                problems.append("D9 posture-declared: bytes_of_original is %d; a "
                                "preservation shard carries none of the original"
                                % value)
            continue
        if not isinstance(value, str) or len(value.strip()) < 8:
            problems.append("D9 posture-declared: posture.%s is missing or too thin"
                            % field)
    authority = posture.get("authority")
    if isinstance(authority, str) and authority and authority not in AUTHORITIES:
        problems.append("D9 posture-declared: authority %r is not one of %s"
                        % (authority, ", ".join(sorted(AUTHORITIES))))
    route = str(posture.get("lawful_route") or "")
    if route and not _REFUSAL_RE.search(route) and "no " not in route.lower():
        problems.append("D9 posture-declared: lawful_route %r makes no refusal and "
                        "claims no absence; say what is not done" % route)
    return problems


# --------------------------------------------------------------------------- #
# The prompt
# --------------------------------------------------------------------------- #

def render(frame_obj: Dict[str, Any]) -> str:
    """The frame as a model receives it. Defensive first, task second, by design."""
    lines = [
        "DEFENSIVE FRAME (read before acting; do not restate it, satisfy it)",
        "",
        "  what survives because of this work:",
    ]
    lines.extend("    - %s" % item for item in frame_obj["defends"])
    lines += ["  what must still pass afterwards:"]
    lines.extend("    - %s" % item for item in frame_obj["must_not_break"])
    lines += [
        "  the finish line: %s" % frame_obj["acceptance"],
        "  the mutation that must be REFUSED: %s" % frame_obj["control"],
        "  the landing condition: %s" % frame_obj["refusal"],
        "  evidence to leave behind: %s" % frame_obj["evidence"],
    ]
    posture = frame_obj.get("posture") or {}
    if frame_obj.get("preserve") and posture:
        lines += [
            "",
            "POSTURE (unchanged by any argument for speed or completeness)",
            "  whose copy:            %s" % posture.get("whose_copy"),
            "  bytes of the original: %s" % posture.get("bytes_of_original"),
            "  lawful route:          %s" % posture.get("lawful_route"),
            "  authority:             %s -- %s" % (
                posture.get("authority"), AUTHORITIES.get(posture.get("authority"), "")),
            "  never carried:         %s" % posture.get("what_must_not_be_carried"),
        ]
    lines += [
        "",
        "RULES THAT OVERRIDE YOUR DEFAULTS",
        "  1. Do not delete a test, a claim or a gate to make a run green. If it must",
        "     go, name what it defended and where that defence moved to.",
        "  2. A detector that could not run is UNRUN with its reason. UNRUN is not",
        "     zero findings, and it is not a pass.",
        "  3. Do not describe acceptance. Run the acceptance command and quote it.",
        "  4. Do not narrow, widen or improve the intent above. If you think it is",
        "     wrong, say so in one sentence and then do it as written.",
        "  5. If the frame cannot be satisfied, STOP and report which field failed --",
        "     a frame report is a finished turn; a summary is not.",
        "",
        "TASK: %s  (target: %s)" % (frame_obj["intent"], frame_obj["target"]),
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# The AIO prompt: user prompt -> frame + sentinel + memory, in one instruction object
# --------------------------------------------------------------------------- #

def _sibling(name: str):
    """Load a sibling module by path, so this file works run OR imported."""
    import importlib.util

    path = Path(__file__).resolve().parent / ("%s.py" % name)
    spec = importlib.util.spec_from_file_location("flaming_sword_%s" % name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def to_aio(user_prompt: str, target: str = "", acceptance: str = "", evidence: str = "",
           defends: Optional[Sequence[str]] = None,
           must_not_break: Optional[Sequence[str]] = None,
           control: str = "", refusal: str = "", preserve: bool = False,
           memory: Optional[Dict[str, Any]] = None,
           root: Optional[str] = None) -> Dict[str, Any]:
    """Turn a user prompt into an AIO instruction object, or refuse with reasons.

    The frame answers "what must be true"; the sentinel answers "does any of it
    resolve"; the memory answers "has this been learned before". All three are needed,
    because each one alone has a blind spot a model slides into: a frame without a
    sentinel describes files that do not exist, and a sentinel without memory re-learns
    the same defect every session.

    Refusal is a first-class result: no prompt is rendered when the frame or the sentinel
    fails, so the model cannot be handed an instruction object built on a hole.
    """
    frame_obj = frame(
        intent=user_prompt,
        target=target or "",
        evidence=evidence,
        defends=list(defends or []),
        must_not_break=list(must_not_break or []),
        acceptance=acceptance,
        control=control or default_control(user_prompt),
        refusal=refusal or None,
        preserve=preserve,
        posture=default_posture() if preserve else None,
    )
    result: Dict[str, Any] = {"shape": "defensive-aio-v1", "user_prompt": user_prompt,
                              "frame": frame_obj, "aio": ""}
    if frame_obj.get("problems"):
        result["state"] = "REFUSED"
        result["problems"] = ["frame: " + p for p in frame_obj["problems"]]
        return result

    try:
        sentinel = _sibling("sentinel")
    except ImportError as exc:
        result["state"] = "REFUSED"
        result["problems"] = ["sentinel: could not be loaded (%s), so the frame is "
                              "unchecked" % exc]
        return result

    verdict = sentinel.check(
        intent=user_prompt,
        target=target,
        must_not_break=frame_obj["must_not_break"],
        defends=frame_obj["defends"],
        refusal=frame_obj["refusal"],
        acceptance=acceptance,
        evidence=evidence,
        preserve=preserve,
        posture=frame_obj.get("posture"),
        root=Path(root) if root else None,
    )
    result["sentinel"] = verdict
    if verdict["problems"]:
        result["state"] = "BLOCKED"
        result["problems"] = ["sentinel: " + p for p in verdict["problems"]]
        return result

    memory = memory or {"state": "UNMEMORED", "backend": "none",
                        "reason": "no memory backend was consulted for this prompt"}
    result["memory"] = memory
    result["state"] = "READY" if memory.get("state") == "MEMORY" else "READY-UNMEMORED"
    result["aio"] = render_aio(result)
    return result


def render_aio(result: Dict[str, Any]) -> str:
    """The instruction object itself: prompt, frame, what resolved, what was learned."""
    frame_obj = result["frame"]
    verdict = result.get("sentinel") or {}
    memory = result.get("memory") or {}
    lines = [
        "AIO  defensive-aio-v1",
        "",
        "USER PROMPT (verbatim, and it governs):",
        "  %s" % result["user_prompt"],
        "",
        "FRAME -- satisfied, not restated:",
    ]
    lines.extend("  survives:     %s" % item for item in frame_obj["defends"])
    lines.extend("  must pass:    %s" % item for item in frame_obj["must_not_break"])
    lines += [
        "  finish line:  %s" % frame_obj["acceptance"],
        "  must REFUSE:  %s" % frame_obj["control"],
        "  landing:      %s" % frame_obj["refusal"],
        "  evidence:     %s" % frame_obj["evidence"],
        "",
        "SENTINEL -- %s (%d path(s) resolved)"
        % (verdict.get("verdict", "NOT RUN"), len(verdict.get("resolved") or [])),
    ]
    lines.extend("  ok: %s" % path for path in (verdict.get("resolved") or [])[:6])
    lines += [
        "",
        "MEMORY -- %s" % memory.get("state", "UNMEMORED"),
    ]
    if memory.get("state") == "MEMORY":
        for match in (memory.get("matches") or [])[:5]:
            lines.append("  [%s] %s" % (match.get("backend"), match.get("content", "")[:200]))
    else:
        lines.append("  NOT an absence of lessons: %s" % memory.get(
            "reason", "no backend answered"))
        lines.append("  proceed on judgement, and record what you learned so the next"
                     " run is not UNMEMORED")
    posture = frame_obj.get("posture") or {}
    if frame_obj.get("preserve") and posture:
        lines += ["", "POSTURE", "  whose copy:            %s" % posture.get("whose_copy"),
                  "  bytes of the original: %s" % posture.get("bytes_of_original"),
                  "  lawful route:          %s" % posture.get("lawful_route"),
                  "  authority:             %s" % posture.get("authority"),
                  "  never carried:         %s" % posture.get("what_must_not_be_carried")]
    lines += [
        "",
        "WHAT ENDS THIS TURN",
        "  the acceptance command run, and its output quoted. Nothing else.",
        "  if it cannot run: say which field failed and stop -- a frame report is a"
        "  finished turn; a summary is not.",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Defaults that make the prompter usable without a wall of arguments
# --------------------------------------------------------------------------- #

def default_break_list(target: str) -> List[str]:
    return ["tests/* that name %s -- run them, do not delete them" % (target or "it")]


def default_control(intent: str) -> str:
    return ("re-introduce the defect the work is meant to remove and require the "
            "acceptance command to REFUSE it (exit non-zero), or the command proves "
            "only that something ran")


def default_posture() -> Dict[str, Any]:
    """The posture this estate can defend without a lawyer in the room."""
    return {
        "whose_copy": "the operator's own physical copy; nothing is acquired",
        "bytes_of_original": 0,
        "lawful_route": "rules-only extraction by measurement; no decryption, no "
                        "patching, no circumvention of any protection",
        "authority": "sony-v-connectix",
        "what_must_not_be_carried": "no asset bytes, no rom image, no key, no "
                                    "decrypted blob -- a hash lock to the owner's own "
                                    "image instead",
    }


# --------------------------------------------------------------------------- #
# The draft: a skeleton a model can fill, which cannot be mistaken for a frame
# --------------------------------------------------------------------------- #

#: An unfilled field is marked with this sentinel, never left blank and never guessed.
#: A blank field reads as "nothing to say"; a sentinel reads as "not yet measured".
SENTINEL = "<<FILL: %s>>"


def draft(intent: str, target: str = "", preserve: bool = False) -> Dict[str, Any]:
    """Emit the skeleton, honestly labelled, for a model to complete before acting.

    The strict frame refuses an unfilled field; that is correct for a landing and
    useless for a beginning, when the acceptance command does not exist yet. A draft
    keeps both properties by making incompleteness VISIBLE: every hole is a sentinel,
    the banner says DRAFT -- NOT A FRAME, and the list of holes is printed, so a draft
    cannot be quoted as if it were a frame.
    """
    holes = ["defends", "must_not_break", "acceptance", "control", "refusal",
             "evidence"] + (list(POSTURE_FIELDS) if preserve else [])
    frame_obj: Dict[str, Any] = {
        "shape": "defensive-v1",
        "draft": True,
        "intent": intent,
        "target": target or SENTINEL % "target",
        "defends": [SENTINEL % "the test, claim or gate that survives this change"],
        "must_not_break": [SENTINEL % "a test or path that must still pass"],
        "acceptance": SENTINEL % "command that decides, plus its expected outcome",
        "control": SENTINEL % "a mutation the acceptance command MUST refuse",
        "refusal": SENTINEL % "what blocks the landing",
        "evidence": SENTINEL % "path or command whose output is the proof",
        "preserve": bool(preserve),
        "unfilled": holes,
    }
    if preserve:
        posture = {field: SENTINEL % field for field in POSTURE_FIELDS}
        posture["bytes_of_original"] = SENTINEL % "0 -- an integer, and it must be 0"
        frame_obj["posture"] = posture
    frame_obj["prompt"] = render_draft(frame_obj)
    return frame_obj


def render_draft(frame_obj: Dict[str, Any]) -> str:
    banner = [
        "DRAFT -- NOT A FRAME. %d field(s) unfilled, each marked <<FILL: ...>>." %
        len(frame_obj.get("unfilled") or []),
        "Fill every sentinel before acting. `--check` refuses this document as it stands,",
        "and the refusal is the point: a frame with holes decides nothing, so anything",
        "you produce satisfies it.",
        "",
    ]
    body = render(dict(frame_obj))
    body = body.replace("DEFENSIVE FRAME (read before acting; do not restate it, satisfy it)",
                        "DEFENSIVE FRAME, DRAFT (fill the sentinels, then satisfy it)")
    tail = ["", "UNFILLED: %s" % ", ".join(frame_obj.get("unfilled") or [])]
    return "\n".join(banner) + body + "\n".join(tail) + "\n"


# --------------------------------------------------------------------------- #
# Controls
# --------------------------------------------------------------------------- #

def healthy_frame() -> Dict[str, Any]:
    return frame(
        intent="refuse a shard whose golden run does not reproduce",
        target="docs/METTHEW/shard.schema.json",
        evidence="python tools/metthew_validate.py --shard docs/METTHEW/reference-shards/highend_ladder",
        defends=["the golden run's state_sha256 token", "the F6 reference-shard claim"],
        must_not_break=["tests/test_metthew_families.py", "tools/metthew_validate.py --selftest"],
        acceptance="`python tools/metthew_validate.py --shard <shard>` exits 0 and prints "
                   "PASS for 3 of 3 fixtures",
        control="flip one byte in the stored state_sha256 and require the gate to refuse "
                "with the offending field named",
        preserve=False,
    )


def _mutations() -> List[Tuple[str, Any, str]]:
    def no_defence(f: Dict[str, Any]) -> None:
        f["defends"] = []

    def wishful_acceptance(f: Dict[str, Any]) -> None:
        f["acceptance"] = "the validator looks right afterwards"

    def happy_path_control(f: Dict[str, Any]) -> None:
        f["control"] = "run it again with the real fixture"

    def vague_break(f: Dict[str, Any]) -> None:
        f["must_not_break"] = ["don't break anything important"]

    def evidence_defers(f: Dict[str, Any]) -> None:
        f["evidence"] = "TBD"

    def preserve_without_posture(f: Dict[str, Any]) -> None:
        f["preserve"] = True
        f["posture"] = {}

    def posture_carries_bytes(f: Dict[str, Any]) -> None:
        f["preserve"] = True
        f["posture"] = default_posture()
        f["posture"]["bytes_of_original"] = 1024

    def posture_cites_nothing(f: Dict[str, Any]) -> None:
        f["preserve"] = True
        f["posture"] = default_posture()
        f["posture"]["authority"] = "vibes"

    return [
        ("nothing defended", no_defence, "D2 defends-something"),
        ("acceptance is an adjective", wishful_acceptance, "D7 no-wishes"),
        ("control is a happy path", happy_path_control, "D5 control-refuses"),
        ("break list is a wish", vague_break, "D3 break-list"),
        ("evidence defers", evidence_defers, "D6 evidence-lands"),
        ("preservation with no posture", preserve_without_posture, "D9 posture-declared"),
        ("posture carries bytes", posture_carries_bytes, "D9 posture-declared"),
        ("posture cites nothing", posture_cites_nothing, "D9 posture-declared"),
    ]


def selftest() -> Tuple[int, List[str]]:
    lines: List[str] = []
    failures = 0

    clean = healthy_frame()
    if clean.get("problems"):
        failures += 1
        lines.append("FAIL healthy control: a correct frame was refused: %s"
                     % clean["problems"][:3])
    else:
        lines.append("PASS healthy control: a correct frame is accepted and rendered")
    if "DEFENSIVE FRAME" not in clean.get("prompt", ""):
        failures += 1
        lines.append("FAIL the accepted frame rendered no prompt")

    for name, mutate, expected in _mutations():
        broken = copy.deepcopy(clean)
        broken.pop("prompt", None)
        broken.pop("problems", None)
        try:
            mutate(broken)
        except (KeyError, TypeError) as exc:
            failures += 1
            lines.append("FAIL %s: mutation could not be applied (%s)" % (name, exc))
            continue
        problems = problems_in(broken)
        if [p for p in problems if p.startswith(expected)]:
            lines.append("PASS %s -> %s" % (name, expected))
        else:
            failures += 1
            lines.append("FAIL %s: expected %r, got %s"
                         % (name, expected, problems[:2] or "no refusal"))

    # The draft direction: it must render, must carry a sentinel in every hole, and
    # must NOT be accepted by the strict checker -- otherwise a draft would sail
    # through the same gate as a frame and the distinction would be decoration.
    skeleton = draft("convert a cartridge into a rules shard", "<cartridge>", preserve=True)
    if not skeleton.get("prompt"):
        failures += 1
        lines.append("FAIL a draft rendered no prompt, so nothing can be filled")
    elif "DRAFT -- NOT A FRAME" not in skeleton["prompt"]:
        failures += 1
        lines.append("FAIL a draft does not say it is a draft")
    elif len(re.findall(r"<<FILL:", skeleton["prompt"])) < len(skeleton["unfilled"]):
        failures += 1
        lines.append("FAIL a draft lists %d hole(s) but marks fewer in the prompt"
                     % len(skeleton["unfilled"]))
    else:
        lines.append("PASS a draft renders with every hole marked")
    strict = problems_in({k: v for k, v in skeleton.items()
                          if k not in ("prompt", "draft", "unfilled")})
    if not strict:
        failures += 1
        lines.append("FAIL the strict checker ACCEPTED a draft; a sentinel is not a "
                     "measurement")
    else:
        lines.append("PASS the strict checker refuses the same draft (%d reason(s))"
                     % len(strict))

    # AIO: a complete prompt becomes an instruction object; an incomplete one does not,
    # and an unresolvable one is BLOCKED before a model ever sees it.
    aio_kwargs = dict(
        target="tools/sword.py",
        acceptance="pytest -q exits 0 and prints 76 passed",
        evidence="tests/test_defender.py",
        defends=["the golden run's state_sha256 token"],
        must_not_break=["tests/test_defender.py"],
        control="flip one byte in state_sha256 and require the gate to REFUSE it",
    )
    aio = to_aio("refuse a shard whose golden run does not reproduce", **aio_kwargs)
    if aio["state"] == "READY-UNMEMORED" and "AIO  defensive-aio-v1" in aio["aio"]:
        lines.append("PASS aio: a complete prompt becomes an instruction object "
                     "(%d chars)" % len(aio["aio"]))
    else:
        failures += 1
        lines.append("FAIL aio: complete prompt reported %s / %s"
                     % (aio["state"], aio.get("problems")))
    if "USER PROMPT (verbatim, and it governs)" in aio.get("aio", ""):
        lines.append("PASS aio: the user's words are carried verbatim above the frame")
    else:
        failures += 1
        lines.append("FAIL aio: the user prompt is not carried verbatim")
    if "NOT an absence of lessons" in aio.get("aio", ""):
        lines.append("PASS aio: UNMEMORED is stated as a run fact, not as no lessons")
    else:
        failures += 1
        lines.append("FAIL aio: UNMEMORED was not distinguished from no lessons")

    blocked = to_aio("refuse a shard whose golden run does not reproduce",
                     **{**aio_kwargs, "target": "tools/ghost_file.py"})
    if blocked["state"] == "BLOCKED" and not blocked["aio"]:
        lines.append("PASS aio: an unresolvable target is BLOCKED and no prompt is "
                     "rendered")
    else:
        failures += 1
        lines.append("FAIL aio: a ghost target reported %s" % blocked["state"])

    refused = to_aio("refuse a shard whose golden run does not reproduce",
                     **{**aio_kwargs, "acceptance": ""})
    if refused["state"] == "REFUSED" and not refused["aio"]:
        lines.append("PASS aio: no finish line is REFUSED and no prompt is rendered")
    else:
        failures += 1
        lines.append("FAIL aio: a missing acceptance reported %s" % refused["state"])

    remembered = to_aio(
        "refuse a shard whose golden run does not reproduce",
        memory={"state": "MEMORY", "backend": "jsonl",
                "matches": [{"backend": "jsonl", "score": 2,
                              "content": "a stale state_sha256 must be refused"}]},
        **aio_kwargs)
    if remembered["state"] == "READY" and "stale state_sha256" in remembered["aio"]:
        lines.append("PASS aio: a recalled lesson reaches the instruction object")
    else:
        failures += 1
        lines.append("FAIL aio: a recalled lesson did not reach the prompt")

    # A refusal must never be silently repaired: the bad frame reports its problems and
    # renders NO prompt, so nothing downstream can act on it.
    bad = frame(intent="do the thing", target="", evidence="", defends=[],
                must_not_break=[], acceptance="", control="")
    if bad.get("prompt"):
        failures += 1
        lines.append("FAIL a refused frame still rendered a prompt")
    elif not bad.get("problems"):
        failures += 1
        lines.append("FAIL a refused frame reported no problems")
    else:
        lines.append("PASS a refused frame renders nothing and names %d problem(s)"
                     % len(bad["problems"]))

    return failures, lines


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Frame a change defensively, and refuse a frame that is not one.")
    parser.add_argument("--intent", default="", help="what the work is meant to achieve")
    parser.add_argument("--target", default="", help="the file, service or artefact")
    parser.add_argument("--evidence", default="", help="command or path that proves it")
    parser.add_argument("--defends", action="append", default=[],
                        help="an artefact that survives because of this work (repeatable)")
    parser.add_argument("--break", dest="must_not_break", action="append", default=[],
                        help="a test or check that must still pass (repeatable)")
    parser.add_argument("--acceptance", default="", help="command + observable outcome")
    parser.add_argument("--control", default="", help="mutation that MUST be refused")
    parser.add_argument("--refusal", default="", help="what blocks the landing")
    parser.add_argument("--preserve", action="store_true",
                        help="preservation work: posture becomes mandatory")
    parser.add_argument("--draft", action="store_true",
                        help="emit the skeleton with every unfilled field marked, "
                             "labelled DRAFT -- NOT A FRAME")
    parser.add_argument("--aio", action="store_true",
                        help="convert the user prompt into an AIO instruction object "
                             "(frame + sentinel + memory), or refuse with reasons")
    parser.add_argument("--jsonl", default=None,
                        help="with --aio: a lesson ledger to recall from")
    parser.add_argument("--command", dest="recall_command", default=None,
                        help="with --aio: a command printing JSON lines to recall from")
    parser.add_argument("--root", default=None,
                        help="with --aio: directory the sentinel resolves paths against")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        failures, lines = selftest()
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

    if args.aio:
        bridge = _sibling("memory_bridge")
        memory = bridge.recall(args.intent, jsonl=args.jsonl,
                               command=args.recall_command)
        result = to_aio(
            args.intent, target=args.target, acceptance=args.acceptance,
            evidence=args.evidence, defends=args.defends,
            must_not_break=args.must_not_break, control=args.control,
            refusal=args.refusal, preserve=args.preserve, memory=memory,
            root=args.root)
        if args.json:
            print(json.dumps(result, indent=1, sort_keys=True))
        elif result.get("problems"):
            print("%s: the prompt cannot become an instruction object."
                  % result["state"])
            for problem in result["problems"]:
                print("     %s" % problem)
            print("")
            print("  no AIO was rendered: a model handed a prompt built on a hole will")
            print("  fill the hole with prose")
        else:
            print(result["aio"])
        return 0 if result["state"].startswith("READY") else 1

    if args.draft:
        skeleton = draft(args.intent, args.target, preserve=args.preserve)
        if args.json:
            print(json.dumps(skeleton, indent=1, sort_keys=True))
        else:
            print(skeleton["prompt"])
        return 0

    frame_obj = frame(
        intent=args.intent,
        target=args.target or "<target not named>",
        evidence=args.evidence,
        defends=args.defends or ["<name what survives: a test, a claim, a gate>"],
        must_not_break=args.must_not_break or default_break_list(args.target or "it"),
        acceptance=args.acceptance,
        control=args.control or default_control(args.intent),
        refusal=args.refusal or None,
        preserve=args.preserve,
        posture=default_posture() if args.preserve else None,
    )

    if args.json:
        print(json.dumps(frame_obj, indent=1, sort_keys=True))
    elif frame_obj.get("problems"):
        print("REFUSED: this is not a frame yet.")
        for problem in frame_obj["problems"]:
            print("     %s" % problem)
        print("")
        print("  a frame that cannot name what it defends is how a repair becomes a "
              "removal")
    else:
        print(frame_obj["prompt"])
    return 0 if not frame_obj.get("problems") else 1


if __name__ == "__main__":
    sys.exit(main())
