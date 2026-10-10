#!/usr/bin/env python3
"""skill_library.py — Procedural-family skill library (SOTA blueprint P2a, L2).

Composes four steals into the skill-bank foundation:

- SkillGLoW (EP474): organize by procedural family (one prior per family,
  regenerate instance detail per task), gate commits on execution proof.
- CASS (EP455): bank gains hide coalition pollution — audit at family level;
  label-free masking after transfer (recorded as transfer note here; the
  masking policy itself is caller-owned).
- MAPD (EP401): the skill-artifact FORMAT — JSON protocols with task type,
  reasoning plan, and extractive grounding facts (style-normalized, dense).
- EvoSOP (EP354): the artifact LIFECYCLE. `protocol_artifact` constructs,
  `commit_gate` evaluate-admits and `family_index` organizes; the set was
  missing its two maintenance operators, so add order-preserving
  `merge_sops` (never a set union — a real order conflict is NAMED) and
  evidence-explained `prune_sops`.

Deliberately stdlib-only and LLM-free. Commit verdicts ride the existing
`verification_gate` ledger entry (subject "skill:<name>") — no new ledger
type. This module never executes skills; it validates artifacts and gates
admission (remediate-don't-deny, PolicyGuide rule).

Usage:
    from CORE.skill_library import protocol_artifact, commit_gate, family_index

    proto = protocol_artifact("worm-edit", ["plan", "edit", "verify"],
                              ["registry holds 200+ worms"])
    verdict = commit_gate({"name": " WormX ", "family": "dispatch"},
                          {"proof": ".audit/session_X.jsonl:12",
                           "transfer_masking": "masked to dispatch queries",
                           "version": 2})
    wider = merge_sops(proto, protocol_artifact(
        "worm-edit", ["plan", "edit", "audit"], ["ledger is hash-chained"]))
    trimmed = prune_sops([{"name": "WormX"}, {"name": "Unproven"}],
                         {"WormX": [".audit/session_X.jsonl:12"]})
"""

import hashlib
import json
from collections import Counter
from itertools import permutations
from typing import Any, Dict, List, Optional

from CORE.local_memory import get_memory_store

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


# -- MAPD: protocol artifact format -------------------------------------------
PROTOCOL_REQUIRED = ("task_type", "reasoning_plan", "grounding_facts")


def protocol_artifact(task_type: str, plan: List[str],
                      grounding: List[str]) -> Dict[str, Any]:
    """Build a style-normalized JSON skill protocol (MAPD steal).

    Returns {"task_type", "reasoning_plan", "grounding_facts", "valid",
    "gaps"} — valid iff task_type non-empty, plan has >=1 step, and at
    least one grounding fact. Gaps name what's missing (repair targets).
    """
    gaps: List[str] = []
    task = str(task_type or "").strip()
    steps = [str(s) for s in (plan or []) if str(s).strip()]
    facts = [str(g) for g in (grounding or []) if str(g).strip()]
    if not task:
        gaps.append("task_type missing")
    if not steps:
        gaps.append("reasoning_plan empty")
    if not facts:
        gaps.append("grounding_facts empty")
    return {"task_type": task, "reasoning_plan": steps,
            "grounding_facts": facts, "valid": not gaps, "gaps": gaps}


