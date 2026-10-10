#!/usr/bin/env python3
"""structured_action.py — Agent-native software interface (blueprint L7).

Implements the ASIL mechanics (EP465, 2608.26991) as pure helpers:
screenshot-and-click is state-incomplete and semantically weak, so

- observations are STRUCTURED JSON validated for state-completeness
  (every required key present — the screenshot failure mode, named);
- actions are SEMANTIC and code-executable, validated against the
  application's contract (verb + target must exist — brittle GUI clicks
  fail here, with the repair named).

Deliberately stdlib-only and LLM-free. Verdicts ride the existing
`verification_gate` ledger entry (subject "asil:<app>") — no new ledger
type. Helpers never touch software; they validate interface artifacts
(remediate-don't-deny, PolicyGuide rule).

Adds the EP44 ReAct driver loop (2210.03629) on top of those two halves. The
map records the gap precisely: the act half and the observe half are present as
validators, and "the interleaved thought->action->observation driver loop that
induces and updates the plan" was missing -- the reasoning-trace controller.
`drive()` is that controller. It is LLM-free: the caller supplies cognition
through `thought_fn` and this module supplies the loop, the validation, and the
plan repair.

The plan that gets repaired is held by `workflow.py :: WorkflowEngine` /
`DependencyGraph`, which owns the node set and the execution order — so the EP44
host edit is a CALL PATH, not more reasoning: the engine calls
`drive_for_workflow_step()` and applies the returned `mutations` to its graph.
This module never imports the engine (the host imports us); inverting that edge
would trade one call for a cycle.
"""

from typing import Any, Dict, List

#: Fail-open swallows recorded when the runtime recorder is unavailable. An
#: unrecorded swallow is indistinguishable from success, so every handler in
#: this module records first.
_SWALLOWED: List[str] = []


try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # runtime absent: stay importable
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


def _note_failure(where: str, exc: BaseException | None = None) -> None:
    """Record a fail-open swallow. Never raises."""
    try:
        note_failure(where, exc)
    except Exception as _e:
        _SWALLOWED.append("%s:%s" % (where, type(_e).__name__))


# -- Structured observations -------------------------------------------------------
def observe(app: str, state: Dict[str, Any],
            required: List[str]) -> Dict[str, Any]:
    """Validate a structured JSON observation for completeness (ASIL).

    app: application name. state: the structured observation. required:
    keys the task needs (absent key == the state-incomplete screenshot
    failure). Returns {"app", "observation" (the state, verbatim),
    "complete", "gaps" (["state-incomplete:<key>"])}.
    """
    app = str(app or "?").strip()
    state = dict(state or {})
    gaps = [f"state-incomplete:{k}" for k in (required or [])
            if str(k) not in state]
    return {"app": app, "observation": state,
            "complete": not gaps, "gaps": gaps}


