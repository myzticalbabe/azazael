# coding: utf-8
"""sword -- find, queue, fix, prove and land a sweep of one codebase.

WHAT THIS IS
------------
A runner for `aio/flaming_sword.aio.json`: the instruction object says what a
sweep is, this executes the parts a machine can execute honestly. It is written to
be pointed at a repository it has never seen, so it depends on nothing but the
standard library and `git`.

WHAT IT REFUSES
---------------
Three refusals are load-bearing, and each one is a defect this project was built
after seeing:

* **A detector that could not run is UNRUN, not clean.** "0 findings" from a
  detector that threw is the most expensive sentence in this file's history:
  it reads as a pass and licenses a destructive remedy.
* **No verification command, no landing.** A commit that fixes things without a
  command that says the project still works is a claim, and claims are worth what
  their command is worth.
* **Nothing is pushed.** Landing is local. A push is a separate declared act,
  because it is the one step that cannot be undone by `git revert` locally.

USAGE
-----
    python tools/sword.py --brief                  # the protocol: decision blocks, 12 followups
    python tools/sword.py --scan    [--root DIR] [--json]
    python tools/sword.py --plan                   # findings -> queue, ordered
    python tools/sword.py --status
    python tools/sword.py --run --batch 5 --test "python -m pytest -q" [--dry-run]
    python tools/sword.py --land                     # commit the verified batch
    python tools/sword.py --self-test               # seeded fixtures, both directions

State lives in `.flaming_sword/` beside the repository under sweep: `findings.jsonl`,
`queue.jsonl`, `batches.jsonl`. It is disposable: deleting it re-derives everything.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SPEC = HERE.parent / "aio" / "flaming_sword.aio.json"


def _sibling(name: str):
    """Load a module that lives beside this file, by path.

    `import housekeep` works when the script is run and fails when the module is
    loaded through an import spec (which is how the tests load it), so the path
    is resolved once and the module registered under its own name.
    """
    path = HERE / ("%s.py" % name)
    spec = importlib.util.spec_from_file_location("flaming_sword_%s" % name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


housekeep = _sibling("housekeep")
disposition = _sibling("disposition")
defender = _sibling("defender")
memory_bridge = _sibling("memory_bridge")


def cmd_aio(user_prompt: str, target: str, acceptance: str, evidence: str,
            defends: Sequence[str], preserve: bool, jsonl: Optional[str],
            as_json: bool) -> int:
    """The whole product in one call: prompt -> frame -> sentinel -> memory -> AIO.

    Three checks, in this order, because each catches what the previous one cannot:
    the frame refuses a prompt with no finish line, the sentinel refuses a frame whose
    paths do not resolve, and the memory says whether anything was learned before (and
    says UNMEMORED when it could not ask). No AIO is printed unless all three pass, so a
    model is never handed an instruction object built on a hole.
    """
    memory = memory_bridge.recall(user_prompt, jsonl=jsonl) if jsonl else \
        memory_bridge.probe()
    result = defender.to_aio(
        user_prompt, target=target, acceptance=acceptance, evidence=evidence,
        preserve=preserve,
        defends=defends,
        must_not_break=defender.default_break_list(target or "it"),
        control=defender.default_control(user_prompt), memory=memory)
    if as_json:
        print(json.dumps(result, indent=1, sort_keys=True))
        return 0 if result["state"].startswith("READY") else 1
    if result.get("problems"):
        print("%s: the prompt cannot become an instruction object." % result["state"])
        for problem in result["problems"]:
            print("     %s" % problem)
        print("")
        print("  the frame is where a repair stops being a removal; fill it, do not")
        print("  work around it")
        return 1
    print(result["aio"])
    return 0


def cmd_defend(intent: str, target: str, evidence: str, preserve: bool,
               as_json: bool) -> int:
    """Print the defensive frame for a change; refuse a frame that is not one.

    This is the prompter, and it runs BEFORE the change so the frame cannot become a
    rationalisation of work already done. It never fills a missing field in: a frame
    that cannot name what it defends is the shape in which a repair turns into a
    removal, so it is reported as REFUSED and the exit code says so.
    """
    # No evidence and no acceptance means the frame does not exist yet: emit the DRAFT
    # with every hole marked rather than a strict frame that would be refused for
    # being empty. The two paths cannot be confused -- one says DRAFT -- NOT A FRAME.
    if not evidence:
        skeleton = defender.draft(intent, target, preserve=preserve)
        if as_json:
            print(json.dumps(skeleton, indent=1, sort_keys=True))
        else:
            print(skeleton["prompt"])
        return 0
    frame = defender.frame(
        intent=intent,
        target=target or "<target not named>",
        evidence=evidence,
        defends=["<name what survives: a test, a claim, a gate>"],
        must_not_break=defender.default_break_list(target or "it"),
        acceptance="",
        control=defender.default_control(intent),
        preserve=preserve,
        posture=defender.default_posture() if preserve else None,
    )
    if as_json:
        print(json.dumps(frame, indent=1, sort_keys=True))
        return 0 if not frame.get("problems") else 1
    if frame.get("problems"):
        print("REFUSED: this is not a frame yet.")
        for problem in frame["problems"]:
            print("     %s" % problem)
        print("")
        print("  pass --defend with a named defence, an acceptance command and an")
        print("  evidence path; the frame is the thing the sweep is judged against")
        return 1
    print(frame["prompt"])
    return 0


def record_error(root: Path, stage: str, kind: str, subject: str, what: str,
                 evidence: str = "", remedy: str = "") -> Optional[Dict]:
    """Turn one error into one task, the moment it is found.

    A ledger that cannot be written must not take the sweep down with it, and it
    must not fail silently either: the warning is printed and the row is missing,
    which the reader can see. `suppress` keeps the anti-pattern scanner honest
    about what this actually is -- a report path, not an error swallow.
    """
    with contextlib.suppress(OSError):
        return disposition.record(root, stage, kind, subject, what, evidence, remedy)
    print("  WARNING: could not record this error in %s/%s" % (STATE_DIR, disposition.LEDGER))
    return None
STATE_DIR = ".flaming_sword"

#: Directories a sweep does not edit. Archives are history and vendored code is
#: somebody else's tree: proposing edits there produces findings that can never be
#: fixed, which is how a report becomes noise. Both are named rather than matched
#: by pattern, so adding one is a decision somebody makes.
SKIP_DIRS = {".git", "node_modules", "venv", "venvs", ".venv", ".venvs", "__pycache__",
             "site-packages", "dist", "build", ".mypy_cache", ".pytest_cache", "logs",
             "archive", "archived", "archived_unified", "nuitka_build_backup",
             "inline_copy", "vendor", "third_party", ".agents", "skills.pkg-archive"}
MAX_MARKDOWN = 400
MAX_PYTHON = 4000
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

CODE_BLOCK_FENCE = re.compile(r"^\s*(```|~~~)")
COMMAND_PATH = re.compile(r"\b(?:python3?|py|node|bash|sh|pwsh)\s+([A-Za-z0-9_./\\-]+"
                          r"\.(?:py|js|mjs|sh|ps1|bat))")
TICK_PATH = re.compile(r"`([A-Za-z0-9_./\\-]+\.(?:py|js|mjs|sh|ps1|json|ya?ml|md))`")
CONSTANT_ASSIGN = re.compile(r"^\s*([A-Z][A-Z0-9_]{3,})\s*=\s*(-?\d+(?:\.\d+)?)\s*(?:#.*)?$")
#: The shape this estate actually ships: `NAME = float(os.environ.get("NAME", "0.89"))`.
#: A detector that only understood `NAME = 0.89` was blind to every floor, port and
#: budget in the tree, because the canonical form of a tunable is an env default and
#: not a bare assignment -- and a copy of that default in a second file is exactly
#: the defect this detector exists for.
ENV_DEFAULT = re.compile(r"os\.environ\.get\(\s*[\"']([A-Z][A-Z0-9_]{3,})[\"']\s*,\s*"
                         r"[\"'](-?\d+(?:\.\d+)?)[\"']")
#: `NAME = ...` (optionally annotated). A line that merely CONTAINS the call is
#: not a definition, so it does not count as a source of the value.
ENV_ASSIGN = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*(?::[^=\n]+)?=\s*\S")
BARE_PYTEST = re.compile(r"\bpython\s+-m\s+pytest\b")
EXPLICIT_INTERPRETER = re.compile(r"(?:[A-Za-z]:[\\/][^\s`]*python(?:\.exe)?"
                                  r"|(?:^|[\s`])\.?\.?venvs?/[^\s`]*python"
                                  r"|/usr/(?:local/)?bin/python)")
FIGURE_WORDS = re.compile(r"\b\d{2,}(?:[,\s]\d{3})*\s+(?:gates?|tests?|books?|verses?|"
                          r"claims?|hooks?|checks?|files?)\b")
TEST_INVOCATION = re.compile(r"\b(pytest|npm\s+test|yarn\s+test|go\s+test|cargo\s+test|"
                             r"jest|vitest|tox|nox)\b")
#: A `run:` step that invokes a script in this repository. A ratchet gate is not
#: a test suite, but it is also not "nothing": measured on the home tree, both
#: workflows reported as untested run real gates (`check_no_catch_alls.py`,
#: `anti_pattern_gate.py --check`, `canon_drift_check.py`) that can fail the build.
GATE_INVOCATION = re.compile(r"\bpython3?\s+((?:tools|scripts|src)/[A-Za-z0-9_./-]+\.py)")


# --------------------------------------------------------------------------- #
# Findings
# --------------------------------------------------------------------------- #

def _finding(detector: str, path: Path, line: int, evidence: str, severity: str,
             remedy: str, auto: bool = False, root: Optional[Path] = None,
             detail: str = "") -> Dict:
    rel = path
    if root is not None:
        try:
            rel = path.resolve().relative_to(root.resolve())
        except ValueError:
            rel = path
    digest = hashlib.sha1(("%s|%s|%d|%s" % (detector, rel, line, evidence[:80]))
                          .encode("utf-8")).hexdigest()[:12]
    return {
        "id": "%s:%s" % (detector, digest),
        "detector": detector,
        "severity": severity,
        "path": str(rel).replace("\\", "/"),
        "line": int(line),
        "evidence": evidence.strip()[:300],
        "remedy": remedy,
        "auto": bool(auto),
        "detail": detail,
        "status": "open",
    }


def iter_files(root: Path, pattern: str, limit: int) -> Iterable[Path]:
    count = 0
    for path in sorted(root.rglob(pattern)):
        if count >= limit:
            return
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        count += 1
        yield path


def code_block_lines(path: Path) -> Iterable[Tuple[int, str]]:
    """Only fenced-block lines. A path in prose may be an example; a path in a
    block is an instruction somebody will paste."""
    # A document that cannot be read yields no instruction lines. `suppress`
    # says so deliberately rather than swallowing an error and looking healthy:
    # the caller sees an empty iterable, not a fabricated finding.
    text = ""
    with contextlib.suppress(OSError):
        text = path.read_text(encoding="utf-8", errors="replace")
    inside = False
    for number, line in enumerate(text.splitlines(), start=1):
        if CODE_BLOCK_FENCE.match(line):
            inside = not inside
            continue
        if inside:
            yield number, line


# --------------------------------------------------------------------------- #
# Detectors. Each returns (findings, ran: bool, note)
# --------------------------------------------------------------------------- #

def detect_phantom_reference(root: Path) -> Tuple[List[Dict], bool, str]:
    findings: List[Dict] = []
    for path in iter_files(root, "*.md", MAX_MARKDOWN):
        for number, line in code_block_lines(path):
            tokens = COMMAND_PATH.findall(line) + TICK_PATH.findall(line)
            for token in tokens:
                clean = token.replace("\\", "/").strip()
                if not clean or any(ch in clean for ch in "<>*$%{}"):
                    continue
                if clean.startswith(("/", "http", "logs/")) or clean.startswith(".."):
                    continue
                # Placeholders are not instructions. `path/to/file.py` in a
                # template is a template, and reporting it trains the reader to
                # ignore the detector.
                if any(marker in clean for marker in ("path/to/", "your_", "example_")):
                    continue
                # Resolve from the document's own directory first, then the repo
                # root. A skill's `bin/x.mjs` is relative to the skill, and a
                # detector that only tries the root reports 132 phantom commands
                # that are all correct -- precision is the whole value here.
                if (path.parent / clean).exists() or (root / clean).exists():
                    continue
                findings.append(_finding(
                    "phantom-reference", path, number, line,
                    "high",
                    "replace `%s` with a command that exists, or delete the block "
                    "(a reader copies this line and it fails)" % clean,
                    root=root, detail=clean))
    return findings, True, ""


def numeric_key(value: str) -> str:
    try:
        return repr(float(value))
    except ValueError:
        return value


def constant_values(line: str) -> List[Tuple[str, str]]:
    """Every (name, numeric value) a single source line pins.

    Two forms count, and they are both "a value somebody will copy":
    `NAME = 0.89` and `os.environ.get("NAME", "0.89")`. The second is matched by
    the ENV name, not the local variable, because `MIN_BEST` in one file and
    `QUERY_FLOOR` in another can both carry the same env default -- the names
    differ, the setting does not.
    """
    values: List[Tuple[str, str]] = []
    match = CONSTANT_ASSIGN.match(line)
    if match:
        values.append((match.group(1), match.group(2)))
    # An env default only counts where the line IS an assignment. Without this
    # the pattern also matches its own test fixtures -- a test that writes
    # `'FLOOR = float(os.environ.get("X", "0.70"))'` into a scratch file is 
    # test data, not a second copy of the setting, and reporting it is the false
    # positive that gets a watchlist abandoned.
    if ENV_ASSIGN.match(line):
        for name, value in ENV_DEFAULT.findall(line):
            values.append((name, value))
    return values


def detect_duplicate_constant(root: Path) -> Tuple[List[Dict], bool, str]:
    """WATCHLIST ONLY, and that is the whole design.

    Scanning for `NAME = <number>` in two files produced 45 findings on this tree
    and almost all were false: `BLACK = 30` in one colour module and `BLACK = 0`
    in another are two different settings that happen to share a name. A detector
    whose precision is that low is not a detector, it is a nuisance that gets
    switched off -- and a detector that gets switched off protects nothing.

    So the sweep is told which constants must be single-sourced. No watchlist is
    UNRUN with a reason, never "0 findings".
    """
    watch = [name for name in (read_config(root).get("constants") or [])]
    if not watch:
        return [], False, ("no constants watchlist: declare `constants` in "
                           "%s/config.json to say which values must be single-sourced"
                           % STATE_DIR)
    seen: Dict[str, List[Tuple[Path, int, str, str]]] = {}
    for path in iter_files(root, "*.py", MAX_PYTHON):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for name, value in constant_values(line):
                if name in watch:
                    seen.setdefault(name, []).append((path, number, value, line))
    findings: List[Dict] = []
    for name, entries in seen.items():
        # Compared numerically: a copy written as `0.7` and one written as `0.70`
        # are the same threshold, and calling that a divergence is the false
        # positive that gets a watchlist abandoned.
        values = {numeric_key(value) for _p, _n, value, _l in entries}
        if len(values) < 2:
            continue
        where = "; ".join("%s:%d = %s" % (p.relative_to(root).as_posix(), n, v)
                          for p, n, v, _l in entries[:6])
        first_path, first_line, _v, first_text = entries[0]
        findings.append(_finding(
            "duplicate-constant", first_path, first_line, first_text,
            "high",
            "%s holds %d different values (%s). Pick the source, import it in the "
            "other file, and re-run whatever measured it -- two copies that agree "
            "today disagree after the next edit" % (name, len(values), where),
            root=root, detail=name))
    return findings, True, ""


def detect_hooks_unwired(root: Path) -> Tuple[List[Dict], bool, str]:
    hooks = root / ".githooks"
    if not hooks.is_dir():
        return [], True, "no .githooks directory: nothing to wire"
    try:
        completed = subprocess.run(["git", "config", "core.hooksPath"],
                                   cwd=str(root), capture_output=True, text=True,
                                   timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], False, "git could not be run (%s)" % type(exc).__name__
    value = (completed.stdout or "").strip()
    if value in (".githooks", str(hooks)):
        return [], True, ""
    finding = _finding(
        "hooks-unwired", root / ".githooks", 0,
        "core.hooksPath is %r" % (value or "unset"),
        "high",
        "git config core.hooksPath .githooks",
        auto=True, root=root,
        detail="tracked gates in .githooks never run; a clone runs whatever is in "
               ".git/hooks, which is untracked and may be stale")
    return [finding], True, ""


#: Probed once per (interpreter, module) for the life of the process. The fact
#: is about this host, not about the tree being swept, so it survives a rescan.
_INTERPRETER_PROBE: Dict[Tuple[str, str], bool] = {}


def interpreter_can(interpreter: str, module: str) -> bool:
    """Can this interpreter import `module`? A documented command must be able
    to run where the page sends the reader, and that is checkable in 60 ms."""
    key = (interpreter, module)
    if key not in _INTERPRETER_PROBE:
        try:
            done = subprocess.run([interpreter, "-c", "import %s" % module],
                                  capture_output=True, text=True, timeout=60)
            _INTERPRETER_PROBE[key] = done.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            _INTERPRETER_PROBE[key] = False
    return _INTERPRETER_PROBE[key]


def detect_two_interpreters(root: Path) -> Tuple[List[Dict], bool, str]:
    """A page that names the exact interpreter and then runs a bare `python`.

    This one is auto-fixable only while the replacement is not a guess: the
    interpreter must be the literal already written in the same file, and there
    must be exactly ONE such literal. Measured on the home tree: CAPABILITIES.md
    names a ComfyUI venv, a `.pmb-venv` and a production interpreter, and the
    "most frequent wins" rule would have rewritten a production command to run
    under ComfyUI's python. A page with several interpreters is a proposal, not a
    fix, and it says which candidates it saw.
    """
    findings: List[Dict] = []
    for path in iter_files(root, "*.md", MAX_MARKDOWN):
        bare: List[Tuple[int, str]] = []
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        declared = EXPLICIT_INTERPRETER.findall(text)
        if not declared:
            continue
        candidates = sorted({item.strip() for item in declared})
        if len(candidates) > 1:
            for number, line in code_block_lines(path):
                if not BARE_PYTEST.search(line):
                    continue
                findings.append(_finding(
                    "two-interpreters", path, number, line, "medium",
                    "this page names %d interpreters (%s): say which one the bare "
                    "`python` means, and nothing here guesses between them"
                    % (len(candidates), ", ".join(candidates[:4])),
                    auto=False, root=root, detail="ambiguous"))
            continue
        interpreter = candidates[0]
        usable = interpreter_can(interpreter, "pytest")
        for number, line in code_block_lines(path):
            if BARE_PYTEST.search(line):
                bare.append((number, line))
        for number, line in bare[:5]:
            if usable:
                findings.append(_finding(
                    "two-interpreters", path, number, line, "medium",
                    "replace `python -m pytest` with `%s -m pytest`, or say that the "
                    "bare `python` is the intended target" % interpreter,
                    auto=True, root=root, detail=interpreter))
            else:
                # Measured: CAPABILITIES.md names exactly one interpreter
                # (a `.pmb-venv` python) and it answers "No module named
                # pytest". Rewriting the line to it would document a command
                # that fails, so the fix is not offered at all.
                findings.append(_finding(
                    "two-interpreters", path, number, line, "medium",
                    "the only interpreter this page names (%s) cannot import "
                    "pytest, so it is not the one that runs this line: name the "
                    "interpreter that does" % interpreter,
                    auto=False, root=root, detail="interpreter-lacks-pytest"))
    return findings, True, ""


def detect_untested_ci(root: Path) -> Tuple[List[Dict], bool, str]:
    workflows = list((root / ".github" / "workflows").glob("*.y*ml"))
    if not workflows:
        return [], True, "no .github/workflows"
    has_tests = any((root / name).exists() for name in ("tests", "test", "spec"))
    if not has_tests:
        return [], True, "no test directory: CI cannot be blamed for skipping one"
    findings = []
    for workflow in workflows:
        try:
            text = workflow.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if TEST_INVOCATION.search(text):
            continue
        # A workflow that never checks the repository out cannot run its tests, so
        # it is not a CI-without-tests defect: it is a guard, a labeler, or a
        # notice. Reporting it would be the false positive that gets this detector
        # switched off, which is how a real missing test step stops being seen.
        if "actions/checkout" not in text:
            continue
        # A gate script that exists verifies something. The predicate is "this
        # CI runs nothing", not "this CI does not spell pytest" -- and the
        # second one is how a working ratchet gets reported as a dead workflow,
        # which trains the reader to ignore the whole detector.
        gates = [name for name in GATE_INVOCATION.findall(text) if (root / name).exists()]
        if gates:
            continue
        findings.append(_finding(
            "untested-ci", workflow, 1, "no test or gate invocation in this workflow",
            "medium",
            "add the step, or delete the workflow: a green CI that runs nothing "
            "is worse than no CI", root=root))
    return findings, True, ""


def detect_stale_claims(root: Path) -> Tuple[List[Dict], bool, str]:
    config = read_config(root)
    claims = (config.get("claims") or {})
    command = claims.get("command")
    ledger = claims.get("ledger")
    if not command:
        # NOT `ran=True`. A detector with nothing to run has found nothing, and
        # "0 findings" from a detector that could not run is the exact sentence
        # this project exists to prevent -- it was reporting itself clean here
        # until 2026-11-01.
        return [], False, ("no claims.command configured: nothing was run, so this "
                           "is unknown, not clean")
    if ledger and not (root / ledger).exists():
        return [], False, "claims ledger %s is absent" % ledger
    try:
        completed = subprocess.run([str(part) for part in command], cwd=str(root),
                                   capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], False, "claims command could not run (%s)" % type(exc).__name__
    if completed.returncode == 0:
        return [], True, ""
    tail = ((completed.stdout or "") + (completed.stderr or "")).strip().splitlines()
    evidence = tail[-1] if tail else "exit %d" % completed.returncode
    return [_finding("stale-claims", root / (ledger or "."), 0, evidence, "high",
                     "fix the page or the code; never delete the claim to make the "
                     "run green -- that is how a guide stops being checked",
                     root=root)], True, ""


def detect_figure_without_command(root: Path) -> Tuple[List[Dict], bool, str]:
    """Advisory, and capped: a figure may be a quotation of somebody else's
    measurement, so this reports and never edits."""
    findings: List[Dict] = []
    for path in iter_files(root, "*.md", MAX_MARKDOWN):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for index, line in enumerate(lines):
            if not FIGURE_WORDS.search(line) or "`" in line:
                continue
            window = lines[max(0, index - 5): index + 6]
            if any("`" in neighbour or "```" in neighbour for neighbour in window):
                continue
            findings.append(_finding(
                "figure-without-command", path, index + 1, line, "low",
                "cite the command that produced the figure, or drop the number",
                root=root))
            if len(findings) >= 50:
                return findings, True, "capped at 50 findings"
    return findings, True, ""


DETECTORS = (
    ("phantom-reference", detect_phantom_reference),
    ("duplicate-constant", detect_duplicate_constant),
    ("hooks-unwired", detect_hooks_unwired),
    ("two-interpreters", detect_two_interpreters),
    ("untested-ci", detect_untested_ci),
    ("stale-claims", detect_stale_claims),
    ("figure-without-command", detect_figure_without_command),
)


# --------------------------------------------------------------------------- #
# State
# --------------------------------------------------------------------------- #

def state_dir(root: Path) -> Path:
    path = root / STATE_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_config(root: Path) -> Dict:
    path = root / STATE_DIR / "config.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_jsonl(path: Path, rows: Sequence[Dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                    encoding="utf-8")


def read_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def scan(root: Path, disabled: Sequence[str] = ()) -> Tuple[List[Dict], List[str]]:
    findings: List[Dict] = []
    unrun: List[str] = []
    for name, detector in DETECTORS:
        if name in disabled:
            unrun.append("%s: disabled by config (not run, not clean)" % name)
            continue
        try:
            produced, ran, note = detector(root)
        except Exception as exc:                     # noqa: BLE001 - reported, never swallowed
            unrun.append("%s: UNRUN (%s: %s)" % (name, type(exc).__name__, exc))
            record_error(root, "scan", "detector-crashed", name,
                         "%s raised %s: %s" % (name, type(exc).__name__, exc),
                         evidence=repr(exc),
                         remedy="fix the detector, or disable it explicitly in config")
            continue
        if not ran:
            unrun.append("%s: UNRUN (%s)" % (name, note or "no reason given"))
            record_error(root, "scan", "detector-unrun", name,
                         "%s could not run: %s" % (name, note or "no reason given"),
                         remedy="supply what %s needs in %s/config.json, or say why it "
                                "is off: %s"
                                % (name, STATE_DIR, note or "no reason given"))
            continue
        findings.extend(produced)
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["detector"],
                                 f["path"], f["line"]))
    return findings, unrun


def plan(root: Path) -> List[Dict]:
    config = read_config(root)
    findings, unrun = scan(root, config.get("detectors", {}).get("disable", []))
    previous = {row["id"]: row for row in read_jsonl(state_dir(root) / "queue.jsonl")}
    queue = []
    for finding in findings:
        prior = previous.get(finding["id"])
        # A queue entry keeps the status it earned: re-planning must not reopen
        # work that was fixed, or a resumed sweep re-does its own commits.
        if prior and prior.get("status") in ("fixed", "proposed", "skipped"):
            finding["status"] = prior["status"]
        queue.append(finding)
    queue.sort(key=lambda row: (0 if row["status"] == "open" else 1,
                                SEVERITY_ORDER.get(row["severity"], 9),
                                0 if row["auto"] else 1, row["path"], row["line"]))
    write_jsonl(state_dir(root) / "findings.jsonl", findings)
    write_jsonl(state_dir(root) / "queue.jsonl", queue)
    if unrun:
        (state_dir(root) / "unrun.txt").write_text("\n".join(unrun) + "\n", encoding="utf-8")
    return queue


def apply_fix(root: Path, item: Dict) -> Tuple[bool, str, Optional[str]]:
    """Two mechanical fixes exist. Both are reversible, and neither guesses.

    Returns (ok, what happened, the file this fix touched or None). A fix that
    touched no file is a local configuration change: it is real, and it cannot be
    landed, which `land` says out loud rather than committing nothing.
    """
    if item["detector"] == "hooks-unwired":
        try:
            subprocess.run(["git", "config", "core.hooksPath", ".githooks"],
                           cwd=str(root), check=True, capture_output=True, timeout=30)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            return False, "git config failed (%s)" % type(exc).__name__, None
        return True, "core.hooksPath set to .githooks (local config: not landable)", None

    if item["detector"] == "two-interpreters":
        interpreter = item.get("detail") or ""
        target = root / item["path"]
        if not interpreter or not target.is_file():
            return False, "the declared interpreter or the file is gone", None
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        index = item["line"] - 1
        if index < 0 or index >= len(lines) or "python -m pytest" not in lines[index]:
            return False, "the line moved since the scan; re-run --plan", None
        lines[index] = lines[index].replace("python -m pytest",
                                            "%s -m pytest" % interpreter, 1)
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True, "bare `python -m pytest` -> `%s -m pytest`" % interpreter, item["path"]

    return False, "no mechanical fixer for %s" % item["detector"], None


def run_batch(root: Path, size: int, test_command: Optional[str],
              dry_run: bool = False) -> int:
    queue = read_jsonl(state_dir(root) / "queue.jsonl")
    open_items = [item for item in queue if item["status"] == "open"]
    batch = [item for item in open_items if item["auto"]][:size]
    proposed = [item for item in open_items if not item["auto"]]

    print("DECISION  run batch")
    print("  batch:     %d auto-fixable item(s), %d propose-only left alone"
          % (len(batch), len(proposed)))
    print("  test:      %s" % (test_command or "NOT DECLARED (landing will be refused)"))
    print("  rollback:  git checkout -- <touched paths>")
    print("")
    if not batch:
        print("nothing auto-fixable in the queue. %d item(s) need a human decision:"
              % len(proposed))
        for item in proposed[:12]:
            print("  - [%s] %s:%d  %s" % (item["severity"], item["path"], item["line"],
                                          item["remedy"].split("\n")[0][:110]))
        if len(proposed) > 12:
            print("  ... and %d more" % (len(proposed) - 12))
        return 0

    touched: List[str] = []
    applied: List[Dict] = []
    failed: List[Dict] = []
    for item in batch:
        if dry_run:
            print("  would fix %-34s %s:%d" % (item["id"], item["path"], item["line"]))
            continue
        ok, note, touched_path = apply_fix(root, item)
        print("  %-4s %-34s %s" % ("fix" if ok else "FAIL", item["id"], note))
        if ok:
            item["status"] = "fixed"
            applied.append(item)
            if touched_path:
                touched.append(touched_path)
        else:
            failed.append(item)
            record_error(root, "fix", "fix-failed", item["id"], note,
                         evidence="%s:%d %s" % (item["path"], item["line"],
                                                item["detector"]),
                         remedy=item.get("remedy", ""))

    if dry_run:
        return 0
    write_jsonl(state_dir(root) / "queue.jsonl", queue)
    record = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "fixed": [i["id"] for i in applied], "failed": [i["id"] for i in failed],
              "touched": sorted(set(touched)), "test": test_command,
              "verified": None, "landed": None}
    with (state_dir(root) / "batches.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")

    # Re-run the detectors that produced this batch. A fix whose own detector
    # still fires is a failed fix, whatever the suite says.
    after, unrun = scan(root)
    still = {item["id"] for item in after}
    regressed = [item["id"] for item in applied if item["id"] in still]
    if regressed:
        print("\n  FAILED: %d fixed item(s) still fire after the fix: %s"
              % (len(regressed), ", ".join(regressed)))
        for item_id in regressed:
            record_error(root, "fix", "fix-ineffective", item_id,
                         "the detector still fires after its own fix",
                         remedy="the fix was cosmetic: re-open it and look again")
        return 1
    if unrun:
        print("\n  UNRUN (not clean, just unknown):")
        for note in unrun:
            print("    - %s" % note)
    print("\n  %d item(s) fixed; %d propose-only still open" % (len(applied), len(proposed)))
    return 0


#: A verification command is bounded. A suite that wedges must fail the landing,
#: not hold the terminal open until somebody kills it.
VERIFY_TIMEOUT = 3600


def split_command(command: str) -> List[str]:
    """Split a declared command into argv WITHOUT a shell.

    `shell=True` would turn an operator-typed command into an interpreted one:
    pipelines, redirection and `&&` become possible, and a path with a space or a
    semicolon changes meaning. The declared commands this takes are argv-shaped,
    so a split is enough and the class disappears. On Windows the non-posix split
    keeps backslashes intact; on POSIX the quoting rules apply as written.
    """
    if sys.platform == "win32":
        return [part.strip('"') for part in shlex.split(command, posix=False)]
    return shlex.split(command, posix=True)


def land(root: Path, test_command: Optional[str]) -> int:
    if not test_command:
        print("REFUSED: no --test command. A commit that fixes things without a")
        print("command that says the project still works is a claim, not a landing.")
        record_error(root, "land", "refused", "no-test-command",
                     "a landing was attempted with no verification command",
                     remedy="pass --test with the project's own command")
        return 1
    batches = read_jsonl(state_dir(root) / "batches.jsonl")
    if not batches:
        print("REFUSED: no batch recorded. Run --run first.")
        record_error(root, "land", "refused", "no-batch",
                     "a landing was attempted with no batch on record",
                     remedy="run --run to apply and record a batch first")
        return 1
    batch = batches[-1]
    if batch.get("landed"):
        print("REFUSED: batch already landed at %s" % batch["landed"])
        record_error(root, "land", "refused", "already-landed",
                     "the same batch was offered twice (landed at %s)" % batch["landed"],
                     remedy="nothing to do: the batch is in history")
        return 1
    touched = batch.get("touched") or []
    if not touched:
        print("REFUSED: the batch touched no file, so there is nothing to land.")
        print("What it changed was local git configuration (hooksPath), which no")
        print("commit records. Either re-run --scan so a file fix joins the batch,")
        print("or record the config change in the run report and land nothing.")
        record_error(root, "land", "refused", "nothing-touched",
                     "the batch changed only local git configuration",
                     remedy="run a batch that edits a file, or record the config change")
        return 1

    print("verifying: %s" % test_command)
    started = time.monotonic()
    argv = split_command(test_command)
    if not argv:
        print("REFUSED: the verification command is empty.")
        return 1
    completed = subprocess.run(argv, cwd=str(root), capture_output=True, text=True,
                               timeout=VERIFY_TIMEOUT)
    elapsed = time.monotonic() - started
    tail = ((completed.stdout or "") + (completed.stderr or "")).strip().splitlines()
    summary = tail[-1] if tail else "no output"
    print("  exit %d in %.1fs: %s" % (completed.returncode, elapsed, summary[:200]))
    if completed.returncode != 0:
        print("\nREFUSED: the verification command failed. The batch is NOT landed.")
        print("Roll back or fix, then re-run. A red suite never lands.")
        record_error(root, "land", "verification-red", "batch-%d" % len(batches),
                     "the project's own command failed: %s" % summary.strip()[:200],
                     evidence="%s -> exit %d" % (test_command, completed.returncode),
                     remedy="roll back, or fix the cause; never land on red")
        return 1

    batch_index = len(batches)
    message = ("Fix %d finding(s) from a FLAMING SWORD sweep (batch %d)\n\n%s\n\n"
               "Verified: %s -> %s"
               % (len(batch.get("fixed") or []), batch_index,
                  "\n".join("- " + item for item in (batch.get("fixed") or [])),
                  test_command, summary.strip()[:200]))
    staged = subprocess.run(["git", "add", "--", *touched], cwd=str(root),
                            capture_output=True, text=True, timeout=120)
    if staged.returncode != 0:
        print("REFUSED: git add failed: %s" % (staged.stderr or "").strip()[:200])
        record_error(root, "land", "git-add-failed", "batch-%d" % len(batches),
                     "git add refused the batch's touched paths",
                     evidence=(staged.stderr or "").strip()[:300])
        return 1
    # The pathspec is not decoration: a plain `git commit` carries every staged
    # file, so an unrelated change somebody staged before the sweep would land
    # under this batch's message and its Verified: line.
    commit = subprocess.run(["git", "commit", "-m", message, "--", *touched],
                            cwd=str(root), capture_output=True, text=True, timeout=600)
    if commit.returncode != 0:
        print("REFUSED: git commit failed: %s" % (commit.stderr or "").strip()[:300])
        return 1
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(root),
                         capture_output=True, text=True, timeout=60).stdout.strip()
    batch["landed"] = sha
    batch["verified"] = summary.strip()[:200]
    batches[-1] = batch
    write_jsonl(state_dir(root) / "batches.jsonl", batches)
    print("landed batch %d as %s (not pushed: pushing is a separate, declared act)"
          % (batch_index, sha))
    return 0


RESEARCH_FIELDS = ("theme", "query", "url", "tier", "finding", "adaptation",
                   "removes", "verify_command")


def record_research(root: Path, source: Path) -> int:
    """Validate and queue what the agent found. Never applies it.

    The runner cannot browse, so this is the seam where a deep search becomes a
    queue entry instead of a paragraph in a chat. Validation is the point: a
    record with no `verify_command` is a wish, and a tier-D record may not license
    a change to code that currently works.
    """
    if not source.exists():
        print("REFUSED: %s does not exist" % source)
        return 1
    problems: List[str] = []
    accepted: List[Dict] = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append("line %d: not JSON (%s)" % (number, exc))
            continue
        missing = [field for field in RESEARCH_FIELDS if not record.get(field)]
        if missing:
            problems.append("line %d: missing %s" % (number, ", ".join(missing)))
            continue
        if record["tier"] not in ("A", "B", "C", "D"):
            problems.append("line %d: tier must be A, B, C or D" % number)
            continue
        if not str(record["url"]).startswith(("http://", "https://")):
            problems.append("line %d: url is not http(s)" % number)
            continue
        record["id"] = "research:%s" % hashlib.sha1(
            (record["theme"] + record["url"]).encode("utf-8")).hexdigest()[:12]
        record["detector"] = "research"
        record["severity"] = "low"
        record["auto"] = False
        record["status"] = "proposed"
        record["path"] = record.get("removes", "")
        record["line"] = 0
        record["evidence"] = "[tier %s] %s" % (record["tier"], record["finding"][:200])
        record["remedy"] = ("%s | replaces: %s | verify: %s"
                            % (record["adaptation"], record["removes"],
                               record["verify_command"]))
        accepted.append(record)
    if problems:
        print("REFUSED: %d record(s) failed validation:" % len(problems))
        for problem in problems:
            print("  - %s" % problem)
        return 1
    queue_path = state_dir(root) / "queue.jsonl"
    queue = read_jsonl(queue_path)
    known = {item["id"] for item in queue}
    added = [record for record in accepted if record["id"] not in known]
    write_jsonl(queue_path, queue + added)
    write_jsonl(state_dir(root) / "research.jsonl", accepted)
    tiers: Dict[str, int] = {}
    for record in accepted:
        tiers[record["tier"]] = tiers.get(record["tier"], 0) + 1
    print("%d research record(s) accepted (%s), %d newly queued as proposals."
          % (len(accepted), ", ".join("tier %s: %d" % (t, n) for t, n in sorted(tiers.items())),
             len(added)))
    print("They are PROPOSALS: --run never applies them, and tier D may not license")
    print("a change to code that currently works.")
    return 0


def brief() -> int:
    print("== FLAMING SWORD -- the operating brief ==")
    print("")
    spec = json.loads(SPEC.read_text(encoding="utf-8")) if SPEC.exists() else {}
    protocol = spec.get("protocol", {})
    for block in protocol.get("decision_blocks", []):
        print("-- decision block: %s" % block["id"])
        print("   emit when: %s" % block["emit_when"])
        for line in block["template"].splitlines():
            print("   %s" % line)
        print("   rule: %s" % block.get("rule", ""))
        print("")
    followups = protocol.get("followups", {})
    print("-- followups: exactly %d, %s" % (followups.get("count", 12),
                                            followups.get("shape", "")))
    for forbidden in followups.get("forbidden", []):
        print("   forbidden: %s" % forbidden)
    print("   %s" % followups.get("counting_rule", ""))
    print("")
    print("-- stages: %s" % " -> ".join(stage["id"] for stage in
                                        sorted(spec.get("stages", []),
                                               key=lambda s: s["order"])))
    ledger = protocol.get("disposition", {})
    print("-- errors: %s" % ledger.get("rule", ""))
    print("   captured: %s" % ", ".join(ledger.get("captured", [])[:3]) + " ...")
    print("   --tasks to read them, --dispose <id> --as <%s> to close one"
          % "|".join(ledger.get("dispositions", disposition.DISPOSITIONS)))
    print("")
    house = next((stage for stage in spec.get("stages", [])
                  if stage.get("id") == "housekeep"), None)
    print("-- housekeep: dry run unless --apply; %s"
          % (house.get("does", "") if house else ""))
    print("-- limits: %s" % ", ".join(spec.get("limits", {}).get("forbidden", [])[:3]))
    return 0


def self_test() -> int:
    """Seeded fixtures in both directions: every detector must fire on a broken
    tree and stay silent on a clean one. An oracle tested only on clean input is
    indistinguishable from one that does nothing."""
    failures: List[str] = []

    def git(args, cwd):
        return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                              text=True, timeout=120)

    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / "broken"
        clean = Path(tmp) / "clean"
        for root in (broken, clean):
            root.mkdir()
            git(["init", "-q"], root)
            git(["config", "user.email", "sweep@example.invalid"], root)
            git(["config", "user.name", "sweep"], root)

        # -- broken: one seam per detector
        (broken / ".githooks").mkdir()
        (broken / ".githooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (broken / "docs").mkdir()
        (broken / "docs" / "install.md").write_text(
            "# Install\n\n```bash\npython tools/does_not_exist.py\n```\n\n"
            "```bash\npython -m pytest tests/ -q\n```\n\n"
            "```bash\n%s -m pytest tests/ -q\n```\n" % sys.executable,
            encoding="utf-8")
        (broken / "tools").mkdir()
        (broken / "tools" / "a.py").write_text("FLOOR = 0.89\n", encoding="utf-8")
        (broken / "tools" / "b.py").write_text("FLOOR = 0.70\n", encoding="utf-8")
        (broken / STATE_DIR).mkdir()
        (broken / STATE_DIR / "config.json").write_text(
            json.dumps({"constants": ["FLOOR"],
                        "claims": {"ledger": "claims.json",
                                   "command": [sys.executable, "-c", "pass"]}}),
            encoding="utf-8")
        (broken / "claims.json").write_text("{}\n", encoding="utf-8")
        (broken / "tests").mkdir()
        (broken / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n",
                                                    encoding="utf-8")
        (broken / ".github" / "workflows").mkdir(parents=True)
        (broken / ".github" / "workflows" / "ci.yml").write_text(
            "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - uses: actions/checkout@v4\n      - run: echo hello\n",
            encoding="utf-8")
        (broken / "README.md").write_text(
            "The tree carries 15 gates and 42 tests.\n", encoding="utf-8")
        git(["add", "-A"], broken)
        git(["commit", "-qm", "seed"], broken)

        findings, unrun = scan(broken)
        fired = {item["detector"] for item in findings}
        for expected in ("phantom-reference", "duplicate-constant", "hooks-unwired",
                         "two-interpreters", "untested-ci"):
            if expected not in fired:
                failures.append("%s did not fire on the seeded tree" % expected)
        if not any("UNRUN" in note for note in unrun) and unrun:
            failures.append("an unrun detector was reported without the word UNRUN")

        # -- clean: same shape, no defects
        (clean / ".githooks").mkdir()
        (clean / ".githooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        git(["config", "core.hooksPath", ".githooks"], clean)
        (clean / "tools").mkdir()
        (clean / "tools" / "real.py").write_text("FLOOR = 0.89\n", encoding="utf-8")
        (clean / STATE_DIR).mkdir()
        # `claims` is configured on the clean tree because a detector with nothing
        # to run is UNRUN, not clean -- the clean fixture must be a tree where every
        # detector actually ran, or it proves only that unconfigured is quiet.
        (clean / STATE_DIR / "config.json").write_text(
            json.dumps({"constants": ["FLOOR"],
                        "claims": {"ledger": "claims.json",
                                   "command": [sys.executable, "-c", "pass"]}}),
            encoding="utf-8")
        (clean / "claims.json").write_text("{}\n", encoding="utf-8")
        (clean / "docs").mkdir()
        (clean / "docs" / "install.md").write_text(
            "# Install\n\n```bash\npython tools/real.py\n```\n", encoding="utf-8")
        (clean / "tests").mkdir()
        (clean / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n",
                                                   encoding="utf-8")
        (clean / ".github" / "workflows").mkdir(parents=True)
        (clean / ".github" / "workflows" / "ci.yml").write_text(
            "name: ci\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - run: python -m pytest tests/ -q\n", encoding="utf-8")
        git(["add", "-A"], clean)
        git(["commit", "-qm", "seed"], clean)

        findings, unrun = scan(clean)
        if findings:
            failures.append("the clean tree produced %d finding(s): %s"
                            % (len(findings), sorted({f["detector"] for f in findings})))
        if unrun:
            failures.append("the clean tree produced UNRUN detectors: %s" % unrun)

        # -- a scan must persist what it printed. "It wrote findings.jsonl" is
        # documented behaviour; a scan that only prints makes the next reader
        # re-run the sweep to learn what was already known.
        with contextlib.redirect_stdout(io.StringIO()):
            cmd_scan(broken, as_json=True)
        findings_file = broken / STATE_DIR / "findings.jsonl"
        if not findings_file.exists():
            failures.append("cmd_scan printed findings but wrote no findings.jsonl")
        else:
            persisted = read_jsonl(findings_file)
            fresh, _ = scan(broken)
            if len(persisted) != len(fresh):
                failures.append("findings.jsonl holds %d row(s), a fresh scan found %d"
                                % (len(persisted), len(fresh)))
        if (broken / STATE_DIR / "unrun.txt").exists():
            failures.append("a scan with nothing UNRUN left a stale unrun.txt behind")

        # -- the loop: plan, fix, refuse to land without a command, then land
        queue = plan(broken)
        if not queue:
            failures.append("plan() produced an empty queue on the seeded tree")
        passing = "%s -c pass" % sys.executable
        failing = "%s -c \"import sys; sys.exit(1)\"" % sys.executable
        if run_batch(broken, 5, passing, dry_run=True) != 0:
            failures.append("dry run did not exit 0")
        if run_batch(broken, 5, passing) != 0:
            failures.append("the auto-fix batch failed")
        if land(broken, None) == 0:
            failures.append("landing without a verification command was allowed")
        if land(broken, failing) == 0:
            failures.append("landing succeeded with a failing verification command")
        if land(broken, passing) != 0:
            failures.append("landing failed with a passing verification command")
        if land(broken, passing) == 0:
            failures.append("the same batch landed twice")

        # The fix must be visible in git, not only in our own state file.
        log = git(["log", "-1", "--pretty=%s"], broken).stdout
        if "FLAMING SWORD" not in log:
            failures.append("the landed commit is not the batch commit: %r" % log.strip())
        show = git(["show", "--stat", "--oneline", "HEAD"], broken).stdout
        if "install.md" not in show:
            failures.append("the landed commit did not carry the edited file: %r"
                            % show.strip()[:200])

        # The fixed detector must go quiet, or the fix was cosmetic.
        after, _ = scan(broken)
        if any(item["detector"] == "two-interpreters" for item in after):
            failures.append("two-interpreters still fires after its own fix")
        if any(item["detector"] == "hooks-unwired" for item in after):
            failures.append("hooks-unwired still fires after its own fix")

        # -- housekeeping: removes what regenerates, refuses what git owns
        (broken / "junk" / "__pycache__").mkdir(parents=True)
        (broken / "junk" / "__pycache__" / "x.pyc").write_bytes(b"x" * 10)
        (broken / "junk" / "keep.py").write_text("KEPT = 1\n", encoding="utf-8")
        git(["add", "junk/keep.py"], broken)
        plan_items = housekeep.collect(broken)
        planned = {(item["rule"], item["path"], item["action"]) for item in plan_items}
        if ("bytecode-cache", "junk/__pycache__", "delete") not in planned:
            failures.append("housekeeping did not plan the cache directory for removal")
        if ("editor-leftover", "junk/keep.py", "delete") in planned:
            failures.append("housekeeping planned a tracked file for removal")
        removed, _freed, housekeep_failures = housekeep.apply(broken, plan_items)
        if housekeep_failures:
            failures.append("housekeeping refused its own plan: %s" % housekeep_failures)
        if removed == 0:
            failures.append("housekeeping removed nothing from a tree with a cache directory")
        if (broken / "junk" / "__pycache__").exists():
            failures.append("housekeeping reported a removal it did not make")
        if not (broken / "junk" / "keep.py").exists():
            failures.append("housekeeping deleted a tracked file")
        if not (broken / STATE_DIR / "batches.jsonl").exists():
            failures.append("housekeeping deleted the landing record")

    if failures:
        print("SELF-TEST FAILED")
        for failure in failures:
            print("  - %s" % failure)
        return 1
    print("SELF-TEST PASSED: 5 detectors fire on a seeded tree, 0 on a clean one,")
    print("  scan persists what it printed, land refuses without a command, on red,")
    print("  and twice, and housekeeping removes caches while refusing what git owns.")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def cmd_scan(root: Path, as_json: bool) -> int:
    config = read_config(root)
    findings, unrun = scan(root, config.get("detectors", {}).get("disable", []))
    # A scan that prints and forgets is a report, not a sweep: the documented
    # state file has to exist afterwards, or the next reader (--plan, an audit,
    # the agent that resumes tomorrow) has to re-run the whole thing to learn
    # what was already known. Scan never touches the queue: ranking is plan's job.
    write_jsonl(state_dir(root) / "findings.jsonl", findings)
    unrun_path = state_dir(root) / "unrun.txt"
    if unrun:
        unrun_path.write_text("\n".join(unrun) + "\n", encoding="utf-8")
    elif unrun_path.exists():
        # A stale UNRUN list is worse than none: it reports a detector as blind
        # after it started seeing, and teaches the reader to ignore the section.
        unrun_path.unlink()
    if as_json:
        print(json.dumps({"findings": findings, "unrun": unrun}, indent=1))
    else:
        for finding in findings:
            print("  [%-6s] %-24s %s:%d  %s" % (finding["severity"], finding["detector"],
                                                finding["path"], finding["line"],
                                                finding["evidence"][:90]))
        print("\n%d finding(s) across %d detector(s)"
              % (len(findings), len({f["detector"] for f in findings})))
        if unrun:
            print("\nUNRUN -- not clean, unknown:")
            for note in unrun:
                print("  - %s" % note)
        waiting = disposition.tasks(root)
        if waiting:
            print("\n%d error task(s) open for disposition (--tasks to read, "
                  "--dispose <id> --as <decision> to close one)" % len(waiting))
    return 0


def cmd_plan(root: Path) -> int:
    queue = plan(root)
    open_items = [item for item in queue if item["status"] == "open"]
    print("%d item(s) in the queue, %d open (%d auto-fixable)"
          % (len(queue), len(open_items), sum(1 for i in open_items if i["auto"])))
    for item in open_items[:15]:
        print("  %-6s %-4s %-24s %s:%d" % (item["severity"],
                                           "auto" if item["auto"] else "prop",
                                           item["detector"], item["path"], item["line"]))
    if len(open_items) > 15:
        print("  ... and %d more" % (len(open_items) - 15))
    return 0


def cmd_status(root: Path) -> int:
    queue = read_jsonl(state_dir(root) / "queue.jsonl")
    batches = read_jsonl(state_dir(root) / "batches.jsonl")
    counts: Dict[str, int] = {}
    for item in queue:
        counts[item.get("status", "open")] = counts.get(item.get("status", "open"), 0) + 1
    print("queue: %s" % (counts or "empty"))
    print("batches: %d (%d landed)" % (len(batches),
                                      sum(1 for b in batches if b.get("landed"))))
    unrun = state_dir(root) / "unrun.txt"
    if unrun.exists():
        print("UNRUN detectors:\n%s" % unrun.read_text(encoding="utf-8").strip())
    return 0


def cmd_housekeep(root: Path, act: bool, as_json: bool, state_days: int,
                  max_mb: int) -> int:
    """The other half of a sweep: what accumulated, and what may go.

    The plan comes from `housekeep.py`, which refuses everything git tracks, every
    symlink and every path outside the root. This wrapper only decides whether it
    is a report or an act, because `--apply` has to be typed by a person.
    """
    items = housekeep.collect(root, state_days=state_days, max_mb=max_mb)
    removed, freed, failures = (0, 0, [])
    if act:
        removed, freed, failures = housekeep.apply(root, items)
    if as_json:
        print(json.dumps({"applied": act, "removed": removed, "bytes_freed": freed,
                          "failures": failures, "items": items}, indent=1))
    else:
        print(housekeep.report(items, applied=act))
        if act:
            print("removed %d item(s), %s freed" % (removed, housekeep.human(freed)))
        for failure in failures:
            print("  REFUSED %s" % failure)
    for failure in failures:
        record_error(root, "housekeep", "refused", failure.split(":")[0], failure,
                     remedy="look at the path: it moved, became a symlink, or is owned "
                            "by something this tool will not touch")
    return 1 if failures else 0


def cmd_tasks(root: Path, include_disposed: bool) -> int:
    rows = disposition.tasks(root, include_disposed=include_disposed)
    if not rows:
        print("no %stask(s) recorded" % ("/all " if include_disposed else "open "))
        return 0
    for row in rows:
        state = row["status"] if row["status"] == "open" else row.get("disposition") or "closed"
        print("  %-7s %-5s %-16s %-24s %s"
              % (row["id"], state, row["stage"], row["subject"][:24], row["what"][:96]))
        if row["seen"] > 1:
            print("  %-7s %s, seen %d time(s), last %s"
                  % ("", "" , row["seen"], row.get("last_seen", "")))
        if row.get("note"):
            print("  %-7s note: %s" % ("", row["note"][:110]))
    counts = disposition.summary(root)
    print("\n%d task(s): %s" % (len(rows), ", ".join("%s %d" % (key, value)
                                                for key, value in sorted(counts.items()))))
    return 0


def cmd_dispose(root: Path, task_id: str, as_what: Optional[str], note: str) -> int:
    if not as_what:
        print("REFUSED: --dispose needs --as <%s>. A task closed without a reason is "
              "a task deleted." % "|".join(disposition.DISPOSITIONS))
        return 2
    try:
        row = disposition.dispose(root, task_id, as_what, note)
    except ValueError as exc:
        print("REFUSED: %s" % exc)
        return 2
    if row is None:
        print("REFUSED: no task %s in %s/%s" % (task_id, STATE_DIR, disposition.LEDGER))
        return 2
    print("disposed %s as %s%s" % (task_id, as_what, ": %s" % note if note else ""))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="A FLAMING SWORD sweep of a codebase.")
    parser.add_argument("--root", default=".", help="repository to sweep (default: cwd)")
    parser.add_argument("--housekeep", action="store_true",
                        help="plan the housekeeping pass: caches, leftovers, empty "
                             "directories, disposable sweep state, and the hazards "
                             "a human has to look at")
    parser.add_argument("--apply", action="store_true",
                        help="with --housekeep: delete, instead of reporting")
    parser.add_argument("--state-days", type=int, default=housekeep.DEFAULT_STATE_DAYS)
    parser.add_argument("--max-mb", type=int, default=housekeep.DEFAULT_MAX_MB)
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--land", action="store_true")
    parser.add_argument("--brief", action="store_true")
    parser.add_argument("--record-research", metavar="JSONL",
                        help="validate research records and queue them as proposals")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--aio", metavar="PROMPT", default=None,
                        help="turn a user prompt into an AIO instruction object "
                             "(frame + sentinel + memory); refuses with reasons and "
                             "renders nothing when any of them fails")
    parser.add_argument("--jsonl", default=None,
                        help="with --aio: a lesson ledger to recall from")
    parser.add_argument("--acceptance", default="",
                        help="with --aio: the command and outcome that ends the task")
    parser.add_argument("--defends", action="append", default=[],
                        help="with --aio: a test, claim or gate that survives "
                             "(repeatable; a placeholder is refused)")
    parser.add_argument("--defend", metavar="INTENT", default=None,
                        help="print the defensive frame for a change, and refuse a "
                             "frame that cannot name what it defends")
    parser.add_argument("--target", default="", help="with --defend: the artefact")
    parser.add_argument("--evidence", default="", help="with --defend: command or path")
    parser.add_argument("--preserve", action="store_true",
                        help="with --defend: preservation work (posture becomes "
                             "mandatory)")
    parser.add_argument("--batch", type=int, default=5)
    parser.add_argument("--test", dest="test_command", default=None,
                        help="the project's own verification command")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--tasks", action="store_true",
                        help="read the disposition ledger: every error the sweep met, "
                             "one task per error, waiting for a decision")
    parser.add_argument("--all", action="store_true",
                        help="with --tasks: include disposed tasks")
    parser.add_argument("--dispose", metavar="TASK",
                        help="close one task with --as, after deciding what it is")
    parser.add_argument("--as", dest="as_what", metavar="DISPOSITION",
                        choices=list(disposition.DISPOSITIONS),
                        help="how the task was closed: %s"
                             % "|".join(disposition.DISPOSITIONS))
    parser.add_argument("--note", default="", help="with --dispose: why, in one line")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.brief:
        return brief()
    if args.aio is not None:
        return cmd_aio(args.aio, args.target, args.acceptance, args.evidence,
                       args.defends, args.preserve, args.jsonl, args.json)
    if args.defend is not None:
        return cmd_defend(args.defend, args.target, args.evidence, args.preserve,
                          args.json)
    root = Path(args.root).resolve()
    if args.record_research:
        return record_research(root, Path(args.record_research))
    if not root.is_dir():
        print("REFUSED: %s is not a directory" % root)
        return 2
    if args.scan:
        return cmd_scan(root, args.json)
    if args.tasks:
        return cmd_tasks(root, args.all)
    if args.dispose:
        return cmd_dispose(root, args.dispose, args.as_what, args.note or "")
    if args.housekeep:
        return cmd_housekeep(root, args.apply, args.json, args.state_days, args.max_mb)
    if args.apply:
        print("REFUSED: --apply only means something with --housekeep")
        return 2
    if args.plan:
        return cmd_plan(root)
    if args.status:
        return cmd_status(root)
    if args.run:
        return run_batch(root, args.batch, args.test_command, dry_run=args.dry_run)
    if args.land:
        return land(root, args.test_command)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