# -- SkillGLoW + CASS: commit gate ----------------------------------------------
def commit_gate(skill: Dict[str, Any],
                evidence: Optional[Dict[str, Any]],
                record: bool = True) -> Dict[str, Any]:
    """Gate a skill-bank commit on execution proof (SkillGLoW + CASS).

    skill: {"name", "family" (procedural family, required), ...}.
    evidence: {"proof" (execution citation, required),
               "transfer_masking" (str note, required — CASS post-transfer
               masking must be STATED even if "n/a: single-domain skill"),
               "version": int}.

    Accepted iff family present + proof present + masking stated. Every
    verdict is written to the hash-chained ledger via audit_verification_gate
    (subject "skill:<name>", lazy import, fails open). Rejections carry
    remediations, never bare denies.
    """
    name = str((skill or {}).get("name", "?")).strip()
    family = str((skill or {}).get("family", "")).strip()
    ev = evidence or {}
    proof = str(ev.get("proof", "")).strip()
    masking = str(ev.get("transfer_masking", "")).strip()

    reasons: List[str] = []
    remediations: List[str] = []
    accepted = True
    if not family:
        accepted = False
        reasons.append("no-family")
        remediations.append(
            "assign a procedural family before commit "
            "(see family_index unassigned bucket)")
    else:
        reasons.append(f"family-ok({family})")
    if not proof:
        accepted = False
        reasons.append("no-execution-proof")
        remediations.append(
            "gate commits on execution proof: run the skill and cite the "
            "ledger line (SkillGLoW commit rule)")
    else:
        reasons.append("proof-ok")
    if not masking:
        accepted = False
        reasons.append("no-transfer-masking")
        remediations.append(
            "state post-transfer masking (CASS rule), even if "
            "'n/a: single-domain skill'")
    else:
        reasons.append("masking-ok")
    version = ev.get("version", None)
    version_consumed = version is not None and str(version).strip() != ""
    reasons.append(f"version-seen({version})" if version_consumed
                   else "version-unread")

    citation = ""
    if record:
        try:
            from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
            citation = _at.audit_verification_gate(
                f"skill:{name}", accepted, reasons, remediations)
        except Exception as exc:                      # noqa: BLE001 - ledger best-effort
            _note_failure("skill_library:commit-gate-cite", exc)
    return {"accepted": accepted, "reasons": reasons,
            "remediations": remediations, "citation": citation,
            "version_consumed": version_consumed}


