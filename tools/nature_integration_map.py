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


#: Where a "production" reference may come from. `scripts/` and `tools/` are
#: entry points -- the schedulers, monitors and audit tools -- and they are
#: production consumers in every sense that matters: they RUN. Scanning only
#: `src/` made a capability with its only caller in `scripts/` look unreferenced,
#: which is how `get_gossip_trust_state` (called by `mesh_gossip_cycle.py`)
#: ended up in the unresolved bucket.
USE_ROOTS = ("src", "scripts", "tools")


def production_uses() -> tuple:
    """(name -> [(file, line)], file -> scope) outside tests and shims.

    `__init__.py` is excluded because a re-export is not a consumer -- counting
    it made every worm look wired and left the colour queens with nothing to
    evaluate, which is inert rather than correct.

    The scope map is returned alongside the uses so a disposition can say WHERE
    its referrer lives: a `src` referrer is a library consumer, while a
    `scripts` referrer is an entry point. Both are real, but they are not the
    same kind of evidence and the plan should not have to guess.
    """
    uses: dict = defaultdict(list)
    scope_of: dict = {}
    for sub in USE_ROOTS:
        root = REPO / sub
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts or path.name == "__init__.py":
                continue
            if "tests" in path.parts or path.name.startswith("test_"):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8",
                                                 errors="replace"))
            except Exception:
                continue
            rel = str(path.relative_to(REPO)).replace("\\", "/")
            scope_of[rel] = sub
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    uses[node.id].append((rel, node.lineno))
                elif isinstance(node, ast.Attribute):
                    uses[node.attr].append((rel, node.lineno))
    return uses, scope_of


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


def _scope_tag(refs, scope_of: dict) -> list:
    """Sorted, de-duplicated `src`/`scripts`/`tools` tags for a ref list."""
    roles = {scope_of.get(f, str(Path(f).parts[0] if Path(f).parts else "?"))
             for f, _ln in refs}
    return sorted(roles)


def classify(finding: dict, natures: dict, defs: dict, uses: dict,
             modules: dict | None = None, scope_of: dict | None = None) -> dict:
    """Disposition for one census row, with the evidence that decided it."""
    qual = str(finding.get("qualname") or finding.get("key") or "")
    module = str(finding.get("module") or "")
    owner, _, method = qual.rpartition(".")
    if not owner:
        # A module-level function has no class to inherit a nature from, but its
        # MODULE does: the registry records `__module__` for every registered
        # class, so a module -> nature index derived from it answers the same
        # question one level up. The first version punted here ("needs a caller
        # decided per function, not per class"): that left 23 findings -- 22% of
        # the backlog, including `spine_reset` and `get_gossip_trust_state` --
        # with a disposition no consumer could act on, and the Mermaid emitter
        # then skipped them entirely, so they were not even visible.
        mod = (modules or {}).get(module, "")
        contract = defs.get(mod) or {}
        consumer_natures = list(contract.get("feeds_into") or [])
        refs = [(f, ln) for f, ln in uses.get(qual, [])]
        if refs:
            disposition = "wire_at_site"
            reason = ("module-level function with a production referrer at "
                      "%s:%s, so a real call site exists" % refs[0])
        elif mod:
            disposition = "integrate_via_stage"
            reason = ("module-level function with no production referrer; its "
                      "own module belongs to nature %s, which feeds into %s, so "
                      "that stage must drive it"
                      % (mod, ", ".join(consumer_natures) or "(nothing)"))
        else:
            disposition = "unresolved"
            reason = ("module-level function with no production referrer and a "
                      "module the registry attributes to no nature")
        return {"owner": "", "method": qual, "module": module,
                "nature": mod, "kind": "module_level",
                "disposition": disposition, "reason": reason,
                "consumer_natures": consumer_natures,
                "ref_scope": _scope_tag(refs, scope_of or {}),
                "refs": refs[:5], "emits": {}, "requires": {}}

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
        return {"owner": owner, "method": method, "module": module,
                "nature": nature,
                "kind": "class_unregistered", "consumer_natures": [],
                "disposition": "unresolved",
                "reason": "class is not in the registry and nothing references it",
                "ref_scope": [], "emits": {}, "requires": {}, "refs": []}

    if reachable:
        return {"owner": owner, "method": method, "module": module,
                "nature": nature,
                "kind": "reachable_class", "consumer_natures": consumer_natures,
                "disposition": "wire_at_site",
                "reason": "class is referenced in production at %s:%s, so a real "
                          "call site exists" % refs[0],
                "ref_scope": _scope_tag(refs, scope_of or {}),
                "emits": emits, "requires": requires, "refs": refs[:5]}

    stage = consumer_natures[0] if consumer_natures else ""
    return {"owner": owner, "method": method, "module": module,
            "nature": nature,
            "kind": "orphan_class", "consumer_natures": consumer_natures,
            "disposition": "integrate_via_stage",
            "reason": ("class has no production referrer; %s declares it feeds "
                       "into %s, so the %s stage must drive it"
                       % (nature or "nature unknown",
                          ", ".join(consumer_natures) or "(nothing)",
                          stage or "consumer")),
            "ref_scope": [], "emits": emits, "requires": requires, "refs": []}


