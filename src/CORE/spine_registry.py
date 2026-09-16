# coding: utf-8
"""
spine_registry — Process-wide shared state for the neural mesh spine.

Two shared organs, one module, no heavy imports:

1. SPINE_MAP  — the live topology snapshot that SpineMapperWorm publishes
   and any consumer (dashboard, CLI, Red Queen) can read. Keyed by
   "env:worm" so multi-env gossip can merge without collisions.

2. HOMEOSTAT — the cross-process feedback ledger. NatureCluster.execute()
   records every worm outcome here (record_outcome()); HomeostatWorm consumes
   it and proposes cooldown/priority adjustments. This closes the loop that
   previously ended at "results returned to caller and dropped".

Design constraints:
- stdlib only, no PAMS/MemoryBus dependency at module level (avoid cycles)
- all mutable state behind threading.RLock (3.14t free-threading safe)
- bounded memory: outcome history and events are capped
- pure data: no worm classes registered here (registry hygiene)

Usage:
    from CORE.spine_registry import record_outcome, get_homeostat_view
    record_outcome("mesh", "MeshRouterWorm", True, 12.3)
    view = get_homeostat_view()
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

__version__ = "1.0.0"

# ── SPINE MAP (topology snapshot) ────────────────────────────────────
# key: "env:worm" -> node record
_SPINE_MAP: Dict[str, Dict[str, Any]] = {}
_SPINE_LOCK = threading.RLock()
_SPINE_MAP_MAX = 4096  # bound memory under gossip storms
_SPINE_EVENTS: List[Dict[str, Any]] = []
_SPINE_EVENTS_MAX = 200

# ── HOMEOSTAT (feedback ledger) ──────────────────────────────────────
# key: "nature:worm" -> {"successes": int, "failures": int, ...}
_HOMEOSTAT: Dict[str, Dict[str, Any]] = {}
_HIST_MAX = 20  # per-worm rolling duration history
_OUTCOME_EVENTS_MAX = 200

# ── OUTCOME RING (striped, append-only, merged on read) ──────────────
# The ring used to be one shared list appended under the global lock — the
# purest LongAdder case in the module: append-only, never read-modify-write,
# order-insensitive for every consumer. It now has its own lock stripes, so
# a write takes an outcome lock only when another thread picked the same
# stripe (8 stripes — 8 consecutive thread idents, which the interpreter
# hands out sequentially, so in practice each thread keeps its own).
#
# Trade, stated plainly: rings are per-stripe, so worst-case in-memory
# history is 8 × _OUTCOME_EVENTS_MAX events instead of 200. Every *read*
# is still merged, re-sorted and trimmed to exactly _OUTCOME_EVENTS_MAX, so
# the public bound and the single-threaded history depth are unchanged
# (asserted in test_spine_mesh_ledger_striping.py).
_OUTCOME_STRIPE_COUNT = 8
_OUTCOME_LOCKS: tuple = tuple(threading.RLock() for _ in range(_OUTCOME_STRIPE_COUNT))
_OUTCOME_RINGS: tuple = tuple([] for _ in range(_OUTCOME_STRIPE_COUNT))


def _outcome_stripe() -> tuple:
    """``(lock, ring)`` for the calling thread's stripe."""
    idx = threading.get_ident() % _OUTCOME_STRIPE_COUNT
    return _OUTCOME_LOCKS[idx], _OUTCOME_RINGS[idx]


def _append_outcome_event(event: Dict[str, Any]) -> None:
    """Append to this thread's outcome ring, self-capping. Lock is per-stripe."""
    lock, ring = _outcome_stripe()
    with lock:
        ring.append(event)
        if len(ring) > _OUTCOME_EVENTS_MAX:
            del ring[:len(ring) - _OUTCOME_EVENTS_MAX]


def _merged_outcome_events() -> List[Dict[str, Any]]:
    """All rings merged, oldest-first, trimmed to _OUTCOME_EVENTS_MAX.

    The trim is what preserves the documented public bound: callers can
    never observe more than _OUTCOME_EVENTS_MAX events regardless of how
    many stripes are live.
    """
    merged: List[Dict[str, Any]] = []
    for lock, ring in zip(_OUTCOME_LOCKS, _OUTCOME_RINGS):
        with lock:
            merged.extend(ring)
    merged.sort(key=lambda e: e.get("at", ""))
    if len(merged) > _OUTCOME_EVENTS_MAX:
        del merged[:len(merged) - _OUTCOME_EVENTS_MAX]
    return merged


def _clear_outcome_events() -> None:
    """Drop every ring's contents (reset path)."""
    for lock, ring in zip(_OUTCOME_LOCKS, _OUTCOME_RINGS):
        with lock:
            ring.clear()


def _outcome_event_count() -> int:
    """Raw (untrimmed) event count across stripes, for health reporting."""
    return sum(len(ring) for ring in _OUTCOME_RINGS)


# ── STRIPED LEDGER LOCKS (F9: stop serialising the hot path) ────────
# Audit F9: "every outcome takes a global RLock, and the reflex arc does a
# registry lookup inside it." True — and it is a *scale* defect: at 224 worms
# it is fine, and it is the first thing that breaks when the fleet 10×'s.
#
# Instead of LongAdder-style per-thread counters (which would make the
# learning numbers order-dependent and therefore *different*), the ledger
# uses **key striping** — the ConcurrentHashMap shape. Every key
# ("nature:worm") still has exactly ONE authoritative record mutated under
# exactly one lock, so every learned value is bit-identical to the
# single-lock version (asserted in test_spine_mesh_ledger_striping.py), but
# two different worms no longer contend with each other. Only same-key
# updates serialise, which is not an option to remove: it is a
# read-modify-write.
#
# LOCK ORDER INVARIANT — "holding any Q stripe implies holding every
# homeostat stripe". Writers acquire homeostat-stripe(key) then
# Q-stripe(key); readers acquire the whole barrier (`_HOMEOSTAT_LOCK`,
# all homeostat stripes then all Q stripes). A writer can therefore only be
# blocked by a peer writer (bounded work) or by a reader that holds no
# homeostat stripe — never by a reader holding homeostat stripes. That is
# what makes this deadlock-free rather than merely unlikely.
_STRIPE_COUNT = 16
_HOMEOSTAT_STRIPES: tuple = tuple(threading.RLock() for _ in range(_STRIPE_COUNT))
_Q_STRIPES: tuple = tuple(threading.RLock() for _ in range(_STRIPE_COUNT))

# ── SCAR LOCK (reflex state, previously unguarded) ──────────────────
# _SCARS was mutated from record_outcome() and read from q_order()/views
# with no lock at all. That was survivable only because those mutations
# happened inside the global ledger lock. Now that writers use stripes, the
# scar table gets an explicit lock rather than an accidentally-inherited one.
_SCAR_LOCK = threading.RLock()


def _stripe_index(key: str) -> int:
    """Stable stripe for a ledger key.

    ``hash()`` on str is randomised per process (PYTHONHASHSEED) but stable
    within one, which is all a stripe assignment needs; no ordering and no
    persistence depends on it.
    """
    return hash(key) % _STRIPE_COUNT


def _homeostat_stripe(key: str) -> threading.RLock:
    """The one lock that guards ``_HOMEOSTAT[key]``."""
    return _HOMEOSTAT_STRIPES[_stripe_index(key)]


def _q_stripe(key: str) -> threading.RLock:
    """The one lock that guards the Q-table entries for ``key``."""
    return _Q_STRIPES[_stripe_index(key)]


class _LedgerBarrier:
    """Reader/resetter gate: acquires EVERY stripe, homeostat then Q.

    Keeps the old ``with _HOMEOSTAT_LOCK:`` spelling working — and meaning
    "no writer anywhere may run while I read" — without putting 32 acquires
    on the write path. Every multi-key read (views, snapshots, persist,
    reset, gossip merge) uses it; only the two hot writers bypass it.
    """

    __slots__ = ("_stripes",)

    def __init__(self, stripes: tuple) -> None:
        self._stripes = stripes

    def __enter__(self) -> "_LedgerBarrier":
        for lock in self._stripes:
            lock.acquire()
        return self

    def __exit__(self, *exc: Any) -> bool:
        for lock in reversed(self._stripes):
            lock.release()
        return False


# Barrier spanning both tables, in the canonical order.
_HOMEOSTAT_LOCK = _LedgerBarrier(_HOMEOSTAT_STRIPES + _Q_STRIPES)

# ── Q-WEIGHT BRAINSTEM ─────────────────────────────────────────────
# Shared, process-wide reinforcement table keyed "nature:worm". Every
# record_outcome() auto-reinforces here (the fast signal), and
# NatureCluster.execute() reads it to order execution: healthy worms
# run earlier, failing ones later. Distinct from SynapseWeightWorm's
# private table, which is the batch-learned routing substrate; this is
# the always-on brainstem reflex.
_Q_WEIGHTS: Dict[str, float] = {}
_Q_ALPHA_BASE = 0.2
_Q_MIN, _Q_MAX = -1.0, 1.0
# Adaptive alpha: per-key variance tracking for G2
_Q_VARIANCE: Dict[str, float] = {}  # key -> running variance of Q-values
_Q_UPDATE_COUNTS: Dict[str, int] = {}  # key -> number of updates seen

# ── REFLEX ARC + SCARS (autonomic response, no worm in the loop) ────
# record_outcome() reacts INSTANTLY to consecutive failures: demotes
# priority, inflates cooldown, and opens a "scar" that demotes the worm
# below all healthy peers in q_order() until it succeeds again. This is
# the spinal reflex — HomeostatWorm is the slower deliberative layer.
_SCARS: Dict[str, Dict[str, Any]] = {}   # "nature:worm" -> {"since", "reason"}
_REFLEX_FAIL_THRESHOLD = 4               # consecutive failures before reflex
_REFLEX_COOLDOWN_MULT = 3.0              # cooldown inflation on reflex
_REFLEX_COOLDOWN_CAP = 3600.0            # absolute cooldown ceiling

# ── POLICY JOURNAL (endocrine memory) ─────────────────────────────
# Every programmatic change to worm priority/cooldown is journalled so
# it can be audited and reverted as a whole. The delibrate layer
# (HomeostatWorm apply=True, SpineCycleWorm) writes here; the reflex
# arc writes too (actor="reflex") so a revert undoes emergency measures
# as well. Bounded; thread-safe.
_POLICY_JOURNAL: List[Dict[str, Any]] = []
_POLICY_JOURNAL_MAX = 100
_POLICY_LOCK = threading.RLock()

# ── POLICY LATEST (compacting adaptation memory) ─────────────────────
# Audit G10 (2026-09-14): the journal above is a bounded FIFO ring, and
# `worm_registry._replay_policy_journal()` reconstructs adapted cooldowns by
# replaying it on restart. That makes the *audit trail* load-bearing for
# *state*, so once the ring wraps past 100 entries a worm whose last
# adaptation has been evicted silently reverts to its decorator default —
# a scale-dependent regression that only appears once the fleet is busy.
#
# This map keeps exactly one entry per worm (its latest adaptation), so the
# replay source is bounded by the number of worms rather than by journal
# traffic. The ring keeps growing/shrinking as the human-readable audit log;
# this is the authoritative state. Keyed by worm name.
_POLICY_LATEST: Dict[str, Dict[str, Any]] = {}


def _remember_policy(entry: Dict[str, Any]) -> None:
    """Fold one journal entry into the compacting latest-per-worm map.

    Last writer wins, which is exactly the semantics the replay needs
    (`later adaptation supersedes the earlier one`). Caller holds no lock
    requirement: safe to call with or without `_POLICY_LOCK` held.
    """
    worm = entry.get("worm")
    if not worm:
        return
    with _POLICY_LOCK:
        _POLICY_LATEST[str(worm)] = dict(entry)


