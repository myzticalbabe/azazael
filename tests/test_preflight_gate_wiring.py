# coding: utf-8
"""Presence control: a gate in ``tools/`` that no hook runs is not a gate.

This repository's recurring defect is **"mechanized but not enforced"**: the
check is written, reviewed, and then reported as "in place" while nothing
executes it. Two live instances are the reason this file exists:

* ``tools/preflight_all.py`` (38 KB, an 11-gate registry with its own hook-parity
  self-test) was invoked by **nothing** -- so its ``--self-test`` drift check had
  never run either. A control inside an unrun script cannot report.
* ``tools/test_paradigm_gate.py`` *was* wired, which proves the class is about
  the wiring step being skipped, not about the gate being unwanted.

So this test asserts the wiring, not the gate's judgement. It is a **presence
control**: it can prove a script is named by a real (non-comment, non-``echo``)
line of the hook. It cannot prove the gate is correct, that it fails when it
should, or that its baseline is fresh -- those need the gate's own control test,
named in ``preflight_all.py``'s registry.

Two deliberate design choices, both earned from this repo's own mistakes:

1. **Comment lines are stripped before matching.** The hook's header names
   ``tools/install_git_hooks.py`` in prose; a matcher that counts a mention as a
   gate fires on a correct tree. AGENTS.md records a gate that fired on its own
   rulebook for exactly this reason.
2. **``echo`` lines are stripped too.** The hook prints remediation hints such as
   ``echo "[Canon] Reconcile: python tools/canon_drift_check.py --fix"``. A
   matcher that accepted them would keep passing after the real invocation was
   deleted -- a false pass manufactured by a *help message*.

The allowlist is not a parking lot. Each entry carries a reason the test
verifies against the file it describes, so the entry cannot quietly become true
or false: fix the underlying condition and the test fails until the entry is
re-adjudicated.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".githooks" / "pre-commit"
TOOLS = REPO / "tools"
PREFLIGHT = TOOLS / "preflight_all.py"

#: ``(?:tools|scripts)/name.py`` -- the same shape ``preflight_all.py`` uses to
#: re-derive the hook's inventory, written independently here on purpose: two
#: instruments that must agree are worth more than one that is trusted.
_SCRIPT_RE = re.compile(r"(?:tools|scripts)/[A-Za-z0-9_]+\.py")

#: An existence test -- ``[ -f path ]``, ``if [[ -x path ]]``, ``[ ! -f path ]``.
#: It asks whether a script is there; it does not execute it, so crediting it as
#: wiring would let the hook pass this control while the real invocation was
#: deleted -- the same false pass as an ``echo`` hint, one step closer to the code.
_GUARD_RE = re.compile(r"^\s*(?:(?:if|elif|while|until)\s+)?\[\[?\s*!?\s*-[fx]\s")

#: Gates on disk that the hook does not invoke directly, each with the *kind* of
#: reason and a one-line justification the test below can verify.
#:
#: kind="registered-slow"  -> registered in ``preflight_all.py`` with
#:                            ``inside_hook=False`` because it is too slow for
#:                            every commit; it is run by the preflight runner.
#: kind="unregistered"     -> in NO registry at all. This is a REAL GAP, kept
#:                            visible as a ratchet instead of being wired to the
#:                            wrong place. It must not silently grow.
#: kind="hardcoded-root"   -> judges a different tree than this repo, so wiring
#:                            it would enforce a verdict about another checkout.
KNOWN_UNWIRED = {
    "aggregate_suite_gate.py": (
        "registered-slow",
        "runs single-process pytest over all of tests/ (slow=True in the "
        "preflight_all.py registry); too slow for a per-commit hook",
    ),
    "type_check_gate.py": (
        "registered-slow",
        "basedpyright over the tree, measured at ~64s (module docstring); "
        "slow=True in the preflight_all.py registry",
    ),
    "failure_evidence_gate.py": (
        "unregistered",
        "baseline ratchet over unbounded waits / unnamed encodings in scripts/ "
        "and tools/; it appears in NO preflight_all.py Gate row -- wiring or "
        "registering it is an open decision, not an oversight to paper over",
    ),
    "cain_render_gate.py": (
        "hardcoded-root",
        "a module-level root constant points at a different checkout than this "
        "repo, so a commit here would be judged against another tree; it must "
        "be repointed before it can be wired",
    ),
}


# --------------------------------------------------------------------------- #
# Parsing helpers (pure functions, so the negative control can exercise them)
# --------------------------------------------------------------------------- #


def _non_comment_lines(text):
    """Yield ``(lineno, stripped)`` for lines the shell actually EXECUTES.

    A line whose first non-space character is ``#`` is prose. Blank lines carry
    nothing. ``echo`` lines are help text, never invocations -- see the module
    docstring for why accepting them is a false pass.
    """
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("echo "):
            continue
        yield lineno, line


def _is_existence_guard(line):
    """True when the line only TESTS for a script rather than executing it."""
    return bool(_GUARD_RE.match(line))


def _invocation_lines(text):
    """Yield ``(lineno, line)`` for executed lines that name a script to run.

    Existence guards are skipped: they name a script to decide whether to run
    it, and a matcher that counted them would report wiring for a hook that
    only asks the question.
    """
    for lineno, line in _non_comment_lines(text):
        if _is_existence_guard(line):
            continue
        if _SCRIPT_RE.search(line):
            yield lineno, line


def _invoked_scripts(text):
    """Return the ``tools/``/``scripts/`` paths named by executed lines."""
    found = []
    for _lineno, line in _invocation_lines(text):
        for match in _SCRIPT_RE.findall(line):
            if match not in found:
                found.append(match)
    return found


def _gate_blocks(text):
    """Split ``preflight_all.py``'s registry into one block per ``Gate(`` row."""
    blocks = []
    for chunk in text.split("Gate(")[1:]:
        blocks.append(chunk.split("Gate(")[0])
    return blocks