#: Keys every worm result carries regardless of nature -- the protocol envelope
#: plus the routing shims. A contract is about the PAYLOAD, so these are not
#: emits: counting them made every nature look like it declared
#: `{success, method, result}` and said nothing about the data.
ENVELOPE_KEYS = frozenset({
    "success", "method", "result", "error", "ok", "data", "timestamp",
    "duration_ms", "elapsed_ms", "worm", "worm_name",
})

#: Methods whose literal dict returns describe a worm's output.
RESULT_METHODS = ("execute", "run", "_execute", "process", "apply", "cycle",
                  "tick")


def _module_file(module: str):
    """Locate a module path from its dotted name, tolerating stems."""
    rel = module.replace(".", "/") + ".py"
    for base in ("src", "scripts"):
        cand = REPO / base / rel
        if cand.is_file():
            return cand
    stem = module.rsplit(".", 1)[-1] + ".py"
    hits = sorted((REPO / "src").rglob(stem))
    return hits[0] if hits else None


def derived_contracts(natures: dict) -> dict:
    """Derive each nature's emits from what its member worms actually return.

    Only four of twenty-six natures declared a `data_contracts` block, so
    `emits` was an empty dict for the other twenty-two and the decoration check
    could not run at all for them. Hand-writing twenty-two contracts would have
    invented names that no code produces, which is worse than an empty dict: it
    would make the check pass while proving nothing.

    So the contract is READ OFF the code instead -- every literal dict key a
    member worm returns from execute()/run()/apply()/cycle(), minus the protocol
    envelope. That is reproducible, and it is the only form of the claim that
    can be falsified by someone reading a worm.
    """
    by_nature: dict = defaultdict(set)
    for info in natures.values():
        nat = info.get("nature") or ""
        mod = info.get("module") or ""
        if nat and mod:
            by_nature[nat].add(mod)

    out: dict = {}
    parsed: dict = {}
    for nature, mods in sorted(by_nature.items()):
        counts: dict = defaultdict(int)
        for mod in sorted(mods):
            if mod not in parsed:
                path = _module_file(mod)
                tree = None
                if path is not None:
                    try:
                        tree = ast.parse(path.read_text(encoding="utf-8",
                                                         errors="replace"))
                    except Exception:
                        tree = None
                parsed[mod] = tree
            tree = parsed[mod]
            if tree is None:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name not in RESULT_METHODS:
                    continue
                for sub in ast.walk(node):
                    if not (isinstance(sub, ast.Return)
                            and isinstance(sub.value, ast.Dict)):
                        continue
                    for key in sub.value.keys:
                        if (isinstance(key, ast.Constant)
                                and isinstance(key.value, str)
                                and key.value
                                and key.value not in ENVELOPE_KEYS):
                            counts[key.value] += 1
        if counts:
            out[nature] = {"emits": dict(sorted(counts.items())),
                           "members": len(mods)}
    return out


