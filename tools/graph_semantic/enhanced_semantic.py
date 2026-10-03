"""Enhanced semantic extraction across ALL project documents.

The doc layer gives every document a node and a bucket edge. The concept layer
gives it its shared headings. Neither reads the document's *body* for the entities
it names. This layer does: for every included doc it extracts mentions of known
graph entities (code labels like ``DirectMemory``, ``MetaCluster``; concept and
document titles) and adds a ``mentions`` edge from the doc to each entity it names.

The result is that a reader can start at any document and reach the subsystems it
is actually about — the semantic content the doctrine "we need all docs graphed"
was asking for, extended from "every doc has an identity" to "every doc states
what it is about".

Grounded by construction: an edge exists only if the entity's label literally
appears in the document text. No entity is inferred from topic similarity.

Two guards keep the extraction from creating generic hubs (the same defect class
the god-node filter exists for):

* **distinctive shape** — a label must be an identifier (an uppercase letter after
  the first character, or an underscore, or a digit). A plain lowercase English
  word like ``state`` or ``graph`` is not an entity.
* **document-frequency cap** — a label that appears in more than ``MAX_DOC_FREQ``
  documents is a vocabulary word for this corpus (``Environment``, ``Category``),
  not a distinctive entity, and is skipped.

Usage (from the repo root, after doc_layer.py has produced its fragment):
    python tools/graph_semantic/enhanced_semantic.py
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path

ROOT = Path("graphify-out")
GRAPH = json.loads((ROOT / "graph.json").read_text(encoding="utf-8"))
DOC_FRAG = json.loads((ROOT / "doc_layer_fragment.json").read_text(encoding="utf-8"))
SCOPE = json.loads((ROOT / "_doc_scope.json").read_text(encoding="utf-8"))
INCLUDED: list[str] = SCOPE["included"]
DOC_IDS = {n["id"] for n in DOC_FRAG["nodes"]}

MAX_DOC_FREQ = 40
MAX_PER_DOC = 30

# Generic English / structural headings that are never entities.
STOP = {
    "related", "verify", "identity", "overview", "usage", "examples", "example",
    "notes", "note", "summary", "introduction", "purpose", "background", "context",
    "architecture", "configuration", "installation", "requirements", "workflow",
    "output", "inputs", "outputs", "parameters", "returns", "raises", "description",
    "features", "benefits", "limits", "troubleshooting", "references", "environment",
    "category", "session", "test", "tests", "main", "code", "data", "file", "files",
    "start", "end", "name", "type", "value", "key", "config", "status", "script",
    "scripts", "graph", "state", "result", "results", "component", "components",
    "system", "systems", "module", "modules", "class", "classes", "method", "methods",
    "function", "functions", "path", "paths", "error", "errors", "warning", "info",
}


def _is_identifier(label: str) -> bool:
    """True if the label looks like a symbol/entity rather than a dictionary word."""
    body = label.replace(" ", "")
    if not body:
        return False
    if "_" in body or any(c.isdigit() for c in body):
        return True
    # CamelCase / PascalCase: an uppercase letter after the first character.
    return any(c.isupper() for c in body[1:])


def _doc_stem(path: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", path[:-3].lower()).strip("_") if path.lower().endswith(".md") \
        else re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")


by_label: dict[str, list[str]] = collections.defaultdict(list)
for n in GRAPH["nodes"]:
    if n.get("file_type") not in ("code", "concept", "document"):
        continue
    label = str(n.get("label") or "").strip()
    low = label.lower()
    if low in STOP or len(low) < 5 or len(low) > 60:
        continue
    if low.startswith(".") or low.endswith("()"):
        continue
    if not _is_identifier(label):
        continue
    by_label[label].append(n["id"])

if not by_label:
    raise SystemExit("no candidate entity labels found")

keys = sorted(by_label, key=len, reverse=True)
pattern = re.compile("|".join(re.escape(k) for k in keys))

# --- Pass 1: document frequency per label (to drop corpus vocabulary). ---
docs: dict[str, str] = {}
df: collections.Counter = collections.Counter()
for path in INCLUDED:
    if not path.endswith(".md") or _doc_stem(path) not in DOC_IDS:
        continue
    try:
        text = Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    docs[path] = text
    for label in set(pattern.findall(text)):
        df[label] += 1

kept = {k for k in keys if 1 <= df[k] <= MAX_DOC_FREQ}
dropped = len(by_label) - len(kept)
print(f"candidate labels: {len(by_label)}  kept: {len(kept)}  dropped as corpus vocabulary: {dropped}")

# --- Pass 2: emit doc -> entity mention edges. ---
nodes: list[dict] = []
edges: list[dict] = []
seen: set[tuple[str, str]] = set()
docs_with_entity = 0
for path, text in docs.items():
    src = _doc_stem(path)
    hits = collections.Counter(m for m in pattern.findall(text) if m in kept)
    added = 0
    for label, count in sorted(hits.items(), key=lambda kv: (-kv[1], -len(kv[0]))):
        for tgt in by_label.get(label, [])[:2]:
            if tgt == src or (src, tgt) in seen:
                continue
            seen.add((src, tgt))
            edges.append({
                "source": src, "target": tgt, "relation": "mentions",
                "confidence": "EXTRACTED", "confidence_score": 0.85,
                "source_file": path, "source_location": None, "weight": float(min(count, 5)),
            })
            added += 1
            if added >= MAX_PER_DOC:
                break
        if added >= MAX_PER_DOC:
            break
    if added:
        docs_with_entity += 1

print(f"docs with >=1 entity edge: {docs_with_entity} / {len(docs)}")
print(f"mention edges: {len(edges)}")
frag = {"nodes": nodes, "edges": edges, "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
out = ROOT / "enhanced_semantic_fragment.json"
out.write_text(json.dumps(frag, indent=1, ensure_ascii=False), encoding="utf-8")
print("wrote", out)
