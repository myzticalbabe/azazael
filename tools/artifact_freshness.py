#!/usr/bin/env python3
# coding: utf-8
"""Derived-artifact freshness audit.

Every artifact in REGISTRY is *derived* from source. A derived artifact older
than its source is a stale map, and stale maps get acted on: the PF16 census,
the wire-or-cut table, the integration map and the knowledge graph were each
consumed while stale at least once before the 2026-09-18 refresh
(NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md, section 12). This is the
check that catches it before the map is trusted, rather than after.

It also checks one thing mtime cannot see: whether `graphify-out/GRAPH_REPORT.md`
describes the graph sitting next to it, or a different one. Regenerating a
report from a re-derived graph while the graph.json write is refused (graphify's
shrink guard) leaves the pair describing two different graphs -- both files
fresh, neither agreeing. Freshness alone cannot detect that; the clustered-ness
of graph.json can.

Exit 0 = no stale artifact and no report/graph mismatch.
Exit 1 = at least one problem, each printed with its evidence.

Usage:
    python tools/artifact_freshness.py
    python tools/artifact_freshness.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]

# (artifact, source roots, source patterns). Roots are relative to the repo root
# so the audit is portable across the W11 / WSL / bare-metal checkouts.
REGISTRY: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("NEURAL_MESH_FUNCTION_TODO.md", ("src",), ("*.py",)),
    ("NEURAL_MESH_WIRE_OR_CUT.json", ("src",), ("*.py",)),
    ("NEURAL_MESH_WIRE_OR_CUT_WORKLIST.md", ("src",), ("*.py",)),
    ("NEURAL_MESH_INTEGRATION_MAP.json", ("src",), ("*.py",)),
    ("NEURAL_MESH_INTEROP.mmd", ("src",), ("*.py",)),
    ("logs/capability_wiring_dataset.jsonl", ("src",), ("*.py",)),
    ("graphify-out/graph.json", ("src",), ("*.py",)),
    ("graphify-out/GRAPH_REPORT.md", ("src",), ("*.py",)),
)

GRAPH_JSON = "graphify-out/graph.json"
GRAPH_REPORT = "graphify-out/GRAPH_REPORT.md"


def source_files(root: Path, roots: Sequence[str],
                 patterns: Sequence[str]) -> list[Path]:
    """Every source file an artifact is derived from."""
    found: list[Path] = []
    for rel in roots:
        base = root / rel
        if not base.is_dir():
            continue
        for pattern in patterns:
            found.extend(p for p in base.rglob(pattern) if p.is_file())
    return found


def audit(root: Path | None = None,
          registry: Iterable[tuple[str, tuple[str, ...], tuple[str, ...]]] | None = None
          ) -> list[dict[str, Any]]:
    """One row per artifact: exists, mtime, and which sources are newer.

    `registry` is bound late (not as a def-time default) so a caller -- or a
    test -- can substitute the set being audited without editing the module.
    """
    root = Path(root) if root is not None else ROOT
    if registry is None:
        registry = REGISTRY
    rows: list[dict[str, Any]] = []
    for artifact, roots, patterns in registry:
        path = root / artifact
        row: dict[str, Any] = {"artifact": artifact, "exists": path.is_file()}
        if not row["exists"]:
            row.update({"stale": True, "newer_count": 0, "newer": [],
                        "reason": "missing"})
            rows.append(row)
            continue
        stamp = path.stat().st_mtime
        newer = [p for p in source_files(root, roots, patterns)
                 if p.stat().st_mtime > stamp]
        newer.sort(key=lambda p: -p.stat().st_mtime)
        row.update({
            "stale": bool(newer),
            "newer_count": len(newer),
            # as_posix(), not str(): the audit runs on W11, WSL and bare metal,
            # and a Windows separator makes the same evidence non-comparable
            # across environments (and breaks the pinned test).
            "newer": [p.relative_to(root).as_posix() for p in newer[:5]],
            "reason": "older than source" if newer else "",
        })
        rows.append(row)
    return rows


def graph_report_mismatch(root: Path | None = None) -> dict[str, Any]:
    """Does GRAPH_REPORT.md describe the graph in graph.json?

    The failure this catches: a report regenerated from a re-derived clustered
    graph while the graph.json write was refused, leaving a fresh report and a
    fresh graph that disagree about communities. Both files pass an mtime
    check, so only the content can tell.
    """
    root = Path(root) if root is not None else ROOT
    graph, report = root / GRAPH_JSON, root / GRAPH_REPORT
    out: dict[str, Any] = {"checked": False, "mismatch": False, "reason": ""}
    if not (graph.is_file() and report.is_file()):
        out["reason"] = "graph.json or GRAPH_REPORT.md absent"
        return out
    try:
        data = json.loads(graph.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        out.update({"checked": True, "mismatch": True,
                    "reason": "graph.json unreadable: %s" % str(exc)[:80]})
        return out
    nodes = data.get("nodes") or []
    clustered = any(n.get("community") is not None for n in nodes)
    out.update({
        "checked": True,
        "nodes": len(nodes),
        "clustered": clustered,
        "report_newer": report.stat().st_mtime > graph.stat().st_mtime,
    })
    if out["report_newer"] and not clustered:
        out.update({"mismatch": True,
                    "reason": ("GRAPH_REPORT.md is newer than graph.json but "
                               "graph.json carries no communities: the report "
                               "describes a re-derived graph, not this one")})
    return out


def main(argv: Sequence[str] | None = None,
         registry: Iterable[tuple[str, tuple[str, ...], tuple[str, ...]]] | None = None
         ) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--root", default=None, help="repo root override (tests)")
    args = ap.parse_args(argv)

    root = Path(args.root) if args.root else ROOT
    rows = audit(root, registry)
    graph = graph_report_mismatch(root)
    stale = [r for r in rows if r["stale"]]

    if args.json:
        print(json.dumps({"artifacts": rows, "graph": graph,
                          "stale_count": len(stale)}, indent=2))
        return 1 if stale or graph["mismatch"] else 0

    print("%-44s %-8s %s" % ("ARTIFACT", "STATUS", "NEWER SOURCES"))
    for row in rows:
        if not row["exists"]:
            status, detail = "MISSING", "-"
        elif row["stale"]:
            status, detail = "STALE", "%d (e.g. %s)" % (
                row["newer_count"], ", ".join(row["newer"][:2]))
        else:
            status, detail = "current", "0"
        print("%-44s %-8s %s" % (row["artifact"], status, detail))

    print()
    if not graph["checked"]:
        print("graph/report: not checked (%s)" % graph["reason"])
    elif graph["mismatch"]:
        print("graph/report: MISMATCH -- %s" % graph["reason"])
    else:
        print("graph/report: consistent (nodes=%d clustered=%s)"
              % (graph.get("nodes"), graph.get("clustered")))

    if stale or graph["mismatch"]:
        print()
        print("FAIL: %d stale artifact(s)%s"
              % (len(stale), ", plus a graph/report mismatch"
                 if graph["mismatch"] else ""))
        print("Refresh with: python tools/mesh_function_preflight.py "
              "&& python tools/mesh_function_preflight.py --verdict "
              "&& python tools/nature_integration_map.py")
        return 1
    print()
    print("OK: every derived artifact is at least as new as its sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
