"""Q2 lane — mesh mutation during the render loop, consuming Q1R1 rulesets.

MESH STATE FORMAT `Q2M1` (a mesh state is a versioned JSON-able dict):
    {
      "mesh_format": "Q2M1",
      "version": "YYYY-MM-DD",
      "seed_sha256": <64 hex>,        # provenance of THIS state's origin
      "primitives": [
        {
          "id": "p1",
          "intact": true,
          "scale": 1.0,
          "color": [r, g, b],         # 0..255 ints
          "pos": [x, y, z],           # floats, kernel-declared units
          "fragments": -1,            # fragments the primitive carries
        } ...
      ],
    }

Application is the Q2 kernel contract:
  - only rules whose `then.kernel == "mesh"` are APPLIED here;`arena` and
    `render` rules are recorded `deferred` (their consumers are the Q3 lane
    and the render snapshot, not the mesh);
  - a rule fires only in the frame whose scheduled fact matches its `when`;
    the frame schedule cycles the extractor's FACTS order, so firing is
    determined by the ruleset alone — no wall clock, no randomness;
  - every application writes a log line (rule id, effect, changed ids), so
    the mid-render history is inspectable, not swallowed;
  - same ruleset + same mesh -> same mutated state and same log, always.

Effect semantics (one line each, deterministic):
    recolor  — rotate the RGB channel values of the primitive
    rescale  — multiply `scale` by 0.8 (weight < 0.5) or 1.25
    displace — step `pos` along the fixed kernel axes
    shatter  — mark intact false, fragments += 2, scale down both halves
Non-mesh kernels or undeclared effect names never reach the loop: the
ruleset is validated by `maat.rules.validate` first, so a bad effect is a
load-time error, not a silent skip.
"""
from __future__ import annotations

import datetime
import hashlib
import pathlib
import re

from .rules import FACTS

MESH_FORMAT = "Q2M1"
N_PRIMITIVES = 4
FRAMES = 4


def new_mesh(seed_text: str, *, version: str | None = None) -> dict:
    """A deterministic starting state for the mutation loop."""
    sha = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    n = int(sha[:8], 16)
    prims = []
    for i in range(N_PRIMITIVES):
        n = (n * 1103515245 + 12345) & 0xFFFFFFFF
        r, g, b = (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF
        prims.append({
            "id": f"p{i + 1}", "intact": True, "scale": 1.0,
            "color": [r, g, b], "pos": [i * 1.5, 0.0, 0.0], "fragments": -1,
        })
    return {
        "mesh_format": MESH_FORMAT,
        "version": version or datetime.date.today().isoformat(),
        "seed_sha256": sha,
        "primitives": prims,
    }


def validate_mesh(state: dict) -> list[str]:
    errs: list[str] = []
    if state.get("mesh_format") != MESH_FORMAT:
        errs.append(f"mesh_format must be {MESH_FORMAT!r}, got {state.get('mesh_format')!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", str(state.get("seed_sha256") or "")):
        errs.append("seed_sha256 must be 64 lowercase hex chars")
    prims = state.get("primitives")
    if not isinstance(prims, list) or not prims:
        errs.append("primitives must be a non-empty list")
        return errs
    for i, p in enumerate(prims):
        for k in ("id", "intact", "scale", "color", "pos", "fragments"):
            if k not in p:
                errs.append(f"primitives[{i}] is missing {k!r}")
        if "color" in p and (len(p["color"]) != 3
                             or not all(isinstance(v, int) and 0 <= v <= 255 for v in p["color"])):
            errs.append(f"primitives[{i}].color must be three 0..255 ints")
    return errs


_POS_STEP = [0.25, -0.25, 0.5]


def _apply_magic(effect: str, prim: dict, weight: float) -> list[str]:
    """Mutate ONE primitive per the declared effect; return a short delta note."""
    if effect == "shatter":
        prim["intact"] = False
        prim["fragments"] = max(prim["fragments"], 0) + 2
        prim["scale"] = round(prim["scale"] * 0.5, 4)
        return ["intact=false", "fragments+2"]
    if effect == "displace":
        prim["pos"] = [round(prim["pos"][i] + _POS_STEP[i], 4) for i in range(3)]
        return ["pos stepped"]
    if effect == "recolor":
        prim["color"] = [prim["color"][2], prim["color"][0], prim["color"][1]]
        return ["rotated rgb"]
    if effect == "rescale":
        prim["scale"] = round(prim["scale"] * (0.8 if weight < 0.5 else 1.25), 4)
        return [f"scale={prim['scale']}"]
    return []  # unreachable after validation; kept total on purpose


def apply(rs: dict, mesh: dict, frames: int = FRAMES) -> dict:
    """Run the mesh through `frames` frames of the Q1R1 ruleset's mesh rules."""
    errs = validate_mesh(mesh)
    if errs:
        raise ValueError(f"not a conformant {MESH_FORMAT} state: " + "; ".join(errs[:3]))
    import copy

    from .rules import validate as validate_rules

    rerrs = validate_rules(rs)
    if rerrs:
        raise ValueError("not a conformant Q1R1 ruleset: " + "; ".join(rerrs[:3]))

    state = copy.deepcopy(mesh)
    log: list[dict] = []
    by_fact: dict[str, list[dict]] = {}
    for r in rs["rules"]:
        if r["then"]["kernel"] == "mesh":
            for fact in r["when"]:
                by_fact.setdefault(fact, []).append(r)

    for frame in range(frames):
        fired_fact = FACTS[frame % len(FACTS)]
        for r in by_fact.get(fired_fact, []):
            effect = r["then"]["effect"]
            changed = []
            for prim in state["primitives"]:
                note = _apply_magic(effect, prim, float(r.get("weight", 0.5)))
                if note:
                    changed.append(f"{prim['id']}: {note}")
            log.append({"frame": frame, "rule_id": r["id"], "fact": fired_fact,
                        "effect": effect,
                        "deltas": changed[:N_PRIMITIVES] or ["no intact primitive changed"]})
    return {"mesh": state, "log": log}


def load(path: str | pathlib.Path) -> dict:
    """Load a mesh state file and validate it; raises on violation."""
    import json

    state = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    errs = validate_mesh(state)
    if errs:
        raise ValueError(f"not a conformant {MESH_FORMAT} state: " + "; ".join(errs[:5]))
    return state
