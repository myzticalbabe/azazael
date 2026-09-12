# coding: utf-8
"""
PROTEUS hooks — the Phase D and Phase E integration surface.

Kept OUT of `scripts/evolution_cycle.py` on purpose. The cycle is a 2,200-line
production script; putting this logic inline would make it untestable and would
bury the two rules that actually matter here.

Phase D
-------
* **Cranium** (`cranium_decide`) pools margin evidence ACROSS eras.
  `_sprt_history` hard-stops at the first `pool_id`/`baseline_hash` change, and
  on the 2026-09-11 batch that break happened 28 times in 51 cycles (~1.8 cycles
  per era). The SPRT needs 2..6 same-era observations, so evidence could never
  accumulate: 1 promotion in 51 cycles. Treating each era as a random effect and
  pooling through the grand mean means a new era ADDS information rather than
  resetting the count.

* **Circulation** (`circulation_decide` / `circulation_update`) replaces the
  fixed arm gate. The old rule was
  `_cma_wanted = margin < 2 * PROMOTE_MARGIN`; every margin on that batch was
  >= 2.91 against a 1.5 threshold, so the second arm was skipped 50/50. A fixed
  threshold can only say "not needed right now" — it can never say "this operator
  earns its keep", and once a regime shifts the arm is structurally unreachable.

Phase E
-------
`morph_candidate_gene` rotates ONE extra gene into the search space per cycle.

The candidate list is short and deliberate, because a gene that is not CONSUMED
is worse than no gene at all: `_eval_salt` reads exactly four keys
(`learning_rate`, `epsilon`, `epsilon_decay`, `discount`), so a fifth gene added
to `GENE_BOUNDS` without a matching pass-through would be silently ignored and
the whole experiment void. `morph_trainer_kwargs` is the matching pass-through,
and only kwargs `train_from_memory` genuinely accepts are offered.

`val_ratio`/`test_ratio` are deliberately EXCLUDED: they only take effect when
the split flag is on, so alone they are inert. That is the same "every gene pays
rent" rule the Morph organ applies to pruning.

An inert candidate is not only one that is off. `by_session` DEFAULT-True means
a `by_session=True` trial passes the trainer exactly what production passes it,
so that row is equally unable to attribute the margin it reports. `morph_is_inert`
therefore compares the RESOLVED value against the trainer's own default
(`MORPH_TRAINER_DEFAULTS`) instead of against zero, `morph_record` stamps the
verdict on every row it writes, and `morph_dimension_summary` re-derives it for
older rows so the correction is retroactive.
"""

from __future__ import annotations

import json
import math
import os
import random
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .allocation import ThompsonAllocator, PROTEUS_ARMS, reward_for_outcome
from .evidence import EraEvidence

__all__ = [
    "cranium_decide",
    "cranium_override",
    "circulation_decide",
    "circulation_update",
    "SEARCH_ARMS",
    "MORPH_CANDIDATES",
    "MORPH_TRAINER_DEFAULTS",
    "morph_candidate_gene",
    "morph_strip",
    "morph_trainer_kwargs",
    "morph_effective",
    "morph_is_inert",
    "morph_treatment_value",
    "morph_ab_plan",
    "morph_record",
    "morph_dimension_summary",
    "row_payload",
]

# --------------------------------------------------------------------------
# shared helpers
# --------------------------------------------------------------------------

def row_payload(row: Any) -> Optional[dict]:
    """Normalise a memory-store row into its payload dict.

    Mirrors `evolution_cycle._row_payload` so the hooks can be used without
    importing the cycle (which runs a GA on import in older revisions).
    """
    if not isinstance(row, dict):
        return None
    data = row.get("data", row)
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return None
    return data if isinstance(data, dict) else None


def _margin_of(data: dict) -> Optional[float]:
    """Margin from a row, deriving it when the key predates the fix."""
    m = data.get("margin")
    if m is None:
        try:
            m = float(data.get("best_total")) - float(data.get("baseline"))
        except (TypeError, ValueError):
            return None
    try:
        f = float(m)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