def get_policy_latest() -> Dict[str, Dict[str, Any]]:
    """Latest journalled adaptation per worm (the replay source). Copy."""
    with _POLICY_LOCK:
        return {k: dict(v) for k, v in _POLICY_LATEST.items()}

# ── QUARANTINE VOTE LEDGER (cross-env quorum that can actually decide) ──
# Audit 2026-09-15: RedQueenWorm.order_quarantine() built a FRESH
# QuorumVoterWorm(quorum=2) on every call and cast exactly ONE vote from the
# local env, so `decided` (distinct count >= 2) could never become True — the
# quarantine gate was structurally dead code. Two changes make it live while
# preserving the original safety intent (one env must never quarantine alone):
#   1. votes are counted per DISTINCT ENV, not per call, and
#   2. the ledger is persisted AND gossiped, so a peer env's vote arrives
#      in-process instead of dying in another process's memory.
# A single env still cannot reach quorum. Two envs can.
_QUARANTINE_VOTES: Dict[str, Dict[str, Dict[str, Any]]] = {}
_QUARANTINE_LOCK = threading.RLock()
_QUARANTINE_FINDINGS_MAX = 256


def cast_quarantine_vote(finding: str, env: str, verdict: str = "quarantine",
                         quorum: int = 2) -> Dict[str, Any]:
    """Record one env's vote on `finding`; decide on DISTINCT envs.

    Later votes from the same env replace that env's earlier vote (an env
    changing its mind must not stuff the ballot). Returns the tally plus
    `decided` = the leading verdict has >= `quorum` distinct envs.
    Thread-safe; never raises.
    """
    finding = str(finding or "")[:160]
    env = str(env or "")[:40]
    verdict = str(verdict or "quarantine")[:40]
    if not finding or not env:
        return {"success": False, "error": "finding and env are required"}
    # Fold any persisted votes in first, so a second env's vote that arrived
    # via gossip (or a previous session) counts toward this quorum.
    _ensure_loaded()
    with _QUARANTINE_LOCK:
        box = _QUARANTINE_VOTES.setdefault(finding, {})
        # `at` stays human-readable ISO (it is displayed and parsed by
        # callers); `hlc` is the ordering stamp the merge uses. Additive on
        # purpose: no time-based consumer of `at` changes behaviour.
        box[env] = {"verdict": verdict, "at": _now_iso(), "hlc": _hlc_now()}
        if len(_QUARANTINE_VOTES) > _QUARANTINE_FINDINGS_MAX:
            oldest = min(_QUARANTINE_VOTES.items(),
                         key=lambda kv: max((v.get("at", "") for v in kv[1].values()),
                                            default=""))
            _QUARANTINE_VOTES.pop(oldest[0], None)
        tally: Dict[str, int] = {}
        for rec in box.values():
            tally[rec["verdict"]] = tally.get(rec["verdict"], 0) + 1
        top, count = ("", 0)
        if tally:
            top, count = max(tally.items(), key=lambda kv: kv[1])
        return {"success": True, "finding": finding, "envs": sorted(box),
                "env_count": len(box), "tally": tally, "top": top,
                "count": count, "quorum": int(quorum),
                "decided": count >= int(quorum)}


def get_quarantine_votes(finding: Optional[str] = None) -> Dict[str, Any]:
    """Read the quarantine ledger (one finding, or the whole ledger). Copy."""
    _ensure_loaded()
    with _QUARANTINE_LOCK:
        if finding is not None:
            return {str(finding): dict(_QUARANTINE_VOTES.get(str(finding), {}))}
        return {k: {e: dict(v) for e, v in box.items()}
                for k, box in _QUARANTINE_VOTES.items()}


# ── FABRIC STATE STORE (the mesh's operational memory) ──────────────
# Audit 2026-09-15 (finding #7): save_spine_state() persisted the spine's
# *learning* (map, ledger, Q, scars, policy, trust, anomaly model) but
# NOTHING persisted the fabric natures' *operational* state — routing
# tables, elected leader + term, quorum tallies, federated clients, model
# shard catalogue, endpoint loads. All of it lived in per-instance dicts,
# cached in NatureCluster.instances, so it was lost on every new
# NatureClusterManager() and on restart. The mesh remembered how to feel
# and forgot what it knew.
#
# The fabric worms live in CORE.WORMS.expansion.*, which this module must
# not import (cycle). So they publish *through* this store: hydrate in
# __init__, publish on mutation. Keyed by provider (class name), bounded,
# persisted, and gossiped with the rest of the spine payload.
# Each record is `{provider, updated_at, state, field_stamps}`. `state` is the
# flattened attribute map callers already expect; `field_stamps` carries one
# HLC stamp per attribute. Per-FIELD stamps are what make two envs that each
# publish a different subset of a provider's attributes converge to the union
# instead of clobbering each other (deep dive 2026-09-15).
_FABRIC_STATE: Dict[str, Dict[str, Any]] = {}
_FABRIC_LOCK = threading.RLock()
_FABRIC_STATE_MAX = 256


def _hlc_now() -> str:
    """A fresh stamp from the process-wide hybrid logical clock."""
    try:
        from CORE.hlc import hlc
        return hlc().stamp()
    except Exception:  # pragma: no cover - defensive
        return _now_iso()


def _observe_stamp(stamp: Any) -> None:
    """Fold a remote stamp into the local clock (causal ordering).

    Without this the local clock could hand out a stamp lower than one it has
    already seen, which is the inversion the HLC exists to prevent.
    """
    try:
        from CORE.hlc import hlc
        hlc().observe(str(stamp or ""))
    except Exception:  # pragma: no cover - defensive
        pass


def get_clock_skew_ms() -> int:
    """> 0 when the newest observed peer clock is ahead of ours.

    Diagnostic only — ordering never consults it. The mesh could not measure
    clock skew before, so skew-induced divergence was indistinguishable from
    a real disagreement.
    """
    try:
        from CORE.hlc import hlc
        return int(hlc().skew_ms())
    except Exception:  # pragma: no cover - defensive
        return 0


def _fabric_field_stamp(rec: Dict[str, Any], attr: str) -> str:
    """Ordering stamp for one attribute, falling back to the record-level one.

    The fallback is the migration path: a record written before per-field
    stamps existed has only `updated_at`, and treating it as the stamp for
    every field is the best available reading of it.
    """
    try:
        from CORE.hlc import normalize_stamp
        stamps = rec.get("field_stamps") or {}
        own = stamps.get(attr)
        if own:
            return normalize_stamp(str(own))
        return _rec_stamp(rec, "updated_at")
    except Exception:  # pragma: no cover - defensive
        return str(rec.get("updated_at") or "")


def _rec_stamp(rec: Any, iso_field: str) -> str:
    """Ordering stamp for a record: its HLC sidecar, else the legacy field.

    The additive half of the migration. Every record that participates in a
    cross-env merge carries BOTH a human-readable ISO field (`updated_at`,
    `last_at`, `at` — parsed and displayed by existing callers) and an `hlc`
    sidecar. Ordering consults the sidecar; nothing else changes. A record
    written before the sidecar existed normalises from its ISO field, so old
    and new records still compare correctly during the upgrade window.
    """
    if not isinstance(rec, dict):
        return ""
    stamp = rec.get("hlc")
    if not stamp:
        stamp = rec.get(iso_field)
    try:
        from CORE.hlc import normalize_stamp
        return normalize_stamp(str(stamp or ""))
    except Exception:  # pragma: no cover - defensive
        return str(stamp or "")


def _stamp_adoptable(stamp: str) -> bool:
    """False when a stamp is too far in the future to be trusted for ordering.

    The HLC refuses a remote physical time beyond its drift window so that a
    broken peer clock cannot pin the LOCAL clock (`HybridLogicalClock.observe`).
    Ordering is a separate path that uses the peer's stamp directly, so without
    this guard the same poisoned value still won every merge it took part in:

    * a real store was found carrying 98 stamps at year 2999
      (`032472162000000-04631-windows`, ~+30,682,668,693,692ms) that had been
      written before the drift bound existed;
    * those records would have won every future merge of that field until
      real time reached year 2999, i.e. permanently, with no way for a correct
      peer's later write to displace them.

    Refusing at the ordering chokepoint makes such a value inert: it cannot
    win, and it cannot propagate (a peer receives our poisoned stamp as a
    candidate and refuses it too, so the era stops spreading). An unparseable
    or legacy stamp is NOT refused here — it is handled by normalisation, and
    refusing it would re-break the migration path.
    """
    try:
        from CORE.hlc import MAX_DRIFT_MS, unpack_stamp
        import time as _t
        u = unpack_stamp(str(stamp or ""))
        if u is None:
            return True
        return u[0] <= int(_t.time() * 1000) + MAX_DRIFT_MS
    except Exception:  # pragma: no cover - defensive
        return True


def _stamp_newer(candidate: Any, current: Any) -> bool:
    """True when `candidate` is strictly newer than `current`, HLC-aware.

    Both sides are normalised before comparison, which is what lets a legacy
    naive-ISO timestamp persisted by an older build coexist with a new HLC
    stamp. A raw string compare would order *every* HLC stamp before *every*
    ISO one (HLC stamps begin with a zero-padded millisecond count, so they
    start with `0`), silently handing the win to the older write during the
    whole migration window.

    An empty candidate never wins, preserving the original guard's behaviour.

    Beyond-drift stamps are handled in BOTH directions, and the asymmetry is
    deliberate:

    * a candidate from beyond the drift window never wins, and the refusal is
      recorded on the shared clock so the diagnostic reports it even when the
      merge is what saw the stamp first; and
    * a *stored* value from beyond the window does not win either — otherwise a
      poisoned record would be frozen in place until real time caught up with
      it (year 2999), and a correct peer's later write could never displace it.
      Treating it as "not newer" means the first trustworthy write heals it.

    See `_stamp_adoptable`.
    """
    # Emptiness is judged on the RAW value, not the normalised one:
    # `normalize_stamp("")` is a perfectly valid zero stamp, so normalising
    # first makes an absent candidate look like a real one — and against a
    # poisoned incumbent that would let "no stamp at all" win.
    raw = str(candidate if candidate is not None else "").strip()
    if not raw:
        return False
    try:
        from CORE.hlc import normalize_stamp
        a = normalize_stamp(raw)
        b = normalize_stamp(str(current if current is not None else ""))
    except Exception:  # pragma: no cover - defensive
        a = raw
        b = str(current or "")
    if not _stamp_adoptable(a):
        _observe_stamp(candidate)
        return False
    if not _stamp_adoptable(b):
        # The incumbent is the untrustworthy one: an adoptable candidate wins
        # by default, which is how a poisoned record gets repaired.
        return True
    return a > b


