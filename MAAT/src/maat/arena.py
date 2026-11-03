"""Q3 lane — the game-tree arena: content candidates evaluated under rules.

ARENA STATE FORMAT `Q3A1` (a versioned JSON-able dict):
    {
      "arena_format": "Q3A1",
      "version": "YYYY-MM-DD",
      "seed_sha256": <64 hex>,       # provenance of this arena's origin
      "branches": [
        {
          "id": "b1",
          "parent": None | "b1",     # None for roots, else the branch id
          "alive": true,
          "forbidden": false,        # a forbidden branch can never score
          "depth": 0,
          "score": 0.0,
          "tokens": ["mirror", ...], # kernel-declared facts this branch holds
        } ...
      ],
    }

Scheduling is the Q3 kernel contract, mirroring the Q2 consumer:
  - only rules with `then.kernel == "arena"` drive the tree; `mesh` and
    `render` rules are logged deferred (their turn was the Q2 lane and the
    render snapshot, not the arena);
  - per frame, the scheduled fact decides which rules fire; effect
    semantics (all deterministic, all decided by the ruleset + seed):
      spawn    — a forbidden-free live branch grows a child (parent=id,
                 depth+1, inherits facts+[the fired fact])
      retire   — the lowest-scoring live branch leaves the tree
      promote  — every live branch matching a `when` fact gains `weight`
      forbid   — a branch holding the fired fact loses its right to score
  - after `frames`, the tree is READ OFF: alive, un-forbidden branches
    ranked by score (then depth, then id) — the ranking IS the evaluation;
  - same seed + ruleset -> same tree, same ranking, same log, always.
"""
from __future__ import annotations

import copy
import datetime
import hashlib

from .rules import FACTS, validate as validate_rules

ARENA_FORMAT = "Q3A1"
FRAMES = 4
ROOTS = 2


def new_arena(seed_text: str, *, version: str | None = None) -> dict:
    sha = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    branches = [{
        "id": f"b{i + 1}", "parent": None, "alive": True, "forbidden": False,
        "depth": 0, "score": 0.0, "tokens": [],
    } for i in range(ROOTS)]
    return {
        "arena_format": ARENA_FORMAT,
        "version": version or datetime.date.today().isoformat(),
        "seed_sha256": sha,
        "branches": branches,
    }


def validate_arena(state: dict) -> list[str]:
    errs: list[str] = []
    if state.get("arena_format") != ARENA_FORMAT:
        errs.append(f"arena_format must be {ARENA_FORMAT!r}, got {state.get('arena_format')!r}")
    if not re_hex64(state.get("seed_sha256")):
        errs.append("seed_sha256 must be 64 lowercase hex chars")
    branches = state.get("branches")
    if not isinstance(branches, list) or not branches:
        errs.append("branches must be a non-empty list")
        return errs
    ids = [str(b.get("id")) for b in branches]
    for i, b in enumerate(branches):
        for k in ("id", "parent", "alive", "forbidden", "depth", "score", "tokens"):
            if k not in b:
                errs.append(f"branches[{i}] is missing {k!r}")
        if b.get("parent") is not None and str(b["parent"]) not in ids:
            errs.append(f"branches[{i}].parent names no branch in this tree")
        if "tokens" in b and any(t not in FACTS for t in b["tokens"]):
            errs.append(f"branches[{i}].tokens holds a fact outside the kernel vocabulary")
    return errs


def re_hex64(v) -> bool:
    import re

    return bool(re.fullmatch(r"[0-9a-f]{64}", str(v or "")))


def _live(branches: list[dict]) -> list[dict]:
    return [b for b in branches if b["alive"] and not b["forbidden"]]


def apply(rs: dict, arena: dict, frames: int = FRAMES) -> dict:
    """Run candidate branches through the Q1R1 ruleset's arena rules."""
    errs = validate_arena(arena)
    if errs:
        raise ValueError(f"not a conformant {ARENA_FORMAT} state: " + "; ".join(errs[:3]))
    rerrs = validate_rules(rs)
    if rerrs:
        raise ValueError("not a conformant Q1R1 ruleset: " + "; ".join(rerrs[:3]))

    state = copy.deepcopy(arena)
    log: list[dict] = []
    by_fact: dict[str, list[dict]] = {}
    for r in rs["rules"]:
        for fact in r["when"]:
            by_fact.setdefault(fact, []).append(r)

    next_id = len(state["branches"])
    for frame in range(frames):
        fact = FACTS[frame % len(FACTS)]
        for r in by_fact.get(fact, []):
            effect, weight = r["then"]["effect"], float(r.get("weight", 0.5))
            branches = state["branches"]
            if effect == "promote":
                for b in _live(branches):
                    if fact in b["tokens"] or not b["tokens"]:
                        b["score"] = round(b["score"] + weight, 4)
                log.append(_entry(frame, r["id"], fact, effect,
                                  ["score" for _ in _live(branches)]))
            elif effect == "forbid":
                changed = []
                for b in branches:
                    if b["alive"] and fact in b["tokens"]:
                        b["forbidden"] = True
                        changed.append(b["id"])
                log.append(_entry(frame, r["id"], fact, effect,
                                  changed or ["no branch held the fact"]))
            elif effect == "retire":
                pool = _live(branches)
                if pool:
                    dead = sorted(pool, key=lambda b: (b["score"], b["depth"], b["id"]))[0]
                    dead["alive"] = False
                    changed = [dead["id"]]
                else:
                    changed = ["no live branch to retire"]
                log.append(_entry(frame, r["id"], fact, effect, changed))
            elif effect == "spawn":
                pool = _live(branches)
                host = pool[0] if pool else None
                if host is None:
                    changed = ["no live branch to grow"]
                else:
                    next_id += 1
                    child = {
                        "id": f"b{next_id}", "parent": host["id"], "alive": True,
                        "forbidden": False, "depth": host["depth"] + 1,
                        "score": round(weight * 0.5, 4), "tokens": [fact],
                    }
                    branches.append(child)
                    changed = [f"{child['id']} (of {host['id']}, depth {child['depth']})"]
                log.append(_entry(frame, r["id"], fact, effect, changed))
            else:
                # effect name, not kernel, so the log reads like applied entries;
                # the deferred delta carries which kernel owns it
                log.append(_entry(frame, r["id"], fact, r["then"]["effect"],
                                  [f"deferred: {r['then']['kernel']}/{r['then']['effect']} "
                                   f"belongs to another kernel"]))

    ranking = sorted(_live(state["branches"]),
                     key=lambda b: (-b["score"], b["depth"], b["id"]))
    return {"arena": state,
            "ranking": [{"id": b["id"], "score": b["score"], "depth": b["depth"]}
                        for b in ranking],
            "log": log}


def _entry(frame: int, rule_id: str, fact: str, effect: str, changed: list[str]) -> dict:
    return {"frame": frame, "rule_id": rule_id, "fact": fact,
            "effect": effect, "deltas": changed}
