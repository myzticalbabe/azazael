"""Static codebase graph extraction and multi-format export utilities."""

from __future__ import annotations

import ast
import csv
import html
import io
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


@dataclass
class GraphNode:
    """A graph node representing a Python module or directory."""

    node_id: str
    label: str
    kind: str
    path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphEdge:
    """A directed relationship between graph nodes."""

    source: str
    target: str
    kind: str = "imports"


class CodebaseGraph:
    """Extract a safe, static graph from Python files without importing them."""

    def __init__(self, root: Path | str, include_tests: bool = True) -> None:
        self.root = Path(root).resolve()
        self.include_tests = include_tests
        self.nodes: dict[str, GraphNode] = {}
        self.edges: set[GraphEdge] = set()
        self.parse_errors: list[dict[str, str]] = []

    def build(self) -> "CodebaseGraph":
        """Parse Python files below ``root`` and populate nodes and imports."""
        files = [path for path in sorted(self.root.rglob("*.py")) if not self._skip(path)]
        for path in files:
            self._add_module(path)
        self._add_architecture_edges(files)
        for path in files:
            self._add_import_edges(path)
        return self

    def _add_architecture_edges(self, files: list[Path]) -> None:
        """Add directory/package nodes and containment edges."""
        directories: set[Path] = set()
        for path in files:
            relative_parent = path.relative_to(self.root).parent
            while relative_parent != Path("."):
                directories.add(relative_parent)
                relative_parent = relative_parent.parent
        for directory in sorted(directories, key=lambda item: (len(item.parts), item.as_posix())):
            directory_id = f"dir:{directory.as_posix()}"
            self.nodes.setdefault(directory_id, GraphNode(
                node_id=directory_id,
                label=directory.name,
                kind="directory",
                path=directory.as_posix(),
            ))
            parent = directory.parent
            if parent != Path("."):
                self.edges.add(GraphEdge(f"dir:{parent.as_posix()}", directory_id, "contains"))
        for path in files:
            parent = path.relative_to(self.root).parent
            if parent != Path("."):
                self.edges.add(GraphEdge(f"dir:{parent.as_posix()}", self._module_id(path), "contains"))

    def _skip(self, path: Path) -> bool:
        parts = set(path.relative_to(self.root).parts)
        if parts.intersection({"__pycache__", ".venv", "build", "dist", "archive"}):
            return True
        return not self.include_tests and "tests" in parts

    def _module_id(self, path: Path) -> str:
        relative = path.relative_to(self.root).with_suffix("")
        parts = list(relative.parts)
        if parts[-1] == "__init__":
            parts.pop()
        return ".".join(parts) or self.root.name

    def _add_module(self, path: Path) -> None:
        module_id = self._module_id(path)
        try:
            lines = path.read_text(encoding="utf-8").count("\n") + 1
        except (OSError, UnicodeError):
            note_failure("codebase_graph:L98", None)
            lines = 0
        self.nodes[module_id] = GraphNode(
            node_id=module_id,
            label=path.stem,
            kind="module",
            path=path.relative_to(self.root).as_posix(),
            metadata={"lines": lines},
        )

    def _add_import_edges(self, path: Path) -> None:
        source = self._module_id(path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            note_failure("codebase_graph:L112", exc)
            self.parse_errors.append({"path": str(path), "error": str(exc)})
            return
        for node in ast.walk(tree):
            imported: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    self._add_edge_if_local(source, imported)
            elif isinstance(node, ast.ImportFrom):
                imported = self._resolve_import(source, node.module or "", node.level)
                if imported:
                    self._add_edge_if_local(source, imported)

    def _resolve_import(self, source: str, module: str, level: int) -> str:
        if level <= 0:
            return module
        package = source.split(".")[:-1]
        if level > len(package):
            return module
        return ".".join(package[: len(package) - level + 1] + ([module] if module else []))

    def _add_edge_if_local(self, source: str, imported: str) -> None:
        candidates = [imported]
        while "." in imported:
            imported = imported.rsplit(".", 1)[0]
            candidates.append(imported)
        target = next((item for item in candidates if item in self.nodes), None)
        if target and target != source:
            self.edges.add(GraphEdge(source, target))

    def add_overlay(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        """Merge runtime or externally computed nodes and edges into this graph."""
        for node in nodes:
            self.nodes[node.node_id] = node
        self.edges.update(edges)

    def cycles(self) -> list[list[str]]:
        """Return strongly connected components containing import cycles."""
        adjacency = self._adjacency()
        index = 0
        stack: list[str] = []
        on_stack: set[str] = set()
        indices: dict[str, int] = {}
        lowlinks: dict[str, int] = {}
        result: list[list[str]] = []

        def visit(node: str) -> None:
            nonlocal index
            indices[node] = index
            lowlinks[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            for target in adjacency.get(node, []):
                if target not in indices:
                    visit(target)
                    lowlinks[node] = min(lowlinks[node], lowlinks[target])
                elif target in on_stack:
                    lowlinks[node] = min(lowlinks[node], indices[target])
            if lowlinks[node] == indices[node]:
                component: list[str] = []
                while True:
                    item = stack.pop()
                    on_stack.remove(item)
                    component.append(item)
                    if item == node:
                        break
                if len(component) > 1 or node in adjacency.get(node, []):
                    result.append(sorted(component))

        for node in sorted(self.nodes):
            if node not in indices:
                visit(node)
        return sorted(result, key=lambda item: item[0])

    def _adjacency(self) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = {node: [] for node in self.nodes}
        for edge in self.edges:
            adjacency.setdefault(edge.source, []).append(edge.target)
        return adjacency

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON graph representation."""
        return {
            "schema_version": 1,
            "root": str(self.root),
            "nodes": [node.__dict__ for node in sorted(self.nodes.values(), key=lambda n: n.node_id)],
            "edges": [edge.__dict__ for edge in sorted(self.edges, key=lambda e: (e.source, e.target, e.kind))],
            "cycles": self.cycles(),
            "parse_errors": self.parse_errors,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    def to_mermaid(self) -> str:
        """Render modules and imports as a Mermaid flowchart."""
        lines = [
            "flowchart LR",
            "    classDef module fill:#16213e,stroke:#00d9ff,color:#fff;",
            "    classDef directory fill:#1e293b,stroke:#86efac,color:#fff;",
            "    classDef runtime fill:#3b1d5a,stroke:#f0abfc,color:#fff;",
            "    classDef cycle fill:#4c1d1d,stroke:#f87171,color:#fff;",
        ]
        cycle_nodes = {item for cycle in self.cycles() for item in cycle}
        for node in sorted(self.nodes.values(), key=lambda n: n.node_id):
            safe_id = _safe_id(node.node_id)
            label = node.label.replace('"', "'")
            style = "cycle" if node.node_id in cycle_nodes else ("directory" if node.kind == "directory" else ("runtime" if node.kind.startswith("runtime") else "module"))
            lines.append(f'    {safe_id}["{label}"]:::{style}')
        for edge in sorted(self.edges, key=lambda e: (e.source, e.target, e.kind)):
            connector = "-.->" if edge.kind == "contains" else "-->|" + edge.kind + "|"
            lines.append(f"    {_safe_id(edge.source)} {connector} {_safe_id(edge.target)}")
        if not self.nodes:
            lines.append('    empty["No Python modules found"]')
        return "\n".join(lines)

    def to_dot(self) -> str:
        """Render modules and imports as Graphviz DOT."""
        lines = ["digraph Codebase {", "  rankdir=LR;", "  node [shape=box];"]
        cycle_nodes = {item for cycle in self.cycles() for item in cycle}
        for node in sorted(self.nodes.values(), key=lambda n: n.node_id):
            shape = "folder" if node.kind == "directory" else "box"
            color = "#f87171" if node.node_id in cycle_nodes else ("#86efac" if node.kind == "directory" else ("#f0abfc" if node.kind.startswith("runtime") else "#00d9ff"))
            lines.append(f'  "{_dot_escape(node.node_id)}" [label="{_dot_escape(node.label)}", shape={shape}, color="{color}"];')
        for edge in sorted(self.edges, key=lambda e: (e.source, e.target, e.kind)):
            style = "dashed" if edge.kind == "contains" else "solid"
            lines.append(f'  "{_dot_escape(edge.source)}" -> "{_dot_escape(edge.target)}" [label="{_dot_escape(edge.kind)}", style={style}];')
        lines.append("}")
        return "\n".join(lines)

    def to_mermaid_mindmap(self, title: str = "Azazael Codebase") -> str:
        """Render a compact Mermaid mind-map grouped by top-level package."""
        lines = ["mindmap", f"  root(({_mindmap_escape(title)}))", "    Directories"]
        directories = [node for node in sorted(self.nodes.values(), key=lambda n: n.node_id) if node.kind == "directory"]
        for node in directories:
            lines.append(f"      {_mindmap_escape(node.path or node.label)}")
        lines.append("    Modules")
        modules = [node for node in sorted(self.nodes.values(), key=lambda n: n.node_id) if node.kind != "directory"]
        grouped: dict[str, list[GraphNode]] = {}
        for node in modules:
            grouped.setdefault(node.node_id.split(".", 1)[0], []).append(node)
        for group, items in grouped.items():
            lines.append(f"      {_mindmap_escape(group)}")
            for node in items:
                lines.append(f"        {_mindmap_escape(node.node_id)}")
        if not directories and not modules:
            lines.append("    No source files discovered")
        return "\n".join(lines)

    def to_graphml(self) -> str:
        """Render a standards-based GraphML document for graph applications."""
        namespace = "http://graphml.graphdrawing.org/xmlns"
        ET.register_namespace("", namespace)
        root = ET.Element(f"{{{namespace}}}graphml")
        for key_id, name, scope in (("label", "label", "node"), ("kind", "kind", "node"), ("path", "path", "node"), ("edge_kind", "kind", "edge")):
            ET.SubElement(root, f"{{{namespace}}}key", {"id": key_id, "for": scope, "attr.name": name, "attr.type": "string"})
        graph = ET.SubElement(root, f"{{{namespace}}}graph", {"id": "G", "edgedefault": "directed"})
        for node in sorted(self.nodes.values(), key=lambda n: n.node_id):
            element = ET.SubElement(graph, f"{{{namespace}}}node", {"id": _safe_id(node.node_id)})
            for key, value in (("label", node.label), ("kind", node.kind), ("path", node.path)):
                ET.SubElement(element, f"{{{namespace}}}data", {"key": key}).text = value
        for index, edge in enumerate(sorted(self.edges, key=lambda e: (e.source, e.target, e.kind))):
            element = ET.SubElement(graph, f"{{{namespace}}}edge", {"id": f"e_{index}", "source": _safe_id(edge.source), "target": _safe_id(edge.target)})
            ET.SubElement(element, f"{{{namespace}}}data", {"key": "edge_kind"}).text = edge.kind
        ET.indent(root, space="  ")
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + ET.tostring(root, encoding="unicode")

    def to_gexf(self) -> str:
        """Render a GEXF 1.2 document for Gephi and compatible tools."""
        root = ET.Element("gexf", {"xmlns": "http://gexf.net/1.2draft", "version": "1.2"})
        graph = ET.SubElement(root, "graph", {"mode": "static", "defaultedgetype": "directed"})
        nodes = ET.SubElement(graph, "nodes", {"count": str(len(self.nodes))})
        for node in sorted(self.nodes.values(), key=lambda n: n.node_id):
            ET.SubElement(nodes, "node", {"id": _safe_id(node.node_id), "label": node.label})
        edges = ET.SubElement(graph, "edges", {"count": str(len(self.edges))})
        for index, edge in enumerate(sorted(self.edges, key=lambda e: (e.source, e.target, e.kind))):
            ET.SubElement(edges, "edge", {"id": f"e_{index}", "source": _safe_id(edge.source), "target": _safe_id(edge.target), "label": edge.kind})
        ET.indent(root, space="  ")
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + ET.tostring(root, encoding="unicode")

    def to_cytoscape_json(self) -> str:
        """Render Cytoscape.js-compatible elements JSON."""
        payload = {
            "elements": {
                "nodes": [{"data": {"id": _safe_id(node.node_id), "label": node.label, "kind": node.kind, "path": node.path}} for node in sorted(self.nodes.values(), key=lambda n: n.node_id)],
                "edges": [{"data": {"id": f"e_{index}", "source": _safe_id(edge.source), "target": _safe_id(edge.target), "kind": edge.kind}} for index, edge in enumerate(sorted(self.edges, key=lambda e: (e.source, e.target, e.kind)))],
            },
            "metadata": {"schema_version": 1, "root": str(self.root), "cycles": self.cycles()},
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    def to_csv(self) -> str:
        """Render a portable edge-list CSV for spreadsheets and data tools."""
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("source", "target", "kind"))
        for edge in sorted(self.edges, key=lambda e: (e.source, e.target, e.kind)):
            writer.writerow((edge.source, edge.target, edge.kind))
        return stream.getvalue()

    def to_svg(self, title: str = "Azazael Codebase Graph") -> str:
        """Render a self-contained SVG overview without Graphviz or browser tooling."""
        nodes = sorted(self.nodes.values(), key=lambda n: n.node_id)
        columns, row_height, margin = 2, 34, 60
        positions: dict[str, tuple[int, int]] = {}
        for index, node in enumerate(nodes):
            positions[node.node_id] = (margin + (index % columns) * 560, margin + (index // columns) * row_height)
        width = 1180
        height = max(180, margin * 2 + ((len(nodes) + columns - 1) // columns) * row_height)
        cycle_nodes = {item for cycle in self.cycles() for item in cycle}
        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', f"<title>{html.escape(title)}</title>", '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#94a3b8"/></marker></defs>', '<rect width="100%" height="100%" fill="#0f172a"/>', f'<text x="{margin}" y="28" fill="#67e8f9" font-family="system-ui" font-size="18">{html.escape(title)} — {len(nodes)} nodes, {len(self.edges)} edges</text>']
        for edge in sorted(self.edges, key=lambda e: (e.source, e.target, e.kind)):
            source, target = positions.get(edge.source), positions.get(edge.target)
            if source and target:
                style = "stroke-dasharray:6 4;" if edge.kind == "contains" else ""
                lines.append(f'<line x1="{source[0]}" y1="{source[1]}" x2="{target[0]}" y2="{target[1]}" stroke="#64748b" stroke-width="1" marker-end="url(#arrow)" style="{style}"/>')
        for node in nodes:
            x, y = positions[node.node_id]
            color = "#f87171" if node.node_id in cycle_nodes else ("#86efac" if node.kind == "directory" else ("#f0abfc" if node.kind.startswith("runtime") else "#00d9ff"))
            lines.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/><text x="{x + 10}" y="{y + 4}" fill="#e2e8f0" font-family="system-ui" font-size="11">{html.escape(node.node_id)}</text>')
        lines.append("</svg>")
        return "\n".join(lines)

    def to_html(self, title: str = "Azazael Codebase Graph") -> str:
        """Render a dependency explorer with search and kind filtering."""
        payload = self.to_json().replace("</", "<\\/")
        rows = []
        for edge in sorted(self.edges, key=lambda e: (e.source, e.target, e.kind)):
            rows.append(f"<tr data-search=\"{html.escape(edge.source + ' ' + edge.target + ' ' + edge.kind)}\"><td>{html.escape(edge.source)}</td><td>{html.escape(edge.target)}</td><td>{html.escape(edge.kind)}</td></tr>")
        cycle_text = "<br>".join(" -> ".join(html.escape(item) for item in cycle) for cycle in self.cycles()) or "None detected"
        return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>body{{font:14px system-ui;background:#0f172a;color:#e2e8f0;margin:2rem}}h1,h2{{color:#67e8f9}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #334155;padding:.45rem;text-align:left}}th{{color:#86efac}}pre{{white-space:pre-wrap;background:#111827;padding:1rem;max-height:24rem;overflow:auto}}.card{{background:#1e293b;padding:1rem;margin:1rem 0;border-radius:.5rem}}input,select{{background:#0f172a;color:#fff;border:1px solid #475569;padding:.5rem;margin-right:.5rem}}</style></head>
<body><h1>{html.escape(title)}</h1><div class="card"><b>Nodes:</b> {len(self.nodes)} &nbsp; <b>Edges:</b> {len(self.edges)} &nbsp; <b>Cycles:</b> {len(self.cycles())}<br><input id="filter" placeholder="Filter edges..."><select id="kind"><option value="">All edge types</option><option>imports</option><option>contains</option><option>registry</option><option>routes</option></select></div>
<div class="card"><h2>Cycles</h2><p>{cycle_text}</p></div><div class="card"><h2>Relationships</h2><table id="edges"><tr><th>From</th><th>To</th><th>Type</th></tr>{''.join(rows)}</table></div>
<div class="card"><h2>Canonical graph JSON</h2><details><summary>Show data</summary><pre id="graph-data"></pre></details></div>
<script>const data={payload};document.getElementById('graph-data').textContent=JSON.stringify(data,null,2);const filter=document.getElementById('filter'),kind=document.getElementById('kind');function apply(){{const q=filter.value.toLowerCase(),k=kind.value;document.querySelectorAll('#edges tr[data-search]').forEach(row=>{{row.hidden=!!((q&&!row.dataset.search.toLowerCase().includes(q))||(k&&row.children[2].textContent!==k));}});}}filter.oninput=apply;kind.onchange=apply;</script></body></html>"""

    def snapshot_diff(self, previous: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
        """Compare this graph with a previous ``to_dict()`` snapshot."""
        current_nodes = {item["node_id"]: item for item in self.to_dict()["nodes"]}
        old_nodes = {item["node_id"]: item for item in previous.get("nodes", [])}
        current_edges = {tuple(item[key] for key in ("source", "target", "kind")) for item in self.to_dict()["edges"]}
        old_edges = {tuple(item[key] for key in ("source", "target", "kind")) for item in previous.get("edges", [])}
        return {
            "added_nodes": [current_nodes[key] for key in sorted(current_nodes.keys() - old_nodes.keys())],
            "removed_nodes": [old_nodes[key] for key in sorted(old_nodes.keys() - current_nodes.keys())],
            "added_edges": [{"source": source, "target": target, "kind": kind} for source, target, kind in sorted(current_edges - old_edges)],
            "removed_edges": [{"source": source, "target": target, "kind": kind} for source, target, kind in sorted(old_edges - current_edges)],
        }


def _safe_id(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]", "_", value)
    return "m_" + result


def _mindmap_escape(value: str) -> str:
    """Keep labels valid and readable in Mermaid mind-map syntax."""
    return re.sub(r"[\\n\\r()\\[\\]{}]", " ", str(value)).strip() or "unnamed"


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_graph(root: Path | str, include_tests: bool = True) -> CodebaseGraph:
    """Build and return a static codebase graph."""
    return CodebaseGraph(root, include_tests=include_tests).build()