def _gate_blocks_containing(text, script_path):
    """Registry rows whose ``argv`` names ``script_path``."""
    return [block for block in _gate_blocks(text) if script_path in block]


def _hook_text():
    return HOOK.read_text(encoding="utf-8", errors="replace")


def _preflight_text():
    return PREFLIGHT.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# Negative control: the matcher itself must be falsifiable
# --------------------------------------------------------------------------- #


def test_matcher_ignores_comments_and_echo_hints():
    """The matcher must not credit a mention or a remediation hint as wiring.

    Without this, a correctly-wired hook and a hook that only *documents* the
    gate are indistinguishable -- and the second is the defect this file exists
    to catch.
    """
    fixture = (
        "# tools/commented_gate.py -- prose mention, not a gate run\n"
        'echo "reconcile: python tools/echo_hint_gate.py --fix"\n'
        '"$PYTHON3" "$SCRIPT_DIR/tools/real_gate.py" --check\n'
    )
    found = _invoked_scripts(fixture)
    assert found == ["tools/real_gate.py"], found


def test_matcher_ignores_existence_guards():
    """``[ -f path ]`` asks whether a gate exists; it does not run the gate.

    Crediting it is a false pass in the same family as an ``echo`` hint: the
    stanza survives the deletion of the invocation it is supposed to guard.
    """
    fixture = (
        'if [ -f "$SCRIPT_DIR/tools/guarded_only.py" ]; then\n'
        '    "$PYTHON3" "$SCRIPT_DIR/tools/guarded_only.py" --check\n'
        "fi\n"
    )
    assert _is_existence_guard(_non_comment_lines(fixture).__next__()[1])
    assert _invoked_scripts(fixture) == ["tools/guarded_only.py"]

    guard_only = 'if [ -f "$SCRIPT_DIR/tools/never_run.py" ]; then\n    :\nfi\n'
    assert _invoked_scripts(guard_only) == [], (
        "a hook that only tests for the script must not count as invoking it"
    )


# --------------------------------------------------------------------------- #
# The hook contract (worker B1's side; fails until the hook lands)
# --------------------------------------------------------------------------- #


def test_hook_is_readable_and_non_trivial():
    """Absence of the hook is MISSING EVIDENCE, never a pass."""
    assert HOOK.is_file(), "hook not found: %s" % HOOK
    executable_lines = sum(1 for _ in _non_comment_lines(_hook_text()))
    assert executable_lines > 10, (
        "hook has no executable body: %d executable lines" % executable_lines
    )


def test_preflight_all_is_invoked_by_the_hook():
    """The registry runner must be executed, not just present in tools/."""
    assert "tools/preflight_all.py" in _invoked_scripts(_hook_text()), (
        "tools/preflight_all.py exists but no executable line of "
        ".githooks/pre-commit invokes it -- its --self-test hook-parity check "
        "has therefore never run"
    )


def test_preflight_invocation_uses_the_pinned_interpreter():
    """Bare ``python``/``python3`` resolves to a different interpreter on this host."""
    lines = _hook_text().splitlines()
    hits = [
        lineno - 1
        for lineno, line in _invocation_lines(_hook_text())
        if "tools/preflight_all.py" in line
    ]
    assert hits, "no executable invocation line to inspect"
    for index in hits:
        window = " ".join(lines[max(0, index - 2): index + 1])
        assert "$PYTHON3" in window, (
            "line %d invokes preflight_all.py without $PYTHON3 -- bare python is "
            "3.14.7 GIL on this host, not the 3.15t production interpreter"
            % (index + 1)
        )
        assert not re.search(r"(?<![$\w])python3?\b", lines[index]), (
            "line %d uses a bare python token on the invocation itself" % (index + 1)
        )