def contract_coverage(defs: dict, uses: dict, derived: dict | None = None) -> dict:
    """Which natures declare a data contract, and which declared fields none reads.

    `emits` / `requires` are the half of this audit that can prove a wiring is
    REAL rather than decorative. A capability whose declared output no
    production code names is the `SplitBrainResolverWorm.report_fork` failure --
    the writer filled a box the reader never consulted -- generalised.

    The declaration gap is reported alongside the unread fields on purpose: only
    a quarter of the natures declared a contract at all when this was written,
    and for the rest `emits`/`requires` are empty dicts that a reader would
    otherwise mistake for "clean".
    """
    declared: dict = {}
    silent: list = []
    unread: dict = {}
    for nature, contract in sorted(defs.items()):
        dc = contract.get("data_contracts") or {}
        if not dc:
            silent.append(nature)
            continue
        emits = dc.get("emits") or {}
        requires = dc.get("requires") or {}
        declared[nature] = {"emits": len(emits), "requires": len(requires)}
        dead = sorted(f for f in emits if not uses.get(f))
        if dead:
            unread[nature] = dead

    # The derived set is the check that actually covers the tree: every key a
    # member worm returns that no production code names is decoration, whether or
    # not the nature got round to declaring a contract.
    derived_ok: dict = {}
    derived_dead: dict = {}
    for nature, item in sorted((derived or {}).items()):
        emits = item.get("emits") or {}
        derived_ok[nature] = {"emits": len(emits),
                              "members": item.get("members", 0)}
        dead = sorted(f for f in emits if not uses.get(f))
        if dead:
            derived_dead[nature] = dead

    return {"natures_total": len(defs), "declared": declared,
            "no_contract_declared": silent,
            "declared_emits_nothing_reads": unread,
            "derived": derived_ok,
            "derived_emits_nothing_reads": derived_dead,
            "derived_natures": len(derived_ok),
            "coverage": ("%d/%d natures declare a contract, %d/%d have one "
                         "derivable from code"
                         % (len(declared), len(defs), len(derived_ok),
                            len(defs)))}


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
    uses, scope_of = production_uses()
    # module -> nature, taken from the registry's own `__module__` records. This
    # is what lets a module-level capability inherit a nature instead of dead-
    # ending on "module_level".
    # Keyed by BOTH the dotted module and its last component: the census records
    # a short stem (`exmachina`), while the registry records `__module__`
    # (`CORE.WORMS.expansion.exmachina`). Indexing only the dotted form made
    # every module-level finding miss, so all 23 fell through to `unresolved`.
    modules: dict = {}
    for info in natures.values():
        mod = info.get("module") or ""
        nat = info.get("nature") or ""
        if not (mod and nat):
            continue
        modules.setdefault(mod, nat)
        modules.setdefault(mod.rsplit(".", 1)[-1], nat)
    derived = derived_contracts(natures)
    cov = contract_coverage(defs, uses, derived)
    print("pending findings : %d" % len(pending))
    print("registry classes : %d" % len(natures))
    print("natures declared : %d" % len(defs))
    print("modules mapped   : %d" % len(modules))

    plan = {}
    for key, rec in pending.items():
        row = dict(rec or {})
        row["key"] = key
        item = classify(row, natures, defs, uses, modules, scope_of)
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

    print("\ndata-contract coverage (the half that can prove a wiring is real):")
    print("  coverage                         : %s" % cov["coverage"])
    if cov["no_contract_declared"]:
        print("  no contract declared (%d): %s"
              % (len(cov["no_contract_declared"]),
                 ", ".join(cov["no_contract_declared"])))
    for nature, dead in sorted(cov["declared_emits_nothing_reads"].items()):
        print("  declared-but-unread emits in %-12s %s"
              % (nature, ", ".join(dead)))

    # The derived census is the one that spans the whole tree.
    dead_natures = cov["derived_emits_nothing_reads"]
    live = cov["derived_natures"] - len(dead_natures)
    print("  derived from code (%d natures; %d with every emit read):"
          % (cov["derived_natures"], live))
    for nature, dead in sorted(dead_natures.items()):
        total = cov["derived"][nature]["emits"]
        print("    %-14s %2d/%2d emits nothing reads: %s"
              % (nature, len(dead), total, ", ".join(dead[:6])))

    MAP_OUT.write_text(json.dumps(
        {"generated_from": str(CENSUS.name), "pending": len(pending),
         "dispositions": {k: len(v) for k, v in buckets.items()},
         "stage_ownership": {k: sorted(v) for k, v in by_stage.items()},
         "contract_coverage": cov,
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
                    "ref_scope": item["ref_scope"],
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
    print("wrote %s (%d rows)" % (JSONL_OUT.relative_to(REPO), len(plan)))    # ── Mermaid: nature -> owner class -> capability, edges from feeds_into ──
    #
    # The disposition is why this diagram exists, so it has to be VISIBLE. The
    # first version computed a `style` for every node and then threw it away: it
    # emitted exactly one classDef and never attached C_wire / C_integrate /
    # C_unresolved to anything, so wireable, orphaned and unresolved capabilities
    # all rendered identically. Per the Mermaid flowchart spec a class only takes
    # effect when it is BOTH declared with `classDef <name>` AND attached to a
    # node, either as `node:::name` or with `class node name;`.
    disp_classes = {
        "wire_at_site": ("C_wire", "fill:#dff5df,stroke:#2e7d32"),
        "integrate_via_stage": ("C_integrate", "fill:#fdf3d6,stroke:#b8860b"),
        "unresolved": ("C_unresolved", "fill:#fbe3e3,stroke:#b71c1c"),
    }

    # Every natures node is declared up front so the nature-to-nature contract
    # edges are the WHOLE contract graph. Drawing only the natures that happened
    # to own a pending finding made the inter-nature picture look sparse for a
    # reason that had nothing to do with the contracts.
    contract_natures = set(defs)
    for contract in defs.values():
        contract_natures.update(contract.get("feeds_into") or [])
    contract_natures.update((item.get("nature") or "unknown")
                            for item in plan.values())

    lines = ["graph LR"]
    seen_nature: set = set()
    for nature in sorted(contract_natures):
        lines.append("  N_%s[\"%s\"]" % (nature, nature))
        seen_nature.add(nature)

    seen_owner, seen_mod = set(), set()
    for key, item in sorted(plan.items()):
        owner = item.get("owner") or ""
        nature = item.get("nature") or "unknown"
        label = disp_classes.get(item["disposition"], ("", ""))[0]
        suffix = ":::%s" % label if label else ""
        if owner:
            if owner not in seen_owner:
                lines.append("  C_%s([\"%s\"])%s" % (owner, owner, suffix))
                lines.append("  N_%s --> C_%s" % (nature, owner))
                seen_owner.add(owner)
            parent = "C_%s" % owner
            mid = "M_%s_%s" % (owner, item["method"])
        else:
            # Module-level capabilities are graphed under their module.
            # Skipping them (the old `continue`) hid 23 findings from the only
            # picture of the mesh a human actually reads.
            mod = (item.get("module") or "unknown").replace(".", "_")
            if mod not in seen_mod:
                lines.append("  D_%s[[\"%s\"]]%s"
                             % (mod, item.get("module") or "unknown", suffix))
                lines.append("  N_%s --> D_%s" % (nature, mod))
                seen_mod.add(mod)
            parent = "D_%s" % mod
            mid = "M_mod_%s" % item["method"]
        lines.append("  %s[\"%s\"]:::M" % (mid, item["method"]))
        lines.append("  %s --> %s" % (parent, mid))

    for nature, contract in sorted(defs.items()):
        for target in (contract.get("feeds_into") or []):
            lines.append("  N_%s -.->|feeds| N_%s" % (nature, target))
    for _name, (_cls, _style) in sorted(disp_classes.items()):
        lines.append("  classDef %s %s;" % (_cls, _style))
    lines.append("  classDef M fill:#eee,stroke:#999;")
    MMD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote %s (%d edges)" % (MMD_OUT.name, len(lines) - 1))

    return 0


if __name__ == "__main__":
    sys.exit(main())
