#!/usr/bin/env python3
# coding: utf-8
"""Map the wire-or-cut backlog onto the natures' own data contracts.

The problem this solves
-----------------------
The census says which functions no production code names. It does not say what
to DO about each one, and guessing is how you get callers that nothing reads --
decoration, not integration. The mesh already answers the question, though:
`NATURE_DEFINITIONS` declares, per nature, what it EMITS, what it REQUIRES and
which natures it FEEDS INTO. That is a data-contract graph, written by the
project, so a consumer for a capability can be derived instead of invented:

    wire X into Y  <=>  Y's nature DECLARES it requires what X's nature emits

Two dispositions follow, and they are different jobs:

* **wire_at_site** -- the class is reachable in production AND production code
  references it, so a real call site exists. A bounded, local change.
  (`SplitBrainResolverWorm.report_fork` was one of these; `resolve()` read a box
  that the only writer, `report_fork()`, never filled, so the stage reported
  `no_forks` forever.)
* **integrate_via_stage** -- the class is NOT reachable, so the class itself must
  first be driven by a stage of one of the natures it feeds into. Adding a caller
  to a method on a class nobody instantiates changes nothing observable.

Outputs (all under the repo root):
    NEURAL_MESH_INTEGRATION_MAP.json     machine-readable plan, per finding
    NEURAL_MESH_INTEROP.mmd              Mermaid: nature -> class -> capability
    logs/capability_wiring_dataset.jsonl one row per finding, for training

A test reference is NOT a production consumer: `src/tests/` and `test_*.py` are
excluded, which is the rule PF16 itself had to be taught.
"""
from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src"
CENSUS = REPO / "NEURAL_MESH_WIRE_OR_CUT.json"
MAP_OUT = REPO / "NEURAL_MESH_INTEGRATION_MAP.json"
MMD_OUT = REPO / "NEURAL_MESH_INTEROP.mmd"
JSONL_OUT = REPO / "logs" / "capability_wiring_dataset.jsonl"


def production_uses() -> dict:
    """name -> [(file, line)] for NAME/ATTRIBUTE uses outside tests and shims.

    `__init__.py` is excluded because a re-export is not a consumer -- counting
    it made every worm look wired and left the colour queens with nothing to
    evaluate, which is inert rather than correct.
    """
    uses: dict = defaultdict(list)
    for path in SRC.rglob("*.py"):
        if "__pycache__" in path.parts or path.name == "__init__.py":
            continue
        if "tests" in path.parts or path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        rel = str(path.relative_to(REPO))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                uses[node.id].append((rel, node.lineno))
            elif isinstance(node, ast.Attribute):
                uses[node.attr].append((rel, node.lineno))
    return uses


def registry_natures() -> dict:
    """class name -> {nature, module, registered} from the REAL registry."""
    out: dict = {}
    try:
        from CORE.worm_registry import WORM_REGISTRY, discover_worms
        if len(WORM_REGISTRY) < 20:
            discover_worms()
        for name, info in WORM_REGISTRY.items():
            cls = (info or {}).get("class")
            if cls is None:
                continue
            out[getattr(cls, "__name__", str(name))] = {
                "registered": True,
                "worm": name,
                "nature": str((info or {}).get("category") or ""),
                "module": str(getattr(cls, "__module__", "") or ""),
            }
    except Exception as exc:  # pragma: no cover - registry optional
        print("registry unavailable: %r" % (exc,), file=sys.stderr)
    return out


def nature_defs() -> dict:
    """NATURE_DEFINITIONS, tolerating an import failure."""
    try:
        from CORE.WORMS.NATURE_CLUSTERS import NATURE_DEFINITIONS
        return dict(NATURE_DEFINITIONS)
    except Exception as exc:  # pragma: no cover
        print("NATURE_DEFINITIONS unavailable: %r" % (exc,), file=sys.stderr)
        return {}


def _posix(path) -> str:
    """Normalise a path for comparison across Windows and POSIX separators."""
    return str(path).replace("\\", "/")