def test_preflight_has_a_declared_override():
    """An escape hatch must be declared, not a silent bypass."""
    text = "\n".join(line for _n, line in _non_comment_lines(_hook_text()))
    assert "ALLOW_PREFLIGHT" in text, (
        "no declared override: a blocking gate with no escape hatch gets disabled "
        "by editing the hook, which is the silent bypass this project forbids"
    )


# --------------------------------------------------------------------------- #
# Registry coverage: every gate on disk is either run or explicitly adjudicated
# --------------------------------------------------------------------------- #


def test_gate_inventory_is_not_vacuous():
    """Guard the guard: a glob that finds nothing must fail, not pass."""
    inventory = sorted(p.name for p in TOOLS.glob("*_gate.py"))
    assert len(inventory) >= 8, "only found %r -- the scan is not seeing tools/" % (
        inventory,
    )
    assert PREFLIGHT.is_file(), "registry runner missing: %s" % PREFLIGHT


def test_every_gate_is_wired_or_named():
    """A new unwired gate FAILS: it may not silently join the backlog."""
    inventory = sorted(p.name for p in TOOLS.glob("*_gate.py"))
    invoked = {Path(p).name for p in _invoked_scripts(_hook_text())}

    unaccounted = [
        name for name in inventory if name not in invoked and name not in KNOWN_UNWIRED
    ]
    assert not unaccounted, (
        "gate(s) in tools/ that no hook runs and no allowlist names: %r -- wire "
        "it or add it to KNOWN_UNWIRED with a reason this file can verify"
        % (unaccounted,)
    )


def test_allowlist_entries_still_describe_real_files():
    """A stale allowlist entry is how a deleted gate hides a missing one."""
    missing = [name for name in KNOWN_UNWIRED if not (TOOLS / name).is_file()]
    assert not missing, "allowlisted gate(s) no longer on disk: %r" % (missing,)


def test_registered_slow_reasons_match_the_registry():
    """``registered-slow`` is a claim about preflight_all.py; verify it there."""
    text = _preflight_text()
    for name, (kind, _reason) in sorted(KNOWN_UNWIRED.items()):
        if kind != "registered-slow":
            continue
        path = "tools/%s" % name
        blocks = _gate_blocks_containing(text, path)
        assert len(blocks) == 1, (
            "%s is allowlisted as registered-slow, but the registry has %d "
            "Gate( row(s) naming %s" % (name, len(blocks), path)
        )
        assert "inside_hook=False" in blocks[0], (
            "%s is registered but NOT marked inside_hook=False -- either wire it "
            "or correct the allowlist reason" % name
        )


def test_unregistered_gap_is_named_and_does_not_grow():
    """A gate in no registry is a real gap; it is visible as a ratchet.

    This does not demand the gap be zero -- it demands the gap be *known*. A
    new unregistered gate, or someone quietly registering this one, fails here
    so the decision is re-made rather than assumed.
    """
    declared = {n for n, (kind, _r) in KNOWN_UNWIRED.items() if kind == "unregistered"}
    text = _preflight_text()
    observed = {
        name
        for name, (kind, _r) in KNOWN_UNWIRED.items()
        if kind == "unregistered"
        and not _gate_blocks_containing(text, "tools/%s" % name)
    }
    assert observed == declared, (
        "unregistered-gate set drifted: declared=%r observed=%r" % (declared, observed)
    )


def test_hardcoded_root_reason_is_still_true():
    """The moment the root is repointed at this repo, re-adjudicate the entry.

    The path is read out of the file rather than copied into this assertion:
    embedding it would add a second copy of the same defect the entry is about,
    and a fixed file would keep matching its own stale quote.
    """
    text = (TOOLS / "cain_render_gate.py").read_text(encoding="utf-8", errors="replace")
    match = re.search(r'AZ\s*=\s*r"([^"]+)"', text)
    assert match, (
        "no AZ root constant found in cain_render_gate.py -- its shape changed, "
        "re-check whether it can now be wired"
    )
    hardcoded = Path(match.group(1))
    assert hardcoded.is_absolute() and hardcoded != REPO, (
        "cain_render_gate.py no longer points its AZ constant at another tree -- "
        "re-check whether it can now be wired, then drop the allowlist entry"
    )
