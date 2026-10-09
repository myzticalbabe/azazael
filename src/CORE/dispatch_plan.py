#!/usr/bin/env python3
"""dispatch_plan.py — Plan-modeled dispatch (SOTA blueprint P2b, L5).

Composes two L5 steals as pure helpers over the existing flat dispatch
(MetaCluster orchestrates per-nature with no plan model — see
CORE/WORMS/METACLUSTER.py):

- Helium (plan modeling): model a multi-nature dispatch as a task DAG and
  topologically order it before execution, so shared prefixes are visible
  instead of being re-discovered per nature at runtime.
- Common-subgraph elimination: find identical ordered task segments shared
  by >=2 nature plans and report dedup savings (run once, fan results out).

Deliberately stdlib-only and LLM-free. Plan verdicts ride the existing
`verification_gate` ledger entry (subject "dispatch:<name>") — no new ledger
type. This module never executes dispatches; it validates plans and reports
sharing (remediate-don't-deny, PolicyGuide rule).

Usage:
    from CORE.dispatch_plan import plan_dag, eliminate_common_subgraphs

    dag = plan_dag([{"id": "discover", "deps": []},
                    {"id": "execute", "deps": ["discover"]}])
    sharing = eliminate_common_subgraphs(
        {"security": ["discover", "execute"],
         "monitor": ["discover", "execute", "report"]})
"""

from typing import Any, Dict, List, Set

#: Fail-open swallows recorded when the runtime recorder is unavailable. An
#: unrecorded swallow is indistinguishable from success, so every handler in
#: this module records first (degradation stays observable).
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