# --------------------------------------------------------------------------
# Phase D — Cranium
# --------------------------------------------------------------------------
# A posterior sd at (or numerically indistinguishable from) zero is NOT
# confidence — it is an unidentifiable variance component pinned at its
# boundary. Measured 2026-09-12: three observations whose era means happened to
# coincide gave sd = 0.0, hence `p_above = 1.0` exactly, and the organ proposed
# a promotion. `prob_above` cannot distinguish "certain" from "could not
# estimate", so the decision gate must refuse to act on the degenerate case.
CRANIUM_MIN_SD = 1e-9
# ...and the floor is scaled to the decision scale, because an absolute
# epsilon cannot tell "confident" from "collapsed": measured sd for three
# coincident era means was 5.8e-07, i.e. ~1.3 million sigma of clearance on a
# 0.75 threshold. A sd that small is the moments estimator pinned at its
# boundary, not knowledge.
CRANIUM_MIN_SD_FRAC = 1e-3

def cranium_decide(rows: Iterable[Any], pool_id: str, margin_now: float,
                   threshold: float, alpha: float = 0.05,
                   limit: int = 400) -> Dict[str, Any]:
    """Cross-era promotion decision. Pure stdlib; identical under both interpreters.

    Returns `{'decision': 'promote'|'reject'|'continue', ...}` using the same
    vocabulary as `_sprt_decide`, so callers can swap it in without changes.
    """
    ev = EraEvidence(threshold=float(threshold), alpha=float(alpha))
    n_eras_seen: Dict[str, int] = {}
    # Within-era duplicate margins are ONE observation, not many.
    #
    # Measured on the live store (2026-09-12): one era carried 58 rows whose
    # margin was 3.295 on every one, and another repeated 0.403 and 0.212. A
    # bit-identical margin is the same candidate re-evaluated against an
    # unchanged baseline — it adds no information, but it DOES shrink the
    # posterior sd and push `p_above` toward certainty. Counting those repeats
    # is the "absence of new data read as evidence" failure the COMPAGES
    # cointegration fix already caught once in this codebase. Deduping is the
    # conservative direction: it can only make promotion HARDER.
    seen: Dict[str, set] = {}
    dup = 0
    used = 0
    for row in list(rows or [])[:int(limit)]:
        data = row_payload(row)
        if data is None:
            continue
        # Only v3-scale rows carry a comparable margin (same rule as the SPRT).
        if not str(data.get("fitness", "")).startswith("v3"):
            continue
        m = _margin_of(data)
        if m is None:
            continue
        era = str(data.get("pool_id") or "unknown")
        key = round(float(m), 6)
        bucket = seen.setdefault(era, set())
        if key in bucket:
            dup += 1
            n_eras_seen[era] = n_eras_seen.get(era, 0) + 1
            used += 1
            continue
        bucket.add(key)
        ev.observe(era, m)
        n_eras_seen[era] = n_eras_seen.get(era, 0) + 1
        used += 1

    # The cycle's own observation, attributed to the CURRENT era.
    try:
        _cur = round(float(margin_now), 6)
        if _cur not in seen.setdefault(str(pool_id), set()):
            ev.observe(str(pool_id), float(margin_now))
    except (TypeError, ValueError):
        pass

    post = ev.posterior()
    p_above = ev.prob_above(float(threshold))
    _sd = float(post["sd"])
    _floor = max(CRANIUM_MIN_SD, abs(float(threshold)) * CRANIUM_MIN_SD_FRAC)
    # NaN-safe: `not (x > floor)` is True for NaN too.
    degenerate = not (_sd > _floor)
    why = None
    if ev.n_eras < 2:
        # Cranium exists to POOL. With one era there is nothing to pool, so it
        # must defer to the SPRT rather than restate it with a point-estimate
        # variance. Measured: one era with two observations reported
        # p_above = 1.0000 and proposed a promotion from two numbers.
        decision = "continue"
        why = "single era: no cross-era pooling available"
    elif degenerate:
        # Variance is unidentifiable, so p_above (necessarily exactly 0.0 or
        # 1.0 here) carries no information. Refuse to act rather than convert
        # a boundary estimate into a decision.
        decision = "continue"
        why = "posterior sd %.2e below credible floor %.2e" % (_sd, _floor)
    # Strong evidence AGAINST improvement mirrors the SPRT's 'reject'.
    elif ev.n_observations >= 2 and p_above < float(alpha):
        decision = "reject"
    elif ev.n_observations >= 2 and ev.should_promote(float(alpha)):
        decision = "promote"
    else:
        decision = "continue"

    return {
        "decision": decision,
        "n_eras": ev.n_eras,
        # n_obs keeps its ORIGINAL contract — evidence units in the posterior,
        # the cycle's own observation included — because existing tests and
        # log consumers read it that way. The two new keys expose what it no
        # longer counts: rows read, and rows discarded as repeats.
        "n_obs": ev.n_observations,
        "rows_read": used,
        "duplicate_rows": dup,
        "prior_rows_used": used,
        "eras_prior": len(n_eras_seen),
        "posterior_mean": round(float(post["mean"]), 4),
        "posterior_sd": round(float(post["sd"]), 4),
        "tau": round(float(post["tau"]), 4),
        "sigma": round(float(post["sigma"]), 4),
        "p_above_threshold": round(float(p_above), 4),
        "threshold": float(threshold),
        # True when the variance could not be estimated, so the reported
        # p_above is a boundary artifact and the decision is forced to
        # 'continue'. Surfaced rather than swallowed: an organ that silently
        # declines looks identical to one that found nothing.
        "degenerate_variance": bool(degenerate),
        "raw_posterior_sd": _sd,
        "sd_floor": _floor,
        # Set only when the organ DECLINED to decide. An organ that silently
        # declines is indistinguishable from one that found nothing.
        "deferred": why,
    }