# -- CASS: family-level audit input ----------------------------------------------
def family_index(skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Group skill descriptors into procedural families (CASS audit input).

    Input: [{"name", "family" (optional), ...}]. Returns {"families":
    {family: [names]}, "unassigned": [names], "n_families", "n_skills"}.
    Coalition-pollution audits read family sizes: a family whose banked
    gains concentrate in one skill while siblings regress is the CASS
    pollution shape — flag, don't merge (audit finding, not verdict).
    """
    families: Dict[str, List[str]] = {}
    unassigned: List[str] = []
    for s in skills or []:
        nm = str(s.get("name", "?"))
        fam = str(s.get("family", "")).strip()
        if fam:
            families.setdefault(fam, []).append(nm)
        else:
            unassigned.append(nm)
    return {"families": families, "unassigned": unassigned,
            "n_families": len(families),
            "n_skills": sum(len(v) for v in families.values()) + len(unassigned)}


# -- EvoSOP: the two missing lifecycle operators (EP354) --------------------------
def _steps_of(sop: Any) -> List[str]:
    """Read a step sequence from a protocol artifact or a bare step list."""
    if isinstance(sop, dict):
        seq = sop.get("reasoning_plan", sop.get("steps", []))
    else:
        seq = sop
    return [str(s).strip() for s in (seq or []) if str(s).strip()]


def _facts_of(sop: Any) -> List[str]:
    """Read grounding facts from a protocol artifact ([] for a bare list)."""
    seq = sop.get("grounding_facts", []) if isinstance(sop, dict) else []
    return [str(s).strip() for s in (seq or []) if str(s).strip()]


def _uniq(seq: List[str]) -> List[str]:
    """First-occurrence dedupe: order preserved, identity collapsed."""
    out: List[str] = []
    for s in seq:
        if s not in out:
            out.append(s)
    return out


def _order_conflicts(a: List[str], b: List[str]) -> List[str]:
    """Name step pairs the two plans order oppositely (a true conflict).

    This is the case merge_sops must NOT resolve on its own: both plans bound
    the same two steps and disagree about which comes first, so any merged
    order breaks one of them.
    """
    pos_a = {s: i for i, s in enumerate(a)}
    pos_b = {s: i for i, s in enumerate(b)}
    shared = [s for s in pos_a if s in pos_b]
    out: List[str] = []
    for i, x in enumerate(shared):
        for y in shared[i + 1:]:
            if (pos_a[x] < pos_a[y]) != (pos_b[x] < pos_b[y]):
                out.append(f"order-conflict:{x}|{y}")
    return out


def _declared_conflicts(a: Any, b: Any) -> List[str]:
    """Name steps either SOP declares mutually exclusive with the other's."""
    def _excl(x: Any) -> List[str]:
        if not isinstance(x, dict):
            return []
        return [str(s).strip() for s in
                (x.get("mutually_exclusive_with", []) or [])]

    out: List[str] = []
    b_steps, a_steps = set(_steps_of(b)), set(_steps_of(a))
    for s in _excl(a):
        if s and s in b_steps:
            out.append(f"mutually-exclusive:{s}")
    for s in _excl(b):
        if s and s in a_steps:
            out.append(f"mutually-exclusive:{s}")
    return out


def merge_sops(a: Any, b: Any) -> Dict[str, Any]:
    """Merge two SOP/protocol artifacts order-preservingly (EvoSOP, EP354).

    A skill set grows by merging SOPs, and the two ways to get that wrong are
    a set union (which discards each plan's ordering) and a silent pick of one
    order over the other. This computes the shortest common SUPERSQUENCE, so
    the result is the minimal plan that preserves the order of BOTH inputs and
    emits a shared step once; `provenance` records which input carried each
    retained step (a / b / ab).

    Inputs accept a protocol artifact or a bare step list. Returns
    {"merged" (a protocol artifact), "provenance", "from" {a, b, shared},
    "deduped" (steps the merge collapsed), "conflicts", "gaps", "ok"}. A real
    order conflict, or a step one side declares mutually exclusive with the
    other's, is NAMED in `conflicts` and sets ok=False — never resolved.

    Production caller: tools/canon_drift_check._reconcile (EvoSOP union
    resolver with overwrite fallback, EP354).
    """
    raw_a, raw_b = _steps_of(a), _steps_of(b)
    sa, sb = _uniq(raw_a), _uniq(raw_b)
    gaps: List[str] = []
    if not sa:
        gaps.append("empty-plan:a")
    if not sb:
        gaps.append("empty-plan:b")

    # Shortest common supersequence, by DP over the deduped step lists.
    n, m = len(sa), len(sb)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if sa[i] == sb[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = 1 + min(dp[i + 1][j], dp[i][j + 1])

    plan: List[str] = []
    prov: List[Dict[str, str]] = []
    i = j = 0
    while i < n and j < m:
        if sa[i] == sb[j]:
            plan.append(sa[i])
            prov.append({"step": sa[i], "from": "ab"})
            i += 1
            j += 1
        elif dp[i + 1][j] <= dp[i][j + 1]:
            plan.append(sa[i])
            prov.append({"step": sa[i], "from": "a"})
            i += 1
        else:
            plan.append(sb[j])
            prov.append({"step": sb[j], "from": "b"})
            j += 1
    while i < n:
        if sa[i] not in plan:
            plan.append(sa[i])
            prov.append({"step": sa[i], "from": "a"})
        i += 1
    while j < m:
        if sb[j] not in plan:
            plan.append(sb[j])
            prov.append({"step": sb[j], "from": "b"})
        j += 1

    conflicts = _order_conflicts(sa, sb) + _declared_conflicts(a, b)

    ta = str(a.get("task_type", "")).strip() if isinstance(a, dict) else ""
    tb = str(b.get("task_type", "")).strip() if isinstance(b, dict) else ""
    task = ta if ta and ta == tb else "+".join(t for t in (ta, tb) if t)
    facts = _uniq(_facts_of(a) + _facts_of(b))
    merged = protocol_artifact(task, plan, facts)

    counts = {"a": 0, "b": 0, "shared": 0}
    for p in prov:
        counts["shared" if p["from"] == "ab" else p["from"]] += 1

    return {"merged": merged, "provenance": prov, "from": counts,
            "deduped": (len(raw_a) + len(raw_b)) - len(plan),
            "conflicts": conflicts, "gaps": gaps,
            "ok": not gaps and not conflicts}


def prune_sops(entries: List[Any], evidence: Dict[str, Any],
               min_support: int = 1,
               record: bool = False) -> Dict[str, Any]:
    """Drop SOPs the evidence does not support (EvoSOP, EP354).

    entries: SOP descriptors — a dict with "name", or a bare name.
    evidence: {name: support}, where support is a count or a list of
    citations (len() is used). An entry with no evidence key, or support
    below min_support, is pruned. Every decision is explained per entry, so a
    prune is auditable rather than a silent deletion.

    Returns {"kept", "pruned" (names), "reasons" {name: why}, "n_kept",
    "n_pruned", "gaps"}. gaps names malformed input, not pruning itself.

    No production caller yet (EP354): wiring it needs a real evidence source
    ({name: support}); never call with empty evidence — every entry would prune.
    """
    kept: List[str] = []
    pruned: List[str] = []
    reasons: Dict[str, str] = {}
    gaps: List[str] = []
    ev = evidence or {}
    floor = int(min_support)
    for e in entries or []:
        name = (str((e or {}).get("name", "")) if isinstance(e, dict)
                else str(e)).strip()
        if not name:
            gaps.append("unnamed-entry")
            continue
        raw = ev.get(name, None)
        if raw is None:
            support = 0
        elif isinstance(raw, (list, tuple, set)):
            support = len(raw)
        elif isinstance(raw, bool):
            support = int(raw)
        elif isinstance(raw, (int, float)):
            support = int(raw)
        else:
            support = 0
            gaps.append(f"unreadable-evidence:{name}")
        if support >= floor:
            kept.append(name)
            reasons[name] = f"kept:support={support}>={floor}"
        else:
            pruned.append(name)
            reasons[name] = ("no-evidence" if raw is None
                             else f"unsupported:support={support}<{floor}")

    result = {"kept": kept, "pruned": pruned, "reasons": reasons,
              "n_kept": len(kept), "n_pruned": len(pruned), "gaps": gaps}
    if record:
        result["citation"] = record_sop_ops(result)
    return result


def record_sop_ops(result: Dict[str, Any]) -> str:
    """Cite a lifecycle-operator verdict on the ledger (fails open).

    Accepts either a merge_sops or a prune_sops result. Subject is
    "sop:<n>", where n is the merged plan length or the kept count.
    """
    result = result or {}
    merged = result.get("merged") or {}
    if merged:
        n = len(merged.get("reasoning_plan", []) or [])
    else:
        n = int(result.get("n_kept", 0))
    conflicts = [str(c) for c in (result.get("conflicts", []) or [])]
    gaps = [str(g) for g in (result.get("gaps", []) or [])]
    accepted = bool(result.get("ok", not (conflicts or gaps)))

    reasons = ["sop-merge-ok" if accepted else "sop-merge-flags"]
    if merged:
        f = result.get("from", {}) or {}
        reasons.append(f"from-a={f.get('a', 0)}")
        reasons.append(f"from-b={f.get('b', 0)}")
        reasons.append(f"shared={f.get('shared', 0)}")
        reasons.append(f"deduped={result.get('deduped', 0)}")
    else:
        reasons.append(f"kept={result.get('n_kept', 0)}")
        reasons.append(f"pruned={result.get('n_pruned', 0)}")

    repairs = [f"resolve {c}" for c in conflicts] + [f"repair {g}" for g in gaps]
    citation = ""
    try:
        from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
        citation = _at.audit_verification_gate(
            f"sop:{n}", accepted, reasons, repairs)
    except Exception as exc:                          # noqa: BLE001 - ledger best-effort
        _note_failure("skill_library:sop-cite", exc)
    return citation


# -- Backlog builds (Oct-10 churn): small pure hosts --------------------------
# Each function below closes one named delta. All stdlib-only, no I/O except
# where stated. Anything needing a consumer, a model, or training stays
# deferred in the adapter text.


def replicator_step(family_sizes: Dict[str, int],
                    fitness: Dict[str, float],
                    dt: float = 0.1) -> Dict[str, Any]:
    """SkillSmith replicator update (EP265, input-side half).

    shares x_i -> x_i * (1 + dt * (f_i - mean_f)), renormalized (negatives
    clipped to 0). Missing fitness defaults to 0.0. Version-scoped nogoods
    (the second half of the delta) remain deferred: no nogood store exists.
    """
    total = sum(max(0, int(n)) for n in family_sizes.values()) or 1
    shares = {f: max(0, int(n)) / total for f, n in family_sizes.items()}
    fits = {f: float(fitness.get(f, 0.0)) for f in shares}
    mean_f = sum(shares[f] * fits[f] for f in shares)
    grown = {f: max(0.0, shares[f] * (1.0 + dt * (fits[f] - mean_f)))
             for f in shares}
    norm = sum(grown.values()) or 1.0
    nxt = {f: round(v / norm, 6) for f, v in grown.items()}
    return {"shares": {f: round(v, 6) for f, v in shares.items()},
            "next_shares": nxt, "mean_fitness": round(mean_f, 6)}


def render_plan_to_prompt(proto: Any,
                          exemplars: Optional[List[str]] = None) -> Dict[str, Any]:
    """Render a stored reasoning plan back into a model prompt (EP34).

    The stored `reasoning_plan` IS the step chain; this is the thin renderer
    the delta names, plus a few-shot exemplar block. Pure text, no model call.
    """
    steps = _steps_of(proto)
    facts = _facts_of(proto)
    lines = [f"Step {i + 1}: {s}" for i, s in enumerate(steps)]
    if facts:
        lines.append("Grounding:")
        lines += [f"- {g}" for g in facts]
    ex = [str(e) for e in (exemplars or []) if str(e).strip()]
    if ex:
        lines.append("Examples:")
        lines += [f"Example {i + 1}: {e}" for i, e in enumerate(ex)]
    return {"prompt": "\n".join(lines), "n_steps": len(steps),
            "n_facts": len(facts), "n_exemplars": len(ex)}


def check_transfer_mask(skill_family: str, masking: str,
                        target_domains: List[str]) -> Dict[str, Any]:
    """ENFORCED mask check (EP302): masking text must cover every target.

    commit_gate accepts masking as caller-owned prose (the gap). This is the
    enforcement half: each target domain must be named in the masking note,
    unless the note declares single-domain scope and there is at most one
    target. The layout-sketch index half of the delta stays deferred.
    """
    fam = str(skill_family or "").strip()
    note = str(masking or "")
    domains = [str(d) for d in (target_domains or []) if str(d).strip()]
    low = note.lower()
    single = ("n/a" in low or "single-domain" in low) and len(domains) <= 1
    covered = [d for d in domains if d.lower() in low]
    uncovered = [d for d in domains if d.lower() not in low]
    enforced = single or (bool(domains) and not uncovered)
    return {"family": fam, "enforced": enforced, "covered": covered,
            "uncovered": uncovered, "single_domain_claim": single}


def mine_action_sequences(trajectories: List[Any],
                          min_support: int = 2) -> Dict[str, Any]:
    """Mine repeated adjacent action pairs -> typed-pseudo-tool input (EP270).

    trajectories: [{“actions”: [...]}] or bare action lists. Counts ordered
    bigrams with support >= min_support. Typing the artifact (`types` field)
    stays deferred: no type-schema consumer exists.
    """
    seqs: List[List[str]] = []
    for t in trajectories or []:
        acts = t.get("actions", []) if isinstance(t, dict) else t
        acts = [str(a) for a in (acts or [])]
        seqs.append(acts)
    counts: Counter = Counter()
    for acts in seqs:
        for a, b in zip(acts, acts[1:]):
            counts[(a, b)] += 1
    motifs = [{"sequence": [a, b], "support": c}
              for (a, b), c in sorted(counts.items(), key=lambda kv: -kv[1])
              if c >= int(min_support)]
    return {"motifs": motifs, "n_trajectories": len(seqs)}


def compile_leaf_rules(decisions: List[Dict[str, Any]],
                       min_support: int = 2) -> Dict[str, Any]:
    """Compile frequent leaf decisions -> auditable rules (EP447, miner half).

    Groups by state, takes the majority action with support >= min_support.
    Low-support states land in `abstain_states`. Wiring the abstain fallback
    into a consumer stays deferred: no leaf-decision call site exists yet.
    """
    by_state: Dict[str, Counter] = {}
    for d in decisions or []:
        if not isinstance(d, dict):
            continue
        by_state.setdefault(str(d.get("state", "?")), Counter())[str(d.get("action", "?"))] += 1
    rules: List[Dict[str, Any]] = []
    abstain: List[str] = []
    for state, counter in by_state.items():
        action, support = counter.most_common(1)[0]
        total = sum(counter.values())
        if support >= int(min_support):
            rules.append({"when": state, "do": action, "support": support,
                          "confidence": round(support / max(total, 1), 4)})
        else:
            abstain.append(state)
    return {"rules": rules, "abstain_states": sorted(abstain)}


def shapley_marginal(members: List[str],
                     value: Any) -> Dict[str, Any]:
    """Shapley marginal-contribution audit over a coalition (EP455).

    Exact permutation Shapley (factorial cost — members capped at 8).
    value: callable frozenset -> float. Post-transfer masking-flag half stays
    deferred: no transfer pipeline exists to hang the flag on.
    """
    ms = [str(m) for m in (members or [])]
    if len(ms) > 8:
        raise ValueError("exact Shapley capped at 8 members")
    phis = {m: 0.0 for m in ms}
    perms = list(permutations(ms)) or [()]
    for perm in perms:
        seen: set = set()
        prev = float(value(frozenset()))
        for m in perm:
            seen.add(m)
            cur = float(value(frozenset(seen)))
            phis[m] += cur - prev
            prev = cur
    n = len(perms)
    return {"shapley": {m: round(v / n, 6) for m, v in phis.items()},
            "n_permutations": n,
            "grand_value": round(float(value(frozenset(ms))), 6)}


def distill_trajectory_to_protocol(traj: Dict[str, Any],
                                  task_type: str) -> Dict[str, Any]:
    """Trajectory -> protocol distiller, the EP155/EP401 shared wire.

    Steps come from traj[“actions”]; grounding from outcome + evidence. The
    MGPO reward split is reported, not optimized: per-step rewards pass
    through, the outcome reward is the scalar the loop would step from.
    """
    traj = traj or {}
    actions = [str(a) for a in (traj.get("actions") or [])]
    step_rewards = [float(r) for r in (traj.get("step_rewards") or [])]
    outcome = traj.get("outcome", "")
    evidence = [str(e) for e in (traj.get("evidence") or [])]
    grounding = ([f"outcome: {outcome}"] if outcome else []) + evidence
    proto = protocol_artifact(str(task_type or "distilled"), actions,
                              grounding or ["trajectory-distilled: no grounding"])
    return {"protocol": proto, "step_rewards": step_rewards,
            "outcome_reward": traj.get("outcome_reward", None),
            "n_steps": len(actions)}


def emit_skill_md(proto: Any, description: str) -> Dict[str, Any]:
    """Emit a SKILL.md payload from a protocol artifact (EP427).

    Frontmatter `description` is the only field this client pushes (AGENTS.md);
    the body carries the plan + grounding so a renderer can use the rest.
    """
    desc = str(description or "").strip() or "skill distilled from trajectories"
    task = str((proto or {}).get("task_type", "skill")) if isinstance(proto, dict) else "skill"
    steps = _steps_of(proto)
    facts = _facts_of(proto)
    body = ["---", f'description: "{desc}"', "---", f"# {task}",
            "## Reasoning plan"]
    body += [f"{i + 1}. {s}" for i, s in enumerate(steps)]
    body += ["## Grounding facts"] + [f"- {g}" for g in facts]
    return {"markdown": "\n".join(body) + "\n", "description": desc}


def record_experience(name: str, outcome: Any, citation: str,
                      store: Any = None) -> Dict[str, Any]:
    """Record one skill-experience row (EP255, recording half).

    The caller supplies a TYPED outcome (not sync stats, not drift — per the
    M-row lesson). refine_prompt() over the store stays deferred: no prompt
    synthesizer consumes these rows yet. Fails open (recorded=False).
    """
    try:
        if store is None:
            store = get_memory_store()
        cite = store.record_event(
            source="skill_library", event_type="skill_experience",
            data={"name": str(name), "outcome": outcome,
                  "citation": str(citation)},
            severity="info", tags=["skill", "experience"])
        return {"recorded": True, "citation": bool(cite)}
    except Exception as exc:                          # noqa: BLE001 - fail-open
        _note_failure("skill_library:record-experience", exc)
        return {"recorded": False, "citation": False}


def scan_witness_canonical(artifact: Any) -> Dict[str, Any]:
    """Witness-determinism scan (EP347, check half): canonical round-trip.

    An artifact is deterministic iff canonical JSON (sorted keys, compact
    separators) parses back to an equal object. Reports stability + sha, not
    a verdict: the calibrated-deopt guard flag needs a consumer (deferred).
    """
    required = ("task_type", "reasoning_plan")
    missing = [k for k in required
               if not (isinstance(artifact, dict) and artifact.get(k))]
    try:
        canonical = json.dumps(artifact, sort_keys=True,
                                separators=(",", ":"), default=str)
        stable = json.loads(canonical) == json.loads(
            json.dumps(artifact, default=str))
        sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    except Exception as exc:                          # noqa: BLE001 - probe
        _note_failure("skill_library:witness-scan", exc)
        return {"deterministic": False, "canonical_sha": "",
                "missing": missing or ["unserializable"]}
    return {"deterministic": stable and not missing, "canonical_sha": sha,
            "missing": missing}


def route_hierarchy(skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Hierarchical routing tree over procedural families (EP364).

    family_index is flat (depth 1, no manifests). This nests it: families
    become branch nodes; skills with a "domain" field become leaves under
    family/domain; the rest sit directly under the family. Leaf manifests
    stay LAZY (names only, no loaded payloads) per the delta. LIFO context
    ordering (most-recent-registered first) is reported as leaf order.
    """
    families = family_index(skills)
    tree: Dict[str, Any] = {}
    for fam, names in (families.get("families") or {}).items():
        node: Dict[str, Any] = {"leaves": [], "domains": {}}
        for nm in names:
            dom = ""
            for s in skills or []:
                if str(s.get("name", "?")) == nm:
                    dom = str(s.get("domain", "")).strip()
                    break
            if dom:
                node["domains"].setdefault(dom, []).append(nm)
            else:
                node["leaves"].append(nm)
        node["leaves"] = list(reversed(node["leaves"]))
        tree[fam] = node
    depth = 1 + (1 if any(n.get("domains") for n in tree.values()) else 0)
    return {"tree": tree, "depth": depth,
            "families": sorted(tree),
            "lazy_manifests": True,
            "unassigned": list(families.get("unassigned") or [])}