def classify(finding: dict, natures: dict, defs: dict, uses: dict) -> dict:
    """Disposition for one census row, with the evidence that decided it."""
    qual = str(finding.get("qualname") or finding.get("key") or "")
    module = str(finding.get("module") or "")
    owner, _, method = qual.rpartition(".")
    if not owner:
        return {"owner": "", "method": qual, "kind": "module_level",
                "disposition": "module_level",
                "reason": "no class in the qualname; a module-level function needs "
                          "a caller decided per function, not per class"}

    reg = natures.get(owner, {})
    nature = reg.get("nature") or ""
    contract = defs.get(nature) or {}
    consumer_natures = list(contract.get("feeds_into") or [])
    emits = (contract.get("data_contracts") or {}).get("emits") or {}
    requires = (contract.get("data_contracts") or {}).get("requires") or {}

    # The class's OWN module is not a consumer of itself. Normalise to POSIX
    # before comparing: the first version compared "CORE/NeuralPipeline.py"
    # against a Windows "src\\CORE\\NeuralPipeline.py", never matched, and so
    # counted the class's own definition site as a production referrer --
    # inflating the wireable set with findings that have no caller anywhere.
    # Found by checking one: `replay_failed` appears only at its own `def`.
    own_rel = module.replace(".", "/") + ".py"
    refs = [(f, ln) for f, ln in uses.get(owner, [])
            if not _posix(f).endswith(own_rel)]
    reachable = bool(refs)

    if not reg and not reachable:
        return {"owner": owner, "method": method, "nature": nature,
                "kind": "class_unregistered", "consumer_natures": [],
                "disposition": "unresolved",
                "reason": "class is not in the registry and nothing references it",
                "emits": {}, "requires": {}, "refs": []}

    if reachable:
        return {"owner": owner, "method": method, "nature": nature,
                "kind": "reachable_class", "consumer_natures": consumer_natures,
                "disposition": "wire_at_site",
                "reason": "class is referenced in production at %s:%s, so a real "
                          "call site exists" % refs[0],
                "emits": emits, "requires": requires, "refs": refs[:5]}

    stage = consumer_natures[0] if consumer_natures else ""
    return {"owner": owner, "method": method, "nature": nature,
            "kind": "orphan_class", "consumer_natures": consumer_natures,
            "disposition": "integrate_via_stage",
            "reason": ("class has no production referrer; %s declares it feeds "
                       "into %s, so the %s stage must drive it"
                       % (nature or "nature unknown",
                          ", ".join(consumer_natures) or "(nothing)",
                          stage or "consumer")),
            "emits": emits, "requires": requires, "refs": []}