# --------------------------------------------------------------------------
# Phase D — Circulation
# --------------------------------------------------------------------------

# Arms that are genuinely FUNDABLE as an alternative search operator.
#
# PROTEUS_ARMS lists every organ named in the plan, but only `cma` and `de` have
# an implemented second-search-arm in the cycle (`_run_cma_arm`); `tpe`,
# `morph`, `arena` and `chorus` are wired elsewhere or not as a duel.
#
# Measured on the first live circulation batch (2026-09-12): the allocator drew
# `arena`, `morph` and `chorus`, the cycle ran the slot-alternating `cma` arm
# anyway, and the feedback credited `cma` — three posterior updates for an arm
# that was never selected. That is exactly the mislabelling the forcing
# parameter was added to prevent, and it happens whenever the decision set is
# wider than the executable set. So the set is narrowed to what can run.
SEARCH_ARMS: Tuple[str, ...] = ("ga", "cma", "de")


def cranium_override(sprt_decision: str, cranium: Dict[str, Any]) -> Dict[str, Any]:
    """Apply the Cranium policy to an SPRT decision. Pure; no I/O, no globals.

    Extracted from `evolution_cycle.main` on purpose. Inline, this two-branch
    policy sat 2,000 lines inside the production script behind a `beats` guard
    that no cycle in the 2026-09-12 batches satisfied (25/25 had `beats=False`),
    so it was reachable only in a regime that never occurred and therefore
    never executed, never asserted, and never observed. As a pure function both
    directions are testable without running a 2,350-line cycle.

    Both directions are deliberate:
      * **rescue** — the SPRT needs 2..6 SAME-era observations and the era
        breaks every ~1.8 cycles, so `continue` after n=1 is the common shape
        even when the candidate cleared the margin gate. Pooled cross-era
        evidence is the only way that case can ever promote.
      * **veto** — the mirror case, and the E9 protection: a promotion whose
        pooled posterior sits below the threshold across eras is the exact
        shape that bought 0/4 holdout passes.

    Returns `{'decision', 'sprt_ok', 'action'}` where action is one of
    `rescue` / `veto` / `agree` / `noop`. A malformed or absent Cranium verdict
    yields `noop`, so the SPRT decision stands unchanged.
    """
    cd = (cranium or {}).get("decision")
    sprt_ok = str(sprt_decision) == "promote"
    if cd not in ("promote", "reject", "continue"):
        return {"decision": sprt_decision, "sprt_ok": sprt_ok, "action": "noop"}
    if cd == "promote" and not sprt_ok:
        return {"decision": "promote", "sprt_ok": True, "action": "rescue"}
    if cd == "reject" and sprt_ok:
        # Withdrawn to 'continue', never to 'reject': the SPRT has not itself
        # rejected anything, and recording a rejection would overstate how
        # decisive the evidence was (the E2 lesson from the 50-run analysis).
        return {"decision": "continue", "sprt_ok": False, "action": "veto"}
    return {"decision": sprt_decision, "sprt_ok": sprt_ok, "action": "agree"}


