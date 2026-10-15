#!/usr/bin/env python3
# coding: utf-8
"""preflight_all.py — the tracked gate registry, runner, and self-test.

Why this exists
---------------
STRUCTURAL_FLAWS S10 recorded that the pre-commit gate lived only in
`.githooks/pre-commit`, which is gitignored, so "which gates exist" was readable
only by reading a shell hook, and a fresh clone had no gate at all. The hook is
now force-added, but the inventory problem remains: the checks are assembled
inline, so nothing can answer -- mechanically -- "what gates does this repo run,
on which interpreter, against which artifact, and what proves each one CAN
fail".

The false-green protocol
(`.agents/skills/azazael-false-green-protocol/SKILL.md`) states its Enforcement
clause as a requirement nobody executes:

    "every gate has tree hash + mtime + --force + missing evidence fail"

This tool executes it as a MEASUREMENT rather than an assertion:

  * ``--list``      the inventory, transcribed from the hook (the producer).
  * ``--check``     run the gates. A gate that cannot run is a FAILURE, never a
                    silent pass, unless declared via ``--allow-unrunnable``.
  * ``--self-test`` prove fail-ability: every declared interpreter must actually
                    execute, every declared control artifact must exist on disk,
                    every executable control must fail as required, every gate's
                    REQUIRED artifact must be present (a gate whose input is gone
                    cannot judge at all -- it is BLIND, not green), and the number
                    of gates with NO control is PRINTED rather than rounded to a
                    pass. Add ``--run-controls`` to EXECUTE each declared control
                    artifact, which turns declared fail-ability into demonstrated;
                    add ``--strict`` to make a BLIND gate a failure.
  * ``--force``     re-run. A cached PASS is reused only while its evidence still
                    describes the tree it was recorded against (the gate's own
                    bytes + the staged and worktree state it judged), so a gate
                    -- or the tree -- edited after its last green run re-runs.

A control the instrument cannot fail is not a control, so a gate that has no
control is reported as UNCONTROLLED with its reason -- never counted as green.

Exit codes: 0 pass, 1 a gate failed / a control did not fail / evidence missing,
2 the registry or the interpreter environment is unusable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".githooks" / "pre-commit"
EVIDENCE = REPO / "logs" / "preflight_all_evidence.json"

#: A gate that hangs must not hang the gate runner. The suite gates are the long
#: ones (the two-interpreter gate runs pytest twice); this is the ceiling.
RUN_TIMEOUT = 3600.0
PROBE_TIMEOUT = 120.0
GIT_TIMEOUT = 120.0

#: `(?:tools|scripts)/name.py` -- used to re-derive the hook's gate inventory
#: from the hook text itself, so the registry cannot drift from its producer.
_SCRIPT_RE = re.compile(r"(?:tools|scripts)/[A-Za-z0-9_]+\.py")


class Gate(NamedTuple):
    """One registered gate.

    ``interpreter`` is a NAME, not a path: resolution happens at run time so the
    same registry works on every host. ``env`` holds ``K=V`` entries that the
    hook prepends (``PYTHONPATH=src`` is how the tools import ``CORE``).
    """

    name: str
    argv: Tuple[str, ...]
    interpreter: str
    env: Tuple[str, ...]
    inside_hook: bool
    blocking: bool
    slow: bool
    reads: str
    control_test: Optional[str]
    control: Optional[str]
    uncontrolled_because: Optional[str]
    #: Repo-relative artifacts the gate READS to reach a verdict. Their absence
    #: means the gate cannot judge at all -- BLIND. A baseline that was never
    #: recorded on this machine is the common case: the gate exits 2 rather than
    #: reporting green, and nothing before this surfaced that as a fact.
    requires: Tuple[str, ...] = ()


#: The registry. Every ``inside_hook`` row is transcribed verbatim from
#: `.githooks/pre-commit`; `--self-test` re-derives that list from the hook text
#: and fails if the two disagree, so this table cannot silently drift from the
#: gate that actually runs.
GATES: Tuple[Gate, ...] = (
    Gate(
        name="changeset-focus",
        argv=("scripts/commit_gate.py", "--hook"),
        interpreter="python3",
        env=(),
        inside_hook=True,
        blocking=True,
        slow=False,
        reads="the staged changeset (git index) -- file count and changed lines",
        control_test="tests/test_commit_gate.py",
        control=None,
        uncontrolled_because=None,
        requires=(),  # reads the git index, which repo_state_hash covers
    ),
    Gate(
        name="stale-index-guard",
        argv=("tools/index_drift_check.py",),
        interpreter="python",
        env=(),
        inside_hook=True,
        blocking=True,
        slow=False,
        reads="every staged path vs its worktree content",
        control_test="tests/test_index_drift_check.py",
        control=None,
        uncontrolled_because=None,
        requires=(),  # two git queries, no file
    ),
    Gate(
        name="staged-scanner",
        argv=("tools/staged_scanner_gate.py",),
        interpreter="python",
        env=("PYTHONPATH=src",),
        inside_hook=True,
        blocking=True,
        slow=False,
        reads="each staged .py at :0: (the INDEX) vs HEAD, per finding category",
        control_test="tests/test_staged_scanner_gate.py",
        control=None,
        uncontrolled_because=None,
        requires=(),  # the index, not a file
    ),
    Gate(
        name="canon-drift",
        argv=("tools/canon_drift_check.py", "--check"),
        interpreter="python",
        env=(),
        inside_hook=True,
        blocking=True,
        slow=False,
        reads="skills/ (source corpus, RULE 0R) vs .agents/skills/<n>/SKILL.md",
        control_test="tests/test_canon_drift_check.py",
        control=None,
        uncontrolled_because=None,
        requires=("skills", ".agents/skills"),  # SOURCE_DIR / LOAD_DIR
    ),
    Gate(
        name="anti-pattern-ratchet",
        argv=("tools/anti_pattern_gate.py", "--check"),
        interpreter="python",
        env=("PYTHONPATH=src",),
        inside_hook=True,
        blocking=True,
        slow=False,
        reads="the whole src/ tree vs logs/anti_pattern_baseline.json",
        control_test="tests/test_anti_pattern_gate.py",
        control="anti-pattern-ratchet",
        uncontrolled_because=None,
        requires=("logs/anti_pattern_baseline.json",),
    ),
    Gate(
        name="mesh-ledger-freshness",
        argv=("tools/mesh_function_preflight.py", "--check"),
        interpreter="python",
        env=("PYTHONPATH=src",),
        inside_hook=True,
        blocking=True,
        slow=False,
        reads="NEURAL_MESH_WIRE_OR_CUT.json vs the live call graph",
        control_test="tests/test_mesh_wire_or_cut.py",
        control=None,
        uncontrolled_because=None,
        requires=("NEURAL_MESH_WIRE_OR_CUT.json",),
    ),
    Gate(
        name="pmb-outcome-observer",
        argv=("tools/pmb_session_observe.py", "--commit-ok", "--quiet"),
        interpreter="pmb-venv",
        env=(),
        inside_hook=True,
        # Deliberately non-blocking IN THE HOOK: "a memory side-effect must never
        # reject a commit", so its exit code is ignored there. Registered anyway,
        # so that the inventory is complete and `--check` still reports it.
        blocking=False,
        slow=False,
        reads="the PMB agent_actions table (Earned-Memory loop)",
        control_test=None,
        control=None,
        uncontrolled_because=(
            "side-effect recorder, exit code ignored by the hook; a non-zero exit "
            "is not a defect signal, so there is nothing to control"
        ),
        requires=(),  # the PMB daemon's own store, not a repo path
    ),
    Gate(
        name="two-interpreter-suite",
        argv=("scripts/ci_two_interpreter_gate.py", "--check"),
        interpreter="python",
        env=(),
        inside_hook=False,
        blocking=True,
        slow=True,
        reads="the suite on both interpreters vs logs/ci_two_interpreter_gate_baseline.json",
        control_test="tests/test_ci_two_interpreter_gate.py",
        control=None,
        uncontrolled_because=None,
        requires=("logs/ci_two_interpreter_gate_baseline.json",),
    ),
    Gate(
        name="aggregate-suite-isolation",
        argv=("tools/aggregate_suite_gate.py", "--check", "--profile", "isolation"),
        interpreter="python",
        env=(),
        inside_hook=False,
        blocking=True,
        slow=True,
        reads="single-process tests/ vs logs/aggregate_suite_baseline.json",
        control_test="tests/test_aggregate_suite_gate.py",
        control=None,
        uncontrolled_because=None,
        requires=("logs/aggregate_suite_baseline.json",),
    ),
    Gate(
        name="type-check",
        argv=("tools/type_check_gate.py", "--check"),
        interpreter="python",
        env=(),
        inside_hook=False,
        blocking=True,
        slow=True,
        reads="basedpyright output vs its own baseline",
        control_test=None,
        control=None,
        uncontrolled_because=(
            "no dedicated control artifact is asserted for this gate at "
            "registration time; its baseline-ratchet shape is the same as "
            "anti-pattern-ratchet, whose control is executable"
        ),
        requires=("logs/basedpyright_baseline.json",),
    ),
)


# --------------------------------------------------------------------------- #
# Interpreter resolution and probing                                            #
# --------------------------------------------------------------------------- #


def resolve_interpreter(name: str) -> Optional[str]:
    """Resolve an interpreter NAME to an executable path, or None if absent."""
    if name == "pmb-venv":
        override = os.environ.get("PMB_VENV_PYTHON")
        if override and Path(override).exists():
            return override
        home = Path.home()
        for candidate in (
            home / ".pmb-venv" / "Scripts" / "python.exe",
            home / ".pmb-venv" / "bin" / "python",
        ):
            if candidate.exists():
                return str(candidate)
        return None
    return shutil.which(name)


def probe_interpreter(path: str) -> Tuple[bool, str]:
    """Prove an interpreter RUNS, rather than that a name resolves.

    `shutil.which` answers "is there a file called python3 on PATH?". On this
    host that file is Python 3.13.14 while `python` is 3.14.7, so the hook's
    check 1 and checks 1b-5 run on different interpreters. Resolving a NAME is
    therefore not evidence that the gate runs -- so probe it.
    """
    script = "import json,sys;print(json.dumps({'v':sys.version.split()[0],'exe':sys.executable}))"
    try:
        proc = subprocess.run(
            [path, "-c", script],
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)
    if proc.returncode != 0:
        return False, "exit=%d %s" % (proc.returncode, (proc.stderr or "").strip()[:200])
    return True, (proc.stdout or "").strip()


# --------------------------------------------------------------------------- #
# Hook parity -- the registry must describe the gate that actually runs        #
# --------------------------------------------------------------------------- #


def hook_gate_scripts(hook_text: str) -> List[str]:
    """Re-derive the gate scripts the hook RUNS (not the ones it mentions).

    Comment lines are skipped on purpose: the hook's own header mentions
    `tools/install_git_hooks.py` in prose, and counting a mention as a gate would
    make this control fail on a correct tree.
    """
    found: List[str] = []
    for raw in hook_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "python" not in line and "PMB_PY" not in line:
            continue
        for match in _SCRIPT_RE.findall(line):
            if match not in found:
                found.append(match)
    return found


def hook_parity(gates: Sequence[Gate], hook_text: Optional[str]) -> Tuple[bool, str]:
    """Return (ok, message). Absence of the hook is MISSING EVIDENCE, not a pass."""
    if hook_text is None:
        return False, "MISSING_EVIDENCE: %s not readable -- cannot verify the registry" % HOOK
    ran = set(hook_gate_scripts(hook_text))
    registered = {g.argv[0] for g in gates if g.inside_hook}
    only_hook = sorted(ran - registered)
    only_registry = sorted(registered - ran)
    if only_hook or only_registry:
        return False, "registry drift: ran-but-unregistered=%s registered-but-not-run=%s" % (
            only_hook,
            only_registry,
        )
    return True, "registry matches the hook (%d gates)" % len(registered)


# --------------------------------------------------------------------------- #
# Evidence: a cached PASS must still describe the tree it was recorded against  #
# --------------------------------------------------------------------------- #


def repo_state_hash() -> Optional[str]:
    """Hash the staged + worktree state that the commit-time gates judge.

    This is the template's "tree hash", in the terms these gates actually use:
    they read the git INDEX and the worktree (staged scanner, index-drift guard,
    ratchet, mesh ledger), so a cached PASS goes stale when either moves.

    Returns None when git cannot answer, and None means NO cached pass is
    reused: reusing evidence that cannot be shown to still describe the tree is
    the exact defect this file exists to prevent.
    """
    digest = hashlib.sha256()
    for args in (("diff", "--cached", "--binary"), ("diff", "--binary")):
        try:
            proc = subprocess.run(
                ["git", *args], cwd=str(REPO), capture_output=True, timeout=GIT_TIMEOUT
            )
        except (OSError, subprocess.SubprocessError) as exc:
            print("[preflight] git %s could not run (%s) -- no cached pass will be reused"
                  % (" ".join(args), type(exc).__name__))
            return None
        if proc.returncode != 0:
            print("[preflight] git %s exited %d -- no cached pass will be reused"
                  % (" ".join(args), proc.returncode))
            return None
        digest.update(proc.stdout)
        digest.update(b"\0")
    return digest.hexdigest()


def gate_fingerprint(gate: Gate, interpreter_path: str, state: Optional[str]) -> str:
    """Hash the things that make a recorded result still true.

    The gate's own bytes (a gate edited after its last green run must re-run),
    its argv, the interpreter that ran it, and the repo state it judged.
    """
    digest = hashlib.sha256()
    script = REPO / gate.argv[0]
    if script.is_file():
        digest.update(script.read_bytes())
    digest.update(b"\0".join(a.encode("utf-8") for a in gate.argv))
    digest.update(interpreter_path.encode("utf-8"))
    digest.update(b"\0".join(e.encode("utf-8") for e in gate.env))
    digest.update((state or "no-git-state").encode("utf-8"))
    return digest.hexdigest()


def load_evidence() -> Dict[str, dict]:
    try:
        text = EVIDENCE.read_text(encoding="utf-8")
    except FileNotFoundError:
        # No evidence file is a NORMAL first run, not a failure -- but it is
        # said out loud, because "no evidence" must never be mistaken for a
        # recorded pass.
        print("[preflight] no evidence recorded yet -- every gate will be run")
        return {}
    except (OSError, UnicodeDecodeError) as exc:
        print("[preflight] evidence unreadable (%s) -- treating as absent" % exc)
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print("[preflight] evidence corrupt (%s) -- treating as absent" % exc)
        return {}
    return data if isinstance(data, dict) else {}


def save_evidence(evidence: Dict[str, dict]) -> None:
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# Running gates                                                                 #
# --------------------------------------------------------------------------- #


class Result(NamedTuple):
    gate: str
    outcome: str  # PASS | FAIL | UNRUNNABLE | CACHED
    exit_code: Optional[int]
    seconds: float
    detail: str


def run_gate(gate: Gate, interpreter_path: str, timeout: float = RUN_TIMEOUT) -> Result:
    started = time.monotonic()
    env = dict(os.environ)
    for entry in gate.env:
        key, _, value = entry.partition("=")
        env[key] = value + (os.pathsep + env.get(key, "")) if env.get(key) else value
    cmd = [interpreter_path, str(REPO / gate.argv[0]), *gate.argv[1:]]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return Result(gate.name, "FAIL", None, time.monotonic() - started,
                      "TIMEOUT after %.0fs -- a run that never completed is not a pass" % timeout)
    except OSError as exc:
        return Result(gate.name, "FAIL", None, time.monotonic() - started,
                      "could not spawn %s: %s" % (interpreter_path, exc))
    seconds = time.monotonic() - started
    tail = "\n".join((proc.stdout or "").splitlines()[-8:])
    outcome = "PASS" if proc.returncode == 0 else "FAIL"
    return Result(gate.name, outcome, proc.returncode, seconds, tail)


# --------------------------------------------------------------------------- #
# The executable control: drive the ratchet into a sandbox and make it fail     #
# --------------------------------------------------------------------------- #


def control_anti_pattern_ratchet(interpreter_path: str) -> Tuple[bool, str]:
    """A real negative control for the repo-wide ratchet.

    Fabricate, entirely inside a temp directory: a clean file, a baseline
    recorded against it, then one file carrying an anti-pattern. `--check` must
    exit non-zero. `--baseline-file` is passed EXPLICITLY because a narrowed
    `--dir` redirects the default baseline on purpose (measured: same shape as
    `aggregate_suite_gate`'s `.partial` redirect), and silently comparing against
    the repo baseline would make this control test nothing.
    """
    clean = "def ok():\n    return 1\n"
    # Assembled from parts so this file's own AST carries no anti-pattern
    # literal; the staged scanner parses statements, not string constants, but
    # an explicit construction also keeps the intent readable.
    dirty = "def bad():\n    try:\n        return 1\n    " + "except" + ":\n        " + "pass" + "\n"
    with tempfile.TemporaryDirectory(prefix="az744_ratchet_") as tmp:
        root = Path(tmp)
        (root / "clean.py").write_text(clean, encoding="utf-8")
        baseline = root / "baseline.json"
        record = run_control(
            [interpreter_path, str(REPO / "tools/anti_pattern_gate.py"),
             "--baseline", "--dir", str(root), "--baseline-file", str(baseline)],
            env=("PYTHONPATH=src",),
        )
        if record.exit_code != 0:
            return False, "control setup failed: --baseline exited %s (%s)" % (
                record.exit_code, record.detail)
        (root / "dirty.py").write_text(dirty, encoding="utf-8")
        check = run_control(
            [interpreter_path, str(REPO / "tools/anti_pattern_gate.py"),
             "--check", "--dir", str(root), "--baseline-file", str(baseline)],
            env=("PYTHONPATH=src",),
        )
        if check.exit_code == 0:
            return False, ("control did NOT fail: ratchet exited 0 on an added "
                           "anti-pattern -- the gate cannot fail on its own subject")
        return True, "ratchet exits %s on an added anti-pattern" % check.exit_code


def run_control(cmd: Sequence[str], env: Tuple[str, ...], timeout: float = RUN_TIMEOUT) -> Result:
    child_env = dict(os.environ)
    for entry in env:
        key, _, value = entry.partition("=")
        child_env[key] = value
    try:
        proc = subprocess.run(
            list(cmd), cwd=str(REPO), env=child_env, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return Result("control", "FAIL", None, timeout, "TIMEOUT")
    except OSError as exc:
        return Result("control", "FAIL", None, 0.0, str(exc))
    tail = "\n".join((proc.stderr or proc.stdout or "").splitlines()[-4:])
    return Result("control", "PASS" if proc.returncode == 0 else "FAIL",
                  proc.returncode, 0.0, tail)


CONTROLS = {"anti-pattern-ratchet": control_anti_pattern_ratchet}


# --------------------------------------------------------------------------- #
# Commands                                                                      #
# --------------------------------------------------------------------------- #


def cmd_list(gates: Sequence[Gate], as_json: bool) -> int:
    if as_json:
        print(json.dumps(
            [{"name": g.name, "argv": list(g.argv), "interpreter": g.interpreter,
              "env": list(g.env), "inside_hook": g.inside_hook, "blocking": g.blocking,
              "slow": g.slow, "reads": g.reads, "requires": list(g.requires),
              "control_test": g.control_test, "control": g.control,
              "uncontrolled_because": g.uncontrolled_because}
             for g in gates], indent=2))
        return 0
    print("registered gates (source of truth for what --check runs):\n")
    for g in gates:
        where = "hook" if g.inside_hook else "CI"
        kind = "blocking" if g.blocking else "NON-blocking"
        print("  %-26s %-4s %-12s %-9s %s %s" % (
            g.name, where, kind, g.interpreter, g.argv[0], " ".join(g.argv[1:])))
        print("      reads:   %s" % g.reads)
        if g.requires:
            print("      needs:   %s (absent = BLIND, cannot judge)" % ", ".join(g.requires))
        if g.control:
            print("      control: executable (%s)" % g.control)
        elif g.control_test:
            print("      control: artifact %s" % g.control_test)
        else:
            print("      control: NONE -- %s" % g.uncontrolled_because)
    print("\n%d gates: %d hook, %d CI-only"
          % (len(gates), sum(1 for g in gates if g.inside_hook),
             sum(1 for g in gates if not g.inside_hook)))
    return 0


def cmd_check(gates: Sequence[Gate], force: bool, include_slow: bool,
              allow_unrunnable: Sequence[str]) -> int:
    ok, message = hook_parity(gates, read_hook())
    print("[preflight] hook parity: %s" % message)
    if not ok:
        return 1

    evidence = load_evidence()
    state = repo_state_hash()
    results: List[Result] = []
    for gate in gates:
        if gate.slow and not include_slow:
            continue
        interpreter_path = resolve_interpreter(gate.interpreter)
        if interpreter_path is None:
            if gate.name in allow_unrunnable:
                print("[preflight] %-26s DECLARED UNRUNNABLE (interpreter %r absent)"
                      % (gate.name, gate.interpreter))
                continue
            results.append(Result(gate.name, "UNRUNNABLE", None, 0.0,
                                  "interpreter %r not found -- a gate that cannot run is "
                                  "not a pass" % gate.interpreter))
            continue
        fingerprint = gate_fingerprint(gate, interpreter_path, state)
        cached = evidence.get(gate.name)
        if (not force and state is not None and isinstance(cached, dict)
                and cached.get("fingerprint") == fingerprint
                and cached.get("exit_code") == 0):
            results.append(Result(gate.name, "CACHED", 0, 0.0,
                                  "evidence still describes this tree (--force to re-run)"))
            continue
        result = run_gate(gate, interpreter_path)
        evidence[gate.name] = {
            "fingerprint": fingerprint,
            "exit_code": result.exit_code,
            "seconds": round(result.seconds, 3),
            "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        results.append(result)

    save_evidence(evidence)
    print()
    for result in results:
        mark = {"PASS": "PASS", "CACHED": "PASS", "FAIL": "FAIL", "UNRUNNABLE": "FAIL"}[result.outcome]
        print("[%s] %-26s %6.2fs %s" % (mark, result.gate, result.seconds, result.outcome))
        if result.outcome in ("FAIL", "UNRUNNABLE") and result.detail:
            for line in result.detail.splitlines():
                print("        %s" % line)

    failed = [r for r in results if r.outcome in ("FAIL", "UNRUNNABLE")]
    blocking_failed = [r for r in failed if is_blocking(gates, r.gate)]
    print("\n%d ran, %d failed (%d blocking), %d reused from evidence"
          % (len(results), len(failed), len(blocking_failed),
             sum(1 for r in results if r.outcome == "CACHED")))
    return 1 if blocking_failed else 0


def is_blocking(gates: Sequence[Gate], name: str) -> bool:
    for gate in gates:
        if gate.name == name:
            return gate.blocking
    return True


def read_hook() -> Optional[str]:
    try:
        return HOOK.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        # Two statements on purpose: a lone `return None` here is the shape the
        # compliance scanner flags as `except_return_default`, and it IS a real
        # swallow -- the caller cannot tell "unreadable hook" from "empty hook"
        # unless this says so. `hook_parity` turns the None into MISSING_EVIDENCE.
        print("[preflight] hook unreadable (%s: %s) -- parity cannot be verified"
              % (type(exc).__name__, exc))
        return None


def cmd_self_test(gates: Sequence[Gate], run_controls: bool = False,
                  strict: bool = False, allow_blind: Sequence[str] = ()) -> int:
    """Prove fail-ability. A check that passes on nothing has proved nothing.

    ``strict=False`` (the default) reports a BLIND gate -- one whose required
    artifact is absent -- as a counted note rather than a failure, because a
    baseline that was never recorded on this machine is a normal state for the
    CI-only gates and failing on it would make the self-test noise. It is still
    PRINTED, so absence of evidence is never presented as a pass. ``--strict``
    promotes it, which is the form for a gate that is supposed to be runnable.
    """
    failures: List[str] = []
    notes: List[str] = []

    print("== 1. hook parity (the registry must describe the gate that runs) ==")
    parity_ok, parity_message = hook_parity(gates, read_hook())
    print("   %s: %s" % ("OK" if parity_ok else "FAIL", parity_message))
    if not parity_ok:
        failures.append("hook parity: %s" % parity_message)

    print("\n== 2. interpreters actually execute (%d distinct) ==" % len({g.interpreter for g in gates}))
    # A missing interpreter is a failure only for a gate that is supposed to
    # BLOCK. The PMB observer is non-blocking by design ("a memory side-effect
    # must never reject a commit"), so its absent venv is a note, not a red --
    # but it is still printed, never silently dropped.
    blocking_interpreters = {g.interpreter for g in gates if g.blocking}
    seen: Dict[str, Tuple[bool, str]] = {}
    for name in sorted({g.interpreter for g in gates}):
        required = name in blocking_interpreters
        path = resolve_interpreter(name)
        if path is None:
            seen[name] = (False, "not on PATH")
            print("   %s %-10s not found%s" % ("FAIL" if required else "note", name,
                                               "" if required else " (non-blocking gate only)"))
            if required:
                failures.append("interpreter %r does not resolve" % name)
            else:
                notes.append("interpreter %r absent; only non-blocking gates use it" % name)
            continue
        ok, info = probe_interpreter(path)
        seen[name] = (ok, info)
        print("   %s %-10s %s" % ("OK  " if ok else ("FAIL" if required else "note"), name, info))
        if not ok:
            if required:
                failures.append("interpreter %r does not execute: %s" % (name, info))
            else:
                notes.append("interpreter %r does not execute: %s" % (name, info))
    paths = {name: resolve_interpreter(name) for name in seen}
    distinct = {p for p in paths.values() if p}
    if len(distinct) > 1:
        notes.append(
            "the hook runs its gates on %d different interpreters (%s) -- resolved by "
            "NAME; a gate may behave differently depending on which one it lands on"
            % (len(distinct), ", ".join(sorted(str(p) for p in distinct))))

    print("\n== 3. declared control artifacts exist on disk ==")
    for gate in gates:
        if not gate.control_test:
            continue
        if (REPO / gate.control_test).is_file():
            print("   OK   %-26s %s" % (gate.name, gate.control_test))
        else:
            print("   FAIL %-26s %s MISSING" % (gate.name, gate.control_test))
            failures.append(
                "%s declares control artifact %s, which is not in the tree"
                % (gate.name, gate.control_test))

    blind: List[Tuple[Gate, str]] = []
    print("\n== 4. required artifacts: a gate whose input is ABSENT cannot judge ==")
    for gate in gates:
        for rel in gate.requires:
            if not (REPO / rel).exists():
                blind.append((gate, rel))
                break
    if not blind:
        print("   OK   every gate's required artifact is present")
    for gate, rel in blind:
        declared = gate.name in allow_blind
        tag = "FAIL" if (strict and not declared) else ("note" if not declared else "ok  ")
        print("   %s %-26s BLIND -- %s is absent, so it cannot produce a verdict%s"
              % (tag, gate.name, rel, " [declared via --allow-blind]" if declared else ""))
        if strict and not declared:
            failures.append("%s is BLIND: %s is absent, so it cannot judge" % (gate.name, rel))

    print("\n== 5. executable controls must FAIL as required ==")
    for gate in gates:
        if not gate.control:
            continue  # artifact-declared or uncontrolled; reported in section 5
        interpreter_path = resolve_interpreter(gate.interpreter)
        if interpreter_path is None:
            failures.append("%s: interpreter %r absent" % (gate.name, gate.interpreter))
            continue
        control = CONTROLS.get(gate.control)
        if control is None:
            failures.append("%s names control %r with no implementation" % (gate.name, gate.control))
            continue
        ok, message = control(interpreter_path)
        print("   %s %-26s %s" % ("OK  " if ok else "FAIL", gate.name, message))
        if not ok:
            failures.append("%s: %s" % (gate.name, message))

    # Fail-ability is not a boolean. Three honest buckets, because calling an
    # artifact-declared gate "uncontrolled" while printing the artifact it
    # declares is a self-contradiction:
    #   executable  -- demonstrated here, by making the gate fail for real;
    #   artifact    -- a named test is asserted as its control, and that test is
    #                  verified to EXIST, but its fail-ability is not re-run here;
    #   none        -- nothing declared, with the reason.
    executable = [g for g in gates if g.control]
    artifact_only = [g for g in gates if not g.control and g.control_test]
    none_declared = [g for g in gates if not g.control and not g.control_test]
    print("\n== 6. fail-ability by evidence class ==")
    print("   executable control, demonstrated here : %d" % len(executable))
    print("   artifact-declared, existence verified : %d" % len(artifact_only))
    print("   nothing declared                      : %d" % len(none_declared))
    for gate in artifact_only:
        print("     artifact  %-24s %s" % (gate.name, gate.control_test))
    for gate in none_declared:
        print("     NONE      %-24s %s" % (gate.name, gate.uncontrolled_because))

    if run_controls:
        print("\n== 7. control artifacts EXECUTED -- declared fail-ability, now demonstrated ==")
        for gate in gates:
            if not gate.control_test:
                continue
            interpreter_path = resolve_interpreter(gate.interpreter)
            if interpreter_path is None:
                print("   FAIL %-26s interpreter %r absent" % (gate.name, gate.interpreter))
                failures.append("%s: cannot run its control, interpreter %r absent"
                                % (gate.name, gate.interpreter))
                continue
            started = time.monotonic()
            result = run_control(
                [interpreter_path, "-m", "pytest", gate.control_test, "-q"],
                env=("PYTHONPATH=src",),
            )
            seconds = time.monotonic() - started
            ok = result.exit_code == 0
            print("   %s %-26s %5.1fs %s"
                  % ("OK  " if ok else "FAIL", gate.name, seconds, gate.control_test))
            if not ok:
                failures.append("%s: control artifact %s exited %s"
                                % (gate.name, gate.control_test, result.exit_code))
                for line in result.detail.splitlines()[-4:]:
                    print("        %s" % line)

    for note in notes:
        print("\n[note] %s" % note)
    print("\n%d gate(s), %d failure(s), %d blind, %d with no declared control"
          % (len(gates), len(failures), len(blind), len(none_declared)))
    if run_controls:
        print("   (artifact-declared controls were EXECUTED above: their fail-ability")
        print("    is demonstrated for THIS run, and expires with the tree it ran on)")
    else:
        print("   (an artifact-declared control is NOT a demonstrated one -- re-run")
        print("    with --run-controls to execute it, or read the test named beside it)")
    if failures:
        for failure in failures:
            print("  FAIL %s" % failure)
        return 1
    return 0


def main(argv: Optional[Sequence[str]] = None, gates: Sequence[Gate] = GATES) -> int:
    parser = argparse.ArgumentParser(
        prog="preflight_all.py",
        description="Tracked gate registry, runner and self-test.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="print the registry and exit")
    group.add_argument("--check", action="store_true",
                       help="run the registered gates (default)")
    group.add_argument("--self-test", action="store_true",
                       help="prove fail-ability: interpreters, controls, uncontrolled count")
    parser.add_argument("--include-slow", action="store_true",
                        help="also run the CI-only suite gates")
    parser.add_argument("--force", action="store_true",
                        help="re-run instead of reusing evidence that still matches")
    parser.add_argument("--allow-unrunnable", action="append", default=[], metavar="GATE",
                        help="declare a gate unrunnable; repeatable, and it is printed")
    parser.add_argument("--run-controls", action="store_true",
                        help="with --self-test: EXECUTE each declared control artifact")
    parser.add_argument("--strict", action="store_true",
                        help="with --self-test: a BLIND gate is a failure")
    parser.add_argument("--allow-blind", action="append", default=[], metavar="GATE",
                        help="with --strict: declare a gate known to be blind; repeatable")
    parser.add_argument("--json", action="store_true", help="machine-readable --list")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not (REPO / "tools").is_dir():
        print("[preflight] %s is not a repo root" % REPO, file=sys.stderr)
        return 2
    if args.json and not args.list:
        print("[preflight] --json applies to --list", file=sys.stderr)
        return 2
    if (args.run_controls or args.strict or args.allow_blind) and not args.self_test:
        print("[preflight] --run-controls/--strict/--allow-blind apply to --self-test",
              file=sys.stderr)
        return 2

    if args.list:
        return cmd_list(gates, args.json)
    if args.self_test:
        return cmd_self_test(gates, args.run_controls, args.strict, args.allow_blind)
    return cmd_check(gates, args.force, args.include_slow, args.allow_unrunnable)


if __name__ == "__main__":
    raise SystemExit(main())
