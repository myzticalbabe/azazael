#!/usr/bin/env python3
# coding: utf-8
"""prompt_check — FLAMING SWORD's missing gate: the zero-shot prompt is falsifiable.

Everything else in this tree is checked: the generated order blocks against their
source, the staged diff against a scanner, the suite per file, the bible against
its own citations. The instruction file a fresh model reads FIRST was prose
nobody verified — and it had rotted where nobody was looking: measured
2026-11-02, it claimed 5,380 tests against a live collection of 6,277 (16% low),
and nothing in the estate could notice.

Four checks, all mechanical. Each resolves something against the disk or against a
recorded reading; none can be satisfied by better prose.

  P1 start-block-present   the START-HERE contract exists, and sits in the first
                           4,000 characters. A precedence statement under 20 KB of
                           canon is met last or never.
  P2 paths-resolve         every backticked path in the prompt exists on this host.
                           A command pointing at a file that is gone is an
                           instruction to fail, read by someone who cannot tell.
  P3 numbers-dated         every count ("N tests", "N skills", "N rules") matches
                           state/head.json within tolerance, or carries "measured
                           <date>" / "cached" / "historical" on the same line.
                           A number with no date is a rumour wearing knowledge.
  P4 handoff-resolves      the newest docs/*HANDOFF*.md names a commit that
                           resolves. A handoff citing a SHA nobody can check is a
                           story about a session.

Exit codes: 0 clean, 1 a prompt defect, 2 the instrument could not run (no prompt
found, no git). 2 is never a pass -- the same contract as every other gate here.

    python tools/prompt_check.py                 # controls, then the live prompts
    python tools/prompt_check.py --selftest      # controls only
    python tools/prompt_check.py --json          # machine-readable
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "state" / "head.json"
#: The contract must be reachable at the top. 4,000 characters is roughly the first
#: screen and a half; a block below that competes with the canon it is meant to
#: replace, and the measurement behind the number is that the canon it would sit
#: under is 1.12 MB long.
TOP_WINDOW = 4000
#: A count is "the same reading" within this fraction -- one parametrised test moves
#: a collection number, and a gate that fails on ±1 gets switched off within a day.
TOLERANCE = 0.10
START_MARKER = "<!-- AO:start-here START -->"

_PATH = re.compile(r"`([\w][\w./\\:-]*\.(?:py|md|json|jsonl|ya?ml|cmd|vbs|toml|txt))`")
# The thousands branch must come FIRST and the lookbehind must exclude `,`: with
# `(\d{2,4}(?:,\d{3})*)` the engine rejected "6,27" and settled on the tail "277",
# so 6,277 read as 277 -- a control caught it, and it would have failed every
# honest current count while passing a stale one that happened to end in the
# recorded digits.
_COUNT = re.compile(r"(?<![\w.,])(\d{1,3}(?:,\d{3})+|\d{2,4})\s+"
                    r"(tests?|skills?|rules?|modules?|shards?)\b")
_DATED = re.compile(r"measured\s+\d{4}-\d{2}-\d{2}|cached|historical|unverified", re.I)
#: The one word that lets a stale figure stand: it declares the number as a past
#: reading, not a claim about the tree as it is now.
_HISTORICAL = re.compile(r"\bhistorical(ly)?\b", re.I)
_SHA = re.compile(r"\b([0-9a-f]{7,40})\b")
#: Hosts this process cannot stat. Named, printed, never silently skipped.
REMOTE_PREFIXES = ("/root/", "/mnt/c/")
#: Roots that only exist on the Kali lane. A Windows run that called these dead
#: would fail the beam prompt for a tree it has never been able to see.
REMOTE_ROOTS = ("BCC-REINVESTIGATION/", "03_tooling/", "00_raw/")
#: Directories that hold artefacts a command WRITES. A prompt naming
#: `logs/golden_arrow_staged.json` before the first run is not citing a missing file,
#: so the absence is correct until the command runs. Deliberately a short list of
#: generated-output roots -- a general "parent exists" rule would pass almost every
#: wrong path, since most of them would sit in a directory that really exists.
OUTPUT_PREFIXES = ("logs/", "state/", "renders/", "runs/", "artifacts/", "out/")


class Blind(Exception):
    """The check could not be performed. Never a pass, never a defect."""


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _roots(repo: Path) -> Tuple[Path, ...]:
    """Every base a lane prompt legitimately writes a path against.

    Measured on this box: the Kilo prompt says `azazael/MANDATES.md` (relative to
    C:/Azazael), another lane says `tools/golden_arrow.py` (relative to the repo
    root), a third gives an absolute Windows path. All three name the same file. A
    resolver that knows only one base reports working commands as dead -- and a
    gate that cries on correct instructions is a gate the next session learns to
    ignore, which is how the stale counts survived in the first place.
    """
    home = Path.home()
    appdata = os.environ.get("APPDATA")
    startup = (Path(appdata) / "Microsoft/Windows/Start Menu/Programs/Startup"
               if appdata else None)
    roots: List[Path] = []
    for root in (repo, repo.parent, home, home / ".config", startup):
        if root is not None and root not in roots:
            roots.append(root)
    return tuple(roots)


def resolve(path: str, repo: Path = REPO) -> Optional[bool]:
    """True when the path exists here, False when it does not, None when not an address.

    None is returned in two honest cases: a path on a host this process cannot see
    (a WSL lane's `/root/...`), and a bare filename with no directory part. A bare
    `SKILL.md` in prose is a mention -- "a skill is a directory holding SKILL.md" --
    not a claim about a file at a known address, and resolving mentions by basename
    search would pass a wrong path as easily as a right one. The caller counts them
    aloud so the difference between verified and unverifiable stays visible.
    """
    cleaned = _norm(os.path.expanduser(os.path.expandvars(path)))
    if cleaned.startswith(REMOTE_PREFIXES):
        return None
    if cleaned.startswith(REMOTE_ROOTS) and not Path(cleaned).is_absolute():
        return None
    # `Startup\pmb-floor-proxy.vbs` is how the prompt names the logon shortcut; the
    # folder is not under any repo root, so it needs naming here or the gate fails
    # a file that is running on this box right now.
    if cleaned.lower().startswith("startup/"):
        cleaned = cleaned[len("startup/"):]
        for root in _roots(repo):
            if (root / cleaned).exists():
                return True
    if "/" not in cleaned.strip("/"):
        return None
    candidate = Path(cleaned)
    if candidate.is_absolute():
        return candidate.exists()
    return any((root / cleaned).exists() for root in _roots(repo))


def readings(repo: Path = REPO) -> Dict[str, object]:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise Blind("no %s -- the counts in the prompt cannot be compared to a "
                    "recording; run tools/head_state.py --write" % STATE)


def _section_start(text: str, pos: int) -> int:
    """Offset of the nearest markdown heading above `pos` (0 when there is none).

    A heading sets the context for everything under it until the next heading, so
    "measured 2026-10-31" in a caption dates the table beneath it.
    """
    starts = [m.start() for m in re.finditer(r"(?m)^#{1,4} ", text) if m.start() < pos]
    return starts[-1] if starts else 0


def check_text(text: str, *, repo: Path = REPO,
               measured: Optional[Dict[str, object]] = None,
               sha_resolves: Optional[Callable[[str], bool]] = None) -> List[str]:
    """Every defect in one prompt. Pure: no disk writes, no globals."""
    problems: List[str] = []
    measured = measured or {}

    # P1 -- the contract is present, and near the top.
    index = text.find(START_MARKER)
    if index < 0:
        problems.append("P1 START-HERE block absent (%s)" % START_MARKER)
    elif index > TOP_WINDOW:
        problems.append("P1 START-HERE block starts at char %d, past the %d-char "
                        "window: the contract is below the canon it exists to replace"
                        % (index, TOP_WINDOW))

    # P2 -- every backticked path that is an address resolves.
    for match in _PATH.finditer(text):
        raw = match.group(1)
        if resolve(raw, repo) is not False:
            continue
        if _norm(raw).startswith(OUTPUT_PREFIXES):
            continue
        line = text.count("\n", 0, match.start()) + 1
        problems.append("P2 line %d: `%s` does not exist under %s"
                        % (line, raw, " | ".join(str(r) for r in _roots(repo))))

    # P3 -- every count is either current or dated.
    for match in _COUNT.finditer(text):
        number = int(match.group(1).replace(",", ""))
        kind = match.group(2).lower().rstrip("s")
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        line = text[line_start:line_end if line_end > 0 else len(text)]
        # The date belongs to the section, not to every row of its table: a caption
        # reading "measured 2026-10-31" over forty rows is one dating act, and
        # demanding it on each row produces noise that gets the gate switched off.
        # The window must reach the END OF THE LINE as well -- a date written after
        # the number ("5,380 tests existed (measured 2026-10-30)") is the commonest
        # form there is, and a slice ending at the number fails every honest one.
        window = text[_section_start(text, match.start()):line_end]
        dated = _DATED.search(window) is not None
        key = {"test": "collected_tests", "skill": "skills"}.get(kind)
        expected = measured.get(key) if key else None
        if isinstance(expected, int) and expected:
            if abs(number - expected) / expected <= TOLERANCE:
                continue
            # A DATE IS NOT A LICENCE TO BE WRONG. Measured 2026-11-02: the prompt
            # carried "5,380 tests" under a heading that said "measured 2026-10-30",
            # so the number was dated, defensible, and 16% low -- a fresh session
            # read it as the size of the suite it was about to trust. When a
            # reading exists, a mismatch is a defect whether or not it is dated;
            # the one exemption is the word "historical", which says the figure is
            # a past reading quoted for its lesson rather than a claim about now.
            if _HISTORICAL.search(window):
                continue
            problems.append("P3 %r claims %d %ss; the recorded reading is %d%s. Fix "
                            "the number, or mark the line historical"
                            % (line.strip()[:70], number, kind, expected,
                               " (dated, but the tree moved past that date)" if dated else ""))
        elif not dated:
            problems.append("P3 %r quotes %d %ss with no recorded reading to compare "
                            "against -- measure, or mark it cached"
                            % (line.strip()[:70], number, kind))

    # P4 -- a handoff's commit resolves.
    if sha_resolves is not None:
        handoffs = sorted(repo.glob("docs/*HANDOFF*.md"), key=lambda p: p.stat().st_mtime,
                          reverse=True)
        if handoffs:
            text_h = handoffs[0].read_text(encoding="utf-8", errors="replace")
            claims = [m.group(1) for m in _SHA.finditer(text_h)]
            if not claims:
                problems.append("P4 %s names no commit at all: a handoff with no HEAD "
                                "cannot be checked" % handoffs[0].name)
            elif not any(sha_resolves(sha) for sha in claims):
                problems.append("P4 %s cites %s and none of them resolve"
                                % (handoffs[0].name, ", ".join(sorted(set(claims))[:4])))
    return list(dict.fromkeys(problems))


# --------------------------------------------------------------------------- #
# Live run
# --------------------------------------------------------------------------- #

def lane_prompts() -> List[Path]:
    home = Path.home()
    candidates = [home / "AGENTS.md", Path("C:/Azazael/AGENTS.md"),
                  home / ".config/kilo/AGENTS.md", home / ".config/kilo/BEAM_AGENTS.md",
                  home / ".config/opencode/AGENTS.md", home / ".claude/CLAUDE.md",
                  home / ".codebuff/rules.md"]
    return [path for path in candidates if path.is_file()]


def git_resolver(repo: Path = REPO) -> Callable[[str], bool]:
    """True when the commit exists, False when git ran and said it does not.

    A git that cannot RUN (absent binary, a timeout) raises Blind rather than
    answering False: "this commit does not resolve" and "I could not ask" are
    different findings, and the scanner in this repo flagged the first version of
    this function for exactly that -- `except: return False` converts an
    unrunnable instrument into a defect on the thing it was meant to measure.
    """
    def resolves(sha: str) -> bool:
        try:
            done = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"],
                                  cwd=str(repo), capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Blind("git could not run (%s), so handoff commits cannot be "
                        "resolved on this host" % exc)
        return done.returncode == 0
    return resolves


def live(json_out: bool = False, explicit: Optional[Sequence[str]] = None) -> int:
    """Judge the lane prompts. `explicit` exists for the executable control,
    which must drive this gate on a fixture whose verdict is known in advance --
    a control that can only run against whatever is on the host cannot prove the
    gate fails when it should."""
    prompts = [Path(p) for p in explicit] if explicit else lane_prompts()
    if not prompts:
        raise Blind("no lane prompt found on this host -- nothing was verified")
    measured = readings()
    resolver = git_resolver()
    findings: List[Tuple[str, str]] = []
    for path in prompts:
        text = path.read_text(encoding="utf-8", errors="replace")
        for problem in check_text(text, measured=measured, sha_resolves=resolver):
            findings.append((str(path), problem))
    if json_out:
        print(json.dumps({"ok": not findings, "prompts": [str(p) for p in prompts],
                          "findings": findings}, indent=2))
    else:
        for path, problem in findings:
            print("DEFECT %-38s %s" % (Path(path).name, problem))
        per_file: Dict[str, int] = {}
        for path, _ in findings:
            per_file[str(path)] = per_file.get(str(path), 0) + 1
        for path, count in sorted(per_file.items(), key=lambda kv: -kv[1]):
            print("%-64s %3d defect(s)" % (path, count))
        print("%s -- %d prompt(s), %d defect(s)"
              % ("clean" if not findings else "%d defects" % len(findings),
                 len(prompts), len(findings)))
    return 0 if not findings else 1


# --------------------------------------------------------------------------- #
# Controls -- both directions, because a gate that only ever says "clean" is decor
# --------------------------------------------------------------------------- #

def selftest() -> int:
    good = (START_MARKER + "\n\n" + "python tools/golden_arrow.py\n"
            "state/head.json holds the counts.\n")
    failures: List[str] = []

    def expect(name: str, text: str, *, want: str, measured: Optional[Dict] = None,
               resolver: Optional[Callable[[str], bool]] = None) -> None:
        problems = check_text(text, measured=measured if measured is not None else {},
                              sha_resolves=resolver)
        hit = [p for p in problems if p.startswith(want)]
        if want and not hit:
            failures.append("%s: expected a %s finding, got %r" % (name, want, problems))
        if not want and problems:
            failures.append("%s: expected no finding, got %r" % (name, problems))

    expect("clean prompt", good, want="")
    expect("start block absent", "python tools/golden_arrow.py\n", want="P1")
    expect("start block buried", ("x" * (TOP_WINDOW + 10)) + START_MARKER, want="P1")
    expect("path gone", good + "`tools/does_not_exist.py`\n", want="P2")
    expect("path exists", good + "`tools/golden_arrow.py`\n", want="")
    expect("stale count", good + "5,380 tests exist.\n", want="P3",
           measured={"collected_tests": 6277})
    expect("current count", good + "6,277 tests exist.\n", want="",
           measured={"collected_tests": 6277})
    # The pair that matters: a DATED stale count is still a defect (that is exactly
    # the state this gate was built to catch), while the same count marked
    # `historical` is a past reading quoted for its lesson and must pass.
    expect("count dated but stale", good + "5,380 tests existed (measured 2026-10-30).\n",
           want="P3", measured={"collected_tests": 6277})
    expect("count marked historical",
           good + "5,380 tests existed (historical: the suite has since grown).\n",
           want="", measured={"collected_tests": 6277})
    expect("skills stale", good + "1,042 skills remain.\n", want="P3",
           measured={"skills": 204})
    expect("no reading at all", good + "9,999 tests exist.\n", want="P3")

    # P4 needs a handoff file; build one in a scratch repo.
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        (root / "docs").mkdir()
        (root / "docs" / "HANDOFF_test.md").write_text("HEAD 0123456 is the commit.\n",
                                                       encoding="utf-8")
        bad = check_text(good, repo=root, sha_resolves=lambda sha: False)
        if not [p for p in bad if p.startswith("P4")]:
            failures.append("handoff with an unresolvable commit was accepted: %r" % bad)
        ok = check_text(good, repo=root, sha_resolves=lambda sha: True)
        if [p for p in ok if p.startswith("P4")]:
            failures.append("handoff with a resolving commit was refused: %r" % ok)
        (root / "docs" / "HANDOFF_test.md").write_text("no commit here\n", encoding="utf-8")
        empty = check_text(good, repo=root, sha_resolves=lambda sha: True)
        if not [p for p in empty if p.startswith("P4")]:
            failures.append("handoff naming no commit was accepted: %r" % empty)

    for failure in failures:
        print("CONTROL FAILED: " + failure)
    print("%s -- %d control(s)" % ("controls pass" if not failures else "controls failed",
                                   10 + 3))
    return 0 if not failures else 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true", help="controls only")
    parser.add_argument("--no-selftest", action="store_true",
                        help="skip the built-in controls (used by the executable control)")
    parser.add_argument("--no-live", action="store_true", help="skip the real prompts")
    parser.add_argument("--prompt", action="append", default=None, metavar="PATH",
                        help="judge this file instead of the discovered lane prompts")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if not args.no_selftest:
            rc = selftest()
            if rc != 0:
                return rc
        if args.selftest or args.no_live:
            return 0
        return live(json_out=args.json, explicit=args.prompt)
    except Blind as blind:
        print("BLIND: %s" % blind, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