def _load_allocator(state_path: str, arms: Sequence[str]) -> ThompsonAllocator:
    if state_path and os.path.exists(state_path):
        try:
            alloc = ThompsonAllocator.load(state_path)
            for a in arms:
                if a not in alloc.arms:
                    alloc.arms.append(a)
                    alloc._s[a] = alloc._prior[0]
                    alloc._f[a] = alloc._prior[1]
            return alloc
        except Exception:
            pass
    return ThompsonAllocator(list(arms), floor=0.02, rng=random.Random())


def circulation_decide(state_path: str, arms: Sequence[str] = SEARCH_ARMS,
                       primary: str = "ga") -> Dict[str, Any]:
    """Choose which operator to fund this cycle (Thompson sampling).

    `run_secondary` False means the primary operator stands unopposed this
    cycle. Unlike the replaced threshold, a starved arm keeps a floor share, so
    it stays discoverable when the regime changes.
    """
    arms = list(arms or SEARCH_ARMS)
    alloc = _load_allocator(state_path, arms)
    picked = alloc.choose(1)
    arm = picked[0] if picked else primary
    w = alloc.weights()
    return {
        "arm": arm,
        "run_secondary": arm != primary,
        "weights": {k: round(v, 4) for k, v in sorted(w.items())},
        "report": alloc.report(),
    }


def circulation_update(state_path: str, arm: str, outcome: str,
                       arms: Sequence[str] = SEARCH_ARMS) -> Dict[str, Any]:
    """Feed one cycle's outcome back to the allocator, then persist.

    Outcome strings are weighted by `reward_for_outcome`: a holdout pass is worth
    far more than beating a reused snapshot, because E9 showed a +3.3 snapshot
    margin buying 0/4 holdout passes. Unknown outcomes fail closed.
    """
    arms = list(arms or SEARCH_ARMS)
    alloc = _load_allocator(state_path, arms)
    success, weight = reward_for_outcome(outcome)
    try:
        alloc.update(str(arm), bool(success), float(weight))
    except Exception as exc:
        return {"updated": False, "reason": str(exc)[:120]}
    try:
        if state_path:
            os.makedirs(os.path.dirname(os.path.abspath(state_path)), exist_ok=True)
            alloc.save(state_path)
    except Exception as exc:
        return {"updated": True, "saved": False, "reason": str(exc)[:120]}
    return {"updated": True, "saved": True, "arm": arm, "outcome": outcome,
            "success": bool(success), "weight": float(weight)}


# --------------------------------------------------------------------------
# Phase E — Morph gene rotation
# --------------------------------------------------------------------------
# Every entry must name a kwarg `RLTrainMemory.train_from_memory` accepts AND a
# pass-through in `morph_trainer_kwargs`, or the gene is inert (see module doc).
MORPH_CANDIDATES: Tuple[Tuple[str, str, float, float, str], ...] = (
    # (name, kind, lo, hi, trainer_kwarg)
    ("use_schema_features", "bool", 0.0, 1.0, "use_schema_features"),
    ("by_session", "bool", 0.0, 1.0, "by_session"),
)

# The trainer's OWN defaults for the two switch kwargs, read from
# `RLTrainLoop.train_from_memory` (learning_rl.py:302-303). This is the whole
# basis of the inert rule: a trial whose resolved value EQUALS the default
# produces a trainer call identical to production's, so the recorded
# `fitness - baseline_fitness` cannot be about the gene — it measures the
# surrounding search (GA vs the production snapshot). Measured 2026-09-12:
# 65 morph rows, 64 retained, and `use_schema_features` resolved OFF in 31/31
# of its trials (raw 0.056, 0.069, False) while being credited every time.
# Written as data, not prose, so `test_morph_inert_matches_trainer_defaults`
# can pin it to the real signature instead of letting the two drift.
MORPH_TRAINER_DEFAULTS: Dict[str, Any] = {
    "use_schema_features": False,
    "by_session": True,
}