# -- Helium: DAG plan modeling ------------------------------------------------
def plan_dag(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Model a dispatch as a DAG and topologically order it (Helium steal).

    tasks: [{"id" (required, non-empty), "deps" (optional list of ids)}].

    Returns {"order", "levels" ({id: depth}), "valid", "gaps"} — valid iff
    every dep names a known task and the graph is acyclic. Gaps name what's
    wrong (repair targets): "task missing id", "duplicate-task:<id>",
    "unknown-dep:<task>:<dep>", "cycle-detected(...)".
    """
    gaps: List[str] = []
    ids: List[str] = []
    deps_of: Dict[str, List[str]] = {}
    for t in tasks or []:
        tid = str((t or {}).get("id", "")).strip()
        if not tid:
            gaps.append("task missing id")
            continue
        if tid in deps_of:
            gaps.append(f"duplicate-task:{tid}")
            continue
        ids.append(tid)
        raw = (t or {}).get("deps", []) or []
        deps_of[tid] = [str(d).strip() for d in raw if str(d).strip()]
    for tid in ids:
        for dep in deps_of[tid]:
            if dep not in deps_of:
                gaps.append(f"unknown-dep:{tid}:{dep}")

    # Kahn's algorithm over known edges only.
    indegree = {tid: 0 for tid in ids}
    children: Dict[str, List[str]] = {tid: [] for tid in ids}
    for tid in ids:
        for dep in deps_of[tid]:
            if dep in deps_of:
                indegree[tid] += 1
                children[dep].append(tid)
    order: List[str] = sorted([t for t in ids if indegree[t] == 0])
    levels: Dict[str, int] = {t: 0 for t in order}
    queue = list(order)
    while queue:
        node = queue.pop(0)
        for child in sorted(children[node]):
            indegree[child] -= 1
            levels[child] = max(levels.get(child, 0), levels[node] + 1)
            if indegree[child] == 0:
                order.append(child)
                queue.append(child)
    if len(order) != len(ids):
        stuck = sorted(set(ids) - set(order))
        gaps.append(f"cycle-detected({','.join(stuck)})")
    for tid in ids:
        levels.setdefault(tid, 0)
    return {"order": order, "levels": levels,
            "valid": not gaps, "gaps": gaps}


# -- Common-subgraph elimination ----------------------------------------------
def _first_segment_at(order: List[str], seg: tuple) -> int:
    """Index of the first occurrence of `seg` in `order` (-1 when absent)."""
    n = len(seg)
    if n == 0 or n > len(order):
        return -1
    for i in range(len(order) - n + 1):
        if tuple(order[i:i + n]) == seg:
            return i
    return -1


def eliminate_common_subgraphs(plans: Dict[str, List[str]],
                               min_len: int = 2) -> Dict[str, Any]:
    """Find ordered task segments shared by >=2 nature plans (CSE steal).

    plans: {nature: [task ids in execution order]}. A shared segment is a
    contiguous subsequence of length >= min_len appearing in >=2 natures'
    orders.

    Returns {"shared": [{"segment", "natures"}], "savings", "owners":
    [{"segment", "owner", "inherited_by"}], "deduped": {nature: order as
    actually run}, "elision": {nature: [task ids dropped]}, "executed_slots":
    {"before", "after"}}.

    `savings` is the redundant task-slot count the sharing creates (total
    shared slots beyond the first copy). `owners` names the ONE nature that
    executes each shared segment; every other nature holding it has its FIRST
    occurrence elided in `deduped`, because it inherits the owner's results.
    So the reducer is real -- "run once, fan results out" -- and `elision`
    records exactly which task ids each nature stopped running, which is what
    makes the saving auditable instead of merely reported. `deduped` equals
    the input for every nature that owns all of its shared segments.
    """
    plans = {str(k): [str(t) for t in (v or [])]
             for k, v in (plans or {}).items()}
    span: Dict[tuple, List[str]] = {}
    for nature, order in plans.items():
        seen = set()
        for i in range(len(order)):
            for j in range(i + int(min_len or 2), len(order) + 1):
                seg = tuple(order[i:j])
                if seg not in seen:
                    seen.add(seg)
                    span.setdefault(seg, []).append(nature)
    # Keep only maximal segments (drop any segment contained in a longer
    # shared one with identical nature sets).
    shared = [{"segment": list(seg), "natures": sorted(nats)}
              for seg, nats in span.items() if len(nats) >= 2]
    shared.sort(key=lambda s: (-len(s["segment"]), -len(s["natures"]),
                               s["segment"]))
    maximal = []
    for cand in shared:
        if any(set(cand["segment"]) <= set(kept["segment"])
               and len(cand["segment"]) < len(kept["segment"])
               and set(cand["natures"]) <= set(kept["natures"])
               for kept in maximal):
            continue
        maximal.append(cand)
    savings = sum(len(s["segment"]) * (len(s["natures"]) - 1)
                  for s in maximal)

    # -- the reducer: one deterministic owner per shared segment ------------
    # `natures` is already sorted, so the owner is stable across runs; a
    # non-owner elides its first occurrence and inherits the owner's result.
    owners: List[Dict[str, Any]] = []
    owner_of: Dict[tuple, str] = {}
    for info in maximal:
        seg = tuple(info["segment"])
        nats = list(info["natures"])
        owner_of[seg] = nats[0]
        owners.append({"segment": list(seg), "owner": nats[0],
                       "inherited_by": nats[1:]})

    deduped: Dict[str, List[str]] = {}
    elision: Dict[str, List[str]] = {}
    for nature, order in plans.items():
        drop: Set[int] = set()
        for seg, owner in owner_of.items():
            if owner == nature:
                continue
            at = _first_segment_at(order, seg)
            if at >= 0:
                drop.update(range(at, at + len(seg)))
        if drop:
            deduped[nature] = [t for i, t in enumerate(order) if i not in drop]
            elision[nature] = [order[i] for i in sorted(drop)]
        else:
            deduped[nature] = list(order)

    return {"shared": maximal, "savings": savings, "owners": owners,
            "deduped": deduped, "elision": elision,
            "executed_slots": {"before": sum(len(v) for v in plans.values()),
                               "after": sum(len(v) for v in deduped.values())}}


# -- Ledger citation (P1 gate, remediate-don't-deny) ---------------------------
def record_dispatch_plan(name: str, result: Dict[str, Any]) -> str:
    """Cite a plan verdict on the hash-chained ledger (fails open).

    subject "dispatch:<name>", accepted iff result valid / savings >= 0
    (sharing reports are findings, never denies). Returns the citation.
    """
    accepted = bool((result or {}).get("valid", True))
    gaps = list((result or {}).get("gaps", []) or [])
    remediations = [f"repair plan gap: {g}" for g in gaps]
    citation = ""
    try:
        from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
        citation = _at.audit_verification_gate(
            f"dispatch:{str(name or '?').strip()}", accepted,
            [f"plan-{('ok' if accepted else 'gaps')}:{len(gaps)}"],
            remediations)
    except Exception as exc:                      # noqa: BLE001 — ledger best-effort
        _note_failure("dispatch_plan:dag-ledger", exc)
    return citation


# -- Agora: role pools + affinity scheduling (P2b slice 2) ----------------------
def assign_roles(order: List[str],
                 task_roles: Dict[str, str],
                 role_pools: Dict[str, str]) -> Dict[str, Any]:
    """Pool dispatch tasks by role with affinity scheduling (Agora steal).

    order: task ids in execution order (a plan_dag "order").
    task_roles: {task: role} (inference vs orchestration vs tools, ...).
    role_pools: {role: pool} (cores pooled by role).

    Returns {"assignment" ({task: {"role", "pool"}}), "pools"
    ({pool: [tasks in order]}), "locality_hits" (adjacent same-pool pairs —
    affinity preserved, no pool switch), "valid", "gaps"}. Gaps:
    "unassigned-task:<t>" (no role), "role-for-unknown-task:<t>" (role for
    a task outside the order), "no-pool-for-role:<role>".
    """
    order = [str(t) for t in (order or [])]
    in_order = set(order)
    task_roles = {str(k): str(v).strip() for k, v in (task_roles or {}).items()}
    role_pools = {str(k): str(v).strip() for k, v in (role_pools or {}).items()}
    gaps: List[str] = []
    assignment: Dict[str, Dict[str, Any]] = {}
    for t in task_roles:
        if t not in in_order:
            gaps.append(f"role-for-unknown-task:{t}")
    for t in order:
        role = task_roles.get(t, "")
        if not role:
            gaps.append(f"unassigned-task:{t}")
            assignment[t] = {"role": "", "pool": ""}
            continue
        pool = role_pools.get(role, "")
        if not pool:
            gaps.append(f"no-pool-for-role:{role}")
        assignment[t] = {"role": role, "pool": pool}
    pools: Dict[str, List[str]] = {}
    for t in order:
        pool = assignment[t]["pool"] or "unpooled"
        pools.setdefault(pool, []).append(t)
    pools_seq = [assignment[t]["pool"] for t in order]
    locality_hits = sum(1 for a, b in zip(pools_seq, pools_seq[1:])
                        if a and a == b)
    return {"assignment": assignment, "pools": pools,
            "locality_hits": locality_hits,
            "valid": not gaps, "gaps": gaps}


# -- L4: rehearse-before-execute + backtrack-with-lesson -------------------------
def rehearse_dispatch(dag: Dict[str, Any],
                      assignment: Dict[str, Any]) -> Dict[str, Any]:
    """Dry-run a planned dispatch and predict failures (rehearsal slice).

    Never executes: folds plan gaps and assignment gaps into predicted
    failures plus per-pool load (oversubscription signal — Agora). Returns
    {"rehearsed": True, "predicted_failures", "pool_load", "go"} — go iff
    no predicted failures.
    """
    dag = dag or {}
    assignment = assignment or {}
    predicted = ([f"plan-gap:{g}" for g in dag.get("gaps", []) or []]
                 + [f"assign-gap:{g}" for g in assignment.get("gaps", []) or []])
    pool_load = {pool: len(tasks)
                 for pool, tasks in (assignment.get("pools", {}) or {}).items()}
    return {"rehearsed": True, "predicted_failures": predicted,
            "pool_load": pool_load, "go": not predicted}


def record_backtrack(branch: str, corrective_lesson: str) -> str:
    """Prune a failed branch but keep its corrective lesson (LoongReflect).

    Always accepted — backtracking is a finding, never a deny. The lesson
    rides the ledger as the remediation so the failure mode stays measured.
    Returns the citation (fails open).
    """
    branch = str(branch or "?").strip()
    lesson = str(corrective_lesson or "").strip() or "no lesson recorded"
    citation = ""
    try:
        from CORE import audit_trail as _at  # noqa: PLC0415 (lazy: no cycle)
        citation = _at.audit_verification_gate(
            f"backtrack:{branch}", True, [f"pruned:{branch}"],
            [lesson])
    except Exception as exc:                      # noqa: BLE001 — ledger best-effort
        _note_failure("dispatch_plan:subgraph-ledger", exc)
    return citation