# -- Semantic actions ------------------------------------------------------------------
def semantic_action(action: Dict[str, Any],
                    contract: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a code-executable semantic action (ASIL).

    action: {"verb", "target", "args" (optional)}. contract: {"verbs": [...],
    "targets": [...]} — the application's deepest feasible access path.
    Returns {"executable", "gaps" (["unknown-verb:<v>",
    "unknown-target:<t>"])}. Unexecutable actions name their repair instead
    of failing silently at click time.
    """
    action = action or {}
    contract = contract or {}
    verb = str(action.get("verb", "")).strip()
    target = str(action.get("target", "")).strip()
    verbs = [str(v) for v in (contract.get("verbs", []) or [])]
    targets = [str(t) for t in (contract.get("targets", []) or [])]
    gaps = []
    if verb not in verbs:
        gaps.append(f"unknown-verb:{verb or '?'}")
    if target not in targets:
        gaps.append(f"unknown-target:{target or '?'}")
    return {"verb": verb, "target": target,
            "args": action.get("args", {}),
            "executable": not gaps, "gaps": gaps}


# -- Authority ledger + effect rows (EP327/EP382) ------------------------------------
def authority_ledger() -> Dict[str, Dict[str, float]]:
    """GRANTED vs EXERCISED accounting (EP327, ledger half).

    Reads technique-link rows: subjects that appear as granted authorities
    vs actions actually exercised. exercised>granted is the privilege gap.
    Read-only; empty store yields empty halves, never a fabrication.
    """
    granted: Dict[str, float] = {}
    exercised: Dict[str, float] = {}
    try:
        from CORE.local_memory import get_memory_store  # noqa: PLC0415
        rows = get_memory_store().query_memories(source="technique-link",
                                                 limit=200) or []
    except Exception as exc:                          # noqa: BLE001 - fail-open
        _note_failure("structured_action:authority-read", exc)
        rows = []
    for r in rows:
        d = (r or {}).get("data") or {}
        subj = str(d.get("subject", "?"))
        exercised[subj] = exercised.get(subj, 0.0) + 1.0
        for t in (d.get("granted_to") or []):
            granted[str(t)] = granted.get(str(t), 0.0) + 1.0
    gap = {s: exercised.get(s, 0.0) - granted.get(s, 0.0) for s in exercised}
    return {"granted": granted, "exercised": exercised, "gap": gap}


def effect_row(action: Dict[str, Any]) -> Dict[str, Any]:
    """Declared EFFECT ROW per action (EP382, declaration half).

    Every validated action declares its effect: reads/writes + scope.
    Obligation MONITORING over the rows (watching effects land) stays
    deferred: declaration without a watcher is honest intake, not control.
    """
    action = action or {}
    verb = str(action.get("verb", "")).strip()
    target = str(action.get("target", "")).strip()
    writes = verb in ("write", "push", "delete", "edit", "create")
    return {"verb": verb, "target": target,
            "effect": "write" if writes else "read",
            "scope": target.split("/")[0] if "/" in target else target,
            "typed_trace": [f"{verb}:{target}"]}


# -- Ledger citation ----------------------------------------------------------------------
def record_asil(app: str, result: Dict[str, Any]) -> str:
    """Cite an interface verdict on the hash-chained ledger (fails open)."""
    result = result or {}
    accepted = bool(result.get("complete", result.get("executable", True)))
    gaps = list(result.get("gaps", []) or [])
    citation = ""
    try:
        from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
        citation = _at.audit_verification_gate(
            f"asil:{str(app or '?').strip()}", accepted,
            [f"asil-{('ok' if accepted else 'gaps')}:{len(gaps)}"],
            [f"repair interface gap: {g}" for g in gaps])
    except Exception as exc:                          # noqa: BLE001 - ledger best-effort
        _note_failure("structured_action:asil-cite", exc)
    return citation


# -- EP44 ReAct driver loop (thought -> action -> observation) ----------------------
def drive(app: str, plan: List[str], contract: Dict[str, Any],
          required_keys: List[str], thought_fn: Any,
          max_steps: int = 12) -> Dict[str, Any]:
    """Interleave thought -> action -> observation and repair the plan (EP44).

    app: application name. plan: the goal decomposition (list of step ids).
    contract / required_keys: passed straight to `semantic_action` / `observe`.
    thought_fn: caller-supplied cognition, `fn(state) -> proposal`; a falsy
    return is the TERMINATING thought. A proposal is
    {"thought": str, "action": {"verb", "target", ...}, "state" (optional)}:
    when `state` is present it becomes the state observed this step.

    A gap does NOT crash the loop: it is recorded AND the plan is extended with
    a `repair:<gap>` step before the loop continues. That plan-update-on-gap is
    the technique; a controller that only reports gaps is the thing EP44
    replaces.

    Returns {"app", "steps", "plan", "updates", "gaps", "closed"}. `closed`
    is True only for a terminating thought reached with no gap outstanding.
    """
    app = str(app or "?").strip()
    plan = [str(s) for s in (plan or [])]
    steps: List[Dict[str, Any]] = []
    updates: List[Dict[str, Any]] = []
    gaps: List[str] = []
    closed = False
    state: Dict[str, Any] = {}

    for i in range(max(0, int(max_steps))):
        try:
            proposal = thought_fn(dict(state)) if callable(thought_fn) else None
        except Exception as exc:  # a broken thought is a named gap, not a crash
            note_failure("structured_action:L145", exc)
            gaps.append(f"thought-failed:{type(exc).__name__}")
            break
        if not proposal:
            closed = not gaps          # terminating thought closes only a clean run
            break

        proposal = dict(proposal)
        thought = str(proposal.get("thought", "") or "").strip()
        if isinstance(proposal.get("state"), dict):
            state = dict(proposal["state"])
        verdict = semantic_action(proposal.get("action") or {}, contract)
        obs = observe(app, state, required_keys)

        for gap in list(verdict["gaps"]) + list(obs["gaps"]):
            gaps.append(gap)
            repair = f"repair:{gap}"
            if repair not in plan:
                plan.append(repair)
                updates.append({"at": i, "inserted": repair, "because": gap})

        steps.append({"i": i, "thought": thought, "action": verdict,
                      "observation": obs})
        state = dict(obs["observation"])
        state.setdefault("last_verb", verdict["verb"])
        state.setdefault("last_target", verdict["target"])
    else:
        gaps.append("max-steps-reached")

    return {"app": app, "steps": steps, "plan": plan, "updates": updates,
            "gaps": gaps, "closed": closed}


def record_reasoning_trace(app: str, result: Dict[str, Any]) -> str:
    """Cite a ReAct trace verdict on the hash-chained ledger (fails open)."""
    result = result or {}
    accepted = bool(result.get("closed"))
    gaps = list(result.get("gaps", []) or [])
    updates = list(result.get("updates", []) or [])
    citation = ""
    try:
        from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
        citation = _at.audit_verification_gate(
            f"react:{str(app or '?').strip()}", accepted,
            [f"react-{('closed' if accepted else 'open')}:{len(gaps)}",
             f"react-plan-updates:{len(updates)}"],
            [f"repair reasoning gap: {g}" for g in gaps])
    except Exception as exc:                          # noqa: BLE001 - ledger best-effort
        _note_failure("structured_action:reasoning-cite", exc)
    return citation


# -- EP44 host hand-off: the engine applies these, we never import the engine -------
def plan_mutations(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Turn a `drive()` result's plan updates into engine-appliable insertions (EP44).

    `drive()` induces and repairs the plan; the graph that HOLDS the plan lives
    in `workflow.py :: WorkflowEngine` / `DependencyGraph`. This is the whole
    hand-off surface: one entry per recorded update, in the order they
    happened, each naming the step to insert and the gap that justifies it.

    Returns [{"after": int, "insert": str, "because": str, "step": str}] where
    `after` is the 0-based ReAct step index the insertion happened at and `step`
    is a node name the engine can use. A clean run legitimately yields [].

    A malformed update is RECORDED and skipped, never raised: the caller is an
    executor that must not die on one bad row.
    """
    out: List[Dict[str, Any]] = []
    for idx, upd in enumerate((result or {}).get("updates") or []):
        if not isinstance(upd, dict):
            _note_failure("structured_action:plan-mutation-not-a-dict", None)
            continue
        insert = str(upd.get("inserted", "") or "").strip()
        if not insert:
            _note_failure("structured_action:plan-mutation-without-insert", None)
            continue
        try:
            at = int(upd.get("at", -1))
        except (TypeError, ValueError) as exc:
            _note_failure("structured_action:plan-mutation-noninteger-at", exc)
            at = -1
        out.append({"after": at, "insert": insert,
                    "because": str(upd.get("because", "") or ""),
                    "step": f"react-{idx}:{insert}"})
    return out


def drive_for_workflow_step(app: str, plan: List[str], contract: Dict[str, Any],
                            required_keys: List[str], thought_fn: Any,
                            max_steps: int = 12,
                            cite: bool = True) -> Dict[str, Any]:
    """`drive()` plus the two things an engine STEP needs (EP44 host entry).

    Same contract as `drive()`. Adds `mutations` (what the graph applies) and,
    when `cite` is true, `citation` (the hash-chained trace verdict), so an
    executing step records its reasoning without importing the audit module
    itself. Returns drive()'s dict plus {"mutations": [...], "citation": str}.
    """
    result = dict(drive(app, plan, contract, required_keys, thought_fn,
                        max_steps))
    result["mutations"] = plan_mutations(result)
    result["citation"] = record_reasoning_trace(app, result) if cite else ""
    return result