def publish_fabric_state(provider: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Merge one fabric worm's snapshot in, per field. Never raises.

    This used to *replace* the provider record wholesale. Because a provider
    key is shared by every env (each env's ``Lilith``, ``ModelShardServerWorm``
    ... publishes under the same name), a peer with a newer stamp erased the
    other env's fields entirely — which is why a catalogue meant to hold two
    envs' shards could only ever hold one. Fields are now merged individually
    and a publish only touches the attributes it actually carries.
    """
    provider = str(provider or "")[:80]
    if not provider or not isinstance(state, dict):
        return {"success": False, "error": "provider and dict state required"}
    stamp = _hlc_now()
    try:
        with _FABRIC_LOCK:
            rec = _FABRIC_STATE.get(provider)
            if rec is None:
                if len(_FABRIC_STATE) >= _FABRIC_STATE_MAX:
                    oldest = min(_FABRIC_STATE.items(),
                                 key=lambda kv: _rec_stamp(kv[1], "updated_at"))
                    _FABRIC_STATE.pop(oldest[0], None)
                rec = {"provider": provider, "updated_at": _now_iso(),
                       "hlc": stamp, "state": {}, "field_stamps": {}}
                _FABRIC_STATE[provider] = rec
            fields = rec.setdefault("state", {})
            stamps = rec.setdefault("field_stamps", {})
            for k, v in dict(state).items():
                key = str(k)[:120]
                fields[key] = v
                stamps[key] = stamp
            if _stamp_newer(stamp, _rec_stamp(rec, "updated_at")):
                rec["hlc"] = stamp
                rec["updated_at"] = _now_iso()
        return {"success": True, "provider": provider,
                "keys": sorted(state.keys())[:12]}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:120]}


def get_fabric_state(provider: str) -> Optional[Dict[str, Any]]:
    """Flattened last-known state for `provider` (copy), or None if unseen.

    Deliberately does NOT call `_ensure_loaded()`: this is called from every
    fabric worm's ``__init__``, so an auto-load here would mean a disk read
    per construction and would let a stale on-disk snapshot shadow in-process
    state. Disk restore happens on the explicit startup path
    (``startup_warm.restore_spine_state``) which is the one place it belongs.
    """
    with _FABRIC_LOCK:
        rec = _FABRIC_STATE.get(str(provider))
        return dict(rec.get("state") or {}) if rec else None


def get_fabric_record(provider: str) -> Optional[Dict[str, Any]]:
    """Full record including per-field stamps (diagnostics / merge debugging)."""
    with _FABRIC_LOCK:
        rec = _FABRIC_STATE.get(str(provider))
        return dict(rec) if rec else None


def get_fabric_view() -> Dict[str, Any]:
    """Introspection: which fabric providers have persisted state."""
    with _FABRIC_LOCK:
        return {k: {"updated_at": v.get("updated_at", ""),
                    "keys": sorted((v.get("state") or {}).keys()),
                    "stamped_fields": len(v.get("field_stamps") or {})}
                for k, v in _FABRIC_STATE.items()}


def _merge_fabric(remote: Any) -> int:
    """Fold a remote fabric collection in, per FIELD, HLC-ordered.

    Two changes over the previous per-provider recency merge:

    * **Per field.** A peer publishing `_lease_env` no longer erases our
      `_genome_version`; both survive, keyed by their own stamps.
    * **HLC ordering.** "Newer" is decided by a hybrid logical clock rather
      than by comparing naive local-time strings, so a timezone offset or a
      skewed clock can no longer invert the winner (or delay it by hours).

    Returns the number of individual field writes applied.
    """
    merged = 0
    if not isinstance(remote, dict):
        return 0
    with _FABRIC_LOCK:
        for provider, rec in remote.items():
            if not isinstance(rec, dict):
                continue
            r_state = rec.get("state")
            if not isinstance(r_state, dict):
                continue
            name = str(provider)[:80]
            cur = _FABRIC_STATE.get(name)
            if cur is None:
                if len(_FABRIC_STATE) >= _FABRIC_STATE_MAX:
                    oldest = min(_FABRIC_STATE.items(),
                                 key=lambda kv: _rec_stamp(kv[1], "updated_at"))
                    _FABRIC_STATE.pop(oldest[0], None)
                cur = {"provider": name, "updated_at": "", "hlc": "",
                       "state": {}, "field_stamps": {}}
                _FABRIC_STATE[name] = cur
            fields = cur.setdefault("state", {})
            stamps = cur.setdefault("field_stamps", {})
            for attr, value in r_state.items():
                key = str(attr)[:120]
                r_ts = _fabric_field_stamp(rec, attr)
                l_ts = _fabric_field_stamp(cur, key)
                # Via `_stamp_newer`, not a raw `>`: this comparison used to
                # bypass the drift guard entirely, which is how a poisoned
                # year-2999 field stamp could still win a fabric merge after
                # the clock itself had learned to refuse it.
                if key not in fields or _stamp_newer(r_ts, l_ts):
                    fields[key] = value
                    if r_ts:
                        stamps[key] = r_ts
                    merged += 1
            r_top = _rec_stamp(rec, "updated_at")
            if _stamp_newer(r_top, _rec_stamp(cur, "updated_at")):
                cur["hlc"] = r_top
                cur["updated_at"] = str(rec.get("updated_at") or "")
            # Fold the peer's clock into ours so nothing we stamp after this
            # can be ordered before a value we just adopted (causality). Only
            # stamps we would actually trust are folded in: taking a raw `max`
            # here would pick a poisoned value over a valid one and drop the
            # valid observation entirely.
            candidates = [r_top] + [str(v) for v in (stamps.values()
                                                     if isinstance(stamps, dict) else [])]
            adoptable = [c for c in candidates if c and _stamp_adoptable(c)]
            _observe_stamp(max(adoptable) if adoptable else (r_top or ""))
    return merged


def _merge_quarantine(remote: Any) -> int:
    """Fold remote quarantine votes in, per (finding, env) recency wins."""
    merged = 0
    if not isinstance(remote, dict):
        return 0
    with _QUARANTINE_LOCK:
        for finding, box in remote.items():
            if not isinstance(box, dict):
                continue
            local = _QUARANTINE_VOTES.setdefault(str(finding)[:160], {})
            for env, rec in box.items():
                if not isinstance(rec, dict):
                    continue
                cur = local.get(str(env))
                if cur is None or _stamp_newer(_rec_stamp(rec, "at"),
                                               _rec_stamp(cur, "at")):
                    local[str(env)[:40]] = {"verdict": rec.get("verdict", "quarantine"),
                                           "at": rec.get("at", ""),
                                           "hlc": rec.get("hlc", "")}
                    merged += 1
            if len(_QUARANTINE_VOTES) > _QUARANTINE_FINDINGS_MAX:
                overflow = len(_QUARANTINE_VOTES) - _QUARANTINE_FINDINGS_MAX
                for k in list(_QUARANTINE_VOTES)[:overflow]:
                    _QUARANTINE_VOTES.pop(k, None)
    return merged


# ── PERSISTENCE (restart-safe, gossip-ready) ────────────────────────
_STATE_FILE = Path.home() / ".azazael" / "spine_state.json"

# Load-once guard: separate cron/script processes used to start empty and
# save() OVERWROTE each other's ledgers (found 2026-09-14: state file held
# 3 keys after 60+ samples fed across runs). First write in a process with
# empty memory now merges disk state instead of clobbering it.
_LOADED_ONCE = False
_LOAD_LOCK = threading.Lock()


def _merge_disk_state() -> None:
    """Fold the on-disk state file into memory (counters = MAX, missing adopted).

    Makes save-then-exit processes composable: N parallel hourly jobs each
    contribute their samples instead of clobbering each other. Never raises.
    """
    try:
        if not _STATE_FILE.exists():
            return
        payload = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return
    try:
        with _HOMEOSTAT_LOCK:
            for k, v in (payload.get("homeostat") or {}).items():
                if not isinstance(v, dict):
                    continue
                cur = _HOMEOSTAT.get(k)
                if cur is None:
                    _HOMEOSTAT[k] = v
                    continue
                for f in ("successes", "failures"):
                    try:
                        cur[f] = max(int(cur.get(f, 0)), int(v.get(f, 0)))
                    except (TypeError, ValueError):
                        pass
                if _stamp_newer(_rec_stamp(v, "last_at"),
                                _rec_stamp(cur, "last_at")):
                    for f in ("last_ms", "last_at", "last_error", "hist_ms",
                              "consec_fail", "hlc"):
                        if f in v:
                            cur[f] = v[f]
            for k, w in (payload.get("q_weights") or {}).items():
                if k not in _Q_WEIGHTS:
                    try:
                        _Q_WEIGHTS[k] = max(_Q_MIN, min(_Q_MAX, float(w)))
                    except (TypeError, ValueError):
                        pass
            for k, n in (payload.get("q_update_counts") or {}).items():
                try:
                    _Q_UPDATE_COUNTS[k] = max(_Q_UPDATE_COUNTS.get(k, 0), int(n))
                except (TypeError, ValueError):
                    pass
            for k, var in (payload.get("q_variance") or {}).items():
                try:
                    _Q_VARIANCE.setdefault(k, float(var))
                except (TypeError, ValueError):
                    pass
            for k, v in (payload.get("scars") or {}).items():
                if isinstance(v, dict):
                    _SCARS.setdefault(k, v)
        with _SPINE_LOCK:
            for k, v in (payload.get("spine_map") or {}).items():
                _SPINE_MAP.setdefault(k, v if isinstance(v, dict) else {})
        _merge_quarantine(payload.get("quarantine_votes"))
        _merge_fabric(payload.get("fabric_state"))
    except Exception:
        pass


def _ensure_loaded() -> None:
    global _LOADED_ONCE
    if _LOADED_ONCE:
        return
    with _LOAD_LOCK:
        if _LOADED_ONCE:
            return
        _LOADED_ONCE = True
        try:
            if not _HOMEOSTAT and not _Q_WEIGHTS and _STATE_FILE.exists():
                load_spine_state()
        except Exception:
            pass


def _now_iso() -> str:
    return datetime.now().isoformat()


# ── SPINE MAP API ────────────────────────────────────────────────────

def _ordering_stamp(info: Dict[str, Any]) -> str:
    """Pick the HLC sidecar for a new record.

    A caller that explicitly pinned `hlc` or `updated_at` in `info` is
    asserting when the content became true (tests, backfill, a record imported
    from a peer), and the ordering sidecar must AGREE with that pin —
    otherwise the pin is silently ignored and the merge orders by wall clock,
    which is the exact failure this sidecar exists to remove.
    """
    pinned = info.get("hlc") or info.get("updated_at")
    if pinned:
        try:
            from CORE.hlc import normalize_stamp
            return normalize_stamp(str(pinned))
        except Exception:  # pragma: no cover - defensive
            return str(pinned)
    return _hlc_now()


def record_spine_node(env: str, worm: str, info: Dict[str, Any]) -> None:
    """Record/refresh one spine node (env:worm). Thread-safe."""
    key = f"{env}:{worm}"
    # `updated_at` stays ISO for the many readers that parse it; `hlc` is the
    # sidecar that decides cross-env recency in merge_spine_gossip, so a
    # timezone offset or a skewed clock cannot invert the winner.
    info = dict(info or {})
    rec: Dict[str, Any] = {"env": env, "worm": worm, "updated_at": _now_iso()}
    rec.update(info)
    rec.setdefault("hlc", _ordering_stamp(info))
    with _SPINE_LOCK:
        if key not in _SPINE_MAP and len(_SPINE_MAP) >= _SPINE_MAP_MAX:
            # Evict oldest-updated node (simple bounded-growth policy)
            oldest = min(_SPINE_MAP.items(),
                         key=lambda kv: kv[1].get("updated_at", ""))
            del _SPINE_MAP[oldest[0]]
        _SPINE_MAP[key] = rec


def get_spine_map() -> Dict[str, Dict[str, Any]]:
    """Copy of the full spine map. Thread-safe."""
    with _SPINE_LOCK:
        return {k: dict(v) for k, v in _SPINE_MAP.items()}


def get_spine_summary() -> Dict[str, Any]:
    """Aggregate summary: node count, per-env counts, route edges."""
    with _SPINE_LOCK:
        envs: Dict[str, int] = {}
        routes = 0
        for rec in _SPINE_MAP.values():
            env_name = rec.get("env", "?")
            envs[env_name] = envs.get(env_name, 0) + 1
            routes += len(rec.get("routes", []) or [])
        return {
            "nodes": len(_SPINE_MAP),
            "envs": envs,
            "route_edges": routes,
            "events": len(_SPINE_EVENTS),
        }


def get_spine_events(since: Optional[str] = None) -> List[Dict[str, Any]]:
    """Spine events (most recent first, capped)."""
    with _SPINE_LOCK:
        events = list(_SPINE_EVENTS)
    events.reverse()
    if since:
        events = [e for e in events if e.get("at", "") >= since]
    return events


def record_spine_event(kind: str, detail: Dict[str, Any]) -> None:
    """Append a spine event (bounded). Thread-safe."""
    with _SPINE_LOCK:
        _SPINE_EVENTS.append({"kind": kind, "detail": detail, "at": _now_iso()})
        if len(_SPINE_EVENTS) > _SPINE_EVENTS_MAX:
            del _SPINE_EVENTS[:len(_SPINE_EVENTS) - _SPINE_EVENTS_MAX]


# ── HOMEOSTAT API ────────────────────────────────────────────────────

def record_outcome(nature: str, worm: str, success: bool,
                   duration_ms: float = 0.0,
                   error: Optional[str] = None,
                   reward: Optional[float] = None) -> None:
    """Record one worm execution outcome. Called from NatureCluster.execute().

    Thread-safe, never raises (feedback must not break execution).

    `reward` (optional) is the SIGNED reinforcement magnitude for the
    brainstem. When omitted the signal is the boolean sign (+1/-1) — the
    original behaviour. Callers that computed a real learning signal (a TD
    error, a shaped reward) pass it here so **magnitude survives the
    hand-off**: the ledger counters still key off `success` (a boolean is
    the right unit for fail-rate statistics), but the Q-table learns from
    the caller's magnitude instead of a sign bit.
    """
    _ensure_loaded()
    key = f"{nature}:{worm}"
    try:
        with _homeostat_stripe(key):
            rec = _HOMEOSTAT.setdefault(key, {
                "successes": 0, "failures": 0,
                "last_ms": 0.0, "last_at": "", "last_error": "",
                "hist_ms": [], "consec_fail": 0,
            })
            if success:
                rec["successes"] += 1
                rec["consec_fail"] = 0
            else:
                rec["failures"] += 1
                rec["consec_fail"] = rec.get("consec_fail", 0) + 1
                rec["last_error"] = (error or "")[:120]
            rec["last_ms"] = round(float(duration_ms), 2)
            rec["last_at"] = _now_iso()
            rec["hlc"] = _hlc_now()
            hist: List[float] = rec["hist_ms"]
            hist.append(round(float(duration_ms), 2))
            if len(hist) > _HIST_MAX:
                del hist[:len(hist) - _HIST_MAX]
            _append_outcome_event({
                "nature": nature, "worm": worm,
                "success": bool(success), "ms": rec["last_ms"],
                "at": rec["last_at"],
            })
            # Auto-reinforce the brainstem. Default signal is the boolean
            # sign (success ~ +1, failure ~ -1); callers that computed a real
            # reward (e.g. a TD error) supply a signed magnitude instead, so
            # the Q-table is not quantised to one bit.
            if reward is None:
                signal = 1.0 if success else -1.0
            else:
                try:
                    signal = max(_Q_MIN, min(_Q_MAX, float(reward)))
                except (TypeError, ValueError):
                    signal = 1.0 if success else -1.0
            rec["last_reward"] = round(signal, 4)
            # _reinforce_q takes that key's Q stripe itself (homeostat
            # stripe is held here, which is the canonical H→Q order).
            _reinforce_q(key, signal)
            # Capture everything the reflex needs so the reflex can run
            # OUTSIDE this stripe. F9: the reflex used to do a
            # `from CORE.worm_registry import WORM_REGISTRY` — an import and
            # a foreign subsystem's dict access — while holding the ledger
            # lock, serialising every other worm behind it.
            reflex_fired = rec["consec_fail"] == _REFLEX_FAIL_THRESHOLD
            consec_fail = rec["consec_fail"]
            last_at = rec["last_at"]

        # ── REFLEX ARC: instant autonomic response ──────────────────
        # Fires at the failure threshold with no scheduler, no worm and no
        # delay — but now *after* releasing the stripe, so the emergency
        # path cannot stall the ledger. Lock order here is POLICY/SPINE/
        # SCAR with no ledger stripe held, which removes the old
        # HOMEOSTAT→SPINE nesting entirely.
        if reflex_fired:
            try:
                from CORE.worm_registry import WORM_REGISTRY as _WR
                info = _WR.get(worm)
                if info is not None:
                    old_cd = float(info.get("cooldown_seconds", 30.0))
                    old_pr = int(info.get("priority", 5))
                    info["cooldown_seconds"] = round(
                        min(old_cd * _REFLEX_COOLDOWN_MULT,
                            _REFLEX_COOLDOWN_CAP), 2)
                    info["priority"] = max(1, old_pr - 1)
                    # Journalled so revert_policy() can undo emergency
                    # measures once the incident is understood.
                    journal_policy("reflex", "emergency_backoff", worm, {
                        "cooldown_seconds": {"from": old_cd,
                                             "to": info["cooldown_seconds"]},
                        "priority": {"from": old_pr,
                                     "to": info["priority"]},
                    })
            except Exception:
                pass
            with _SCAR_LOCK:
                _SCARS[key] = {"since": last_at,
                               "reason": (error or "unspecified")[:80]}
            try:
                record_spine_event("reflex_response", {
                    "key": key, "consec_fail": consec_fail,
                    "action": "cooldown+priority+scar",
                })
            except Exception:
                pass
        elif success:
            # G7: Graduated scar healing. Instead of instant full heal,
            # the scar fades over N consecutive successes. heal_count
            # tracks progress; full heal at HEAL_THRESHOLD successes.
            _HEAL_THRESHOLD = 3  # consecutive successes to fully heal
            with _SCAR_LOCK:
                if key in _SCARS:
                    scar = _SCARS.get(key, {})
                    scar["heal_count"] = scar.get("heal_count", 0) + 1
                    if scar["heal_count"] >= _HEAL_THRESHOLD:
                        _SCARS.pop(key, None)
                        healed = scar["heal_count"]
                    else:
                        _SCARS[key] = scar  # write back updated count
                        healed = None
                else:
                    healed = None
                    scar = {}
            if healed is not None:
                try:
                    record_spine_event("scar_healed", {"key": key,
                        "heal_count": healed})
                except Exception:
                    pass
            elif scar:
                try:
                    record_spine_event("scar_fading", {"key": key,
                        "heal_count": scar.get("heal_count"),
                        "threshold": _HEAL_THRESHOLD})
                except Exception:
                    pass
    except Exception:
        pass  # feedback is best-effort by design


def get_homeostat_view() -> Dict[str, Dict[str, Any]]:
    """Full homeostat ledger (copy). Thread-safe."""
    _ensure_loaded()
    with _HOMEOSTAT_LOCK:
        return {k: {kk: (list(vv) if isinstance(vv, list) else vv)
                    for kk, vv in v.items()}
                for k, v in _HOMEOSTAT.items()}


def get_outcome_events(since: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recent outcome events (most recent first)."""
    events = list(_merged_outcome_events())
    events.reverse()
    since = since or ""
    return [e for e in events if e.get("at", "") >= since]


# ── Q-WEIGHT API (brainstem) ───────────────────────────────────────

def _reinforce_q(key: str, reward: float) -> None:
    """EMA Q-update: q += alpha * (reward - q), clamped to [-1, 1].

    G2: Adaptive alpha. High-variance keys (volatile worms) get a higher
    alpha so they learn faster; low-variance keys (stable worms) get a
    lower alpha so they don't oscillate. Alpha is clamped to [0.05, 0.5].

    F9: takes ``_q_stripe(key)`` itself, so both call sites (the live hot
    path in ``record_outcome``, which already holds that key's homeostat
    stripe, and ``dream_reinforce``) are safe by construction and cannot
    address a key under the wrong lock. Homeostat→Q is the canonical order
    the lock invariant depends on.
    """
    with _q_stripe(key):
        _reinforce_q_unlocked(key, reward)


def _reinforce_q_unlocked(key: str, reward: float) -> None:
    """Body of ``_reinforce_q``. Caller must hold ``_q_stripe(key)``."""
    q = _Q_WEIGHTS.get(key, 0.0)
    n = _Q_UPDATE_COUNTS.get(key, 0)
    # Adaptive alpha: scale by sqrt of running variance
    var = _Q_VARIANCE.get(key, 0.25)  # default variance ~ moderate
    adaptive_alpha = _Q_ALPHA_BASE * (1.0 + min(2.0, (var ** 0.5) * 2.0))
    adaptive_alpha = max(0.05, min(0.5, adaptive_alpha))
    # Update running variance via Welford's online algorithm
    n += 1
    _Q_UPDATE_COUNTS[key] = n
    delta = reward - q
    old_var = _Q_VARIANCE.get(key, 0.0)
    _Q_VARIANCE[key] = old_var + (delta * delta - old_var) / n
    q = q + adaptive_alpha * (reward - q)
    _Q_WEIGHTS[key] = max(_Q_MIN, min(_Q_MAX, q))


def get_q_weights() -> Dict[str, float]:
    """Copy of the Q-weight table. Thread-safe."""
    _ensure_loaded()
    with _HOMEOSTAT_LOCK:
        return dict(_Q_WEIGHTS)


def dream_reinforce(nature: str, worm: str, reward: float) -> bool:
    _ensure_loaded()
    """Offline-learning channel: move Q without touching the live ledger.

    Used by ConsolidationWorm (sleep phase) to replay dream-derived
    policy suggestions into the Q-table. Deliberately does NOT count
    successes/failures — dreams are simulations, not executions — so
    homeostat fail-rate statistics stay grounded in reality while the
    routing substrate still benefits from offline experience.
    """
    try:
        key = f"{nature}:{worm}"
        with _q_stripe(key):
            _reinforce_q_unlocked(key, max(_Q_MIN, min(_Q_MAX, float(reward))))
        return True
    except Exception:
        return False


def is_idle(window_seconds: float = 300.0) -> bool:
    """True when no live outcome has been recorded recently.

    Gate for the sleep phase (ConsolidationWorm): dreaming on a busy
    system would both pollute Q with stale replay and compete for CPU.
    """
    try:
        cutoff = (datetime.now().timestamp() - window_seconds)
        # ISO timestamps compare lexicographically with isoformat strings
        from datetime import datetime as _dt
        since = _dt.fromtimestamp(cutoff).isoformat()
        with _HOMEOSTAT_LOCK:
            return not any(e.get("at", "") >= since for e in _merged_outcome_events())
    except Exception:
        return False


def get_q_weight(nature: str, worm: str) -> float:
    """Single Q-weight; 0.0 (neutral) if the worm has no history."""
    _ensure_loaded()
    with _HOMEOSTAT_LOCK:
        return _Q_WEIGHTS.get(f"{nature}:{worm}", 0.0)


def get_q_updates(nature: str, worm: str) -> int:
    """How many times this key has ever been reinforced. 0 if never.

    Added 2026-09-14 for elastic AOA arm selection. ``get_q_weight()``
    returns 0.0 for an unknown key and for a known key that has settled on
    a neutral 0.0 -- so a *proven neutral* arm is indistinguishable from a
    *never-tried* one by Q alone. Any selector that ranks on Q therefore
    starves untried arms permanently: they score 0, are never chosen, and
    so are never scored (the cold-start collapse four live inference
    providers independently flagged).

    The count already existed as ``_Q_UPDATE_COUNTS`` (used to drive the
    Welford variance in ``_reinforce_q_unlocked``); this exposes it
    read-only so a caller can distinguish "unknown" from "measured" and
    apply a minimum-pull quota before trusting Q.
    """
    _ensure_loaded()
    with _HOMEOSTAT_LOCK:
        return int(_Q_UPDATE_COUNTS.get(f"{nature}:{worm}", 0))


def get_q_update_counts() -> Dict[str, int]:
    """Copy of the WHOLE update-count table, keyed "nature:worm".

    Added 2026-09-15 for the RL monitor. ``get_q_updates()`` is per-key, so a
    caller that wants to render the entire Q-table had to either loop over
    every key (one lock acquisition each) or -- as the first cut of the RL
    monitor did -- call it with no arguments, raise ``TypeError``, and get
    swallowed by a defensive ``except``. That produced a card which silently
    reported "0 measured" for a populated brainstem while claiming the spine
    as its source, which is exactly the failure mode the monitor exists to
    prevent.

    Read-only copy, so a caller can pair it with ``get_q_weights()`` and tell
    a *proven neutral* key (weight 0.0, pulls > 0) from a *starved* one
    (weight 0.0, pulls == 0).
    """
    _ensure_loaded()
    with _HOMEOSTAT_LOCK:
        return dict(_Q_UPDATE_COUNTS)


def q_order(nature: str, worm_names: List[str]) -> List[str]:
    """Order worm names by descending Q-weight (healthy first).

    Scarred worms are demoted below every healthy peer regardless of
    their Q-weight (reflex arc consequence), then healed worms return
    to normal ordering. Unknown worms keep relative input order among
    themselves (stable sort on a 0.0 default).
    """
    # G18: `worm_names.index(n)` inside the comprehension made this O(n^2)
    # (a linear scan per element) on a path that runs once per nature per
    # cycle. Precomputing first-seen positions keeps the exact tie-break
    # semantics — equal (scar, q) pairs still fall back to input order —
    # in O(n log n) total.
    positions: Dict[str, int] = {}
    for i, n in enumerate(worm_names):
        positions.setdefault(n, i)
    with _HOMEOSTAT_LOCK:
        with _SCAR_LOCK:  # reflex writes scars outside the ledger barrier
            ranked = [(positions[n],
                       0 if f"{nature}:{n}" in _SCARS else 1,  # scar demotion band
                       _Q_WEIGHTS.get(f"{nature}:{n}", 0.0), n)
                      for n in worm_names]
    ranked.sort(key=lambda t: (-t[1], -t[2], t[0]))
    return [n for _, _, _, n in ranked]


def get_route_usage() -> Dict[str, Dict[str, Any]]:
    """Per-route learned state, keyed by "src>dst".

    Audit section 7 (2026-09-14): the mapper published *nature* edges only,
    so which route actually fired — and whether it worked — was unfilled
    telemetry. `record_route_result()` writes `route:<src>><dst>` keys into
    the homeostat ledger (auto-reinforced by the brainstem), so this reads
    that ledger back as route telemetry rather than inventing a new store.

    Returns {route: {successes, failures, total, q, last_at, last_ms,
    effective_weight}}. Empty when no route has ever been observed.
    """
    _ensure_loaded()
    with _HOMEOSTAT_LOCK:
        homeo = {k: dict(v) for k, v in _HOMEOSTAT.items()
                 if str(k).startswith("route:")}
        q_weights = dict(_Q_WEIGHTS)
    out: Dict[str, Dict[str, Any]] = {}
    for key, rec in homeo.items():
        route = str(key)[len("route:"):]
        s = int(rec.get("successes") or 0)
        f = int(rec.get("failures") or 0)
        q = float(q_weights.get(key, 0.0))
        out[route] = {
            "successes": s, "failures": f, "total": s + f,
            "q": round(q, 4),
            "last_at": rec.get("last_at", ""),
            "last_ms": rec.get("last_ms", 0.0),
            # Same formula MeshRouterWorm.route() applies, so the telemetry
            # reports the weight routing would actually use.
            "effective_weight": round(max(0.1, min(5.0, 1.0 * (1.0 + q))), 4),
        }
    return out


def _scars_snapshot() -> Dict[str, Dict[str, Any]]:
    """Copy of the scar table. Caller may hold (or not hold) the ledger
    barrier; the scar lock is taken here because reflex writes now land
    outside that barrier."""
    with _SCAR_LOCK:
        return {k: dict(v) for k, v in _SCARS.items()}


def get_scars() -> Dict[str, Dict[str, Any]]:
    """Copy of the reflex-arc scar table. Thread-safe."""
    return _scars_snapshot()


# ── PERSISTENCE (restart-safe, gossip-ready) ───────────────────────

def save_spine_state() -> Dict[str, Any]:
    """Persist spine + homeostat + Q-weights to ~/.azazael/spine_state.json.

    Written atomically (tmp + os.replace) so concurrent readers never see
    a torn file. Returns a summary; never raises (persistence is
    best-effort — a read-only home dir must not break the mesh).
    """
    summary: Dict[str, Any] = {"saved": False}
    try:
        # Merge-on-save (2026-09-14): hourly jobs + manual runs interleave as
        # separate processes; last-writer-wins was silently dropping samples
        # (ledger swung 257 -> 18 between hours). Fold disk state in first:
        # counters take MAX (monotonic), missing keys are adopted.
        _merge_disk_state()
        with _SPINE_LOCK:
            spine_map = {k: dict(v) for k, v in _SPINE_MAP.items()}
            spine_events = list(_SPINE_EVENTS)
        with _HOMEOSTAT_LOCK:
            homeostat = {k: {kk: (list(vv) if isinstance(vv, list) else vv)
                             for kk, vv in v.items()}
                         for k, v in _HOMEOSTAT.items()}
            q_weights = dict(_Q_WEIGHTS)
            # The pull-count and the Welford variance are as much a part of the
            # learned brainstem as the weights are. Persisting the weights
            # alone (pre-2026-09-15) reset adaptive alpha to its default and
            # made every key look never-pulled on each restart -- which defeats
            # get_q_updates(), whose entire purpose is telling a proven-neutral
            # key (weight 0.0, pulls > 0) from a starved one (both 0).
            q_update_counts = {k: int(v) for k, v in _Q_UPDATE_COUNTS.items()}
            q_variance = {k: float(v) for k, v in _Q_VARIANCE.items()}
        with _POLICY_LOCK:
            policy_journal = [dict(e) for e in _POLICY_JOURNAL]
            policy_latest = {k: dict(v) for k, v in _POLICY_LATEST.items()}
        with _GOSSIP_TRUST_LOCK:
            gossip = {"seq": _GOSSIP_SEQ_LOCAL,
                      "seq_seen": dict(_GOSSIP_SEQ_SEEN),
                      "keys": dict(_GOSSIP_KEYS)}
        quarantine_votes = get_quarantine_votes()
        with _FABRIC_LOCK:
            fabric_state = {k: dict(v) for k, v in _FABRIC_STATE.items()}
        payload = {
            "version": __version__,
            "saved_at": _now_iso(),
            "spine_map": spine_map,
            "spine_events": spine_events,
            "homeostat": homeostat,
            "q_weights": q_weights,
            "q_update_counts": q_update_counts,
            "q_variance": q_variance,
            "scars": _scars_snapshot(),
            "policy_journal": policy_journal,
            "policy_latest": policy_latest,
            "gossip": gossip,
            "quarantine_votes": quarantine_votes,
            "fabric_state": fabric_state,
        }
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = _STATE_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(str(tmp), str(_STATE_FILE))
        summary = {"saved": True, "path": str(_STATE_FILE),
                   "spine_nodes": len(spine_map),
                   "homeostat_worms": len(homeostat),
                   "q_weights": len(q_weights),
                   "q_update_counts": len(q_update_counts),
                   "quarantine_findings": len(quarantine_votes),
                   "fabric_providers": len(fabric_state)}
    except Exception as exc:
        summary = {"saved": False, "error": str(exc)[:120]}
    return summary


def load_spine_state() -> Dict[str, Any]:
    """Restore spine state saved by save_spine_state(). Merges into memory.

    Safe against missing/corrupt files (returns counts restored, never
    raises). Called at session start so learned Q-weights and the last
    known topology survive restarts — the mesh remembers itself.
    """
    restored: Dict[str, Any] = {"restored": False}
    try:
        if not _STATE_FILE.exists():
            return {"restored": False, "reason": "no_state_file"}
        payload = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        spine_map = payload.get("spine_map") or {}
        spine_events = payload.get("spine_events") or []
        homeostat = payload.get("homeostat") or {}
        q_weights = payload.get("q_weights") or {}
        if not isinstance(spine_map, dict):
            spine_map = {}
        if not isinstance(homeostat, dict):
            homeostat = {}
        if not isinstance(q_weights, dict):
            q_weights = {}
        with _SPINE_LOCK:
            for k, v in spine_map.items():
                _SPINE_MAP.setdefault(k, v if isinstance(v, dict) else {})
            _SPINE_EVENTS.extend(e for e in spine_events if isinstance(e, dict))
            if len(_SPINE_EVENTS) > _SPINE_EVENTS_MAX:
                del _SPINE_EVENTS[:len(_SPINE_EVENTS) - _SPINE_EVENTS_MAX]
        with _HOMEOSTAT_LOCK:
            for k, v in homeostat.items():
                if isinstance(v, dict):
                    _HOMEOSTAT.setdefault(k, v)
            for k, w in q_weights.items():
                try:
                    _Q_WEIGHTS[k] = max(_Q_MIN, min(_Q_MAX, float(w)))
                except (TypeError, ValueError):
                    pass
            # Counts are monotone observations: take MAX so N parallel
            # save-then-exit processes compose instead of overwriting (same
            # rule as successes/failures in _merge_disk_state).
            for k, n in (payload.get("q_update_counts") or {}).items():
                try:
                    _Q_UPDATE_COUNTS[k] = max(_Q_UPDATE_COUNTS.get(k, 0), int(n))
                except (TypeError, ValueError):
                    pass
            # Variance: adopt only when we have none; a restored value must not
            # overwrite variance this process has already measured.
            for k, var in (payload.get("q_variance") or {}).items():
                try:
                    _Q_VARIANCE.setdefault(k, float(var))
                except (TypeError, ValueError):
                    pass
            for k, v in (payload.get("scars") or {}).items():
                if isinstance(v, dict):
                    with _SCAR_LOCK:
                        _SCARS.setdefault(k, v)
        with _POLICY_LOCK:
            for e in payload.get("policy_journal") or []:
                if isinstance(e, dict) and e.get("worm"):
                    _POLICY_JOURNAL.append(e)
            if len(_POLICY_JOURNAL) > _POLICY_JOURNAL_MAX:
                del _POLICY_JOURNAL[:len(_POLICY_JOURNAL) - _POLICY_JOURNAL_MAX]
            # G10: rebuild the compacting map from whatever the payload has.
            # Newer payloads carry it explicitly; older ones only have the
            # (possibly wrapped) ring, so fold that too — best effort, and
            # never both overwriting a newer explicit entry.
            # setdefault, not assignment: `load_spine_state()` is callable
            # mid-process (via _ensure_loaded / _replay_policy_journal), and an
            # in-memory adaptation is always newer than the disk one. Blind
            # assignment would roll a live adaptation back to the last saved
            # value — the same class of silent reversion G10 is about.
            for name, e in (payload.get("policy_latest") or {}).items():
                if isinstance(e, dict) and e.get("worm"):
                    _POLICY_LATEST.setdefault(str(name), dict(e))
            for e in _POLICY_JOURNAL:
                worm = e.get("worm")
                if worm and str(worm) not in _POLICY_LATEST:
                    _POLICY_LATEST[str(worm)] = dict(e)
        # Anti-replay state must survive restarts, or a saved old payload
        # could be replayed against a freshly-started process.
        global _GOSSIP_SEQ_LOCAL
        gossip = payload.get("gossip") or {}
        if isinstance(gossip, dict):
            with _GOSSIP_TRUST_LOCK:
                try:
                    _GOSSIP_SEQ_LOCAL = max(_GOSSIP_SEQ_LOCAL,
                                            int(gossip.get("seq") or 0))
                except (TypeError, ValueError):
                    pass
                for env, seq in (gossip.get("seq_seen") or {}).items():
                    try:
                        _GOSSIP_SEQ_SEEN[str(env)] = max(
                            int(_GOSSIP_SEQ_SEEN.get(str(env), -1)), int(seq))
                    except (TypeError, ValueError):
                        continue
                for env, key in (gossip.get("keys") or {}).items():
                    if isinstance(key, str) and key:
                        _GOSSIP_KEYS.setdefault(str(env), key)
        # Fabric operational state + quarantine votes: the mesh's memory of
        # *what it knew*, not just how it felt (audit 2026-09-15, finding #7).
        _merge_quarantine(payload.get("quarantine_votes"))
        _merge_fabric(payload.get("fabric_state"))
        restored = {"restored": True,
                    "spine_nodes": len(spine_map),
                    "homeostat_worms": len(homeostat),
                    "q_weights": len(q_weights),
                    "quarantine_findings": len(payload.get("quarantine_votes") or {}),
                    "fabric_providers": len(payload.get("fabric_state") or {})}
    except Exception as exc:
        restored = {"restored": False, "error": str(exc)[:120]}
    return restored


def homeostat_reset() -> None:
    """Clear feedback ledger (for tests / explicit operator action)."""
    with _HOMEOSTAT_LOCK:
        _HOMEOSTAT.clear()
        _clear_outcome_events()


# ── POLICY JOURNAL API (endocrine memory) ─────────────────────────

def journal_policy(actor: str, action: str, worm: str,
                   changes: Dict[str, Any]) -> None:
    """Append one programmatic policy change to the journal (bounded)."""
    entry = {
        "actor": actor, "action": action, "worm": worm,
        "changes": dict(changes), "at": _now_iso(),
    }
    with _POLICY_LOCK:
        _POLICY_JOURNAL.append(entry)
        if len(_POLICY_JOURNAL) > _POLICY_JOURNAL_MAX:
            del _POLICY_JOURNAL[:len(_POLICY_JOURNAL) - _POLICY_JOURNAL_MAX]
    # G10: the compacting map is the state; the ring is the audit log.
    _remember_policy(entry)


def get_policy_journal(limit: int = 50) -> List[Dict[str, Any]]:
    """Most recent policy changes first (copy, bounded by `limit`)."""
    with _POLICY_LOCK:
        entries = [dict(e) for e in _POLICY_JOURNAL[-limit:]]
    entries.reverse()
    return entries


def revert_policy(actor: str = "operator", count: int = 1) -> List[Dict[str, Any]]:
    """Undo the last `count` journalled cooldown/priority changes.

    Scans the journal newest-first, applies each entry's inverse to the
    registry, and stops after `count` reverted ENTRIES (journal entries
    whose worms are no longer registered are skipped, still counted).
    Returns the reverted entries for audit. Never raises.
    """
    reverted: List[Dict[str, Any]] = []
    try:
        from CORE.worm_registry import WORM_REGISTRY as _WR
    except ImportError:
        return reverted
    with _POLICY_LOCK:
        for entry in reversed(_POLICY_JOURNAL):
            if len(reverted) >= count:
                break
            changes = entry.get("changes") or {}
            info = _WR.get(entry.get("worm", ""))
            if info is None:
                continue
            inv: Dict[str, Any] = {}
            if "cooldown_seconds" in changes:
                inv["cooldown_seconds"] = changes["cooldown_seconds"]["from"]
            if "priority" in changes:
                inv["priority"] = changes["priority"]["from"]
            if not inv:
                continue
            info.update(inv)
            reverted.append({"at": entry.get("at"), "worm": entry.get("worm"),
                             "actor": entry.get("actor"), "undone": inv})
            _POLICY_JOURNAL.remove(entry)
    if reverted:
        try:
            record_spine_event("policy_reverted", {"by": actor,
                                                   "entries": len(reverted)})
        except Exception:
            pass
    return reverted


def spine_reset() -> None:
    """Clear spine state (for tests / explicit operator action)."""
    with _SPINE_LOCK:
        _SPINE_MAP.clear()
        _SPINE_EVENTS.clear()
    with _HOMEOSTAT_LOCK:
        _HOMEOSTAT.clear()
        _clear_outcome_events()
        _Q_WEIGHTS.clear()
        # The brainstem is three tables, not one. Clearing only the weights
        # left the pull-count and the Welford variance behind, so a "reset"
        # produced a Q-table that was empty of values but full of evidence:
        # every arm immediately read as proven, and the variance kept driving
        # adaptive alpha from data the weights no longer had (2026-09-15).
        _Q_UPDATE_COUNTS.clear()
        _Q_VARIANCE.clear()
    with _SCAR_LOCK:
        _SCARS.clear()
    with _POLICY_LOCK:
        _POLICY_JOURNAL.clear()
        _POLICY_LATEST.clear()
    with _GOSSIP_TRUST_LOCK:
        _GOSSIP_SEQ_SEEN.clear()
        _GOSSIP_KEYS.clear()
    with _ANOMALY_MODEL_LOCK:
        _ANOMALY_MODEL.clear()
        global _ANOMALY_MODEL_SOURCE
        _ANOMALY_MODEL_SOURCE = "local"
    with _QUARANTINE_LOCK:
        _QUARANTINE_VOTES.clear()
    with _FABRIC_LOCK:
        _FABRIC_STATE.clear()


def purge_implausible_stamps(dry_run: bool = True) -> Dict[str, Any]:
    """Repair ordering stamps that sit beyond the clock's drift window.

    Opt-in, never automatic. Refusal (see `_stamp_adoptable`) makes a poisoned
    stamp harmless — it cannot win a merge and cannot propagate — but it stays
    in the store, and therefore in every gossip payload, forever. A real store
    was found carrying 98 year-2999 stamps
    (``032472162000000-04631-windows``) written before the drift bound existed.

    Each implausible ``hlc`` sidecar is REPLACED with a stamp derived from the
    record's own human-readable ISO field, not deleted: deleting it would make
    the record look older than every real write and lose its next merge, which
    is a different bug from the one being fixed. ``field_stamps`` on fabric
    records are repaired the same way.

    ``dry_run=True`` (the default) reports what would change and touches
    nothing. Returns per-area counts plus `repaired` / `scanned`. Never raises.

    Operator usage:
        python -c "from CORE import spine_registry as s; print(s.purge_implausible_stamps(False))"
    """
    report: Dict[str, Any] = {"dry_run": bool(dry_run), "repaired": 0,
                              "scanned": 0, "areas": {}, "examples": []}

    def _fix(rec: Any, iso_field: str, area: str) -> None:
        if not isinstance(rec, dict):
            return
        report["scanned"] += 1
        stamp = rec.get("hlc")
        if not stamp or _stamp_adoptable(str(stamp)):
            return
        report["repaired"] += 1
        report["areas"][area] = report["areas"].get(area, 0) + 1
        if len(report["examples"]) < 5:
            report["examples"].append({"area": area, "stamp": str(stamp)[:40],
                                      "from": str(rec.get(iso_field) or "")[:32]})
        if dry_run:
            return
        try:
            from CORE.hlc import normalize_stamp
            rec["hlc"] = normalize_stamp(str(rec.get(iso_field) or ""))
        except Exception:  # pragma: no cover - defensive
            rec.pop("hlc", None)

    try:
        with _HOMEOSTAT_LOCK:
            for rec in _HOMEOSTAT.values():
                _fix(rec, "last_at", "homeostat")
        with _SPINE_LOCK:
            for rec in _SPINE_MAP.values():
                _fix(rec, "last_at", "spine_map")
        with _QUARANTINE_LOCK:
            for box in _QUARANTINE_VOTES.values():
                for rec in (box or {}).values():
                    _fix(rec, "at", "quarantine_votes")
        with _FABRIC_LOCK:
            for rec in _FABRIC_STATE.values():
                _fix(rec, "updated_at", "fabric_state")
                stamps = rec.get("field_stamps") if isinstance(rec, dict) else None
                if not isinstance(stamps, dict):
                    continue
                for key, stamp in list(stamps.items()):
                    if stamp and not _stamp_adoptable(str(stamp)):
                        report["repaired"] += 1
                        report["areas"]["fabric_field_stamps"] = \
                            report["areas"].get("fabric_field_stamps", 0) + 1
                        if not dry_run:
                            try:
                                from CORE.hlc import normalize_stamp
                                stamps[key] = normalize_stamp(
                                    str(rec.get("updated_at") or ""))
                            except Exception:  # pragma: no cover - defensive
                                stamps.pop(key, None)
    except Exception as exc:  # pragma: no cover - defensive
        report["error"] = str(exc)[:160]
    return report


def get_module_health() -> Dict[str, Any]:
    """Introspection endpoint for doctor/health tooling."""
    with _SPINE_LOCK:
        spine_nodes = len(_SPINE_MAP)
        spine_events = len(_SPINE_EVENTS)
    with _HOMEOSTAT_LOCK:
        homeostat_worms = len(_HOMEOSTAT)
        outcome_events = _outcome_event_count()
    with _QUARANTINE_LOCK:
        quarantine_findings = len(_QUARANTINE_VOTES)
    with _FABRIC_LOCK:
        fabric_providers = len(_FABRIC_STATE)
    return {
        "version": __version__,
        "spine_nodes": spine_nodes,
        "spine_events": spine_events,
        "homeostat_worms": homeostat_worms,
        "outcome_events": outcome_events,
        "quarantine_findings": quarantine_findings,
        "fabric_providers": fabric_providers,
    }


# ── GOSSIP TRUST (signature + monotonic sequence + key pinning) ──────
# Audit G9 (2026-09-14): merge_spine_gossip() used to adopt a peer record on
# timestamp comparison ALONE, so anything able to write a file into the
# gossip drop dir could inject Q-weights and thereby re-order worm execution
# across an environment. Payloads now carry a monotonic per-env `seq` and,
# when cryptography is importable, an Ed25519 signature over the canonical
# payload plus the signer's public key.
#
# Policy (env AZAZAEL_GOSSIP_POLICY):
#   strict (default) — signature required; unsigned peers refused
#   warn             — verify when present, admit unsigned (legacy peers)
#   off              — no signature checks (seq rollback checks always apply)
#
# When cryptography is unavailable or broken, `strict` degrades to
# seq-only enforcement and the merge result says so explicitly
# ("signature": "unavailable") instead of implying the payload was
# authenticated. Degradation is recorded as a spine event.
_GOSSIP_POLICY_ENV = "AZAZAEL_GOSSIP_POLICY"
_GOSSIP_POLICY_DEFAULT = "strict"
_GOSSIP_SEQ_LOCAL = 0                 # our own outgoing counter
_GOSSIP_SEQ_SEEN: Dict[str, int] = {}  # env -> highest seq accepted
_GOSSIP_KEYS: Dict[str, str] = {}      # env -> pinned base64 public key (TOFU)
_GOSSIP_TRUST_LOCK = threading.RLock()


def _gossip_policy() -> str:
    """Effective signature policy for this process (strict | warn | off)."""
    raw = (os.environ.get(_GOSSIP_POLICY_ENV) or _GOSSIP_POLICY_DEFAULT)
    pol = raw.strip().lower()
    return pol if pol in ("strict", "warn", "off") else _GOSSIP_POLICY_DEFAULT


def _gossip_crypto():
    """Lazy Ed25519 accessor: (sign_fn, verify_fn, local_pub_b64) or None.

    `sign_fn(canonical) -> signature_b64`; the local public key is returned
    separately so the caller can place it in the payload BEFORE signing — the
    signature covers the key, so signing first and attaching the key after
    silently invalidates every payload (caught by the stubbed-crypto test).

    Imported lazily because spine_registry is documented stdlib-only at
    module level (no heavy imports, no PAM/MemoryBus cycles). audit_trail
    degrades gracefully when its crypto backend is missing or broken, so
    this must too — a broken signing backend must never break execution.
    """
    try:
        import base64 as _b64
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from CORE.audit_trail import PUBLIC_KEY_PATH, _get_signing_key
    except Exception:
        return None
    try:
        key = _get_signing_key()
        local_pub = _b64.b64encode(PUBLIC_KEY_PATH.read_bytes()).decode("ascii")
    except Exception:
        return None
    if not key or not local_pub:
        return None

    def _sign(canonical: str) -> str:
        try:
            priv = ed25519.Ed25519PrivateKey.from_private_bytes(key)
            return _b64.b64encode(
                priv.sign(canonical.encode("utf-8"))).decode("ascii")
        except Exception:
            return ""

    def _verify(canonical: str, sig_b64: str, pub_b64: str) -> bool:
        try:
            pub = ed25519.Ed25519PublicKey.from_public_bytes(_b64.b64decode(pub_b64))
            pub.verify(_b64.b64decode(sig_b64), canonical.encode("utf-8"))
            return True
        except Exception:
            # Retry against the local public key: same-machine envs sharing
            # a home dir sign with one key, so a peer's declared key may be
            # absent from an older payload while ours still verifies it.
            try:
                pub = ed25519.Ed25519PublicKey.from_public_bytes(
                    PUBLIC_KEY_PATH.read_bytes())
                pub.verify(_b64.b64decode(sig_b64), canonical.encode("utf-8"))
                return True
            except Exception:
                return False

    return _sign, _verify, local_pub


def _gossip_canonical(payload: Dict[str, Any]) -> str:
    """Deterministic JSON of the payload minus the signature field itself.

    Every other envelope field (seq, signer_pub, gossip_from, exported_at)
    IS covered by the signature, so a tampered sequence number or a swapped
    public key invalidates it.
    """
    body = {k: v for k, v in payload.items() if k != "signature"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, default=str)


def _peer_env(payload: Dict[str, Any]) -> str:
    """Env id claimed by a peer payload (bounded, sanitised for keying)."""
    env = payload.get("gossip_from") or "peer"
    env = str(env).strip()[:40]
    return env or "peer"


def check_gossip_trust(payload: Any,
                       policy: Optional[str] = None) -> Dict[str, Any]:
    """Validate a peer payload's provenance before it may be merged.

    Enforces, in order:
      1. **Monotonic seq per env.** A payload whose seq is strictly below the
         highest seq already accepted from that env is a replay and is
         refused. Equal seq is admitted, because merge is idempotent by
         contract and an identical replay changes nothing (that property is
         covered by the existing idempotency tests).
      2. **Ed25519 signature** over the canonical payload, verified against
         the env's TOFU-pinned public key. First key seen for an env wins;
         a later payload from the same env presenting a different key is
         refused as impersonation.

    Returns {ok, reason, env, seq, signature, policy, key_pinned}.
    Never raises — a malformed payload is simply untrusted.
    """
    pol = policy or _gossip_policy()
    res: Dict[str, Any] = {
        "ok": False, "reason": "", "env": "peer", "seq": 0,
        "signature": "skipped", "policy": pol, "key_pinned": False,
    }
    try:
        if not isinstance(payload, dict):
            res["reason"] = "not_a_payload"
            return res
        env = _peer_env(payload)
        res["env"] = env
        try:
            seq = int(payload.get("seq") or 0)
        except (TypeError, ValueError):
            seq = 0
        res["seq"] = seq

        # 1. replay / rollback guard (crypto-independent)
        with _GOSSIP_TRUST_LOCK:
            seen = int(_GOSSIP_SEQ_SEEN.get(env, -1))
            pinned = _GOSSIP_KEYS.get(env, "")
        if seq < seen:
            res["reason"] = "replayed_seq"
            return res

        sig = str(payload.get("signature") or "")
        pub = str(payload.get("signer_pub") or "")
        res["signer_pub"] = pub

        # 2. key pinning: an env may not change its identity key
        if pub and pinned and pub != pinned:
            res["reason"] = "key_changed"
            res["signature"] = "invalid"
            return res
        res["key_pinned"] = bool(pinned)

        crypto = _gossip_crypto()
        if pol == "off":
            res["signature"] = "skipped"
            res["ok"] = True
            return res

        if crypto is None:
            # Degraded: cannot authenticate. Under strict we still enforce the
            # sequence guard but must NOT claim authentication happened.
            res["signature"] = "unavailable"
            res["ok"] = True
            res["reason"] = "crypto_unavailable_seq_only"
            return res

        _sign, _verify, _local_pub = crypto
        if not sig:
            if pol == "strict":
                res["reason"] = "unsigned_payload"
                res["signature"] = "missing"
                return res
            res["signature"] = "missing"
            res["ok"] = True
            return res

        if not pub:
            res["reason"] = "missing_signer_key"
            res["signature"] = "missing"
            return res

        if _verify(_gossip_canonical(payload), sig, pub):
            res["signature"] = "verified"
            res["ok"] = True
            return res

        res["reason"] = "bad_signature"
        res["signature"] = "invalid"
        return res
    except Exception as exc:  # never raise out of a trust check
        res["reason"] = f"trust_error:{str(exc)[:60]}"
        return res


def _remember_gossip(trust: Dict[str, Any]) -> None:
    """Commit an accepted payload's env/seq/key to the anti-replay state."""
    try:
        env = trust.get("env") or "peer"
        seq = int(trust.get("seq") or 0)
        pub = str(trust.get("signer_pub") or "")
        with _GOSSIP_TRUST_LOCK:
            if seq > int(_GOSSIP_SEQ_SEEN.get(env, -1)):
                _GOSSIP_SEQ_SEEN[env] = seq
            # First key seen for an env is pinned (trust-on-first-use); later
            # payloads from that env must present the same key.
            if pub and not _GOSSIP_KEYS.get(env):
                _GOSSIP_KEYS[env] = pub
    except Exception:
        pass


def get_gossip_trust_state() -> Dict[str, Any]:
    """Introspection: local sequence, per-env high-water marks, pinned keys."""
    with _GOSSIP_TRUST_LOCK:
        return {
            "policy": _gossip_policy(),
            "local_seq": _GOSSIP_SEQ_LOCAL,
            "seq_seen": dict(_GOSSIP_SEQ_SEEN),
            "pinned_keys": {k: v[:16] + "..." for k, v in _GOSSIP_KEYS.items()},
            "crypto_available": _gossip_crypto() is not None,
        }


# ── SHARED ANOMALY MODEL (G13/G5 over the gossip transport) ──────────
# The fitted autoencoder is the mesh's only trained neural network. It fits
# per-process, so without transport every env relearns from zero and the mesh
# never accumulates a single detector — the exact "per-instance, not persisted,
# not shared" defect G13 named.
#
# The transport deliberately reuses the signed gossip envelope: the model is
# simply another field in the payload, so it is covered by the Ed25519
# signature and by the replay/key-pinning gate with **no separate trust
# path**. It can never travel unsigned, and a tampered model is a
# `bad_signature` rejection like any other edited field.
#
# `_ANOMALY_MODEL` is a *transport snapshot*, not the live detector. The
# authority for a running process is the worm instance (which persists to
# ~/.azazael/anomaly_model.json); this copy exists so a trained detector can be
# handed to a peer that has seen fewer observations.
_ANOMALY_MODEL: Dict[str, Any] = {}
_ANOMALY_MODEL_SOURCE = "local"
_ANOMALY_MODEL_LOCK = threading.RLock()
_ANOMALY_MAX_DIM = 512
_ANOMALY_MAX_OBSERVATIONS = 10_000_000


def _valid_anomaly_model(model: Any) -> bool:
    """Structural validation for a model arriving from disk or a peer.

    Shape-checks both weight matrices and bounds every number, so a malformed
    or hostile payload cannot cause a large allocation, load a NaN weight, or
    reach a peer's net at all.
    """
    if not isinstance(model, dict):
        return False
    try:
        n = int(model.get("input_dim"))
        h = int(model.get("hidden_dim"))
    except (TypeError, ValueError):
        return False
    if not (1 <= n <= _ANOMALY_MAX_DIM and 1 <= h <= _ANOMALY_MAX_DIM):
        return False
    w_enc = model.get("W_enc")
    w_dec = model.get("W_dec")
    if not isinstance(w_enc, list) or not isinstance(w_dec, list):
        return False
    if len(w_enc) != h or len(w_dec) != n:
        return False
    try:
        for row in w_enc:
            if not isinstance(row, list) or len(row) != n:
                return False
            for v in row:
                f = float(v)
                if f != f or abs(f) > 1e6:
                    return False
        for row in w_dec:
            if not isinstance(row, list) or len(row) != h:
                return False
            for v in row:
                f = float(v)
                if f != f or abs(f) > 1e6:
                    return False
        obs = int(model.get("observations") or 0)
    except (TypeError, ValueError):
        return False
    return 0 <= obs <= _ANOMALY_MAX_OBSERVATIONS


def publish_anomaly_model(model: Any) -> Dict[str, Any]:
    """Offer a fitted model for transport. Monotone: strictly-better-trained only.

    The single rule (more observations wins) prevents the ping-pong where two
    envs holding snapshots overwrite each other forever, and it keeps the best
    detector regardless of which environment produced it.
    """
    if not _valid_anomaly_model(model):
        return {"published": False, "reason": "invalid_model"}
    obs = int(model.get("observations") or 0)
    with _ANOMALY_MODEL_LOCK:
        current = int((_ANOMALY_MODEL or {}).get("observations") or 0)
        if _ANOMALY_MODEL and obs <= current:
            return {"published": False, "reason": "not_better_trained",
                    "observations": obs, "current": current}
        _ANOMALY_MODEL.clear()
        _ANOMALY_MODEL.update(dict(model))
        global _ANOMALY_MODEL_SOURCE
        _ANOMALY_MODEL_SOURCE = "local"
    return {"published": True, "observations": obs, "current": current}


def get_anomaly_model() -> Optional[Dict[str, Any]]:
    """Transport snapshot of the shared model (deep copy), or None if unset."""
    with _ANOMALY_MODEL_LOCK:
        if not _ANOMALY_MODEL:
            return None
        return {k: ([list(r) for r in v] if isinstance(v, list) else v)
                for k, v in _ANOMALY_MODEL.items()}


def get_anomaly_model_meta() -> Dict[str, Any]:
    """Provenance of the snapshot: who fitted it and how well trained it is."""
    with _ANOMALY_MODEL_LOCK:
        return {"present": bool(_ANOMALY_MODEL),
                "source": _ANOMALY_MODEL_SOURCE,
                "observations": int((_ANOMALY_MODEL or {}).get("observations") or 0)}


# ── GOSSIP (cross-env merge) ────────────────────────────────────────
# The spine_state.json payload (see save_spine_state) is the gossip unit.
# export_spine_gossip() produces it; merge_spine_gossip() absorbs a peer's
# payload with a recency-wins conflict policy. Keyed by "env:worm", so
# same-named worms in different envs never collide, and merging is
# commutative/idempotent for identical payloads.

def _iso_or(ts: Any) -> str:
    """Best-effort ISO timestamp extraction from a record ("" if absent)."""
    if isinstance(ts, dict):
        ts = ts.get("updated_at") or ts.get("last_at") or ""
    return ts if isinstance(ts, str) else ""


def export_spine_gossip() -> Dict[str, Any]:
    """Export the gossip payload to send to peer environments.

    Reuses the persistence payload (same shape save_spine_state writes)
    but does NOT touch the filesystem. Envelope fields ("gossip_from",
    "exported_at") let the receiver trace provenance.

    Every payload carries a strictly increasing `seq` for anti-replay, and
    is Ed25519-signed over its canonical form when cryptography is
    available (`signature` + `signer_pub`). The signature covers seq, the
    public key and every state collection, so none of them can be edited in
    transit. When crypto is unavailable the payload is exported unsigned and
    receivers handle the degradation explicitly.
    """
    global _GOSSIP_SEQ_LOCAL
    with _SPINE_LOCK:
        spine_map = {k: dict(v) for k, v in _SPINE_MAP.items()}
        spine_events = list(_SPINE_EVENTS)
    with _HOMEOSTAT_LOCK:
        homeostat = {k: {kk: (list(vv) if isinstance(vv, list) else vv)
                         for kk, vv in v.items()}
                     for k, v in _HOMEOSTAT.items()}
        q_weights = dict(_Q_WEIGHTS)
        # Travel with the weights so a peer adopting a Q value does not read as
        # a starved key on the receiving monitor (the counts are the evidence
        # behind the weight).
        q_update_counts = dict(_Q_UPDATE_COUNTS)
    with _GOSSIP_TRUST_LOCK:
        _GOSSIP_SEQ_LOCAL += 1
        seq = _GOSSIP_SEQ_LOCAL
    quarantine_votes = get_quarantine_votes()
    with _FABRIC_LOCK:
        fabric_state = {k: dict(v) for k, v in _FABRIC_STATE.items()}
    payload: Dict[str, Any] = {
        "version": __version__,
        "exported_at": _now_iso(),
        "gossip_from": os.environ.get("AZAZAEL_ENV", "local"),
        "seq": seq,
        "signer_pub": "",
        "signature": "",   # filled below when crypto is available
        "spine_map": spine_map,
        "spine_events": spine_events,
        "homeostat": homeostat,
        "q_weights": q_weights,
        "q_update_counts": q_update_counts,
        # Inside the signed envelope: `_gossip_canonical` covers every field
        # except the signature itself, so the model needs no extra trust
        # machinery and cannot be edited in transit.
        "anomaly_model": get_anomaly_model(),
        # Cross-env quorum votes and fabric operational state travel with the
        # same signed payload: a peer's quarantine vote is what lets the
        # quorum gate on THIS host actually reach `decided`, and fabric state
        # is what stops the mesh forgetting its routing/consensus on restart.
        "quarantine_votes": quarantine_votes,
        "fabric_state": fabric_state,
    }
    crypto = _gossip_crypto()
    if crypto is not None:
        try:
            sign, _verify, local_pub = crypto
            # The key must be IN the payload before signing — it is covered
            # by the signature (see _gossip_crypto's contract).
            payload["signer_pub"] = local_pub
            payload["signature"] = sign(_gossip_canonical(payload))
        except Exception:
            pass  # unsigned export; receiver reports the degradation
    return payload


def merge_spine_gossip(payload: Any) -> Dict[str, Any]:
    """Merge a peer's gossip payload into local state (recency wins).

    Conflict policy per collection:
    - spine_map / homeostat: per-key, the record with the newer
      timestamp (updated_at / last_at) replaces the older one; missing
      timestamps never overwrite existing records.
    - q_weights: the value whose homeostat record is newer wins; with
      no ledger evidence, local value is kept (conservative).
    - spine_events: unioned, re-sorted by timestamp, re-capped.

    Defensive by contract: wrong types, missing keys, and malformed
    records are skipped, never raised. Returns a merge summary.
    Idempotent: re-merging the same payload changes nothing.
    """
    stats: Dict[str, Any] = {"merged": False, "spine_nodes": 0, "homeostat_worms": 0,
                             "q_weights": 0, "events": 0}
    try:
        if not isinstance(payload, dict):
            return stats
        # Provenance gate: replay + signature + key pinning (audit G9).
        trust = check_gossip_trust(payload)
        stats.update({"env": trust.get("env", ""), "seq": trust.get("seq", 0),
                      "signature": trust.get("signature", "?"),
                      "policy": trust.get("policy", "?")})
        if not trust.get("ok"):
            stats["rejected"] = trust.get("reason", "untrusted")
            try:
                record_spine_event("gossip_rejected", {
                    "env": trust.get("env", "?"),
                    "reason": stats["rejected"],
                    "seq": trust.get("seq", 0),
                    "signature": trust.get("signature", "?"),
                })
            except Exception:
                pass
            return stats
        remote_map = payload.get("spine_map")
        remote_home = payload.get("homeostat")
        remote_q = payload.get("q_weights")
        remote_counts = payload.get("q_update_counts")
        remote_events = payload.get("spine_events")
        if not all(isinstance(x, dict) for x in
                   (remote_map or {}, remote_home or {}, remote_q or {})):
            # tolerate None collections; a non-dict one is ignored
            if remote_map is not None and not isinstance(remote_map, dict):
                remote_map = {}
            if remote_home is not None and not isinstance(remote_home, dict):
                remote_home = {}
            if remote_q is not None and not isinstance(remote_q, dict):
                remote_q = {}
        remote_map = remote_map or {}
        remote_home = remote_home or {}
        remote_q = remote_q or {}

        with _SPINE_LOCK:
            for k, v in (remote_map or {}).items():
                if not isinstance(v, dict):
                    continue
                cur = _SPINE_MAP.get(k)
                if cur is None:
                    _SPINE_MAP[k] = v
                    stats["spine_nodes"] += 1
                    continue
                # recency wins; strictly-newer only so re-merging the
                # same payload is a true no-op (idempotency contract).
                if _stamp_newer(_rec_stamp(v, "updated_at"),
                                _rec_stamp(cur, "updated_at")):
                    _SPINE_MAP[k] = v
                    stats["spine_nodes"] += 1
            if isinstance(remote_events, list):
                known = {json.dumps(e, sort_keys=True) for e in _SPINE_EVENTS}
                for e in remote_events:
                    if isinstance(e, dict):
                        sig = json.dumps(e, sort_keys=True)
                        if sig not in known:
                            _SPINE_EVENTS.append(e)
                            known.add(sig)
                            stats["events"] += 1
                _SPINE_EVENTS.sort(key=lambda e: e.get("at", ""))
                if len(_SPINE_EVENTS) > _SPINE_EVENTS_MAX:
                    del _SPINE_EVENTS[:len(_SPINE_EVENTS) - _SPINE_EVENTS_MAX]

        with _HOMEOSTAT_LOCK:
            for k, v in (remote_home or {}).items():
                if not isinstance(v, dict):
                    continue
                cur = _HOMEOSTAT.get(k)
                if cur is None:
                    _HOMEOSTAT[k] = v
                    stats["homeostat_worms"] += 1
                    continue
                if _stamp_newer(_rec_stamp(v, "last_at"),
                                _rec_stamp(cur, "last_at")):
                    _HOMEOSTAT[k] = v
                    stats["homeostat_worms"] += 1
            for k, w in (remote_q or {}).items():
                try:
                    wv = max(_Q_MIN, min(_Q_MAX, float(w)))
                except (TypeError, ValueError):
                    continue
                # conservative: adopt remote Q only when our ledger has no
                # newer evidence; if the key is unknown locally, adopt it.
                if k not in _Q_WEIGHTS:
                    _Q_WEIGHTS[k] = wv
                    stats["q_weights"] += 1
            # Counts are evidence, not a value: take the MAX so a key adopted
            # from a peer still shows why it is trusted rather than reading as
            # never-pulled. Never lowers a local count.
            if isinstance(remote_counts, dict):
                for k, n in remote_counts.items():
                    try:
                        _Q_UPDATE_COUNTS[k] = max(_Q_UPDATE_COUNTS.get(k, 0), int(n))
                    except (TypeError, ValueError):
                        continue

        # Shared anomaly model. Only reached after the trust gate, so this is
        # an authenticated, non-replayed, key-pinned model — and it is
        # explicitly NOT adopted when this env already has a better-trained
        # one (that is what stops two envs overwriting each other forever).
        remote_model = payload.get("anomaly_model")
        if remote_model is not None:
            if not _valid_anomaly_model(remote_model):
                stats["anomaly_model"] = "rejected"
            else:
                remote_obs = int(remote_model.get("observations") or 0)
                with _ANOMALY_MODEL_LOCK:
                    local_obs = int((_ANOMALY_MODEL or {}).get("observations") or 0)
                    if remote_obs > local_obs:
                        _ANOMALY_MODEL.clear()
                        _ANOMALY_MODEL.update(dict(remote_model))
                        global _ANOMALY_MODEL_SOURCE
                        _ANOMALY_MODEL_SOURCE = f"peer:{stats.get('env') or 'peer'}"
                        stats["anomaly_model"] = "adopted"
                    else:
                        stats["anomaly_model"] = "kept_local"
        # Cross-env quorum votes + fabric operational state (authenticated: we
        # are past the trust gate). Both merge per-key with recency wins, so
        # re-merging the same payload stays a no-op.
        q_merged = _merge_quarantine(payload.get("quarantine_votes"))
        f_merged = _merge_fabric(payload.get("fabric_state"))
        if q_merged:
            stats["quarantine_votes"] = q_merged
        if f_merged:
            stats["fabric_state"] = f_merged
        # Acceptance commits the seq high-water mark and pins the env's key.
        _remember_gossip(trust)
        stats["merged"] = True
        record_spine_event("gossip_merged", {
            "from": payload.get("gossip_from", "peer"),
            **stats,
        })
        return stats
    except Exception as exc:
        return {"merged": False, "error": str(exc)[:120]}


# ── GOSSIP TRANSPORT (shared-filesystem drop) ───────────────────────
# Each env writes its payload to ~/.azazael/gossip/<env>.json and merges
# every other env's file it finds. Works across windows/wsl2/bare envs
# sharing a home volume; absence of peers is a clean no-op. Atomic writes
# only; readers tolerate missing/corrupt files.

_GOSSIP_DIR = Path.home() / ".azazael" / "gossip"
_GOSSIP_MAX_AGE_S = 24 * 3600.0  # ignore peer files older than 24h


def _local_env_name() -> str:
    """Local env id for gossip file naming — canonical (CORE.env_id).

    Audit 2026-09-15 (finding #4): this was a third stale 3-way copy whose
    docstring claimed it matched spine.py's _local_env(). Both returned
    "wsl2" while envmesh had split the bucket in two, so the gossip file this
    host wrote could never be matched by a peer's Kademlia lookup, which
    keyed on the 5-way id. Delegation, not a copy — and CORE.env_id is
    stdlib-only, so it stays safe for this module's "no heavy imports" rule.
    AZAZAEL_ENV still wins (that is the supported way to run two logical envs
    on one machine for gossip testing).
    """
    try:
        from CORE.env_id import env_id
        return env_id()[:40]
    except Exception:  # pragma: no cover - defensive
        env = os.environ.get("AZAZAEL_ENV")
        if env:
            return env[:40]
        return "windows" if os.name == "nt" else "bare"


def gossip_exchange(publish: bool = True) -> Dict[str, Any]:
    """Publish local spine state and merge peers' state from the drop dir.

    1. Export payload (export_spine_gossip).
    2. Write ~/.azazael/gossip/<env>.json (atomic tmp+replace).
    3. Merge every other env's fresh-enough file via merge_spine_gossip.

    `publish=False` skips only the write (used by the cycle's quota gate):
    peers are still merged, because throttling our own visibility must not
    blind us to theirs. The summary always states which happened via
    `published` / `publish_skipped`, so a suppressed publish is observable
    rather than silent.

    Never raises; returns a summary {exchanged, env, peers, merges}.
    """
    summary: Dict[str, Any] = {"exchanged": False, "env": _local_env_name(),
                               "peers": [], "merges": {}}
    try:
        payload = export_spine_gossip()
        mine = _GOSSIP_DIR / f"{summary['env']}.json"
        if not publish:
            summary["published"] = False
            summary["publish_skipped"] = "quota"
        else:
            _GOSSIP_DIR.mkdir(parents=True, exist_ok=True)
            tmp = mine.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            os.replace(str(tmp), str(mine))
            summary["published"] = True

        now = datetime.now().timestamp()
        for f in sorted(_GOSSIP_DIR.glob("*.json")):
            if f.name == mine.name:
                continue
            env_name = f.stem
            try:
                if now - f.stat().st_mtime > _GOSSIP_MAX_AGE_S:
                    continue  # stale peer drop
                peer_payload = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue  # corrupt/in-flight file — skip, never raise
            summary["merges"][env_name] = merge_spine_gossip(peer_payload)
            summary["peers"].append(env_name)
        summary["exchanged"] = True
        return summary
    except Exception as exc:
        summary["error"] = str(exc)[:120]
        return summary