def morph_candidate_gene(cycle_index: int,
                         candidates: Sequence[Sequence[Any]] = MORPH_CANDIDATES
                         ) -> Optional[Dict[str, Any]]:
    """Which extra gene to trial this cycle. Deterministic round-robin.

    Round-robin rather than random so every candidate gets an equal number of
    cycles over a batch — otherwise the comparison against the 4-gene best is
    confounded by which gene happened to be sampled most.
    """
    cands = list(candidates or MORPH_CANDIDATES)
    if not cands:
        return None
    name, kind, lo, hi, kwarg = cands[int(cycle_index) % len(cands)]
    return {"name": str(name), "kind": str(kind), "lo": float(lo),
            "hi": float(hi), "kwargs": str(kwarg),
            "cycle_index": int(cycle_index)}


def morph_gene_specs(cycle_index: int,
                     base_bounds: Dict[str, Tuple[float, float]],
                     enabled: bool = True,
                     candidates: Sequence[Sequence[Any]] = MORPH_CANDIDATES
                     ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """Mixed-type specs for `EvolutionEngine.set_gene_specs`, plus the added gene.

    The dict key is `"type"` (NOT `"kind"`) because that is the key the engine
    reads: `EvolutionEngine.set_gene_specs` looks up `spec.get("type", "float")`.
    Emitting `"kind"` was a real integration bug — the engine would fall back to
    `"float"`, so a gene declared `bool` would have been sampled as a CONTINUOUS
    coordinate and then collapsed by `morph_trainer_kwargs`'s `bool(v)`, which
    makes almost every draw True. Verified against `evolution.py`; this is why
    the round-trip test `test_morph_specs_round_trip_through_engine` exists.

    Floats keep the legacy `(lo, hi)` tuple shape the engine auto-detects; the
    added gene is an explicit spec dict, which is what makes a `bool` gene a
    switch rather than a continuous coordinate.
    """
    specs: Dict[str, Any] = {k: {"type": "float", "lo": float(v[0]), "hi": float(v[1])}
                             for k, v in (base_bounds or {}).items()}
    gene = morph_candidate_gene(cycle_index, candidates) if enabled else None
    if gene is not None:
        specs[gene["name"]] = {"type": gene["kind"],
                               "lo": gene["lo"], "hi": gene["hi"]}
    return specs, gene


def morph_strip(genes: Dict[str, Any],
                candidates: Sequence[Sequence[Any]] = MORPH_CANDIDATES
                ) -> Dict[str, Any]:
    """Remove every Phase E gene from a seed genome.

    THE bug this exists to prevent, measured 2026-09-12: the morph history
    contained a row with dimension **6** carrying BOTH candidate genes. Seeds
    come from `last_best_genes()`, which returns the previous cycle's winner —
    including whatever extra gene that cycle trialled. The engine's
    `initialize_population` fills MISSING genes from the current specs but
    never PRUNES keys it was not told about, so a seed carrying `by_session`
    entered the next cycle (which added `use_schema_features`) and left with
    both. Dimension then crept 4 -> 5 -> 6 and never came back.

    Two consequences, both fatal to the measurement:
      * fitness stops being comparable across rows (the plan's stated risk),
      * the per-gene verdict is confounded, because a gene trialled ALONGSIDE
        another is not the same treatment as the gene trialled alone.

    Stripping makes each cycle a clean 4 + 1 factorial.
    """
    drop = {str(c[0]) for c in (candidates or MORPH_CANDIDATES)}
    return {k: v for k, v in (genes or {}).items() if k not in drop}


def morph_trainer_kwargs(genes: Dict[str, Any]) -> Dict[str, Any]:
    """Pass extra genes through to the trainer. THE point of Phase E.

    Without this, `_eval_salt` reads only its four hardcoded keys and a fifth
    gene is silently discarded — the search would appear to grow while the
    fitness landscape stayed four-dimensional.
    """
    out: Dict[str, Any] = {}
    for name, kind, _lo, _hi, kwarg in MORPH_CANDIDATES:
        if name not in (genes or {}):
            continue
        v = genes[name]
        if kind == "bool":
            out[kwarg] = _as_bool(v)
        else:
            try:
                out[kwarg] = float(v)
            except (TypeError, ValueError):
                continue
    return out


def _as_bool(v: Any) -> bool:
    """Coerce a gene to bool, THRESHOLDING continuous values at 0.5.

    `bool(v)` is wrong here because the secondary search arms are continuous
    optimisers: they are handed the switch as a (0.0, 1.0) coordinate, so a
    CMA draw of 0.3 would have read as True and the switch would have been
    "on" for almost every candidate. Thresholding makes the relaxed search
    agree with the GA's discrete switch.
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("1", "true", "yes", "on")
    try:
        return float(v) >= 0.5
    except (TypeError, ValueError):
        return False


def morph_effective(gene: Any, genes: Dict[str, Any]) -> Any:
    """What `train_from_memory` actually RECEIVES for the trialled gene.

    `None` means "not determinable" (unknown gene, gene absent from the genome,
    or an uncoercible value) and must never be read as "inert" — absence of
    evidence is not evidence, which is the rule MUTAGEN also encodes.
    """
    name = (gene or {}).get("name") if isinstance(gene, dict) else gene
    name = str(name or "")
    if not name or not isinstance(genes, dict) or name not in genes:
        return None
    for cname, kind, _lo, _hi, _kwarg in MORPH_CANDIDATES:
        if cname != name:
            continue
        v = genes[name]
        if kind == "bool":
            return _as_bool(v)
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    return None


def morph_is_inert(gene: Any, genes: Dict[str, Any],
                   defaults: Optional[Dict[str, Any]] = None) -> bool:
    """True when the trial arm's trainer call is IDENTICAL to production's.

    A trial only measures its gene if it changes what the trainer is called
    with. Resolving to the trainer's own default leaves the call unchanged, so
    the margin it reports belongs to the search, not to the gene — crediting it
    is the "genome grew for free" failure MUTAGEN scores as `free_growth`.

    Note this is per-gene and that is not cosmetic: `by_session` defaults to
    **True**, so a `by_session=True` trial is as inert as a
    `use_schema_features=False` one, even though a naive on/off reading would
    call the first a real treatment.
    """
    name = (gene or {}).get("name") if isinstance(gene, dict) else gene
    name = str(name or "")
    if not name:
        return False
    kwarg = next((c[4] for c in MORPH_CANDIDATES if c[0] == name), None)
    if kwarg is None:
        return False
    table = MORPH_TRAINER_DEFAULTS if defaults is None else defaults
    if kwarg not in table:
        return False                     # no known default -> cannot claim inert
    eff = morph_effective(name, genes)
    if eff is None:
        return False
    return bool(eff) == bool(table[kwarg])


def morph_treatment_value(gene: Any) -> Any:
    """The value that MOVES this gene off the trainer's default.

    For a bool switch that is simply the negation, and "negation" is per-gene:
    `by_session` must be set to **False** to be a treatment, because True is what
    the trainer already does. This is the value the A/B arm is forced to.
    """
    name = (gene or {}).get("name") if isinstance(gene, dict) else gene
    name = str(name or "")
    if not name:
        return None
    kwarg = next((c[4] for c in MORPH_CANDIDATES if c[0] == name), None)
    if kwarg is None or kwarg not in MORPH_TRAINER_DEFAULTS:
        return None
    return not bool(MORPH_TRAINER_DEFAULTS[kwarg])


def morph_ab_plan(gene: Any, genes: Optional[Dict[str, Any]] = None) -> Optional[dict]:
    """A matched pair for the trialled gene: default arm vs treatment arm.

    THE problem this exists to solve. The Morph trial as originally recorded
    compares a 5-gene champion against the 4-gene PRODUCTION baseline, so from
    the moment the added gene resolves to its default the difference it reports
    is the search's, not the gene's — and 52 of 69 rows did exactly that while
    being credited as wins.

    The A/B holds everything else fixed: SAME champion genome, SAME frozen
    pools, SAME seeds, ONE gene changed — the trainer's default value versus
    the value that moves it. That difference is attributable to the gene by
    construction, whatever the search was doing.

    Returns `{"gene", "control", "treatment", "default"}` or None when the
    candidate is not a known switch (never a made-up pair).
    """
    name = (gene or {}).get("name") if isinstance(gene, dict) else gene
    name = str(name or "")
    if not name:
        return None
    kwarg = next((c[4] for c in MORPH_CANDIDATES if c[0] == name), None)
    if kwarg is None or kwarg not in MORPH_TRAINER_DEFAULTS:
        return None
    if genes is not None and name not in genes:
        return None
    default = bool(MORPH_TRAINER_DEFAULTS[kwarg])
    return {"gene": name,
            "default": default,
            "control": default,
            "treatment": (not default)}


def morph_ab_delta(control_fitness: Any, treatment_fitness: Any) -> Optional[float]:
    """treatment - control, or None when either side is missing/non-finite.

    Sign convention: POSITIVE means the trial arm beat the trainer's default,
    i.e. the gene earned its place. Kept explicit because the same quantity
    computed in the other order would invert every verdict.
    """
    if control_fitness is None or treatment_fitness is None:
        return None
    try:
        c, t = float(control_fitness), float(treatment_fitness)
        delta = t - c
        if delta != delta or delta in (float("inf"), float("-inf")):
            return None
        return round(delta, 4)
    except (TypeError, ValueError):
        return None


def morph_record(history_path: str, cycle_index: int, gene: Optional[dict],
                 genes: Dict[str, Any], fitness: Optional[float],
                 baseline_fitness: Optional[float] = None,
                 ab: Optional[dict] = None) -> None:
    """Append one JSONL row: which gene was trialled, dimension, fitness.

    Dimension is recorded alongside fitness on purpose — the plan's honest-risk
    mitigation. Once the genome can grow, fitness is only comparable WITHIN a
    dimension, so any headline number must be reported per dimension.

    The row also carries the trial's VERDICT ABOUT ITSELF, added 2026-09-12
    after 65 rows were appended that no reader could attribute:

      * `applied` — the kwargs the trainer actually received (post-resolution),
      * `inert`   — whether those kwargs equal the trainer's defaults, i.e.
                    whether this row can speak about the gene at all,
      * `ab`      — the matched default-vs-treatment pair for the gene, when the
                    caller ran one. THIS is the attributable measurement: the
                    `fitness`/`baseline_fitness` pair above answers "did a wider
                    genome beat production", which conflates the gene with the
                    search.

    Recomputed on read for older rows (see `morph_dimension_summary`), so a
    ledger written before this change is still classified correctly rather than
    silently trusted.
    """
    try:
        applied = morph_trainer_kwargs(genes)
        row = {
            "cycle_index": int(cycle_index),
            "gene": (gene or {}).get("name"),
            "dimension": len(genes or {}),
            "fitness": None if fitness is None else float(fitness),
            "baseline_fitness": (None if baseline_fitness is None
                                 else float(baseline_fitness)),
            "extra": {k: genes[k] for k in (genes or {})
                      if k in [c[0] for c in MORPH_CANDIDATES]},
            "applied": {k: applied[k] for k in sorted(applied)},
            "inert": morph_is_inert(gene, genes),
            "ab": (dict(ab) if isinstance(ab, dict) and ab else None),
        }
        os.makedirs(os.path.dirname(os.path.abspath(history_path)), exist_ok=True)
        with open(history_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    except Exception:
        pass


def _row_ab_delta(r: dict) -> Optional[float]:
    """The matched-pair delta recorded on a row, if it carries a usable one.

    Derives it from the two arm scores when they are present but the summary
    `delta` is not, so a row that records the measurement still counts as
    measured instead of silently reading as "no A/B".
    """
    ab = r.get("ab")
    if not isinstance(ab, dict):
        return None
    if ab.get("delta") is not None:
        try:
            d = float(ab["delta"])
            if d == d and d not in (float("inf"), float("-inf")):
                return round(d, 4)
        except (TypeError, ValueError):
            pass
    return morph_ab_delta(ab.get("control_fitness"),
                          ab.get("treatment_fitness"))


def _row_inert(r: dict) -> bool:
    """Inert for a ledger row: the recorded flag, else recomputed.

    Legacy rows (written before `inert` existed) are re-derived from `gene` +
    `extra` through the same rule, so the fix applies retroactively instead of
    only to future cycles.
    """
    if isinstance(r.get("inert"), bool):
        return bool(r["inert"])
    extra = r.get("extra") if isinstance(r.get("extra"), dict) else {}
    gene = r.get("gene")
    if not extra or not gene:
        return False
    if gene in extra:
        return morph_is_inert(gene, extra)
    return False


def morph_dimension_summary(history_path: str) -> Dict[str, Any]:
    """Per-dimension fitness, plus a per-gene verdict.

    The per-gene verdict is the measurement Phase E exists to produce: does a
    wider genome actually beat the 4-gene best, and if so, which added gene did
    it — or was the extra dimension dead weight that should be pruned?
    """
    rows: List[dict] = []
    try:
        with open(history_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if isinstance(d, dict) and d.get("fitness") is not None:
                    rows.append(d)
    except Exception:
        pass

    by_dim: Dict[int, List[float]] = {}
    by_gene: Dict[str, List[float]] = {}          # EFFECTIVE trials only
    by_gene_inert: Dict[str, List[float]] = {}
    by_gene_ab: Dict[str, List[float]] = {}       # matched-pair deltas
    inert_rows = 0
    measured_rows = 0
    for r in rows:
        try:
            fit = float(r["fitness"])
            by_dim.setdefault(int(r["dimension"]), []).append(fit)
        except (KeyError, TypeError, ValueError):
            continue
        g = r.get("gene")
        if not g:
            continue
        _ab = _row_ab_delta(r)
        if _ab is not None:
            measured_rows += 1
            by_gene_ab.setdefault(str(g), []).append(_ab)
        if _row_inert(r):
            inert_rows += 1
            by_gene_inert.setdefault(str(g), []).append(fit)
        else:
            by_gene.setdefault(str(g), []).append(fit)

    def _stat(vals: List[float]) -> dict:
        m = sum(vals) / len(vals)
        var = sum((x - m) ** 2 for x in vals) / len(vals)
        return {"n": len(vals), "best": max(vals), "mean": round(m, 4),
                "sd": round(math.sqrt(var), 4)}

    base = [v for v in by_dim.get(4, [])]
    out = {
        "by_dimension": {str(k): _stat(v) for k, v in sorted(by_dim.items())},
        "by_gene": {k: _stat(v) for k, v in sorted(by_gene.items())},
        "by_gene_inert": {k: _stat(v) for k, v in sorted(by_gene_inert.items())},
        "by_gene_ab": {k: _stat(v) for k, v in sorted(by_gene_ab.items())},
        "n_rows": len(rows),
        "inert_rows": inert_rows,
        "effective_rows": len(rows) - inert_rows,
        "measured_rows": measured_rows,
        "inert_share": (round(inert_rows / float(len(rows)), 4) if rows else None),
        "baseline_4gene_best": max(base) if base else None,
        "verdict": {},
    }
    b4 = out["baseline_4gene_best"]
    # The verdict is computed from EFFECTIVE trials only. A gene whose every
    # trial left the trainer call at its default is reported as UNTESTED rather
    # than as a winner — that is the whole bug this guards: the previous code
    # read `by_gene` straight off every row, so `use_schema_features` "won" 31
    # times on a switch the trainer never saw change.
    for g in sorted(set(list(out["by_gene"].keys())
                         + list(out["by_gene_inert"].keys()))):
        st = out["by_gene"].get(g)
        n_inert = (out["by_gene_inert"].get(g) or {}).get("n", 0)
        ab = out["by_gene_ab"].get(g) or {}
        ab_vals = by_gene_ab.get(g) or []
        best = None if st is None else st["best"]
        out["verdict"][g] = {
            "best": best,
            "informative_n": 0 if st is None else st["n"],
            "inert_n": n_inert,
            "tested": bool(st),
            # The matched A/B is the attributable reading: same champion, same
            # pools, one gene moved. Reported alongside (not instead of) the
            # fitness comparison, because they answer different questions.
            "ab_n": ab.get("n", 0),
            "ab_mean": (None if not ab_vals
                        else round(sum(ab_vals) / len(ab_vals), 4)),
            "ab_positive": sum(1 for x in ab_vals if x > 0.0),
            # "did the treatment beat the trainer's default, on average" -- a
            # TALLY, not a significance claim; the per-row deltas are in the
            # ledger so anyone wanting a test can run one on the real numbers.
            "ab_beats_default": (None if not ab_vals
                                 else bool(sum(ab_vals) / len(ab_vals) > 0.0)),
            "delta_vs_4gene": (None if (b4 is None or best is None)
                               else round(best - b4, 4)),
            "beats_4gene": (None if (b4 is None or best is None)
                            else bool(best > b4)),
            "note": (None if st else
                     "no informative trial: every row resolved to the trainer "
                     "default, so the ledger cannot say what this gene does"),
        }
    return out