def main() -> int:
    sys.path.insert(0, str(SRC))
    if not CENSUS.exists():
        print("census missing: %s (run tools/mesh_function_preflight.py)" % CENSUS,
              file=sys.stderr)
        return 2
    declared = json.loads(CENSUS.read_text(encoding="utf-8")).get("declared") or {}
    pending = {k: v for k, v in declared.items()
               if (v or {}).get("status") == "pending"}

    natures = registry_natures()
    defs = nature_defs()
    uses = production_uses()
    print("pending findings : %d" % len(pending))
    print("registry classes : %d" % len(natures))
    print("natures declared : %d" % len(defs))

    plan = {}
    for key, rec in pending.items():
        row = dict(rec or {})
        row["key"] = key
        item = classify(row, natures, defs, uses)
        # Normalise ONCE at the boundary instead of trusting every branch to
        # return the same shape: the module_level early-return omitted
        # `consumer_natures`, which is a KeyError three functions later, long
        # after the thing that was actually wrong.
        for field, default in (("nature", ""), ("kind", "unknown"),
                               ("consumer_natures", []), ("emits", {}),
                               ("requires", {}), ("refs", []),
                               ("owner", ""), ("method", "")):
            item.setdefault(field, default)
        plan[key] = item

    buckets: dict = defaultdict(list)
    for key, item in plan.items():
        buckets[item["disposition"]].append(key)
    print("\ndispositions:")
    for name in sorted(buckets):
        print("  %-22s %4d" % (name, len(buckets[name])))

    # Who would consume each orphan, and how many orphans each stage would own.
    by_stage: dict = defaultdict(list)
    for key, item in plan.items():
        if item["disposition"] == "integrate_via_stage" and item["consumer_natures"]:
            by_stage[item["consumer_natures"][0]].append("%s.%s"
                                                         % (item["owner"], item["method"]))
    print("\norphan capabilities grouped by the stage that should drive them:")
    for stage in sorted(by_stage, key=lambda s: -len(by_stage[s])):
        print("  %-16s %4d  e.g. %s" % (stage, len(by_stage[stage]),
                                        ", ".join(sorted(by_stage[stage])[:2])))

    MAP_OUT.write_text(json.dumps(
        {"generated_from": str(CENSUS.name), "pending": len(pending),
         "dispositions": {k: len(v) for k, v in buckets.items()},
         "stage_ownership": {k: sorted(v) for k, v in by_stage.items()},
         "findings": plan}, indent=1), encoding="utf-8")

    # ── training data: one row per finding, inputs + derived label ──────
    JSONL_OUT.parent.mkdir(parents=True, exist_ok=True)
    with JSONL_OUT.open("w", encoding="utf-8") as fh:
        for key, item in sorted(plan.items()):
            fh.write(json.dumps({
                "id": key,
                "inputs": {
                    "owner": item["owner"], "method": item["method"],
                    "nature": item["nature"], "kind": item["kind"],
                    "class_registered": item["kind"] != "class_unregistered",
                    "production_ref_count": len(item["refs"]),
                    "declared_emits": sorted(item["emits"]),
                    "declared_requires": sorted(item["requires"]),
                    "feeds_into": item["consumer_natures"],
                },
                "label": {
                    "disposition": item["disposition"],
                    "consumer_stage": (item["consumer_natures"] or [""])[0],
                    "rule": "wire_at_site if a production referrer exists, else "
                            "integrate_via_stage(consumer nature from feeds_into)",
                },
                "evidence": {"reason": item["reason"], "refs": item["refs"]},
            }, ensure_ascii=False) + "\n")
    print("\nwrote %s" % MAP_OUT.name)
    print("wrote %s (%d rows)" % (JSONL_OUT.relative_to(REPO), len(plan)))

    # ── Mermaid: nature -> owner class -> capability, edges from feeds_into ──
    lines = ["graph LR"]
    seen_nature, seen_owner = set(), set()
    for key, item in sorted(plan.items()):
        if item["kind"] == "module_level":
            continue
        owner = item["owner"]
        nature = item["nature"] or "unknown"
        if nature not in seen_nature:
            lines.append("  N_%s[\"%s\"]" % (nature, nature))
            seen_nature.add(nature)
        if owner not in seen_owner:
            lines.append("  C_%s([\"%s\"])" % (owner, owner))
            lines.append("  N_%s --> C_%s" % (nature, owner))
            seen_owner.add(owner)
        style = {"wire_at_site": "C_wire", "integrate_via_stage": "C_integrate",
                 "unresolved": "C_unresolved"}.get(item["disposition"], "C_other")
        lines.append("  M_%s_%s[\"%s\"]:::M" % (owner, item["method"],
                                                item["method"]))
        lines.append("  C_%s --> M_%s_%s" % (owner, owner, item["method"]))
    for nature, contract in sorted(defs.items()):
        for target in (contract.get("feeds_into") or []):
            if nature in seen_nature and target in seen_nature:
                lines.append("  N_%s -.->|feeds| N_%s" % (nature, target))
    lines.append("  classDef M fill:#eee,stroke:#999;")
    MMD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote %s (%d edges)" % (MMD_OUT.name, len(lines) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
