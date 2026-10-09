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

from typing import Any, Dict, List, Optional

#: Fail-open swallows recorded when the runtime recorder is unavailable. An
#: unrecorded swallow is indistinguishable from success, so every handler in
#: this module records first.
_SWALLOWED: List[str] = []


try:
    from CORE.technique_runtime import note_failure
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

    citation = ""
    if record:
        try:
            from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
            citation = _at.audit_verification_gate(
                f"skill:{name}", accepted, reasons, remediations)
        except Exception as exc:                      # noqa: BLE001 - ledger best-effort
            _note_failure("skill_library:commit-gate-cite", exc)
    return {"accepted": accepted, "reasons": reasons,
            "remediations": remediations, "citation": citation}


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
